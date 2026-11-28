# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử (phần nối model) | Claude Code (Sonnet 5.5) | Viết `call_bedrock()` và `embed()` trong `codebase/ai.py` (Haiku 4.5 qua Amazon Bedrock Converse, token lấy từ `usage` của API); thêm biến AWS vào `.env.example`, `boto3` vào `requirements.txt` | Công chạy lại bằng khoá AWS của mình, kiểm gọi Haiku và Titan embedding thành công; chạy `python run.py check` và 21 test của `tests/` sau khi thêm | Công |
| Prompt / thiết kế lời gọi mô hình | *(Đức tự khai phần `prompts.py` bản đầu, commit `fb9ef84`)* | | | Đức |
| Sửa prompt sau khi chạy thử, đo chất lượng lịch | Claude Code (Opus 5.5) | Chạy thử từng câu bằng model thật, tìm 4 lỗi (K01/K02 từ chối nhầm là `multi_day`, K15 coi lịch tự dán là bắt buộc, K13 coi Hòa Khánh là nơi khác, quán chay luôn lên đầu). Sửa bằng luật chung trong `SYSTEM_PARSE` (`prompts.py`) và `verify.score()`; `maxTokens` 2048, `temperature` 0.2 trong `ai.py`. Viết `eval/quality.py` (chỉ số phụ, không thay chuẩn "đạt") và `eval/metric-gaps.md` | Công đọc lại từng dòng prompt đổi; chạy lại K01, K02, K13, K15, R03, R04 và 29 test; Đức duyệt dòng đổi ở `verify.py` | Công |
| Thu thập data địa điểm (`data/places.csv`, `travel_override.csv`, `transport_rates.csv`) | Claude Code (Opus 5.5), agent con có tìm web và trình duyệt | Theo đặc tả `docs/prompt-thu-thap-data.md`: tra trang chính thức, cổng du lịch Đà Nẵng, Google Maps, Michelin, trang giá Grab; ghi 39 dòng kèm link nguồn và ngày kiểm, ghi chú `data/collection-notes.md`; tự kiểm schema bằng script. Sau đó tra bổ sung giá cho 5 dòng thiếu, bỏ 5 dòng không tìm được số (không đoán) → còn 34 dòng | Đạt kiểm tay bằng cách mở lại link nguồn trong `places.csv` (có kiểm các link Michelin), quyết bỏ dòng thiếu dữ liệu thay vì đoán, chạy `python run.py` và test sau khi thêm data | Đạt |
| Đếm khảo sát, viết tổng hợp bằng chứng | Claude Code (Opus 5.5) | Đếm `evidence/survey/results.csv` bằng script theo đúng cách đếm ghi trước ở `questions.md` (lọc câu 3, câu 5 → n = 22); soạn `evidence/summary.md`, `spec.md` §1–§2 (bảng impact, số lượt khách từ nguồn công khai) | Đạt xác nhận mọi phiếu là người thật ngoài nhóm, đọc lại số và trích dẫn, duyệt giả định 10% *(tự ước tính)* trong bảng impact | Đạt |
| Rà câu hỏi phỏng vấn / khảo sát | Claude Code (Opus 5.5) | Soạn bản đầu bộ câu hỏi khảo sát hỏi về chuyến gần nhất (không hỏi "có thích không"), giả thuyết `evidence/hypothesis.md` | Form dùng thật là bản 13 câu nhóm tự sửa (`evidence/survey/questions.md`, `create_form.gs`); Đạt gửi form qua Zalo | Đạt |
| Viết câu thử (benchmark) | | | Mỗi câu thử có `source`; câu thử AI viết được ghi rõ | |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Slide, văn bản (spec, canvas) | Claude Code (Sonnet 5.5) | Soạn bản đầu `spec.md` §4–§7, §9–§10 và dòng CP2 của `canvas.md` từ nội dung canvas CP1. Bản nháp này sau đó được thay bằng bản chuyên biệt hoá cho Đà Nẵng của nhóm (`docs/design.md`), nên không còn trong repo | Công đọc và quyết chuẩn "đạt" ở §7 | Công |
| Web: nhiều phương án, sửa bằng lời, bản đồ tuyến | Claude Code (Opus 5.5) | Viết `answer_options`, `choose`, `_honor_new_likes` (`agent.py`), `propose_alternatives` và luật chỉ điểm theo giờ trong `SYSTEM_REVISE` (`prompts.py`), `/api/choose` (`web/server.py`), thẻ phương án + bản đồ Leaflet/OSRM + micro (`chat.js`, `style.css`). Tách phần hiểu yêu cầu của `answer()` thành `_understand()` | Kiểm: 30 câu thử ở chế độ giả cho output giống hệt trước khi sửa (khung eval không đổi); 31 test đạt; chạy thật kịch bản chọn phương án rồi "thay chỗ đi biển lúc 13h bằng quán cà phê"; chụp màn hình 1366 và 1920px | Công (Đức duyệt `agent.py`, `web/`) |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).

*(Các dòng còn trống ở trên do người phụ trách từng phần tự khai; không điền thay.)*
