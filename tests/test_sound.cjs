const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'assets/js/interaction-hub.js'), 'utf8');

function setup({ audioAvailable = true, resumeRejects = false } = {}) {
  const nodes = new Map();
  const calls = { oscillators: [], resumes: 0, settings: [] };
  function node(tag = 'div') {
    const child = new Map();
    return {
      tag, children: [], attributes: {}, style: {setProperty(){}}, dataset: {},
      classList: {add(){},remove(){},toggle(){},contains(){return false}},
      innerHTML:'', open:false, disabled:false,
      append(...args){this.children.push(...args);},
      remove(){}, focus(){}, addEventListener(type,callback){this.listeners ||= {};this.listeners[type]=callback;},
      setAttribute(k,v){this.attributes[k]=v;},
      getAttribute(k){return this.attributes[k];},
      querySelector(selector) {
        if (!child.has(selector)) child.set(selector,node());
        return child.get(selector);
      },
      querySelectorAll(){return [];},
      close(){this.open=false;},showModal(){this.open=true;}
    };
  }
  const document = {
    documentElement: {dataset:{},scrollHeight:2000},
    body:node('body'), createElement:node,
    getElementById(id){
      if (!nodes.has(id)) nodes.set(id,node('button'));
      return nodes.get(id);
    },
    querySelector(){return null;},querySelectorAll(){return[];},addEventListener(){}
  };
  const media = {matches:false,addEventListener(){}};
  class FakeAudioContext {
    constructor(){this.state='suspended';this.currentTime=0;this.destination={};}
    resume(){
      calls.resumes++;
      if (resumeRejects) return Promise.reject(new Error('blocked'));
      this.state='running';return Promise.resolve();
    }
    createOscillator(){
      const osc = {type:null,frequency:{setValueAtTime(hz){osc.hz=hz;}},
        connect(){},start(t){osc.started=t;},stop(t){osc.stopped=t;}};
      calls.oscillators.push(osc);return osc;
    }
    createGain(){return {gain:{setValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){}};}
  }
  const window={AudioContext:audioAvailable?FakeAudioContext:undefined,addEventListener(){}};
  const storage = {getItem(){return null;},setItem(key,value){calls.settings.push(JSON.parse(value));}};
  const sandbox={
    document,window,matchMedia:()=>media,localStorage:storage,
    navigator:{clipboard:{writeText:async()=>{}}},
    location:{href:'https://aradmanamnaoon.github.io/'},
    addEventListener(){},requestAnimationFrame(){return 1;},
    setTimeout(){return 1;},scrollY:0,innerHeight:800,console
  };
  vm.runInNewContext(source,sandbox,{timeout:2000});
  // document.getElementById and rail.querySelector must see the same button.
  // The production document finds actual elements created by the rail.
  // Here we manually remap by overwriting the getElementById method before calls.
  const rail=document.body.children.find(el=>el.className==='interaction-rail');
  for(const id of ['hub-sound','hub-test-sound','hub-theme']){
    const el=rail.querySelector('#'+id);
    nodes.set(id,el);
  }
  return {calls,window,rail,nodes};
}

test('Web Audio makes a two-note audible cue immediately after enabling',async()=>{
  const {calls,rail} = setup();
  const button=rail.querySelector('#hub-sound');
  await button.listeners.click();
  assert.equal(calls.resumes,1);
  assert.equal(calls.oscillators.length,2);
  assert.equal(calls.oscillators[0].type,'triangle');
  assert.ok(calls.oscillators[0].stopped-calls.oscillators[0].started>=.2);
  assert.equal(calls.settings.at(-1).sound,true);
  assert.equal(rail.querySelector('#hub-test-sound').disabled,false);
  await rail.querySelector('#hub-test-sound').listeners.click();
  assert.equal(calls.oscillators.length,4);
  await button.listeners.click();
  assert.equal(calls.settings.at(-1).sound,false);
  assert.equal(rail.querySelector('#hub-test-sound').disabled,false);
  await rail.querySelector('#hub-test-sound').listeners.click();
  assert.equal(calls.oscillators.length,6, 'sound preview works even while notifications are off');
});

test('sound activation failure resets the toggle to off',async()=>{
  for(const settings of [{audioAvailable:false},{resumeRejects:true}]){
    const {calls,rail}=setup(settings);
    await rail.querySelector('#hub-sound').listeners.click();
    assert.equal(calls.settings.at(-1).sound,false);
    assert.equal(rail.querySelector('#hub-sound').attributes['aria-pressed'],'false');
    assert.equal(rail.querySelector('#hub-test-sound').disabled,false);
  }
});

test('mobile controls are reachable and help provides touch navigation',()=>{
  const styles = fs.readFileSync(path.join(__dirname,'..','assets/css/interaction-hub.css'),'utf8');
  assert.match(styles,/grid-template-columns:repeat\(5,minmax\(0,1fr\)\)/);
  assert.match(styles,/padding-bottom:calc\(94px \+ env\(safe-area-inset-bottom/);
  assert.match(styles,/hub-back-top \{right:12px;bottom:calc\(86px/);
  assert.match(styles,/min-height:55px/);
  assert.match(styles,/env\(safe-area-inset-left/);
  assert.match(source,/touchHelp\.matches/);
  assert.match(source,/class="hub-help-links"/);
  assert.match(source,/<a href="\/projects\/">Projects<\/a>/);
  assert.match(source,/<a href="\/skills\/">Skills<\/a>/);
  assert.match(source,/hub-rail-label/);
});

test('all pages and page generators receive the new sound assets',()=>{
  const files=['index.html','projects/index.html','skills/index.html','search/index.html',
    '404.html','offline.html','research/index.html',
    'projects/3d-cardiac-mri-segmentation/index.html',
    'projects/multi-agent-ai-research-assistant/index.html',
    'projects/persian-gpt-from-scratch/index.html',
    'scripts/project_pages.py','scripts/utility_pages.py'];
  for(const file of files){
    const content=fs.readFileSync(path.join(__dirname,'..',file),'utf8');
    assert.match(content,/interaction-hub\.js\?v=20261011-sound-v3/,file);
    assert.match(content,/interaction-hub\.css\?v=20261011-sound-v3/,file);
  }
  assert.match(source,/hub-test-sound/);
  assert.match(source,/Test sound/);
});
