# Tóm tắt mô phỏng simulate-2@20261128-135919

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| xep_mot_lan | 3 | 1 | 5318 | 206 | 1.7 | 0.3 |
| sua_vai_lan | 33 | 3 | 36136 | 1191 | 10.2 | 3.1 |
| len_ke_hoach_ky | 14 | 5 | 49531 | 1539 | 13.9 | 3.8 |

Tỉ lệ đạt dùng để tính: 28/30 (93%) — lượt run-3@20261128-124115

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-3.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (1.400 người) | Chi phí / tháng — cơ sở (2.800 người) | Chi phí / tháng — cao (8.500 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| claude-haiku-4.5 (vào 1.0 · ra 5.0 $/1M) | $0.0442 (≈ 1.149 ₫) | $0.0473 (≈ 1.231 ₫) | $0.0138 (≈ 358 ₫) | $77.27 (≈ 2.009.035 ₫) | $154.54 (≈ 4.018.069 ₫) | $469.14 (≈ 12.197.710 ₫) | $0.0552 (≈ 1.435 ₫) |
| claude-haiku-5.5 (vào 0.1 · ra 0.5 $/1M) | $0.0044 (≈ 115 ₫) | $0.0047 (≈ 123 ₫) | $0.0014 (≈ 36 ₫) | $7.73 (≈ 200.903 ₫) | $15.45 (≈ 401.807 ₫) | $46.91 (≈ 1.219.771 ₫) | $0.0055 (≈ 144 ₫) |
| claude-sonnet-4.6 (vào 3.0 · ra 15.0 $/1M) | $0.1326 (≈ 3.446 ₫) | $0.1420 (≈ 3.692 ₫) | $0.0413 (≈ 1.073 ₫) | $231.81 (≈ 6.027.104 ₫) | $463.62 (≈ 12.054.207 ₫) | $1,407.43 (≈ 36.593.130 ₫) | $0.1656 (≈ 4.305 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (3.4) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: global.anthropic.claude-haiku-4-5-20251001-v1:0. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
- Tỷ giá: 1 USD = 26.000 ₫ ((tự ước tính) tỉ giá làm tròn, chưa kiểm ngày cụ thể).
