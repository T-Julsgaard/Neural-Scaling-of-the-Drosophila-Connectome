"""Audited episode engine adapted from the immutable EXP-003 implementation."""
from dataclasses import asdict
import os
import json
from pathlib import Path
import shutil
import time
import numpy as np
from exp002.baseline import BatchEpisode, Config, block_metrics, feature_statistics, feature_summary
from exp002.campaign import atomic_json, read_json, peak_memory
from exp002.data import sha256
from exp003.growth import load_base
from .inputs import EpisodeTask, Inputs, conditions, grid


def retained_bytes(output):
    """Concurrent atomic renames may remove a path between enumeration and stat."""
    total = 0
    for path in Path(output).rglob('*'):
        try:
            if path.is_file():
                total += path.stat().st_size
        except FileNotFoundError:
            continue
    return total

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
            "readout_weights": 64 if condition["mode"].startswith("bottleneck") else 2 * condition["size"],
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
        cells = task.encode(task.observations, bottleneck=False) if task.mode.startswith("bottleneck") else batch.activities
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
            retained = retained_bytes(output)
            if retained >= 10 * 1024**3:
                raise RuntimeError("10 GiB campaign artifact cap")
        configs = grid()
        if condition["size"] == 73 and condition["arm"] == "clone" and condition["mode"].startswith("full"):
            configs += [Config("native", "frozen", 0., .2)]
        rows.append(execute_condition(directory, condition, inputs, configs, contract_hash))
        if (index + 1) % 10 == 0:
            print(json.dumps({"block": block, "conditions_complete": index + 1, "of": 28}), flush=True)
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


