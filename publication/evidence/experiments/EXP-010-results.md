# EXP-010 / Session B — where memory is lost

2026-09-15. Completed development, frozen prediction, 24 fresh confirmation tasks and deterministic audit. [Prospective protocol](EXP-010-protocol.md); [frozen selection](../results/exp010/selection.json); [numeric analysis](../results/exp010/analysis.json); [audit](../results/exp010/audit.json).

## Conclusion

**The tested sparse encoders retain useful linearly readable information that the fixed sequential online procedure fails to retain.** Averaging native and calibrated K6 within each task, offline full-outcome old-pair accuracy is 96.97% [95.84, 98.10], compared with 76.72% [72.49, 80.95] for fully supervised online delta. Paired gap: **20.26 pp [16.46, 24.05]**, 95% Student-t interval across 24 independent task blocks. Online acquisition-to-final loss is 23.23 pp [19.02, 27.45]. Prediction passed: **True**.

This favors a learning-procedure limitation in this fixed regime. Feedback access and clipping are contributors to examine separately; neither is a sufficient explanation of the offline versus supervised-online gap. At .3 observation noise, the same native/calibrated offline readouts recover only 84.49% of old preferences. Thus the evidence also retains a noise/representation/readout limitation; it does not support a universal learning-only account. It does not identify a unique optimal repair, establish irreversible encoder information loss, or explain the entire published compensation result. This is a familiar sequential-interference explanation; no novelty is claimed.

## Matched diagnostic and performance

Values below are deterministic correct preferences on 64 independent .1-noise observations per old pair (first 15 of 16). Chance ties count .5. They are not the historical stochastic-choice metric. Random rows average all three fixed degree/contact-controlled instances within each task. Core representations use mean squared feature norm 100/6; raw direct is a separate scale sensitivity.

| Frozen representation | Chosen online | Full online | Unclipped full online | Full online, 10 passes | Offline chosen only | Offline full |
|---|---:|---:|---:|---:|---:|---:|
| native | 78.25% | 77.42% | 79.88% | 86.53% | 89.13% | 97.05% |
| calibrated | 78.32% | 76.02% | 77.64% | 84.64% | 89.51% | 96.89% |
| random | 73.12% | 72.84% | 73.81% | 78.34% | 84.72% | 92.64% |
| random_cal | 73.70% | 73.36% | 74.68% | 78.75% | 84.54% | 93.19% |
| direct | 88.74% | 86.42% | 89.76% | 97.82% | 96.38% | 99.88% |
| direct_raw | 89.61% | 87.63% | 91.60% | 99.35% | 97.83% | 99.88% |

Native/calibrated paired descriptive contrasts (95% intervals, no multiplicity adjustment):

- matched_chosen_fit_gap: 11.03 pp [7.35, 14.71].
- offline_feedback_access: 7.65 pp [5.70, 9.61].
- remove_clipping: 2.04 pp [0.94, 3.15].
- ten_pass_replay: 8.87 pp [6.20, 11.53].

The chosen-only fit gap supports a learning-procedure limitation even without unchosen outcomes. Full outcome access improves offline recovery, but it does not rescue this blocked online learner. Removing clipping and revisiting data each help, so the residual cause is a mixture of trajectory constraints and sequential fitting/schedule limitations; the relative contribution of convergence, objective choice, and schedule is not separately identified.

The chosen-only offline fit uses exactly the archived chosen observations and stochastic +/-1 outcomes of the chosen online learner. Full offline and full online receive the same 4,096 observations/outcomes per task, in contrast to 2,048 chosen outcomes. Neither offline arm receives latent valence labels, expected rewards, clean targets or held-out noise during fitting. Both observations are visible for online choice, but unchosen outcomes cannot affect chosen updates; a test flips them and verifies identical learned weights. Full online receives cue 0 then cue 1 at each presentation. The second update uses the weights after the first; this declared sequence is not a batch gradient.

Offline fitting has storage, optimization and historical-data access advantages. Ten-pass replay revisits the same data and performs 40,960 updates, versus 4,096 for full online and 2,048 for chosen online. Thus offline is an explanatory diagnostic, not a fair online competitor or a proven capacity upper bound. The remaining contrast combines convergence to a ridge objective with fitting/schedule differences. Replay is a diagnostic intervention, not an optimized repair.

