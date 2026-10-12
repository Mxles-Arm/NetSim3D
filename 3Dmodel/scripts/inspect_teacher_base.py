from pathlib import Path
import json, collections, math
P=Path('D:/NetSim3D/3Dmodel/temp/teacher_male/source')
v=[]; faces=collections.defaultdict(list); group=''
for line in (P/'base.obj').read_text().splitlines():
    a=line.split()
    if not a: continue
    if a[0]=='v':v.append(list(map(float,a[1:4])))
    elif a[0]=='g':group=a[1]
    elif a[0]=='f':faces[group].append([int(x.split('/')[0])-1 for x in a[1:]])
for filename,factor in [('asian-male-young.target',.85),('caucasian-male-young.target',.15),('universal-male-young-maxmuscle-averageweight.target',.15)]:
    for line in (P/filename).read_text().splitlines():
        a=line.split()
        if not a or a[0].startswith('#'):continue
        i=int(a[0])
        for k in range(3):v[i][k]+=float(a[k+1])*factor
for g in ['body','helper-tights','helper-hair','helper-l-eye','helper-r-eye']:
    ids=set(i for f in faces[g] for i in f)
    print(g,len(ids),len(faces[g]),'bounds',[[min(v[i][k] for i in ids),max(v[i][k] for i in ids)] for k in range(3)])
print('BODY SLICES')
body=set(i for f in faces['body'] for i in f)
for y in [0,1,2,3,4,5,6,7,8]:
    ids=[i for i in body if abs(v[i][1]-y)<.2]
    print(y,[[round(min(v[i][k] for i in ids),4),round(max(v[i][k] for i in ids),4)] for k in [0,2]] if ids else '-')
r=json.loads((P/'default.mhskel').read_text())
print('BONES')
for name,b in r['bones'].items():
    if any(w in name for w in ['spine','neck','head','upperarm','lowerarm','wrist','upperleg','lowerleg','foot','pelvis']):
        pts=[]
        for end in ['head','tail']:
            ids=r['joints'][b[end]]
            pts.append([round(sum(v[i][k] for i in ids)/len(ids),4) for k in range(3)])
        print(name,b['parent'],pts)
print('FACE SLICES: frontmost points')
for y in [6.0,6.1,6.2,6.3,6.4,6.5,6.6,6.7,6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.5,7.6]:
    ids=[i for i in body if abs(v[i][1]-y)<.055 and abs(v[i][0])<.18]
    print(y,sorted([(i,*[round(a,3) for a in v[i]]) for i in ids],key=lambda a:-a[3])[:3])
print('EYE')
for y in [7.0,7.1,7.2,7.3,7.4]:
    ids=[i for i in body if abs(v[i][1]-y)<.055 and .2<v[i][0]<.45]
    print(y,sorted([(i,*[round(a,3) for a in v[i]]) for i in ids],key=lambda a:-a[3])[:5])
