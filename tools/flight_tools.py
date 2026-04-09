from utils import get_flights

def get_flight_info(flight_code: str, date: str = None):
    """
    NHIỆM VỤ CỦA CAO:
    - Lọc danh sách chuyến bay dựa trên flight_code.
    - Nếu có date, lọc thêm theo ngày (scheduled_departure).
    - Trả về thông tin chi tiết: Giờ đi, giờ đến, trạng thái.
    """
    flights = get_flights()
    # TODO: Cao thực hiện logic lọc dữ liệu ở đây
    results = [f for f in flights if f["flight_code"] == flight_code]
    return results
