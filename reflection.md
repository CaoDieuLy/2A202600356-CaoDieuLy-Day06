# 🪞 Reflection — Thành viên: Ly

**Dự án:** NEO 2.0 — Vietnam Airlines AI Assistant  
**Nhóm:** Nhóm 21-403  
**Vai trò:** Feature 3 Developer · Prompt Engineer · QA  
**Ngày:** 09/04/2026

---

## 1. Phần việc đã thực hiện

### 1.1. Feature 3 — Tra cứu giá vé (`search_fares`)

Tôi chịu trách nhiệm xây dựng tính năng **Tìm kiếm giá vé** (`fare_search`) — một trong 4 core features của chatbot NEO 2.0. Cụ thể, tôi đã phát triển hàm `search_fares()` trong file `tools/fare_tools.py` với các khả năng:

- **Cross-reference 2 bảng dữ liệu:** Đây là thách thức lớn nhất của Feature 3. Bảng `fares` trong JSON không hề chứa thông tin điểm đi/điểm đến — chỉ có `flight_code`. Vì vậy, tôi phải thiết kế logic lọc theo 2 bước: **(1)** Duyệt bảng `flights` để tìm tập hợp `flight_code` khớp với cặp sân bay đi/đến, **(2)** Dùng tập hợp đó để lọc tiếp bảng `fares` và trả kết quả giá vé.
- **Lọc đa điều kiện:** Hỗ trợ lọc theo ngày bay (`date`), hạng ghế (`cabin_class`), buổi bay (`time_of_day`: sáng/chiều/tối), và chế độ "rẻ nhất" (`cheapest_only`).
- **Normalize dữ liệu đầu vào:** Xử lý format ngày kiểu Việt Nam (`10/4` → `04-10`), so khớp case-insensitive cho tên sân bay, và map tiếng Việt sang tiếng Anh cho hạng vé (`Thương gia` → `Business`).
- **Cơ chế bảo vệ (Guard Clause):** Thêm lớp bảo vệ ngay đầu hàm — nếu thiếu `departure` hoặc `arrival` thì trả `[]` ngay lập tức, ngăn AI lấy rác từ toàn bộ cơ sở dữ liệu khi bị thiếu thông tin cốt lõi.
- **Sắp xếp kết quả:** Tự động sắp xếp danh sách vé theo giá từ rẻ → đắt, giới hạn trả về tối đa 5 kết quả để tránh quá tải thông tin cho khách hàng.

### 1.2. Cập nhật Prompts (Prompt Engineering)

Ngoài Feature 3, tôi còn phụ trách **cập nhật và tinh chỉnh toàn bộ hệ thống Prompt** trong thư mục `prompts/`, bao gồm:

- **`extraction_prompt.txt`** — Prompt trích xuất ý định (Intent Classification & Entity Extraction):
  - Thiết kế cấu trúc ROLE → TASK → CONTEXT → EXTRACTION RULES → FEW-SHOT EXAMPLES → OUTPUT FORMAT.
  - Bổ sung quy tắc xử lý input ngắn (chuỗi số → `ticket_info`, chuỗi "VNxxx" → `flight_info`).
  - Thêm quy tắc Date Resolution để AI hiểu "hôm nay", "ngày mai", "hôm đó" dựa theo context.
  - Định nghĩa rõ output JSON schema với tất cả entity fields (`flight_code`, `ticket_number`, `departure`, `arrival`, `date`, `time_of_day`, `cheapest_only`, `cabin_class`, `baggage_type`).

- **`response_prompt.txt`** — Prompt phản hồi tổng quát (Response Generation):
  - Thiết lập quy tắc chuyển đổi dữ liệu thô JSON → văn xuôi tiếng Việt tự nhiên.
  - Thêm quy tắc quan trọng: khi khách hỏi "rẻ nhất" → BẮT BUỘC chỉ trả 1 kết quả, CẤM liệt kê các chuyến khác.
  - Bổ sung hướng dẫn xử lý khi thiếu thông tin hoặc không tìm thấy dữ liệu cho từng intent cụ thể.


### 1.3. Thiết kế Test Cases & Kiểm thử

Tôi đảm nhiệm vai trò **QA** — thiết kế kịch bản kiểm thử cho toàn bộ team:

- **`test_case.md`** — Bộ test cases tổng hợp cho cả 4 features:
  - Feature 1: Happy path, xử lý ngữ cảnh "hôm đó" (relative date/memory), sai mã chuyến bay (pre-check lỗi).
  - Feature 2: Slot-filling (thiếu ngày bay → hỏi lại), bổ sung thông tin, bộ lọc đa điều kiện phức tạp.
  - Feature 3: Từ chối tra vé theo tên (bảo mật), luồng chuẩn bằng mã vé.
  - Feature 4: Hỏi chung chung (Economy), hỏi cụ thể (Business carry-on).

- **`test_ly.py`** — Script kiểm thử tự động multi-turn conversation cho feature 3 (5 lượt):
  - Lượt 1: Tìm giá vé thiếu ngày → kiểm tra Slot-Filling có hoạt động không.
  - Lượt 2: Bổ sung ngày + hạng Economy → kiểm tra kết hợp context.
  - Lượt 3: Follow-up hỏi hạng Thương gia "hôm đó" → kiểm tra Memory (persistent slots).
  - Lượt 4: Hỏi chuyến rẻ nhất → kiểm tra `cheapest_only`.
  - Lượt 5: Lọc buổi chiều → kiểm tra `time_of_day` filter.

