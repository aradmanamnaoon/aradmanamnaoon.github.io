/* Desktop regression checks using Chrome DevTools Protocol and Node 22.
 * No Playwright, Selenium, or remote service is required. Run after npm run build.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const { setTimeout: delay } = require('node:timers/promises');

const ROOT = path.resolve(__dirname, '..');
const types = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.webmanifest': 'application/manifest+json'
};
const server = http.createServer((request, response) => {
  let pathname;
  try { pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname); }
  catch (_) { response.writeHead(400); response.end(); return; }
  const filename = path.resolve(ROOT, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
  if (!filename.startsWith(ROOT + path.sep)) { response.writeHead(403); response.end(); return; }
  fs.readFile(filename, (error, body) => {
    if (error) { response.writeHead(404); response.end('Not found'); return; }
    response.writeHead(200, { 'Content-Type': types[path.extname(filename)] || 'application/octet-stream',
      'Cache-Control': 'no-store' });
    response.end(body);
  });
});
function chromeBinary() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;
  for (const name of ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']) {
    const found = spawnSync('which', [name], { encoding: 'utf8' });
    if (found.status === 0) return found.stdout.trim();
  }
  throw new Error('Desktop smoke checks require Chrome or Chromium');
}
function makeClient(socket) {
  let sequence = 0;
  const pending = new Map();
  socket.addEventListener('message', event => {
    const response = JSON.parse(event.data);
    const task = pending.get(response.id);
    if (!task) return;
    pending.delete(response.id);
    if (response.error) task.reject(new Error(JSON.stringify(response.error)));
    else task.resolve(response.result);
  });
  return (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++sequence;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
    setTimeout(() => {
      if (pending.has(id)) { pending.delete(id); reject(new Error('CDP timeout: ' + method)); }
    }, 15000).unref();
  });
}
async function waitUntil(check, label, tries = 100) {
  for (let n = 0; n < tries; n++) {
    try { if (await check()) return; } catch (_) {}
    await delay(100);
  }
  throw new Error('Timeout waiting for ' + label);
}
async function run() {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'portfolio-chrome-'));
  const browser = spawn(chromeBinary(), [
    '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
    '--disable-gpu', '--no-first-run', '--disable-background-networking',
    '--no-proxy-server', '--remote-debugging-port=0', '--user-data-dir=' + profile, 'about:blank'
  ], { stdio: 'ignore' });
  let socket;
  try {
    const portFile = path.join(profile, 'DevToolsActivePort');
    await waitUntil(() => fs.existsSync(portFile), 'Chrome debugging endpoint');
    const debugPort = Number(fs.readFileSync(portFile, 'utf8').split('\n')[0]);
    const targets = await (await fetch('http://127.0.0.1:' + debugPort + '/json/list')).json();
    const tab = targets.find(x => x.type === 'page');
    assert.ok(tab, 'Chrome must have a page target');
    socket = new WebSocket(tab.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => {
      socket.addEventListener('open', resolve, { once: true });
      socket.addEventListener('error', reject, { once: true });
    });
    const send = makeClient(socket);
    await send('Page.enable');
    await send('Runtime.enable');
    async function js(expression) {
      const result = await send('Runtime.evaluate',
        { expression, returnByValue: true, awaitPromise: true });
      if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
      return result.result.value;
    }
    async function visit(route, width = 1440, height = 900) {
      await send('Emulation.setDeviceMetricsOverride',
        { width, height, deviceScaleFactor: 1, mobile: false });
      await send('Page.navigate', { url: base + route });
      await waitUntil(async () => await js('document.readyState === "complete" && !!window.SiteInteractions && location.pathname === ' + JSON.stringify(route)), route);
      await delay(200);
      const layout = await js('(() => {const d=document.documentElement; const h=document.querySelector("h1");return {title:document.title,width:innerWidth,actual:d.scrollWidth,heading:!!h,nav:!!document.querySelector(\'nav[aria-label="Primary navigation"]\'),rail:!!document.querySelector(".interaction-rail"),customCursor:!!document.querySelector(".motion-cursor")};})()');
      assert.equal(layout.width, width, route + ' viewport');
      assert.ok(layout.heading && layout.nav && layout.rail, route + ' document shell');
      assert.ok(!layout.customCursor, route + ' unexpected custom cursor');
      assert.ok(layout.actual <= width + 6, route + ' has horizontal overflow: ' + JSON.stringify(layout));
      console.log('[desktop]', route, width + 'x' + height, 'scrollWidth=' + layout.actual);
      if (width === 1440) {
        try {
          const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
          fs.mkdirSync(path.join(ROOT, 'test-artifacts'), { recursive: true });
          fs.writeFileSync(path.join(ROOT, 'test-artifacts', route.replace(/[^a-z0-9]+/gi, '-') + '.png'), Buffer.from(shot.data, 'base64'));
        } catch (error) { console.warn('Screenshot unavailable:', String(error)); }
      }
    }
    const routes = ['/', '/projects/', '/skills/', '/search/',
      '/projects/3d-cardiac-mri-segmentation/', '/projects/persian-gpt-from-scratch/',
      '/projects/multi-agent-ai-research-assistant/', '/404.html', '/offline.html'];
    for (const route of routes) await visit(route);
    for (const width of [1024, 1280]) {
      for (const route of ['/', '/projects/', '/skills/']) await visit(route, width, 800);
    }
    await visit('/');
    assert.ok(await js('(() => { document.querySelector("#hub-commands").click(); return document.querySelector(".hub-dialog").open && document.activeElement.id==="hub-command-search" })()'),
      'Desktop command palette must open and focus search');
    assert.ok(await js('(() => {const dialog=document.querySelector(".hub-dialog"); dialog.querySelector(".hub-close").click(); return !dialog.open})()'),
      'Desktop command palette must close');
    assert.ok(await js('(() => {const old=document.documentElement.dataset.themeSetting;document.querySelector("#hub-theme").click();const changed=document.documentElement.dataset.themeSetting!==old;document.querySelector("#hub-theme").click();document.querySelector("#hub-theme").click();return changed && document.documentElement.dataset.themeSetting===old;})()'),
      'Theme button must cycle through modes');
    await js('window.scrollTo(0,650)');
    await delay(250);
    assert.ok(await js('(() => {const a=document.querySelector("#cv-chat-floating"),b=document.querySelector(".hub-back-top"); if(getComputedStyle(b).visibility!=="visible")return true;const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();return x.right<y.left || y.right<x.left || x.bottom<y.top || y.bottom<x.top;})()'),
      'AI assistant button must not overlap Back to top');
    await visit('/skills/');
    await js('(() => {const input=document.querySelector("#skills-query"); input.value="scikit-learn"; input.dispatchEvent(new Event("input",{bubbles:true}));})()');
    await delay(350);
    assert.ok(await js('(() => {const cards=[...document.querySelectorAll("#skills-directory .inventory-card")];return cards.some(c=>!c.hidden && c.id==="classical_machine_learning") && cards.some(c=>c.hidden);})()'),
      'Skills search should filter to classical ML');
    assert.ok(await js('(() => {document.querySelector("#skills-clear").click();return [...document.querySelectorAll("#skills-directory .inventory-card")].every(c=>!c.hidden);})()'), 'Skills reset should restore cards');
    assert.ok(await js('!document.querySelector(".skill-compare-toolbar,.pin-skill,.copy-skill")'),
      'Removed Skills pin/copy must stay removed');
    await visit('/projects/');
    await js('(() => {const input=document.querySelector("#archive-search"); input.value="MONAI";input.dispatchEvent(new Event("input",{bubbles:true}));})()');
    await delay(350);
    assert.ok(await js('window.portfolioArchive.count() > 0 && window.portfolioArchive.count() < window.portfolioArchive.total()'),
      'Project archive search should reduce results');
    await js('document.querySelector("#archive-clear").click()');
    assert.ok(await js('window.portfolioArchive.count() === window.portfolioArchive.total()'),
      'Project archive reset must restore results');
    const next = await js('!!document.querySelector(\'button[aria-label="Next page"]:not([disabled])\')');
    if (next) {
      await js('document.querySelector(\'button[aria-label="Next page"]\').click()');
      await delay(600);
      assert.ok(await js('window.portfolioArchive.currentPage() === 2'), 'Next page button must advance');
    }
    await visit('/search/');
    await js('(() => {const q=document.querySelector("#site-search");q.value="MRI";q.closest("form").requestSubmit()})()');
    await waitUntil(async () => await js('document.querySelectorAll("#search-results a").length > 0'), 'portfolio search results');
    await visit('/projects/persian-gpt-from-scratch/');
    assert.ok(await js('(() => {const t=document.querySelector(".case-collapse");if(!t)return false;t.click();const c=t.getAttribute("aria-expanded")==="false";t.click();return c && t.getAttribute("aria-expanded")==="true";})()'),
      'Case-study sections must collapse and expand');
    console.log('[desktop] All interactive desktop smoke checks passed.');
  } finally {
    socket?.close();
    browser.kill();
    await delay(300);
    server.close();
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }); }
    catch (error) { console.warn('Could not remove temporary Chrome profile:', error.code); }
  }
}
run().catch(error => { console.error('[desktop] FAILED', error); process.exitCode = 1; });
