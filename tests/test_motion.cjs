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

test('resuming a saved pause initializes pointer motion on a fine pointer', () => {
  const nodes = [];
  const html = { classList: classes(), scrollHeight: 1200 };
  const nav = { append(node) { nodes.push(node); } };
  const document = {
    readyState: 'complete', documentElement: html,
    body: { append: node => nodes.push(node), classList: classes() },
    querySelector: selector => selector.includes('Primary navigation') ? nav : null,
    querySelectorAll: () => [],
    createElement: tag => ({ tag, className: '', style: {}, classList: classes(),
      setAttribute() {}, addEventListener(type, callback) { this[type] = callback; },
      getContext: () => null }),
    addEventListener() {},
  };
  const context = {
    document, window: { onpageswap: null }, navigator: {},
    matchMedia: query => ({ matches: query.includes('pointer: fine'), addEventListener() {} }),
    localStorage: { getItem: () => 'true', setItem() {} }, sessionStorage: {},
    addEventListener() {}, innerHeight: 800, innerWidth: 1200, scrollY: 0,
    requestAnimationFrame() {}, performance: { now: () => 0 },
  };
  vm.runInNewContext(source, context);
  assert.ok(html.classList.contains('motion-off'));
  const toggle = nodes.find(node => node.className === 'motion-toggle');
  toggle.click();
  assert.ok(!html.classList.contains('motion-off'));
  assert.ok(nodes.some(node => node.className === 'motion-cursor'));
  assert.ok(html.classList.contains('motion-pointer'));
});
