# EXP-006: persistent-memory load and similarity — audited results

2026-09-14. Priority 2 complete: six development and 32 confirmation blocks; nine preflight tests, complete task/metric audits, exact full-block replay in both stages. No weight resets between memories or during reversal. No performance-based exclusions, retuning or sample extension.

[Frozen protocol](EXP-006-protocol.md) · [analysis and intervals](../results/exp006_confirmation/analysis.json) · [audited run](../research/runs/EXP-006-confirmation.json) · [all profile values](../results/exp006_confirmation/profiles.csv) · [memory-age table](../results/exp006_confirmation/memory_age.csv)

## What the experiment establishes

Six winners continue to help under persistent memory, including noisy probes. At 16 similar cue pairs with 128 presentations per pair, K6 retains 78.74% versus K4 71.14%: +7.60 percentage points [4.68,10.43], primary 98.75%. At noise .3, the advantage is +6.06 pp [3.61,8.31]. This preserves the useful K6 direction from EXP-005 under a substantially different memory task.

The important limit is cumulative forgetting. K6 immediately learns the similar pairs at 98.65% on average, then retains only 78.74% after all 16 pairs. Its retention falls 18.22 pp [14.05,22.21] from load2 to load16 despite constant exposure per pair. Learning later pairs therefore damages earlier associations; the load cost cannot be attributed simply to fewer presentations per memory.

Direct input reaches 85.88% retention in that condition with 80 learned weights versus 146 for sparse circuits. Its descriptive paired advantage over native K6 is +7.15 pp [4.83,9.36], 95%. Direct input also has better noisy retention and reversal profiles. The input contains usable information that the tested sparse encoding plus readout-learning setup does not retain as effectively. This does not identify whether representation collisions, shared-feature updates, or bounded optimization is the unique cause.

The additional similarity penalty predicted for K6 was not established: at load16, overlap6 minus overlap2 retention is -0.02 pp [-5.21,5.13], primary 98.75%. Similar cues do alter geometry, and low-load point estimates are worse, but a high-load retention penalty is inconclusive. Do not call these conditions equivalent or claim reproduction of the Chen et al. phenotype.

Randomized K6 has the same certified load as native K6. Native minus randomized K6 retention at the difficult condition is +1.69 pp [-1.01,4.37], descriptive 95%; no clear native-wiring advantage is established there.

## Prespecified primary contrasts

All four are paired across 32 independent blocks, constant-per-pair exposure. Intervals are nominal Bonferroni-adjusted 98.75% percentile bootstrap intervals. Numbers are percentage points.

| Contrast | Estimate [interval] |
|---|---:|
| K6 minus K4, load16/overlap6 retention | 7.60 [4.68, 10.43] |
| K6 minus K4, load16/overlap6 noise .3 | 6.06 [3.61, 8.31] |
| K6 load16 minus load2, overlap6 | -18.22 [-22.21, -14.05] |
| K6 overlap6 minus overlap2, load16 | -0.02 [-5.21, 5.13] |

## Capability criterion and its limits

Largest tested load with simultaneous lower bounds above .80 for both mean retention and immediate new learning, requiring every lower tested load to pass too. One-sided Bonferroni bootstrap bounds cover 160 checks across experimental models/conditions/endpoints at nominal familywise 95%; these are approximate bootstrap bounds. Certification concerns the final acquisition probe at noise .1, not post-reversal retention or stronger noise. No interpolation or extrapolation beyond 2/4/8/16 pairs. Failure to certify does not by itself prove the population mean is below .80.

| Model | Overlap2, 128/pair | Overlap6, 128/pair | Overlap2, 512 total | Overlap6, 512 total |
|---|---:|---:|---:|---:|
| Native K4 | 4 | 2 | 4 | 2 |
| Native K6 | 8 | 8 | 8 | 8 |
| Direct input | 16 | 16 | 16 | 16 |
| Random K4 | 4 | 4 | 4 | 4 |
| Random K6 | 8 | 8 | 8 | 8 |

**Passing this average criterion does not mean every memory is safe.** At load16/overlap6/128 per pair, mean worst-pair retention is only 11.35% for K6 and 26.77% for direct input. These are averages of each sequence's minimum pair probability; chance is 50%. Some memories are strongly reversed or lost even when average retention passes. The next intervention should report these tails, not optimize mean capacity alone.

For K6/overlap6/128 per pair, simultaneous retention lower bounds at loads 2/4/8/16 are 93.84%, 85.56%, 84.71%, 73.66%; new-learning lower bounds all exceed 97%. The failure at load16 comes from retention, not the new-learning guardrail.

