"""Index final Session A artifacts and verify local links and frozen source."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import hashlib
import re
import datetime
import urllib.parse
from tools.run_compensation import verify_frozen
ROOT=Path(__file__).resolve().parents[1]

def main():
    verify_frozen()
    paths=set()
    for directory in ['results/exp009','results/exp009_source','research/sources/exp009','exp009']:
        paths.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in str(p))
    for pattern in ['tools/*compensation*','tests/test_exp009.py','experiments/EXP-009*','research/exp009*','research/SESSION_A*','research/SESSION_B*','research/runs/EXP-009*']:
        paths.update(p for p in ROOT.glob(pattern) if p.is_file())
    names=['README.md','ROADMAP.md','DECISIONS.md','EXPERIMENTS.md','REPRODUCTIONS.md','CLAIMS_LEDGER.md','OPEN_QUESTIONS.md','FAILED_PATHS.md','DATA_PROVENANCE.md','SOFTWARE_AUDIT.md','RESEARCH_LOG.md','research/SEARCH_LOG.md','research/experiment_manifest.json','research/references.json','tools/validate_foundation.py','research/validation_report.json','.gitignore','.gitattributes']
    paths.update(ROOT/n for n in names)
    target=ROOT/'research/exp009_artifacts.json'; paths.discard(target)
    files={p.relative_to(ROOT).as_posix():dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(paths)}
    obj=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='complete',scope='Session A only; author-parameter adaptation, not exact published figure reproduction',files=files,total_bytes=sum(v['bytes'] for v in files.values()),continuation='Session B per research/SESSION_B_HANDOFF.md; no further A experiments',local_only_binary_traces='results/exp009/**/*.npz')
    target.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    for p in paths:
        if p.suffix!='.md' or 'sources' in p.parts: continue
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if link.startswith(('http:','https:','#','mailto:')): continue
            link=urllib.parse.unquote(link.strip('<>').split('#')[0])
            assert (p.parent/link).exists(),(p,link)
    print(json.dumps(dict(files=len(files),bytes=obj['total_bytes'],links='passed',frozen_source='passed')))

if __name__=='__main__': main()
