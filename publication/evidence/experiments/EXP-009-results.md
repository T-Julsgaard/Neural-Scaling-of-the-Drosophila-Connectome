# Session A / EXP-009: published-parameter positive control

2026-09-15 (Europe/Copenhagen; machine timestamps are UTC). **Session A gate: PASS. Stop here; Session B has not been run.**

The supplied compensated model scored **62.46 [61.86, 63.03]%** versus **53.88 [53.53, 54.22]%** for its uncompensated counterpart. The primary paired difference is **+8.58 [8.13, 9.03] percentage points**, with a 95% task-block bootstrap interval. This establishes a useful positive effect in the bounded author-parameter regime. It does not explain the project's previous null results.

[Frozen protocol](EXP-009-protocol.md) · [Source/equation audit](../research/SESSION_A_SOURCE_AUDIT.md) · [Machine-readable analysis](../results/exp009/analysis.json) · [Run record](../research/runs/EXP-009-positive-control.json) · [Session B handoff](../research/SESSION_B_HANDOFF.md)

![Session A paired results](../results/exp009/positive_control.png)

## What was reproduced, adapted and left unresolved

Selected comparison: Abdelrahman, Vasilaki and Lin (2021), **Figure 4B2, magenta threshold compensation versus red random model, c=1**. Source commit `9f3f7e9e85117febef1ad32e3152c830570f74d3`, published paper, supplementary equations and Dataset S1 are saved with hashes. Dataset S1's twenty-model means are 53.3492% and 63.3565%, difference +10.0073 pp. Those are published observations extracted from `Fig 4!I3:I22` and `M3:M22`, not pooled with our results or used as new confirmation.

**Classification: independent bounded transfer/adaptation using author-fitted parameters, with author-runtime equation validation.** The experiment uses the one supplied calibrated MAT instance, not twenty newly fitted networks. The source's uncapped joint optimizer was inspected, not rerun or validated. The saved compensated projection is 5 times the raw projection, while the current script specifies 4.5. Both preserve identical connectivity. Saved optimizer history, seed and exact figure-rate mapping remain unresolved. No claim of exact panel reproduction or threshold-only causal isolation is justified.

Fresh blocks resample 100 synthetic odors independently from 24 supplied empirical PN marginals. Each block has balanced random labels, independent random output initialization, 15 training and 15 held-out noisy observations per odor, paired across arms. Models retain 2,000 graded KCs, pseudo-feedforward APL inhibition and two output channels with 4,000 learned weights **per arm**. Input scale and all encoder parameters come from the supplied author instance and are frozen. There is no new homeostatic fit or anatomy selection.

Declared adaptations: newly resampled empirical rather than recovered original histogram odors; all training trials noisy; fixed inherited PN scale instead of all-trial rescaling; training-only KC maximum instead of using test extrema; independent NumPy RNG; and equal prospective development tuning. This tests transfer from the authors' original calibration pool to fresh task prototypes from the same marginals. It is not a new chemical-class distribution shift. Unknown upstream calibration costs are not reported as zero.

Learning uses full labels and exponential depression of the wrong-valence output, with rate divided by mean training activity. Sufficient statistics implement the exact product of the per-odor exponential factors; all training associations are assessed afterward. The endpoint is average correct-valence choice **probability**, not a sampled accuracy or the project's pairwise sequential-retention endpoint. There is no action-conditioned reward access, prediction-error update, reversal or old-memory-age trajectory in this comparison.

## Prospective choices and findings

Four development blocks each evaluated the same ten learning rates per arm. Selected rates: uncompensated 0.001, compensated 0.00177828; neither is a grid boundary. No settings changed after development. Paired development SD=0.015705; uncapped precision calculation requested 4 blocks, and the protocol's minimum fixed **24**. Projected halfwidth was 0.79 pp; achieved halfwidth is 0.45 pp. Four development blocks provide an uncertain variance estimate, so the sample minimum and final precision gate matter.

