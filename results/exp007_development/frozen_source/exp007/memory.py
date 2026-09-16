"""Paired streams, persistent chosen-action delta learning, and read-only probes."""
import hashlib
import numpy as np
from exp002.data import load_projection

LOADS = (2, 4, 8, 16)
OVERLAPS = (2, 6)
REGIMES = ('per_pair', 'total')
FAMILIES = ('native4', 'native6', 'direct', 'random4', 'random6', 'oracle')
GRID = [(e, t) for e in (.01/3, .02/3, .01, .015) for t in (.1, .2)]


def rng(stage, block, component, *extra):
    return np.random.default_rng(np.random.SeedSequence([7007, {'validation': 0, 'development': 1, 'confirmation': 2}[stage], block, component, *extra]))


def digest(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def prototypes(stage, block, overlap):
    r = rng(stage, block, 1, overlap)
    perm = r.permutation(40)
    p = np.zeros((16, 2, 40))
    p[:, :, perm[:overlap]] = 1
    used = set()
    for i in range(16):
        while True:
            residual = r.permutation(perm[overlap:])[:2*(10-overlap)].reshape(2, 10-overlap)
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


def encode(u, family, projection, priority, identities=None):
    if family == 'direct':
        return np.asarray(u).copy()
    if family == 'oracle':
        return np.eye(32)[identities] * np.sqrt(10)
    k = int(family[-1])
    z = np.asarray(u) @ projection
    order = np.lexsort((np.broadcast_to(priority, z.shape), -z), axis=-1)[..., :k]
    x = np.zeros_like(z)
    np.put_along_axis(x, order, 10/k, axis=-1)
    return x


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
            phase_obs.append(np.clip(p[i]+r.normal(0, .1, (n, 2, 40)), 0, 1))
            pref = labels[i] if phase == 0 else 1-labels[i]
            prob = np.where(np.arange(2) == pref, .8, .2)
            phase_out.append(np.where(rng(stage, block, 4, overlap, phase, i).random((n, 2)) < prob, 1., -1.))
            phase_uni.append(rng(stage, block, 5, overlap, phase, i).random(n))
        obs.append(np.array(phase_obs)); outcomes.append(np.array(phase_out)); uniforms.append(np.array(phase_uni))
    probes = np.array([np.clip(p[:load, None]+rng(stage, block, 6, overlap, s).normal(0, sigma, (load, probe_count, 2, 40)), 0, 1) for s, sigma in enumerate((.1, .3))])
    return {'p': p[:load], 'labels': labels[:load], 'obs': obs, 'outcomes': outcomes, 'uniforms': uniforms, 'probes': probes, 'count': count}


def sequence(t, family, projection, priority, settings):
    load = len(t['labels'])
    identities = np.arange(2*load).reshape(load, 2)
    x = [encode(a, family, projection, priority, np.broadcast_to(identities[:, None], a.shape[:-1])) for a in t['obs']]
    px = encode(t['probes'], family, projection, priority, np.broadcast_to(identities[None, :, None], t['probes'].shape[:-1]))
    proto = encode(t['p'], family, projection, priority, identities)
    eta, temp = np.array(settings).T
    plus = np.full((len(settings), x[0].shape[-1]), .1)
    minus = plus.copy()
    history = np.full((len(settings), 2, load, load), np.nan)
    boundary = []
    for i in range(load):
        before = digest(plus, minus)
        for j in range(t['count']):
            plus, minus = update(plus, minus, x[0][i, j], t['outcomes'][0][i, j], t['uniforms'][0][i, j], eta, temp)
        after = digest(plus, minus)
        for s in range(2):
            history[:, s, i, :i+1] = probe(plus, minus, px[s, :i+1], temp, t['labels'][:i+1])
        assert digest(plus, minus) == after
        boundary.append((before, after))
    prereversal = np.stack((plus, minus))
    for i in range(0, load, 2):
        for j in range(128):
            plus, minus = update(plus, minus, x[1][i, j], t['outcomes'][1][i, j], t['uniforms'][1][i, j], eta, temp)
    labels = t['labels'].copy(); labels[::2] = 1-labels[::2]
    reverse = np.stack([probe(plus, minus, a, temp, labels) for a in px], axis=1)
    assert np.isfinite(plus).all() and np.isfinite(minus).all() and max(plus.max(), minus.max()) < 1e6
    assert all(boundary[i][0] == boundary[i-1][1] for i in range(1, load))
    flat = proto.reshape(2*load, -1)
    norms = np.linalg.norm(flat, axis=1)
    cosine = (flat @ flat.T)/(norms[:, None]*norms)
    stability = np.mean(np.sum(px[0]*proto[:, None], axis=-1)/(np.linalg.norm(px[0], axis=-1)*np.linalg.norm(proto, axis=-1)[:, None]))
    return {'history': history, 'reverse': reverse, 'prereversal': prereversal, 'final': np.stack((plus, minus)), 'boundaries': np.array(boundary), 'cosine': cosine, 'stability': np.array(stability), 'unused': np.array(np.mean(np.concatenate(x[0]).sum((0, 1)) == 0))}


def metrics(result):
    h = result['history']
    new = np.diagonal(h[:, 0], axis1=-2, axis2=-1)
    final = h[:, 0, -1]
    r = result['reverse']
    return np.stack((final.mean(-1), final.min(-1), new.mean(-1), (new-final).mean(-1), h[:, 1, -1].mean(-1), r[:, 0, ::2].mean(-1), r[:, 0, 1::2].mean(-1), r[:, 1, ::2].mean(-1)), axis=-1)


METRICS = ('retention', 'worst_pair', 'new_learning', 'forgetting', 'noise_retention', 'reversal', 'unchanged_after_reversal', 'noise_reversal')

