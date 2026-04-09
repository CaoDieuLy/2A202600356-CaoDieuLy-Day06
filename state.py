import operator
from typing import Annotated, List, TypedDict, Union
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Định nghĩa state cho LangGraph workflow."""
    # Danh sách các tin nhắn trong hội thoại
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Các thông tin thực thể trích xuất được
    extracted_data: dict
    
    # Kết quả từ việc truy vấn database/json
    query_results: Union[dict, list, str]
    
    # Trạng thái hiện tại của flow (ví dụ: 'flight_info', 'ticket_info', v.v.)
    current_intent: str
