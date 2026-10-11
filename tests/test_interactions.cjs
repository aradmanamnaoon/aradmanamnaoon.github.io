/* Regression coverage for route registration, accessibility and interactions. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const test=require('node:test');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const pages=[
 'index.html','projects/index.html','skills/index.html','search/index.html',
 'projects/3d-cardiac-mri-segmentation/index.html',
 'projects/multi-agent-ai-research-assistant/index.html',
 'projects/persian-gpt-from-scratch/index.html',
 '404.html','offline.html','research/index.html'
];
test('all existing routes load reusable CSS and JavaScript without changing content',()=>{
 for(const page of pages){
   const source=read(page);
   assert.match(source,/assets\/css\/interaction-hub\.css\?v=/,page);
   assert.match(source,/assets\/css\/page-extras\.css\?v=/,page);
   assert.match(source,/assets\/js\/interaction-hub\.js\?v=/,page);
   assert.match(source,/assets\/js\/page-extras\.js\?v=/,page);
   assert.match(source,/animations\.js\?v=/,page);
   assert.match(source,/assets\/js\/brand-icons\.js\?v=/,page);
 }
 assert.match(read('research/index.html'),/canonical" href="https:\/\/aradmanamnaoon\.github\.io\/projects\/"/);
});

test('all new JS bundles parse as standalone vanilla JavaScript',()=>{
 for(const file of ['assets/js/interaction-hub.js','assets/js/page-extras.js','assets/js/search.js']) {
   assert.doesNotThrow(()=>new Function(read(file)),file);
   assert.doesNotMatch(read(file),/on(click|submit)\s*=/);
 }
});

test('global interaction hub supports modal navigation, themes, preference persistence and toast',()=>{
 const hub=read('assets/js/interaction-hub.js');
 for(const feature of [
  'Command palette','Keyboard shortcuts','hub-command-search','prefers-reduced-motion',
  'localStorage','dark', 'light','system','aria-selected','aria-live',
  'requestAnimationFrame','navigator.clipboard',
  'site-toasts','hub-back-top','contact-form-status','celebrate()'
 ]) assert.ok(hub.includes(feature),feature);
 assert.match(hub,/e\.metaKey \|\| e\.ctrlKey/);
 assert.match(hub,/palette\.showModal/);
 assert.match(hub,/beforeDialog.*focus/);
 assert.match(hub,/navigator\.clipboard\.writeText/);
 assert.doesNotMatch(hub,/hub-cursor|follower\.style\.transform/);
 assert.doesNotMatch(hub,/AudioContext|oscillator|soundCycle|testSound|hub-sound|hub-test-sound/);
 assert.match(hub,/Cycle theme/);
 assert.match(hub,/\.hub-rail-state/);
});

test('mobile and accessibility fallbacks are intentional',()=>{
 const css=read('assets/css/interaction-hub.css');
 assert.match(css,/@media \(max-width:760px\)/);
 assert.match(css,/@media \(max-width:760px\), \(pointer:coarse\)/);
 assert.match(css,/@media\s*\(prefers-reduced-motion:reduce\)/);
 assert.match(css,/data-theme="light"/);
 assert.match(css,/\.hub-dialog::backdrop/);
 assert.match(css,/\.hub-ring-progress/);
 const extras=read('assets/css/page-extras.css');
 assert.match(extras,/@media\(max-width:720px\)/);
 assert.match(extras,/@media print/);
 assert.match(extras,/prefers-reduced-motion:reduce/);
});

test('portfolio selection remains and Skills pin/copy controls are retired',()=>{
 const projects=read('projects/index.html');
 assert.match(projects,/all: function\(\) \{ return projects\.slice\(\); \}/);
 assert.match(projects,/portfolio:archive-rendered/);
 assert.match(projects,/window\.portfolioArchive/);
 const extras=read('assets/js/page-extras.js');
 for(const name of ['Saved projects','Compare:','project-compare-grid','localStorage',
  'case-interactive-toc','case-collapse','Print case study',
  'research','Psychology & statistics','aria-expanded','offline-status'])
   assert.ok(extras.includes(name),name);
 assert.doesNotMatch(extras,/function skills\(\)|pin-skill|copy-skill|Pinned skills:|Copy skills/);
 assert.match(read('scripts/build_site.py'),/all: function\(\) \{ return projects\.slice\(\); \}/);
});

test('case-study and utility generators retain new scripts across future builds',()=>{
 for(const file of ['scripts/project_pages.py','scripts/utility_pages.py']){
  const text=read(file);
  assert.ok(text.includes('interaction-hub.js?v='),file);
  assert.ok(text.includes('page-extras.js?v='),file);
  assert.ok(text.includes('interaction-hub.css?v='),file);
 }
});

test('live portfolio search debounces input, updates history and never injects result HTML',()=>{
 const source=read('assets/js/search.js');
 assert.match(source,/setTimeout\(\(\)=>run\(input\.value\),220\)/);
 assert.match(source,/history\.replaceState/);
 assert.match(source,/localStorage/);
 assert.match(source,/query\.trim\(\)\.slice\(0,120\)/);
 assert.match(source,/link\.append\(title,summary\)/);
 assert.match(source,/new URLSearchParams/);
 assert.match(source,/search-skeleton/);
 assert.match(source,/recent\.splice\(0\)/);
 assert.match(read('search/index.html'),/assets\/js\/search\.js/);
});


test('light theme tokens, legible surfaces and cache versions cover every route', () => {
  const css = read('assets/css/interaction-hub.css');
  for (const name of [
    '--color-text: #192c40', '--color-muted: #435c73',
    '--ink: #192c40', '--ux-ink: #192c40', '--surface: #f3f6fa',
    '--color-bg-raised: #fff', 'color-scheme: light',
    '.project-case-study .case-section :is(p,li)',
    '.hub-dialog', '.archive .project', '.skills-explorer',
    '.interaction-rail', 'body::before'
  ]) assert.ok(css.includes(name), name);
  assert.doesNotMatch(css, /html\[data-theme="light"\] :is\(h1,h2,h3,h4,p,li,strong/);
  const routes = [
    'index.html','projects/index.html','skills/index.html',
    'search/index.html','404.html','offline.html','research/index.html',
    'projects/3d-cardiac-mri-segmentation/index.html',
    'projects/multi-agent-ai-research-assistant/index.html',
    'projects/persian-gpt-from-scratch/index.html',
    'scripts/project_pages.py','scripts/utility_pages.py'
  ];
  for(const route of routes) {
    assert.match(read(route), /interaction-hub\.css\?v=20261011-dotlight-v6/, route);
  }
});
test('light palette reaches WCAG AA contrast for regular text and controls', () => {
  const rgb = hex => (hex.match(/[0-9a-f]{2}/gi) || []).map(part => {
    const channel = parseInt(part,16) / 255;
    return channel <= .04045 ? channel / 12.92 : Math.pow((channel + .055) / 1.055, 2.4);
  });
  const lum = hex => {
    const [r,g,b] = rgb(hex);
    return .2126 * r + .7152 * g + .0722 * b;
  };
  const contrast=(a,b)=>{
    const x=lum(a), y=lum(b);
    return (Math.max(x,y)+.05) / (Math.min(x,y)+.05);
  };
  for (const [foreground,background] of [
    ['#192c40','#f3f6fa'],['#192c40','#ffffff'],
    ['#435c73','#ffffff'],['#245f96','#ffffff'],
    ['#ffffff','#245f96']
  ]) assert.ok(contrast(foreground,background)>=4.5,
    'Contrast must be >= 4.5:1 for '+foreground+' on '+background);
});

test('only native cursor and smoothly fading dot illumination remain', () => {
  const css = read('assets/css/interaction-hub.css');
  const hub = read('assets/js/interaction-hub.js');
  const motion = read('assets/css/motion.css');
  assert.doesNotMatch(css,/\.hub-cursor\s*\{/);
  assert.doesNotMatch(hub,/createElement\('span'\); follower\.className/);
  assert.doesNotMatch(motion,/circle 230px at var\(--dot-pointer-x/);
  assert.match(motion,/circle 520px at var\(--dot-pointer-x/);
  assert.match(motion,/background-size: 30px 30px/);
  assert.match(motion,/transparent 100%/);
  assert.match(motion,/rgb\(218 241 255 \/ 1\)/);
  assert.match(motion,/rgb\(0 0 0 \/ \.94\) 10%/);
  assert.match(css,/body\.dots-active:not\(\.motion-disabled\)::after \{ opacity: 1; \}/);
  assert.match(css,/rgb\(23 105 169 \/ \.96\)/);
});

test('desktop Back to top does not overlap the CV assistant launcher', () => {
  const css=read('assets/css/interaction-hub.css');
  assert.match(css, /Desktop floating controls occupy distinct regions/);
  assert.ok(css.includes('.hub-back-top { left:18px; right:auto; bottom:84px; }'));
});

test('mobile dock has 3 spaced controls with visible theme state and no audio remnants', () => {
  const hub = read('assets/js/interaction-hub.js');
  const css = read('assets/css/interaction-hub.css');
  const pkg = read('package.json');
  assert.match(css,/grid-template-columns:repeat\(3,minmax\(0,1fr\)\)/);
  assert.match(css,/\.interaction-rail button \{ display:inline-flex/);
  assert.match(css,/gap:\.55rem/);
  assert.match(css,/\.hub-rail-state \{display:inline-block/);
  assert.match(hub,/hub-theme/);
  assert.match(hub,/hub-shortcuts/);
  assert.doesNotMatch(hub,/id="hub-sound"|id="hub-test-sound"/);
  assert.doesNotMatch(css,/hub-test-sound|hub-sound/);
  assert.doesNotMatch(pkg,/test_sound\.cjs/);
});

test('desktop CV assistant supports keyboard control and clear Back-to-top placement',()=>{
  const page=read('index.html'), js=read('assets/js/cv-chat-ui.js'), css=read('assets/css/interaction-hub.css');
  for(const token of ['aria-label="AI CV assistant"','role="log" aria-live="polite"','role="status" aria-live="polite"']) assert.ok(page.includes(token),token);
  for(const token of ['function closeChat()','event.key === "Escape"','lastLauncher.focus({ preventScroll: true })','button.setAttribute("aria-expanded", "false")']) assert.ok(js.includes(token),token);
  assert.ok(css.includes('body:has(#cv-chat-floating) .hub-back-top'));
  assert.ok(css.includes('body:has(#cv-chat-window[aria-hidden="false"]) .hub-back-top'));
});
