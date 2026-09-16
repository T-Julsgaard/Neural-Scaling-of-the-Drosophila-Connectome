"""Refresh project handoff after audited EXP-005; preserve historical experiment reports."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
from exp002.data import ROOT
from exp005.campaign import read, folder


def edit(name, old, new):
    path=ROOT/name
    text=path.read_text(encoding='utf-8')
    if old not in text:
        raise ValueError('Missing expected text in '+name)
    path.write_text(text.replace(old,new),encoding='utf-8')


def main():
    assert read(folder('evaluation')/'audit.json')['status']=='passed'
    a=read(folder('evaluation')/'analysis.json')
    path=ROOT/'ROADMAP.md'
    text=path.read_text(encoding='utf-8')
    text=text.replace('This is a strategic recommendation; follow-up protocols and campaigns are not yet frozen or executed.',
        '**Priority 1 is now complete:** [EXP-005](experiments/EXP-005-results.md) finds a K6 advantage after matched updates and equal tuning (+3.78 pp [2.39,5.27], primary 98.75%). Better noisy-cue repeatability is a candidate contributor; unique mediation remains unresolved. **Next is priority 2**, the [persistent-memory benchmark design](experiments/EXP-006-design.md), which has not run.')
    start=text.index('### Selected course after mission review')
    stop=text.index('### Completed baseline and current handoff')
    text=text[:start]+'''### Current course after EXP-005

1. **Complete — explain the bounded N73 activity benefit.** K6 beats K4 after slow and fast update matching, norm matching and equal development tuning. Tuned retention is 96.00% versus 92.23%, a +3.78 pp difference [2.39,5.27] (98.75%). New learning does not show a compensating deficit. No additional mechanism samples are planned. The exact representation mediator is unresolved; this does not prevent completing the bounded milestone.
2. **Next — persistent memory under increasing load and cue similarity.** Finalize and validate [EXP-006](experiments/EXP-006-design.md), then run fresh development and a frozen confirmation. Preserve weights across memories; probe every previously learned pair. Compare native K4/K6, direct-input delta and degree/contact-controlled randomized sparse N73 circuits. Separate constant exposure per memory from constant total exposure.
3. **Then — balanced participation across existing cells.** Use the benchmark to test development-calibrated threshold/gain homeostasis against ordinary tuning and shuffled calibration. K6 reduces unused cells but increases between-cue overlap; participation itself is not the outcome to optimize.
4. **Then — validate a specific prediction in another circuit.** Transfer a frozen intervention or observed limitation with fresh tasks and anatomy controls.
5. **Conditional alternatives remain.** Growth requires evidence that extra features address a representation limit; targeted rewiring requires collision evidence. B5 evolution needs an informative held-out capability battery and equal-budget random search, with ancestry preserved and learned weights initially reset between candidate lifetimes. EXP-001 remains the recurrent-computation alternative. None is promoted by a positive result in this narrow assay alone.

**What changed:** learning-rate adjustment does not remove the activity advantage. The next benchmark should test whether K6's greater noisy-cue stability remains useful as similar-cue overlap and memory load increase. The roadmap order is unchanged, and these results do not justify restarting growth.

''' + text[stop:]
    old='Next concrete action: specify a fresh N73-only diagnostic separating winner count from activity per winner and effective learning-update size, with explicit normalization and learning-rate-matched controls. N73/K6 is a promising same-assay candidate; a new task family is needed before broader adaptation claims. Do not extend completed samples or prioritize population expansion from this evidence. See the [EXP-004 interpretation](experiments/EXP-004-results.md). Adult transfer and a bounded lineage pilot remain later design decisions.'
    text=text.replace(old,'Next concrete action: finalize and validate the [EXP-006 persistent-memory benchmark](experiments/EXP-006-design.md). EXP-005 is complete; no old sample will be extended or retuned. See the [mechanism results](experiments/EXP-005-results.md).')
    text=text.replace('Clarify normalization/effective updates at N73 before broader transfer; do not prioritize more growth. Keep B2/B4 and bounded B5 alternatives',
                      'EXP-005 now completes the bounded N73 update diagnostic; proceed to persistent-memory load/similarity before broader transfer or more growth. Keep B2/B4 and bounded B5 alternatives')
    path.write_text(text,encoding='utf-8')
    edit('EXPERIMENTS.md','**Three scientific hypothesis experiments completed: EXP-002 baseline, EXP-003 confirmation and EXP-004 activity/population diagnostic.**',
         '**Four scientific experiments completed: EXP-002 baseline, EXP-003 confirmation, EXP-004 activity/population diagnostic and EXP-005 mechanism controls.** EXP-005 supports a K6 retention benefit after matched updates and equal tuning. EXP-006 is the next benchmark design, not an executed campaign.')
    edit('EXPERIMENTS.md','Common authoritative rules:',
         '| EXP-005 | [Activity mechanism at N73](experiments/EXP-005.md) | completed / audited | 21 preflight tests; six development and 32 evaluation blocks; root 6 | Tuned K6-K4 retention +3.78 pp [2.39,5.27], primary 98.75%. [Results](experiments/EXP-005-results.md) |\n| EXP-006 | [Persistent-memory load and similarity](experiments/EXP-006-design.md) | proposed design / not executed | EXP-005; final protocol and validation pending | Continuous retained weights, increasing load/similarity, direct-input and randomized sparse baselines |\n\nCommon authoritative rules:')
    # Keep table contiguous for Markdown rendering.
    edit('EXPERIMENTS.md','\n\n| EXP-005 |','\n| EXP-005 |')
    edit('README.md','**EXP-002, EXP-003 and EXP-004 complete and audited • 13 September 2026.**',
         '**EXP-002 through EXP-005 complete and audited • 13 September 2026.**\n\n[EXP-005 mechanism results](experiments/EXP-005-results.md): K6 retains a +3.78 pp advantage [2.39,5.27] after matched updates and equal tuning (primary 98.75%). New learning does not show a compensating deficit. More repeatable noisy-cue responses and broader participation are candidate contributors; unique mediation is unresolved. Next: [persistent-memory load and cue similarity](experiments/EXP-006-design.md), with direct-input and randomized sparse baselines.')
    edit('README.md','Start with [EXP-004](experiments/EXP-004-results.md), then the historical [EXP-003 confirmation](experiments/EXP-003-confirmation-results.md) and [EXP-002 baseline](experiments/EXP-002-baseline-results.md). Next specify a fresh N73-only diagnostic separating winner count from activity per winner and effective learning-update size, with explicit normalization and learning-rate-matched controls. N73/K6 is a promising same-assay candidate; a new task family is needed before broader adaptation claims. Do not extend completed samples or prioritize population expansion from this evidence. [EXP-001](experiments/EXP-001.md) remains independent.',
         'Start with [EXP-005](experiments/EXP-005-results.md), then the historical EXP-004/003/002 reports. Priority 1 is complete; finalize and validate EXP-006 next. No completed sample should be retuned or extended, and growth remains conditional on a measured capacity limit. [EXP-001](experiments/EXP-001.md) remains independent.')
    edit('README.md','The foundation and completed EXP-002/EXP-003 evidence remain intact. EXP-004 completed the requested activity/population diagnostic using fresh streams; its next step is normalization/update-size clarification at N73.',
         'The historical foundation and EXP-002/003/004 evidence remain intact. EXP-005 completed the bounded N73 mechanism milestone; the next step is persistent-memory load and cue similarity.')
    path=ROOT/'OPEN_QUESTIONS.md'
    text=path.read_text(encoding='utf-8')
    text=text.replace('Fresh N73-only normalization and learning-rate-matched controls, followed by a new task family if useful. EXP-004 held total activity at 10, so 10/K per-cell amplitude changed',
         'RESOLVED within the bounded assay: EXP-005 matched-update and norm controls remain positive; tuned K6-K4 +3.78 pp [2.39,5.27] (98.75%). Stability/participation are candidate contributors; unique causal mediation remains open')
    pos=text.index('Default next action:')
    text=text[:pos]+'Default next action: finalize and validate EXP-006 persistent-memory load/similarity, including direct-input and randomized sparse baselines. EXP-005 is complete; do not extend the completed samples. Test whether K6 stability remains useful when cue overlap and cumulative load increase.\n'
    path.write_text(text,encoding='utf-8')
    path=ROOT/'research/experiment_manifest.json'
    manifest=json.loads(path.read_text(encoding='utf-8'))
    manifest['scientific_experiments_completed']=4
    manifest['experiments'] += [
        {'id':'EXP-005','status':'completed','spec':'experiments/EXP-005.md','source_ids':['S64'],
         'runtime_measured':True,'seed_root':6,'development_blocks_completed':6,'evaluation_blocks_completed':32,
         'validation_tests':21,'primary_interval_percent':98.75,'results':'experiments/EXP-005-results.md',
         'evaluation_run':'research/runs/EXP-005-evaluation.json',
         'primary_results':{k:a['contrasts'][k]['retention_after'] for k in ('historical','slow_matched','fast_matched','tuned')},
         'next_action':'Finalize and validate EXP-006 persistent-memory load/similarity benchmark'},
        {'id':'EXP-006','status':'proposed','spec':'experiments/EXP-006-design.md','source_ids':['S64'],
         'runtime_measured':False,'next_action':'Freeze benchmark implementation, precision and tuning budget before confirmation'}]
    path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    path=ROOT/'RESEARCH_LOG.md'
    text=path.read_text(encoding='utf-8')
    heading=text.index('\n')+1
    text=text[:heading]+'''
## 2026-09-13 — EXP-005 closes bounded activity mechanism milestone

The user authorized completion of roadmap priority 1 and requested findings, next action and any change of course. Created and froze EXP-005 before development: eight fixed amplitude/update/norm settings, equal eight-candidate tuning per K, frozen controls, six development and 32 evaluation blocks on fresh root 6. Twenty reset episodes per block. Created the prospective EXP-006 benchmark design before evaluation.

21 preflight tests passed after repairing a checkpoint JSON-envelope reader mismatch before campaign execution. Both campaigns completed and audited with raw hashes, task regeneration, metric recomputation and exact full-block replay. No exclusions or campaign failures. No subagents or external reviewer. Old source/protocol/results were preserved.

Historical K6-K4 retention +4.25 pp [2.71,5.90]; slow matched and tuned +3.78 [2.39,5.27]; fast matched +3.91 [2.17,5.74] (four primary 98.75% intervals). Positive residual after equal tuning; neither practical equivalence nor an effect definitely above +3 pp is established. New learning improves on secondary online measures. Actual matched coefficients are .33258/.33276; geometry shows greater within-cue repeatability but slightly greater between-cue overlap. Stability and participation are candidate contributors, not proven mediation.

Close priority 1 without further sampling. Roadmap order stays: persistent memory/load/similarity with restored baselines, then homeostasis, then a specific circuit transfer; growth/rewiring/evolution conditional. See [report](experiments/EXP-005-results.md), [run](research/runs/EXP-005-evaluation.json), [next design](experiments/EXP-006-design.md).

''' + text[heading:]
    path.write_text(text,encoding='utf-8')
    edit('DECISIONS.md','When reversing a decision,',
         '| D031 (2026-09-13) | Complete user-authorized EXP-005 and advance to persistent-memory load/similarity | The bounded N73 mechanism experiment passes both matched-update contrasts and retains a tuned K6 gain +3.78 pp [2.39,5.27] (98.75%), with no demonstrated new-learning deficit. Nominal learning-rate adjustment is insufficient; stability/participation are candidate contributors. Close this sample and finalize EXP-006; homeostasis and circuit transfer follow, with growth conditional. Supersedes the old immediate mechanism-design handoff, not historical results. [Report](experiments/EXP-005-results.md) |\n\nWhen reversing a decision,')
    edit('CLAIMS_LEDGER.md','## Update rule',
         '## EXP-005 additions — 2026-09-13\n\n- In this N73 synthetic assay, K6 retains a positive retention advantage after slow/fast nominal update matching and equal bounded tuning. Tuned +3.78 pp [2.39,5.27] (98.75%). This is not proof of a >3 pp effect or global tuning superiority.\n- Online new learning does not show a compensating deficit; the independent new-cue probe remains directionally uncertain. Secondary intervals are exploratory.\n- K6 has more repeatable noisy-cue representations and fewer unused cells, alongside slightly higher cross-cue overlap. These are descriptive candidate mechanisms, not identified causal mediation or a memory-capacity result.\n\nEvidence: [EXP-005 report](experiments/EXP-005-results.md), [audited run](research/runs/EXP-005-evaluation.json).\n\n## Update rule')


if __name__=='__main__': main()
