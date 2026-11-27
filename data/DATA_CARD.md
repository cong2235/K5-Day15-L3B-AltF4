# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

**Trạng thái (27/11, bản đầu CP2):** đã chốt cột, định dạng và cách lấy dữ liệu. `places.csv` đang được dựng; số dòng và ngày kiểm điền khi commit file. Chủ file: Đạt.

## Phạm vi địa lý
Đà Nẵng **gồm cả Hội An**. 5 cụm, ghi ở cột `cluster`: `my_khe` (Mỹ Khê – Ngũ Hành Sơn), `son_tra`, `trung_tam`, `ba_na` (cụm xa), `hoi_an` (cụm xa).

## Dataset 1 · `data/places.csv` — điểm tham quan và quán ăn

| | |
|---|---|
| Dùng để làm gì | Nguồn duy nhất về địa điểm, giờ mở cửa, giá cho các công cụ `shortlist`, `get_place`, `verify`, `cost`, `travel_min`. Ràng buộc đúng `c=` trong `eval/benchmark.csv` được chấm trên file này. Không dùng làm bằng chứng pain |
| Từ đâu | Nhóm tự nhập tay từ thông tin công khai: trang chính thức của điểm đến, cổng du lịch Đà Nẵng, trang địa điểm trên bản đồ trực tuyến. Không chép review: mỗi dòng tối đa 2 câu mô tả do nhóm tự viết |
| Xử lý những bước gì | Chọn 25–40 điểm trải đều 5 cụm (15–20 điểm tham quan, 12–18 quán / cafe) · chuẩn hoá giờ về `HH:MM`, giá về VND · gắn tag theo danh sách dưới · mỗi dòng ghi `source` và `checked_on` · thêm ca khó cố ý (xem "Giới hạn"). Nhập tay, không có script |
| Số dòng | __ *(mục tiêu 25–40; điền khi commit)* |
| Phiên bản / ngày lấy | v0 · __/11/2026 *(ngày kiểm ghi riêng từng dòng ở `checked_on`)* |
| Nhãn | Thật: dòng có `source` là nguồn công khai. `synthetic`: giá trị nhóm tự đặt để tạo ca khó, cột `source` ghi `synthetic: <lý do>` |
| Giới hạn | Giá và giờ là **tham khảo** tại ngày `checked_on`, không cập nhật thời gian thực, nên output luôn nhắc người dùng xác nhận lại. Không có dữ liệu thời tiết, giờ cao điểm hay mùa lễ hội. Thiên về điểm nổi tiếng, ít quán nhỏ trong hẻm. Giá vé đổi theo mùa (Bà Nà) chỉ lấy một mức |

**Cột** (khớp `Place` ở `docs/design.md` mục 5). Cột "Ví dụ" chỉ minh hoạ định dạng, không phải dữ liệu của điểm nào:

| Cột | Định dạng | Ví dụ |
|---|---|---|
| `id` | `DN-` + 3 số, duy nhất | `DN-014` |
| `name` | tên thường gọi | Quán A |
| `kind` | `tham_quan` · `an` · `cafe` | `tham_quan` |
| `cluster` | 1 trong 5 cụm ở trên | `trung_tam` |
| `tags` | nối bằng `;` | `van_hoa;trong_nha` |
| `open_windows` | các khoảng `HH:MM-HH:MM` nối bằng `;` | `07:00-11:00;13:30-21:00` |
| `closed_days` | số nối bằng `;`, 0 = Thứ Hai … 6 = Chủ Nhật; để trống nếu mở mọi ngày | `0` |
| `visit_min` | số phút ở lại tối thiểu | `60` |
| `price_pp` | VND, 0 nếu miễn phí | `60000` |
| `price_basis` | `moi_nguoi` · `ca_nhom` | `moi_nguoi` |
| `best_windows` | (tuỳ chọn) khung giờ nên ghé, như `open_windows` | `21:00-21:30` |
| `event_days` | (tuỳ chọn) ngày có sự kiện, như `closed_days` | `5;6` |
| `lat`, `lon` | độ thập phân | `16.0610`, `108.2234` |
| `source` | link, tên nguồn, hoặc `synthetic: …` | |
| `checked_on` | `YYYY-MM-DD` | `2026-11-27` |

**Tag dùng chung:** `bien`, `hai_san`, `chay`, `an_vat`, `cho`, `dac_san`, `cafe`, `check_in`, `van_hoa`, `tam_linh`, `thien_nhien`, `trong_nha`, `yen_tinh`, `soi_dong`. Thêm tag mới thì ghi vào đây trước.

