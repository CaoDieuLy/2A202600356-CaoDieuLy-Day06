# 🪞 Reflection — Cao Diệu Ly

**Dự án:** NEO 2.0 — Vietnam Airlines AI Assistant  
**Nhóm:** Nhóm 21-403  
**Ngày:** 09/04/2026

---

## 1. Role cụ thể trong nhóm

Trong nhóm 4 người (Cao, Nam, Ly, Tuấn), tôi đảm nhiệm **3 vai trò song song**:

- **Feature 3 Developer:** Chịu trách nhiệm toàn bộ tính năng **Tra cứu giá vé** (`fare_search`) — từ thiết kế logic cross-reference 2 bảng dữ liệu, viết hàm `search_fares()` trong `tools/fare_tools.py`, đến tích hợp vào pipeline LangGraph trong `main.py`.
- **Prompt Engineer:** Phụ trách viết và tinh chỉnh **toàn bộ hệ thống prompt** trong thư mục `prompts/` cho cả 4 features — không chỉ riêng Feature 3 của mình. Đây là phần ảnh hưởng trực tiếp đến chất lượng AI của toàn bộ sản phẩm.
- **QA (Kiểm thử):** Thiết kế bộ test cases (`test_case.md`) cho cả nhóm và viết script test tự động (`test_ly.py`) để kiểm thử luồng multi-turn conversation.

---

## 2. Phần phụ trách cụ thể (đóng góp có output rõ)

### Đóng góp 1: Hàm `search_fares()` — file `tools/fare_tools.py`

Viết hàm tra cứu giá vé **97 dòng** với các khả năng:
- **Cross-reference 2 bảng:** Bảng `fares` không chứa điểm đi/đến — chỉ có `flight_code`. Tôi phải lọc bảng `flights` trước để tìm tập `flight_code` hợp lệ, rồi dùng tập đó match sang bảng `fares`.
- **Lọc đa điều kiện:** Hỗ trợ lọc theo ngày bay, hạng ghế (`Economy`/`Business`), buổi bay (`morning`/`afternoon`/`evening`), và chế độ `cheapest_only`.
- **Normalize dữ liệu:** Xử lý format ngày Việt Nam (`10/4` → `04-10`), case-insensitive matching, mapping tiếng Việt (`Thương gia` → `Business`).
- **Guard Clause:** Nếu thiếu `departure` hoặc `arrival` → trả `[]` ngay, ngăn AI lấy rác toàn bộ database.
- **Sắp xếp:** Tự động sort giá rẻ → đắt, giới hạn tối đa 5 kết quả.

### Đóng góp 2: Hệ thống Prompt — thư mục `prompts/`

Viết và cập nhật **3 file prompt** điều khiển hành vi AI cho toàn bộ chatbot:
- **`extraction_prompt.txt`:** Prompt trích xuất intent + entities theo cấu trúc ROLE → TASK → CONTEXT → RULES → FEW-SHOT → OUTPUT FORMAT. Thêm quy tắc xử lý input ngắn (chuỗi số → `ticket_info`, "VNxxx" → `flight_info`) và Date Resolution ("hôm nay", "ngày mai", "hôm đó").
- **`response_prompt.txt`:** Prompt phản hồi tổng quát — quy tắc chuyển JSON thô → văn xuôi tiếng Việt. Thêm rule: hỏi "rẻ nhất" → BẮT BUỘC chỉ trả 1 kết quả.
- **`feature1_prompt.txt`:** Prompt chuyên biệt cho Feature 1 (chuyến bay) — format bullet points chuẩn, kịch bản xử lý lỗi.

### Đóng góp 3: Bộ Test Cases — `test_case.md` + `test_ly.py`

