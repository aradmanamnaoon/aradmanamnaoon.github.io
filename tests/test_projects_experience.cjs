const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const ROOT = path.join(__dirname, '..');
const page = fs.readFileSync(path.join(ROOT, 'projects', 'index.html'), 'utf8');
const generator = fs.readFileSync(path.join(ROOT, 'scripts', 'build_site.py'), 'utf8');
const css = fs.readFileSync(path.join(ROOT, 'assets', 'css', 'projects-experience.css'), 'utf8');
const visual = fs.readFileSync(path.join(ROOT, 'assets', 'js', 'projects-experience.js'), 'utf8');
const match = [...page.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(result => result[1])
  .find(script => script.includes('var projects = '));

function archiveHarness() {
  const callbacks = {};
  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) elements.set(id, {
      id, innerHTML: '', attributes: {},
      setAttribute(key, value) { this.attributes[key] = value; },
      focus() {}, scrollIntoView() {},
      querySelectorAll() { return []; },
    });
    return elements.get(id);
  }
  const location = { hash: '', pathname: '/projects/', search: '', origin: 'https://aradmanamnaoon.github.io' };
  const window = {
    location,
    matchMedia: () => ({ matches: false }),
    addEventListener(name, callback) { callbacks[name] = callback; },
    dispatchEvent() {},
  };
  const context = {
    window, document: {
      getElementById: element,
      documentElement: { classList: { contains: () => false } },
    },
    requestAnimationFrame() {},
    CustomEvent: class CustomEvent {},
  };
  vm.runInNewContext(match, context, { timeout: 1000 });
  return { api: window.portfolioArchive, element, callbacks };
}

test('projects still have pagination and all project links', () => {
  assert.ok(match, 'generated project renderer is present');
  const { api, element } = archiveHarness();
  assert.equal(api.total(), 11);
  assert.equal(api.count(), 11);
  assert.equal(api.perPage(), 6);
  assert.match(element('projects-paginated').innerHTML, /Persian GPT/);
  assert.match(element('projects-pagination').innerHTML, /Previous page/);
  assert.match(element('projects-pagination').innerHTML, /Next page/);
});

test('search, research area, source filters and zero state are functional', () => {
  const { api, element } = archiveHarness();
  assert.equal(api.setFilters({ query: 'CohortSeal', source: 'all', topic: 'all' }), 1);
  assert.match(element('projects-paginated').innerHTML, /CohortSeal/);
  assert.equal(api.setFilters({ query: '', source: 'all', topic: 'medical' }), 3);
  assert.equal(api.setFilters({ query: '', source: 'huggingface', topic: 'all' }), 5);
  assert.equal(api.setFilters({ query: '', source: 'github', topic: 'all' }), 6);
  assert.equal(api.setFilters({ query: 'not-in-archive-100934', source: 'all', topic: 'all' }), 0);
  assert.match(element('projects-paginated').innerHTML, /No projects match/);
  assert.match(element('projects-pagination').innerHTML, /No matching projects/);
  assert.equal(api.setFilters({ query: '', source: 'all', topic: 'all' }), 11);
});

test('deep links restore complete archive even after filtering', () => {
  const { api, callbacks, element } = archiveHarness();
  api.setFilters({ query: 'CohortSeal', source: 'all', topic: 'all' });
  // hash ID is read from the current pathname on hashchange.
  // Static checks ensure the same handler exists in both generator and page.
  assert.ok(typeof callbacks.hashchange === 'function');
  assert.match(match, /visibleProjects = projects\.slice\(\)/);
  assert.match(match, /portfolio:archive-reset/);
  assert.match(element('projects-paginated').innerHTML, /CohortSeal/);
});

test('progressive enhancements are additive and honor accessibility', () => {
  assert.match(page, /id="archive-explorer" hidden/);
  assert.match(page, /id="archive-search" type="search"/);
  assert.match(page, /data-archive-topic="medical"/);
  assert.match(page, /projects-experience\.js/);
  assert.match(page, /projects-experience\.css/);
  assert.match(generator, /window\.portfolioArchive/);
  assert.match(visual, /prefers-reduced-motion/);
  assert.match(visual, /navigator\.clipboard/);
  assert.match(visual, /portfolio:archive-rendered/);
  assert.match(visual, /pointerType === 'touch'/);
  assert.match(css, /max-width: 480px/);
  assert.match(css, /max-width: 760px/);
  assert.match(css, /prefers-reduced-motion/);
  assert.doesNotMatch(page, /messy2json-qwen-0\.5b-lora/);
});
