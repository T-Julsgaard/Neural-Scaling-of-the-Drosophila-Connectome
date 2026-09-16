"""Bounded baseline execution, immutable artifacts and block-level inference."""
from dataclasses import asdict
from datetime import datetime, timezone
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import time

import numpy as np

from .baseline import (BatchEpisode, Config, STAGES, Task, block_metrics, development_configs,
                       feature_statistics, feature_summary, interval, select_configs)
from .data import ROOT, load_projection, sha256


def now():
    return datetime.now(timezone.utc).isoformat()


def text_hash(path):
    return hashlib.sha256(Path(path).read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def snapshot():
    files = [*ROOT.glob("exp002/*.py"), ROOT / "tests/test_baseline.py",
             ROOT / "tools/run_baseline.py", ROOT / "experiments/EXP-002-baseline-protocol.md"]
    return {p.relative_to(ROOT).as_posix(): text_hash(p) for p in sorted(files)}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(value, sort_keys=True, allow_nan=False)
    envelope = {"sha256": hashlib.sha256(serialized.encode()).hexdigest(), "payload": value}
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(envelope, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_json(path):
    envelope = json.loads(Path(path).read_text(encoding="utf-8"))
    p = envelope["payload"]
    if hashlib.sha256(json.dumps(p, sort_keys=True, allow_nan=False).encode()).hexdigest() != envelope["sha256"]:
        raise ValueError("Checkpoint digest mismatch: " + str(path))
    return p


def environment():
    return {"python": platform.python_version(), "numpy": np.__version__, "os": platform.platform(),
            "processor": platform.processor(), "logical_cpus": os.cpu_count(),
            "machine_role": "current_session_not_colleague_target", "executable": os.sys.executable}


def peak_memory():
    if os.name == "nt":
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (n, ctypes.c_size_t) for n in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        c = Counters()
        c.cb = ctypes.sizeof(c)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(c), c.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(c.PeakWorkingSetSize)
    import resource
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if platform.system() == "Darwin" else 1024))


def verify_gates():
    validation = json.loads((ROOT / "research/exp002_baseline_validation.json").read_text())
    if validation["status"] != "passed" or validation["code_snapshot"] != snapshot():
        raise ValueError("Current baseline implementation is not validated")
    r02 = json.loads((ROOT / "research/exp002_r02_runtime.json").read_text())
    if r02["status"] != "passed" or not r02["runtime_executed"]:
        raise ValueError("R02 runtime gate unresolved")
    for name, digest in r02["checked_code_sha256"].items():
        if text_hash(ROOT / name) != digest:
            raise ValueError("R02 checked code changed")
    for name, digest in r02["evidence_sha256"].items():
        if sha256(ROOT / name) != digest:
            raise ValueError("R02 evidence changed")


