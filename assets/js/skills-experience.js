/* Progressive, mobile-first explorer for the complete Skills inventory. */
(function () {
  'use strict';
  const grid = document.getElementById('skills-directory');
  const explorer = document.getElementById('skills-explorer');
  if (!grid || !explorer) return;
  const cards = [...grid.querySelectorAll('.inventory-card')];
  const input = document.getElementById('skills-query');
  const count = document.getElementById('skills-count');
  const clear = document.getElementById('skills-clear');
  const chips = [...explorer.querySelectorAll('[data-skill-area]')];
  if (!input || !count || !clear || !chips.length) return;

  const groups = {
    all: null,
    medical: ['classical_machine_learning','deep_learning','computer_vision','medical_imaging'],
    humanities: ['statistics_and_humanities_data','classical_machine_learning','programming'],
    language: ['natural_language_processing','llm_engineering','rag','fine_tuning','agentic_ai'],
    engineering: ['software_and_delivery','programming','mobile_development','agentic_ai']
  };
  let area = 'all';
  let timer = 0;
  function filter() {
    const query = input.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      const groupOK = !groups[area] || groups[area].includes(card.id) || card.classList.contains('inventory-tools');
      const queryOK = !query || card.textContent.toLocaleLowerCase().includes(query);
      const show = groupOK && queryOK;
      card.hidden = !show;
      card.classList.toggle('skill-filtered-out', !show);
      if (show) visible += 1;
      // Respect already-applied progressive reveal styles after a filter reset.
      if (show && card.hasAttribute('data-reveal')) card.classList.add('is-revealed');
      card.querySelectorAll('.skill-list li').forEach(item => {
        item.classList.toggle('skill-hit', Boolean(query) && item.textContent.toLocaleLowerCase().includes(query));
      });
    }
    count.textContent = visible + ' of ' + cards.length + ' skill groups';
    chips.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.skillArea === area)));
    const existing = grid.querySelector('.skills-no-results');
    if (visible) existing?.remove();
    else if (!existing) {
      const message = document.createElement('p');
      message.className = 'skills-no-results';
      message.setAttribute('role', 'status');
      message.textContent = 'No matching skills. Try a broader term or reset the filters.';
      grid.appendChild(message);
    }
  }
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(filter, 100); });
  input.addEventListener('search', () => { clearTimeout(timer); filter(); });
  chips.forEach(button => button.addEventListener('click', () => { area = button.dataset.skillArea; filter(); }));
  clear.addEventListener('click', () => {
    clearTimeout(timer);
    input.value = '';
    area = 'all';
    filter();
    input.focus({ preventScroll:true });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.activeElement === input) {
      if (input.value) { input.value=''; filter(); } else input.blur();
    }
  });

  const ns = 'http://www.w3.org/2000/svg';
  function graphic(card, index) {
    // One compact procedural signal per skill card; the ID determines its shape.
    const type = /medical|imaging|computer_vision/.test(card.id) ? 'pulse'
      : /statistics|classical/.test(card.id) ? 'distribution'
      : /language|llm|rag|agentic|fine_tuning/.test(card.id) ? 'network' : 'circuit';
    const wrapper = document.createElement('button');
    wrapper.className = 'skills-visual';
    wrapper.type = 'button';
    wrapper.setAttribute('aria-label', 'Animate skill graphic for ' + (card.querySelector('h3')?.textContent || 'skill group'));
    wrapper.title = 'Animate the skill diagram';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox','0 0 130 56');
    svg.setAttribute('aria-hidden','true');
    svg.setAttribute('focusable','false');
    const points = Array.from({length:7},(_,i)=>[10+i*18,12+((index*11+i*7)%32)]);
    const path = (d, cls) => '<path class="'+cls+'" d="'+d+'"/>';
    const line = points.map(([x,y])=>x+','+y).join(' ');
    const content = type === 'pulse'
      ? path('M8 29h25l9-14 13 29 12-22 8 7h47','skill-trace')
      : type === 'distribution'
        ? '<path class="skill-trace" d="M9 47c26 0 26-38 56-38s30 38 56 38"/><path class="skill-guide" d="M65 9v40M9 47h112"/>'
        : type === 'network'
          ? '<polyline class="skill-trace" points="'+line+'"/>'+points.map(([x,y])=>'<circle class="skill-point" cx="'+x+'" cy="'+y+'" r="3.5"/>').join('')
          : path('M10 11h28v13h24v-8h33v28h25M10 44h26v-8h27v9h30','skill-trace');
    svg.innerHTML = '<path class="skill-guide" d="M0 54h130"/>'+content;
    wrapper.appendChild(svg);
    wrapper.addEventListener('click', () => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      wrapper.classList.remove('is-playing');
      void wrapper.offsetWidth;
      wrapper.classList.add('is-playing');
    });
    wrapper.addEventListener('animationend', () => wrapper.classList.remove('is-playing'));
    card.appendChild(wrapper);
  }
  cards.forEach((card,index)=>{
    if (!card.classList.contains('inventory-tools') && !card.querySelector('.skills-visual')) graphic(card,index);
  });
  explorer.hidden = false;
  filter();
})();
