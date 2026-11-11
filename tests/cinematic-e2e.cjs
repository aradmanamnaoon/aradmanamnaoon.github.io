/**
 * Actual headless browser acceptance for the cinematic site.
 *
 * Uses a local ephemeral HTTP server and system Chrome to avoid disturbing
 * the user's visible desktop. Reusable locally and on GitHub Actions.
 */
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { chromium } = require("playwright-core");

const root = path.resolve(__dirname, "..");
const mime = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".mp4": "video/mp4",
  ".xml": "application/xml; charset=utf-8",
};

const chromeCandidates = [
  process.env.CHROME_PATH,
  process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
].filter(Boolean);
const executablePath = chromeCandidates.find(x => fs.existsSync(x));
if (!executablePath) throw new Error("Headless Chrome/Chromium not found; set CHROME_PATH.");

const server = http.createServer((req, res) => {
  let url;
  try {
    url = decodeURIComponent(new URL(req.url || "/", "http://127.0.0.1").pathname);
  } catch {
    res.writeHead(400).end("Invalid path");
    return;
  }
  const relative = url.replace(/^\/+/, "");
  let file = path.resolve(root, relative);
  if (!(file === root || file.startsWith(root + path.sep))) {
    res.writeHead(403).end("Forbidden");
    return;
  }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
  if (!fs.existsSync(file)) {
    res.writeHead(404, { "content-type": "text/html; charset=utf-8" });
    fs.createReadStream(path.join(root, "404.html")).pipe(res);
    return;
  }
  const stat = fs.statSync(file);
  res.writeHead(200, {
    "content-type": mime[path.extname(file).toLowerCase()] || "application/octet-stream",
    "content-length": stat.size,
  });
  fs.createReadStream(file).pipe(res);
});