| Endpoint | Estimate [95% interval] |
|---|---:|
| Uncompensated probability, % | 53.88 [53.53, 54.22] |
| Compensated probability, % | 62.46 [61.86, 63.03] |
| Primary equal-tuning difference, pp | 8.58 [8.13, 9.03] |
| Compensated at the uncompensated learning rate, difference, pp; descriptive | 8.23 [7.73, 8.71] |

Uncertainty units are independent **task blocks conditional on one fixed author network and its empirical source table**. Odors, trials and KCs are not independent replicates for this interval. The two-sided percentile bootstrap uses 50,000 draws. It is approximate; it does not support confidence intervals across biological animals or random network instances.

Gate criteria were fixed before new tasks: arithmetic/data/replay audits pass; compensated mean>=55%; primary lower interval>3 pp; halfwidth<=2 pp. **All pass**. No failed runs, exclusions, tuning extensions, replacement confirmation seeds or additional panels were used to obtain the effect. Access/runtime issues and source mismatch remain in the audit. During reporting, the cached plotting library required read escalation and a Windows default-text-decoding error was fixed by specifying UTF-8; neither changed scientific outputs. A separate source-only check matched all 2,640 empirical noise SD lookups to the unmodified author function exactly. The original EXP-007/008 practical-null results are unchanged.

Descriptive response profiles, averaged over new held-out probes:

| Measure | Uncompensated | Compensated |
|---|---:|---:|
| Coding level | 0.1119 | 0.1051 |
| Unused cells in the probe pool, % | 40.44 | 0.05 |
| CV of per-cell mean activity | 2.564 | 0.541 |
| Effective cells by mean activity | 264.3 | 1547.1 |
| Mean squared feature norm after training-max scaling | 6.032 | 3.764 |

Original supplied calibration makes all 2,000 cells' mean activities lie between .50924 and .51908, within .51 +/-6%. Raw per-cell means range 0 to 10.908. Equalization remains imperfect on fresh odors, and feature norms differ. The same-rate result does **not** establish norm-matched learning or unique mediation by participation.

## Differences from our model and ranked explanations

| Factor | Published/supplied positive-control regime | EXP-007/008 regime |
|---|---|---|
| Input weights | Raw heterogeneous lognormal claw weights; random projection from 24 PNs to 2,000 KCs, duplicate claws summed. Compensated supplied gain 5x | Extracted contact matrices, each KC's incoming sum normalized to 1; 40-to-73 larval or 104-to-590 adult |
| Responses | Graded ReLU after APL and threshold; global coding target near 10%, variable active count and norm | Fixed top-K, every winner 10/K; total activity 10, squared norm 100/K |
| Compensation target/range | Near-complete per-cell mean-activity equalization, nonnegative but broadly variable thresholds, jointly fitted coding constraints/APL; frozen supplied fit | Partial participation-probability targets, bounded centered offsets; fitted on separate 4,096-input pool; many offsets saturate |
| Noise | Author empirical mean-rate SD lookup; Gaussian PN noise; probabilistic c=1 decision | Synthetic binary-core cues, Gaussian .1/.3 noise clipped [0, 1], stochastic .8/.2 reward and cue choice |
| Task | 100 independent random-valence odor identities, full label exposure, 15 observations each, final classification | Persistent sequential training on up to 16 cue pairs, shared cores, blocked arrivals, reversal and all-memory probes |
| Learning rule | Multiplicative wrong-output depression; products commute across odor order; normalized by mean training activity | Opponent delta prediction-error updates, chosen cue only, nonnegative clipping, updates depend on current weights |
| Schedule/access | Every training odor receives its valence label; full task exposure before final test | New pairs displace old-pair training; only chosen outcomes drive learning; previous pair preferences may be overwritten |

**Rank 1: baseline normalization plus weak residual compensation may leave little additional useful change.** Our per-cell input normalization removes one source of excitability variability before bounded offsets are added. The author regime begins with much greater activity inequality and reaches much more complete equalization. This is a plausible account, not a demonstrated normalization effect: graded outputs, inhibition and input distributions also differ.

