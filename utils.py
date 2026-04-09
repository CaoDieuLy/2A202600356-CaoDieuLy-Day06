import json
import os

def load_data(file_path="flight_ticket_fare_data.json"):
    """Đọc dữ liệu từ file JSON."""
    if not os.path.exists(file_path):
        # Fallback for different directory structures if needed
        file_path = os.path.join(os.path.dirname(__file__), file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_flights():
    return load_data().get("flights", [])

def get_tickets():
    return load_data().get("tickets", [])

def get_fares():
    return load_data().get("fares", [])

def get_baggage_rules():
    return load_data().get("baggage_rules", [])
