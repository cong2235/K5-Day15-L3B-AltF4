# Phân công phần còn lại — từ 21:30 T6 27/11 đến khóa repo 23:59 T7 28/11

> Cập nhật sau khi kéo repo (HEAD `29aab33`). Bản này thay phần "Giai đoạn B → E" của [phan-cong.md](phan-cong.md); phần chốt hợp đồng và luật chung ở file đó vẫn đúng.
> Nguyên tắc cũ giữ nguyên: **mỗi file một chủ**, thiếu đầu vào thì dùng bản giả của mình, commit nhỏ, `git pull --rebase` trước khi push.

## 1. Đang ở đâu

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| CP1, CP2 | Đã nộp (spec §7 và 4 metric đã khóa) | **Không sửa** §7, `metric_spec.yaml`, không xóa câu thử nào |
| Code lõi (`domain`, `verify`, `rules`, `tools`, `agent`) | Xong, 21 test đạt, `eval --fake` chạy hết 30 câu | Đức |
| `ai.py` nối Bedrock (Haiku 4.5) | Có code, **chưa có `.env`** trong máy kiểm, chưa thấy lượt `--try` thật | Công |
| **`codebase/prompts.py`** | **CHƯA CÓ.** `agent.py` đang rơi về `rules.parse_rule` (luật code), tức **chưa có quyết định AI nào chạy** | Công. **Đường găng của cả dự án** |
| `data/places.csv` | 34 dòng + `travel_override` + `transport_rates` | Đạt |
| Bằng chứng pain | 6 phiếu khảo sát, 0 phỏng vấn, `summary.md` còn trống, `benchmark.csv` 0/30 câu từ người dùng/data thật | Đạt (lỗ hổng lớn nhất sau `prompts.py`) |
| `eval/grade.py` + 11 test | Xong | Quân |
| `eval/report.md`, `cost/`, `slides/`, spec §1–§3, §8 | Chưa điền | Quân / Đạt / Công |
| `web/` (website giới thiệu Đà Nẵng, 46 file) | Có, **không nằm trong rubric**, `web/content/sources.md` ghi nhiều câu "CẦN KIỂM" | Đức |

**Hai rủi ro cần xử lý trước:**
1. Không có `prompts.py` thì không có điều kiện cứng số 1 ("gọi AI thật ở quyết định trung tâm"). Mọi thứ khác xếp sau việc này.
2. Khảo sát chưa đủ 20 người và chưa có phỏng vấn: nếu 23:00 vẫn chưa đủ thì mở nguồn dự phòng (đào ~100 review công khai) ngay, đừng đợi sáng.

**Về `web/`:** dừng thêm tính năng. Chỉ dùng nếu cuối cùng cần một giao diện cho phần demo; không đưa vào pitch như bằng chứng, và không công bố câu "CẦN KIỂM" như sự thật.

## 2. Việc theo người

### Công (đội trưởng, AI + điều phối)
| # | Việc | Xong khi | Hạn |
|---|---|---|---|
| C1 | Tạo `.env` (không commit), chạy `python run.py eval --try 5` | Thấy "Nối model được", token > 0 | 22:00 |
| C2 | Viết `codebase/prompts.py`: `parse_request` trước (JSON theo `domain.request_from_dict`) | 10 câu tự gõ cho ra ràng buộc đúng, ca thiếu thông tin thì hỏi lại 1 câu | 23:00 |
| C3 | `propose`, `repair` (nhận danh sách vi phạm cụ thể), `why` (không chứa chữ số) | Chạy được qua `agent.answer` với 5 câu `thuong`, 0 vi phạm | 02:00 sáng T7 |
| C4 | Nháp pitch + `slides/outline.md` (khung, chưa có số) | Có khung 5 phút | trước khi ngủ |
| C5 | Nộp Form 2 CP3 | | 09:45 |
| C6 | Video 30 giây AI thật (Unlisted, kiểm tab ẩn danh) | Mở được | 09:30 |
| C7 | Video demo dự phòng, `demo-slides.pdf` ra gốc repo, quét key, nộp CP4 | 4 điều kiện cứng đủ | 14:15 |
| C8 | `spec.md` §0, §3, §4, §6, §9, §10; `docs/ai-usage.md`; `canvas.md`; README mục "Phần nào thật, phần nào giả" | Hết dấu `[CẦN…]`, `[NHÓM…]` | §0,§3: 12:00 · còn lại: 23:30 T7 |

Nếu C2–C3 trễ, báo ngay lúc 23:00: Đức sang giúp viết `propose`/`repair` (Đức đã nắm hợp đồng trong `agent.py`).

