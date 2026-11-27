# Khảo sát — lên lịch một ngày đi chơi ở nơi lạ

> Nguồn bằng chứng cho `spec.md` §1–§2 và `cost/personas.yaml`. Ngưỡng: **≥20 người ngoài nhóm, đúng người dùng** (sau khi lọc, xem dưới).
> Form một trang, 13 câu, tạo bằng script [`create_form.gs`](create_form.gs), nên câu chữ trong form khớp đúng file này.

## Thông tin đợt khảo sát (điền khi gửi)

| | |
|---|---|
| Link form | https://docs.google.com/forms/d/e/1FAIpQLSdEqzYxl_n1jD7Gb0dkohq3n8DoQI-_O9NjI4BgTinvsmd3Dw/viewform |
| Kênh đã gửi | __ (ví dụ: nhóm lớp L3A, L3B · nhóm bạn đại học · người thân) |
| Giờ mở | 18h ngày 27/11/2006 |
| Giờ chốt | __ (trước CP3 10:00 Thứ Bảy 28/11) |
| Số phiếu nhận / số phiếu đúng người dùng | __ / __ |

## Người trả lời đúng là ai

Người **trong 12 tháng qua** đã tự đi chơi (không theo tour) ở một tỉnh hay thành phố chưa quen, cùng bạn bè hoặc người thân. Mô tả đầu form ghi rõ đối tượng này.

Form không có câu lọc riêng. Khi phân tích, **loại phiếu** chọn "Hơn 12 tháng" ở câu 3 **hoặc** chọn "0" ở câu 5. Những phiếu còn lại mới tính vào n.

Lấy mốc 12 tháng vì đa số người chỉ đi du lịch vài lần mỗi năm. Câu 3 ghi chuyến đó cách đây bao lâu, nên khi phân tích có thể lọc riêng những người đi trong 3 tháng gần nhất để giảm sai số do nhớ không chính xác.

## Câu hỏi

Mọi câu hỏi về **chuyến gần nhất đã xảy ra**, không hỏi "bạn có thích / có muốn dùng không".

