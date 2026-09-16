"""Frozen, resumable local campaign and block-level inference."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import json
import platform
import shutil
import sys
import time
import unittest
import numpy as np
from exp002.data import ROOT, sha256, load_projection
from exp002.campaign import peak_memory
from exp006.memory import *


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    tmp.replace(path)


def read(path):
    return json.loads(Path(path).read_text())


def folder(stage):
    return ROOT/f'results/exp006_{stage}'


def snapshot():
    paths = [*ROOT.glob('exp006/*.py'), ROOT/'tests/test_exp006.py', ROOT/'tools/run_memory.py', ROOT/'experiments/EXP-006-protocol.md', *ROOT.glob('exp002/*.py')]
    return {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(paths)}


def verify(c):
    assert c['source'] == snapshot(), 'Frozen source drift'
    assert c['numpy'] == np.__version__ and c['python'] == platform.python_version()


def compute(stage, number, settings):
    start, cpu = time.perf_counter(), time.process_time()
    native, provenance = load_projection()
    priority = rng(stage, number, 7).permutation(73)
    nulls = [random_projection(native, rng(stage, number, 8, i)) for i in range(3)]
    arrays = {'native': native, 'random_projections': np.array([a[0] for a in nulls]), 'priority': priority}
    scores = []
    for overlap in OVERLAPS:
        for regime in REGIMES:
            for load in LOADS:
                key = f's{overlap}_{regime}_l{load}'
                t = task(stage, number, overlap, load, regime)
                flat = t['p'].reshape(-1, 40)
                arrays[key+'_input_overlap'] = flat @ flat.T
                arrays[key+'_labels'] = t['labels']
                arrays[key+'_task_hash'] = np.array(digest(t['p'], t['labels'], *t['obs'], *t['outcomes'], *t['uniforms'], t['probes']))
                family_scores = []
                for family in FAMILIES:
                    reps = [a[0] for a in nulls] if family.startswith('random') else [native]
                    values = []
                    for rep, projection in enumerate(reps):
                        result = sequence(t, family, projection, priority, settings[family])
                        values.append(metrics(result))
                        for name, a in result.items():
                            arrays[f'{key}_{family}_{rep}_{name}'] = a
                    family_scores.append(np.mean(values, axis=0))
                scores.append(family_scores)
    arrays['scores'] = np.array(scores)
    return arrays, {'wall_seconds': time.perf_counter()-start, 'cpu_seconds': time.process_time()-cpu, 'peak_memory_bytes': peak_memory(), 'randomization': [a[1] for a in nulls], 'projection': provenance}


def freeze(stage):
    target = folder(stage); target.mkdir(parents=True, exist_ok=True)
    if (target/'contract.json').exists():
        c = read(target/'contract.json'); verify(c); return c
    validation = read(ROOT/'research/exp006_validation.json')
    assert validation['status'] == 'passed' and validation['source'] == snapshot()
    selection = None
    if stage == 'confirmation':
        assert read(folder('development')/'audit.json')['status'] == 'passed'
        selection = read(folder('development')/'selection.json')
    settings = {f: [selection['settings'][f]] if selection else GRID for f in FAMILIES}
    c = {'stage': stage, 'blocks': list(range(100, 106) if stage == 'development' else range(1000, 1032)), 'settings': settings, 'source': snapshot(), 'python': platform.python_version(), 'numpy': np.__version__, 'platform': platform.platform(), 'executable': sys.executable, 'projection': load_projection()[1], 'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'selection_sha256': sha256(folder('development')/'selection.json') if selection else None, 'validation_sha256': sha256(ROOT/'research/exp006_validation.json')}
    for name in c['source']:
        dest = target/'frozen_source'/name; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, dest)
    write(target/'contract.json', c)
    return c


def block(stage, number):
    target = folder(stage); c = read(target/'contract.json'); verify(c)
    assert number in c['blocks']
    record = target/f'block_{number}.json'; path = record.with_suffix('.npz')
    if record.exists():
        m = read(record)
        assert m['contract_sha256'] == sha256(target/'contract.json') and m['sha256'] == sha256(path)
        return number
    a, m = compute(stage, number, c['settings'])
    with path.with_suffix('.tmp').open('wb') as f:
        np.savez_compressed(f, **a)
    path.with_suffix('.tmp').replace(path)
    m.update(block=number, sha256=sha256(path), contract_sha256=sha256(target/'contract.json'))
    write(record, m)
    assert sum(p.stat().st_size for p in target.glob('*.npz')) < 2_000_000_000
    return number


def run(stage, workers):
    c = freeze(stage)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(block, stage, b) for b in c['blocks']]
        for f in as_completed(futures):
            print(stage, f.result(), 'complete', flush=True)
    audit(stage)
    analyze(stage)


def audit(stage):
    target = folder(stage); c = read(target/'contract.json'); verify(c)
    for b in c['blocks']:
        record = read(target/f'block_{b}.json')
        assert record['sha256'] == sha256(target/f'block_{b}.npz')
        assert record['contract_sha256'] == sha256(target/'contract.json')
        with np.load(target/f'block_{b}.npz') as a:
            rebuilt = []
            for s in OVERLAPS:
                for regime in REGIMES:
                    for load in LOADS:
                        key = f's{s}_{regime}_l{load}'
                        t = task(stage, b, s, load, regime)
                        assert str(a[key+'_task_hash']) == digest(t['p'], t['labels'], *t['obs'], *t['outcomes'], *t['uniforms'], t['probes'])
                        fam = []
                        for family in FAMILIES:
                            reps = []
                            for rep in range(3 if family.startswith('random') else 1):
                                prefix = f'{key}_{family}_{rep}_'
                                boundaries = a[prefix+'boundaries']
                                np.testing.assert_array_equal(boundaries[1:, 0], boundaries[:-1, 1])
                                reps.append(metrics({'history': a[prefix+'history'], 'reverse': a[prefix+'reverse']}))
                            fam.append(np.mean(reps, axis=0))
                        rebuilt.append(fam)
            np.testing.assert_array_equal(a['scores'], rebuilt)
    replay, _ = compute(stage, c['blocks'][0], c['settings'])
    with np.load(target/f'block_{c["blocks"][0]}.npz') as a:
        assert set(a.files) == set(replay)
        for k, v in replay.items():
            np.testing.assert_array_equal(a[k], v)
    write(target/'audit.json', {'status': 'passed', 'blocks': len(c['blocks']), 'full_replay_block': c['blocks'][0], 'source': snapshot(), 'contract_sha256': sha256(target/'contract.json')})


def interval(a, coverage=.95, draws=20000):
    a = np.asarray(a)
    samples = a[np.random.default_rng(600691).integers(len(a), size=(draws, len(a)))].mean(1)
    return {'mean': float(a.mean()), 'interval': np.quantile(samples, [(1-coverage)/2, (1+coverage)/2]).tolist()}


def analyze(stage):
    target = folder(stage); c = read(target/'contract.json')
    data = np.array([np.load(target/f'block_{b}.npz')['scores'] for b in c['blocks']])
    if stage == 'development':
        score = data[..., [0, 2, 4, 5, 6]].mean(axis=(0, 1, 4))
        chosen = [int(np.flatnonzero(v.max()-v <= 1e-12)[0]) for v in score]
        selected = {f: GRID[i] for f, i in zip(FAMILIES, chosen)}
        values = np.stack([data[:, :, j, chosen[j]] for j in range(len(FAMILIES))], axis=2)
        primary = values[:, 11, 1, 0]-values[:, 11, 0, 0]
        precision = {'primary_estimated_98_75_halfwidth_at_32': float(2.50*primary.std(ddof=1)/np.sqrt(32)), 'note': 'Six development blocks give a noisy precision estimate; fixed 32 confirmation blocks, no sample extension.', 'retention_distance_from_0_8_by_condition_family': (values[..., 0].mean(0)-.8).tolist(), 'new_learning_distance_from_0_8_by_condition_family': (values[..., 2].mean(0)-.8).tolist()}
        write(target/'selection.json', {'settings': selected, 'scores': score.tolist(), 'precision': precision, 'contract_sha256': sha256(target/'contract.json')})
        print(json.dumps({'selection': selected, 'precision': precision['primary_estimated_98_75_halfwidth_at_32']}), flush=True)
        return
    data = data[:, :, :, 0]
    profiles = {}
    for ci, (s, regime, load) in enumerate((s, r, l) for s in OVERLAPS for r in REGIMES for l in LOADS):
        key = f's{s}_{regime}_l{load}'
        profiles[key] = {family: {m: interval(data[:, ci, fi, mi]) for mi, m in enumerate(METRICS)} for fi, family in enumerate(FAMILIES)}
        profiles[key]['comparisons'] = {f'k6_minus_{family}': {m: interval(data[:, ci, 1, mi]-data[:, ci, fi, mi]) for mi, m in enumerate(METRICS)} for fi, family in enumerate(FAMILIES[:5]) if fi != 1}
    primary = {'hard_retention_k6_minus_k4': data[:, 11, 1, 0]-data[:, 11, 0, 0], 'hard_noise_k6_minus_k4': data[:, 11, 1, 4]-data[:, 11, 0, 4], 'k6_load16_minus_load2_similar': data[:, 11, 1, 0]-data[:, 8, 1, 0], 'k6_similar_minus_dissimilar_load16': data[:, 11, 1, 0]-data[:, 3, 1, 0]}
    capacity = {}; indices = np.random.default_rng(600692).integers(32, size=(200000, 32))
    for fi, family in enumerate(FAMILIES[:5]):
        for si, s in enumerate(OVERLAPS):
            for ri, regime in enumerate(REGIMES):
                bounds = []; certified = []; passed = True
                for li, load in enumerate(LOADS):
                    ci = si*8+ri*4+li
                    lower = [float(np.quantile(data[:, ci, fi, mi][indices].mean(1), .05/160)) for mi in (0, 2)]
                    bounds.append(lower); passed = passed and min(lower) > .8
                    if passed: certified.append(load)
                capacity[f'{family}_s{s}_{regime}'] = {'certified_load': max(certified) if certified else None, 'lower_bounds_retention_new': bounds}
    write(target/'analysis.json', {'profiles': profiles, 'primary': {k: interval(v, .9875) for k, v in primary.items()}, 'capacity': capacity, 'block_count': 32})
    print(json.dumps({'primary': {k: interval(v, .9875) for k, v in primary.items()}, 'capacity': {k: v['certified_load'] for k, v in capacity.items()}}), flush=True)


def validate():
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_exp006')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    assert result.wasSuccessful()
    settings = {f: GRID for f in FAMILIES}
    a, record = compute('validation', 0, settings)
    b, _ = compute('validation', 0, settings)
    for key in a: np.testing.assert_array_equal(a[key], b[key])
    record.update(status='passed', tests=result.testsRun, source=snapshot(), replay='full validation block exact', estimated_development_seconds_three_workers=record['wall_seconds']*3, estimated_confirmation_seconds_three_workers=record['wall_seconds']*12, storage_budget_bytes=2_000_000_000)
    write(ROOT/'research/exp006_validation.json', record)
    print(json.dumps(record), flush=True)
