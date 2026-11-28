# Tóm tắt mô phỏng simulate-1@20261128-101403

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| xep_mot_lan | 3 | 1 | 5318 | 207 | 1.7 | 0.3 |
| sua_vai_lan | 33 | 3 | 37035 | 1069 | 10.3 | 3.2 |
| len_ke_hoach_ky | 14 | 5 | 53732 | 1433 | 14.4 | 4.2 |

Tỉ lệ đạt dùng để tính: 27/30 (90%) — lượt run-1@20261128-000747

- Tự chọn: lượt run-N mới nhất đã chấm xong, chạy bằng đúng model đang đo (run-1.csv). Muốn dùng lượt khác (vd lượt 2): thêm `--rate-from eval/run-2.csv`.

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (1.400 người) | Chi phí / tháng — cơ sở (2.800 người) | Chi phí / tháng — cao (8.500 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| claude-haiku-4.5 (vào 1.0 · ra 5.0 $/1M) | $0.0454 (≈ 1.180 ₫) | $0.0504 (≈ 1.312 ₫) | $0.0147 (≈ 381 ₫) | $80.27 (≈ 2.087.076 ₫) | $160.54 (≈ 4.174.151 ₫) | $487.37 (≈ 12.671.531 ₫) | $0.0573 (≈ 1.491 ₫) |
| claude-haiku-5.5 (vào 0.1 · ra 0.5 $/1M) | $0.0045 (≈ 118 ₫) | $0.0050 (≈ 131 ₫) | $0.0015 (≈ 38 ₫) | $8.03 (≈ 208.708 ₫) | $16.05 (≈ 417.415 ₫) | $48.74 (≈ 1.267.153 ₫) | $0.0057 (≈ 149 ₫) |
| claude-sonnet-4.6 (vào 3.0 · ra 15.0 $/1M) | $0.1362 (≈ 3.541 ₫) | $0.1513 (≈ 3.935 ₫) | $0.0440 (≈ 1.144 ₫) | $240.82 (≈ 6.261.227 ₫) | $481.63 (≈ 12.522.454 ₫) | $1,462.10 (≈ 38.014.592 ₫) | $0.1720 (≈ 4.472 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (3.4) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: global.anthropic.claude-haiku-4-5-20251001-v1:0. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
- Tỷ giá: 1 USD = 26.000 ₫ ((tự ước tính) tỉ giá làm tròn, chưa kiểm ngày cụ thể).
