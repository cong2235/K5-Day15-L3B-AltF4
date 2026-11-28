# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-000747` | 27/30 | 90% | 5/6 | 16/18 | 6/6 | **đạt** (khong_vi_pham_cung 18/19 ≥ 17 · khong_bia_dia_diem 30/30 · xu_ly_bat_kha_thi 3/3 · tu_choi_dung 6/6) |
| 2 | | __/__ | | __/__ | __/__ | __/__ | đạt / chưa |

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

- Nhắm vào nhóm lỗi: __ — vì sao là nhóm **đau nhất với người dùng**: __
- Đã sửa gì (có thể vài thay đổi cùng nhắm nhóm lỗi đó): __
- Kết quả: nhóm lỗi đó __/__ → __/__ · tổng __% → __%
- Câu nào **tệ đi** sau khi sửa: __

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
