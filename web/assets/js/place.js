// Dựng trang dia-diem.html?id=... từ window.PLACES.
(() => {
  const id = new URLSearchParams(location.search).get('id');
  const p = placeById(id);
  const $ = (sel) => document.querySelector(sel);

  if (!p) {
    $('[data-place-root]').innerHTML = `
      <section class="section"><div class="wrap not-found">
        <h1>Không tìm thấy điểm đến này</h1>
        <p>Đường dẫn có thể đã sai. <a href="index.html#ban-do">Xem tất cả điểm đến trên bản đồ</a>.</p>
      </div></section>`;
    document.title = 'Không tìm thấy — Đà Nẵng';
    return;
  }

  const credit = (ph) => {
    const lic = ph.licenseUrl ? `<a href="${ph.licenseUrl}">${ph.license}</a>` : ph.license;
    return `Ảnh: <a href="${ph.page}">${ph.author}</a> / Wikimedia Commons · ${lic}`;
  };
  const groupAnchor = p.group === 'Thiên nhiên' ? 'thien-nhien' : 'van-hoa';
  const hero = p.photos[0];
  const i = PLACES.indexOf(p);
  const prev = PLACES[(i - 1 + PLACES.length) % PLACES.length];
  const next = PLACES[(i + 1) % PLACES.length];

  document.title = `${p.name} — Đà Nẵng`;
  document.querySelector('meta[name="description"]').content = p.lead;

  $('[data-hero-img]').src = hero.src;
  $('[data-hero-img]').alt = hero.alt;
  $('[data-hero-credit]').innerHTML = `${hero.caption} · ${credit(hero)}`;
  $('[data-crumbs]').innerHTML = `<a href="index.html">Trang chủ</a><span aria-hidden="true">/</span><a href="index.html#${groupAnchor}">${p.group}</a><span aria-hidden="true">/</span><span aria-current="page">${p.short}</span>`;
  $('[data-eyebrow]').textContent = `${p.group} · ${p.tag}`;
  $('[data-name]').textContent = p.name;
  $('[data-lead]').textContent = p.lead;

  $('[data-body]').innerHTML = p.body.map((t, n) => `<p${n === 0 ? ' class="dropcap"' : ''}>${t}</p>`).join('');
  $('[data-todo]').innerHTML = p.todo.map((t) => `<li>${t}</li>`).join('');
  $('[data-tip]').textContent = p.tip;

  $('[data-place-map]').dataset.placeMap = p.id;
  $('[data-facts]').innerHTML = `
    <div><dt>Nhóm</dt><dd>${p.group} · ${p.tag}</dd></div>
    <div><dt>Tọa độ</dt><dd>${p.lat.toFixed(4)}° B, ${p.lng.toFixed(4)}° Đ</dd></div>`;
  $('[data-osm]').href = `https://www.openstreetmap.org/?mlat=${p.lat}&mlon=${p.lng}#map=14/${p.lat}/${p.lng}`;

  $('[data-photo-count]').textContent = `${p.photos.length} ảnh · bấm để xem lớn`;
  $('[data-gallery]').classList.toggle('gallery--few', p.photos.length < 3);
  $('[data-gallery]').innerHTML = p.photos.map((ph) => `
    <figure class="gallery__item" data-reveal>
      <img src="${ph.src}" width="${ph.w}" height="${ph.h}" alt="${ph.alt}" loading="lazy" data-lightbox>
      <figcaption><strong>${ph.caption}</strong> <span class="credit">${credit(ph)}</span></figcaption>
    </figure>`).join('');

  $('[data-related]').innerHTML = p.related.map(placeById).map((r) => `
    <article class="tile" data-reveal>
      <img src="${r.photos[0].src}" alt="${r.photos[0].alt}" loading="lazy" style="object-position:${r.photos[0].pos}">
      <div class="tile__body">
        <p class="tile__tag">${r.tag}</p>
        <h3><a class="tile__link" href="${placeUrl(r.id)}">${r.name}</a></h3>
        <p>${r.lead}</p>
      </div>
    </article>`).join('');

  $('[data-pager]').innerHTML = `
    <a href="${placeUrl(prev.id)}" rel="prev"><small>Điểm trước</small>← ${prev.name}</a>
    <a href="${placeUrl(next.id)}" rel="next"><small>Điểm tiếp theo</small>${next.name} →</a>`;
})();
