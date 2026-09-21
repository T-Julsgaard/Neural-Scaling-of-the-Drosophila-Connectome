"""Read saved arrays/summaries; independently check report means without learning."""
from pathlib import Path
import json, hashlib, csv
import numpy as np
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
checks=[]; rows=[]; manifest={}
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def check(name,a,b):
    assert abs(float(a)-float(b))<1e-10,(name,a,b)
    checks.append(name)
for number,n,condition,ci in [(7,32,'6_per_pair_16_False',11),(8,24,'16_per_pair_16_False',5)]:
    folder=ROOT/f'results/exp{number:03}_confirmation'
    analysis=read(folder/'analysis.json');contract=read(folder/'contract.json')
    methods=list(contract['settings']); collected={m:[] for m in ['ordinary','homeostasis']}
    unused={m:[] for m in ['ordinary','homeostasis']}
    for p in sorted(folder.glob('block_*.npz')):
        record=read(p.with_suffix('.json'));rawhash=hashlib.sha256(p.read_bytes()).hexdigest()
        assert rawhash==record['sha256'];manifest[p.relative_to(ROOT).as_posix()]=rawhash
        with np.load(p,allow_pickle=False) as z:
            for method in collected:
                v=z['scores'][ci,methods.index(method),0]
                h=z[f'c{ci}_{method}_g0_r0_history']
                final=h[:,0,-1,:];acquired=np.diagonal(h[:,0],axis1=-2,axis2=-1)
                check(f'{number}/{p.stem}/{method} retained mean',final.mean(),v[0])
                check(f'{number}/{p.stem}/{method} worst pair',final.min(-1).mean(),v[1])
                check(f'{number}/{p.stem}/{method} acquisition',acquired.mean(),v[2])
                collected[method].append(v)
                unused[method].append(np.mean(z[f'c{ci}_{method}_g0_r0_presented']==0))
                rows.append(dict(experiment=f'EXP-{number:03}',block=p.stem,method=method,retention=v[0],worst_pair=v[1],new_learning=v[2],below_chance=v[7],unused_presented=unused[method][-1]))
    assert len(collected['ordinary'])==n
    for method,vs in collected.items():
        vs=np.array(vs)
        for j,ep in enumerate(['retention','worst_pair','new_learning','forgetting','noise_retention','reversal','unchanged','below_chance']):
            check(f'EXP-{number:03} {method} {ep}',vs[:,j].mean(),analysis['profiles'][condition][method][ep]['mean'])
    delta=np.array(collected['homeostasis'])[:,0]-np.array(collected['ordinary'])[:,0]
    check(f'EXP-{number:03} paired primary mean',delta.mean(),analysis['primary']['ordinary']['mean'])
    g=read(folder/'geometry.json')
    for method in unused: check(f'EXP-{number:03} unused {method}',np.mean(unused[method]),g[condition+'_'+method]['unused_presented']['mean'])
    assert sum(v['lower']>-.03 for arm in analysis['guardrails'].values() for v in arm.values())==9
    assert all(arm['worst_pair']['lower']<=-.03 for arm in analysis['guardrails'].values())
    checks.append(f'EXP-{number:03} nine guardrails pass and three worst-pair guardrails fail')
aroot=ROOT/'results/exp009';a=read(aroot/'analysis.json')
recs=[read(p) for p in sorted((aroot/'confirmation').glob('block_*.json'))]
assert len(recs)==24
x=np.array([[r['scores'][0][0],r['scores'][1][0]] for r in recs])
check('EXP-009 uncompensated mean',x[:,0].mean(),a['uncompensated']['mean'])
check('EXP-009 compensated mean',x[:,1].mean(),a['compensated']['mean'])
check('EXP-009 paired primary mean',(x[:,1]-x[:,0]).mean(),a['primary']['mean'])
cal=read(ROOT/'results/exp007_calibration/record.json')['fits']['p0_l0.25']
assert round(cal['clamp_fraction']*100,2)==49.32
assert round(cal['bound'],6)==.052509
checks.append('Larval offset bound and saturation agree with fitted-state record')
with (HERE/'calibration_block_data.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(HERE/'raw_array_checks.json').write_text(json.dumps({'passed':True,'checks_count':len(checks),'checks':checks,'raw_inputs_sha256':manifest,'scope':'EXP-007/008 selected hard-condition acquisition/final/tail values from archived histories, mean primary contrasts and participation; EXP-009 means from confirmation summaries. Original bootstrap limits retained, not newly sampled.'},indent=2),encoding='utf-8')
print('Saved-array checks passed:',len(checks))
