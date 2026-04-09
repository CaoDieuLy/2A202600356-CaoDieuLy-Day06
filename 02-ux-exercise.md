# Bài tập UX: phân tích sản phẩm AI thật

**Thời gian:** 40 phút | **Cá nhân** | **Output:** sketch giấy, nộp cuối bài

---

## Chọn sản phẩm

| Sản phẩm | AI feature | Truy cập |
|----------|-----------|---------|
| ☑️ Vietnam Airlines — Chatbot NEO | Chatbot hỗ trợ khách hàng, tra cứu chuyến bay | vietnamairlines.com hoặc Zalo VNA |

---

## Phần 1 — Khám phá (15 phút)

> **Marketing & PR:** Chatbot NEO quảng bá là Trợ lý ảo AI 24/7, hỗ trợ hành khách ngay lập tức mọi lúc mọi nơi. Mục tiêu là giúp khách hàng giải quyết nhanh chóng các tác vụ như: tra cứu quy định hành lý, lịch bay, và hỗ trợ tài khoản Lotusmiles. Nhấn mạnh vào việc giảm thời gian chờ đợi thay vì phải gọi tổng đài.

> **Trải nghiệm dùng thử:**
> - **Giao diện & UI:** UI thân thiện, AI chủ động chào hỏi .
> - **Tương tác:** Tốc độ phản hồi cực kỳ nhanh. Nếu nhập từ khoá ngắn/chuẩn thì luồng hội thoại đi rất mượt, nhưng nếu nhập câu quá phức tạp thì hệ thống thường bị bế tắc và chuyển hướng ép người dùng dùng menu có sẵn.

## Phần 2 — Phân tích 4 paths (10 phút)

Dùng framework 4 paths để mổ xẻ sản phẩm:

| Path | Câu hỏi | Trả lời phân tích |
|------|---------|-------------------|
| 1. Khi AI **đúng** | Kích thước hành lý ký gửi tối đa là bao nhiêu? | Bot trả lời ngay lập tức, đầy đủ thông tin, kèm thông tin bonus. |
| 2. Khi AI **không chắc** | Tìm chuyến bay từ Hà Nội vào Hồ Chí Minh vào ngày hôm nay | Hệ thống đợi 1 lúc, sau đó hiển thị các lựa chọn cần tra cứu thêm. |
| 3. Khi AI **sai** | Phí hoàn lại vé là bao nhiêu? | Câu hỏi tra cứu thông tin mà hệ thống lại trả về nâng hạng vé, sau đó tôi phải tìm thủ công |
| 4. Khi user **mất tin** | Giá vé rẻ nhất ngày mai | Đưa ra thông tin về hotline, email, khiến người dùng bất lực|

**Tự phân tích:**
- **Path nào sản phẩm xử lý tốt nhất? Tại sao?** Path 1 (Khi AI đúng). Đặc biệt xử lý xuất sắc ở các câu hỏi mang tính quy định tĩnh (Chính sách hành lý, luật check-in). Lý do vì VNA chuẩn bị kho dữ liệu FAQ rất chi tiết và chuyển hoá nó thành các block text dễ đọc tích hợp sẵn trong kịch bản.
- **Path nào yếu nhất hoặc không tồn tại?** Path 3 (Khi AI sai). Engine xử lý của NEO có xu hướng "tự tin thái quá". Khi nó bắt được 1 từ khoá quen thuộc trong một câu hỏi rất phức tạp, nó sẽ đẩy ra luồng thông tin rập khuôn thay vì dùng kỹ thuật xác nhận ý định (Did you mean...?).
- **Kỳ vọng từ marketing khớp thực tế không? Gap ở đâu?** Có tồn tại gap. Marketing khiến user kỳ vọng đây là một AI linh hoạt giống Generative AI (kiểu ChatGPT). Nhưng thực tế NEO thiên về hệ thống truy xuất thông tin truyền thống (Intent-matching / Rule-based). Khi đối mặt với ngữ cảnh rắc rối, AI của NEO sẽ bộc lộ khuyết điểm.

## Phần 3 — Sketch "làm tốt hơn" (10 phút)



**Chuyển hoá Sketch sang mô tả Text (nội dung để vẽ lên giấy nháp):**

> **Tình huống Giả định:** User gõ câu hỏi: *"Hôm qua tôi mua vé bay chuyến vn245 hạng Economy Lite số vé 12345678 giờ muốn huỷ để mua vé mới thì có được hoàn tiền không?"*

- **As-is (bên trái):** user journey hiện tại → đánh dấu chỗ gãy
  - **User:** (Gõ câu hỏi trên).
  - **Bot:** (Bắt nhầm từ khóa "mua vé" hoặc "hạng vé") trả lời: *"Bạn muốn tìm hiểu về hạng vé. Vui lòng chọn..."* [Hạng Thương gia] [Hạng Phổ thông].
  - ❌ **Chỗ gãy:** User ức chế vì câu hỏi là hoàn tiền nhưng lại tư vấn hạng vé. User phải mò mẫm qua tận menu chính để tìm đúng luồng Hoàn tiền/Gặp nhân viên.

- **To-be (bên phải):** user journey đề xuất → vẽ kế bên
  - **User:** (Gõ câu hỏi trên).
  - **Bot:** (Hệ thống phát hiện Confidence score rất thấp, kích hoạt kỹ thuật Intent Confirmation). *"Dường như bạn muốn hỏi về **Quy định hoàn tiền đối với hạng Phổ thông siêu tiết kiệm (Economy Lite)** đúng không?"*
    - 👉 Nút 01: `[Đúng, hãy tư vấn cho tôi]` -> Trả lời thẳng vấn đề.
    - 👉 Nút 02: `[Không, tôi muốn hỏi cái khác]` -> Cho phép gặp trực tiếp nhân viên ngay.

- **Ghi rõ: thêm gì? Bớt gì? Đổi gì?**
  - **Thêm:** Bước xác nhận lại ý định (Intent Confirmation) đóng vai trò như một màng lọc khi độ tin cậy của AI không đạt mức an toàn.
  - **Bớt:** Bớt hành vi "rập khuôn" ép user phải tự lội ngược dòng trong hàng tá options không liên quan ở Fallback menu.
  - **Đổi:** Chuyển UX thiết kế từ tâm thế "Phỏng đoán mù" sang "Hợp tác đa chiều cùng user để làm sáng tỏ thông tin".

## Phần 4 — Share + vote (5 phút)

Chia sẻ sketch với nhóm. Mỗi người trình bày ngắn (30 giây). Nhóm vote sketch hay nhất → **bonus điểm**.

---

## Nộp bài

Mỗi người nộp sketch giấy + ghi chú phân tích 4 paths. Đây là **điểm cá nhân**.

**Nice to have:** screenshot màn hình app + annotate (khoanh, ghi chú) chỗ hay / chỗ gãy. Nộp kèm sketch.

---

## Tiêu chí chấm (10 điểm + bonus)

| Tiêu chí | Điểm |
|----------|------|
| Phân tích 4 paths đủ + nhận xét path yếu nhất | 4 |
| Sketch as-is + to-be rõ ràng | 4 |
| Nhận xét gap marketing vs thực tế | 2 |
| **Bonus:** nhóm vote sketch hay nhất | +bonus |

---

*Bài tập UX — Ngày 5 — VinUni A20 — AI Thực Chiến · 2026*
