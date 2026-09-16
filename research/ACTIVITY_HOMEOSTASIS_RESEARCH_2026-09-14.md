# Priority 3: activity homeostasis across existing cells

2026-09-14. Targeted literature research and implementation-grounded experimental recommendation. No new learning campaign was run. This is a design handoff, not a frozen protocol or evidence that homeostasis improves this system.

## Recommendation

Test bounded, development-calibrated **cell-specific offsets before winner selection**, initially at N=73 and K=6. Keep six winners, amplitude 10/6, the anatomical projection and full readout fixed. Ask whether redistributing participation improves persistent retention and adaptation beyond tuning and shuffled calibration. Treat gain adjustment as a secondary alternative, and continuous homeostasis as a separate later algorithm.

This is a strong next experiment because it directly intervenes on a plausible limitation without adding cells. It is not yet an established solution. Success means preserving useful memories while learning new ones, not eliminating silent cells.

## What the project evidence actually says

The original 38.8% unused-cell statistic concerns synthetic task blocks, not biologically silent neurons. EXP-005 found a residual K6 benefit after update matching, with improved noisy-response repeatability and participation, but did not identify either as a unique mediator. [Baseline](../experiments/EXP-002-baseline-results.md); [EXP-005](../experiments/EXP-005-results.md).

The relevant current boundary is EXP-006's 16 similar pairs with 128 presentations per pair:

| Native K6 measure | Recorded result |
|---|---:|
| Immediate new learning | 98.65% |
| Final mean retention | 78.74% |
| Mean of each sequence's worst-pair retention | 11.35% |
| Unused cells during acquisition observations | 41.78% |
| Largest certified load under the prospective criterion | 8 pairs |
| Direct-input final retention in the same condition | 85.88% |

These percentages are preferred-choice probabilities where applicable. Direct input has 80 learned weights versus 146 for the sparse circuit. The failure is primarily cumulative forgetting despite successful acquisition; it is not proof of an absolute 73-cell capacity limit. Several development choices hit the lower learning-rate grid boundary. [EXP-006 results](../experiments/EXP-006-results.md).

The unused statistic includes both presented alternatives, not only the chosen cue that updates the readout: see `sequence` in [memory.py](../exp006/memory.py). Future diagnostics should distinguish presentation participation from participation in actual updates. The original and current unused fractions have different task distributions and observation windows and should not be interpreted as a longitudinal trend.

## Closest scientific precedent

