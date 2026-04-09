from utils import get_flights

def get_flight_info(flight_code: str, date: str = None):
    """
    NHIỆM VỤ CỦA CAO:
    - Lọc danh sách chuyến bay dựa trên flight_code.
    - Nếu có date, lọc thêm theo ngày (scheduled_departure).
    - Trả về thông tin chi tiết: Giờ đi, giờ đến, trạng thái.
    """
    flights = get_flights()
    results = []
    
    # Chuẩn hóa flight_code
    f_code = flight_code.upper().strip() if flight_code else ""
    
    for f in flights:
        if f.get("flight_code", "").upper() == f_code:
            if date:
                # So khớp ngày vì scheduled_departure có format 2026-04-10T08:00:00
                if f.get("scheduled_departure", "").startswith(date):
                    results.append(f)
            else:
                results.append(f)
    return results
