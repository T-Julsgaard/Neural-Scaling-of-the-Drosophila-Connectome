"""Audit every development episode, nested summary and frozen shared selection."""
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.campaign import now, read_json
from exp002.data import sha256
from exp003.campaign import snapshot, summarize_condition
from exp003.development import EpisodeTask, Inputs, grid, rebuild, select_shared
from exp003.growth import load_base
from tools.audit_growth import verify


def audit():
    verify()
    folder = ROOT / "results/exp003_development"
    contract = read_json(folder / "contract.json")
    validated = json.loads((ROOT / "research/exp003_development_validation.json").read_text())
    frozen_snapshot = contract["contract"]["code_snapshot"]
    if validated["code_snapshot"] != frozen_snapshot:
        raise ValueError("Frozen contract differs from validated development code")
    from exp002.campaign import text_hash
    for name, expected in frozen_snapshot.items():
        if name == "experiments/EXP-003.md":
            continue  # Live experiment status; stage protocol is separately frozen.
        if text_hash(ROOT / name) != expected:
            raise ValueError("Development code/protocol changed after freeze: " + name)
    report = read_json(folder / "report.json")
    selection = read_json(folder / "selection.json")
    contract_hash = sha256(folder / "contract.json")
    if report["status"] != "complete" or report["contract_sha256"] != contract_hash or selection["contract_sha256"] != contract_hash:
        raise ValueError("Incomplete or mismatched development run")
    if report["confirmation_blocks"] or report["excluded_episodes"] or report["numerical_failures"]:
        raise ValueError("Unexpected confirmation/exclusion/failure")
    base = load_base()
    blocks, files, episodes = [], {}, 0
    start = time.perf_counter()
    def remember(path):
        path = Path(path)
        files[path.relative_to(ROOT).as_posix()] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    for path in folder.iterdir():
        if path.is_file() and path.suffix != '.tmp':
            remember(path)
    for block in range(100, 110):
        directory = folder / f"block_{block}"
        summary_path = directory / "summary.json"
        summary = read_json(summary_path)
        if selection["block_summary_sha256"][str(block)] != sha256(summary_path) or len(summary["conditions"]) != 80:
            raise ValueError("Block summary changed/incomplete")
        inputs = [Inputs("development", block, ep) for ep in range(20)]
        input_hashes = [i.digest() for i in inputs]
        if summary["input_hashes"] != input_hashes:
            raise ValueError("Wrong exogenous inputs")
        seen = set()
        for row in summary["conditions"]:
            if row["id"] in seen:
                raise ValueError("Duplicated condition")
            seen.add(row["id"])
            local = directory / row["id"]
            graph = rebuild(base, read_json(local / "graph.json"))
            state = read_json(local / "checkpoint.json")
            if state["next_episode"] != 20 or len(state["artifacts"]) != 20:
                raise ValueError("Missing episodes")
            expected_identity = {"contract_sha256": contract_hash, "graph_sha256": graph.sha256,
                                 "condition": row["id"], "mode": row["mode"], "inputs": input_hashes}
            for k, value in expected_identity.items():
                if state["identity"][k] != value:
                    raise ValueError("Checkpoint identity differs: " + k)
            expected_configs = [c.id for c in grid()]
            if row["size"] == 73 and row["arm"] == "clone" and row["mode"] == "full":
                expected_configs.append("native_frozen_eta0_T0.2")
            if state["config_ids"] != expected_configs or row["config_ids"] != expected_configs:
                raise ValueError("Wrong settings/order")
            for ep, item in enumerate(state["artifacts"]):
                path = local / item["file"]
                if item["file"] != f"episode_{ep:02d}.npz" or sha256(path) != item["sha256"]:
                    raise ValueError("Changed episode artifact")
                task = EpisodeTask(inputs[ep], graph, row["mode"])
                with np.load(path, allow_pickle=False) as data:
                    if str(data["task_hash"]) != task.digest() or item["task_hash"] != task.digest() or str(data["inputs_hash"]) != input_hashes[ep]:
                        raise ValueError("Saved episode identity mismatch")
                    np.testing.assert_array_equal(data["config_ids"], expected_configs)
                    for key in ("trace", "probes", "plus", "minus"):
                        if not np.isfinite(data[key]).all():
                            raise ValueError("Nonfinite episode")
                    if len(expected_configs) == 10:
                        np.testing.assert_array_equal(data["trace"][-1, :, 0], .5)
                        np.testing.assert_array_equal(data["probes"][-1], .5)
                        np.testing.assert_array_equal(data["plus"][-1], .1)
                        np.testing.assert_array_equal(data["minus"][-1], .1)
                remember(path)
                episodes += 1
            calculated = summarize_condition(local, state, {**row, "graph": graph})
            if row != calculated or read_json(local / "summary.json") != calculated:
                raise ValueError("Metrics or features disagree with raw artifacts")
            for name in ("graph.json", "checkpoint.json", "summary.json"):
                remember(local / name)
        remember(summary_path)
        blocks.append(summary["conditions"])
        print(json.dumps({"audited_block": block, "episodes": episodes}), flush=True)
    expected = select_shared(blocks)
    for key, value in expected.items():
        if selection[key] != value:
            raise ValueError("Selected setting does not follow frozen weighting")
    if episodes != 16000 or report["episode_batches"] != episodes:
        raise ValueError("Wrong episode count")
    recovery_path = ROOT / "research/exp003_development_recovery.json"
    recovery = json.loads(recovery_path.read_text()) if recovery_path.exists() else None
    record = {"run_id": "EXP-003-development-v1.0", "status": "completed_development_only", "audited_utc": now(),
              "validation": "36 tests passed before freezing", "development_blocks": 10, "confirmation_blocks": 0,
              "graph_conditions": 800, "episode_batches": episodes, "configuration_episodes": report["configuration_episodes"],
              "excluded_episodes": 0, "numerical_failures": 0, "selected": selection["selected"],
              "selection_scores": selection["scores"], "resources": report, "files": files,
              "infrastructure_recovery": recovery,
              "retained_bytes": sum(f["bytes"] for f in files.values()), "audit_seconds": time.perf_counter() - start,
              "limits": ["Development comparisons are descriptive because these blocks selected the setting",
                         "Graph replicates are nested within ten independent task blocks", "No H3 confirmation or biological superiority established"]}
    dest = ROOT / "research/runs/EXP-003-development.json"
    dest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: record[k] for k in ("status", "episode_batches", "selected", "retained_bytes", "audit_seconds")}))


if __name__ == "__main__":
    audit()