## Joint profile at 16 similar pairs

128 presentations per pair; mean percentages. “Forgetting” is immediate post-learning minus final retention in pp. Other profile intervals and paired comparisons are descriptive 95% and available in the linked analysis/CSV; only the four contrasts above have primary multiplicity control.

| Model | New learning | Retention | Forgetting | Noise .3 | Reversed pairs | Unchanged after reversal |
|---|---:|---:|---:|---:|---:|---:|
| Native K4 | 97.35 | 71.14 | 26.21 | 68.28 | 80.95 | 62.92 |
| Native K6 | 98.65 | 78.74 | 19.91 | 74.34 | 84.69 | 69.32 |
| Direct input | 98.88 | 85.88 | 12.99 | 81.66 | 88.78 | 75.43 |
| Random K4 | 97.03 | 72.37 | 24.65 | 68.82 | 79.22 | 58.64 |
| Random K6 | 98.48 | 77.04 | 21.44 | 72.65 | 82.98 | 64.55 |
| Identity oracle | 99.77 | 99.77 | 0.00 | 99.77 | 99.81 | 99.76 |

K6 improves new learning by +1.29 pp [0.67,2.08], reversal by +3.74 [0.77,6.74], and unchanged-pair retention after reversal by +6.40 [2.88,9.87] versus K4 (descriptive 95%). The retention gain does not come with a demonstrated new-learning or reversal deficit. Reversal still damages unchanged memories substantially; all pairs are probed after the entire reversal phase, so earlier reversed pairs can also suffer further interference.

Higher noisy-probe performance is distinct from a smaller noise penalty. In this condition the .1-to-.3 noise cost is 4.40 pp for K6 and 2.86 pp for K4; K6-minus-K4 cost is 1.54 [0.62, 2.51] pp, descriptive 95%. Thus K6 performs better at both noise levels, but its loss when noise increases is larger here. See the [supplementary noise-cost diagnostic](../results/exp006_confirmation/noise_costs.json); this post-confirmation decomposition does not replace the prespecified noisy-performance contrast.

The oldest K6 pair in this condition retains 66.46% after 1,920 subsequent presentations (32.09 pp forgetting); pair8 retains 67.78% after 1,024 subsequent presentations; the newest retains 98.67% with zero subsequent presentations. The full memory-age table reports every pair; these are descriptive examples, not a fitted monotonic law.

## Exposure and similarity controls

| Load | Presentations/pair: constant-per-pair | Acquisition total | Presentations/pair: constant-total | Acquisition total | Additional reversal presentations |
|---|---:|---:|---:|---:|---:|
| 2 | 128 | 256 | 256 | 512 | 128 |
| 4 | 128 | 512 | 128 | 512 | 256 |
| 8 | 128 | 1024 | 64 | 512 | 512 |
| 16 | 128 | 2048 | 32 | 512 | 1024 |

At load16/overlap6, reducing exposure from 128 to 32 per pair changes K6 new learning from 98.65% to 95.43% and retention from 78.74% to 77.92%. K4 retention is 71.14% versus 73.33%; more training is not uniformly better for old memories. These descriptive exposure comparisons use coupled streams and are not new primary tests. All models receive identical input observations, potential rewards and choice uniforms; realized choices and hence observed rewards may differ.

The cue family uses a shared 2- or 6-input core, exact within-pair intersection, and unique ten-active-input prototypes. Across-memory overlap is fully saved, not assumed equal to within-pair overlap. At load16 in the similar condition its mean intersection is 6.474/10, range 6–9. This manipulates clustered similarity across memories as well as within each pair; it does not isolate one type of similarity.

![Retention with equal exposure per memory](../results/exp006_confirmation/retention_per_pair.png)

![Retention with equal total acquisition exposure](../results/exp006_confirmation/retention_total.png)

Shading is descriptive pointwise 95% block-bootstrap uncertainty. Dashed horizontal .80 is the mean-retention threshold, not a confidence bound; visual crossings do not define certified capacity.

## Representation diagnostics and resource comparison

At load16/overlap6/128 per pair, K6 noisy-to-clean representation cosine is .946 versus K4 .874; unused-cell fractions are 41.78% versus 57.79%. Between-memory clean cosine is slightly higher for K6 (.535 versus .525), while exact identical representations occur less often (.53% versus 4.25% of cross-memory comparisons). These descriptive features are compatible with a role for stability and feature reuse, but no mediation or unique cause has been established. Complete input overlaps, representation matrices and participation/stability summaries are retained in the raw arrays and [geometry report](../results/exp006_confirmation/geometry.json).

