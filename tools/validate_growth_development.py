"""Validate the fresh development runner on stage-zero inputs before freezing."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.campaign import environment, now
from exp003.campaign import snapshot
from tools.audit_growth import verify


if __name__ == "__main__":
    verify()
    if (ROOT / "results/exp003_development/contract.json").exists():
        raise SystemExit("Do not replace validation evidence after development freeze")
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT)))
    report = {"status": "passed" if result.wasSuccessful() and not result.skipped else "failed",
              "created_utc": now(), "tests_run": result.testsRun,
              "failures": [{"test": str(t), "traceback": tb} for t, tb in result.errors + result.failures],
              "skipped": [str(t) for t, _ in result.skipped], "code_snapshot": snapshot(), "environment": environment(),
              "scope": "Stage-zero implementation validation; no development/confirmation inputs"}
    (ROOT / "research/exp003_development_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("status", "tests_run", "failures")}))
    raise SystemExit(report["status"] != "passed")
