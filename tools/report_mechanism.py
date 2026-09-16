"""Tables and provenance for the audited EXP-005 campaign; no new selection."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import time
import numpy as np
from exp005.campaign import read, folder
from exp002.data import ROOT, sha256


def fmt(row, scale=100):
    return f"{scale*row['mean']:+.2f} [{scale*row['interval'][0]:+.2f}, {scale*row['interval'][1]:+.2f}]"


def main():
    target=folder('evaluation')
    audit=read(target/'audit.json')
    assert audit['status']=='passed'
    a=read(target/'analysis.json')
    contract=read(target/'contract.json')
    selection=read(folder('development')/'selection.json')
    lines=['# EXP-005: activity mechanism at 73 cells — audited results','',
        '2026-09-13. Six development blocks and 32 fresh held-out evaluation blocks completed; 120 and 640 distinct reset episodes respectively. Evaluation compares twelve settings on each episode (7,680 configuration-episodes). No sample extension or evaluation-driven tuning.', '',
        '[Prospective protocol](EXP-005-protocol.md), [full analysis](../results/exp005_evaluation/analysis.json), [audit](../results/exp005_evaluation/audit.json), [run record](../research/runs/EXP-005-evaluation.json).', '',
        'The K6 retention advantage survives ordinary learning-rate adjustment, both nominal update matches, norm matching and the equal eight-candidate tuning budget. Historical K6-K4 is +4.25 pp; tuned K6-K4 is +3.78 pp [2.39, 5.27] (primary 98.75%). The positive direction is supported, but the interval crosses the prespecified +3 pp practical threshold: an effect larger than 3 pp is not established. Tuned equivalence within ±3 pp is not established either.', '',
        'The measured same-cue update coefficients are nearly equal for tuned K4/K6 (.33258/.33276), with similar clipping (2.29%/2.56%) and old-cue perturbation magnitudes (.04490/.04523). Thus simply making updates gentler is insufficient to account for the residual benefit. The fixed-action validation shows exact compensation is possible for amplitude alone when initial weights and eta are rescaled consistently; it does not prove K4 and K6 representations are equivalent.', '',
        'K6 shows more repeatable noisy-cue responses (cosine .9206 versus .8376), and fewer unused cells per task block (15.28% versus 37.16%). Between-cue overlap also rises (.1756 versus .1622): K6 does not reduce between-cue overlap on this measure. Better response stability and broader participation are plausible contributors, not uniquely identified causal mediators.', '',
        'Retention is not bought by a demonstrated new-learning deficit: tuned K6 improves early intervening-cue learning +1.54 pp [0.72, 2.33], late learning +0.60 [0.11, 1.13], and early reversal +1.96 [0.53, 3.44] (secondary 95%). The independent intervening-cue probe is +0.89 [-0.04, 1.73], which is uncertain in direction and rules out a 3 pp deficit at this exploratory coverage. K6 begins interference somewhat ahead too; before/after contrasts below separate that from subsequent forgetting.', '',
        'The amplitude factorial also limits the claim: using six winners at the larger 2.5 amplitude produces acquisition, new-learning and noise costs, with an uncertain retention advantage. More activity is not uniformly better. The supported candidate is a calibrated K6 representation in this assay.', '',
        '## Primary retention contrasts', '',
        'All differences are six minus four winners, in percentage points. Each primary interval has 98.75% coverage (Bonferroni family of four); paired bootstrap resamples 32 task blocks, not individual episodes. Practical band ±3 pp.', '',
        '| Comparison | Retention difference [interval], pp |', '|---|---:|']
    for name in ('historical','slow_matched','fast_matched','tuned'):
        lines.append(f"| {name} | {fmt(a['contrasts'][name]['retention_after'])} |")
    lines+=['', 'Selected on development only: '+ '; '.join(f"K{c['k']}: eta={c['eta']:.8g}, T={c['temperature']:g}" for c in selection['settings'])+'. The tuned contrast coincides with the slow matched contrast in this campaign; these are not independent replications.', '',
            '## Capability guardrails and amplitude controls', '',
            'Secondary exploratory 95% intervals, pp. Retention for the four primary rows above retains its primary coverage in the saved analysis.', '',
            '| Comparison | Acquisition | Early reversal | New learning, early | New learning, late | New probe | Noise .3 |',
            '|---|---:|---:|---:|---:|---:|---:|']
    for name,c in a['contrasts'].items():
        lines.append('| '+name+' | '+' | '.join(fmt(c[k]) for k in ('acquisition','early_reversal','new_early','new_late','new_probe','noise_03'))+' |')
    lines+=['','| Amplitude/norm control | Retention difference [95% interval], pp |','|---|---:|']
    for name in ('equal_low_amplitude','equal_high_amplitude','low_norm','high_norm'):
        lines.append(f"| {name} | {fmt(a['contrasts'][name]['retention_after'])} |")
    lines+=['','| Comparison | Before-interference difference, pp | Difference in before-to-after change, pp |','|---|---:|---:|']
    for name in ('historical','slow_matched','fast_matched','tuned'):
        lines.append(f"| {name} | {fmt(a['contrasts'][name]['retention_before'])} | {fmt(a['contrasts'][name]['retention_change'])} |")
    lines+=['','## Absolute profiles','','Means are probabilities; full intervals and block values are in the analysis. New probe assesses the intervening pair immediately after training it.','','| Setting | Before interference | After interference | Reversal | New learning, late | New probe | Noise .3 |','|---|---:|---:|---:|---:|---:|---:|']
    for id,p in a['profiles'].items():
        lines.append('| '+id+' | '+' | '.join(f"{p[k]['mean']:.4f}" for k in ('retention_before','retention_after','early_reversal','new_late','new_probe','noise_03'))+' |')
    lines+=['','## Measured update mechanics','','Values averaged over online learning; old-cue change is RMS predicted-value change on clean old prototypes during interference. These are descriptive diagnostics, not mediation estimates.','','| Setting | Mean absolute selected q change | Mean actual/error coefficient | Clipped updates, % | Old-cue change during interference |','|---|---:|---:|---:|---:|']
    for id,p in a['profiles'].items():
        lines.append(f"| {id} | {p['selected_update_abs']['mean']:.5f} | {p['effective_coefficient']['mean']:.5f} | {100*p['clipping_fraction']['mean']:.2f} | {p['old_update_interference']['mean']:.5f} |")
    lines+=['','## Representation geometry','','Cosine overlaps; same-cue repeats use independent noise draws. These measures use equal-amplitude binary winner masks, so they describe which cells participate rather than activity scale.','','| K | Within-cue cosine | Between-cue cosine | Old/new prototype cosine | Never used in whole block, % |','|---|---:|---:|---:|---:|']
    for k,g in a['geometry'].items():
        lines.append(f"| {k} | {g['same_cue_cosine']['mean']:.4f} | {g['between_cue_cosine']['mean']:.4f} | {g['old_new_cosine']['mean']:.4f} | {100*a['block_never_active'][k]['mean']:.2f} |")
    validation=read(ROOT/'research/exp005_validation.json')
    resources={}
    for stage in ('development','evaluation'):
        directory=folder(stage)
        cc=read(directory/'contract.json')
        rows=[read(directory/f'block_{b}.json') for b in cc['blocks']]
        resources[stage]={'wall_seconds':sum(read(p)['wall_seconds'] for p in directory.glob('invocation_*.json')),
            'summed_worker_cpu_seconds':sum(r['cpu_seconds'] for r in rows),
            'peak_individual_worker_bytes':max(r['peak_worker_memory_bytes'] for r in rows),
            'retained_bytes':sum(p.stat().st_size for p in directory.rglob('*') if p.is_file()),
            'audit_wall_seconds':read(directory/'audit.json')['wall_seconds']}
    lines+=['','## Validation and resources','',f"{validation['tests_run']} preflight tests passed. Historical-engine comparison, scalar clipped recurrence, exact compensated-amplitude replay including clipping, exact winner/norm checks, independent streams, frozen chance and completed-block resume/corruption rejection passed. Both stage audits verified all raw hashes, regenerated all task identities, recomputed metrics/analysis and exactly replayed their first complete block. No failed campaign, exclusions or nonfinite values.", '',
        'The first preflight attempt found a JSON-envelope reader mismatch in the new checkpoint code; it was repaired before campaign learning began. Scientific source and protocol were then frozen. No independent reviewer or subagent was used.', '',
        'Protocol deviation: the preflight stream-separation test instantiated development block 100/episode 0 and evaluation block 1000/episode 0 before freeze, comparing only their task hashes. No learner ran on those inputs, no performance was inspected, and they did not enter tuning before the declared stages. Thus the literal promise to defer all evaluation input generation until selection was not met, although evaluation performance remained held out. No episode was removed or replaced, and the sample was not extended.', '',
        '| Stage | Run wall seconds | Summed worker CPU seconds | Maximum individual worker MiB | Retained MiB | Audit seconds |','|---|---:|---:|---:|---:|---:|']
    for stage,r in resources.items():
        lines.append(f"| {stage} | {r['wall_seconds']:.1f} | {r['summed_worker_cpu_seconds']:.1f} | {r['peak_individual_worker_bytes']/2**20:.1f} | {r['retained_bytes']/2**20:.1f} | {r['audit_wall_seconds']:.1f} |")
    lines+=['','Three local CPU processes; CPython '+contract['python']+', NumPy '+contract['numpy']+'. Worker peak memory is not aggregate concurrent memory. These measurements concern the current session machine, not the colleague workstation.','',
        '## Scope and next step','',
        'This is one larval-derived representation and the existing synthetic associative assay. Population remains 73 and weights reset between episodes. More repetitions are not more persistent memories. Nominal update matching does not fix clipping, errors or chosen-action histories. The tuning budget is bounded; it does not establish global optima. Representation diagnostics cannot identify a unique causal mediator.', '',
        'Proceed to [EXP-006 persistent-memory load/similarity design](EXP-006-design.md), finalize and validate its confirmation protocol, then compare native K4/K6, direct-input delta and randomized sparse N73 learning under explicitly matched training exposure. Homeostasis follows a measured participation/capacity limitation; growth and circuit transfer keep their roadmap gates. EXP-006 has not been run.','']
    (ROOT/'experiments/EXP-005-results.md').write_text('\n'.join(lines),encoding='utf-8')
    files={p.relative_to(ROOT).as_posix():{'sha256':sha256(p),'bytes':p.stat().st_size} for p in target.iterdir() if p.is_file()}
    run={'experiment':'EXP-005','protocol_version':'1.0','status':'completed_and_audited',
         'created_utc':contract['created_utc'],'completed_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
         'code_commit':'uncommitted workspace; exact source hashes in contract', 'source_hashes':contract['source'],
         'environment':{k:contract[k] for k in ('python','numpy','platform','executable')},
         'hardware_id':'current_session_not_colleague_target','configuration_sha256':sha256(target/'contract.json'),
         'seed_derivation':'PCG64 SeedSequence [6, stage_index, block, 0, component, *suffix]; stage 0 validation, 1 development, 2 evaluation',
         'planned_blocks':32,'completed_blocks':32,'episodes':640,'configuration_episodes':7680,
         'checkpoint_unit':'complete block','files':files,'resources':resources,'validation':validation['status'],
         'audit':audit,'exclusions':[],'campaign_failures':[],'metrics_and_uncertainty':'results/exp005_evaluation/analysis.json',
         'protocol_deviations':['Preflight instantiated one development and one evaluation task for hash-only stream separation before freeze; no learner or performance inspection. Evaluation performance remained held out; no exclusions or replacement.'],
         'interpretation':'See experiments/EXP-005-results.md','limitations':'One circuit, reset assay, bounded tuning; no capacity or unique mediator claim',
         'follow_up':'EXP-006 persistent-memory load/similarity protocol and validation'}
    (ROOT/'research/runs/EXP-005-evaluation.json').write_text(json.dumps(run,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__': main()
