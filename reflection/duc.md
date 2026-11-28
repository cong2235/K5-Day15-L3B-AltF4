# Reflection — Trịnh Minh Đức

1. **Vai trò + phần mình làm:**
   Mình làm phần code lõi không gọi model, ghép luồng AI vào code và làm cải tiến Lượt 2.
   - **Code lõi:** `domain.py` (kiểu dữ liệu, kiểm JSON ở biên), `verify.py` (10 mã vi phạm, mọi số tiền / giờ / quãng đường), `tools.py`, `agent.py` (parse → shortlist → propose → verify → repair tối đa 3 vòng → lịch hoặc cách nới), `rules.py` làm phương án dự phòng khi model trả JSON hỏng, và test trong `tests/test_core.py` (commit `2c6c0a0`).
   - **Nối AI:** bản đầu `prompts.py` và chat nhiều lượt (`fb9ef84`). Mình chia việc rõ: model chỉ chọn tập điểm, code xếp thứ tự và giờ. Sau đó sửa `propose`/`repair` để model trả thẳng JSON (`3b5727b`).
   - **Lượt 2:** sửa nhóm lỗi "điểm người dùng nêu không đi được → bỏ cả lịch", chạy `run-2` và `run-3` (`dc2ef4e`). Kết quả từ 27/30 lên 28/30.
   - **Khác:** khung chat trên web nối với agent (`c833869`), slide CP4 (`9b1a0d8`), duyệt phần `agent.py`, `verify.py`, `web/` mà Công sửa.

2. **AI hỗ trợ mình thế nào:**
   - **Công cụ:** mọi commit code của mình đều viết cùng Claude Code (Opus 5.5). Mình viết hợp đồng giữa các file trước (`agent.answer`, `domain.request_from_dict`) rồi cho agent viết theo.
   - **Phải sửa lần 1:** ở bước chọn điểm, model viết phân tích dài trước khối JSON, chạm `max_tokens` nên bị cắt và phải hỏi lại (2/5 câu khi chạy `eval --try 5`). Mình thêm câu `JSON_ONLY` vào lời nhắn. Token ra mỗi câu giảm từ 829–1414 xuống 318–397, không còn câu nào phải hỏi lại.
   - **Phải sửa lần 2:** bản sửa Lượt 2 đầu tiên ghi giá vé của một điểm không có trong lịch vào câu lý do. Như vậy là vi phạm `khong_bia_dia_diem`, làm K01, K10 tụt và `run-2` chỉ được 26/30. Mình bỏ con số đó khỏi câu lý do rồi chạy lại thành `run-3`, và vẫn giữ `run-2` trong repo.
   - **Cách mình kiểm:** đọc từng dòng đổi trong `verify.py`, chạy hết test (hiện có 42 test đạt) và chạy 30 câu bằng model giả để chắc không câu nào ra exception trước khi chạy model thật.

3. **Một câu thử trượt của nhóm và mình học được gì:**
   - **Câu K18 (Lượt 1):** khách muốn trưa 12h ăn bún bò Bà Thương rồi chiều ra biển Mỹ Khê. Quán chỉ mở 06:00–10:00, nên agent trả "không xếp được" cho cả ngày, dù ngày đó hoàn toàn đi được. Cách nới còn ghi "bỏ cả Mỹ Khê" nhưng lịch đi kèm vẫn có Mỹ Khê.
   - **Vì sao trượt:** danh sách vi phạm gửi cho `repair` không nói quán nào không làm bữa được. Vì vậy cả 4 vòng sửa model đều trả lại cùng một tập điểm.
   - **Mình học được:**
     - Một yêu cầu không làm được thì phải báo đúng yêu cầu đó và vẫn xếp phần còn lại, không bỏ cả lịch.
     - Lời nhắn sửa gửi cho model phải nói cụ thể sai ở đâu thì vòng sửa mới có tác dụng.
     - Sửa một lỗi có thể làm câu khác tụt (run-2). Vì vậy sau mỗi lần sửa phải chạy lại cả bộ câu thử, không chỉ chạy câu vừa sửa.
