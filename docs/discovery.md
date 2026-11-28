# Discovery & Problem Framing — Lịch trình 1 ngày ở Đà Nẵng

> Áp phương pháp của lab Day 02 (Double Diamond · Job Story · Opportunity Solution Tree · Assumption Map · The Mom Test · ma trận mơ hồ × phức tạp · No AI / Rule / Workflow / Agent · AI Canvas · Google PAIR · 4 rủi ro Cagan) vào bài AltF4.
> Viết ngày 27/11/2026, vai BA senior. **Mọi con số trong file đều là giả thuyết hoặc *(tự ước tính)*** cho đến khi có phỏng vấn hoặc khảo sát thật. File này **không phải bằng chứng pain**: bằng chứng phải nằm trong `evidence/`.
> Liên quan: [spec.md](../spec.md) · [design.md](design.md) · [architecture-review.md](architecture-review.md) · [eval/benchmark.csv](../eval/benchmark.csv) · [eval/metric_spec.yaml](../eval/metric_spec.yaml)

---

## 1. Discover — mở rộng: bài toán thật có thể là gì?

### 1.1 Job Stories ứng viên

Gom từ đề track C1 và mô tả của nhóm. Chưa lọc.

| # | Job Story | Loại bài toán |
|---|---|---|
| J1 | Khi nhóm đã chốt đi Đà Nẵng thứ Bảy, **tôi (người lên lịch)** muốn có một lịch từng giờ không lệch giờ mở cửa và không đi vòng, để cả nhóm không mất buổi chiều vì đến nơi thì đã đóng cửa | Xếp lịch khả thi (TTDP/OPTW) |
| J2 | Khi cả nhóm góp 200k/người, tôi muốn biết trước tổng tiền ăn, vé và xe, để không phải xin thêm tiền giữa chừng | Kiểm soát ngân sách |
| J3 | Khi đọc 5 bài "Đà Nẵng 1 ngày" trên TikTok hoặc blog, tôi muốn biết lịch nào làm được thật, để không tin nhầm bài quảng cáo | Tin cậy nguồn / kiểm lịch |
| J4 | Khi lịch không vừa tiền hoặc không đủ giờ, tôi muốn biết bỏ hoặc nới chỗ nào là ít thiệt nhất, để cả nhóm chốt nhanh mà không cãi nhau | Giải thích bất khả thi |
| J5 | Khi lần đầu đến Đà Nẵng, tôi muốn biết có những chỗ nào hợp gu nhóm (biển, ăn vặt, check-in), để không bỏ lỡ chỗ đáng đi | Khám phá (discovery) |
| J6 | Khi trời mưa hoặc một điểm đột ngột đóng cửa, tôi muốn xếp lại phần còn lại của ngày, để không bỏ phí nửa ngày | Xếp lại giữa ngày |
| J7 | Khi mỗi người trong nhóm thích một kiểu, tôi muốn gộp sở thích công bằng, để không ai thấy bị bỏ rơi | Ra quyết định nhóm |

> **Phạm vi địa lý (nhóm đã chốt 27/11):** Đà Nẵng **gồm cả Hội An**. Hội An là cụm xa (mất nửa ngày để đi và chơi, giống Bà Nà), không phải "tỉnh khác". Câu từ chối "ngoài phạm vi" dùng nơi rõ ràng nằm ngoài, ví dụ Hà Giang. Nhóm cần kiểm lại địa giới hành chính từ nguồn chính thức trước khi ghi trong slide.

### 1.2 Reframe — 3 cách hiểu chính

Phân tích chi tiết theo phương pháp pstack (reframe, attack the premise, 3 kiến trúc): [07-phan-tich-de-tai-pstack.md](07-phan-tich-de-tai-pstack.md).

| Bài toán | Job Story | Đã có giải pháp tốt chưa? | Đo được bằng code? |
|---|---|---|---|
| **A. Thiếu thông tin** | J5 | Rồi: Google Maps, TikTok, listicle | Khó, vì "hợp gu" không có đáp án đúng |
| **B. Không xếp được lịch khả thi** *(lõi hiện tại)* | J1, J2, J4 | Một phần: app lịch trình và AI chung **không kiểm** giờ, tiền, quãng đường | **Có:** đếm vi phạm bằng `verify()` |
| **C. Không tin nguồn** | J3 | Chưa | Có: dùng lại `verify()` trên lịch người dùng dán vào |

