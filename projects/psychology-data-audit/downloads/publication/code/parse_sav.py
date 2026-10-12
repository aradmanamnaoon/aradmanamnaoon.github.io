"""Minimal, read-only parser for SPSS system files ($FL2), for audit in offline runtimes.
Supports standard variable/value-label metadata and zlib-free byte compression.
Fails loudly on unsupported features. Does not replace pyreadstat for general-purpose SAV imports.
"""
from __future__ import annotations
import struct, math, json, pathlib, collections
import numpy as np
import pandas as pd

class Parser:
    def __init__(self, path):
        self.path=path; self.b=pathlib.Path(path).read_bytes(); self.pos=0
    def read(self,n):
        v=self.b[self.pos:self.pos+n]
        if len(v)!=n: raise ValueError(f'EOF offset {self.pos}, requested {n}')
        self.pos+=n;return v
    def i(self): return struct.unpack('<i', self.read(4))[0]
    def d(self): return struct.unpack('<d', self.read(8))[0]
    def peek_i(self): return struct.unpack_from('<i',self.b,self.pos)[0]
    @staticmethod
    def s(b):
        return b.rstrip(b' \x00').decode('utf-8',errors='replace')
    def parse(self):
        magic=self.read(4).decode('ascii')
        if magic != '$FL2': raise NotImplementedError('Not a standard little-endian $FL2 SAV')
        product=self.s(self.read(60)); layout=self.i(); nslots=self.i(); compression=self.i(); weight_idx=self.i(); ncases=self.i();bias=self.d();date=self.s(self.read(9)); time=self.s(self.read(8)); label=self.s(self.read(64)); self.read(3)
        print('header',dict(product=product,layout=layout,nslots=nslots,compression=compression,weight_idx=weight_idx,ncases=ncases,bias=bias,date=date,time=time,label=label))
        vars=[]; labels=[]; add=[]; value_label_sets=[]; docs=[]; slots=[]
        while True:
            offset=self.pos; rec=self.i()
            if rec==2:
                vartype=self.i(); haslabel=self.i(); miss=self.i(); printformat=self.i(); writeformat=self.i(); name=self.s(self.read(8));
                lab=None
                if haslabel:
                    l=self.i(); lab=self.s(self.read(((l+3)//4)*4)[:l])
                missvals=[]
                if miss:
                    if abs(miss)>3: raise ValueError(f'Unusual missing values count: {miss}')
                    for _ in range(abs(miss)): missvals.append(self.d())
                v=dict(name=name,type=vartype,label=lab,missing_code=miss,missing_values=missvals,printformat=printformat,writeformat=writeformat,slot=len(slots)+1)
                if vartype==-1:
                    slots.append(None)
                else:
                    vars.append(v); slots.append(v)
            elif rec==3:
                n=self.i(); dic=[]
                for _ in range(n):
                    val=self.read(8); ln=self.read(1)[0]; raw=self.read(ln); pad=(- (1+ln))%8; self.read(pad)
                    dic.append((val,self.s(raw)))
                if self.i()!=4: raise ValueError('Missing record 4 after value labels')
                k=self.i();idx=[self.i() for _ in range(k)]
                value_label_sets.append(dict(items=dic,indices=idx))
            elif rec==6:
                n=self.i(); docs.append(self.read(n*80))
            elif rec==7:
                subtype=self.i(); size=self.i(); count=self.i(); x=self.read(size*count)
                add.append(dict(subtype=subtype,size=size,count=count,data=x))
            elif rec==999:
                filler=self.i(); break
            else:
                raise ValueError(f'Unexpected record {rec} at {offset}')
        print('dictionary offset',self.pos,'vars',len(vars),'slots',len(slots),'labels',len(value_label_sets),'extra',[(x['subtype'],x['size'],x['count']) for x in add])
        for ds in value_label_sets:
            for j in ds['indices']:
                if 1<=j<=len(slots) and slots[j-1] is not None:
                    v=slots[j-1]; vd=v.setdefault('value_labels',{})
                    for val, lab in ds['items']:
                        if v['type']==0:
                            num=struct.unpack('<d',val)[0]
                            vd[float(num)]=lab
                        else: vd[self.s(val)]=lab
        # Extended metadata includes full names, and measuring level
        for item in add:
            if item['subtype']==11:
                lev=list(struct.unpack('<'+'i'*item['count'],item['data']))
                for vi,slot in enumerate(slots):
                    if slot is not None and 3*vi+2<len(lev):
                        slot['measurement_level']=lev[3*vi]
                        slot['display_width']=lev[3*vi+1]
                        slot['alignment']=lev[3*vi+2]
            if item['subtype']==13:
                item['preview']=item['data'][:300].decode('utf-8',errors='replace')
        rows=[]
        if compression==1:
            # 8 control bytes then uncompressed values (8B) are inlined; 0 code means no slot consumed.
            vals=[];end=False
            while not end and (ncases<0 or len(vals)<ncases*len(slots)):
                if self.pos>=len(self.b):break
                controls=self.read(8)
                for ctl in controls:
                    if ctl==0: continue
                    if ctl==252: end=True; break
                    if ctl==253: vals.append(self.read(8))
                    elif ctl==254: vals.append(b' '*8)
                    elif ctl==255: vals.append(None)
                    elif 1<=ctl<=251: vals.append(struct.pack('<d',float(ctl)-bias))
                    else: raise ValueError(f'Invalid compression byte {ctl}')
            ndata=len(vals)//len(slots)
            if ncases!=-1 and ndata!=ncases: raise ValueError(f'Number of cases mismatch parsed {ndata}, expected {ncases}, values={len(vals)}')
            if len(vals)%len(slots): raise ValueError('Unaligned data slots')
            for row in range(ndata):
                v=[]
                for j,slot in enumerate(slots):
                    bb=vals[row*len(slots)+j]
                    if slot is None: continue
                    if bb is None: v.append(np.nan)
                    elif slot['type']==0:
                        num=struct.unpack('<d',bb)[0]; v.append(num if math.isfinite(num) and abs(num)<1e100 else np.nan)
                    else: v.append(self.s(bb))
                rows.append(v)
        elif compression==0:
            for row in range(ncases):
                v=[]
                for slot in slots:
                    bb=self.read(8)
                    if slot is None: continue
                    v.append(struct.unpack('<d',bb)[0] if slot['type']==0 else self.s(bb))
                rows.append(v)
        else: raise NotImplementedError('zlib compression not supported')
        df=pd.DataFrame(rows,columns=[x['name'] for x in vars]);
        for v in vars:
            if v['type']!=0: continue
            name=v['name']; numeric=pd.to_numeric(df[name],errors='coerce')
            # Preserve raw missing-value codes here; apply user-defined missing values separately downstream
            df[name]=numeric
        metadata=dict(source=str(self.path),header=dict(product=product,layout=layout,nslots=nslots,compression=compression,weight_idx=weight_idx,ncases=ncases,bias=bias,date=date,time=time,label=label),variables=vars,additional=[{k:v for k,v in a.items() if k!='data'} for a in add])
        return df,metadata
