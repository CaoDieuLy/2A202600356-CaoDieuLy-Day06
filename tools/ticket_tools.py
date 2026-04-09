from utils import get_tickets

def get_ticket_details(ticket_number: str = None):
    """
    Tìm kiếm vé DỰA TRÊN ticket_number.
    Tuyệt đối không hỗ trợ tìm kiếm vé bằng tên hành khách.
    """
    tickets = get_tickets()
    results = []
    
    if ticket_number:
        # Chuẩn hóa mã vé (loại bỏ khoảng trắng nếu có)
        clean_number = str(ticket_number).strip()
        results = [t for t in tickets if any(clean_number == tn for tn in t.get("ticket_number", []))]
        
    return results
