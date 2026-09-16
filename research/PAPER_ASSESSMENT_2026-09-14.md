# Findings, novelty and paper assessment after EXP-008

2026-09-14. Requested candid assessment of the four completed priorities. Based on reports, protocols, selected source inspection, saved geometry and calibration records, and targeted primary-literature searches. This review did not run new experiments, repeat all artifact audits, reproduce external papers or establish priority through an exhaustive literature search.

## Verdict

The project has a coherent set of controlled computational findings and a plausible narrow paper. It has not established a major new biological mechanism, a general neural scaling law, or a better general-purpose learning algorithm. The best candidate contribution is a bounded negative finding: partial participation calibration does not add practically useful persistent retention beyond ordinary tuning in two connectome-derived feedforward models, despite changing recruitment. Its strength is the controlled comparison and prospective transfer of the limitation; its weakness is the narrow model/task regime and incomplete causal explanation.

A carefully scoped preprint or short computational study is reasonable to draft. Calling the current evidence a strong, submission-ready neuroscience discovery would be premature. Publication prospects depend on positioning, independent scrutiny and the additional discriminating evidence below. Negative results can contribute, but their sign does not automatically confer novelty or importance.

## What the four steps found

| Priority | Evidence | Supported interpretation |
|---|---|---|
| Activity mechanism, EXP-005 | Tuned K6 minus K4 retention +3.78 pp [2.39, 5.27], primary 98.75%; benefits also survive nominal update/norm matching | Gentler updates alone do not explain the larval K6 benefit. Stability and participation remain candidate contributors, not uniquely established mechanisms. |
| Persistent memory, EXP-006 | At 16 similar pairs and 128 presentations per pair, K6 immediate learning 98.65%, final retention 78.74%; K4 retention 71.14%; direct input 85.88% | The tested system learns new associations but forgets old ones. K6 improves the tested capability profile, while direct input shows remaining headroom. This is not an absolute neuron-count capacity limit. |
| Participation calibration, EXP-007 | Calibrated 79.28% versus ordinary 79.55%; difference -0.27 pp [-1.67, 1.13], primary 98.333333% | Practical equivalence within the prospective +/-3 pp band for this endpoint. The proposed intervention failed its useful-benefit gate. |
| Adult transfer, EXP-008 | Adult calibrated minus ordinary -0.19 pp [-1.01, 0.68], primary 98.333333% | The bounded equivalence prediction transfers to an independently reconstructed adult subcircuit using the same task/learner family. This does not show universal homeostasis failure. |

Evidence: [EXP-005](../experiments/EXP-005-results.md), [EXP-006](../experiments/EXP-006-results.md), [EXP-007](../experiments/EXP-007-results.md), [EXP-008](../experiments/EXP-008-results.md).

Historical EXP-003/004 further showed that the initial apparent growth gain was conditional on activity/readout choices; the crossed experiment did not establish an independent useful population gain. No complete neural scaling law follows from those interventions, or from comparing larval and adult scores.

## What is surprising within this project

**Recruiting additional cells did not buy useful memory.** In EXP-007, unused presented cells fell from 40.88% to 35.66%, but mean retention did not improve beyond ordinary tuning. Noisy-response stability declined and average cross-memory similarity also declined. Thus apparently favorable changes in participation and overlap did not translate into the intended behavioral outcome. The hypothesis motivating homeostasis was plausible and failed its practical test; it should not be rewritten as if this null outcome had been the original prediction.

**Direct input is a demanding baseline.** EXP-007 direct input retained 85.52% with 80 reward-learned weights versus 79.55% and 146 for ordinary sparse coding. Adult means are 96.12% with 208 weights for direct input versus 93.94% and 1,180 for ordinary sparse coding. These profile means should not be converted into new primary claims or a universal dominance statement. They do undermine any current claim that anatomical expansion is necessary for this benchmark.

**Good average performance can hide severely damaged memories.** EXP-007 ordinary K6 has 79.55% average retention, but the mean of each sequence's worst-pair probability is 13.54%, and 18.36% of pairs fall below chance. These are different statistics, not a contradiction. Forgetting and averaging problems are known; the quantified dissociation is useful evidence here.

**The adult follow-up reproduced a limitation.** It did not establish that the larval activity-density optimum transfers. Ordinary adult tuning selected K32, whereas calibrated methods were restricted to K48. Nor did it establish an adult population-size effect: anatomy, input dimensionality, subtype and coding adapter all changed together.

## Prior work and novelty

| Candidate claim | Prior work | Assessment |
|---|---|---|
| Sparse coding/expansion can improve learning and memory | Litwin-Kumar et al. 2017; Ardin et al. 2016; Zou et al. 2025 | Established territory. A K4-to-K6 improvement alone is weak novelty. |
| Compensating uneven KC activity can improve memory | Abdelrahman et al. 2021 | Direct precedent. Our offset implementation is an adaptation, not invention of homeostasis. |
| Noise, reliability and overlap create discrimination tradeoffs | Srinivasan et al. 2023 | Direct precedent for the broad principle. Our recruitment/stability account remains a hypothesis. |
| Fly-inspired networks address continual forgetting | Zou et al. 2025 and earlier MB models | Established research area. Persistent-memory benchmarking alone does not establish originality. |
| Partial frozen calibration gives no useful retention gain beyond strong tuning across larval/adult extracted projections | No exact match identified in this targeted check | Most plausible incremental contribution. Neither worldwide priority nor a general principle is established. |

