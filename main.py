import os
import json
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from state import AgentState
from tools.flight_tools import get_flight_info
from tools.ticket_tools import get_ticket_details
from tools.fare_tools import search_fares
from tools.baggage_tools import get_baggage_policy

load_dotenv()

# Khởi tạo LLM
llm = ChatOpenAI(model="gpt-4o-mini")

def read_prompt(file_name):
    """Đọc nội dung file prompt từ thư mục prompts/."""
    full_path = os.path.join("prompts", file_name)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def manage_memory_and_cache(state: AgentState):
    """Giữ 5 lượt chat gần nhất và kiểm tra Cache."""
    messages = state["messages"]
    
    # 1. Cắt tỉa memory (giữ 5 lượt = 10 messages)
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
    """Node phân loại ý định và trích xuất thực thể bằng LLM (LLM-based Extraction)."""
    if state.get("is_cached"):
        return state

    # Đọc prompt trích xuất từ file txt
    system_prompt = read_prompt("extraction_prompt.txt")
    user_query = state["messages"][-1].content
    
    # Khôi phục: Phải đưa Lịch sử hội thoại (Memory) vào để LLM Extraction hiểu ngữ cảnh cũ
    messages = [{"role": "system", "content": system_prompt}]
    for m in state["messages"][-6:]:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        messages.append({"role": role, "content": m.content})
    response = llm.invoke(messages, response_format={"type": "json_object"})
    
    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
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
    entities = state.get("extracted_data", {}).get("entities", {})
    query_results = "Không tìm thấy thông tin phù hợp."
    
    if intent == "flight_info":
        query_results = get_flight_info(
            flight_code=entities.get("flight_code")
        )
    elif intent == "ticket_info":
        query_results = get_ticket_details(
            ticket_number=entities.get("ticket_number"),
            passenger_name=entities.get("passenger_name")
        )
    elif intent == "fare_search":
        dep = entities.get("departure")
        arr = entities.get("arrival")
        date = entities.get("date")
        time_of_day = entities.get("time_of_day")
        
        # KHÔI PHỤC SLOT FILLING & BẢO VỆ TOOL
        if not dep or not arr or not date:
            missing = []
            if not dep: missing.append("điểm khởi hành")
            if not arr: missing.append("điểm đến")
            if not date: missing.append("ngày bay")
            query_results = f"LỖI HỆ THỐNG: User chưa cung cấp đủ thông tin. KHÔNG ĐƯỢC PHỊA GIÁ VÉ. Hãy lịch sự đề nghị họ bổ sung các thông tin còn thiếu sau: {', '.join(missing)}."
        else:
            query_results = search_fares(
                departure=dep,
                arrival=arr,
                date=date,
                time_of_day=time_of_day,
                cabin_class=entities.get("cabin_class"),
                cheapest_only=entities.get("cheapest_only", False)
            )
    elif intent == "baggage_info":
        query_results = get_baggage_policy(
            cabin_class=entities.get("cabin_class"),
            baggage_type=entities.get("baggage_type", "checked")
        )
        
    return {"query_results": query_results}

def responder(state: AgentState):
    """Node tạo câu trả lời cuối cùng dùng response_prompt.txt."""
    if state.get("is_cached"):
        return {"messages": [AIMessage(content=state["query_results"])]}

    results = state.get("query_results")
    intent = state.get("current_intent")
    entities = state.get("extracted_data", {}).get("entities", {})
    system_prompt = read_prompt("response_prompt.txt")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Ý định người dùng: {intent}\nThông tin đã trích xuất: {entities}\nDữ liệu từ hệ thống: {results}"}
    ]
    
    response = llm.invoke(messages)
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

app = workflow.compile()

if __name__ == "__main__":
    print("--- Chatbot Hàng Không (NEO 2.0) đã sẵn sàng! (Gõ 'exit' để thoát) ---")
    
    state = {
        "messages": [],
        "extracted_data": {},
        "query_results": "",
        "current_intent": "general",
        "is_cached": False
    }
    
    while True:
        user_input = input("\nKhách hàng: ")
        if user_input.lower() in ["exit", "quit", "thoát"]:
            print("Cảm ơn bạn đã sử dụng dịch vụ. Tạm biệt!")
            break
            
        state["messages"].append(HumanMessage(content=user_input))
        state = app.invoke(state)
        
        final_response = state["messages"][-1].content
        print(f"NEO 2.0: {final_response}")
        
        if state.get("is_cached"):
            print("(Phản hồi từ Cache)")