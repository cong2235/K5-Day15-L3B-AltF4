// Bản đồ OpenStreetMap (Leaflet) cho trang chủ và trang chi tiết. Đọc điểm từ window.PLACES.
(() => {
  if (!window.L || !window.PLACES) return;

  const TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  const ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';

  function popupHtml(p) {
    return `<a class="map-popup" href="${placeUrl(p.id)}">
      <img src="${p.photos[0].src}" alt="">
      <span class="map-popup__tag">${p.group} · ${p.tag}</span>
      <strong>${p.name}</strong>
      <span class="map-popup__more">Xem chi tiết →</span>
    </a>`;
  }

  function createMap(el, { activeId } = {}) {
    const map = L.map(el, { scrollWheelZoom: false });
    L.tileLayer(TILE_URL, { maxZoom: 18, attribution: ATTRIBUTION }).addTo(map);
    const markers = {};
    PLACES.forEach((p, i) => {
      const muted = activeId && p.id !== activeId;
      const icon = L.divIcon({
        className: `map-pin${muted ? ' map-pin--muted' : ''}${p.id === activeId ? ' map-pin--active' : ''}`,
        html: `<span>${i + 1}</span>`, iconSize: [32, 32], iconAnchor: [16, 16], popupAnchor: [0, -14],
      });
      markers[p.id] = L.marker([p.lat, p.lng], { icon, title: p.name, alt: p.name, riseOnHover: true })
        .addTo(map)
        .bindPopup(popupHtml(p), { closeButton: false, maxWidth: 240 });
    });
    return { map, markers };
  }

  // Trang chủ: danh sách + bản đồ lớn.
  const atlasMap = document.querySelector('[data-atlas-map]');
  const atlasList = document.querySelector('[data-atlas-list]');
  if (atlasMap && atlasList) {
    atlasList.innerHTML = PLACES.map((p, i) => `
      <li>
        <button type="button" class="atlas__item" data-place="${p.id}">
          <span class="atlas__num">${i + 1}</span>
          <span class="atlas__name">${p.name}<small>${p.group} · ${p.tag}</small></span>
        </button>
        <a class="atlas__more" href="${placeUrl(p.id)}" aria-label="Xem chi tiết ${p.name}">→</a>
      </li>`).join('');

    const { map, markers } = createMap(atlasMap);
    map.fitBounds(L.latLngBounds(PLACES.map((p) => [p.lat, p.lng])), { padding: [36, 36] });

    const setActive = (id) => {
      atlasList.querySelectorAll('.atlas__item').forEach((b) => b.classList.toggle('is-active', b.dataset.place === id));
      Object.entries(markers).forEach(([pid, m]) => m.getElement()?.classList.toggle('map-pin--active', pid === id));
    };
    atlasList.addEventListener('click', (e) => {
      const btn = e.target.closest('.atlas__item');
      if (!btn) return;
      const p = placeById(btn.dataset.place);
      map.flyTo([p.lat, p.lng], 15, { duration: 0.9 });
      map.once('moveend', () => markers[p.id].openPopup());
      setActive(p.id);
    });
    Object.entries(markers).forEach(([id, m]) => m.on('click', () => setActive(id)));
  }

  // Trang chi tiết: bản đồ nhỏ quanh điểm đang xem.
  const placeMap = document.querySelector('[data-place-map]');
  if (placeMap) {
    const p = placeById(placeMap.dataset.placeMap);
    if (p) createMap(placeMap, { activeId: p.id }).map.setView([p.lat, p.lng], 12);
  }
})();
