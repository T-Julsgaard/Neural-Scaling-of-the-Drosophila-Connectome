"""Bounded unlabeled calibration and instrumented persistent learning."""
import numpy as np
from exp008.memory import D, N, KLOW, KHIGH, ACTIVE, LOW, HIGH, rng, prototypes, random_projection, digest, task, probability, probe

ETAS = [(.01/3)*2**j for j in (-4, -3, -2, -1, 0, 1)] + [.01, .015]
TEMPS = (.1, .2)
METHODS = ('ordinary', 'homeostasis', 'sham', 'random_ordinary', 'random_homeostasis', 'direct', 'oracle')
NAMES = ('retention', 'worst_pair', 'new_learning', 'forgetting', 'noise_retention', 'reversal', 'unchanged', 'below_chance')


def candidates(method):
    if method in ('direct', 'oracle'):
        scale = 10/ACTIVE if method == 'direct' else 1.
        return [dict(k=0, strength=0., eta=float(e)*scale, temperature=t) for e in np.geomspace(ETAS[0], .015, 16) for t in TEMPS]
    pairs = [(KLOW, 0.), (KHIGH, 0.)] if method.endswith('ordinary') else [(KHIGH, .25), (KHIGH, .5)]
    return [dict(k=k, strength=l, eta=e*8, temperature=t) for k,l in pairs for e in ETAS for t in TEMPS]


def box_center(a, bound):
    lo, hi = a.min()-bound, a.max()+bound
    for _ in range(60):
        mid = (lo+hi)/2
        if np.clip(a-mid, -bound, bound).sum() > 0: lo = mid
        else: hi = mid
    return np.clip(a-(lo+hi)/2, -bound, bound)


def winners(z, priority, k):
    # Partial selection is identical to lexsort; resolve only exact cutoff ties.
    flat = np.asarray(z).reshape(-1, z.shape[-1])
    ix = np.argpartition(-flat, k-1, axis=-1)[:, :k]
    cutoff = np.take_along_axis(flat, ix, axis=-1).min(-1)
    tied = ((flat == cutoff[:, None]).sum(-1) > 1)
    for row in np.flatnonzero(tied):
        ix[row] = np.lexsort((priority, -flat[row]))[:k]
    return ix.reshape(z.shape[:-1]+(k,))


def encode(u, p, priority, k, theta):
    z = np.asarray(u) @ p-theta
    ix = winners(z, priority, k)
    x = np.zeros_like(z)
    np.put_along_axis(x, ix, 10/k, axis=-1)
    return x


def calibration_pool(validation=False):
    # Validation-stage namespace is dedicated to calibration and is not an outcome stream.
    pool = []
    for overlap in (LOW, HIGH):
        for j in range(64):
            number = 20000 + 1000*int(validation) + j
            p, _ = prototypes('calibration_validation' if validation else 'calibration', number, overlap)
            noise = rng('calibration_validation' if validation else 'calibration', number, 90, overlap).normal(0, .1, p.shape)
            pool.append(np.clip(p+noise, 0, 1).reshape(-1, D))
    return np.concatenate(pool)


def fit(p, u, priority, strength):
    z = u @ p
    scale = float(np.median(z.std(0)[z.std(0) > 0]))
    bound = .25*scale
    theta = np.zeros(p.shape[1])
    p0 = (encode(u, p, priority, KHIGH, theta) > 0).mean(0)
    target = (1-strength)*p0+strength*KHIGH/p.shape[1]
    history = []
    for _ in range(100):
        current = np.bincount(winners(z-theta, priority, KHIGH).ravel(), minlength=p.shape[1])/len(u)
        history.append(float(np.mean((current-target)**2)))
        theta = box_center(theta+.5*scale*(current-target), bound)
    final = (encode(u, p, priority, KHIGH, theta) > 0).mean(0)
    return theta, dict(scale=scale, bound=bound, target=target.tolist(), before=p0.tolist(), after=final.tolist(), fit_mse=history, clamp_fraction=float(np.mean(np.abs(theta) >= bound-1e-12)))


