# SPEC — AI Product Hackathon (Vietnam Airlines Chatbot NEO)

**Nhóm:** Cá nhân
**Track:** ☐ VinFast · ☐ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☑ Open (Hàng không)
**Problem statement (1 câu):** Hành khách mất nhiều thời gian tìm kiếm chính sách bay/vé lắt léo hoặc chờ đợi tổng đài viên quá lâu, AI Chatbot NEO giúp trích xuất và giải đáp thông tin tự động 24/7, giảm tải cho nhân viên CSKH.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | *Hành khách VNA cần tra cứu quy định bay, hành lý, đổi vé nhanh mà lười đọc web, ngại chờ tổng đài. AI tóm tắt câu trả lời tức thì.* | *AI tư vấn sai luật -> user có nguy cơ lỡ chuyến/mất tiền phạt. User nhận ra bot trả lời loanh quanh, thoát bot và chuyển sang Live Agent.* | *Cost cực thấp ~$0.001/request (dùng NLP matching). Latency < 1s. Risk: AI hallucinate điều kiện đền bù/hoàn vé.* |

**Automation hay augmentation?** ☐ Automation · ☑ Augmentation
Justify: *Với những nghiệp vụ mang tính thay đổi booking, nhạy cảm liên quan đến tiền bạc (đổi vé, mua thêm dịch vụ), AI chỉ gợi ý luồng thủ tục và mức phí (Augmentation). Người dùng tự thao tác bằng link và xác nhận bước thanh toán cuối cùng.*

**Learning signal:**

1. User correction đi vào đâu? *Log chat hệ thống. Khi user liên tục gõ đi gõ lại 1 câu hỏi hoặc nhấn nút "Gặp nhân viên" ngay sau khi bot vừa phản hồi, session đó được gán cờ lỗi (failure).*
2. Product thu signal gì để biết tốt lên hay tệ đi? *CSAT (chấm sao sau chat 1-5), Deflection Rate (Tỷ lệ phần trăm những ca giải quyết xong tự động mà không cần pass qua Agent).*
3. Data thuộc loại nào? ☑ User-specific · ☑ Domain-specific · ☐ Real-time · ☑ Human-judgment · ☐ Khác: ___
   Có marginal value không? (Model đã biết cái này chưa?) *Có marginal value tuyệt đối. LLM chung trên mạng (như ChatGPT) không có dữ liệu bảng giá/chính sách nội bộ thay đổi liên tục của VNA, cũng như không thể biết mã đặt chỗ PNR của từng cá nhân hành khách để tra cứu đích danh.*

---

## 2. User Stories — 4 paths

### Feature: Trợ lý giải đáp quy định hành lý

