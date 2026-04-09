# Individual Reflection — Nguyễn Trí Cao (2A202600223)

## 1. Role
**AI Engineer & Feature 1 Lead** — Chịu trách nhiệm chính về kiến trúc hệ thống AI (LangGraph pipeline), thiết kế luồng Slot-filling cho tính năng Tra cứu thông tin chuyến bay, prompt engineering và tích hợp LLM.

## 2. Đóng góp cụ thể
- **Thiết kế & triển khai kiến trúc LangGraph hoàn chỉnh** cho chatbot NEO 2.0: xây dựng state machine 4 node (Memory → Classifier → Tool → Responder) với conditional routing, MemorySaver checkpointer và cache layer.
- **Viết toàn bộ NLU pipeline cho Feature 1 (Thông tin chuyến bay):** Sử dụng Pydantic Structured Output để ép LLM (gpt-4o-mini) trả JSON chuẩn, triển khai logic Pre-check mã chuyến bay (kiểm tra tồn tại trước khi yêu cầu ngày), và Slot-filling thông minh (thiếu slot → hỏi lại đúng thông tin cần).
- **Prompt engineering cho Feature 1:** Soạn `feature1_prompt.txt` với vai trò NEO 2.0 chuyên nghiệp, xử lý cả happy path (trả thông tin chính xác) lẫn error path (mã chuyến không tồn tại → báo lỗi thân thiện, không hỏi vặn thêm).

## 3. SPEC mạnh/yếu
- **Mạnh nhất: Failure modes (Phần 4)** — Nhóm đã xác định được 3 failure mode rất thực tế: (1) user hỏi câu phức hợp nhiều biến số khiến bot bắt sai intent, (2) bot giữ nhầm ngữ cảnh cũ gây loop, (3) policy/giá thay đổi nhưng knowledge base chưa cập nhật. Mỗi failure đều có mitigation cụ thể (slot-filling bắt buộc, session TTL, fallback sang live agent).
- **Yếu nhất: ROI 3 kịch bản (Phần 5)** — 3 kịch bản (conservative/realistic/optimistic) chủ yếu khác nhau ở quy mô session và deflection rate, nhưng assumption về chi phí infrastructure và benefit chưa tách biệt rõ. Ví dụ: conservative nên giới hạn scope chỉ 1-2 feature đơn giản (tra cứu chuyến bay), realistic mở rộng 4 feature, optimistic bao gồm cả upsell. Cần bóc tách assumption rõ hơn để thuyết phục hơn.

## 4. Đóng góp khác
- Hỗ trợ Nam debug logic tìm kiếm vé trong `ticket_tools.py` — đề xuất chuẩn hóa tên hành khách bằng `.upper()` để match với format JSON
- Viết file `plan.md` phân công nhiệm vụ chi tiết cho cả nhóm 4 người, giúp mọi người biết rõ scope và output cần nộp
- Cấu hình bảo mật cho dự án: tạo `.env`, `.env.example`, `.gitignore` để team không lỡ commit API key lên GitHub

## 5. Điều học được
Trước hackathon, mình nghĩ xây chatbot AI chỉ cần gọi LLM và "để nó tự xử lý". Sau khi thực chiến mới nhận ra: **LLM không nên là nguồn chân lý**. Trong domain hàng không, nếu để LLM tự bịa số liệu (hallucination) thì hành khách có thể mất tiền hoặc lỡ chuyến. Kiến trúc hybrid (LLM chỉ làm NLU + sinh văn, data thật từ database) an toàn hơn nhiều. Đặc biệt, kỹ thuật Pre-check (kiểm tra mã chuyến tồn tại trước khi hỏi thêm thông tin) giúp tiết kiệm 1 vòng hội thoại thừa — đây là bài học UX mà chỉ khi code thật mới thấy rõ.

## 6. Nếu làm lại
Sẽ **test prompt sớm hơn từ tối Day 5** thay vì chờ đến buổi sáng Day 6 mới bắt đầu. Cụ thể: nếu có thêm 1 buổi tối để iterate prompt, mình sẽ thử ít nhất 5 biến thể extraction prompt với các edge case (câu hỏi thiếu mã bay, câu hỏi tiếng Việt lẫn tiếng Anh, câu hỏi kết hợp nhiều intent) để chọn ra version tốt nhất. Ngoài ra, sẽ **xây UI Streamlit song song** thay vì chỉ làm CLI — demo trên giao diện chat đẹp hơn sẽ gây ấn tượng mạnh hơn với ban giám khảo.

## 7. AI giúp gì / AI sai gì

**AI giúp:**
- Dùng **Antigravity (Gemini)** để scaffold toàn bộ kiến trúc LangGraph từ đầu — từ việc thiết kế state machine, viết Pydantic schema, đến việc kết nối các node. Tiết kiệm được khoảng 2-3 giờ so với việc đọc docs rồi tự code từ đầu.
- Dùng AI để brainstorm failure modes và edge cases cho Feature 1 — AI gợi ý được case "mã chuyến bay không tồn tại nhưng bot vẫn hỏi ngày" mà nhóm không nghĩ ra ban đầu, dẫn đến việc thiết kế logic Pre-check rất hữu ích.
- AI giúp soạn prompt `feature1_prompt.txt` với tone "NEO 2.0 chuyên nghiệp" — sau 2-3 vòng chỉnh sửa, prompt trả lời mượt hơn nhiều so với prompt viết tay ban đầu.

**AI sai/mislead:**
- Ban đầu AI gợi ý dùng **OpenRouter API** thay vì OpenAI trực tiếp (vì mình có key OpenRouter). Tuy nhiên sau khi nhóm pull code mới từ main, toàn bộ cấu hình bị conflict và phải chuyển lại về OpenAI API. Mất khoảng 20 phút debug lỗi `OPENAI_API_KEY environment variable not set` chỉ vì config bị lẫn lộn giữa 2 provider.
- AI từng tạo ra code với hàm `.dict()` của Pydantic v1 trong khi project dùng Pydantic v2 — gây ra warning deprecation mỗi lần chạy. Bài học: **AI không phải lúc nào cũng biết version thư viện mình đang dùng**, cần kiểm tra kỹ.
- AI gợi ý thêm tính năng Streamlit UI + ticket tools + fare tools vào cùng 1 sprint — scope quá lớn cho thời gian hackathon. Mình phải chủ động cắt scope chỉ làm Feature 1 cho chắc, thay vì làm dàn trải 4 feature dở dang. **AI brainstorm tốt nhưng không biết giới hạn thời gian thực tế.**
