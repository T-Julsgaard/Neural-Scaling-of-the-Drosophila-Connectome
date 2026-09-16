"""Freeze/resume and run EXP-003 development; confirmation is deliberately unavailable."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    from exp003.campaign import run
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/exp003_development")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    run(args.output, args.workers)
