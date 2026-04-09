from utils import get_fares, get_flights

def search_fares(departure: str, arrival: str, date: str = None, cabin_class: str = None):
    """
    NHIỆM VỤ CỦA LY (HOÀN THÀNH):
    - Tìm kiếm nhanh giá vé và sắp xếp từ rẻ nhất đến đắt nhất
    - Lọc theo điểm khởi hành, điểm đến, ngày bay và hạng ghế (nếu có).
    - Cắt lọc những chuyến bay còn chỗ trống (is_available = True).
    """
    flights = get_flights()
    # Tìm mã các chuyến bay thỏa mãn điểm đi và điểm đến
    matching_flight_codes = set()
    for f in flights:
        # Kiểm tra departure (support cả tên sân bay và mã, vd: "Đà Nẵng" hoặc "DAD")
        if departure:
            departure_lower = departure.lower()
            flight_departure = f.get("departure", "").lower()
            if departure_lower not in flight_departure:
                continue
        
        # Kiểm tra arrival tương tự
        if arrival:
            arrival_lower = arrival.lower()
            flight_arrival = f.get("arrival", "").lower()
            if arrival_lower not in flight_arrival:
                continue
        
        matching_flight_codes.add(f.get("flight_code"))
        
    fares = get_fares()
    results = []
    
    for fare in fares:
        # Bỏ qua những chuyến đã bán hết vé cho hạng này
        if not fare.get("is_available"):
            continue
            
        # Bỏ qua nếu mã chuyến bay không thỏa mãn điểm đi/đến
        if fare.get("flight_code") not in matching_flight_codes:
            continue
            
        # Kiểm tra ngày — support format "10/4" → "2026-04-10" hoặc "2026-04-10T..."
        if date:
            scheduled_dep = fare.get("scheduled_departure", "")
            # Normalize date: "10/4" → "04-10" (so sánh tháng-ngày)
            if "/" in date:
                date_parts = date.split("/")
                if len(date_parts) == 2:
                    normalized_date = f"{date_parts[1]:0>2}-{date_parts[0]:0>2}"
                    if normalized_date not in scheduled_dep.replace("-", "-")[-10:]:
                        continue
            else:
                # Format YYYY-MM-DD hoặc chỉ MM-DD
                if date not in scheduled_dep:
                    continue
            
        # So khớp hạng vé nếu user có yêu cầu cụ thể
        # Support cả "Business", "Thương gia", "Economy" (case-insensitive)
        if cabin_class:
            cabin_class_lower = cabin_class.lower()
            fare_cabin = fare.get("cabin_class", "").lower()
            # Map Việt sang Anh
            if "thương gia" in cabin_class_lower or "business" in cabin_class_lower:
                if "business" not in fare_cabin:
                    continue
            elif cabin_class_lower not in fare_cabin:
                continue
            
        results.append(fare)
        
    # Sắp xếp các lựa chọn theo mức giá từ rẻ nhất đến đắt nhất
    results = sorted(results, key=lambda x: x.get("price", 0))
    
    # Chỉ trả về top 5 để LLM không bị ngập lụt context (token limit)
    return results[:5]
