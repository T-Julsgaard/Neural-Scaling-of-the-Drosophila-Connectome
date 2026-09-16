"""Execute the prepared source-preserving author fixture in a supplied Octave CLI."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.campaign import text_hash
from exp002.data import sha256
from tools.prepare_bennett_reference import prepare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--octave", type=Path, required=True)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    executable = args.octave.resolve()
    if not executable.is_file():
        raise FileNotFoundError(executable)
    directory, manifest = prepare()
    flags = [str(executable), "--no-init-file", "--no-site-file", "--no-history", "--quiet"]
    calls = []
    for command in ([str(executable), "--version"], flags + ["run_reference.m"]):
        completed = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=120)
        calls.append({"command": command, "cwd": str(directory), "returncode": completed.returncode,
                      "stdout": completed.stdout, "stderr": completed.stderr})
        if completed.returncode != 0:
            (directory / "runtime_failure.json").write_text(json.dumps(calls, indent=2) + "\n")
            raise RuntimeError("Author runtime failed: " + completed.stderr)
    version = calls[0]["stdout"].splitlines()[0]
    command = [sys.executable, str(ROOT / "tools/compare_bennett_reference.py"),
               str(directory / "author_trace.csv"), "--runtime", version]
    comparison = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
    calls.append({"command": command, "cwd": str(ROOT), "returncode": comparison.returncode,
                  "stdout": comparison.stdout, "stderr": comparison.stderr})
    log = directory / "runtime_execution.json"
    log.write_text(json.dumps({"created_utc": datetime.now(timezone.utc).isoformat(),
                              "calls": calls}, indent=2) + "\n", encoding="utf-8")
    numerical = json.loads((ROOT / "research/exp002_author_comparison.json").read_text())
    evidence = [log, directory / "preparation.json", directory / "author_trace.csv",
                directory / "mb_mv_a_fixture.m", directory / "run_reference.m",
                ROOT / "research/exp002_author_comparison.json"]
    evidence += [directory / name for name in ("activities.csv", "choices.csv", "rewards.csv", "initial_plus.csv", "initial_minus.csv")]
    report = {"created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if comparison.returncode == 0 and numerical["status"] == "passed" else "failed",
        "runtime_executed": True, "runtime_version": version, "runtime_executable": str(executable),
        "runtime_executable_sha256": sha256(executable),
        "runtime_download_source": "https://ftp.gnu.org/gnu/octave/windows/octave-11.3.0-w64.zip",
        "runtime_archive_sha256": sha256(args.archive) if args.archive else None,
        "source_commit": manifest["source_commit"], "source_sha256": manifest["source_sha256"],
        "maximum_absolute_error": numerical["maximum_absolute_error"], "tolerance": numerical["tolerance"],
        "checked_code_sha256": {p: text_hash(ROOT / p) for p in (
            "exp002/rules.py", "tests/decimal_reference.py", "tests/test_exp002.py",
            "tests/fixtures/bennett_eq8_256.json", "tools/prepare_bennett_reference.py",
            "tools/compare_bennett_reference.py", "tools/run_bennett_reference.py")},
        "evidence_sha256": {p.relative_to(ROOT).as_posix(): sha256(p) for p in evidence},
        "scope": "256 supplied-input author eq8 updates; source DAN/update arithmetic preserved",
        "limit": "Equation-level author-runtime validation, not reproduction of the paper's figures or biological findings"}
    (ROOT / "research/exp002_r02_runtime.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "runtime_version", "maximum_absolute_error", "scope")}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
