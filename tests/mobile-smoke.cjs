/* Headless mobile Chromium regression tests; Node 22, no third-party packages. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),http=require('node:http');
const os=require('node:os'),path=require('node:path');
const {spawn,spawnSync}=require('node:child_process');
const {setTimeout:delay}=require('node:timers/promises');
const ROOT=path.resolve(__dirname,'..');
const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json'};
const server=http.createServer((req,res)=>{
  let uri;
  try{uri=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch(_){res.writeHead(400);res.end();return;}
  const file=path.resolve(ROOT,'.'+uri+(uri.endsWith('/')?'index.html':''));
  if(!file.startsWith(ROOT+path.sep)){res.writeHead(403);res.end();return;}
  fs.readFile(file,(err,body)=>{
    if(err){res.writeHead(404);res.end();return;}
    res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'});
    res.end(body);
  });
});
function chrome(){
  if(process.env.CHROME_BIN)return process.env.CHROME_BIN;
  for(const n of ['google-chrome','chromium','chromium-browser']){
    const r=spawnSync('which',[n],{encoding:'utf8'});if(r.status===0)return r.stdout.trim();
  }
  throw Error('Chrome missing');
}
async function until(check,label){
  for(let i=0;i<120;i++){try{if(await check())return;}catch(_){ }await delay(100);}
  throw Error('Timeout '+label);
}
function client(socket){
  let id=0;const pending=new Map();
  socket.addEventListener('message',e=>{
    const m=JSON.parse(e.data),job=pending.get(m.id);if(!job)return;
    pending.delete(m.id);m.error?job.reject(Error(JSON.stringify(m.error))):job.resolve(m.result);
  });
  return (method,params={})=>new Promise((resolve,reject)=>{
    const n=++id;pending.set(n,{resolve,reject});
    socket.send(JSON.stringify({id:n,method,params}));
    setTimeout(()=>{if(pending.has(n)){pending.delete(n);reject(Error('CDP timeout '+method));}},16000).unref();
  });
}
async function run(){
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const base='http://127.0.0.1:'+server.address().port;
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'site-mobile-'));
  const browser=spawn(chrome(),['--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',
    '--disable-background-networking','--no-proxy-server','--no-first-run',
    '--remote-debugging-port=0','--user-data-dir='+dir,'about:blank'],{stdio:'ignore'});
  let socket,send,last='startup';
  try{
    const file=path.join(dir,'DevToolsActivePort');
    await until(()=>fs.existsSync(file),'Chrome port');
    const port=Number(fs.readFileSync(file,'utf8').split('\n')[0]);
    const targets=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();
    socket=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
    await new Promise((resolve,reject)=>{
      socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});
    });
    send=client(socket);await send('Page.enable');await send('Runtime.enable');
    await send('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:5});
    async function js(expr){
      const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});
      if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));
      return r.result.value;
    }
    async function visit(route,width){
      last=route+' '+width+'px';const height=width>=768?1024:812;
      await send('Emulation.setDeviceMetricsOverride',{
        width,height,screenWidth:width,screenHeight:height,deviceScaleFactor:2,mobile:true
      });
      await send('Page.navigate',{url:base+route});
      await until(()=>js('document.readyState==="complete" && location.pathname==='+JSON.stringify(route)),last);
      await delay(120);
      const data=await js('(()=>{const h=document.querySelector("h1"),d=document.documentElement,rail=document.querySelector(".interaction-rail");const box=rail?.getBoundingClientRect();return {w:innerWidth,scroll:d.scrollWidth,h:!!h&&h.getBoundingClientRect().height>0,nav:!!document.querySelector(\'nav[aria-label="Primary navigation"], nav[aria-label="Page sections"], nav[aria-label="Research sections"]\'),rail:!!rail,left:box?.left,right:box?.right,targets:rail?[...rail.querySelectorAll("button")].map(b=>[b.getBoundingClientRect().width,b.getBoundingClientRect().height]):[]};})()');
      if(data.w!==width){
        const extra=await js('(()=>({innerWidth,outerWidth,screenWidth:screen.width,visualWidth:visualViewport?.width,clientWidth:document.documentElement.clientWidth,bodyWidth:document.body.scrollWidth,offenders:[...document.querySelectorAll("body *")].map(e=>({tag:e.tagName,cls:typeof e.className==="string"?e.className.slice(0,65):"",id:e.id,x:e.getBoundingClientRect().x,w:e.getBoundingClientRect().width,r:e.getBoundingClientRect().right,scroll:e.scrollWidth})).filter(e=>e.r>screen.width+2||e.w>screen.width+2).sort((a,b)=>a.r-b.r).slice(0,60)}))()');
        console.error('LAYOUT DIAGNOSTIC',last,JSON.stringify(extra));
      }
      assert.equal(data.w,width,'viewport metadata: '+last);
      const standalone=/^\/projects\/(emotion-appraisal-video-audit|psoriasis-wellbeing-audit|psychology-data-audit|survey-response-integrity)\/$/.test(route);
      assert.ok(data.h&&data.nav&&(data.rail||standalone),'missing essential page elements: '+last);
      assert.ok(data.scroll<=width+3,'horizontal overflow: '+last+' '+JSON.stringify(data));
      if(!standalone){
        assert.ok(data.left>=-2&&data.right<=width+2,'bottom toolbar clipped: '+last);
        assert.ok(data.targets.length===3&&data.targets.every(s=>s[0]>=44&&s[1]>=44),
          'mobile touch targets undersized: '+last);
      }
      console.log('PASS',last,'scrollWidth='+data.scroll);
    }
    const important=['/','/projects/','/skills/','/search/','/404.html','/offline.html',
      '/projects/3d-cardiac-mri-segmentation/','/projects/constellation/','/projects/persian-gpt-from-scratch/'];
    for(const width of [320,375,430,768])for(const route of important)await visit(route,width);
    const rest=['/research/','/projects/emotion-appraisal-video-audit/','/projects/holdout-ledger/',
      '/projects/mindhealth-observatory/','/projects/neurobehavior-inference-lab/',
      '/projects/psoriasis-wellbeing-audit/','/projects/psychemetrics-atlas/',
      '/projects/psychology-data-audit/','/projects/psylex-studio/','/projects/replicationscope/',
      '/projects/researchos/','/projects/researchweave/','/projects/schoolmind-global/',
      '/projects/survey-response-integrity/'];
    for(const route of rest)await visit(route,390);
    await visit('/',375);
    assert.ok(await js('(()=>{const n=document.querySelector(".site-nav.mobile-nav-ready"),b=n?.querySelector(".nav-toggle"),l=n?.querySelector(".site-nav-links");if(!b||!l)return false;b.click();const r=l.getBoundingClientRect();const open=b.getAttribute("aria-expanded")==="true"&&getComputedStyle(l).visibility==="visible"&&r.left>=-2&&r.right<=innerWidth+2;document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));return open&&b.getAttribute("aria-expanded")==="false";})()'),
      'mobile navigation must open in viewport and close on Escape');
    assert.ok(await js('(()=>{const n=document.querySelector(".site-nav.mobile-nav-ready"),b=n?.querySelector(".nav-toggle"),l=n?.querySelector(".site-nav-links");if(!b||!l)return false;const initiallyInert=l.inert;b.click();const open=!l.inert&&b.getAttribute("aria-expanded")==="true";document.body.click();const closed=l.inert&&b.getAttribute("aria-expanded")==="false";return initiallyInert&&open&&closed;})()'),
      'mobile menu links must be inert while closed, keyboard accessible when open, and close on outside click');
    await send('Emulation.setDeviceMetricsOverride',{width:1024,height:812,screenWidth:1024,screenHeight:812,deviceScaleFactor:2,mobile:true});
    await delay(100);
    assert.ok(await js('(()=>{const n=document.querySelector(".site-nav.mobile-nav-ready"),b=n?.querySelector(".nav-toggle"),l=n?.querySelector(".site-nav-links");return !!b&&!!l&&!l.inert&&b.getAttribute("aria-expanded")==="false";})()'),
      'desktop breakpoint must restore keyboard access to navigation');
    await visit('/',375);
    assert.ok(await js('(()=>{const e=document.querySelector(".story-viewport");if(!e)return false;e.scrollLeft=180;return e.scrollLeft>0&&e.scrollWidth>e.clientWidth&&!document.querySelector(".story-section.story-pinned");})()'),
      'story should swipe natively and not pin on phones');
    await visit('/skills/',375);
    assert.ok(await js('(()=>{const x=document.querySelector("#skills-query");if(!x)return false;x.value="scikit-learn";x.dispatchEvent(new Event("input",{bubbles:true}));return true;})()'),'skills input');
    await delay(350);
    assert.ok(await js('[...document.querySelectorAll("#skills-directory .inventory-card")].some(x=>x.hidden)'),'skills filter');
    await visit('/projects/',375);
    assert.ok(await js('(()=>{const x=document.querySelector("#archive-search");if(!x)return false;x.value="cardiac";x.dispatchEvent(new Event("input",{bubbles:true}));return true;})()'),'projects input');
    await delay(350);
    assert.ok(await js('window.portfolioArchive?.count()>0'),'projects filter');
    console.log('All phone/tablet browser tests passed');
  }catch(err){
    console.error('FAIL',last,err.stack);process.exitCode=1;
    if(send)try{
      const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
      fs.mkdirSync(path.join(ROOT,'test-artifacts'),{recursive:true});
      fs.writeFileSync(path.join(ROOT,'test-artifacts','mobile-failure.png'),Buffer.from(shot.data,'base64'));
    }catch(_){}
  }finally{
    socket?.close();browser.kill('SIGTERM');server.close();
    await delay(300);
    try{fs.rmSync(dir,{recursive:true,force:true,maxRetries:6,retryDelay:150});}catch(e){console.warn('Temporary Chrome profile could not be fully removed:',e.code);}
  }
}
run().catch(e=>{console.error(e);process.exitCode=1;server.close();});
