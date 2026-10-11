/* Route-aware enhancements; uses the existing project/skill engines.
 * Existing content is untouched and still works if this file never loads. */
(() => {
 'use strict';
 const path = location.pathname;
 const reduced = matchMedia('(prefers-reduced-motion: reduce)');
 const animate = () => !reduced.matches;
 const toast = (text, ok=true) => window.SiteInteractions?.toast(text,ok);
 const store=(key,fallback)=>{
   try {
     const value=JSON.parse(localStorage.getItem(key)||'null');
     return Array.isArray(value)
       ? value.filter(item=>typeof item==='string' && item.length<150).slice(0,100)
       : fallback;
   } catch(_) { return fallback; }
 };
 const save=(key,value)=>{try{localStorage.setItem(key,JSON.stringify(value));}catch(_){}};
 const button=(text,cls,label)=>{const b=document.createElement('button');b.type='button';b.className=cls;b.textContent=text;b.setAttribute('aria-label',label||text);return b};
 const heading=(text)=>{const h=document.createElement('h3');h.textContent=text;return h};
 const scrollTo=(el)=>el?.scrollIntoView({behavior:animate()?'smooth':'instant',block:'start'});
 const share=async text=>{
   try {await navigator.clipboard.writeText(text);toast('Copied to clipboard');}
   catch(_){toast('Clipboard permission unavailable',false);}
 };
 const esc=s=>String(s).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

 function home() {
   // Explore the two documented research directions, not unverified projects.
   const section=document.getElementById('about')||document.querySelector('#main');
   const destination=document.getElementById('projects');
   const hero=document.querySelector('.hero-bio,.hero-copy,.hero-content');
   if (!hero || !section) return;
   const bar=document.createElement('nav');bar.className='focus-explorer';
   bar.setAttribute('aria-label','Explore professional focus');
   const label=document.createElement('span');label.textContent='Explore focus';
   bar.append(label);
   const links=[
     ['Medical AI','/projects/3d-cardiac-mri-segmentation/'],
     ['Psychology & statistics','/skills/#statistics_and_humanities_data'],
     ['All research','/projects/#research-directions']
   ];
   links.forEach(([title,url])=>{
     const a=document.createElement('a');a.href=url;a.textContent=title;bar.append(a);
   });
   hero.insertAdjacentElement('afterend',bar);
   const socials=document.querySelectorAll('.public-proof a, .surface-card[href^="https://"]');
   socials.forEach(el=>{el.classList.add('hub-hover-float');});
   const copy=button('Copy portfolio link','hub-secondary-button','Copy current portfolio URL');
   copy.addEventListener('click',()=>share(location.origin+'/'));
   bar.append(copy);
 }

 function projects() {
   const root=document.getElementById('selected-projects');
   const container=document.getElementById('projects-paginated');
   if(!root || !container)return;
   const key='arad-saved-projects-v1';
   let saved=new Set(store(key,[]));
   const tools=document.createElement('div');tools.className='project-selection-tools';
   const savedButton=button('Saved projects: 0','hub-secondary-button','Show saved projects');
   const compareButton=button('Compare: 0 / 3','hub-secondary-button','Compare up to three projects');
   const resetButton=button('Clear saved and comparison','hub-secondary-button','Clear saved and comparison selection');
   const set=new Set();
   tools.append(savedButton,compareButton,resetButton);
   const explorer=document.getElementById('archive-explorer');
   if(explorer)explorer.insertAdjacentElement('afterend',tools);else root.prepend(tools);

   const dialog=document.createElement('dialog');dialog.className='hub-dialog project-comparison';
   dialog.setAttribute('aria-label','Project comparison');
   dialog.innerHTML='<div class="hub-dialog-head"><h2>Compare research projects</h2><button type="button" class="hub-close" aria-label="Close comparison">×</button></div><div class="project-compare-content"></div>';
   document.body.append(dialog);
   dialog.querySelector('.hub-close').addEventListener('click',()=>dialog.close());
   dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});

   function projectsData() {
     const list=window.portfolioArchive?.all?.() || [];
     return Array.isArray(list)?list:[];
   }
   function renderComparison(ids) {
     const content=dialog.querySelector('.project-compare-content');content.replaceChildren();
     const data=projectsData().filter(x=>ids.includes(x.id));
     if (!data.length){const p=document.createElement('p');p.textContent='Save a project or select up to three to compare its evidence and metrics.';content.append(p);return;}
     const grid=document.createElement('div');grid.className='project-compare-grid';
     data.forEach(project=>{
       const card=document.createElement('section');card.className='project-compare-card';
       card.append(heading(project.title));
       const desc=document.createElement('p');desc.textContent=project.description;card.append(desc);
       (project.metrics||[]).forEach(metric=>{
         const row=document.createElement('p');const strong=document.createElement('strong');
         strong.textContent=metric.value+' ';row.append(strong,document.createTextNode(metric.label));card.append(row);
       });
       const note=document.createElement('small');note.textContent=project.note||'';
       card.append(note);
       const link=document.createElement('a');
       link.href='/projects/#'+encodeURIComponent(project.id);
       link.textContent='Open project';
       link.addEventListener('click',event=>{
         event.preventDefault();
         dialog.close();
         const fragment='#'+encodeURIComponent(project.id);
         // Trigger the archive's existing paging/filters reset even when this
         // is already the current fragment. Native same-hash clicks do nothing.
         if(location.hash===fragment) window.dispatchEvent(new Event('hashchange'));
         else location.hash=fragment;
       });
       card.append(link);
       grid.append(card);
     });
     content.append(grid);
   }
   function refresh() {
     const ids=projectsData().map(x=>x.id);
     saved=new Set([...saved].filter(id=>ids.includes(id)));
     save(key,[...saved]);
     savedButton.textContent='Saved projects: '+saved.size;
     compareButton.textContent='Compare: '+set.size+' / 3';
     compareButton.disabled=set.size===0;
     container.querySelectorAll('.project[id]').forEach(card=>{
       const id=card.id;
       if(!card.querySelector('.project-save')) {
         const row=document.createElement('div');row.className='project-choice-row';
         const mark=button('Save','project-save','Save project to local shortlist');
         mark.addEventListener('click',()=>{if(saved.has(id))saved.delete(id);else saved.add(id);refresh();toast(saved.has(id)?'Project saved locally':'Project removed from saved');});
         const pick=button('Compare','project-compare-pick','Add project to comparison');
         pick.addEventListener('click',()=>{
           if(set.has(id))set.delete(id);
           else if(set.size<3)set.add(id);
           else {toast('Compare up to 3 projects',false);return;}
           refresh();
         });
         row.append(mark,pick);
         card.append(row);
       }
       const mark=card.querySelector('.project-save');
       const pick=card.querySelector('.project-compare-pick');
       mark.textContent=saved.has(id)?'★ Saved':'☆ Save';
       mark.setAttribute('aria-pressed',String(saved.has(id)));
       pick.textContent=set.has(id)?'✓ Comparing':'Compare';
       pick.setAttribute('aria-pressed',String(set.has(id)));
     });
   }
   savedButton.addEventListener('click',()=>{const ids=[...saved];renderComparison(ids);dialog.showModal?.();});
   compareButton.addEventListener('click',()=>{renderComparison([...set]);dialog.showModal?.();});
   resetButton.addEventListener('click',()=>{saved.clear();set.clear();refresh();toast('Project selections cleared');});
   addEventListener('portfolio:archive-rendered',()=>queueMicrotask(refresh));
   refresh();
 }

 function caseStudy() {
   const sections=[...document.querySelectorAll('.case-grid .case-section')];
   if(!sections.length)return;
   const main=document.querySelector('main');
   const toc=document.createElement('nav');toc.className='case-interactive-toc';
   toc.setAttribute('aria-label','Case study sections');
   const label=document.createElement('strong');label.textContent='On this page';
   toc.append(label);
   sections.forEach((section,i)=>{
     const h=section.querySelector('h2');if(!h)return;
     h.id||='case-part-'+(i+1);
     const a=document.createElement('a');a.href='#'+h.id;a.textContent=h.textContent;
     toc.append(a);
     const toggle=button('− Collapse','case-collapse','Collapse '+h.textContent);
     toggle.setAttribute('aria-expanded','true');
     const body=document.createElement('div');body.className='case-fold-body';
     [...section.children].filter(el=>el!==h && !el.classList.contains('eyebrow')).forEach(x=>body.append(x));
     section.append(toggle,body);
     toggle.addEventListener('click',()=>{
       const open=toggle.getAttribute('aria-expanded')!=='true';
       toggle.setAttribute('aria-expanded',String(open));
       toggle.textContent=open?'− Collapse':'+ Expand';
       body.hidden=!open;
     });
   });
   const tools=document.createElement('div');tools.className='case-actions';
   const print=button('Print case study','hub-secondary-button','Print or save case study as PDF');
   print.addEventListener('click',()=>window.print());
   const cite=button('Copy citation','hub-secondary-button','Copy project citation');
   cite.addEventListener('click',()=>share(document.querySelector('h1')?.textContent+' — Seyyed Arad Hosseini Moghaddam. '+location.href));
   const all=button('Expand all','hub-secondary-button','Expand all case study sections');
   all.addEventListener('click',()=>sections.forEach(sec=>{
     const t=sec.querySelector('.case-collapse'),b=sec.querySelector('.case-fold-body');
     if(t){t.textContent='− Collapse';t.setAttribute('aria-expanded','true');b.hidden=false;}
   }));
   tools.append(print,cite,all);
   main?.querySelector('.hero')?.append(tools);
   main?.querySelector('.case-grid')?.before(toc);
 }

 function utility() {
   const input=document.querySelector('.utility-search input[type=search]');
   const box=document.querySelector('.utility-directory');
   const searchForm=document.querySelector('.utility-search');
   if(input && searchForm){
     const hints=document.createElement('div');hints.className='utility-hints';
     hints.setAttribute('role','group');hints.setAttribute('aria-label','Suggested searches');
     ['medical imaging','statistics','Persian NLP','agents'].forEach(term=>{
       const chip=button(term,'hub-secondary-button','Search for '+term);
       chip.addEventListener('click',()=>{
         input.value=term;searchForm.requestSubmit?.();if(!searchForm.requestSubmit)searchForm.submit();
       });
       hints.append(chip);
     });
     searchForm.after(hints);
   }
   if(path==='/offline.html'||path==='/offline/'){
     const status=document.createElement('p');status.className='offline-status';status.setAttribute('role','status');
     const update=()=>{status.textContent=navigator.onLine?'A network connection is detected. You can retry.':'You appear to be offline. Cached pages may still work.';};
     update();window.addEventListener('online',update);window.addEventListener('offline',update);
     document.querySelector('.utility-actions')?.after(status);
   }
   if(box) {
     box.querySelectorAll('a').forEach(a=>a.classList.add('hub-hover-float'));
   }
 }

 if(path==='/'||path==='/index.html')home();
 else if(path==='/projects/'||path==='/projects')projects();
 else if(path.startsWith('/projects/')&&document.body.classList.contains('project-case-study'))caseStudy();
 else if(path.includes('search')||path.includes('404')||path.includes('offline'))utility();
})();
