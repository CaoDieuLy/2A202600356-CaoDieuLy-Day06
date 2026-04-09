from utils import get_baggage_rules

def get_baggage_policy(cabin_class: str, baggage_type: str = "checked" ) -> dict:
    """
    Truy vấn quy định hành lý dựa trên hạng ghế (Economy/Business) và loại hành lý.
    """
    rules = get_baggage_rules()
    
    # Chuẩn hóa input
    if not cabin_class:
        return {"error": "Thiếu thông tin hạng ghế (cabin_class)."}
        
    for rule in rules:
        if rule.get("cabin_class") == cabin_class and rule.get("type") == baggage_type:
            return {
                "status": "success",
                "cabin_class": cabin_class,
                "baggage_type": baggage_type,
                "pieces": rule.get("pieces"),
                "total_weight_kg": rule.get("weight_kg"),
                "max_weight_per_piece_kg": rule.get("max_weight_per_piece_kg"),
                "max_dimensions_cm": rule.get("max_dimensions_cm")
            }
            
    return {"status": "error", "message": f"Không tìm thấy quy định hành lý cho hạng {cabin_class} (loại: {baggage_type})."}
