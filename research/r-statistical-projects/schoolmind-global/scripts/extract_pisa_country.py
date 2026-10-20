from pathlib import Path
from collections import defaultdict
from contextlib import ExitStack
import pyreadstat, gzip, csv, time, re
PROJECT=Path(__file__).resolve().parents[1]
sav=str(PROJECT/'data'/'raw'/'CY08MSP_STU_QQQ.SAV')
out=PROJECT/'data'/'derived'/'country_csv_gz';out.mkdir(exist_ok=True)
cols=['CNT','BELONG','W_FSTUWT']+[f'W_FSTURWT{i}' for i in range(1,81)]
rows=0;counts=defaultdict(int);start=time.monotonic()
with ExitStack() as stack:
 writers={}
 for frame,metadata in pyreadstat.read_file_in_chunks(pyreadstat.read_sav,sav,chunksize=12000,usecols=cols):
  frame=frame[['CNT','BELONG','W_FSTUWT']+cols[3:]]
  for country,group in frame.groupby('CNT',dropna=True,sort=False):
   if not re.fullmatch(r'[A-Z0-9]{2,5}',str(country)):raise RuntimeError('Unexpected country '+str(country))
   if country not in writers:
    fh=stack.enter_context(gzip.open(out/(country+'.csv.gz'),'wt',compresslevel=1,newline=''))
    wr=csv.writer(fh);wr.writerow(cols);writers[country]=wr
   writers[country].writerows(group.itertuples(index=False,name=None))
   counts[country]+=len(group)
  rows+=len(frame)
  if rows%120000==0:print('PROGRESS',rows,'elapsed',round(time.monotonic()-start,1),flush=True)
print('EXTRACTED_ROWS',rows,'COUNTRIES',len(counts),'SECONDS',round(time.monotonic()-start,2),flush=True)
print('COUNTRY_SAMPLE',dict(sorted(counts.items())[:12]),flush=True)
