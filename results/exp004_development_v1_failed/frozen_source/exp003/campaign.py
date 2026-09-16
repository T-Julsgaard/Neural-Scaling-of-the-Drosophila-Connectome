"""Immutable development contracts, episode recovery and nested graph aggregation."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil
import time

import numpy as np

from exp002.baseline import BatchEpisode, Config, block_metrics, feature_statistics, feature_summary
from exp002.campaign import atomic_json, environment, now, peak_memory, read_json, snapshot as baseline_snapshot, text_hash
from exp002.data import ROOT, sha256
from .development import EpisodeTask, Inputs, conditions, grid, select_shared
from .growth import digest, load_base


def snapshot():
    old = json.loads((ROOT / "research/exp003_validation.json").read_text())["code_snapshot"]
    files = ["exp003/development.py", "exp003/campaign.py", "tests/test_growth_development.py",
             "tools/run_growth_development.py", "tools/validate_growth_development.py",
             "experiments/EXP-003-development-protocol.md"]
    return {**baseline_snapshot(), **{p: text_hash(ROOT / p) for p in old},
            **{p: text_hash(ROOT / p) for p in files}}


def summarize_condition(directory, state, condition):
    traces, probes, cell, readout = [], [], {}, {}
    for item in state["artifacts"]:
        with np.load(directory / item["file"], allow_pickle=False) as data:
            traces.append(data["trace"])
            probes.append(data["probes"])
            for prefix, target in (("cell", cell), ("readout", readout)):
                for key in ("count", "sum", "gram", "active"):
                    target[key] = target.get(key, 0) + data[f"{prefix}_{key}"]
    if len(traces) != 20:
        raise ValueError("Incomplete condition cannot be summarized")
    full = feature_summary(cell)
    full["native_never_active_fraction"] = float(np.mean(cell["active"][:73] == 0))
    full["added_never_active_fraction"] = float(np.mean(cell["active"][73:] == 0)) if condition["size"] > 73 else None
    graph = condition["graph"]
    full["duplicate_normalized_columns"] = graph.raw.shape[1] - len(set(map(tuple, graph.projection.T)))
    return {**{k: condition[k] for k in ("id", "size", "arm", "replicate", "mode")},
            "metrics": block_metrics(traces, probes), "cell_features": full,
            "readout_features": feature_summary(readout), "config_ids": state["config_ids"],
            "graph_sha256": graph.sha256, "resources": state["resources"],
            "edges": int(np.count_nonzero(graph.raw)), "contacts": int(graph.raw.sum()),
            "readout_weights": 64 if condition["mode"] == "bottleneck" else 2 * condition["size"],
            "realized_ratio": condition["size"] / 73}


def execute_condition(output, condition, inputs, configs, contract_hash, episode_limit=20):
    """All inputs are reset episodes; uncheckpointed writes are safe to replay."""
    if not 0 <= episode_limit <= 20 or len(inputs) != 20:
        raise ValueError("Invalid episode limit/inputs")
    directory = Path(output) / condition["id"]
    directory.mkdir(parents=True, exist_ok=True)
    identity = {"contract_sha256": contract_hash, "graph_sha256": condition["graph"].sha256,
                "condition": condition["id"], "mode": condition["mode"],
                "inputs": [i.digest() for i in inputs], "configs": [asdict(c) for c in configs]}
    checkpoint = directory / "checkpoint.json"
    state = {"identity": identity, "next_episode": 0, "artifacts": [], "config_ids": [c.id for c in configs],
             "resources": {"wall_seconds": 0., "cpu_seconds": 0., "preprocessing_seconds": 0.,
                           "learning_seconds": 0., "peak_worker_memory_bytes": 0},
             "boundary": "Next episode reset: all weights 0.1; no live RNG/state crosses boundary"}
    if checkpoint.exists():
        state = read_json(checkpoint)
        if state["identity"] != identity or state["next_episode"] != len(state["artifacts"]):
            raise ValueError("Condition checkpoint identity/chronology mismatch")
        for ep, item in enumerate(state["artifacts"]):
            if item["file"] != f"episode_{ep:02d}.npz" or sha256(directory / item["file"]) != item["sha256"]:
                raise ValueError("Completed artifact changed")
        if read_json(directory / "graph.json") != condition["graph"].record:
            raise ValueError("Saved graph changed")
    else:
        atomic_json(directory / "graph.json", condition["graph"].record)
    summary_file = directory / "summary.json"
    if summary_file.exists():
        if state["next_episode"] != 20:
            raise ValueError("Summary precedes completed episodes")
        result = read_json(summary_file)
        if result != summarize_condition(directory, state, condition):
            raise ValueError("Completed summary differs from artifacts")
        return result
    for ep in range(state["next_episode"], episode_limit):
        if shutil.disk_usage(directory).free < 20 * 1024**3:
            raise RuntimeError("Less than 20 GiB free")
        start, cpu = time.perf_counter(), time.process_time()
        task = EpisodeTask(inputs[ep], condition["graph"], condition["mode"])
        batch = BatchEpisode(task, configs)
        prep = time.perf_counter() - start
        t = time.perf_counter()
        batch.run_until()
        learning = time.perf_counter() - t
        cells = task.encode(task.observations, bottleneck=False) if task.mode == "bottleneck" else batch.activities
        data = {"trace": batch.trace, "probes": batch.probes, "plus": batch.plus, "minus": batch.minus,
                "task_hash": np.array(task.digest()), "inputs_hash": np.array(inputs[ep].digest()),
                "config_ids": np.array([c.id for c in configs])}
        for prefix, activity in (("cell", cells), ("readout", batch.activities)):
            data.update({prefix + "_" + k: v for k, v in feature_statistics(activity).items()})
        target = directory / f"episode_{ep:02d}.npz"
        tmp = target.with_suffix(".npz.tmp")
        with tmp.open("wb") as file:
            np.savez_compressed(file, **data)
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp, target)
        state["artifacts"].append({"file": target.name, "sha256": sha256(target), "task_hash": task.digest()})
        state["next_episode"] = ep + 1
        for key, value in (("wall_seconds", time.perf_counter() - start), ("cpu_seconds", time.process_time() - cpu),
                           ("preprocessing_seconds", prep), ("learning_seconds", learning)):
            state["resources"][key] += value
        state["resources"]["peak_worker_memory_bytes"] = max(state["resources"]["peak_worker_memory_bytes"], peak_memory())
        atomic_json(checkpoint, state)
    if state["next_episode"] < 20:
        return state
    result = summarize_condition(directory, state, condition)
    atomic_json(summary_file, result)
    return result


def execute_block(output, stage, block, contract_hash):
    started = time.perf_counter()
    output = Path(output)
    directory = output / f"block_{block}"
    directory.mkdir(parents=True, exist_ok=True)
    base = load_base()
    inputs = [Inputs(stage, block, ep) for ep in range(20)]
    rows = []
    for index, condition in enumerate(conditions(base, stage, block)):
        if time.perf_counter() - started > 7 * 86400:
            raise RuntimeError("Seven-day block limit")
        if index % 10 == 0:
            retained = sum(p.stat().st_size for p in output.rglob("*") if p.is_file())
            if retained >= 10 * 1024**3:
                raise RuntimeError("10 GiB campaign artifact cap")
        configs = grid()
        if condition["size"] == 73 and condition["arm"] == "clone" and condition["mode"] == "full":
            configs += [Config("native", "frozen", 0., .2)]
        rows.append(execute_condition(directory, condition, inputs, configs, contract_hash))
        if (index + 1) % 10 == 0:
            print(json.dumps({"block": block, "conditions_complete": index + 1, "of": 80}), flush=True)
    result = {"block": block, "conditions": rows, "contract_sha256": contract_hash,
              "input_hashes": [i.digest() for i in inputs], "elapsed_seconds": time.perf_counter() - started}
    path = directory / "summary.json"
    if not path.exists():
        atomic_json(path, result)
    else:
        old = read_json(path)
        if old["conditions"] != rows or old["contract_sha256"] != contract_hash:
            raise ValueError("Completed block changed")
        result = old
    return result


def run(output, workers=3):
    from tools.audit_growth import verify
    verify()
    validation = json.loads((ROOT / "research/exp003_development_validation.json").read_text())
    if validation["status"] != "passed" or validation["code_snapshot"] != snapshot():
        raise ValueError("Development code is not validated")
    if workers not in (1, 2, 3):
        raise ValueError("Use 1..3 workers")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    contract = {"protocol": "EXP-003-development-1.0", "stage": "development", "blocks": list(range(100, 110)),
                "graph_replicates": 3, "episodes": 20, "conditions_per_block": 80,
                "grid": [asdict(c) for c in grid()], "code_snapshot": snapshot(), "environment": environment(),
                "source": load_base().provenance, "validation_sha256": sha256(ROOT / "research/exp003_development_validation.json"),
                "r03_sha256": sha256(ROOT / "research/exp003_validation.json"), "confirmation_authorized": False}
    contract_file = output / "contract.json"
    if contract_file.exists():
        if read_json(contract_file)["contract"] != contract:
            raise ValueError("Frozen development contract mismatch")
    else:
        atomic_json(contract_file, {"frozen_utc": now(), "contract": contract})
    contract_hash = sha256(contract_file)
    report_file = output / "report.json"
    if report_file.exists():
        report = read_json(report_file)
        if report["contract_sha256"] != contract_hash:
            raise ValueError("Completed report contract mismatch")
        print("Development already complete; use audit_growth_development.py to verify retained results")
        return report
    started, start_utc = time.perf_counter(), now()
    blocks = []
    try:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(execute_block, output, "development", block, contract_hash): block for block in range(100, 110)}
            for future in as_completed(futures):
                blocks.append(future.result())
                if time.perf_counter() - started > 7 * 86400:
                    raise RuntimeError("Seven-day campaign limit")
                print(json.dumps({"blocks_complete": len(blocks), "latest_block": futures[future]}), flush=True)
    except Exception as error:
        atomic_json(output / f"failure_{time.time_ns()}.json", {"created_utc": now(), "error": repr(error)})
        raise
    blocks.sort(key=lambda b: b["block"])
    selection = select_shared([b["conditions"] for b in blocks])
    selection.update({"frozen_utc": now(), "contract_sha256": contract_hash,
                      "selected": asdict(grid()[selection["index"]]), "confirmation_blocks_completed": 0,
                      "block_summary_sha256": {str(b["block"]): sha256(output / f"block_{b['block']}" / "summary.json") for b in blocks}})
    selected_path = output / "selection.json"
    if selected_path.exists():
        old = read_json(selected_path)
        if {k: v for k, v in old.items() if k != "frozen_utc"} != {k: v for k, v in selection.items() if k != "frozen_utc"}:
            raise ValueError("Frozen selection mismatch")
        selection = old
    else:
        atomic_json(selected_path, selection)
    all_rows = [r for b in blocks for r in b["conditions"]]
    report = {"status": "complete", "stage": "development", "blocks": 10, "conditions": len(all_rows),
              "episode_batches": len(all_rows) * 20, "configuration_episodes": sum(len(r["config_ids"]) * 20 for r in all_rows),
              "confirmation_blocks": 0, "excluded_episodes": 0, "numerical_failures": 0,
              "started_utc": start_utc, "completed_utc": now(), "contract_sha256": contract_hash,
              "selection_sha256": sha256(selected_path), "environment": environment(), "workers": workers,
              "wall_seconds_this_invocation": time.perf_counter() - started,
              "summed_condition_wall_seconds": sum(r["resources"]["wall_seconds"] for r in all_rows),
              "summed_worker_cpu_seconds": sum(r["resources"]["cpu_seconds"] for r in all_rows),
              "max_worker_peak_memory_bytes": max(r["resources"]["peak_worker_memory_bytes"] for r in all_rows),
              "retained_bytes_before_report": sum(p.stat().st_size for p in output.rglob("*") if p.is_file()),
              "limit": "Development selection and descriptive comparisons only; no H3 confirmation"}
    atomic_json(report_file, report)
    print(json.dumps({"status": "complete", "selected": selection["selected"], "resources": report}), flush=True)
    return report
