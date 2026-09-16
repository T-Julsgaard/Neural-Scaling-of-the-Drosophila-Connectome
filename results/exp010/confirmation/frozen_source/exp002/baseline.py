"""Paired EXP-002 task blocks and batched, scalar-validated learning episodes."""
from dataclasses import asdict, dataclass
import hashlib
import json

import numpy as np

from .data import encode

STAGES = {"validation": (0, range(5)), "development": (1, range(100, 110)),
          "confirmation": (2, range(1000, 1020))}
FAMILIES = ("reversal", "interference")
TRACE_COLUMNS = ("preferred_probability", "choice", "reward", "chosen_q", "d_plus",
                 "d_minus", "both_positive", "rate_match", "weight_min", "weight_max")
PROBE_KEYS = ((128, .1), (256, .1), (384, 0.), (384, .1), (384, .3))


def rng(stage, block, component, *suffix):
    if stage not in STAGES or block not in STAGES[stage][1]:
        raise ValueError("Stage/seed mismatch")
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [2, STAGES[stage][0], block, 0, component, *suffix])))


@dataclass(frozen=True)
class Config:
    representation: str
    arm: str
    eta: float
    temperature: float

    def __post_init__(self):
        if self.representation not in ("native", "pn") or self.arm not in ("frozen", "reward_only", "feedback", "delta"):
            raise ValueError("Unknown configuration")
        if self.representation == "pn" and self.arm != "delta":
            raise ValueError("Direct PN comparator uses delta only")
        if not np.isfinite(self.eta) or self.eta < 0 or not np.isfinite(self.temperature) or self.temperature <= 0:
            raise ValueError("Invalid hyperparameters")

    @property
    def id(self):
        return f"{self.representation}_{self.arm}_eta{self.eta:g}_T{self.temperature:g}"


def development_configs():
    return [Config("native", "frozen", 0., .2)] + [
        Config(rep, arm, eta, temp)
        for rep, arm in (("native", "reward_only"), ("native", "feedback"),
                         ("native", "delta"), ("pn", "delta"))
        for eta in (.0001, .001, .01) for temp in (.1, .2, .5)]


def encode_many(projection, observations, priority, representation):
    if representation == "pn":
        # Match total activity to the native encoder without introducing KC sparsity.
        totals = observations.sum(axis=-1, keepdims=True)
        if np.any(totals <= 0):
            raise ValueError("Zero PN activity")
        return observations * (10. / totals)
    flat = observations.reshape(-1, 40)
    return np.array([encode(projection, row, priority) for row in flat]).reshape(
        *observations.shape[:-1], projection.shape[1])


