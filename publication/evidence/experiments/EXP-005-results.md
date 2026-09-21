# EXP-005: activity mechanism at 73 cells — audited results

2026-09-13. Six development blocks and 32 fresh held-out evaluation blocks completed; 120 and 640 distinct reset episodes respectively. Evaluation compares twelve settings on each episode (7,680 configuration-episodes). No sample extension or evaluation-driven tuning.

[Prospective protocol](EXP-005-protocol.md), [full analysis](../results/exp005_evaluation/analysis.json), [audit](../results/exp005_evaluation/audit.json), [run record](../research/runs/EXP-005-evaluation.json).

The K6 retention advantage survives ordinary learning-rate adjustment, both nominal update matches, norm matching and the equal eight-candidate tuning budget. Historical K6-K4 is +4.25 pp; tuned K6-K4 is +3.78 pp [2.39, 5.27] (primary 98.75%). The positive direction is supported, but the interval crosses the prespecified +3 pp practical threshold: an effect larger than 3 pp is not established. Tuned equivalence within ±3 pp is not established either.

The measured same-cue update coefficients are nearly equal for tuned K4/K6 (.33258/.33276), with similar clipping (2.29%/2.56%) and old-cue perturbation magnitudes (.04490/.04523). Thus simply making updates gentler is insufficient to account for the residual benefit. The fixed-action validation shows exact compensation is possible for amplitude alone when initial weights and eta are rescaled consistently; it does not prove K4 and K6 representations are equivalent.

K6 shows more repeatable noisy-cue responses (cosine .9206 versus .8376), and fewer unused cells per task block (15.28% versus 37.16%). Between-cue overlap also rises (.1756 versus .1622): K6 does not reduce between-cue overlap on this measure. Better response stability and broader participation are plausible contributors, not uniquely identified causal mediators.

Retention is not bought by a demonstrated new-learning deficit: tuned K6 improves early intervening-cue learning +1.54 pp [0.72, 2.33], late learning +0.60 [0.11, 1.13], and early reversal +1.96 [0.53, 3.44] (secondary 95%). The independent intervening-cue probe is +0.89 [-0.04, 1.73], which is uncertain in direction and rules out a 3 pp deficit at this exploratory coverage. K6 begins interference somewhat ahead too; before/after contrasts below separate that from subsequent forgetting.

The amplitude factorial also limits the claim: using six winners at the larger 2.5 amplitude produces acquisition, new-learning and noise costs, with an uncertain retention advantage. More activity is not uniformly better. The supported candidate is a calibrated K6 representation in this assay.

## Primary retention contrasts

All differences are six minus four winners, in percentage points. Each primary interval has 98.75% coverage (Bonferroni family of four); paired bootstrap resamples 32 task blocks, not individual episodes. Practical band ±3 pp.

| Comparison | Retention difference [interval], pp |
|---|---:|
| historical | +4.25 [+2.71, +5.90] |
| slow_matched | +3.78 [+2.39, +5.27] |
| fast_matched | +3.91 [+2.17, +5.74] |
| tuned | +3.78 [+2.39, +5.27] |

Selected on development only: K4: eta=0.0066666667, T=0.1; K6: eta=0.01, T=0.1. The tuned contrast coincides with the slow matched contrast in this campaign; these are not independent replications.

## Capability guardrails and amplitude controls

Secondary exploratory 95% intervals, pp. Retention for the four primary rows above retains its primary coverage in the saved analysis.

