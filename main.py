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
from datetime import datetime

load_dotenv()

# Khởi tạo LLM với OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def load_prompt(file_name: str) -> str:
    """Đặc tả: Load prompt từ thư mục prompts/."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", file_name)
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Pydantic struct cho Extraction Node (GIÚP TRÍCH XUẤT CHUẨN 100%)
class Entities(BaseModel):
    flight_code: Optional[str] = Field(default=None, description="Mã chuyến bay, ví dụ VN123")
    ticket_number: Optional[str] = Field(default=None)
    departure: Optional[str] = Field(default=None)
    arrival: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None, description="Ngày khởi hành định dạng YYYY-MM-DD")
    cabin_class: Optional[str] = Field(default=None)
    baggage_type: Optional[str] = Field(default=None)

class ExtractionResult(BaseModel):
    intent: str = Field(description="general, flight_info, ticket_info, fare_search, hoặc baggage_info")
    entities: Entities

def manage_memory_and_cache(state: AgentState):
    """Giữ lượt chat gần nhất và kiểm tra Cache."""
    messages = state["messages"]
    
    if len(messages) > 10:
        messages = messages[-10:]
    
    # Kiểm tra Cache để trả lời ngay nếu câu hỏi trùng lặp
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
    """Node phân loại ý định và trích xuất thực thể dùng Structured Output."""
    if state.get("is_cached"):
        return state

    sys_prompt = load_prompt("extraction_prompt.txt")
    if not sys_prompt:
        sys_prompt = "Bạn là trợ lý ảo trích xuất thông tin."

    # Bơm Context thời gian thực để xử lý "ngày mai", "hôm qua"
    today = datetime.now().strftime('%Y-%m-%d')
    sys_prompt += f"\n\nLưu ý Context quan trọng:\n- Hôm nay là: {today}\n- Nếu khách nói 'hôm đó', hãy tìm trong lịch sử chat xem họ đã nhắc đến ngày nào gần nhất."
    
    structured_llm = llm.with_structured_output(ExtractionResult)
    
    try:
        # Pass toàn bộ lịch sử trò chuyện để AI tự nhớ Context (Ví dụ khách nói VN123 từ trước)
        messages_to_pass = [SystemMessage(content=sys_prompt)] + state["messages"]
        result = structured_llm.invoke(messages_to_pass)
        
        intent = result.intent
        extracted_data = result.entities.model_dump()
    except Exception as e:
        intent = "general"
        extracted_data = {}

    return {"current_intent": intent, "extracted_data": extracted_data}

def tool_node(state: AgentState):
    """Node gọi hàm Python truy vấn dữ liệu thực tế."""
    if state.get("is_cached"):
        return state

    intent = state.get("current_intent")
    entities = state.get("extracted_data", {})
    query_results = "Không nhận diện được yêu cầu phù hợp."
    
    if intent == "flight_info":
        f_code = entities.get("flight_code")
        f_date = entities.get("date")
        
        if not f_code:
            query_results = "SYSTEM_NOTE: Vui lòng yêu cầu khách hàng cung cấp mã chuyến bay."
        else:
            # PRE-CHECK: Kiểm tra mã chuyến bay có tồn tại không trước khi hỏi ngày
            all_flights_for_code = get_flight_info(flight_code=f_code, date=None)
            
            if not all_flights_for_code:
                query_results = f"SYSTEM_NOTE: Mã chuyến bay {f_code} không có trong hệ thống hiện tại, khuyên khách hàng kiểm tra lại mã."
            elif not f_date:
                query_results = f"SYSTEM_NOTE: Mã chuyến {f_code} hợp lệ. Vui lòng hỏi khách hàng họ muốn khởi hành vào ngày nào?"
            else:
                data = get_flight_info(flight_code=f_code, date=f_date)
                query_results = str(data) if data else f"SYSTEM_NOTE: Không tìm thấy chuyến bay {f_code} vào ngày cung cấp. Khuyên khách hàng kiểm tra lại."
            
    elif intent == "ticket_info":
        ticket_num = entities.get("ticket_number")
        if not ticket_num:
            query_results = "SYSTEM_NOTE: Vui lòng yêu cầu khách hàng cung cấp **Mã vé** (ví dụ: 0905262286). Hệ thống không hỗ trợ tra cứu theo họ tên."
        else:
            query_results = get_ticket_details(ticket_number=ticket_num)
    elif intent == "fare_search":
        dep = entities.get("departure")
        arr = entities.get("arrival")
        if not dep or not arr:
            query_results = "SYSTEM_NOTE: Vui lòng hỏi khách hàng điểm đi và điểm đến cụ thể để tìm vé."
        else:
            query_results = search_fares(departure=dep, arrival=arr)
    elif intent == "baggage_info":
        query_results = get_baggage_policy(
            cabin_class=entities.get("cabin_class"),
            baggage_type=entities.get("baggage_type", "checked")
        )
        
    return {"query_results": query_results}

def responder(state: AgentState):
    """Node tạo câu trả lời cuối cùng sạch sẽ, tự nhiên."""
    if state.get("is_cached"):
        return {"messages": [AIMessage(content=state["query_results"])]}

    results = state.get("query_results")
    
    # Định tuyến System Prompt dựa trên INTENT để có chất lượng cao nhất
    if state.get("current_intent") == "flight_info":
        sys_prompt = load_prompt("feature1_prompt.txt")
    else:
        sys_prompt = load_prompt("response_prompt.txt")
        
    if not sys_prompt:
        sys_prompt = "Bạn là trợ lý giải đáp của Vietnam Airlines."

    # FIX LỖI QUAN TRỌNG: Đọc tin nhắn cuối cùng [-1] thay vì tin nhắn đầu [0]
    user_question = state["messages"][-1].content if state["messages"] else ""

    prompt_content = f"Dựa trên dữ liệu sau (hoặc lưu ý từ hệ thống): {results}\nHãy trả lời câu hỏi sau một cách tự nhiên: {user_question}"
    
    response = llm.invoke([
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
    print("--- ✈️ Chatbot Hàng Không (NEO 2.0) đã sẵn sàng! ✈️ ---")
    
    # Thread ID duy nhất để giữ Memory cho phiên làm việc
    config = {"configurable": {"thread_id": "user_session_999"}}
    
    while True:
        user_input = input("\nKhách hàng: ")
        if user_input.lower() in ["exit", "quit", "thoát"]:
            print("Cảm ơn bạn đã sử dụng dịch vụ. Tạm biệt!")
            break
            
        # Chạy Graph (LangGraph sẽ tự động append message vào memory nhờ reducer)
        state = app.invoke({"messages": [HumanMessage(content=user_input)]}, config)
        
        final_response = state["messages"][-1].content
        print(f"NEO 2.0: {final_response}")
        
        if state.get("is_cached"):
            print("(Phản hồi từ Cache)")