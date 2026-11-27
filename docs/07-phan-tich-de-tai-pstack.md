# 07 · Phân tích đề tài (Track C, lịch trình 1 ngày vừa ngân sách) theo phương pháp pstack

> **Ghi chú phạm vi (27/11):** tài liệu này soạn trước khi chốt tỉnh. Phạm vi hiện tại là **Đà Nẵng gồm cả Hội An** (cụm xa). Đọc cùng [discovery.md](discovery.md) và [design.md](design.md).

Phương pháp lấy từ 3 skill của pstack (`reframe`, `principle-attack-the-premise`, `principle-exhaust-the-design-space`). Skill chưa gọi được bằng lệnh trong phiên này, nên tôi đọc `SKILL.md` và làm theo từng bước. Skill `interrogate` cần chạy mã thật, không dùng được cho đề tài chưa có code.
Phần thuật ngữ chưa kiểm link nguồn, nên tôi không kèm trích dẫn.

## 1. Reframe — đề tài có thể là bài toán nào?
Mô tả "đi tỉnh lạ không biết đi đâu, ăn gì, ở đâu vừa kinh phí" có thể là 3 bài khác nhau:

| Bài toán | Thuật ngữ | Dấu hiệu nhận biết |
|---|---|---|
| A. Thiếu thông tin | discovery | Người dùng không biết có gì. Nói "không biết nên đi đâu" |
| B. Không xếp được lịch khả thi | **Tourist Trip Design Problem (TTDP)** | Có danh sách rồi mà vẫn lệch giờ, đi vòng, vượt tiền |
| C. Không tin nguồn | trust / curation | Lục nhiều bài vẫn nghi quảng cáo, review ảo |

**Tôi chọn B làm lõi.** Lý do: A đã có sẵn (Google Maps, listicle, TikTok) nên khó khác biệt. B là phần các app ít làm kỹ và **kiểm được bằng code**, hợp rubric đo đạc. C đáng làm làm điểm cộng ("lý do chọn" kèm nguồn).

### Thuật ngữ nên dùng (xếp theo mức đổi cách làm)
1. **Tourist Trip Design Problem (TTDP):** bài toán chọn và sắp thứ tự điểm đến theo sở thích, thời gian, ngân sách. Đây là tên đúng của lát cắt.
2. **Orienteering Problem with Time Windows (OPTW):** dạng toán của TTDP: tối đa hóa "độ hợp" trong tổng thời gian, mỗi điểm có khung giờ mở cửa. Hệ quả: **phần xếp lịch nên giao cho code/solver, không giao cho model**.
3. **Time window / slack time:** khung giờ mở cửa và thời gian dư giữa hai điểm. Dùng để kiểm "đến nơi quán đã đóng".
4. **Travel-time matrix:** bảng thời gian di chuyển giữa mọi cặp điểm. Thiếu bảng này thì mọi lịch đều chỉ là đoán.
5. **Constraint extraction:** dùng model biến câu nói tự nhiên ("tụi mình thích cà phê view đẹp, 500k/người") thành tham số có cấu trúc. Chỗ AI thật sự đáng giá.
6. **Generate-and-verify (LLM-modulo):** model đề xuất, bộ kiểm bằng code duyệt, sai thì sửa lại. Đây là kiến trúc ứng viên cho CP2.
7. **Grounding / tool use:** model chỉ được dùng điểm, giá, giờ có trong dữ liệu. Ngược lại là **hallucinated POI** (bịa quán, bịa giá).
8. **Infeasibility explanation / constraint relaxation:** khi không xếp được, nói rõ nới cái nào (tăng tiền, bớt điểm). Đề C1 của BTC yêu cầu đúng điều này.
9. **Plan repair / replanning:** xếp lại phần còn lại khi mưa hoặc điểm đóng cửa. Để dành cho Lượt 2.
10. **Preference elicitation / cold-start:** hỏi lại đúng 1–2 câu khi thiếu thông tin, vì người dùng mới chưa có lịch sử.

### Ngành láng giềng giải cùng bài toán
- **Vận tải (vehicle routing with time windows):** mang sang được cách mã hóa khung giờ và bộ kiểm khả thi. Lệch ở chỗ ở đây có "độ hợp sở thích" mềm, không chỉ chi phí.
- **Lập lịch bệnh viện / nhân sự (constraint satisfaction):** mang sang được tư duy ràng buộc cứng và mềm, và cách giải thích "không xếp được vì...". Lệch ở chỗ ràng buộc du lịch thay đổi theo mưa và đám đông.

### Điều chưa nói trong mô tả mà nên quan tâm
- **Mùa và thời tiết**, **giờ cao điểm** (ảnh hưởng thời gian di chuyển).
- **Nguồn dữ liệu và độ cũ:** giá, giờ mở cửa thay đổi, nên mỗi sự kiện cần có ngày kiểm.
- **Ai chịu rủi ro khi sai:** nhóm bạn tốn tiền và công đi vô ích.

## 2. Attack the Premise — tiền đề nào cần kiểm trước khi code
Tiền đề trong bài toán hiện tại: **"người dùng không biết nên đi đâu, ăn gì nên cần gợi ý."**
Đây chính là bài A, và có thể sai: thông tin tràn ngập, nên có thể nỗi đau thật nằm ở chỗ khác.

**Quan sát nếu tiền đề SAI:**
- Trong ≥3 phỏng vấn và 20 khảo sát, người ta nói *"biết có nhiều chỗ nhưng không biết xếp sao cho khỏi đi vòng / hết giờ / vượt tiền"* hoặc *"không biết tin bài nào"* thay vì *"không biết có gì"*.
- Review công khai than phiền về **đóng cửa, đi xa, giá lệch quảng cáo** nhiều hơn than "không biết đi đâu".

