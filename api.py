from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from main import app as graph_app  # Lấy biểu đồ Graph đã compile từ main.py

app = FastAPI(title="VNA AI Assistant API")

# Cấu hình CORS để Next.js (port 3000) có thể gọi được API port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # Khởi tạo state với tin nhắn của user
    initial_state = {"messages": [HumanMessage(content=request.message)]}
    
    try:
        # Chạy workflow thông qua LangGraph
        # Vì main.py sử dụng checkpointer (MemorySaver) nên phải truyền config thread_id vào để LangGraph lưu lịch sử
        config = {"configurable": {"thread_id": "front_end_session_1"}}
        final_state = graph_app.invoke(initial_state, config)
        
        # Tin nhắn cuối cùng trong state là câu trả lời của AI
        response_msg = final_state["messages"][-1].content
        return {"response": response_msg}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
