"""Build, verify, or restore the saved NPZ evidence distributed with a release.

Uses only Python's standard library. Restore never replaces differing files.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/reproduction_archive_manifest.json"
LIMIT = 512 * 1024 * 1024


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_target(name):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT / "results") or path.suffix != ".npz":
        raise ValueError(f"Invalid evidence path: {name}")
    return path


def build(directory):
    directory.mkdir(parents=True, exist_ok=True)
    names = subprocess.check_output([
        "git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "results"
    ], cwd=ROOT).decode().split("\0")
    paths = sorted(safe_target(name) for name in names if name)
    if not paths:
        raise ValueError("No ignored saved arrays found")
    groups = []; group = []; size = 0
    for path in paths:
        if group and size + path.stat().st_size > LIMIT:
            groups.append(group); group = []; size = 0
        group.append(path); size += path.stat().st_size
    groups.append(group)
    archives = []; files = {}
    for index, group in enumerate(groups, 1):
        name = f"saved-arrays-{index:02}.zip"
        destination = directory / name
        # NPZ is already compressed; ZIP_STORED preserves bytes without wasted compression.
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
            for path in group:
                relative = path.relative_to(ROOT).as_posix()
                files[relative] = {"sha256": digest(path), "bytes": path.stat().st_size, "archive": name}
                archive.write(path, relative)
        archives.append({"name": name, "sha256": digest(destination), "bytes": destination.stat().st_size, "files": len(group)})
        print(f"Built {name}: {len(group)} saved arrays", flush=True)
    record = {"schema_version": 1, "release_tag": "academic-report-2026-09-21", "algorithm": "SHA-256",
              "scope": "All Git-ignored NPZ files under results at public release preparation; original bytes, no retraining",
              "file_count": len(files), "total_bytes": sum(f["bytes"] for f in files.values()),
              "archives": archives, "files": files}
    MANIFEST.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    (directory / "SHA256SUMS").write_text("".join(f"{a['sha256']}  {a['name']}\n" for a in archives), encoding="ascii")


def verify(directory, restore):
    record = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in record["archives"]:
        source = directory / entry["name"]
        if digest(source) != entry["sha256"]:
            raise ValueError(f"Archive checksum mismatch: {source.name}")
        expected = {name: item for name, item in record["files"].items() if item["archive"] == source.name}
        with zipfile.ZipFile(source) as archive:
            if len(archive.namelist()) != len(expected) or set(archive.namelist()) != set(expected):
                raise ValueError(f"Archive inventory mismatch: {source.name}")
            for name, item in expected.items():
                target = safe_target(name) if restore else None
                data = archive.read(name)
                if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
                    raise ValueError(f"Evidence checksum mismatch: {name}")
                if restore:
                    if target.exists():
                        if digest(target) != item["sha256"]:
                            raise ValueError(f"Refusing to replace changed evidence: {name}")
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with target.open("xb") as output:
                            output.write(data)
        print(f"{'Restored' if restore else 'Verified'} {source.name}", flush=True)
    print(f"Verified {record['file_count']} saved arrays.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify", "restore"))
    parser.add_argument("--directory", type=Path, default=ROOT / ".cache/public-release")
    args = parser.parse_args()
    if args.action == "build":
        build(args.directory)
    else:
        verify(args.directory, args.action == "restore")
