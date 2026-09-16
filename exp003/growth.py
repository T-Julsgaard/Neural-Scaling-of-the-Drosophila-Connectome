"""Audited raw-count growth with reconstructable donor lineage."""
from dataclasses import dataclass
import csv
import hashlib
import io
import json
import re
import zipfile

import numpy as np

from exp002.data import ROOT, load_projection

SIZES = (73, 80, 91, 110, 146)
ARMS = ("clone", "structured", "uniform", "degree_null")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


@dataclass
class Base:
    raw: np.ndarray
    strata: np.ndarray
    pn_ids: list
    kc_ids: list
    provenance: dict


def load_base():
    projection, provenance = load_projection()  # Verify archive, axes and counts first.
    audit = json.loads((ROOT / "research/reference_data_audit.json").read_text())
    with zipfile.ZipFile(ROOT / ".cache/research_assets/eichler_matrix.zip") as z:
        rows = list(csv.reader(io.StringIO(z.read(audit["csv_member"]).decode("utf-8-sig"), newline="")))
    counts = np.array([r[1:] for r in rows[1:]], dtype=np.int64)
    pn, kc = audit["groups"]["PN_left"], audit["groups"]["KC_mature_left"]
    raw = counts[np.ix_(pn, kc)]
    strata = []
    for i in kc:
        match = re.fullmatch(r"([1-6]) claw KC left", audit["nodes"][i]["label"])
        if not match:
            raise ValueError("Unexpected mature KC claw label")
        strata.append(int(match[1]))
    np.testing.assert_array_equal(raw / raw.sum(axis=0), projection)
    raw.setflags(write=False)
    return Base(raw, np.array(strata), provenance["pn_ids"], provenance["kc_ids"], provenance)


def generator(block, replicate, size, component):
    # Validation only. Reserve stage 1/2 for a separately frozen campaign contract.
    if block not in range(5) or replicate not in range(3) or size not in SIZES:
        raise ValueError("Validation block/replicate/size outside declared scope")
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [3, 0, block, replicate, size, component])))


def allocation(strata, added):
    counts = np.bincount(strata, minlength=7)[1:7]
    # Integer arithmetic makes largest-remainder ties exact.
    numerators = added * counts
    result = numerators // len(strata)
    order = sorted(range(6), key=lambda i: (-(numerators[i] % len(strata)), i))
    for i in order[:added - int(result.sum())]:
        result[i] += 1
    return result


def resample(column, probabilities, random):
    weights = column[column > 0]
    p = probabilities.astype(float).copy()
    partners = []
    for _ in weights:
        partner = int(random.choice(len(p), p=p / p.sum()))
        partners.append(partner)
        p[partner] = 0.
    result = np.zeros(len(column), dtype=np.int64)
    result[partners] = random.permutation(weights)
    return result


def degree_shuffle(added, random):
    output = added.copy()
    edges = np.argwhere(output > 0)
    e = len(edges)
    successes = attempts = 0
    while e >= 2 and successes < 10 * e and attempts < 100 * e:
        attempts += 1
        a, b = random.choice(e, 2, replace=False)
        p1, k1 = edges[a]
        p2, k2 = edges[b]
        if p1 == p2 or k1 == k2 or output[p1, k2] or output[p2, k1]:
            continue
        # Contact counts travel with the target, not the source PN.
        output[p2, k1], output[p1, k2] = output[p1, k1], output[p2, k2]
        output[p1, k1] = output[p2, k2] = 0
        edges[a], edges[b] = (p2, k1), (p1, k2)
        successes += 1
    return output, {"edges_added": e, "attempts": attempts, "successful_swaps": successes,
                    "mixing_passed": successes >= e,
                    "edge_overlap_fraction": float(np.count_nonzero((added > 0) & (output > 0)) / e) if e else 1.}


@dataclass
class Graph:
    raw: np.ndarray
    record: dict

    @property
    def projection(self):
        return self.raw / self.raw.sum(axis=0)

    @property
    def sha256(self):
        return digest(self.record)


