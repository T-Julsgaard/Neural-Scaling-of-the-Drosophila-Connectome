"""Confirmation-only copy of frozen development adapters; validation streams are identical."""
import copy

import numpy as np

from exp002.baseline import Config, FAMILIES
from .growth import (ARMS, SIZES, Base, Graph, allocation, degree_shuffle, digest,
                     from_record as validation_rebuild, resample)

STAGES = {"validation": (0, range(5)), "confirmation": (2, range(1000, 1020))}


def stream(stage, block, domain, component, *suffix, replicate=0, size=0):
    if stage not in STAGES or block not in STAGES[stage][1]:
        raise ValueError("Stage/block outside confirmation runner contract")
    if domain not in (0, 1, 2) or replicate not in range(3) or size not in (0, *SIZES):
        raise ValueError("Invalid stream domain")
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [3, STAGES[stage][0], block, domain, replicate, size, component, *suffix])))


def grid():
    return [Config("native", "delta", .01, .1)]


def rebuild(base, record):
    """Validate campaign identity, then reuse R03's raw lineage checks unchanged."""
    stage, block, rep, size = (record[k] for k in ("stage", "block", "replicate", "size"))
    stream(stage, block, 1, 1, replicate=rep, size=size)
    if record["schema"] != 2 or record["arm"] not in (*ARMS, "whole_uniform"):
        raise ValueError("Unknown campaign graph")
    if record["seed_namespace"] != [3, STAGES[stage][0], block, 1, rep, size]:
        raise ValueError("Graph seed metadata mismatch")
    legacy = copy.deepcopy(record)
    for j, node in enumerate(legacy["added_nodes"]):
        if node["id"] != f"grown:{block}:{rep}:{size}:{j}":
            raise ValueError("Campaign node identity mismatch")
        node["id"] = f"grown:0:{rep}:{size}:{j}"
    legacy["block"] = 0
    legacy["stage"] = "validation"
    replacement = record["native_replacement"]
    if record["arm"] == "whole_uniform":
        raw = np.asarray(replacement)
        if raw.shape != (40, 73) or not np.isfinite(raw).all() or (raw < 0).any() or (raw != np.floor(raw)).any():
            raise ValueError("Invalid native replacement")
        np.testing.assert_array_equal(np.sort(raw, axis=0), np.sort(base.raw, axis=0))
        adapted_base = Base(raw.astype(np.int64), base.strata, base.pn_ids, base.kc_ids, base.provenance)
        legacy["arm"] = "uniform"
    else:
        if replacement is not None:
            raise ValueError("Main growth changed native base")
        adapted_base = base
    graph = validation_rebuild(adapted_base, legacy)
    return Graph(graph.raw, copy.deepcopy(record))


def graphs_for(base, stage, block, size, replicate):
    random = lambda c, **kw: stream(stage, block, 1, c, replicate=replicate, size=kw.get("size", size))
    donors = []
    donor_rng = random(1)
    for stratum, count in enumerate(allocation(base.strata, size - 73), 1):
        donors.extend(donor_rng.choice(np.flatnonzero(base.strata == stratum), count, replace=True).tolist())
    priors = {s: (base.raw[:, base.strata == s] > 0).sum(axis=1) + 1. for s in range(1, 7)}
    added = {a: np.zeros((40, size - 73), dtype=np.int64) for a in ARMS[:3]}
    structured, uniform = random(2), random(3)
    for j, donor in enumerate(donors):
        column = base.raw[:, donor]
        added["clone"][:, j] = column
        added["structured"][:, j] = resample(column, priors[int(base.strata[donor])], structured)
        added["uniform"][:, j] = resample(column, np.ones(40), uniform)
    added["degree_null"], swaps = degree_shuffle(added["structured"], random(4))
    if not swaps["mixing_passed"]:
        raise ValueError("Degree null mixing failed")
    native_rng = random(6, size=0)
    replacement = np.column_stack([resample(c, np.ones(40), native_rng) for c in base.raw.T])
    added["whole_uniform"] = added["uniform"]
    graphs = {}
    for arm, columns in added.items():
        nodes = []
        for j, donor in enumerate(donors):
            partners = np.flatnonzero(columns[:, j]).tolist()
            nodes.append({"id": f"grown:{block}:{replicate}:{size}:{j}", "donor_column": donor,
                          "donor_id": base.kc_ids[donor], "stratum": int(base.strata[donor]),
                          "pn_columns": partners, "pn_ids": [base.pn_ids[p] for p in partners],
                          "raw_counts": columns[partners, j].tolist()})
        record = {"schema": 2, "stage": stage, "block": block, "replicate": replicate, "size": size,
                  "arm": arm, "source": base.provenance, "added_nodes": nodes,
                  "seed_namespace": [3, STAGES[stage][0], block, 1, replicate, size],
                  "native_replacement": replacement.tolist() if arm == "whole_uniform" else None,
                  "null_swaps": swaps if arm == "degree_null" else None}
        graphs[arm] = rebuild(base, record)
    for arm, graph in graphs.items():
        np.testing.assert_array_equal(np.sort(graph.raw[:, 73:], axis=0), np.sort(base.raw[:, donors], axis=0))
        if arm != "whole_uniform":
            np.testing.assert_array_equal(graph.raw[:, :73], base.raw)
    np.testing.assert_array_equal((graphs["degree_null"].raw[:, 73:] > 0).sum(axis=1),
                                  (graphs["structured"].raw[:, 73:] > 0).sum(axis=1))
    return graphs