**Giả thuyết làm việc:** B là lõi. C là phần mở rộng rẻ, vì dùng lại cùng bộ kiểm. A thì loại.
Phỏng vấn ở mục 4 sẽ quyết định giữ hay đổi giả thuyết này. Xem tín hiệu phản bác ở 4.4.

---

## 2. Define — thu hẹp

### 2.1 Opportunity Solution Tree

```text
OUTCOME (đo được): Người lên lịch cho nhóm có một lịch 1 ngày ở Đà Nẵng đi được thật
                   (0 lần đến nơi đã đóng cửa, không vượt ngân sách), với ít thời gian lên kế hoạch hơn
├── O1: Thông tin giờ mở cửa, giá, khoảng cách nằm rải rác nhiều nguồn, phải tự ghép     (J1, J2)
├── O2: Không biết lịch mình ghép có khả thi không cho đến khi đi thật                   (J1, J3)
├── O3: Không biết nên nới ràng buộc nào khi lịch không vừa                              (J4)
├── O4: Chi phí thực tế (gồm xe) vượt dự tính                                            (J2)
└── O5: Kế hoạch vỡ giữa ngày (mưa, đến muộn, điểm đóng)                                 (J6, để sau)
     ✗ "Chatbot du lịch AI", "app lịch trình", "bản đồ tương tác"  ← đây là SOLUTION, gạch khỏi tầng này
```

Lát cắt hackathon phủ **O1 + O2 + O3**. O4 nên đưa vào nếu kịp (xem architecture-review A2). O5 để sau hackathon.

### 2.2 Quy trình hiện tại (giả thuyết, phải kiểm bằng phỏng vấn)

```text
HIỆN TẠI — ước 60–180 phút/lần lên lịch (tự ước tính, khảo sát cho ≈ 90 phút, xem spec.md §2)

[1. Tìm "Đà Nẵng 1 ngày" trên Google/TikTok: 20–40']
 → [2. Chọn điểm, ghi ra note/nhóm chat: 10–20']
 → [3. Tra giờ mở cửa + giá từng điểm trên Maps: 15–40']   ← BOTTLENECK ứng viên #1
 → [4. Ước khoảng cách, sắp thứ tự: 10–30']                ← BOTTLENECK ứng viên #2
 → [5. Cộng tiền nhẩm: 5–10']
 → [6. Gửi nhóm, bị phản đối, sửa lại: 10–40', lặp]         ← BOTTLENECK ứng viên #3
 → [7. Đi thật: lệch giờ / đóng cửa / vượt tiền]            ← chi phí ẩn, đo bằng số lần gặp
```

Phỏng vấn cần trả lời: **bước nào thật sự đau nhất**, và hậu quả ở bước 7 xảy ra bao nhiêu lần trong 1 chuyến đi gần nhất.

### 2.3 Quy trình tương lai (theo thiết kế, xem `design.md`)

```text
[Người lên lịch gõ 1 đoạn yêu cầu: 1']                         ← CON NGƯỜI
 → [AI trích ràng buộc; thiếu thì hỏi lại 1 câu]               ← AI
 → [Code lọc ứng viên ≤15]                                     ← RULE
 → [AI chọn điểm hợp gu]                                       ← AI
 → [Code xếp giờ + kiểm + tính tiền]                           ← RULE (nguồn sự thật)
 → [AI viết lý do; bất khả thi thì code tính cách nới, AI diễn đạt] ← AI + RULE
 → [Người lên lịch duyệt, gửi nhóm, xác nhận lại giờ/giá: 5–10'] ← CON NGƯỜI (boundary)
Phương án quay về: lịch sai / AI lỗi → người dùng tự tra theo quy trình cũ; output luôn ghi "giá, giờ tham khảo ngày …"
```

**Boundary:** AI không đặt vé, không thanh toán, không hứa giá hay giờ chắc chắn, không bịa địa điểm, không đưa lịch vi phạm ràng buộc cứng.

### 2.4 Problem Statement v0

