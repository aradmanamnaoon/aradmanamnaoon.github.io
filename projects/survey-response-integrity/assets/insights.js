/* English-only; reference grid/pointer/reveal/progress/orbit patterns retained.
   New components: aggregated chart controls, tooltip/zoom, searchable dictionary. */
(() => {
'use strict';
const $=id=>document.getElementById(id);const root=document.documentElement,body=document.body;
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');const fine=window.matchMedia('(hover: hover) and (pointer: fine)');
const DATA=window.PROJECT_DATA||{};const fmt=n=>Number(n).toLocaleString('en-US');
function setupDots(){if(!fine.matches||reduced.matches)return;let raf=0,x=-1000,y=-1000;const paint=()=>{raf=0;if(document.hidden)return;body.style.setProperty('--dot-pointer-x',x+'px');body.style.setProperty('--dot-pointer-y',y+'px')};const clear=()=>{body.classList.remove('dots-active');if(raf)cancelAnimationFrame(raf);raf=0};window.addEventListener('pointermove',e=>{if(e.pointerType==='touch')return;x=e.clientX;y=e.clientY;body.classList.add('dots-active');if(!raf)raf=requestAnimationFrame(paint)},{passive:true});document.addEventListener('pointerleave',clear);window.addEventListener('blur',clear);document.addEventListener('visibilitychange',()=>{if(document.hidden)clear()})}
function progress(){let raf=0;const update=()=>{raf=0;const total=Math.max(1,root.scrollHeight-innerHeight);if($('pageProgress'))$('pageProgress').style.transform=`scaleX(${Math.min(1,scrollY/total)})`};const queue=()=>{if(!raf)raf=requestAnimationFrame(update)};window.addEventListener('scroll',queue,{passive:true});window.addEventListener('resize',queue,{passive:true});update()}
function reveals(){const nodes=document.querySelectorAll('.reveal');if(reduced.matches||!('IntersectionObserver'in window))return;root.classList.add('motion-ready');const ob=new IntersectionObserver(ee=>{for(const e of ee){if(e.isIntersecting){e.target.classList.add('visible');ob.unobserve(e.target)}}},{rootMargin:'0px 0px -20px 0px',threshold:.08});nodes.forEach(e=>ob.observe(e))}
function patternField(){const el=$('patternField');if(!el)return;const count=86,fragment=document.createDocumentFragment();for(let i=0;i<count;i++){const a=i*137.507764*Math.PI/180,r=13+Math.sqrt((i+1)/count)*34,node=document.createElement('span');node.style.left=50+Math.cos(a)*r+'%';node.style.top=50+Math.sin(a)*r+'%';node.style.setProperty('--delay',i%7);node.style.setProperty('--duration',4+i%5);node.style.setProperty('--fade',.3+(i%5)*.13);fragment.append(node)}el.append(fragment)}
function setupComparison(){const btns=[...document.querySelectorAll('.switch[data-mode]')];const entries=DATA.integrity||{};const update=mode=>{let q=entries['comparison_'+mode];if(!q)return;$('differenceValue').textContent=fmt(q.value);$('differenceCaption').textContent=q.label;const reading=$('comparisonInterpretation'),activeButton=btns.find(b=>b.dataset.mode===mode);if(reading&&activeButton)reading.textContent=activeButton.dataset.reading||'';btns.forEach(b=>{let active=b.dataset.mode===mode;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});const max=Math.max(entries.comparison_a?.value||0,entries.comparison_b?.value||0,1);for(const k of ['a','b']){const e=entries['comparison_'+k];$('bar'+k.toUpperCase()).style.width=(e.value/max*100).toFixed(2)+'%';$('barLabel'+k.toUpperCase()).textContent=e.label;$('barValue'+k.toUpperCase()).textContent=fmt(e.value)}};btns.forEach(b=>b.addEventListener('click',()=>update(b.dataset.mode)));update('a')}
const tips=$('tooltip');function showTip(el,text){if(!tips)return;tips.textContent=text;tips.hidden=false;const r=el.getBoundingClientRect(),w=260;tips.style.left=Math.max(8,Math.min(innerWidth-w-8,r.left+r.width/2-80))+'px';tips.style.top=Math.min(innerHeight-72,Math.max(8,r.bottom+8))+'px'}function hideTip(){if(tips)tips.hidden=true}
function installTooltips(container){if(!container)return;container.querySelectorAll('[data-tip]').forEach(el=>{el.addEventListener('mouseenter',()=>showTip(el,el.dataset.tip));el.addEventListener('mouseleave',hideTip);el.addEventListener('focus',()=>showTip(el,el.dataset.tip));el.addEventListener('blur',hideTip);el.addEventListener('touchstart',()=>showTip(el,el.dataset.tip),{passive:true})})}
function charts(){const bars=DATA.bars||[],filter=$('chartFilter'),target=$('qualityChart');function render(){let visible=filter?.value==='top'?bars.filter(x=>x.value===Math.max(...bars.map(x=>x.value))):bars;const max=Math.max(...visible.map(x=>x.value),1);target.replaceChildren();for(const b of visible){const row=document.createElement('div');row.className='chart-bar';row.tabIndex=0;row.dataset.tip=b.label+': '+fmt(b.value)+' records or cells as labeled';row.setAttribute('role','img');row.setAttribute('aria-label',row.dataset.tip);const title=document.createElement('div');title.className='bar-title';const label=document.createElement('span');label.textContent=b.label;const count=document.createElement('strong');count.textContent=fmt(b.value);title.append(label,count);const track=document.createElement('div');track.className='bar-track';const fill=document.createElement('div');fill.className='bar-fill';fill.style.width=(100*b.value/max)+'%';track.append(fill);row.append(title,track);target.append(row)}installTooltips(target)}filter?.addEventListener('change',render);render()}
function matrix(){
 const info=DATA.heatmap||{},labels=info.labels||[],cells=info.cells||[];
 const grid=$('heatmap');if(!grid)return;
 grid.replaceChildren();if(labels.length!==4||cells.length!==4){grid.textContent='Correlation matrix unavailable.';return;}
 grid.style.gridTemplateColumns='minmax(0,1.4fr) repeat(4,minmax(0,1fr))';
 const corner=document.createElement('span');corner.className='heat-label';corner.textContent='Spearman ρ';grid.append(corner);
 for(const label of labels){const el=document.createElement('span');el.className='heat-label';el.textContent=label;el.title=label;grid.append(el);}
 for(let i=0;i<4;i++){
  const row=document.createElement('span');row.className='heat-label heat-label-row';row.textContent=labels[i];grid.append(row);
  for(let j=0;j<4;j++){
   const obj=cells?.[i]?.[j],v=obj?.rho;
   const box=document.createElement('button');box.type='button';box.className='heat-cell';
   box.textContent=Number.isFinite(v)?(v>=0?'+':'')+Number(v).toFixed(2):'N/A';
   if(Number.isFinite(v))box.style.background=`rgba(125,180,240,${Math.min(.66,Math.abs(v)*.65+.08).toFixed(3)})`;
   box.dataset.tip=labels[i]+' vs '+labels[j]+': exploratory Spearman rho = '+(Number.isFinite(v)?v.toFixed(3):'not estimable')+', n='+(obj?.n??0);
   box.setAttribute('aria-label',box.dataset.tip);grid.append(box);
  }
 }
 installTooltips(grid);const z=$('zoomModal');
 function zoom(){if(!z)return;const clone=grid.cloneNode(true);clone.id='heatmapZoom';const existing=z.querySelector('.heatmap');if(existing)existing.replaceWith(clone);z.hidden=false;document.body.style.overflow='hidden';installTooltips(clone);$('zoomClose')?.focus()}
 $('zoomOpen')?.addEventListener('click',zoom);
 function close(){z.hidden=true;document.body.style.overflow='';hideTip();$('zoomOpen')?.focus()}
 $('zoomClose')?.addEventListener('click',close);z?.addEventListener('click',e=>{if(e.target===z)close()});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!z.hidden)close()});
}
function dictionary(){
 const input=$('variableSearch'),out=$('dictionaryItems'),status=$('searchStatus');
 if(!input||!out||!status)return;
 const dict=DATA.dictionary||[];
 const render=()=>{
  const q=input.value.toLowerCase().trim();
  const filtered=q?dict.filter(d=>[d.variable,d.type,d.description,d.negative_values,d.coded_values].join(' ').toLowerCase().includes(q)):dict;
  const maxShown=40;
  out.replaceChildren();
  for(const d of filtered.slice(0,maxShown)){
   const row=document.createElement('div');row.className='dictionary-item';
   const trigger=document.createElement('button');trigger.className='dictionary-trigger';trigger.type='button';trigger.setAttribute('aria-expanded','false');
   const name=document.createElement('strong');name.textContent=d.variable;
   const category=document.createElement('span');category.textContent=d.type+(d.null_count?' · '+d.null_count+' nulls':'');
   const arrow=document.createElement('span');arrow.textContent='+';arrow.className='dictionary-chevron';arrow.setAttribute('aria-hidden','true');
   trigger.append(name,category,arrow);
   const detail=document.createElement('div');detail.className='dictionary-detail';detail.hidden=true;
   const safe=(val)=>String(val??'Not supplied');
   for(const [label,value] of [['Description',d.description],['Recorded codes',d.coded_values],['Observed special codes',d.negative_values]]){
    const text=document.createElement('p');const strong=document.createElement('strong');strong.textContent=label+': ';
    text.append(strong,document.createTextNode(safe(value)||'None recorded'));detail.append(text);
   }
   trigger.addEventListener('click',()=>{const opening=detail.hidden;detail.hidden=!opening;trigger.setAttribute('aria-expanded',String(opening));arrow.textContent=opening?'−':'+'});
   row.append(trigger,detail);out.append(row);
  }
  status.textContent=filtered.length+' of '+dict.length+' fields match'+(filtered.length>maxShown?' · showing first '+maxShown:'');
 };
 input.addEventListener('input',render);render();
}
$('themeToggle')?.addEventListener('click',()=>{root.dataset.theme=root.dataset.theme==='light'?'dark':'light';try{localStorage.setItem('portfolio-theme',root.dataset.theme)}catch(e){}});
try{root.dataset.theme=localStorage.getItem('portfolio-theme')==='light'?'light':'dark'}catch(e){}
patternField();progress();reveals();setupDots();setupComparison();charts();matrix();dictionary();
})();


