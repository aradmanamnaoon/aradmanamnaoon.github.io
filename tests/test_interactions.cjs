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
  'requestAnimationFrame','audioContext','visibilitychange','navigator.clipboard',
  'site-toasts','hub-back-top','hub-cursor','contact-form-status','celebrate()'
 ]) assert.ok(hub.includes(feature),feature);
 assert.match(hub,/e\.metaKey \|\| e\.ctrlKey/);
 assert.match(hub,/palette\.showModal/);
 assert.match(hub,/beforeDialog.*focus/);
 assert.match(hub,/navigator\.clipboard\.writeText/);
 assert.match(hub,/pointerType==='touch'/);
});

test('mobile and accessibility fallbacks are intentional',()=>{
 const css=read('assets/css/interaction-hub.css');
 assert.match(css,/@media\(max-width:760px\)/);
 assert.match(css,/@media\s*\(hover:none\),\(pointer:coarse\)/);
 assert.match(css,/@media\s*\(prefers-reduced-motion:reduce\)/);
 assert.match(css,/data-theme="light"/);
 assert.match(css,/\.hub-dialog::backdrop/);
 assert.match(css,/\.hub-ring-progress/);
 const extras=read('assets/css/page-extras.css');
 assert.match(extras,/@media\(max-width:720px\)/);
 assert.match(extras,/@media print/);
 assert.match(extras,/prefers-reduced-motion:reduce/);
});

test('portfolio selection and Skills pinning work atop existing filters and pagination',()=>{
 const projects=read('projects/index.html');
 assert.match(projects,/all: function\(\) \{ return projects\.slice\(\); \}/);
 assert.match(projects,/portfolio:archive-rendered/);
 assert.match(projects,/window\.portfolioArchive/);
 const extras=read('assets/js/page-extras.js');
 for(const name of ['Saved projects','Compare:','project-compare-grid','localStorage',
  'Pin','Copy skills','case-interactive-toc','case-collapse','Print case study',
  'research','Psychology & statistics','aria-expanded','offline-status'])
   assert.ok(extras.includes(name),name);
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