def from_record(base, record):
    """Rebuild from explicit lineage, without consuming random streams."""
    if record["source"] != base.provenance or record["arm"] not in ARMS or record["size"] not in SIZES:
        raise ValueError("Graph source/arm/size mismatch")
    size = record["size"]
    generator(record["block"], record["replicate"], size, 0)
    nodes = record["added_nodes"]
    if len(nodes) != size - 73:
        raise ValueError("Lineage length mismatch")
    raw = np.zeros((40, size), dtype=np.int64)
    raw[:, :73] = base.raw
    for ordinal, node in enumerate(nodes):
        expected = f'grown:{record["block"]}:{record["replicate"]}:{size}:{ordinal}'
        donor = node["donor_column"]
        if not isinstance(donor, int) or donor not in range(73):
            raise ValueError("Invalid donor")
        if node["id"] != expected or node["donor_id"] != base.kc_ids[donor] or node["stratum"] != int(base.strata[donor]):
            raise ValueError("Donor lineage mismatch")
        partners, weights = node["pn_columns"], node["raw_counts"]
        if len(partners) != len(weights) or len(set(partners)) != len(partners):
            raise ValueError("Duplicate or missing partners")
        if any(not isinstance(p, int) or p not in range(40) for p in partners):
            raise ValueError("Invalid PN column")
        if node["pn_ids"] != [base.pn_ids[p] for p in partners]:
            raise ValueError("PN lineage mismatch")
        if any(not isinstance(w, int) or w <= 0 for w in weights):
            raise ValueError("Invalid contact count")
        column = base.raw[:, donor]
        if sorted(weights) != sorted(column[column > 0].tolist()):
            raise ValueError("Donor contact multiset mismatch")
        raw[partners, 73 + ordinal] = weights
        if record["arm"] == "clone" and not np.array_equal(raw[:, 73 + ordinal], column):
            raise ValueError("Clone changed donor column")
    observed = np.bincount([n["stratum"] for n in nodes], minlength=7)[1:7]
    if not np.array_equal(observed, allocation(base.strata, size - 73)):
        raise ValueError("Stratum allocation mismatch")
    if (raw.sum(axis=0) <= 0).any():
        raise ValueError("Zero-input feature")
    raw.setflags(write=False)
    return Graph(raw, record)


def grow(base, size, block=0, replicate=0):
    donor_rng = generator(block, replicate, size, 1)
    donors = []
    for stratum, count in enumerate(allocation(base.strata, size - 73), start=1):
        donors.extend(donor_rng.choice(np.flatnonzero(base.strata == stratum), count, replace=True).tolist())
    priors = {s: (base.raw[:, base.strata == s] > 0).sum(axis=1) + 1. for s in range(1, 7)}
    additions = {arm: np.zeros((40, size - 73), dtype=np.int64) for arm in ARMS[:3]}
    structured_rng, uniform_rng = (generator(block, replicate, size, c) for c in (2, 3))
    for j, donor in enumerate(donors):
        column = base.raw[:, donor]
        additions["clone"][:, j] = column
        additions["structured"][:, j] = resample(column, priors[int(base.strata[donor])], structured_rng)
        additions["uniform"][:, j] = resample(column, np.ones(40), uniform_rng)
    additions["degree_null"], swaps = degree_shuffle(additions["structured"], generator(block, replicate, size, 4))
    graphs = {}
    for arm in ARMS:
        nodes = []
        for j, donor in enumerate(donors):
            partners = np.flatnonzero(additions[arm][:, j]).tolist()
            nodes.append({"id": f"grown:{block}:{replicate}:{size}:{j}", "donor_column": donor,
                          "donor_id": base.kc_ids[donor], "stratum": int(base.strata[donor]),
                          "pn_columns": partners, "pn_ids": [base.pn_ids[p] for p in partners],
                          "raw_counts": additions[arm][partners, j].tolist()})
        record = {"schema": 1, "stage": "validation", "block": block, "replicate": replicate,
                  "size": size, "arm": arm, "source": base.provenance, "added_nodes": nodes,
                  "seed_namespace": [3, 0, block, replicate, size],
                  "null_swaps": swaps if arm == "degree_null" else None}
        graphs[arm] = from_record(base, record)
    return graphs


def check_matched(base, graphs):
    """Independent checks on the realized matrices, including cross-arm constraints."""
    reference = graphs["structured"].raw
    donors = [n["donor_column"] for n in graphs["structured"].record["added_nodes"]]
    for arm in ARMS:
        graph = graphs[arm]
        np.testing.assert_array_equal(graph.raw[:, :73], base.raw)
        np.testing.assert_array_equal(from_record(base, graph.record).raw, graph.raw)
        if [n["donor_column"] for n in graph.record["added_nodes"]] != donors:
            raise ValueError("Unpaired donors")
        np.testing.assert_array_equal(np.sort(graph.raw[:, 73:], axis=0), np.sort(base.raw[:, donors], axis=0))
        np.testing.assert_allclose(graph.projection.sum(axis=0), 1., atol=1e-12, rtol=0)
    null = graphs["degree_null"]
    np.testing.assert_array_equal((null.raw[:, 73:] > 0).sum(axis=1), (reference[:, 73:] > 0).sum(axis=1))
    swaps = null.record["null_swaps"]
    if not swaps["mixing_passed"]:
        raise ValueError("Degree-null mixing failed; organization contrast prohibited")
    return True
