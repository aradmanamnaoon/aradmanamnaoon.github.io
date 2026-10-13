/* Progressive enhancement for /projects/. No framework, network request or dependency. */
(function () {
  'use strict';
  const archive = document.getElementById('selected-projects');
  const api = window.portfolioArchive;
  const explorer = document.getElementById('archive-explorer');
  if (!archive || !api || !explorer) return;

  const container = document.getElementById('projects-paginated');
  const search = document.getElementById('archive-search');
  const source = document.getElementById('archive-source');
  const reset = document.getElementById('archive-clear');
  const count = document.getElementById('archive-count');
  const chapter = document.getElementById('archive-chapter');
  const topicButtons = [...explorer.querySelectorAll('[data-archive-topic]')];
  const categoryButtons = [...explorer.querySelectorAll('[data-archive-category]')];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)');
  const state = { query: '', source: 'all', topic: 'all', category: 'all' };
  let debounce = 0;
  let paintQueued = false;
  let copyMessage = '';

  const motionOK = () => !reduced.matches && !document.documentElement.classList.contains('motion-off');
  const revealObserver = 'IntersectionObserver' in window
    ? new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.setAttribute('data-archive-enter', 'shown');
            revealObserver.unobserve(entry.target);
          }
        });
      }, { threshold: .08, rootMargin: '0px 0px 50px 0px' })
    : null;

  function hashId(text) {
    let hash = 2166136261;
    for (const char of text) {
      hash ^= char.charCodeAt(0);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function signature(id) {
    // Deterministic, data-specific editorial artwork. No visual assets fetched.
    const seed = hashId(id);
    const svgNS = 'http://www.w3.org/2000/svg';
    const wrapper = document.createElement('div');
    wrapper.className = 'archive-sigil';
    wrapper.setAttribute('aria-hidden', 'true');
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 140 140');
    svg.setAttribute('fill', 'none');
    const circle = (cx, cy, r, opacity) => {
      const shape = document.createElementNS(svgNS, 'circle');
      shape.setAttribute('cx', String(cx));
      shape.setAttribute('cy', String(cy));
      shape.setAttribute('r', String(r));
      shape.setAttribute('stroke', '#9bc8f5');
      shape.setAttribute('stroke-width', '1.1');
      shape.setAttribute('opacity', String(opacity));
      svg.appendChild(shape);
    };
    circle(70, 70, 56, .45);
    circle(70, 70, 35, .55);
    circle(70, 70, 14, .42);
    for (let i = 0; i < 6; i++) {
      const angle = (i / 6) * Math.PI * 2 + (seed % 360) * Math.PI / 180;
      const radius = 25 + ((seed >>> (i * 4)) % 30);
      const cx = 70 + Math.cos(angle) * radius;
      const cy = 70 + Math.sin(angle) * radius;
      circle(cx.toFixed(2), cy.toFixed(2), i % 2 ? 2.4 : 3.5, .8);
    }
    const curve = document.createElementNS(svgNS, 'path');
    const shift = 22 + seed % 43;
    curve.setAttribute('d', 'M15 95 Q45 ' + shift + ' 68 70 T125 40');
    curve.setAttribute('stroke', '#abd9ff');
    curve.setAttribute('stroke-width', '1.4');
    curve.setAttribute('opacity', '.8');
    svg.appendChild(curve);
    wrapper.appendChild(svg);
    return wrapper;
  }

  function copyButton(card) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'archive-copy';
    button.setAttribute('aria-label', 'Copy link to ' + (card.querySelector('h2')?.textContent || 'project'));
    button.setAttribute('title', 'Copy project link');
    button.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>';
    button.addEventListener('click', async () => {
      const link = new URL('/projects/#' + encodeURIComponent(card.id), location.origin).href;
      let copied = false;
      try {
        if (navigator.clipboard?.writeText) {
          await navigator.clipboard.writeText(link);
          copied = true;
        } else {
          const input = document.createElement('textarea');
          input.value = link;
          input.style.cssText = 'position:fixed;left:-9999px;top:0';
          document.body.append(input);
          input.select();
          copied = document.execCommand('copy');
          input.remove();
        }
      } catch (_) { copied = false; }
      button.dataset.state = copied ? 'success' : 'failure';
      button.title = copied ? 'Link copied' : 'Could not copy link';
      const original = card.querySelector('h2')?.textContent || 'project';
      button.setAttribute('aria-label', copied ? 'Link copied for ' + original : 'Copy unavailable for ' + original);
      setTimeout(() => { if (button.isConnected) {
        button.removeAttribute('data-state');
        button.title = 'Copy project link';
        button.setAttribute('aria-label', 'Copy link to ' + original);
      } }, 1800);
    });
    return button;
  }

  function applyFilters() {
    state.query = search.value.trim();
    state.source = source.value;
    api.setFilters(state);
    topicButtons.forEach(button => {
      const selected = button.dataset.archiveTopic === state.topic;
      button.setAttribute('aria-pressed', String(selected));
    });
    categoryButtons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.archiveCategory === state.category));
    });
    updateCount();
  }

  function updateCount() {
    const visible = api.count();
    const total = api.total();
    count.textContent = visible + ' of ' + total + ' projects';
  }

  function decorateCards() {
    if (!container) return;
    archive.classList.add('archive-enhanced');
    container.querySelectorAll('.project').forEach((card, i) => {
      if (!card.querySelector('.archive-sigil')) {
        const heading = card.querySelector('h2')?.textContent || 'project';
        card.appendChild(window.PortfolioProjectSymbols
          ? window.PortfolioProjectSymbols.create(card.id, heading, 'archive')
          : signature(card.id));
      }
      if (!card.querySelector('.archive-copy')) card.appendChild(copyButton(card));
      card.querySelectorAll('.tag:not(.archive-tag)').forEach(tag => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'archive-tag';
        button.textContent = tag.textContent;
        button.title = 'Find projects tagged ' + tag.textContent;
        button.setAttribute('aria-label', 'Filter projects by ' + tag.textContent);
        button.addEventListener('click', () => {
          state.topic = 'all';
          state.category = 'all';
          state.source = 'all';
          source.value = 'all';
          search.value = button.textContent.trim();
          applyFilters();
          explorer.scrollIntoView({ behavior: motionOK() ? 'smooth' : 'auto', block: 'start' });
          search.focus({ preventScroll: true });
        });
        tag.replaceWith(button);
      });
      if (motionOK() && revealObserver) {
        card.style.setProperty('--archive-delay', Math.min(3, i) * 65 + 'ms');
        card.setAttribute('data-archive-enter', 'pending');
        revealObserver.observe(card);
      } else card.setAttribute('data-archive-enter', 'shown');
    });
    updateCount();
    scheduleScroll();
  }

  function pointerGlow(event) {
    if (!motionOK() || !fine.matches || event.pointerType === 'touch') return;
    const card = event.target.closest?.('.project');
    if (!card) return;
    const bounds = card.getBoundingClientRect();
    card.style.setProperty('--archive-x', (event.clientX - bounds.left).toFixed(0) + 'px');
    card.style.setProperty('--archive-y', (event.clientY - bounds.top).toFixed(0) + 'px');
  }

  // One delegated pointer handler continues working after pagination and filtering.
  // Do not paint broad pointer glows; the independent dot background still brightens.
  search.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(applyFilters, 120);
  });
  search.addEventListener('search', () => {
    clearTimeout(debounce);
    applyFilters();
  });
  source.addEventListener('change', applyFilters);
  categoryButtons.forEach(button => button.addEventListener('click', () => {
    state.category = button.dataset.archiveCategory;
    applyFilters();
  }));
  topicButtons.forEach(button => button.addEventListener('click', () => {
    state.topic = button.dataset.archiveTopic;
    applyFilters();
  }));
  reset.addEventListener('click', () => {
    clearTimeout(debounce);
    search.value = '';
    source.value = 'all';
    state.topic = 'all';
    state.category = 'all';
    applyFilters();
    search.focus({ preventScroll: true });
  });
  document.addEventListener('keydown', event => {
    const editing = event.target.matches?.('input, textarea, select, [contenteditable="true"]');
    if (event.key === '/' && !editing && !event.metaKey && !event.ctrlKey && !event.altKey) {
      event.preventDefault();
      explorer.scrollIntoView({ behavior: motionOK() ? 'smooth' : 'auto', block: 'nearest' });
      search.focus({ preventScroll: true });
    }
    if (event.key === 'Escape' && document.activeElement === search) {
      if (search.value) { search.value = ''; applyFilters(); }
      else search.blur();
    }
  });

  // The global interaction hub owns the single accessible Back to top button.
  // Keep this archive's chapter tracker, without introducing a second control.

  function updateScroll() {
    paintQueued = false;
    const cards = [...container.querySelectorAll('.project')];
    if (!cards.length) {
      chapter.textContent = '00 / ' + String(api.count()).padStart(2, '0');
      return;
    }
    let current = 1;
    const center = innerHeight * .47;
    cards.forEach((card, i) => {
      if (card.getBoundingClientRect().top <= center) current = i + 1;
    });
    const offset = (api.currentPage() - 1) * api.perPage();
    chapter.textContent = String(offset + current).padStart(2, '0') +
      ' / ' + String(api.count()).padStart(2, '0');
  }
  function scheduleScroll() {
    if (paintQueued) return;
    paintQueued = true;
    requestAnimationFrame(updateScroll);
  }

  addEventListener('scroll', scheduleScroll, { passive: true });
  addEventListener('resize', scheduleScroll, { passive: true });
  addEventListener('portfolio:archive-rendered', decorateCards);
  addEventListener('portfolio:archive-reset', () => {
    search.value = '';
    source.value = 'all';
    state.query = '';
    state.source = 'all';
    state.topic = 'all';
    state.category = 'all';
    topicButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.archiveTopic === 'all')));
    categoryButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.archiveCategory === 'all')));
    updateCount();
  });
  reduced.addEventListener?.('change', () => {
    if (reduced.matches) container.querySelectorAll('.project').forEach(card => card.setAttribute('data-archive-enter', 'shown'));
  });
  explorer.hidden = false;
  decorateCards();
})();
