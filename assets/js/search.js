(function () {
  'use strict';
  const input = document.getElementById('site-search');
  const results = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  if (!input || !results || !status) return;

  const query = (new URLSearchParams(location.search).get('q') || '').trim().slice(0, 120);
  input.value = query;
  if (!query) return;
  const words = query.toLocaleLowerCase().split(/\s+/).filter(Boolean).slice(0, 8);
  status.textContent = 'Searching…';
  fetch('/search-index.json')
    .then(function (response) {
      if (!response.ok) throw new Error('Search index unavailable');
      return response.json();
    })
    .then(function (entries) {
      const matches = entries.map(function (entry) {
        const title = entry.title.toLocaleLowerCase();
        const terms = entry.terms.toLocaleLowerCase();
        const summary = entry.summary.toLocaleLowerCase();
        const score = words.reduce(function (total, word) {
          return total + (title.includes(word) ? 4 : 0) +
            (terms.includes(word) ? 2 : 0) + (summary.includes(word) ? 1 : 0);
        }, 0);
        return { entry: entry, score: score };
      }).filter(function (item) { return item.score > 0; })
        .sort(function (a, b) { return b.score - a.score; });
      status.textContent = matches.length
        ? matches.length + ' result' + (matches.length === 1 ? '' : 's') + ' for “' + query + '”.'
        : 'No results for “' + query + '”. Try a broader term such as medical imaging, Persian NLP, or statistics.';
      matches.forEach(function (item) {
        const link = document.createElement('a');
        link.className = 'utility-result';
        link.href = item.entry.url;
        const title = document.createElement('strong');
        title.textContent = item.entry.title;
        const summary = document.createElement('span');
        summary.textContent = item.entry.summary;
        link.append(title, summary);
        results.append(link);
      });
    })
    .catch(function () {
      status.textContent = 'Search is unavailable right now. Use the links below to browse the portfolio.';
    });
})();
