# EXP-011 / Session C — nonlinear compound-task transfer

2026-09-15. Complete, development-selected and freshly evaluated; automated self-audit passed. [Protocol](EXP-011-protocol.md), [selection](../results/exp011/selection.json), [analysis](../results/exp011/analysis.json), [audit](../results/exp011/audit.json).

## Conclusion

The prospective prediction is supported: useful nonlinear distinctions remain readable from frozen sparse representations while the tuned sequential readout loses previously learned associations.

Native/calibrated offline old-context accuracy 95.67 [92.91, 98.44]%; tuned sequential accuracy 51.73 [41.24, 62.21]%; paired gap 43.95 [34.23, 53.67] pp; acquisition-to-final loss 45.86 [35.78, 55.93] pp (95% intervals, 24 fresh blocks).

Classification: **supported**. Held-out capable/direct gate: True; sparse old-context recovery >=80%: True. All three primary criteria were required. No confirmation samples were added, excluded, replaced or used for tuning.

## What changed from B

This is supervised XOR classification with two continuous compound components, variable nuisance inputs and noisy fresh observations. Learning proceeds through two contexts in which the same second component has opposite labels. Both contexts contain both labels. There are no arbitrary cue-ID inputs or assigned cue-pair rewards. This tests interpolation to fresh observations/nuisance mixtures within four trained logical categories, not extrapolation to unseen logical combinations or natural sensory generalization. Context order, channel mapping and label polarity vary independently across blocks.

The task was chosen and written before any outcomes because it tests context-dependent associations and nonlinear representation sufficiency. It was the only task tried. Development used six blocks, four learning rates per representation/schedule and four ridge penalties. Selection balances old and new final performance. No sparse-encoder or stimulus tuning occurred. Existing EXP-007 offsets were transferred unchanged; this is not task-specific recalibration.

## Primary endpoints and controls

| Native/calibrated average | Estimate [95% CI], % or pp |
|---|---:|
| Offline old-context accuracy | 95.67 [92.91, 98.44] |
| Tuned blocked old-context accuracy | 51.73 [41.24, 62.21] |
| Paired offline minus blocked, pp | 43.95 [34.23, 53.67] |
| Blocked acquisition accuracy | 97.58 [95.67, 99.50] |
| Acquisition minus final old, pp | 45.86 [35.78, 55.93] |

All intervals use independent task blocks, not individual probes or null instances. Native/calibrated and the three nulls are averaged within each block. The sample size was fixed at 24 before fresh outcomes. A planning SD of .10 implies about 4.2 pp half-width; actual intervals above determine precision. Secondary intervals are unadjusted descriptive comparisons.

| Representation | Offline old | Blocked old | Blocked new | Acquisition | Worst phase | Fixed B rate old |
|---|---:|---:|---:|---:|---:|---:|
| native | 95.78 | 45.27 | 97.22 | 97.84 | 44.92 | 14.10 |
| calibrated | 95.56 | 58.18 | 97.74 | 97.33 | 58.10 | 30.52 |
| random | 95.89 | 53.83 | 95.08 | 97.86 | 52.43 | 28.93 |
| direct | 49.17 | 0.00 | 100.00 | 100.00 | 0.00 | 0.00 |
| polynomial | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 99.23 |

Values are percentages. Worst phase is computed per block, then averaged. Polynomial is a generic quadratic feature diagnostic with 861 signed coefficients; direct has 40, sparse has 73. Online stores two coefficient vectors (80, 146 or 1722 scalars); offline fits one signed vector. All core feature mean squared norms are 100/6 using training-only normalization for direct/polynomial. Fixed B rate is 1/150; the primary online comparator is ordinarily tuned, not that fixed anchor.

## Order, computation and historical access

