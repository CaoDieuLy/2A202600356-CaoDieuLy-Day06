from utils import get_baggage_rules

def get_baggage_policy(cabin_class: str, baggage_type: str = "checked"):
    """
    NHIỆM VỤ CỦA TUẤN:
    - Truy vấn quy định hành lý dựa trên hạng ghế (Economy/Business).
    - baggage_type có thể là 'checked' (ký gửi) hoặc 'carry_on' (xách tay).
    - Trả về: Trọng lượng tối đa, số kiện, kích thước.
    """
    rules = get_baggage_rules()
    # TODO: Tuấn thực hiện logic lọc quy định ở đây
    for rule in rules:
        if rule["cabin_class"] == cabin_class and rule["type"] == baggage_type:
            return rule
    return None
