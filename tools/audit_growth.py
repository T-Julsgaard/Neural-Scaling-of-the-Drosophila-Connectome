"""Verify retained R03 evidence and optionally recompute all feature diagnostics."""
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.campaign import read_json, snapshot, text_hash, verify_gates
from exp002.data import sha256
from exp003.assay import diagnostics
from exp003.growth import from_record, load_base


def verify(recompute=False):
    verify_gates()
    report = json.loads((ROOT / "research/exp003_validation.json").read_text())
    if report["status"] != "passed" or report["failures"] or report["skipped"]:
        raise ValueError("R03 did not pass")
    if report["development_blocks"] or report["confirmation_blocks"]:
        raise ValueError("Bounded validation mislabelled as a campaign")
    if report["baseline_code_snapshot"] != snapshot():
        raise ValueError("Frozen baseline changed")
    for name, expected in report["code_snapshot"].items():
        if name == "experiments/EXP-003.md":
            # The experiment specification includes a live status line and links to later stages.
            # Frozen executable code and stage-specific protocols remain hash checked below.
            continue
        if text_hash(ROOT / name) != expected:
            raise ValueError("Stale R03 code/protocol: " + name)
    folder = ROOT / report["artifact_directory"]
    for name, expected in report["files"].items():
        path = folder / name
        if path.stat().st_size != expected["bytes"] or sha256(path) != expected["sha256"]:
            raise ValueError("Changed R03 artifact: " + name)
    graphs = read_json(folder / "graphs.json")
    rows = read_json(folder / "diagnostics.json")
    if len(rows) != report["diagnostics"]["rows"]:
        raise ValueError("Incomplete diagnostic rows")
    if recompute:
        base = load_base()
        for row in rows:
            graph = from_record(base, graphs[row["graph"]])
            if graph.sha256 != row["graph_sha256"]:
                raise ValueError("Graph digest mismatch")
            with np.load(folder / row["archive"], allow_pickle=False) as archive:
                np.testing.assert_array_equal(archive["raw"], graph.raw)
                activity = np.unpackbits(archive["packed_activity"], axis=-1, count=row["size"]) * archive["active_value"]
                np.testing.assert_array_equal(activity.shape, archive["activity_shape"])
                for key in ("traces", "probes", "plus", "minus"):
                    if not np.isfinite(archive[key]).all():
                        raise ValueError("Nonfinite smoke learning artifact")
            for key, expected in diagnostics(graph, activity).items():
                if expected is None:
                    if row[key] is not None:
                        raise ValueError("Unexpected added-cell statistic")
                else:
                    np.testing.assert_allclose(row[key], expected, rtol=0, atol=1e-12, err_msg=key)
    return {"status": "passed", "artifact_files": len(report["files"]),
            "diagnostic_rows_recomputed": len(rows) if recompute else 0,
            "tests_run": report["tests_run"], "baseline_unchanged": True}


if __name__ == "__main__":
    print(json.dumps(verify(recompute=True)))
