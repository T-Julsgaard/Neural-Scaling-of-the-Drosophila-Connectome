"""Index Session B outputs and update only current continuity records."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import run_readout_diagnostic as d

def prepend(path, heading, body):
    p=d.ROOT/path; s=p.read_text(encoding='utf-8')
    if heading in s: return
    first,rest=s.split('\n',1)
    p.write_text(first+'\n\n'+heading+'\n\n'+body+'\n'+rest,encoding='utf-8')

def main():
    a=d.read(d.OUT/'analysis.json'); audit=d.read(d.OUT/'audit.json'); assert audit['passed'] and audit['blocks']==31
    g=a['primary_gap']; off=a['offline']['mean']; on=a['supervised']['mean']
    result=f"Offline full-outcome old-pair accuracy {100*off:.2f}% versus fully supervised online {100*on:.2f}%; paired difference {100*g['mean']:.2f} pp [{100*g['lower']:.2f}, {100*g['upper']:.2f}] (95%, 24 fresh task blocks, native/calibrated average)."
    link='[EXP-010 report](experiments/EXP-010-results.md)'
    body=result+' Frozen-feature information remains linearly recoverable despite sequential readout forgetting in this fixed larval assay. Offline is an explanatory diagnostic with different fitting/history access, not an equal-budget competitor or capacity bound. Five validation tests; six development tasks; all 31 validation/development/confirmation blocks replayed. B gate passed; C is explicitly deferred by the user. '+link+'.'
    prepend('RESEARCH_LOG.md','## 2026-09-15 — Session B completed and audited',body+' No normalization factorial, stronger compensation, new anatomy, growth, paid compute or C task was run. Next action: retain the frozen prediction for a later explicitly requested Session C; stop now.')
    prepend('DECISIONS.md','## 2026-09-15 — D039: close Session B; defer C',body)
    prepend('EXPERIMENTS.md','## EXP-010 / Session B — complete, 2026-09-15',body)
    prepend('CLAIMS_LEDGER.md','## Session B claim update — 2026-09-15',body+' The result does not establish unique causation by clipping, universal encoder sufficiency, biological homeostasis, or a novel mechanism. The published-versus-local compensation discrepancy remains incompletely explained.')
    for path in ('README.md','ROADMAP.md','OPEN_QUESTIONS.md'):
        prepend(path,'## Current Session B status — 2026-09-15',body+' The next scientific question is transfer beyond this associative assay; new seeds here are not task-family transfer.')
    prepend('SOFTWARE_AUDIT.md','## EXP-010 validation — 2026-09-15','Five tests passed; existing delta arithmetic, ridge augmented least-squares equivalence, signed/nonnegative decomposition, orthogonal learning, scale equivalence, stream/access isolation and author order invariance checked. All 31 blocks and saved arrays replay exactly; 70 historical scientific files unchanged. Bundled SciPy was absent; before any task execution, the t critical value for fixed n=24 replaced that optional dependency. '+link+'.')
    m=d.read(d.ROOT/'research/experiment_manifest.json')
    if not any(x['id']=='EXP-010' for x in m['experiments']):
        m['experiments'].append(dict(id='EXP-010',status='completed_audited',spec='experiments/EXP-010-protocol.md',results='experiments/EXP-010-results.md',prediction_passed=a['prediction_passed'],next='C permitted by evidence, explicitly deferred by user'))
        m['scientific_experiments_completed']=9
        d.write(d.ROOT/'research/experiment_manifest.json',m)
    handoff='''# After Session B — saved gate, no Session C execution

2026-09-15. Session B / EXP-010 is complete. Read [report](../experiments/EXP-010-results.md), [selection](../results/exp010/selection.json), [analysis](../results/exp010/analysis.json) and [audit](../results/exp010/audit.json).

'''+result+'''

## Saved explanation and falsifier

Within the fixed K6 larval pair-memory regime, sequential learning loses useful old preferences although a signed linear readout can recover them from the same frozen features. Full outcome supervision alone does not close the deficit. The operational prediction was frozen and confirmed: offline old accuracy >=80%, offline-versus-full-online paired lower CI >5 pp, and online acquisition-to-final loss lower CI >5 pp. Failure of any criterion would have falsified it. Keep access, clipping, scale, replay and numerical-fitting distinctions from the report.

The later transfer hypothesis is that a distinct validated task with shared sparse features and sequential acquisition will show an offline-versus-online gap even under matched supervision. A task on which a well-fitted held-out linear readout also fails, or supervised online retains as well as offline, would count against that generalization. This is a candidate for later prospective C design, not a frozen new-task protocol and not evidence of transfer. No task family or success-favoring evaluation has been selected.

## Boundary

C is permitted by the B gate but the user explicitly deferred it. Do not start C, D, speculative expansion or another campaign from this handoff alone. If later authorized, C must first choose one distinct task family and validate learnability; do not reuse these confirmation tasks to tune it. If the user instead requests D, use the narrower familiar sequential-interference result without inventing novelty. A repair should address demonstrated update interference, with matched feedback and resource accounting; added anatomy or stronger compensation is not justified by B.

## Recovery

All 31 EXP-010 blocks are archived, source-hashed and exactly replayed. Preserve EXP-002–009 scientific artifacts and all confirmation samples. The archive contains per-update pair-margin changes, fitting coefficients, choices, stochastic outcomes, noise probes, contracts, selection, regularizers and resource records. Raw NPZ files are locally retained and Git-ignored; compact records are versionable. Source freeze predates stages and prediction freeze predates confirmation. No external publication or push occurred.
'''
    (d.ROOT/'research/SESSION_B_COMPLETION.md').write_text(handoff,encoding='utf-8')
    paths=[p for p in d.OUT.rglob('*') if p.is_file() and 'frozen_source' not in p.parts]
    paths += [d.ROOT/p for p in ('experiments/EXP-010-protocol.md','experiments/EXP-010-results.md','tools/run_readout_diagnostic.py','tools/report_readout_diagnostic.py','tools/finalize_readout_records.py','tests/test_exp010.py','research/SESSION_B_COMPLETION.md')]
    d.write(d.ROOT/'research/exp010_artifacts.json',{p.relative_to(d.ROOT).as_posix():dict(sha256=d.sha(p),bytes=p.stat().st_size) for p in paths})
    d.write(d.ROOT/'research/runs/EXP-010-readout-diagnostic.json',dict(status='completed_audited',created_utc=d.stamp(),summary=result,prediction_passed=a['prediction_passed'],report='experiments/EXP-010-results.md',artifacts='research/exp010_artifacts.json',next='Stop; C explicitly deferred'))
    print(result)

if __name__=='__main__': main()
