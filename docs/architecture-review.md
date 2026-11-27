# Review kiến trúc & sản phẩm — AltF4 (handoff cho agent)

> **Đọc file này trước khi sửa code.** File gom toàn bộ ngữ cảnh: hệ thống là gì, đang ở trạng thái nào, điểm yếu, cách sửa và thứ tự ưu tiên.
> Viết ngày 27/11/2026 (trước CP2 19:30). Người review: AI, vai BA + system architect. **Đây là đề xuất. Nhóm duyệt rồi mới làm.**
> Luật bắt buộc của repo nằm ở [AGENTS.md](../AGENTS.md). Khi file này mâu thuẫn với AGENTS.md hoặc rubric, **AGENTS.md và rubric thắng**.

---

## 0. Tóm tắt một đoạn

AltF4 là bản chạy thử cho hackathon AI20K, Track C (Du lịch), dựa trên gợi ý C1 của BTC. **Lát cắt:** một nhóm bạn trẻ lần đầu đến Đà Nẵng nhập ngân sách, số người, khung giờ và sở thích. AI chọn và sắp thứ tự các điểm tham quan và bữa ăn trong 1 ngày sao cho thoả giờ mở cửa, thời gian di chuyển và ngân sách. Nếu không có lịch hợp lệ, AI nói "không xếp được" kèm cách nới ràng buộc.

**Kiến trúc đã chọn:** workflow cố định kiểu *generate-and-verify*. Model đề xuất, code kiểm, sau đó model sửa, tối đa 3 vòng. Đánh giá chung: **thiết kế đúng hướng, nhưng gần như chưa có phần nào được cài đặt**. Rủi ro lớn nhất là không kịp các mốc và thiếu bằng chứng pain. Thiết kế chỉ là rủi ro thứ yếu.

---

## 1. Bối cảnh cuộc thi (ràng buộc cứng, không được vi phạm)

| Mốc | Thời điểm | Cần có |
|---|---|---|
| CP2 | **19:30 Thứ Sáu 27/11** | Chốt chuẩn "đạt" (`spec.md` §7, `eval/metric_spec.yaml`). **Sau mốc này không được sửa**, sửa thì khối đánh giá 0 điểm. Cần ≥10 câu thử |
| CP3 | 10:00 Thứ Bảy 28/11 | `spec.md` §0–§7, 20–30 câu thử, bằng chứng pain, video 30 giây AI thật |
| CP4 | 14:30 Thứ Bảy 28/11 | Đủ §0–§10, `eval/report.md` có Lượt 1 → Lượt 2, `simulate` ≥50 phiên, `demo-slides.pdf` |
| Hạn chót | 23:59 Thứ Bảy 28/11 | Changelog, reflection |

**Điều kiện cứng để được xét giải** (thiếu một mục là không xét):
1. Gọi AI thật ở quyết định trung tâm. Model giả không tính.
2. Bằng chứng pain đạt ngưỡng ở ≥1 nguồn: ≥3 phỏng vấn người ngoài nhóm, hoặc ≥20 khảo sát, hoặc đào data ra x/N.
3. ≥20 câu thử, có kết quả % đạt.
4. Có `demo-slides.pdf`.

**Trọng số rubric (85 điểm):** R1 pain 14 · R2 impact 11 · R3 thiết kế + bản chạy thử 16 · R4 bộ câu thử + metric 14 · R5 báo cáo eval 8 · R6 chi phí 12 · R7 slide/demo 10. BTC **chấm quyết định và bằng chứng**, không chấm độ hoành tráng. Kết quả thấp mà trung thực vẫn được đủ điểm.

**Cấm** (chi tiết ở AGENTS.md):
- Hardcode đáp án hoặc so khớp nguyên văn input của câu thử.
- Sửa ngưỡng sau CP2, xoá câu trượt, sửa `expected` cho khớp output.
- Bịa phỏng vấn hoặc số liệu.
- Commit `.env` hay API key.
- Sửa các file khung: `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py`, `run.py`.

---

## 2. Hệ thống theo thiết kế (nguồn: `spec.md`, `docs/design.md`)

### 2.1 Luồng
```
parse_request (AI) → shortlist (code) → propose (AI) → verify (code)
   → [vi phạm, ≤3 vòng] repair (AI) → verify
   → sạch: render (code) + why (AI)  |  hết vòng: relax_options (code) + AI diễn đạt
```
Các nhánh khác của `parse_request`:
- Ngoài phạm vi (đặt vé, thanh toán, tỉnh khác) → từ chối.
- Thiếu ngân sách, số người hoặc khung giờ → hỏi lại đúng 1 câu.

