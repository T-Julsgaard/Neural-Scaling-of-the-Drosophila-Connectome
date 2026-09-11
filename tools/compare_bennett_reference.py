"""Compare an externally generated author trace. Never infer runtime provenance."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from tests.test_exp002 import FIXTURE_PATH, fixture_trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--runtime", required=True, help="Actual runtime and version used to generate the trace")
    parser.add_argument("--report", type=Path, default=ROOT / "research/exp002_author_comparison.json")
    args = parser.parse_args()
    fixture = json.loads(FIXTURE_PATH.read_text())
    rows = fixture_trace(fixture)
    expected = np.array([r["values"] + [r["d_plus"], r["d_minus"]] + r["plus"] + r["minus"] for r in rows])
    actual = np.loadtxt(args.trace, delimiter=",")
    if actual.shape != (256, 44) or not np.isfinite(actual).all():
        raise ValueError("Author trace must contain 256 finite rows of q(2), d(2), post-update weights(40)")
    error = float(np.max(abs(actual-expected)))
    report = {"kind": "provided_author_trace_comparison", "status": "passed" if error <= 1e-10 else "failed",
              "maximum_absolute_error": error, "tolerance": 1e-10, "runtime_reported_by_operator": args.runtime,
              "trace_sha256": hashlib.sha256(args.trace.read_bytes()).hexdigest(),
              "fixture_sha256": hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest(),
              "limit": "Numerical comparison alone does not authenticate author runtime execution; retain generation log and preparation manifest."}
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    return 0 if error <= 1e-10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
