# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử (phần nối model) | Claude Code (Sonnet 5.5) | Viết `call_bedrock()` và `embed()` trong `codebase/ai.py` (Haiku 4.5 qua Amazon Bedrock Converse, token lấy từ `usage` của API); thêm biến AWS vào `.env.example`, `boto3` vào `requirements.txt` | Công chạy lại bằng khoá AWS của mình, kiểm gọi Haiku và Titan embedding thành công; chạy `python run.py check` và 21 test của `tests/` sau khi thêm | Công |
| Prompt / thiết kế lời gọi mô hình | *(chưa làm)* | `codebase/prompts.py` chưa viết, `agent.py` chưa gọi model | | Công |
| Đào data (viết script đếm, gợi ý nhãn) | | | Kiểm tay __ dòng, khớp __ | |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | | | Mỗi câu thử có `source`; câu thử AI viết được ghi rõ | |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Slide, văn bản (spec, canvas) | Claude Code (Sonnet 5.5) | Soạn nháp `spec.md` §4–§7, §9–§10 và dòng CP2 của `canvas.md` từ nội dung canvas CP1. Bản nháp này sau đó được thay bằng bản chuyên biệt hoá cho Đà Nẵng của nhóm (`docs/design.md`), nên không còn trong repo | Công đọc và quyết chuẩn "đạt" ở §7 | Công |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).

*(Các dòng còn trống ở trên do người phụ trách từng phần tự khai; không điền thay.)*
