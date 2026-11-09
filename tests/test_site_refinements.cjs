const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const symbols = read('assets/js/project-symbols.js');
const symbolsStyle = read('assets/css/motion.css');
const projectsStyle = read('assets/css/projects-experience.css');
const projectsScript = read('assets/js/projects-experience.js');
const skillsStyle = read('assets/css/skills-experience.css');
const skillsScript = read('assets/js/skills-experience.js');
const home = read('index.html');
const skills = read('skills/index.html');
const projectPage = read('projects/index.html');
const allProjects = JSON.parse(read('projects.json'));

function testDocument() {
  const events = {};
  const document = {
    readyState: 'loading',
    addEventListener(name, handler) { events[name] = handler; },
    querySelectorAll() { return []; },
    createElement(tag) {
      return {
        tag, dataset: {}, attributes: {}, children: [], classList: {
          add() {}, remove() {}, contains() { return false; }
        },
        setAttribute(key, value) { this.attributes[key] = value; },
        addEventListener(name, handler) { this.handlers ??= {}; this.handlers[name] = handler; },
        appendChild(child) { this.children.push(child); }
      };
    },
    createElementNS(ns, tag) { return this.createElement(tag); }
  };
  const window = {
    matchMedia() { return {matches:false}; },
    addEventListener() {},
  };
  vm.runInNewContext(symbols, {document,window,Math,console}, {timeout:1000});
  return {window,document,events};
}

test('every current project receives a visually distinct semantic symbol', () => {
  const {window} = testDocument();
  const actual = allProjects.map(project => {
    const button = window.PortfolioProjectSymbols.create(project.id, project.title, 'archive');
    assert.equal(button.tag, 'button');
    assert.match(button.attributes['aria-label'], /Animate/);
    assert.equal(button.dataset.projectSymbol, project.id);
    assert.equal(button.children.length, 1);
    return button.children[0].innerHTML;
  });
  assert.equal(actual.length, allProjects.length);
  assert.equal(new Set(actual).size, actual.length, 'No project symbol may repeat');
  for (const id of [
    'emotion-appraisal-video-audit',
    'survey-response-integrity',
    'psoriasis-wellbeing-audit'
  ]) {
    assert.ok(allProjects.some(project => project.id === id), 'Approved project missing: ' + id);
  }
});

test('Persian GPT uses a Persian-script token emblem instead of the old lattice', () => {
  const {window} = testDocument();
  const button = window.PortfolioProjectSymbols.create('persian-lm-from-scratch', 'Persian GPT', 'archive');
  const picture = button.children[0].innerHTML;
  assert.match(button.attributes['aria-label'], /Persian letter Peh with Transformer tokens/);
  assert.match(picture, /cx="55" cy="112"/);
  assert.match(picture, /cx="70" cy="114"/);
  assert.match(picture, /cx="85" cy="112"/);
  assert.match(picture, /x="27" y="24"/);
  assert.doesNotMatch(picture, /stroke-dasharray="2 9"/);
  assert.match(projectPage, /project-symbols\.js\?v=20261011-glyph-v8/);
});

