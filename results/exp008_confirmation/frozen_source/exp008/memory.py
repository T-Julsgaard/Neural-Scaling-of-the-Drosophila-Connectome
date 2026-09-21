"""Paired streams, persistent chosen-action delta learning, and read-only probes."""
import hashlib
import numpy as np
from exp008.data import load_projection
D, N = 104, 590
KLOW, KHIGH = 32, 48
ACTIVE = 26
LOW, HIGH = 5, 16


def rng(stage, block, component, *extra):
    return np.random.default_rng(np.random.SeedSequence([8008, {'validation': 0, 'development': 1, 'confirmation': 2, 'calibration': 3, 'calibration_validation': 4}[stage], block, component, *extra]))


def digest(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def prototypes(stage, block, overlap):
    r = rng(stage, block, 1, overlap)
    perm = r.permutation(D)
    p = np.zeros((16, 2, D))
    p[:, :, perm[:overlap]] = 1
    used = set()
    for i in range(16):
        while True:
            residual = r.permutation(perm[overlap:])[:2*(ACTIVE-overlap)].reshape(2, ACTIVE-overlap)
            keys = [tuple(sorted(a)) for a in residual]
            if all(k not in used for k in keys):
                break
        for j in range(2):
            p[i, j, residual[j]] = 1
            used.add(keys[j])
    labels = rng(stage, block, 2).integers(0, 2, 16)
    return p, labels


def random_projection(p, r):
    """Bipartite switches; normalized contact values stay with each KC."""
    q = p.copy()
    edges = np.argwhere(q > 0)
    n = len(edges)
    checkpoints = []
    accepted = attempts = 0
    while accepted < 40*n and attempts < 800*n:
        attempts += 1
        a, b = r.choice(n, 2, replace=False)
        u, v = edges[a]
        x, y = edges[b]
        if u == x or v == y or q[u, y] or q[x, v]:
            continue
        q[x, v], q[u, y] = q[u, v], q[x, y]
        q[u, v] = q[x, y] = 0
        edges[a], edges[b] = (x, v), (u, y)
        accepted += 1
        if accepted % (10*n) == 0:
            checkpoints.append(float(np.count_nonzero((p > 0) & (q > 0))/n))
    assert accepted == 40*n
    np.testing.assert_array_equal((q > 0).sum(0), (p > 0).sum(0))
    np.testing.assert_array_equal((q > 0).sum(1), (p > 0).sum(1))
    np.testing.assert_array_equal(np.sort(q, axis=0), np.sort(p, axis=0))
    return q, {'attempts': attempts, 'accepted': accepted, 'edges': n, 'overlap_at_10_20_30_40_sweeps': checkpoints}


def probability(plus, minus, x, temperature):
    q = np.einsum('cn,...jn->c...j', plus-minus, x)
    delta = np.clip((q[..., 1]-q[..., 0])/np.asarray(temperature).reshape((-1,)+(1,)*(q.ndim-2)), -700, 700)
    return 1/(1+np.exp(delta))


def update(plus, minus, x, outcomes, uniform, eta, temperature):
    p = probability(plus, minus, x, temperature)
    choice = (uniform >= p).astype(int)
    chosen = x[choice]
    reward = outcomes[choice]
    q = ((plus-minus)*chosen).sum(-1)
    change = np.asarray(eta)[:, None]*chosen*(reward-q)[:, None]
    return np.maximum(0, plus+change), np.maximum(0, minus-change)


def probe(plus, minus, x, temperature, labels):
    p = probability(plus, minus, x, temperature)
    return np.where(np.asarray(labels)[None, :, None] == 0, p, 1-p).mean(-1)


def task(stage, block, overlap, load, regime, probe_count=64):
    p, labels = prototypes(stage, block, overlap)
    count = 128 if regime == 'per_pair' else 512//load
    # Prefix coupling across load and exposure, independent training/reversal/probe streams.
    obs, outcomes, uniforms = [], [], []
    for phase in range(2):
        phase_obs, phase_out, phase_uni = [], [], []
        for i in range(load):
            n = count if phase == 0 else 128
            r = rng(stage, block, 3, overlap, phase, i)
            phase_obs.append(np.clip(p[i]+r.normal(0, .1, (n, 2, D)), 0, 1))
            pref = labels[i] if phase == 0 else 1-labels[i]
            prob = np.where(np.arange(2) == pref, .8, .2)
            phase_out.append(np.where(rng(stage, block, 4, overlap, phase, i).random((n, 2)) < prob, 1., -1.))
            phase_uni.append(rng(stage, block, 5, overlap, phase, i).random(n))
        obs.append(np.array(phase_obs)); outcomes.append(np.array(phase_out)); uniforms.append(np.array(phase_uni))
    probes = np.array([np.clip(p[:load, None]+rng(stage, block, 6, overlap, s).normal(0, sigma, (load, probe_count, 2, D)), 0, 1) for s, sigma in enumerate((.1, .3))])
    return {'p': p[:load], 'labels': labels[:load], 'obs': obs, 'outcomes': outcomes, 'uniforms': uniforms, 'probes': probes, 'count': count}


