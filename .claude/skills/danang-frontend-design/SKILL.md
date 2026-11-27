---
name: danang-frontend-design
description: Định hướng thẩm mỹ và hệ thiết kế cho website tiếng Việt giới thiệu thiên nhiên, văn hóa, con người Đà Nẵng (bản máy tính). Dùng TRƯỚC khi viết hoặc sửa bất kỳ HTML/CSS/JS nào của website, khi chọn màu, font, bố cục, hiệu ứng, hoặc khi được yêu cầu "làm đẹp", "thiết kế lại", "trang chủ", "hero", "section".
---

# Thiết kế frontend: website Đà Nẵng

Mục tiêu: một trang có **cá tính riêng**, không phải mẫu landing page chung chung. Người xem phải thấy biển, đá, đèn lồng, nắng miền Trung ngay trong màu, chữ và nhịp bố cục. Mỗi section chỉ nên có một ý.

## 0. Trước khi code

1. Đọc skill `vietnamese-web-content` để biết quy tắc nội dung, nguồn ảnh và kiểm chứng.
2. Chọn **một** hướng thẩm mỹ trong mục 1 và ghi lý do thành 1–2 dòng trong `web/README.md`. Không trộn nhiều hướng.
3. Phác cấu trúc trang (mục 3) trước, sau đó định token (mục 2), rồi mới viết component.
4. Code ở `web/` (HTML + CSS + JS thuần, không cần build). Chỉ thêm framework khi người dùng yêu cầu.

## 1. Chọn một hướng thẩm mỹ

| Hướng | Cảm giác | Font gợi ý (đều có bộ dấu tiếng Việt) | Khi nào chọn |
|---|---|---|---|
| **Tạp chí du lịch** (editorial) | sang, nhiều khoảng trắng, ảnh lớn tràn mép, chữ serif to | Tiêu đề `Playfair Display` hoặc `Cormorant Garamond`; thân `Be Vietnam Pro` | mặc định, hợp nhất với "vẻ đẹp" |
| **Biển và nắng** (coastal modern) | tươi, sáng, khối màu lớn, bo góc mềm | Tiêu đề `Lexend` hoặc `Montserrat` đậm; thân `Be Vietnam Pro` | trang trẻ trung, hướng tới sinh viên |
| **Di sản ấm** (heritage) | giấy dó, vàng tường Hội An, đỏ đèn lồng, họa tiết | Tiêu đề `Lora` hoặc `Noto Serif`; thân `Noto Sans` | nhấn mạnh văn hóa và Hội An |

Kiểm font trước khi dùng: gõ thử "Ngũ Hành Sơn · Sơn Trà · Hội An · Mỹ Khê · ưởng ỗ ợ" ở cỡ lớn. Nếu dấu bị lệch, bị cắt hay rơi về font dự phòng thì bỏ font đó. Google Fonts: thêm `&subset=vietnamese` (API cũ) hoặc kiểm tab "Language" có Vietnamese.

**Không dùng:** Inter/Roboto/Arial làm font tiêu đề, gradient tím xanh, glassmorphism tràn lan, icon emoji thay cho minh họa, ba thẻ đều nhau có icon tròn ở trên, chữ "Khám phá ngay" trên mọi nút.

## 2. Design token (đặt trong `:root`, không hardcode màu rải rác)

Bảng màu lấy từ cảnh thật. Chọn 1 màu chủ, 1 màu nhấn, phần còn lại là nền và trung tính.

```css
:root {
  /* Biển Mỹ Khê */
  --sea-900: #0b3d5c; --sea-600: #1673a3; --sea-300: #7cc4e4;
  /* Cát và nắng */
  --sand-100: #faf5ec; --sand-300: #ead9bd; --sun-500: #f2a541;
  /* Rừng Sơn Trà */
  --forest-700: #2f5d3a;
  /* Đá Ngũ Hành Sơn */
  --stone-500: #8a8378; --ink-900: #1c1a17;
  /* Đèn lồng Hội An */
  --lantern-600: #c8392b; --wall-400: #e7b94c;

  --font-display: "Playfair Display", "Noto Serif", Georgia, serif;
  --font-body: "Be Vietnam Pro", "Noto Sans", system-ui, sans-serif;

  /* Thang chữ cho màn máy tính, tỉ lệ ~1.333 */
  --step-0: 1.125rem;  --step-1: 1.5rem;  --step-2: 2rem;
  --step-3: 2.666rem;  --step-4: 3.555rem; --step-5: clamp(3.5rem, 6vw, 6.5rem);

  --space-1: .5rem; --space-2: 1rem; --space-3: 1.5rem; --space-4: 2.5rem;
  --space-5: 4rem;  --space-6: 6.5rem; --space-7: 10rem;

  --radius: 4px;            /* editorial: gần vuông; coastal: 20px */
  --content: 72rem;         /* bề rộng nội dung chính */
  --measure: 65ch;          /* độ dài dòng đọc */
  --ease-out: cubic-bezier(.22, 1, .36, 1);
}
```

