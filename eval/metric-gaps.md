# Lỗ hổng của bộ metric và cách nhóm xử lý

> Ghi ngày 27/11, sau khi khóa chuẩn "đạt" ở CP2. File này **không sửa** `spec.md` §7 hay `eval/metric_spec.yaml`. Chuẩn "đạt" và 4 metric giữ nguyên. Mục đích là nhóm tự nói ra điểm mù của cách đo, đo thêm cho thấy rõ, và nói đã làm gì với nó.

## 1. Lỗ hổng chính: metric đo "đi được", chưa đo "đáng đi"

4 metric đã khóa trả lời được các câu: lịch có **khả thi** không (0 vi phạm giờ mở cửa, di chuyển, ngân sách), có **bịa** không, có **nói được "không xếp được"** không, có **từ chối đúng** không. Chưa có metric nào trả lời: lịch có **đáng đi** không.

Một lịch để trống nửa ngày, hay bắt nhóm ăn ba bữa liền nhau, vẫn qua cả 4 metric.

**Ví dụ thật** (bản chạy thử ngày 27/11, khi còn dùng luật code thay model). Đầu vào: "2 người, 800k, 8h–20h, thích biển và cà phê". Kết quả nhận được:
- Cả bữa trưa và bữa tối đều là **quán chay**, dù không ai yêu cầu.
- Có **khoảng trống 4 tiếng 20 phút** (12:39–17:00).
- Chỉ có 4 điểm trong 12 tiếng.

Lịch này vẫn qua cả 4 metric.

**Đo trên bộ câu thử** (`python eval/quality.py eval/run-try.csv`, lần thử bằng một bản prompt nháp trước Lượt 1, **không tính là một lượt**; chạy lại trên Lượt 1 để có số chính thức): **9 trên 18** lịch có ít nhất một khoảng chờ trên 60 phút. Trung bình mỗi lịch có 82 phút chết, và chỉ 60% khung giờ có hoạt động.

## 2. Vì sao không sửa metric

Luật cuộc thi khóa chuẩn "đạt" lúc 19:30 Thứ Sáu 27/11. Đổi ngưỡng hay thêm metric vào chuẩn "đạt" sau mốc đó bị 0 điểm khối đánh giá. Ngoài ra, nếu đổi thước đo sau khi đã thấy kết quả thì con số không còn đáng tin. Vì vậy nhóm làm hai việc khác:
1. **Báo cáo thêm, tách riêng**: chỉ số phụ đo bằng code, in cạnh 4 metric, không cộng vào % đạt.
2. **Sửa ở sản phẩm**, rồi dùng chỉ số phụ để chứng minh bản sửa có tác dụng.

## 3. Chỉ số phụ: `eval/quality.py`

Script chỉ đọc file lượt chạy, không ghi gì. Ràng buộc lấy từ `c=` của câu, giống cách grader làm.

| Chỉ số | Cách tính | Hướng tốt |
|---|---|---|
| Phút chết / lịch | Tổng (giờ đến điểm sau − giờ rời điểm trước − phút di chuyển) | Thấp |
| Lịch có khoảng chờ > 60 phút | Số lịch có ít nhất một khoảng như vậy | Thấp |
| Lịch có quán ăn thừa | Số quán loại `an` > số bữa bắt buộc | 0 |
| % khung giờ có hoạt động | Tổng thời gian ở các điểm / độ dài khung giờ | Cao |
| % ngân sách dùng | `cost()` / ngân sách (chỉ để tham khảo, không cần dùng hết) | — |

Lệnh: `python eval/quality.py eval/run-1.csv eval/run-2.csv`. Script in bảng từng câu và bảng so sánh hai lượt.

## 4. Đã sửa gì ở sản phẩm (trước Lượt 1)

