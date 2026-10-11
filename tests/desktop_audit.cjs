/* Desktop Chromium smoke checks for the static portfolio.
 * Launches a local HTTP server and exercises real pointer/keyboard interactions.
 * Install Playwright temporarily in CI; no runtime browser dependency is shipped.
 */
'use strict';
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const {setTimeout: delay} = require('node:timers/promises');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const PORT = 8765;
const BASE = 'http://127.0.0.1:' + PORT;
const SHOTS = path.join(ROOT, 'artifacts', 'desktop-audit');
const issues = [];
let browser, server;

async function check(label, task, page) {
  try {
    await task();
    console.log('PASS ' + label);
  } catch (error) {
    issues.push({label, detail: error.message});
    console.error('FAIL ' + label + ': ' + error.stack);
    if (page) {
      try {
        fs.mkdirSync(SHOTS,{recursive:true});
        const name = label.replace(/[^a-z0-9]+/gi,'-').slice(0,75).toLowerCase();
        await page.screenshot({path:path.join(SHOTS,name+'.png'),fullPage:true,timeout:12000});
      } catch (screenshotError) {
        console.error('  Screenshot unavailable: ' + screenshotError.message);
      }
    }
  }
}

async function waitForServer() {
  for (let i=0;i<50;i++) {
    try { const r=await fetch(BASE+'/'); if(r.ok)return; } catch (_) {}
    await delay(200);
  }
  throw new Error('HTTP server did not start');
}

async function visit(context, route) {
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const response = await page.goto(BASE+route,{waitUntil:'domcontentloaded',timeout:30000});
  assert.ok(response && response.ok(),route+' HTTP response');
  await page.waitForTimeout(250);
  return {page,errors};
}
(async () => {
  server=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{
    cwd:ROOT,stdio:['ignore','ignore','pipe']
  });
  server.stderr.on('data', chunk => {
    const message=String(chunk);
    if(/Traceback|Error/.test(message))console.error(message);
  });
  await waitForServer();
  browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  const routes=['/','/projects/','/skills/','/search/','/404.html','/offline.html',
    '/projects/3d-cardiac-mri-segmentation/',
    '/projects/persian-gpt-from-scratch/',
    '/projects/multi-agent-ai-research-assistant/'];
  for(const width of [1024,1440,1920]) {
    const context=await browser.newContext({
      viewport:{width,height:width===1920?1080:width===1024?768:900},
      reducedMotion:'reduce',deviceScaleFactor:1,locale:'en-US'
    });
    for(const route of routes) {
      const {page,errors}=await visit(context,route);
      await check(width+'px '+route+' desktop layout',async()=>{
        const state=await page.evaluate(()=>{
          const root=document.documentElement;
          const h1=document.querySelector('h1');
          const nav=document.querySelector('nav[aria-label="Primary navigation"]');
          const buttons=[...document.querySelectorAll('button,a')].filter(el=>{
            const style=getComputedStyle(el),r=el.getBoundingClientRect();
            return style.visibility!=='hidden'&&style.display!=='none'&&r.width>0&&r.height>0;
          });
          return {
            viewport:innerWidth,scrollWidth:root.scrollWidth,
            heading:!!h1&&getComputedStyle(h1).visibility!=='hidden',
            nav:!!nav,actions:buttons.length
          };
        });
        assert.ok(state.heading,'missing visible H1');
        assert.ok(state.nav,'missing primary navigation');
        assert.ok(state.actions>=2,'no actionable controls');
        assert.ok(state.scrollWidth<=state.viewport+4,
          'horizontal overflow: '+JSON.stringify(state));
        assert.deepEqual(errors,[],'page script errors');
      },page);
      await page.close();
    }
    await context.close();
  }
  const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'reduce'});
  let home=await visit(context,'/');
  await check('desktop keyboard command palette and focus semantics',async()=>{
    await home.page.keyboard.press('Control+k');
    const dialog=home.page.locator('dialog.hub-dialog').first();
    await dialog.waitFor({state:'visible'});
    const search=dialog.locator('#hub-command-search');
    assert.equal(await search.getAttribute('aria-expanded'),'true');
    assert.equal(await search.getAttribute('role'),'combobox');
    await search.fill('skills');
    assert.match(await search.getAttribute('aria-activedescendant')||'',/hub-command-option-/);
    await home.page.keyboard.press('Escape');
    await dialog.waitFor({state:'hidden'});
  },home.page);
  await check('desktop FAQ and navigation',async()=>{
    const question=home.page.locator('details.faq-item summary').first();
    await question.click();
    assert.equal(await home.page.locator('details.faq-item').first().getAttribute('open'),'');
    const link=home.page.locator('.site-nav-links a[href="#about"]');
    await link.click();
    assert.equal(new URL(home.page.url()).hash,'#about');
  },home.page);
  await home.page.close();
  let skills=await visit(context,'/skills/');
  await check('Skills filtering without Pin/Copy controls',async()=>{
    const input=skills.page.locator('#skills-query');
    await input.fill('Random forests');
    await skills.page.waitForTimeout(250);
    assert.match(await skills.page.locator('#skills-count').innerText(),/1 of/);
    assert.equal(await skills.page.locator('.pin-skill,.copy-skill,.skill-compare-toolbar').count(),0);
    assert.equal(await skills.page.locator('.inventory-card:not([hidden])').count(),1);
    assert.equal(await skills.page.locator('.nav-links a[href="/skills/"]').getAttribute('aria-current'),'page');
  },skills.page);
  await skills.page.close();
  let projects=await visit(context,'/projects/');
  await check('Projects filter, pagination and keyboard input',async()=>{
    await projects.page.locator('#archive-explorer').waitFor({state:'visible'});
    await projects.page.locator('#archive-search').fill('cardiac');
    await projects.page.waitForTimeout(300);
    assert.match(await projects.page.locator('#archive-count').innerText(),/[1-9] of/);
    const rendered=await projects.page.locator('#projects-paginated .project').count();
    assert.ok(rendered>0,'no rendered filtered projects');
  },projects.page);
  await projects.page.close();
  let searchPage=await visit(context,'/search/');
  await check('Search index fetch and results',async()=>{
    await searchPage.page.locator('#site-search').fill('cardiac');
    await searchPage.page.locator('.utility-result').first().waitFor({state:'visible',timeout:10000});
    assert.match(await searchPage.page.locator('#search-status').innerText(),/result/);
  },searchPage.page);
  await searchPage.page.close();
  let story=await visit(context,'/');
  await check('desktop story panels cover their viewport',async()=>{
    const result=await story.page.evaluate(()=>{
      const section=document.querySelector('.story-section');
      const panel=section?.querySelector('.story-panel');
      const viewport=section?.querySelector('.story-viewport');
      return {panel:panel?.getBoundingClientRect().width,viewport:viewport?.getBoundingClientRect().width};
    });
    assert.ok(result.panel>=result.viewport-2,'story panel narrower than viewport: '+JSON.stringify(result));
  },story.page);
  await story.page.close();
  await context.close();
})().catch(error=>{issues.push({label:'setup',detail:error.stack});console.error(error);}).finally(async()=>{
  if(browser)await browser.close();
  if(server)server.kill('SIGTERM');
  if(issues.length){
    console.error('\nDesktop audit found '+issues.length+' issue(s):\n'+JSON.stringify(issues,null,2));
    process.exitCode=1;
  }else console.log('\nDesktop Chromium audit passed.');
});