Tiếng Việt có dấu chồng nhiều tầng: `line-height` thân bài ≥ 1.65, tiêu đề ≥ 1.15. Không để `overflow: hidden` cắt mất dấu trên chữ hoa (Ổ, Ặ).

## 3. Cấu trúc trang (bản máy tính, 1280–1920px)

Gợi ý một trang dài có điều hướng neo, thêm trang con nếu nội dung nhiều:

1. **Hero**: một ảnh hoặc video toàn màn hình (bình minh Mỹ Khê, cầu Rồng về đêm). Tiêu đề lớn đặt lệch trái, một câu dẫn, không quá 1 nút. Có lớp phủ tối để chữ đạt độ tương phản.
2. **Thiên nhiên**: biển, bán đảo Sơn Trà, Ngũ Hành Sơn, đèo Hải Vân, Bà Nà. Dùng lưới bất đối xứng (ảnh lớn 7 cột + 2 ảnh nhỏ xếp chồng 5 cột) thay vì 3 thẻ đều nhau.
3. **Văn hóa**: Hội An, Bảo tàng Điêu khắc Chăm, chùa, lễ hội, ẩm thực. Hợp với cuộn ngang hoặc dòng thời gian.
4. **Con người**: chân dung, trích lời (chỉ khi có nguồn thật), nghề biển, thúng chai, làng đá Non Nước. Bố cục kiểu phóng sự: ảnh lớn kèm đoạn văn hẹp.
5. **Ẩm thực** (tùy chọn): mì Quảng, bánh tráng cuốn thịt heo, bún chả cá.
6. **Footer**: nguồn ảnh, nguồn tư liệu, nhóm thực hiện.

Lưới: 12 cột, `gap` từ `--space-3` trở lên, lề hai bên ≥ 5vw. Xen kẽ nhịp: section rộng tràn mép, rồi section hẹp nhiều chữ, rồi lại section rộng. Mỗi section có đủ khoảng thở (`padding-block: var(--space-6)` trở lên).

## 4. Chi tiết tạo điểm nhấn

- **Chữ lớn đè lên ảnh** hoặc tràn qua ranh giới hai section.
- **Số thứ tự kiểu tạp chí** (01 / 02 / 03) cho từng chương.
- **Họa tiết riêng** làm bằng SVG tự vẽ: đường sóng, vòm cầu Rồng, mái ngói, hoa văn Chăm. Dùng làm vạch chia section, độ mờ thấp.
- **Nền có chất liệu**: noise nhẹ (SVG `feTurbulence`) trên màu cát để không bị phẳng.
- **Ảnh**: tỉ lệ cố định (`aspect-ratio`), `object-fit: cover`, có chú thích nhỏ in nghiêng gồm địa danh và tác giả ảnh.
- **Bản đồ minh họa** (SVG tĩnh) đánh dấu vị trí các điểm, không cần bản đồ tương tác.

## 5. Chuyển động

- Hiện dần khi cuộn: `IntersectionObserver` thêm class, CSS lo transition (opacity + translateY 24px, 600–900ms, `--ease-out`). Phần tử cùng nhóm hiện lệch nhau 80–120ms.
- Parallax nhẹ cho ảnh hero (≤ 15% quãng cuộn). Không dùng thư viện nặng nếu chỉ cần chừng này.
- Hover trên ảnh: zoom 1.03–1.05 trong khung `overflow: hidden`.
- **Bắt buộc** tôn trọng `@media (prefers-reduced-motion: reduce)`: tắt parallax, chỉ giữ fade.
- Không tự chạy carousel. Không dùng hiệu ứng làm chậm việc đọc.

## 6. Kỹ thuật bắt buộc

- `<html lang="vi">`, `<meta charset="utf-8">`, HTML ngữ nghĩa (`header`, `nav`, `main`, `section[aria-labelledby]`, `figure/figcaption`, `footer`).
- Ảnh: AVIF/WebP kèm JPEG dự phòng qua `<picture>`, `loading="lazy"` (trừ ảnh hero), có `width`/`height` để không giật bố cục. Ảnh hero ≤ 400 KB.
- Font: `font-display: swap`, chỉ tải các độ đậm thực sự dùng, `preconnect` tới nơi cung cấp font.
- Độ tương phản chữ ≥ 4.5:1 (chữ lớn ≥ 3:1). Có trạng thái `:focus-visible` rõ ràng.
- CSS tổ chức theo thứ tự: token → reset → bố cục → component → tiện ích. Đặt tên class theo BEM hoặc theo section (`.nature__grid`).

## 7. Xong một phần thì kiểm

Sau mỗi section, chạy skill `web-visual-qa` để chụp màn hình ở 1366, 1440 và 1920px rồi **tự xem ảnh**. Không báo "đã đẹp" khi chưa nhìn ảnh chụp.