**Abdelrahman, Vasilaki and Lin (2021), PNAS:** computational compensation of excitability-related variability improved associative memory; adult hemibrain correlations supported predicted compensatory anatomy. Their models adjusted excitation, inhibition or thresholds. Threshold-only equalization needed more variability than observed experimentally. Equalizing response probability helped, but less than equalizing mean activity in their graded model. Calibration on one odor class transferred imperfectly to other classes. This supports partial, bounded calibration and explicit distribution-shift testing; it does not establish benefit in this larval sequential learner. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC8670477/); [accessible published PDF, Figures 4–5](https://eprints.whiterose.ac.uk/id/eprint/181348/1/Abdelrahman%20Lin%20Proceedings%20of%20the%20National%20Academy%20of%20Sciences%202021.pdf).

**Apostolopoulou and Lin (2020):** prolonged excess APL inhibition elicited compensatory changes in KC excitation and APL activity, with subtype differences; compensation for lost inhibition was limited. This provides in-vivo precedent for regulation, not evidence that uniform activity targets optimize memory. [Author accepted manuscript](https://www.aclinlab.org/uploads/3/9/2/6/39268489/apostolopoulou_and_lin_accepted_manuscript.pdf).

**Lin et al. (2014):** disrupting KC–APL feedback increased response density and inter-odor correlation and impaired learned discrimination of similar odors. The design implication is to preserve per-cue sparsity while changing participation across cues. [Primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4000970/).

**Bergmann et al. (2026):** after prolonged KC activation, reduced APL sensitivity opposed KC compensation. Local homeostatic changes can conflict at network level. This motivates testing a single frozen intervention before introducing interacting online controllers. The present model has no explicit APL dynamics and cannot reproduce this mechanism. [Primary-study abstract](https://pubmed.ncbi.nlm.nih.gov/41784532/).

## Why balance could help, and why it might fail

Population sparsity asks how many cells respond to one cue; participation asks how frequently each cell responds across cues. These are distinct. At fixed K, underused cells can take some responses from frequent winners without increasing total activity.

An analytical motivation follows directly from the binary winner code. Let p_i be cell i's response probability over an input distribution. For two independent draws from that same distribution, expected shared winners are sum_i p_i^2. Since sum_i p_i=K, this is minimized at p_i=K/N, with value K^2/N. Thus balancing marginal participation can reduce average overlap at fixed K. This is a mathematical motivation, not a measured mechanism. Actual paired or clustered cues need not be independent; task-relevant overlap can remain high.

For the implemented opponent delta learner, away from clipping, an update using cue x changes an old pair's value difference by

`Delta[q(a)-q(b)] = 2 * eta * error(x) * dot(x_a-x_b, x)`.

Therefore measure perturbations of old **pair margins**, not only raw cue overlap. Features shared equally by both alternatives cancel in the margin. Reducing average overlap need not reduce harmful updates, and participation entropy cannot establish causal mediation.

Homeostasis can also promote weak, noise-sensitive winners, collapse useful response margins, or overfit the calibration distribution. Some apparently unused cells may be selective for cues absent from the task. A broad unlabeled pool should therefore sample many independently generated cue cores, with balanced coverage of the development similarity conditions. Never calibrate separately on a confirmation sequence's own prototypes or core.

## Proposed intervention

The existing encoder computes z=uP, sorts cells, then assigns equal winner amplitude. Use adjusted scores

`score_i = z_i - theta_i`

before the same top-K selection. Start theta at zero. Estimate baseline participation p_i^0 on a dedicated unlabeled calibration pool and define a partial target

`target_i = (1-lambda)*p_i^0 + lambda*K/N`.

Candidate strengths lambda={0, .25, .5} are a proposed engineering starting grid, not biological constants. Fit offsets with batch negative feedback: increase theta for cells above target and decrease it for cells below target. Project updates onto bounded, zero-mean offsets; use a fixed iteration budget and record residual imbalance. Define the bound relative to a development-only drive scale, for example .25 times the median nonzero across-input drive standard deviation, and examine its effect on winner margins before freezing. This numerical bound is provisional and carries no physiological interpretation.

Freeze one calibration vector per anatomy and K before rewarded confirmation. For randomized anatomies, apply the identical fitting procedure on the same unlabeled pool, without accessing their confirmation task inputs. Keep tie priorities fixed. Reject invalid or nonfinite fits, but do not exclude poorly performing cells or runs.

At fixed K and amplitude, response probability and mean output activity are proportional in this implementation. The intervention preserves total activity 10 and squared feature norm 100/K, so it removes a nominal update-scale confound. Actual errors, chosen actions and clipping can still differ and must be measured.

A gain alternative would use score_i=g_i*z_i with bounded positive gains before ranking. Applying a per-cell gain to projection columns and then renormalizing each column to sum one would cancel it exactly. Post-winner gains would instead change feature norms and update scale. A common offset or positive common gain cannot alter top-K membership and is only an invariance check.

## Comparisons that answer the question

| Arm | What it establishes |
|---|---|
| Native K6, zero offsets | Contemporary paired baseline |
| Native K6, calibrated offsets | Fixed-K participation intervention |
| Native K6, shuffled calibrated offsets | Whether the cell-specific assignment matters beyond offset heterogeneity |
| Equally tuned native K4/K6 without offsets | Whether ordinary K/eta/temperature tuning recovers the practical benefit |
| Degree/contact-preserving random K6, with and without calibration | Whether benefit depends on native wiring |
| Direct PN learner | Whether sparse encoding earns its additional resources |
| Identity oracle | Task and persistent-memory implementation validation only |

Use several prespecified offset permutations, averaging shams within each task block rather than counting permutations as independent evidence. Preserve their offset distribution and bounds. A sham need not match achieved participation; it tests assignment, not uniquely the participation mechanism. Give sham and uncalibrated arms fair learner tuning opportunities.

Separate two estimands: a fixed-setting intervention contrast with identical eta/temperature, and achievable performance under equal **total** development search budgets. Counting only eta/temperature choices while granting homeostasis extra rewarded searches over strengths or bounds would be unequal tuning. Fit on unlabeled inputs, select any task-dependent settings on separate rewarded development sequences, and reserve fresh confirmation streams. Expand the ordinary eta search below the old grid edge during development before treating its comparator as strong.

Frozen calibration adds 73 fitted values (72 independent after centering), data exposure and fitting work. Report these alongside the unchanged 146 reward-learned weights and 73 cells. The method uses no extra cells but is not resource-free. Online adaptation would add state and could remap stored associations; it is outside the primary experiment.

## Outcomes, inference and decision gates

Use EXP-006's persistent learning and reversal battery, emphasizing loads8/16, both similarities, both exposure regimes and noise .1/.3. Retain loads2/4 if claiming an increased certified capacity under the existing all-lower-loads criterion. A study limited to loads8/16 can establish improvement at those loads but cannot reuse old lower-load results to certify a newly calibrated model.

Prespecify final retention at load16/overlap6/128-per-pair as the main behavioral endpoint. The two essential comparisons are calibrated versus contemporary uncalibrated K6 and calibrated versus shuffled offsets. Report corrected paired intervals over independent task blocks; choose the block count from fresh development variance and intended precision, not automatic reuse of 32. Freeze the contrast family, margins and sample size before confirmation.

A proposed practical retention margin is +3 percentage points, carried forward as a convention rather than a known biological threshold. Establishing an effect above that margin requires its lower confidence bound to exceed +3, not just its point estimate. Prespecify guardrails for immediate acquisition, reversal, unchanged memories after reversal, and the worst-pair endpoint; demonstrate noninferiority with interval bounds rather than interpreting a nonsignificant deficit as safety. A provisional maximum tolerated loss is 3 points, to finalize before confirmation. Keep worst-pair retention visible and also report a less extreme tail measure, such as the fraction of pairs below chance. Any claim of improved tails requires direct evidence, not merely passing a no-harm guardrail.

Record participation by cell and stimulus class, effective number of participating cells, clean/noisy winner agreement, rank margins, cross-memory pair geometry, exact collisions, actual update/clipping statistics and memory-age curves. Normalize observation counts when comparing unused fractions. Analyze chosen-update participation separately from presented-cue participation.

Reserve an input-distribution shift after selecting calibration, for example altered PN activation frequencies or an uncalibrated cue family. New seeds alone test generalization within the same distribution. Hold the calibration vector fixed in this test. For priority4, transfer the algorithm, bounds and selection rules to another anatomy; fit its cell-specific vector only on its declared development inputs rather than transplanting 73 offsets to unrelated cells.

Interpret outcomes prospectively:

- Better participation without behavioral benefit: recruitment changed, but useful capacity improvement is unsupported.
- Retention improves but new learning/reversal or tails worsen beyond guardrails: a tradeoff, not an overall capability improvement.
- Calibrated beats uncalibrated but not sham: targeted homeostatic assignment is not established as the explanation.
- Benefit disappears under equal tuning: ordinary optimization recovers the tested advantage.
- Useful gains survive controls but fail distribution shift: a distribution-specific calibrated encoder.
- Useful gains survive controls and transfer: evidence that balanced use of existing cells addresses part of this system's memory limitation.

The credible contribution is controlled persistent-memory and transfer evidence beyond the existing homeostasis literature. Do not claim invention of activity equalization or that a positive result proves growth unnecessary in every regime. Next action: turn this handoff into a prospective EXP-007 protocol and validation fixtures before running development and fresh confirmation.

## Research provenance

Read project EXP-002/005/006 reports, EXP-006 protocol and current encoding/update/participation code. Searched primary literature for Abdelrahman compensation, KC/APL homeostasis, sparse coding and recent opposing adaptations. Inspected the published Abdelrahman PDF's Figures4–5 discussion and code-availability statement, Apostolopoulou's accepted manuscript, indexed Lin primary text and Bergmann's primary abstract. PMC full-page access sometimes returned a challenge; the published repository PDF resolved the decision-critical Abdelrahman methods and transfer points. No author-code reproduction, supplementary-data audit or exhaustive systematic review is claimed. All proposed mechanisms, constants and decision rules above remain recommendations.
