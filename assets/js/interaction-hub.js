/* Progressive site-wide interaction hub. No framework, tracking or remote assets.
 * Every control is optional; content remains accessible without JavaScript.
 */
(() => {
  'use strict';
  const root = document.documentElement;
  const prefersReduced = matchMedia('(prefers-reduced-motion: reduce)');
  const prefersDark = matchMedia('(prefers-color-scheme: dark)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const storageKey = 'arad-ui-preferences-v1';
  const settings = { theme: 'dark', sound: false };
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
    if (['dark', 'light', 'system'].includes(saved.theme)) settings.theme = saved.theme;
    settings.sound = saved.sound === true;
  } catch (_) {}
  let audioContext = null;
  const reduced = () => prefersReduced.matches;
  const save = () => { try { localStorage.setItem(storageKey, JSON.stringify(settings)); } catch (_) {} };
  const applyTheme = () => {
    const theme = settings.theme === 'system' ? (prefersDark.matches ? 'dark' : 'light') : settings.theme;
    root.dataset.theme = theme;
    root.dataset.themeSetting = settings.theme;
    const btn = document.getElementById('hub-theme');
    if (btn) {
      btn.textContent = 'Theme: ' + settings.theme;
      btn.setAttribute('aria-label', 'Theme: ' + settings.theme + '. Switch to next theme');
    }
  };
  function themeCycle() {
    const variants = ['dark', 'light', 'system'];
    settings.theme = variants[(variants.indexOf(settings.theme) + 1) % 3];
    save(); applyTheme(); toast('Theme: ' + settings.theme);
  }
  applyTheme();
  prefersDark.addEventListener?.('change', () => { if (settings.theme === 'system') applyTheme(); });

  function tone(success = true) {
    if (!settings.sound) return;
    try {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) return;
      audioContext ||= new Audio();
      if (audioContext.state === 'suspended') audioContext.resume();
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();
      osc.type = 'sine';
      osc.frequency.value = success ? 680 : 340;
      gain.gain.setValueAtTime(.0001, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(.026, audioContext.currentTime + .012);
      gain.gain.exponentialRampToValueAtTime(.0001, audioContext.currentTime + .105);
      osc.connect(gain); gain.connect(audioContext.destination);
      osc.start(); osc.stop(audioContext.currentTime + .115);
    } catch (_) { /* audio is strictly optional */ }
  }
  const toasts = document.createElement('div');
  toasts.id = 'site-toasts'; toasts.setAttribute('role', 'status');
  toasts.setAttribute('aria-live', 'polite'); toasts.setAttribute('aria-atomic', 'true');
  document.body.append(toasts);
  function toast(message, success = true) {
    const el = document.createElement('div');
    el.className = 'site-toast'; el.textContent = message;
    toasts.append(el); tone(success);
    setTimeout(() => el.remove(), 3600);
  }

  const actions = [
    {title: 'Home', subtitle: 'Introduction and featured work', url: '/'},
    {title: 'Projects', subtitle: 'Research methods, models, and evidence', url: '/projects/'},
    {title: 'Skills', subtitle: 'Tools, methods, statistics, and machine learning', url: '/skills/'},
    {title: 'Search', subtitle: 'Search the portfolio', url: '/search/'},
    {title: 'Cardiac MRI segmentation', subtitle: 'Medical AI project', url: '/projects/3d-cardiac-mri-segmentation/'},
    {title: 'Persian GPT', subtitle: '110M-parameter language model', url: '/projects/persian-gpt-from-scratch/'},
    {title: 'Research assistant', subtitle: 'LangGraph research agents', url: '/projects/multi-agent-ai-research-assistant/'},
    {title: 'Contact', subtitle: 'Get in touch', url: '/#contact'}
  ];
  const palette = document.createElement('dialog');
  palette.className = 'hub-dialog';
  palette.setAttribute('aria-label', 'Command palette');
  palette.innerHTML = '<div class="hub-dialog-head"><h2>Go to…</h2><button type="button" class="hub-close" aria-label="Close command palette">×</button></div>' +
    '<label class="hub-label" for="hub-command-search">Navigate or search</label>' +
    '<input id="hub-command-search" type="search" autocomplete="off" placeholder="Search pages, projects, or commands…" />' +
    '<div class="hub-command-results" role="listbox" aria-label="Matching commands"></div>' +
    '<p class="hub-hint">↑ / ↓ to choose · Enter to open · Esc to close</p>';
  document.body.append(palette);
  const search = palette.querySelector('input');
  const resultBox = palette.querySelector('.hub-command-results');
  let resultIndex = 0, matches = [];
  let beforeDialog = null;
  function close(dialog) {
    if (dialog.open) dialog.close();
    beforeDialog?.focus?.({preventScroll: true});
    beforeDialog = null;
  }
  palette.querySelector('.hub-close').addEventListener('click', () => close(palette));
  palette.addEventListener('click', e => { if (e.target === palette) close(palette); });
  palette.addEventListener('close', () => { beforeDialog?.focus?.({preventScroll:true}); beforeDialog = null; });
  const commands = () => actions.concat([
    {title: 'Cycle theme', subtitle: 'Dark / light / system', run: themeCycle},
    {title: 'Toggle sounds', subtitle: 'Off by default', run: soundCycle},
    {title: 'Copy page link', subtitle: 'Share the current page', run: copyPage},
    {title: 'Keyboard shortcuts', subtitle: 'Show accessibility shortcuts', run: openHelp}
  ]);
  function renderCommands() {
    const query = search.value.trim().toLocaleLowerCase();
    matches = commands().filter(a => (a.title + ' ' + a.subtitle).toLocaleLowerCase().includes(query)).slice(0, 12);
    resultIndex = Math.min(resultIndex, Math.max(0, matches.length - 1));
    resultBox.replaceChildren();
    for (let i = 0; i < matches.length; i++) {
      const a = matches[i];
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'hub-command';
      btn.setAttribute('role','option'); btn.setAttribute('aria-selected',String(i === resultIndex));
      const title = document.createElement('strong'); title.textContent = a.title;
      const sub = document.createElement('small'); sub.textContent = a.subtitle;
      btn.append(title, sub);
      btn.addEventListener('click', () => activate(i));
      resultBox.append(btn);
    }
    if (!matches.length) {
      const link = document.createElement('button'); link.className = 'hub-command'; link.type = 'button';
      link.textContent = 'Search the portfolio for “' + search.value.trim().slice(0, 80) + '”';
      link.addEventListener('click', () => { location.href = '/search/?q=' + encodeURIComponent(search.value.trim()); });
      resultBox.append(link);
    }
  }
  function selectCommand() {
    [...resultBox.querySelectorAll('[role="option"]')].forEach((node,i) => node.setAttribute('aria-selected',String(i===resultIndex)));
  }
  function activate(i) {
    const command = matches[i];
    if (!command) return;
    close(palette);
    if (command.url) location.assign(command.url);
    else command.run();
  }
  function openPalette() {
    if (!palette.showModal) return;
    beforeDialog = document.activeElement;
    search.value = ''; resultIndex = 0; renderCommands(); palette.showModal(); search.focus();
  }
  search.addEventListener('input', () => { resultIndex=0; renderCommands(); });
  search.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); resultIndex = Math.min(matches.length-1, resultIndex+1); selectCommand(); }
    if (e.key === 'ArrowUp') { e.preventDefault(); resultIndex = Math.max(0, resultIndex-1); selectCommand(); }
    if (e.key === 'Enter') { e.preventDefault(); if (matches.length) activate(resultIndex); else location.assign('/search/?q='+encodeURIComponent(search.value.trim())); }
  });

  const help = document.createElement('dialog');
  help.className = 'hub-dialog hub-help'; help.setAttribute('aria-label', 'Keyboard shortcuts');
  help.innerHTML = '<div class="hub-dialog-head"><h2>Keyboard shortcuts</h2><button type="button" class="hub-close" aria-label="Close keyboard help">×</button></div>' +
    '<dl class="hub-shortcuts"><dt>Ctrl / Cmd + K</dt><dd>Open command palette</dd>' +
    '<dt>?</dt><dd>Show this help</dd><dt>Esc</dt><dd>Close a dialog</dd>' +
    '<dt>Home</dt><dd>Scroll to page beginning</dd><dt>Tab / Shift + Tab</dt><dd>Move between controls</dd></dl>';
  document.body.append(help);
  help.querySelector('.hub-close').addEventListener('click', () => close(help));
  help.addEventListener('click', e => { if (e.target === help) close(help); });
  help.addEventListener('close',()=>{beforeDialog?.focus?.({preventScroll:true});beforeDialog=null;});
  function openHelp() {
    if (!help.showModal) return;
    beforeDialog = document.activeElement; help.showModal(); help.querySelector('.hub-close').focus();
  }
  async function copyPage() {
    try {
      await navigator.clipboard.writeText(location.href);
      toast('Page link copied');
    } catch (_) { toast('Copy unavailable in this browser', false); }
  }
  function soundCycle() {
    settings.sound = !settings.sound; save();
    const button = document.getElementById('hub-sound');
    if (button) { button.textContent = settings.sound ? 'Sound: on' : 'Sound: off'; button.setAttribute('aria-pressed', String(settings.sound)); }
    toast(settings.sound ? 'UI sounds enabled' : 'UI sounds disabled');
  }

  const rail = document.createElement('div');
  rail.className = 'interaction-rail'; rail.setAttribute('role','group'); rail.setAttribute('aria-label','Website preferences and navigation');
  rail.innerHTML = '<button id="hub-commands" type="button" aria-label="Open command palette">⌕ <span>Search</span></button>' +
    '<button id="hub-theme" type="button" aria-label="Switch theme">Theme: dark</button>' +
    '<button id="hub-sound" type="button" aria-pressed="false">Sound: off</button>' +
    '<button id="hub-shortcuts" type="button" aria-label="Keyboard shortcuts help">?</button>';
  document.body.append(rail);
  rail.querySelector('#hub-commands').addEventListener('click',openPalette);
  rail.querySelector('#hub-theme').addEventListener('click',themeCycle);
  rail.querySelector('#hub-sound').addEventListener('click',soundCycle);
  rail.querySelector('#hub-shortcuts').addEventListener('click',openHelp);
  rail.querySelector('#hub-sound').setAttribute('aria-pressed',String(settings.sound));
  rail.querySelector('#hub-sound').textContent=settings.sound?'Sound: on':'Sound: off';
  applyTheme();
  document.addEventListener('keydown', e => {
    const typing = e.target.closest?.('input, textarea, select, [contenteditable="true"]');
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); if (!palette.open) openPalette(); else close(palette); }
    else if (!typing && !e.altKey && !e.ctrlKey && !e.metaKey && e.key === '?' && !palette.open && !help.open) { e.preventDefault(); openHelp(); }
  });

  const back = document.createElement('button');
  back.type = 'button'; back.className = 'hub-back-top';
  back.setAttribute('aria-label','Back to top');
  back.title='Back to top';
  back.innerHTML='<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="20" class="hub-ring-track"/><circle cx="24" cy="24" r="20" class="hub-ring-progress"/><path d="m17 27 7-7 7 7M24 20v14" class="hub-ring-arrow"/></svg>';
  document.body.append(back);
  back.addEventListener('click', () => window.scrollTo({top:0,behavior:reduced()?'instant':'smooth'}));
  let queued = false;
  const tick = () => {
    queued = false;
    const max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    const value = Math.min(1, Math.max(0, scrollY / max));
    back.style.setProperty('--progress',String(value));
    back.classList.toggle('is-visible',scrollY > Math.max(450,innerHeight*.6));
  };
  const queue = () => { if (!queued) { queued=true; requestAnimationFrame(tick); } };
  addEventListener('scroll',queue,{passive:true});
  addEventListener('resize',queue,{passive:true}); queue();

  // Keep normal pointer and click affordances. The tiny offset follower never
  // replaces the native cursor and is disabled for touch/reduced motion.
  if (fine.matches && !reduced()) {
    const follower = document.createElement('span'); follower.className = 'hub-cursor';
    follower.setAttribute('aria-hidden','true'); document.body.append(follower);
    let px=-50,py=-50,curX=-50,curY=-50,id=0;
    function step() {
      curX+=(px-curX)*.38;curY+=(py-curY)*.38;
      follower.style.transform='translate3d('+curX+'px,'+curY+'px,0)';
      if (Math.abs(px-curX)+Math.abs(py-curY)>.4) id=requestAnimationFrame(step); else id=0;
    }
    addEventListener('pointermove', e => {
      if (e.pointerType==='touch') return;
      px=e.clientX+15;py=e.clientY+15;
      follower.classList.add('visible'); if(!id)id=requestAnimationFrame(step);
    },{passive:true});
    document.addEventListener('pointerleave',()=>follower.classList.remove('visible'));
    document.addEventListener('visibilitychange',()=>{if(document.hidden)follower.classList.remove('visible')});
    prefersReduced.addEventListener?.('change',()=>{ if(prefersReduced.matches) follower.remove(); });
  }
  const targets = document.querySelectorAll('.case-section, .utility-directory, .utility-result, .research-direction, .contact-form, img:not([loading])');
  targets.forEach(el=>{if(el.tagName==='IMG') { if(!el.closest('.hero,.hero-media')) { el.loading='lazy';el.decoding='async'; } }});
  if ('IntersectionObserver' in window && !reduced()) {
    const observed = [...document.querySelectorAll('.case-section, .utility-directory, .research-direction, .utility-results')];
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('hub-revealed');observer.unobserve(entry.target);}});
    },{threshold:.08,rootMargin:'0px 0px 45px 0px'});
    observed.forEach(el=>{el.classList.add('hub-reveal-ready');observer.observe(el)});
  }
  const field = document.querySelector('.contact-form-status');
  if (field && 'MutationObserver' in window) {
    let previous='';
    new MutationObserver(()=>{
      const state=field.dataset.state;
      if(state===previous)return;previous=state;
      if(state==='success') {toast('Message sent successfully');celebrate();}
      else if(state==='error')toast('Message could not be sent',false);
    }).observe(field,{attributes:true,attributeFilter:['data-state']});
  }
  function celebrate() {
    if(reduced())return;
    const span=document.createElement('div');span.className='hub-celebration';span.setAttribute('aria-hidden','true');
    for(let i=0;i<18;i++){const piece=document.createElement('span');piece.style.setProperty('--i',String(i));span.append(piece);}
    document.body.append(span);setTimeout(()=>span.remove(),1150);
  }
  window.SiteInteractions = Object.freeze({toast,openPalette,openHelp,copyPage,celebrate,themeCycle});
})();
