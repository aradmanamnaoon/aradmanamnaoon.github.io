(function () {
  'use strict';

  const prefersReduced = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  const isMobile = window.matchMedia('(max-width: 640px)').matches;
  const isTouch = window.matchMedia('(pointer: coarse)').matches;

  document.documentElement.classList.add('js-ready');

  // ---------- 1. REVEAL ON SCROLL ----------
  function setupReveal() {
    const els = document.querySelectorAll('.reveal');

    if (!els.length) return;

    // On mobile, show sections immediately.
    // This prevents Projects and other sections from appearing late.
    if (
      isMobile ||
      prefersReduced ||
      !('IntersectionObserver' in window)
    ) {
      els.forEach((el) => {
        el.classList.add('visible');
      });

      return;
    }

    // Desktop reveal animation
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            io.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.06,
        rootMargin: '0px 0px 100px 0px'
      }
    );

    els.forEach((el) => {
      io.observe(el);
    });
  }

  // ---------- 2. CURSOR GLOW + PARALLAX ----------
  function setupCursorEffects() {
    // Disable expensive cursor animation on phones/tablets
    if (isTouch || prefersReduced) return;

    let targetGlowX = -9999;
    let targetGlowY = -9999;

    let currentGlowX = -9999;
    let currentGlowY = -9999;

    let targetDotX = 0;
    let targetDotY = 0;

    let currentDotX = 0;
    let currentDotY = 0;

    window.addEventListener(
      'mousemove',
      (e) => {
        targetGlowX = e.clientX;
        targetGlowY = e.clientY;

        targetDotX =
          (e.clientX / window.innerWidth - 0.5) * 14;

        targetDotY =
          (e.clientY / window.innerHeight - 0.5) * 14;
      },
      { passive: true }
    );

    window.addEventListener('mouseleave', () => {
      targetGlowX = -9999;
      targetGlowY = -9999;
    });

    function tick() {
      currentGlowX +=
        (targetGlowX - currentGlowX) * 0.18;

      currentGlowY +=
        (targetGlowY - currentGlowY) * 0.18;

      document.documentElement.style.setProperty(
        '--glow-x',
        `${currentGlowX}px`
      );

      document.documentElement.style.setProperty(
        '--glow-y',
        `${currentGlowY}px`
      );

      currentDotX +=
        (targetDotX - currentDotX) * 0.06;

      currentDotY +=
        (targetDotY - currentDotY) * 0.06;

      document.body.style.setProperty(
        '--dot-x',
        `${currentDotX}px`
      );

      document.body.style.setProperty(
        '--dot-y',
        `${currentDotY}px`
      );

      requestAnimationFrame(tick);
    }

    tick();
  }

  // ---------- INIT ----------
  function init() {
    setupReveal();
    setupCursorEffects();
  }

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      init,
      { once: true }
    );
  } else {
    init();
  }
})();
