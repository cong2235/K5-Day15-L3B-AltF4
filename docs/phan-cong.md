# Phân công AltF4 — 27–28/11

> Nguyên tắc: **mỗi file có đúng 1 chủ**, ai cần thì đọc, không sửa. Chốt hợp đồng trước, nên không ai phải đợi người khác: ai cũng làm trên dữ liệu giả của chính mình, đến mốc ghép thì thay bằng hàng thật.

## 0. Chốt hợp đồng (15 phút, cả nhóm, làm NGAY)
Lấy nguyên từ `docs/design.md`, không bàn lại:
1. **Cột `data/places.csv`** = các trường của `Place` (§5). `open_windows` ghi dạng `07:00-11:00;13:30-21:00`, `closed_days` ghi `0;6`, `tags` ghi `bien;am_thuc`.
2. **Kiểu dữ liệu** `Constraints`, `Stop`, `Plan`, `Violation` + 10 mã vi phạm (§5). Đức commit `codebase/domain.py` trong 30 phút đầu.
3. **Khối JSON cuối `output`** (§8): `{"status":"plan|infeasible|ask_back|refuse","stops":[{"id","arrive","leave"}],"total_vnd":...,"relax":[{"change":"budget_total=450000","stops":[...]}]}` (`relax` chỉ có khi `infeasible`, mảng rỗng ở các trạng thái khác; `eval/metric_spec.yaml` đọc trường này).
4. **Chữ ký hàm** (§6): `parse_request`, `propose`, `repair`, `why` (AI) · `shortlist`, `verify`, `cost`, `relax_options`, `render`, `travel_min`, `transport_cost` (code).
5. **Ngân sách gồm cả tiền di chuyển:** `cost(plan, c)` = vé + ăn + Σ `transport_cost`. Đạt thêm `data/transport_rates.csv` (đơn giá có nguồn); Đức cài `transport_cost` trong `verify.py`.

Đổi hợp đồng sau mốc này = báo cả nhóm trước, Công duyệt.

## 1. Ai giữ file nào

| Người | Vai | Chủ các file |
|---|---|---|
| **Công** (đội trưởng) | PM + phần AI của bản chạy thử | `codebase/ai.py`, `codebase/prompts.py` (mới), `spec.md` (§0, §3, §4, §6, §9, §10), `canvas.md`, `README.md`, `docs/ai-usage.md`, `slides/`, `demo-slides.pdf`, video |
| **Đức** | Phần code chắc chắn (không gọi model) | `codebase/domain.py`, `codebase/verify.py`, `codebase/tools.py`, `codebase/agent.py`, `codebase/app.py`, `tests/` |
| **Đạt** | Dữ liệu + bằng chứng pain | `data/places.csv`, `data/travel_override.csv`, `data/transport_rates.csv`, `data/DATA_CARD.md`, `evidence/**`, `spec.md` §1–§2 |
| **Quân** | Đo lường + chi phí | `eval/**` (benchmark, metric_spec, `grade.py`, report, README), `cost/**`, `spec.md` §5, §7, §8, `validation/log.md` |

`spec.md` có nhiều chủ: mỗi người chỉ sửa mục của mình, `git pull` trước khi sửa, commit ngay sau khi sửa.

## 2. Việc theo giai đoạn

### Giai đoạn A · Bây giờ → CP2 19:30 T6
| Người | Việc | Xong khi | Không phải đợi vì |
|---|---|---|---|
| Công | Lấy API key, nối `call_model` trong `ai.py` (`docs/connect-model.md`) → `python run.py eval --try` thấy token > 0. Viết prompt `parse_request` trả JSON, có bản giả khi chưa có `.env` | Gọi được model thật, `parse_request` trả `Constraints` cho 5 câu tự gõ | Dùng `domain.py` của Đức; trong 30 phút chờ thì tự định nghĩa tạm theo §5 |
| Đức | `domain.py` → `verify()` + `cost()` + `travel_min()` (từ tọa độ) + test 10 kế hoạch viết tay (5 đúng, 5 mỗi cái 1 lỗi). Khung `answer()` chạy hết luồng với model giả | `python run.py` và `python run.py eval --fake` chạy không lỗi | Tự viết `tests/places_fixture.csv` 6–8 dòng, không đợi data của Đạt |
| Đạt | **Gửi khảo sát trước** (Google Form, 10 câu theo Mom Test, đăng nhóm lớp/bạn bè) để thu dần qua đêm. Hẹn 3 phỏng vấn tối nay. Rồi dựng `places.csv` 25–40 dòng có nguồn + ngày kiểm + ca khó cố ý. `DATA_CARD.md` bản đầu | Form đã gửi; ≥15 dòng `places.csv` + DATA_CARD trước 19:30 | Không phụ thuộc ai |
| Quân | Rà 30 câu `benchmark.csv`, bỏ câu trùng; rút `metric_spec.yaml` còn 3–4 metric đo bằng code; soạn ngưỡng "đạt" §7; viết khung `grade.py` (đọc JSON, chấm `tu_choi` bằng luật, gọi `verify`) | `python run.py check` không còn lỗi CP2 (trừ cảnh báo 1/3 nguồn thật, xử lý ở CP3) | Test `grade.py` bằng 5 chuỗi output tự viết tay; `verify` import theo chữ ký đã chốt |

**18:45 – họp 15 phút chốt ngưỡng §7** (Quân trình, Công quyết, ghi số). **19:15** Công nộp Form 2 nhánh CP2. **Sau 19:30 không ai sửa §7 và `metric_spec.yaml`.**

