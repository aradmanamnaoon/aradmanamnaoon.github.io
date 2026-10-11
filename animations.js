/* Shared progressive motion. The content remains visible without this script. */
(function () {
  'use strict';
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const desktop = matchMedia('(min-width: 900px)');
  // Respect the operating system's reduced-motion preference.
  // Ignore the retired user-controlled pause setting from older releases.
  const enabled = () => !reduced.matches;
  let storyMedia = null, storyLoaded = false, storyPromise = null, storyObserver = null, detailReady = false;

  function preference() {
    root.classList.toggle('motion-off', !enabled());
    if (!enabled()) document.body.classList.remove('dots-active');
    root.classList.toggle('motion-enabled', enabled() && 'IntersectionObserver' in window);
    if (!enabled()) {
      document.querySelectorAll('[data-reveal="true"]').forEach(el => el.classList.add('is-revealed'));
      document.querySelectorAll('.motion-split').forEach(el => el.classList.add('is-in'));
      if (storyMedia) { storyMedia.revert(); storyMedia = null; }
      document.querySelector('.story-section')?.classList.remove('story-pinned');
      document.querySelector('.motion-intro')?.remove();
      document.querySelector('.motion-curtain')?.remove();
    } else {
      detail();
      if (storyLoaded) pinStory(); else watchStory();
    }
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
    // One CSS dot grid is the only background layer. Move a radial light
    // across it rather than drawing a second, differently sized canvas grid.
    const surface = document.body;
    const supportsHover = fine.matches;
    if (!supportsHover) return; // No pointer tracking or animation loop on touch devices.
    let raf = 0, px = -1000, py = -1000;
    function paint() {
      raf = 0;
      if (!enabled() || document.hidden) return;
      surface.style.setProperty('--dot-pointer-x', px + 'px');
      surface.style.setProperty('--dot-pointer-y', py + 'px');
    }
    function move(event) {
      if (!enabled() || event.pointerType === 'touch') return;
      px = event.clientX; py = event.clientY;
      surface.classList.add('dots-active');
      if (!raf) raf = requestAnimationFrame(paint);
    }
    function clear() {
      surface.classList.remove('dots-active');
      if (raf) { cancelAnimationFrame(raf); raf = 0; }
    }
    addEventListener('pointermove', move, { passive: true });
    document.addEventListener('pointerleave', clear);
    addEventListener('blur', clear);
    document.addEventListener('visibilitychange', () => { if (document.hidden) clear(); });
  }
  function pointer() {
    // Preserve subtle card depth on fine pointers without replacing the
    // browser's accessible native cursor or moving actionable controls.
    if (!fine.matches || !enabled()) return;
    let active = null, bounds = null, pending = false, x = 0, y = 0;
    document.addEventListener('pointermove', event => {
      if (!enabled() || event.pointerType === 'touch') return;
      x = event.clientX; y = event.clientY;
      const card = event.target.closest?.('.project-card, .research-evidence-card, .inventory-card, .case-section, .surface-card');
      if (card !== active) {
        if (active) {
          active.classList.remove('motion-tilt');
          active.style.removeProperty('--tilt-x');
          active.style.removeProperty('--tilt-y');
        }
        active = card; bounds = card?.getBoundingClientRect();
        card?.classList.add('motion-tilt');
      }
      if (active && bounds && !pending) {
        pending = true;
        requestAnimationFrame(() => {
          pending = false;
          if (!active || !enabled()) return;
          const rx = (y - bounds.top) / bounds.height - .5;
          const ry = (x - bounds.left) / bounds.width - .5;
          active.style.setProperty('--tilt-x', (-rx * 3).toFixed(2) + 'deg');
          active.style.setProperty('--tilt-y', (ry * 3).toFixed(2) + 'deg');
          active.style.setProperty('--spot-x', (x - bounds.left - 110) + 'px');
          active.style.setProperty('--spot-y', (y - bounds.top - 110) + 'px');
        });
      }
    }, { passive: true });
    document.addEventListener('pointerleave', () => {
      if (active) active.classList.remove('motion-tilt');
      active = null; bounds = null;
    });
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
      viewport.scrollLeft = 0; story.classList.add('story-pinned');
      const distance = () => Math.max(1, track.scrollWidth - viewport.clientWidth);
      // Viewport-wide panels keep every pinned chapter within the visible screen.
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
  function sectionNavigation() {
    // Explicitly animate same-page anchors; browser defaults may jump instantly
    // when a section changes its layout during a scroll-driven story.
    let frame = 0;
    const stop = () => { if (frame) cancelAnimationFrame(frame); frame = 0; };
    document.addEventListener('click', event => {
      if (!enabled() || event.defaultPrevented || event.button !== 0 ||
          event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const link = event.target.closest?.('a[href]');
      if (!link || link.target || link.hasAttribute('download')) return;
      const url = new URL(link.href, location.href);
      if (url.origin !== location.origin || url.pathname !== location.pathname ||
          url.search !== location.search || !url.hash) return;
      let id;
      try { id = decodeURIComponent(url.hash.slice(1)); }
      catch (_) { return; }
      const target = document.getElementById(id);
      if (!target) return;
      event.preventDefault();
      stop();
      const nav = document.querySelector('.site-nav-wrap, .site-nav, .nav');
      const navHeight = nav?.getBoundingClientRect().height || 76;
      const start = window.scrollY;
      const maxScroll = Math.max(0, document.documentElement.scrollHeight - innerHeight);
      const destination = Math.min(maxScroll, Math.max(0, start + target.getBoundingClientRect().top - navHeight - 20));
      const distance = destination - start;
      history.pushState(null, '', url.hash);
      if (Math.abs(distance) < 2) return;
      const duration = Math.min(1250, Math.max(500, 440 + Math.abs(distance) * .22));
      let started = null;
      function step(now) {
        if (!enabled()) { stop(); window.scrollTo(0, destination); return; }
        if (started === null) started = now;
        const t = Math.min(1, (now - started) / duration);
        const ease = 1 - Math.pow(1 - t, 3);
        window.scrollTo(0, start + distance * ease);
        if (t < 1) frame = requestAnimationFrame(step);
        else frame = 0;
      }
      frame = requestAnimationFrame(step);
    });
    // Allow visitors to interrupt the animation with touch, wheel, or keyboard.
    document.addEventListener('wheel', stop, { passive: true });
    document.addEventListener('touchstart', stop, { passive: true });
    document.addEventListener('keydown', event => {
      if (['PageDown', 'PageUp', 'Home', 'End', 'ArrowDown', 'ArrowUp', ' '].includes(event.key)) stop();
    });
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
    reduced.addEventListener?.('change', preference);
    preference(); progress(); dots(); intro(); story(); sectionNavigation(); routes();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
