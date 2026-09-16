"""Final nonexperimental report cleanup and integrity record."""
from pathlib import Path
import json
import re
ROOT=Path(__file__).resolve().parents[1]

names=['README.md','ROADMAP.md','DECISIONS.md','EXPERIMENTS.md','REPRODUCTIONS.md','CLAIMS_LEDGER.md','OPEN_QUESTIONS.md','FAILED_PATHS.md','DATA_PROVENANCE.md','SOFTWARE_AUDIT.md','RESEARCH_LOG.md','research/SEARCH_LOG.md']
for name in names:
    p=ROOT/name; text=p.read_text(encoding='utf-8')
    text=re.sub(r'(?<!\n)\n(?=## )','\n\n',text)
    p.write_text(text,encoding='utf-8')
p=ROOT/'FAILED_PATHS.md'; text=p.read_text(encoding='utf-8')
note='The final link indexer initially did not strip Markdown angle brackets around a filename; it was corrected. A one-line shell edit also failed from quoting before changing any file; the edit was applied with the patch tool. These reporting-tool failures did not alter scientific outputs.'
if note not in text: p.write_text(text+'\n'+note+'\n',encoding='utf-8')
validation=json.loads((ROOT/'research/validation_report.json').read_text(encoding='utf-8'))
assert validation['status']=='passed' and validation['scientific_experiments_run']==8
record=dict(status='complete',session='A',scientific_gate='passed',experiment='EXP-009',
            no_session_b_run=True,validation_tests=7,confirmed_blocks=24,replayed_readouts=152,
            historical_files_verified=82263,foundation_integrity=validation['status'],
            reports=['experiments/EXP-009-results.md','research/SESSION_A_SOURCE_AUDIT.md','research/SESSION_B_HANDOFF.md'],
            remaining_session_a_work=[],next_action='Execute Session B only when requested; follow its saved handoff.')
(ROOT/'research/exp009_completion.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