| Comparison | Acquisition | Early reversal | New learning, early | New learning, late | New probe | Noise .3 |
|---|---:|---:|---:|---:|---:|---:|
| historical | +1.16 [+0.79, +1.51] | +3.47 [+1.54, +5.39] | +2.62 [+1.63, +3.63] | +1.01 [+0.45, +1.59] | +1.03 [-0.09, +2.19] | +1.71 [+1.07, +2.40] |
| slow_matched | +0.56 [+0.24, +0.87] | +1.96 [+0.53, +3.44] | +1.54 [+0.72, +2.33] | +0.60 [+0.11, +1.13] | +0.89 [-0.04, +1.73] | +1.01 [+0.49, +1.51] |
| fast_matched | +0.23 [-0.23, +0.69] | +3.04 [+1.06, +5.10] | +1.63 [+0.81, +2.52] | +0.24 [-0.31, +0.77] | +0.53 [-0.86, +1.90] | +1.17 [+0.51, +1.89] |
| tuned | +0.56 [+0.24, +0.87] | +1.96 [+0.53, +3.44] | +1.54 [+0.72, +2.33] | +0.60 [+0.11, +1.13] | +0.89 [-0.04, +1.73] | +1.01 [+0.49, +1.51] |
| equal_low_amplitude | -0.07 [-0.38, +0.21] | +4.38 [+3.04, +5.70] | +1.19 [+0.50, +1.87] | +0.22 [-0.14, +0.57] | -0.20 [-1.06, +0.48] | +0.67 [+0.21, +1.10] |
| equal_high_amplitude | -2.51 [-3.35, -1.75] | +2.46 [+0.18, +4.64] | -0.63 [-1.62, +0.35] | -2.36 [-3.69, -1.22] | -1.28 [-3.23, +0.62] | -2.29 [-3.22, -1.37] |
| low_norm | +0.54 [+0.23, +0.84] | +2.47 [+0.87, +4.13] | +1.56 [+0.82, +2.31] | +0.52 [+0.08, +0.97] | +0.65 [-0.20, +1.35] | +0.96 [+0.46, +1.46] |
| high_norm | +0.17 [-0.29, +0.61] | +2.95 [+0.92, +5.04] | +1.59 [+0.76, +2.50] | +0.30 [-0.23, +0.80] | +0.62 [-0.77, +2.01] | +1.16 [+0.51, +1.88] |

| Amplitude/norm control | Retention difference [95% interval], pp |
|---|---:|
| equal_low_amplitude | +2.56 [+1.67, +3.49] |
| equal_high_amplitude | +1.54 [-1.33, +4.14] |
| low_norm | +3.73 [+2.59, +4.94] |
| high_norm | +3.85 [+2.44, +5.30] |

| Comparison | Before-interference difference, pp | Difference in before-to-after change, pp |
|---|---:|---:|
| historical | +1.79 [+0.77, +2.97] | +2.47 [+0.86, +4.03] |
| slow_matched | +1.37 [+0.52, +2.40] | +2.41 [+1.01, +3.77] |
| fast_matched | +0.82 [-0.59, +2.23] | +3.09 [+1.45, +4.68] |
| tuned | +1.37 [+0.52, +2.40] | +2.41 [+1.01, +3.77] |

## Absolute profiles

Means are probabilities; full intervals and block values are in the analysis. New probe assesses the intervening pair immediately after training it.

| Setting | Before interference | After interference | Reversal | New learning, late | New probe | Noise .3 |
|---|---:|---:|---:|---:|---:|---:|
| k4_historical | 0.9742 | 0.9175 | 0.7142 | 0.9772 | 0.9732 | 0.9675 |
| k6_historical | 0.9920 | 0.9600 | 0.7489 | 0.9873 | 0.9836 | 0.9847 |
| k4_slow | 0.9783 | 0.9223 | 0.7293 | 0.9813 | 0.9746 | 0.9746 |
| k6_fast | 0.9824 | 0.9566 | 0.7446 | 0.9796 | 0.9786 | 0.9792 |
| k4_low_amplitude | 0.9865 | 0.9344 | 0.7050 | 0.9851 | 0.9856 | 0.9780 |
| k6_high_amplitude | 0.9641 | 0.9329 | 0.7388 | 0.9536 | 0.9605 | 0.9446 |
| k4_low_norm | 0.9788 | 0.9227 | 0.7241 | 0.9821 | 0.9771 | 0.9750 |
| k6_high_norm | 0.9819 | 0.9561 | 0.7437 | 0.9802 | 0.9794 | 0.9792 |
| k4_tune_e1_t0 | 0.9783 | 0.9223 | 0.7293 | 0.9813 | 0.9746 | 0.9746 |
| k6_tune_e2_t0 | 0.9920 | 0.9600 | 0.7489 | 0.9873 | 0.9836 | 0.9847 |
| k4_frozen | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| k6_frozen | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 0.5000 |

