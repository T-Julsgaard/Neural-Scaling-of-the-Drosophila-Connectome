"""Audit retained baseline artifacts and emit a compact scientific run record."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from exp002.baseline import Config, STAGES, block_metrics
from exp002.campaign import read_json, snapshot, verify_gates, now
from exp002.data import sha256


def main():
    verify_gates()
    base = ROOT / "results/exp002_baseline"
    frozen_evidence = base / "validation_evidence"
    frozen_evidence.mkdir(exist_ok=True)
    for name in ("exp002_baseline_validation.json", "exp002_r02_runtime.json"):
        if not (frozen_evidence / name).exists():
            shutil.copyfile(ROOT / "research" / name, frozen_evidence / name)
    stages, files = {}, {}
    for stage in ("development", "confirmation"):
        directory = base / stage
        frozen = read_json(directory / "contract.json")
        contract = frozen["contract"]
        if contract["validation_report_sha256"] != sha256(frozen_evidence / "exp002_baseline_validation.json"):
            raise ValueError("Frozen validation evidence changed")
        if contract["r02_report_sha256"] != sha256(frozen_evidence / "exp002_r02_runtime.json"):
            raise ValueError("Frozen R02 evidence changed")
        if contract["code_snapshot"] != snapshot():
            raise ValueError("Frozen code changed")
        report = read_json(directory / "report.json")
        if report["contract_sha256"] != sha256(directory / "contract.json"):
            raise ValueError("Report/contract mismatch")
        if report["status"] != "complete" or report["blocks"] != len(STAGES[stage][1]):
            raise ValueError("Incomplete stage")
        configs = [Config(**c) for c in contract["configs"]]
        for block in STAGES[stage][1]:
            folder = directory / f"block_{block}"
            state, summary = read_json(folder / "checkpoint.json"), read_json(folder / "summary.json")
            if state["contract"] != contract or state["next_episode"] != 20 or len(state["artifacts"]) != 20:
                raise ValueError("Invalid block checkpoint")
            traces, probes = [], []
            for ep, artifact in enumerate(state["artifacts"]):
                if artifact["file"] != f"episode_{ep:02d}.npz":
                    raise ValueError("Episode chronology mismatch")
                file = folder / artifact["file"]
                if sha256(file) != artifact["sha256"]:
                    raise ValueError("Episode hash mismatch")
                with np.load(file, allow_pickle=False) as f:
                    if list(f["config_ids"]) != [c.id for c in configs] or str(f["task_hash"]) != artifact["task_hash"]:
                        raise ValueError("Episode identity mismatch")
                    t, p = f["trace"], f["probes"]
                    if not np.isfinite(t).all() or not np.isfinite(p).all():
                        raise ValueError("Nonfinite scientific artifact")
                    if not np.isin(t[:, :, 1], [0, 1]).all() or not np.isin(t[:, :, 2], [-1, 1]).all():
                        raise ValueError("Invalid actions/rewards")
                    if ((t[:, :, 0] < 0) | (t[:, :, 0] > 1)).any() or ((p < 0) | (p > 1)).any():
                        raise ValueError("Invalid probabilities")
                    for i, c in enumerate(configs):
                        if c.arm == "frozen" and (not np.all(t[i, :, 0] == .5) or not np.all(p[i] == .5)):
                            raise ValueError("Frozen control is not chance")
                    traces.append(t)
                    probes.append(p)
            computed = block_metrics(traces, probes)
            if computed != summary["metrics"]:
                raise ValueError("Metrics do not match retained traces")
        stages[stage] = {"status": report["status"], "blocks": report["blocks"],
            "episodes_per_block": 20, "configurations": report["configs"], "resources": report["resources"],
            "conclusions": report["conclusions"], "environment": report["environment"],
            "frozen_utc": frozen["frozen_utc"], "finished_utc": report["created_utc"],
            "report": (directory / "report.json").relative_to(ROOT).as_posix()}
    selection = read_json(base / "development/selection.json")
    confirmation_contract = read_json(base / "confirmation/contract.json")["contract"]
    if confirmation_contract["selection_sha256"] != sha256(base / "development/selection.json"):
        raise ValueError("Confirmation did not use retained selection")
    for block, digest in selection["development_block_summaries"].items():
        if sha256(base / f"development/block_{block}/summary.json") != digest:
            raise ValueError("Selection provenance changed")
    for path in sorted(base.rglob("*")):
        if path.is_file():
            files[path.relative_to(ROOT).as_posix()] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    report = {"schema_version": 1, "run_id": "EXP-002-baseline-v1.1", "experiment": "EXP-002",
        "protocol": "experiments/EXP-002-baseline-protocol.md", "status": "completed", "audited_utc": now(),
        "code_base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "code_state": "uncommitted implementation identified by exact normalized source hashes",
        "code_snapshot": snapshot(), "R02": "passed_author_runtime_equation_comparison",
        "R02_report": "research/exp002_r02_runtime.json", "implementation_validation": "research/exp002_baseline_validation.json",
        "stages": stages, "excluded_episodes": 0, "numerical_failures": 0,
        "artifact_count": len(files), "artifact_bytes": sum(v["bytes"] for v in files.values()), "files": files,
        "interpretation": "Validated and measured synthetic-task learning baseline; see results report for hypothesis and adequacy decisions",
        "next_action": "Validate controlled structural operators for EXP-003 using the frozen native delta baseline; do not tune on EXP-002 confirmation outcomes",
        "limits": ["Single larval-derived circuit, two synthetic outputs, two related task families",
                   "No biological superiority, broad intelligence, growth or evolution demonstrated",
                   "Resources measured on current session CPU, not colleague target",
                   "Large per-trial NPZ artifacts retained locally and reconstructable; excluded from default Git snapshot"]}
    output = ROOT / "research/runs/EXP-002-baseline.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "artifact_count", "artifact_bytes", "excluded_episodes", "numerical_failures")}))


if __name__ == "__main__":
    main()