**Ca khó cố ý mà bộ câu thử cần** (chi tiết `docs/discovery.md` mục 6.3): điểm nghỉ 1 ngày trong tuần (K06, T07) · quán nghỉ trưa · quán chỉ mở tối · Chợ Hàn có giờ đóng cửa theo nguồn (K14) · Bà Nà vé đắt, ở lâu, đi xa (K01, K10) · Hội An có điểm và quán ăn tối (K11) · đủ quán chay không hải sản (K07) · quán ≤ 50.000đ/người và điểm miễn phí (K08) · cầu Rồng có `best_windows` / `event_days` (T05). **Không** có quán tên "Bún chả cá Cô Bảy" (K13).

## Dataset 2 · `data/travel_override.csv` — thời gian di chuyển ghi đè

| | |
|---|---|
| Dùng để làm gì | Ghi đè `travel_min` cho các cặp điểm mà ước tính từ tọa độ sai nhiều (đường đèo, qua sông, cụm xa) |
| Từ đâu | Nhóm tra thời gian lái xe trên bản đồ trực tuyến, ghi `source` và `checked_on` từng dòng |
| Xử lý những bước gì | Cột `from_id`, `to_id`, `minutes`, `source`, `checked_on`. Áp cho cả hai chiều. Ưu tiên các cặp có Bà Nà, Hội An, đỉnh Sơn Trà |
| Số dòng | __ *(dự kiến 5–10)* |
| Phiên bản / ngày lấy | v0 · __/11/2026 |
| Nhãn | Thật (tra thủ công), một lần tra cho mỗi cặp |
| Giới hạn | Cặp không có trong file thì `travel_min` **ước tính** từ tọa độ: khoảng cách đường chim bay × hệ số đường vòng ÷ tốc độ đô thị ước tính (tham số ghi trong code). Đây là **ước tính, không phải số đo thật**, và phải ghi như vậy trong output và slide. Không tính tắc đường giờ cao điểm |

## Dataset 3 · `data/transport_rates.csv` — đơn giá đi lại

| | |
|---|---|
| Dùng để làm gì | Đơn giá cho `transport_cost`. Ngân sách của người dùng gồm vé + ăn + di chuyển, nên `cost` và `OVER_BUDGET` cộng cả tiền đi lại giữa các điểm |
| Từ đâu | Bảng giá công khai của xe công nghệ (`grab`, theo km) và tiệm thuê xe máy (`xe_may`, theo ngày). Mỗi dòng ghi `source` và `checked_on` |
| Xử lý những bước gì | Cột `mode`, `base_vnd`, `per_km_vnd`, `per_day_vnd`, `source`, `checked_on` (`docs/design.md` mục 7). Km lấy từ tọa độ × hệ số đường vòng, cùng cách với `travel_min` |
| Số dòng | 2–3 |
| Phiên bản / ngày lấy | v0 · __/11/2026 |
| Nhãn | **(tự ước tính)**: giá thật đổi theo giờ, thời tiết và khuyến mãi; bảng chỉ lấy một mức |
| Giới hạn | Không tính giá giờ cao điểm hay phụ phí đêm. Tiền đi lại trong output là ước tính, phải ghi như vậy |

## Dataset 4 · `eval/benchmark.csv` — bộ câu thử

| | |
|---|---|
| Dùng để làm gì | Chạy `python run.py eval`, chấm theo `eval/metric_spec.yaml` |
| Từ đâu | 30 câu `tu_viet` theo lưới 5 chiều ở `docs/discovery.md` mục 6.1. Trước CP3 thêm câu `nguoi_dung`: chép nguyên văn từ câu Q9 phỏng vấn và S7 khảo sát, không sửa lời |
| Xử lý những bước gì | Mỗi câu ghi status được chấp nhận và ràng buộc đúng (`status=…; c=…`) ở đầu `pass_criterion` |
| Số dòng | 30 (thuong 9 · kho 15 · tu_choi 6) |
| Phiên bản / ngày lấy | CP2 · 27/11/2026 |
| Nhãn | `tu_viet` cả 30 câu. Câu do nhóm tự viết **không phải bằng chứng pain** |
| Giới hạn | Chưa có câu từ người dùng thật (0/30, khung đòi ≥ 1/3). Câu tự viết có thể sạch và chuẩn hơn cách người thật gõ |

**Data `synthetic` (nhóm tự sinh):** chỉ là các giá trị ca khó trong `places.csv`, có nhãn ở cột `source`. Không sinh bằng model, không có seed. Người kiểm tay: __ · số dòng đã kiểm: __/__. Data tự dựng **không phải bằng chứng pain**.

**Dữ liệu test của code** (`tests/places_fixture.csv`, Đức giữ): 6–8 dòng tự đặt, toàn bộ `synthetic`, chỉ để test `verify` và `cost`, không dùng khi chạy eval.
