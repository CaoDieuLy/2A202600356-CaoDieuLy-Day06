from utils import get_tickets

def get_ticket_details(ticket_number: str = None, passenger_name: str = None):
    """
    NHIỆM VỤ CỦA NAM:
    - Tìm kiếm vé dựa trên ticket_number HOẶC passenger_name.
    - Lưu ý: passenger_name có thể cần chuẩn hóa (in hoa, không dấu) để tìm đúng.
    - Trả về thông tin: Mã hiệu chuyến bay, hạng ghế, số ghế, ngày bay.
    """
    tickets = get_tickets()
    # TODO: Nam thực hiện logic tìm kiếm ở đây
    if ticket_number:
        return [t for t in tickets if ticket_number in t.get("ticket_number", [])]
    return []
