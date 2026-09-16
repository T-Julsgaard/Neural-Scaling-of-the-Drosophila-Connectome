"""R03 implementation validation plus descriptive, stage-zero feature diagnostics."""
import argparse
import json
from pathlib import Path
import sys
import time
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.baseline import BatchEpisode, Config, Task
from exp002.campaign import atomic_json, environment, now, peak_memory, snapshot, text_hash, verify_gates
from exp002.data import sha256
from exp003.assay import GrowthTask, diagnostics
from exp003.growth import ARMS, SIZES, check_matched, grow, load_base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/validation/exp003")
    parser.add_argument("--report", type=Path, default=ROOT / "research/exp003_validation.json")
    args = parser.parse_args()
    if args.output.exists() or args.report.exists():
        raise SystemExit("Preserve earlier runs; supply fresh --output and --report paths")
    verify_gates()
    started, clock = now(), time.perf_counter()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:
        raise SystemExit("R03 tests failed or skipped; no diagnostic run launched")
    args.output.mkdir(parents=True)
    base = load_base()
    projection = base.raw / base.raw.sum(axis=0)
    tasks = [Task(projection, "validation", 0, ep) for ep in range(20)]
    configs = [Config("native", "delta", .01, .1)]
    rows, graph_records, smoke = [], {}, []
    # One validation block, three nested graph replicates, no independent-block inference.
    for size in SIZES:
        for replicate in (range(1) if size == 73 else range(3)):
            graphs = grow(base, size, 0, replicate)
            check_matched(base, graphs)
            for arm in (ARMS[:1] if size == 73 else ARMS):
                graph = graphs[arm]
                graph_id = f"N{size}_r{replicate}_{arm}"
                graph_records[graph_id] = graph.record
                modes = ("proportional", "fixed4") if size == 110 and arm in ("structured", "degree_null", "clone") else ("proportional",)
                for mode in modes:
                    row_started = time.perf_counter()
                    adapted = [GrowthTask(t, graph, mode) for t in tasks]
                    activity = np.concatenate([t.activities("native") for t in adapted], axis=0)
                    row = diagnostics(graph, activity)
                    row.update({"graph": graph_id, "graph_sha256": graph.sha256, "arm": arm,
                                "replicate": replicate, "block": 0, "sparsity": mode})
                    runs = []
                    for ep in (0, 10):
                        batch = BatchEpisode(adapted[ep], configs)
                        batch.run_until()
                        runs.append(batch)
                    archive = args.output / f"{graph_id}_{mode}.npz"
                    np.savez_compressed(archive, raw=graph.raw, packed_activity=np.packbits(activity > 0, axis=-1),
                                        activity_shape=np.array(activity.shape), active_value=np.array(10. / int((activity[0, 0] > 0).sum())),
                                        traces=np.array([r.trace for r in runs]), probes=np.array([r.probes for r in runs]),
                                        plus=np.array([r.plus for r in runs]), minus=np.array([r.minus for r in runs]))
                    row["elapsed_seconds"] = time.perf_counter() - row_started
                    row["archive"] = archive.name
                    row["archive_sha256"] = sha256(archive)
                    # Independently recover exactly the cell activities retained for audit.
                    with np.load(archive, allow_pickle=False) as data:
                        restored = np.unpackbits(data["packed_activity"], axis=-1, count=size) * data["active_value"]
                        np.testing.assert_array_equal(restored, activity)
                    rows.append(row)
                if size in (73, 110) and (size == 73 or arm in ("structured", "degree_null")):
                    for ep in (0, 10):
                        batch = BatchEpisode(GrowthTask(tasks[ep], graph, bottleneck=True), configs)
                        batch.run_until()
                        smoke.append({"graph": graph_id, "episode": ep, "readout_weights": int(batch.plus.size * 2),
                                      "final_plus": batch.plus.tolist(), "final_minus": batch.minus.tolist(),
                                      "probes": batch.probes.tolist()})
            print(f"Validated diagnostic size={size} replicate={replicate}", flush=True)
    atomic_json(args.output / "graphs.json", graph_records)
    atomic_json(args.output / "bottleneck_smoke.json", smoke)
    atomic_json(args.output / "diagnostics.json", rows)
    files = {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size} for p in sorted(args.output.iterdir())}
    code = [*ROOT.glob("exp003/*.py"), ROOT / "tests/test_exp003.py", Path(__file__),
            ROOT / "experiments/EXP-003.md", ROOT / "experiments/EXP-003-validation-protocol.md"]
    report = {"status": "passed", "kind": "bounded_implementation_validation_and_descriptive_diagnostics",
              "started_utc": started, "completed_utc": now(), "tests_run": result.testsRun,
              "failures": [], "skipped": [], "development_blocks": 0, "confirmation_blocks": 0,
              "invariant_validation": {"blocks": list(range(5)), "replicates": list(range(3)), "sizes": SIZES,
                                       "arms": ARMS, "graph_instances": 300},
              "diagnostics": {"block": 0, "episodes": 20, "presented_cues_per_graph": 15360,
                              "rows": len(rows), "independent_blocks": 1, "parameter_selection": False},
              "smoke_learning": {"episodes_per_configuration": [0, 10], "eta": .01, "temperature": .1,
                                 "learner": "EXP-002 development-selected generic delta", "full_configurations": len(rows),
                                 "bottleneck_episodes": len(smoke)},
              "baseline_code_snapshot": snapshot(), "code_snapshot": {p.relative_to(ROOT).as_posix(): text_hash(p) for p in code},
              "source": base.provenance, "environment": environment(),
              "elapsed_seconds": time.perf_counter() - clock, "peak_memory_bytes": peak_memory(),
              "artifact_directory": args.output.relative_to(ROOT).as_posix(), "files": files,
              "retained_bytes": sum(v["bytes"] for v in files.values()),
              "limits": ["Not a growth hypothesis test or fresh development campaign",
                         "One validation block; graph replicates are not independent task blocks",
                         "Distinct wiring/activity does not establish useful learning or biological advantage",
                         "Exploratory replacement of the entire native base remains unimplemented"]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("status", "tests_run", "elapsed_seconds", "retained_bytes")}))


if __name__ == "__main__":
    main()
