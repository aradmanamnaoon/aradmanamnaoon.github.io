/* Regression: vertical desktop scrolling must drive the horizontal research chapters.
 * Headless Chrome + its DevTools protocol; no extra test dependencies.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { setTimeout: delay } = require('node:timers/promises');

const root = path.resolve(__dirname, '..');
const browserPath = process.env.CHROME_BIN || '/usr/bin/google-chrome';
const server = http.createServer((req, res) => {
  const pathPart = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  const file = path.resolve(root, '.' + pathPart + (pathPart.endsWith('/') ? 'index.html' : ''));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (error, body) => {
    if (error) { res.writeHead(404).end(); return; }
    const ext = path.extname(file);
    const type = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml' }[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-store' });
    res.end(body);
  });
});
async function until(predicate, label) {
  for (let i = 0; i < 110; i++) {
    try { if (await predicate()) return; } catch (_) {}
    await delay(100);
  }
  throw new Error('Timed out: ' + label);
}
async function run() {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'arad-story-smoke-'));
  const browser = spawn(browserPath, [
    '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
    '--no-first-run', '--disable-background-networking', '--no-proxy-server',
    '--remote-debugging-port=0', '--user-data-dir=' + profile, 'about:blank'
  ], { stdio: 'ignore' });
  let socket;
  try {
    await until(() => fs.existsSync(path.join(profile, 'DevToolsActivePort')), 'Chrome port');
    const port = Number(fs.readFileSync(path.join(profile, 'DevToolsActivePort'), 'utf8').split('\n')[0]);
    const targets = await (await fetch('http://127.0.0.1:' + port + '/json/list')).json();
    socket = new WebSocket(targets.find(item => item.type === 'page').webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { socket.addEventListener('open', resolve, { once: true }); socket.addEventListener('error', reject, { once: true }); });
    const pending = new Map();
    let nextId = 0;
    socket.addEventListener('message', e => {
      const result = JSON.parse(e.data), p = pending.get(result.id);
      if (!p) return;
      pending.delete(result.id);
      result.error ? p.reject(new Error(JSON.stringify(result.error))) : p.resolve(result.result);
    });
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      const id = ++nextId;
      pending.set(id, { resolve, reject });
      socket.send(JSON.stringify({ id, method, params }));
    });
    const js = async expr => {
      const result = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
      if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
      return result.result.value;
    };
    await send('Page.enable');
    await send('Runtime.enable');
    const width = Number(process.env.STORY_WIDTH || 1440);
    const mobile = process.env.STORY_MOBILE === '1';
    await send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile });
    if (mobile) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 1 });
    await send('Page.navigate', { url: 'http://127.0.0.1:' + server.address().port + '/' });
    await until(() => js('document.readyState === "complete" && !!document.querySelector(".story-section")'), 'homepage');
    if (process.env.STORY_PERF) {
      const data = await js('(() => {const n=performance.getEntriesByType("navigation")[0];const p=performance.getEntriesByType("paint");return {domContentLoaded:Math.round(n.domContentLoadedEventEnd),load:Math.round(n.loadEventEnd),paints:p.map(x=>[x.name,Math.round(x.startTime)]),resources:performance.getEntriesByType("resource").map(x=>({url:x.name.replace(location.origin,""),duration:Math.round(x.duration),size:x.transferSize,kind:x.initiatorType})).sort((a,b)=>b.duration-a.duration).slice(0,25)}})()');
      console.log('[performance]', JSON.stringify(data));
    }
    const target = process.env.STORY_TARGET || '.story-section';
    await js('window.scrollTo({top: window.scrollY + document.querySelector(' + JSON.stringify(target) + ').getBoundingClientRect().top - 120, behavior:"instant"})');
    await delay(2500);
    const measure = '(() => {const section=document.querySelector(".story-section"),track=section.querySelector(".story-track"),view=section.querySelector(".story-viewport"),panel=section.querySelector(".story-panel"),link=panel.querySelector("a");return {pinned:section.classList.contains("story-pinned"),gsap:!!window.gsap,ScrollTrigger:!!window.ScrollTrigger,scrollY:window.scrollY,progress:getComputedStyle(section).getPropertyValue("--story-progress"),transform:getComputedStyle(track).transform,trackWidth:track.scrollWidth,viewportWidth:view.clientWidth,sectionLeft:section.getBoundingClientRect().left,documentWidth:document.documentElement.scrollWidth,firstLinkBottom:link.getBoundingClientRect().bottom,viewportBottom:view.getBoundingClientRect().bottom,media:matchMedia("(min-width:900px)").matches,fine:matchMedia("(hover:hover) and (pointer:fine)").matches,touchPoints:navigator.maxTouchPoints,saveData:navigator.connection?.saveData||false}})()';
    const initial = await js(measure);
    console.log('[story] initial:', JSON.stringify(initial));
    if (process.env.STORY_CAPTURE) {
      const image = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
      fs.writeFileSync(path.join(root, 'test-artifacts', (process.env.STORY_TARGET ? 'lenses' : 'story-before') + '-' + width + '.png'), Buffer.from(image.data, 'base64'));
    }
    await js('window.scrollBy({top:1600,behavior:"instant"})');
    await delay(1350);
    const next = await js(measure);
    console.log('[story] after vertical scroll:', JSON.stringify(next));
    if (process.env.STORY_TARGET) {
      const lenses = await js('(() => {const cards=[...document.querySelectorAll(".neuro-focus-core,.neuro-focus-card")];const rects=cards.map(e=>({rect:e.getBoundingClientRect().toJSON(),scrollHeight:e.scrollHeight,clientHeight:e.clientHeight}));let overlaps=[];for(let i=0;i<rects.length;i++)for(let j=i+1;j<rects.length;j++){const a=rects[i].rect,b=rects[j].rect,w=Math.min(a.right,b.right)-Math.max(a.left,b.left),h=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);if(w>2&&h>2) overlaps.push([i,j,w,h]);}return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,rects,overlaps}})()');
      console.log('[lenses]', JSON.stringify({width:lenses.width,scrollWidth:lenses.scrollWidth,overlaps:lenses.overlaps,cardSizes:lenses.rects.map(r=>[Math.round(r.rect.width),Math.round(r.rect.height)])}));
      assert.ok(lenses.scrollWidth <= width + 3, 'Homepage should not overflow horizontally');
      assert.equal(lenses.overlaps.length, 0, 'Neuroscience lens cards must not intersect');
      assert.ok(lenses.rects.every(x => x.scrollHeight <= x.clientHeight + 3), 'All lens descriptions and links must fit their cards');
      return;
    }
    if (mobile) {
      assert.ok(initial.touchPoints > 0, 'Mobile test must emulate touch hardware');
      assert.ok(!initial.pinned, 'Touch phone must stay unpinned');
      assert.ok(initial.trackWidth > initial.viewportWidth, 'Touch phone must support horizontal swipe');
      console.log('[story] PASS: touch devices retain swipe-based chapters');
      return;
    }
    assert.ok(initial.pinned, 'Desktop story must become pinned before the user scrolls past it');
    // Classic scrollbars are ~15px wide and make a centered 100vw section
    // sit at -7.5px. That is expected, not an off-screen chapter.
    assert.ok(Math.abs(initial.sectionLeft) <= 9, 'Pinned chapter section must align with viewport, accounting for classic scrollbar');
    assert.ok(initial.documentWidth <= width + 3, 'Pinned story must not introduce horizontal document overflow');
    assert.ok(initial.firstLinkBottom <= initial.viewportBottom + 3, 'First chapter link must be fully visible without clipping');
    assert.ok(next.pinned, 'Desktop story must remain pinned while moving through chapters');
    assert.notEqual(initial.transform, next.transform, 'Vertical page scroll must move story track horizontally');
    console.log('[story] PASS: desktop vertical scrolling moves research chapters');
  } finally {
    socket?.close();
    browser.kill();
    server.close();
    await delay(300);
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 6, retryDelay: 200 }); }
    catch (error) { console.warn('[story] Could not remove Chrome profile:', error.code); }
  }
}
run().catch(error => { console.error('[story] FAIL:', error); process.exitCode = 1; });