class Inputs:
    def __init__(self, stage, block, episode):
        if episode not in range(20):
            raise ValueError("Episode outside 0..19")
        self.stage, self.block, self.episode = stage, block, episode
        self.family = FAMILIES[episode // 10]
        self.priority = stream(stage, block, 0, 1).permutation(73)
        stim = stream(stage, block, 0, 2, episode)
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
        self.observations = np.clip(cues + stream(stage, block, 0, 3, episode).normal(0., .1, (384, 2, 40)), 0., 1.)
        p = np.where(np.arange(2)[None, :] == self.preferred[:, None], .8, .2)
        self.outcomes = np.where(stream(stage, block, 0, 4, episode).random((384, 2)) < p, 1, -1)
        self.uniforms = stream(stage, block, 0, 5, episode).random(384)

    def probe_observations(self, trial, sigma):
        random = stream(self.stage, self.block, 0, 3, self.episode, 32, trial, int(round(sigma * 1000)))
        return np.clip(self.prototypes[self.order][None] + random.normal(0., sigma, (32, 2, 40)), 0., 1.)

    def digest(self):
        import hashlib
        h = hashlib.sha256()
        for a in (self.prototypes, self.order, self.observations, self.outcomes, self.uniforms, self.priority):
            h.update(np.ascontiguousarray(a, dtype="<f8").tobytes())
        return h.hexdigest()


def encode_fast(graph, observations, priority, sparsity="proportional", bottleneck=False):
    p, u = graph.projection, np.asarray(observations)
    n = p.shape[1]
    if sparsity not in ("proportional", "fixed4") or u.shape[-1] != 40:
        raise ValueError("Invalid encoding shape/mode")
    if not np.isfinite(u).all() or (u < 0).any() or (u > 1).any():
        raise ValueError("Invalid observations")
    if not np.isfinite(p).all() or (p < 0).any() or not np.allclose(p.sum(axis=0), 1., atol=1e-12, rtol=0):
        raise ValueError("Invalid normalized projection")
    if not np.array_equal(np.sort(priority), np.arange(n)):
        raise ValueError("Invalid tie priorities")
    flat = u.reshape(-1, 40)
    z = np.array([p.T @ row for row in flat])  # Preserve scalar dot-product arithmetic.
    k = 4 if sparsity == "fixed4" else max(1, int(np.floor(.05 * n + .5)))
    winners = np.lexsort((np.broadcast_to(priority, z.shape), -z), axis=-1)[:, :k]
    a = np.zeros_like(z)
    np.put_along_axis(a, winners, 10. / k, axis=1)
    if bottleneck:
        bins = np.array([int(i.split(":")[1]) % 32 for i in graph.record["source"]["kc_ids"]] + [j % 32 for j in range(n - 73)])
        counts = np.bincount(bins, minlength=32)
        adapter = np.zeros((n, 32))
        adapter[np.arange(n), bins] = 1. / counts[bins]
        a = a @ adapter
        totals = a.sum(axis=1, keepdims=True)
        if np.any(totals <= 0):
            raise ValueError("Zero bottleneck activity")
        a *= 10. / totals
    return a.reshape(*u.shape[:-1], a.shape[-1])


class EpisodeTask:
    def __init__(self, inputs, graph, mode="full"):
        if mode not in ("full", "fixed4", "bottleneck"):
            raise ValueError("Unknown assay control")
        if (inputs.stage, inputs.block) != (graph.record["stage"], graph.record["block"]):
            raise ValueError("Unpaired task/graph")
        self.inputs, self.graph, self.mode = inputs, graph, mode
        n = graph.raw.shape[1]
        self.priority = inputs.priority.copy()
        if n > 73:
            self.priority = stream(inputs.stage, inputs.block, 1, 5, replicate=graph.record["replicate"], size=n).permutation(n)
            self.priority[:73] = np.sort(self.priority[:73])[inputs.priority]
        self._activity = None

    def __getattr__(self, name):
        return getattr(self.inputs, name)

    def encode(self, observations, bottleneck=None):
        return encode_fast(self.graph, observations, self.priority,
                           "fixed4" if self.mode == "fixed4" else "proportional",
                           self.mode == "bottleneck" if bottleneck is None else bottleneck)

    def activities(self, representation):
        if representation != "native":
            raise ValueError("KC assay only")
        if self._activity is None:
            self._activity = self.encode(self.inputs.observations)
            self._activity.setflags(write=False)
        return self._activity

    def probe_activities(self, representation, trial, sigma):
        if representation != "native":
            raise ValueError("KC assay only")
        return self.encode(self.inputs.probe_observations(trial, sigma))

    def digest(self):
        return digest({"inputs": self.inputs.digest(), "graph": self.graph.sha256,
                       "mode": self.mode, "priority": self.priority.tolist()})


def conditions(base, stage, block):
    rows = []
    for size in SIZES:
        for rep in range(3):
            graphs = graphs_for(base, stage, block, size, rep)
            for arm, graph in graphs.items():
                if size == 73 and arm != "whole_uniform" and (rep != 0 or arm != "clone"):
                    continue
                modes = ["full"]
                if size == 110 and arm in ("clone", "structured", "degree_null"):
                    modes.append("fixed4")
                if (size == 110 and arm in ("structured", "degree_null")) or (size == 73 and arm == "clone"):
                    modes.append("bottleneck")
                for mode in modes:
                    rows.append({"id": f"N{size}_r{rep}_{arm}_{mode}", "size": size, "replicate": rep,
                                 "arm": arm, "mode": mode, "graph": graph})
    if len(rows) != 80:
        raise ValueError("Incomplete condition grid")
    return rows

