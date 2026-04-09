from main import app
from langchain_core.messages import HumanMessage

def test_ai_flow():
    # Khởi tạo state gốc như trong main.py
    state = {
        "messages": [],
        "extracted_data": {},
        "persistent_slots": {},  # CHÌA KHÓA: Khởi tạo persistent slots
        "query_results": "",
        "current_intent": "general",
        "is_cached": False
    }

    # Cấu hình thread_id cho Checkpointer (bắt buộc khi dùng MemorySaver)
    config = {"configurable": {"thread_id": "test_session_123"}}

    print("=== BẮT ĐẦU TEST LUỒNG TRÍ TUỆ NHÂN TẠO (SLOT FILLING & MEMORY) ===")

    # Lượt 1: Yêu cầu tìm giá vé — thiếu ngày bay
    user_msg_1 = "Tìm giá vé từ Đà Nẵng đi Hà Nội cho tôi"
    print(f"\n🙎‍♂️ [Khách hàng Lượt 1]: {user_msg_1}")
    state["messages"].append(HumanMessage(content=user_msg_1))
    
    state = app.invoke(state, config)
    print(f"🤖 [NEO 2.0 Lượt 1]: {state['messages'][-1].content}")

    # Lượt 2: Cung cấp ngày bay (AI phải tự kết nối ngày + cặp sân bay ở lượt 1)
    user_msg_2 = "Ngày 10/4 nhé, tìm cho tôi vé thường (Economy)"
    print(f"\n🙎‍♂️ [Khách hàng Lượt 2]: {user_msg_2}")
    state["messages"].append(HumanMessage(content=user_msg_2))
    
    state = app.invoke(state, config)
    print(f"🤖 [NEO 2.0 Lượt 2]: {state['messages'][-1].content}")

    # Lượt 3: Tiếp tục hỏi follow-up — khách muốn xem giá vé hạng Thương gia (Business)
    user_msg_3 = "Còn vé hạng Thương gia ngày hôm đó thì giá bao nhiêu?"
    print(f"\n🙎‍♂️ [Khách hàng Lượt 3]: {user_msg_3}")
    state["messages"].append(HumanMessage(content=user_msg_3))
    
    state = app.invoke(state, config)
    print(f"🤖 [NEO 2.0 Lượt 3]: {state['messages'][-1].content}")

    # Lượt 4: Kịch bản tìm giá vé rẻ nhất
    user_msg_4 = "Vậy chốt lại, chuyến bay nào có giá rẻ nhất trong ngày hôm đó vậy?"
    print(f"\n🙎‍♂️ [Khách hàng Lượt 4]: {user_msg_4}")
    state["messages"].append(HumanMessage(content=user_msg_4))
    
    state = app.invoke(state, config)
    print(f"🤖 [NEO 2.0 Lượt 4]: {state['messages'][-1].content}")

    # Lượt 5: Tính năng lọc giờ bay (Buổi chiều)
    user_msg_5 = "Chuyến đi buổi chiều thì sao? Có chuyến nào xuất phát buổi chiều không?"
    print(f"\n🙎‍♂️ [Khách hàng Lượt 5]: {user_msg_5}")
    state["messages"].append(HumanMessage(content=user_msg_5))
    
    state = app.invoke(state, config)
    print(f"🤖 [NEO 2.0 Lượt 5]: {state['messages'][-1].content}")

if __name__ == "__main__":
    test_ai_flow()
