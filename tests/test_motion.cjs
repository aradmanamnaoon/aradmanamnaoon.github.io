const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'animations.js'), 'utf8');

function classes() {
  const values = new Set();
  return {
    add: name => values.add(name),
    remove: name => values.delete(name),
    toggle(name, force) { if (force) values.add(name); else values.delete(name); },
    contains: name => values.has(name),
  };
}

test('system reduced motion leaves evidence readable and skips animated intro', () => {
  const elements = [];
  const evidence = { classList: classes() };
  const html = { classList: classes(), scrollHeight: 1200 };
  const document = {
    readyState: 'complete', documentElement: html,
    body: { append: item => elements.push(item), classList: classes() },
    querySelector: () => null,
    querySelectorAll: selector => selector === '[data-reveal="true"]' ? [evidence] : [],
    createElement: tag => ({ tag, className: '', style: {}, setAttribute() {}, getContext: () => null }),
    addEventListener() {},
  };
  const context = {
    document, window: { onpageswap: null }, navigator: {},
    matchMedia: query => ({ matches: query.includes('reduced-motion'), addEventListener() {} }),
    localStorage: { getItem: () => null }, sessionStorage: {},
    addEventListener() {}, innerHeight: 800, innerWidth: 1200, scrollY: 0,
    requestAnimationFrame() {}, performance: { now: () => 0 },
  };
  vm.runInNewContext(source, context);
  assert.ok(html.classList.contains('motion-off'));
  assert.ok(!html.classList.contains('motion-enabled'));
  assert.ok(evidence.classList.contains('is-revealed'));
  assert.ok(!elements.some(item => item.className === 'motion-intro'));
  assert.ok(!elements.some(item => item.tag === 'script'));
});

test('retired pause state is ignored and no motion button is created', () => {
  const nodes = [];
  const html = { classList: classes(), scrollHeight: 1200 };
  const nav = { append(node) { nodes.push(node); } };
  const document = {
    readyState: 'complete', documentElement: html,
    body: { append: node => nodes.push(node), classList: classes() },
    querySelector: selector => selector.includes('Primary navigation') ? nav : null,
    querySelectorAll: () => [],
    createElement: tag => ({
      tag, className: '', style: {}, classList: classes(),
      setAttribute() {}, addEventListener() {}, getContext: () => null,
    }),
    addEventListener() {},
  };
  const context = {
    document, window: { onpageswap: null }, navigator: {},
    matchMedia: query => ({ matches: query.includes('pointer: fine'), addEventListener() {} }),
    localStorage: { getItem: () => { throw Error('legacy preference must not be read'); } },
    sessionStorage: {
      getItem: key => key === 'arad-intro-seen' ? 'true' : null,
      setItem() {}, removeItem() {},
    },
    addEventListener() {}, innerHeight: 800, innerWidth: 1200, scrollY: 0,
    requestAnimationFrame() {}, performance: { now: () => 0 },
  };
  vm.runInNewContext(source, context);
  assert.ok(!html.classList.contains('motion-off'));
  assert.ok(!nodes.some(node => node.className === 'motion-toggle'));
  assert.ok(!nodes.some(node => node.className === 'motion-cursor'));
  assert.ok(!html.classList.contains('motion-pointer'));
});

// Regression checks for layered backgrounds and mobile-friendly story layout.
test('one dot grid, native cursor and viewport-wide desktop chapters', () => {
  const css = fs.readFileSync(path.join(__dirname, '..', 'assets/css/motion.css'), 'utf8');
  assert.ok(css.includes('body::before'));
  assert.ok(css.includes('background-size: 30px 30px'));
  assert.ok(css.includes('body::after'));
  assert.ok(css.includes('flex-basis: 100dvw'));
  assert.ok(css.includes('min-height: 100svh'));
  assert.ok(css.includes('@media (max-width: 899px)'));
  assert.ok(!css.includes('cursor: none'));
  assert.ok(!source.includes("createElement('canvas')"));
  assert.ok(!source.includes("createElement('div'); cursor.className"));
});

test('pause control and legacy CSS are removed while reduced motion remains', () => {
  const css = fs.readFileSync(path.join(__dirname, '..', 'assets/css/motion.css'), 'utf8');
  assert.ok(!source.includes('function control()'));
  assert.ok(!source.includes('arad-motion-paused'));
  assert.ok(!source.includes('Pause motion'));
  assert.match(css, /\.motion-toggle\s*\{\s*display:\s*none\s*!important/);
  assert.ok(source.includes("reduced.addEventListener?.('change', preference)"));
  assert.ok(source.includes("const enabled = () => !reduced.matches"));
});

test('active nav tracks visible homepage sections', () => {
  assert.ok(source.includes('function activeSections()'));
  assert.ok(source.includes("link.setAttribute('aria-current', 'location')"));
  assert.ok(source.includes('rootMargin'));
});

test('same-page section links use eased scrolling with native reduced-motion fallback', () => {
  assert.ok(source.includes('function sectionNavigation()'));
  assert.ok(source.includes('history.pushState(null'));
  assert.ok(source.includes("window.scrollTo({ top: start + distance * ease, behavior: 'instant' })"));
  assert.ok(source.includes('if (!enabled() || event.defaultPrevented')); 
  assert.ok(source.includes("window.scrollTo({ top: destination, behavior: 'instant' })"));
  assert.ok(source.includes('document.addEventListener(\'wheel\', stop'));
});