### 2.2 Mô hình miền (thiết kế, chưa có code)
- `Place(id, name, kind, cluster, tags, open_windows, closed_days, visit_min, price_pp, price_basis, source, checked_on, lat, lon)`
- `Constraints(people, budget_total, day, start, end, like, avoid, base_cluster)`
- `Plan(stops: tuple[Stop(place_id, arrive, leave)])`
- `Violation(code, stop_index, detail)`. Các mã: `UNKNOWN_PLACE, CLOSED, OVERLAP, TRAVEL_GAP, OVER_BUDGET, OUT_OF_WINDOW, NO_MEAL, AVOID_TAG, TOO_MANY, DUPLICATE`

### 2.3 Nguyên tắc đã chốt (giữ nguyên)
- Tiền, giờ và quãng đường **chỉ do code tính**. Model không tự nhẩm số.
- Biên chặt, lõi tin kiểu: JSON từ model và input người dùng được kiểm ở biên.
- Không có lịch hợp lệ thì nói "không xếp được". Không đưa lịch gần đúng.
- Mọi con số trong output lần ngược được về dòng dữ liệu và `checked_on`.
- Mọi công cụ chỉ đọc. Không đặt vé, không thanh toán.

### 2.4 Đầu ra cho grader
Cuối `output` có một khối JSON:
```json
{"status":"plan|infeasible|ask_back|refuse","stops":[{"id":"DN-014","arrive":"09:30","leave":"11:00"}],"total_vnd":0}
```

### 2.5 Phân công
Công: kiến trúc, spec, nộp form, video · Đức: `verify`, điều phối, nối model · Đạt: data địa điểm, bằng chứng, phỏng vấn · Quân: câu thử, metric, `grade.py`, chi phí.

---

## 3. Trạng thái thực tế (kiểm ngày 27/11)

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| `spec.md`, `docs/design.md`, `docs/roadmap.md` | ✅ Có bản nháp do AI soạn | Còn nhiều chỗ `[CẦN BẰNG CHỨNG]`, `[NHÓM CHỐT]` |
| `codebase/agent.py` | ❌ Code mẫu của khung | Vẫn gọi `search_example`, `SYSTEM = ""` |
| `codebase/tools.py` | ❌ Code mẫu | Chưa có `shortlist`, `get_place`, `travel_min`, `verify`, `relax_options` |
| `codebase/ai.py` | ❌ Chưa nối model | Nhánh thật vẫn báo `NotImplementedError`, chỉ chạy được `fake` |
| `data/places.csv`, `data/travel.csv` | ❌ Chưa có | `DATA_CARD.md` còn là template |
| `eval/benchmark.csv` | ❌ 3 dòng mẫu | Cần ≥10 câu ở CP2, ≥20 ở CP4 |
| `eval/metric_spec.yaml` | ⚠️ Có 4 metric đề xuất | **Chưa chốt.** Phải chốt trước 19:30 27/11 |
| `eval/grade.py` | ❌ Chưa có | |
| `evidence/` | ❌ Trống | Thiếu thì không được xét giải |
| `cost/personas.yaml` | ❌ Số ví dụ của track A | Phải thay bằng số của track C |

---

## 4. Điểm yếu kiến trúc và cách sửa

Mức ưu tiên: **P0** chặn mốc hoặc điểm · **P1** nên làm trong hackathon · **P2** làm sau.

### A1 · [P1, quan trọng nhất về thiết kế] Model đang tự xếp giờ, việc này code làm tốt hơn
- **Vấn đề:** `propose` cho model trả cả thứ tự và `arrive/leave`. Nhưng khi đã có thứ tự, giờ hoàn toàn tính được: `arrive[i] = max(leave[i-1] + travel_min(i-1,i), mở_cửa[i])` và `leave[i] = arrive[i] + visit_min[i]`. Để model đoán giờ sinh ra lỗi `OVERLAP`, `TRAVEL_GAP` và `CLOSED` một cách vô ích, rồi tốn thêm vòng `repair`.
- **Sửa:**
  - Model chỉ trả `[{id, priority, reason}]`, tức là chọn điểm và mức ưu tiên.
  - Hàm code `schedule(ids, c) -> Plan | Infeasible` lo xếp thứ tự và tính giờ. Với ≤15 ứng viên và ≤6 điểm, chèn tham lam hoặc beam search là đủ, chỉ cần thư viện chuẩn.
  - `repair` chỉ còn một việc: đổi tập điểm khi `schedule` báo bất khả thi.
