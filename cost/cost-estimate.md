# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): 3 kiểu theo số lần sửa lịch trước chuyến đi — `xep_mot_lan` 45% (1 phiên / tháng × 1 lượt) · `sua_vai_lan` 40% (1 × 3 lượt) · `len_ke_hoach_ky` 15% (2 × 5 lượt, có cả câu ngoài phạm vi). Nguồn: **(tự ước tính)**, thay bằng phân bố câu 12 của khảo sát (`evidence/survey/questions.md`) khi xuất kết quả.
- **Số người dùng thật** (người lên lịch / tháng) 3 kịch bản: thấp 1.400 · cơ sở 2.800 · cao 8.500. Nguồn: ~17,3 triệu lượt khách lưu trú Đà Nẵng năm 2025 ([VietnamNet](https://vietnamnet.vn/en/da-nang-tourism-surpasses-pre-pandemic-peak-remains-top-regional-leader-2477340.html), xem 27/11/2026) → ~1,44 triệu / tháng × 59% nội địa (tỉ lệ trong [kế hoạch 2025](https://nhadautu.vn/da-nang-dat-muc-tieu-don-gan-12-trieu-luot-khach-nam-2025-d92319.html), số kế hoạch) ÷ 3 người / nhóm ≈ 283.000 người lên lịch / tháng × tỉ lệ dùng 0,5% · 1% · 3% **(tự ước tính)**.
- **Giá** 3 mức model (bảng giá chung của BTC, `further-reading/model-prices.md` của repo đề, [trang giá Anthropic](https://platform.claude.com/docs/en/about-claude/pricing), BTC xem 25/11/2026), USD / 1 triệu token vào · ra: Claude Haiku 4.5 1,00 · 5,00 (model đang chạy, qua Amazon Bedrock — giá Bedrock chưa kiểm riêng) · Claude Haiku 5.5 0,10 · 0,50 · Claude Sonnet 4.6 3,00 · 15,00
- **Tỉ lệ đạt** dùng để tính: __/__ (__%) — lượt `run-__` (lượt 2)
- Đo token trên model __, tính giá model __ và __

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-__.csv` · run ID __ · __ phiên · seed __

*(dán bảng từ `cost/simulate-N-summary.md`)*

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp | / tháng — cơ sở | / tháng — cao | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): __
- Chi phí / người / tháng (cơ sở, model __): __
- **Kết luận một dòng — đáng làm không:** __

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Bảng độ nhạy: model rẻ hơn · cache · cắt ngữ cảnh · giới hạn bước — mỗi cần gạt đổi chi phí bao nhiêu
- Chi phí ngoài model: hosting, lưu trữ, giờ công người duyệt
- Quy mô nào thì bài toán còn đáng làm
