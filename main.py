import os
import json
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from state import AgentState
from tools.flight_tools import get_flight_info
from tools.ticket_tools import get_ticket_details
from tools.fare_tools import search_fares
from tools.baggage_tools import get_baggage_policy
from datetime import datetime

load_dotenv()

# Khởi tạo LLM với OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def load_prompt(file_name: str) -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", file_name)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def manage_memory_and_cache(state: AgentState):
    """Giữ lượt chat gần nhất và kiểm tra Cache."""
    messages = state["messages"]
    
    if len(messages) > 10:
        messages = messages[-10:]
    
    # 2. Kiểm tra Cache
    current_user_msg = messages[-1].content.strip().lower()
    for i in range(len(messages) - 2, -1, -1):
        msg = messages[i]
        if isinstance(msg, HumanMessage) and msg.content.strip().lower() == current_user_msg:
            if i + 1 < len(messages) and isinstance(messages[i+1], AIMessage):
                cached_response = messages[i+1].content
                return {
                    "messages": messages, 
                    "query_results": cached_response, 
                    "is_cached": True
                }
    
    return {"messages": messages, "is_cached": False}

def intent_classifier(state: AgentState):
    """Node phân loại ý định và trích xuất thực thể bằng LLM."""
    if state.get("is_cached"):
        return state

    # 1. Đọc prompt và xử lý fallback (từ nhánh cao)
    sys_prompt = load_prompt("extraction_prompt.txt")
    if not sys_prompt:
        sys_prompt = "Bạn là hệ thống Trích xuất thông tin hàng không."

    # 2. Thêm ngữ cảnh thời gian thực (từ nhánh cao)
    today = datetime.now().strftime('%Y-%m-%d')
    sys_prompt += f"\nLưu ý Context: Hôm nay là ngày {today}."

    # 3. Khôi phục Lịch sử hội thoại - Memory (từ nhánh main)
    messages = [{"role": "system", "content": sys_prompt}]
    for m in state["messages"][-6:]:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        messages.append({"role": role, "content": m.content})

    # 4. Gọi LLM 
    # Option A: Nếu bạn dùng Pydantic (ExtractionResult) như trong nhánh cao:
    # structured_llm = llm.with_structured_output(ExtractionResult)
    # response = structured_llm.invoke(messages)
    # return {"current_intent": response.intent, "extracted_data": response.dict()}

    # Option B: Nếu vẫn dùng JSON Mode như code main hiện tại:
    response = llm.invoke(messages, response_format={"type": "json_object"})
    
    # Parse cấu trúc JSON từ LLM
    try:
        content = response.content.strip()
        # Xử lý xóa markdown nếu có
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        extracted_data = json.loads(content)
        return {
            "current_intent": extracted_data.get("intent", "general"),
            "extracted_data": extracted_data
        }
    except Exception as e:
        print(f"Lỗi trích xuất thông tin: {e}")
        return {"current_intent": "general", "extracted_data": {"intent": "general", "entities": {}}}

def tool_node(state: AgentState):
    """Node gọi các hàm Python để truy vấn dữ liệu thực tế từ Entities trích xuất được."""
    if state.get("is_cached"):
        return state

    intent = state.get("current_intent")
    entities = state.get("extracted_data", {})
    
    query_results = "Không nhận diện được yêu cầu cụ thể."
    
    if intent == "flight_info":
        flight_code = entities.get("flight_code")
        if flight_code:
            query_results = get_flight_info(flight_code=flight_code)
    elif intent == "ticket_info":
        passenger_name = entities.get("passenger_name")
        ticket_number = entities.get("ticket_number")
        if ticket_number:
            query_results = get_ticket_details(ticket_number=ticket_number)
        elif passenger_name:
            query_results = get_ticket_details(passenger_name=passenger_name)
    elif intent == "fare_search":
        departure = entities.get("departure")
        arrival = entities.get("arrival")
        if departure and arrival:
            query_results = search_fares(departure=departure, arrival=arrival)
    elif intent == "baggage_info":
        cabin_class = entities.get("cabin_class")
        baggage_type = entities.get("baggage_type") or "checked"
        if cabin_class:
            query_results = get_baggage_policy(cabin_class=cabin_class, baggage_type=baggage_type)
        else:
            query_results = {"error": "Thiếu thông tin hạng ghế (Economy hoặc Business)."}
            
    return {"query_results": query_results}

def responder(state: AgentState):
    """Node tạo câu trả lời cuối cùng sử dụng System Prompt."""
    if state.get("is_cached"):
        return {"messages": [AIMessage(content=state["query_results"])]}

    results = state.get("query_results")
    last_message = state["messages"][0].content if state["messages"] else ""
    
    response_prompt = load_prompt("response_prompt.txt")
    
    prompt = f"Dữ liệu tra cứu: {json.dumps(results, ensure_ascii=False)}\nCâu hỏi gốc của người dùng: {last_message}"
    
    response = llm.invoke([
        SystemMessage(content=response_prompt),
        HumanMessage(content=prompt)
    ])
    return {"messages": [response]}

# Xây dựng Graph
workflow = StateGraph(AgentState)

workflow.add_node("memory_and_cache", manage_memory_and_cache)
workflow.add_node("classifier", intent_classifier)
workflow.add_node("tools", tool_node)
workflow.add_node("responder", responder)

workflow.set_entry_point("memory_and_cache")

def route_after_cache(state: AgentState):
    if state.get("is_cached"):
        return "responder"
    return "classifier"

workflow.add_conditional_edges("memory_and_cache", route_after_cache)
workflow.add_edge("classifier", "tools")
workflow.add_edge("tools", "responder")
workflow.add_edge("responder", END)

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    print("--- Chatbot Hàng Không (NEO 2.0) đã sẵn sàng! (Gõ 'exit' để thoát) ---")
    
    config = {"configurable": {"thread_id": "user_session_1"}}
    
    while True:
        user_input = input("\nKhách hàng: ")
        if user_input.lower() in ["exit", "quit", "thoát"]:
            print("Cảm ơn bạn đã sử dụng dịch vụ. Tạm biệt!")
            break
            
        # Chạy Graph với dữ liệu mới và truyền config state vào
        # Chú ý: LangGraph dùng reducer nên {"messages": [HumanMessage(content=user_input)]} sẽ tự append liên tục
        state = app.invoke({"messages": [HumanMessage(content=user_input)]}, config)
        
        final_response = state["messages"][-1].content
        print(f"NEO 2.0: {final_response}")
        
        if state.get("is_cached"):
            print("(Phản hồi từ Cache)")