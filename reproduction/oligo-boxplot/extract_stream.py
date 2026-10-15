"""Bounded XDR reader for colData only. Fail on unsupported serialization types.
No R code evaluation; no assays materialized. Large metadata vectors spool to disk.
Format reference: R src/main/serialize.c. Not a general RDS reader.
"""
import gzip,io,json,struct,sys
from pathlib import Path

class Captured(Exception): pass
class Reader:
    def __init__(self,f,out):
        self.f=f;self.out=out;self.refs=[];self.serial=0;self.pos=0
    def read(self,n):
        b=self.f.read(n);self.pos+=len(b)
        if len(b)!=n:raise EOFError((n,len(b),self.pos))
        return b
    def integer(self):return struct.unpack('>i',self.read(4))[0]
    def length(self):
        n=self.integer()
        if n==-1:n=(self.integer()<<32)+(self.integer()&0xffffffff)
        if n<0:raise ValueError('negative length')
        return n
    def bclang(self,t,depth):
        if t==243:self.integer();return
        if t in (244,6,2,240,239):
            if t==244:self.integer();t=self.integer()
            if t in (240,239):self.item(False,depth+1)
            self.item(False,depth+1)
            self.bclang(self.integer(),depth+1)
            self.bclang(self.integer(),depth+1)
        else:self.item(False,depth+1)
    def bc(self,depth):
        self.item(False,depth+1)
        for _ in range(self.integer()):
            t=self.integer()
            if t==21:self.bc(depth+1)
            elif t in (6,2,244,243,240,239):self.bclang(t,depth+1)
            else:self.item(False,depth+1)
    def item(self,keep=False,depth=0):
        flags=self.integer();t=flags&255;attr=bool(flags&512);tagged=bool(flags&1024)
        if t in (0,254,253,252,251,250,242,241):return None
        if t==255:
            idx=flags>>8 or self.integer()
            return self.refs[idx-1]
        if t==1:
            s=self.item(True,depth+1);self.refs.append(s);return s
        if t==238:
            return {'type':'altrep','info':self.item(keep,depth+1),'state':self.item(keep,depth+1),'attrs':self.item(keep,depth+1)}
        if t==4:
            locked=self.integer();v={};self.refs.append(v)
            for key in ('enclosure','frame','hashtable','attrs'):v[key]=self.item(keep,depth+1)
            return v if keep else None
        if t in (2,6,3,5,17):
            a=self.item(keep,depth+1) if attr else None
            tag=self.item(t in (2,6,17),depth+1) if tagged else None
            capture=tag=='colData' and depth<=2
            if depth<=2 and tag:print('slot',tag,'offset',self.pos,flush=True)
            car=self.item(keep or capture,depth+1)
            if capture:
                (self.out/'colData-structure.json').write_text(json.dumps(car),encoding='utf-8')
                print('Captured colData at',self.pos,flush=True);raise Captured()
            cdr=self.item(keep,depth)
            return {'tag':tag,'car':car,'cdr':cdr,'attrs':a} if keep else None
        if t==9:
            n=self.integer();v=None if n==-1 else self.read(n).decode('utf-8')
            if attr:self.item(False,depth+1)
            return v
        if t in (10,13,14,15,24):
            n=self.length();width={10:4,13:4,14:8,15:16,24:1}[t]
            if keep:
                self.serial+=1;p=self.out/f'vector-{self.serial}.bin'
                with p.open('xb') as out:
                    left=n*width
                    while left:
                        b=self.read(min(left,1024*1024));out.write(b);left-=len(b)
                v={'file':p.name,'length':n}
            else:
                left=n*width
                while left:left-=len(self.read(min(left,1024*1024)))
                v=None
        elif t in (16,19,20):
            n=self.length()
            if t==16 and keep and n>100:
                self.serial+=1;p=self.out/f'vector-{self.serial}.jsonl'
                with p.open('x',encoding='utf-8') as out:
                    for _ in range(n):out.write(json.dumps(self.item(True,depth+1))+'\n')
                v={'file':p.name,'length':n}
            else:
                v=[]
                for _ in range(n):
                    x=self.item(keep,depth+1)
                    if keep:v.append(x)
        elif t==25:v=None
        elif t==21:
            self.integer();self.bc(depth+1);v=None
        elif t in (7,8):v=self.read(self.integer()).decode()
        elif t==23:v={};self.refs.append(v)
        elif t in (247,248,249):
            assert self.integer()==0
            n=self.integer();v=[self.item(True,depth+1) for _ in range(n)];self.refs.append(v);return v
        elif t==22:
            v={};self.refs.append(v);v['protected']=self.item(keep,depth+1);v['tag']=self.item(keep,depth+1)
        else:raise ValueError(('Unsupported type',t,'offset',self.pos))
        a=self.item(keep,depth+1) if attr else None
        return {'type':t,'value':v,'attrs':a} if keep else None
    def run(self):
        assert self.read(2)==b'X\n'
        version=self.integer();writer=self.integer();minimum=self.integer()
        assert version in (2,3)
        encoding=self.read(self.integer()).decode() if version==3 else None
        (self.out/'serialization.json').write_text(json.dumps(dict(version=version,writer=writer,minimum=minimum,encoding=encoding)))
        self.item()

if __name__=='__main__':
    source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
    with gzip.open(source,'rb') as outer:
        # GEO wraps an already compressed RDS in a second gzip layer.
        f=io.BufferedReader(outer)
        inner=gzip.GzipFile(fileobj=f,mode='rb') if f.peek(2)[:2]==b'\x1f\x8b' else f
        try:Reader(inner,out).run()
        except Captured:pass
        else:raise ValueError('colData not found')

