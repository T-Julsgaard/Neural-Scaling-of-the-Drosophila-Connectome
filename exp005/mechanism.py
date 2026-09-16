"""N73 amplitude/update controls with explicit trial-level instrumentation."""
from dataclasses import dataclass, asdict
import hashlib
import numpy as np
from exp002.data import load_projection


def stream(stage, block, component, *suffix):
    ranges = {'validation': range(5), 'development': range(100, 106), 'evaluation': range(1000, 1032)}
    if stage not in ranges or block not in ranges[stage]:
        raise ValueError('Invalid stage/block')
    return np.random.default_rng(np.random.SeedSequence([6, list(ranges).index(stage), block, 0, component, *suffix]))


class Inputs:
    def __init__(self, stage, block, episode):
        if episode not in range(20):
            raise ValueError('Invalid episode')
        self.stage, self.block, self.episode = stage, block, episode
        self.family = 'reversal' if episode < 10 else 'interference'
        self.priority = stream(stage, block, 1).permutation(73)
        stim = stream(stage, block, 2, episode)
        prototypes = []
        for _ in range(2):
            pair = []
            while len(pair) < 2:
                u = np.zeros(40)
                u[stim.choice(40, 10, replace=False)] = 1.
                if not pair or not np.array_equal(pair[0], u):
                    pair.append(u)
            prototypes.extend(pair)
        self.prototypes, self.order = np.array(prototypes), stim.permutation(2)
        canonical = np.zeros(384, dtype=int)
        if self.family == 'reversal':
            canonical[128:256] = 1
        self.preferred = np.array([int(np.flatnonzero(self.order == c)[0]) for c in canonical])
        offsets = np.zeros(384, dtype=int)
        if self.family == 'interference':
            offsets[128:256] = 2
        cues = self.prototypes[offsets[:, None] + self.order]
        self.observations = np.clip(cues + stream(stage, block, 3, episode).normal(0, .1, (384, 2, 40)), 0, 1)
        p = np.where(np.arange(2)[None] == self.preferred[:, None], .8, .2)
        self.outcomes = np.where(stream(stage, block, 4, episode).random((384, 2)) < p, 1, -1)
        self.uniforms = stream(stage, block, 5, episode).random(384)

    def probe_observations(self, trial, sigma, new=False):
        suffix = (32, trial, int(round(sigma * 1000))) + ((1,) if new else ())
        random = stream(self.stage, self.block, 3, self.episode, *suffix)
        return np.clip(self.prototypes[self.order + (2 if new else 0)][None] + random.normal(0, sigma, (32, 2, 40)), 0, 1)

    def digest(self):
        h = hashlib.sha256()
        for a in (self.prototypes, self.order, self.observations, self.outcomes, self.uniforms, self.priority):
            h.update(np.ascontiguousarray(a, dtype='<f8').tobytes())
        return h.hexdigest()


@dataclass(frozen=True)
class Setting:
    id: str
    k: int
    amplitude: float
    eta: float
    temperature: float = .1
    initial: float = .1


def fixed():
    return [Setting('k4_historical', 4, 2.5, .01), Setting('k6_historical', 6, 10/6, .01),
            Setting('k4_slow', 4, 2.5, .01*2/3), Setting('k6_fast', 6, 10/6, .015),
            Setting('k4_low_amplitude', 4, 10/6, .01), Setting('k6_high_amplitude', 6, 2.5, .01),
            Setting('k4_low_norm', 4, np.sqrt((100/6)/4), .01),
            Setting('k6_high_norm', 6, np.sqrt(25/6), .01)]


def tuning():
    return [Setting(f'k{k}_tune_e{i}_t{j}', k, 10/k, e, t)
            for k in (4, 6) for i, e in enumerate((.01/3, .02/3, .01, .015)) for j, t in enumerate((.1, .2))]


def configs(selected=None):
    return fixed() + (tuning() if selected is None else [Setting(**c) for c in selected]) + [
        Setting(f'k{k}_frozen', k, 10/k, 0) for k in (4, 6)]


def encode(projection, observations, priority, k):
    u = np.asarray(observations)
    z = np.array([projection.T @ row for row in u.reshape(-1, 40)])
    winners = np.lexsort((np.broadcast_to(priority, z.shape), -z), axis=-1)[:, :k]
    result = np.zeros_like(z)
    np.put_along_axis(result, winners, 1., axis=1)
    return result.reshape(*u.shape[:-1], 73)


TRACE = ('probability', 'choice', 'reward', 'q_before', 'delta_q_selected', 'predicted_delta_q',
         'delta_q_unchosen', 'old_cue_delta_rms', 'update_norm', 'clipped', 'effective_coefficient')
PROBES = ((128, .1, False), (256, .1, False), (384, .3, False), (256, .1, True))


def probabilities(weights, x, temperatures):
    q = np.einsum('cn,c...jn->c...j', weights, x)
    shape = (len(temperatures),) + (1,) * (q.ndim - 1)
    logits = (q - q.max(axis=-1, keepdims=True)) / temperatures.reshape(shape)
    p = np.exp(logits)
    return p / p.sum(axis=-1, keepdims=True)