| Model | Learned weights | Encoding work per cue | Other resources |
|---|---:|---|---|
| Native/random sparse | 146 | Executed dense 40×73 projection: 2,920 multiply-accumulate terms plus sorting 73 values; 365 nonzero anatomical edges | 73 cells, exactly K4 or K6 active; total activity 10 |
| Direct input | 80 | Copy 40 clipped PN activities; no projection or winner sort | All input information available to the readout |
| Identity oracle | 4L effective weights | True cue identity to one-hot feature; privileged validation control | 32 allocated features, only 2L used, never an experimental competitor |

Three independently switched null circuits per block preserve both binary degree sequences and each KC's contact multiset. Each used 14,600 accepted switches (40 per native edge); overlap diagnostics at 10/20/30/40 sweeps are saved per block. These audits verify invariants and extensive switching, not uniformity over every admissible graph. Null replicates were averaged before inference, not counted as extra task blocks.

All experimental families received the same eight development candidates. Selected eta/T: .003333/.1 for native/random K4/K6, .006667/.1 for direct input, .003333/.1 for oracle. One global setting per family; no condition-specific tuning. The grid is bounded and several choices are at its lower learning-rate edge, so this is not an optimized-capacity ceiling over all possible hyperparameters.

## Validation, execution and deviations

Validation pilot: 18.40 seconds, 63.19 MB peak process memory; exact full-block replay. Confirmation block computations total 593.19 CPU seconds and 648.72 summed worker-wall seconds with three workers; peak worker memory 60.78 MB; raw checkpoint storage 23.72 MB. Summed worker time is not elapsed campaign time and excludes the audit/replay. Development totals 130.77 CPU seconds. No paid compute or separate workstation execution.

Nine preflight tests cover streams/exposure, exact overlap/uniqueness, null invariants, independent scalar update reference, scalar versus batch sequence behavior, persistent boundary hashes, read-only probes, deterministic replay, oracle adequacy and metric definitions. All 6 development and 32 confirmation checkpoints pass checksums, regenerated task digests, continuity checks and metric recomputation. One complete block in each stage replays exactly, including arrays and boundary hashes. The oracle retains approximately 99% across the battery and has exactly zero acquisition forgetting, validating the task/reward pipeline when cues have separate features.

Protocol timing deviation: the stream-independence preflight constructed prototype arrays for development block100/overlap6 and confirmation block1000/overlap6 before their stage contracts. No learner or performance evaluation used those fixtures before freeze, and no outcome-based tuning or sample replacement occurred. This is a deviation from literal input-generation timing, not evidence of a fully untouched-input preflight. Historical EXP-002–005 source/results were preserved.

WindowsApps Python was unavailable, so execution used bundled CPython. CIM inventory was denied; platform, logical-processor count and process counters are recorded without inventing a hardware model. Rendering used the existing cached Matplotlib under read access escalation. No experimental sample failed or was excluded. Run records include source/configuration hashes, dirty-worktree commit context and reproducible stream definitions.

## Decision and next milestone

Close priority 2. K6 is certified through load8 and is not certified at load16; K4 reaches its certified boundary earlier. This identifies a boundary for the tested performance criterion, not an exact theoretical maximum or proof that K6 population-mean retention is below .80 at load16. Six-winner coding helps, but direct input and the oracle show headroom without adding cells. Severe worst-memory losses and reversal interference make durable retention the practical target.

Proceed next to the already ordered priority 3: a separately frozen test of development-calibrated threshold/gain homeostasis across existing cells, compared with ordinary tuning and shuffled calibration. Use load8/load16, both exposure regimes and similarity conditions, and retain direct/random baselines. Require useful retention and tail behavior alongside new learning and reversal; reducing unused cells is not itself success. Do not claim homeostasis already helps, and do not start growth from this result alone. Cross-circuit validation follows a specific prediction.

Scope remains one static larval anatomy, synthetic clustered cue pairs, and this chosen-action delta learner. The experiment limits the tested encoding-plus-learning system, not the theoretical information capacity of every 73-cell representation. Chen et al. found sleep-related pattern-separation impairment with disrupted sparse coding in flies; that motivates stress testing but is not a result reproduced here. [Chen et al., Current Biology (2026)](https://pubmed.ncbi.nlm.nih.gov/41844155/).
