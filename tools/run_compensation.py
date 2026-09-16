"""Bounded, resumable EXP-009 validation/development/confirmation/audit."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import datetime
import hashlib
import json
import time
import platform
import ctypes
import unittest
import io
import numpy as np
from exp009.compensation import *

OUT=ROOT/'results/exp009'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp'); tmp.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8'); tmp.replace(p)
def peak():
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(s,ctypes.c_size_t) for s in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
    c=Counters(); c.cb=ctypes.sizeof(c)
    handle=ctypes.windll.kernel32.GetCurrentProcess
    handle.restype=ctypes.c_void_p
    fn=ctypes.windll.psapi.GetProcessMemoryInfo
    fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    if not fn(handle(),ctypes.byref(c),c.cb): raise OSError('Memory counter failed')
    return c.PeakWorkingSetSize
def signature():
    paths=[ROOT/p for p in ['exp009/compensation.py','tools/run_compensation.py','tools/prepare_compensation.py','tools/prepare_compensation_reference.m','tests/test_exp009.py','experiments/EXP-009-protocol.md']]
    paths+=list((ROOT/'research/sources/exp009').rglob('*'))
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}
def verify_frozen():
    frozen=json.loads((OUT/'validation.json').read_text())
    if signature()!=frozen['source_hashes']: raise ValueError('Source drift')
    if not frozen['passed']: raise ValueError('Validation failed')
def caps():
    storage=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    if storage>1024**3 or peak()>2*1024**3: raise RuntimeError('Storage or memory cap')
    return storage
def block(stage,index,rates):
    directory=OUT/['validation','development','confirmation'][stage]; directory.mkdir(parents=True,exist_ok=True)
    record=directory/f'block_{index:03}.json'; data=record.with_suffix('.npz')
    if record.exists():
        old=json.loads(record.read_text())
        if old['sha256']!=sha(data) or old['rates']!=rates or old['source_hashes']!=signature(): raise ValueError('Checkpoint drift')
        return old
    start=time.perf_counter(); cpu=time.process_time(); p=parameters(); t=task(stage,index,p)
    saved,metrics=evaluate(t,p,rates)
    for v in saved.values():
        if not np.isfinite(v).all(): raise FloatingPointError('Nonfinite archive')
    tmp=data.with_suffix('.npz.tmp')
    with tmp.open('wb') as f: np.savez_compressed(f,**saved)
    tmp.replace(data)
    obj=dict(stage=stage,block=index,created_utc=now(),rates=rates,task_digest=array_digest(t),
             sha256=sha(data),source_hashes=signature(),wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,
             peak_bytes=peak(),bytes=data.stat().st_size,**metrics)
    write(record,obj); caps(); print(f'stage={stage} block={index} scores={metrics["scores"]} wall={obj["wall_seconds"]:.2f}',flush=True)
    return obj
def validation():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'validation.json').exists(): raise ValueError('Validation already recorded')
    from tests.test_exp009 import CompensationTests
    stream=io.StringIO(); result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CompensationTests))
    (OUT/'validation_tests.txt').write_text(stream.getvalue(),encoding='utf-8')
    if not result.wasSuccessful():
        write(OUT/'validation_failure.json',dict(created_utc=now(),tests=stream.getvalue())); raise ValueError('Tests failed')
    rates=[RATES.tolist(),RATES.tolist()]
    b=block(0,100,rates)
    p=parameters(); t=task(0,100,p); start=time.perf_counter(); saved,metrics=evaluate(t,p,rates)
    with np.load(OUT/'validation/block_100.npz') as z:
        for k,v in saved.items(): np.testing.assert_array_equal(v,z[k])
    errors=[]
    src=ROOT/'results/exp009_source'
    x=np.loadtxt(src/'fixture_inputs.csv',delimiter=',').reshape(24,8,4,order='F')
    init=np.loadtxt(src/'fixture_initial.csv',delimiter=','); labels=np.arange(8)%2==0
    for arm in (0,1):
        y=encode(x,*model(p,arm)); y/=y[:,:,:2].max()
        ref=np.loadtxt(src/f'fixture_Y{arm+1}.csv',delimiter=',').reshape(2000,8,4,order='F')
        w=learn(y[:,:,:2],labels,init,.001)
        errors.extend([float(abs(y-ref).max()),float(abs(w-np.loadtxt(src/f'fixture_W{arm+1}.csv',delimiter=',')).max()),abs(float(probabilities(y[:,:,2:],w,labels).mean())-np.loadtxt(src/'fixture_stats.csv',delimiter=',')[arm,2])])
    # Full-size workload includes ten rates per arm, an upper bound for confirmation work.
    projected_seconds=b['wall_seconds']*52*3
    if projected_seconds>1800: raise RuntimeError('Measured projection exceeds cap')
    obj=dict(created_utc=now(),passed=True,tests=result.testsRun,full_size_replay_exact=True,
             author_runtime='GNU Octave 11.3.0',author_fixture_max_errors=errors,tolerance=1e-10,
             source_hashes=signature(),python=sys.version,numpy=np.__version__,platform=platform.platform(),
             measured_full_block=b,validation_replay_seconds=time.perf_counter()-start,
             measured_projection_with_3x_reserve_seconds=projected_seconds,
             caps=dict(campaign_wall_seconds=1800,peak_bytes=2*1024**3,output_bytes=1024**3,workers=1,blas_threads=1,max_confirmation_blocks=48))
    write(OUT/'validation.json',obj); print(json.dumps({k:obj[k] for k in ['passed','tests','author_fixture_max_errors','measured_projection_with_3x_reserve_seconds']}))
def development():
    verify_frozen(); start=time.perf_counter(); rates=[RATES.tolist(),RATES.tolist()]
    rows=[block(1,i,rates) for i in range(4)]
    scores=np.array([r['scores'] for r in rows]); means=scores.mean(0)
    selected=[int(np.flatnonzero(m>=m.max()-1e-12)[0]) for m in means]
    delta=scores[:,1,selected[1]]-scores[:,0,selected[0]]
    sd=float(delta.std(ddof=1)); uncapped=int(np.ceil((1.96*1.25*sd/.02)**2))
    n=int(min(48,max(24,8*np.ceil(uncapped/8))))
    settings=dict(created_utc=now(),selected_indices=selected,selected_rates=[float(RATES[i]) for i in selected],
                  means=means.tolist(),paired_sd=sd,uncapped_n=uncapped,n=n,projected_halfwidth=1.96*1.25*sd/np.sqrt(n),
                  source_hashes=signature(),development_sha256={str((OUT/'development'/f'block_{i:03}.json').relative_to(ROOT)):sha(OUT/'development'/f'block_{i:03}.json') for i in range(4)},
                  stage_wall_seconds=time.perf_counter()-start)
    target=OUT/'selection.json'
    if target.exists():
        old=json.loads(target.read_text()); assert old['selected_rates']==settings['selected_rates'] and old['n']==n
    else: write(target,settings)
    print(json.dumps(settings,indent=2))
def confirmation():
    verify_frozen(); selection=json.loads((OUT/'selection.json').read_text())
    assert selection['source_hashes']==signature()
    for f,h in selection['development_sha256'].items(): assert sha(ROOT/f)==h
    a,b=selection['selected_rates']; rates=[[a],[b,a]]
    for i in range(selection['n']):
        block(2,i,rates)
        elapsed=sum(json.loads(p.read_text())['wall_seconds'] for stage in ['development','confirmation'] for p in (OUT/stage).glob('block_*.json'))
        if elapsed>1800: raise RuntimeError('Campaign wall cap')
    print('Confirmation sample complete; audit required.')
def audit():
    verify_frozen(); start=time.perf_counter(); cpu=time.process_time(); p=parameters(); checks=0
    selection=json.loads((OUT/'selection.json').read_text()); rows=[]
    for stage,count in [(1,4),(2,selection['n'])]:
        for i in range(count):
            directory=OUT/['validation','development','confirmation'][stage]
            record=json.loads((directory/f'block_{i:03}.json').read_text()); path=directory/f'block_{i:03}.npz'
            assert sha(path)==record['sha256'] and record['source_hashes']==signature()
            t=task(stage,i,p); assert array_digest(t)==record['task_digest']
            with np.load(path) as z:
                for k,v in t.items(): np.testing.assert_array_equal(z[k],v)
                for arm in (0,1):
                    tr,te,scale=features(t,p,arm); assert scale==z[f'scale_{arm}']
                    for j,eta in enumerate(record['rates'][arm]):
                        w=learn(tr,t['labels'],t['initial'],eta)
                        np.testing.assert_array_equal(w,z[f'weights_{arm}_{j}'])
                        prob=probabilities(te,w,t['labels'])
                        np.testing.assert_array_equal(prob,z[f'probabilities_{arm}_{j}'])
                        assert float(prob.mean())==record['scores'][arm][j]
                        checks+=1
            if stage==2: rows.append(record)
    historical=json.loads((ROOT/'research/exp009_historical_hashes.json').read_text())
    changed=[f for f,h in historical.items() if not (ROOT/f).exists() or sha(ROOT/f)!=h]
    assert not changed,changed
    raw=np.array([r['scores'][0][0] for r in rows]); comp=np.array([r['scores'][1][0] for r in rows]); matched=np.array([r['scores'][1][1] for r in rows])
    boot=np.random.default_rng(900991).integers(0,len(rows),(50000,len(rows)))
    def summary(values):
        return dict(mean=float(values.mean()),interval=np.quantile(values[boot].mean(1),[.025,.975]).tolist())
    contrast=summary(comp-raw); half=(contrast['interval'][1]-contrast['interval'][0])/2
    passed=bool(comp.mean()>=.55 and contrast['interval'][0]>.03 and half<=.02)
    resources={}
    for name in ['validation','development','confirmation']:
        rr=[json.loads(f.read_text()) for f in (OUT/name).glob('block_*.json')]
        resources[name]=dict(blocks=len(rr),wall_seconds=sum(r['wall_seconds'] for r in rr),cpu_seconds=sum(r['cpu_seconds'] for r in rr),peak_bytes=max(r['peak_bytes'] for r in rr),archive_bytes=sum(r['bytes'] for r in rr))
    result=dict(created_utc=now(),gate_passed=passed,classification='validated author-parameter positive control' if passed else 'positive-control gate not met',
                n=len(rows),uncertainty_unit='independent new task block conditional on one fixed author-fitted network',
                primary=contrast,uncompensated=summary(raw),compensated=summary(comp),matched_rate=summary(matched-raw),halfwidth=half,
                profiles=[{k:float(np.mean([r['profiles'][a][k] for r in rows])) for k in rows[0]['profiles'][a]} for a in (0,1)],
                numerical_audits=checks,all_archives_replayed_exactly=True,historical_files_verified=len(historical),resources=resources,
                audit_wall_seconds=time.perf_counter()-start,audit_cpu_seconds=time.process_time()-cpu,total_output_bytes=caps(),source_hashes=signature(),selection_sha256=sha(OUT/'selection.json'))
    write(OUT/'analysis.json',result); write(ROOT/'research/runs/EXP-009-positive-control.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('stage',choices=['validation','development','confirmation','audit']); args=parser.parse_args()
    try: globals()[args.stage]()
    except Exception as exc:
        write(OUT/f'failure_{args.stage}_{time.time_ns()}.json',dict(created_utc=now(),stage=args.stage,error=repr(exc)))
        raise
