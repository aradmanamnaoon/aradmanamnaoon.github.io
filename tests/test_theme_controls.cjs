const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname,'..');
const read = p => fs.readFileSync(path.join(root,p),'utf8');
const source = read('assets/js/interaction-hub.js');

function mockNode(tag='div') {
  const nested = new Map();
  const events = new Map();
  const el = {
    tagName:tag.toUpperCase(),innerHTML:'',textContent:'',dataset:{},
    attributes:{},children:[],open:false,style:{setProperty(){}},
    classList:{add(){},remove(){},toggle(){},contains(){return false}},
    setAttribute(key,value){this.attributes[key]=value;},
    addEventListener(name,listener){events.set(name,listener);},
    dispatch(name){return events.get(name)?.();},
    append(...nodes){this.children.push(...nodes);},
    replaceChildren(...nodes){this.children=[...nodes];},
    querySelector(selector){
      if(!nested.has(selector))nested.set(selector,mockNode('button'));
      return nested.get(selector);
    },
    querySelectorAll(){return[];},
    focus(){},remove(){},
    showModal(){this.open=true;},
    close(){this.open=false;}
  };
  return el;
}

function harness({theme='system',dark=true,touch=true,legacyAudio=true}={}) {
  const body=mockNode('body');
  const html={dataset:{},scrollHeight:2600};
  const saved={theme};
  if(legacyAudio)saved.sound=true;
  const stored=[],queries={};
  const systemPreference={matches:dark,handlers:{}};
  const touchPreference={matches:touch,handlers:{}};
  const otherPreference={matches:false,handlers:{}};
  const media=query=> {
    const state=query.includes('prefers-color-scheme')?systemPreference:
      query.includes('max-width: 760px')?touchPreference:otherPreference;
    return {
      get matches(){return state.matches;},
      addEventListener(name,listener){state.handlers[name]=listener;}
    };
  };
  const document={
    body,documentElement:html,
    createElement:mockNode,
    getElementById(id) {
      const rail=body.children.find(el=>el.className==='interaction-rail');
      return rail?rail.querySelector('#'+id):null;
    },
    querySelectorAll(){return[];},
    querySelector(){return null;},
    addEventListener(){}
  };
  const window={};
  vm.runInNewContext(source,{
    document,window,matchMedia:media,
    localStorage:{
      getItem(){return JSON.stringify(saved);},
      setItem(key,value){stored.push({key,value:JSON.parse(value)});}
    },
    navigator:{clipboard:{writeText:async()=>{}}},
    location:{href:'https://aradmanamnaoon.github.io/'},
    addEventListener(){},requestAnimationFrame(){return 1;},
    setTimeout(){return 1;},innerHeight:800,scrollY:0
  },{timeout:1500});
  const rail=body.children.find(el=>el.className==='interaction-rail');
  return {rail,html,stored,window,body,systemPreference};
}

test('legacy audio preference is discarded while selected theme remains',()=>{
  const h=harness();
  assert.ok(h.rail);
  assert.equal(h.stored.length,1);
  assert.equal(h.stored[0].value.theme,'system');
  assert.deepEqual(Object.keys(h.stored[0].value),['theme']);
  assert.equal(h.html.dataset.theme,'dark');
  assert.equal(h.html.dataset.themeSetting,'system');
  assert.equal(h.rail.querySelector('#hub-theme').querySelector('.hub-rail-state').textContent,'System');
});

test('theme button cycles System → Dark → Light → System with readable labels',()=>{
  const h=harness();
  const button=h.rail.querySelector('#hub-theme');
  assert.match(h.rail.innerHTML,/hub-commands/);
  assert.match(h.rail.innerHTML,/hub-shortcuts/);
  assert.doesNotMatch(h.rail.innerHTML,/hub-sound|hub-test-sound/);
  assert.equal((h.rail.innerHTML.match(/<button /g)||[]).length,3);
  for(const [mode,resolved,next] of [
    ['dark','dark','Light'],['light','light','System'],['system','dark','Dark']
  ]){
    button.dispatch('click');
    assert.equal(h.html.dataset.themeSetting,mode);
    assert.equal(h.html.dataset.theme,resolved);
    assert.equal(button.querySelector('.hub-rail-state').textContent,mode[0].toUpperCase()+mode.slice(1));
    assert.match(button.attributes['aria-label'],new RegExp('Switch to '+next));
    assert.equal(h.stored.at(-1).value.theme,mode);
    assert.deepEqual(Object.keys(h.stored.at(-1).value),['theme']);
  }
  h.systemPreference.matches=false;
  h.systemPreference.handlers.change();
  assert.equal(h.html.dataset.theme,'light');
});

test('mobile help retains quick links without removed sound instructions',()=>{
  const h=harness();
  h.window.SiteInteractions.openHelp();
  const dialog=h.body.children.find(el=>el.className==='hub-dialog hub-help');
  assert.ok(dialog?.open);
  const help=dialog.querySelector('.hub-help-content').innerHTML;
  assert.match(help,/Quick navigation/);
  assert.match(help,/\/projects\//);
  assert.match(help,/\/skills\//);
  assert.doesNotMatch(help,/sound|audio|test sound/i);
});

test('source has no audio engine, controls, palette actions, or sound tests',()=>{
  const css=read('assets/css/interaction-hub.css');
  const pkg=read('package.json');
  for(const expression of [/AudioContext/,/audioContext/,/createOscillator/,/soundCycle/,
      /testSound/,/hub-test-sound/,/hub-sound/,/Toggle sounds/,/Test sound/]) {
    assert.doesNotMatch(source,expression);
  }
  assert.doesNotMatch(css,/hub-sound|hub-test-sound/);
  assert.doesNotMatch(pkg,/test_sound\.cjs/);
  assert.equal(fs.existsSync(path.join(root,'tests/test_sound.cjs')),false);
});

test('mobile dock provides three aligned controls with theme state visible',()=>{
  const css=read('assets/css/interaction-hub.css');
  assert.match(css,/grid-template-columns:repeat\(3,minmax\(0,1fr\)\)/);
  assert.match(css,/\.interaction-rail button \{ display:inline-flex/);
  assert.match(css,/\.interaction-rail \.hub-rail-state \{display:inline-block/);
  assert.match(css,/env\(safe-area-inset-bottom/);
  assert.match(css,/min-height:65px/);
});

test('all content routes and generators have refreshed interaction assets',()=>{
  for(const route of [
    'index.html','skills/index.html','projects/index.html','search/index.html',
    '404.html','offline.html','research/index.html',
    'projects/3d-cardiac-mri-segmentation/index.html',
    'projects/persian-gpt-from-scratch/index.html',
    'projects/multi-agent-ai-research-assistant/index.html',
    'scripts/project_pages.py','scripts/utility_pages.py'
  ]) {
    assert.match(read(route),/interaction-hub\.js\?v=20261011-theme-v6/,route);
    assert.match(read(route),/interaction-hub\.css\?v=20261011-dotlight-v6/,route);
  }
});

test('floating desktop controls retreat instead of covering footer links', () => {
  const css = read('assets/css/interaction-hub.css');
  assert.ok(css.includes('.interaction-rail.is-footer-visible'));
  assert.ok(css.includes('pointer-events: none'));
  assert.ok(source.includes("document.querySelector('footer')"));
  assert.ok(source.includes('footer.getBoundingClientRect().top < innerHeight'));
  assert.ok(source.includes('rail.inert = blocked'));
  assert.ok(source.includes("desktopDock.addEventListener?.('change', positionDock)"));
});