def execute_block(output, stage, block, configs, contract, episode_limit=20):
    """Checkpoint at reset boundaries; deterministic restart of an interrupted episode."""
    if not 0 <= episode_limit <= 20:
        raise ValueError("Invalid episode limit")
    directory = Path(output) / f"block_{block}"
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / "checkpoint.json"
    projection, _ = load_projection()
    state = {"contract": contract, "block": block, "stage": stage, "next_episode": 0,
             "artifacts": [], "wall_seconds": 0., "cpu_seconds": 0., "peak_working_set_bytes": 0,
             "preprocessing_seconds": 0., "learning_and_probe_seconds": 0.,
             "boundary": "reset before next episode; RNG streams derived from stage/block/episode"}
    if checkpoint.exists():
        state = read_json(checkpoint)
        if state["contract"] != contract or state["stage"] != stage or state["block"] != block:
            raise ValueError("Resume contract mismatch")
        if state["next_episode"] != len(state["artifacts"]):
            raise ValueError("Checkpoint chronology mismatch")
        for artifact in state["artifacts"]:
            if sha256(directory / artifact["file"]) != artifact["sha256"]:
                raise ValueError("Completed episode artifact changed")
    for ep in range(state["next_episode"], episode_limit):
        if shutil.disk_usage(directory).free < 20 * 1024**3:
            raise RuntimeError("Storage guard: less than 20 GiB free")
        retained = sum(p.stat().st_size for p in Path(output).rglob("*") if p.is_file())
        if retained >= 10 * 1024**3:
            raise RuntimeError("Storage guard: 10 GiB artifact cap")
        if state["wall_seconds"] >= 7 * 86400:
            raise RuntimeError("Elapsed budget exceeded")
        start, cpu_start = time.perf_counter(), time.process_time()
        task = Task(projection, stage, block, ep)
        prep, learning = time.perf_counter() - start, 0.
        data = {}
        ordered_trace, ordered_probes = {}, {}
        for rep in ("native", "pn"):
            local = [c for c in configs if c.representation == rep]
            if not local:
                continue
            timer = time.perf_counter()
            episode = BatchEpisode(task, local)
            prep += time.perf_counter() - timer
            timer = time.perf_counter()
            episode.run_until()
            learning += time.perf_counter() - timer
            for i, c in enumerate(local):
                ordered_trace[c.id], ordered_probes[c.id] = episode.trace[i], episode.probes[i]
            data[rep + "_plus"], data[rep + "_minus"] = episode.plus, episode.minus
            for key, value in feature_statistics(episode.activities).items():
                data[rep + "_feature_" + key] = value
        data["trace"] = np.array([ordered_trace[c.id] for c in configs])
        data["probes"] = np.array([ordered_probes[c.id] for c in configs])
        data["task_hash"] = np.array(task.digest())
        data["config_ids"] = np.array([c.id for c in configs])
        file = directory / f"episode_{ep:02d}.npz"
        tmp = file.with_suffix(".npz.tmp")
        with tmp.open("wb") as f:
            np.savez_compressed(f, **data)
            f.flush()
            os.fsync(f.fileno())
        # A crash after artifact write but before checkpoint safely replays this episode.
        os.replace(tmp, file)
        state["artifacts"].append({"file": file.name, "sha256": sha256(file), "task_hash": task.digest()})
        state["next_episode"] = ep + 1
        state["wall_seconds"] += time.perf_counter() - start
        state["cpu_seconds"] += time.process_time() - cpu_start
        state["preprocessing_seconds"] += prep
        state["learning_and_probe_seconds"] += learning
        state["peak_working_set_bytes"] = max(state["peak_working_set_bytes"], peak_memory())
        state["last_boundary_state"] = {"artifact": file.name, "trial": 384,
            "next_episode_weights": .1, "live_rng": None,
            "seed_template": [2, STAGES[stage][0], block, 0, "component", ep + 1]}
        atomic_json(checkpoint, state)
    if state["next_episode"] < 20:
        return state
    traces, probes, statistics = [], [], {}
    for a in state["artifacts"]:
        with np.load(directory / a["file"], allow_pickle=False) as f:
            traces.append(f["trace"])
            probes.append(f["probes"])
            for rep in {c.representation for c in configs}:
                local = statistics.setdefault(rep, {})
                for key in ("count", "sum", "gram", "active"):
                    value = f[rep + "_feature_" + key]
                    local[key] = local.get(key, 0) + value
    metrics = block_metrics(traces, probes)
    result = {"block": block, "config_ids": [c.id for c in configs], "metrics": metrics,
              "features": {k: feature_summary(v) for k, v in statistics.items()},
              "resources": {k: state[k] for k in ("wall_seconds", "cpu_seconds", "peak_working_set_bytes",
                                                "preprocessing_seconds", "learning_and_probe_seconds")}}
    atomic_json(directory / "summary.json", result)
    return result


def summarize(blocks, configs, stage):
    summaries = {}
    for i, config in enumerate(configs):
        row = {}
        for metric in blocks[0]["metrics"]:
            values = [b["metrics"][metric][i] for b in blocks]
            if metric.endswith("curve"):
                row[metric] = np.mean(values, axis=0).tolist()
            else:
                row[metric] = interval(values, stage)
        summaries[config.id] = row
    return summaries


