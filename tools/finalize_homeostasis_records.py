"""Build numerical EXP-007 handoff from audited artifacts; no learning runs."""
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from exp007.campaign import ROOT, folder, read, write, REPORT, NAMES
from exp002.data import sha256


def fmt(v): return f"{100*v['mean']:.2f} [{100*v['interval'][0]:.2f}, {100*v['interval'][1]:.2f}]"


def main():
    out = folder('confirmation'); a = read(out/'analysis.json'); c = read(out/'contract.json')
    dev = read(folder('development')/'selection.json'); geo = read(out/'geometry.json')
    cal = read(folder('calibration')/'record.json'); resources = read(out/'resources.json')
    geometry_contrasts = read(out/'geometry_contrasts.json')['values']
    matched = read(ROOT/'results/exp007_matched_sham/analysis.json')
    assert matched['status'] == 'passed'
    assert read(out/'audit.json')['status'] == 'passed'
    hard = a['profiles']['6_per_pair_16_False']
    practical = all(v['interval'][0] > .03 for v in a['primary'].values())
    guards = all(v['lower'] > -.03 for g in a['guardrails'].values() for v in g.values())
    guard_count = sum(v['lower'] > -.03 for g in a['guardrails'].values() for v in g.values())
    effect = a['primary']['ordinary']; lo, hi = effect['interval']
    if lo > .03:
        interpretation = 'Homeostasis establishes a retention gain above the three-point practical margin versus ordinary tuning.'
    elif lo > -.03 and hi < .03:
        interpretation = 'Homeostasis and ordinary tuning are practically equivalent within the prespecified ±3-point retention band in the primary condition.'
    elif hi < .03:
        interpretation = 'The primary interval rules out a retention gain as large as three points versus ordinary tuning; equivalence or harm requires separate inspection of its lower bound.'
    elif lo > 0:
        interpretation = 'A positive retention effect is established versus ordinary tuning, but an effect larger than three points is not established.'
    else:
        interpretation = 'The primary comparison with ordinary tuning is inconclusive about direction and a practically useful gain.'
    summary = f"{interpretation} Calibrated K6 retains {100*hard['homeostasis']['retention']['mean']:.2f}% versus {100*hard['ordinary']['retention']['mean']:.2f}% for ordinary tuning; difference {fmt(effect)} pp (98.333333%)."
    names = {'baseline6': 'Uncalibrated K6', 'ordinary': 'Ordinary K/eta/T tuning', 'homeostasis': 'Calibrated K6', 'sham': 'Shuffled offsets', 'random_ordinary': 'Random ordinary', 'random_homeostasis': 'Random calibrated', 'direct': 'Direct input', 'oracle': 'Identity oracle', 'fixed_homeostasis': 'Calibrated, K6-reference eta/T', 'fixed_sham': 'Shuffled, K6-reference eta/T'}
    lines = ['# EXP-007: participation homeostasis — audited results', '',
        f"2026-09-14. Eight development blocks and {a['blocks']} fresh confirmation blocks completed. Ten preflight tests passed; full validation replay, checkpoint audits and one full-block replay in each stage passed. Historical experiments remain unchanged.", '',
        '[Prospective protocol](EXP-007-protocol.md) · [analysis](../results/exp007_confirmation/analysis.json) · [geometry](../results/exp007_confirmation/geometry.json) · [profiles](../results/exp007_confirmation/profiles.csv) · [memory-age table](../results/exp007_confirmation/memory_age.csv) · [run record](../research/runs/EXP-007-confirmation.json)', '',
        '## Prespecified conclusion', '', summary, '',
        f"The complete practical-success gate is {'met' if practical and guards else 'not met'}: a retention advantage above 3 percentage points against all three primary comparators is {'established' if practical else 'not established'}, and {guard_count} of 12 adaptation/tail noninferiority guardrails pass. The three worst-pair guardrails fail to establish preservation within the allowed margin; this does not prove harm. Equivalence above follows from the interval fitting inside the prespecified band, not simply from a nonsignificant difference.", '',
        'The primary endpoint is final preferred-choice probability at16 similar pairs,128 presentations per pair, noise .1. Differences are homeostasis minus comparator, in percentage points; intervals have98.333333% coverage for the three-contrast family. The practical band is ±3 points.', '',
        '| Comparator | Retention difference [interval], pp |', '|---|---:|']
    for m, v in a['primary'].items(): lines.append(f'| {names[m]} | {fmt(v)} |')
    lines += ['', 'Native K6 reference is selected from the16 K6 candidates inside the ordinary32-candidate search. If ordinary tuning selects this same configuration, its primary contrast equals the K6-reference contrast; they are not independent replications.', '',
        '## Stronger ordinary tuning and calibration', '',
        'Each experimental method received 32 unique rewarded candidate settings per development condition. Ordinary methods searched K4/K6; calibrated methods searched two partial targets at fixed K6. Sham/null candidates average three replica evaluations, so candidate-search opportunities are matched but simulation costs are not. These are averages of separate learners, not a three-model ensemble at deployment. The shared eight-rate grid extends from 0.0002083333 through 0.015, with temperatures .1/.2. Direct input received 16 geometric rates over the same endpoints x two temperatures. One global setting per method was selected; no condition-specific or confirmation-driven tuning.', '',
        '| Method | K | Calibration strength | Learning rate | Temperature |', '|---|---:|---:|---:|---:|']
    for m in REPORT[:8]:
        v = dev['settings'][m]
        lines.append(f"| {names[m]} | {v['k'] or '—'} | {v['strength']} | {v['eta']:.9f} | {v['temperature']} |")
    selected_fit = cal['fits'][f"p0_l{dev['settings']['homeostasis']['strength']}"]
    lines += ['', 'The newly available lower learning-rate boundary was tested but not selected. Native ordinary and calibrated K6 both chose .006667. Direct input selected the upper .015 boundary, so its optimum is still bounded by the search; no global optimization claim is warranted.', '', f"Selected native calibration uses a bound of {selected_fit['bound']:.6f} in normalized drive units; {100*selected_fit['clamp_fraction']:.2f}% of offsets reach that bound. This is bounded partial compensation, not proof of fully equalized participation or physiological thresholds. Offset fitting used 4096 unlabeled inputs; a distinct 4096-input pool measured calibration generalization. Offsets were frozen before rewarded development and unchanged during confirmation and shift testing.", '',
        '## Joint capability profile', '',
        'Hard condition; mean preferred-choice percentages. Below-chance is the fraction of pairs with final preferred-choice probability below .5. Worst-pair minima are computed within each replicate before averaging replicas and task blocks. These profiles are descriptive; use the primary and guardrail intervals for confirmatory claims.', '',
        '| Method | Retention | Worst pair | New learning | Noise .3 | Reversal | Unchanged after reversal | Pairs below chance |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for m in REPORT:
        vals = [hard[m][metric]['mean']*100 for metric in ('retention', 'worst_pair', 'new_learning', 'noise_retention', 'reversal', 'unchanged', 'below_chance')]
        lines.append('| '+names[m]+' | '+' | '.join(f'{v:.2f}' for v in vals)+' |')
    lines += ['', '## Adaptation and tail guardrails', '',
        'Homeostasis minus comparator, pp. Each lower bound is one-sided at alpha .05/12; passing requires lower bound strictly above−3. Failure to pass does not by itself establish harm.', '',
        '| Comparator | Outcome | Mean difference | Simultaneous lower bound | Pass |', '|---|---|---:|---:|---|']
    for m, vals in a['guardrails'].items():
        for metric, v in vals.items(): lines.append(f"| {names[m]} | {metric} | {100*v['mean']:.2f} | {100*v['lower']:.2f} | {'yes' if v['lower'] > -.03 else 'no'} |")
    lines += ['', '## Participation and interference diagnostics', '',
        'Hard condition. Effective participation=(sum cell counts)^2/sum squared cell counts. Presented counts include both alternatives; chosen counts include actual acquisition updates only. Pair-margin perturbation measures absolute value-difference changes of previously learned clean cue pairs per new update, averaged across old pairs. These are descriptive diagnostics, not proof of mediation.', '',
        '| Method | Unused presented (%) | Effective presented cells | Unused chosen (%) | Noise stability | Cross-memory cosine | Absolute old-pair margin change |', '|---|---:|---:|---:|---:|---:|---:|']
    for m in ('baseline6', 'homeostasis', 'sham', 'random_ordinary', 'random_homeostasis'):
        g = geo['6_per_pair_16_False_'+m]
        vals = [g[k]['mean'] for k in ('unused_presented', 'effective_presented', 'unused_chosen', 'noise_stability', 'cross_memory_cosine', 'old_pair_margin_abs_change')]
        lines.append(f'| {names[m]} | {100*vals[0]:.2f} | {vals[1]:.2f} | {100*vals[2]:.2f} | {vals[3]:.4f} | {vals[4]:.4f} | {vals[5]:.6f} |')
    lines += ['', 'Participation changed without a useful retention gain. On the hard condition, the unused presented-cell fraction falls from 40.88% to 35.66%; its paired change is '+fmt(geometry_contrasts['unused_presented'])+' pp (descriptive 95%). Effective participation increases by '+f"{geometry_contrasts['effective_presented']['mean']:.3f}"+' cells, while noisy-to-clean cosine changes by '+fmt(geometry_contrasts['noise_stability'])+' percentage points. Cross-memory cosine also decreases, but the paired interval for absolute old-pair margin perturbation includes zero; reduced average overlap did not establish reduced update interference. Clean and noisy winner margins narrow. These results are consistent with a recruitment/stability tradeoff, not uniquely identified causal mediation. [Paired geometry diagnostics](../results/exp007_confirmation/geometry_contrasts.json).', '',
        'Both calibrated and uncalibrated K6 keep total activity 10 and squared norm 100/6. Actual update errors, choices and clipping can differ. Selected fixed-setting contrasts reuse the reference K6 learning rate/temperature, with no extra tuning:', '',
        '| Matched comparison versus K6 reference | Retention difference [95% interval], pp |', '|---|---:|']
    for m in ('fixed_homeostasis', 'fixed_sham'): lines.append(f"| {names[m]} | {fmt(hard['fixed_contrasts'][m]['retention'])} |")
    lines += ['', '### Exact assignment control', '',
        'Development selected different strengths for homeostasis (.25) and the optimized sham (.5). Before confirmation, a [transparent addendum](EXP-007-matched-sham-addendum.md) froze an additional no-search control using exactly the homeostasis offset multiset and eta/T, with three shuffled assignments. Original primary comparisons and sample size were unchanged. Both the matched control and homeostasis use the same hard-condition streams; three replicas are averaged within blocks. This is a development-informed addition, not a confirmation-driven analysis choice. [Supplemental audited results](../results/exp007_matched_sham/analysis.json).', '',
        '| Outcome | Homeostasis minus exact-multiset sham [95% interval], pp |', '|---|---:|']
    for name in NAMES: lines.append(f"| {name} | {fmt(matched['descriptive_95'][name])} |")
    lines += ['', '## Certified load', '',
        'Largest tested load whose mean retention and immediate acquisition lower bounds exceed .80, with all lower loads also passing. Bonferroni family covers224 checks across seven experimental reported models, two similarities, two regimes, four loads and two endpoints; one-sided approximate bootstrap bounds. This does not certify every memory or post-reversal performance. Failure to certify is not proof of subthreshold population mean.', '',
        '| Method | Overlap2,128/pair | Overlap6,128/pair | Overlap2,512 total | Overlap6,512 total |', '|---|---:|---:|---:|---:|']
    for m in REPORT[:7]:
        vals = [a['capacity'][f'{m}_s{s}_{r}']['certified_load'] for r in ('per_pair', 'total') for s in (2, 6)]
        lines.append('| '+names[m]+' | '+' | '.join(str(v) if v else 'none certified' for v in vals)+' |')
    lines += ['', '![Retention and worst-memory profiles](../results/exp007_confirmation/retention_per_pair.png)', '',
        'Shading is pointwise descriptive 95% uncertainty. Horizontal lines show the .80 mean-retention threshold and .50 chance for the worst-pair panel; they do not define confidence-bound certification. [Fixed-total-exposure figure](../results/exp007_confirmation/retention_total.png).', '',
        '## Held-out input-distribution shift', '',
        'The first 20 PN channels are attenuated by .5 throughout training, reversal and probes; calibration is unchanged. The gain multiplies the already clipped noisy observations, including their noise, and clean prototypes. It is invertible at the PN level, so raw input information is preserved; the sparse encoder and bounded learner can nevertheless respond differently. This clarifies the protocol\'s broad information-loss caveat. The condition was absent from development selection. It is one defined input shift, not cross-circuit validation. Values below are homeostasis-minus-comparator retention differences with descriptive 95% intervals at load16/128 per pair.', '',
        '| Overlap | Versus K6 reference | Versus ordinary tuning | Versus shuffled | Versus direct input |', '|---|---:|---:|---:|---:|']
    for s in (2, 6):
        prof = a['profiles'][f'{s}_per_pair_16_True']
        lines.append('| '+str(s)+' | '+' | '.join(fmt(prof['contrasts'][m]['retention']) for m in ('baseline6', 'ordinary', 'sham', 'direct'))+' |')
    lines += ['', 'Shifted full profiles, oracle checks and raw arrays are retained. Direct/oracle controls help distinguish encoder/learner sensitivity from task invalidity. No retuning on shift results is permitted.', '',
        '## Precision, verification and resources', '',
        f"Development's maximum primary paired SD was{dev['precision']['max_sd']:.5f}. The prospective inflation/precision rule requested{dev['precision']['uncapped_n']} blocks before rounding and bounds, producing{dev['confirmation_n']} confirmation blocks. Projected primary halfwidth was{100*dev['precision']['projected_halfwidth']:.2f} pp; this was an estimate from only eight development blocks, not a guaranteed interval width. Confirmation was not extended.", '',
        'Preflight covered scalar chosen updates and pair-margin changes, zero-offset encoder and complete sequence equivalence, calibration bounds/direction and shuffle invariants, lower-rate budgets, disjoint calibration streams, task overlap and shift transformation, persistent weights, read-only probes, null-graph invariants and oracle adequacy. Full validation and stage replays are exact. Every checkpoint passed checksum, regenerated task digest, weight continuity and metric recomputation audits. Three sham/null replicas are averaged inside each independent task block.', '',
        'Three fixed random anatomies were calibrated before development; uncertainty is conditional on these anatomies. Compared with EXP-006, both tuning and random-anatomy sampling design changed, so historical percentages are contextual rather than paired intervention estimates. No independent-agent review was performed.', '',
        '| Stage | Block CPU seconds | Summed worker-wall seconds | Peak worker MB | Checkpoint MB |', '|---|---:|---:|---:|---:|']
    for stage, v in resources.items(): lines.append(f"| {stage} | {v['cpu_seconds']:.2f} | {v['summed_worker_wall_seconds']:.2f} | {v['peak_worker_bytes']/1e6:.2f} | {v['checkpoint_bytes']/1e6:.2f} |")
    supplemental_records = [read(p) for p in (ROOT/'results/exp007_matched_sham').glob('block_*.json')]
    supplemental_wall = sum(v['wall_seconds'] for v in supplemental_records)
    lines += ['', f'These resource totals exclude full replay/audit, reporting and the supplemental control; summed worker time is not elapsed campaign time. Calibration took {cal["wall_seconds"]:.2f} wall seconds; supplemental-control block computation totals {supplemental_wall:.2f} summed worker-wall seconds, excluding its replay. Local bundled CPython/NumPy and three CPU workers were used. Plotting reads the existing cached Matplotlib installation under read-access escalation; no paid compute or separate workstation run.', '',
        'Sparse models retain 73 cells and 146 reward-learned weights. Calibrated/sham versions add 73 stored offsets, with 72 independent values after centering, and unlabeled fitting/data costs. Direct input uses 80 learned weights. Oracle receives privileged identity and is only a validation control. The baseline already normalizes each KC\'s total incoming projection weight to one; this experiment tests additional compensation of residual participation imbalance. No new biological dynamics, online homeostasis, gain intervention, growth or cross-circuit test was implemented.', '',
        'Priority3 is a bounded experimental test, not a universal verdict on homeostasis. Interpret practical effects, guardrails and transfer jointly before choosing the prediction to validate in another circuit. Do not tune or extend this completed confirmation sample.']
    text = re.sub(r'\b(above|all|at|have|the|ordinary|covers|descriptive|was|requested|producing|retains|through|within|overlap|load)(?=\d)', r'\1 ', '\n'.join(lines)+'\n')
    text = text.replace('pairs,128', 'pairs, 128').replace('above−3', 'above −3')
    (ROOT/'experiments/EXP-007-results.md').write_text(text, encoding='utf-8')
    for stage in ('development', 'confirmation'):
        path = ROOT/f'research/runs/EXP-007-{stage}.json'; record = read(path)
        record['reporting_sources'] = {name: sha256(ROOT/name) for name in ('tools/report_homeostasis.py', 'tools/finalize_homeostasis_records.py', 'tools/analyze_homeostasis_geometry.py')}
        record['matched_sham_sources'] = {name: sha256(ROOT/name) for name in ('tools/run_homeostasis_matched_sham.py', 'experiments/EXP-007-matched-sham-addendum.md')}
        record['matched_sham_analysis_sha256'] = sha256(ROOT/'results/exp007_matched_sham/analysis.json')
        record['artifact_hashes'] = {p.relative_to(ROOT).as_posix(): sha256(p) for p in folder(stage).glob('*') if p.is_file() and p.suffix in ('.json', '.csv', '.png')}
        record['calibration_record_sha256'] = sha256(folder('calibration')/'record.json')
        record['result_sha256'] = sha256(ROOT/'experiments/EXP-007-results.md')
        write(path, record)
    print('Wrote audited numerical handoff', flush=True)


if __name__ == '__main__': main()
