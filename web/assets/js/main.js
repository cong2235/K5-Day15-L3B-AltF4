const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Header: trong suốt trên hero, nền đặc khi đã cuộn qua hero.
const header = document.querySelector('[data-header]');
const hero = document.querySelector('[data-hero]');
const heroMedia = document.querySelector('[data-parallax]');

let ticking = false;
function onScroll() {
  if (ticking) return;
  ticking = true;
  requestAnimationFrame(() => {
    const y = window.scrollY;
    const heroH = hero ? hero.offsetHeight : 0;
    header.classList.toggle('is-solid', y > heroH - header.offsetHeight);
    if (heroMedia && !reduceMotion && y < heroH) {
      heroMedia.style.transform = `translate3d(0, ${y * 0.12}px, 0)`;
    }
    ticking = false;
  });
}
addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Hiện dần khi cuộn tới; phần tử trong [data-stagger] hiện lệch nhau.
document.querySelectorAll('[data-stagger]').forEach((group) => {
  group.querySelectorAll('[data-reveal]').forEach((el, i) => el.style.setProperty('--d', `${i * 110}ms`));
});
const revealer = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (e.isIntersecting) {
      e.target.classList.add('is-in');
      revealer.unobserve(e.target);
    }
  }
}, { threshold: 0.12 });
document.querySelectorAll('[data-reveal]').forEach((el) => revealer.observe(el));

// Đánh dấu mục đang xem trên menu.
const navLinks = [...document.querySelectorAll('.nav a')];
const sectionIo = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (e.isIntersecting) navLinks.forEach((a) => a.setAttribute('aria-current', String(a.hash === `#${e.target.id}`)));
  }
}, { rootMargin: '-45% 0px -50% 0px' });
document.querySelectorAll('main > section[id]').forEach((s) => sectionIo.observe(s));

// "Một ngày": điểm dừng đang chọn đổi ảnh lớn bên trái (cuộn, rê chuột hoặc Tab).
const stops = [...document.querySelectorAll('[data-stop]')];
const stageImgs = [...document.querySelectorAll('[data-stop-img]')];
const stageLabel = document.querySelector('[data-stage-label]');
function showStop(n) {
  stops.forEach((s) => s.classList.toggle('is-active', s.dataset.stop === n));
  stageImgs.forEach((img) => img.classList.toggle('is-active', img.dataset.stopImg === n));
  stageLabel.textContent = stops.find((s) => s.dataset.stop === n).querySelector('h3').textContent;
}
stops.forEach((s) => {
  s.addEventListener('mouseenter', () => showStop(s.dataset.stop));
  s.addEventListener('focus', () => showStop(s.dataset.stop));
});
const stopIo = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) showStop(e.target.dataset.stop);
}, { rootMargin: '-45% 0px -50% 0px' });
stops.forEach((s) => stopIo.observe(s));