| # | Câu hỏi | Kiểu | Lựa chọn | Lấy số cho |
|---|---|---|---|---|
| 1 | Trong chuyến tự đi chơi gần nhất, ai là người lên lịch đi chơi? | Chọn một, bắt buộc | Tôi lên lịch chính · Tôi cùng lên lịch với người khác · Người khác lên lịch, tôi đi theo | Tách riêng nhóm người lên lịch (người dùng chính) |
| 2 | Chuyến gần nhất đó bạn đi đâu? | Chọn một + Khác, bắt buộc | Đà Nẵng / Hội An · Đà Lạt · Nha Trang · Phú Quốc · Hà Nội · TP.HCM · Sa Pa / Hà Giang · Khác | Bao nhiêu người đã đi đúng nơi trong lát cắt |
| 3 | Chuyến đó cách đây bao lâu? | Chọn một, bắt buộc | Trong 1 tháng qua · 1–3 tháng · 3–6 tháng · 6–12 tháng · Hơn 12 tháng *(loại)* | Lọc đúng người dùng + độ mới của trí nhớ |
| 4 | Chuyến đó đi mấy người (tính cả bạn)? | Chọn một, bắt buộc | 1 · 2 · 3–4 · 5 trở lên | Kiểm người dùng chính (nhóm 2–4 người) |
| 5 | Trong 12 tháng qua, bạn tự đi chơi kiểu này mấy chuyến? | Chọn một, bắt buộc | 0 *(loại)* · 1 · 2 · 3–4 · 5 trở lên | Lọc + impact: số lần / năm → / tháng |
| 6 | Để lên lịch cho **một ngày** đi chơi trong chuyến đó, bạn (hoặc người lên lịch) đã mất tổng cộng bao lâu? | Chọn một, bắt buộc | Dưới 30 phút · 30–60 phút · 1–2 giờ · 2–4 giờ · Trên 4 giờ · Không biết | Impact: thời gian mỗi lần |
| 7 | Khi lên lịch, bạn đã dùng những nguồn nào? | Chọn nhiều + Khác, bắt buộc | Google Maps · TikTok / Reels / YouTube · Nhóm Facebook du lịch · Blog / bài review · Tripadvisor · App du lịch (Traveloka, Klook…) · ChatGPT / Gemini / trợ lý AI khác · Hỏi người quen | §0 luồng hiện tại · số nguồn phải lục |
| 8 | Trong chuyến đó, những chuyện nào **đã xảy ra**? | Chọn nhiều, bắt buộc | Đến nơi thì điểm đã đóng cửa / hết giờ bán vé · Di chuyển giữa các điểm lâu hơn dự tính / phải đi vòng · Phải bỏ bớt điểm vì không kịp giờ · Tiêu nhiều hơn dự tính · Quán ăn / điểm chơi không như review · Cả nhóm mất nhiều thời gian bàn vì không thống nhất · Không có chuyện nào kể trên | **Số chính của pain:** x/n gặp ≥1 sự cố lịch trình |
| 9 | So với dự tính, mỗi người đã tiêu thêm khoảng bao nhiêu trong một ngày đó? | Chọn một, bắt buộc | Không tiêu thêm · Dưới 100k · 100–300k · 300–500k · Trên 500k · Không nhớ | Impact: tiền mất mỗi lần |
| 10 | Khi lên lịch, phần nào mất công nhất? | Chọn một + Khác, bắt buộc | Tìm chỗ đáng đi, quán đáng ăn · Tính điểm nào gần nhau, đi theo thứ tự nào · Kiểm giờ mở cửa · Ước tổng tiền cho vừa ngân sách · Thống nhất ý kiến cả nhóm · Không biết nguồn nào đáng tin | **Kiểm tiền đề** ở `spec.md` §1: nỗi đau là xếp lịch, thiếu thông tin hay không tin nguồn |
| 11 | Nếu đã dùng ChatGPT / trợ lý AI để lên lịch, kết quả thế nào? | Chọn một, bắt buộc | Chưa dùng AI cho việc này · Đi theo được gần hết · Phải sửa nhiều mới dùng được · Có thông tin sai (giờ mở, giá, địa điểm không có thật) | §3 giải pháp tương tự: AI chung hỏng ở đâu |
| 12 | Trước chuyến đi, lịch đã được sửa lại mấy lần? | Chọn một, bắt buộc | Không sửa · 1–2 lần · 3–5 lần · Trên 5 lần | `cost/personas.yaml`: số lần gọi mỗi người dùng |
| 13 | Kể lại một lần cụ thể trong chuyến đó khi lịch trình không như dự tính: chuyện gì xảy ra, nhóm đã xử lý thế nào? | Đoạn văn, không bắt buộc | — | ≥5 trích dẫn nguyên văn cho `evidence/summary.md` |

Form **không thu email, không thu tên, không thu thông tin liên hệ**.

## Cách tính các số chính (viết trước khi xem kết quả)

- **n** = số phiếu còn lại sau khi loại "Hơn 12 tháng" (câu 3) hoặc "0" (câu 5). Phiếu của thành viên nhóm không tính.
- **Pain:** x/n chọn ≥1 trong 3 sự cố đầu ở câu 8 (đóng cửa · đi vòng · bỏ điểm vì không kịp giờ). Báo riêng cho nhóm câu 1 = "Tôi lên lịch chính".
- **Thời gian lên lịch:** trung vị câu 6, quy về giữa khoảng (30–60 phút → 45 phút; trên 4 giờ → 4 giờ). Bỏ "Không biết" ra khỏi mẫu số.
- **Số chuyến / tháng:** trung bình câu 5 quy về số (3–4 → 3,5; 5 trở lên → 5), chia 12.
- **Tiêu thêm:** trung vị câu 9, quy về giữa khoảng. Bỏ "Không nhớ".
- **Tiền đề:** đếm từng lựa chọn câu 10. Nếu "tính thứ tự" + "giờ mở cửa" + "ước tiền" cộng lại **không** phải nhóm lớn nhất thì phải xem lại lát cắt (ghi `spec.md` §10).
- Dưới khoảng 10 người trong một nhóm con thì chỉ ghi x/n, không ghi %.

## Lưu kết quả

- `results.csv`: xuất từ Google Sheets, **xoá cột Dấu thời gian** trước khi commit. Bản gốc không commit.
- Số chính + ≥3 câu trả lời nguyên văn ở câu 13 (bỏ tên người, tên quán nếu nhận ra được ai) → `evidence/summary.md`.
