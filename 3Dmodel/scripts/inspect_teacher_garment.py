from pathlib import Path
from collections import defaultdict
p=Path('D:/NetSim3D/3Dmodel/temp/teacher_male/system_assets/clothes/male_casualsuit01/male_casualsuit01.obj')
v=[];f=[];adj=defaultdict(set)
for ln in p.read_text().splitlines():
    a=ln.split()
    if not a:continue
    if a[0]=='v':v.append(list(map(float,a[1:4])))
    elif a[0]=='f':
        ids=[int(i.split('/')[0])-1 for i in a[1:]];f.append(ids)
        for i,j in zip(ids,ids[1:]+ids[:1]):adj[i].add(j);adj[j].add(i)
unseen=set(range(len(v)))
while unseen:
    start=unseen.pop();comp={start};q=[start]
    while q:
        for j in adj[q.pop()]:
            if j in unseen:unseen.remove(j);comp.add(j);q.append(j)
    bounds=[[round(min(v[i][k] for i in comp),3),round(max(v[i][k] for i in comp),3)] for k in range(3)]
    print('PART',start,len(comp),bounds)
