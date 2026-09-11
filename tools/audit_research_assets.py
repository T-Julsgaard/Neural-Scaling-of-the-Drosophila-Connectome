"""Download bounded public source material for inspection, never execute it."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "flyvis": ["readme.md", "pyproject.toml", "flyvis/connectome/connectome.py", "flyvis/connectome/fib25-fib19_v2.2.json", "flyvis/network/dynamics.py"],
    "flygym": ["README.md", "pyproject.toml"],
    "shiu": ["Readme.md", "model.py"],
    "conn2res": ["README.rst", "conn2res/reservoir.py", "pyproject.toml"],
    "flybody": ["README.md", "pyproject.toml"],
    "flywire_annotations": ["README.md"],
    "neurotransmitters": ["README.md"],
    "topology_sensitivity": ["README.md", "configs/stage3_canonical_config.json"],
    "bennett": ["README", "mb_mv_a.m", "mb_vs.m", "mb_reward_schedules.m"],
}

def fetch(item):
    name, url = item
    path = ROOT / ".cache" / "research_assets" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"name": name, "url": url}
    try:
        if path.exists():
            data = path.read_bytes()
            record.update(status="downloaded_for_inspection", bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            return record
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Connectome-Research-Foundation/0.1"}), timeout=35) as response:
            data = response.read(20_000_001)
        if len(data) > 20_000_000:
            raise ValueError("Response exceeds 20 MB limit")
        path.write_bytes(data)
        record.update(status="downloaded_for_inspection", bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as error:
        record.update(status="unresolved", error=f"{type(error).__name__}: {error}")
    return record

def main():
    repos = json.loads((ROOT / "research/software_metadata.json").read_text())
    tasks = []
    for repo in repos:
        if repo.get("commit"):
            tasks.extend((repo["id"] + "/" + path, f'https://raw.githubusercontent.com/{repo["repository"]}/{repo["commit"]}/{path}') for path in FILES.get(repo["id"], []))
    tasks.extend([
        ("fafb_downloads.json", "https://codex.flywire.ai/api/download?dataset=fafb"),
        ("banc_downloads.json", "https://codex.flywire.ai/api/download?dataset=banc"),
        ("xie2025.pdf", "https://arxiv.org/pdf/2509.19351"),
        ("bennett2021.html", "https://www.nature.com/articles/s41467-021-22592-4"),
        ("elkahlah2020.html", "https://elifesciences.org/articles/52278"),
        ("dambre2012.html", "https://www.nature.com/articles/srep00514"),
        ("eichler_matrix.zip", "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnature23455/MediaObjects/41586_2017_BFnature23455_MOESM3_ESM.zip"),
    ])
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, tasks))
    (ROOT / "research/asset_audit.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    for record in records:
        print(record["name"], record["status"], record.get("bytes", record.get("error")))

if __name__ == "__main__":
    main()
