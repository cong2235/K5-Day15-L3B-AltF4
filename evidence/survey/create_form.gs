/**
 * Tạo Google Form khảo sát "Lên lịch một ngày đi chơi ở nơi lạ" (nhóm AltF4, Track C).
 * Câu chữ khớp evidence/survey/questions.md — sửa câu hỏi thì sửa cả hai nơi.
 * Form một trang, 13 câu.
 *
 * Cách chạy:
 *   1. Mở https://script.google.com → New project → xoá code mẫu → dán toàn bộ file này.
 *   2. Ctrl + S để lưu → chọn hàm createSurvey → Run → cho phép quyền (Forms, Sheets).
 *   3. Xem Execution log: có link sửa form, link gửi đi, link Sheet kết quả.
 *   4. Mở link sửa form, xem lại một lượt, bấm Send để lấy link rút gọn.
 */
function createSurvey() {
  var form = FormApp.create('Khảo sát: lên lịch một ngày đi chơi ở nơi lạ');
  form.setDescription(
    'Nhóm sinh viên đang tìm hiểu cách mọi người lên lịch một ngày đi chơi khi tự đi du lịch ' +
    'ở tỉnh / thành phố chưa quen.\n\n' +
    '• Dành cho người trong 12 tháng qua đã tự đi chơi (không theo tour) ở nơi chưa quen, cùng bạn bè hoặc người thân.\n' +
    '• Khoảng 3 phút, 13 câu, hỏi về chuyến đi gần nhất của bạn.\n' +
    '• Ẩn danh: form không thu email, không hỏi tên.\n' +
    '• Kết quả chỉ dùng ở dạng số tổng hợp cho bài hackathon.'
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setConfirmationMessage('Cảm ơn bạn đã dành thời gian!');

  single(form, '1. Trong chuyến tự đi chơi gần nhất, ai là người lên lịch đi chơi?', [
    'Tôi lên lịch chính',
    'Tôi cùng lên lịch với người khác',
    'Người khác lên lịch, tôi đi theo'
  ], true);

  single(form, '2. Chuyến gần nhất đó bạn đi đâu?', [
    'Đà Nẵng / Hội An', 'Đà Lạt', 'Nha Trang', 'Phú Quốc', 'Hà Nội', 'TP.HCM', 'Sa Pa / Hà Giang'
  ], true, true);

  single(form, '3. Chuyến đó cách đây bao lâu?', [
    'Trong 1 tháng qua', '1–3 tháng', '3–6 tháng', '6–12 tháng', 'Hơn 12 tháng'
  ], true);

  single(form, '4. Chuyến đó đi mấy người (tính cả bạn)?', [
    '1', '2', '3–4', '5 trở lên'
  ], true);

  single(form, '5. Trong 12 tháng qua, bạn tự đi chơi kiểu này mấy chuyến?', [
    '0', '1', '2', '3–4', '5 trở lên'
  ], true);

  single(form, '6. Để lên lịch cho MỘT ngày đi chơi trong chuyến đó, bạn (hoặc người lên lịch) đã mất tổng cộng bao lâu?', [
    'Dưới 30 phút', '30–60 phút', '1–2 giờ', '2–4 giờ', 'Trên 4 giờ', 'Không biết'
  ], true);

  multi(form, '7. Khi lên lịch, bạn đã dùng những nguồn nào?', [
    'Google Maps',
    'TikTok / Reels / YouTube',
    'Nhóm Facebook du lịch',
    'Blog / bài review',
    'Tripadvisor',
    'App du lịch (Traveloka, Klook…)',
    'ChatGPT / Gemini / trợ lý AI khác',
    'Hỏi người quen'
  ], true, true);

  multi(form, '8. Trong chuyến đó, những chuyện nào ĐÃ XẢY RA?', [
    'Đến nơi thì điểm đã đóng cửa / hết giờ bán vé',
    'Di chuyển giữa các điểm lâu hơn dự tính / phải đi vòng',
    'Phải bỏ bớt điểm vì không kịp giờ',
    'Tiêu nhiều hơn dự tính',
    'Quán ăn / điểm chơi không như review',
    'Cả nhóm mất nhiều thời gian bàn vì không thống nhất',
    'Không có chuyện nào kể trên'
  ], true);

  single(form, '9. So với dự tính, mỗi người đã tiêu thêm khoảng bao nhiêu trong một ngày đó?', [
    'Không tiêu thêm', 'Dưới 100k', '100–300k', '300–500k', 'Trên 500k', 'Không nhớ'
  ], true);

  single(form, '10. Khi lên lịch, phần nào mất công nhất?', [
    'Tìm chỗ đáng đi, quán đáng ăn',
    'Tính điểm nào gần nhau, đi theo thứ tự nào',
    'Kiểm giờ mở cửa',
    'Ước tổng tiền cho vừa ngân sách',
    'Thống nhất ý kiến cả nhóm',
    'Không biết nguồn nào đáng tin'
  ], true, true);

  single(form, '11. Nếu đã dùng ChatGPT / trợ lý AI để lên lịch, kết quả thế nào?', [
    'Chưa dùng AI cho việc này',
    'Đi theo được gần hết',
    'Phải sửa nhiều mới dùng được',
    'Có thông tin sai (giờ mở, giá, địa điểm không có thật)'
  ], true);

  single(form, '12. Trước chuyến đi, lịch đã được sửa lại mấy lần?', [
    'Không sửa', '1–2 lần', '3–5 lần', 'Trên 5 lần'
  ], true);

  form.addParagraphTextItem()
    .setTitle('13. Kể lại một lần cụ thể trong chuyến đó khi lịch trình không như dự tính: chuyện gì xảy ra, nhóm đã xử lý thế nào?')
    .setHelpText('Không bắt buộc, nhưng rất có ích cho nhóm. Đừng ghi tên người.')
    .setRequired(false);

  // ---- Sheet nhận kết quả ----
  var ss = SpreadsheetApp.create('Kết quả - Khảo sát lên lịch đi chơi');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log('Link SỬA form : ' + form.getEditUrl());
  Logger.log('Link GỬI đi   : ' + form.getPublishedUrl());
  Logger.log('Sheet kết quả : ' + ss.getUrl());
}

function single(form, title, choices, required, other) {
  var item = form.addMultipleChoiceItem().setTitle(title).setChoiceValues(choices).setRequired(required);
  if (other) item.showOtherOption(true);
  return item;
}

function multi(form, title, choices, required, other) {
  var item = form.addCheckboxItem().setTitle(title).setChoiceValues(choices).setRequired(required);
  if (other) item.showOtherOption(true);
  return item;
}
