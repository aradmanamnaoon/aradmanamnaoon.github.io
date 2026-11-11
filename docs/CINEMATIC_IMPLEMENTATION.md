# Cinematic portfolio: implementation and QA handoff

## Source of truth

- Working directory: `D:\coding\codex\CinematicPortfolio`.
- Origin: `https://github.com/aradmanamnaoon/aradmanamnaoon.github.io`.
- Original prompt: local `prompt.txt`, excluded from commits.
- Source template: `scripts/render_cinematic_home.py`.
- Project content: `projects.json`, with feature selection in `scripts/configure_cinematic_projects.py`.
- Generated output: `index.html`, individual `projects/<slug>/index.html`, project archive, search index and sitemap.
- Core styling and animation: `assets/css/cinematic.css`, `assets/js/cinematic.js`, locally bundled GSAP and ScrollTrigger.
- Featured case styling: `assets/css/cinematic-case.css`. Error/offline styling: `assets/css/cinematic-states.css`.

## Visual narrative

Seven scenes: cinematic MRI video introduction; human identity with one existing photograph; engineering-to-neuroscience intersection; four scientific learning directions; orbital toolchain; five rotated rectangular project planes; and closing collaboration invitation. The layout uses navy, charcoal, blue-white and cool paper, with a deliberately restrained editorial typography system. The case-study pages share a consistent visual hero. The contact destination is LinkedIn.

Motion is scroll-linked in capable desktop browsers, uses shorter entrance transitions on mobile, and is explicitly disabled for `prefers-reduced-motion`. The video pauses when offscreen, when the tab is hidden, on data-saving connections, and for reduced motion. CSS displays a static poster when video is unavailable. The loader is decorative and has a CSS fail-safe.

## Featured evidence

Exactly five featured projects appear in this order:

1. Constellation: experimental Rust/Tauri local AI agent workspace.
2. 3D Cardiac MRI Segmentation: author-reported validation, no clinical claim.
3. AI Research Assistant Platform: LangGraph workflow software with offline checks; no answer-quality claims.
4. Holdout Ledger: explainable research data leakage audits with synthetic checks, no universal detection claim.
5. EU Loneliness & Social Support Analysis: exploratory secondary analysis of the 2022 survey; cross-sectional observations, author-reported Python odds ratios, unexecuted R replication.

The scientific and archived case studies remain accessible under `/projects/`. Existing deep links, distinct route titles, structured data, indexable pages and archive search were retained. Generated URLs are written into the sitemap.

The public CV is disabled. `assets/js/site-config.js` has `showCV: false` and `resumeUrl: null`. Public PDF copies were removed from the branch, the automatic CV generation workflow was disabled, and the archive's visible PDF link was removed. An intentional future configuration path is retained, but the feature does not appear in public navigation or the site.

## Assets and motion provenance

The photographic and illustration assets came from the local `CinematicWebsiteAssets` directory provided with the project. They were validated and optimized locally with Pillow. `enhanced-video.mp4` and `enhanced-video2.mp4` were transcoded using FFmpeg for desktop and mobile. The approved favicon variants were copied from the source icons directory.

A supplied brain MRI GLB was structurally inspected and deliberately omitted from runtime because of its weight. The hero videos, science visuals, abstract orbit effects, perspective transforms, and project covers provide the planned depth without requiring WebGL downloads. Static composition was based on inspection of the specified visual reference sites and then implemented in an original layout.

## Reproduce locally

```powershell
cd D:\coding\codex\CinematicPortfolio
npm ci
npm run build
npm test
npm run test:browser
npm run validate
```

`scripts/python.cjs` selects the installed Python 3 interpreter on Windows and `python3` in Linux CI. The build is static and can be hosted directly from the repository root. Headless Chrome/Chromium is required for `npm run test:browser`. Pass `CHROME_PATH` if necessary.

The browser test starts its own local server on a random port, uses a hidden headless Chrome process and tests widths 1440, 1024, 768, 390 and 320. It checks overflow, exactly five cases, navigation, link routing, loading, scroll animation, disabled CV, reduced motion, broken images, JavaScript errors, custom error pages and the video source selection. It captures local screenshots under `docs/qa/`.

## Verification notes

- `npm run build`: passes locally.
- `npm test`: 9 cinematic static checks, 6 empirical atlas checks, 4 statistical-project checks and 5 service-worker checks pass.
- `npm run test:browser`: five viewport sizes, seven routes, no console errors or failed local requests; 29 ScrollTrigger instances observed.
- `npm run validate`: existing site auditor returns low-priority historical findings but no High or Critical findings.

The original broad regression suite was written for the retired site design and includes assumptions about the old hero, CV chat assistant, theme and toolbar. It is retained under `npm run test:legacy` for reference; those specific assertions are obsolete and fail against the authorized replacement design. The new acceptance suite tests the current product while the previously established scientific suites remain in the default gate.

The runtime service worker uses a new versioned offline cache, keeps preloading lightweight core resources, and intentionally avoids pre-caching the full video files. The nightly GitHub Pages build, mobile audit and desktop audit workflows were updated to run the current acceptance gates.

## Deferred material

There is no public CV until `showCV` and the actual future document are deliberately enabled. The supplied large GLB was not loaded, and standalone render exports or Figma/Remotion project files are not claimed. This is a static portfolio implementation with production-oriented fallbacks, not a rendered film asset pipeline.