test('new project IDs get stable automatic nonrepeating symbols', () => {
  const {window} = testDocument();
  const factory = window.PortfolioProjectSymbols;
  const a = factory.create('future-medical-study-a', 'A', 'archive');
  const again = factory.create('future-medical-study-a', 'A', 'archive');
  const b = factory.create('future-humanities-study-b', 'B', 'archive');
  assert.equal(a.children[0].innerHTML,again.children[0].innerHTML);
  assert.notEqual(a.children[0].innerHTML,b.children[0].innerHTML);
  assert.notEqual(factory.seedFor('future-medical-study-a'),factory.seedFor('future-humanities-study-b'));
  assert.match(projectsScript, /PortfolioProjectSymbols\.create\(card\.id/);
});

test('pointer halos are gone but small pointer-reactive dots are retained', () => {
  assert.match(symbolsStyle, /body\.dots-active/);
  assert.match(symbolsStyle, /dot-pointer-x/);
  assert.match(symbolsStyle, /background-size:\s*30px 30px/);
  assert.match(symbolsStyle, /mask-image: radial-gradient\(circle 520px/);
  assert.match(symbolsStyle, /rgb\(0 0 0 \/ \.73\) 24%/);
  assert.match(symbolsStyle, /\.motion-tilt::before\s*\{\s*content:\s*none/);
  assert.match(projectsStyle, /\.archive \.project::before\s*\{\s*content:\s*none/);
  assert.doesNotMatch(projectsStyle, /470px circle at var\(--archive-x/);
});

test('CV assistant stays desktop-only without removing desktop functionality', () => {
  const html = read('index.html');
  const styles = read('src/input.css');
  for (const source of [html, styles]) {
    assert.match(source, /@media \(max-width: 767px\), \(hover: none\) and \(pointer: coarse\)/);
    for (const id of ['cv-chat-open', 'cv-chat-floating', 'cv-chat-window']) {
      assert.ok(source.includes('#' + id), 'Missing mobile hide rule for ' + id);
    }
    assert.match(source, /display: none !important/);
  }
  assert.match(html, /id="cv-chat-open"/);
  assert.match(html, /id="cv-chat-floating"/);
  assert.match(html, /import\("\.\/assets\/js\/cv-chat-ui\.js"\)/);
});

test('symbol animation supports hover, keyboard, touch and reduced motion', () => {
  assert.match(symbolsStyle,/\.project-symbol:focus-visible/);
  assert.match(symbolsStyle,/\.project-symbol\.symbol-play/);
  assert.match(symbolsStyle,/prefers-reduced-motion: reduce/);
  assert.match(symbolsStyle,/project-glyph-orbit/);
  assert.match(home,/project-symbols\.js/);
  assert.match(projectPage,/project-symbols\.js/);
});

test('Skills page progressively enhances searchable, mobile-safe content', () => {
  assert.match(skills,/skills-explorer" class="skills-explorer" hidden/);
  assert.match(skills,/data-skill-area="medical"/);
  assert.match(skills,/data-skill-area="humanities"/);
  assert.match(skillsScript,/input\.addEventListener\('input'/);
  assert.match(skillsScript,/aria-pressed/);
  assert.match(skillsScript,/data-reveal/);
  assert.match(skillsStyle,/max-width:700px/);
  assert.match(skillsStyle,/prefers-reduced-motion:reduce/);
  assert.match(skillsStyle,/\.skill-filtered-out/);
  assert.match(skillsStyle,/\.skills-visual/);
});

test('Homepage SEO scope, descriptions, and structured data remain accurate', () => {
  assert.match(home,/AI Engineering &amp; Neuroscience/);
  assert.match(home,/AI engineering\./);
  assert.match(home,/advanced neuroscience/i);
  const match = home.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
  assert.ok(match);
  const graph = JSON.parse(match[1])['@graph'];
  const person = graph.find(e=>e['@type']==='Person');
  const featured = graph.find(e=>e['@type']==='ItemList');
  assert.match(person.description,/AI engineer/i);
  assert.match(person.description,/brain genomics/i);
  assert.equal(featured.numberOfItems,featured.itemListElement.length);
  assert.equal(featured.numberOfItems,3);
  assert.ok(featured.itemListElement.every(item=>item.url.startsWith('https://aradmanamnaoon.github.io/projects/')));
  assert.ok(!home.includes('https://github.com/AradMn'));
  assert.match(home,/rel="canonical"/);
});

test('Neuroscience homepage preserves the branded dot backdrop and all prior project/skill sections', () => {
  const neuroCss = read('assets/css/neuro-focus.css');
  const motionCss = read('assets/css/motion.css');
  assert.match(home,/href="\/assets\/css\/neuro-focus\.css\?v=/);
  for (const id of ['neuro-genomics','neuro-informatics','neuro-imaging','neuro-pharmacology'])
    assert.ok(home.includes('id="' + id + '"'), 'missing research focus ' + id);
  assert.equal((home.match(/class="story-panel"/g)||[]).length,6);
  assert.ok(home.includes('id="skills"') && home.includes('id="projects"'));
  assert.doesNotMatch(home,/<img src="\/assets\/images\/ai-psychology-neuroscience-map\.svg"/);
  assert.match(neuroCss,/\.neuro-focus-layout/);
  assert.match(motionCss,/body\.dots-active:not\(\.motion-disabled\)::after/);
  assert.match(read('animations.js'),/updateNativeProgress/);
});

test('Projects research introduction uses the coherent neuroscience layout without removing archive evidence', () => {
  const archive = read('projects/index.html');
  const skillsPage = read('skills/index.html');
  const sharedCss = read('assets/css/ux.css');
  const siteUi = read('assets/js/site-ui.js');
  assert.doesNotMatch(archive, /<h3>Deep learning for medical applications<\/h3>/);
  assert.match(archive, /class="neuro-arc-layout"/);
  assert.equal((archive.match(/class="neuro-arc-field"/g) || []).length, 4);
  assert.match(archive, /AUTO:RESEARCH_PROJECTS:START/);
  assert.match(archive, /id="selected-projects"/);
  for (const label of ['Brain genomics','Neuroinformatics','Neuroimaging','Neuropharmacology']) {
    assert.match(archive, new RegExp(label, 'i'), label);
    assert.match(skillsPage, new RegExp(label, 'i'), label);
  }
  assert.match(skillsPage, /AUTO:SKILLS:START/);
  assert.match(skillsPage, /id="skills-explorer"/);
  assert.match(sharedCss, /\.neuro-arc-layout/);
  assert.match(sharedCss, /\.research-continuum-note/);
  assert.match(siteUi, /independently studying advanced neuroscience/);
  assert.doesNotThrow(() => new Function(siteUi));
});
