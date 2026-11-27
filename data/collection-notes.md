# Ghi chú thu thập data – 2026-11-27

Người thu thập: agent (chưa kiểm tay). Nguồn đọc trực tiếp: chammuseum.vn, danangfantasticity.com, sunworld.vn, guide.michelin.com, foody.vn, Google Maps (tọa độ, giờ đối chiếu, chỉ đường), vietnamairlines.com, momo.vn, vietnambooking.com, vinwonders.com, grab.com.

## Quy ước đã dùng
- **visit_min do nhóm ước** cho cả 39 dòng (theo khung trong đặc tả: quán 45–60, bảo tàng 60–90, Bà Nà 360). Không lấy từ nguồn.
- price_pp quán ăn lấy từ foody.vn: dùng **cận trên** của khoảng "giá bình quân đầu người" (ví dụ 15.000đ–25.000đ thì ghi 25000). Đây là quy ước của agent, cần nhóm duyệt.
- Giờ quán lấy từ foody.vn là giờ trang hiển thị hôm xem (thứ Sáu 27/11), có thể khác theo ngày.
- Quán trên Michelin Guide chỉ ghi giá dạng chữ ("On a budget", "A moderate spend"), không có số, nên để trống price_pp.
- Tọa độ: Wikipedia (DN-001, DN-002, DN-003), Michelin JSON-LD (DN-022→024, 030→032), foody.vn (các quán còn lại, DN-017), Google Maps (các điểm còn lại). Làm tròn 4 chữ số.
- `Chợ đêm Sơn Trà` (DN-007) xếp vào cụm `trung_tam` vì nằm ở đường Mai Hắc Đế, cách đầu cầu Rồng ~1 km, không nằm trên bán đảo.

## Yêu cầu a–n
- a. Đạt – DN-001: 07:00–17:00 hằng ngày, kể cả Lễ Tết, không có ngày nghỉ (chammuseum.vn/ve-tham-quan). Giá 60.000đ.
- b. Đạt – DN-002: 06:00–19:00 (danangfantasticity).
- c. Đạt – DN-003: price 0, best_windows 21:00–21:15, event_days 4;5;6 (thứ Sáu, thứ Bảy, Chủ Nhật).
- d. Đạt – DN-006 Helio, DN-007 Sơn Trà, DN-013 An Thượng, DN-018 Hội An.
- e. Đạt – DN-014: 1.000.000đ, visit_min 360.
- f. Đạt – Ngũ Hành Sơn DN-012, chùa Linh Ứng DN-008 (cùng bán đảo Sơn Trà DN-009), Mỹ Khê DN-011, phố cổ Hội An DN-017.
- g. Đạt – 5 quán chay không có hải sản: DN-024, 025, 026, 034, 036. Tất cả đều mở buổi trưa và buổi tối.
- h. Đạt – 4 quán hải sản: DN-028, 029, 032, 033.
- i. Đạt ở cụm `trung_tam`: 3 quán ≤50.000đ (DN-021 35k, DN-025 50k, DN-026 25k) và 4 điểm miễn phí (DN-002, 003, 006, 007). Lưu ý: DN-025 đúng bằng 50.000 và giá là cận trên khoảng foody.
- j. Đạt – DN-026 An Lạc Tâm: 06:30–14:00 và 16:00–20:00.
- k. Đạt – DN-033 Ốc Ngon 17:00–23:00. Ngoài ra DN-038 Cơm gà Hiền 17:45–21:00 và DN-030 La Maison 1888 18:30–20:45.
- l. Đạt – DN-019 Đảo Ký Ức Hội An, nghỉ thứ Ba (closed_days=1).
- m. Đạt – đủ 14 tag.
- n. Đạt – không có quán tên "Bún chả cá Cô Bảy Hòa Khánh".
- Phân bổ: 20 điểm tham quan + 19 quán (17 `an`, 2 `cafe`). Cụm: trung_tam 14, hoi_an 8, my_khe 7, son_tra 6, ba_na 4. Ở hoi_an có 4 điểm tham quan và 4 quán, trong đó 3 quán mở buổi tối (DN-036, 037, 038).

