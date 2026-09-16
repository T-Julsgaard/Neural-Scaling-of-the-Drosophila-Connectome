"""EXP-010 bounded, frozen-feature diagnostic. Run validate/development/confirmation/audit."""
import os
for _key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[_key] = '1'
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hashlib
import json
import time
import shutil
import platform
import numpy as np
from exp007.memory import task, update, digest
from exp007.homeostasis import encode
from exp002.campaign import peak_memory

OUT = ROOT/'results/exp010'
CAL = ROOT/'results/exp007_calibration/calibration.npz'
LAMBDAS = [1e-6, 1e-4, 1e-2, 1e-1]
REPS = ['native', 'calibrated'] + [f'random{j}{suffix}' for j in range(1, 4) for suffix in ('', '_cal')] + ['direct', 'direct_raw']
ETA = .006666666666666667

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def write(p, x):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix('.tmp'); tmp.write_text(json.dumps(x, indent=2, allow_nan=False)+'\n'); tmp.replace(p)
def stamp(): return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
def sources():
    paths = [Path(__file__), ROOT/'tests/test_exp010.py', ROOT/'experiments/EXP-010-protocol.md', CAL]
    paths += [p for mod in ('exp002', 'exp007', 'exp009') for p in (ROOT/mod).glob('*.py')]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
def get_task(stage, b): return task(stage, b, 6, 16, 'per_pair')

def features(t, rep, cal):
    if rep.startswith('direct'):
        tr = t['obs'][0].copy(); scale = 1. if rep == 'direct_raw' else np.sqrt((100/6)/np.mean(np.sum(tr**2, axis=-1)))
        return tr*scale, t['probes']*scale, t['p']*scale, scale
    j = int(rep[6]) if rep.startswith('random') else 0
    theta = cal[f'p{j}_l0.25'] if rep == 'calibrated' or rep.endswith('_cal') else np.zeros(73)
    def enc(x): return encode(x, cal['projections'][j], cal['priority'], 6, theta)
    return enc(t['obs'][0]), enc(t['probes']), enc(t['p']), 1.

def ridge(x, y, lam):
    a = x.T@x/len(x)+lam*np.eye(x.shape[1]); b = x.T@y/len(x)
    w = np.linalg.solve(a, b)
    residual = np.linalg.norm(a@w-b)/max(np.linalg.norm(b), 1e-15)
    assert residual < 1e-9
    return w, residual

def margins(w, x, labels):
    return ((x[..., 0, :]-x[..., 1, :])@w)*(1-2*labels).reshape((-1,)+(1,)*(x.ndim-3))

def accuracy(m): return (m > 0).astype(float)+.5*(m == 0)

def online(x, outcomes, uniforms, proto, labels, mode):
    n, count, _, d = x.shape
    plus = np.full(d, .1); minus = plus.copy()
    diff = (proto[:, 0]-proto[:, 1])*(1-2*labels)[:, None]
    passes = 10 if mode == 'replay' else 1
    full = mode != 'chosen'
    changes = np.zeros((passes*n*count*(2 if full else 1), n), np.float32)
    indices = np.zeros((len(changes), 2), np.int16)
    choices = np.zeros((n, count), int)
    boundary = []; clipped = 0; at = 0
    for epoch in range(passes):
        for i in range(n):
            for j in range(count):
                if full: actions = (0, 1)
                else:
                    q = x[i, j]@(plus-minus)
                    p0 = np.exp(-np.logaddexp(0, (q[1]-q[0])/.1))
                    choices[i, j] = int(uniforms[i, j] >= p0)
                    actions = (choices[i, j],)
                for a in actions:
                    z = x[i, j, a]; old = plus-minus
                    change = ETA*z*(outcomes[i, j, a]-old@z)
                    rawp, rawm = plus+change, minus-change
                    clipped += int(np.count_nonzero(rawp < 0)+np.count_nonzero(rawm < 0))
                    plus, minus = (rawp, rawm) if mode == 'unclipped' else (np.maximum(0, rawp), np.maximum(0, rawm))
                    changes[at] = diff@((plus-minus)-old)
                    indices[at] = (epoch, i); at += 1
            if epoch == 0: boundary.append((plus-minus).copy())
    assert np.isfinite(plus).all() and np.isfinite(minus).all()
    np.testing.assert_allclose(changes.sum(0, dtype=np.float64), diff@(plus-minus), atol=2e-6)
    return dict(w=plus-minus, boundary=np.array(boundary), changes=changes, update_pair=indices, choices=choices, clipped=np.array(clipped))

def score(w, px, proto, labels):
    m = np.stack([margins(w, z, labels) for z in px])
    clean = margins(w, proto, labels)
    a = accuracy(m)
    return np.array([a[0, :-1].mean(), a[0].mean(), a[0].mean(-1).min(), a[1, :-1].mean(), accuracy(clean).mean(), np.exp(-np.logaddexp(0, -m[0]/.1)).mean()]), m, clean

