"""Build Session A's report and static plot from audited EXP-009 evidence."""
from pathlib import Path
import os
import json
import sys
import hashlib
import datetime
ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/'.cache/baseline-plot-deps'))
os.environ['MPLCONFIGDIR']=str(ROOT/'.cache/matplotlib')
import numpy as np

def main():
    out=ROOT/'results/exp009'; a=json.loads((out/'analysis.json').read_text()); s=json.loads((out/'selection.json').read_text())
    v=json.loads((out/'validation.json').read_text()); source=json.loads((ROOT/'research/exp009_source_audit.json').read_text())
    parallel=json.loads((out/'historical_parallel_audit.json').read_text())
    assert a['all_archives_replayed_exactly']
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,(ax,bx)=plt.subplots(1,2,figsize=(10,4),gridspec_kw={'width_ratios':[1.1,1]})
    for path in sorted((out/'confirmation').glob('block_*.json')):
        r=json.loads(path.read_text()); ax.plot([0,1],100*np.array([r['scores'][0][0],r['scores'][1][0]]),color='#94a3b8',alpha=.55,lw=.8)
    for i,key,color in [(0,'uncompensated','#b91c1c'),(1,'compensated','#a21caf')]:
        mean=a[key]['mean']*100; lo,hi=np.array(a[key]['interval'])*100
        ax.errorbar(i,mean,yerr=[[mean-lo],[hi-mean]],fmt='o',color=color,markersize=8,capsize=5,zorder=5)
    ax.axhline(50,color='#64748b',ls=':',lw=1); ax.set_ylim(48,68)
    ax.set_xticks([0,1],['Uncompensated','Compensated']); ax.set_ylabel('Correct-valence choice probability (%)')
    ax.set_title('Fresh tasks; one fixed author model')
    bx.axvline(0,color='#64748b',lw=1); bx.axvspan(0,3,color='#e2e8f0'); bx.axvline(3,color='#64748b',ls=':',lw=1)
    for y,key,label,color in [(1,'primary','Equal tuning','#a21caf'),(0,'matched_rate','Same learning rate','#475569')]:
        mean=a[key]['mean']*100; lo,hi=np.array(a[key]['interval'])*100
        bx.errorbar(mean,y,xerr=[[mean-lo],[hi-mean]],fmt='o',color=color,markersize=7,capsize=5)
        bx.text(mean,y+.22,f'{mean:.2f} [{lo:.2f}, {hi:.2f}]',ha='center',fontsize=9)
    bx.set_yticks([0,1],['Same rate\n(descriptive)','Equal tuning\n(primary)']); bx.set_ylim(-.6,1.6); bx.set_xlim(-.5,11)
    bx.set_xlabel('Compensated minus uncompensated (pp)'); bx.set_title('Paired 95% task-block intervals')
    for axis in (ax,bx): axis.spines[['top','right']].set_visible(False)
    fig.suptitle('Session A: bounded author-parameter positive control',fontsize=14)
    fig.text(.5,.02,'24 independent tasks conditional on one supplied network; not an exact Figure 4 reproduction',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,.93)); fig.savefig(out/'positive_control.png',dpi=180); plt.close(fig)
    def interval(key):
        z=a[key]; return f"{100*z['mean']:.2f} [{100*z['interval'][0]:.2f}, {100*z['interval'][1]:.2f}]"
    profiles=a['profiles']; r=a['resources']
    resources='\n'.join(f"| {name} | {z['blocks']} | {z['wall_seconds']:.2f} | {z['cpu_seconds']:.2f} | {z['peak_bytes']/2**20:.2f} | {z['archive_bytes']/2**20:.2f} |" for name,z in r.items())
    report=f'''# Session A / EXP-009: published-parameter positive control

2026-09-15 (Europe/Copenhagen; machine timestamps are UTC). **Session A gate: {'PASS' if a['gate_passed'] else 'NOT MET'}. Stop here; Session B has not been run.**

The supplied compensated model scored **{interval('compensated')}%** versus **{interval('uncompensated')}%** for its uncompensated counterpart. The primary paired difference is **+{interval('primary')} percentage points**, with a 95% task-block bootstrap interval. This establishes a useful positive effect in the bounded author-parameter regime. It does not explain the project's previous null results.

[Frozen protocol](EXP-009-protocol.md) · [Source/equation audit](../research/SESSION_A_SOURCE_AUDIT.md) · [Machine-readable analysis](../results/exp009/analysis.json) · [Run record](../research/runs/EXP-009-positive-control.json) · [Session B handoff](../research/SESSION_B_HANDOFF.md)

![Session A paired results](../results/exp009/positive_control.png)

## What was reproduced, adapted and left unresolved

Selected comparison: Abdelrahman, Vasilaki and Lin (2021), **Figure 4B2, magenta threshold compensation versus red random model, c=1**. Source commit `9f3f7e9e85117febef1ad32e3152c830570f74d3`, published paper, supplementary equations and Dataset S1 are saved with hashes. Dataset S1's twenty-model means are53.3492% and63.3565%, difference+10.0073pp. Those are published observations extracted from `Fig 4!I3:I22` and `M3:M22`, not pooled with our results or used as new confirmation.

**Classification: independent bounded transfer/adaptation using author-fitted parameters, with author-runtime equation validation.** The experiment uses the one supplied calibrated MAT instance, not twenty newly fitted networks. The source's uncapped joint optimizer was inspected, not rerun or validated. The saved compensated projection is5 times the raw projection, while the current script specifies4.5. Both preserve identical connectivity. Saved optimizer history, seed and exact figure-rate mapping remain unresolved. No claim of exact panel reproduction or threshold-only causal isolation is justified.

Fresh blocks resample100 synthetic odors independently from24 supplied empirical PN marginals. Each block has balanced random labels, independent random output initialization,15 training and15 held-out noisy observations per odor, paired across arms. Models retain2,000 graded KCs, pseudo-feedforward APL inhibition and two4,000-parameter readouts (4,000 learned weights **per arm**). Input scale and all encoder parameters come from the supplied author instance and are frozen. There is no new homeostatic fit or anatomy selection.

Declared adaptations: newly resampled empirical rather than recovered original histogram odors; all training trials noisy; fixed inherited PN scale instead of all-trial rescaling; training-only KC maximum instead of using test extrema; independent NumPy RNG; and equal prospective development tuning. This tests transfer from the authors' original calibration pool to fresh task prototypes from the same marginals. It is not a new chemical-class distribution shift. Unknown upstream calibration costs are not reported as zero.

Learning uses full labels and exponential depression of the wrong-valence output, with rate divided by mean training activity. Sufficient statistics implement the exact product of the per-odor exponential factors; all training associations are assessed afterward. The endpoint is average correct-valence choice **probability**, not a sampled accuracy or the project's pairwise sequential-retention endpoint. There is no action-conditioned reward access, prediction-error update, reversal or old-memory-age trajectory in this comparison.

## Prospective choices and findings

Four development blocks each evaluated the same ten learning rates per arm. Selected rates: uncompensated{s['selected_rates'][0]:.6g}, compensated{s['selected_rates'][1]:.6g}; neither is a grid boundary. No settings changed after development. Paired development SD={s['paired_sd']:.6f}; uncapped precision calculation requested{s['uncapped_n']} blocks, and the protocol's minimum fixed **{s['n']}**. Projected halfwidth was{100*s['projected_halfwidth']:.2f}pp; achieved halfwidth is{100*a['halfwidth']:.2f}pp. Four development blocks provide an uncertain variance estimate, so the sample minimum and final precision gate matter.

| Endpoint | Estimate [95% interval] |
|---|---:|
| Uncompensated probability, % | {interval('uncompensated')} |
| Compensated probability, % | {interval('compensated')} |
| Primary equal-tuning difference, pp | {interval('primary')} |
| Compensated at the uncompensated learning rate, difference, pp; descriptive | {interval('matched_rate')} |

Uncertainty units are independent **task blocks conditional on one fixed author network and its empirical source table**. Odors, trials and KCs are not independent replicates for this interval. The two-sided percentile bootstrap uses50,000 draws. It is approximate; it does not support confidence intervals across biological animals or random network instances.

Gate criteria were fixed before new tasks: arithmetic/data/replay audits pass; compensated mean>=55%; primary lower interval>3pp; halfwidth<=2pp. **{'All pass' if a['gate_passed'] else 'The complete gate does not pass'}**. No failed runs, exclusions, tuning extensions, replacement confirmation seeds or additional panels were used to obtain the effect. Access/runtime issues and source mismatch remain in the audit. The original EXP-007/008 practical-null results are unchanged.

Descriptive response profiles, averaged over new held-out probes:

| Measure | Uncompensated | Compensated |
|---|---:|---:|
| Coding level | {profiles[0]['coding_level']:.4f} | {profiles[1]['coding_level']:.4f} |
| Unused cells in the probe pool, % | {100*profiles[0]['unused_fraction']:.2f} | {100*profiles[1]['unused_fraction']:.2f} |
| CV of per-cell mean activity | {profiles[0]['mean_activity_cv']:.3f} | {profiles[1]['mean_activity_cv']:.3f} |
| Effective cells by mean activity | {profiles[0]['effective_mean_activity_cells']:.1f} | {profiles[1]['effective_mean_activity_cells']:.1f} |
| Mean squared feature norm after training-max scaling | {profiles[0]['mean_squared_norm']:.3f} | {profiles[1]['mean_squared_norm']:.3f} |

Original supplied calibration makes all2,000 cells' mean activities lie between.50924 and.51908, within.51 +/-6%. Raw per-cell means range0 to10.908. Equalization remains imperfect on fresh odors, and feature norms differ. The same-rate result does **not** establish norm-matched learning or unique mediation by participation.

## Differences from our model and ranked explanations

| Factor | Published/supplied positive-control regime | EXP-007/008 regime |
|---|---|---|
| Input weights | Raw heterogeneous lognormal claw weights; random24-to2,000 projection, duplicate claws summed. Compensated supplied gain5x | Extracted contact matrices, each KC's incoming sum normalized to1;40-to73 larval or104-to590 adult |
| Responses | Graded ReLU after APL and threshold; global coding target near10%, variable active count and norm | Fixed top-K, every winner10/K; total activity10, squared norm100/K |
| Compensation target/range | Near-complete per-cell mean-activity equalization, nonnegative but broadly variable thresholds, jointly fitted coding constraints/APL; frozen supplied fit | Partial participation-probability targets, bounded centered offsets; fitted on separate4,096-input pool; many offsets saturate |
| Noise | Author empirical mean-rate SD lookup; Gaussian PN noise; probabilistic c=1 decision | Synthetic binary-core cues, Gaussian .1/.3 noise clipped[0,1], stochastic .8/.2 reward and cue choice |
| Task |100 independent random-valence odor identities, full label exposure,15 observations each, final classification | Persistent sequential training on up to16 cue pairs, shared cores, blocked arrivals, reversal and all-memory probes |
| Learning rule | Multiplicative wrong-output depression; products commute across odor order; normalized by mean training activity | Opponent delta prediction-error updates, chosen cue only, nonnegative clipping, updates depend on current weights |
| Schedule/access | Every training odor receives its valence label; full task exposure before final test | New pairs displace old-pair training; only chosen outcomes drive learning; previous pair preferences may be overwritten |

**Rank1: baseline normalization plus weak residual compensation may leave little additional useful change.** Our per-cell input normalization removes one source of excitability variability before bounded offsets are added. The author regime begins with much greater activity inequality and reaches much more complete equalization. This is a plausible account, not a demonstrated normalization effect: graded outputs, inhibition and input distributions also differ.

**Rank2: error-dependent sequential learning may overwrite usable representations.** The published depression rule has commutative accumulated sufficient statistics. Our learner's later updates depend on current predictions, feedback access and clipping. This makes representation-versus-readout diagnostics more discriminating than another participation correlation. Mere odor ordering cannot cause forgetting in the fixed-input multiplicative rule; the bridge must distinguish update rule and supervision from schedule.

These are the only two nominated explanatory factors. The other table entries remain confounds to hold fixed or document, not additional hypotheses launched in A. No result here identifies the cause of our previous null.

## Validation, preservation and resource accounting

Seven tests passed, including scalar arithmetic, orthogonal learnability, label complement/chance, nonmutation, stream separation, training-only scaling and supplied-input Octave comparison. Maximum discrepancy across author response/weight/probability checks **{max(v['author_fixture_max_errors']):.3g}**, tolerance1e-10. A full-size ten-rate validation workload took{v['measured_full_block']['wall_seconds']:.2f}s and replayed exactly; the threefold-reserve52-block projection was{v['measured_projection_with_3x_reserve_seconds']:.2f}s, below the30-minute cap. Limits: one CPU worker/BLAS thread,2GiB peak memory,1GiB outputs, maximum48 confirmation blocks. No GPU, paid compute or new infrastructure.

| Stage | Blocks | Worker wall s | CPU s | Peak process MiB | Archive MiB |
|---|---:|---:|---:|---:|---:|
{resources}

Every development and confirmation archive was checksum-verified, its task regenerated, and **all {a['numerical_audits']} readout evaluations replayed exactly** from saved inputs/labels/initial weights. Historical preservation checked **{a['historical_files_verified']:,} files**. Full audit wall time is{a['audit_wall_seconds']:.2f}s and CPU time{a['audit_cpu_seconds']:.2f}s, separately from campaign computation. The historical snapshot/verification involves many small files and dominates elapsed I/O; these are not model runtime measurements. Report/plot generation, literature retrieval, source preparation and original upstream calibration are excluded from block counters. No target-colleague-machine benchmark or independent human/agent review is claimed.

Development exposes12,000 PN observations across four tasks and trains80 readouts; confirmation exposes72,000 PN observations and computes72 readouts including the prespecified same-rate diagnostic. Each arm has4,000 reward-learned output weights and two derived training scalars (global maximum, mean activity). Threshold compensation adds2,000 inherited fitted thresholds plus global gain/scale fitting; its original data/compute cost is unknown. The sparse projection stores48,000 entries per arm with many zeros. Global activity scaling and mean-activity rate normalization do not match feature norms across arms.

Recovery commands use the existing bundled Python executable with `tools/run_compensation.py development`, `confirmation`, then `audit`. Finished blocks verify hashes and are reused; do not delete or regenerate the sample. Source, protocol, selection, checkpoints and reports are pinned in [the artifact manifest](../research/exp009_artifacts.json). Binary traces are local and ignored by Git; source bundle and compact records are versionable.

## Session A decision

{'A validated positive effect permits Session B to investigate a controlled bridge to this one supplied-parameter regime.' if a['gate_passed'] else 'B may investigate our pipeline, but must not claim a validated bridge to the published effect.'} The exact published ensemble and its optimizer remain unreproduced. Session B should first separate frozen-feature information from online readout limitations, then choose at most the two nominated factors with explicit access and norm controls. [The handoff](../research/SESSION_B_HANDOFF.md) specifies the next action and falsifying outcomes. **No Session B experiment has been launched.**
'''
    report=report.replace('two4,000-parameter readouts (4,000 learned weights **per arm**)','two output channels with4,000 learned weights **per arm**')
    report=report.replace("Full audit wall time is", "Scientific replay and cached-hash verification wall time is")
    report=report.replace('The historical snapshot/verification involves',f"The I/O-only historical audit used16 file-reading threads and took {parallel['wall_seconds']:.2f}s wall / {parallel['cpu_seconds']:.2f}s CPU; combined audit took {parallel['total_audit_wall_seconds']:.2f}s wall. Model execution remained single-worker. The historical snapshot/verification involves")
    report=report.replace('No target-colleague-machine benchmark', 'The preservation snapshot began before model validation but finished after confirmation because of slow file I/O: this was not a completed pre-run historical freeze. Historical scientific files were not edited, and the final verification matches the snapshot. New model/protocol and selected settings were frozen before their respective stages. No target-colleague-machine benchmark')
    import re
    words='are|and|uses|specifies|time|difference|is|was|contains|resample|from|retain|with|per|all|below|between|within|range|to|random|gain|normalized to|or|near|winner|activity|norm|separate|exposure|Rank|tolerance|took|reserve|the|thread|memory|maximum|exposes|trains|computes|has|adds|stores|requested|uncompensated|compensated|used'
    report=re.sub(r'\b('+words+r')(?=(?:[0-9]|\.[0-9]))',r'\1 ',report)
    report=re.sub(r',(?!\d{3}(?:\D|$))(?=\d)',', ',report)
    report=report.replace('difference+10.0073pp','difference +10.0073 pp').replace('random 24-to 2,000 projection','random projection from 24 PNs to 2,000 KCs').replace('1;40-to 73 larval or 104-to 590 adult','1; 40-to-73 larval or 104-to-590 adult').replace('|100 independent','| 100 independent').replace('clipped[0, 1]','clipped [0, 1]')
    report=re.sub(r'(?<=\d)(pp|GiB|s)\b',r' \1',report)
    report=report.replace('Access/runtime issues and source mismatch remain in the audit.', 'Access/runtime issues and source mismatch remain in the audit. During reporting, the cached plotting library required read escalation and a Windows default-text-decoding error was fixed by specifying UTF-8; neither changed scientific outputs. A separate source-only check matched all 2,640 empirical noise SD lookups to the unmodified author function exactly.')
    (ROOT/'experiments/EXP-009-results.md').write_text(report,encoding='utf-8')
    print('Report and plot created from audited evidence.')

if __name__=='__main__': main()
