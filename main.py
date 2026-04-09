import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage
from state import AgentState
from tools.flight_tools import get_flight_info
from tools.ticket_tools import get_ticket_details
from tools.fare_tools import search_fares
from tools.baggage_tools import get_baggage_policy

load_dotenv()

# Khởi tạo LLM
llm = ChatOpenAI(model="gpt-4o-mini")

def intent_classifier(state: AgentState):
    """Node phân loại ý định người dùng."""
    # TODO: Các thành viên sẽ cải thiện prompt trích xuất thực thể ở đây
    last_message = state["messages"][-1].content
    
    # Logic phân loại mẫu (Simple string matching)
    intent = "general"
    if "chuyến bay" in last_message.lower() or "vn" in last_message.lower():
        intent = "flight_info"
    elif "vé" in last_message.lower() and "giá" not in last_message.lower():
        intent = "ticket_info"
    elif "giá vé" in last_message.lower() or "tìm vé" in last_message.lower():
        intent = "fare_search"
    elif "hành lý" in last_message.lower():
        intent = "baggage_info"
        
    return {"current_intent": intent}

def tool_node(state: AgentState):
    """Node gọi các hàm Python để truy vấn dữ liệu."""
    intent = state.get("current_intent")
    query_results = "Không tìm thấy thông tin phù hợp."
    
    # Giả định dữ liệu đã được trích xuất (Extraction logic sẽ do các thành viên code thêm)
    if intent == "flight_info":
        query_results = get_flight_info(flight_code="VN123") # Placeholder
    elif intent == "ticket_info":
        query_results = get_ticket_details(passenger_name="NGUYEN/DUNG BP") # Placeholder
    elif intent == "fare_search":
        query_results = search_fares(departure="HAN", arrival="SGN") # Placeholder
    elif intent == "baggage_info":
        query_results = get_baggage_policy(cabin_class="Economy") # Placeholder
        
    return {"query_results": query_results}

def responder(state: AgentState):
    """Node tạo câu trả lời cuối cùng."""
    results = state.get("query_results")
    # Sử dụng LLM để biến results thành câu trả lời tự nhiên
    prompt = f"Dựa trên dữ liệu sau: {results}, hãy trả lời câu hỏi của người dùng một cách chuyên nghiệp."
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

# Xây dựng Graph
workflow = StateGraph(AgentState)

workflow.add_node("classifier", intent_classifier)
workflow.add_node("tools", tool_node)
workflow.add_node("responder", responder)

workflow.set_entry_point("classifier")
workflow.add_edge("classifier", "tools")
workflow.add_edge("tools", "responder")
workflow.add_edge("responder", END)

app = workflow.compile()

if __name__ == "__main__":
    print("Chatbot Hàng Không (NEO 2.0) đã sẵn sàng!")