def compute(stage, b, selection=None):
    start, cpu = time.perf_counter(), time.process_time()
    t = get_task(stage, b)
    with np.load(CAL) as z: cal = dict(z)
    arrays = dict(task_hash=np.array(digest(t['p'], t['labels'], t['obs'][0], t['outcomes'][0], t['uniforms'][0], t['probes'])), labels=t['labels'], train=t['obs'][0], outcomes=t['outcomes'][0], probes=t['probes'], prototypes=t['p'], uniforms=t['uniforms'][0])
    summary = {}
    for rep in REPS:
        x, px, proto, scale = features(t, rep, cal)
        flat = x.reshape(-1, x.shape[-1]); y = t['outcomes'][0].ravel()
        sv = np.linalg.svd(flat, compute_uv=False); cs = np.linalg.svd(proto.reshape(32, -1), compute_uv=False)
        rank = int(np.sum(sv > sv[0]*max(flat.shape)*np.finfo(float).eps))
        info = dict(scale=scale, norm2=float(np.mean(np.sum(flat**2, -1))), rank=rank, clean_rank=int(np.linalg.matrix_rank(proto.reshape(32, -1))), condition=float(sv[0]/sv[rank-1]), pair_distance=float(np.linalg.norm(proto[:, 0]-proto[:, 1], axis=-1).mean()), noise_deviation=float(np.mean(np.sum((px[0]-proto[:, None])**2, -1))), models={})
        arrays[rep+'_singular'] = sv; arrays[rep+'_clean_singular'] = cs
        chosen = None
        for mode in ('chosen', 'supervised', 'unclipped', 'replay'):
            r = online(x, t['outcomes'][0], t['uniforms'][0], proto, t['labels'], mode)
            if mode == 'chosen': chosen = r['choices']
            s, m, cm = score(r['w'], px, proto, t['labels'])
            acquired = np.array([accuracy(margins(w, px[0], t['labels']))[i].mean() for i, w in enumerate(r['boundary'])])
            info['models'][mode] = dict(score=s.tolist(), acquisition_old=float(acquired[:-1].mean()), forgetting_old=float(acquired[:-1].mean()-s[0]), clips=int(r['clipped']))
            key = rep+'_'+mode
            arrays.update({key+'_'+k: v for k, v in r.items()}); arrays[key+'_margins'] = m; arrays[key+'_clean'] = cm; arrays[key+'_acquired'] = acquired
        for access in ('chosen', 'full'):
            if access == 'chosen':
                ix = np.indices(chosen.shape); fx = x[ix[0], ix[1], chosen]; fy = t['outcomes'][0][ix[0], ix[1], chosen]
                fx, fy = fx.reshape(-1, x.shape[-1]), fy.ravel()
            else: fx, fy = flat, y
            grid = [selection['lambdas'][rep][access]] if selection else LAMBDAS
            for k, lam in enumerate(grid):
                w, res = ridge(fx, fy, lam)
                np.testing.assert_allclose(np.maximum(w, 0)-np.maximum(-w, 0), w, atol=0)
                s, m, cm = score(w, px, proto, t['labels'])
                name = f'offline_{access}_{k}'
                info['models'][name] = dict(score=s.tolist(), residual=res, lambda_value=lam, observations=len(fy), train_mse=float(np.mean((fx@w-fy)**2)))
                arrays[rep+'_'+name+'_w'] = w; arrays[rep+'_'+name+'_margins'] = m; arrays[rep+'_'+name+'_clean'] = cm
        summary[rep] = info
    return arrays, dict(representations=summary, wall_seconds=time.perf_counter()-start, cpu_seconds=time.process_time()-cpu, peak_memory_bytes=peak_memory())

def freeze(stage):
    path = OUT/stage/'contract.json'
    if path.exists():
        c = read(path); assert c['source'] == sources(); return c
    selection = read(OUT/'selection.json') if stage == 'confirmation' else None
    if stage != 'validation':
        v = read(OUT/'validation.json'); assert v['passed'] and v['source'] == sources()
    if selection: assert selection['gate'] and selection['source'] == sources()
    blocks = [100000] if stage == 'validation' else list(range(101000, 101006)) if stage == 'development' else list(range(102000, 102024))
    c = dict(created_utc=stamp(), source=sources(), selection=selection, blocks=blocks, python=sys.version, numpy=np.__version__, platform=platform.platform())
    for name in c['source']:
        if name.endswith('.py') or name.endswith('.md'):
            dest = OUT/stage/'frozen_source'/name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT/name, dest)
    write(path, c); return c

def run(stage):
    c = freeze(stage); total = 0.
    for b in c['blocks']:
        path = OUT/stage/f'block_{b}.npz'; rec = path.with_suffix('.json')
        if rec.exists():
            r = read(rec); assert r['sha256'] == sha(path) and r['contract_sha256'] == sha(OUT/stage/'contract.json')
        else:
            a, r = compute(stage, b, c['selection'])
            with path.with_suffix('.tmp').open('wb') as f: np.savez_compressed(f, **a)
            path.with_suffix('.tmp').replace(path)
            r.update(sha256=sha(path), contract_sha256=sha(OUT/stage/'contract.json')); write(rec, r)
        total += r['wall_seconds']
        assert total < 1800 and r['peak_memory_bytes'] < 2*1024**3
        assert sum(p.stat().st_size for p in OUT.rglob('*.npz')) < 1024**3
        print(stage, b, round(r['wall_seconds'], 2), flush=True)

