import json
from pathlib import Path
import numpy as np

def attrs(node):
    result={}
    while node:
        result[node['tag']]=node['car'];node=node['cdr']
    return result

def vector(node,folder):
    t=node['type'];v=node['value'];a=attrs(node.get('attrs'))
    if t==16:
        if isinstance(v,list):return v
        return [json.loads(line) for line in (folder/v['file']).open(encoding='utf-8')]
    if t in (10,13,14):
        result=np.memmap(folder/v['file'],dtype='>f8' if t==14 else '>i4',mode='r',shape=(v['length'],)) if v['length'] else np.array([])
        if 'levels' in a:
            levels=vector(a['levels'],folder)
            return [None if i==-2147483648 else levels[i-1] for i in result]
        return result
    raise ValueError(('Unsupported metadata vector',t))

def columns(folder):
    obj=json.loads((folder/'colData-structure.json').read_text())
    if obj['type']==25:
        slots=attrs(obj['attrs']);data=slots['listData'];row=slots.get('rownames')
    else:data=obj;row=None
    names=vector(attrs(data['attrs'])['names'],folder)
    return dict(zip(names,data['value'])),row

def iter_vector(node,folder):
    if node['type']==16 and isinstance(node['value'],dict):
        with (folder/node['value']['file']).open(encoding='utf-8') as f:
            for line in f:yield json.loads(line)
    else:
        yield from vector(node,folder)

