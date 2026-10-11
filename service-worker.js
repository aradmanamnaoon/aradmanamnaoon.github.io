/* Network-first pages; a small cached fallback for offline navigation. */
const CACHE = 'arad-portfolio-v12';
const CORE = [
  '/', '/projects/', '/skills/', '/search/',
  '/offline.html', '/dist/output.css', '/assets/css/ux.css', '/assets/css/motion.css',
  '/animations.js', '/assets/js/site-ui.js', '/assets/js/search.js', '/search-index.json',
  '/assets/js/projects-experience.js', '/assets/css/projects-experience.css',
  '/assets/js/project-symbols.js', '/assets/js/brand-icons.js', '/assets/js/skills-experience.js', '/assets/css/skills-experience.css',
  '/assets/js/interaction-hub.js', '/assets/css/interaction-hub.css',
  '/assets/js/page-extras.js', '/assets/css/page-extras.css'
];

self.addEventListener('install', function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) {
    return cache.addAll(CORE);
  }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (event) {
  event.waitUntil(Promise.all([
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (key) { return key !== CACHE; })
        .map(function (key) { return caches.delete(key); }));
    }),
    self.clients.claim()
  ]));
});
self.addEventListener('fetch', function (event) {
  const request = event.request;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || request.method !== 'GET') return;

  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).then(function (response) {
      if (response.ok) {
        const copy = response.clone();
        event.waitUntil(caches.open(CACHE).then(function (cache) {
          return cache.put(request, copy);
        }));
      }
      return response;
    }).catch(async function () {
      const cached = await caches.match(request, { ignoreSearch: true });
      if (cached) return cached;
      const offline = await caches.match('/offline.html');
      if (!offline) return Response.error();
      return new Response(await offline.text(), {
        status: 503, statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'text/html; charset=utf-8' }
      });
    }));
    return;
  }

  if (CORE.includes(url.pathname)) {
    event.respondWith(fetch(request).catch(function () {
      return caches.match(url.pathname);
    }));
  }
});
