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

  // Semantic, individually authored illustrations: never reuse a generic
  // network/circuit icon across unrelated disciplines.
  const icons = {
    programming: ['Terminal and code', '<rect x="12" y="12" width="40" height="36" rx="5"/><path d="m22 23 8 7-8 7M34 38h10"/>'],
    mobile_development: ['Mobile application', '<rect x="19" y="7" width="29" height="46" rx="6"/><path d="M28 14h11M30 46h7"/><rect x="26" y="20" width="15" height="19" rx="2" class="skill-accent"/>'],
    classical_machine_learning: ['Decision tree', '<path d="M32 8v10M32 18 14 33M32 18l18 15M14 33v10M50 33v10"/><rect x="25" y="5" width="14" height="12" rx="3"/><rect x="5" y="43" width="18" height="12" rx="3"/><rect x="41" y="43" width="18" height="12" rx="3"/>'],
    deep_learning: ['Neural network layers', '<path d="M12 13 30 8 52 15M12 29 30 8M12 29l18 20M12 47 30 49M30 8 52 31M30 49l22-18M12 13l18 20M12 47l18-14M30 33 52 15M30 33l22-2"/><g class="skill-accent"><circle cx="12" cy="13" r="4"/><circle cx="12" cy="29" r="4"/><circle cx="12" cy="47" r="4"/><circle cx="30" cy="8" r="4"/><circle cx="30" cy="33" r="4"/><circle cx="30" cy="49" r="4"/><circle cx="52" cy="15" r="4"/><circle cx="52" cy="31" r="4"/></g>'],
    computer_vision: ['Computer vision aperture', '<circle cx="32" cy="30" r="24"/><circle cx="32" cy="30" r="8" class="skill-accent"/><path d="m17 11 9 12M47 11 35 22M55 32l-16 1M45 49 35 38M18 49l10-13M8 28l16 1"/>'],
    medical_imaging: ['Cardiac medical scan', '<path d="M7 30h10l7-12 8 26 9-17 5 5h11"/><path d="M20 10c-11 3-15 17-5 30l17 14 17-14c10-13 6-27-5-30-6-2-10 1-12 5-3-4-7-7-12-5Z" class="skill-accent"/>'],
    natural_language_processing: ['Language and translation', '<path d="M10 12h42v26H33l-11 11V38H10Z"/><path d="M19 22h25M19 29h17"/><path d="m44 43 6-6 6 6M50 37v13" class="skill-accent"/>'],
    llm_engineering: ['Transformer blocks', '<rect x="11" y="9" width="16" height="16" rx="3"/><rect x="38" y="9" width="16" height="16" rx="3"/><rect x="24" y="36" width="16" height="16" rx="3"/><path d="m19 25 13 11 14-11"/><path d="m14 13 9 9M41 13l9 9" class="skill-accent"/>'],
    rag: ['Retrieval of evidence', '<rect x="8" y="11" width="29" height="36" rx="3"/><path d="M15 20h15M15 27h10M15 34h8"/><circle cx="43" cy="39" r="10" class="skill-accent"/><path d="m50 46 9 9"/>'],
    agentic_ai: ['Agent planning and tool routing', '<rect x="4" y="19" width="17" height="19" rx="4"/><rect x="43" y="6" width="17" height="17" rx="4"/><rect x="43" y="41" width="17" height="17" rx="4"/><path d="M21 28h10M31 28V14h12M31 28v21h12"/><circle cx="12" cy="28" r="3" class="skill-accent"/>'],
    fine_tuning: ['Model parameter tuning', '<path d="M13 12v42M32 9v45M51 12v42"/><rect x="6" y="20" width="14" height="9" rx="3" class="skill-accent"/><rect x="25" y="39" width="14" height="9" rx="3" class="skill-accent"/><rect x="44" y="25" width="14" height="9" rx="3" class="skill-accent"/>'],
    statistics_and_humanities_data: ['Statistical distribution', '<path d="M7 49h51M9 47c11 0 11-35 23-35s12 35 25 35"/><path d="M32 12v37M18 37v12M46 37v12" stroke-dasharray="3 4"/><circle cx="32" cy="12" r="3" class="skill-accent"/>'],
    software_and_delivery: ['Software delivery pipeline', '<rect x="5" y="21" width="16" height="20" rx="3"/><path d="M21 31h10l-4-4M31 31l-4 4"/><rect x="32" y="13" width="27" height="36" rx="4"/><path d="M39 21h13M39 29h13M39 37h9"/><path d="m48 43 3 3 6-7" class="skill-accent"/>'],
    libraries_and_tools: ['Libraries and development tools', '<path d="M8 22h48v30H8Z"/><path d="M23 22v-8h18v8M8 31h48"/><path d="m25 38 7 6 7-6" class="skill-accent"/><path d="M32 31v13"/>']
  };

  const ns = 'http://www.w3.org/2000/svg';
  function graphic(card) {
    const key = card.id || 'libraries_and_tools';
    const [description, shapes] = icons[key] || ['Specialized technical methods',
      '<path d="M12 15h40v34H12Z"/><path d="m22 26 9 7-9 7M36 41h8"/>'];
    const button = document.createElement('button');
    button.className = 'skills-visual';
    button.type = 'button';
    button.dataset.skillIcon = key;
    button.setAttribute('aria-label', 'Animate ' + description);
    button.title = description + ' — animate icon';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox','0 0 64 64');
    svg.setAttribute('aria-hidden','true');
    svg.setAttribute('focusable','false');
    svg.innerHTML = '<g class="skill-trace">' + shapes + '</g>';
    button.appendChild(svg);
    button.addEventListener('click', () => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      button.classList.remove('is-playing');
      void button.offsetWidth;
      button.classList.add('is-playing');
    });
    button.addEventListener('animationend', () => button.classList.remove('is-playing'));
    card.appendChild(button);
  }
  cards.forEach(card => {
    if (!card.querySelector('.skills-visual')) graphic(card);
  });
  explorer.hidden = false;
  filter();
})();