**Rank 2: error-dependent sequential learning may overwrite usable representations.** The published depression rule has commutative accumulated sufficient statistics. Our learner's later updates depend on current predictions, feedback access and clipping. This makes representation-versus-readout diagnostics more discriminating than another participation correlation. Mere odor ordering cannot cause forgetting in the fixed-input multiplicative rule; the bridge must distinguish update rule and supervision from schedule.

These are the only two nominated explanatory factors. The other table entries remain confounds to hold fixed or document, not additional hypotheses launched in A. No result here identifies the cause of our previous null.

## Validation, preservation and resource accounting

Seven tests passed, including scalar arithmetic, orthogonal learnability, label complement/chance, nonmutation, stream separation, training-only scaling and supplied-input Octave comparison. Maximum discrepancy across author response/weight/probability checks **1.17e-15**, tolerance 1e-10. A full-size ten-rate validation workload took 0.75 s and replayed exactly; the threefold-reserve 52-block projection was 117.02 s, below the 30-minute cap. Limits: one CPU worker/BLAS thread, 2 GiB peak memory, 1 GiB outputs, maximum 48 confirmation blocks. No GPU, paid compute or new infrastructure.

| Stage | Blocks | Worker wall s | CPU s | Peak process MiB | Archive MiB |
|---|---:|---:|---:|---:|---:|
| validation | 1 | 0.75 | 0.64 | 177.98 | 1.27 |
| development | 4 | 3.21 | 2.81 | 172.43 | 5.10 |
| confirmation | 24 | 12.72 | 11.30 | 171.94 | 16.13 |

Every development and confirmation archive was checksum-verified, its task regenerated, and **all 152 readout evaluations replayed exactly** from saved inputs/labels/initial weights. Historical preservation checked **82,263 files**. Scientific replay and cached-hash verification wall time is 55.44 s and CPU time 51.06 s, separately from campaign computation. The I/O-only historical audit used 16 file-reading threads and took 163.21 s wall / 113.48 s CPU; combined audit took 219.13 s wall. Model execution remained single-worker. The historical snapshot/verification involves many small files and dominates elapsed I/O; these are not model runtime measurements. Report/plot generation, literature retrieval, source preparation and original upstream calibration are excluded from block counters. The preservation snapshot began before model validation but finished after confirmation because of slow file I/O: this was not a completed pre-run historical freeze. Historical scientific files were not edited, and the final verification matches the snapshot. New model/protocol and selected settings were frozen before their respective stages. No target-colleague-machine benchmark or independent human/agent review is claimed.

Development exposes 12,000 PN observations across four tasks and trains 80 readouts; confirmation exposes 72,000 PN observations and computes 72 readouts including the prespecified same-rate diagnostic. Each arm has 4,000 reward-learned output weights and two derived training scalars (global maximum, mean activity). Threshold compensation adds 2,000 inherited fitted thresholds plus global gain/scale fitting; its original data/compute cost is unknown. The sparse projection stores 48,000 entries per arm with many zeros. Global activity scaling and mean-activity rate normalization do not match feature norms across arms.

Recovery commands use the existing bundled Python executable with `tools/run_compensation.py development`, `confirmation`, then `audit`. Finished blocks verify hashes and are reused; do not delete or regenerate the sample. Source, protocol, selection, checkpoints and reports are pinned in [the artifact manifest](../research/exp009_artifacts.json). Binary traces are local and ignored by Git; source bundle and compact records are versionable.

## Session A decision

A validated positive effect permits Session B to investigate a controlled bridge to this one supplied-parameter regime. The exact published ensemble and its optimizer remain unreproduced. Session B should first separate frozen-feature information from online readout limitations, then choose at most the two nominated factors with explicit access and norm controls. [The handoff](../research/SESSION_B_HANDOFF.md) specifies the next action and falsifying outcomes. **No Session B experiment has been launched.**
