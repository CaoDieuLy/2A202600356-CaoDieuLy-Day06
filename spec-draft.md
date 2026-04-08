# SPEC - AI Product Hackathon

**Nhóm:Nhóm 21-403**

**Track:** ☐ VinFast · ☐ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☑ Open

**Problem statement (1 câu):** Hành khách Vietnam Airlines mất nhiều thời gian tra cứu giá vé, thông tin chuyến bay và các policy áp dụng cho đúng trường hợp của mình; NEO phiên bản cải thiện giúp hiểu câu hỏi tự nhiên tốt hơn, giảm loop/lệch flow và điều hướng user tới đúng thông tin hoặc đúng kênh hỗ trợ nhanh hơn.

> Lưu ý: Đây là SPEC đề xuất cho phiên bản cải thiện của NEO hiện tại, không phải mô tả nguyên trạng chatbot đang chạy.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | ***User chính**: hành khách Vietnam Airlines (nội địa/quốc tế), đặc biệt là người cần tra cứu nhanh trước giờ bay, người không quen website, và hội viên Lotusmiles. <br>**Pain**: phải đi qua nhiều bước (form, filter) để tìm thông tin (giá vé, giờ bay, hành lý), không nhớ chính xác mã chuyến/điều kiện vé, policy khó hiểu và không gắn với hành trình cụ thể, thông tin bị rời rạc. <br>**AI hỗ trợ nâng cao trải nghiệm** bằng 4 core feature: <br>(1) Thông tin chuyến bay: hiểu query → trả giờ + trạng thái;<br>(2) Thông tin vé: xác định user → trả booking cá nhân hóa;<br>(3) Tìm kiếm giá vé: hiểu nhu cầu → đề xuất option phù hợp;<br>(4) Thông tin hành lý: lấy context vé → trả policy chính xác.<br> → **Giá trị cốt lõi**: AI thay thế việc user phải tự hiểu hệ thống bằng cách hiểu ngôn ngữ tự nhiên, kết nối dữ liệu rời rạc và cá nhân hóa câu trả lời → tra cứu 1 bước, nhanh và chính xác hơn.* | *Khi AI sai: <br> (1) Chuyến bay: trả sai chuyến/ngày/trạng thái → user detect ngay vì lệch kế hoạch → sửa bằng nhập lại mã chuyến/ngày hoặc chọn quick reply → system log mismatch để cải thiện mapping intent;<br>(2) Vé: không tìm thấy hoặc trả sai booking → user nhận ra vì không khớp thông tin cá nhân → sửa bằng nhập lại mã booking/email hoặc chọn lại flow “Xem vé của tôi” → system ghi nhận failed retrieval;<br>(3) Giá vé: hiểu sai route/ngày hoặc trả option không phù hợp → user thấy không đúng nhu cầu → sửa bằng chỉnh lại điểm đi/đến/ngày hoặc chọn suggestion → system học từ pattern re-search;<br>(4) Hành lý: trả sai policy (sai hạng vé/route) → user nghi ngờ vì không khớp vé → sửa bằng bổ sung mã vé/hạng vé → system cải thiện mapping policy theo context;<br>→ UI: luôn hiển thị input đã hiểu (route/ngày/booking) để user kiểm tra nhanh + cho sửa trực tiếp (inline edit) + có fallback “gặp nhân viên” khi confidence thấp.* | *Core flow dựa trên database để trả dữ liệu chính xác; AI chỉ dùng để hiểu câu hỏi tự nhiên, parse input và rephrase output cho dễ đọc, không quyết định kết quả mà chỉ đề xuất gợi ý cho người dùng. <br> **Latency** mục tiêu <4–5s, cost thấp vì chỉ gọi LLM cho augmentation, không cho critical path. <br> **Risk chính**: hiểu sai intent, thiếu context, sai policy → xử lý bằng slot filling bắt buộc, inline edit cho user sửa nhanh, và fallback sang human khi confidence thấp.* |

**Automation hay augmentation?** ☐ Automation · ☑ Augmentation