**Trigger:** *User lên app/web VNA mở box chat, hỏi: "Tôi mang cái va li 10 kg lên máy bay được không?"*

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | *Bot trả lời đúng quy định hành lý xách tay (7kg or 10kg tuỳ hạng vé). Cung cấp Nút "Mua thêm hành lý". User nhấn có hoặc đóng cửa sổ.* |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *Bot phản hồi: "Có phải bạn muốn hỏi Quy định hành lý xách tay không?". Hiện 2 nút [Hành lý xách tay] / [Hành lý ký gửi] để user làm rõ ý.* |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | *Bot trả lời sai sang chính sách gửi thú cưng. User bực mình gõ từ "Nhân viên" để thoát bot.* |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | *User dùng fallback menu (gặp người thật). Tín hiệu bot giải quyết trượt lưu vào Dataset để team Product retrain lại Intent.* |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision · ☐ Recall
Tại sao? *Đối với các ngành có tính pháp lý rủi ro cao như hàng không, thà bot báo "Tôi không biết, xin nối máy cho nhân viên" (Low recall) còn hơn là "Tự tin bịa ra chính sách sai lệch" (High recall, Low precision) làm khách ra sân bay bị phạt nặng.*
Nếu sai ngược lại thì chuyện gì xảy ra? *Nếu optimize Recall (cố rặn ra câu trả lời dù không chắc) -> Bot tự bịa luật vé. Khách ra sân bay bị bỏ lại, khởi kiện hãng vì tin bot.*

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| *Deflection Rate (Tỉ lệ tự xử lý)* | *≥ 40%* | *< 20% trong 2 tuần (AI quá dốt, đẩy hết việc lại cho human).* |
| *CSAT Score* | *≥ 3.8/5* | *< 3.0/5 trong 1 tháng liên tục.* |
| *Intent Classification Accuracy*| *≥ 85%* | *< 75%* |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | *Khách gõ sai chính tả / ngôn ngữ mạng* | *Bot báo lỗi liên tục, nhãn sai ý.* | *Filter qua module spell check / NLP xử lý từ khoá đa dạng.* |
| 2 | *Hỏi về chính sách mới vừa được VNA đổi sáng nay* | *Bot dùng knowledge cũ ảo giác.* | *Tự động đồng bộ Knowledge Base ngay lập tức qua API.* |
| 3 | *Khách đang bực mình, chửi bậy vào ứng dụng* | *Bot đáp lại "Tôi chưa hiểu" làm khách ức chế thêm.* | *Tích hợp Sentiment Analysis -> chuyển thẳng cho Human Agent có kỹ năng xoa dịu nếu phát hiện tông giọng giận dữ.* |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | *5,000 phiên/ngày, tự động 30%* | *15,000 phiên/ngày, tự động 50%* | *30,000 phiên/ngày, tự động 70%* |
| **Cost** | *$500/tháng* | *$1,200/tháng* | *$2,500/tháng* |
| **Benefit** | *Tiết kiệm 5 CSKH nhân sự* | *Tiết kiệm 15 CSKH, giảm hàng chờ* | *Tiết kiệm 30 CSKH, tăng upsell vé phụ trợ trực tiếp* |
| **Net** | *Dương nhẹ* | *Khả thi* | *Lãi ròng cao* |

**Kill criteria:** *Cost maintain hạ tầng NLP + AI cao hơn chi phí thuê CSKH thật, hoặc Deflection Rate liên tục rớt dưới ngưỡng 15%.*

---

## 6. Mini AI spec (1 trang)

Chatbot NEO là trợ lý ảo giải đáp đa nền tảng (Web/App/Zalo) của Vietnam Airlines. Pain point cốt lõi cần giải quyết là nỗi đau mất thời gian chờ qua mạng tổng đài điện thoại (rất lâu) chỉ để hỏi những quy định cứng ngắc như "số kg hành lý" hay "phí đổi vé máy bay" của hành khách.

Về cấu trúc, là một AI tích hợp trong mảng tài chính-dịch vụ, NEO tuyệt đối thiên về **"Augmentation"**. AI thay vì tự động mở vé ra và thao tác đổi vé trên hệ thống CRS (Automation, rủi ro khổng lồ), nó chỉ đóng vai trò trích xuất luồng thủ tục tài liệu, báo giá và đưa ra các nút tương tác (Quick Links). Người dùng sẽ sử dụng luồng này để tự hoàn tất giao dịch. 

Đạt đến tiêu chí "Trust": Mô hình của NEO phải được optimize **Precision (Độ chuẩn xác)** ở mức tuyệt đối. Nếu AI không tự tin giải quyết, Bot sẽ dùng Fallback Menu: *Xác nhận lại ý định một lần nữa* hoặc *Chuyển thẳng cho chuyên viên*. Thà báo không biết còn hơn nhảm nhí.

Vòng lặp Data Flywheel của hệ thống hoạt động như sau: Khách hàng sử dụng tính năng tra cứu Chatbot -> Khối lượng Chat logs đa dạng giúp hệ thống NLP học được các cách biểu đạt ý định phức tạp của tiếng Việt -> Tinh chỉnh Bot tốt hơn -> Tăng Deflection Rate (Giải quyết tự động lớn hơn) -> Trải nghiệm tốt thúc đẩy khách hàng tìm đến chatbot ở chuyến bay tiếp theo. Signal học lại được focus xác định ngay khi user "Drop off" sang nhân viên báo lỗi hệ thống.