def run_stage(stage, output, selection_path=None):
    if stage not in ("development", "confirmation"):
        raise ValueError("Use tests for validation")
    verify_gates()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    selection = read_json(selection_path) if selection_path else None
    if stage == "development":
        if selection is not None:
            raise ValueError("Development may not use a selected configuration")
        configs = development_configs()
    else:
        if selection is None or not selection["provisional_adequacy"]:
            raise ValueError("Confirmation requires adequate frozen development selection")
        if selection["code_snapshot"] != snapshot():
            raise ValueError("Code changed since development selection")
        configs = [Config("native", "frozen", 0., .2)] + [Config(**v) for v in selection["selected"].values()]
        configs += [Config("native", arm, .001, .2) for arm in ("feedback", "delta", "reward_only")]
        configs = list({c.id: c for c in configs}.values())
    _, provenance = load_projection()
    contract = {"schema_version": 1, "stage": stage, "configs": [asdict(c) for c in configs],
                "code_snapshot": snapshot(), "projection": provenance, "environment": environment(),
                "selection_sha256": sha256(selection_path) if selection_path else None,
                "r02_report_sha256": sha256(ROOT / "research/exp002_r02_runtime.json"),
                "validation_report_sha256": sha256(ROOT / "research/exp002_baseline_validation.json")}
    contract_file = output / "contract.json"
    if contract_file.exists():
        if read_json(contract_file)["contract"] != contract:
            raise ValueError("Frozen campaign contract mismatch; use a new output directory")
    else:
        atomic_json(contract_file, {"frozen_utc": now(), "contract": contract})
    blocks = []
    try:
        for seed in STAGES[stage][1]:
            blocks.append(execute_block(output, stage, seed, configs, contract))
            elapsed = sum(b["resources"]["wall_seconds"] for b in blocks)
            if elapsed >= 7 * 86400:
                raise RuntimeError("Seven-day campaign budget exceeded")
            print(json.dumps({"stage": stage, "block_completed": seed, "active_seconds": round(elapsed, 2)}), flush=True)
    except Exception as e:
        atomic_json(output / "failure.json", {"created_utc": now(), "type": type(e).__name__, "error": str(e)})
        raise
    summary = summarize(blocks, configs, stage)
    resources = {key: sum(b["resources"][key] for b in blocks) for key in (
        "wall_seconds", "cpu_seconds", "preprocessing_seconds", "learning_and_probe_seconds")}
    resources.update({"peak_working_set_bytes": max(b["resources"]["peak_working_set_bytes"] for b in blocks),
        "inference_trials": len(blocks) * len(configs) * 20 * 384,
        "learning_updates": len(blocks) * sum(c.arm != "frozen" for c in configs) * 20 * 384,
        "probe_presentations": len(blocks) * len(configs) * 20 * 5 * 32,
        "artifact_bytes_before_summary": sum(p.stat().st_size for p in output.rglob("*") if p.is_file()),
        "native_dimensions": {"PN": 40, "KC": 73, "outputs": 2, "trainable_weights": 146,
                              "projection_edges": provenance["edges"], "contacts": provenance["contacts"]},
        "direct_PN_dimensions": {"PN": 40, "outputs": 2, "trainable_weights": 80},
        "time_scope": "episode preprocessing, batched learning, probes and artifact writes; no per-arm timing claim",
        "energy_joules": None})
    if stage == "development":
        scores = {k: v["selection_score"]["mean"] for k, v in summary.items()}
        selected = select_configs(configs, scores)
        feedback, delta = Config(**selected["native_feedback"]), Config(**selected["native_delta"])
        candidate = feedback if scores[feedback.id] - scores[delta.id] > .02 else delta
        candidate_row = summary[candidate.id]
        adequate = candidate_row["acquisition"]["interval"][0] > .65 and min(
            candidate_row["early_reversal"]["mean"], candidate_row["retention_after"]["mean"]) < .9
        selection = {"created_utc": now(), "selected": selected, "structural_candidate": asdict(candidate),
                     "provisional_adequacy": bool(adequate), "code_snapshot": snapshot(),
                     "development_contract_sha256": sha256(contract_file),
                     "development_block_summaries": {str(b["block"]): sha256(output / f"block_{b['block']}" / "summary.json") for b in blocks},
                     "limit": "Selection and adequacy on development data are provisional; no H2 inference"}
        atomic_json(output / "selection.json", selection)
        conclusions = {"provisional_adequacy": bool(adequate), "structural_candidate": candidate.id}
    else:
        ids = {k: Config(**v).id for k, v in selection["selected"].items()}
        def contrast(a, b, metric, coverage=.95):
            return interval(np.array(summary[ids[a]][metric]["block_values"]) -
                            np.array(summary[ids[b]][metric]["block_values"]), stage, coverage)
        primary = contrast("native_feedback", "native_reward_only", "early_reversal", .9833)
        acquisition = contrast("native_feedback", "native_reward_only", "acquisition")
        delta = contrast("native_feedback", "native_delta", "early_reversal")
        candidate = Config(**selection["structural_candidate"])
        row = summary[candidate.id]
        adequate = row["acquisition"]["interval"][0] > .65 and min(
            row["early_reversal"]["mean"], row["retention_after"]["mean"]) < .9
        lo, hi = primary["interval"]
        conclusions = {"primary_feedback_minus_reward_only": primary,
            "H2": "supported" if lo > .05 else "useful_benefit_ruled_out_in_this_assay" if hi < .05 else "inconclusive",
            "acquisition_feedback_minus_reward_only": acquisition,
            "acquisition_noninferiority": acquisition["interval"][0] > -.02,
            "feedback_minus_delta_reversal": delta,
            "feedback_delta_equivalent_within_0_02": delta["interval"][0] >= -.02 and delta["interval"][1] <= .02,
            "adequate_for_structural_experiments": bool(adequate), "structural_candidate": candidate.id}
    report = {"created_utc": now(), "stage": stage, "status": "complete", "blocks": len(blocks),
        "episodes_per_block": 20, "configs": [asdict(c) for c in configs], "summary": summary,
        "conclusions": conclusions, "resources": resources, "environment": environment(),
        "features_by_block": {str(b["block"]): b["features"] for b in blocks},
        "contract_sha256": sha256(contract_file),
        "limits": ["Single larval-derived feedforward circuit with synthetic outputs", "Two related task families",
                   "Block bootstrap quantifies task randomness, not independent animal replication",
                   "No whole-brain, biological superiority, broad cognition or growth result"]}
    atomic_json(output / "report.json", report)
    print(json.dumps({"stage": stage, "conclusions": conclusions, "resources": resources}), flush=True)
    return report