Two nonnegative opponent weight vectors with no upper bound can represent every signed linear vector: w = max(w,0) - max(-w,0). The decomposition exactly reproduces fitted predictions. Clipping can alter a learning trajectory without removing that representational possibility. Removing online clipping holds eta, data, initialization and order fixed. Offline fit residuals and an independent augmented least-squares fixture validate the numerical solution, not the sufficiency of every possible readout class. The archived `clips` counter counts negative coordinate proposals; for the unclipped arm these proposals are recorded but are not clipped.

## Acquisition, update interference, geometry and noise

| Representation | Online mode | Old acquisition | Final old accuracy | Acquisition loss |
|---|---|---:|---:|---:|
| native | chosen | 99.59% | 78.25% | 21.33 pp |
| native | supervised | 99.96% | 77.42% | 22.54 pp |
| native | unclipped | 99.93% | 79.88% | 20.05 pp |
| native | replay | 99.96% | 86.53% | 13.43 pp |
| calibrated | chosen | 99.36% | 78.32% | 21.04 pp |
| calibrated | supervised | 99.94% | 76.02% | 23.92 pp |
| calibrated | unclipped | 99.92% | 77.64% | 22.29 pp |
| calibrated | replay | 99.94% | 84.64% | 15.30 pp |
| direct | chosen | 99.72% | 88.74% | 10.99 pp |
| direct | supervised | 100.00% | 86.42% | 13.58 pp |
| direct | unclipped | 100.00% | 89.76% | 10.24 pp |
| direct | replay | 100.00% | 97.82% | 2.18 pp |

Replay acquisition is measured on its first pass; its final score is after ten passes.

| Representation | Clean rank / 32 | Training rank | Nonzero condition | Mean squared norm | Clean pair distance | Noisy squared deviation |
|---|---:|---:|---:|---:|---:|---:|
| native | 27.46 | 42.54 | 111.97 | 16.667 | 4.029 | 1.739 |
| calibrated | 28.42 | 46.46 | 108.68 | 16.667 | 4.093 | 2.129 |
| direct | 32.00 | 40.00 | 45.27 | 16.667 | 3.766 | 0.354 |
| direct_raw | 32.00 | 40.00 | 45.27 | 9.403 | 2.828 | 0.200 |

Ranks and condition numbers use float64 SVD and the NumPy matrix-rank tolerance; conditions refer to nonzero singular values, not infinite condition of a rank-deficient matrix. Geometry is descriptive. Native/calibrated/random sparse norm equality is exact, so compensation cannot improve this comparison simply by changing feature norm. Direct normalization uses training observations only. A scalar-rescaling fixture verifies the corresponding inverse-square rate relationship for unclipped delta. Here the raw-direct versus norm-matched-direct comparison deliberately shows sensitivity at a fixed eta; it is not a new representation.

Every update records the signed change to all 16 clean pair margins, its training pair and replay pass. The following summarizes first-pass updates on strictly older pairs; negative change weakens the correct preference, positive change strengthens it. All changes telescope to the final margin within the declared float32 trace tolerance. Acquisition/final noisy probes independently establish forgetting; interference is not inferred from participation correlation.

| Representation / learner | Harmful old-margin changes | Mean absolute change | Mean signed change |
|---|---:|---:|---:|
| native_chosen | 30.70% | 0.017617 | -0.000276 |
| native_supervised | 30.54% | 0.017572 | -0.000315 |
| native_unclipped | 30.32% | 0.017536 | -0.000278 |
| native_replay | 30.54% | 0.017572 | -0.000315 |
| calibrated_chosen | 29.56% | 0.017264 | -0.000291 |
| calibrated_supervised | 29.67% | 0.017205 | -0.000326 |
| calibrated_unclipped | 29.47% | 0.017189 | -0.000297 |
| calibrated_replay | 29.67% | 0.017205 | -0.000326 |