- **`test_case.md`:** Thiết kế kịch bản kiểm thử cho cả 4 features (7 test cases), bao gồm Happy Path, Slot-Filling, Edge Cases, và Security (từ chối tra vé theo tên).
- **`test_ly.py`:** Script tự động chạy 5 lượt hội thoại liên tiếp cho Feature 3, kiểm tra Slot-Filling → Context Memory → Follow-up → Cheapest Only → Time-of-day Filter.

---

## 3. SPEC — Phần mạnh nhất và yếu nhất

### Phần mạnh nhất: **User Stories — 4 Paths** (Section 2)

Đây là phần SPEC tôi đánh giá cao nhất vì nó **bắt buộc nhóm phải nghĩ trước** 4 kịch bản cho mỗi feature: Happy Path, Low-confidence, Failure, và Correction. Nhờ vậy, khi code Feature 3, tôi đã biết trước:
- Khi AI **đúng**: trả giá + link tra cứu.
- Khi AI **không chắc**: hỏi lại route/ngày bằng quick reply.
- Khi AI **sai**: user sửa điểm đi/đến/ngày.
- Khi user **sửa**: log pattern re-search để cải thiện.

Điều này giúp tôi thiết kế logic Slot-Filling và Guard Clause **có chủ đích** thay vì code xong mới nghĩ edge case.

### Phần yếu nhất: **ROI 3 kịch bản** (Section 5)

Phần ROI có các con số (`3,000 session/ngày`, `$300/tháng`) nhưng hoàn toàn là **giả định order-of-magnitude** — không có cơ sở dữ liệu thực để kiểm chứng. Trong hackathon, chúng tôi không có access vào traffic thật của Vietnam Airlines, nên phần này mang tính "điền cho đủ template" hơn là phân tích có giá trị. Nếu có thời gian, tôi sẽ benchmark bằng cách đo latency thực tế và tính cost API call từ GPT-4o-mini để có con số chính xác hơn.

---

## 4. Đóng góp khác ngoài phần phụ trách chính

Ngoài 3 đóng góp output ở mục 2, tôi còn thực hiện:

- **Debug Slot-Filling cho cả nhóm:** Khi Feature 1 (Cao) bị lỗi AI hỏi ngày cả khi mã chuyến bay sai, tôi phát hiện nguyên nhân (thiếu pre-check) và gợi ý thêm logic kiểm tra mã chuyến bay tồn tại trước khi hỏi ngày trong `main.py` (dòng 109-113).
- **Test prompt cross-feature:** Sau khi viết `extraction_prompt.txt`, tôi test thủ công với các câu hỏi lắt léo cho cả 4 features (ví dụ: "Thế vé chuyến bay hạng thương gia hôm đó giá bao nhiêu?" — câu này chuyển từ Feature 1 sang Feature 3 giữa chừng) để đảm bảo prompt không bóc sai intent.
- **Support tích hợp `main.py`:** Hỗ trợ thiết kế logic `tool_node()` cho Feature 3 trong `main.py` — thêm SYSTEM_NOTE khi thiếu departure/arrival hoặc thiếu date, buộc chatbot hỏi lại thay vì trả kết quả sai.

---

## 5. Một điều học được trong hackathon mà trước đó chưa biết

**Structured Output của LLM (Pydantic + `with_structured_output`) thay đổi hoàn toàn cách làm việc với AI.**

Trước hackathon, tôi nghĩ trích xuất thông tin từ câu hỏi tự nhiên phải dùng regex hoặc NLP truyền thống (tokenize, NER). Nhưng khi sử dụng `llm.with_structured_output(ExtractionResult)` trong `main.py`, LLM tự động trả về object Pydantic đã validate — không cần parse JSON thủ công, không lo format sai. Điều này giúp toàn bộ pipeline **intent → entities → tool call** trở nên cực kỳ gọn gàng và đáng tin cậy. Đây là kỹ thuật tôi chắc chắn sẽ áp dụng lại trong các dự án AI sau này.

---

## 6. Nếu làm lại, tôi sẽ thay đổi gì?