/* Incremental UI/UX review enhancements. Intentionally separate from existing data renderer. */
(() => {
'use strict';
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const desktop=matchMedia('(min-width: 741px) and (hover: hover) and (pointer: fine)');
const ease=t=>1-Math.pow(1-t,4);
const menu=document.getElementById('mobileNavToggle'), nav=document.getElementById('mobilePageNav');
function closeMenu(){if(!menu||!nav)return;nav.hidden=true;menu.setAttribute('aria-expanded','false');menu.setAttribute('aria-label','Open section menu')}
menu?.addEventListener('click',()=>{const isOpen=nav.hidden;nav.hidden=!isOpen;menu.setAttribute('aria-expanded',String(isOpen));menu.setAttribute('aria-label',isOpen?'Close section menu':'Open section menu')});
nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav&&!nav.hidden){closeMenu();menu.focus()}});
document.addEventListener('pointerdown',e=>{if(nav&&!nav.hidden&&!nav.contains(e.target)&&!menu.contains(e.target))closeMenu()});
// Reveal counters only once; the original markup remains the no-JS and reduced-motion result.
const counters=[...document.querySelectorAll('.finding .metric-numeral,.finding strong')];
function animateCounter(el){if(el.dataset.counterPlayed)return;el.dataset.counterPlayed='true';const initial=el.textContent.trim(), m=initial.match(/^([\d,]+(?:\.\d+)?)(%?)$/);if(!m||reduced.matches)return;
 const target=Number(m[1].replaceAll(',','')),suffix=m[2],decimals=m[1].includes('.')?m[1].split('.')[1].length:0;
 if(!Number.isFinite(target))return;
 const format=x=>x.toLocaleString('en-US',{minimumFractionDigits:decimals,maximumFractionDigits:decimals})+suffix;
 const start=performance.now();
 const frame=now=>{const t=Math.min(1,(now-start)/750);el.textContent=format(t>=1?target:target*ease(t));if(t<1)requestAnimationFrame(frame);else el.textContent=initial};
 requestAnimationFrame(frame);
}
if('IntersectionObserver'in window){const ob=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting){animateCounter(e.target);ob.unobserve(e.target)}})},{threshold:.2});counters.forEach(n=>ob.observe(n))}else counters.forEach(animateCounter);
// Stagger existing child grids without changing their layout or DOM hierarchy.
const staggerNodes=[...document.querySelectorAll('.finding-grid,.insight-cards,.workflow,.data-tools,.lab-content,.download-list')];
if(!reduced.matches&&'IntersectionObserver'in window){
 staggerNodes.forEach(e=>e.classList.add('reveal-stagger'));
 const staggerObs=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');staggerObs.unobserve(e.target)}}),{threshold:.05});
 staggerNodes.forEach(e=>staggerObs.observe(e));
}
const limits=document.querySelector('.limit-list');
if(limits&&'IntersectionObserver'in window&&!reduced.matches){const ob=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){limits.classList.add('limits-entered');ob.disconnect()}}),{threshold:.05});ob.observe(limits)}else limits?.classList.add('limits-entered');
const chart=document.getElementById('qualityChart');
if(chart&&!reduced.matches&&'IntersectionObserver'in window){
 const ob=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){chart.classList.add('chart-entered');ob.disconnect()}}),{threshold:.05});ob.observe(chart);
}else chart?.classList.add('chart-entered');
const chartFilter=document.getElementById('chartFilter');
chartFilter?.addEventListener('change',()=>{if(reduced.matches||!chart)return;chart.animate([{opacity:.35,transform:'translateY(4px)'},{opacity:1,transform:'none'}],{duration:400,easing:'cubic-bezier(.22,1,.36,1)'});});
// Pointer-follow tooltip for hover; keyboard/touch remain anchored to the target.
const tooltip=document.getElementById('tooltip');
function positionTip(x,y){if(!tooltip||tooltip.hidden)return;const b=tooltip.getBoundingClientRect();tooltip.style.left=Math.max(8,Math.min(innerWidth-b.width-8,x+12))+'px';tooltip.style.top=Math.max(8,Math.min(innerHeight-b.height-8,y+16))+'px'}
document.addEventListener('pointermove',e=>{if(e.pointerType==='mouse'&&tooltip&&!tooltip.hidden&&e.target.closest('[data-tip]'))positionTip(e.clientX,e.clientY)},{passive:true});
document.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse'&&tooltip&&!e.target.closest('[data-tip]'))tooltip.hidden=true},{passive:true});
window.addEventListener('scroll',()=>{if(tooltip)tooltip.hidden=true},{passive:true});
// Enlarge and pan the zoomed heatmap. Keyboard arrows continue to work in its scroll container.
const modal=document.getElementById('zoomModal'), zoomBtn=document.getElementById('zoomOpen');
const pan=modal?.querySelector('.zoom-pan');let zoom=1;
function setZoom(v){zoom=Math.max(1,Math.min(2.5,v));if(pan){pan.style.setProperty('--zoom-width',(zoom*100)+'%');pan.setAttribute('aria-label',`Pan correlation chart, zoom ${Math.round(zoom*100)} percent`)}}
modal?.querySelectorAll('[data-zoom]').forEach(btn=>btn.addEventListener('click',()=>setZoom(btn.dataset.zoom==='in'?zoom+.25:btn.dataset.zoom==='out'?zoom-.25:1)));
zoomBtn?.addEventListener('click',()=>{setZoom(1);pan?.scrollTo(0,0);pan?.focus()});
let x=0,y=0,left=0,top=0,drag=false;
pan?.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse'||e.button!==0||e.target.closest('button'))return;drag=true;x=e.clientX;y=e.clientY;left=pan.scrollLeft;top=pan.scrollTop;pan.setPointerCapture(e.pointerId)});
pan?.addEventListener('pointermove',e=>{if(drag){pan.scrollLeft=left-(e.clientX-x);pan.scrollTop=top-(e.clientY-y)}});
pan?.addEventListener('pointerup',()=>drag=false);pan?.addEventListener('pointercancel',()=>drag=false);
modal?.addEventListener('keydown',e=>{if(e.key!=='Tab'||modal.hidden)return;const nodes=[...modal.querySelectorAll('button,[tabindex="0"]')].filter(n=>n.offsetParent!==null);if(!nodes.length)return;const a=nodes[0],b=nodes[nodes.length-1];if(e.shiftKey&&document.activeElement===a){e.preventDefault();b.focus()}else if(!e.shiftKey&&document.activeElement===b){e.preventDefault();a.focus()}});
// Section anchors: smooth existing scroll, indicate arrival without blocking content.
document.querySelectorAll('a[href^="#"]').forEach(a=>{a.addEventListener('click',e=>{const id=a.getAttribute('href')?.slice(1),section=id&&document.getElementById(id);if(!section||!section.querySelector('.section-heading')||reduced.matches)return;e.preventDefault();section.scrollIntoView({behavior:'smooth',block:'start'});history.replaceState(null,'','#'+id);section.classList.add('target-pulse');section.addEventListener('animationend',()=>section.classList.remove('target-pulse'),{once:true});setTimeout(()=>section.classList.remove('target-pulse'),480)})});
// Perceptually small (<4px) desktop-only effect, single frame scheduled and only first 300px.
let raf=0;function moveHero(){raf=0;if(!desktop.matches||reduced.matches){document.documentElement.style.setProperty('--hero-shift','0px');return}document.documentElement.style.setProperty('--hero-shift',(Math.min(300,scrollY)/300*4).toFixed(2)+'px')}
window.addEventListener('scroll',()=>{if(scrollY<=350&&!raf)raf=requestAnimationFrame(moveHero)},{passive:true});moveHero();
// Feedback indicates a click, not a confirmed successful download. Native download remains immediate.
document.querySelectorAll('a[download]').forEach(a=>a.addEventListener('click',()=>{if(reduced.matches)return;a.classList.remove('download-feedback');void a.offsetWidth;a.classList.add('download-feedback');const previous=a.textContent;const textNode=[...a.childNodes].find(n=>n.nodeType===Node.TEXT_NODE);if(textNode)textNode.textContent='✓ '+previous.trim();setTimeout(()=>{a.classList.remove('download-feedback');if(textNode)textNode.textContent=previous},300)}));
})();
