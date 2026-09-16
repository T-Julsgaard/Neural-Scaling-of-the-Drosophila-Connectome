"""Hash-checked, axis-aware loader for the audited D05 mature left circuit."""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_projection(archive_path=None):
    archive_path = Path(archive_path or ROOT / ".cache/research_assets/eichler_matrix.zip")
    audit = json.loads((ROOT / "research/reference_data_audit.json").read_text())
    assets = json.loads((ROOT / "research/asset_audit.json").read_text())
    expected = next(a["sha256"] for a in assets if a["name"] == "eichler_matrix.zip")
    if sha256(archive_path) != expected:
        raise ValueError("D05 archive hash mismatch")
    with zipfile.ZipFile(archive_path) as z:
        raw = z.read(audit["csv_member"])
    if hashlib.sha256(raw).hexdigest() != audit["csv_sha256"]:
        raise ValueError("D05 CSV hash mismatch")
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline="")))
    row_labels, column_labels = [r[0] for r in rows[1:]], rows[0][1:]
    counts = np.array([r[1:] for r in rows[1:]], dtype=np.float64)
    pn, kc = audit["groups"]["PN_left"], audit["groups"]["KC_mature_left"]
    if counts.shape != (387, 387) or len(pn) != 40 or len(kc) != 73:
        raise ValueError("Unexpected D05 dimensions")
    selected = pn + kc
    if len(set(selected)) != len(selected):
        raise ValueError("Duplicate matrix IDs")
    for i in selected:
        if row_labels[i] != column_labels[i] or row_labels[i] != audit["nodes"][i]["label"]:
            raise ValueError("Selected axis identity mismatch")
    c = counts[np.ix_(pn, kc)]
    if not np.isfinite(c).all() or (c < 0).any() or (c != np.floor(c)).any() or (c.sum(axis=0) <= 0).any():
        raise ValueError("Invalid selected counts")
    expected_counts = audit["pn_kc_mature_left"]
    if np.count_nonzero(c) != expected_counts["aggregated_edges"] or c.sum() != expected_counts["synapse_count_sum"]:
        raise ValueError("Audited count totals differ")
    p = c / c.sum(axis=0)
    return p, {"source_id": "S64", "archive_sha256": expected,
               "csv_sha256": audit["csv_sha256"],
               "projection_sha256": hashlib.sha256(p.astype("<f8").tobytes()).hexdigest(),
               "pn_ids": [f"matrix:{i}" for i in pn], "kc_ids": [f"matrix:{i}" for i in kc],
               "orientation": "row PN -> column mature KC", "shape": list(p.shape),
               "edges": int(np.count_nonzero(c)), "contacts": int(c.sum())}


def encode(projection, inputs, priority):
    p, u, priority = map(np.asarray, (projection, inputs, priority))
    if p.ndim != 2 or u.shape != (p.shape[0],) or priority.shape != (p.shape[1],):
        raise ValueError("Encoding dimensions differ")
    if not np.isfinite(u).all() or (u < 0).any() or (u > 1).any():
        raise ValueError("PN input outside [0,1]")
    if not np.isfinite(p).all() or (p < 0).any() or not np.allclose(p.sum(axis=0), 1, rtol=0, atol=1e-12):
        raise ValueError("Projection is not target-normalized")
    if not np.array_equal(np.sort(priority), np.arange(p.shape[1])):
        raise ValueError("Priority must be a permutation of feature indices")
    z = p.T @ u
    k = max(1, int(np.floor(0.05 * p.shape[1] + 0.5)))
    winners = np.lexsort((priority, -z))[:k]
    s = np.zeros(p.shape[1], dtype=np.float64)
    s[winners] = 10. / k
    return s