Justify: *Với các truy vấn thông tin cơ bản như giá vé, tình trạng chuyến bay, tra cứu theo mã đặt chỗ, NEO có thể trả lời gần như tự động. Nhưng với các case có nhiều biến số hoặc liên quan giao dịch thật như đổi vé, hoàn vé, thay đổi booking, AI chỉ nên đóng vai trò hướng dẫn luồng xử lý và tóm tắt policy. Quyết định cuối cùng và thao tác xác nhận vẫn thuộc về user hoặc nhân viên hỗ trợ.*

**Learning signal:**

1. User correction đi vào đâu?  
   *Đi vào chat logs và event logs. Các tín hiệu quan trọng gồm: user hỏi lại nhiều lần, đổi cách diễn đạt, bấm `Gặp nhân viên hỗ trợ`, bỏ dở giữa chừng, hoặc bị lặp trong cùng một flow. Các transcript này được gắn cờ để review luồng gãy và intent sai.*

2. Product thu signal gì để biết tốt lên hay tệ đi?  
   *CSAT sau chat, Deflection Rate, tỷ lệ hand-off sang người thật, tỷ lệ re-ask trong cùng session, tỷ lệ loop flow, và tỷ lệ hoàn tất tra cứu thành công.*

3. Data thuộc loại nào? ☑ User-specific · ☑ Domain-specific · ☐ Real-time · ☑ Human-judgment · ☐ Khác: ___  
   Có marginal value không?  
   *Có. Model chung không biết policy nội bộ, giá vé theo thời điểm, logic tra cứu booking cụ thể, hoặc các luồng user thường bị kẹt trong hệ sinh thái Vietnam Airlines. Dữ liệu hội thoại thật giúp xây “data moat” về support flow và error patterns.*

---

## 2. User Stories — 4 paths

### Feature 1: Thông tin chuyến bay

**Trigger:** User hỏi giờ cất/hạ cánh hoặc trạng thái chuyến bay, ví dụ: “VN123 bay ngày mai mấy giờ?”  

| Path | Câu hỏi thiết kế | Mô tả |
|------|-----------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Bot hiểu đúng ý, hỏi bổ sung nếu thiếu (ngày, chuyến) → trả giờ cất/hạ cánh + trạng thái chuyến bay. User tiếp tục tra cứu hoặc chuyển sang đặt vé. |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Bot thông báo đang thiếu thông tin, hiển thị quick reply [Nhập ngày], [Chọn chuyến], user chọn → bot tiếp tục flow. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | Bot trả nhầm giờ/trạng thái → user nhận ra khi thông tin không khớp kế hoạch → sửa bằng nhập lại ngày/mã chuyến hoặc chọn quick reply khác. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User chỉnh lại input hoặc chọn quick reply → session lưu correction log → cải thiện mapping intent & retrieval. |

---

### Feature 2: Thông tin vé

**Trigger:** User hỏi về booking cá nhân, ví dụ: “Xem vé của tôi mã ABC123”  

| Path | Câu hỏi thiết kế | Mô tả |
|------|-----------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Bot trả booking chính xác, hiển thị đầy đủ chi tiết hành trình. User xem xong, có thể tra cứu tiếp hành lý hoặc giá vé. |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Bot thông báo không chắc tìm thấy booking, gợi ý chọn lại flow “Xem vé của tôi” hoặc nhập lại mã booking/email. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | Bot không tìm thấy hoặc trả sai booking → user nhận ra vì không khớp thông tin cá nhân → nhập lại mã booking/email hoặc chọn flow khác. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User nhập lại thông tin, session lưu failed retrieval → cải thiện database query & fallback. |

---

### Feature 3: Tìm kiếm giá vé

**Trigger:** User hỏi tìm giá vé, ví dụ: “Giá vé từ Hà Nội đi TP.HCM tuần này rẻ nhất?”  

| Path | Câu hỏi thiết kế | Mô tả |
|------|-----------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Bot đề xuất giá và chuyến phù hợp, hiển thị link tra cứu chính thức. User chọn tiếp chuyến hoặc xem chi tiết. |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Bot thông báo không chắc, hiển thị quick reply [Chọn ngày khác], [Chọn route khác], user chọn → bot tiếp tục tra cứu. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | Bot hiểu sai route/ngày, giá đề xuất không phù hợp → user nhận ra → sửa điểm đi/đến/ngày hoặc chọn quick reply đúng. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User chỉnh input hoặc chọn suggestion → session log pattern re-search → cải thiện retrieval và intent mapping. |