| Trường | Nội dung |
|---|---|
| **Actor** | Người lên lịch trong một nhóm bạn trẻ 2–4 người (sinh viên / mới đi làm), lần đầu tự đi Đà Nẵng (gồm cả Hội An) 1 ngày, tự trả tiền |
| **Quy trình** | Tìm gợi ý → chọn điểm → tra giờ, giá → sắp thứ tự theo khoảng cách → cộng tiền → gửi nhóm, sửa → đi thật (mục 2.2) |
| **Bottleneck** | Bước 3–4 (tra giờ và sắp thứ tự khả thi) và bước 6 (sửa đi sửa lại); khảo sát n = 22: 13/22 gặp sự cố giờ hoặc quãng đường (`evidence/summary.md`) |
| **Impact** | ≈ 90 phút lên lịch/chuyến · 13/22 (59%) từng gặp sự cố giờ hoặc quãng đường · ≈ 2,5 chuyến tự đi/năm (khảo sát n = 22, xem `spec.md` §2) |
| **Success Metric** | (1) Vi phạm cứng trong lịch đưa ra: baseline = số vi phạm khi dán cùng yêu cầu vào AI chung (đo bằng `verify`) → target 0 ở ≥85% câu · (2) Thời gian lên lịch: baseline ≈ 90 phút (khảo sát) → target ≤10 phút gồm cả duyệt · (3) Ca bất khả thi có cách nới đã kiểm: ≥80% |
| **Boundary** | Chỉ đề xuất. Người dùng duyệt và tự xác nhận giờ, giá với nơi đến. Không có hành động ra ngoài |

### 2.5 Problem Statement v1 (thêm 3 trường)

| Trường | Nội dung |
|---|---|
| **AI intervention point** | (a) Biến câu nói tự do thành ràng buộc có kiểu · (b) chọn điểm hợp sở thích viết tự do · (c) chọn và diễn đạt cách đánh đổi khi bất khả thi · (d) viết lý do. **Không** để AI tính giờ, tiền, quãng đường |
| **Mức chọn** | **Workflow** (các bước định sẵn bằng code, AI ở 3–4 bước, vòng sửa có trần) |
| **Rủi ro & người kiểm** | Lịch trông hợp lệ nhưng dựa trên dữ liệu cũ → `checked_on` + lời nhắc xác nhận. AI hiểu sai ràng buộc (ví dụ ngân sách mỗi người và cả nhóm) → nhắc lại ràng buộc đã hiểu ở đầu output. Người kiểm: người lên lịch, trước khi gửi nhóm |

---

## 3. Chọn mức can thiệp

### 3.1 Ma trận độ mơ hồ × độ phức tạp

Bài nằm ở ô **mơ hồ cao × phức tạp cao**, nhưng **tách được** thành hai phần:

| Phần | Mơ hồ | Phức tạp | Mức phù hợp |
|---|---|---|---|
| Hiểu yêu cầu, sở thích ("chỗ chill, ăn vặt, đừng xa quá") | Cao | Thấp | AI (1 bước) |
| Xếp giờ, kiểm giờ mở cửa, tính tiền, quãng đường | **Thấp** (đúng/sai rõ) | Cao (nhiều ràng buộc ghép) | **Rule / code** |
| Chọn cách nới khi bất khả thi | Trung bình | Trung bình | Code sinh và kiểm lựa chọn, AI diễn đạt |

Vì phần khó đo đều là xác định, bài **không cần Agent**. Workflow có AI ở các bước mơ hồ là đủ.

### 3.2 So sánh 4 mức

| Mức | Phương án | Đủ khi | Vì sao không/có |
|---|---|---|---|
| No AI | Template lịch mẫu và checklist "kiểm giờ mở cửa" | Người dùng chỉ thiếu thông tin (bài A) | Không giải bài B: vẫn phải tự ghép và tự kiểm |
| Rule | Form chọn tag + solver xếp lịch | Người dùng chịu điền form có cấu trúc | Mất phần "hiểu câu nói tự do" và lý do. **Là phương án quay về** nếu AI parse kém |
| **Workflow** ✅ | Mục 2.3 | Thứ tự bước biết trước, cần kiểm cố định, chi phí có trần | Chọn |
| Agent | AI tự gọi công cụ, tự quyết khi nào kiểm | Đường đi không đoán trước | Tốn token, khó tái lập, có thể "quên" kiểm. Không cần |

### 3.3 AI Canvas

| Ô | Nội dung |
|---|---|
| Prediction | Ràng buộc có cấu trúc từ câu tự do · tập điểm hợp gu · cách nới "ít thiệt nhất" theo cảm nhận người dùng |
| Judgment | Người dùng cân nhắc đánh đổi (thêm tiền hay bỏ điểm), và độ tin của giờ, giá |
| Action | Người dùng gửi lịch cho nhóm, tự xác nhận với nơi đến. AI không hành động ra ngoài |
| Outcome | Số vi phạm cứng · % ca bất khả thi có cách nới đã kiểm · thời gian lên lịch |
| Input | `places.csv` (giờ, giá, tag, tọa độ, nguồn, ngày kiểm) + yêu cầu người dùng. **Chưa có. Phải dựng trước CP2** |
| Feedback | Câu trượt trong `eval/run-N.csv` · người dùng thử (`validation/log.md`) báo sai giờ/giá |

