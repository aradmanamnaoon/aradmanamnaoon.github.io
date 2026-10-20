from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import urllib.request,time,os
url='https://webfs.oecd.org/pisa2022/STU_QQQ_SPSS.zip'
length=682364259;chunk_size=4*1024*1024
partdir=ROOT/'data'/'raw'/'pisa_download_chunks';partdir.mkdir(exist_ok=True)
n=(length+chunk_size-1)//chunk_size

def fetch(i):
 start=i*chunk_size;end=min(length-1,start+chunk_size-1)
 path=partdir/f'{i:04d}.part'
 if path.exists() and path.stat().st_size == end-start+1:return i
 for trial in range(3):
  try:
   req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}','User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(req,timeout=60) as r:
    data=r.read()
    if r.status!=206 or len(data)!=end-start+1 or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{length}':raise RuntimeError('Bad range response')
    tmp=path.with_suffix('.tmp');tmp.write_bytes(data);os.replace(tmp,path)
    return i
  except Exception as e:
   if trial==2:raise
 raise RuntimeError('Unreachable')
t0=time.monotonic();good=0
with ThreadPoolExecutor(max_workers=24) as pool:
 tasks=[pool.submit(fetch,i) for i in range(n)]
 for f in as_completed(tasks):
  try:f.result();good+=1
  except Exception as e:print('FAIL',str(e)[:120],flush=True)
print('GOOD_PARTS',good,'OF',n,'SECONDS',round(time.monotonic()-t0,2),flush=True)
if good==n:
 out=ROOT/'data'/'raw'/'STU_QQQ_SPSS.zip'
 with out.open('wb') as fh:
  for i in range(n):
   with (partdir/f'{i:04d}.part').open('rb') as f:
    for segment in iter(lambda:f.read(1048576),b''):fh.write(segment)
 import zipfile,hashlib
 with zipfile.ZipFile(out) as z:
  print('VALID_ZIP',z.testzip(),'MEMBERS',[(i.filename,i.file_size) for i in z.infolist()],flush=True)
 with out.open('rb') as file:
  sha=hashlib.file_digest(file,'sha256').hexdigest()
 print('SHA256',sha,flush=True)
 if sha!='24ee020cd6315d8aca52e07fd9aaef21cbf4f9e5b21601734b4ee6d0928a0905':
  raise RuntimeError('Official PISA ZIP changed: checksum mismatch')