1. **Tách prompt riêng cho từng feature thay vì dùng chung `response_prompt.txt`:** Hiện tại chỉ Feature 1 có prompt riêng (`feature1_prompt.txt`). Feature 2, 3, 4 dùng chung `response_prompt.txt` → AI phản hồi đôi khi không đủ chuyên biệt. Nếu làm lại, tôi sẽ tạo thêm `feature2_prompt.txt`, `feature3_prompt.txt`, `feature4_prompt.txt` với hướng dẫn output format riêng cho từng loại dữ liệu.

2. **Viết Unit Test cho `search_fares()` bằng `pytest` thay vì chỉ test end-to-end:** File `test_ly.py` hiện tại test luồng AI end-to-end (gọi LLM thật → tốn API + chậm). Nếu làm lại, tôi sẽ viết thêm unit test thuần Python cho hàm `search_fares()` — mock data đầu vào, assert kết quả đầu ra — để chạy nhanh và không phụ thuộc API key.

3. **Thêm `time_of_day` và `cheapest_only` vào logic Slot-Filling trong `main.py`:** Hiện tại `tool_node()` chỉ truyền `departure`, `arrival`, `date` cho `search_fares()` mà bỏ sót `time_of_day`, `cabin_class`, `cheapest_only`. Các tham số này tuy đã được extract ở `intent_classifier` nhưng không được forward xuống tool — khiến các bộ lọc nâng cao không hoạt động qua chatbot (chỉ hoạt động khi gọi trực tiếp hàm Python).

---

## 7. AI đã giúp gì? AI sai/mislead ở đâu?

### AI giúp gì ✅

- **Sinh boilerplate code nhanh:** Khi tôi mô tả logic cross-reference 2 bảng, AI (Cursor/Copilot) sinh ra skeleton cho vòng lặp lọc flights + fares khá chính xác, tiết kiệm ~30 phút code thủ công.
- **Viết prompt draft:** AI giúp tạo bản nháp `extraction_prompt.txt` với cấu trúc ROLE-TASK-CONTEXT. Tôi chỉ cần tinh chỉnh rules và thêm few-shot examples cụ thể cho domain hàng không.
- **Gợi ý edge cases:** Khi tôi hỏi "còn case nào cần xử lý?", AI gợi ý thêm việc normalize ngày tháng và mapping tiếng Việt → tiếng Anh cho `cabin_class` — điều tôi chưa nghĩ tới.

### AI sai/mislead ở đâu ❌

- **AI từng xóa Guard Clause:** Trong một lần refactor, AI gợi ý "đơn giản hóa" hàm `search_fares()` và xóa mất dòng `if not departure or not arrival: return []`. Hậu quả: chatbot trả về toàn bộ giá vé trong database khi khách chưa nói điểm đi/đến. Tôi phải debug mất 20 phút mới phát hiện và thêm lại (có kèm comment `# KHÔNG ĐƯỢC XÓA ĐOẠN NÀY LẦN NỮA` ở dòng 10 của `fare_tools.py`).
- **AI hallucinate format ngày:** Khi tôi hỏi cách normalize "10/4", AI ban đầu gợi ý dùng `datetime.strptime()` với format phức tạp — nhưng thực tế data trong JSON chỉ cần so khớp substring đơn giản. Cách của AI tuy "đúng về mặt kỹ thuật" nhưng over-engineering và gây thêm bug khi timezone không khớp.
- **AI không hiểu kiến trúc cross-table:** Khi tôi hỏi "làm sao tìm giá vé theo điểm đi/đến?", AI gợi ý query trực tiếp bảng `fares` theo field `departure` — nhưng field đó **không tồn tại** trong bảng `fares`. Tôi phải tự đọc file JSON, hiểu cấu trúc dữ liệu, rồi tự thiết kế logic 2 bước (flights → fares). Bài học: **AI không đọc data thay mình được — phải tự hiểu dữ liệu trước khi nhờ AI code.**