### 3.4 Hai câu hỏi Google PAIR

- **Augment hay automate?** **Augment.** Người dùng giữ quyết định đi đâu, vì sai thì mất tiền và công. *(Cần xác nhận khi phỏng vấn: hỏi "lần trước bạn có tự kiểm lại lịch người khác gửi không?")*
- **Sai kiểu nào tệ hơn?**
  - **Đưa lịch sai mà trông như đúng** (dương tính giả về khả thi) tệ hơn nhiều so với **nói "không xếp được" khi thật ra xếp được** (âm tính giả).
  - Vì vậy thiết kế nghiêng về phía chặt: `verify` là cổng bắt buộc, metric `khong_vi_pham_cung` và `khong_bia_dia_diem` là ràng buộc cứng.
  - Âm tính giả cũng bị chặn: mỗi câu thử ghi status được chấp nhận ở đầu `pass_criterion`. Câu xếp được mà output trả `infeasible` hay `ask_back` thì trượt metric `khong_vi_pham_cung`, để sản phẩm không "từ chối cho an toàn".

---

## 4. Kiểm chứng (Mom Test)

### 4.1 Assumption Map

Xếp theo thứ tự kiểm: quan trọng cao, bằng chứng thấp thì kiểm trước.

| # | Giả định | Loại | Quan trọng | Bằng chứng hiện có | Kiểm bằng |
|---:|---|---|---:|---:|---|
| A1 | Người lên lịch từng gặp ≥1 lần "đến nơi đã đóng cửa / đi vòng / vượt tiền" trong chuyến tỉnh lạ gần nhất | Value | 5 | 1 | Phỏng vấn Q4–Q6, khảo sát S4 |
| A2 | Bước đau nhất là ghép lịch khả thi, không phải tìm chỗ hay không tin nguồn | Value | 5 | 1 | Phỏng vấn Q3, khảo sát S3 |
| A3 | Người dùng đã thử dán yêu cầu vào AI chung, và lịch AI chung có vi phạm đo được | Value | 4 | 1 | Phỏng vấn Q7 + tự thử: dán 5 câu benchmark vào AI chung, chạy `verify` |
| A4 | Nhóm dựng được 25–40 điểm có giờ, giá, nguồn công khai và ngày kiểm trong 1 tối | Feasibility | 5 | 2 | Đạt dựng thử 10 dòng trong 30' |
| A5 | Model parse đúng ngân sách (mỗi người hay cả nhóm), giờ, ngày từ tiếng Việt tự do, kể cả không dấu | Feasibility | 4 | 2 | Câu thử T06, K04, K05 |
| A6 | Người dùng chấp nhận giờ, giá là "tham khảo" và tự xác nhận lại | Usability | 3 | 1 | Phỏng vấn Q8 |
| A7 | Chi phí mỗi lịch đạt ở mức vài trăm đồng với model nhỏ | Viability | 3 | 2 | `simulate` |

### 4.2 Kịch bản phỏng vấn (≥3 người ngoài nhóm, 10–15')

Đối tượng: người **đã tự lên lịch** cho một chuyến đi tỉnh lạ trong khoảng 6 tháng gần nhất, ưu tiên Đà Nẵng. Ghi P1, P2… Không ghi tên. Mỗi người 1 file `evidence/interviews/Pn.md`.

1. Lần gần nhất bạn đi chơi một tỉnh/thành mới là khi nào? Đi với ai, mấy người?
2. Ai lên lịch? Bạn bắt đầu từ đâu? Kể lại từng bước.
3. Bước nào mất thời gian nhất? Tổng cộng khoảng bao lâu?
4. Lúc đi thật, có chỗ nào không như dự tính không? (đóng cửa, đi xa hơn tưởng, hết giờ, tốn hơn)
5. Chuyện đó làm nhóm mất gì? (bao nhiêu tiền, bao nhiêu thời gian, có cãi nhau không)
6. Trong chuyến đó, chuyện kiểu này xảy ra mấy lần?
7. Bạn đã từng dùng app, ChatGPT/Gemini hay bài review để lên lịch chưa? Kết quả ra sao? Có chỗ nào sai không?
8. Bạn có tự kiểm lại giờ mở cửa, giá trước khi đi không? Bằng cách nào?
9. **(Lấy câu thử thật)** "Nếu nhờ một người bạn rành Đà Nẵng lên lịch hộ, bạn sẽ nhắn đúng câu gì?" → chép **nguyên văn** vào phần ghi chép.

