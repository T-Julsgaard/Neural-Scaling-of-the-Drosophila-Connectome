"""Create the EXP-010 report from audited frozen confirmation artifacts."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import run_readout_diagnostic as d
import numpy as np

def main():
    audit=d.read(d.OUT/'audit.json'); assert audit['passed'] and audit['blocks']==31
    a=d.read(d.OUT/'analysis.json'); selection=d.read(d.OUT/'selection.json')
    records=[d.read(p) for p in sorted((d.OUT/'confirmation').glob('block_*.json'))]
    contrasts={}
    for name,left,right in [('matched_chosen_fit_gap','offline_chosen_0','chosen'),('offline_feedback_access','offline_full_0','offline_chosen_0'),('remove_clipping','unclipped','supervised'),('ten_pass_replay','replay','supervised')]:
        vals=[np.mean([r['representations'][rep]['models'][left]['score'][0]-r['representations'][rep]['models'][right]['score'][0] for rep in ('native','calibrated')]) for r in records]
        contrasts[name]=d.interval(vals)
    detail={}
    for rep in ('native','calibrated','direct','direct_raw'):
        rs=[r['representations'][rep] for r in records]
        detail[rep]={k:float(np.mean([r[k] for r in rs])) for k in ('rank','clean_rank','condition','pair_distance','noise_deviation','norm2','scale')}
        detail[rep]['models']={mode:{k:float(np.mean([r['models'][mode][k] for r in rs])) for k in ('acquisition_old','forgetting_old','clips')} for mode in ('chosen','supervised','unclipped','replay')}
    interference={}
    for rep in ('native','calibrated'):
        for mode in ('chosen','supervised','unclipped','replay'):
            rows=[]
            for p in sorted((d.OUT/'confirmation').glob('block_*.npz')):
                with np.load(p) as z:
                    key=rep+'_'+mode
                    changes=z[key+'_changes']; ids=z[key+'_update_pair']
                    mask=(np.arange(16)[None,:]<ids[:,1,None]) & (ids[:,0,None]==0)
                    vals=changes[mask]
                    rows.append([np.mean(vals<0),np.mean(np.abs(vals)),np.mean(vals)])
            interference[rep+'_'+mode]=np.mean(rows,axis=0).tolist()
    resources={}
    for stage in ('validation','development','confirmation'):
        rs=[d.read(p) for p in (d.OUT/stage).glob('block_*.json')]
        resources[stage]=dict(blocks=len(rs),compute_wall_seconds=sum(r['wall_seconds'] for r in rs),cpu_seconds=sum(r['cpu_seconds'] for r in rs),peak_mib=max(r['peak_memory_bytes'] for r in rs)/1024**2,archive_mib=sum(p.stat().st_size for p in (d.OUT/stage).glob('*.npz'))/1024**2)
    d.write(d.OUT/'report_details.json',dict(geometry=detail,interference=interference,resources=resources,descriptive_contrasts=contrasts))
    def ci(x): return f"{100*x['mean']:.2f}% [{100*x['lower']:.2f}, {100*x['upper']:.2f}]"
    def gap(x): return f"{100*x['mean']:.2f} pp [{100*x['lower']:.2f}, {100*x['upper']:.2f}]"
    text=f'''# EXP-010 / Session B — where memory is lost

2026-09-15. Completed development, frozen prediction, 24 fresh confirmation tasks and deterministic audit. [Prospective protocol](EXP-010-protocol.md); [frozen selection](../results/exp010/selection.json); [numeric analysis](../results/exp010/analysis.json); [audit](../results/exp010/audit.json).

## Conclusion

**The tested sparse encoders retain useful linearly readable information that the fixed sequential online procedure fails to retain.** Averaging native and calibrated K6 within each task, offline full-outcome old-pair accuracy is {ci(a['offline'])}, compared with {ci(a['supervised'])} for fully supervised online delta. Paired gap: **{gap(a['primary_gap'])}**, 95% Student-t interval across 24 independent task blocks. Online acquisition-to-final loss is {gap(a['forgetting'])}. Prediction passed: **{a['prediction_passed']}**.

This favors a learning-procedure limitation in this fixed regime. Feedback access and clipping are contributors to examine separately; neither is a sufficient explanation of the offline versus supervised-online gap. At .3 observation noise, the same native/calibrated offline readouts recover only {100*np.mean([a['tables'][rep]['offline_full_0']['mean_scores'][3] for rep in ('native','calibrated')]):.2f}% of old preferences. Thus the evidence also retains a noise/representation/readout limitation; it does not support a universal learning-only account. It does not identify a unique optimal repair, establish irreversible encoder information loss, or explain the entire published compensation result. This is a familiar sequential-interference explanation; no novelty is claimed.

## Matched diagnostic and performance

Values below are deterministic correct preferences on 64 independent .1-noise observations per old pair (first 15 of 16). Chance ties count .5. They are not the historical stochastic-choice metric. Random rows average all three fixed degree/contact-controlled instances within each task. Core representations use mean squared feature norm 100/6; raw direct is a separate scale sensitivity.

| Frozen representation | Chosen online | Full online | Unclipped full online | Full online, 10 passes | Offline chosen only | Offline full |
|---|---:|---:|---:|---:|---:|---:|
'''
    for rep, models in a['tables'].items():
        text+='| '+rep+' | '+' | '.join(f"{100*models[m]['old_accuracy']['mean']:.2f}%" for m in ('chosen','supervised','unclipped','replay','offline_chosen_0','offline_full_0'))+' |\n'
    text+='\nNative/calibrated paired descriptive contrasts (95% intervals, no multiplicity adjustment):\n\n'
    for name,c in contrasts.items(): text+=f'- {name}: {gap(c)}.\n'
    text+='\nThe chosen-only fit gap supports a learning-procedure limitation even without unchosen outcomes. Full outcome access improves offline recovery, but it does not rescue this blocked online learner. Removing clipping and revisiting data each help, so the residual cause is a mixture of trajectory constraints and sequential fitting/schedule limitations; the relative contribution of convergence, objective choice, and schedule is not separately identified.\n'
    text+='''
The chosen-only offline fit uses exactly the archived chosen observations and stochastic +/-1 outcomes of the chosen online learner. Full offline and full online receive the same 4,096 observations/outcomes per task, in contrast to 2,048 chosen outcomes. Neither offline arm receives latent valence labels, expected rewards, clean targets or held-out noise during fitting. Both observations are visible for online choice, but unchosen outcomes cannot affect chosen updates; a test flips them and verifies identical learned weights. Full online receives cue 0 then cue 1 at each presentation. The second update uses the weights after the first; this declared sequence is not a batch gradient.

Offline fitting has storage, optimization and historical-data access advantages. Ten-pass replay revisits the same data and performs 40,960 updates, versus 4,096 for full online and 2,048 for chosen online. Thus offline is an explanatory diagnostic, not a fair online competitor or a proven capacity upper bound. The remaining contrast combines convergence to a ridge objective with fitting/schedule differences. Replay is a diagnostic intervention, not an optimized repair.

Two nonnegative opponent weight vectors with no upper bound can represent every signed linear vector: w = max(w,0) - max(-w,0). The decomposition exactly reproduces fitted predictions. Clipping can alter a learning trajectory without removing that representational possibility. Removing online clipping holds eta, data, initialization and order fixed. Offline fit residuals and an independent augmented least-squares fixture validate the numerical solution, not the sufficiency of every possible readout class. The archived `clips` counter counts negative coordinate proposals; for the unclipped arm these proposals are recorded but are not clipped.

## Acquisition, update interference, geometry and noise

| Representation | Online mode | Old acquisition | Final old accuracy | Acquisition loss |
|---|---|---:|---:|---:|
'''
    for rep in ('native','calibrated','direct'):
        for mode in ('chosen','supervised','unclipped','replay'):
            info=detail[rep]['models'][mode]; final=a['tables'][rep][mode]['old_accuracy']['mean']
            text+=f"| {rep} | {mode} | {100*info['acquisition_old']:.2f}% | {100*final:.2f}% | {100*info['forgetting_old']:.2f} pp |\n"
    text+='\nReplay acquisition is measured on its first pass; its final score is after ten passes.\n\n'
    text+='| Representation | Clean rank / 32 | Training rank | Nonzero condition | Mean squared norm | Clean pair distance | Noisy squared deviation |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for rep,r in detail.items():
        text+=f"| {rep} | {r['clean_rank']:.2f} | {r['rank']:.2f} | {r['condition']:.2f} | {r['norm2']:.3f} | {r['pair_distance']:.3f} | {r['noise_deviation']:.3f} |\n"
    text+='''
Ranks and condition numbers use float64 SVD and the NumPy matrix-rank tolerance; conditions refer to nonzero singular values, not infinite condition of a rank-deficient matrix. Geometry is descriptive. Native/calibrated/random sparse norm equality is exact, so compensation cannot improve this comparison simply by changing feature norm. Direct normalization uses training observations only. A scalar-rescaling fixture verifies the corresponding inverse-square rate relationship for unclipped delta. Here the raw-direct versus norm-matched-direct comparison deliberately shows sensitivity at a fixed eta; it is not a new representation.

Every update records the signed change to all 16 clean pair margins, its training pair and replay pass. The following summarizes first-pass updates on strictly older pairs; negative change weakens the correct preference, positive change strengthens it. All changes telescope to the final margin within the declared float32 trace tolerance. Acquisition/final noisy probes independently establish forgetting; interference is not inferred from participation correlation.

| Representation / learner | Harmful old-margin changes | Mean absolute change | Mean signed change |
|---|---:|---:|---:|
'''
    for k,v in interference.items(): text+=f'| {k} | {100*v[0]:.2f}% | {v[1]:.6f} | {v[2]:.6f} |\n'
    text+='\n| Representation | Offline full clean accuracy | Offline full .3-noise old accuracy | Offline full worst-pair .1 accuracy | Full online worst-pair .1 accuracy |\n|---|---:|---:|---:|---:|\n'
    for rep,m in a['tables'].items():
        s=m['offline_full_0']['mean_scores']; on=m['supervised']['mean_scores']
        text+=f'| {rep} | {100*s[4]:.2f}% | {100*s[3]:.2f}% | {100*s[2]:.2f}% | {100*on[2]:.2f}% |\n'
    text+='''
Worst-pair entries average each task's worst pair, rather than finding a worst pair after pooling. High-noise limitations can coexist with low-noise recoverability. Poor offline performance at any noise level would motivate a representation/noise or linear-readout/fitting limitation; it would not prove destruction of all useful information.

## Prospective prediction and falsification

Six development tasks selected one ridge penalty per representation/access from four candidates using development probes only. Development full offline mean was '''+f"{100*selection['development_offline']:.2f}% versus {100*selection['development_supervised']:.2f}% full online."+'''
The source-hashed selection was saved before any confirmation tasks were constructed. Fixed prediction: **native/calibrated mean offline old-pair accuracy >=80%; paired offline-minus-full-online lower 95% CI >5 pp; full-online acquisition-minus-final lower CI >5 pp.** Failure of any criterion would falsify this operational prediction. All 24 fresh tasks were retained; there was no sample extension or confirmation tuning. Descriptive contrasts have no multiplicity-adjusted discovery status. Inference is conditional on one larval anatomy and fixed nulls, not animals or a population of connectomes.

Session A motivates the update-dynamics hypothesis but its author model remains a fixed historical positive reference. The author multiplicative rule's odor-order invariance passed a validation fixture. No author-versus-delta causal comparison or raw-contact normalization factorial was run: the preliminary diagnostic already discriminated recoverability from the fixed online procedure, and its result does not justify attributing the A/B difference to any one architectural factor. Existing bounded .25 compensation was frozen; no stronger equalization or biological-homeostasis claim was introduced.

## Audit, resources and limitations

Five tests cover existing update equivalence, ridge solution and signed/nonnegative equivalence, orthogonal learning, scaling, outcome-access isolation, stream separation and multiplicative order invariance. First test import failed because bundled Python lacks SciPy; before task execution, the sole use was replaced by the fixed Student-t critical value for 23 degrees of freedom. No scientific outcomes were discarded. Normal-equation residual <1e-9 is enforced for every fit; all frozen arrays and summary values replay exactly. This is an automated self-audit with analytic fixtures, not an independent human or agent review.

| Stage | Tasks | Compute wall s | CPU s | Peak MiB | NPZ MiB |
|---|---:|---:|---:|---:|---:|
'''
    for stage,r in resources.items(): text+=f"| {stage} | {r['blocks']} | {r['compute_wall_seconds']:.2f} | {r['cpu_seconds']:.2f} | {r['peak_mib']:.2f} | {r['archive_mib']:.2f} |\n"
    text+=f'''
One CPU worker and one BLAS thread; no GPU or paid compute. Compute counters cover task/feature/readout computation, excluding compression, checkpoint I/O, report generation and audit. Full scientific audit took {audit['wall_seconds']:.2f} wall seconds, replaying **{audit['blocks']} blocks / {audit['arrays']} arrays**, with **{audit['preserved_files']} historical scientific dependencies/records unchanged**. This is a scoped preservation audit, not another full historical 82,263-file audit. The 30-minute compute, 2-GiB memory and 1-GiB archive caps passed. Checkpoints, contracts and SHA256 records support recovery without replacing samples.

Recovery: use the bundled Python with `tools/run_readout_diagnostic.py development`, `confirmation`, `analyze`, `audit`, then `tools/report_readout_diagnostic.py`; completed stages verify source and archive hashes. Do not rerun `select` over the existing frozen selection. NPZ traces are local/Git-ignored; source, compact records and reports are versionable.

**Gate:** Session B supplies a valid diagnostic and a testable confirmed prediction, so C is permitted by the scientific gate. **C has not started and is explicitly deferred at the user's request.** A targeted future repair would address repeated interference in the readout procedure and preserve matched access/budget controls; this result does not prescribe more neurons or stronger compensation. The next authorized action is to stop with this audited report and saved evidence.
'''
    (d.ROOT/'experiments/EXP-010-results.md').write_text(text,encoding='utf-8')
    print('report written')

if __name__=='__main__': main()
