# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): 3 kiểu theo số lần sửa lịch trước chuyến đi — `xep_mot_lan` 18% (1 phiên / tháng × 1 lượt) · `sua_vai_lan` 55% (1 × 3 lượt) · `len_ke_hoach_ky` 27% (2 × 5 lượt, có cả câu ngoài phạm vi). Nguồn: tỉ lệ từ khảo sát câu 12 (n = 22, `evidence/survey/results.csv`: không sửa 4 · 1–2 lần 12 · ≥3 lần 6); số phiên và số lượt mỗi phiên **(tự ước tính)**.
- **Số người dùng thật** (người lên lịch / tháng) 3 kịch bản: thấp 1.400 · cơ sở 2.800 · cao 8.500. Nguồn: ~17,3 triệu lượt khách lưu trú Đà Nẵng năm 2025 ([VietnamNet](https://vietnamnet.vn/en/da-nang-tourism-surpasses-pre-pandemic-peak-remains-top-regional-leader-2477340.html), xem 27/11/2026) → ~1,44 triệu / tháng × 59% nội địa (tỉ lệ trong [kế hoạch 2025](https://nhadautu.vn/da-nang-dat-muc-tieu-don-gan-12-trieu-luot-khach-nam-2025-d92319.html), số kế hoạch) ÷ 3 người / nhóm (khảo sát câu 4) ≈ 283.000 người lên lịch / tháng × tỉ lệ dùng 0,5% · 1% · 3% **(tự ước tính)**.
- **Giá** 3 mức model (bảng giá chung của BTC, `further-reading/model-prices.md` của repo đề, [trang giá Anthropic](https://platform.claude.com/docs/en/about-claude/pricing), BTC xem 25/11/2026), USD / 1 triệu token vào · ra: Claude Haiku 4.5 1,00 · 5,00 (model đang chạy, qua Amazon Bedrock — giá Bedrock chưa kiểm riêng) · Claude Haiku 5.5 0,10 · 0,50 · Claude Sonnet 4.6 3,00 · 15,00
- **Tỉ lệ đạt** dùng để tính trong bảng mục 2: 28/30 (93%) — Lượt 2 `run-3@20261128-124115` (`python run.py simulate --rate-from eval/run-3.csv`). Lượt mô phỏng trước, `simulate-1`, dùng tỉ lệ 27/30 (90%) của `run-1` và cho 1.312 ₫ / task thành công; giữ lại để đối chiếu
- Đo token trên model Claude Haiku 4.5 (`global.anthropic.claude-haiku-4-5-20251001-v1:0`, Bedrock), tính giá Claude Haiku 4.5, Claude Haiku 5.5 và Claude Sonnet 4.6. Haiku 5.5 và Sonnet 4.6 có thể tách token khác, nên hai dòng đó là ước tính theo token của Haiku 4.5

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-2.csv` · 50 phiên, 0 phiên lỗi · seed 42 · tóm tắt máy sinh: `cost/simulate-2-summary.md` (chép nguyên, không sửa số)

**Token đo được theo persona** (trung bình mỗi phiên):

| Persona | Số phiên | Lượt hỏi / phiên | Token vào | Token ra | Gọi model | Gọi công cụ |
|---|---:|---:|---:|---:|---:|---:|
| xep_mot_lan | 3 | 1 | 5318 | 206 | 1.7 | 0.3 |
| sua_vai_lan | 33 | 3 | 36136 | 1191 | 10.2 | 3.1 |
| len_ke_hoach_ky | 14 | 5 | 49531 | 1539 | 13.9 | 3.8 |

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp (1.400) | / tháng — cơ sở (2.800) | / tháng — cao (8.500) | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| **Claude Haiku 4.5** (đang chạy) | $0.0442 (≈ 1.149 ₫) | **$0.0473 (≈ 1.231 ₫)** | $77.27 (≈ 2,01 triệu ₫) | $154.54 (≈ 4,02 triệu ₫) | $469.14 (≈ 12,20 triệu ₫) | $0.0552 (≈ 1.435 ₫) |
| Claude Haiku 5.5 (rẻ hơn) | $0.0044 (≈ 115 ₫) | $0.0047 (≈ 123 ₫) | $7.73 (≈ 0,20 triệu ₫) | $15.45 (≈ 0,40 triệu ₫) | $46.91 (≈ 1,22 triệu ₫) | $0.0055 (≈ 144 ₫) |
| Claude Sonnet 4.6 (lớn hơn) | $0.1326 (≈ 3.446 ₫) | $0.1420 (≈ 3.692 ₫) | $231.81 (≈ 6,03 triệu ₫) | $463.62 (≈ 12,05 triệu ₫) | $1,407.43 (≈ 36,59 triệu ₫) | $0.1656 (≈ 4.305 ₫) |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**. Tỉ giá 26.000 ₫/USD *(tự ước tính)*.

**Đọc bảng:** chi phí do **số lần sửa lịch** quyết định. Một lượt hỏi tốn khoảng 1,7–3,4 lần gọi model và 5–18 nghìn token vào (mỗi lần gửi danh sách ứng viên cho `propose`/`repair`). Persona sửa ≥3 lần chỉ chiếm 27% người dùng nhưng một phiên tốn gấp ~10 lần persona xếp một lần.

## 3. So với impact

- **Impact / người / tháng** (`spec.md` §2): một người lên lịch mất trung vị **90 phút** cho một ngày đi chơi (khảo sát câu 6, n = 21), và 13/22 chuyến (59%) gặp sự cố đóng cửa / đi vòng / bỏ điểm. Nếu quy thời gian ra tiền ở mức 25.000 ₫ / giờ *(tự ước tính)*: 90 phút ≈ **37.500 ₫ / người / lần lên lịch**. Chưa cộng 200.000 ₫ / người / ngày tiêu thêm (khảo sát câu 9) vì câu hỏi không tách nguyên nhân.
- **Chi phí / người / tháng** (cơ sở, Claude Haiku 4.5): **≈ 1.435 ₫**, tức khoảng **4%** giá trị 90 phút đó; đổi sang Haiku 5.5 còn ≈ 144 ₫.
- **Kết luận một dòng — đáng làm không:** **Đáng làm về chi phí model** (≈ 1.400 ₫ / người / tháng so với ≈ 37.500 ₫ thời gian lên lịch, kể cả ở kịch bản cao chỉ ≈ 12,2 triệu ₫ / tháng), với điều kiện bản chạy thử thật sự rút ngắn thời gian lên lịch — điều này **chưa đo** (cần người dùng thử bấm giờ, `validation/log.md`).
- **Đối chiếu quy mô với `spec.md` §2:** §2 ước ≈ 86.000 chuyến tự đi theo nhóm trẻ / tháng; kịch bản thấp · cơ sở · cao ở đây (1.400 · 2.800 · 8.500 người) tương ứng khoảng 1,6% · 3,3% · 10% số chuyến đó.

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Bảng độ nhạy: model rẻ hơn · cache · cắt ngữ cảnh · giới hạn bước — mỗi cần gạt đổi chi phí bao nhiêu
- Chi phí ngoài model: hosting, lưu trữ, giờ công người duyệt
- Quy mô nào thì bài toán còn đáng làm