- **Lợi ích:** ít lần gọi model hơn, rẻ hơn, kết quả tái lập được.
- **Dùng làm cải tiến Lượt 2:** Lượt 1 chạy thiết kế gốc (model tự xếp giờ). Lượt 2 chuyển việc xếp giờ sang code. So số vi phạm và chi phí trên mỗi task thành công. Mỗi lượt chỉ đổi đúng một thứ.
- **Khi BGK hỏi "AI đóng góp gì?":** hiểu sở thích viết tự do, chọn điểm hợp gu, chọn cách đánh đổi khi bất khả thi, viết lý do.

### A2 · [P1] Ngân sách bỏ qua tiền đi lại
- **Vấn đề:** `budget_total` "không gồm xe". Với sinh viên, tiền Grab giữa các cụm (Sơn Trà, Mỹ Khê, Ngũ Hành Sơn, trung tâm) chiếm phần đáng kể. Pain của nhóm cũng ghi "tốn hơn dự tính".
- **Sửa:** thêm `transport_cost(a, b, mode)` tính bằng code theo km × đơn giá (ghi *(tự ước tính)* và nguồn đơn giá), cộng vào `cost()` và vào luật `OVER_BUDGET`. Thêm `mode` (xe máy, ô tô) vào `Constraints`.

### A3 · [P1] Giá chỉ có một con số
- **Vấn đề:** một `price_pp` duy nhất khiến người dùng tin rằng giá chắc chắn như vậy. Quán ăn thì giá dao động.
- **Sửa:** lưu `price_min`, `price_typical`. `verify` kiểm theo `typical`. `render` hiển thị khoảng giá kèm "giá tham khảo ngày `checked_on`".

### A4 · [P1] Thiếu khung "đúng thời điểm"
- **Vấn đề:** nhiều trải nghiệm ở Đà Nẵng chỉ có giá trị vào giờ cố định: cầu Rồng phun lửa tối cuối tuần, hoàng hôn Sơn Trà, chợ đêm, biển buổi trưa quá nắng. Hiện chỉ có `open_windows`.
- **Sửa:** thêm `best_windows` (ràng buộc mềm, dùng để xếp hạng) và `event_days`. Đây là nguồn ca khó tốt cho bộ thử, ví dụ "muốn xem cầu Rồng phun lửa vào thứ Ba". **Nhóm phải kiểm lịch thật** từ nguồn công khai trước khi đưa vào data.

### A5 · [P0, chặn bộ câu thử] Phạm vi địa lý có thể sai thực tế
- **Vấn đề:** theo hiểu biết của người review, từ 07/2025 Quảng Nam đã sáp nhập vào Đà Nẵng, nên Hội An thuộc Đà Nẵng. Nếu bộ thử coi Hội An là "ngoài phạm vi → từ chối" thì sai. **Cần nhóm kiểm lại từ nguồn chính thức.**
- **Sửa đề xuất:** giữ Hội An trong data như một cụm xa (mất nửa ngày, giống Bà Nà). Câu từ chối "tỉnh khác" dùng nơi rõ ràng nằm ngoài, ví dụ Hà Giang.

### A6 · [P1] `answer()` không nhớ phiên trước, demo sẽ lộ
- **Vấn đề:** đường "người dùng sửa" ("bỏ Bà Nà") và đường "hỏi lại 1 câu" đều cần nhớ ràng buộc và `Plan` của lượt trước. Lúc eval từng câu thì không sao, nhưng khi BGK tự gõ trong demo thì sẽ hỏng.
- **Sửa:** giữ `session_state` (ràng buộc + `Plan` cuối) ở tầng ứng dụng, tức `codebase/app.py`. Có thể dùng một biến module trong `agent.py`, reset khi `run.py eval` gọi. **Không đổi hợp đồng** `answer(text) -> {"output": str}`. Không sửa `run.py`.

### A7 · [P1] Metric "không bịa địa điểm" khó chấm nếu lời văn tự do
- **Vấn đề:** nếu model viết tên quán, giá hoặc giờ trong đoạn `why`, grader phải dò chuỗi trong văn bản tự do.
- **Sửa:** `render` dựng toàn bộ tên, giờ và tiền từ data. Model chỉ trả `{id: reason}`, và trong `reason` không được có số tiền hay giờ (code kiểm bằng regex, có thì loại). Khi đó metric `khong_bia_dia_diem` được bảo đảm bởi cấu trúc, và `grade.py` chỉ cần so `id` trong khối JSON với `places.csv`.

