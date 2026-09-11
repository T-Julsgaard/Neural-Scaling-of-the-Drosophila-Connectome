"""Retrieve only the two pinned public inputs needed for EXP-002 validation."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    assets = json.loads((ROOT / "research/asset_audit.json").read_text())
    for name in ("eichler_matrix.zip", "bennett/mb_mv_a.m"):
        asset = next(a for a in assets if a["name"] == name)
        target = ROOT / ".cache/research_assets" / name
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == asset["sha256"]:
            print(name + ": cached hash verified")
            continue
        with urllib.request.urlopen(asset["url"], timeout=60) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000 or hashlib.sha256(data).hexdigest() != asset["sha256"]:
            raise ValueError("Refusing mismatched/oversized source: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print(name + ": downloaded hash verified")


if __name__ == "__main__":
    main()
