"""Read official CC0 ZIP directory with HTTP ranges; download only selected assets."""
from pathlib import Path
import urllib.request, struct, json, zlib, sys
URL='https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip'
OUT=Path('D:/NetSim3D/3Dmodel/temp/teacher_male/system_assets')
OUT.mkdir(parents=True,exist_ok=True)
def request(byte_range):
    req=urllib.request.Request(URL,headers={'Range':'bytes='+byte_range,'User-Agent':'NetSim3D-asset-preparation/1.0'})
    with urllib.request.urlopen(req,timeout=60) as r:
        if r.status!=206: raise RuntimeError('Server must support partial content; refusing an unintended full archive download')
        return r.read(),dict(r.headers)
tail,headers=request('-65536')
pos=tail.rfind(b'PK\x05\x06')
assert pos>=0
_,disk,cddisk,entries_here,entries,cdsize,cdoffset,comment=struct.unpack_from('<4s4H2LH',tail,pos)
data,_=request(f'{cdoffset}-{cdoffset+cdsize-1}')
records=[];off=0
while off<len(data):
    fields=struct.unpack_from('<4s6H3L5H2L',data,off)
    assert fields[0]==b'PK\x01\x02'
    method=fields[4];packed=fields[8];size=fields[9];namelen,extralen,commentlen=fields[10:13];localoff=fields[16]
    name=data[off+46:off+46+namelen].decode('utf-8')
    records.append({'name':name,'method':method,'compressed_size':packed,'size':size,'offset':localoff})
    off+=46+namelen+extralen+commentlen
(OUT/'archive_index.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
if '--list' in sys.argv:
    for rec in records:
        if any(v in rec['name'].lower() for v in ('short0','male_casual','male_elegant','shoes0','young_asian_male','eyebrow001')):
            print(rec['name'],rec['size'])
    sys.exit()
selected=sys.argv[1:]
for rec in records:
    if not any(v in rec['name'] for v in selected) or rec['name'].endswith('/'):continue
    name=rec['name']
    target=(OUT/name).resolve()
    assert target.is_relative_to(OUT.resolve())
    if target.exists() and target.stat().st_size==rec['size']:continue
    start=rec['offset']
    head,_=request(f'{start}-{start+29}')
    h=struct.unpack('<4s5H3L2H',head)
    assert h[0]==b'PK\x03\x04'
    begin=start+30+h[-2]+h[-1]
    compressed,_=request(f'{begin}-{begin+rec["compressed_size"]-1}')
    raw=zlib.decompress(compressed,-15) if rec['method']==8 else compressed
    assert len(raw)==rec['size']
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(raw)
    print('DOWNLOADED',name,len(raw),flush=True)
