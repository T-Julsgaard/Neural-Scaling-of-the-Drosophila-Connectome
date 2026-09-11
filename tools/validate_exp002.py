"""Run bounded validation fixtures and write compact evidence, never a pilot."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from tests.test_exp002 import EVIDENCE, FIXTURE_PATH, fixture_trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "research/exp002_validation.json")
    args = parser.parse_args()
    EVIDENCE.clear()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_exp002.py", top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    files = sorted([*ROOT.glob("exp002/*.py"), *ROOT.glob("tests/*.py"), *ROOT.glob("tests/fixtures/*.json"),
                    ROOT / "tools/validate_exp002.py", ROOT / "tools/prepare_bennett_reference.py",
                    ROOT / "tools/compare_bennett_reference.py", ROOT / "tools/fetch_validation_assets.py",
                    ROOT / "requirements-validation.txt", ROOT / "BENCHMARK_SPEC.md", ROOT / "experiments/EXP-002.md",
                    ROOT / "research/reference_data_audit.json", ROOT / "research/asset_audit.json"])
    if result.wasSuccessful():
        trace_path = ROOT / "results/validation/exp002_equation_trace.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(json.dumps({"kind": "python_adaptation_trace_not_author_runtime",
            "fixture": json.loads(FIXTURE_PATH.read_text()),
            "trace": fixture_trace(json.loads(FIXTURE_PATH.read_text()))}, indent=2, allow_nan=False) + "\n")
        EVIDENCE["retained_trace"] = {"path": str(trace_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(), "bytes": trace_path.stat().st_size}
    report = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "kind": "bounded_implementation_validation_not_scientific_confirmation", "experiment": "EXP-002",
        "status": "passed" if result.wasSuccessful() else "failed", "tests_run": result.testsRun,
        "failures": [{"test": str(t), "traceback": tb} for t, tb in result.failures + result.errors],
        "skipped": [{"test": str(t), "reason": r} for t, r in result.skipped],
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(),
                        "environment_kind": "project venv inheriting pinned bundled NumPy; not a clean install validation",
                        "machine_role": "current_session_not_verified_target"},
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "code_snapshot_hashing": "UTF-8 text with universal newlines normalized to LF",
        "code_snapshot_sha256": {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_text(encoding="utf-8").encode("utf-8")).hexdigest() for p in files},
        "author_runtime": {name: shutil.which(name) for name in ("octave-cli", "octave", "matlab")},
        "author_code_reproduction": "not_run", "independent_reviewer": "not_performed",
        "adaptation_validation": "automated_checks_passed_review_pending" if result.wasSuccessful() else "failed",
        "target_pilot": "skipped_by_user", "development_blocks": 0, "confirmation_blocks": 0,
        "evidence": EVIDENCE,
        "limits": ["No author MATLAB execution or independent person/agent review",
                   "Toy/episode checks are validation data, not H2 evidence or a larval assay adequacy result",
                   "No target hardware benchmark, resource promise, development sweep or confirmation campaign",
                   "Checkpoint is for a bounded episode; campaign scheduling/resource counters remain unimplemented"]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("status", "tests_run", "author_code_reproduction", "target_pilot")}))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
