import os
import json
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage
from state import AgentState
from tools.flight_tools import get_flight_info
from tools.ticket_tools import get_ticket_details
from tools.fare_tools import search_fares
from tools.baggage_tools import get_baggage_policy

load_dotenv()

# Khởi tạo LLM cho việc trích xuất
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY", "not_provided")
)

# Pydantic struct cho Extraction Node
class Entities(BaseModel):
    flight_code: Optional[str] = Field(default=None, description="Mã chuyến bay, ví dụ VN123")
    ticket_number: Optional[str] = Field(default=None)
    passenger_name: Optional[str] = Field(default=None)
    departure: Optional[str] = Field(default=None)
    arrival: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None, description="Ngày khởi hành theo định dạng YYYY-MM-DD")
    cabin_class: Optional[str] = Field(default=None)
    baggage_type: Optional[str] = Field(default=None)

class ExtractionResult(BaseModel):
    intent: str = Field(description="general, flight_info, ticket_info, fare_search, hoặc baggage_info")
    entities: Entities

def read_prompt(file_name):
    """Đọc nội dung file prompt từ thư mục prompts/."""
    full_path = os.path.join("prompts", file_name)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

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
    """Node phân loại ý định người dùng và trích xuất thực thể."""
    if state.get("is_cached"):
        return state

    sys_prompt = read_prompt("extraction_prompt.txt")
    if not sys_prompt:
        sys_prompt = "Bạn là hệ thống Trích xuất."

    # Lấy thông tin ngày hiện tại để làm base time
    from datetime import datetime
    sys_prompt += f"\nLưu ý Context: Hôm nay là {datetime.now().strftime('%Y-%m-%d')}."
    
    structured_llm = llm.with_structured_output(ExtractionResult)
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
        # Pass toàn bộ lịch sử trò chuyện (messages) để AI tự nhớ Context
        messages_to_pass = [SystemMessage(content=sys_prompt)] + state["messages"]
        result = structured_llm.invoke(messages_to_pass)
        
        intent = result.intent
        extracted_data = result.entities.model_dump()
    except Exception as e:
        intent = "general"
        extracted_data = {}

    return {"current_intent": intent, "extracted_data": extracted_data}

def tool_node(state: AgentState):
    """Node gọi các hàm Python để truy vấn dữ liệu thực tế từ Entities trích xuất được."""
    if state.get("is_cached"):
        return state

    intent = state.get("current_intent")
    entities = state.get("extracted_data", {})
    query_results = "Không tìm thấy thông tin phù hợp."
    
    if intent == "flight_info":
        f_code = entities.get("flight_code")
        f_date = entities.get("date")
        
        if not f_code:
            query_results = "SYSTEM_NOTE: Vui lòng yêu cầu khách hàng cung cấp mã chuyến bay."
        else:
            # Tra cứu thử xem mã chuyến bay có tồn tại không kể cả khi chưa có ngày
            all_flights_for_code = get_flight_info(flight_code=f_code, date=None)
            
            if not all_flights_for_code:
                # Nếu không ra data nào, báo ngay lỗi mã sai mà không cần hỏi ngày!
                query_results = f"SYSTEM_NOTE: Mã chuyến bay {f_code} không có trong hệ thống hiện tại, khuyên khách hàng không cần cung cấp ngày mà hãy kiểm tra lại mã."
            elif not f_date:
                # Mã đúng chuẩn, nhưng khách thiếu ngày đi
                query_results = f"SYSTEM_NOTE: Mã chuyến {f_code} hợp lệ. Vui lòng hỏi khách hàng họ muốn khởi hành vào ngày nào?"
            else:
                data = get_flight_info(flight_code=f_code, date=f_date)
                query_results = str(data) if data else f"SYSTEM_NOTE: Không tìm thấy chuyến bay {f_code} theo ngày cung cấp. Khuyên khách hàng kiểm tra lại."
            
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
    
    # Định tuyến System Prompt dựa trên tính năng để tối ưu chất lượng Text
    if state.get("current_intent") == "flight_info":
        sys_prompt = read_prompt("feature1_prompt.txt")
    else:
        sys_prompt = read_prompt("response_prompt.txt")
        
    if not sys_prompt:
        sys_prompt = "Bạn là trợ lý giải đáp của Vietnam Airlines."

    prompt_content = f"Dựa trên dữ liệu sau (hoặc lưu ý điều hướng từ hệ thống): {results}\nHãy đưa ra câu trả lời trực tiếp cho khách hàng một cách tự nhiên dựa trên câu hỏi sau: {state['messages'][-1].content}."
    
    chat_llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=os.environ.get("OPENAI_API_KEY", "not_provided")
    )
    
    response = chat_llm.invoke([
        SystemMessage(content=sys_prompt), 
        HumanMessage(content=prompt_content)
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