| Representation | Shuffled one-pass old/new | Local10 old/new | Replay10 old/new | Unclipped old/new |
|---|---:|---:|---:|---:|
| native | 89.44 / 94.55 | 17.29 / 99.96 | 83.84 / 98.00 | 45.27 / 97.22 |
| calibrated | 90.85 / 97.03 | 34.04 / 99.85 | 89.36 / 98.56 | 58.18 / 97.74 |
| random | 93.56 / 93.52 | 31.34 / 99.15 | 89.09 / 97.77 | 53.83 / 95.08 |
| direct | 51.49 / 47.75 | 0.00 / 100.00 | 0.00 / 100.00 | 0.00 / 100.00 |
| polynomial | 100.00 / 100.00 | 99.98 / 100.00 | 100.00 / 100.00 | 100.00 / 100.00 |

| Native/calibrated paired contrast | pp [95% CI] |
|---|---:|
| unclipped_minus_blocked_old | 0.00 [0.00, 0.00] |
| shuffled_minus_blocked_old | 38.42 [29.71, 47.13] |
| local10_minus_blocked_old | -26.06 [-36.82, -15.30] |
| replay10_minus_blocked_old | 34.87 [26.52, 43.22] |
| offline_minus_blocked_old | 43.95 [34.23, 53.67] |
| replay10_minus_local10_old | 60.93 [51.62, 70.25] |
| replay10_minus_local10_new | -1.63 [-2.33, -0.93] |

Every learner receives the same 256 observations and exact +/-1 labels. One-pass schedules perform 256 updates; local10 and replay10 perform 2560. Shuffled one-pass requires both contexts available together and full storage, but adds no updates. Local10 stores/repeats only the current 128-example context before switching; replay10 stores/revisits all 256. Thus replay-versus-local10 matches updates and unique data but changes historical access and ordering. It does not isolate storage from scheduling. Each schedule has the same four-candidate development opportunity; paired schedule contrasts include the effect of their separately selected rates. Unclipped comparisons likewise include retuning.

The offline solver uses simultaneous full-history storage and a penalized least-squares objective. It receives no additional observations, feedback, or test fitting access, but is **an explanatory diagnostic, not an equal-budget competitor or a capacity upper bound**. Signed coefficients can be expressed as the difference of nonnegative readouts; clipping constrains the learning trajectory, not the set of expressible signed linear functions. CPU timings are aggregate task timings, not method-level efficiency rankings.

## Common-rate schedule control

All rows use eta=1/150, with the same update rule, observations and feedback. Values average native/calibrated within each block.

| Schedule | Old accuracy [95% CI], % | New accuracy [95% CI], % |
|---|---:|---:|---:|
| blocked | 22.31 [14.85, 29.77] | 99.89 [99.78, 100.01] |
| unclipped | 26.20 [17.68, 34.72] | 99.89 [99.77, 100.00] |
| shuffled | 90.52 [85.32, 95.72] | 94.08 [89.97, 98.19] |
| local10 | 22.04 [14.16, 29.93] | 99.81 [99.58, 100.03] |
| replay10 | 78.72 [67.54, 89.91] | 98.92 [98.37, 99.47] |

At the same rate and 2560 updates, replay10 minus local10 is 56.68 [46.97, 66.39] pp for old learning and -0.89 [-1.44, -0.33] pp for new learning. This specifically compares revisiting stored old data against extra practice confined to the current context; data availability and order change together. The common-rate control was specified before C outcomes, and uses the archived fixed-anchor models. Numerical record: [fixed-rate controls](../results/exp011/fixed_rate_controls.json).

## Development, boundary results and selected settings

| Representation | Development offline overall, % | Ridge lambda | Selected blocked eta |
|---|---:|---:|---:|
| native | 95.26 | 0.01 | 0.0004166666666666667 |
| calibrated | 96.58 | 1e-06 | 0.0004166666666666667 |
| random1 | 94.97 | 1e-06 | 0.0004166666666666667 |
| random2 | 93.91 | 0.01 | 0.0004166666666666667 |
| random3 | 96.08 | 1e-06 | 0.0004166666666666667 |
| direct | 49.64 | 0.1 | 0.0004166666666666667 |
| polynomial | 100.00 | 0.01 | 0.0004166666666666667 |