### Đức (code chắc chắn, ghép luồng)
| # | Việc | Xong khi | Hạn |
|---|---|---|---|
| D1 | Chạy `agent.answer` với model giả trên **toàn bộ** 30 câu, ghi những câu rơi vào nhánh nào; sửa `rules.py`/`verify.py` nếu lộ lỗi (đây là phương án dự phòng khi model trả JSON hỏng) | Không câu nào ra exception | 23:00 |
| D2 | Khi Công đẩy `prompts.py`: ghép, chạy `eval --try`, sửa lỗi hợp đồng JSON hai phía | `eval --try 5` chạy ra khối ```json đúng | khi C2 xong |
| D3 | Giới hạn chi phí: kiểm 3 vòng `repair` thật sự dừng, token mỗi câu không bùng | `run-try.csv` có token hợp lý | 02:00 |
| D4 | **08:00 T7: chạy `python run.py eval` → `run-1.csv`** cùng Công. Lỗi kỹ thuật thì chạy lại thành lượt mới, không sửa tay CSV | Có `run-1.csv`, Run ID | 08:30 |
| D5 | Cải tiến Lượt 2 (theo ca trượt, mỗi lượt đổi **một** thứ) rồi chạy `run-2.csv` | Có Run ID lượt 2 | 12:00 |
| D6 | Sau đó: tập demo (Đức thao tác máy, cho BGK gõ câu bất kỳ); xử lý `web/` chỉ nếu còn giờ | | 13:15 |

### Đạt (bằng chứng + dữ liệu)
| # | Việc | Xong khi | Hạn |
|---|---|---|---|
| T1 | Đếm lại số phiếu khảo sát lọc theo câu 3 và câu 5; nhắc thêm kênh (lớp, nhóm sinh viên) | ≥20 người "Có" | 08:00 T7 |
| T2 | 3 phỏng vấn người ngoài nhóm → `evidence/interviews/P1–P3.md` (ẩn tên). Nhờ Công/Quân hẹn giúp nếu thiếu người | 3 file | 09:00 T7 |
| T3 | **22:30 tối nay: đưa ≥10 trích dẫn thô** (khảo sát câu 13 + phỏng vấn nếu đã có) vào `evidence/` cho Quân dùng viết câu thử | Quân đọc được | 22:30 |
| T4 | Đào review công khai làm nguồn dự phòng (chỉ khi 23:00 khảo sát <20) | `evidence/data-mining.md` có x/N, ≥5 ví dụ | 01:00 |
| T5 | `evidence/summary.md` (số chính, ≥5 trích dẫn nguyên văn, khớp/lệch giữa các nguồn) | Đạt ngưỡng ≥1 nguồn | 09:00 T7 |
| T6 | `spec.md` §1–§2: số người, số lần/tháng, phút/lần, impact/tháng (ghi "tự ước tính" khi chưa có nguồn) | Hết `[CẦN SỐ]` | 09:30 T7 |
| T7 | Rà `DATA_CARD.md`; thêm ca khó cố ý nếu `places.csv` còn thiếu (sửa data thì báo Đức và Quân, vì ràng buộc trong câu thử tham chiếu id) | | 10:00 T7 |
| T8 | Dựng slide theo `slides/outline.md` (phần pain, impact) + 2–3 người dùng thử → `validation/log.md` (bonus) | Slide có chỗ chừa số cho Quân | 13:15 |

### Quân (đo lường + chi phí)
| # | Việc | Xong khi | Hạn |
|---|---|---|---|
| Q1 | Điền `eval/README.md` mục 1–4, kiểm `run.py check` | Không còn cảnh báo ngoài 1/3 nguồn thật | 22:30 |
| Q2 | Điền `cost/personas.yaml` từ khảo sát; chạy `python run.py simulate --try` bằng model giả để biết khung chạy | Chạy ra `cost/simulate-try.csv` | 23:30 |
| Q3 | Sau T3: viết **≥10 câu mới** có `source=nguoi_dung` (từ trích dẫn) hoặc `data_that`. **Chỉ thêm, không xóa, không sửa câu cũ**; thêm câu bất khả thi để metric (c) có nghĩa | `run.py check` không còn cảnh báo 0/30 | 07:30 T7 |
| Q4 | Ghi "quyết định trước lượt 1" (nếu <85% thì đổi gì) vào `eval/README.md`; chạy lại cùng input 2 lần để đo nhiễu | | 08:30 |
| Q5 | 08:30: chấm `run-1.csv` bằng `grade.py`, **kiểm tay 5 câu**, `python run.py score` → x/N + Run ID gửi Công | Gửi trước 09:15 | 09:15 |
| Q6 | 10:15: đọc to các câu trượt cho cả nhóm; gom nhóm lỗi trong `eval/report.md` | | 10:30 |
| Q7 | Chấm Lượt 2, viết `report.md` (Lượt 1 → 2, 3 câu vẫn trượt và vì sao), `simulate --rate-from eval/run-2.csv` ≥50 phiên, `cost-estimate.md`, spec §5, §7 (chỉ phần Kết quả), §8 | Số khớp CSV, không chỉnh tay | 13:00 |

## 3. Điểm ghép và họp ngắn

| Giờ | Việc | Ai |
|---|---|---|
| **23:00 T6** | Kiểm `prompts.py`: nếu `parse_request` chưa chạy được thì Đức sang giúp. Kiểm khảo sát: nếu <20 thì T4 bắt đầu | Công, Đạt |
| 22:30 T6 | Đạt đẩy trích dẫn thô | Đạt → Quân |
| **08:00–08:30 T7** | Chạy Lượt 1 | Đức, Công |
| 09:15 | Quân gửi x/N + Run ID | Quân → Công |
| 09:45 | Nộp CP3 | Công |
| **10:15 (15 phút)** | Chọn đúng 1 cải tiến Lượt 2, Công quyết | Cả nhóm |
| 13:15–14:00 | Tập pitch 2 lần có bấm giờ | Cả nhóm |
| 14:15 | Nộp CP4 | Công |
| 22:00 | Mỗi người xong `reflection/<tên>.md` và gửi Công 2–3 dòng "dùng AI vào việc gì" | Cả nhóm |
| 23:30 | Công kiểm lần cuối: key, link ẩn danh, §10 | Công |

## 4. Chuẩn bị Q&A pitch (mỗi người một mảng)
- Công: kiến trúc, guardrail, "vậy AI đóng góp gì khi `verify` bắt hết lỗi?"
- Đức: demo và "nếu AI sai thì sao?"
- Đạt: pain, bằng chứng, impact
- Quân: số liệu, câu trượt, "chi phí khi có 10k người dùng?"

## 5. Ba điều cấm (nhắc lại)
Commit `.env`/key (−10đ) · sửa §7, metric, hoặc xóa câu trượt (0 điểm khối đánh giá) · quá 23:59 T7 (mất phần cập nhật cuối).
