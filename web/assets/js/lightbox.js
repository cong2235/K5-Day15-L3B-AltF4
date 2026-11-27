// Phóng to ảnh: mọi <img data-lightbox>. Ảnh cùng [data-gallery] (hoặc cùng trang) xem trước/sau được.
// Chú thích lấy từ <figcaption> của <figure> chứa ảnh, nếu không có thì từ .credit trong <article>.
(() => {
  const dialog = document.createElement('dialog');
  dialog.className = 'lightbox';
  dialog.setAttribute('aria-label', 'Xem ảnh lớn');
  dialog.innerHTML = `
    <figure class="lightbox__figure">
      <img class="lightbox__img" alt="">
      <figcaption class="lightbox__caption"></figcaption>
    </figure>
    <p class="lightbox__count" aria-live="polite"></p>
    <button class="lightbox__btn lightbox__close" type="button" aria-label="Đóng" autofocus>✕</button>
    <button class="lightbox__btn lightbox__prev" type="button" aria-label="Ảnh trước">←</button>
    <button class="lightbox__btn lightbox__next" type="button" aria-label="Ảnh sau">→</button>`;
  document.body.append(dialog);

  const bigImg = dialog.querySelector('.lightbox__img');
  const caption = dialog.querySelector('.lightbox__caption');
  const count = dialog.querySelector('.lightbox__count');
  const prevBtn = dialog.querySelector('.lightbox__prev');
  const nextBtn = dialog.querySelector('.lightbox__next');
  let items = [];
  let index = 0;

  function show(i) {
    index = (i + items.length) % items.length;
    const el = items[index];
    bigImg.src = el.currentSrc || el.src;
    bigImg.alt = el.alt;
    const source = el.closest('figure')?.querySelector('figcaption') ?? el.closest('article')?.querySelector('.credit');
    caption.innerHTML = source ? source.innerHTML : el.alt;
    count.textContent = `${index + 1} / ${items.length}`;
  }

  function open(el) {
    const scope = el.closest('[data-gallery]') || document;
    items = [...scope.querySelectorAll('img[data-lightbox]')];
    const single = items.length < 2;
    prevBtn.hidden = nextBtn.hidden = count.hidden = single;
    show(items.indexOf(el));
    document.documentElement.classList.add('has-lightbox');
    dialog.showModal();
  }

  dialog.addEventListener('close', () => document.documentElement.classList.remove('has-lightbox'));
  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
  dialog.querySelector('.lightbox__close').addEventListener('click', () => dialog.close());
  prevBtn.addEventListener('click', () => show(index - 1));
  nextBtn.addEventListener('click', () => show(index + 1));
  dialog.addEventListener('keydown', (e) => {
    if (items.length < 2) return;
    if (e.key === 'ArrowLeft') show(index - 1);
    if (e.key === 'ArrowRight') show(index + 1);
  });

  function prepare() {
    document.querySelectorAll('img[data-lightbox]:not([tabindex])').forEach((el) => {
      el.tabIndex = 0;
      el.setAttribute('role', 'button');
      el.setAttribute('aria-label', `Phóng to ảnh: ${el.alt}`);
    });
  }
  document.addEventListener('click', (e) => {
    const el = e.target.closest('img[data-lightbox]');
    if (el) open(el);
  });
  document.addEventListener('keydown', (e) => {
    const el = e.target.closest?.('img[data-lightbox]');
    if (el && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); open(el); }
  });
  prepare();
  window.Lightbox = { prepare };
})();
