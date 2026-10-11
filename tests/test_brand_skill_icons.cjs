const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const skillSource = read('assets/js/skills-experience.js');
const brandSource = read('assets/js/brand-icons.js');
const skillStyles = read('assets/css/skills-experience.css');
const sharedStyles = read('assets/css/motion.css');
const home = read('index.html');
const pages = ['index.html', 'projects/index.html', 'skills/index.html'];

const inventory = [
  'programming','mobile_development','classical_machine_learning','deep_learning',
  'computer_vision','medical_imaging','natural_language_processing','llm_engineering',
  'rag','agentic_ai','fine_tuning','statistics_and_humanities_data',
  'software_and_delivery','libraries_and_tools'
];

function node() {
  return {
    children: [], attributes:{}, dataset:{}, handlers:{}, innerHTML:'',
    classList: { add(){}, remove(){}, toggle(){}, contains(){return false;} },
    setAttribute(key,value){this.attributes[key]=value;},
    addEventListener(event,handler){this.handlers[event]=handler;},
    appendChild(child){this.children.push(child);},
    querySelector(){return null;}, querySelectorAll(){return[];},
    hasAttribute(){return false;}
  };
}
test('all fourteen skill groups receive their own semantic SVG buttons', () => {
  const cards = inventory.map(id => {
    const card = node();
    card.id = id === 'libraries_and_tools' ? '' : id;
    card.textContent = id.replaceAll('_',' ');
    card.querySelector = selector => selector === 'h3' ? {textContent:card.textContent} : null;
    card.classList.contains = cls => id === 'libraries_and_tools' && cls === 'inventory-tools';
    return card;
  });
  const grid=node(), explorer=node(), search=node(), count=node(), clear=node();
  const chips = ['all','medical','humanities','language','engineering'].map(category => {
    const el=node();el.dataset.skillArea=category;return el;
  });
  grid.querySelectorAll=selector => selector === '.inventory-card' ? cards : [];
  explorer.querySelectorAll=selector => selector === '[data-skill-area]' ? chips : [];
  const controls={
    'skills-directory':grid,'skills-explorer':explorer,'skills-query':search,
    'skills-count':count,'skills-clear':clear
  };
  search.value='';
  const doc={
    getElementById(id){return controls[id] || null;},
    createElement(){return node();},
    createElementNS(){return node();},
    addEventListener(){}
  };
  vm.runInNewContext(skillSource,{
    document:doc,window:{matchMedia(){return {matches:false}}},clearTimeout,setTimeout
  },{timeout:1500});
  assert.equal(explorer.hidden,false);
  assert.ok(count.textContent.includes('14 of 14'));
  const drawings=cards.map(card=>card.children.find(child=>child.className==='skills-visual'));
  assert.equal(drawings.length,14);
  assert.ok(drawings.every(Boolean),'no skill group is allowed to have a missing icon');
  assert.equal(new Set(drawings.map(button=>button.children[0].innerHTML)).size,14,
    'each skill group should have its own meaningful illustration');
  assert.match(drawings[5].attributes['aria-label'],/Cardiac medical scan/);
  assert.match(drawings[11].attributes['aria-label'],/Statistical distribution/);
  assert.match(drawings[13].attributes['aria-label'],/Libraries and development tools/);
  assert.match(skillStyles,/max-width:700px/);
  assert.match(skillStyles,/prefers-reduced-motion:reduce/);
});

test('brand icons decorate proper links exactly once and leave other URLs alone',()=>{
  const makeLink=(url,card=false)=>{
    const link=node();link.href=url;link.dataset={};
    const heading=node();
    link.matches=selector => selector==='.surface-card' && card;
    link.querySelector=selector => {
      if (selector==='[data-brand-icon]') return link.icon || heading.icon || null;
      if (selector==='h3, h2') return card ? heading : null;
      return null;
    };
    link.prepend=x=>{link.icon=x};
    heading.prepend=x=>{heading.icon=x};
    return {link,heading};
  };
  const gh=makeLink('https://github.com/aradmanamnaoon/repo');
  const hf=makeLink('https://huggingface.co/aradmanamnaoon/model');
  const internal=makeLink('https://aradmanamnaoon.github.io/projects/');
  const tile=makeLink('https://github.com/aradmanamnaoon',true);
  const links=[gh.link,hf.link,internal.link,tile.link];
  const body=node();
  body.nodeType=1;
  body.matches=()=>false;
  body.querySelectorAll=()=>links;
  const doc={
    readyState:'complete',body,
    createElement:()=>node(),
    createElementNS:()=>node()
  };
  const win={};
  vm.runInNewContext(brandSource,{
    document:doc,window:win,location:{href:'https://aradmanamnaoon.github.io/',origin:'https://aradmanamnaoon.github.io/'},
    URL
  },{timeout:1500});
  assert.equal(gh.link.dataset.platform,'github');
  assert.equal(hf.link.dataset.platform,'huggingface');
  assert.equal(tile.link.dataset.platform,'github');
  assert.ok(!internal.link.icon && !internal.link.dataset.platform);
  assert.ok(gh.link.icon);
  assert.equal(hf.link.icon.textContent,'🤗');
  assert.ok(tile.heading.icon,'icon should appear in heading for full-card links');
});
test('Skills nav targets the full directory and platform icons load on every page',()=>{
  assert.equal((home.match(/href="\/skills\/"/g)||[]).length>=2,true);
  assert.doesNotMatch(home,/href="#skills"/);
  for(const page of pages){
    const html=read(page);
    assert.match(html,/assets\/js\/brand-icons\.js\?v=/);
  }
  assert.match(sharedStyles,/\.brand-link-icon/);
  assert.match(sharedStyles,/\.project-symbol\s*\{/);
  assert.match(read('assets/css/projects-experience.css'),/\.archive \.project h2/);
});