async function main() {
  await new Promise((resolve, reject) => server.listen(0, "127.0.0.1", error => error ? reject(error) : resolve()));
  const address = server.address();
  const base = `http://127.0.0.1:${address.port}`;
  const browser = await chromium.launch({
    executablePath, headless: true,
    args: ["--disable-dev-shm-usage", "--no-default-browser-check"],
  });
  const output = { testedWidths: [], projectPages: [], consoleErrors: [], failedAssets: [], motion: null, reducedMotion: null };

  try {
    for (const [width, height] of [[1440, 900], [1024, 768], [768, 1024], [390, 844], [320, 720]]) {
      const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1 });
      const page = await context.newPage();
      page.on("pageerror", error => output.consoleErrors.push({width, message: error.message}));
      page.on("response", response => {
        if (response.status() >= 400 && response.url().startsWith(base)) output.failedAssets.push({width,status:response.status(),url:response.url()});
      });
      try {
        const response = await page.goto(base + "/", { waitUntil: "domcontentloaded" });
        assert.equal(response.status(), 200);
        await page.waitForFunction(
          () => getComputedStyle(document.querySelector("#site-loader")).opacity === "0",
          null, { timeout: 5000 }
        );
        const status = await page.evaluate(() => {
          const visibleControls = [...document.querySelectorAll("a,button")].filter(el => {
            const css = getComputedStyle(el);
            return css.display !== "none" && css.visibility !== "hidden";
          });
          return {
            viewport: innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            h1Count: document.querySelectorAll("h1").length,
            sectionCount: document.querySelectorAll("main > section").length,
            featuredCount: document.querySelectorAll(".project-plane").length,
            portraitCount: document.querySelectorAll('img[src*="photo_2026-10-06_09-42-56"]').length,
            cvControls: visibleControls.filter(el => /\bcv\b|\bresume\b/i.test(el.textContent || "")).length,
            missingImages: [...document.images].filter(img => img.complete && img.naturalWidth === 0).map(img => img.src),
            projectWidth: Math.max(...[...document.querySelectorAll(".project-plane")].map(el => el.getBoundingClientRect().width)),
            worldsWidth: Math.max(...[...document.querySelectorAll(".world")].map(el => el.getBoundingClientRect().width)),
            loaderGone: getComputedStyle(document.querySelector("#site-loader")).opacity === "0",
            videoSrc: document.querySelector("#hero-film").currentSrc,
          };
        });
        assert.equal(status.h1Count, 1);
        assert.equal(status.featuredCount, 5);
        assert.equal(status.sectionCount, 7);
        assert.equal(status.portraitCount, 1);
        assert.equal(status.cvControls, 0);
        assert.equal(status.missingImages.length, 0, status.missingImages.join("\n"));
        assert.ok(status.loaderGone, `Loader failed to clear at ${width}px`);
        assert.ok(status.scrollWidth <= width + 1, `Horizontal overflow at ${width}px: ${status.scrollWidth}`);
        assert.ok(status.worldsWidth <= width + 1, `Science chapter extends beyond viewport at ${width}px: ${status.worldsWidth}`);
        assert.ok(status.projectWidth <= width + 1, `Project panel extends beyond viewport at ${width}px`);
        if (width <= 720) assert.match(status.videoSrc, /hero-mobile\.mp4$/);
        else assert.match(status.videoSrc, /hero-desktop\.mp4$/);

        if (width === 1440) {
          output.motion = await page.evaluate(() => ({
            triggerCount: window.ScrollTrigger?.getAll().length || 0,
            gsapReady: !!window.gsap,
          }));
          assert.ok(output.motion.gsapReady, "GSAP failed to initialize");
          assert.ok(output.motion.triggerCount >= 5, "GSAP scroll scenes did not register");
          const progress = await page.locator("#reading-progress");
          await page.evaluate(() => window.scrollTo({top: document.body.scrollHeight * .55, behavior: "instant"}));
          await page.waitForTimeout(400);
          const mid = await progress.evaluate(el => parseFloat(el.style.width));
          assert.ok(mid > 10 && mid < 90, `Reading progress outside bounds: ${mid}`);
          await page.evaluate(() => window.scrollTo({top: 0, behavior: "instant"}));
          await page.waitForTimeout(400);
          const back = await progress.evaluate(el => parseFloat(el.style.width));
          assert.ok(back < 2, `Reverse scroll did not reset progress: ${back}`);
          await page.screenshot({path: path.join(root, "docs", "qa", "cinematic-headless-desktop.png")});
        }
        if (width === 390) {
          const toggle = page.locator("#menu-toggle");
          assert.equal(await toggle.isVisible(), true);
          await toggle.click();
          assert.equal(await toggle.getAttribute("aria-expanded"), "true");
          await page.locator('.nav a[href="#work"]').click();
          assert.equal(await toggle.getAttribute("aria-expanded"), "false");
          assert.equal(new URL(page.url()).hash, "#work");
          await page.screenshot({path: path.join(root, "docs", "qa", "cinematic-headless-mobile.png")});
        }
        output.testedWidths.push({width, height, overflow:status.scrollWidth - width, featured:status.featuredCount, worldsWidth:status.worldsWidth});
      } finally {
        await context.close();
      }
    }

    const reducedContext = await browser.newContext({
      viewport: { width: 390, height: 844 }, reducedMotion: "reduce",
    });
    try {
      const page = await reducedContext.newPage();
      await page.goto(base + "/", { waitUntil: "domcontentloaded" });
      await page.waitForTimeout(200);
      output.reducedMotion = await page.evaluate(() => ({
        loader: getComputedStyle(document.querySelector("#site-loader")).display,
        paused: document.querySelector("#hero-film").paused,
        projectOpacity: getComputedStyle(document.querySelector(".project-plane")).opacity,
      }));
      assert.equal(output.reducedMotion.loader, "none");
      assert.equal(output.reducedMotion.paused, true);
      assert.equal(output.reducedMotion.projectOpacity, "1");
    } finally {
      await reducedContext.close();
    }

    const routeContext = await browser.newContext();
    try {
      const page = await routeContext.newPage();
      for (const route of [
        "/projects/constellation/",
        "/projects/3d-cardiac-mri-segmentation/",
        "/projects/multi-agent-ai-research-assistant/",
        "/projects/holdout-ledger/",
        "/projects/eu-loneliness-social-support-analysis/",
        "/404.html",
        "/offline.html",
      ]) {
        const response = await page.goto(base + route, { waitUntil: "domcontentloaded" });
        assert.equal(response.status(), 200, route);
        assert.equal(await page.locator("h1").count(), 1, route);
        output.projectPages.push({ route, status: response.status() });
      }
      const missing = await page.goto(base + "/this-page-does-not-exist/", {waitUntil:"domcontentloaded"});
      assert.equal(missing.status(), 404);
      assert.match(await page.title(), /404/);
    } finally {
      await routeContext.close();
    }
    assert.deepEqual(output.consoleErrors, []);
    assert.deepEqual(output.failedAssets, []);
    console.log(JSON.stringify({status:"PASS", ...output}, null, 2));
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}

main().catch(error => {
  console.error(error.stack || error);
  server.close();
  process.exitCode = 1;
});