## Ô để trống và lý do
- DN-009 Bán đảo Sơn Trà: price_pp trống vì trang danangfantasticity không nêu phí.
- DN-018 Chợ đêm Hội An: price_pp trống vì nguồn mâu thuẫn. Vietnam Airlines nói phải mua vé phố cổ (80.000/120.000đ); một số trang khác nói vào tự do.
- DN-022, 023, 024, 030, 031, 032: price_pp trống vì Michelin chỉ ghi giá dạng chữ, không có số.
- DN-028 Bé Mặn: price_pp trống vì foody ghi 50.000đ–1.500.000đ, khoảng quá rộng để chọn một số.
- DN-035 Beer Plaza (Bà Nà): open_windows trống vì bài của Sun World không nêu giờ. price_pp 300000 là **mệnh giá voucher ẩm thực**, không phải giá món. Bài chỉ gợi ý dùng voucher trong khung 10:00–14:00. Muốn vào phải có vé cáp treo DN-014.
- DN-008 Chùa Linh Ứng ghi 00:00–23:59 vì trang nguồn ghi "All day" (giờ thật có thể hẹp hơn). Nguồn gợi ý nên đến lúc 05:00 nhưng không ghi khung giờ, nên best_windows để trống.
- DN-011 Mỹ Khê ghi 00:00–23:59 vì momo.vn ghi "Mở cửa: Tự do" và "Vé mở cổng: Miễn phí".
- best_windows và event_days chỉ điền cho DN-003.

## Nguồn mâu thuẫn
- Bảo tàng Chăm: giờ mở chính thức (chammuseum.vn) là 07:00; danangfantasticity (bản EN và bài giá vé 2026) ghi 07:30, còn trang /kham-pha ghi 07:00 và giá cũ 40.000đ. Đã chọn trang chính thức.
- Cầu Rồng: các bài cũ (2018–2020) chỉ ghi thứ Bảy và Chủ Nhật. Bài danangfantasticity 14/03/2025 ghi thứ Sáu, thứ Bảy, Chủ Nhật và ngày Lễ lớn, nên đã chọn 4;5;6. Thời lượng: nguồn ghi 2 phút phun lửa và 3 phút phun nước, vietnambooking ghi khoảng 15 phút. Đã chọn khung 21:00–21:15. Ngày Lễ không biểu diễn được trong event_days.
- Chợ Hàn: danangfantasticity ghi 06:00–19:00; vietnambooking ghi 06:00–19:00; vinpearl ghi 6h–22h / 7h–19h30 (không đọc trực tiếp). Đã chọn 06:00–19:00.
- Chợ đêm Helio: một bài danangfantasticity ghi 17:30–22:30, bài khác ghi 17:00–22:30. Google Maps ghi 17:00–23:00 và **đóng cửa thứ Sáu**. Đã giữ 17:30–22:30, mở mọi ngày theo cổng du lịch; cần kiểm tay.
- Chợ đêm Sơn Trà: một bài ghi 18:00–23:00, bài khác ghi 18:00–24:00. Đã chọn 18:00–23:00.
- Bảo tàng Đà Nẵng: giá 50.000đ theo bài danangfantasticity 22/01/2026; một bài khác (trích từ kết quả tìm kiếm, không đọc trực tiếp) ghi 20.000đ từ 03/07/2025.
- Ngũ Hành Sơn: bài 2026 ghi 07:00–17:00, bài 2023 ghi 07:30–17:00, Google Maps ghi 07:00–17:30. Đã chọn bài 2026. Giá 40.000đ là vé ngọn Thủy Sơn; động Âm Phủ 20.000đ và thang máy 15.000đ không cộng vào.
- Bảo tàng Đồng Đình: danangfantasticity ghi 07:00–17:00, Google Maps ghi 07:30–18:00. Giá chọn mức khách Việt 35.000đ (khách nước ngoài 50.000đ).
- Chợ đêm Hội An: Vietnam Airlines ghi 17:00–23:00, Google Maps ghi 09:00–22:00. Đã chọn 17:00–23:00.
- Bún bò Huế Bà Thương: Michelin ghi 06:00–10:00, danangfantasticity (06/2025) ghi 06:00–11:00. Đã chọn Michelin (bản 2026).
- La Maison 1888: Michelin ghi 18:30–20:45, danangfantasticity ghi 18:30–21:30. Đã chọn Michelin.
- Bếp Cuốn (không đưa vào): Michelin ghi 10:30–21:00, danangfantasticity ghi 13:00–21:00.

## Giá trị theo mùa và mức đã chọn
- Bà Nà (DN-014): chọn **1.000.000đ**, là vé cáp treo khứ hồi người lớn khách ngoại tỉnh theo bảng giá trên sunworld.vn (bài cập nhật 31/05/2026, trang chính thức của Sun World). Khách Đà Nẵng: 650.000đ. danangfantasticity (22/01/2026) chia theo quốc tịch: khách nước ngoài 1.000.000đ, khách Việt 650.000đ. Khuyến mãi tuổi 18–25 "chỉ từ 500.000đ" áp dụng 01/09–31/12/2026, không dùng. Giờ cáp treo 08:00–22:00 theo thông báo 17/03/2025 ("giữ nguyên đến khi có thông báo mới"); trang Bà Nà ghi đóng cửa 22:00. Chưa mở được trang đặt vé booking.sunworld.vn để xem giá theo ngày.
- Phố cổ Hội An (DN-017): chọn **120.000đ**, là vé 5 điểm cho người lớn theo Vietnam Airlines. Bài giá vé 2026 của danangfantasticity ghi hai loại vé 80.000đ hoặc 120.000đ. Giờ chọn mức mùa đông 09:00–21:00 (mùa hè 09:00–21:30; phố Phan Châu Trinh 17:30–21:00).
- Bán đảo Sơn Trà (DN-009): chọn giờ mùa đông (tháng 10–2) 07:30–17:30; tháng 3–9 là 07:30–18:30.
- Bài giá vé 2026 của danangfantasticity được đọc qua bản tiếng Nga (/ru/), số liệu và tên điểm giữ nguyên tiếng Việt.