## Measured update mechanics

Values averaged over online learning; old-cue change is RMS predicted-value change on clean old prototypes during interference. These are descriptive diagnostics, not mediation estimates.

| Setting | Mean absolute selected q change | Mean actual/error coefficient | Clipped updates, % | Old-cue change during interference |
|---|---:|---:|---:|---:|
| k4_historical | 0.34525 | 0.49700 | 6.54 | 0.06865 |
| k6_historical | 0.22352 | 0.33276 | 2.56 | 0.04523 |
| k4_slow | 0.22722 | 0.33258 | 2.29 | 0.04490 |
| k6_fast | 0.33730 | 0.49797 | 6.42 | 0.06826 |
| k4_low_amplitude | 0.15122 | 0.22020 | 8.37 | 0.02972 |
| k6_high_amplitude | 0.52016 | 0.74783 | 4.18 | 0.10559 |
| k4_low_norm | 0.22674 | 0.33106 | 6.79 | 0.04473 |
| k6_high_norm | 0.33805 | 0.49913 | 2.79 | 0.06836 |
| k4_tune_e1_t0 | 0.22722 | 0.33258 | 2.29 | 0.04490 |
| k6_tune_e2_t0 | 0.22352 | 0.33276 | 2.56 | 0.04523 |
| k4_frozen | 0.00000 | 0.00000 | 0.00 | 0.00000 |
| k6_frozen | 0.00000 | 0.00000 | 0.00 | 0.00000 |

## Representation geometry

Cosine overlaps; same-cue repeats use independent noise draws. These measures use equal-amplitude binary winner masks, so they describe which cells participate rather than activity scale.

| K | Within-cue cosine | Between-cue cosine | Old/new prototype cosine | Never used in whole block, % |
|---|---:|---:|---:|---:|
| k4 | 0.8376 | 0.1622 | 0.1796 | 37.16 |
| k6 | 0.9206 | 0.1756 | 0.1904 | 15.28 |

## Validation and resources

21 preflight tests passed. Historical-engine comparison, scalar clipped recurrence, exact compensated-amplitude replay including clipping, exact winner/norm checks, independent streams, frozen chance and completed-block resume/corruption rejection passed. Both stage audits verified all raw hashes, regenerated all task identities, recomputed metrics/analysis and exactly replayed their first complete block. No failed campaign, exclusions or nonfinite values.

The first preflight attempt found a JSON-envelope reader mismatch in the new checkpoint code; it was repaired before campaign learning began. Scientific source and protocol were then frozen. No independent reviewer or subagent was used.

Protocol deviation: the preflight stream-separation test instantiated development block 100/episode 0 and evaluation block 1000/episode 0 before freeze, comparing only their task hashes. No learner ran on those inputs, no performance was inspected, and they did not enter tuning before the declared stages. Thus the literal promise to defer all evaluation input generation until selection was not met, although evaluation performance remained held out. No episode was removed or replaced, and the sample was not extended.

| Stage | Run wall seconds | Summed worker CPU seconds | Maximum individual worker MiB | Retained MiB | Audit seconds |
|---|---:|---:|---:|---:|---:|
| development | 11.4 | 28.4 | 100.6 | 49.3 | 7.9 |
| evaluation | 42.1 | 111.5 | 68.5 | 109.2 | 12.7 |

Three local CPU processes; CPython 3.12.14, NumPy 2.3.5. Worker peak memory is not aggregate concurrent memory. These measurements concern the current session machine, not the colleague workstation.

## Scope and next step

This is one larval-derived representation and the existing synthetic associative assay. Population remains 73 and weights reset between episodes. More repetitions are not more persistent memories. Nominal update matching does not fix clipping, errors or chosen-action histories. The tuning budget is bounded; it does not establish global optima. Representation diagnostics cannot identify a unique causal mediator.

Proceed to [EXP-006 persistent-memory load/similarity design](EXP-006-design.md), finalize and validate its confirmation protocol, then compare native K4/K6, direct-input delta and randomized sparse N73 learning under explicitly matched training exposure. Homeostasis follows a measured participation/capacity limitation; growth and circuit transfer keep their roadmap gates. EXP-006 has not been run.