---

## 2. Bài học rút ra

### 2.1. Kỹ thuật
- **Cross-reference dữ liệu là kỹ năng quan trọng:** Khi database không được thiết kế tối ưu (bảng `fares` thiếu trường đi/đến), developer phải tự thiết kế logic nối bảng. Đây là bài học thực tế về Data Engineering mà tôi không lường trước.
- **Prompt Engineering là "nghệ thuật":** Một prompt tốt phải cân bằng giữa việc cho AI đủ context (không thiếu) nhưng cũng không quá dài (gây hallucination). Việc thêm Few-Shot Examples và rõ ràng Output Format đã cải thiện đáng kể độ chính xác của extraction.
- **Guard Clause cứu mạng:** Ban đầu tôi không có dòng kiểm tra `if not departure or not arrival: return []`, khiến AI có lúc gọi `search_fares()` với tham số rỗng và trả về toàn bộ database — gây trải nghiệm rất tệ. Bài học: luôn validate input trước khi xử lý.

### 2.2. Làm việc nhóm
- **Phân chia feature độc lập rất hiệu quả:** Mỗi người viết 1 file tool riêng (`fare_tools.py`, `flight_tools.py`,...), sau đó tích hợp vào `main.py` một cách gọn gàng. Kiến trúc module hóa giúp giảm xung đột code.
- **Test cases phải viết từ sớm:** Khi tôi viết `test_case.md` trước, cả nhóm có chung "tiêu chuẩn đầu ra" để hướng tới. Điều này giúp tiết kiệm thời gian debug rất nhiều so với việc test thủ công không có kịch bản.

### 2.3. Sản phẩm AI
- **Slot-Filling là linh hồn của chatbot:** Nếu AI cứ cố trả lời khi chưa đủ thông tin, kết quả sẽ sai. Cách tiếp cận đúng là: thiếu slot → hỏi lại khách hàng → nhận đủ → mới truy vấn. Điều này thể hiện triết lý **Precision > Recall** của dự án.
- **Context Memory phức tạp hơn tưởng tượng:** Xử lý "hôm đó", "ngày mai" đòi hỏi bơm timestamp thực vào system prompt và để AI tự tham chiếu lịch sử hội thoại. Đây là phần tốn nhiều thời gian tinh chỉnh nhất.

---

## 3. Khó khăn gặp phải & Cách giải quyết

| Khó khăn | Cách giải quyết |
|-----------|----------------|
| Bảng `fares` không chứa điểm đi/đến, chỉ có `flight_code` | Thiết kế logic 2 bước: lọc `flights` → lấy tập `flight_code` → match sang `fares` |
| Ngày tháng format không thống nhất (10/4 vs 2026-04-10) | Viết hàm normalize: tách chuỗi "10/4" → "04-10" rồi so khớp substring |
| AI trả toàn bộ DB khi thiếu tham số | Thêm Guard Clause đầu hàm + SYSTEM_NOTE trong `main.py` buộc hỏi lại |
| Prompt ban đầu quá chung chung, AI bóc sai intent | Tái cấu trúc prompt theo ROLE-TASK-CONTEXT-RULES, bổ sung Few-Shot Examples |
| Khách nói "Thương gia" nhưng DB lưu "Business" | Thêm mapping Việt-Anh trong logic lọc `cabin_class` |

---

## 4. Nếu được làm lại, tôi sẽ thay đổi gì?

1. **Viết Unit Test trước khi code (TDD):** Thay vì code xong mới viết test, tôi sẽ định nghĩa test cases trước để có hướng phát triển rõ ràng hơn.
2. **Tách Prompt thành nhiều file hơn:** Mỗi feature nên có prompt riêng (giống `feature1_prompt.txt` cho Feature 1), thay vì dùng chung `response_prompt.txt` cho Feature 2, 3, 4.
3. **Thêm Error Logging chi tiết:** Hiện tại khi hàm lỗi chỉ return `[]` hoặc chuỗi rỗng — rất khó debug. Nên thêm logging với severity level.
4. **Tối ưu hiệu suất truy vấn:** Hiện tại duyệt toàn bộ mảng `flights` mỗi lần gọi. Nếu dữ liệu lớn, nên build index hoặc dùng dictionary lookup.

---

## 5. Đánh giá tổng thể

Dự án NEO 2.0 đã đạt được mục tiêu ban đầu: xây dựng một chatbot hàng không **end-to-end** (Option C) với kiến trúc LangGraph, hỗ trợ 4 tính năng chính, có giao diện Next.js hiện đại, và khả năng Slot-Filling thông minh. Phần việc của tôi (Feature 3 + Prompts + Test Cases) đã đóng góp vào cả 3 trụ cột của sản phẩm: **tính năng nghiệp vụ**, **chất lượng AI**, và **đảm bảo chất lượng**.

Trải nghiệm hackathon này giúp tôi hiểu sâu hơn về cách xây dựng một sản phẩm AI thực chiến — không chỉ là viết code, mà còn là thiết kế prompt, quản lý context, xử lý edge cases, và làm việc nhóm hiệu quả dưới áp lực thời gian.