def select():
    records = [read(p)['representations'] for p in sorted((OUT/'development').glob('block_*.json'))]
    assert len(records) == 6
    lambdas = {}
    for rep in REPS:
        lambdas[rep] = {}
        for access in ('chosen', 'full'):
            means = [np.mean([r[rep]['models'][f'offline_{access}_{k}']['score'][0] for r in records]) for k in range(4)]
            lambdas[rep][access] = LAMBDAS[int(np.argmax(means))]
    offline = []; online_scores = []
    for r in records:
        offline.append(np.mean([r[rep]['models'][f'offline_full_{LAMBDAS.index(lambdas[rep]["full"])}']['score'][0] for rep in REPS[:2]]))
        online_scores.append(np.mean([r[rep]['models']['supervised']['score'][0] for rep in REPS[:2]]))
    gate = bool(np.mean(offline) >= .8 and np.mean(offline)-np.mean(online_scores) >= .1)
    result = dict(created_utc=stamp(), source=sources(), lambdas=lambdas, gate=gate, development_offline=float(np.mean(offline)), development_supervised=float(np.mean(online_scores)), n=24, prediction='Offline-full old-pair accuracy >= .80; paired lower 95% CI versus supervised online > .05; supervised acquisition-to-final old accuracy loss lower CI > .05. Failure of any criterion falsifies this fixed-regime prediction.', explanation='Sequential error-dependent readout procedure loses still-linearly-recoverable preferences; full outcome access alone does not remove the deficit.', development_hashes={p.name: sha(p) for p in (OUT/'development').glob('block_*.json')})
    assert not (OUT/'selection.json').exists()
    write(OUT/'selection.json', result); print(json.dumps(result, indent=2))

def interval(x):
    x = np.asarray(x); assert len(x) == 24
    mean = float(x.mean()); h = float(2.0686576104190406*x.std(ddof=1)/np.sqrt(len(x))) # t(.975, df=23)
    return dict(mean=mean, lower=mean-h, upper=mean+h)

def analyze():
    recs = [read(p) for p in sorted((OUT/'confirmation').glob('block_*.json'))]; assert len(recs) == 24
    def val(r, rep, model, field='score'): return r['representations'][rep]['models'][model][field]
    off = [np.mean([val(r, rep, 'offline_full_0')[0] for rep in REPS[:2]]) for r in recs]
    on = [np.mean([val(r, rep, 'supervised')[0] for rep in REPS[:2]]) for r in recs]
    loss = [np.mean([val(r, rep, 'supervised', 'forgetting_old') for rep in REPS[:2]]) for r in recs]
    gap = interval(np.array(off)-on); lossci = interval(loss)
    tables = {}
    for label, reps in {'native':['native'], 'calibrated':['calibrated'], 'random':[f'random{j}' for j in range(1,4)], 'random_cal':[f'random{j}_cal' for j in range(1,4)], 'direct':['direct'], 'direct_raw':['direct_raw']}.items():
        tables[label] = {m:dict(old_accuracy=interval([np.mean([val(r, rep, m)[0] for rep in reps]) for r in recs]), mean_scores=np.mean([[val(r, rep, m) for rep in reps] for r in recs], axis=(0,1)).tolist()) for m in ('chosen','supervised','unclipped','replay','offline_chosen_0','offline_full_0')}
    result = dict(primary_gap=gap, offline=interval(off), supervised=interval(on), forgetting=lossci, prediction_passed=bool(gap['lower']>.05 and np.mean(off)>=.8 and lossci['lower']>.05), tables=tables)
    write(OUT/'analysis.json', result); print(json.dumps(result, indent=2))

def audit():
    start = time.perf_counter(); blocks = 0; arrays = 0
    for stage in ('validation','development','confirmation'):
        if not (OUT/stage/'contract.json').exists(): continue
        c = freeze(stage)
        for b in c['blocks']:
            path = OUT/stage/f'block_{b}.npz'; rec = read(path.with_suffix('.json'))
            assert sha(path) == rec['sha256'] and rec['contract_sha256'] == sha(OUT/stage/'contract.json')
            rebuilt, report = compute(stage, b, c['selection'])
            assert report['representations'] == rec['representations']
            with np.load(path) as z:
                assert set(z.files) == set(rebuilt)
                for k, v in rebuilt.items(): np.testing.assert_array_equal(z[k], v); arrays += 1
            blocks += 1; print('replayed', stage, b, flush=True)
    preserved = read(OUT/'preservation.json')
    for p, h in preserved.items(): assert sha(ROOT/p) == h
    write(OUT/'audit.json', dict(passed=True, blocks=blocks, arrays=arrays, preserved_files=len(preserved), wall_seconds=time.perf_counter()-start, source=sources(), utc=stamp()))

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode in ('validation','development','confirmation'): run(mode)
    elif mode == 'select': select()
    elif mode == 'analyze': analyze()
    elif mode == 'audit': audit()
    else: raise ValueError(mode)
