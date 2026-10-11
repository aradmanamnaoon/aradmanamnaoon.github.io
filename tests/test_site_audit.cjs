'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT = path.join(__dirname, '..');
const BASE = 'https://aradmanamnaoon.github.io';
const read = name => fs.readFileSync(path.join(ROOT, name), 'utf8');
const ROUTES = [
  'index.html', 'projects/index.html', 'skills/index.html', 'search/index.html',
  'projects/3d-cardiac-mri-segmentation/index.html',
  'projects/persian-gpt-from-scratch/index.html',
  'projects/multi-agent-ai-research-assistant/index.html',
  'research/index.html', '404.html', 'offline.html'
];
const existingProjects = JSON.parse(read('projects.json')).map(project => project.id);

function pathForUrl(url) {
  const decoded = decodeURIComponent(url.pathname);
  const pathname = decoded.endsWith('/') ? decoded + 'index.html' : decoded;
  return pathname.slice(1) || 'index.html';
}

test('every route has one H1, unique IDs, and shared accessible controls', () => {
  for (const file of ROUTES) {
    const html = read(file);
    assert.equal((html.match(/<h1\b/g) || []).length, 1, file + ' H1');
    const ids = [...html.matchAll(/\bid=["']([^"']+)["']/g)].map(match => match[1]);
    assert.equal(new Set(ids).size, ids.length, file + ' duplicate ID');
    assert.match(html, /<html lang="en">/, file);
    assert.match(html, /<title>[\s\S]*?<\/title>/, file);
    assert.match(html, /class="skip-link"/, file);
    assert.match(html, /assets\/js\/interaction-hub\.js\?v=/, file);
    assert.match(html, /assets\/js\/page-extras\.js\?v=20261011-audit-v2/, file);
    assert.match(html, /assets\/css\/page-extras\.css\?v=20261011-audit-v2/, file);
  }
});

test('internal links, static assets, and fragment targets resolve', () => {
  const routeTexts = new Map(ROUTES.map(file => [file, read(file)]));
  for (const file of ROUTES) {
    const source = routeTexts.get(file);
    const base = new URL('/' + file, BASE);
    const refs = [
      ...source.matchAll(/\bhref=["']([^"']+)["']/g),
      ...source.matchAll(/<script\b[^>]*src=["']([^"']+)["']/g)
    ];
    for (const match of refs) {
      const value = match[1];
      if (value === '#' || /^(?:mailto:|tel:|data:|javascript:)/.test(value)) continue;
      const resolved = new URL(value, base);
      if (resolved.origin !== BASE) continue;
      const local = pathForUrl(resolved);
      assert.ok(fs.existsSync(path.join(ROOT,local)), file + ': missing ' + local);
      if (!resolved.hash) continue;
      const id = decodeURIComponent(resolved.hash.slice(1));
      const target = routeTexts.get(local);
      if (target && !existingProjects.includes(id)) {
        assert.ok(target.includes('id="' + id + '"') || target.includes("id='" + id + "'"),
          file + ': missing fragment ' + resolved.hash + ' in ' + local);
      }
    }
  }
});

test('selected theme is set before stylesheets, including generated pages', () => {
  const bootstrap = read('assets/js/theme-init.js');
  assert.doesNotThrow(() => new Function(bootstrap));
  for (const route of ROUTES) {
    const html = read(route);
    const scriptAt = html.indexOf('src="/assets/js/theme-init.js"');
    const cssAt = html.indexOf('rel="stylesheet"');
    assert.ok(scriptAt > 0 && scriptAt < cssAt, route + ': theme bootstrapping order');
  }
  for (const src of ['scripts/project_pages.py','scripts/utility_pages.py'])
    assert.match(read(src), /src="\/assets\/js\/theme-init\.js"/);
  for (const [saved,systemDark,expected] of [
    ['dark',false,'dark'],['light',true,'light'],
    ['system',false,'light'],['system',true,'dark']
  ]) {
    const document = {documentElement:{dataset:{}}};
    const storage = {getItem:()=>JSON.stringify({theme:saved})};
    vm.runInNewContext(bootstrap, {
      document,localStorage:storage,
      matchMedia:()=>({matches:systemDark})
    });
    assert.equal(document.documentElement.dataset.theme, expected);
    assert.equal(document.documentElement.dataset.themeSetting, saved);
  }
});

test('interactive project links recover pagination even for identical URL hashes', () => {
  const extras = read('assets/js/page-extras.js');
  const archive = read('projects/index.html');
  assert.match(extras,/location\.hash===fragment/);
  assert.match(extras,/dispatchEvent\(new Event\('hashchange'\)\)/);
  assert.match(extras,/dialog\.close\(\)/);
  assert.match(archive,/addEventListener\('hashchange'/);
  assert.match(archive,/portfolio:archive-reset/);
  assert.doesNotMatch(read('assets/js/projects-experience.js'),/className = 'archive-top'/);
  assert.match(read('assets/js/interaction-hub.js'),/className = 'hub-back-top'/);
});

test('Skills pinned links resolve to their real card after clearing filters', () => {
  const page=read('skills/index.html');
  const extras=read('assets/js/page-extras.js');
  assert.match(page,/id="libraries_and_tools"/);
  assert.ok(read('scripts/build_site.py').includes('id="libraries_and_tools"'));
  assert.match(extras,/document\.getElementById\('skills-clear'\)\?\.click\(\)/);
  assert.match(read('assets/js/skills-experience.js'),/searchCorpus\.get\(card\)\.includes\(query\)/);
  assert.match(extras,/validIds\.has\(id\)/);
  assert.match(extras,/getElementById\(id\)\?\.scrollIntoView/);
  assert.match(read('assets/css/page-extras.css'),/scroll-margin-top/);
});

test('saved selections and recent searches resist malformed localStorage', () => {
  const extras = read('assets/js/page-extras.js');
  const search = read('assets/js/search.js');
  assert.match(extras,/Array\.isArray\(value\)/);
  assert.match(extras,/typeof item==='string'/);
  assert.match(search,/Array\.isArray\(values\)/);
  assert.match(search,/typeof item==='string'/);
  assert.match(search,/\.slice\(0,4\)/);
  assert.match(search,/textContent=item\.entry\.summary/);
});

test('all patched local scripts parse and offline cache contains theme initializer', () => {
  for(const file of ['assets/js/page-extras.js','assets/js/search.js',
    'assets/js/projects-experience.js','assets/js/theme-init.js']){
    assert.doesNotThrow(()=>new Function(read(file)), file);
  }
  const worker=read('service-worker.js');
  assert.match(worker,/arad-portfolio-v13/);
  assert.match(worker,/\/assets\/js\/theme-init\.js/);
});
