from utils import get_fares

def search_fares(departure: str, arrival: str, cabin_class: str = None):
    """
    NHIỆM VỤ CỦA LY:
    - Lọc danh sách giá vé theo điểm xuất phát (departure) và điểm đến (arrival).
    - Nếu có hạng ghế (cabin_class), lọc đúng hạng ghế đó.
    - Trả về các option kèm giá tiền và trạng thái còn chỗ (is_available).
    """
    fares = get_fares()
    # TODO: Ly thực hiện logic tìm kiếm và sắp xếp giá ở đây
    return fares # Placeholder
