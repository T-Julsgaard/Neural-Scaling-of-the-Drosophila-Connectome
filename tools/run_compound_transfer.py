"""EXP-011: prospective XOR transfer, immutable stages and exact replay."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[key] = '1'
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import time
import shutil
import platform
import numpy as np
from tools.run_readout_diagnostic import sha, read, write, stamp, ridge, interval
from exp007.homeostasis import encode
from exp002.campaign import peak_memory

OUT = ROOT/'results/exp011'
CAL = ROOT/'results/exp007_calibration/calibration.npz'
REPS = ['native', 'calibrated', 'random1', 'random2', 'random3', 'direct', 'polynomial']
MODES = ['blocked', 'unclipped', 'shuffled', 'local10', 'replay10']
ETAS = [1/2400, 1/600, 1/150, 2/75]
LAMBDAS = [1e-6, 1e-4, .01, .1]

def rng(stage, block, part):
    return np.random.default_rng(np.random.SeedSequence([11011, {'validation':0,'development':1,'confirmation':2}[stage], block, part]))

def task(stage, block):
    r = rng(stage, block, 0)
    perm = r.permutation(40); order = r.permutation(2); polarity = int(r.choice([-1, 1]))
    def samples(n, noise, part):
        rr = rng(stage, block, part); x = np.zeros((2,n,40)); y = np.zeros((2,n))
        for phase, a in enumerate(order):
            bs = rr.permutation(np.tile([0,1],n//2))
            for j, b in enumerate(bs):
                x[phase,j,perm[5*a:5*a+5]] = rr.uniform(.6,1)
                x[phase,j,perm[10+5*b:15+5*b]] = rr.uniform(.6,1)
                x[phase,j,rr.choice(perm[20:],2,replace=False)] = rr.uniform(.1,.3,2)
                y[phase,j] = polarity*(1-2*(a ^ b))
        return np.clip(x+rr.normal(0,noise,x.shape),0,1), y
    tr,y = samples(128,.05,1); px,py = samples(512,.05,2); hx,hy = samples(512,.2,3)
    return dict(train=tr,labels=y,probes=px,probe_labels=py,high=hx,high_labels=hy,permutation=perm,phase_order=order,polarity=np.array(polarity),shuffle=rng(stage,block,4).permutation(256))

def polynomial(x):
    i,j = np.triu_indices(x.shape[-1])
    return np.concatenate([np.ones((*x.shape[:-1],1)),x,x[...,i]*x[...,j]],axis=-1)

def features(t, rep, cal):
    if rep in ('direct','polynomial'):
        f = (lambda x:x.copy()) if rep == 'direct' else polynomial
        tr,px,hx = [f(t[k]) for k in ('train','probes','high')]
        scale = np.sqrt((100/6)/np.mean(np.sum(tr**2,-1)))
        return tr*scale,px*scale,hx*scale,scale
    j = int(rep[-1]) if rep.startswith('random') else 0
    theta = cal['p0_l0.25'] if rep == 'calibrated' else np.zeros(73)
    f = lambda x:encode(x,cal['projections'][j],cal['priority'],6,theta)
    return *[f(t[k]) for k in ('train','probes','high')],1.

def schedule(mode, shuffle, n=128):
    if mode == 'shuffled': return shuffle
    if mode == 'local10': return np.r_[np.tile(np.arange(n),10),np.tile(np.arange(n,2*n),10)]
    return np.tile(np.arange(2*n),10 if mode == 'replay10' else 1)

def learn(x,y,eta,mode,shuffle):
    n=x.shape[1]; x=x.reshape(-1,x.shape[-1]); y=y.ravel()
    p=np.full(x.shape[-1],.1); m=p.copy(); boundary=[]; clipped=0
    ix=schedule(mode,shuffle,n)
    for j,k in enumerate(ix):
        delta=eta*x[k]*(y[k]-x[k]@(p-m))
        pp,mm=p+delta,m-delta
        clipped += int(np.count_nonzero(pp<0)+np.count_nonzero(mm<0))
        p,m=(pp,mm) if mode=='unclipped' else (np.maximum(0,pp),np.maximum(0,mm))
        # Acquisition is meaningful only for phase-blocked schedules.
        if j in ((10*n-1,20*n-1) if mode=='local10' else (n-1,2*n-1)):
            boundary.append((p-m).copy())
    assert np.isfinite(p).all() and np.isfinite(m).all()
    return dict(w=p-m,boundary=np.array(boundary),indices=ix,clips=np.array(clipped))

def acc(w,x,y):
    margin=(x@w)*y
    return ((margin>0)+.5*(margin==0)).mean(-1)

def metrics(w,px,py,hx,hy):
    a=acc(w,px,py); h=acc(w,hx,hy)
    return dict(old=float(a[0]),new=float(a[1]),overall=float(a.mean()),worst=float(a.min()),high_old=float(h[0]))

def compute(stage,b,selection=None):
    start,cpu=time.perf_counter(),time.process_time()
    t=task(stage,b); arrays=dict(t); summary={}
    with np.load(CAL) as z: cal=dict(z)
    for rep in REPS:
        x,px,hx,scale=features(t,rep,cal); models={}
        flat=x.reshape(-1,x.shape[-1]); y=t['labels'].ravel()
        for mode in MODES:
            grid=sorted(set([selection['etas'][rep][mode],ETAS[2]])) if selection else ETAS
            for eta in grid:
                k=f'{mode}_{ETAS.index(eta)}'; r=learn(x,t['labels'],eta,mode,t['shuffle'])
                met=metrics(r['w'],px,t['probe_labels'],hx,t['high_labels'])
                if mode != 'shuffled':
                    acquired=float(acc(r['boundary'][0],px,t['probe_labels'])[0])
                    met.update(acquisition=acquired,forgetting=acquired-met['old'])
                met.update(eta=eta,updates=len(r['indices']),clips=int(r['clips']))
                models[k]=met
                for field,v in r.items(): arrays[f'{rep}_{k}_{field}']=v
        grid=[selection['lambdas'][rep]] if selection else LAMBDAS
        for lam in grid:
            w,res=ridge(flat,y,lam); k=f'offline_{LAMBDAS.index(lam)}'
            models[k]=dict(**metrics(w,px,t['probe_labels'],hx,t['high_labels']),residual=res,lambda_value=lam,train_mse=float(np.mean((flat@w-y)**2)))
            arrays[f'{rep}_{k}_w']=w
        summary[rep]=dict(scale=scale,dimension=x.shape[-1],norm2=float(np.mean(np.sum(flat**2,-1))),models=models)
    return arrays,dict(representations=summary,wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,peak_memory_bytes=peak_memory())

def sources():
    paths=[Path(__file__),ROOT/'tests/test_exp011.py',ROOT/'experiments/EXP-011-protocol.md',ROOT/'tools/run_readout_diagnostic.py',CAL]
    paths += [p for module in ('exp002','exp007') for p in (ROOT/module).glob('*.py')]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}

def preserve():
    path=OUT/'preservation.json'
    if path.exists(): return
    # Scoped preservation: prior source/reports, top-level and stage contracts,
    # prior audit manifests, and all B raw traces. Avoid rehashing older bulk data.
    paths=list((ROOT/'experiments').glob('*'))
    paths += [p for base in ('exp002','exp003','exp004','exp005','exp006','exp007','exp008','exp009','tools','tests') for p in (ROOT/base).glob('*.py')]
    for folder in (ROOT/'results').glob('exp*'):
        if folder.name=='exp011':continue
        paths += list(folder.glob('*.json'))
        paths += list(folder.glob('*/contract.json'))
    paths += list((ROOT/'results/exp010').glob('*/*.npz'))
    paths += list((ROOT/'results/exp010').glob('*/block_*.json'))
    paths += [ROOT/'research/SESSION_B_COMPLETION.md',ROOT/'research/exp010_artifacts.json',ROOT/'research/exp009_historical_hashes.json',CAL]
    paths=[p for p in paths if p.is_file() and '011' not in p.name and p.name not in ('run_compound_transfer.py','report_compound_transfer.py')]
    write(path,dict(created_utc=stamp(),files={p.relative_to(ROOT).as_posix():sha(p) for p in paths}))

def freeze(stage):
    path=OUT/stage/'contract.json'
    if path.exists():
        c=read(path); assert c['source']==sources()
        if stage=='confirmation': assert c['selection_sha256']==sha(OUT/'selection.json')
        return c
    if stage != 'validation': assert read(OUT/'validation.json')['passed']
    selection=read(OUT/'selection.json') if stage=='confirmation' else None
    if selection: assert selection['source']==sources() and selection['development_gate']
    c=dict(created_utc=stamp(),source=sources(),selection=selection,selection_sha256=sha(OUT/'selection.json') if selection else None,blocks=list(range(1 if stage=='validation' else 6 if stage=='development' else 24)),python=sys.version,numpy=np.__version__,platform=platform.platform())
    for name in c['source']:
        if name.endswith(('.py','.md')):
            dest=OUT/stage/'frozen_source'/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/name,dest)
    write(path,c); return c

def run(stage):
    c=freeze(stage)
    for b in c['blocks']:
        path=OUT/stage/f'block_{b:03}.npz'; rec=path.with_suffix('.json')
        if rec.exists():
            r=read(rec); assert r['sha256']==sha(path) and r['contract_sha256']==sha(OUT/stage/'contract.json')
        else:
            a,r=compute(stage,b,c['selection'])
            with path.with_suffix('.tmp').open('wb') as f: np.savez_compressed(f,**a)
            path.with_suffix('.tmp').replace(path)
            r.update(sha256=sha(path),contract_sha256=sha(OUT/stage/'contract.json'));write(rec,r)
        total=sum(read(p)['wall_seconds'] for p in OUT.glob('*/block_*.json'))
        assert total<1800 and r['peak_memory_bytes']<2*1024**3
        assert sum(p.stat().st_size for p in OUT.rglob('*.npz'))<1024**3
        print(stage,b,round(r['wall_seconds'],2),flush=True)

def select():
    assert not (OUT/'selection.json').exists()
    c=freeze('development'); records=[read(OUT/'development'/f'block_{b:03}.json')['representations'] for b in c['blocks']]
    etas={}; lambdas={}
    for rep in REPS:
        etas[rep]={mode:ETAS[int(np.argmax([np.mean([r[rep]['models'][f'{mode}_{k}']['overall'] for r in records]) for k in range(4)]))] for mode in MODES}
        lambdas[rep]=LAMBDAS[int(np.argmax([np.mean([r[rep]['models'][f'offline_{k}']['overall'] for r in records]) for k in range(4)]))]
    offline={rep:float(np.mean([r[rep]['models'][f'offline_{LAMBDAS.index(lambdas[rep])}']['overall'] for r in records])) for rep in REPS}
    selection=dict(created_utc=stamp(),source=sources(),etas=etas,lambdas=lambdas,development_offline=offline,development_gate=bool(offline['polynomial']>=.9 and .4<=offline['direct']<=.6),sparse_development_adequate=bool(np.mean([offline[k] for k in REPS[:2]])>=.8),n=24,prediction='Native/calibrated mean offline old >=.80; paired offline-minus-tuned-blocked old lower 95% CI >.05; tuned-blocked acquisition-minus-final old lower 95% CI >.05. Require all. Interpret only with polynomial/direct gates; inadequate sparse recovery is uninformative about recoverable-information forgetting.',development_hashes={p.name:sha(p) for p in (OUT/'development').glob('block_*.json')})
    write(OUT/'selection.json',selection); print(selection)

def analyze():
    s=read(OUT/'selection.json'); recs=[read(OUT/'confirmation'/f'block_{b:03}.json')['representations'] for b in range(24)]
    def val(r,rep,mode,field):
        key=f'offline_{LAMBDAS.index(s["lambdas"][rep])}' if mode=='offline' else f'{mode}_{ETAS.index(s["etas"][rep][mode])}'
        return r[rep]['models'][key][field]
    groups={'native':['native'],'calibrated':['calibrated'],'random':REPS[2:5],'direct':['direct'],'polynomial':['polynomial'],'native_calibrated':REPS[:2]}
    tables={}; contrasts={}
    for group,reps in groups.items():
        def values(mode,field): return np.array([np.mean([val(r,rep,mode,field) for rep in reps]) for r in recs])
        tables[group]={mode:{field:interval(values(mode,field)) for field in ('old','new','overall','worst','high_old')+ (('acquisition','forgetting') if mode not in ('offline','shuffled') else ())} for mode in MODES+['offline']}
        contrasts[group]={mode+'_minus_blocked_old':interval(values(mode,'old')-values('blocked','old')) for mode in MODES[1:]+['offline']}
        contrasts[group]['replay10_minus_local10_old']=interval(values('replay10','old')-values('local10','old'))
        contrasts[group]['replay10_minus_local10_new']=interval(values('replay10','new')-values('local10','new'))
        tables[group]['fixed_B_blocked']={field:interval([np.mean([r[rep]['models']['blocked_2'][field] for rep in reps]) for r in recs]) for field in ('old','new','overall','acquisition','forgetting')}
    primary=tables['native_calibrated']; gap=contrasts['native_calibrated']['offline_minus_blocked_old']
    capable=tables['polynomial']['offline']['overall']['mean']>=.9 and .4<=tables['direct']['offline']['overall']['mean']<=.6
    recovery=primary['offline']['old']['mean']>=.8
    passed=bool(capable and recovery and gap['lower']>.05 and primary['blocked']['forgetting']['lower']>.05)
    result=dict(created_utc=stamp(),selection_sha256=sha(OUT/'selection.json'),tables=tables,contrasts=contrasts,primary_gap=gap,primary_forgetting=primary['blocked']['forgetting'],capable_gate=capable,recovery_gate=recovery,prediction_passed=passed,classification='supported' if passed else 'uninformative_recovery_or_task' if not(capable and recovery) else 'not_supported',calibration_minus_native_offline_old=interval([val(r,'calibrated','offline','old')-val(r,'native','offline','old') for r in recs]))
    write(OUT/'analysis.json',result); print({k:v for k,v in result.items() if k not in ('tables','contrasts')})

def audit():
    start=time.perf_counter(); count=0; total=0
    s=read(OUT/'selection.json')
    for name,h in s['development_hashes'].items(): assert sha(OUT/'development'/name)==h
    for stage in ('validation','development','confirmation'):
        c=freeze(stage)
        for b in c['blocks']:
            p=OUT/stage/f'block_{b:03}.npz'; rec=read(p.with_suffix('.json'))
            assert sha(p)==rec['sha256'] and sha(OUT/stage/'contract.json')==rec['contract_sha256']
            arr,met=compute(stage,b,c['selection']); assert met['representations']==rec['representations']
            with np.load(p) as z:
                assert set(arr)==set(z.files)
                for k,v in arr.items(): np.testing.assert_array_equal(v,z[k]); total+=1
            count+=1; assert time.perf_counter()-start<1800
            print('replayed',stage,b,flush=True)
    historical=read(OUT/'preservation.json')['files']
    for name,h in historical.items(): assert sha(ROOT/name)==h,name
    before=read(OUT/'analysis.json'); analyze(); after=read(OUT/'analysis.json')
    before.pop('created_utc');after.pop('created_utc');assert before==after
    write(OUT/'audit.json',dict(passed=True,blocks=count,arrays=total,preserved_files=len(historical),wall_seconds=time.perf_counter()-start,source=sources(),utc=stamp(),review_type='automated self-audit; not independent review'))

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='validate':
        import unittest
        preserve()
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_exp011')
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        assert result.wasSuccessful()
        run('validation')
        r=read(OUT/'validation/block_000.json')
        write(OUT/'validation.json',dict(passed=True,tests=result.testsRun,source=sources(),created_utc=stamp(),measured_wall_seconds=r['wall_seconds'],projected_31_blocks_seconds=31*r['wall_seconds'],peak_memory_bytes=r['peak_memory_bytes']))
    elif mode in ('development','confirmation'):run(mode)
    elif mode=='select':select()
    elif mode=='analyze':analyze()
    elif mode=='audit':audit()
    else:raise ValueError(mode)
