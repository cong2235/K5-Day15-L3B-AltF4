# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-000747` | 27/30 | 90% | 5/6 | 16/18 | 6/6 | **đạt** (khong_vi_pham_cung 18/19 ≥ 17 · khong_bia_dia_diem 30/30 · xu_ly_bat_kha_thi 3/3 · tu_choi_dung 6/6) |
| 2a | `run-2@20261128-121330` | 26/30 | 87% | 5/6 | 15/18 | 6/6 | chưa (khong_bia_dia_diem 28/30: câu lý do ghi giá vé của điểm không có trong lịch) |
| **2** | `run-3@20261128-124115` | **28/30** | **93%** | 5/6 | 17/18 | 6/6 | **đạt** (19/19 · 30/30 · 3/3 · 6/6) |

- Run-1 chạy trên bộ câu thử bản 27/11; run-2 và run-3 chạy trên bộ cuối (T08, K08, K11 đã thay bằng T10, K19, K20 — `eval/README.md` mục 2). **So trên 27 câu chung: 24/27 → 25/27.** Trên đủ 30 câu: 27/30 (bộ cũ) → 28/30 (bộ cuối). Nhóm không chạy lượt mốc trên bộ cuối trước khi sửa code, nên chỉ so trực tiếp được trên 27 câu chung.
- Cả 3 lượt cùng model (Claude Haiku 4.5), cùng `eval/grade.py`, chuẩn "đạt" không đổi. Quân chấm lại độc lập bằng `python eval/grade.py --dry`: khớp cột `pass` cả 3 lượt.

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`. Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| **Điểm người dùng nêu không đi được → bỏ cả lịch** (điểm bắt buộc ngoài giờ mở thì trả "không xếp được" thay vì báo điểm đó và xếp phần còn lại) | 1 trượt + 1 đạt nhưng sai lý do | K18 (trượt) · K10 (grader cho đạt, kiểm tay thấy lý do sai) |
| **Bỏ qua khung giờ sự kiện** (`best_windows`, `event_days` có trong data nhưng lịch không đặt theo) | 1 | T05 |
| **Sở thích mâu thuẫn bị bỏ một vế mà không nói** (không hỏi lại, cũng không nêu đánh đổi) | 1 | K09 |

**≥3 lỗi cụ thể:**

| Câu | Input | Output (rút gọn từ `eval/run-1.csv`) | Vì sao sai |
|---|---|---|---|
| K18 | Thứ Bảy 2 người 9h–17h, 500k, trưa 12h muốn ăn bún bò Bà Thương rồi chiều ra biển Mỹ Khê | `status=infeasible`: "không xếp được lịch nào thoả hết yêu cầu với Bún bò Huế Bà Thương, Bãi biển Mỹ Khê: không đủ thời gian". Cách nới duy nhất: "Bỏ Bún bò Huế Bà Thương, Bãi biển Mỹ Khê" nhưng lịch nới vẫn có Mỹ Khê | Quán chỉ mở 06:00–10:00 (DN-022). Đúng ra phải báo quán không mở buổi trưa và vẫn đưa lịch có bữa trưa + biển (đủ giờ, đủ tiền). Người dùng nhận "không xếp được" dù hoàn toàn đi được; nhãn cách nới còn ghi bỏ cả Mỹ Khê, sai với lịch đi kèm |
| T05 | Tối thứ Bảy 2 người 16h–23h, 1,5 triệu, ăn tối lãng mạn rồi ra xem cầu Rồng | Lịch 6 điểm, cầu Rồng 21:35–23:00; đi lại 327.000đ trên tổng 387.000đ | Data ghi cầu Rồng phun lửa 21:00–21:15 tối T6–CN (DN-003). Lịch đến sau giờ phun lửa nên lỡ đúng thứ người dùng muốn xem; lịch còn đi vòng Sơn Trà → Mỹ Khê → trung tâm, tiền đi lại gấp 5 lần tiền ăn |
| K09 | 2 người 1 triệu, thứ Bảy 14h–23h, muốn chỗ thật yên tĩnh nhưng tối cũng ra chợ đêm sôi động | Lịch 6 điểm gồm chợ Hàn, cầu Rồng và 3 chợ đêm; không có điểm nào tag `yen_tinh` | Bỏ hẳn vế "yên tĩnh" mà không hỏi lại hay nói đánh đổi; lý do còn ghi cầu Rồng "không quá đông" (data không có thông tin này) |
| K10 *(đạt theo grader)* | 2 người 1,2 triệu, thứ Bảy 7h–21h, sáng Bà Nà, chiều Mỹ Khê, tối hải sản | `status=infeasible`, lý do "không đủ thời gian trong khung giờ"; cách nới "Bỏ Sun World Bà Nà Hills, Bãi biển Mỹ Khê" nhưng lịch nới có Mỹ Khê | Lý do thật là tiền: vé Bà Nà 2 × 1.000.000đ > 1.200.000đ. Cùng lỗi với K18: phần nêu lý do và nhãn cách nới không khớp dữ liệu |

## 3. Một lần cải tiến

- **Nhắm vào nhóm lỗi:** "điểm người dùng nêu không đi được → bỏ cả lịch" (K18, K10). **Vì sao đau nhất:** người dùng nhận "không xếp được" cho một ngày hoàn toàn đi được (K18), hoặc nhận lý do sai (K10 nói thiếu thời gian trong khi vé Bà Nà vượt ngân sách), nên sẽ bỏ công cụ hoặc tự đi tra lại — đúng việc sản phẩm muốn thay. Hai nhóm lỗi còn lại (T05 lỡ giờ phun lửa, K09 bỏ vế "yên tĩnh") làm lịch kém hay hơn nhưng không làm hỏng cả lịch.
- **Đã sửa gì** (Đức, commit `dc2ef4e`, cùng nhắm một nhóm lỗi):
  1. Quán không mở trong khung bữa chính thì xếp ghé ăn thêm và chọn quán khác cho bữa chính, lịch ghi rõ việc này (`_timed`, `plan_greedy`).
  2. `repair` được báo quán nào không làm bữa được (run-1 K18 trả cùng tập điểm cả 4 vòng sửa).
  3. `relax_options` thử bỏ ít điểm bắt buộc nhất trước; điểm đã bỏ không quay lại trong lịch nới (run-1 ghi "Bỏ Bà Nà, Mỹ Khê" nhưng lịch nới vẫn có Mỹ Khê).
  4. Câu lý do "không xếp được" lấy từ phép thử bỏ giới hạn tiền, không đoán theo loại cách nới.
  5. Run-2 (26/30) làm tụt K01, K10: câu lý do mới ghi giá vé của điểm không có trong lịch, vi phạm `khong_bia_dia_diem`. Sửa tiếp trong cùng nhóm lỗi: bỏ con số giá vé khỏi câu lý do → run-3. Ghi cả hai lượt, không bỏ run-2.
- **Kết quả:** nhóm lỗi đó 1/2 → **2/2** theo grader (K18 0 → 1; K10 giữ 1), và theo kiểm tay **0/2 → 2/2**: K18 giờ đưa lịch có bữa chính ở quán khác và báo "Bún bò Huế Bà Thương chỉ mở 06:00–10:00"; K10 giờ nêu đúng lý do "riêng vé Sun World Bà Nà Hills cho 2 người đã vượt ngân sách 1.200.000đ" và cách nới chỉ bỏ Bà Nà. Tổng 27/30 (90%) → **28/30 (93%)**; trên 27 câu chung 24 → 25.
- **Câu tệ đi sau khi sửa:** ở run-2 có K01 và K10 (1 → 0, lý do ở trên); ở run-3 không câu nào tệ đi so với run-1. Token vào cả lượt giảm 342.824 → 299.182, số lần gọi model 92 → 85.

## 4. Còn lại

- **T05 (lỡ giờ phun lửa cầu Rồng):** lịch đặt cầu Rồng 21:35–23:00 trong khi data ghi phun lửa 21:00–21:15 tối T6–CN. Nguy hiểm vừa: người dùng đến nơi đúng lúc vừa hết show — đúng loại "đến nơi thì đã hết giờ" mà 7/22 người khảo sát gặp. Sửa: đưa `best_windows` vào bước xếp giờ bằng code như giờ mở cửa.
- **K09 (sở thích mâu thuẫn):** lịch toàn chợ đêm, bỏ vế "yên tĩnh" mà không hỏi lại hay nói đánh đổi. Nguy hiểm thấp nhưng làm người dùng thấy công cụ không nghe mình.
- **Lỗ hổng của cách đo:** luật K10 "văn bản có cụm vé hoặc Bà Nà" quá lỏng (run-1 đạt dù lý do sai, phát hiện khi kiểm tay); metric chưa đo lịch "đáng đi" (đi vòng, tiền đi lại gấp nhiều lần tiền ăn ở T05) — xem `eval/metric-gaps.md`.
- **Nếu có thêm 1 tuần:** chạy mỗi câu ≥3 lần để đo độ ổn định; thêm câu người dùng thật từ phỏng vấn; đo thời gian lên lịch với người dùng thử (`validation/log.md`) để kiểm giả định "rút ngắn 90 phút".
