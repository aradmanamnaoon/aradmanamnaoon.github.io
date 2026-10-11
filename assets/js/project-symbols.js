/* Distinct, deterministic and accessible project glyphs.
   Project additions automatically receive an ID-seeded glyph without editing HTML. */
(function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const paths = {
    'persian-lm-from-scratch': {
      name: 'Language token lattice',
      markup: '<g class="symbol-orbit"><circle cx="70" cy="70" r="51" stroke-dasharray="2 9"/><circle cx="70" cy="70" r="39" stroke-dasharray="20 10"/></g><g class="symbol-draw"><path d="M43 54h54M43 70h54M43 86h33"/><path d="M53 43v54M87 43v33"/></g><circle class="symbol-core" cx="88" cy="86" r="9"/>'
    },
    'medical-image-segmentation': {
      name: 'Cardiac MRI slices',
      markup: '<g class="symbol-orbit"><ellipse cx="70" cy="70" rx="55" ry="21" transform="rotate(-25 70 70)"/><ellipse cx="70" cy="70" rx="55" ry="21" transform="rotate(25 70 70)"/></g><g class="symbol-draw"><path d="M34 76h16l9-21 14 35 12-22 7 8h16"/><path d="M53 43c-18 2-27 22-12 41l29 28 29-28c15-19 6-39-12-41-8-1-14 3-17 9-3-6-9-10-17-9Z"/></g><circle class="symbol-core" cx="70" cy="70" r="4"/>'
    },
    'ai-research-assistant-platform': {
      name: 'Research agent network',
      markup: '<g class="symbol-draw"><path d="M70 29 34 53 43 100 90 110 113 65 70 29ZM34 53 89 63 43 100M89 63 90 110 113 65M70 29 89 63"/></g><g class="symbol-nodes"><circle cx="70" cy="29" r="6"/><circle cx="34" cy="53" r="5"/><circle cx="43" cy="100" r="6"/><circle cx="90" cy="110" r="5"/><circle cx="113" cy="65" r="6"/></g><circle class="symbol-core" cx="89" cy="63" r="9"/>'
    },
    'cohortseal': {
      name: 'Patient cohort shield',
      markup: '<g class="symbol-draw"><path d="m70 18 42 17v32c0 30-16 44-42 55-26-11-42-25-42-55V35Z"/><path d="M49 59h42M49 71h42M49 83h29M70 44v54"/></g><g class="symbol-nodes"><circle cx="49" cy="59" r="4"/><circle cx="91" cy="71" r="4"/><circle cx="78" cy="83" r="4"/></g>'
    },
    'holdout-ledger': {
      name: 'Data split ledger',
      markup: '<g class="symbol-draw"><rect x="26" y="24" width="88" height="92" rx="8"/><path d="M43 44h54M43 61h54M43 78h54M43 95h54M60 35v72M78 35v72"/></g><g class="symbol-nodes"><circle cx="51" cy="52" r="4"/><circle cx="69" cy="69" r="4"/><circle cx="87" cy="86" r="4"/></g><path class="symbol-pulse" d="m87 105 9-9 7 7 13-17"/>'
    },
    'agent-guardrails': {
      name: 'Five-stage agent guardrails',
      markup: '<g class="symbol-orbit"><path d="m70 13 54 39-20 64H36L16 52Z"/></g><g class="symbol-draw"><path d="m70 32 35 24-13 43H48L35 56Z"/><path d="m70 32 0 48-22 19M70 80l22 19M70 80l35-24M70 80 35 56"/></g><circle class="symbol-core" cx="70" cy="80" r="10"/>'
    },
    'jibay2-medical-v2': {
      name: 'Clinical notes',
      markup: '<g class="symbol-draw"><path d="M42 22h48l19 20v77H42Z"/><path d="M90 22v22h19M56 64h39M56 81h39M56 98h17"/><path d="M72 36v21M61.5 46.5h21"/></g><circle class="symbol-core" cx="93" cy="97" r="11"/>'
    },
    'messy2json-qwen-0.5b': {
      name: 'Text-to-JSON transformation',
      markup: '<g class="symbol-draw"><path d="M47 29c-13 0-14 10-14 21v8c0 8-4 11-11 12 7 1 11 4 11 12v8c0 11 1 21 14 21M93 29c13 0 14 10 14 21v8c0 8 4 11 11 12-7 1-11 4-11 12v8c0 11-1 21-14 21"/><path d="M53 51h34M53 71h25M53 91h34"/></g><circle class="symbol-core" cx="83" cy="71" r="4"/>'
    },
    'persian-wikipedia-cleaned-for-persian-NLP': {
      name: 'Persian corpus archive',
      markup: '<g class="symbol-draw"><path d="M69 37c-16-11-34-11-49-4v75c16-7 34-7 49 4 17-11 35-11 51-4V33c-16-7-34-7-51 4Z"/><path d="M69 37v75M32 52c10-3 19-2 28 4M32 70c10-3 19-2 28 4M80 56c9-6 18-6 28-3M80 76c9-6 18-6 28-3"/></g><circle class="symbol-core" cx="69" cy="24" r="4"/>'
    },
    'nllb-en-fa-psych-translation': {
      name: 'Bilingual psychology bridge',
      markup: '<g class="symbol-draw"><path d="M17 62c10-21 24-30 45-24l16 8M123 78c-10 21-24 30-45 24l-16-8"/><path d="M43 83c7-13 16-19 27-19 12 0 21 8 28 20M43 52h24M55 52v34M78 52l18 34M78 86l18-34"/></g><g class="symbol-nodes"><circle cx="25" cy="52" r="5"/><circle cx="115" cy="88" r="5"/></g><circle class="symbol-core" cx="70" cy="70" r="7"/>'
    }
  };

  function seedFor(id) {
    let result = 2166136261;
    for (let i = 0; i < id.length; i++) {
      result = Math.imul(result ^ id.charCodeAt(i), 16777619);
    }
    return result >>> 0;
  }
  function fallback(id) {
    const seed = seedFor(id);
    const count = 4 + seed % 6;
    const points = [];
    const dots = [];
    for (let i = 0; i < count; i++) {
      const angle = Math.PI * 2 * (i / count) + ((seed >>> 9) % 360) * Math.PI / 180;
      const radius = 27 + ((seed >>> ((i * 3) % 24)) % 26);
      const x = (70 + Math.cos(angle) * radius).toFixed(2);
      const y = (70 + Math.sin(angle) * radius).toFixed(2);
      points.push(x + ',' + y);
      dots.push('<circle cx="' + x + '" cy="' + y + '" r="' + (i % 2 ? 3 : 5) + '"/>');
    }
    return {
      name: 'Project-specific procedural geometry',
      markup: '<g class="symbol-draw"><polygon points="' + points.join(' ') + '"/><path d="M' + points.filter((_,i) => i % 2 === 0).join('L') + 'Z"/></g><g class="symbol-nodes">' + dots.join('') + '</g><circle class="symbol-core" cx="70" cy="70" r="' + (6 + seed % 7) + '"/>'
    };
  }

  function create(projectId, projectTitle, kind) {
    const definition = paths[projectId] || fallback(projectId);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = kind === 'home' ? 'home-project-symbol project-symbol' : 'archive-sigil project-symbol';
    button.dataset.projectSymbol = projectId;
    button.dataset.symbolName = definition.name;
    button.setAttribute('aria-label', 'Animate ' + definition.name + ' for ' + projectTitle);
    button.setAttribute('title', 'Animate project symbol');
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 140 140');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    // Only authored constants or deterministic numbers go into the SVG markup.
    svg.innerHTML = definition.markup;
    button.appendChild(svg);
    button.addEventListener('click', () => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      button.classList.remove('symbol-play');
      void button.offsetWidth;
      button.classList.add('symbol-play');
    });
    button.addEventListener('animationend', e => {
      if (e.target === svg || e.target.classList.contains('symbol-draw')) button.classList.remove('symbol-play');
    });
    return button;
  }

  window.PortfolioProjectSymbols = Object.freeze({ create, seedFor });

  // Decorate featured work only, never replace its existing content/links.
  function decorateHomepage() {
    document.querySelectorAll('.projects-grid article.project-card[id]').forEach(card => {
      if (card.querySelector('.project-symbol')) return;
      card.appendChild(create(card.id, card.querySelector('h3')?.textContent || 'project', 'home'));
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', decorateHomepage, { once: true });
  } else decorateHomepage();
})();
