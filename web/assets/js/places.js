// Dữ liệu 9 điểm đến: trang chi tiết (dia-diem.html) và bản đồ đều đọc từ đây.
// Tọa độ: Wikipedia tiếng Anh/Việt hoặc OpenStreetMap (xem content/sources.md).
// Ảnh: Wikimedia Commons (xem content/credits.md).

const LICENSES = {
  'CC0': null,
  'CC BY 2.0': 'https://creativecommons.org/licenses/by/2.0',
  'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0',
  'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0',
  'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0',
};

function photo(file, w, h, alt, caption, author, license, commonsFile, pos) {
  return {
    src: `assets/img/${file}.webp`, w, h, alt, caption, author, license,
    licenseUrl: LICENSES[license],
    page: `https://commons.wikimedia.org/wiki/File:${commonsFile}`,
    pos: pos || 'center',
  };
}

window.PLACES = [
  {
    id: 'my-khe', group: 'Thiên nhiên', tag: 'Biển', name: 'Biển Mỹ Khê', short: 'Mỹ Khê',
    lat: 16.0704, lng: 108.2461,
    lead: 'Bờ cát dài ngay sát thành phố. Sáng sớm là lúc người dân xuống tắm biển và ngư dân kéo thúng chai lên bờ.',
    body: [
      'Mỹ Khê nằm ở phía đông trung tâm thành phố: qua sông Hàn là tới biển. Bờ cát dài và thoải, phía bắc là bán đảo Sơn Trà, phía nam bãi biển kéo dài về Non Nước.',
      'Sáng sớm và chiều muộn là lúc bãi biển đông người địa phương nhất. Có người tắm biển, có người tập thể dục, và có ngư dân đưa thúng chai vào bờ sau một đêm trên biển.',
    ],
    todo: ['Ngắm bình minh trên biển', 'Xem ngư dân đưa thúng chai vào bờ', 'Tắm biển lúc sáng sớm hoặc chiều muộn', 'Ăn hải sản ở các quán ven biển'],
    tip: 'Nắng giữa trưa rất gắt, nên ra biển trước 8 giờ sáng hoặc sau 4 giờ chiều. Chỉ tắm ở khu vực có cứu hộ và để ý cờ báo.',
    related: ['son-tra', 'ngu-hanh-son', 'cau-rong'],
    photos: [
      photo('my-khe', 1600, 744, 'Bãi biển Mỹ Khê trải dài, phía xa là các tòa nhà ven biển và bán đảo Sơn Trà', 'Bãi biển Mỹ Khê', 'Christophe95', 'CC BY-SA 4.0', 'My_Khe_Beach_5.jpg'),
      photo('ngu-dan', 1200, 900, 'Ngư dân phân loại cá và vá lưới dưới mái bạt trên bãi cát', 'Ngư dân trên bãi Mỹ Khê', 'Christophe95', 'CC BY-SA 4.0', 'Fishermen_on_My_Khe_Beach.jpg'),
      photo('my-khe-2', 1200, 900, 'Cỏ và cát ven biển Mỹ Khê, phía xa là dãy nhà cao tầng', 'Ven biển Mỹ Khê', 'Christophe95', 'CC BY-SA 4.0', 'My_Khe_Beach_18.jpg'),
      photo('my-khe-3', 1200, 900, 'Thuyền đánh cá kéo lên bờ dưới hàng dừa gần bãi Mỹ Khê', 'Thuyền trên bãi Mỹ Khê', 'Christophe95', 'CC BY-SA 4.0', 'Boats_on_My_Khe_Beach_1.jpg'),
    ],
  },
  {
    id: 'son-tra', group: 'Thiên nhiên', tag: 'Rừng', name: 'Bán đảo Sơn Trà', short: 'Sơn Trà',
    lat: 16.116, lng: 108.277,
    lead: 'Khối núi phủ rừng nhô ra biển, che chắn cho vịnh Đà Nẵng, nhà của loài voọc chà vá chân nâu.',
    body: [
      'Sơn Trà là khối núi nhô ra biển ở phía đông bắc thành phố, che chắn cho vịnh Đà Nẵng. Phần lớn bán đảo được rừng bao phủ.',
      'Rừng Sơn Trà là nơi sống của voọc chà vá chân nâu, loài linh trưởng có bộ lông nhiều màu. Con đường ven núi đưa bạn qua những bãi tắm nhỏ, chùa Linh Ứng và nhiều điểm nhìn xuống thành phố.',
    ],
    todo: ['Viếng chùa Linh Ứng', 'Đi con đường ven biển quanh bán đảo', 'Tìm voọc chà vá chân nâu (cần may mắn, và giữ khoảng cách)', 'Ngắm thành phố từ trên cao'],
    tip: 'Đường lên núi dốc, nhiều khúc cua. Nên đi ban ngày, mang theo nước và không cho động vật hoang dã ăn.',
    related: ['linh-ung', 'my-khe', 'hai-van'],
    photos: [
      photo('son-tra', 1200, 900, 'Một vịnh nhỏ nước xanh dưới chân những ngọn đồi phủ rừng ở bán đảo Sơn Trà', 'Bán đảo Sơn Trà', 'Christophe95', 'CC BY-SA 4.0', 'Son_Tra_Peninsula.jpg'),
      photo('mot-ngay-son-tra', 1200, 900, 'Nhìn từ sườn núi Sơn Trà xuống vịnh và thành phố Đà Nẵng', 'Đà Nẵng nhìn từ Sơn Trà', 'Christophe95', 'CC BY-SA 4.0', 'Da_Nang_and_the_Son_Tra_Peninsula.jpg'),
      photo('son-tra-2', 1200, 900, 'Đường Hoàng Sa men theo sườn núi xanh trên bán đảo Sơn Trà', 'Đường Hoàng Sa, Sơn Trà', 'Christophe95', 'CC BY-SA 4.0', 'Hoàng_Sa_Road,_Son_Tra_Peninsula.jpg'),
      photo('linh-ung', 1200, 895, 'Cổng tam quan chùa Linh Ứng mái cong, nổi bật trên nền trời xanh', 'Cổng chùa Linh Ứng', 'CEphoto, Uwe Aranas', 'CC BY-SA 3.0', 'Son-Tra-Peninsula_Da-Nang_Vietnam_Linh-Ung-Pagoda-01.jpg'),
    ],
  },
  {
    id: 'ngu-hanh-son', group: 'Thiên nhiên', tag: 'Đá', name: 'Ngũ Hành Sơn', short: 'Ngũ Hành Sơn',
    lat: 16.0, lng: 108.26,
    lead: 'Năm ngọn núi đá Kim, Mộc, Thủy, Hỏa, Thổ, trong lòng có hang động và chùa.',
    body: [
      'Ngũ Hành Sơn là cụm năm ngọn núi đá mọc lên giữa vùng đất bằng ven biển, phía nam trung tâm. Năm ngọn mang tên năm hành: Kim, Mộc, Thủy, Hỏa, Thổ.',
      'Trong lòng núi có nhiều hang động và chùa. Dưới chân núi là làng đá mỹ nghệ Non Nước, nơi thợ đá chạm tượng và đồ trang trí.',
    ],
    todo: ['Leo bậc đá lên Thủy Sơn', 'Vào các hang động trong lòng núi', 'Viếng chùa trên núi', 'Xem thợ đá làm việc ở làng Non Nước'],
    tip: 'Bậc đá dốc và có thể trơn sau mưa. Nên đi giày đế bám và đi vào buổi sáng cho đỡ nắng.',
    related: ['my-khe', 'hoi-an', 'cham'],
    photos: [
      photo('ngu-hanh-son', 1600, 809, 'Nhìn từ trên Ngũ Hành Sơn xuống, các ngọn núi đá nhô lên giữa phố xá', 'Ngũ Hành Sơn nhìn từ trên cao', 'Kuroczynski', 'CC BY-SA 4.0', 'Da_Nang_Marble_Mountains_2020_IMG_4008.jpg'),
      photo('mot-ngay-ngu-hanh-son', 1200, 675, 'Cổng chùa dưới chân vách đá Ngũ Hành Sơn', 'Cổng chùa dưới chân núi', 'Andre Hospers', 'CC BY 4.0', 'Marble_Mountain_Hoi_An,_Da_Nang_(71468).jpg'),
      photo('ngu-hanh-son-2', 1200, 900, 'Chùa Non Nước với mái ngói xanh và hàng cây cảnh', 'Chùa Non Nước', 'Christophe95', 'CC BY-SA 4.0', 'Non_Nuoc_Pagoda_Da_Nang_1.jpg'),
    ],
  },
  {
    id: 'hai-van', group: 'Thiên nhiên', tag: 'Mây', name: 'Đèo Hải Vân', short: 'Hải Vân',
    lat: 16.2, lng: 108.1333,
    lead: 'Con đèo men sườn núi sát biển, giữa Đà Nẵng và Huế. "Hải Vân" là biển và mây.',
    body: [
      'Đèo Hải Vân vắt qua một nhánh núi đâm ra biển, nằm giữa Đà Nẵng và Huế. Tên đèo ghép từ hai chữ: hải là biển, vân là mây.',
      'Đỉnh đèo thường có mây phủ, trên đỉnh còn dấu tích cửa ải xưa. Từ đường đèo, một phía nhìn xuống vịnh Đà Nẵng, phía kia là vùng biển Lăng Cô.',
    ],
    todo: ['Đi qua con đường đèo', 'Dừng ở đỉnh đèo xem cửa ải xưa', 'Ngắm vịnh Đà Nẵng từ trên cao'],
    tip: 'Thời tiết trên đèo đổi rất nhanh và hay có sương mù. Đi chậm, bật đèn, tránh đi khi mưa lớn.',
    related: ['son-tra', 'ba-na', 'my-khe'],
    photos: [
      photo('hai-van', 1200, 800, 'Sườn núi xanh đổ xuống biển, mây mù phủ dãy núi phía xa', 'Đèo Hải Vân, nhìn về phía nam', 'Vyacheslav Argenberg', 'CC BY 4.0', 'Hai_Van_Pass,_Vietnam,_View_southwards.jpg'),
      photo('hai-van-2', 1200, 800, 'Sườn núi trên đèo Hải Vân trong sương, nhìn ra biển', 'Sườn đèo Hải Vân', 'Vyacheslav Argenberg', 'CC BY 4.0', 'Hai_Van_Pass,_Vietnam.jpg'),
      photo('hai-van-3', 1200, 800, 'Sương mù phủ các ngọn núi quanh đèo Hải Vân', 'Đèo Hải Vân trong sương', 'Vyacheslav Argenberg', 'CC BY 4.0', 'Hai_Van_Pass_under_fog,_Vietnam.jpg'),
    ],
  },
  {
    id: 'ba-na', group: 'Thiên nhiên', tag: 'Đỉnh', name: 'Bà Nà', short: 'Bà Nà',
    lat: 15.9956, lng: 107.9942,
    lead: 'Đỉnh núi phía tây thành phố, mát hơn hẳn dưới phố. Lên bằng cáp treo xuyên mây.',
    body: [
      'Bà Nà là vùng núi ở phía tây thành phố. Trên đỉnh, khí hậu mát hơn hẳn dưới đồng bằng.',
      'Ngày nay đỉnh núi là một khu du lịch lớn, lên bằng cáp treo. Điểm nổi tiếng nhất là Cầu Vàng, cây cầu đi bộ được đỡ bởi hai bàn tay đá khổng lồ.',
    ],
    todo: ['Đi cáp treo qua rừng và mây', 'Dạo Cầu Vàng', 'Ngắm biển mây vào buổi sáng'],
    tip: 'Đây là khu du lịch có bán vé, giá và giờ hoạt động cần xem trên trang chính thức. Trên đỉnh lạnh hơn dưới phố, nên mang theo áo khoác mỏng.',
    related: ['hai-van', 'son-tra', 'ngu-hanh-son'],
    photos: [
      photo('ba-na', 1600, 1067, 'Cầu Vàng được đỡ bởi hai bàn tay đá khổng lồ, phía sau là biển mây trắng', 'Cầu Vàng trên biển mây', 'Vivu Vietnam', 'CC BY-SA 4.0', 'Golden_Bridge_above_the_clouds_Ba_Na_Hills_Da_Nang_Vietnam.jpg'),
      photo('ba-na-2', 1200, 776, 'Hai bàn tay đá đỡ Cầu Vàng giữa rừng xanh dưới nắng', 'Cầu Vàng, Bà Nà', 'DvTor8303', 'CC0', 'Golden_Bridge_at_Ba_Na_Hills_20250718.jpg'),
    ],
  },
  {
    id: 'hoi-an', group: 'Văn hóa', tag: 'Di sản', name: 'Phố cổ Hội An', short: 'Hội An',
    lat: 15.8771, lng: 108.326,
    lead: 'Thương cảng xưa bên sông Thu Bồn, Di sản Thế giới, lung linh đèn lồng khi trời tối.',
    body: [
      'Hội An từng là một thương cảng sầm uất bên sông Thu Bồn. Phố cổ còn giữ những dãy nhà gỗ, hội quán và Chùa Cầu.',
      'Phố cổ được UNESCO ghi danh là Di sản Thế giới năm 1999. Khi trời tối, đèn lồng thắp sáng khắp các con phố và mặt sông.',
    ],
    todo: ['Đi bộ qua Chùa Cầu', 'Ghé các hội quán và nhà cổ', 'Ngắm đèn lồng khi trời tối', 'Ăn một tô cao lầu'],
    tip: 'Phố cổ đông nhất vào buổi tối. Một số điểm tham quan trong phố cổ cần vé, nên xem quy định hiện hành trước khi đi.',
    related: ['ngu-hanh-son', 'cham', 'cau-rong'],
    photos: [
      photo('hoi-an-den-long', 1600, 1200, 'Phố cổ Hội An lúc chạng vạng, đèn lồng nhiều màu treo kín trên đầu người đi bộ', 'Phố cổ Hội An lúc lên đèn', 'Christophe95', 'CC BY-SA 4.0', 'Lanterns_in_Hoi_An_3.jpg'),
      photo('mot-ngay-hoi-an', 1200, 821, 'Chùa Cầu ở Hội An soi bóng xuống con lạch, hai bên là nhà tường vàng', 'Chùa Cầu', 'Steffen Schmitz', 'CC BY-SA 4.0', 'Hội_An,_Chùa_Cầu,_2020-01_CN-01.jpg'),
      photo('hoi-an-2', 1200, 540, 'Sông Thu Bồn về đêm với thuyền đèn lồng và ánh đèn phố cổ', 'Sông Thu Bồn về đêm', 'Nguyen QuocTrung', 'CC BY-SA 4.0', 'Thu_Bồn_River_at_night_-_Hội_An_2022.jpg'),
      photo('hoi-an-3', 1200, 800, 'Con phố cổ Hội An vắng người sau cơn mưa, nhà tường vàng treo đèn lồng', 'Phố cổ sau cơn mưa', 'lumoplank', 'CC0', 'Hoi_An_-_HoiAn1457.jpg'),
    ],
  },
  {
    id: 'cham', group: 'Văn hóa', tag: 'Chămpa', name: 'Bảo tàng Điêu khắc Chăm', short: 'Điêu khắc Chăm',
    lat: 16.0599, lng: 108.2226,
    lead: 'Kho tàng điêu khắc đá sa thạch của vương quốc Chămpa, ngay bên bờ sông Hàn.',
    body: [
      'Bảo tàng nằm bên bờ sông Hàn, gần cầu Rồng. Đây là nơi lưu giữ nhiều tác phẩm điêu khắc của vương quốc Chămpa xưa.',
      'Phần lớn hiện vật làm bằng đá sa thạch: tượng thần, phù điêu, bệ thờ. Nhiều hiện vật được đưa về từ các khu đền tháp trong vùng, như Mỹ Sơn.',
    ],
    todo: ['Xem bệ thờ Mỹ Sơn E1', 'Tìm các tượng thần Ganesha', 'Đi chậm qua từng phòng trưng bày'],
    tip: 'Bảo tàng hợp cho một buổi trưa nắng. Giờ mở cửa và giá vé cần xem trên trang chính thức.',
    related: ['cau-rong', 'hoi-an', 'linh-ung'],
    photos: [
      photo('cham', 1600, 1067, 'Bệ thờ bằng đá sa thạch chạm khắc tinh xảo, phía trên là các pho tượng', 'Bệ thờ Mỹ Sơn E1', 'Daderot', 'CC0', 'Pedestal,_My_Son_E1,_view_1,_7th_century,_Quang_Nam_-_Museum_of_Cham_Sculpture_-_Danang,_Vietnam_-_DSC01700.JPG'),
      photo('cham-2', 900, 1525, 'Tượng thần Ganesha bằng đá sa thạch trong Bảo tàng Điêu khắc Chăm', 'Tượng Ganesha, Mỹ Sơn E5', 'Daderot', 'CC0', 'Ganesh,_My_Son_E5,_7th_century,_Quang_Nam_-_Museum_of_Cham_Sculpture_-_Danang,_Vietnam_-_DSC01715.JPG', 'top'),
      photo('cham-3', 1200, 752, 'Phòng trưng bày với nhiều tượng và phù điêu đá Chăm', 'Một phòng trưng bày', 'Daderot', 'CC0', 'Interior_view_-_Museum_of_Cham_Sculpture_-_Danang,_Vietnam_-_DSC01931.JPG'),
    ],
  },
  {
    id: 'linh-ung', group: 'Văn hóa', tag: 'Tâm linh', name: 'Chùa Linh Ứng', short: 'Linh Ứng',
    lat: 16.1003, lng: 108.2779,
    lead: 'Ngôi chùa trên sườn Sơn Trà, tượng Quan Âm trắng nhìn ra vịnh.',
    body: [
      'Chùa Linh Ứng nằm trên sườn bán đảo Sơn Trà, nhìn thẳng ra vịnh và thành phố.',
      'Pho tượng Quan Âm màu trắng của chùa nhìn thấy được từ nhiều nơi dọc bờ biển. Khuôn viên chùa có cổng tam quan, bậc thang rồng và nhiều cây cảnh.',
    ],
    todo: ['Viếng tượng Quan Âm', 'Ngắm vịnh từ sân chùa', 'Đi tiếp con đường ven núi Sơn Trà'],
    tip: 'Chùa là nơi thờ tự: mặc trang phục kín đáo và giữ yên lặng.',
    related: ['son-tra', 'my-khe', 'cham'],
    photos: [
      photo('linh-ung', 1200, 895, 'Cổng tam quan chùa Linh Ứng mái cong, nổi bật trên nền trời xanh', 'Cổng chùa Linh Ứng', 'CEphoto, Uwe Aranas', 'CC BY-SA 3.0', 'Son-Tra-Peninsula_Da-Nang_Vietnam_Linh-Ung-Pagoda-01.jpg'),
      photo('linh-ung-2', 1200, 800, 'Bậc thang có lan can hình rồng dẫn lên chùa Linh Ứng', 'Bậc thang rồng', 'CEphoto, Uwe Aranas', 'CC BY-SA 3.0', 'Son-Tra-Peninsula_Da-Nang_Vietnam_Linh-Ung-Pagoda-02.jpg'),
    ],
  },
  {
    id: 'cau-rong', group: 'Văn hóa', tag: 'Hiện đại', name: 'Cầu Rồng và sông Hàn', short: 'Cầu Rồng',
    lat: 16.0611, lng: 108.2267,
    lead: 'Cây cầu hình con rồng uốn mình qua sông Hàn, rực rỡ khi trời tối.',
    body: [
      'Cầu Rồng bắc qua sông Hàn, nối trung tâm với phía biển. Thân cầu mang hình con rồng uốn lượn, về đêm được chiếu sáng nhiều màu.',
      'Vào một số tối cuối tuần, đầu rồng phun lửa và phun nước, thu hút đông người xem hai bên bờ. Dọc sông Hàn còn nhiều cây cầu khác cùng lên đèn khi trời tối.',
    ],
    todo: ['Dạo bờ sông Hàn buổi tối', 'Xem cầu Rồng phun lửa, phun nước (theo lịch)', 'Ngắm các cây cầu lên đèn'],
    tip: 'Lịch phun lửa có thể thay đổi, nên xem thông báo của thành phố trước khi đi.',
    related: ['cham', 'my-khe', 'hoi-an'],
    photos: [
      photo('cau-rong', 1600, 900, 'Cầu Rồng về đêm, thân rồng phát sáng vàng rực in bóng xuống mặt sông', 'Cầu Rồng về đêm', 'Supanut Arunoprayote', 'CC BY 4.0', 'Da_Nang_Dragon_Bridge_(II).jpg'),
      photo('hero-song-han', 2400, 1601, 'Sông Hàn lúc hoàng hôn, cầu Rồng vàng óng nối hai bờ', 'Sông Hàn lúc hoàng hôn', 'Quangpraha', 'CC0', 'Da_Nang,_Vietnam.jpg'),
      photo('mot-ngay-song-han', 1200, 900, 'Tượng đá trắng bên sông Hàn, phía sau là cầu Rồng lên đèn', 'Bờ sông Hàn về đêm', 'Christophe95', 'CC BY-SA 4.0', 'Dragon_Bridge_at_night_6.jpg'),
      photo('song-han-2', 1200, 619, 'Sông Hàn lúc bình minh, các tòa nhà trải dọc bờ', 'Sông Hàn lúc bình minh', 'Christophe95', 'CC BY-SA 4.0', 'Han_River_in_Da_Nang_at_sunrise.jpg'),
    ],
  },
];

window.placeById = (id) => window.PLACES.find((p) => p.id === id);
window.placeUrl = (id) => `dia-diem.html?id=${id}`;