Development capable/direct gate: True; sparse adequacy: True. All candidate outcomes are retained in development checkpoints; all schedule rates are in selection.json. The prediction and n=24 were frozen at 2026-09-15T19:37:12Z, before confirmation's contract and inputs.

| Representation | Offline overall [95% CI], % | Offline high-noise old [95% CI], % |
|---|---:|---:|
| native | 96.70 [95.04, 98.36] | 84.86 [81.37, 88.34] |
| calibrated | 96.74 [95.15, 98.33] | 83.59 [80.72, 86.45] |
| random | 96.76 [96.16, 97.36] | 84.32 [82.58, 86.07] |
| direct | 50.76 [49.95, 51.56] | 48.67 [46.13, 51.21] |
| polynomial | 100.00 [100.00, 100.00] | 99.99 [99.98, 100.01] |

Calibrated minus native offline old: -0.22 [-1.85, 1.41] pp. This secondary comparison is not a confirmation of homeostasis benefit or equivalence. Direct linear behavior is a negative control on XOR expressibility. Polynomial recovery validates this synthetic task's learnability; poor direct performance is not evidence for anatomical superiority. Randomized controls must remain visible, including any results matching or exceeding anatomy.

## Validation, audit and resources

Five tests cover analytic XOR/direct and quadratic behavior, independent augmented-least-squares verification, clipped update arithmetic, probe noninterference, exact observation/update accounting, phase-local versus historical revisiting, balanced labels, independent validation inputs and training-only normalization. No fixture generates confirmation inputs. Every ridge fit enforces normal-equation relative residual <1e-9. Every stage freezes source and protocol hashes; confirmation also pins the selection hash. Audit regenerates every array and scientific summary exactly, checks checkpoint hashes and rebuilds analysis. This is an automated self-audit, not independent review.

| Stage | Blocks | Compute wall s | CPU s | Peak MiB | NPZ MiB |
|---|---:|---:|---:|---:|---:|
| validation | 1 | 5.02 | 4.78 | 89.74 | 1.11 |
| development | 6 | 24.93 | 23.83 | 78.18 | 6.67 |
| confirmation | 24 | 109.35 | 68.22 | 76.82 | 18.42 |

Audit replayed 31 blocks / 11218 arrays and verified 460 historical files unchanged in 102.88 wall seconds. Preservation scope includes historical experiment documents, code/tests, top-level result JSON and stage contracts, prior audit manifests and all B raw blocks/checkpoints plus calibration. Older bulk NPZ archives were not reread; this is not a full repository audit. One local CPU worker and one BLAS thread, no paid compute or GPU. Computation counters exclude archive compression, file hashing, reporting and process startup. The 30-minute computation, 2-GiB memory and 1-GiB archive caps passed; audit has its own 30-minute cap.

No failed scientific runs or discarded outcomes. The first overbroad preservation scan was interrupted before tests or any scientific block; its scope was narrowed before validation (see execution notes). An independent five-test preflight had passed during that scan. An optional plotting-library availability check found matplotlib absent; the report uses numeric tables and no dependency installation was needed. Raw NPZ remains local and Git-ignored; compact checkpoints, code and reports are versionable.

## What the controls establish

Randomized sparse offline old accuracy is 95.89% versus 95.67% for native/calibrated. The result supports a shared sparse-feature/readout phenomenon and supplies no demonstrated anatomical advantage. The capable quadratic model reaches 100.00% overall; direct linear reaches 50.76% as expected for this XOR negative control.

The generic quadratic representation also reaches 100.00% old accuracy with the tuned one-pass sequential procedure. Sequential failure is therefore not inevitable on this task: the deficit concerns an interaction between these sparse features and the tested update procedure. Quadratic features have 861 dimensions versus 73, so this does not isolate a single geometric mechanism or constitute an equal-parameter competitor.

