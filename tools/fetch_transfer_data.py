"""Recover the exact EXP-008 public inputs using the committed anatomy manifest."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/exp008'

def fetch(url, name, expected, maximum):
    path=CACHE/name
    if path.exists():
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected, f'Existing input differs: {name}'
        return
    temporary=path.with_suffix(path.suffix+'.tmp')
    size=0; h=hashlib.sha256()
    with urllib.request.urlopen(url,timeout=60) as response,temporary.open('wb') as output:
        while chunk:=response.read(1024*1024):
            size+=len(chunk);assert size<=maximum,'Download exceeds bound'
            output.write(chunk);h.update(chunk)
    assert h.hexdigest()==expected,f'Source hash mismatch: {name}'
    temporary.replace(path)

def main():
    r=json.loads((ROOT/'results/exp008_anatomy/record.json').read_text())
    CACHE.mkdir(parents=True,exist_ok=True)
    fetch(r['archive_url'],'exported-traced-adjacencies-v1.1.tar.gz',r['archive_sha256'],50_000_000)
    fetch('https://raw.githubusercontent.com/aclinlab/CompensatoryVariability/'+r['annotation_commit']+'/'+r['annotation_path'],
        'monoglom_PNs_v1.1.csv',r['annotation_sha256'],100_000)
    (CACHE/'annotation_commit.txt').write_text(r['annotation_commit']+'\n')
    print('Pinned EXP-008 raw inputs verified. Existing calibration and experimental outputs were not touched.')

if __name__=='__main__':main()