def episode(task, settings, replay=False):
    projection, _ = load_projection()
    masks = {k: encode(projection, task.observations, task.priority, k) for k in (4, 6)}
    x = np.array([masks[c.k] * c.amplitude for c in settings])
    proto = {k: encode(projection, task.prototypes, task.priority, k) for k in (4, 6)}
    old = np.array([proto[c.k][:2] * c.amplitude for c in settings])
    plus = np.array([np.full(73, c.initial) for c in settings])
    minus = plus.copy()
    eta = np.array([c.eta for c in settings])
    temp = np.array([c.temperature for c in settings])
    trace = np.zeros((len(settings), 384, len(TRACE)))
    probes = np.full((len(settings), len(PROBES)), np.nan)
    for t in range(384):
        p = probabilities(plus-minus, x[:, t], temp)
        choice = np.full(len(settings), t % 2) if replay else (task.uniforms[t] >= p[:, 0]).astype(int)
        chosen = x[np.arange(len(settings)), t, choice]
        other = x[np.arange(len(settings)), t, 1-choice]
        reward = task.outcomes[t, choice]
        q = ((plus-minus)*chosen).sum(axis=1)
        error = reward-q
        change = eta[:, None]*chosen*error[:, None]
        raw_plus, raw_minus = plus+change, minus-change
        new_plus, new_minus = np.maximum(0, raw_plus), np.maximum(0, raw_minus)
        dw = (new_plus-new_minus)-(plus-minus)
        actual = (dw*chosen).sum(axis=1)
        predicted = 2*eta*error*(chosen*chosen).sum(axis=1)
        coefficient = np.divide(actual, error, out=np.zeros_like(actual), where=np.abs(error)>1e-12)
        old_delta = np.einsum('cn,cjn->cj', dw, old)
        trace[:, t] = np.column_stack((p[:, task.preferred[t]], choice, reward, q, actual, predicted,
            (dw*other).sum(axis=1), np.sqrt((old_delta**2).mean(axis=1)),
            np.sqrt(((new_plus-plus)**2+(new_minus-minus)**2).sum(axis=1)),
            ((raw_plus<0)|(raw_minus<0)).any(axis=1), coefficient))
        plus, minus = new_plus, new_minus
        if not np.isfinite(plus).all() or not np.isfinite(minus).all() or max(plus.max(),minus.max()) > 1e6:
            raise FloatingPointError('Invalid weights; no exclusions allowed')
        for j, (trial, sigma, new) in enumerate(PROBES):
            if t+1 == trial:
                u = task.probe_observations(trial, sigma, new)
                pm = {k: encode(projection, u, task.priority, k) for k in (4, 6)}
                px = np.array([pm[c.k]*c.amplitude for c in settings])
                probes[:, j] = probabilities(plus-minus, px, temp)[:, :, task.preferred[0]].mean(axis=1)
    geometry, counts = [], []
    for k in (4, 6):
        m = masks[k]
        same = (m[0:126:2]*m[1:127:2]).sum(axis=-1).mean()/k
        cross = (m[:128, 0]*m[:128, 1]).sum(axis=-1).mean()/k
        cross_old_new = np.mean(proto[k][:2] @ proto[k][2:].T)/k
        count = m.sum(axis=(0, 1))
        geometry.append([same, cross, cross_old_new, np.mean(count == 0)])
        counts.append(count)
    return {'trace': trace, 'probes': probes, 'plus': plus, 'minus': minus,
            'geometry': np.array(geometry), 'counts': np.array(counts), 'task_hash': np.array(task.digest())}


def metrics(trace, probes):
    p = trace[..., 0]
    return {'acquisition': p[:, :, 96:128].mean(axis=(0, 2)),
            'early_reversal': p[:10, :, 128:160].mean(axis=(0, 2)),
            'new_early': p[10:, :, 128:160].mean(axis=(0, 2)),
            'new_late': p[10:, :, 224:256].mean(axis=(0, 2)),
            'new_probe': probes[10:, :, 3].mean(axis=0),
            'retention_before': probes[10:, :, 0].mean(axis=0),
            'retention_after': probes[10:, :, 1].mean(axis=0),
            'retention_change': (probes[10:, :, 1]-probes[10:, :, 0]).mean(axis=0),
            'noise_03': probes[:, :, 2].mean(axis=0),
            'selected_update_abs': np.abs(trace[..., 4]).mean(axis=(0, 2)),
            'prediction_gap_abs': np.abs(trace[..., 4]-trace[..., 5]).mean(axis=(0, 2)),
            'unchosen_update_abs': np.abs(trace[..., 6]).mean(axis=(0, 2)),
            'old_update_interference': trace[10:, :, 128:256, 7].mean(axis=(0, 2)),
            'update_norm': trace[..., 8].mean(axis=(0, 2)),
            'clipping_fraction': trace[..., 9].mean(axis=(0, 2)),
            'effective_coefficient': trace[..., 10].mean(axis=(0, 2))}
