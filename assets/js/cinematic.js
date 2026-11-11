/* Cinematic portfolio motion. Content stays readable with JS or media disabled. */
(() => {
  "use strict";

  const doc = document;
  const root = doc.documentElement;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const narrow = window.matchMedia("(max-width: 800px)");
  const saveData = navigator.connection?.saveData === true;
  const lowPower = reduce.matches || saveData;
  const film = doc.querySelector("#hero-film");
  const loader = doc.querySelector("#site-loader");
  const nav = doc.querySelector("#site-nav");
  const toggle = doc.querySelector("#menu-toggle");
  const progress = doc.querySelector("#reading-progress");
  const links = [...doc.querySelectorAll('.nav a[href^="#"]')];
  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  if ("serviceWorker" in navigator &&
      (location.protocol === "https:" || ["localhost", "127.0.0.1"].includes(location.hostname))) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/service-worker.js").catch(() => {});
    }, { once: true });
  }

  // The overlay is decorative. A short maximum ensures a broken script or asset
  // can never indefinitely block content or keyboard input.
  const dismissLoader = () => loader?.classList.add("is-done");
  if (lowPower) dismissLoader();
  else {
    window.setTimeout(dismissLoader, 820);
    window.addEventListener("pageshow", dismissLoader, { once: true });
  }

  const closeMenu = () => {
    nav?.setAttribute("data-open", "false");
    toggle?.setAttribute("aria-expanded", "false");
    toggle?.setAttribute("aria-label", "Open menu");
  };
  toggle?.addEventListener("click", () => {
    const willOpen = toggle.getAttribute("aria-expanded") !== "true";
    nav?.setAttribute("data-open", String(willOpen));
    toggle.setAttribute("aria-expanded", String(willOpen));
    toggle.setAttribute("aria-label", willOpen ? "Close menu" : "Open menu");
  });
  nav?.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });
  doc.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
      toggle?.focus();
    }
  });
  window.addEventListener("resize", () => {
    if (!narrow.matches) closeMenu();
  }, { passive: true });

  const updateProgress = () => {
    if (!progress) return;
    const distance = doc.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = (distance > 0 ? Math.min(100, window.scrollY / distance * 100) : 0) + "%";
  };
  window.addEventListener("scroll", updateProgress, { passive: true });
  window.addEventListener("resize", updateProgress, { passive: true });
  updateProgress();

  // Media plays when visible and the user allows movement. Respect data-saving
  // preferences, invalid/corrupt sources, and modern autoplay restrictions.
  if (film && !lowPower) {
    let isVisible = true;
    const startFilm = () => {
      if (!isVisible || doc.hidden) return;
      film.play().catch(() => {
        film.style.opacity = "0"; // poster/CSS frame remains visible
      });
    };
    const observer = new IntersectionObserver((entries) => {
      isVisible = entries[0]?.isIntersecting ?? false;
      if (isVisible) startFilm();
      else film.pause();
    }, { threshold: 0.02 });
    observer.observe(film);
    film.addEventListener("error", () => { film.style.opacity = "0"; });
    doc.addEventListener("visibilitychange", () => {
      if (doc.hidden) film.pause();
      else startFilm();
    });
    startFilm();
  } else if (film) {
    film.removeAttribute("autoplay");
    film.pause();
    film.style.opacity = "0";
  }

  const chapters = [...doc.querySelectorAll("main section[id]")];
  if ("IntersectionObserver" in window) {
    const activeObserver = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach((a) => {
          if (a.getAttribute("href") === "#" + entry.target.id) {
            a.setAttribute("aria-current", "location");
          } else a.removeAttribute("aria-current");
        });
      }
    }, { rootMargin: "-30% 0px -55% 0px", threshold: 0 });
    chapters.forEach(section => activeObserver.observe(section));
  }

  // All important content is in the DOM before any motion is registered.
  if (lowPower || !gsap || !ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);
  const mm = gsap.matchMedia();

  // A purposeful, three-beat typographic arrival.
  gsap.from(".headline-line > span", {
    yPercent: 112, duration: 1.35, ease: "power4.out", stagger: 0.15, delay: 0.3, clearProps: "transform"
  });
  gsap.from(".hero-overline,.hero-bottom,.hero-coordinate", {
    y: 22, autoAlpha: 0, duration: 1.1, ease: "power2.out", stagger: 0.14, delay: 0.45,
    clearProps: "transform,opacity,visibility"
  });

  mm.add("(min-width: 801px) and (prefers-reduced-motion: no-preference)", () => {
    gsap.to(".hero-title-wrap", {
      yPercent: -26, scale: .93, opacity: .42, ease: "none",
      scrollTrigger: { trigger: ".hero-scene", start: "top top", end: "bottom top", scrub: 1 }
    });
    gsap.to(".hero-film video", {
      scale: 1.2, ease: "none",
      scrollTrigger: { trigger: ".hero-scene", start: "top top", end: "bottom top", scrub: 1.3 }
    });
    gsap.fromTo(".identity-portrait", { y: 100, rotation: 9 }, {
      y: -35, rotation: 2.5, ease: "none",
      scrollTrigger: { trigger: ".identity-scene", start: "top bottom", end: "bottom top", scrub: 1.3 }
    });
    gsap.fromTo(".intersection-visual", { rotate: -12, scale: .72, opacity: .4 }, {
      rotate: 7, scale: 1.07, opacity: 1, ease: "none",
      scrollTrigger: { trigger: ".intersection-scene", start: "top bottom", end: "bottom top", scrub: 1.2 }
    });
    gsap.to(".intersection-shutter", {
      rotate: 44, ease: "none",
      scrollTrigger: { trigger: ".intersection-scene", start: "top bottom", end: "bottom top", scrub: 1.2 }
    });
    gsap.utils.toArray(".world").forEach((scene, i) => {
      const visual = scene.querySelector(".world-image img");
      const copy = scene.querySelector(".world-copy");
      gsap.fromTo(visual, { scale: 1.14, yPercent: -6 }, {
        scale: 1, yPercent: 6, ease: "none",
        scrollTrigger: { trigger: scene, start: "top bottom", end: "bottom top", scrub: 1 }
      });
      gsap.from(copy, {
        x: i % 2 ? -80 : 80, autoAlpha: 0, duration: 1.15, ease: "power3.out",
        scrollTrigger: { trigger: scene, start: "top 72%", toggleActions: "play none none reverse" }
      });
    });
    gsap.utils.toArray(".tool-node").forEach((node, i) => {
      gsap.fromTo(node, { y: i % 2 ? 115 : -110, rotateZ: i % 2 ? 9 : -9, opacity: .2 }, {
        y: 0, rotateZ: 0, opacity: 1, ease: "none",
        scrollTrigger: { trigger: ".toolchain-stage", start: "top 95%", end: "bottom 25%", scrub: .8 }
      });
    });
    gsap.utils.toArray(".project-plane").forEach((plane, i) => {
      const from = { xPercent: i % 2 ? 24 : -24, y: 130, rotateY: i % 2 ? 25 : -25, rotateZ: i % 2 ? 5 : -5, scale: .84, opacity: .18 };
      const to = { xPercent: 0, y: 0, rotateY: i % 2 ? 7 : -7, rotateZ: i % 2 ? 1.2 : -1.4, scale: 1, opacity: 1, ease: "none",
        scrollTrigger: { trigger: plane, start: "top bottom", end: "center center", scrub: .8 } };
      gsap.fromTo(plane, from, to);
    });
    gsap.to(".contact-background img", {
      yPercent: -12, scale: 1.1, ease: "none",
      scrollTrigger: { trigger: ".contact-scene", start: "top bottom", end: "bottom bottom", scrub: 1 }
    });
  });

  mm.add("(max-width: 800px) and (prefers-reduced-motion: no-preference)", () => {
    gsap.utils.toArray(".world-copy,.project-plane,.tool-node").forEach((element) => {
      gsap.from(element, {
        y: 16, duration: .55, ease: "power2.out", clearProps: "transform",
        scrollTrigger: { trigger: element, start: "top 95%", once: true }
      });
    });
  });
  gsap.utils.toArray(".identity-type,.identity-statement,.work-opening,.toolchain-intro,.contact-body").forEach((element) => {
    gsap.from(element, {
      y: 40, autoAlpha: 0, duration: 1, ease: "power3.out",
      clearProps: "transform,opacity,visibility",
      scrollTrigger: { trigger: element, start: "top 88%", once: true }
    });
  });
  window.addEventListener("load", () => ScrollTrigger.refresh(), { once: true });
  reduce.addEventListener?.("change", () => window.location.reload());
})();
