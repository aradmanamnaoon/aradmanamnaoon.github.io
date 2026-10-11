const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'service-worker.js'), 'utf8');
const origin = 'https://aradmanamnaoon.github.io';

function workerWith(fetcher, cachedOffline) {
  const handlers = {};
  let precached = [];
  const cache = { put: async () => {}, addAll: async (items) => { precached = items; } };
  const context = {
    URL, Response, fetch: fetcher,
    caches: {
      open: async () => cache,
      match: async (request) => request === '/offline.html' ? cachedOffline : undefined,
      keys: async () => [], delete: async () => true,
    },
    self: {
      location: { origin },
      addEventListener: (name, handler) => { handlers[name] = handler; },
      skipWaiting: async () => {}, clients: { claim: async () => {} },
    },
  };
  vm.runInNewContext(source, context);
  return { fetchEvent: handlers.fetch, installEvent: handlers.install, precached: () => precached };
}

function dispatch(handler, url, method = 'GET', mode = 'navigate') {
  let response;
  const event = {
    request: { url, method, mode },
    respondWith(promise) { response = Promise.resolve(promise); },
    waitUntil() {},
  };
  handler(event);
  return response;
}

test('offline navigation returns branded content with 503', async () => {
  const { fetchEvent } = workerWith(
    async () => { throw new Error('offline'); },
    new Response('<h1>You are offline.</h1>', { status: 200 }),
  );
  const response = await dispatch(fetchEvent, origin + '/new-page/');
  assert.equal(response.status, 503);
  assert.match(await response.text(), /You are offline/);
});

test('server 404 is passed through and not replaced by offline content', async () => {
  const { fetchEvent } = workerWith(
    async () => new Response('Not found', { status: 404 }),
    new Response('Offline', { status: 200 }),
  );
  const response = await dispatch(fetchEvent, origin + '/missing/');
  assert.equal(response.status, 404);
});

test('cross-origin requests are not intercepted', () => {
  const { fetchEvent } = workerWith(async () => new Response('ok'), undefined);
  assert.equal(dispatch(fetchEvent, 'https://formspree.io/f/example', 'POST', 'cors'), undefined);
});

test('offline shell includes core motion and excludes the optional desktop scene', async () => {
  const worker = workerWith(async () => new Response('ok'), undefined);
  let installation;
  worker.installEvent({ waitUntil(promise) { installation = promise; } });
  await installation;
  assert.ok(worker.precached().includes('/animations.js'));
  assert.ok(worker.precached().includes('/assets/css/motion.css'));
  assert.ok(!worker.precached().includes('/assets/vendor/gsap.min.js'));
  assert.ok(!worker.precached().includes('/research/'));
  assert.ok(worker.precached().includes('/assets/js/projects-experience.js'));
  assert.ok(worker.precached().includes('/assets/css/projects-experience.css'));
  assert.ok(worker.precached().includes('/assets/js/project-symbols.js'));
  assert.ok(worker.precached().includes('/assets/js/brand-icons.js'));
  assert.ok(worker.precached().includes('/assets/js/skills-experience.js'));
  assert.ok(worker.precached().includes('/assets/css/skills-experience.css'));
});

test('updated worker cache supports versioned motion assets offline', () => {
  assert.match(source, /arad-portfolio-v7/);
  assert.ok(source.includes('caches.match(url.pathname)'));
  const home = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
  assert.ok(home.includes('animations.js?v=20261011-motion-exp-v7'));
  assert.ok(home.includes('motion.css?v=20261011-motion-exp-v7'));
});