**Không hỏi:** "Bạn có muốn app AI lên lịch không?", "Ý tưởng này hay không?", "Bạn có dùng không?". Lời khen không phải bằng chứng.

### 4.3 Khảo sát (≥20 người, Google Form, 3')

- S1: 12 tháng qua bạn tự đi tỉnh lạ mấy lần? (0 / 1 / 2–3 / ≥4)
- S2: Lần gần nhất, ai lên lịch? (tôi / bạn khác / không ai, đi đâu tính đó)
- S3: Bước nào tốn công nhất? (tìm chỗ / tra giờ, giá / sắp thứ tự cho khỏi đi vòng / thống nhất với nhóm / không tin review)
- S4: Lần gần nhất có gặp chuyện nào sau đây không? (đến nơi đã đóng · đi xa hơn dự tính · vượt ngân sách · không gặp) — cho chọn nhiều
- S5: Lên lịch mất khoảng bao lâu? (<30' / 30–60' / 1–2h / >2h)
- S6: Đã dùng AI chung để lên lịch chưa? Có phát hiện sai không? (chưa / có, không thấy sai / có, thấy sai: ghi sai gì)
- S7 **(lấy câu thử thật):** "Viết đúng câu bạn sẽ gõ để nhờ lên lịch 1 ngày ở Đà Nẵng." (trả lời tự do)

> **Vì sao S7 và Q9 quan trọng:** `run.py check` đòi **≥1/3 câu thử có nguồn `nguoi_dung` / `data_that`**. Hiện 30/30 câu là `tu_viet` (xem mục 6). Lấy ≥10 câu nguyên văn từ S7/Q9 để thay hoặc thêm vào benchmark trước CP3. **Chỉ dùng câu người thật đã viết, không sửa lời.**

### 4.4 Tín hiệu xác nhận / phản bác và quyết định đổi hướng

| Nếu thấy | Thì |
|---|---|
| ≥2/3 người phỏng vấn (hoặc ≥50% khảo sát S4) từng gặp đóng cửa / đi vòng / vượt tiền | **Giữ lõi B** |
| Đa số chọn "không tin review" ở S3, hoặc kể chuyện AI chung đưa lịch sai | Đẩy F1 "Kiểm lịch của bạn" lên thành tính năng chính (bài C) |
| Đa số chọn "tìm chỗ" và không gặp sự cố ở S4 | Tiền đề B yếu. Ghi trung thực vào §10, cân nhắc thu hẹp (BTC cho đủ điểm nếu số thật) |
| Đa số chọn "thống nhất với nhóm" | Pain thật là J7 (ra quyết định nhóm). Ghi lại, để sau hackathon |
| Thời gian lên lịch phần lớn <30' | Impact theo thời gian thấp. Chuyển trọng tâm impact sang **số sự cố tránh được** |

---

## 5. Quyết định theo 4 rủi ro

| Rủi ro | Mức | Lý do | Giảm bằng |
|---|---|---|---|
| Value | **Cao (chưa kiểm)** | Chưa có phỏng vấn hay khảo sát | Mục 4, trước CP3 |
| Usability | Thấp–TB | Output là bảng giờ + tổng tiền + lý do, quen thuộc. Rủi ro: người dùng tin tuyệt đối | Nhắc lại ràng buộc đã hiểu · "giá, giờ tham khảo ngày …" |
| Feasibility | **TB–Cao** | Chưa có data, chưa nối model, chưa có `verify` | Thứ tự trong architecture-review mục 7 |
| Viability | Thấp | Model nhỏ, ≤6 lần gọi/lượt, công cụ chỉ đọc, không dữ liệu cá nhân | `simulate` ≥50 phiên |

**Quyết định: Not Yet → Go có điều kiện.**
- Làm tiếp phần kỹ thuật song song với kiểm chứng.
- Value phải được kiểm trước CP3 (10:00 28/11).
- **Ngưỡng dừng:**
  - Nếu <2/3 người phỏng vấn từng gặp sự cố ở S4/Q4, đổi trọng tâm theo bảng 4.4 và ghi vào `spec.md` §10.
  - Nếu Lượt 1 có <50% câu `thuong` sạch vi phạm, chuyển việc xếp giờ sang code (architecture-review A1) trước khi làm thêm tính năng.