A prospectively secondary comparison shows calibrated-minus-native tuned sequential old accuracy of 12.91 [5.56, 20.25] pp, new accuracy 0.52 [-1.55, 2.59] pp and overall 6.71 [2.96, 10.47] pp (unadjusted). Both selected rates are identical. Calibration therefore shows a descriptive retention benefit in C even though offline recoverability barely changes. This is not the primary confirmatory claim, has no multiplicity-adjusted discovery status and does not establish causation for B or overturn the task-specific EXP-007/008 nulls. It argues against calling homeostasis universally ineffective. Numeric record: [secondary calibration](../results/exp011/secondary_calibration.json).

At the common B rate, revisiting old data raises old accuracy by 56.68 [46.97, 66.39] pp relative to the same number of phase-local updates, while new-context accuracy changes by -0.89 [-1.44, -0.33] pp. The small new-learning cost is retained. Extra updates alone therefore do not account for that recovery in this control; the availability and ordering of old data matter together. Shuffled one-pass learning also improves old retention without extra updates, but requires all-context availability/storage.

The selected native/calibrated blocked and unclipped rates are identical, and the archived selected blocked runs have zero clipping events. Their scores coincide: clipping is not necessary for the deficit in this selected regime. This does not erase clipping contributions in B or at other rates. Native/calibrated blocked tuning selects the lowest rate in the four-value grid; slower rates or other learners remain untested. No claim of optimally tuned online learning follows, and the confirmation grid was not widened.

Actual primary-gap half-width is 9.72 pp, wider than the planning example because block variability is larger. The interval still clears the five-point margin; the sample remains 24. High-noise offline recovery falls to 84.22%: good low-noise recovery is not universal noise robustness. Reported t intervals are untruncated and can slightly exceed 100% near ceilings; 100% observed quadratic accuracy is not a guarantee of perfect population performance.

## Interpretation and Session D handoff

The prospective prediction is supported: useful nonlinear distinctions remain readable from frozen sparse representations while the tuned sequential readout loses previously learned associations. This strengthens the empirical scope of the learning-procedure explanation beyond random pair association, but does not establish a new mechanism.

Two-context XOR is deliberately small and highly structured. The evidence is conditional on one larval projection, fixed nulls and transferred offsets. Offline fitting does not identify a unique repair or prove that all useful information is preserved. Training rate, clipping, convergence, objective and scheduling remain distinguishable contributors. This does not fully explain EXP-007/008 homeostasis nulls or the difference from A. No biological advantage, scaling law, worldwide novelty or natural-task generality is established.

Next authorized milestone, only on a later user request: D, following [precise handoff](../research/SESSION_D_HANDOFF.md). Critically check prior work and decide the manuscript scope; do not automatically launch more experiments. C ends here. No D work, manuscript draft, publishing, commit or push was performed.

Recovery: with bundled Python, use `tools/run_compound_transfer.py confirmation`, `analyze`, `audit`; completed stages verify hashes and reuse blocks. Do not rerun `select`, change settings, extend n or overwrite historical experiments. To regenerate this report, set `PYTHONPATH=.` and execute `tools/report_compound_transfer.py`.

Access-accounting detail: the paired simulation materializes datasets and probes in memory for reproducibility; the schedule comparisons describe which labeled examples the update procedure is allowed to revisit, not measured streaming-memory savings. Direct and quadratic normalization uses a single scalar from all training inputs, including the later context, so those baselines have unlabeled lookahead for scale and are not strictly causal streaming baselines. Native/calibrated/random sparse norms are fixed without this lookahead; the primary sparse comparison is unaffected. Evaluation observations and labels never enter fitting or scale selection.

Record-check limitation: the unchanged legacy `tools/validate_foundation.py` stops at its hard-coded experiment-count assertion, which only accounts through EXP-009. It cannot validate the current B/C manifest schema. C scientific replay is passed; `tools/audit_compound_records.py` separately checks current manifests, source/selection/temporal integrity, derived controls, artifact hashes and local links. No full legacy-foundation pass is claimed.