Primary sources checked:

- [Abdelrahman, Vasilaki and Lin, 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8670477/): modeled compensation of physiological parameter variability, with anatomy and transfer analyses. Our normalized, fixed-top-K, sequential delta system differs substantially; our result does not refute theirs.
- [Zou, Zang and Ji, 2025 preprint](https://arxiv.org/abs/2502.01427): sparse expansion and coding in continual learning, including direct/no-KC baselines and several learning strategies. Inspected the primary PDF's model discussion and parameter tables. Different expansion ratios, coding levels, tasks and update rules prevent interpreting our direct-input advantage as a failed replication. This close source was not found in the current readable bibliography and deserves a full comparison before any novelty claim.
- [Srinivasan et al., 2023](https://repository.cshl.edu/id/eprint/41306/): measured and modeled reliability/variability tradeoffs in fly and mouse odor representations. Inspected the institutional primary article summary and indexed methods/discussion.
- [Ardin et al., 2016](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004683): memory capacity as a function of network size and activity in an MB route-memory model. Indexed primary capacity analysis inspected.
- [Litwin-Kumar et al., 2017](https://www.sciencedirect.com/science/article/pii/S0896627317300545): expansion-layer dimensionality, sparse connectivity and associative learning; previously inspected in the project assessment.
- [Xie and Ocker, 2025 preprint](https://arxiv.org/abs/2509.19351): larval circuit structural perturbations and synthetic odor classification. Its scope already prevents claiming the structural-intervention paradigm itself as new.

These sources narrow novelty but do not demonstrate an exact duplicate of the current experiment. Search non-detection is not proof of originality. This is a targeted assessment, not deep/systematic research or a completed submission literature review.

## What would concern a reviewer

1. **Weak intervention versus failed principle.** Baseline incoming weights are already normalized per cell. Calibration adds only bounded partial offsets; nearly half of selected larval offsets reach their limit. Adult recruitment changes modestly: unused presented cells fall 25.61% to 24.34% at fixed K48; effective participation rises 123.32 to 125.68. The null concerns this additional procedure, not all possible equalization or online homeostasis.
2. **Shared assay assumptions.** There are two anatomical settings, but one simplified learner and related synthetic tasks. Adult calibration equivalence may reflect a shared task/algorithm limitation. Task blocks do not become independent animals. No recurrent, real MBON, dopamine or APL dynamics were modeled.
3. **No demonstrated need for expansion.** At maximum tested load there are 32 clean cue prototypes versus 40 larval or 104 adult input coordinates. Dimension counting alone does not prove separability, but it motivates a direct learnability/rank test before treating direct-input success as surprising evidence against expansion coding. Adult PNs sharing glomerular identity receive independent synthetic coordinates, further limiting physiological interpretation.
4. **Incomplete explanation.** Average overlap and participation are descriptive. What matters to interference is the change in old cue-pair preferences after new updates. The analysis has not established a causal account that predicts behavior beyond these runs.
5. **Transfer headroom and tails.** Adult ordinary retention is about 94%; the upper 95% bound is 94.89%, just below the written 95% ceiling gate. The gate passed, but headroom is limited. Only loads4/16 were tested. Worst-pair preservation was not established in either calibration experiment; this is uncertainty, not proof of harm.
6. **Reproducibility is necessary but not novelty.** Frozen protocols, raw audits and exact replays strengthen credibility. They are not independent conceptual review, and they do not show the implementation reproduces a biological result. Disclosed earlier protocol timing deviations and shared/identical contrasts must remain visible in a manuscript.

## A defensible paper and the smallest useful extension

Working title: **Bounded participation calibration does not improve sequential retention beyond tuning in two connectome-derived mushroom-body models.** A broader title about limits of sparse coding would exceed the present evidence unless strengthened by more targeted comparisons.

The manuscript can center EXP-007/008, using EXP-005/006 to explain why the intervention was tested. Treat EXP-003/004 as motivation or supporting controls rather than giving every experiment equal narrative weight. Figures should show the primary equivalence intervals, participation versus performance, resource-matched comparisons where possible, and full memory-age/tail behavior.

For a stronger paper, prioritize discriminating evidence rather than additional confirmation seeds:

- **Bridge to a positive-control regime.** Reproduce or independently verify a closely matched published condition where compensation helps, then change normalization, calibration strength, noise or learning schedule one factor at a time. Establish whether our null reflects a bounded intervention, already-compensated baseline or the sequential-learning regime. New data and prospective choices are required; do not retune completed confirmations.
- **Separate representational information from learning interference.** On frozen encodings, compare the online learner with an offline fitted readout using training-only labels and held-out noisy probes. This is a diagnostic with different training access, not an equal-budget online competitor. Test whether proposed pair-margin geometry predicts which memories fail on fresh sequences.
- **Use a distinct task with a reason for expansion.** A prospectively defined nonlinear compound-cue discrimination or structured generalization task would test the method outside the current associative schedule. First verify that the task is learnable and that the extracted representation can express it; do not select a task only because it makes the desired architecture win.

If the project stops now, a transparent narrow empirical report is defensible. If the goal is a stronger general contribution, one bridge/mechanism study and a meaningful task transfer would do more than another small increase in sample size or neuron count. No further campaign is authorized or executed by this assessment.
