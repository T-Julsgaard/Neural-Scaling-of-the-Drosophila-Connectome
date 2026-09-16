"""Generate the EXP-008 evidence report and update current project status."""
import sys
import json
import hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from exp008.campaign import ROOT, folder, read, write, REPORT

def fmt(v):
    return f"{100*v['mean']:.2f} [{100*v['interval'][0]:.2f}, {100*v['interval'][1]:.2f}]"

def main():
    out=folder('confirmation'); a=read(out/'analysis.json'); dev=read(folder('development')/'selection.json')
    cal=read(folder('calibration')/'record.json'); geo=read(out/'geometry.json'); resource=read(out/'resources.json')
    assert read(out/'audit.json')['status']=='passed'
    historical=read(ROOT/'research/exp008_historical_hashes.json')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in historical.items())
    v=a['primary']['ordinary']; hard=a['profiles']['16_per_pair_16_False']
    summary=f"Adult calibration minus ordinary tuning: {fmt(v)} pp (98.333333% interval). Transfer classification: {a['transfer_classification']}; informative-benchmark gate {'passed' if a['informative_gate']['passed'] else 'failed'}."
    interpretation=('The bounded retention limitation transfers to this independently reconstructed adult subcircuit: redistributing participation did not yield a practically useful mean-retention gain beyond strong ordinary tuning. This extends the empirical finding beyond the larval anatomy, but does not establish its causal explanation or generalization to other task families.' if a['informative_transfer'] else 'The transfer prediction is not established as informative equivalence. Interpret the reported interval and benchmark gate separately; do not turn a negative or inconclusive test into a general causal claim.')
    names={'baseline_high':'Uncalibrated K48','ordinary':'Ordinary tuning','homeostasis':'Calibrated K48','sham':'Optimized shuffled offsets','random_ordinary':'Random ordinary','random_homeostasis':'Random calibrated','direct':'Direct input','oracle':'Identity oracle','fixed_homeostasis':'Calibrated at reference eta/T','fixed_sham':'Shuffled at reference eta/T','matched_sham':'Exact-multiset sham'}
    guards=sum(v['lower']>-.03 for row in a['guardrails'].values() for v in row.values())
    lines=['# EXP-008: adult circuit transfer — audited results','',
        f"2026-09-14. Eight development and {a['blocks']} fresh confirmation blocks completed. Nine preflight tests, exact full validation replay, all checkpoint audits and one full-block replay per stage passed. Historical EXP-002–007 scientific sources/protocols/results match their preservation hashes.",'',
        '[Protocol](EXP-008-protocol.md) · [Analysis](../results/exp008_confirmation/analysis.json) · [Anatomy](../results/exp008_anatomy/record.json) · [Run record](../research/runs/EXP-008-confirmation.json) · [Profiles](../results/exp008_confirmation/profiles.csv) · [Memory age](../results/exp008_confirmation/memory_age.csv)','',
        '## Transfer decision','',summary,'',interpretation,'',
        'The prediction was practical retention equivalence within +/-3 pp, based on EXP-007. Statistical equivalence requires the whole simultaneous interval inside the band; absence of significance is insufficient. Useful benefit requires a lower bound above +3 pp, harm an upper bound below -3 pp. Intervals crossing these boundaries are inconclusive. A ceiling/floor or learnability failure prevents treating equivalence as informative transfer.','',
        f"The joint intervention-success gate is {'met' if all(v['interval'][0]>.03 for v in a['primary'].values()) and guards==12 else 'not met'}. {guards}/12 adaptation/tail noninferiority guardrails pass; a failed noninferiority test does not establish harm. In this run the three worst-pair guardrails fail, so preserving the performance of the worst memories is not established.",'',
        '| Comparator | Calibrated minus comparator retention [98.333333% interval], pp |','|---|---:|']
    for m,v in a['primary'].items():lines.append(f'| {names[m]} | {fmt(v)} |')
    lines+=['','## What was transferred','',
        'Adult hemibrain:v1.1 main-calyx contacts from 104 connected monoglomerular PNs to 590 gamma-main KCs: 4,878 positive edges, 85,151 contacts. Subtype/ROI/ID filters were chosen before learning. Raw contacts were normalized per KC. The source archive contains non-cropped traced neurons; unknown residual completeness and the unused author positional exclusion list are disclosed in the protocol.','',
        'The intervention procedure was transferred with new offsets fitted on 4,096 unlabeled development-calibration observations, checked on a separate 4,096, then frozen. No adult evaluation inputs or rewards calibrated offsets. Activity density maps larval K4/K6 to adult K32/K48; sparse learning rates scale eightfold to preserve nominal update scale. Inputs use 26/104 active coordinates and 5/16 shared coordinates. Direct rates adjust for its input norm. This is procedure transfer with declared adapters, not reuse of larval fitted parameters.','',
        'The online learner and two synthetic outputs remain. This tests an independently reconstructed animal/adult subcircuit within the same associative assay. It neither isolates anatomy as the causal difference nor establishes physiological homeostasis, cross-task generalization, or an anatomical population effect. Synthetic PN coordinates are independent even when biological PNs share glomerular identity.','',
        '## Frozen development choices','',
        'Each method received 32 unique rewarded candidates per condition across eight development blocks. Null/sham methods average three fixed replicas, so simulation costs differ. One global configuration was selected using five equally weighted outcomes across both loads, similarities and exposure regimes. The K48 reference reuses ordinary search; when ordinary selects it, those contrasts are identical, not independent replications.','',
        '| Method | K | Strength | Eta | Temperature |','|---|---:|---:|---:|---:|']
    for m in REPORT[:8]:
        c=dev['settings'][m];lines.append(f"| {names[m]} | {c['k']} | {c['strength']} | {c['eta']:.9f} | {c['temperature']} |")
    lines+=['',f"Precision rule: maximum development paired SD {dev['precision']['max_sd']:.5f}; uncapped n={dev['precision']['uncapped_n']}; frozen n={a['blocks']}; projected halfwidth {100*dev['precision']['projected_halfwidth']:.2f} pp. This projection was not a guarantee. Confirmation was not extended.",'',
        '## Primary condition and adequacy','',
        'Sixteen high-similarity cue pairs, 128 presentations per pair, preferred-choice probabilities. Mean percentages below are descriptive; primary/guardrail intervals govern inference.','',
        '| Method | Retention | New learning | Worst pair | Noisy retention | Reversal | Unchanged |','|---|---:|---:|---:|---:|---:|---:|']
    for m in REPORT:lines.append('| '+names[m]+' | '+' | '.join(f"{100*hard[m][k]['mean']:.2f}" for k in ('retention','new_learning','worst_pair','noise_retention','reversal','unchanged'))+' |')
    lines+=['','| Informative-benchmark check | Pass |','|---|---|']
    for k,v in a['informative_gate'].items():lines.append(f'| {k} | {v} |')
    ordinary_interval=hard['ordinary']['retention']['interval']
    lines+=['',f"Ordinary retention has a descriptive95% interval of [{100*ordinary_interval[0]:.2f}, {100*ordinary_interval[1]:.2f}]%. Its upper bound is close to the prespecified95% ceiling threshold, which it passes. This supports the written adequacy decision, not unlimited headroom or generalization to heavier loads."]
    lines+=['','The gate requires ordinary acquisition lower95% >80%, oracle retention/acquisition lower95% >95%, and ordinary retention interval wholly between 55% and 95%. No parameter, task or sample change followed this assessment. Only loads4/16 were tested: no certified-capacity threshold is claimed.','',
        '## Participation and diagnostic interpretation','',
        '| Method | Unused presented cells (%) | Effective presented cells | Noise stability | Cross-memory cosine |','|---|---:|---:|---:|---:|']
    for m in ('baseline_high','ordinary','homeostasis','sham','matched_sham','random_ordinary','direct'):
        g=geo['16_per_pair_16_False_'+m]
        lines.append(f"| {names[m]} | {100*g['unused_presented']['mean']:.2f} | {g['effective_presented']['mean']:.2f} | {g['noise_stability']['mean']:.3f} | {g['cross_memory_cosine']['mean']:.3f} |")
    lines+=['','Effective participation is `(sum counts)^2/sum(counts^2)` over presented acquisition observations, not anatomical cell count or memory capacity. Geometry, clipping, update norms and old-pair margin changes are descriptive. [Paired geometry contrasts](../results/exp008_confirmation/geometry_contrasts.json) do not establish causal mediation.','',
        '## Exact-multiset control','',
        'Three independently shuffled copies of the selected homeostasis offset vector, with identical K/eta/T, were prespecified and frozen before confirmation. Values are homeostasis minus exact-multiset sham; descriptive95% intervals.','',
        '| Outcome | Difference [95% interval], pp |','|---|---:|']
    for k,v in a['exact_multiset_contrasts'].items():lines.append(f'| {k} | {fmt(v)} |')
    if dev['settings']['homeostasis']==dev['settings']['sham']:
        lines+=['','Development selected identical settings for optimized sham and homeostasis, so optimized sham and the exact-multiset sham coincide here. These are the same control, not independent corroborating evidence.']
    lines+=['','## Adaptation and tail guardrails','',
        '| Comparator | Outcome | Mean difference (pp) | Simultaneous lower bound (pp) | Pass |','|---|---|---:|---:|---|']
    for m,row in a['guardrails'].items():
        for k,v in row.items():lines.append(f"| {names[m]} | {k} | {100*v['mean']:.2f} | {100*v['lower']:.2f} | {v['lower']>-.03} |")
    lines+=['','One-sided alpha .05/12; all lower bounds must exceed -3 pp. Inference is conditional on this adult anatomy and three fixed null anatomies; task blocks are independent units. Bootstrap intervals are approximate.','',
        '![Larval and adult retention contrasts](../results/exp008_confirmation/transfer_comparison.png)','',
        '![Adult retention and worst-memory profiles](../results/exp008_confirmation/retention_per_pair.png)','',
        'Bands are descriptive pointwise95% intervals. [Fixed-total-exposure plot](../results/exp008_confirmation/retention_total.png).','',
        '## Resources and reproducibility','',
        '| Stage | Block CPU seconds | Summed worker-wall seconds | Peak worker MB | Checkpoint MB |','|---|---:|---:|---:|---:|']
    for stage,r in resource.items():lines.append(f"| {stage} | {r['cpu_seconds']:.2f} | {r['summed_worker_wall_seconds']:.2f} | {r['peak_worker_bytes']/1e6:.2f} | {r['checkpoint_bytes']/1e6:.2f} |")
    lines+=['',f"Calibration took {cal['wall_seconds']:.2f} wall seconds. Table excludes full replay/audits/reporting; summed worker time is not campaign elapsed time. Local bundled Python/NumPy, three CPU workers, no paid compute. Sparse models use 1,180 learned weights; direct input208; calibrated/sham models additionally store590 offsets (589 independent after centering) and require unlabeled fitting. Oracle uses privileged identity and is only a task-validity control.",'',
        'Source/runtime/anatomy/calibration contracts, task digests, per-block checksums, exact replay and metric recomputation are retained. [Validation](../research/exp008_validation.json), [development freeze](../results/exp008_development/contract.json), [confirmation freeze](../results/exp008_confirmation/contract.json), [historical preservation](../research/exp008_historical_hashes.json). No performance-based exclusions or confirmation-driven changes.','',
        '## Branch decision','',
        'Interpret the transfer classification with adequacy, geometry and tail results. Even informative equivalence extends a bounded limitation across two anatomical settings rather than proving the explanation or universal uselessness of homeostasis. Growth still requires evidence that new features address a representation limit. Rewiring requires predictive collision evidence. Evolution remains conditional on a held-out task-family battery robust to exploitation by selection; this same-assay adult run does not meet that condition alone.']
    (ROOT/'experiments/EXP-008-results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write(out/'completion.json',dict(status='completed',summary=summary,historical_files_verified=len(historical),report_sha256=hashlib.sha256((ROOT/'experiments/EXP-008-results.md').read_bytes()).hexdigest()))
    print(summary)

if __name__=='__main__':main()
