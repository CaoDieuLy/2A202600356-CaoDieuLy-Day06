# Kế Hoạch Dự Án Chatbot Hàng Không (NEO 2.0)

## 1. Giới thiệu
Dự án **NEO 2.0** là phiên bản cải tiến của chatbot hỗ trợ khách hàng Vietnam Airlines. Mục tiêu chính là cung cấp trải nghiệm tra cứu thông tin hàng không nhanh chóng, chính xác thông qua giao tiếp ngôn ngữ tự nhiên.

- **Công nghệ chính:**
    - **LangGraph:** Quản lý luồng hội thoại dưới dạng Graph.
    - **OpenAI (GPT-4o-mini):** Trích xuất thông tin thực thể (Entity Extraction) và sinh phản hồi.
    - **Python:** Xử lý logic nghiệp vụ và truy vấn dữ liệu JSON.
- **Dữ liệu nguồn:** `flight_ticket_fare_data.json` - Chứa thông tin về chuyến bay, vé, giá vé và quy định hành lý.

## 2. Phân Công Nhiệm Vụ

| Thành viên | Tính năng phụ trách | File đảm nhận | Nhiệm vụ cụ thể | Timeline |
| :--- | :--- | :--- | :--- | :--- |
| **Cao** | Feature 1: Thông tin chuyến bay | `tools/flight_tools.py` | - Viết hàm `get_flight_info` để lọc dữ liệu từ `flights`. <br> - Xử lý các query về trạng thái/giờ bay. | Ngày 1-3 |
| **Nam** | Feature 2: Thông tin vé | `tools/ticket_tools.py` | - Viết hàm `get_ticket_details` tra cứu theo mã vé/tên khách. <br> - Đảm bảo bảo mật thông tin cá nhân. | Ngày 1-3 |
| **Ly** | Feature 3: Tìm kiếm giá vé | `tools/fare_tools.py` | - Viết hàm `search_fares` tìm kiếm theo chặng bay/ngày. <br> - Sắp xếp giá vé từ thấp đến cao. | Ngày 2-4 |
| **Tuấn** | Feature 4: Thông tin hành lý | `tools/baggage_tools.py` | - Viết hàm `get_baggage_policy` theo hạng vé (Economy/Business). <br> - Trả về cân nặng/kích thước chi tiết. | Ngày 2-4 |

## 3. Quy Trình Phát Triển Chung (Development Workflow)

Để hoàn thành dự án, mỗi thành viên cần thực hiện đúng quy trình sau:
1. **Bước 1: Trích xuất (LLM Extraction):** Sử dụng LLM để parse input người dùng thành JSON schema. (Cần chỉnh sửa prompt trong `prompts/`).
2. **Bước 2: Truy vấn (Python Tool):** Sử dụng các hàm trong thư mục `tools/` để lấy dữ liệu thực tế từ JSON.
3. **Bước 3: Tích hợp (LangGraph):** Đưa các hàm tool vào LangGraph node trong `main.py`.
4. **Bước 4: Phản hồi:** Dùng LLM để chuyển dữ liệu thô từ JSON thành câu trả lời thân thiện.

## 4. Kiểm Thử và Triển Khai

- **Yêu cầu Kiểm thử:** 
    - Mỗi thành viên chạy file tool của mình một cách độc lập để đảm bảo kết quả JSON trả về đúng.
    - Kiểm tra các trường hợp biên (không tìm thấy chuyến bay, sai định dạng mã vé).
- **Tiêu chí hoàn thành (Definition of Done):** 
    - Chatbot trả lời đúng thông tin trong vòng < 5 giây.
    - Không xảy ra lỗi loop hội thoại.
    - Thông tin trả về khớp 100% với file `flight_ticket_fare_data.json`.

## 5. Tài Liệu Tham Khảo

- **Spec dự án:** [spec-draft.md](file:///home/namdv/workspace/Day06-AI-Product-Hackathon/spec-draft.md)
- **Cấu trúc dữ liệu:** [flight_ticket_fare_data.json](file:///home/namdv/workspace/Day06-AI-Product-Hackathon/flight_ticket_fare_data.json)
- **Mã nguồn cơ sở:** Được khởi tạo tại thư mục gốc.