### A8 · [P1] `relax_options` chưa có tiêu chí xếp hạng
- **Sửa:** sinh các cách nới theo từng tham số: tăng ngân sách theo bậc (+50k, +100k…), kéo dài khung giờ, bỏ 1 điểm hoặc 1 tag. Chạy `schedule` và `verify` cho từng cách. Chỉ giữ cách qua kiểm. Xếp theo "nới ít nhất", ví dụ số tiền thêm, số điểm yêu thích bị bỏ, số giờ kéo dài. Trả 1–3 lựa chọn, mỗi lựa chọn có con số cụ thể.

### A9 · [P1] Rủi ro eval ra 100% giả
- **Vấn đề:** data do nhóm dựng và câu thử do nhóm viết, nên kết quả dễ đẹp giả tạo.
- **Sửa:**
  - ≥1/3 câu thử lấy nguyên văn từ người được phỏng vấn hoặc khảo sát. `run.py check` cũng kiểm điều này.
  - Data cố ý có ca khó: đóng cửa sớm, nghỉ 1 ngày trong tuần, quán nghỉ trưa, một điểm rất đắt, một điểm rất xa, quán chỉ mở tối.
  - Đặt `temperature=0`. Chạy mỗi lượt 2 lần để đo nhiễu.
  - Đọc kỹ từng câu trượt trước khi tin con số % đạt.

### A10 · [P2] `travel_min` là ước tính
Tính từ tọa độ × hệ số đường vòng là chấp nhận được. Phải ghi rõ "ước tính" trong DATA_CARD, output và slide. Thêm bảng ghi đè cho vài cặp điểm quan trọng: Bà Nà, Hội An, đỉnh Sơn Trà.

---

## 5. Điểm yếu góc BA / sản phẩm

| # | Vấn đề | Sửa | Ảnh hưởng điểm |
|---|---|---|---|
| B1 | **Tiền đề chưa kiểm:** pain là lệch lịch/giờ/tiền, thiếu thông tin, hay không tin nguồn? | Phỏng vấn kiểu Mom Test, hỏi chuyện đã xảy ra trong 1 tháng qua. Đếm 3 loại than phiền. Kết quả quyết định giữ hay đổi trọng tâm (xem [07-phan-tich-de-tai-pstack.md](../../07-phan-tich-de-tai-pstack.md) mục 2) | R1 (14đ) + điều kiện cứng |
| B2 | Persona "nhóm bạn 2–4 người" quá rộng. Thực tế thường có **một người lên kế hoạch** cho cả nhóm | Đổi người dùng chính thành "người lên lịch trong nhóm bạn". Hỏi họ mất bao lâu, bị cả nhóm phàn nàn chỗ nào | R1, R3 |
| B3 | Chưa trả lời được "sao không dùng ChatGPT?" | Xem F1: cùng một yêu cầu, đếm vi phạm của AI chung so với AltF4, đo bằng `verify` | R3, R7 |
| B4 | Bảng impact §2 trống | Số người × số lần/tháng × số phút lên kế hoạch, lấy từ khảo sát hoặc ghi *(tự ước tính)* | R2 (11đ) |
| B5 | `personas.yaml` còn số của track A | Persona C1: xếp lịch một lần · sửa lịch nhiều lần trước ngày đi · xếp lại khi mưa. Số người dùng lấy từ nguồn công khai có link | R6 (12đ) |

---

## 6. Tính năng tạo khác biệt

Xếp theo **khác biệt ÷ công sức**. F1–F3 dùng lại `verify` hoặc `schedule`, nên rẻ và có thể làm trong hackathon **sau khi xong các việc P0**.

