/* Lightweight, accessible live search. The index is fetched only once and cached
 * in memory; results are always created as text nodes, not interpolated HTML.
 */
(() => {
 'use strict';
 const input=document.getElementById('site-search');
 const results=document.getElementById('search-results');
 const status=document.getElementById('search-status');
 const form=input?.closest('form');
 if(!input||!results||!status||!form)return;
 const wrap=results.closest('.utility-results');
 const recentKey='arad-recent-search-v1';
 let index=null, pending=null, debounce=0;
 const recent=(()=>{try{return JSON.parse(localStorage.getItem(recentKey)||'[]');}catch(_){return [];}})();
 const recentBox=document.createElement('div');recentBox.className='utility-hints';recentBox.setAttribute('aria-label','Recent searches');
 form.after(recentBox);
 function drawRecent(){
   recentBox.replaceChildren();
   if(!recent.length)return;
   const label=document.createElement('span');label.textContent='Recent:';recentBox.append(label);
   recent.slice(0,4).forEach(term=>{
     const chip=document.createElement('button');chip.type='button';chip.className='hub-secondary-button';chip.textContent=term;
     chip.addEventListener('click',()=>{input.value=term;run(term);});recentBox.append(chip);
   });
   const clear=document.createElement('button');clear.type='button';clear.className='hub-secondary-button';clear.textContent='Clear history';
   clear.addEventListener('click',()=>{recent.splice(0);try{localStorage.removeItem(recentKey)}catch(_){}drawRecent();});
   recentBox.append(clear);
 }
 drawRecent();
 function fetchIndex(){
   if(index)return Promise.resolve(index);
   if(!pending)pending=fetch('/search-index.json').then(r=>{if(!r.ok)throw Error('Search index unavailable');return r.json();}).then(rows=>{
     if(!Array.isArray(rows))throw Error('Invalid search index');
     index=rows;return rows;
   }).catch(e=>{pending=null;throw e});
   return pending;
 }
 function skeleton(){
   results.replaceChildren();
   wrap.dataset.loading='true';
   for(let i=0;i<3;i++){const box=document.createElement('div');box.className='search-skeleton';box.setAttribute('aria-hidden','true');results.append(box);}
 }
 function score(entry,words){
   const title=String(entry.title||'').toLocaleLowerCase();
   const terms=String(entry.terms||'').toLocaleLowerCase();
   const summary=String(entry.summary||'').toLocaleLowerCase();
   return words.reduce((n,word)=>n+(title.includes(word)?4:0)+(terms.includes(word)?2:0)+(summary.includes(word)?1:0),0);
 }
 let serial=0;
 async function run(query, updateUrl=true){
   query=query.trim().slice(0,120);
   input.value=query;
   const current=++serial;
   if(updateUrl){
     const next=query?'/search/?q='+encodeURIComponent(query):'/search/';
     try{history.replaceState(null,'',next)}catch(_){}
   }
   if(!query){wrap.dataset.loading='false';results.replaceChildren();status.textContent='Enter a term to search the portfolio.';return;}
   status.textContent='Searching…';skeleton();
   try{
     const entries=await fetchIndex();
     if(current!==serial)return;
     const words=query.toLocaleLowerCase().split(/\s+/).filter(Boolean).slice(0,8);
     const found=entries.map(entry=>({entry,rank:score(entry,words)})).filter(x=>x.rank>0).sort((a,b)=>b.rank-a.rank).slice(0,60);
     results.replaceChildren();wrap.dataset.loading='false';
     status.textContent=found.length?found.length+' result'+(found.length===1?'':'s')+' for “'+query+'”.':
       'No results for “'+query+'”. Try medical imaging, Persian NLP, or statistics.';
     found.forEach(item=>{
       const link=document.createElement('a');link.className='utility-result';link.href=item.entry.url;
       const title=document.createElement('strong');title.textContent=item.entry.title;
       const summary=document.createElement('span');summary.textContent=item.entry.summary;
       link.append(title,summary);results.append(link);
     });
     if(!recent.includes(query)){recent.unshift(query);recent.splice(4);}
     try{localStorage.setItem(recentKey,JSON.stringify(recent))}catch(_){}
     drawRecent();
   }catch(_){
     if(current!==serial)return;
     results.replaceChildren();wrap.dataset.loading='false';
     status.textContent='Search index unavailable right now. Use the navigation links below.';
   }
 }
 form.addEventListener('submit',event=>{event.preventDefault();clearTimeout(debounce);run(input.value);});
 input.addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(()=>run(input.value),220);});
 input.addEventListener('search',()=>{clearTimeout(debounce);run(input.value);});
 window.addEventListener('popstate',()=>run(new URLSearchParams(location.search).get('q')||'',false));
 const initial=new URLSearchParams(location.search).get('q')||'';
 if(initial)run(initial,false);
})();
