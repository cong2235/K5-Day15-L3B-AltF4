---
name: vietnamese-web-content
description: Quy tắc viết nội dung tiếng Việt, kiểm chứng thông tin và dùng ảnh có bản quyền cho website giới thiệu Đà Nẵng. Dùng khi viết hoặc sửa chữ trên trang (tiêu đề, đoạn giới thiệu, chú thích ảnh, alt text, nút), khi thêm ảnh hoặc video, hoặc khi đưa số liệu và sự kiện về Đà Nẵng lên trang.
---

# Nội dung tiếng Việt cho website Đà Nẵng

Trang đẹp mà sai thông tin hoặc dùng ảnh trái phép thì vẫn hỏng. Luật của repo (`AGENTS.md`) vẫn áp dụng ở đây: **không bịa** số liệu, trích dẫn hay con người.

## 1. Giọng văn

- Gợi hình, cụ thể, câu ngắn. Ví dụ: "Sáng sớm, thúng chai neo kín bờ Mỹ Khê" thay vì "Đà Nẵng là thành phố tuyệt vời với nhiều cảnh đẹp".
- Mỗi đoạn tối đa 3–4 câu. Tiêu đề section từ 2 đến 6 chữ.
- Tránh sáo ngữ: "thiên đường", "điểm đến không thể bỏ qua", "hòa quyện hoàn hảo", "khám phá ngay". Mỗi trang dùng các cụm này nhiều nhất một lần.
- Xưng hô: dùng "bạn" với người đọc. Giữ một cách xưng hô cho cả trang.
- Viết hoa theo quy tắc tiếng Việt: chỉ viết hoa chữ đầu câu và tên riêng ("Bán đảo Sơn Trà", không viết "Bán Đảo Sơn Trà"). Không viết hoa toàn bộ câu dài; nếu cần hiệu ứng chữ in hoa thì dùng CSS `text-transform` cho nhãn ngắn.

## 2. Tên riêng: viết thống nhất

Mỹ Khê · Bán đảo Sơn Trà · Ngũ Hành Sơn · Làng đá mỹ nghệ Non Nước · Đèo Hải Vân · Bà Nà · Cầu Rồng · Cầu sông Hàn · Chùa Linh Ứng · Bảo tàng Điêu khắc Chăm · Phố cổ Hội An · Chợ Hàn · Chợ Cồn · Sông Hàn · Mì Quảng · Bánh tráng cuốn thịt heo · Bún chả cá · Cao lầu.

Khi thêm tên mới thì bổ sung vào danh sách này để cả trang viết giống nhau.

## 3. Kiểm chứng sự kiện

Mọi câu có **số, năm, danh hiệu, kỷ lục, lịch sự kiện, giá vé, giờ mở cửa** phải có nguồn.

- Ghi nguồn vào `web/content/sources.md` theo dạng: `câu trên trang | nguồn (URL hoặc tài liệu) | ngày kiểm`.
- Chưa có nguồn thì không đưa câu đó lên trang, hoặc đánh dấu `<!-- CẦN KIỂM NGUỒN -->` trong HTML và báo người dùng.
- Ưu tiên nguồn chính thức: cổng thông tin của thành phố, sở du lịch, UNESCO, bảo tàng.
- Những điểm dễ sai cần kiểm lại: địa giới hành chính (Hội An và phần đất Quảng Nam cũ thuộc Đà Nẵng từ khi nào, theo văn bản nào), lịch phun lửa của cầu Rồng, năm UNESCO công nhận các di sản, tên loài voọc ở Sơn Trà, giờ mở cửa và giá vé.
- Không viết trích lời của người dân nếu không phỏng vấn thật. Khối "Con người" có thể kể bằng ảnh và mô tả nghề, không cần trích lời giả.

## 4. Ảnh và video

- Chỉ dùng ảnh có giấy phép rõ ràng: ảnh nhóm tự chụp, Unsplash/Pexels (đọc giấy phép), Wikimedia Commons (ghi đúng tác giả và giấy phép CC). Ghi vào `web/content/credits.md`: tệp · tác giả · nguồn · giấy phép.
- Tải ảnh về `web/assets/img/` rồi nén. Không hotlink ảnh từ trang khác.
- Không dùng ảnh AI tạo ra mà giới thiệu như ảnh thật của một địa danh. Nếu dùng ảnh minh họa thì ghi rõ trong chú thích là "minh họa".
- Chụp người rõ mặt thì cần sự đồng ý của người đó. Ảnh tư liệu thì ghi nguồn.
- Chưa có ảnh thật thì dùng khối giữ chỗ có màu từ token, ghi tên ảnh cần tìm (ví dụ: "Ảnh: bình minh Mỹ Khê, ngang, ≥ 2400px"). Không lấy ảnh ngẫu nhiên.

## 5. Alt text và chú thích

- `alt` mô tả nội dung ảnh bằng tiếng Việt, 8–20 chữ: `alt="Thúng chai neo trên bãi Mỹ Khê lúc bình minh"`. Ảnh trang trí thì để `alt=""`.
- `figcaption` gồm địa danh và tác giả: `Bãi Mỹ Khê · Ảnh: Nguyễn Văn A / Unsplash`.

## 6. Kỹ thuật chữ tiếng Việt

- Lưu file UTF-8. Dùng ký tự dựng sẵn (NFC). Nếu chép chữ từ PDF hay Word mà dấu bị tách rời thì chuẩn hóa lại bằng `unicodedata.normalize("NFC", s)`.
- Ngăn ngắt dòng xấu: dùng `&nbsp;` giữa số và đơn vị (`1&nbsp;000&nbsp;m`), giữa từ ngắn cuối tiêu đề. Có thể dùng `text-wrap: balance` cho tiêu đề và `text-wrap: pretty` cho đoạn văn.
- Không dùng `letter-spacing` âm cho chữ có dấu ở cỡ nhỏ. Dấu sẽ dính vào nhau.
- Định dạng số theo kiểu Việt Nam: `1.000.000 đ`, ngày `27/11/2026`.