---

### Feature 4: Thông tin hành lý

**Trigger:** User hỏi về hành lý ký gửi/hành lý xách tay, ví dụ: “Hành lý ký gửi chuyến VN123 là bao nhiêu kg?”  

| Path | Câu hỏi thiết kế | Mô tả |
|------|-----------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Bot trả policy hành lý chính xác theo hạng vé và hành trình. User tiếp tục tra cứu hoặc kết thúc flow. |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Bot thông báo cần thêm thông tin (mã vé, hạng vé), hiển thị quick reply [Nhập mã vé], user chọn → bot tiếp tục trả policy chính xác. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | Bot trả sai policy (sai hạng vé/route) → user nhận ra khi không khớp vé → sửa bằng nhập mã/hạng vé bổ sung. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User nhập lại thông tin, session lưu correction → cải thiện mapping policy theo context. |
---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision · ☐ Recall

Tại sao?  
*Trong domain hàng không, trả lời sai nhưng nghe có vẻ đúng nguy hiểm hơn nhiều so với việc bot nói “tôi chưa đủ thông tin”. Nếu bot bịa hoặc áp sai policy, user có thể mất tiền, lỡ chuyến hoặc chuẩn bị sai giấy tờ. Vì vậy cần ưu tiên precision và fallback sớm khi không chắc.*

Nếu sai ngược lại thì chuyện gì xảy ra?  
*Nếu tối ưu recall quá mức, bot sẽ cố trả lời dù không chắc, làm tăng tỷ lệ hallucination hoặc kéo user vào flow sai. Nếu precision quá cao mà recall quá thấp, bot sẽ chuyển người thật quá sớm và giá trị tự động hóa không còn nhiều.*

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| *Intent routing accuracy* | *>= 85%* | *< 75% trong 2 tuần test liên tiếp* |
| *Loop rate (bị lặp flow/phản hồi)* | *<= 10% session* | *> 20% session* |
| *Deflection Rate* | *>= 35%* | *< 20% sau giai đoạn pilot* |
| *CSAT* | *>= 3.8/5* | *< 3.0/5 trong 1 tháng* |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | *User hỏi có nhiều biến số trong một câu: tuyến bay + thời gian + ưu đãi + ngữ cảnh trước đó* | *Bot bắt sai intent hoặc trả lời theo policy chung, user phải tự đoán câu trả lời có áp dụng không* | *Tách intent trước, hỏi làm rõ bằng quick replies, không trả lời đầy đủ nếu thiếu biến quan trọng* |
| 2 | *Bot giữ nhầm ngữ cảnh cũ và kéo user quay lại flow tra cứu trước đó* | *User bị mắc kẹt trong dead-end, thấy bot “ngu” hoặc spam* | *Session memory có TTL ngắn, cho phép reset flow, thêm nút `Thử cách tra cứu khác`* |
| 3 | *Policy/giá thay đổi nhưng knowledge base hoặc nguồn tra cứu chưa cập nhật* | *Bot đưa thông tin cũ, gây mất niềm tin hoặc rủi ro vận hành* | *Ràng buộc chỉ trả lời từ nguồn chính thức, timestamp nguồn dữ liệu, và fallback sang trang tra cứu/live agent nếu nguồn chưa chắc chắn* |

---

## 5. ROI 3 kịch bản

> Các số dưới đây là giả định order-of-magnitude để ước lượng nhanh cho hackathon.

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | *3,000 session/ngày, deflection 20%* | *8,000 session/ngày, deflection 35%* | *15,000 session/ngày, deflection 50%* |
| **Cost** | *~$300/tháng hạ tầng + vận hành* | *~$800/tháng* | *~$1,800/tháng* |
| **Benefit** | *Giảm tải một phần cho CSKH giờ cao điểm, giảm câu hỏi lặp* | *Giảm đáng kể volume FAQ lặp, tăng tốc xử lý cho tổng đài* | *Giảm tải mạnh cho CSKH, tăng self-service completion, tạo cơ hội upsell dịch vụ phụ trợ* |
| **Net** | *Dương nhẹ* | *Khả thi rõ ràng* | *Rất hấp dẫn nếu adoption cao* |