| Representation | Offline full clean accuracy | Offline full .3-noise old accuracy | Offline full worst-pair .1 accuracy | Full online worst-pair .1 accuracy |
|---|---:|---:|---:|---:|
| native | 98.18% | 82.86% | 76.27% | 2.67% |
| calibrated | 98.18% | 86.12% | 77.18% | 2.08% |
| random | 94.70% | 81.04% | 48.51% | 3.34% |
| random_cal | 94.84% | 82.24% | 50.46% | 3.83% |
| direct | 100.00% | 88.04% | 98.63% | 14.39% |
| direct_raw | 100.00% | 87.96% | 98.63% | 19.86% |

Worst-pair entries average each task's worst pair, rather than finding a worst pair after pooling. High-noise limitations can coexist with low-noise recoverability. Poor offline performance at any noise level would motivate a representation/noise or linear-readout/fitting limitation; it would not prove destruction of all useful information.

## Prospective prediction and falsification

Six development tasks selected one ridge penalty per representation/access from four candidates using development probes only. Development full offline mean was 98.11% versus 76.68% full online.
The source-hashed selection was saved before any confirmation tasks were constructed. Fixed prediction: **native/calibrated mean offline old-pair accuracy >=80%; paired offline-minus-full-online lower 95% CI >5 pp; full-online acquisition-minus-final lower CI >5 pp.** Failure of any criterion would falsify this operational prediction. All 24 fresh tasks were retained; there was no sample extension or confirmation tuning. Descriptive contrasts have no multiplicity-adjusted discovery status. Inference is conditional on one larval anatomy and fixed nulls, not animals or a population of connectomes.

Session A motivates the update-dynamics hypothesis but its author model remains a fixed historical positive reference. The author multiplicative rule's odor-order invariance passed a validation fixture. No author-versus-delta causal comparison or raw-contact normalization factorial was run: the preliminary diagnostic already discriminated recoverability from the fixed online procedure, and its result does not justify attributing the A/B difference to any one architectural factor. Existing bounded .25 compensation was frozen; no stronger equalization or biological-homeostasis claim was introduced.

## Audit, resources and limitations

Five tests cover existing update equivalence, ridge solution and signed/nonnegative equivalence, orthogonal learning, scaling, outcome-access isolation, stream separation and multiplicative order invariance. First test import failed because bundled Python lacks SciPy; before task execution, the sole use was replaced by the fixed Student-t critical value for 23 degrees of freedom. No scientific outcomes were discarded. Normal-equation residual <1e-9 is enforced for every fit; all frozen arrays and summary values replay exactly. This is an automated self-audit with analytic fixtures, not an independent human or agent review.

| Stage | Tasks | Compute wall s | CPU s | Peak MiB | NPZ MiB |
|---|---:|---:|---:|---:|---:|
| validation | 1 | 11.57 | 11.44 | 86.85 | 18.40 |
| development | 6 | 81.97 | 78.36 | 127.15 | 108.11 |
| confirmation | 24 | 301.77 | 293.88 | 126.08 | 405.51 |

One CPU worker and one BLAS thread; no GPU or paid compute. Compute counters cover task/feature/readout computation, excluding compression, checkpoint I/O, report generation and audit. Full scientific audit took 413.85 wall seconds, replaying **31 blocks / 15117 arrays**, with **70 historical scientific dependencies/records unchanged**. This is a scoped preservation audit, not another full historical 82,263-file audit. The 30-minute compute, 2-GiB memory and 1-GiB archive caps passed. Checkpoints, contracts and SHA256 records support recovery without replacing samples.

Recovery: use the bundled Python with `tools/run_readout_diagnostic.py development`, `confirmation`, `analyze`, `audit`, then `tools/report_readout_diagnostic.py`; completed stages verify source and archive hashes. Do not rerun `select` over the existing frozen selection. NPZ traces are local/Git-ignored; source, compact records and reports are versionable.

**Gate:** Session B supplies a valid diagnostic and a testable confirmed prediction, so C is permitted by the scientific gate. **C has not started and is explicitly deferred at the user's request.** A targeted future repair would address repeated interference in the readout procedure and preserve matched access/budget controls; this result does not prescribe more neurons or stronger compensation. The next authorized action is to stop with this audited report and saved evidence.
