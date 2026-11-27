---
name: web-visual-qa
description: Chụp màn hình website ở các độ rộng màn máy tính bằng Chrome/Edge headless rồi tự xem ảnh để kiểm bố cục, chữ tiếng Việt, độ tương phản và lỗi hiển thị. Dùng sau mỗi lần sửa giao diện trong web/, trước khi báo "xong" hoặc "đã đẹp", hoặc khi người dùng hỏi trang trông thế nào.
---

# Kiểm giao diện bằng ảnh chụp thật

"Code chạy" không có nghĩa là "trang đẹp". Phải nhìn ảnh chụp rồi mới kết luận.

## 1. Chụp

```bash
python .claude/skills/web-visual-qa/scripts/screenshot.py web/index.html
# tùy chọn:
#   --widths 1366,1440,1920   (mặc định)
#   --height 900              chiều cao khung nhìn đầu tiên
#   --full                    chụp thêm một ảnh rất cao để thấy cả trang
#   --full-height 6000        chiều cao ảnh --full (tăng nếu trang dài hơn)
#   --query id=my-khe         thêm chuỗi truy vấn (trang dựng bằng JS theo ?id=)
#   --out <thư mục>           mặc định: thư mục tạm của hệ thống
```

Script tự mở một server tĩnh tại thư mục chứa trang (để đường dẫn tương đối, font và ảnh tải đúng), tìm Chrome hoặc Edge, chụp ở từng độ rộng rồi in ra đường dẫn các file PNG. Sau đó **dùng Read để mở từng ảnh** và xem.

## 2. Nhìn gì trong ảnh

**Khung nhìn đầu tiên (1440×900)** là quan trọng nhất:
- [ ] Trong 3 giây có hiểu đây là trang về Đà Nẵng không?
- [ ] Tiêu đề hero đọc rõ trên ảnh, không đè lên chi tiết chính của ảnh.
- [ ] Có một điểm nhìn chính, không có ba thứ cùng giành sự chú ý.

**Toàn trang:**
- [ ] Dấu tiếng Việt đầy đủ, không bị cắt ở đầu dòng hay chữ hoa, không có ô vuông thay ký tự, không rơi về font dự phòng (nét chữ khác hẳn phần còn lại).
- [ ] Không có chữ tràn khỏi khung, không có thanh cuộn ngang.
- [ ] Nhịp khoảng trắng đều giữa các section, lề trái của chữ thẳng hàng theo lưới.
- [ ] Ảnh không bị méo, không có khối trống vì ảnh hỏng.
- [ ] 1920px: nội dung không bị kéo dãn quá rộng (dòng chữ ≤ ~75 ký tự).
- [ ] 1366px: không bị chật, không có cột bị bóp còn 2–3 chữ mỗi dòng.
- [ ] Không có dấu hiệu "mẫu AI chung chung": ba thẻ đều nhau, gradient tím, icon emoji.

Chỉ ra lỗi cụ thể kèm vị trí (section nào, độ rộng nào), sửa, chụp lại. Lặp cho đến khi danh sách trên sạch.

## 3. Kiểm thêm không cần ảnh

- Tương phản: tính tỉ lệ cho từng cặp màu chữ/nền chính trong token. Chữ thường cần ≥ 4.5:1, chữ lớn ≥ 3:1. Chữ đặt trên ảnh thì kiểm trên phần tối nhất và sáng nhất của lớp phủ.
- Bàn phím: mọi link và nút có `:focus-visible` nhìn thấy được.
- `prefers-reduced-motion`: có khối CSS tắt hiệu ứng.
- Link và ảnh hỏng: `grep -o 'src="[^"]*"' web/*.html` rồi kiểm từng file có tồn tại.
- Muốn đánh giá sâu hơn thì dùng thêm skill `design:design-critique` (bố cục, thứ bậc) và `design:accessibility-review` (WCAG).

## 4. Báo kết quả

Báo cho người dùng: đã chụp ở độ rộng nào, đường dẫn đầy đủ tới ảnh, những gì đã sửa, những gì còn tồn tại. Không viết "trang đã hoàn hảo".
