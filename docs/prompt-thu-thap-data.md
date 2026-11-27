# Prompt giao agent thu thập data Đà Nẵng – Hội An

> Dán nguyên phần trong khung dưới cho agent. Kết quả agent trả về **phải được Đạt kiểm tay** (mở lại nguồn ít nhất 10 dòng) trước khi commit vào `data/`. Ghi số dòng đã kiểm vào `data/DATA_CARD.md`.

---

```
Bạn là trợ lý nghiên cứu. Hãy thu thập dữ liệu CÔNG KHAI về điểm tham quan và quán ăn ở Đà Nẵng (gồm cả Hội An) cho một bản mô phỏng xếp lịch du lịch 1 ngày. Trả về đúng 3 file CSV (UTF-8, dấu phẩy, có dòng tiêu đề, ô có dấu phẩy thì bọc ngoặc kép) và một bản ghi chú ngắn.

## LUẬT BẮT BUỘC
1. Chỉ dùng nguồn công khai: trang chính thức của điểm đến, cổng du lịch Đà Nẵng (danangfantasticity.com), trang Hội An chính thức, trang địa điểm trên Google Maps, trang bán vé chính thức. Mỗi dòng phải có link nguồn cụ thể trong cột `source` và ngày bạn xem trong cột `checked_on` (YYYY-MM-DD).
2. KHÔNG bịa. Không tìm thấy giờ mở cửa hoặc giá thì để trống ô đó và ghi lý do trong ghi chú. Không ước đoán rồi ghi như số thật.
3. KHÔNG chép review, không chép tên người viết review, không chép số điện thoại, không chép ảnh. Không cần cột mô tả.
4. Giờ chuẩn hoá về `HH:MM` 24 giờ. Giá chuẩn hoá về số nguyên VND, không dấu chấm, không chữ "đ". Miễn phí ghi `0`.
5. Nếu một nguồn mâu thuẫn với nguồn khác, ưu tiên trang chính thức và ghi cả hai trong ghi chú.

## FILE 1: places.csv (30–40 dòng)
Cột theo đúng thứ tự:
id,name,kind,cluster,tags,open_windows,closed_days,visit_min,price_pp,price_basis,best_windows,event_days,lat,lon,source,checked_on

- id: `DN-` + 3 số, đánh từ DN-001, không trùng.
- name: tên thường gọi.
- kind: một trong `tham_quan` · `an` · `cafe`.
- cluster: một trong 5 cụm:
  `my_khe` (biển Mỹ Khê – Ngũ Hành Sơn) · `son_tra` (bán đảo Sơn Trà) · `trung_tam` (trung tâm, hai bờ sông Hàn) · `ba_na` (Bà Nà Hills, cụm xa) · `hoi_an` (phố cổ Hội An, cụm xa).
- tags: chọn từ danh sách sau, nối bằng `;`, không tự thêm tag mới:
  bien, hai_san, chay, an_vat, cho, dac_san, cafe, check_in, van_hoa, tam_linh, thien_nhien, trong_nha, yen_tinh, soi_dong
- open_windows: các khoảng mở cửa trong ngày, nối bằng `;`. Ví dụ quán nghỉ trưa: `07:00-11:00;13:30-21:00`. Mở 24 giờ: `00:00-23:59`.
- closed_days: ngày nghỉ cố định trong tuần, 0 = Thứ Hai … 6 = Chủ Nhật, nối bằng `;`. Mở mọi ngày thì để trống.
- visit_min: số phút ở lại hợp lý tối thiểu (số nguyên). Quán ăn thường 45–60, bảo tàng 60–90, Bà Nà ≥ 300.
- price_pp: giá vé người lớn hoặc giá một suất ăn trung bình cho 1 người, VND. Với quán ăn, lấy mức giá món chính phổ biến ghi trên trang hoặc thực đơn công khai.
- price_basis: `moi_nguoi` (hầu hết) hoặc `ca_nhom` (tính một lần cho cả nhóm).
- best_windows: (tuỳ chọn) khung giờ nên ghé, ví dụ giờ Cầu Rồng phun lửa phun nước.
- event_days: (tuỳ chọn) ngày có sự kiện, cùng định dạng closed_days.
- lat, lon: độ thập phân, 4 chữ số sau dấu phẩy, lấy từ Google Maps.

Phân bổ:
- 16–20 điểm `tham_quan` + 14–20 quán `an` / `cafe`.
- Mỗi cụm ≥ 4 dòng. `ba_na` ít nhất 1 điểm. `hoi_an` ≥ 2 điểm tham quan + ≥ 2 quán ăn (có ít nhất 1 quán mở buổi tối).

PHẢI CÓ các dòng sau (bộ câu thử cần):
a. Bảo tàng Điêu khắc Chăm Đà Nẵng: giờ mở cửa và ngày nghỉ (nếu có) theo trang chính thức.
b. Chợ Hàn: giờ mở và giờ đóng cửa theo nguồn.
c. Cầu Rồng: điểm miễn phí, có `best_windows` (giờ phun lửa phun nước) và `event_days` (các ngày có biểu diễn) theo nguồn chính thức.
d. Ít nhất 1 chợ đêm có giờ mở buổi tối (ví dụ chợ đêm Sơn Trà hoặc chợ đêm Hội An).
e. Bà Nà Hills: giá vé cáp treo người lớn theo trang bán vé chính thức (ghi rõ đó là mức giá nào, ngày nào), visit_min ≥ 300.
f. Ngũ Hành Sơn, bán đảo Sơn Trà (chùa Linh Ứng), bãi biển Mỹ Khê, phố cổ Hội An.
g. ≥ 4 quán có tag `chay` và KHÔNG có tag `hai_san`, trong đó ≥ 2 quán mở buổi trưa và ≥ 2 quán mở buổi tối.
h. ≥ 4 quán có tag `hai_san`.
i. ≥ 3 quán giá ≤ 50000 đ/người, và ≥ 3 điểm miễn phí (price_pp = 0) NẰM CÙNG MỘT CỤM.
j. ≥ 1 quán có giờ nghỉ trưa (open_windows có 2 khoảng).
k. ≥ 1 quán chỉ mở buổi tối (mở từ 16:00 trở đi).
l. ≥ 1 điểm có ngày nghỉ cố định trong tuần.
m. Có đủ ít nhất 1 dòng cho mỗi tag trong danh sách tag.
n. KHÔNG thêm quán nào tên "Bún chả cá Cô Bảy Hòa Khánh".

## FILE 2: travel_override.csv (6–10 dòng)
Cột: from_id,to_id,minutes,source,checked_on
- Thời gian LÁI XE (ô tô / xe công nghệ) giữa hai điểm, tra trên Google Maps vào khung giờ ban ngày không cao điểm, số nguyên phút.
- Ưu tiên các cặp: trung tâm ↔ Bà Nà, trung tâm ↔ Hội An, Bà Nà ↔ Hội An, trung tâm ↔ đỉnh Sơn Trà / chùa Linh Ứng, Mỹ Khê ↔ Hội An, Ngũ Hành Sơn ↔ Hội An.
- from_id, to_id dùng đúng id trong places.csv. Ghi một chiều là đủ.
- source: link chỉ đường Google Maps hoặc ghi "Google Maps chỉ đường, xem ngày X".

## FILE 3: transport_rates.csv (2–3 dòng)
Cột: mode,base_vnd,per_km_vnd,per_day_vnd,source,checked_on
- `grab`: giá mở cửa và giá mỗi km của xe công nghệ 4 chỗ ở Đà Nẵng, theo trang giá công khai. Để trống per_day_vnd.
- `xe_may`: giá thuê xe máy một ngày phổ biến ở Đà Nẵng, theo ít nhất 1 trang tiệm cho thuê công khai. Để trống base_vnd, per_km_vnd.
- (tuỳ chọn) `grab_bike` nếu có bảng giá công khai.

## GHI CHÚ TRẢ KÈM (dạng danh sách ngắn)
- Mỗi yêu cầu a–n: đã có ở id nào, hoặc chưa tìm được và vì sao.
- Các ô bị để trống và lý do.
- Các chỗ nguồn mâu thuẫn.
- Các giá trị dễ thay đổi theo mùa (vé Bà Nà, giờ cầu Rồng…), ghi rõ mức bạn đã chọn.
```

---

## Sau khi agent trả kết quả
1. Đạt mở lại nguồn của **≥10 dòng** (bắt buộc kiểm a, b, c, e) và sửa chỗ sai. Ghi "đã kiểm x/N dòng" vào `DATA_CARD.md`.
2. Giá trị nhóm tự đặt để tạo ca khó thì sửa cột `source` thành `synthetic: <lý do>`.
3. Báo Quân: giá vé Bà Nà thật (K10) và có xếp được K08 trong 250k hay không, để chỉnh câu thử **trước khi chạy Lượt 1**. Chuẩn "đạt" ở §7 thì không được sửa.
4. Điền số dòng, ngày lấy vào `DATA_CARD.md`, rồi commit `data/places.csv`, `data/travel_override.csv`, `data/transport_rates.csv`.
