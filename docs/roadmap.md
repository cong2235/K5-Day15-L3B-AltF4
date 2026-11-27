# Hướng phát triển tính năng

Sắp theo nguyên tắc pstack `sequence-verifiable-units`: mỗi đơn vị kết thúc bằng một trạng thái kiểm được, xong đơn vị này mới sang đơn vị sau. Cho phép chạy song song chỉ khi hai việc không chạm cùng một file.

## Trong hackathon (bắt buộc)

| # | Đơn vị | Kết thúc khi (kiểm được) | Hạn | Ai gợi ý |
|---|---|---|---|---|
| U1 | `data/places.csv` + `travel_override.csv` + `DATA_CARD.md` | 25–40 dòng, mỗi dòng có nguồn + ngày kiểm, có ca khó cố ý | Tối 27/11 | Đạt |
| U2 | `verify()` + `cost()` + test | 10 kế hoạch viết tay: 5 hợp lệ, 5 mỗi cái một lỗi, `verify` báo đúng mã | Trước CP2 19:30 | Đức |
| U3 | Khung `answer()` chạy bằng model giả | `python run.py eval --fake` chạy hết luồng, không lỗi | CP2 19:30 | Đức |
| U4 | `eval/benchmark.csv` 10 câu + `metric_spec.yaml` + ngưỡng "đạt" chốt | `python run.py check` hết cảnh báo CP2 | CP2 19:30 | Quân |
| U5 | `parse_request` (nối model thật, prompt) + `shortlist` | 10 câu cho ra `Constraints` đúng, hỏi lại đúng ca thiếu | Tối 27/11 | Công (parse), Đức (shortlist) |
| U6 | `propose` + `repair` + `relax_options` | Lượt 1 chạy đủ bộ, ghi Run ID | Sáng 28/11 | Công (prompt `propose`, `repair`) + Đức (`relax_options`, luồng) |
| U7 | `eval/grade.py` | Chạy trên `run-1.csv` ra cột `pass`, khớp với chấm tay 5 câu | Sáng 28/11 | Quân |
| U8 | Bằng chứng pain: ≥3 phỏng vấn / ≥20 khảo sát + ≥5 trích dẫn | `evidence/summary.md` đạt ngưỡng | CP3 10:00 | Đạt, cả nhóm |
| U9 | Video 30 giây AI thật | Mở được bằng tab ẩn danh | CP3 10:00 | Công |
| U10 | **Cải tiến Lượt 2** | Một thay đổi, đo Lượt 1 → 2 trong `eval/report.md` | CP4 14:30 | Cả nhóm |
| U11 | `simulate` ≥50 phiên + `cost-estimate.md` | Chi phí / task thành công + tên model | CP4 14:30 | Quân |
| U12 | `demo-slides.pdf` + video dự phòng | Mở được ẩn danh | CP4 14:30 | Công, Đạt |

## Cải tiến Lượt 2: chọn theo ca trượt, không chọn trước
Quyết định sau khi đọc các câu trượt của Lượt 1. Bốn ứng viên, xếp theo khả năng ăn điểm (ứng viên 0 lấy từ mục A1 của `architecture-review.md`):
0. **Chuyển việc xếp giờ từ model sang code** (`schedule()`): model chỉ chọn điểm và mức ưu tiên, code xếp thứ tự và tính giờ. Ít lần gọi model hơn, tái lập được. Lượt 1 chạy thiết kế gốc (model tự xếp giờ) để có mốc so sánh.
1. **Đưa danh sách vi phạm cụ thể vào `repair`** (ví dụ "điểm 3 đóng cửa lúc 17:00, bạn đến 17:20"), thay vì chỉ nói "sai". Thường giảm số vòng sửa và chi phí.
2. **Xếp hạng ứng viên theo `like` trước khi gửi model** (code), để model bớt sai cụm xa.
3. **Cải thiện `relax_options`** để mọi ca bất khả thi nêu được cách nới có kiểm chứng.

Không nên làm cùng lúc cả ba: mỗi lượt chỉ đổi một thứ để biết nguyên nhân (rubric chấm "một cải tiến rõ ràng").

## Sau hackathon (nếu làm tiếp)
Xếp theo giá trị cho người dùng so với rủi ro:

| Ưu tiên | Tính năng | Giá trị | Rủi ro và điều kiện |
|---|---|---|---|
| 1 | **Xếp lại giữa ngày** (mưa, điểm đóng cửa, đến muộn) | Cao: đúng lúc nhóm cần nhất | Cần dữ liệu thời tiết; tái dùng `verify` nên rẻ |
| 2 | **Nhiều ngày** (ghép lịch từng ngày, tránh lặp cụm) | Cao | Trạng thái nhiều ngày, ngân sách chung |
| 3 | **Chỗ ở làm ràng buộc** (khách sạn là điểm xuất phát/kết thúc) | Vừa | Cần dữ liệu phòng và giá |
| 4 | **Bỏ phiếu sở thích trong nhóm** (mỗi người nhập, hợp nhất) | Vừa: nhóm 4 người hay bất đồng | Cần giao diện, chuẩn hợp nhất |
| 5 | **Pipeline dữ liệu bán tự động** (nhập địa điểm, kiểm giờ, nhắc quá hạn) | Cao khi mở rộng tỉnh | Phải tuân thủ điều khoản nguồn, không cào bừa |
| 6 | **Đặt chỗ có người duyệt** (soạn tin đặt bàn, người dùng gửi) | Vừa | Hành động ra ngoài: chỉ làm bản nháp chờ duyệt |
| 7 | **Mở rộng tỉnh** (Huế, Quy Nhơn, Hà Giang…) | Cao | Chỉ cần thêm dữ liệu nếu lõi `verify` đã tổng quát |

## Chưa nên làm
- **Giá và giờ mở thời gian thực** qua cào dữ liệu: dễ vi phạm điều khoản, dễ sai, mà giá trị với lát cắt thấp.
- **Gợi ý "quán ngon nhất"**: không có đáp án đúng/sai để đo, dễ thành quảng cáo trá hình.
- **Agent tự do nhiều bước** cho cả việc xếp lịch: tốn tiền, khó tái lập, không hơn workflow có kiểm.
- **Tự động thanh toán / đặt vé**: sai là mất tiền thật, nằm ngoài phạm vi 2 ngày.

## Điểm kiểm cho BGK hỏi vặn
- *Vì sao không dùng solver thay model?* → Solver giải phần xếp thứ tự, nhưng không hiểu "thích yên tĩnh và có chút ăn vặt". Model hiểu ý, code bảo đảm đúng. Nếu Lượt 1 cho thấy model xếp thứ tự rất tệ, **thay phần xếp bằng code** (tiết kiệm token) và để model chỉ lo hiểu sở thích và giải thích. Đó cũng là một cải tiến Lượt 2 hợp lệ.
- *AI đóng góp gì?* → Hiểu yêu cầu tự do, chọn điểm hợp gu, chọn cách nới khi bất khả thi, viết lý do.
- *Lỗi nguy hiểm nhất?* → Lịch trông hợp lệ nhưng dựa trên giờ mở cửa cũ. Chặn: ghi ngày kiểm, nhắc xác nhận lại.
