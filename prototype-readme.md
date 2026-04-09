# Prototype — NEO 2.0: Chatbot Hỗ trợ Hàng không Vietnam Airlines

## Mô tả
Chatbot NEO 2.0 hỗ trợ hành khách Vietnam Airlines tra cứu thông tin chuyến bay bằng ngôn ngữ tự nhiên. Hành khách nhập mã chuyến bay (VD: VN123) và ngày khởi hành → hệ thống AI trích xuất intent & entities → truy vấn dữ liệu tĩnh → trả kết quả giờ bay, trạng thái, cửa ra máy bay một cách tự nhiên, chuyên nghiệp.

## Level: Working prototype
- Chatbot chạy thật trên Terminal (CLI) với LLM thật (OpenAI `gpt-4o-mini`)
- Luồng AI hoàn chỉnh: User input → LLM trích xuất (Pydantic Structured Output) → Python tool truy vấn JSON → LLM sinh câu trả lời tự nhiên tiếng Việt
- Có Memory (MemorySaver) lưu ngữ cảnh hội thoại xuyên suốt phiên chat
- Có Cache tự động phát hiện câu hỏi trùng lặp, tiết kiệm API call
- Có Slot-filling thông minh: thiếu mã bay → hỏi lại; mã sai → báo ngay không cần hỏi ngày

## Links
- **Source code (repo nhóm):** https://github.com/KaitoKidKao/Nhom21-403-Day06
- **Dữ liệu tra cứu:** `flight_ticket_fare_data.json` (10 chuyến bay, 5 vé, 6 mức giá, 4 quy định hành lý)
- **Prompt hệ thống Feature 1:** `prompts/feature1_prompt.txt`

## Tools & Công nghệ
| Công nghệ | Vai trò |
|-----------|---------|
| **LangGraph** | Orchestration — điều phối state machine (Memory → Classifier → Tool → Responder) |
| **OpenAI gpt-4o-mini** | LLM — trích xuất intent/entities + sinh câu trả lời tự nhiên |
| **Pydantic v2** | Schema validation — ép LLM trả JSON chuẩn qua Structured Output |
| **LangChain** | Framework kết nối LLM (ChatOpenAI, SystemMessage, HumanMessage) |
| **Python + JSON** | Data layer — truy vấn dữ liệu tĩnh từ file `flight_ticket_fare_data.json` |
| **python-dotenv** | Bảo mật — quản lý API key qua file `.env` |
| **Antigravity (Gemini)** | Vibe-coding — hỗ trợ thiết kế kiến trúc, viết code, debug và prompt engineering |

## Kiến trúc Pipeline (LangGraph State Machine)

```
User Input
    │
    ▼
┌──────────────────┐
│ memory_and_cache  │  ← Cắt tỉa history (giữ 5 lượt) + kiểm tra cache
└──────┬───────────┘
       │
       ├── cached? ──→ responder (trả ngay, không gọi LLM)
       │
       ▼
┌──────────────────┐
│   classifier      │  ← LLM + Pydantic: trích xuất intent + entities
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│     tools         │  ← Python functions: truy vấn JSON data
└──────┬───────────┘   (Pre-check mã chuyến trước khi yêu cầu ngày)
       │
       ▼
┌──────────────────┐
│   responder       │  ← LLM + feature1_prompt: sinh câu trả lời tiếng Việt
└──────────────────┘
       │
       ▼
   Bot Response
```

## Phân công

| Thành viên | Phần phụ trách | Output |
|-----------|----------------|--------|
| **Cao** | Feature 1: Thông tin chuyến bay - Logic tìm kiếm chuyến bay theo mã chuyến bay và ngày bay | `tools/flight_tools.py` |
| **Nam** | Feature 2: Thông tin vé — Logic tìm kiếm vé theo ticket_number/passenger_name | `tools/ticket_tools.py` |
| **Ly** | Feature 3: Tìm kiếm giá vé — Logic cross-reference bảng flights ↔ fares | `tools/fare_tools.py` |
| **Tuấn** | Feature 4: Thông tin hành lý — Logic tra cứu policy theo hạng ghế | `tools/baggage_tools.py` |

## Demo nhanh (CLI)

```bash
# Cài đặt
pip install -r requirements.txt

# Cấu hình API key
echo "OPENAI_API_KEY=sk-..." > .env

# Chạy chatbot
python main.py
```

**Ví dụ hội thoại thành công:**
```
Khách hàng: Chuyến VN123 ngày 10/4 bay lúc mấy giờ?
NEO 2.0: Xin chào! Chuyến bay VN123 ngày 10/04/2026:
  - Giờ khởi hành: 08:00
  - Giờ hạ cánh: 10:15
  - Tình trạng: Đúng giờ (On Time)
  Bạn cần hỗ trợ thêm gì không?
```

**Ví dụ mã chuyến sai (Pre-check hoạt động):**
```
Khách hàng: Thông tin mã VN99999
NEO 2.0: Xin lỗi, mã chuyến bay VN99999 không có trong hệ thống.
  Vui lòng kiểm tra lại mã chuyến bay, hoặc liên hệ hotline Vietnam Airlines.
```