---

## 6. Từ discovery sang bộ câu thử

### 6.1 Lưới phủ input (5 chiều)

| Chiều | Giá trị phủ trong benchmark |
|---|---|
| Số người | 1 · 2 · 3 · 4 · 5 · thiếu |
| Ngân sách | rộng · vừa · sát · quá thấp · mơ hồ · theo người hoặc cả nhóm · thiếu |
| Khung giờ / ngày | cả ngày · nửa ngày · buổi tối · 4 tiếng · sáng sớm · đêm · ngày trong tuần · cuối tuần · thiếu ngày |
| Sở thích / ràng buộc | biển · hải sản · ăn vặt · cafe · check-in · văn hoá · thiên nhiên · ăn chay · dị ứng · tránh biển · đặc sản · mâu thuẫn |
| Cách viết | chuẩn · không dấu/teencode · tiếng Anh · kèm lịch tự soạn · kèm lệnh chèn |

### 6.2 Câu khó theo 4 lớp (`spec.md` §5)

| Lớp | Câu thử |
|---|---|
| 1 · Nguồn sự thật (điểm đóng, không có trong data, tiền đề sai) | K06, K13, K14, K15 |
| 2 · Mơ hồ / thiếu thông tin | K03, K04, K05, K09 |
| 3 · Ngoài phạm vi / tấn công | K12 (lệnh chèn kèm yêu cầu hợp lệ), R01–R06 |
| 4 · Đặc thù lĩnh vực (bất khả thi, ăn uống, cụm xa) | K01, K02, K07, K08, K10, K11 |

### 6.3 Dữ liệu `places.csv` mà benchmark cần

Đạt dựng theo bảng này. Chỗ nào nhóm tự đặt thì gắn nhãn `synthetic`.

| Cần trong data | Câu thử dùng |
|---|---|
| Điểm ở đủ 5 cụm: Mỹ Khê – Ngũ Hành Sơn, Sơn Trà, trung tâm, Bà Nà (cụm xa), Hội An (cụm xa, thuộc phạm vi) | T01–T09, K01, K10, K11 |
| Bảo tàng Điêu khắc Chăm có giờ mở và ngày nghỉ **theo nguồn chính thức** | K06 |
| Quán có tag `chay`, quán có tag `hai_san`; ≥2 quán vừa có tag `chay` vừa không có tag `hai_san` cho mỗi bữa trưa và tối, giá đủ để 3 người ăn 2 bữa trong 900k | K07, T01 |
| ≥3 quán giá ≤ 50.000đ/người và ≥3 điểm miễn phí **gần nhau trong một cụm**, để 2 người đi 8:00–20:00 trong 250k **kể cả tiền xe** (K08 có đáp án duy nhất là xếp được). Khi có `transport_rates.csv`, Quân tính lại K08 bằng `cost`; nếu không cách nào xếp vừa 250k thì đổi K08 **trước khi chạy Lượt 1** | K08 |
| Điểm có tag `trong_nha`, `bien`, `check_in`, `cafe`, `an_vat`, `cho`, `dac_san`, `van_hoa`, `tam_linh`, `thien_nhien`, `yen_tinh`, `soi_dong` | Đa số câu |
| Cầu Rồng, chợ đêm có khung giờ hoặc ngày cụ thể (`best_windows` / `event_days`) | T05, K09 |
| Chợ Hàn có giờ đóng cửa theo nguồn | K14 |
| Bà Nà: giá vé người lớn **theo nguồn chính thức**, `visit_min` dài, `travel_min` xa. K10 coi là không xếp được vì vé cho 2 người vượt 1.200.000đ; nếu giá vé thật ≤ 600.000đ/người thì báo Quân đổi K10 **trước khi chạy Lượt 1** | K01, K10 |
| Hội An có ≥1 điểm cụm `hoi_an` và ≥1 quán ăn tối, giá đủ cho 2 người trong 1 triệu kể cả xe | K11 |
| **Không** có quán tên "Bún chả cá Cô Bảy Hòa Khánh" (tên dựng cho ca không có dữ liệu) | K13 |

### 6.4 Câu dự phòng (chưa đưa vào, đủ 30 câu)

Mưa cả ngày (cần dữ liệu thời tiết, ngoài lát cắt) · khung giờ qua đêm "20h đến 8h" · nhóm 12 người · "bỏ điểm X" ở lượt thứ hai (cần trạng thái phiên, xem architecture-review A6).