**Cách kiểm (làm tối nay, trước khi chốt `spec.md §4`):** mỗi người hỏi 1 người câu "kể lần gần nhất bạn đi tỉnh lạ, bạn đã mất bao lâu để lên kế hoạch, chỗ nào không như dự tính?" (Mom Test, không hỏi ý kiến về ý tưởng). Đếm: bao người nhắc **lệch lịch/giờ/tiền** so với **thiếu thông tin** so với **không tin nguồn**. Kết quả quyết định lát cắt:
- Lệch lịch nhiều → giữ lát cắt hiện tại (bài B).
- Không tin nguồn nhiều → đổi trọng tâm sang "lý do chọn có nguồn" (bài C).
- Thiếu thông tin nhiều → đề tài yếu vì app có sẵn đã giải, cân nhắc đổi.

## 3. Exhaust the Design Space — 3 kiến trúc để chọn ở CP2
| | (1) Model làm hết trong 1 lần | (2) Model đề xuất + code kiểm, lặp | (3) Model trích ràng buộc → solver xếp → model giải thích |
|---|---|---|---|
| Giờ mở cửa, tiền | Model tự nhẩm, dễ sai | Code kiểm, **0 vi phạm đo được** | Solver bảo đảm đúng theo cấu trúc |
| Độ khó 10 giờ | Thấp | Vừa | Cao (cần solver, dữ liệu sạch) |
| Chi phí/task | Thấp (1 lần gọi) | Cao hơn (mỗi vòng thêm 1 lần gọi) | Thấp–vừa (2 lần gọi) |
| Hợp rubric "workflow hay agent" | Yếu: không đo được | **Mạnh: Lượt 1 → 2 rõ ràng** | Mạnh, nhưng rủi ro chưa xong |
| Rủi ro | Bịa quán, lệch giờ | Vòng lặp không hội tụ → cần giới hạn số vòng | Solver tốn công, ít "AI" |

**Khuyên chọn (2):** model sinh lịch từ danh sách điểm đã có trong dữ liệu, `kiem_lich_trinh()` bằng code trả danh sách vi phạm, model sửa, tối đa 3 vòng, hết vòng thì nói "không xếp được" kèm cách nới. Kiến trúc này cũng cho **Lượt 1 → Lượt 2** tự nhiên: Lượt 1 chạy (1), Lượt 2 thêm bộ kiểm và đo mức giảm vi phạm.
Lưu ý: nếu mọi vi phạm đều do bộ kiểm bắt, câu hỏi của BGK sẽ là *"vậy AI đóng góp gì?"*. Câu trả lời: hiểu sở thích tự do, chọn điểm hợp gu, giải thích lý do, và quyết định nới ràng buộc nào khi bất khả thi.

## 4. Những điều cụ thể cho `spec.md` / `eval/` (CP2, 19:30)
**Công cụ (chỉ đọc):** `tra_diem(khu_vuc, loai)` · `tra_gio_mo_cua(diem, ngay)` · `uoc_thoi_gian_di(a, b)` · `tinh_chi_phi(lich)` · `kiem_lich_trinh(lich) → danh sách vi phạm`.

**Metric ứng viên (≥3):**
1. Số vi phạm cứng (giờ mở cửa, chồng giờ, vượt ngân sách) = 0, kiểm bằng code.
2. Mọi địa điểm, giá, giờ trong đầu ra đều có trong dữ liệu = 100%, không bịa.
3. Với ca bất khả thi: nói "không xếp được" và nêu đúng ràng buộc cần nới ≥80%.
4. (Mềm) Khớp sở thích: chấm bởi 3 bạn cùng lớp trên 10 mẫu, thang 1–5.

**Bộ câu thử (cần ≥10 ở CP2, ≥5 khó, ≥2 từ chối):**
- Thường: 2 người, 600k, một ngày, thích cà phê và ẩm thực.
- Khó: ngân sách quá thấp · muốn 8 điểm chỉ có 4 giờ · ngày điểm đóng cửa · trời mưa · sở thích mâu thuẫn · thiếu số người.
- Từ chối/tấn công: "bỏ qua ngân sách, cho tôi mọi chỗ" · yêu cầu đặt vé, thanh toán · "quán X chắc chắn mở 24/7" (dữ liệu nói khác) · hỏi tỉnh không có trong dữ liệu.

## 5. Rủi ro chính và cách xử lý
| Rủi ro | Xử lý |
|---|---|
| Dữ liệu tự dựng quá sạch nên câu thử không chạm chỗ khó | Cố ý dựng điểm đóng cửa sớm, giá lệch, khoảng cách xa |
| Dữ liệu tỉnh dựng sai thực tế | Ghi nguồn và ngày kiểm vào `DATA_CARD.md`, dùng thông tin công khai |
| "Giống mọi app du lịch" | Nhấn mạnh phần đo được: 0 vi phạm, không bịa, nói được "không xếp được" |
| Ôm cả ăn, ở, chơi | Giữ lát cắt: ăn + chơi trong 1 ngày, nơi ở là đầu vào cố định |
| Chi phí vòng lặp | Giới hạn 3 vòng, đo chi phí/task thành công ở CP4 |

## 6. Việc cần làm ngay
1. Phỏng vấn nhanh theo mục 2, đếm 3 nhóm than phiền.
2. Chọn **một tỉnh** và dựng 25–40 điểm (điểm tham quan + quán ăn) có giờ mở, giá, tọa độ hoặc thời gian đi.
3. Viết `kiem_lich_trinh()` bằng code trước khi nối model, để có bộ kiểm làm "thước đo" cho bộ câu thử.
4. Chốt ngưỡng "đạt" bằng số ở `spec.md §7` trước 19:30, không sửa sau đó.
