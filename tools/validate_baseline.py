"""Validate new baseline machinery on stage-zero tasks only."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.campaign import environment, now, snapshot


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"created_utc": now(), "status": "passed" if result.wasSuccessful() else "failed",
        "tests_run": result.testsRun, "failures": [{"test": str(t), "traceback": tb} for t, tb in result.failures + result.errors],
        "skipped": [{"test": str(t), "reason": reason} for t, reason in result.skipped],
        "code_snapshot": snapshot(), "environment": environment(),
        "scope": "Implementation tests, stage 0 seeds 0..4; no scientific campaign results"}
    (ROOT / "research/exp002_baseline_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "tests_run", "failures")}))
    raise SystemExit(not result.wasSuccessful())
