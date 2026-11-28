# Reflection — Hà Văn Khánh Đạt

1. **Vai trò + phần mình làm:**
   Mình phụ trách data, bằng chứng pain, bảng impact và slide.
   - **Data:** `data/places.csv` có 34 điểm ở Đà Nẵng và Hội An, mỗi dòng có link nguồn và ngày kiểm. Thêm `travel_override.csv`, `transport_rates.csv` và ghi chú `collection-notes.md` (commit `3427d44`).
   - **Khảo sát:** viết giả thuyết trước khi đọc kết quả (`evidence/hypothesis.md`, `d19d37d`) và gửi form qua Zalo. Đếm lại theo luật lọc đã ghi trước thì còn n = 22, có 59% gặp sự cố khi đi theo lịch. Kết quả ở `evidence/summary.md`, `spec.md` §1–§2 và bảng impact (`3e699a5`).
   - **Slide:** slide demo `demo-slides.pdf` (`64b1758`). Mình trình bày hai trang Pain và Impact.

2. **AI hỗ trợ mình thế nào:**
   - **Thu thập data:** mình dùng Claude Code, viết đặc tả trước (`docs/prompt-thu-thap-data.md`) rồi để agent tra web.
   - **Phải sửa sau đó:** bản đầu có 5 dòng thiếu giá vé, và code bị lỗi khi đọc ô `price_pp` trống. Mình cho tra bổ sung, dòng nào không tìm được số thì bỏ chứ không đoán, nên từ 39 dòng còn 34.
   - **Kiểm link:** mình mở lại từng link nguồn. Có lần mình tưởng link Michelin hỏng, hóa ra là do mình chép dính cả cột ngày kiểm.
   - **Đếm khảo sát:** cũng dùng AI. AI chỉ ra 15 phiếu gửi trong 8 phút; mình kiểm lại và xác nhận đó là người thật ngoài nhóm thì mới dùng.
   - **Số ước tính:** con số 10% khách tự đi theo nhóm trẻ là mình tự ước tính, nên ghi rõ "(tự ước tính)", không để như số có nguồn.

3. **Một câu thử trượt của nhóm và mình học được gì:**
   - **Câu T05:** khách muốn ăn tối rồi xem cầu Rồng.
     - Data mình đã ghi cầu Rồng phun lửa lúc 21:00–21:15 tối thứ Sáu đến Chủ nhật, ở cột `best_windows` và `event_days`.
     - Nhưng lịch lại xếp cầu Rồng từ 21:35, tức là lỡ đúng thứ khách muốn xem, và qua cả 2 lượt vẫn trượt.
   - **Mình học được:**
     - Có data đúng chưa đủ. Code phải dùng tới cột đó như một ràng buộc thật, giống giờ mở cửa, thì mới có tác dụng.
     - Lần sau làm data, mình sẽ hỏi lại người viết code xem cột nào thật sự được đọc, và đề xuất một câu thử riêng cho từng cột quan trọng.
