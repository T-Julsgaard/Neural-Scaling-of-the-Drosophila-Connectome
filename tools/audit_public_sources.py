"""Capture small public repository metadata and immutable source references.

This audits research dependencies; it installs nothing and runs no experiments.
"""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPOS = {
    "flyvis": "TuragaLab/flyvis",
    "flygym": "NeLy-EPFL/flygym",
    "shiu": "philshiu/Drosophila_brain_model",
    "conn2res": "netneurolab/conn2res",
    "flywire_annotations": "flyconnectome/flywire_annotations",
    "neurotransmitters": "flyconnectome/drosophila_neurotransmitters",
    "flybody": "TuragaLab/flybody",
    "topology_sensitivity": "nalin-dhiman/Connectome-Constrained-Neural-Networks",
    "bennett": "BrainsOnBoard/paper_RPEs_in_drosophila_mb",
    "xie": "kxie2022/mushroom-body-research",
    "neurogym": "neurogym/neurogym",
}

def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Connectome-Research-Foundation/0.1"})
    with urllib.request.urlopen(request, timeout=25) as response:
        data = response.read(5_000_001)
    if len(data) > 5_000_000:
        raise ValueError("Metadata response exceeds 5 MB limit")
    return json.loads(data)

def audit(item):
    name, repo = item
    record = {"id": name, "repository": repo, "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        meta = get("https://api.github.com/repos/" + repo)
        for field in ("html_url", "default_branch", "pushed_at", "archived", "license"):
            record[field] = meta.get(field)
        commit = get("https://api.github.com/repos/" + repo + "/commits/" + meta["default_branch"])
        record["commit"] = commit["sha"]
        tree = get("https://api.github.com/repos/" + repo + "/git/trees/" + commit["sha"] + "?recursive=1")
        record["files"] = [{"path": f["path"], "sha": f["sha"], "size": f.get("size")} for f in tree.get("tree", []) if f["type"] == "blob"]
        record["tree_truncated"] = tree.get("truncated", False)
        record["status"] = "metadata_verified"
    except Exception as error:
        record["status"] = "unresolved"
        record["error"] = f"{type(error).__name__}: {error}"
    return record

def main():
    output = ROOT / "research" / "software_metadata.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(audit, REPOS.items()))
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    for record in records:
        print(record["id"], record["status"], record.get("commit", record.get("error")))

if __name__ == "__main__":
    main()
