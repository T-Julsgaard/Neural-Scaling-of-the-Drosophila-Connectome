"""Prospectively frozen EXP-007 execution, audit and paired inference."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import json
import math
import platform
import shutil
import sys
import time
import unittest
import numpy as np
from exp002.data import ROOT, sha256, load_projection
from exp002.campaign import peak_memory
from exp006.campaign import read, write
from exp007.homeostasis import *

CONDITIONS = [(s, r, l, False) for s in (2, 6) for r in ('per_pair', 'total') for l in (2, 4, 8, 16)]
SHIFT = [(s, 'per_pair', 16, True) for s in (2, 6)]
REPORT = ('baseline6', 'ordinary', 'homeostasis', 'sham', 'random_ordinary', 'random_homeostasis', 'direct', 'oracle', 'fixed_homeostasis', 'fixed_sham')


def folder(stage): return ROOT/f'results/exp007_{stage}'


def snapshot():
    paths = [*ROOT.glob('exp007/*.py'), *ROOT.glob('exp002/*.py'), *ROOT.glob('exp006/*.py'), ROOT/'tests/test_exp007.py', ROOT/'tools/run_homeostasis.py', ROOT/'experiments/EXP-007-protocol.md']
    return {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(paths)}


def prepare():
    out = folder('calibration'); out.mkdir(parents=True, exist_ok=True)
    if (out/'record.json').exists():
        record = read(out/'record.json')
        assert record['source'] == snapshot()
        assert record['sha256'] == sha256(out/'calibration.npz')
        return
    start = time.perf_counter(); p, provenance = load_projection()
    priority = rng('validation', 9000, 7).permutation(73)
    nulls = [random_projection(p, rng('validation', 9000, 8, j)) for j in range(3)]
    projections = np.array([p]+[v[0] for v in nulls])
    pool, valid = calibration_pool(), calibration_pool(True)
    arrays = dict(projections=projections, priority=priority, fit_pool=pool, validation_pool=valid)
    records = {}
    for j, projection in enumerate(projections):
        for strength in (.25, .5):
            key = f'p{j}_l{strength}'
            theta, rec = fit(projection, pool, priority, strength)
            rec['validation_before'] = (encode(valid, projection, priority, 6, np.zeros(73)) > 0).mean(0).tolist()
            rec['validation_after'] = (encode(valid, projection, priority, 6, theta) > 0).mean(0).tolist()
            arrays[key] = theta; records[key] = rec
            if j == 0:
                for rep in range(3): arrays[f'sham{rep}_l{strength}'] = theta[rng('validation', 9000, 9, rep).permutation(73)]
    np.savez_compressed(out/'calibration.npz', **arrays)
    write(out/'record.json', dict(source=snapshot(), sha256=sha256(out/'calibration.npz'), fits=records, randomization=[a[1] for a in nulls], projection=provenance, wall_seconds=time.perf_counter()-start, pool_hash=digest(pool), validation_pool_hash=digest(valid)))


def calibration():
    path = folder('calibration')/'calibration.npz'
    assert sha256(path) == read(folder('calibration')/'record.json')['sha256']
    with np.load(path) as a: return {k: a[k] for k in a.files}


def specs(stage, selection=None):
    if stage != 'confirmation': return {m: candidates(m) for m in METHODS}
    selected = selection['settings']
    result = {m: [selected[m]] for m in METHODS}
    result['baseline6'] = [selected['baseline6']]
    for label in ('homeostasis', 'sham'):
        result['fixed_'+label] = [{**selected[label], 'eta': selected['baseline6']['eta'], 'temperature': selected['baseline6']['temperature']}]
    return {m: result[m] for m in REPORT}


def compute(stage, number, settings):
    start, cpu = time.perf_counter(), time.process_time()
    cal = calibration(); priority = cal['priority']; arrays = {}; scores = []
    conditions = CONDITIONS+(SHIFT if stage == 'confirmation' else [])
    for ci, (s, regime, load, shift) in enumerate(conditions):
        t = task(stage, number, s, load, regime)
        if shift: t = shifted(t)
        key = f'c{ci}'
        arrays[key+'_task_hash'] = np.array(digest(t['p'], t['labels'], *t['obs'], *t['outcomes'], *t['uniforms'], t['probes']))
        arrays[key+'_input_overlap'] = t['p'].reshape(-1, 40) @ t['p'].reshape(-1, 40).T
        arrays[key+'_labels'] = t['labels']
        arms = []
        for method, configs in settings.items():
            groups = {}
            for index, c in enumerate(configs): groups.setdefault((c['k'], c['strength']), []).append(index)
            values = np.zeros((len(configs), len(NAMES)))
            for gi, ((k, strength), indices) in enumerate(groups.items()):
                reps = 3 if ('random' in method or 'sham' in method) else 1
                summaries = []
                for rep in range(reps):
                    pj = rep+1 if 'random' in method else 0
                    theta = np.zeros(73) if strength == 0 else cal[f'sham{rep}_l{strength}' if 'sham' in method else f'p{pj}_l{strength}']
                    r = sequence(t, method, cal['projections'][pj], priority, theta, [configs[i] for i in indices])
                    summaries.append(summarize(r))
                    prefix = f'{key}_{method}_g{gi}_r{rep}_'
                    for name, a in r.items(): arrays[prefix+name] = a
                    arrays[prefix+'indices'] = np.array(indices)
                values[indices] = np.mean(summaries, axis=0)
            arms.append(values)
        scores.append(arms)
    arrays['scores'] = np.array(scores)
    return arrays, dict(wall_seconds=time.perf_counter()-start, cpu_seconds=time.process_time()-cpu, peak_memory_bytes=peak_memory())


def verify(c):
    assert c['source'] == snapshot(), 'Frozen source drift'
    assert c['python'] == platform.python_version() and c['numpy'] == np.__version__
    assert c['calibration_sha256'] == sha256(folder('calibration')/'calibration.npz')


def freeze(stage):
    out = folder(stage); out.mkdir(parents=True, exist_ok=True)
    if (out/'contract.json').exists():
        c = read(out/'contract.json'); verify(c); return c
    v = read(ROOT/'research/exp007_validation.json')
    assert v['status'] == 'passed' and v['source'] == snapshot()
    selection = None
    if stage == 'confirmation':
        assert read(folder('development')/'audit.json')['status'] == 'passed'
        selection = read(folder('development')/'selection.json')
    blocks = list(range(1000, 1000+selection['confirmation_n'])) if selection else list(range(100, 108))
    c = dict(stage=stage, blocks=blocks, settings=specs(stage, selection), source=snapshot(), python=platform.python_version(), numpy=np.__version__, platform=platform.platform(), executable=sys.executable, calibration_sha256=sha256(folder('calibration')/'calibration.npz'), selection_sha256=sha256(folder('development')/'selection.json') if selection else None, validation_sha256=sha256(ROOT/'research/exp007_validation.json'), created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    for name in c['source']:
        dest = out/'frozen_source'/name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT/name, dest)
    write(out/'contract.json', c)
    return c


def block(stage, b):
    out = folder(stage); c = read(out/'contract.json'); verify(c)
    assert b in c['blocks']; path = out/f'block_{b}.npz'; record = path.with_suffix('.json')
    if record.exists():
        assert read(record)['sha256'] == sha256(path)
        assert read(record)['contract_sha256'] == sha256(out/'contract.json')
        return b
    arrays, rec = compute(stage, b, c['settings'])
    with path.with_suffix('.tmp').open('wb') as f: np.savez_compressed(f, **arrays)
    path.with_suffix('.tmp').replace(path)
    rec.update(sha256=sha256(path), contract_sha256=sha256(out/'contract.json'))
    write(record, rec)
    assert sum(p.stat().st_size for p in out.glob('*.npz')) < 2_000_000_000
    return b


def run(stage, workers):
    c = freeze(stage)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for f in as_completed([pool.submit(block, stage, b) for b in c['blocks']]): print(stage, f.result(), 'complete', flush=True)
    audit(stage); analyze(stage)


def audit(stage):
    out = folder(stage); c = read(out/'contract.json'); verify(c)
    conditions = CONDITIONS+(SHIFT if stage == 'confirmation' else [])
    for b in c['blocks']:
        rec = read(out/f'block_{b}.json')
        assert rec['sha256'] == sha256(out/f'block_{b}.npz') and rec['contract_sha256'] == sha256(out/'contract.json')
        with np.load(out/f'block_{b}.npz') as a:
            rebuilt = []
            for ci, (s, regime, load, shift) in enumerate(conditions):
                t = task(stage, b, s, load, regime)
                if shift: t = shifted(t)
                assert str(a[f'c{ci}_task_hash']) == digest(t['p'], t['labels'], *t['obs'], *t['outcomes'], *t['uniforms'], t['probes'])
                arms = []
                for method, configs in c['settings'].items():
                    values = np.zeros((len(configs), len(NAMES))); seen = []
                    for gi in range(len(set((v['k'], v['strength']) for v in configs))):
                        reps = []
                        for rep in range(3 if ('random' in method or 'sham' in method) else 1):
                            prefix = f'c{ci}_{method}_g{gi}_r{rep}_'
                            ix = a[prefix+'indices']; bd = a[prefix+'boundaries']
                            np.testing.assert_array_equal(bd[1:, 0], bd[:-1, 1])
                            reps.append(summarize(dict(history=a[prefix+'history'], reverse=a[prefix+'reverse'])))
                            assert np.isfinite(a[prefix+'final']).all()
                        values[ix] = np.mean(reps, axis=0); seen.extend(ix.tolist())
                    assert sorted(seen) == list(range(len(configs)))
                    arms.append(values)
                rebuilt.append(arms)
            np.testing.assert_array_equal(a['scores'], rebuilt)
    replay, _ = compute(stage, c['blocks'][0], c['settings'])
    with np.load(out/f'block_{c["blocks"][0]}.npz') as a:
        assert set(a.files) == set(replay)
        for k, v in replay.items(): np.testing.assert_array_equal(a[k], v)
    write(out/'audit.json', dict(status='passed', blocks=len(c['blocks']), replay_block=c['blocks'][0], contract_sha256=sha256(out/'contract.json'), source=snapshot()))


def interval(v, coverage=.95, draws=50000, lower_alpha=None):
    v = np.asarray(v); indices = np.random.default_rng(700791).integers(len(v), size=(draws, len(v)))
    means = v[indices].mean(1)
    if lower_alpha is not None: return float(np.quantile(means, lower_alpha))
    return dict(mean=float(v.mean()), interval=np.quantile(means, [(1-coverage)/2, (1+coverage)/2]).tolist())


def analyze(stage):
    out = folder(stage); c = read(out/'contract.json')
    data = np.array([np.load(out/f'block_{b}.npz')['scores'] for b in c['blocks']])
    methods = list(c['settings'])
    if stage == 'development':
        score = data[..., [0, 2, 4, 5, 6]].mean(axis=(0, 1, 4))
        chosen = {m: int(np.flatnonzero(score[j].max()-score[j] <= 1e-12)[0]) for j, m in enumerate(methods)}
        base = [i for i, v in enumerate(c['settings']['ordinary']) if v['k'] == 6]
        chosen['baseline6'] = base[int(np.argmax(score[0, base]))]
        selected = {m: c['settings'][m][i] for m, i in chosen.items() if m != 'baseline6'}
        selected['baseline6'] = c['settings']['ordinary'][chosen['baseline6']]
        h = data[:, 11, methods.index('homeostasis'), chosen['homeostasis'], 0]
        contrasts = [h-data[:, 11, methods.index(m), chosen[m], 0] for m in ('ordinary', 'sham')]
        contrasts.append(h-data[:, 11, 0, chosen['baseline6'], 0])
        sd = max(float(v.std(ddof=1)) for v in contrasts)
        needed = int(math.ceil((2.4*1.25*sd/.025)**2)); n = max(24, min(64, 8*math.ceil(needed/8)))
        write(out/'selection.json', dict(settings=selected, indices=chosen, scores=score.tolist(), confirmation_n=n, precision=dict(max_sd=sd, uncapped_n=needed, projected_halfwidth=2.4*1.25*sd/np.sqrt(n)), contract_sha256=sha256(out/'contract.json')))
        print(json.dumps(dict(selected=selected, confirmation_n=n, sd=sd)), flush=True)
        return
    data = data[..., 0, :]; idx = {m: methods.index(m) for m in methods}
    primary = {}; guards = {}
    for m in ('baseline6', 'ordinary', 'sham'):
        delta = data[:, 11, idx['homeostasis']]-data[:, 11, idx[m]]
        primary[m] = interval(delta[:, 0], 1-.05/3)
        guards[m] = {NAMES[mi]: dict(mean=float(delta[:, mi].mean()), lower=interval(delta[:, mi], draws=100000, lower_alpha=.05/12)) for mi in (2, 5, 6, 1)}
    profiles = {}
    for ci, condition in enumerate(CONDITIONS+SHIFT):
        key = '_'.join(map(str, condition))
        profiles[key] = {m: {name: interval(data[:, ci, idx[m], mi]) for mi, name in enumerate(NAMES)} for m in methods}
        profiles[key]['contrasts'] = {m: {name: interval(data[:, ci, idx['homeostasis'], mi]-data[:, ci, idx[m], mi]) for mi, name in enumerate(NAMES)} for m in ('baseline6', 'ordinary', 'sham', 'direct')}
        profiles[key]['fixed_contrasts'] = {m: {name: interval(data[:, ci, idx[m], mi]-data[:, ci, idx['baseline6'], mi]) for mi, name in enumerate(NAMES)} for m in ('fixed_homeostasis', 'fixed_sham')}
    capacity = {}
    for m in REPORT[:7]:
        for si, s in enumerate((2, 6)):
            for ri, regime in enumerate(('per_pair', 'total')):
                bounds = []; passed = True; certified = []
                for li, load in enumerate((2, 4, 8, 16)):
                    lower = [interval(data[:, si*8+ri*4+li, idx[m], mi], draws=200000, lower_alpha=.05/224) for mi in (0, 2)]
                    bounds.append(lower); passed = passed and min(lower) > .8
                    if passed: certified.append(load)
                capacity[f'{m}_s{s}_{regime}'] = dict(certified_load=max(certified) if certified else None, lower_bounds=bounds)
    write(out/'analysis.json', dict(primary=primary, guardrails=guards, profiles=profiles, capacity=capacity, blocks=len(c['blocks']), contract_sha256=sha256(out/'contract.json')))
    print(json.dumps(dict(primary=primary, guardrails=guards)), flush=True)


def validate():
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_exp007')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    assert result.wasSuccessful()
    prepare()
    a, rec = compute('validation', 0, specs('validation'))
    b, _ = compute('validation', 0, specs('validation'))
    for key in a: np.testing.assert_array_equal(a[key], b[key])
    rec.update(status='passed', tests=result.testsRun, source=snapshot(), full_replay='exact', estimated_development_compute_seconds_three_workers=rec['wall_seconds']*8/3, storage_budget_bytes=2_000_000_000)
    write(ROOT/'research/exp007_validation.json', rec)
    print(json.dumps(rec), flush=True)