def shifted(t):
    out = dict(t)
    factor = np.r_[np.full(D//2, .5), np.ones(D-D//2)]
    out['p'] = t['p']*factor
    out['obs'] = [a*factor for a in t['obs']]
    out['probes'] = t['probes']*factor
    return out


def summarize(r):
    h = r['history']; new = np.diagonal(h[:, 0], axis1=-2, axis2=-1)
    final = h[:, 0, -1]; rev = r['reverse']
    return np.stack((final.mean(-1), final.min(-1), new.mean(-1), (new-final).mean(-1), h[:, 1, -1].mean(-1), rev[:, 0, ::2].mean(-1), rev[:, 0, 1::2].mean(-1), (final < .5).mean(-1)), -1)


def sequence(t, method, p, priority, theta, configs):
    load = len(t['labels']); count = len(configs); k = configs[0]['k']
    identities = np.arange(2*load).reshape(load, 2)
    def enc(u, ids):
        if method == 'direct': return u.copy()
        if method == 'oracle': return np.eye(32)[ids]*np.sqrt(10)
        return encode(u, p, priority, k, theta)
    x = [enc(a, np.broadcast_to(identities[:, None], a.shape[:-1])) for a in t['obs']]
    px = enc(t['probes'], np.broadcast_to(identities[None, :, None], t['probes'].shape[:-1]))
    proto = enc(t['p'], identities)
    eta = np.array([c['eta'] for c in configs]); temp = np.array([c['temperature'] for c in configs])
    plus = np.full((count, x[0].shape[-1]), .1); minus = plus.copy()
    history = np.full((count, 2, load, load), np.nan)
    boundaries = []; chosen_counts = np.zeros_like(plus)
    diag = np.zeros((count, 5)) # clipping-coordinate count, update norm sum, abs old margin perturbation, old margin observations, updates
    pairdiff = proto[:, 0]-proto[:, 1]
    for phase in range(2):
        for i in (range(load) if phase == 0 else range(0, load, 2)):
            before = digest(plus, minus)
            for j in range(x[phase].shape[1]):
                features = x[phase][i, j]
                prob0 = probability(plus, minus, features, temp)
                choice = (t['uniforms'][phase][i, j] >= prob0).astype(int)
                chosen = features[choice]
                error = t['outcomes'][phase][i, j][choice]-((plus-minus)*chosen).sum(-1)
                change = eta[:, None]*chosen*error[:, None]
                rawp, rawm = plus+change, minus-change
                newp, newm = np.maximum(0, rawp), np.maximum(0, rawm)
                delta = (newp-newm)-(plus-minus)
                if phase == 0:
                    chosen_counts += chosen > 0
                    diag[:, 0] += ((rawp < 0).sum(-1)+(rawm < 0).sum(-1))
                    diag[:, 1] += np.linalg.norm(delta, axis=-1)
                    if i:
                        diag[:, 2] += np.abs(delta @ pairdiff[:i].T).sum(-1)
                        diag[:, 3] += i
                    diag[:, 4] += 1
                plus, minus = newp, newm
            after = digest(plus, minus)
            if phase == 0:
                for s in range(2): history[:, s, i, :i+1] = probe(plus, minus, px[s, :i+1], temp, t['labels'][:i+1])
                assert after == digest(plus, minus)
                boundaries.append((before, after))
        if phase == 0: prereversal = np.stack((plus, minus))
    labels = t['labels'].copy(); labels[::2] = 1-labels[::2]
    before = digest(plus, minus)
    reverse = np.stack([probe(plus, minus, a, temp, labels) for a in px], axis=1)
    assert before == digest(plus, minus)
    assert np.isfinite(plus).all() and np.isfinite(minus).all()
    flat = proto.reshape(2*load, -1); norm = np.linalg.norm(flat, axis=-1)
    cosine = (flat @ flat.T)/(norm[:, None]*norm[None])
    stable = np.sum(px[0]*proto[:, None], axis=-1)/(np.linalg.norm(px[0], axis=-1)*np.linalg.norm(proto, axis=-1)[:, None])
    presented = (x[0] > 0).sum((0, 1, 2))
    ranks = np.array([np.nan, np.nan])
    if k:
        clean_z = np.sort(t['p'] @ p-theta, axis=-1)
        noisy_z = np.sort(t['obs'][0] @ p-theta, axis=-1)
        ranks = np.array([(clean_z[..., -k]-clean_z[..., -k-1]).mean(), (noisy_z[..., -k]-noisy_z[..., -k-1]).mean()])
    return dict(history=history, reverse=reverse, prereversal=prereversal, final=np.stack((plus, minus)), boundaries=np.array(boundaries), presented=presented, chosen=chosen_counts, diagnostics=diag, cosine=cosine, stability=stable, rank_gaps=ranks, pairdiff=pairdiff)