class Task:
    """Exogenous task data. The learner is supplied only chosen feedback."""
    def __init__(self, projection, stage, block, episode):
        if episode not in range(20):
            raise ValueError("Episode must be 0..19")
        self.stage, self.block, self.episode = stage, block, episode
        self.family = FAMILIES[episode // 10]
        self.projection = np.asarray(projection)
        if self.projection.shape != (40, 73):
            raise ValueError("Baseline requires the audited 40x73 circuit")
        self.priority = rng(stage, block, 1).permutation(73)
        stim = rng(stage, block, 2, episode)
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
        if self.family == "reversal":
            canonical[128:256] = 1
        self.preferred = np.array([int(np.flatnonzero(self.order == c)[0]) for c in canonical])
        offsets = np.zeros(384, dtype=int)
        if self.family == "interference":
            offsets[128:256] = 2
        cues = self.prototypes[offsets[:, None] + self.order]
        noise = rng(stage, block, 3, episode).normal(0., .1, (384, 2, 40))
        self.observations = np.clip(cues + noise, 0., 1.)
        probabilities = np.where(np.arange(2)[None, :] == self.preferred[:, None], .8, .2)
        self.outcomes = np.where(rng(stage, block, 4, episode).random((384, 2)) < probabilities, 1, -1)
        self.uniforms = rng(stage, block, 5, episode).random(384)

    def activities(self, representation):
        return encode_many(self.projection, self.observations, self.priority, representation)

    def probe_activities(self, representation, trial, sigma):
        noise = rng(self.stage, self.block, 3, self.episode, 32, trial, int(round(sigma * 1000)))
        observations = np.clip(self.prototypes[self.order][None, :, :] +
                               noise.normal(0., sigma, (32, 2, 40)), 0., 1.)
        return encode_many(self.projection, observations, self.priority, representation)

    def digest(self):
        h = hashlib.sha256()
        for a in (self.prototypes, self.order, self.observations, self.outcomes, self.uniforms, self.priority):
            h.update(np.ascontiguousarray(a, dtype="<f8").tobytes())
        return h.hexdigest()


class BatchEpisode:
    """Same recurrence as Learner; vectorizes independent configurations only."""
    def __init__(self, task, configs):
        if not configs or len({c.representation for c in configs}) != 1:
            raise ValueError("Batch must have one representation")
        self.task, self.configs = task, list(configs)
        self.representation = configs[0].representation
        self.activities = task.activities(self.representation)
        self.plus = np.full((len(configs), self.activities.shape[-1]), .1)
        self.minus = self.plus.copy()
        self.eta = np.array([c.eta for c in configs])
        self.temperature = np.array([c.temperature for c in configs])
        self.arms = np.array([c.arm for c in configs])
        self.trace = np.zeros((len(configs), 384, len(TRACE_COLUMNS)))
        self.probes = np.full((len(configs), len(PROBE_KEYS)), np.nan)
        self.trial = 0

    def probabilities(self, activities):
        q = np.einsum("kn,...cn->k...c", self.plus - self.minus, activities, optimize=False)
        shape = (len(self.configs),) + (1,) * (q.ndim - 1)
        logits = (q - q.max(axis=-1, keepdims=True)) / self.temperature.reshape(shape)
        p = np.exp(logits)
        return p / p.sum(axis=-1, keepdims=True)

    def probe(self, trial, sigma):
        activity = self.task.probe_activities(self.representation, trial, sigma)
        return self.probabilities(activity)[:, :, self.task.preferred[0]].mean(axis=1)

    def step(self):
        t = self.trial
        if t >= 384:
            raise StopIteration
        cues = self.activities[t]
        p = self.probabilities(cues)
        choice = (self.task.uniforms[t] >= p[:, 0]).astype(int)
        s = cues[choice]
        reward = self.task.outcomes[t, choice]
        q = np.sum((self.plus - self.minus) * s, axis=1)
        error = reward - q
        raw_plus, raw_minus = .1 * s.sum(axis=1) + error, .1 * s.sum(axis=1) - error
        d_plus, d_minus = np.maximum(0., raw_plus), np.maximum(0., raw_minus)
        drive = np.select([self.arms == "reward_only", self.arms == "feedback", self.arms == "delta"],
                          [reward, d_plus - d_minus, error], default=0.)
        change = self.eta[:, None] * s * drive[:, None]
        plus, minus = np.maximum(0., self.plus + change), np.maximum(0., self.minus - change)
        if not np.isfinite(plus).all() or not np.isfinite(minus).all() or max(plus.max(), minus.max()) > 1e6:
            raise FloatingPointError("Nonfinite or >1e6 weight; no episode may be discarded")
        self.plus, self.minus = plus, minus
        self.trace[:, t, :] = np.column_stack((p[:, self.task.preferred[t]], choice, reward, q,
            d_plus, d_minus, (raw_plus > 0) & (raw_minus > 0), (raw_plus >= 0) & (raw_minus >= 0),
            np.minimum(plus.min(axis=1), minus.min(axis=1)), np.maximum(plus.max(axis=1), minus.max(axis=1))))
        self.trial += 1
        for i, (trial, sigma) in enumerate(PROBE_KEYS):
            if self.trial == trial:
                self.probes[:, i] = self.probe(trial, sigma)

    def run_until(self, stop=384):
        if not self.trial <= stop <= 384:
            raise ValueError("Invalid stop")
        while self.trial < stop:
            self.step()

    def payload(self):
        return {"configs": [asdict(c) for c in self.configs], "task_hash": self.task.digest(),
                "numpy": np.__version__, "trial": self.trial, "plus": self.plus.tolist(),
                "minus": self.minus.tolist(), "trace": self.trace[:, :self.trial].tolist(),
                "probes": [[None if np.isnan(v) else float(v) for v in row] for row in self.probes]}

    @classmethod
    def restore(cls, task, payload):
        if payload["numpy"] != np.__version__ or payload["task_hash"] != task.digest():
            raise ValueError("Checkpoint environment/task mismatch")
        obj = cls(task, [Config(**c) for c in payload["configs"]])
        trial = payload["trial"]
        if not isinstance(trial, int) or not 0 <= trial <= 384:
            raise ValueError("Checkpoint chronology mismatch")
        for key in ("plus", "minus"):
            a = np.asarray(payload[key], dtype=float)
            if a.shape != obj.plus.shape or not np.isfinite(a).all() or (a < 0).any() or (a > 1e6).any():
                raise ValueError("Invalid checkpoint weights")
            setattr(obj, key, a)
        trace = np.asarray(payload["trace"], dtype=float)
        if trial == 0 and trace.shape == (len(obj.configs), 0):
            trace = trace.reshape(len(obj.configs), 0, len(TRACE_COLUMNS))
        if trace.shape != (len(obj.configs), trial, len(TRACE_COLUMNS)):
            raise ValueError("Invalid checkpoint trace")
        if not np.isfinite(trace).all():
            raise ValueError("Nonfinite checkpoint trace")
        obj.trace[:, :trial] = trace
        obj.probes = np.asarray(payload["probes"], dtype=float)
        if obj.probes.shape != (len(obj.configs), len(PROBE_KEYS)):
            raise ValueError("Invalid checkpoint probes")
        for i, (probe_trial, _) in enumerate(PROBE_KEYS):
            column = obj.probes[:, i]
            if probe_trial <= trial:
                if not np.isfinite(column).all() or (column < 0).any() or (column > 1).any():
                    raise ValueError("Invalid completed probe")
            elif not np.isnan(column).all():
                raise ValueError("Unexpected future probe")
        obj.trial = trial
        return obj


def feature_statistics(activity):
    a = activity.reshape(-1, activity.shape[-1])
    return {"count": np.array(len(a)), "sum": a.sum(axis=0), "gram": a.T @ a,
            "active": (a > 0).sum(axis=0)}


def feature_summary(stats):
    n = int(stats["count"])
    mean = stats["sum"] / n
    cov = stats["gram"] / n - np.outer(mean, mean)
    eig = np.maximum(np.linalg.eigvalsh(cov), 0.)
    effective_rank = float(eig.sum() ** 2 / np.sum(eig ** 2)) if np.any(eig) else 0.
    return {"presentations": n, "mean_activity": mean.tolist(),
            "participation": (stats["active"] / n).tolist(),
            "never_active_fraction": float(np.mean(stats["active"] == 0)),
            "covariance_participation_rank": effective_rank}


def block_metrics(traces, probes):
    """Arrays are episode x configuration x trial x column; average episodes first."""
    t, p = np.asarray(traces), np.asarray(probes)
    if t.shape[0] != 20 or t.shape[2:] != (384, len(TRACE_COLUMNS)) or p.shape != (20, t.shape[1], 5):
        raise ValueError("A scientific block requires ten episodes per family")
    scores = t[..., 0]
    result = {"acquisition": scores[:, :, 96:128].mean(axis=(0, 2)),
              "early_reversal": scores[:10, :, 128:160].mean(axis=(0, 2)),
              "return_adaptation": scores[:10, :, 256:288].mean(axis=(0, 2)),
              "retention_before": p[10:, :, 0].mean(axis=0),
              "retention_after": p[10:, :, 1].mean(axis=0),
              "retention_change": (p[10:, :, 1] - p[10:, :, 0]).mean(axis=0),
              "both_positive_fraction": t[..., 6].mean(axis=(0, 2)),
              "rate_match_fraction": t[..., 7].mean(axis=(0, 2))}
    for j, sigma in enumerate((0., .1, .3)):
        result[f"robustness_{sigma:g}"] = p[:, :, j + 2].mean(axis=0)
    result["selection_score"] = (result["acquisition"] + result["early_reversal"] + result["retention_after"]) / 3
    for f, family in enumerate(FAMILIES):
        segment = scores[f * 10:(f + 1) * 10]
        result[f"{family}_acquisition"] = segment[:, :, 96:128].mean(axis=(0, 2))
        result[f"{family}_curve"] = segment.reshape(10, t.shape[1], 24, 16).mean(axis=(0, 3))
        result[f"{family}_reward_curve"] = t[f*10:(f+1)*10, :, :, 2].reshape(10, t.shape[1], 24, 16).mean(axis=(0, 3))
    return {k: v.tolist() for k, v in result.items()}


def interval(values, stage, coverage=.95):
    a = np.asarray(values, dtype=float)
    generator = rng(stage, min(STAGES[stage][1]), 7)
    samples = a[generator.integers(0, len(a), (10000, len(a)))].mean(axis=1)
    lo, hi = np.quantile(samples, [(1-coverage)/2, (1+coverage)/2])
    return {"mean": float(a.mean()), "interval": [float(lo), float(hi)], "coverage": coverage,
            "block_values": a.tolist()}


def select_configs(configs, scores):
    selected = {}
    for rep, arm in (("native", "reward_only"), ("native", "feedback"), ("native", "delta"), ("pn", "delta")):
        candidates = [c for c in configs if c.representation == rep and c.arm == arm]
        best = max(scores[c.id] for c in candidates)
        tied = [c for c in candidates if best - scores[c.id] <= 1e-6]
        selected[f"{rep}_{arm}"] = asdict(min(tied, key=lambda c: (c.eta, -c.temperature)))
    return selected
