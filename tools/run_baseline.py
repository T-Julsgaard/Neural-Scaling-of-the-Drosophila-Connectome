"""Run the prespecified EXP-002 baseline with validated code and frozen inputs."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.campaign import run_stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("development", "confirmation"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--selection", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / "results/exp002_baseline" / args.stage
    selection = args.selection
    if args.stage == "confirmation" and selection is None:
        selection = ROOT / "results/exp002_baseline/development/selection.json"
    run_stage(args.stage, output, selection)


if __name__ == "__main__":
    main()
