"""Render audited EXP-004 evidence without altering analysis or run artifacts."""
from pathlib import Path
import os
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from exp002.campaign import read_json
from exp002.data import sha256


def effect(e):
    lo,hi=e['interval']
    return f"{100*e['mean']:+.2f} [{100*lo:+.2f}, {100*hi:+.2f}]"


def main():
    output=ROOT/'results/exp004_evaluation'
    audit=read_json(ROOT/'research/runs/EXP-004-evaluation.json')
    if audit['status']!='completed_and_audited':
        raise ValueError('Complete audit required')
    for name in ('analysis.json','report.json','contract.json'):
        p=output/name
        if sha256(p)!=audit['files'][p.relative_to(ROOT).as_posix()]['sha256']:
            raise ValueError('Audited source changed')
    data=read_json(output/'analysis.json')
    run=read_json(output/'report.json')
    invocations=[read_json(p) for p in output.glob('invocation_*.json')]
    total_invocation_wall=sum(r.get('wall_seconds',0) for r in invocations)
    profiles,contrasts=data['profiles'],data['secondary_contrasts']
    lines=['# EXP-004 active count versus population: audited results','',
        '2026-09-13. All 32 fresh evaluation blocks completed and audited: 896 conditions, 17,920 reset episodes and 19,200 configuration-episodes. Four separate development blocks were completed and audited first. No evaluation-driven selection or sample expansion.','',
        '[Prospective protocol](EXP-004-protocol.md), [precision/resource plan](../research/exp004_planning.json), [validation](../research/exp004_validation.json), [audited run](../research/runs/EXP-004-evaluation.json), [all block estimates, curves and diagnostics](../results/exp004_evaluation/analysis.json).','',
        '## Post-audit interpretation and next milestone','',
        'The crossed experiment supports a retention benefit from increasing normalized winner count and a retention cost from increasing population under the fixed readout. The primary active-count effect is +5.37 pp [3.89,6.97], while the population effect is -5.03 pp [-7.27,-2.86] (98.333333% intervals). Increasing winner count helps at both N73 and N110; the matched degree-null arm shows the same qualitative pattern in secondary analyses. The tested growth intervention has no independent retention benefit here. This conclusion is conditional on the encoder, growth operators, readout and synthetic tasks.','',
        'The interaction is -0.04 pp [-2.99865,2.98647]. Its direction is unresolved. The frozen interval technically lies inside the prospective ±3 pp band, but only barely; this boundary-sensitive bootstrap classification should not be presented as strong evidence that interaction is absent.','',
        'The full-readout control supports the activity interpretation: at N73, K6 minus K4 improves retention +6.54 pp [4.73,8.46] and early reversal +4.41 pp [2.32,6.49]. At fixed K6, N110 minus N73 reduces retention -3.47 pp [-4.65,-2.36]. At fixed K4 its retention estimate is -1.53 pp [-3.12,0.12], which is uncertain. These are secondary exploratory 95% intervals. The population penalty is larger with the bottleneck, so representation/readout interactions remain important.','',
        'The original diagonal comparison, (N110,K6) minus (N73,K4), remains positive with full readout: retention +3.07 pp [1.86,4.34] and reversal +2.17 pp [0.27,4.11] (secondary 95%). With the fixed readout its retention effect is only +0.35 pp [-1.90,2.73]; the earlier EXP-003 fixed-readout gain was not clearly reproduced. This is a separate prospective result, not a reanalysis or invalidation of the earlier sample.','',
        'Next specify a fresh N73-only diagnostic that separates winner count from activity per winner and effective learning-update size, using explicit normalization and learning-rate-matched controls. Retain N73/K6 as a promising same-assay candidate; test a new task family before claiming broader adaptation. Do not expand populations or favor this wiring prior on the present evidence. Adult transfer and the bounded lineage pilot remain later options; no new follow-up experiment has been executed.','',
        '## Primary retention contrasts','',
        'Structured growth, fixed 32-feature readout (64 learned weights). Three prespecified factorial contrasts, each with a 98.333333% block-bootstrap interval. Values below are percentage points. The practical band is ±3 points; direction and practical magnitude are separate questions.','',
        '| Contrast | Change [interval], pp | Direction supported | Entire interval within ±3 pp |',
        '|---|---:|---|---|']
    for name,e in data['primary'].items():
        lines.append(f"| {name.replace('_',' ').capitalize()} | {effect(e)} | {e['direction']} | {e['within_practical_band']} |")
    lines += ['','The active-count effect averages K6−K4 at both populations. The population effect averages N110−N73 at both winner counts. The interaction is the difference between the two K effects. Their definitions were frozen before evaluation.','',
        '## Crossed retention profiles','',
        'Means are probabilities; intervals are secondary exploratory 95%. Native profiles are shared across arms, with no inflation of block count.','',
        '| Growth arm | Readout | N | K | Retention | 95% interval |','|---|---|---:|---:|---:|---|']
    for arm in ('structured','degree_null'):
        for readout in ('full','bottleneck'):
            for n,k in ((73,4),(73,6),(110,4),(110,6)):
                e=profiles[f'{arm}_{n}_{readout}_k{k}']['metrics']['retention_after']
                lines.append(f"| {arm} | {readout} | {n} | {k} | {e['mean']:.4f} | [{e['interval'][0]:.4f}, {e['interval'][1]:.4f}] |")
    lines += ['','![Crossed retention profiles](../results/exp004_evaluation/retention_factorial.png)','',
        '## Secondary simple effects and capability profile','',
        'All intervals here are exploratory 95%; these are not additional primary claims. Values are percentage points.','',
        '| Arm / readout / change | Retention | Early reversal | Acquisition | Robustness .3 |','|---|---:|---:|---:|---:|']
    for arm in ('structured','degree_null'):
        for readout in ('full','bottleneck'):
            for name in ('active_at_73','active_at_110','population_at_4','population_at_6','diagonal'):
                e=contrasts[f'{arm}_{readout}_{name}']
                lines.append(f"| {arm} / {readout} / {name} | "+' | '.join(effect(e[m]) for m in ('retention_after','early_reversal','acquisition','robustness_0.3'))+' |')
    lines += ['','## Validation, precision and resources','',
        f"{audit['validation']} preflight tests passed. Audit regenerated graphs and task identities, verified every raw episode hash, recomputed all summaries and inference, and checked native frozen controls at exactly chance. No exclusions or numerical failures in the successful campaign. Audit time {audit['audit_seconds']:.1f} seconds.",'',
        'Protocol 1.0 development encountered a concurrent storage-scan/atomic-rename race and is retained in `results/exp004_development_v1_failed/` with its frozen source and failure record. Version 1.1 fixed the bookkeeping race, passed a regression test and repeated all development on root-5 streams. Evaluation had not been generated; scientific settings and sample budget stayed fixed. No failed-attempt observations enter these estimates.','',
        f"Evaluation used {run['workers']} CPU workers: {run['wall_seconds_this_invocation']:.1f} s wall time for this invocation, {run['summed_worker_cpu_seconds']:.1f} s summed worker episode CPU time, {run['max_worker_peak_memory_bytes']/1024**2:.1f} MiB maximum individual worker peak memory (not total concurrent RAM), and {run['retained_bytes_before_report']/1024**2:.1f} MiB retained before reporting. The colleague workstation and energy use were not measured.",'',
        f"Total recorded evaluation invocation wall time is {total_invocation_wall:.1f} seconds across {len(invocations)} invocations. An infrastructure restart switched from the slow restricted filesystem wrapper to local access, preserving the frozen code, sample and checkpoints. Resume verified saved artifacts. Retained-episode CPU counters exclude any discarded uncheckpointed computation; they are not total process CPU or energy. [Execution recovery record](../research/exp004_execution_recovery.json).",'',
        'Evaluation also recorded a Windows permission error while atomically replacing one checkpoint in block 1009. The remaining workers completed their queued blocks, leaving 31 complete blocks. The same frozen implementation subsequently resumed from the last valid checkpoint; the failure record and interrupted invocation are retained. No block or episode was excluded, and no scientific code or analysis plan was changed for this recovery.','',
        'Planned primary half-width at assumed SD .07 was 2.96 pp. Achieved half-widths: '+', '.join(f"{k.replace('_',' ')} {100*v['half_width']:.2f} pp" for k,v in data['primary'].items())+'. No sample was added in response to these widths.','',
        '## Interpretation limits','',
        'Winner count is exact before the readout projection. Total activity remains 10, so K6 also reduces activity per selected cell relative to K4. The intervention can change effective update size, overlap and competition. Fixed learned-weight count does not fix the representation, bottleneck mixing or effective learning rate. A population main effect averaged over K cannot by itself establish that population is irrelevant at each K.','',
        'Uncertainty is across 32 task blocks sharing one anatomy and synthetic task families. This is no adult, cross-specimen or general-adaptation test. EXP-003 remains a separate completed experiment; none of its evaluation observations enter these estimates.']
    (ROOT/'experiments/EXP-004-results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
    sys.path.insert(1,str(ROOT/'.cache/baseline-plot-deps'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained',sharey=True)
    for row,arm in enumerate(('structured','degree_null')):
        for col,readout in enumerate(('full','bottleneck')):
            ax=axes[row,col]
            for n,color in ((73,'#267078'),(110,'#a44e25')):
                values=[profiles[f'{arm}_{n}_{readout}_k{k}']['metrics']['retention_after'] for k in (4,6)]
                means=np.array([e['mean'] for e in values])
                bounds=np.array([e['interval'] for e in values])
                ax.errorbar([4,6],means,yerr=np.stack([means-bounds[:,0],bounds[:,1]-means]),fmt='o-',color=color,capsize=4,label=f'N = {n}')
            ax.set(title=f"{arm.replace('_',' ').title()} / {readout}",xlabel='Exact active KC count',ylabel='Post-interference retention',xticks=[4,6])
            ax.grid(alpha=.2)
            ax.legend()
    fig.suptitle('EXP-004: population size crossed with active count\n32 fresh task blocks; secondary 95% intervals',fontsize=13)
    fig.savefig(output/'retention_factorial.png',dpi=170)
    fig.savefig(output/'retention_factorial.svg')
    plt.close(fig)


if __name__=='__main__':
    main()
