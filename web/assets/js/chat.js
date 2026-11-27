// Trợ lý xếp lịch: nút mở + khung chat, gọi POST /api/chat (web/server.py → codebase/agent.answer).
// Mọi giờ, giá, tổng tiền trong câu trả lời do code tính; trang chỉ hiển thị lại, không tự tính.
(() => {
  const API = '/api/chat';
  const LIKES = [
    ['biển', 'Biển'], ['hải sản', 'Hải sản'], ['cà phê', 'Cà phê'], ['check-in', 'Check-in'],
    ['văn hoá lịch sử', 'Văn hóa'], ['chùa', 'Chùa'], ['thiên nhiên', 'Thiên nhiên'], ['ăn vặt', 'Ăn vặt'],
    ['đặc sản', 'Đặc sản'], ['chợ', 'Chợ'], ['yên tĩnh', 'Yên tĩnh'], ['sôi động', 'Sôi động'],
  ];
  const DAYS = ['thứ Hai', 'thứ Ba', 'thứ Tư', 'thứ Năm', 'thứ Sáu', 'thứ Bảy', 'Chủ Nhật'];
  const STATUS = { plan: 'Lịch đã kiểm', infeasible: 'Chưa xếp được', ask_back: 'Cần thêm thông tin', refuse: 'Ngoài phạm vi' };

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };

  // ---------- khung ----------
  const launcher = el('button', 'chat-launcher');
  launcher.type = 'button';
  launcher.setAttribute('aria-expanded', 'false');
  launcher.setAttribute('aria-controls', 'chat-panel');
  launcher.innerHTML = '<span class="chat-launcher__dot" aria-hidden="true"></span>Trợ lý xếp lịch';

  const panel = el('section', 'chat');
  panel.id = 'chat-panel';
  panel.hidden = true;
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-labelledby', 'chat-title');
  panel.innerHTML = `
    <header class="chat__head">
      <div>
        <p class="chat__kicker">Trợ lý AI · thử nghiệm</p>
        <h2 class="chat__title" id="chat-title">Lịch một ngày cho nhóm bạn</h2>
      </div>
      <div class="chat__actions">
        <button class="chat__reset" type="button">Lịch mới</button>
        <button class="chat__close" type="button" aria-label="Đóng trợ lý">×</button>
      </div>
    </header>
    <div class="chat__log" aria-live="polite"></div>
    <form class="chat__compose">
      <label class="visually-hidden" for="chat-input">Nhập yêu cầu</label>
      <textarea id="chat-input" rows="2" maxlength="2000"
        placeholder="VD: 4 người, 2 triệu cả nhóm, Chủ Nhật 8h–21h, thích biển và hải sản"></textarea>
      <button class="chat__send" type="submit">Gửi</button>
    </form>`;

  document.body.append(launcher, panel);
  const log = panel.querySelector('.chat__log');
  const form = panel.querySelector('.chat__compose');
  const input = panel.querySelector('#chat-input');
  const sendBtn = panel.querySelector('.chat__send');

  // ---------- form nhanh ----------
  function quickForm() {
    const f = el('form', 'quick');
    f.innerHTML = `
      <p class="quick__lead">Điền nhanh, hoặc gõ tự do ở ô dưới cùng.</p>
      <div class="quick__row">
        <label>Số người<input name="people" type="number" min="1" max="20" required placeholder="2"></label>
        <label>Ngân sách cả nhóm<input name="budget" type="text" required placeholder="800k, 1,5 triệu"></label>
      </div>
      <div class="quick__row quick__row--3">
        <label>Ngày đi<select name="day">${DAYS.map((d, i) => `<option value="${d}"${i === 5 ? ' selected' : ''}>${d[0].toUpperCase() + d.slice(1)}</option>`).join('')}</select></label>
        <label>Từ<input name="from" type="time" value="08:00" required></label>
        <label>Đến<input name="to" type="time" value="21:00" required></label>
      </div>
      <fieldset class="quick__likes"><legend>Sở thích</legend>
        ${LIKES.map(([v, l]) => `<label class="chip"><input type="checkbox" name="like" value="${v}"><span>${l}</span></label>`).join('')}
        <label class="chip chip--alt"><input type="checkbox" name="chay"><span>Có người ăn chay</span></label>
      </fieldset>
      <button class="quick__go" type="submit">Xếp lịch cho nhóm</button>`;
    f.addEventListener('submit', (e) => {
      e.preventDefault();
      const d = new FormData(f);
      const likes = d.getAll('like');
      const text = [
        `Nhóm ${d.get('people')} người, ngân sách ${String(d.get('budget')).trim()} cả nhóm,`,
        `đi ${d.get('day')} từ ${d.get('from')} đến ${d.get('to')}.`,
        likes.length ? `Thích ${likes.join(', ')}.` : '',
        d.get('chay') ? 'Có người ăn chay.' : '',
      ].filter(Boolean).join(' ');
      session = newSession();   // form nhanh luôn là một yêu cầu mới, không sửa lên lịch cũ
      send(text);
    });
    return f;
  }

  // ---------- hiển thị ----------
  const STOP = /^(\d{2}:\d{2}–\d{2}:\d{2}) · (.+?) — (.+?) — (.+)$/;
  const LEG = /^\s*↳\s*(.+)$/;

  function renderBot(data) {
    const box = el('div', 'msg msg--bot');
    const status = data.result && data.result.status;
    if (status) box.append(el('p', `msg__status msg__status--${status}`, STATUS[status] || status));
    let list = null;
    for (const raw of data.text.split('\n')) {
      const line = raw.trimEnd();
      if (!line.trim()) { list = null; continue; }
      const s = line.match(STOP);
      const g = !s && line.match(LEG);
      if (s || g) {
        if (!list) { list = el('ol', 'plan'); box.append(list); }
        if (s) {
          const li = el('li', 'plan__stop');
          li.append(el('span', 'plan__time', s[1]), el('strong', 'plan__name', s[2]),
            el('span', 'plan__price', s[3]), el('span', 'plan__why', s[4]));
          list.append(li);
        } else {
          list.append(el('li', 'plan__leg', g[1].replace(/~\s*/, 'khoảng ')));
        }
        continue;
      }
      list = null;
      const cls = line.startsWith('Mình hiểu:') ? 'msg__understood'
        : line.startsWith('Tổng:') ? 'msg__total'
        : line.startsWith('Giờ mở cửa và giá là tham khảo') ? 'msg__fine' : '';
      box.append(el('p', cls, line));
    }
    if (data.editing) {
      box.append(el('p', 'msg__hint', 'Muốn đổi gì thì nhắn tiếp, mình sửa trên lịch này. Ví dụ: bỏ một điểm, thêm quán cà phê, tăng ngân sách, về muộn hơn.'));
    }
    const m = data.meta;
    if (m) {
      box.append(el('p', 'msg__meta', m.model_calls
        ? `AI ${m.models.map((x) => x.replace(/^.*anthropic\./, '').replace(/-\d{8}.*$/, '')).join(', ')} · ${m.model_calls} lần gọi · ${(m.tokens_in + m.tokens_out).toLocaleString('vi-VN')} token`
        : 'Chưa gọi AI (chế độ giả hoặc phương án dự phòng bằng luật)'));
    }
    return box;
  }

  function push(node) {
    log.append(node);
    // câu trả lời dài (lịch) thì cuộn tới đầu câu, để thấy "Mình hiểu" và điểm đầu tiên
    log.scrollTop = node.classList.contains('msg--bot') ? node.offsetTop - log.offsetTop - 12 : log.scrollHeight;
  }

  // ---------- gửi ----------
  // Máy chủ nhớ yêu cầu và lịch gần nhất theo mã phiên: tin nhắn sau được hiểu là sửa trên lịch đó.
  const newSession = () => (crypto.randomUUID ? crypto.randomUUID() : `s-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  let session = newSession();   // tải lại trang là phiên mới, khớp với khung chat trống
  const PLACEHOLDER_NEW = input.placeholder;
  const PLACEHOLDER_EDIT = 'Sửa tiếp: bỏ Chợ Hàn, thêm quán cà phê, tăng ngân sách, về muộn hơn…';
  let busy = false;

  function resetSession() {
    session = newSession();
    input.placeholder = PLACEHOLDER_NEW;
    push(el('p', 'msg msg--divider', 'Bắt đầu lịch mới'));
    push(quickForm());
  }

  async function send(text) {
    text = text.trim();
    if (!text || busy) return;
    busy = true;
    sendBtn.disabled = true;
    push(el('p', 'msg msg--user', text));
    const wait = el('p', 'msg msg--wait', 'Đang xếp lịch và kiểm giờ mở cửa, đường đi, ngân sách…');
    push(wait);
    const WRONG_SERVER = 'Trang đang chạy bằng máy chủ chỉ phục vụ file tĩnh nên chưa có trợ lý. '
      + 'Tắt máy chủ đó rồi chạy "python web/server.py" và mở http://localhost:8000.';
    try {
      const res = await fetch(API, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text, session }),
      });
      const data = await res.json().catch(() => ({ error: WRONG_SERVER }));
      wait.remove();
      if (!res.ok || data.error) {
        push(el('p', 'msg msg--error', data.error || `Lỗi ${res.status}.`));
      } else {
        input.placeholder = data.editing ? PLACEHOLDER_EDIT : PLACEHOLDER_NEW;
        push(renderBot(data));
      }
    } catch {
      wait.remove();
      push(el('p', 'msg msg--error', 'Không kết nối được máy chủ trợ lý. ' + WRONG_SERVER));
    } finally {
      busy = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const t = input.value;
    input.value = '';
    send(t);
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
  });

  // ---------- mở / đóng ----------
  let started = false;
  function open() {
    if (!started) {
      started = true;
      const hello = el('div', 'msg msg--bot');
      hello.append(el('p', '', 'Chào bạn. Cho mình biết số người, ngân sách cả nhóm, ngày và khung giờ, mình xếp lịch tham quan và ăn uống trong một ngày ở Đà Nẵng (gồm Hội An, Bà Nà).'),
        el('p', 'msg__fine', 'Giờ mở cửa, giá và đường đi đều được kiểm bằng dữ liệu của nhóm. Mình không đặt vé hay thanh toán.'));
      push(hello);
      push(quickForm());
    }
    panel.hidden = false;
    launcher.setAttribute('aria-expanded', 'true');
    launcher.hidden = true;
    (panel.querySelector('.quick input') || input).focus();
  }
  function close() {
    panel.hidden = true;
    launcher.hidden = false;
    launcher.setAttribute('aria-expanded', 'false');
    launcher.focus();
  }
  launcher.addEventListener('click', open);
  panel.querySelector('.chat__close').addEventListener('click', close);
  panel.querySelector('.chat__reset').addEventListener('click', () => { if (!busy) resetSession(); });
  panel.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  document.querySelectorAll('[data-chat-open]').forEach((b) => b.addEventListener('click', open));

  // Link mở sẵn trợ lý: #tro-ly mở khung, ?hoi=… mở và gửi luôn câu đó (tiện cho video demo).
  const ask = new URLSearchParams(location.search).get('hoi');
  if (ask || location.hash === '#tro-ly') open();
  if (ask) send(ask);
})();
