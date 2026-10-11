/* Apply the persisted color preference before CSS paints.
   This file intentionally contains no UI controls or dependencies. */
(() => {
  'use strict';
  let mode = 'dark';
  try {
    const saved = JSON.parse(localStorage.getItem('arad-ui-preferences-v1') || '{}');
    if (['dark', 'light', 'system'].includes(saved?.theme)) mode = saved.theme;
  } catch (_) { /* Private browsing or disabled storage: use dark default. */ }
  const resolved = mode === 'system'
    ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : mode;
  document.documentElement.dataset.theme = resolved;
  document.documentElement.dataset.themeSetting = mode;
})();