| Vấn đề | Nguyên nhân | Sửa | Ai |
|---|---|---|---|
| Model tự nhẩm giờ nên sai nhiều, phải sửa nhiều vòng | Model vừa chọn điểm vừa tính giờ | Model chỉ chọn **tập điểm** (`{"ids": [...]}`). Code thử mọi thứ tự và tính giờ (`verify.schedule`). Sai thì `verify.diagnose` nói lý do để model chọn lại | Đức |
| Khoảng trống lớn | Lịch đến sớm nhất có thể, bữa tối không được bắt đầu trước 17:00 | `verify.fill` thêm điểm khi lấp bớt được ít nhất 30 phút trống. `verify.stretch` kéo dài thời gian ở lại. `schedule` chọn thứ tự có tổng thời gian ở lâu nhất. Output ghi rõ "rảnh khoảng …" khi còn trống từ 30 phút | Đức |
| Model bỏ điểm người dùng bắt buộc ghé | Model không bị buộc giữ | `agent._plan` luôn ghép `c.must` vào tập model chọn | Đức |
| Hai bữa chay dù không ai yêu cầu | 5/13 quán ăn là chay và rẻ nhất, nên khi xếp theo giá chúng luôn lên đầu | `verify.score()` hạ hạng quán chay khi nhóm không ăn chay (prompt cũng dặn) | Công |
| Từ chối nhầm ca bất khả thi (K01, K02 bị coi là "nhiều ngày") | Luật `multi_day` trong prompt quá rộng | Prompt: chỉ `multi_day` khi người dùng **nói rõ** nhiều ngày. Quá nhiều điểm, quá xa hay quá ít tiền thì vẫn `ok`, để code nói "không xếp được" | Công |
| Lịch tự dán bị coi là bắt buộc nên báo "không xếp được" (K15) | Mọi điểm người dùng nhắc đều vào `must_names` | Prompt: lịch tự soạn hỏi "ổn không" thì không bắt buộc, đưa lịch thay thế đã kiểm (đúng spec §5) | Công |
| Quán ở Hòa Khánh bị từ chối là "nơi khác" (K13) | Model không biết Hòa Khánh thuộc Đà Nẵng | Prompt liệt kê các quận, huyện của Đà Nẵng là trong phạm vi | Công |

Các lỗi ở 4 dòng cuối được phát hiện khi chạy thử từng câu ngày 27/11, chưa phải Lượt 1. Mỗi chỗ sửa là **luật chung**, không so khớp nguyên văn câu thử nào.

## 5. Còn lại: nói thẳng khi pitch

- **Vẫn còn khoảng trống buổi chiều** ở một số lịch (ví dụ câu demo còn trống khoảng 2 tiếng trước bữa tối). Đây là ứng viên cải tiến cho Lượt 2, đo bằng `quality.py`.
- **Thiếu dữ liệu.** Ở trung tâm, các quán ăn trưa không chay có giá rẻ còn ít; điểm tham quan mở buổi chiều và cho ở lâu cũng ít. Tối đa 6 điểm/ngày nên lịch dễ bị hổng. Cách sửa đúng là bổ sung data có nguồn (việc của Đạt), không phải chỉnh prompt.
- **Khớp sở thích chưa có metric chung.** Hiện chỉ chấm qua điều kiện riêng của từng câu (T09, K09 trượt vì thiếu tag). Chỉ số phụ chưa đo được phần này, vì `c=` không ghi sở thích.
- **Lý do (`why`) có thể dùng tính từ không có trong data**, ví dụ gọi một quán cà phê là "yên tĩnh" khi tag không có `yen_tinh`. Metric (b) chỉ kiểm id, giá, giờ, không kiểm chữ. Đã chặn một phần bằng prompt. Cách sửa tiếp: so từ khóa trong lý do với tag.
- **Metric (c) chỉ có 3 câu áp dụng**, nên ngưỡng 80% thực chất là 100%. Thêm câu bất khả thi ở CP3 (chỉ thêm, không sửa câu cũ) thì metric này mới có ý nghĩa.

## 6. Cách trình bày khi pitch (khoảng 30 giây, slide "Chúng tôi đo gì, và chưa đo gì")

> "4 metric của chúng tôi chứng minh lịch **đi được**: không có quán đóng cửa, không vượt tiền, không bịa. Nhưng khi tự soi, chúng tôi thấy một lịch trống 4 tiếng vẫn qua cả 4 metric. Chuẩn 'đạt' đã khóa nên chúng tôi không sửa. Thay vào đó chúng tôi đo thêm 'thời gian chết' bằng code: lúc đầu 9/18 lịch có khoảng trống trên 1 tiếng. Sau khi để AI chọn điểm, code xếp giờ và lấp chỗ trống: [số Lượt 1] → [số Lượt 2]."

**Q&A chuẩn bị sẵn:**
- *"Sao không thêm metric chất lượng vào chuẩn 'đạt'?"* Chuẩn đã khóa trước khi có kết quả, đổi lúc này là chỉnh thước đo cho đẹp số. Chúng tôi báo cáo tách riêng.
- *"Vậy AI làm gì nếu code tính hết giờ và tiền?"* AI hiểu câu tự do (ngân sách theo người, ai ăn chay, lệnh chèn), **chọn điểm và thứ tự** theo gu, quyết định lấp khoảng trống ra sao, và viết lý do. Code chỉ bảo đảm không ra lịch sai.