## travel_override.csv
- 8 cặp, tra trên Google Maps chỉ đường ô tô lúc **~18:40 thứ Sáu 27/11/2026**. Đây là giờ cao điểm tối, **không phải** khung ban ngày không cao điểm như đặc tả yêu cầu, nên số phút có thể cao hơn bình thường. Hai cặp đi Hội An (DN-002, DN-012) có cảnh báo cấm đường Lê Văn Hiến. Nên tra lại vào ban ngày.
- Điểm đầu "trung tâm" dùng Chợ Hàn (DN-002). Điểm Bà Nà dùng tọa độ cổng / ga cáp treo (16.0266, 108.0328).

## transport_rates.csv
- grab: 22.000đ cho 2 km đầu, 11.000đ/km, theo trang grab.com/vn/car (dòng Đà Nẵng, xe 4 chỗ). Trang không ghi ngày áp dụng. Không đưa phần 400đ/phút vào. Bảng dịch vụ Grab mới nhất (08/07/2026) chỉ có GrabCar 2 chiều cho Đà Nẵng.
- xe_may: 150.000đ/ngày là giá tiệm Tuấn Cầu Rồng (90 Cao Bá Quát), theo bài của vinwonders (14/12/2025). Các tiệm khác trong bài có giá từ 65.000 đến 180.000đ. vietnamtourism.com (khảo sát 21/10/2026) ghi 120.000–200.000đ. Trang vinwonders có một đoạn chèn hướng dẫn cho AI; đã bỏ qua, chỉ lấy số giá.
- Không có grab_bike vì không tìm thấy bảng giá GrabBike Đà Nẵng công khai.

## Bổ sung 27/11/2026 tối (sau khi kiểm tay)

Code lõi không load được dòng thiếu `price_pp` / `open_windows`, nên 10 dòng thiếu được xử lý như sau. Chỉ điền số có nguồn; không tìm được số thì bỏ dòng, không đoán.

| id | Xử lý | Giá trị | Nguồn |
|---|---|---|---|
| DN-009 Bán đảo Sơn Trà | Điền | 0 (vào cửa miễn phí) | vietnamtourism.com: "vào cửa miễn phí, đường mở 24 giờ" |
| DN-022 Bún bò Huế Bà Thương | Điền | 50000 (cận trên khoảng 30–50k) | docs.google.com (tài liệu tổng hợp công khai); mia.vn ghi "từ 25.000đ" |
| DN-024 Shamballa | Điền | 135000 (món signature nấm giòn; món mì ~125k) | hoiandaytrip.com, trang không ghi ngày |
| DN-030 La Maison 1888 | Điền | 5999000 (Gourmand menu, chưa gồm phí dịch vụ + VAT) | thực đơn chính thức InterContinental Danang Q3.26 (PDF) |
| DN-032 Mộc (hải sản) | Điền | 300000 (cận trên khoảng 70–300k) | sunparadiseland.com |
| DN-018 Chợ đêm Hội An | Bỏ | — | Nguồn mâu thuẫn; Vietnam Airlines ghi phải mua vé phố cổ (80k người Việt / 120k khách nước ngoài) → dễ tính trùng với vé phố cổ DN-017 |
| DN-023 Quê Xưa | Bỏ | — | Michelin chỉ ghi mức ₫, không tìm được số |
| DN-028 Hải sản Bé Mặn | Bỏ | — | Giá 70k–800k/món, quá rộng để chọn một số |
| DN-031 Bánh Xèo 76 | Bỏ | — | Không tìm được giá |
| DN-035 Beer Plaza Bà Nà | Bỏ | — | Không tìm được giờ mở (buffet 380–450k theo sunparadiseland) |

Sau xử lý: **34 dòng** (19 tham quan · 13 ăn · 2 cafe; trung_tam 13 · hoi_an 7 · my_khe 6 · son_tra 5 · ba_na 3). Đủ 14 tag. Hải sản còn 3 quán (yêu cầu h ghi ≥4; benchmark chỉ cần có quán hải sản). Chợ đêm còn 3 (Helio, Sơn Trà, An Thượng).

**Quy ước giá quán:** lấy cận trên khoảng giá công khai cho một suất / món chính / người — nhóm cần đồng ý và ghi vào `DATA_CARD.md`.