| # | Tính năng | Mô tả | Vì sao khác biệt | Công sức |
|---|---|---|---|---|
| F1 ⭐ | **"Kiểm lịch của bạn"** | Người dùng dán lịch trình lấy từ ChatGPT, blog hay TikTok. Model chỉ ánh xạ tên điểm sang `id` (tên lạ thì báo "chưa có dữ liệu"). `verify` đánh dấu từng vi phạm, ví dụ "11:30 Bảo tàng Chăm đã đóng", "Sơn Trà → Ngũ Hành Sơn mất ~35 phút chứ không phải 10", "vượt ngân sách 220k" | Giải luôn bài "không tin nguồn". Cho **slide so sánh có số**: AI chung X vi phạm, AltF4 0 vi phạm | Thấp |
| F2 | **Menu đánh đổi khi bất khả thi** | 2–3 lựa chọn đã kiểm (A8): "+150k thì đi được Bà Nà", "bỏ Hội An thì vừa tiền", "đi từ 7h thì kịp cả hai" | Đúng gợi ý C1 của BTC. Giám khảo dễ nhớ | Thấp–vừa |
| F3 | **Độ dư (slack) + phương án B** | Mỗi điểm hiện "trễ tối đa N phút thì lịch vẫn ổn". Kèm sẵn "nếu trễ quá N phút thì bỏ điểm X" | Chạm đúng nỗi lo "đến nơi thì đã đóng cửa". Chỉ cần code | Thấp |
| F4 | **Link Google Maps nhiều điểm** | Code sinh URL chỉ đường theo thứ tự, không cần API key | Bấm vào là đi được, rất thực dụng khi demo | Rất thấp |
| F5 | **Khoảnh khắc đúng giờ** | Dựa trên A4: tự xếp hoàng hôn, cầu Rồng phun lửa, chợ đêm vào đúng khung giờ | Lịch có chất "người địa phương" | Vừa (cần data kiểm) |
| F6 | Xếp lại giữa ngày (mưa, đóng cửa, đến muộn) | Dùng lại `verify` và `schedule` cho phần còn lại của ngày | Đúng lúc người dùng cần nhất | Sau hackathon |
| F7 | Gộp sở thích nhóm bằng bỏ phiếu · chia tiền theo người · nhiều ngày · chỗ ở làm điểm xuất phát | | | Sau hackathon |

**Không làm:** gợi ý "quán ngon nhất" (không đo được), giá hay giờ theo thời gian thực bằng cào web, agent tự do nhiều bước, đặt vé hoặc thanh toán tự động.

---

## 7. Thứ tự việc đề xuất

Mỗi đơn vị kết thúc bằng một trạng thái kiểm được.

1. **Trước CP2 (19:30 27/11), P0:**
   - `data/places.csv` 25–40 dòng, mỗi dòng có `source` và `checked_on`, có ca khó cố ý. Điền `DATA_CARD.md`.
   - `verify()` + `cost()` trong `codebase/tools.py`. Test bằng 10 kế hoạch viết tay: 5 hợp lệ, 5 cái mỗi cái một lỗi.
   - `eval/benchmark.csv` ≥10 câu (≥5 `kho`, ≥2 `tu_choi`). Nhóm **chốt** `metric_spec.yaml` và `spec.md` §7. Chạy `python run.py check` sạch cảnh báo.
   - Hẹn lịch phỏng vấn.
2. **Tối 27/11:**
   - Nối model thật trong `ai.py` theo `docs/connect-model.md`, key nằm trong `.env`.
   - Viết `parse_request`, `shortlist`, `propose` (bản gốc: model tự xếp giờ).
   - Chạy Lượt 1, ghi Run ID.
3. **Sáng 28/11:**
   - ≥3 phỏng vấn, mỗi người 1 file trong `evidence/interviews/`.
   - Mở rộng bộ thử lên 20–30 câu.
   - `eval/grade.py` đọc khối JSON và chạy `verify`. Đối chiếu với chấm tay 5 câu.
4. **Lượt 2 (trước 14:30 28/11):**
   - Áp dụng A1 (code xếp giờ). Đo Lượt 1 → Lượt 2 trong `eval/report.md`.
   - Chạy `simulate` ≥50 phiên.
5. **Còn thời gian:** F1 + slide so sánh với AI chung, sau đó F4, F3.

---

## 8. Hướng dẫn cho agent nhận việc

- Đọc theo thứ tự: file này → [AGENTS.md](../AGENTS.md) → [spec.md](../spec.md) → [docs/design.md](design.md) → [docs/roadmap.md](roadmap.md).
- Chỉ dùng thư viện chuẩn của Python. Thêm thư viện thì ghi vào `requirements.txt`.
- Giữ nguyên hợp đồng của `answer()`, `call_model()` và `@tool` (docstring đủ 4 ý: tên · input · output · có tác động ra ngoài không).
- **Không** tự bịa dữ liệu địa điểm và coi như thật. Data tự dựng phải gắn nhãn `synthetic` trong DATA_CARD, còn giờ và giá thật phải có nguồn công khai.
- **Không** tự viết bằng chứng pain hoặc trích dẫn. Việc đó chỉ con người làm.
- **Không** sửa ngưỡng hay metric sau CP2.
- Mọi thay đổi thiết kế phải ghi vào `spec.md` §10 (changelog) kèm lý do.
