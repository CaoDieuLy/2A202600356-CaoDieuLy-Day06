# Kế Hoạch Dự Án Chatbot Hàng Không

## 1. Giới thiệu
Dự án nhằm xây dựng một chatbot hỗ trợ thông tin du lịch hàng không bám sát vào tài liệu đặc tả (spec-draft). Chatbot áp dụng kiến trúc **Agent** với **LangGraph** để làm luồng điều phối, kết hợp với mô hình LLM mạnh mẽ **gpt-4o-mini** thông qua OpenRouter API để tiến hành "Slot-filling" - bóc tách ngôn ngữ tự nhiên từ câu hỏi của khách hàng thành các tham số chuẩn xác. Toàn bộ dữ liệu tra cứu nội bộ được lấy tập trung từ tệp dữ liệu tĩnh `flight_ticket_fare_data.json`.

## 2. Phân Công Nhiệm Vụ

Dự án được bóc tách thành 4 mảng feature độc lập, tương ứng với 4 mũi nhọn phát triển do thành viên nhóm đảm nhiệm. (Timeline gợi ý: 1 tuần/tính năng).

### 2.1. Feature 1: Thông tin chuyến bay (Cao)
- **Nhiệm vụ:** Thiết lập Agent Node để xử lý ý định tra cứu chuyến bay.
- **Trích xuất LLM (Entity Extraction):** Phải huấn luyện để LLM bắt đúng biến `flight_code` (Mã chuyến bay) và `date` (Ngày bay format ISO).
- **Tích hợp Python:** Viết hàm (`get_flight_info`) lấy data từ block `flights` trong file JSON. Xử lý khớp chuỗi in hoa ký tự mã chuyến và kiểm tra tiền tố giờ bay (`scheduled_departure`).

### 2.2. Feature 2: Thông tin vé cá nhân (Nam)
- **Nhiệm vụ:** Triển khai NLU phát hiện & truy vấn vé hành khách bị lạc/cần xem lại.
- **Trích xuất LLM:** Rút trích 2 biến số `ticket_number` (Chuỗi mã số) và `passenger_name` (Tên hành khách).
- **Tích hợp Python:** Viết hàm (`get_ticket_details`) tìm kiếm chéo dữ liệu hành khách trong block `tickets`. Phải setup normalization (chuẩn hóa) khi gõ tên hành khách ra chữ In hoa và loại bỏ format nhiễu mới tìm ra được trong JSON.

### 2.3. Feature 3: Tra cứu giá vé (Ly)
- **Nhiệm vụ:** Xây dựng tính năng tra cứu mức giá để báo lại cho khách.
- **Trích xuất LLM:** Hệ thống bắt buộc phải bóc ra được `departure` (Sân bay đi) và `arrival` (Sân bay đến). Bóc phụ thêm `cabin_class` (Hạng ghế).
- **Tích hợp Python:** Viết hàm (`search_fares`) móc nối dữ liệu 2 chiều. Chú ý: Entity `fares` trong DB không chứa điểm đi/đến. Hàm phải lọc danh sách `flight_code` hợp lệ từ DB `flights` trước, rồi lấy mảng mã chuyến bay đó match tìm dải giá (`price`) ở DB `fares`.

### 2.4. Feature 4: Hỏi đáp hành lý (Tuấn)
- **Nhiệm vụ:** Module trả lời quy định trọng lượng túi xách, ký gửi.
- **Trích xuất LLM:** Bóc tách `cabin_class` (Economy/Business) và phân định `baggage_type` (checked/carry_on).
- **Tích hợp Python:** Viết hàm (`get_baggage_policy`) query từ block `baggage_rules` JSON. Trả về chính xác cân nặng tối đa (`weight_kg`) và bộ quy chuẩn kích thước (`max_dimensions_cm`).

## 3. Quy Trình Phát Triển Chung
Mỗi nhánh tính năng sẽ được tích hợp đúc kết vào bộ xương `main.py` theo chuẩn kiến trúc Pipeline:
1. **Bóc tách Context (LLM Pydantic):** Tại node `Classifier`, cho LLM (gpt-4o-mini) phân loại Intent trúng 1 trong 4 features, đồng thời điền chuẩn hóa đối tượng (Entities Field).
2. **Kiểm duyệt (Condition - Python Rules):** Cầm Entity trích được quăng vào Tool. Nếu Entity bị hổng (Thiếu Slot), đẩy ra **System Note** cảnh cáo và bắt luồng chatbot quay vòng ra câu hỏi ngược lại người dùng. (VD: "Thiếu ngày đi, hãy hỏi hành khách đi ngày nào!").
3. **Phản hồi linh hoạt (Responder Node):** Hàm Tool trả JSON DB cứng ngắc, node Responder sẽ dùng LLM chuyển thể chuỗi text thành câu chăm sóc khách hàng mượt nhất.

## 4. Kiểm Thử và Triển Khai
- **Test Hàm Độc Lập:** Kiểm tra từng hàm Python (Ví dụ: truyền String thủ công cho hàm Ly bắt cross-reference 2 JSON array) trước khi nối vào LangGraph.
- **Kiểm thử Edge Cases:** Nhử các câu hỏi lắt léo với mô hình ngôn ngữ (Như gõ lộn xộn ngày, sai format, điền tên thừa dấu). 
- **Bảo mật & Cấu hình:** Nhất quán gọi file API Key bằng biến môi trường thông qua thư viện `dotenv` từ tệp `.env`. Không đưa file cấu hình này lên Git!

## 5. Tài Liệu Tham Khảo
- Tài liệu Đặc tả/Design Doc: `spec-draft.md`
- Central Database: `flight_ticket_fare_data.json` 
- LangChain & OpenAI Documentation: Function Calling / Structured Output.
