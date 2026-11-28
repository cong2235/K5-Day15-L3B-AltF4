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
    </form>
    <div class="chat__map" hidden>
      <div class="chat__map-canvas" role="region" aria-label="Bản đồ tuyến đường của lịch đang chọn"></div>
      <p class="chat__map-note"></p>
    </div>`;

  document.body.append(launcher, panel);
  const log = panel.querySelector('.chat__log');
  const form = panel.querySelector('.chat__compose');
  const input = panel.querySelector('#chat-input');
  const sendBtn = panel.querySelector('.chat__send');
  const mapBox = panel.querySelector('.chat__map');
  const mapCanvas = panel.querySelector('.chat__map-canvas');
  const mapNote = panel.querySelector('.chat__map-note');

  const vnd = (n) => `${Number(n).toLocaleString('vi-VN')}đ`;
  const duration = (m) => [Math.floor(m / 60) ? `${Math.floor(m / 60)} tiếng` : '', m % 60 ? `${m % 60} phút` : ''].filter(Boolean).join(' ');

  // ---------- bản đồ tuyến (Leaflet + OpenStreetMap; đường đi thật lấy từ OSRM, không có thì nối nét đứt) ----------
  const TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  const ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · tuyến: OSRM';
  const OSRM = 'https://router.project-osrm.org/route/v1/driving/';
  let map = null;
  let layer = null;
  let pins = [];
  let routeToken = 0;
  const roads = new Map();

  function ensureMap() {
    if (!window.L) return null;
    panel.classList.add('chat--map');
    mapBox.hidden = false;
    if (!map) {
      map = L.map(mapCanvas, { scrollWheelZoom: true });
      L.tileLayer(TILE_URL, { maxZoom: 18, attribution: ATTRIBUTION }).addTo(map);
      layer = L.layerGroup().addTo(map);
    }
    return map;
  }

  async function getJson(url, ms) {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), ms);
    try {
      const res = await fetch(url, { signal: ctl.signal });
      return res.ok ? await res.json() : null;
    } catch {
      return null;
    } finally {
      clearTimeout(timer);
    }
  }

  // Đường bộ: ưu tiên máy chủ của trang (/api/route, gọi OSRM hộ, có lưu đệm, không bị tiện ích trình duyệt chặn);
  // không có máy chủ đó (mở file tĩnh) thì gọi thẳng OSRM. Chỉ lưu đệm khi thành công, để lần sau còn thử lại.
  async function roadPath(points) {
    const key = points.join(';');
    if (roads.has(key)) return roads.get(key);
    let route = await getJson(`/api/route?c=${encodeURIComponent(key)}`, 15000);
    if (!route || !route.line) {
      const coords = points.map(([lat, lon]) => `${lon},${lat}`).join(';');
      const body = await getJson(`${OSRM}${coords}?overview=full&geometries=geojson`, 12000);
      const r = body && body.routes && body.routes[0];
      route = r ? { line: r.geometry.coordinates.map(([lon, lat]) => [lat, lon]), km: Math.round(r.distance / 100) / 10 } : null;
    }
    if (route && route.line) roads.set(key, route);
    return route && route.line ? route : null;
  }

  async function showRoute(option) {
    const m = ensureMap();
    if (!m) return;
    const token = ++routeToken;
    layer.clearLayers();
    const points = option.stops.map((s) => [s.lat, s.lon]);
    pins = option.stops.map((s, i) => L.marker([s.lat, s.lon], {
      icon: L.divIcon({ className: `map-pin${s.kind === 'an' ? ' map-pin--meal' : ''}`, html: `<span>${i + 1}</span>`, iconSize: [32, 32], iconAnchor: [16, 16] }),
      title: s.name, alt: s.name, riseOnHover: true,
    }).bindTooltip(`${i + 1}. ${s.name} · ${s.arrive}–${s.leave}`, { direction: 'top', offset: [0, -14] }).addTo(layer));
    const straight = points.length > 1
      ? L.polyline(points, { color: '#1673a3', weight: 3, opacity: 0.7, dashArray: '6 8' }).addTo(layer) : null;
    requestAnimationFrame(() => {
      m.invalidateSize();
      if (points.length > 1) m.fitBounds(L.latLngBounds(points).pad(0.18));
      else m.setView(points[0], 14);
    });
    if (!straight) { mapNote.textContent = ''; return; }
    mapNote.textContent = 'Đang lấy đường bộ…';
    const route = await roadPath(points);
    if (token !== routeToken) return;          // người dùng đã chuyển sang phương án khác
    if (route) {
      layer.removeLayer(straight);
      L.polyline(route.line, { color: '#0b3d5c', weight: 4, opacity: 0.85 }).addTo(layer);
      mapNote.textContent = `Đường bộ theo OSRM${route.km ? `, khoảng ${String(route.km).replace('.', ',')} km` : ''}. `
        + 'Giờ, thời gian đi và tiền trong lịch do hệ thống tính.';
    } else {
      mapNote.textContent = 'Chưa lấy được đường bộ, đang tạm nối thẳng các điểm. ';
      const retry = el('button', 'chat__map-retry', 'Thử lại');
      retry.type = 'button';
      retry.addEventListener('click', () => showRoute(option));
      mapNote.append(retry);
    }
  }

  // ---------- nói để nhập (Web Speech API, có ở Chrome / Edge) ----------
  const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (Speech) {
    const mic = el('button', 'chat__mic');
    mic.type = 'button';
    mic.setAttribute('aria-label', 'Nói để nhập yêu cầu');
    mic.setAttribute('aria-pressed', 'false');
    mic.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 15a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-2.08A7 7 0 0 0 19 12h-2Z"/></svg>';
    form.classList.add('chat__compose--mic');
    form.insertBefore(mic, sendBtn);
    let rec = null;
    mic.addEventListener('click', () => {
      if (rec) { rec.stop(); return; }
      rec = new Speech();
      rec.lang = 'vi-VN';
      rec.interimResults = true;
      const before = input.value ? `${input.value.trimEnd()} ` : '';
      rec.onresult = (e) => { input.value = before + Array.from(e.results).map((r) => r[0].transcript).join(''); };
      rec.onend = () => { rec = null; mic.classList.remove('is-on'); mic.setAttribute('aria-pressed', 'false'); input.focus(); };
      rec.onerror = rec.onend;
      rec.start();
      mic.classList.add('is-on');
      mic.setAttribute('aria-pressed', 'true');
    });
  }

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

  function planBody(o, data) {
    const wrap = el('div', 'opts__body');
    const list = el('ol', 'plan');
    o.stops.forEach((s, i) => {
      if (s.leg) {
        let t = `đi lại khoảng ${s.leg.min} phút (ước tính)${o.transport === 'grab' ? `, ${vnd(s.leg.vnd)}` : ''}`;
        if (s.leg.idle >= 30) {
          t += s.leg.rest
            ? ` · nghỉ trưa khoảng ${duration(s.leg.idle)} (về khách sạn hoặc ngồi cà phê gần khu ${s.leg.area})`
            : ` · rảnh khoảng ${duration(s.leg.idle)}, dạo quanh khu ${s.leg.area}`;
        }
        list.append(el('li', 'plan__leg', t));
      }
      const li = el('li', 'plan__stop');
      li.append(el('span', 'plan__time', `${s.arrive}–${s.leave}`), el('strong', 'plan__name', `${i + 1}. ${s.name}`),
        el('span', 'plan__price', s.price), el('span', 'plan__why', s.why));
      li.addEventListener('mouseenter', () => pins[i] && pins[i].openTooltip());
      li.addEventListener('mouseleave', () => pins[i] && pins[i].closeTooltip());
      list.append(li);
    });
    wrap.append(list, el('p', 'msg__total', o.transport === 'grab'
      ? `Tổng: ${vnd(o.total_vnd)}, trong đó đi lại ${vnd(o.transport_vnd)} (ước tính). Ngân sách: ${vnd(o.budget_vnd)}.`
      : `Tổng: ${vnd(o.total_vnd)}, đã gồm thuê xe máy theo ngày (ước tính). Ngân sách: ${vnd(o.budget_vnd)}.`));
    if (data.checked_on) {
      wrap.append(el('p', 'msg__fine', `Giờ mở cửa và giá là tham khảo theo dữ liệu kiểm ngày ${data.checked_on}; hãy xác nhận lại với nơi đến trước khi đi.`));
    }
    return wrap;
  }

  // Nhiều phương án: thẻ chọn ở trên, lịch của phương án đang chọn ở dưới, tuyến đường hiện ở bản đồ bên phải.
  // Chọn phương án nào thì báo máy chủ (/api/choose), để tin nhắn sửa tiếp theo áp lên đúng lịch đó.
  function renderOptions(data) {
    const box = el('div', 'msg msg--bot');
    const n = data.options.length;
    box.append(el('p', 'msg__status msg__status--plan', n > 1 ? `${n} phương án đã kiểm` : STATUS.plan));
    if (data.understood) box.append(el('p', 'msg__understood', data.understood));
    (data.notes || []).forEach((t) => box.append(el('p', 'msg__note', t)));
    const tabs = el('div', 'opts');
    tabs.setAttribute('role', 'tablist');
    tabs.setAttribute('aria-label', 'Các phương án lịch');
    const slot = el('div');
    const buttons = data.options.map((o, i) => {
      const b = el('button', 'opt');
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.append(el('span', 'opt__label', o.label), el('span', 'opt__meta', `${o.stops.length} điểm · ${vnd(o.total_vnd)}`));
      b.addEventListener('click', () => select(i, true));
      tabs.append(b);
      return b;
    });
    const owner = session;
    function select(i, tell) {
      buttons.forEach((b, j) => b.setAttribute('aria-selected', String(i === j)));
      slot.replaceChildren(planBody(data.options[i], data));
      showRoute(data.options[i]);
      if (tell) {
        fetch('/api/choose', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session: owner, index: i }) })
          .catch(() => {});
      }
    }
    if (n > 1) box.append(tabs);
    box.append(slot);
    box.append(el('p', 'msg__hint', n > 1
      ? 'Chọn một phương án, rồi muốn đổi gì thì nói hoặc gõ tiếp. Ví dụ: "thay chỗ đi biển lúc 16h bằng chùa", "bỏ chợ Hàn", "về muộn hơn 1 tiếng".'
      : 'Muốn đổi gì thì nói hoặc gõ tiếp, mình sửa trên lịch này. Ví dụ: "thay chỗ lúc 16h bằng quán cà phê".'));
    box.deactivate = () => buttons.forEach((b) => { b.disabled = true; });
    select(0, false);
    return box;
  }

  function renderBot(data) {
    if (data.options && data.options.length) return withMeta(renderOptions(data), data);
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
    return withMeta(box, data);
  }

  function withMeta(box, data) {
    const m = data.meta;
    if (m) {
      box.append(el('p', 'msg__meta', m.model_calls
        ? `AI ${m.models.map((x) => x.replace(/^.*anthropic\./, '').replace(/-\d{8}.*$/, '')).join(', ')} · ${m.model_calls} lần gọi · ${(m.tokens_in + m.tokens_out).toLocaleString('vi-VN')} token`
        : 'Chưa gọi AI (chế độ giả hoặc phương án dự phòng bằng luật)'));
    }
    return box;
  }

  function push(node) {
    // lịch cũ không chọn được nữa: máy chủ chỉ nhớ các phương án của câu trả lời mới nhất
    if (node.classList.contains('msg--bot') || node.classList.contains('msg--divider')) {
      log.querySelectorAll('.msg--bot').forEach((b) => b.deactivate && b.deactivate());
    }
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
