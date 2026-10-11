/* Shared progressive motion. The content remains visible without this script. */
(function () {
  'use strict';
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const desktop = matchMedia('(min-width: 900px)');
  let paused = false;
  try { paused = localStorage.getItem('arad-motion-paused') === 'true'; } catch (_) {}
  const enabled = () => !reduced.matches && !paused;
  let storyMedia = null, storyLoaded = false, storyPromise = null, storyObserver = null, detailReady = false;

  function preference() {
    root.classList.toggle('motion-off', !enabled());
    root.classList.toggle('motion-enabled', enabled() && 'IntersectionObserver' in window);
    if (!enabled()) {
      document.querySelectorAll('[data-reveal="true"]').forEach(el => el.classList.add('is-revealed'));
      document.querySelectorAll('.motion-split').forEach(el => el.classList.add('is-in'));
      if (storyMedia) { storyMedia.revert(); storyMedia = null; }
      document.querySelector('.story-section')?.classList.remove('story-pinned');
      document.querySelector('.motion-intro')?.remove();
      document.querySelector('.motion-curtain')?.remove();
      root.classList.remove('motion-pointer');
      document.querySelector('.motion-cursor')?.classList.remove('is-visible');
    } else {
      detail();
      if (fine.matches && document.querySelector('.motion-cursor')) root.classList.add('motion-pointer');
      if (storyLoaded) pinStory(); else watchStory();
    }
  }
  function control() {
    const nav = document.querySelector('nav[aria-label="Primary navigation"] .site-nav-links, nav[aria-label="Primary navigation"] .nav-links');
    if (!nav) return;
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'motion-toggle';
    const label = () => {
      button.disabled = reduced.matches;
      button.setAttribute('aria-pressed', String(paused || reduced.matches));
      button.textContent = reduced.matches ? 'Reduced motion' : paused ? 'Resume motion' : 'Pause motion';
    };
    label(); nav.append(button);
    button.addEventListener('click', () => {
      paused = !paused;
      try { localStorage.setItem('arad-motion-paused', String(paused)); } catch (_) {}
      label(); preference();
    });
    reduced.addEventListener?.('change', () => { label(); preference(); });
  }
  function intro() {
    if (!enabled()) return;
    let first = false, arriving = false;
    try {
      first = sessionStorage.getItem('arad-intro-seen') !== 'true';
      arriving = sessionStorage.getItem('arad-route-curtain') === 'true';
      sessionStorage.setItem('arad-intro-seen', 'true');
      sessionStorage.removeItem('arad-route-curtain');
    } catch (_) { first = true; }
    if (!first && !arriving) return;
    const overlay = document.createElement('div');
    overlay.className = 'motion-intro'; overlay.setAttribute('aria-hidden', 'true');
    overlay.innerHTML = '<span>ARAD<small>Signals → systems → evidence</small></span>';
    document.body.append(overlay);
    if (!overlay.animate) { overlay.remove(); return; }
    overlay.querySelector('span').animate([
      { opacity: 0, transform: 'translateY(35px) scale(.94)' },
      { opacity: 1, transform: 'translateY(0) scale(1)' }
    ], { duration: 560, easing: 'cubic-bezier(.22,1,.36,1)', fill: 'both' });
    overlay.animate([{ transform: 'translateY(0)' }, { transform: 'translateY(-102%)' }], {
      delay: arriving ? 450 : 650, duration: 620, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards'
    }).finished.then(() => overlay.remove()).catch(() => overlay.remove());
    setTimeout(() => overlay.remove(), 1900);
  }
  function reveals() {
    if (!enabled() || !('IntersectionObserver' in window)) return;
    const targets = [...document.querySelectorAll('[data-reveal="true"]')];
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-revealed'); observer.unobserve(entry.target); }
    }), { rootMargin: '0px 0px 40px 0px', threshold: .08 });
    targets.forEach((el, i) => { el.style.setProperty('--reveal-index', String(i % 4)); observer.observe(el); });
  }
  function splitText() {
    if (!enabled() || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-in'); observer.unobserve(entry.target); }
    }), { threshold: .1 });
    document.querySelectorAll('.hero-title, .hero h1, .story-head h2').forEach(heading => {
      if (heading.querySelector('[data-word]')) return;
      const walker = document.createTreeWalker(heading, NodeFilter.SHOW_TEXT), nodes = [];
      let index = 0;
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(node => {
        if (!node.textContent.trim()) return;
        const fragment = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach(part => {
          if (!part.trim()) { fragment.append(document.createTextNode(part)); return; }
          const word = document.createElement('span'); word.dataset.word = '';
          word.style.setProperty('--split-index', String(Math.min(index++, 9)));
          word.textContent = part; fragment.append(word);
        });
        node.replaceWith(fragment);
      });
      heading.classList.add('motion-split'); observer.observe(heading);
    });
  }
  function counters() {
    if (!enabled() || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      const original = entry.target.textContent.trim();
      const match = /^(\d+(?:\.\d+)?)([MK%]?)$/.exec(original);
      if (!match) return;
      const value = Number(match[1]), digits = (match[1].split('.')[1] || '').length, start = performance.now();
      function frame(now) {
        if (!enabled() || !entry.target.isConnected) { entry.target.textContent = original; return; }
        const t = Math.min((now - start) / 950, 1);
        entry.target.textContent = (value * (1 - Math.pow(1 - t, 3))).toFixed(digits) + match[2];
        if (t < 1) requestAnimationFrame(frame); else entry.target.textContent = original;
      }
      requestAnimationFrame(frame);
    }), { threshold: .35 });
    document.querySelectorAll('.metric strong, .project-metric strong').forEach(el => observer.observe(el));
  }
  function progress() {
    const bar = document.createElement('div'); bar.className = 'motion-progress';
    bar.setAttribute('aria-hidden', 'true'); document.body.append(bar);
    const hero = document.querySelector('.hero-section');
    const foreground = hero?.querySelector('.hero-media');
    const midground = hero?.querySelector('.hero-copy');
    let pending = false;
    function update() {
      pending = false;
      const length = Math.max(1, document.documentElement.scrollHeight - innerHeight);
      bar.style.transform = 'scaleX(' + Math.min(1, Math.max(0, scrollY / length)) + ')';
      document.body.classList.toggle('is-scrolled', scrollY > 80);
      if (foreground && midground && desktop.matches) {
        const distance = enabled() && scrollY < innerHeight * 1.5 ? scrollY : 0;
        foreground.style.transform = 'translate3d(0,' + Math.min(120, distance * .14) + 'px,0)';
        midground.style.transform = 'translate3d(0,' + Math.max(-40, -distance * .045) + 'px,0)';
      }
    }
    function schedule() { if (!pending) { pending = true; requestAnimationFrame(update); } }
    addEventListener('scroll', schedule, { passive: true });
    addEventListener('resize', schedule, { passive: true }); schedule();
  }
  function heroMask() {
    if (!enabled()) return;
    const portrait = document.querySelector('.hero-portrait-frame');
    portrait?.animate?.([
      { clipPath: 'circle(8% at 50% 50%)', opacity: .35, transform: 'scale(1.08)' },
      { clipPath: 'circle(75% at 50% 50%)', opacity: 1, transform: 'scale(1)' }
    ], { duration: 1050, easing: 'cubic-bezier(.22,1,.36,1)' });
  }
  function dots() {
    const canvas = document.createElement('canvas'); canvas.className = 'motion-dots';
    canvas.setAttribute('aria-hidden', 'true'); document.body.append(canvas);
    const ctx = canvas.getContext('2d'); if (!ctx) return;
    let width = 0, height = 0, x = -9999, y = -9999, touched = 0, drawing = false;
    function resize() {
      const dpr = Math.min(devicePixelRatio || 1, 1.5);
      width = innerWidth; height = innerHeight;
      canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function draw(now) {
      if (!enabled() || document.hidden) { ctx.clearRect(0, 0, width, height); drawing = false; return; }
      ctx.clearRect(0, 0, width, height);
      const fade = Math.max(0, 1 - (now - touched) / 950);
      if (!fade) { drawing = false; return; }
      for (let px = 15; px < width; px += 30) for (let py = 15; py < height; py += 30) {
        const d2 = (px - x) ** 2 + (py - y) ** 2;
        if (d2 > 260 ** 2) continue;
        const power = (1 - Math.sqrt(d2) / 260) * fade;
        ctx.fillStyle = 'rgba(154,213,255,' + (power * .88).toFixed(3) + ')';
        ctx.beginPath(); ctx.arc(px, py, 1.3 + power * 2.6, 0, Math.PI * 2); ctx.fill();
      }
      requestAnimationFrame(draw);
    }
    function wake(event) {
      if (!enabled()) return;
      x = event.clientX; y = event.clientY; touched = performance.now();
      if (!drawing) { drawing = true; requestAnimationFrame(draw); }
    }
    addEventListener('resize', resize, { passive: true }); resize();
    addEventListener('pointermove', wake, { passive: true });
    addEventListener('pointerdown', wake, { passive: true });
  }
  function pointer() {
    if (!fine.matches || !enabled()) return;
    const cursor = document.createElement('div'); cursor.className = 'motion-cursor';
    cursor.setAttribute('aria-hidden', 'true'); document.body.append(cursor);
    root.classList.add('motion-pointer');
    let active = null, bounds = null, magnetic = null, magneticBounds = null;
    let pending = false, x = -100, y = -100, cursorRadius = 13;
    document.addEventListener('pointermove', event => {
      if (!enabled()) return;
      x = event.clientX; y = event.clientY;
      cursor.classList.add('is-visible');
      cursor.classList.toggle('is-hover', !!event.target.closest('a, button, summary'));
      cursor.classList.toggle('is-drag', !!event.target.closest('.story-viewport'));
      cursor.classList.toggle('is-text', !!event.target.closest('input, textarea, [contenteditable="true"]'));
      cursorRadius = cursor.classList.contains('is-drag') ? 27 : cursor.classList.contains('is-hover') ? 23 : 13;
      if (!pending) { pending = true; requestAnimationFrame(() => {
        pending = false;
        cursor.style.transform = 'translate3d(' + (x - cursorRadius) + 'px,' + (y - cursorRadius) + 'px,0)';
      }); }
      const card = event.target.closest('.project-card, .research-evidence-card, .inventory-card, .case-section, .surface-card');
      if (card !== active) {
        if (active) { active.classList.remove('motion-tilt'); active.style.removeProperty('--tilt-x'); active.style.removeProperty('--tilt-y'); }
        active = card; bounds = card?.getBoundingClientRect(); card?.classList.add('motion-tilt');
      }
      if (active && bounds) {
        const rx = (y - bounds.top) / bounds.height - .5, ry = (x - bounds.left) / bounds.width - .5;
        active.style.setProperty('--tilt-x', (-rx * 4).toFixed(2) + 'deg');
        active.style.setProperty('--tilt-y', (ry * 4).toFixed(2) + 'deg');
        active.style.setProperty('--spot-x', (x - bounds.left - 110) + 'px');
        active.style.setProperty('--spot-y', (y - bounds.top - 110) + 'px');
      }
      const link = event.target.closest('.hero-button, .pill-link, .action, .utility-action');
      if (link !== magnetic) {
        if (magnetic) { magnetic.style.removeProperty('--mag-x'); magnetic.style.removeProperty('--mag-y'); magnetic.classList.remove('motion-magnetic'); }
        magnetic = link; magneticBounds = link?.getBoundingClientRect(); magnetic?.classList.add('motion-magnetic');
      }
      if (magnetic && magneticBounds) {
        magnetic.style.setProperty('--mag-x', (((x - magneticBounds.left) / magneticBounds.width - .5) * 9).toFixed(1) + 'px');
        magnetic.style.setProperty('--mag-y', (((y - magneticBounds.top) / magneticBounds.height - .5) * 9).toFixed(1) + 'px');
      }
    }, { passive: true });
    document.addEventListener('pointerleave', () => cursor.classList.remove('is-visible'));
  }
  function loadScript(path) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script'); script.src = path; script.async = true;
      script.onload = resolve; script.onerror = reject; document.head.append(script);
    });
  }
  function pinStory() {
    const story = document.querySelector('.story-section');
    if (!story || !storyLoaded || !enabled() || !desktop.matches || storyMedia) return;
    const track = story.querySelector('.story-track'), viewport = story.querySelector('.story-viewport');
    const panels = [...story.querySelectorAll('.story-panel')];
    if (!track || !viewport || panels.length < 2) return;
    const gsap = window.gsap, ScrollTrigger = window.ScrollTrigger;
    gsap.registerPlugin(ScrollTrigger);
    storyMedia = gsap.matchMedia();
    storyMedia.add('(min-width: 900px) and (prefers-reduced-motion: no-preference)', () => {
      if (paused) return;
      viewport.scrollLeft = 0; story.classList.add('story-pinned');
      const distance = () => Math.max(1, track.scrollWidth - viewport.clientWidth);
      gsap.to(track, { x: () => -distance(), ease: 'none', scrollTrigger: {
        trigger: story, pin: true, start: 'top top', end: () => '+=' + Math.max(900, distance()),
        scrub: .65, snap: { snapTo: 1 / (panels.length - 1), duration: { min: .18, max: .42 }, delay: .08 },
        invalidateOnRefresh: true, anticipatePin: 1,
        onUpdate: self => panels.forEach((panel, i) => panel.classList.toggle('is-current', Math.round(self.progress * (panels.length - 1)) === i))
      } });
      story.querySelectorAll('.story-visual path').forEach(path => {
        const length = path.getTotalLength();
        gsap.fromTo(path, { strokeDasharray: length, strokeDashoffset: length }, {
          strokeDashoffset: 0, ease: 'none', scrollTrigger: { trigger: story, start: 'top 80%', end: 'bottom 20%', scrub: true }
        });
      });
      return () => { story.classList.remove('story-pinned'); gsap.set(track, { clearProps: 'transform' }); };
    });
    ScrollTrigger.refresh();
  }
  function story() {
    const section = document.querySelector('.story-section'); if (!section) return;
    const viewport = section.querySelector('.story-viewport');
    section.querySelectorAll('.story-controls button').forEach(button => button.addEventListener('click', () => {
      viewport.scrollBy({ left: viewport.clientWidth * (button.dataset.direction === 'next' ? .85 : -.85), behavior: enabled() ? 'smooth' : 'auto' });
    }));
    desktop.addEventListener?.('change', () => { if (desktop.matches) watchStory(); });
    watchStory();
  }
  function watchStory() {
    const section = document.querySelector('.story-section');
    if (!section || storyLoaded || storyObserver || navigator.connection?.saveData || !desktop.matches || !enabled() || !('IntersectionObserver' in window)) return;
    storyObserver = new IntersectionObserver(entries => {
      if (!entries.some(entry => entry.isIntersecting)) return;
      if (!enabled()) return;
      storyObserver.disconnect(); storyObserver = null;
      if (!storyPromise) storyPromise = loadScript('/assets/vendor/gsap.min.js').then(() => loadScript('/assets/vendor/ScrollTrigger.min.js'));
      storyPromise.then(() => { storyLoaded = true; pinStory(); }).catch(() => {});
    }, { rootMargin: '450px' });
    storyObserver.observe(section);
  }
  function routes() {
    if ('onpageswap' in window) return; // Native cross-document View Transitions.
    document.addEventListener('click', event => {
      if (!enabled() || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const link = event.target.closest('a[href]');
      if (!link || link.target || link.hasAttribute('download')) return;
      const url = new URL(link.href, location.href);
      if (url.origin !== location.origin || (url.pathname === location.pathname && url.search === location.search)) return;
      event.preventDefault();
      const curtain = document.createElement('div'); curtain.className = 'motion-curtain';
      curtain.setAttribute('aria-hidden', 'true'); document.body.append(curtain);
      try { sessionStorage.setItem('arad-route-curtain', 'true'); } catch (_) {}
      let navigating = false;
      const navigate = () => { if (!navigating) { navigating = true; location.assign(url.href); } };
      if (!curtain.animate) { navigate(); return; }
      curtain.animate([{ transform: 'translateY(101%)' }, { transform: 'translateY(0)' }], {
        duration: 380, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards'
      }).finished.then(navigate).catch(navigate);
      setTimeout(navigate, 550);
    });
    addEventListener('pageshow', () => document.querySelector('.motion-curtain')?.remove());
  }
  function detail() {
    if (!enabled() || detailReady) return;
    detailReady = true;
    heroMask(); reveals(); splitText(); counters(); pointer();
  }
  function init() {
    control(); preference(); progress(); dots(); intro(); story(); routes();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
