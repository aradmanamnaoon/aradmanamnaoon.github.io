(() => {
  'use strict';
  const root = document.documentElement;
  const body = document.body;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)');
  const $ = (id) => document.getElementById(id);
  const langButtons = [...document.querySelectorAll('[data-lang]')];
  const switching = [...document.querySelectorAll('[data-mode]')];
  let currentLang = 'en';
  let currentMode = 'stored';
  const content = {
    stored: {
      gap: '4.63', fire: '40.45', non: '35.83',
      en: 'The stored scores make the groups look noticeably different.',
      fa: 'نمره‌های ذخیره‌شده نشان می‌دهند دو گروه تفاوت چشمگیری دارند.'
    },
    checked: {
      gap: '0.08', fire: '39.74', non: '39.67',
      en: 'Checking the original item answers changes the picture: the gap nearly vanishes.',
      fa: 'با بررسی پاسخ‌های اصلی سؤال‌ها، تصویر تغییر می‌کند: اختلاف تقریباً ناپدید می‌شود.'
    }
  };
  const loadSetting = (name, allowed, fallback) => {
    try { const s = localStorage.getItem(name); return allowed.includes(s) ? s : fallback; }
    catch (_) { return fallback; }
  };
  function lang(value) {
    currentLang = value;
    root.lang = value;
    root.dir = value === 'fa' ? 'rtl' : 'ltr';
    langButtons.forEach(btn => {
      const active = btn.dataset.lang === value;
      btn.classList.toggle('selected', active);
      btn.setAttribute('aria-pressed', String(active));
    });
    document.querySelectorAll('[data-en], [data-fa], [data-en-html], [data-fa-html]').forEach(element => {
      const html = element.dataset[value + 'Html'];
      const plain = element.dataset[value];
      if (html !== undefined) element.innerHTML = html; // all values static, authored in the page
      else if (plain !== undefined) element.textContent = plain;
    });
    updateComparison(currentMode);
    document.title = value === 'fa' ? 'از داده‌های آشفته تا بینش روشن | آراد' : 'From Messy Data to Meaningful Insight | Arad';
    try { localStorage.setItem('psychology-atlas-lang', value); } catch (_) {}
  }
  function updateComparison(mode) {
    currentMode = mode;
    const obj = content[mode];
    $('differenceValue').textContent = obj.gap;
    $('valueFire').textContent = obj.fire;
    $('valueNon').textContent = obj.non;
    $('differenceMessage').textContent = obj[currentLang];
    // The bar lengths use a common zero-based scale, not rescaled independently per group.
    $('barFire').style.width = `${(Number(obj.fire) / 50 * 100).toFixed(2)}%`;
    $('barNon').style.width = `${(Number(obj.non) / 50 * 100).toFixed(2)}%`;
    switching.forEach(btn => {
      const selected = btn.dataset.mode === mode;
      btn.classList.toggle('active', selected);
      btn.setAttribute('aria-pressed', String(selected));
    });
  }
  function setupDots() {
    if (!fine.matches || reduced.matches) return;
    let raf = 0, x = -1000, y = -1000;
    const paint = () => {
      raf = 0;
      if (document.hidden || reduced.matches) return;
      body.style.setProperty('--dot-pointer-x', x + 'px');
      body.style.setProperty('--dot-pointer-y', y + 'px');
    };
    const clear = () => {
      body.classList.remove('dots-active');
      if (raf) window.cancelAnimationFrame(raf);
      raf = 0;
    };
    window.addEventListener('pointermove', event => {
      if (event.pointerType === 'touch' || reduced.matches) return;
      x = event.clientX;
      y = event.clientY;
      body.classList.add('dots-active');
      if (!raf) raf = requestAnimationFrame(paint);
    }, {passive:true});
    document.addEventListener('pointerleave', clear);
    window.addEventListener('blur', clear);
    document.addEventListener('visibilitychange', () => {if (document.hidden) clear();});
    reduced.addEventListener?.('change', () => {if (reduced.matches) clear();});
  }
  function patternField() {
    const field = $('patternField');
    const count = 86;
    const frag = document.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      // Deterministic golden-angle placement; no randomness or customer data is visualized.
      const angle = (i * 137.507764) * Math.PI / 180;
      const radius = 13 + Math.sqrt((i + 1) / count) * 34;
      const node = document.createElement('span');
      node.style.left = (50 + Math.cos(angle) * radius) + '%';
      node.style.top = (50 + Math.sin(angle) * radius) + '%';
      node.style.setProperty('--delay', String(i % 7));
      node.style.setProperty('--duration', String(4 + i % 5));
      node.style.setProperty('--fade', String(.3 + (i % 5) * .13));
      frag.appendChild(node);
    }
    field.appendChild(frag);
  }
  function progress() {
    let raf = 0;
    const update = () => {
      raf = 0;
      const total = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      $('pageProgress').style.transform = `scaleX(${Math.min(1, window.scrollY / total)})`;
    };
    const queue = () => { if (!raf) raf = requestAnimationFrame(update); };
    window.addEventListener('scroll', queue, {passive:true});
    window.addEventListener('resize', queue, {passive:true});
    update();
  }
  function reveals() {
    const nodes = document.querySelectorAll('.reveal');
    if (reduced.matches || !('IntersectionObserver' in window)) return;
    root.classList.add('motion-ready');
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    }, {rootMargin:'0px 0px -20px 0px',threshold:.08});
    nodes.forEach(el => observer.observe(el));
  }
  const toggleTheme = () => {
    const theme = root.dataset.theme === 'light' ? 'dark' : 'light';
    root.dataset.theme = theme;
    try {localStorage.setItem('psychology-atlas-theme', theme);} catch (_) {}
  };
  const theme = loadSetting('psychology-atlas-theme', ['dark','light'], 'dark');
  root.dataset.theme = theme;
  langButtons.forEach(btn => btn.addEventListener('click', () => lang(btn.dataset.lang)));
  switching.forEach(btn => btn.addEventListener('click', () => updateComparison(btn.dataset.mode)));
  $('themeToggle').addEventListener('click', toggleTheme);
  lang(loadSetting('psychology-atlas-lang', ['en','fa'],'en'));
  patternField();
  progress();
  reveals();
  setupDots();
})();
