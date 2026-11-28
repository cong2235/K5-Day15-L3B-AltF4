# Lịch hợp lý hơn: đường bộ thật, giờ đẹp, nghỉ trưa (nhánh `lich-hop-ly`, 28/11)

> Làm **sau** Lượt 1 và Lượt 2, trên nhánh riêng. `main` giữ đúng bản đã nộp, vì các thay đổi dưới đây đổi cách tính giờ: chạy lại bộ câu thử trên nhánh này sẽ ra số khác `run-1`, `run-3`.

## Vì sao sửa

Tôi chạy 4 yêu cầu điển hình bằng AI thật. Mọi lịch đều qua `verify`, nhưng nhiều lịch không đáng đi:

- Có lịch ở ngoài trời giữa trưa: Ngũ Hành Sơn 12:35–16:35, Cầu Rồng 12:55.
- Có lịch tắm biển lúc trời đã tối: Mỹ Khê 17:50–20:50.
- Bữa tối luôn bắt đầu 17:00.
- Có lịch rời phố cổ Hội An lúc 17:52, rồi đi 69 phút về Mỹ Khê chỉ để ăn tối.
- Có lịch xếp kín 13 tiếng không nghỉ, có lịch lại trống hơn 4 tiếng.

Thời gian đi lại còn tính theo đường chim bay. So với đường bộ OSRM, phần lớn chặng được ước dài hơn thực tế, nhưng **2 chặng qua đèo Sơn Trà bị ước ngắn hơn khoảng 3 lần** (đỉnh Bàn Cờ → Năm Đảnh: ghi 10 phút, thật 27 phút). Nghĩa là lịch "đã kiểm" vẫn có thể không kịp giờ.

## Đã sửa

| Vấn đề | Sửa | File |
|---|---|---|
| Thời gian đi lại theo đường chim bay | Ma trận đường bộ OSRM cho mọi cặp điểm (`data/build_road_matrix.py` → `data/travel_road.csv`, 1.406 chặng). Phút thật = OSRM × 1,6 + 3 (hệ số hiệu chỉnh từ 8 chặng Google Maps trong `travel_override.csv`, trung vị Google/OSRM ≈ 1,7). Tiền Grab tính theo km đường bộ. Thứ tự ưu tiên: Google Maps đo tay > OSRM > ước tính | `verify.travel_min`, `transport_cost`, `tools.data` |
| Ngoài trời giữa trưa, chợ đêm ban ngày | `data/visit_prefs.csv`: "giờ nên đến" cho từng điểm (nhóm tự ước tính). Lịch được chờ tối đa 2 tiếng để tới đúng giờ đó. `discomfort()` tính số phút lệch giờ nên đến làm phạt khi chọn thứ tự | `verify._nice_start`, `discomfort`, `schedule` |
| Ở một điểm quá lâu | Thời gian ở tối đa riêng từng điểm (`max_visit_min`). Không kéo thời gian ở vượt quá giờ nên đến | `verify.stay_cap`, `stretch` |
| Ăn tối 17:00 | Giờ ăn ưu tiên: trưa từ 11:30, tối từ 18:15. Khung bữa bắt buộc trong `verify` vẫn giữ nguyên | `verify._nice_start` |
| Quay về khu khác chỉ để ăn | `local_meals()`: bữa ăn phải đi từ 25 phút sang khu khác thì đổi sang quán cùng khu với điểm trước | `verify`, `agent._plan` |
| Lịch trống hơn 2 tiếng khi đã đủ 6 điểm | `fill_gaps()`: thay một điểm yếu bằng điểm lấp được khoảng trống. Chỉ nhận khi bớt ít nhất 60 phút trống và không khó chịu hơn | `verify`, `agent` |
| Dòng "rảnh 2 tiếng" không gợi ý gì | Khoảng trống 60–150 phút vào buổi trưa được gọi là **nghỉ trưa**, kèm gợi ý "về khách sạn hoặc ngồi cà phê gần khu …" | `agent._is_rest`, `chat.js` |
| Phương án phụ trái yêu cầu (đưa Hội An sang buổi sáng) hoặc trống nửa ngày | `_comfy()` loại phương án phụ khó chịu hơn lịch chính quá 45 phút, hoặc có khoảng chờ dài hơn quá 60 phút. Phương án dự phòng bằng code cũng qua `local_meals` và `fill_gaps` | `agent` |
| Rời cầu Rồng đúng lúc phun lửa | Ngày có sự kiện (`event_days`), lịch tới trước giờ sự kiện 15 phút | `verify._nice_start` |
| AI không biết giờ đẹp | Bảng ứng viên có thêm cột "nên đến". Prompt thêm luật tránh nắng trưa, ăn tối cùng khu, chừa nghỉ trưa | `prompts.py` |

## Kết quả (AI thật, 28/11)

Cùng 4 yêu cầu, lịch chính trước và sau khi sửa:

| Yêu cầu | Trước | Sau |
|---|---|---|
| 8h–21h, hải sản + thiên nhiên | Ngũ Hành Sơn 12:35–16:35 · biển xen giữa · trống 37' | Bàn Cờ sáng · Ngũ Hành Sơn 14:30 · biển 16:47–18:17 · tối 18:25 |
| 7h–22h, check-in + cà phê | Trống 249', khoảng dài nhất 149' | Biển 07:00 · Linh Ứng 15:00 · cầu Rồng 19:09 · khoảng dài nhất 110' |
| 8h–20h, sáng biển, chiều tối Hội An | Rời phố cổ 17:52, đi 69' về Mỹ Khê ăn tối | Phố cổ 15:30–18:08 · tối Cơm gà Hiền ở Hội An |
| Tối thứ Bảy xem cầu Rồng | Rời cầu lúc 21:00 | Ở cầu 20:45–21:15, đúng giờ phun lửa |

Chạy cả 30 câu thử bằng `eval --try 30` (lần thử, **không phải một lượt chính thức**): **29/30**, cả 4 metric đều đạt (Lượt 2 chính thức: 28/30).

**T05 vẫn trượt, và với dữ liệu hiện tại thì không thể đạt.** Grader đòi cả lượt ghé cầu Rồng nằm trọn trong `best_windows` 21:00–21:15 (15 phút), trong khi `visit_min` của cầu Rồng là 30 phút và `verify` cấm ở ngắn hơn mức đó. Không sửa grader hay dữ liệu sau CP2. Ghi lại ở đây để trình bày.

## Còn lại

- `visit_prefs.csv` do nhóm tự ước tính. Nên kiểm lại bằng phỏng vấn hoặc review.
- OSRM là thời gian ô tô khi đường thông thoáng. Hệ số 1,6 hiệu chỉnh từ 8 chặng đo lúc tối thứ Sáu, chưa tách theo giờ cao điểm hay theo xe máy.
- Bữa tối vẫn hay rơi vào cùng một quán (Ốc Ngon), vì dữ liệu còn ít quán mở buổi tối ở trung tâm và Mỹ Khê.