### Giai đoạn B · Tối T6 → sáng T7 08:30 (đường găng: bản chạy thử gọi AI thật)
| Người | Việc | Xong khi |
|---|---|---|
| Công | Prompt `propose`, `repair` (nhận danh sách vi phạm), `why` (chỉ dùng thuộc tính có trong data). Kiểm JSON ở biên, sai thì hỏi lại model 1 lần | Mỗi hàm chạy được trên `places_fixture.csv` |
| Đức | `shortlist`, `relax_options` (chỉ trả cách nới mà `verify` qua), `render`. Ghép luồng đầy đủ trong `agent.py`, giới hạn 3 vòng sửa. 23:00 đổi sang `places.csv` thật | 5 câu `thuong` chạy ra lịch, 0 vi phạm |
| Đạt | Làm 3 phỏng vấn (mỗi bạn còn lại hỏi giúp 1 người nếu Đạt thiếu người, ghi vào `evidence/interviews/P*.md`). Hoàn thiện `places.csv` + `travel_override.csv`. **22:00 đẩy ≥10 trích dẫn thô** vào `evidence/` | `places.csv` đủ 25–40 dòng; ≥3 phỏng vấn ghi xong |
| Quân | Viết lại ≥10 câu thử từ trích dẫn của Đạt (`source=nguoi_dung`) và từ `places.csv` (`data_that`). Điền `cost/personas.yaml`. Chạy `simulate --try` bằng model giả để biết khung chạy | `run.py check` hết cảnh báo 1/3; `simulate --try` chạy được |

**08:30 T7 – điểm ghép:** Đức + Công chạy `python run.py eval` → `run-1.csv`.

### Giai đoạn C · 08:30 → CP3 10:00 T7
| Người | Việc |
|---|---|
| Công | Quay video 30 giây gọi AI thật, đưa YouTube Unlisted, kiểm bằng tab ẩn danh. Nộp Form 2 CP3 lúc 09:45 |
| Đức | Trực sửa lỗi kỹ thuật khi eval chạy. Lỗi kỹ thuật thì chạy lại thành lượt mới, không sửa tay CSV |
| Đạt | `evidence/summary.md`: chốt nguồn đạt ngưỡng (≥3 phỏng vấn hoặc ≥20 khảo sát) + ≥5 trích dẫn nguyên văn đã ẩn tên. Điền §1–§2 có số |
| Quân | `grade.py` chấm `run-1.csv`, kiểm tay 5 câu xem khớp không, `python run.py score` → x/N + Run ID gửi Công |

### Giai đoạn D · 10:00 → CP4 14:30 T7
**10:15 – họp 15 phút:** Quân đọc to các câu trượt, cả nhóm chọn **đúng 1 cải tiến** (các ứng viên ở `docs/roadmap.md`, gồm cả A1 của `docs/architecture-review.md`), Công quyết.

| Người | Việc | Hạn |
|---|---|---|
| Đức (+Công nếu cải tiến nằm ở prompt) | Làm cải tiến đã chọn, chạy Lượt 2 → `run-2.csv` | 12:00 |
| Quân | Chấm Lượt 2, viết `eval/report.md` (Lượt 1 → 2, 3 câu vẫn trượt và vì sao). `simulate --rate-from eval/run-2.csv` ≥50 phiên, `cost-estimate.md`, §8 | 13:00 |
| Đạt | Dựng slide theo `slides/outline.md` (phần pain, impact dùng số của mình; chừa ô số eval/chi phí để Quân điền 13:00). Nếu dư giờ: 2–3 người dùng thử → `validation/log.md` (bonus) | 13:15 |
| Công | Quay video demo dự phòng (bản đầy đủ, lưu offline). Xuất `demo-slides.pdf` ra gốc repo. Kiểm 4 điều kiện cứng, quét key (`git grep -i "sk-\|api_key"`), nộp Form 2 CP4 lúc 14:15 | 14:15 |

**13:15–14:00 – tập pitch 2 lần có bấm giờ (5 phút + 3 phút Q&A).**
- Công: dẫn pitch · Đức: thao tác demo, cho BGK gõ câu bất kỳ · Đạt: trả lời câu về pain · Quân: trả lời câu về số, câu trượt, chi phí 10k người dùng.

### Giai đoạn E · Sau trao giải → khóa repo 23:59 T7
| Người | Việc |
|---|---|
| Mỗi người | `reflection/<ten>.md` của mình, xong trước 22:00 |
| Mỗi người | Gửi Công 2–3 dòng "đã dùng AI vào việc gì, kiểm lại phần nào" |
| Công | `spec.md` §10 changelog, `docs/ai-usage.md`, kiểm lần cuối trước 23:30 |

## 3. Luật để không phải đợi nhau
1. **Thiếu đầu vào thì dùng bản giả của chính mình**, không ngồi chờ: Đức có `places_fixture.csv`, Công có `domain.py` tạm, Quân có output viết tay.
2. **Báo trễ sớm:** ai thấy không kịp hạn trong bảng thì báo nhóm ngay, không đợi đến hạn.
3. **Commit nhỏ, push thường xuyên** (ít nhất mỗi giờ), chỉ trong file mình giữ.
4. Ba điều cấm: commit `.env`/key · sửa ngưỡng sau 19:30 T6 hoặc xoá câu trượt · sửa file khung (`run.py`, `tracing.py`, `run_eval.py`, `simulate.py`).
