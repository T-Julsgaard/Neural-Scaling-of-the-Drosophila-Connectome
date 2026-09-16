"""Freeze, checkpoint, select, evaluate and audit EXP-005."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
import json
import shutil
import sys
import time
import platform
import numpy as np
from exp002.data import ROOT, sha256, load_projection
from exp002.campaign import atomic_json, peak_memory, read_json
from exp005.mechanism import Inputs, Setting, configs, episode, metrics, fixed


def read(path):
    return read_json(path)


def snapshot():
    paths = [*ROOT.glob('exp005/*.py'), ROOT/'tests/test_exp005.py', ROOT/'tools/run_mechanism.py',
             ROOT/'experiments/EXP-005-protocol.md', *ROOT.glob('exp002/*.py')]
    return {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(paths)}


def folder(stage):
    return ROOT/f'results/exp005_{stage}'


def verify(contract):
    for name, expected in contract['source'].items():
        if sha256(ROOT/name) != expected:
            raise ValueError('Frozen source changed: '+name)
    if contract['numpy'] != np.__version__ or contract['python'] != platform.python_version():
        raise ValueError('Environment changed')


def freeze(stage):
    target = folder(stage)
    target.mkdir(parents=True, exist_ok=True)
    path = target/'contract.json'
    if path.exists():
        contract = read(path)
        verify(contract)
        return contract
    validation = read(ROOT/'research/exp005_validation.json')
    if validation['status'] != 'passed' or validation['source'] != snapshot():
        raise ValueError('Need current passing validation')
    selected = None
    selection_hash = None
    if stage == 'evaluation':
        audit = read(folder('development')/'audit.json')
        if audit['status'] != 'passed':
            raise ValueError('Development audit required')
        selected = read(folder('development')/'selection.json')['settings']
        selection_hash = sha256(folder('development')/'selection.json')
    contract = {'stage': stage, 'source': snapshot(), 'numpy': np.__version__,
                'python': platform.python_version(), 'platform': platform.platform(),
                'executable': sys.executable, 'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'settings': [asdict(c) for c in configs(selected)], 'selection_sha256': selection_hash,
                'blocks': list(range(100,106) if stage == 'development' else range(1000,1032)),
                'projection': load_projection()[1], 'validation_sha256': sha256(ROOT/'research/exp005_validation.json')}
    for name in contract['source']:
        dest = target/'frozen_source'/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, dest)
    atomic_json(path, contract)
    return contract


def block(stage, number, contract_hash):
    start, cpu = time.perf_counter(), time.process_time()
    target = folder(stage)
    contract = read(target/'contract.json')
    verify(contract)
    if sha256(target/'contract.json') != contract_hash or number not in contract['blocks']:
        raise ValueError('Contract mismatch')
    path = target/f'block_{number}.npz'
    record = target/f'block_{number}.json'
    if record.exists():
        meta = read(record)
        if meta['contract_sha256'] != contract_hash or sha256(path) != meta['sha256']:
            raise ValueError('Corrupted completed block')
        return meta
    settings = [Setting(**c) for c in contract['settings']]
    rows = [episode(Inputs(stage, number, e), settings) for e in range(20)]
    data = {key: np.array([r[key] for r in rows]) for key in rows[0]}
    with path.with_suffix('.tmp').open('wb') as f:
        np.savez_compressed(f, **data)
    path.with_suffix('.tmp').replace(path)
    meta = {'block': number, 'contract_sha256': contract_hash, 'sha256': sha256(path),
            'metrics': {k: v.tolist() for k,v in metrics(data['trace'],data['probes']).items()},
            'wall_seconds': time.perf_counter()-start, 'cpu_seconds': time.process_time()-cpu,
            'peak_worker_memory_bytes': peak_memory()}
    atomic_json(record, meta)
    return meta


def interval(values, coverage=.95):
    a = np.asarray(values)
    indices = np.random.default_rng(60591).integers(0, len(a), (20000, len(a)))
    lo, hi = np.quantile(a[indices].mean(axis=1), [(1-coverage)/2,(1+coverage)/2])
    return {'mean': float(a.mean()), 'interval': [float(lo),float(hi)], 'coverage': coverage,
            'block_values': a.tolist()}


def analyze(stage):
    target = folder(stage)
    contract = read(target/'contract.json')
    rows = [read(target/f'block_{b}.json') for b in contract['blocks']]
    ids = [c['id'] for c in contract['settings']]
    values = {k: np.array([r['metrics'][k] for r in rows]) for k in rows[0]['metrics']}
    result = {'profiles': {id: {k: interval(v[:,i]) for k,v in values.items()} for i,id in enumerate(ids)}}
    if stage == 'development':
        scores = sum(values[k].mean(axis=0) for k in ('acquisition','early_reversal','retention_after','new_late'))/4
        chosen = []
        for k in (4,6):
            indices = [i for i,c in enumerate(contract['settings']) if c['k']==k and '_tune_' in c['id']]
            best = max(scores[i] for i in indices)
            tied = [i for i in indices if best-scores[i] <= 1e-6]
            index = min(tied,key=lambda i:(contract['settings'][i]['eta'],-contract['settings'][i]['temperature']))
            chosen.append(contract['settings'][index])
        selection = {'settings': chosen, 'scores': dict(zip(ids,map(float,scores))),
                     'development_contract_sha256': sha256(target/'contract.json')}
        selection_path = target/'selection.json'
        if selection_path.exists() and read(selection_path) != selection:
            raise ValueError('Selection changed')
        atomic_json(selection_path,selection)
    else:
        tuned = [id for id in ids if '_tune_' in id]
        pairs = {'historical': ('k6_historical','k4_historical'),
                 'slow_matched': ('k6_historical','k4_slow'),
                 'fast_matched': ('k6_fast','k4_historical'), 'tuned': (tuned[1],tuned[0]),
                 'equal_low_amplitude': ('k6_historical','k4_low_amplitude'),
                 'equal_high_amplitude': ('k6_high_amplitude','k4_historical'),
                 'low_norm': ('k6_historical','k4_low_norm'),
                 'high_norm': ('k6_high_norm','k4_historical')}
        result['contrasts'] = {name: {k: interval(v[:,ids.index(a)]-v[:,ids.index(b)],
              .9875 if name in ('historical','slow_matched','fast_matched','tuned') and k=='retention_after' else .95)
              for k,v in values.items()} for name,(a,b) in pairs.items()}
        result['contrast_settings'] = {name:list(pair) for name,pair in pairs.items()}
        geometry, counts = [], []
        for b in contract['blocks']:
            with np.load(target/f'block_{b}.npz') as raw:
                geometry.append(raw['geometry'].mean(axis=0))
                counts.append(raw['counts'].sum(axis=0))
        result['geometry'] = {f'k{k}': {name: interval(np.array(geometry)[:,i,j]) for j,name in enumerate(
            ('same_cue_cosine','between_cue_cosine','old_new_cosine','episode_never_active'))} for i,k in enumerate((4,6))}
        result['block_never_active'] = {f'k{k}': interval((np.array(counts)[:,i]==0).mean(axis=1)) for i,k in enumerate((4,6))}
    return result


def run(stage, workers=3):
    start = time.perf_counter()
    contract = freeze(stage)
    target = folder(stage)
    try:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(block,stage,b,sha256(target/'contract.json')) for b in contract['blocks']]
            for count,f in enumerate(as_completed(futures),1):
                row = f.result()
                print(json.dumps({'stage':stage,'complete':count,'of':len(futures),'block':row['block']}),flush=True)
                if time.perf_counter()-start > 7200 or shutil.disk_usage(target).free < 5*1024**3:
                    raise RuntimeError('Resource limit')
                if sum(p.stat().st_size for p in target.rglob('*') if p.is_file()) > 2*1024**3:
                    raise RuntimeError('Storage cap')
        atomic_json(target/'analysis.json',analyze(stage))
        atomic_json(target/f'invocation_{time.time_ns()}.json',{'wall_seconds':time.perf_counter()-start,'workers':workers})
    except Exception as exc:
        atomic_json(target/f'failure_{time.time_ns()}.json',{'error':repr(exc),'wall_seconds':time.perf_counter()-start})
        raise


def audit(stage):
    start = time.perf_counter()
    target = folder(stage)
    contract = read(target/'contract.json')
    verify(contract)
    settings = [Setting(**c) for c in contract['settings']]
    for b in contract['blocks']:
        path = target/f'block_{b}.npz'
        row = read(target/f'block_{b}.json')
        if row['contract_sha256'] != sha256(target/'contract.json') or sha256(path) != row['sha256']:
            raise ValueError('Raw hash mismatch')
        with np.load(path,allow_pickle=False) as raw:
            assert raw['trace'].shape == (20,len(settings),384,11)
            assert raw['probes'].shape == (20,len(settings),4)
            for key in ('trace','probes','plus','minus','geometry','counts'):
                assert np.isfinite(raw[key]).all()
            assert np.all(raw['trace'][:,-2:,:,0]==.5)
            assert np.all(raw['probes'][:,-2:]==.5)
            regenerated = {k:v.tolist() for k,v in metrics(raw['trace'],raw['probes']).items()}
            assert regenerated == row['metrics']
            for ep in range(20):
                task = Inputs(stage,b,ep)
                assert task.digest()==str(raw['task_hash'][ep])
                if b == contract['blocks'][0]:
                    replayed = episode(task,settings)
                    for key,value in replayed.items():
                        np.testing.assert_array_equal(value,raw[key][ep])
    assert analyze(stage) == read(target/'analysis.json')
    if stage == 'evaluation':
        assert sha256(folder('development')/'selection.json') == contract['selection_sha256']
    result = {'status':'passed','blocks':len(contract['blocks']),'episodes':20*len(contract['blocks']),
              'configuration_episodes':20*len(contract['blocks'])*len(settings),
              'raw_hashes_metrics_task_regeneration':True,'full_block_exact_replay':True,
              'contract_sha256':sha256(target/'contract.json'),'analysis_sha256':sha256(target/'analysis.json'),
              'wall_seconds':time.perf_counter()-start}
    atomic_json(target/'audit.json',result)
    print(json.dumps(result),flush=True)


def validate():
    import unittest
    suite = unittest.TestSuite([unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=p)
                               for p in ('test_exp005.py','test_baseline.py','test_exp004.py')])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError('Validation failed')
    replay = episode(Inputs('validation',0,10),fixed(),True)
    out = ROOT/'results/validation/exp005'
    out.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out/'fixed_action_replay.npz',**replay)
    atomic_json(ROOT/'research/exp005_validation.json',{'status':'passed','tests_run':result.testsRun,
                'source':snapshot(),'replay_sha256':sha256(out/'fixed_action_replay.npz')})
