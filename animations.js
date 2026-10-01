(function () {
  'use strict';

  const prefersReduced = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  document.documentElement.classList.add('js-ready');

  // ---------- 1. REVEAL ON SCROLL ----------
  function setupReveal() {
    const els = document.querySelectorAll('.reveal');
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -60px 0px' }
    );
    els.forEach((el) => io.observe(el));
  }

  // ---------- 2. CURSOR-FOLLOWING DOT GLOW + PARALLAX ----------
  function setupCursorEffects() {
    const isTouch = window.matchMedia('(pointer: coarse)').matches;
    if (isTouch) return;

    let targetGlowX = -9999, targetGlowY = -9999;
    let currentGlowX = -9999, currentGlowY = -9999;

    let targetDotX = 0, targetDotY = 0;
    let currentDotX = 0, currentDotY = 0;

    window.addEventListener('mousemove', (e) => {
      targetGlowX = e.clientX;
      targetGlowY = e.clientY;

      targetDotX = (e.clientX / window.innerWidth - 0.5) * 14;
      targetDotY = (e.clientY / window.innerHeight - 0.5) * 14;
    });

    window.addEventListener('mouseleave', () => {
      targetGlowX = -9999;
      targetGlowY = -9999;
    });

    function tick() {
      currentGlowX += (targetGlowX - currentGlowX) * 0.18;
      currentGlowY += (targetGlowY - currentGlowY) * 0.18;

      document.documentElement.style.setProperty(
        '--glow-x',
        `${currentGlowX}px`
      );
      document.documentElement.style.setProperty(
        '--glow-y',
        `${currentGlowY}px`
      );

      currentDotX += (targetDotX - currentDotX) * 0.06;
      currentDotY += (targetDotY - currentDotY) * 0.06;

      document.body.style.setProperty('--dot-x', `${currentDotX}px`);
      document.body.style.setProperty('--dot-y', `${currentDotY}px`);

      requestAnimationFrame(tick);
    }
    tick();
  }

  function init() {
    if (prefersReduced) return;
    setupReveal();
    setupCursorEffects();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();