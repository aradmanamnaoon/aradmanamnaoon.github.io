(function () {
  'use strict';

  const reducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  );

  function setupScrollReveals() {
    const elements = document.querySelectorAll('[data-reveal="true"]');

    if (
      reducedMotion.matches ||
      !elements.length ||
      !('IntersectionObserver' in window)
    ) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed');
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px 96px 0px', threshold: 0.08 }
    );

    document.documentElement.classList.add('motion-enabled');
    elements.forEach((element, index) => {
      element.style.setProperty('--reveal-index', String(Math.min(index, 6)));
      observer.observe(element);
    });

    reducedMotion.addEventListener?.('change', (event) => {
      if (event.matches) {
        document.documentElement.classList.remove('motion-enabled');
        elements.forEach((element) => element.classList.add('is-revealed'));
        observer.disconnect();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupScrollReveals, {
      once: true
    });
  } else {
    setupScrollReveals();
  }
})();
