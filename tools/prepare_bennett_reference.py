"""Prepare a deterministic wrapper around hash-verified author code.

Does not run MATLAB/Octave. Generated modified GPL source is retained in the
private project's validation snapshot with attribution. Original source is unchanged.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np

SOURCE_HASH = "eaaf1641d19e225a84a022ae8d0ebbfafecdfe99cb8ea9f4fa9b58ce4a9aa1f6"


def prepare(output=None):
    source = ROOT / ".cache/research_assets/bennett/mb_mv_a.m"
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_HASH:
        raise ValueError("Pinned author source hash mismatch")
    text = source.read_text()
    fixture = json.loads((ROOT / "tests/fixtures/bennett_eq8_256.json").read_text())
    output = Path(output or ROOT / "results/validation/bennett_author")
    output.mkdir(parents=True, exist_ok=True)
    changes = []

    def replace(old, new, label):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError("Unexpected source anchor: " + label)
        text = text.replace(old, new)
        changes.append(label)

    replace("function out = mb_mv_a(", "function out = mb_mv_a_fixture(", "rename entry point")
    start, end = text.index("%%% Init random # stream"), text.index("%%%% Reward schedules")
    replace(text[start:end], "", "remove unused RNG seeding")
    replace("wkmap(:,:,1) = 0.1*rand(1,nk);", "wkmap(:,:,1) = dlmread('initial_plus.csv', ',');", "supply initial plus weights")
    replace("wkmav(:,:,1) = 0.1*rand(1,nk);", "wkmav(:,:,1) = dlmread('initial_minus.csv', ',');", "supply initial minus weights")
    replace("%%% Allocate memory for firing rates", "s = dlmread('activities.csv', ',');\nprovided_choices = dlmread('choices.csv', ',');\n\n%%% Allocate memory for firing rates", "supply activities and choices")
    start, end = text.index("  % Make decision"), text.index("  % Compute DAN firing rates")
    replace(text[start:end], "  decision(j) = provided_choices(j) + 1;\n\n", "replace random action selection with supplied zero-based choices")
    notice = "% Modified validation wrapper, generated 2026-09-11.\n% Bennett, Philippides & Nowotny; BrainsOnBoard/paper_RPEs_in_drosophila_mb\n% Source commit 7ec52afb9bd7bb748d94d60dea9f483645a2ce8e; GPL-3.0.\n% Original DAN/eq8 arithmetic unchanged; no genetic intervention.\n"
    (output / "mb_mv_a_fixture.m").write_text(notice + text, encoding="utf-8")
    for name in ("initial_plus", "initial_minus"):
        np.savetxt(output / (name + ".csv"), [fixture[name]], delimiter=",", fmt="%.17g")
    np.savetxt(output / "activities.csv", np.asarray(fixture["activities"]).T, delimiter=",", fmt="%.17g")
    # Author code skips its last update: trial 257 is a sentinel, so retain 256 updates.
    np.savetxt(output / "choices.csv", fixture["choices"] + [0], delimiter=",", fmt="%d")
    np.savetxt(output / "rewards.csv", fixture["rewards"] + [[1, -1]], delimiter=",", fmt="%d")
    script = f"""% Run from this generated directory in a compatible MATLAB/Octave runtime.
r = dlmread('rewards.csv', ',');
out = mb_mv_a_fixture({fixture['gamma']}, 1, 257, r, {fixture['eta']}, 'nk', 20, 'plasticity_rule', 'eq8');
trace = zeros(256, 44);
for j = 1:256
    trace(j,:) = [out.map(j,:)-out.mav(j,:), out.dap(j), out.dav(j), out.wkmap(:,:,j+1), out.wkmav(:,:,j+1)];
end
dlmwrite('author_trace.csv', trace, 'delimiter', ',', 'precision', '%.17g');
"""
    (output / "run_reference.m").write_text(script, encoding="utf-8")
    if (source.parent / "LICENSE").is_file():
        shutil.copyfile(source.parent / "LICENSE", output / "LICENSE")
    manifest = {"source_commit": fixture["source_commit"], "source_sha256": SOURCE_HASH,
                "changes": changes, "eq8_update_and_DAN_arithmetic": "unchanged",
                "author_trials": 257, "compared_updates": 256, "runtime_executed": False,
                "license": "GPL-3.0; original source and modified wrapper retained with upstream notice in the private repository",
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if (p.suffix in (".m", ".csv") or p.name == "LICENSE") and p.name != "author_trace.csv"}}
    (output / "preparation.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return output, manifest


if __name__ == "__main__":
    output, manifest = prepare()
    print(json.dumps({"output": str(output), "changes": manifest["changes"], "runtime_executed": False}))
