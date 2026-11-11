"""Deterministic static home renderer.

The home remains valid HTML without JavaScript. Project excerpts are generated
separately from projects.json by build_site.py between the AUTO markers.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HOME = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#10151a">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; base-uri 'none'; object-src 'none'; form-action 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data:; font-src 'self' https://fonts.gstatic.com; media-src 'self'; connect-src 'self'; worker-src 'self'">
  <meta name="color-scheme" content="dark">
  <meta name="author" content="Seyyed Arad Hosseini Moghaddam">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="description" content="Arad Hosseini Moghaddam is an AI engineer and data scientist building medical imaging, language model, agentic AI and reproducible research software, with developing interests in neuroscience.">
  <title>Arad Hosseini Moghaddam — AI Engineering × Neuroscience</title>
  <link rel="canonical" href="https://aradmanamnaoon.github.io/">
  <link rel="alternate" hreflang="en" href="https://aradmanamnaoon.github.io/">
  <link rel="alternate" hreflang="x-default" href="https://aradmanamnaoon.github.io/">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="icon" sizes="any" href="/favicon.ico">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="ARADMANAMNAOON">
  <meta property="og:title" content="Arad Hosseini Moghaddam — AI Engineering × Neuroscience">
  <meta property="og:description" content="A cinematic portfolio of documented AI research engineering, scientific software and an evolving neuroscience direction.">
  <meta property="og:url" content="https://aradmanamnaoon.github.io/">
  <meta property="og:image" content="https://aradmanamnaoon.github.io/og-image.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Arad Hosseini Moghaddam — AI Engineering × Neuroscience">
  <meta name="twitter:description" content="Documented engineering, medical imaging, agentic AI and an evolving neuroscience direction.">
  <meta name="twitter:image" content="https://aradmanamnaoon.github.io/og-image.jpg">
  <script type="application/ld+json">
  {
    "@context":"https://schema.org",
    "@graph":[
      {"@type":"Person","@id":"https://aradmanamnaoon.github.io/#person","name":"Seyyed Arad Hosseini Moghaddam","alternateName":["Arad Hosseini Moghaddam","ARADMANAMNAOON"],"url":"https://aradmanamnaoon.github.io/","image":"https://aradmanamnaoon.github.io/photo_2026-10-06_09-42-56.jpg","jobTitle":"AI Engineer and Data Scientist","sameAs":["https://github.com/aradmanamnaoon","https://www.linkedin.com/in/seyyed-arad-hosseini-moghaddam/","https://huggingface.co/aradmanamnaoon","https://orcid.org/0009-0003-0946-395X"]},
      {"@type":"WebSite","name":"ARADMANAMNAOON","url":"https://aradmanamnaoon.github.io/","inLanguage":"en","author":{"@id":"https://aradmanamnaoon.github.io/#person"}},
      {"@type":"WebPage","url":"https://aradmanamnaoon.github.io/","name":"Arad Hosseini Moghaddam — AI Engineering × Neuroscience","primaryImageOfPage":{"@type":"ImageObject","url":"https://aradmanamnaoon.github.io/photo_2026-10-06_09-42-56.jpg"}}
    ]
  }
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="preload" as="image" href="/assets/cinematic/hero-poster.jpg" fetchpriority="high">
  <link rel="stylesheet" href="/assets/css/cinematic.css?v=20261111-1">
</head>
<body class="cinematic-site">
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="cinematic-loader" id="site-loader" aria-hidden="true">
    <div class="loader-inner"><img src="/favicon-96x96.png" width="56" height="56" alt=""><span class="loader-label">ARAD / IN THE MAKING</span><span class="loader-line"><span></span></span><span class="loader-caption">INITIALIZING THE EXPERIENCE</span></div>
  </div>
  <div class="site-grain" aria-hidden="true"></div>
  <div class="reading-progress" aria-hidden="true"><span id="reading-progress"></span></div>
  <header class="header" id="top">
    <a class="brand" href="/" aria-label="Arad Hosseini Moghaddam, homepage"><span class="brand-mark">A<span>✳</span></span><span class="brand-name">ARADMANAMNAOON<small>INDEPENDENT / ENGINEERING & RESEARCH</small></span></a>
    <nav class="nav" id="site-nav" aria-label="Primary navigation">
      <a href="#identity">About</a>
      <a href="#worlds">Research direction</a>
      <a href="#toolchain">Expertise</a>
      <a href="#work">Selected work</a>
      <a href="#contact">Contact</a>
    </nav>
    <div class="header-actions"><a href="#contact" class="header-reach">LET'S TALK <span aria-hidden="true">↗</span></a><button type="button" id="menu-toggle" aria-controls="site-nav" aria-expanded="false" aria-label="Open menu"><span></span><span></span></button></div>
  </header>

  <main id="main">
    <section class="scene hero-scene" id="home" aria-labelledby="hero-title">
      <div class="hero-film">
        <video id="hero-film" muted loop playsinline preload="none" poster="/assets/cinematic/hero-poster.jpg" aria-hidden="true">
          <source src="/assets/cinematic/hero-mobile.mp4" type="video/mp4" media="(max-width: 720px)">
          <source src="/assets/cinematic/hero-desktop.mp4" type="video/mp4">
        </video>
        <div class="hero-film-tint"></div>
      </div>
      <div class="scene-frame">
        <div class="scene-coordinate hero-coordinate"><span>01 — THE INTRODUCTION</span><span>EXPLORING THE SPACE BETWEEN COMPUTATION & LIFE</span></div>
        <div class="hero-title-wrap">
          <p class="hero-overline reveal">AN ENGINEER'S EYE. A SCIENTIST'S CURIOSITY.</p>
          <h1 class="hero-headline" id="hero-title"><span class="headline-line"><span>THE ART OF</span></span><span class="headline-line outline"><span>UNDERSTANDING</span></span><span class="headline-line last"><span>COMPLEXITY<span class="hero-asterisk">✳</span></span></span></h1>
        </div>
        <div class="hero-bottom"><p>Building intelligent systems.<br>Learning to ask better questions about the brain.</p><a class="round-arrow" href="#identity" aria-label="Explore the portfolio"><span aria-hidden="true">↓</span></a><div class="hero-bottom-meta"><span>ARAD HOSSEINI MOGHADDAM</span><span>AI ENGINEER / DATA SCIENTIST</span></div></div>
      </div>
      <div class="hero-side-label" aria-hidden="true">SCROLL TO EXPLORE — VOL. 01</div>
    </section>

    <section class="scene identity-scene" id="identity" aria-labelledby="identity-title"><span id="about" class="legacy-anchor" aria-hidden="true"></span>
      <div class="section-meta"><span>02 / THE PERSON</span><span>BETWEEN SYSTEMS AND SCIENCE</span></div>
      <div class="identity-layout">
        <div class="identity-type reveal"><p class="eyebrow">HELLO, I'M ARAD.</p><h2 id="identity-title">Curiosity<br>is my <em>operating</em><br>system<span class="period">.</span></h2><p class="identity-lede">I'm Seyyed Arad Hosseini Moghaddam, an AI engineer and data scientist. I build models and research tools, test their limits, and keep looking for the questions worth answering.</p><a class="underlined-link" href="#work">SEE WHAT I'VE BUILT <span aria-hidden="true">↗</span></a></div>
        <figure class="identity-portrait reveal"><span class="portrait-backplate" aria-hidden="true"></span><img src="/photo_2026-10-06_09-42-56.jpg" alt="Portrait of Seyyed Arad Hosseini Moghaddam" width="853" height="1280" loading="lazy" decoding="async"><figcaption><span>FIG. 01 — THE HUMAN BEHIND THE CODE</span><span>ENGINEER / LEARNER / BUILDER</span></figcaption></figure>
        <div class="identity-margin-note" aria-hidden="true">A CONSTANT WORK IN PROGRESS</div>
      </div>
      <div class="identity-statement reveal"><span class="huge-quote">“</span><p>I care about what a system <em>does</em>, what the evidence <em>supports</em>, and what we still <em>don't know</em>.</p></div>
    </section>

    <section class="scene intersection-scene" id="intersection" aria-labelledby="intersection-title">
      <div class="section-meta"><span>03 / THE INTERSECTION</span><span>ENGINEERING × NEUROSCIENCE</span></div>
      <div class="intersection-sticky">
        <div class="intersection-visual" aria-hidden="true"><img src="/assets/cinematic/brain-preview.webp" alt="" loading="lazy"><div class="intersection-shutter"></div><div class="intersection-orbit orbit-a"></div><div class="intersection-orbit orbit-b"></div></div>
        <div class="intersection-content"><p class="eyebrow">THE NEXT FRONTIER</p><h2 id="intersection-title">From building<br><em>intelligence</em><br>to studying it.</h2><p>My established work spans deep learning, medical imaging, language models, agentic systems and data analysis. I'm now studying advanced neuroscience independently and exploring how these methods might help investigate neural systems.</p><p class="boundary-note">THE DISTINCTION MATTERS — these are developing scientific interests, not claims of completed brain research or clinical outcomes.</p></div>
        <div class="intersection-index">AI&nbsp; ↔ &nbsp;BRAIN SCIENCE</div>
      </div>
    </section>

    <section class="scene worlds-scene" id="worlds" aria-labelledby="worlds-title"><span id="research-collaboration" class="legacy-anchor" aria-hidden="true"></span>
      <div class="section-meta"><span>04 / THE WORLDS</span><span>FOUR DIRECTIONS I'M EXPLORING</span></div>
      <div class="worlds-head"><p class="eyebrow">THE QUESTIONS AHEAD</p><h2 id="worlds-title">ONE MIND.<br><em>FOUR LENSES.</em></h2><p>Research starts with understanding the problem. These are the neuroscience areas guiding my current study and future computational work.</p></div>
      <div class="worlds-sequence">
        <article class="world world-imaging" id="neuro-imaging"><div class="world-image"><img src="/assets/cinematic/neural.webp" alt="Abstract visualization of neural fibers" loading="lazy"><span>01 / 04</span></div><div class="world-copy"><p class="eyebrow">VISUALIZING THE INVISIBLE</p><h3>NEURO<br><em>IMAGING.</em></h3><p>Learning to interpret brain structure and function through MRI, neural image analysis and reproducible imaging workflows, building on my existing 3D cardiac MRI experience.</p><span class="world-state">CURRENT DIRECTION / ACTIVE STUDY</span></div></article>
        <article class="world world-informatics" id="neuro-informatics"><div class="world-image"><img src="/assets/cinematic/systems.webp" alt="Abstract data pathways and scientific architecture" loading="lazy"><span>02 / 04</span></div><div class="world-copy"><p class="eyebrow">MAKING COMPLEX DATA USEFUL</p><h3>NEURO<br><em>INFORMATICS.</em></h3><p>Exploring neural data integration, provenance, statistical analysis and machine learning methods that make scientific conclusions more reproducible.</p><span class="world-state">CURRENT DIRECTION / ACTIVE STUDY</span></div></article>
        <article class="world world-genomics" id="neuro-genomics"><div class="world-image"><img src="/assets/cinematic/genomics.webp" alt="Dark metallic DNA helix and molecular structures" loading="lazy"><span>03 / 04</span></div><div class="world-copy"><p class="eyebrow">FROM GENES TO CIRCUITS</p><h3>BRAIN<br><em>GENOMICS.</em></h3><p>Studying genetic variation, gene expression and molecular pathways that shape the nervous system, with an eye toward computational biology.</p><span class="world-state">CURRENT DIRECTION / ACTIVE STUDY</span></div></article>
        <article class="world world-pharma" id="neuro-pharmacology"><div class="world-image"><img src="/assets/cinematic/synapse.webp" alt="Scientific visualization of a synaptic connection" loading="lazy"><span>04 / 04</span></div><div class="world-copy"><p class="eyebrow">MOLECULES, MECHANISMS, MEANING</p><h3>NEURO<br><em>PHARMACOLOGY.</em></h3><p>Learning how drugs interact with neural pathways and how rigorous computational models could support future psychiatric research.</p><span class="world-state">CURRENT DIRECTION / ACTIVE STUDY</span></div></article>
      </div>
    </section>

    <section class="scene toolchain-scene" id="toolchain" aria-labelledby="toolchain-title">
      <div class="section-meta"><span>05 / THE TOOLCHAIN</span><span>CRAFTED THROUGH PRACTICE</span></div>
      <div class="toolchain-intro"><p class="eyebrow">WHAT I WORK WITH</p><h2 id="toolchain-title">A toolkit for<br><em>hard problems.</em></h2></div>
      <div class="toolchain-stage" aria-label="Engineering specialties">
        <div class="toolchain-core"><span class="core-asterisk" aria-hidden="true">✳</span><span>RESEARCH<br>ENGINEERING</span></div>
        <div class="tool-node node-one"><span>01 / DEEP LEARNING</span><strong>PyTorch<br>MONAI<br>TensorFlow</strong></div>
        <div class="tool-node node-two"><span>02 / LLM SYSTEMS</span><strong>Transformers<br>Fine-tuning<br>Hugging Face</strong></div>
        <div class="tool-node node-three"><span>03 / AGENTS & RETRIEVAL</span><strong>LangGraph<br>RAG<br>LangSmith</strong></div>
        <div class="tool-node node-four"><span>04 / SOFTWARE</span><strong>Python<br>FastAPI<br>Docker · Git</strong></div>
        <div class="tool-node node-five"><span>05 / DATA & EVALUATION</span><strong>Statistics<br>SQL<br>Reproducible ML</strong></div>
      </div>
      <div class="toolchain-bottom"><p>Good research software combines clear questions, reliable tools, careful evaluation and respect for uncertainty.</p><a class="underlined-link" href="/skills/">EXPLORE THE FULL SKILLS ARCHIVE <span aria-hidden="true">↗</span></a></div>
    </section>

    <section class="scene work-scene" id="work" aria-labelledby="work-title">
      <div class="section-meta"><span>06 / SELECTED WORK</span><span>FIVE STUDIES FROM THE FIELD</span></div>
      <div class="work-opening"><p class="eyebrow">RESEARCH BUILT, TESTED & DOCUMENTED</p><h2 id="work-title">THE WORK<br><em>BEHIND THE</em><br>QUESTIONS.</h2><p>Five projects from applied AI, medical imaging, research software and behavioral data analysis. Every study links to the source and documents its limits.</p></div>
      <div class="project-gallery" aria-label="Five featured case studies">
        <div class="project-gallery-perspective">
        <!-- AUTO:HOME_PROJECTS:START -->
        <!-- AUTO:HOME_PROJECTS:END -->
        </div>
      </div>
      <div class="work-outro"><span>01—05 / SELECTED WORK</span><a class="underlined-link" href="/projects/">VIEW ALL PROJECTS AND ARCHIVED WORK <span aria-hidden="true">↗</span></a></div>
    </section>

    <section class="scene contact-scene" id="contact" aria-labelledby="contact-title">
      <div class="contact-background" aria-hidden="true"><img src="/assets/cinematic/architecture.webp" alt="" loading="lazy"></div>
      <div class="section-meta"><span>07 / AN OPEN INVITATION</span><span>THE STORY CONTINUES</span></div>
      <div class="contact-body"><p class="eyebrow">SOMETHING INTERESTING IN MIND?</p><h2 id="contact-title">LET'S MAKE<br><em>THE NEXT</em><br>DISCOVERY.</h2><p>Building something in AI, research software or computational neuroscience? I'd like to hear what you're working on.</p><a class="contact-primary" href="https://www.linkedin.com/in/seyyed-arad-hosseini-moghaddam/" target="_blank" rel="noopener noreferrer">START A CONVERSATION <span aria-hidden="true">↗</span></a></div>
      <div class="contact-footer"><span>ARAD HOSSEINI MOGHADDAM / 2026</span><nav aria-label="External profiles"><a href="https://github.com/aradmanamnaoon" target="_blank" rel="noopener noreferrer me">GITHUB ↗</a><a href="https://huggingface.co/aradmanamnaoon" target="_blank" rel="noopener noreferrer me">HUGGING FACE ↗</a><a href="https://orcid.org/0009-0003-0946-395X" target="_blank" rel="noopener noreferrer me">ORCID ↗</a><a href="https://www.linkedin.com/in/seyyed-arad-hosseini-moghaddam/" target="_blank" rel="noopener noreferrer me">LINKEDIN ↗</a></nav><a href="#top">BACK TO TOP ↑</a></div>
    </section>
  </main>
  <script src="/assets/js/site-config.js" defer></script>
  <script src="/assets/vendor/gsap.min.js" defer></script>
  <script src="/assets/vendor/ScrollTrigger.min.js" defer></script>
  <script src="/assets/js/cinematic.js?v=20261111-1" defer></script>
</body>
</html>
'''


def main() -> None:
    (ROOT / "index.html").write_text(HOME, encoding="utf-8")
    print("Wrote", ROOT / "index.html", len(HOME), "characters")


if __name__ == "__main__":
    main()
