/* Site-wide GitHub and Hugging Face identity, including generated project cards. */
(() => {
  'use strict';
  const githubPath = 'M12 .297a12 12 0 0 0-3.793 23.385c.6.111.82-.261.82-.577v-2.234c-3.338.727-4.043-1.416-4.043-1.416-.546-1.387-1.334-1.756-1.334-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.108-.774.419-1.304.762-1.603-2.665-.303-5.467-1.334-5.467-5.93 0-1.31.469-2.381 1.236-3.221-.124-.303-.536-1.524.118-3.176 0 0 1.008-.323 3.3 1.23a11.48 11.48 0 0 1 6.006 0c2.291-1.553 3.297-1.23 3.297-1.23.656 1.652.244 2.873.12 3.176.77.84 1.235 1.911 1.235 3.221 0 4.608-2.807 5.624-5.48 5.921.43.373.823 1.102.823 2.222v3.293c0 .32.216.694.825.576A12.001 12.001 0 0 0 12 .297Z';

  function platform(link) {
    try {
      const host = new URL(link.href, location.href).hostname.toLowerCase();
      if (host === 'github.com' || host === 'www.github.com') return 'github';
      if (host === 'huggingface.co' || host === 'www.huggingface.co') return 'huggingface';
    } catch (_) {}
    return null;
  }
  function decorate(link) {
    const type = platform(link);
    if (!type || link.querySelector('[data-brand-icon]')) return;
    const icon = type === 'github'
      ? document.createElementNS('http://www.w3.org/2000/svg', 'svg')
      : document.createElement('span');
    icon.classList.add('brand-link-icon');
    icon.setAttribute('data-brand-icon', type);
    icon.setAttribute('aria-hidden', 'true');
    if (type === 'github') {
      icon.setAttribute('viewBox', '0 0 24 24');
      icon.setAttribute('focusable', 'false');
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', githubPath);
      path.setAttribute('fill', 'currentColor');
      icon.appendChild(path);
    } else {
      // The hugging-face emoji is the service's distinctive logo.
      icon.textContent = '🤗';
      icon.classList.add('brand-hf');
    }
    // On full-card links keep the logo near the card heading rather than in the layout flow.
    const heading = link.matches('.surface-card') ? link.querySelector('h3, h2') : null;
    if (heading) heading.prepend(icon);
    else link.prepend(icon);
    link.dataset.platform = type;
  }
  function decorateTree(root) {
    if (root.nodeType !== 1) return;
    if (root.matches?.('a[href]')) decorate(root);
    root.querySelectorAll?.('a[href]').forEach(decorate);
  }
  function start() {
    decorateTree(document.body);
    if (!('MutationObserver' in window)) return;
    new MutationObserver(records => {
      for (const entry of records) {
        for (const node of entry.addedNodes) decorateTree(node);
      }
    }).observe(document.body, {childList: true, subtree: true});
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, {once:true});
  } else start();
})();
