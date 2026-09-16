"""Validation bridge to the frozen EXP-002 learner and paired input streams."""
import numpy as np

from exp002.baseline import feature_statistics, feature_summary, rng
from exp002.data import encode
from .growth import digest, generator


def encode_observations(graph, observations, priority, sparsity="proportional", bottleneck=False):
    if sparsity not in ("proportional", "fixed4"):
        raise ValueError("Unknown sparsity control")
    p = graph.projection
    n = p.shape[1]
    flat = np.asarray(observations).reshape(-1, 40)
    if sparsity == "proportional" or n == 73:
        activity = np.array([encode(p, row, priority) for row in flat])
    else:
        # The same scalar projection/order arithmetic as the frozen encoder.
        if not np.isfinite(flat).all() or (flat < 0).any() or (flat > 1).any():
            raise ValueError("PN input outside [0,1]")
        if not np.array_equal(np.sort(priority), np.arange(n)):
            raise ValueError("Invalid priority")
        activity = np.zeros((len(flat), n))
        for i, row in enumerate(flat):
            activity[i, np.lexsort((priority, -(p.T @ row)))[:4]] = 2.5
    if bottleneck:
        native = [int(i.split(":")[1]) % 32 for i in graph.record["source"]["kc_ids"]]
        bins = np.array(native + [j % 32 for j in range(n - 73)])
        counts = np.bincount(bins, minlength=32)
        adapter = np.zeros((n, 32))
        adapter[np.arange(n), bins] = 1. / counts[bins]
        activity = activity @ adapter
        total = activity.sum(axis=1, keepdims=True)
        if np.any(total <= 0):
            raise ValueError("Empty readout bottleneck")
        activity *= 10. / total
    return activity.reshape(*observations.shape[:-1], activity.shape[-1])


class GrowthTask:
    """Reuse validation inputs only; architecture is part of the checkpoint identity.

    EXP-002 validation namespace 2 is intentional for the N=73 identity bridge.
    Fresh EXP-003 development/confirmation inputs require a new frozen contract.
    """
    def __init__(self, base_task, graph, sparsity="proportional", bottleneck=False):
        if base_task.stage != "validation" or base_task.block != graph.record["block"]:
            raise ValueError("Growth bridge accepts paired validation tasks only")
        if sparsity not in ("proportional", "fixed4"):
            raise ValueError("Invalid sparsity")
        self.base_task, self.graph = base_task, graph
        self.sparsity, self.bottleneck = sparsity, bottleneck
        n = graph.raw.shape[1]
        if n == 73:
            self.priority = base_task.priority.copy()
        else:
            priority = generator(base_task.block, graph.record["replicate"], n, 5).permutation(n)
            # Random interleaving with grown cells, native relative tie order preserved.
            priority[:73] = np.sort(priority[:73])[base_task.priority]
            self.priority = priority

    def __getattr__(self, name):
        return getattr(self.base_task, name)

    def activities(self, representation):
        if representation != "native":
            raise ValueError("Growth assay uses KC features")
        return encode_observations(self.graph, self.observations, self.priority, self.sparsity, self.bottleneck)

    def probe_activities(self, representation, trial, sigma):
        if representation != "native":
            raise ValueError("Growth assay uses KC features")
        random = rng(self.stage, self.block, 3, self.episode, 32, trial, int(round(sigma * 1000)))
        observations = np.clip(self.prototypes[self.order][None, :, :] +
                               random.normal(0., sigma, (32, 2, 40)), 0., 1.)
        return encode_observations(self.graph, observations, self.priority, self.sparsity, self.bottleneck)

    def digest(self):
        return digest({"base_task": self.base_task.digest(), "graph": self.graph.sha256,
                       "sparsity": self.sparsity, "bottleneck": self.bottleneck,
                       "priority": self.priority.tolist()})


def diagnostics(graph, activity):
    """Both presented cues, before readout learning; zeros count as unused."""
    a = activity.reshape(-1, activity.shape[-1])
    if a.shape[1] != graph.raw.shape[1]:
        raise ValueError("Cell diagnostics require full pre-bottleneck activities")
    stats = feature_statistics(a)
    result = feature_summary(stats)
    cov = stats["gram"] / len(a) - np.outer(stats["sum"] / len(a), stats["sum"] / len(a))
    eigenvalues = np.linalg.eigvalsh(cov)
    tolerance = max(float(eigenvalues.max()), 1.) * 1e-10
    native_rank = int(np.count_nonzero(np.linalg.eigvalsh(cov[:73, :73]) > tolerance))
    full_rank = int(np.count_nonzero(eigenvalues > tolerance))
    columns = [tuple(c) for c in graph.projection.T]
    seen = set(columns[:73])
    added_novel = 0
    for column in columns[73:]:
        added_novel += column not in seen
        seen.add(column)
    patterns = [np.packbits(a[:, i] > 0).tobytes() for i in range(a.shape[1])]
    seen = set(patterns[:73])
    active_novel = 0
    for i, pattern in enumerate(patterns[73:], 73):
        active_novel += bool(stats["active"][i] > 0 and pattern not in seen)
        seen.add(pattern)
    result.update({"size": a.shape[1], "edges": int(np.count_nonzero(graph.raw)),
                   "contacts": int(graph.raw.sum()), "readout_weights": 2 * a.shape[1],
                   "duplicate_normalized_columns": a.shape[1] - len(set(columns)),
                   "added_novel_normalized_columns": added_novel,
                   "added_novel_active_patterns": active_novel,
                   "centered_activity_rank": full_rank,
                   "added_linear_dimensions_given_native": full_rank - native_rank,
                   "native_never_active_fraction": float(np.mean(stats["active"][:73] == 0)),
                   "added_never_active_fraction": float(np.mean(stats["active"][73:] == 0)) if a.shape[1] > 73 else None})
    return result
