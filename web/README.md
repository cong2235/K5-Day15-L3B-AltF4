# Website Đà Nẵng

Trang tiếng Việt cho màn máy tính, giới thiệu thiên nhiên, văn hóa và con người Đà Nẵng. Đây là phần riêng của repo, không liên quan tới code agent trong `codebase/`.

## Mở trang

Nên chạy qua một máy chủ nhỏ, vì nền bản đồ OpenStreetMap có thể từ chối khi trang mở thẳng từ file:

```
python -m http.server 8000 --directory web
```

rồi vào http://localhost:8000. Mở thẳng `web/index.html` thì mọi thứ vẫn chạy, chỉ riêng nền bản đồ có thể không hiện.

## Các trang

| Trang | Nội dung |
|---|---|
| `index.html` | Trang chủ: Thiên nhiên, Văn hóa, Bản đồ, Con người, Ẩm thực, Một ngày |
| `dia-diem.html?id=…` | Trang chi tiết cho 9 điểm: `my-khe`, `son-tra`, `ngu-hanh-son`, `hai-van`, `ba-na`, `hoi-an`, `cham`, `linh-ung`, `cau-rong`. Có mô tả, việc nên làm, lưu ý, bản đồ nhỏ, bộ ảnh, điểm liên quan, nút trước/sau |

Thêm một điểm đến mới chỉ cần thêm một mục vào `assets/js/places.js`. Trang chi tiết và bản đồ tự đọc dữ liệu từ đó.

## Các quyết định thiết kế

| Quyết định | Lý do |
|---|---|
| Phong cách **tạp chí du lịch**: serif lớn (Playfair Display), thân chữ Be Vietnam Pro | Chủ đề là "vẻ đẹp". Cả hai font đều có đủ dấu tiếng Việt |
| Ảnh thật từ **Wikimedia Commons** (CC / CC0), tải về máy, chuyển sang WebP | Giấy phép rõ ràng, có tên tác giả, không hotlink |
| HTML/CSS/JS thuần, không framework, không bước build | Mở là chạy. Script thường (không dùng module) nên mở thẳng từ file vẫn được |
| Bố cục dày kiểu website du lịch: lưới bento, bài chính + danh sách, thực đơn | Bản đầu mỗi phần cao một màn hình, trông như slide trình chiếu |
| Một trang chi tiết dùng chung, dựng từ dữ liệu (`?id=`) | 9 điểm dùng chung một bố cục, sửa một chỗ là đổi cả 9 |
| Bản đồ Leaflet + OpenStreetMap, nền ô bản đồ được lọc màu cho hợp tông trang | Bản đồ thật, miễn phí, có ghi công. Leaflet được tải về `assets/vendor/`, không phụ thuộc CDN |
| Phóng to ảnh bằng `<dialog>`: phím ← → và Esc, tiêu điểm vào nút Đóng | Dùng được bằng bàn phím, chú thích và giấy phép đi theo ảnh |
| Hiệu ứng nhẹ: hiện dần khi cuộn, parallax ảnh hero | Có tôn trọng `prefers-reduced-motion` |

## Cấu trúc

```
web/
  index.html, dia-diem.html
  assets/css/style.css     token màu và chữ ở đầu file
  assets/js/places.js      dữ liệu 9 điểm đến (chữ, ảnh, tọa độ)
  assets/js/place.js       dựng trang chi tiết
  assets/js/map.js         bản đồ trang chủ và bản đồ nhỏ
  assets/js/lightbox.js    phóng to ảnh
  assets/js/main.js        header, hiện dần, mục đang xem, "Một ngày"
  assets/vendor/leaflet/   Leaflet 1.9.4
  assets/img/*.webp        ảnh, xem content/credits.md
  content/credits.md       tác giả và giấy phép từng ảnh
  content/sources.md       câu nào cần nguồn, tọa độ lấy ở đâu
```

## Trước khi công bố

1. Kiểm từng dòng **CẦN KIỂM** trong `content/sources.md`.
2. Chụp lại giao diện bằng skill `web-visual-qa`:
   `python .claude/skills/web-visual-qa/scripts/screenshot.py web/index.html --full --full-height 9000`
   `python .claude/skills/web-visual-qa/scripts/screenshot.py web/dia-diem.html --query id=hoi-an --full --full-height 4200`
