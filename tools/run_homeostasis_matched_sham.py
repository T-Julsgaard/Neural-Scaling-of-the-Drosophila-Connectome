"""Prespecified, no-search matched-offset secondary control."""
import os
import sys
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import numpy as np
from exp007.campaign import ROOT, read, write, folder, calibration, sequence, task, summarize, digest, interval, sha256, snapshot

OUT = ROOT/'results/exp007_matched_sham'
ADDENDUM = ROOT/'experiments/EXP-007-matched-sham-addendum.md'


def sources(): return dict(main=snapshot(), runner=sha256(Path(__file__)), addendum=sha256(ADDENDUM), calibration=sha256(folder('calibration')/'calibration.npz'), selection=sha256(folder('development')/'selection.json'))


def compute(number, stage='confirmation'):
    cal = calibration(); config = read(OUT/'contract.json')['setting']
    t = task(stage, number, 6, 16, 'per_pair')
    arrays = {'task_hash': np.array(digest(t['p'], t['labels'], *t['obs'], *t['outcomes'], *t['uniforms'], t['probes']))}; vals = []
    for rep in range(3):
        theta = cal[f"sham{rep}_l{config['strength']}"]
        r = sequence(t, 'sham', cal['projections'][0], cal['priority'], theta, [config])
        vals.append(summarize(r)[0])
        for name, value in r.items(): arrays[f'r{rep}_{name}'] = value
    arrays['metrics'] = np.mean(vals, axis=0)
    return arrays


def freeze():
    assert not (folder('confirmation')/'contract.json').exists(), 'Supplement must freeze before confirmation'
    assert read(folder('development')/'audit.json')['status'] == 'passed'
    sel = read(folder('development')/'selection.json'); cal = calibration(); config = sel['settings']['homeostasis']
    theta = cal[f"p0_l{config['strength']}"]
    for rep in range(3): np.testing.assert_array_equal(np.sort(theta), np.sort(cal[f"sham{rep}_l{config['strength']}"]))
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT/'contract.json', dict(sources=sources(), blocks=list(range(1000, 1000+sel['confirmation_n'])), setting=config, created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
    a = compute(0, 'validation'); b = compute(0, 'validation')
    for key in a: np.testing.assert_array_equal(a[key], b[key])
    write(OUT/'preflight.json', dict(status='passed', exact_validation_replay=True, offset_multisets='identical', sources=sources()))
    print('Matched-sham addendum frozen before confirmation', flush=True)


def block(number):
    c = read(OUT/'contract.json'); assert c['sources'] == sources(); assert number in c['blocks']
    path = OUT/f'block_{number}.npz'
    if path.with_suffix('.json').exists():
        assert sha256(path) == read(path.with_suffix('.json'))['sha256']; return number
    start = time.perf_counter(); arrays = compute(number)
    with path.with_suffix('.tmp').open('wb') as f: np.savez_compressed(f, **arrays)
    path.with_suffix('.tmp').replace(path)
    write(path.with_suffix('.json'), dict(sha256=sha256(path), contract_sha256=sha256(OUT/'contract.json'), wall_seconds=time.perf_counter()-start))
    return number


def run():
    c = read(OUT/'contract.json'); assert c['sources'] == sources()
    assert read(folder('confirmation')/'audit.json')['status'] == 'passed'
    with ProcessPoolExecutor(max_workers=3) as pool:
        for f in as_completed([pool.submit(block, b) for b in c['blocks']]): print('matched-sham', f.result(), flush=True)
    differences = []; methods = list(read(folder('confirmation')/'contract.json')['settings'])
    for b in c['blocks']:
        p = OUT/f'block_{b}.npz'; assert sha256(p) == read(p.with_suffix('.json'))['sha256']
        with np.load(p) as a, np.load(folder('confirmation')/f'block_{b}.npz') as main:
            assert str(a['task_hash']) == str(main['c11_task_hash'])
            rebuilt = np.mean([summarize(dict(history=a[f'r{r}_history'], reverse=a[f'r{r}_reverse']))[0] for r in range(3)], axis=0)
            np.testing.assert_array_equal(rebuilt, a['metrics'])
            differences.append(main['scores'][11, methods.index('homeostasis'), 0]-a['metrics'])
    replay = compute(c['blocks'][0])
    with np.load(OUT/f'block_{c["blocks"][0]}.npz') as a:
        for key in replay: np.testing.assert_array_equal(a[key], replay[key])
    from exp007.homeostasis import NAMES
    write(OUT/'analysis.json', dict(status='passed', blocks=len(c['blocks']), replay_block=c['blocks'][0], comparison='homeostasis minus exact-multiset shuffled offsets', descriptive_95={name: interval(np.array(differences)[:, i]) for i, name in enumerate(NAMES)}, contract_sha256=sha256(OUT/'contract.json')))
    print(read(OUT/'analysis.json'), flush=True)


if __name__ == '__main__': freeze() if sys.argv[1] == 'freeze' else run()