**Kill criteria:** *Nếu loop rate cao kéo dài, CSAT dưới 3.0/5, hoặc deflection rate dưới 15-20% sau pilot dù đã tinh chỉnh nhiều vòng, nên dừng hoặc thu hẹp scope về các intent đơn giản hơn.*

---

## 6. Mini AI spec (1 trang)

NEO 2.0 là phiên bản cải thiện của chatbot hỗ trợ khách hàng Vietnam Airlines theo hướng “web-first support agent” cho các nhu cầu tra cứu thông tin trước chuyến bay. Bài toán sản phẩm không phải là làm một AI biết mọi thứ, mà là giảm ma sát trong những câu hỏi lặp có volume cao như giá vé, thông tin chuyến bay, tra cứu theo mã đặt chỗ/số vé, đồng thời tránh để user bị kẹt trong các flow sai hoặc phản hồi lặp.
G
Về bản chất sản phẩm, NEO 2.0 thiên về augmentation hơn là automation. Với các truy vấn tra cứu cơ bản, bot có thể trả lời gần như tự động nếu đã có dữ liệu đúng từ nguồn chính thức. Nhưng với những nghiệp vụ nhạy cảm như thay đổi booking, hoàn vé, hoặc các case có nhiều biến số áp dụng, bot chỉ nên đóng vai trò hướng dẫn: hỏi làm rõ, tóm tắt policy, đưa link chính xác, và chuyển sang nhân viên hỗ trợ khi rủi ro tăng cao.

Về kỹ thuật, phiên bản hackathon không cần xây full agent phức tạp. Core hợp lý nhất là hybrid architecture gồm: intent classifier, session memory ngắn hạn, retrieval từ knowledge base chính thức, API/tool lookup cho các dữ liệu tra cứu được, và một response layer để diễn giải kết quả theo ngôn ngữ tự nhiên. Nếu dùng LLM thì LLM chỉ nên là lớp hiểu câu hỏi và diễn đạt câu trả lời, không phải nguồn chân lý. Source of truth luôn là policy chính thức, dữ liệu tra cứu chuyến bay và booking.

Về chất lượng, hệ thống cần optimize precision trước recall. Trong hàng không, “trả lời sai nhưng tự tin” nguy hiểm hơn “không chắc nên xin thêm dữ liệu hoặc chuyển người thật”. UX lý tưởng là: nếu bot tự tin thì trả lời ngắn gọn, có link nguồn và bước tiếp theo; nếu bot không chắc thì hỏi làm rõ bằng quick replies; nếu bot có dấu hiệu lệch intent hoặc loop thì chủ động cho user thoát sang một flow khác hoặc hand-off sang nhân viên.

Rủi ro lớn nhất của NEO 2.0 không phải latency, mà là trust erosion: bot lặp phản hồi, giữ nhầm ngữ cảnh, áp sai policy, hoặc không cho user một lối thoát rõ ràng. Vì vậy, ngoài intent accuracy, sản phẩm phải theo dõi loop rate, hand-off rate, re-ask rate và CSAT. Đây là các chỉ số phản ánh trải nghiệm thật hơn là chỉ nhìn accuracy đơn thuần.

Data flywheel của sản phẩm hoạt động như sau: user đặt câu hỏi -> bot xử lý và trả lời hoặc hand-off -> session được log lại với các tín hiệu như hỏi lại, bấm gặp nhân viên, đổi cách diễn đạt, bỏ dở giữa chừng -> team dùng các session lỗi để cập nhật intent map, câu hỏi làm rõ và fallback flow -> bot xử lý tốt hơn ở các lượt sau -> nhiều user hoàn tất self-service hơn -> hệ thống thu được thêm dữ liệu hội thoại thực tế để tiếp tục cải thiện. Giá trị lớn nhất ở đây là hiểu được các “support flow” thực tế của khách hàng Vietnam Airlines, chứ không chỉ có một chatbot trả lời FAQ.
