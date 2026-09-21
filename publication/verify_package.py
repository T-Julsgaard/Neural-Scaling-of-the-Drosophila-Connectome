"""Check delivered files against their SHA-256 manifest; no optional dependencies."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / 'output_manifest.json').read_text(encoding='utf-8'))
for name, expected in manifest['files'].items():
    path = (HERE / name).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f'Invalid package path: {name}')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Changed or corrupt file: {name}')
print(f"Verified {len(manifest['files'])} package file hashes.")
