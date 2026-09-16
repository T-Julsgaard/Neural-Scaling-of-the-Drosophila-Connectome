# Independent assessment of the next research steps

2026-09-13. Requested strategic review, based on project records, implementation inspection, saved analysis and a targeted primary-literature check. This is a recommendation, not a frozen protocol or a new experimental result. No new learning campaign was run. Existing results and scientific implementations remain unchanged.

## Recommendation

Take a bounded N73 mechanism study as the next experiment, and make a persistent-memory benchmark the next major milestone. Design that benchmark now rather than waiting for a positive mechanism result. Restore strong simple comparators and use the benchmark to decide whether activity regulation, rewiring or population growth is justified. Validate the resulting explanation or limitation in another circuit after the benchmark is informative.

The central question should become: **Under what memory load, cue similarity and noise conditions does changing activity or adding representations improve learning, retention and adaptation per resource?** This preserves the scaling ambition while giving it a testable operating regime.

The two suggested routes are sensible but incomplete. They underemphasize direct-input baselines, representation stability, activity homeostasis, adapter dependence and the distinction between a fixed-parameter intervention and the best performance each architecture can achieve. Avoid a succession of ever-narrower diagnostics on the same easy assay.

## What the project has established

- A reproducible small learning pipeline exists: equation-level author-runtime comparison, frozen development/evaluation streams, recovery records, artifact audits and 47 EXP-004 preflight tests. Those are recorded checks; this review did not repeat the full raw-artifact audit.
- The implemented learning system is a fixed 40-input to 73-mature-KC larval projection, global winner selection, and two synthetic output units with generic delta learning. It contains no recurrent brain dynamics, actual MBON circuit or explicit dopamine/APL circuit. It is a useful connectome-derived feature-learning assay.
- EXP-003's structured growth prior failed its planned practically useful advantage over its degree-matched growth null. This does not test every feature of native organization: the principal null leaves the original 73 cells intact and randomizes added connections.
- EXP-004 supports normalized K4-to-K6 activity changes. Its fixed-readout primary retention effect is +5.37 percentage points [3.89, 6.97], averaged over N73 and N110. The corresponding population effect is -5.03 points [-7.27, -2.86]. These are planned 98.333333% intervals.
- At N73 with full readout, K6 improves post-interference performance by +6.54 points [4.73, 8.46] and early reversal by +4.41 [2.32, 6.49]. These are exploratory 95% intervals. The fixed-readout diagonal growth gain from EXP-003 did not clearly recur in EXP-004.

Sources: [EXP-002 baseline](../experiments/EXP-002-baseline-results.md), [EXP-003 confirmation](../experiments/EXP-003-confirmation-results.md), [EXP-004 report](../experiments/EXP-004-results.md), [benchmark](../BENCHMARK_SPEC.md).

## Findings that change the next design

**A simpler comparator remains competitive.** EXP-002 direct-PN delta retention was .982 versus .916 for native delta, while early reversal was .693 versus .743. These are within-EXP-002 profile means, not evidence of dominance or a paired significance claim. Never compare the .982 directly with EXP-004's .961 as though they shared tasks. Bring direct PN back into fresh paired comparisons, along with a same-N randomized sparse encoder. The native-derived system must earn its added complexity through a capability/resource tradeoff.

**The current task scarcely tests storage scaling.** Weights reset after each episode. Reversal repeatedly uses one cue pair; interference introduces only one additional pair before returning to the first. Thousands of reset episodes improve precision but do not create thousands of simultaneously retained memories. Acquisition and N73/K6 retention are near ceiling. This makes cumulative memory load more informative than another unconstrained size sweep.

**The learning-rate confound has a specific mathematical form.** With K winners of amplitude a=10/K, the full feature squared norm is K*a^2=100/K: 25 at K4 and 16.6667 at K6. For the implemented two-output delta learner, away from nonnegativity clipping,

`Delta q(x') = 2 * eta * error(x) * dot(x', x)`.

Thus same-cue update sensitivity depends on eta times squared norm; interference depends on cross-cue overlap as well. At eta=.01, the nominal same-cue coefficients are .5 and .3333. K6 therefore changes much more than the number of participating cells. This equation follows from [the implemented update](../exp002/baseline.py); it is not a measured causal explanation. Clipping, changing choices and reward histories prevent a simple scalar match from guaranteeing identical learning.

**The readout control changes the representation.** The bottleneck maps native cells by numeric ID modulo 32, averages within bins, then renormalizes each input to total activity 10. Added cells alter bin occupancies and therefore native-cell coefficients, even before accounting for winner competition. This is an arbitrary adapter with a fixed learned-weight count, not fixed representational access. The full-readout K6 population cost means the bottleneck cannot explain all growth harm. Inspect [the encoder](../exp004/inputs.py).

**The retention signal is worth explaining.** Saved EXP-004 secondary estimates show that at N73/full readout the K6 advantage before interference is only +0.52 points [-0.28, 1.22]; the difference in before-to-after retention change is +6.03 [4.15, 8.00]. Thus the observed post-interference gain is not simply a large initial-performance advantage. This is an inspection of already saved exploratory estimates, not a new test. It does not establish whether gentler updates, noise stability or overlap caused the difference. Source: `secondary_contrasts.structured_full_active_at_73` in [saved analysis](../results/exp004_evaluation/analysis.json).

## Ranked program and gates

| Priority | Work | Decision value and completion condition |
|---|---|---|
| 1 | Bounded N73 mechanism experiment | Determine whether K6 adds value after update matching and equal tuning opportunities; distinguish update scale, representation stability and interference. Complete even if the answer is a narrow negative result. |
| 2 | Persistent memory load and cue-similarity benchmark | Find where simpler and native-derived models fail, and whether a change improves the retention/adaptation tradeoff. Specify before observing new confirmation results. |
| 3 | Activity homeostasis; then targeted rewiring if indicated | Address uneven feature participation without adding cells. Require held-out benefit over ordinary hyperparameter tuning and appropriate controls. |
| 4 | Independent circuit validation | Test a frozen intervention or predicted limitation in an independently reconstructed circuit, preferably adult. Do not require every earlier comparison to be positive. |
| Conditional | Renewed population growth | Proceed when a diagnosed representational limitation makes useful added features plausible; test competition and preservation of learned function. |
| Reserve | EXP-001 recurrent capacity assay | Best distinct branch if the feedforward associative system ceases to answer the mission's questions; requires its own validation and task justification. |
| Later | Bounded evolution, modules or embodiment | Use an informative held-out capability battery first; compare search with equal-budget random search. A larger platform is currently lower information per effort. |

These are scientific judgments, not measured numerical utility rankings or execution-time promises.

## Next experiment: mechanism at fixed population

Use full N73 readout as the main mechanistic comparison: N and learned-weight count are already identical across K. Keep the legacy bottleneck as a secondary bridge rather than making its adapter central again.

Begin with four core conditions at total activity 10:

| Condition | K | Per-winner activity | eta | Nominal `2*eta*||x||^2` |
|---|---:|---:|---:|---:|
| Historical K4 setting | 4 | 2.5 | .01 | .5 |
| Historical K6 setting | 6 | 1.6667 | .01 | .3333 |
| K4 with smaller updates | 4 | 2.5 | .0066667 | .3333 |
| K6 with matched larger updates | 6 | 1.6667 | .015 | .5 |

These are analytical starting controls, not selected optima. Add the bounded amplitude factorial K={4,6} by a={2.5, 10/6} at shared eta, plus any norm-matched counterparts needed by the prespecified contrasts. This tests fixed per-cell amplitude and fixed total activity explicitly. State which resource each comparison changes. Check initialization scaling and clipping before freeze; unchanged initial q=0 does not imply identical clipping dynamics when equal positive/negative starting weights are retained.

Instrument the actual change in selected-cue value and in unchosen/old-cue values, update norms, clipping frequency, within-cue repeatability under noise, between-cue overlap, lifetime participation and learning curves. Record both pre- and post-interference performance and learning of the intervening cues. A system can retain old information by failing to learn the new information.

Use a small fixed-action/reward replay diagnostic to separate update mechanics from diverging behavior. A replay is explanatory validation, not a replacement for online learning with chosen-action feedback. Use geometry measurements to make predictions; correlations alone do not prove mediation.

Separate two questions in development: a fixed-setting causal intervention and each K's achievable performance with the same bounded eta/temperature tuning budget. Freeze final choices before fresh evaluation. If tuned K4 matches tuned K6's capability profile, classify the practical gain as recoverable by tuning even if fixed-setting dynamics remain different. If a residual K effect survives, carry its predicted stability/overlap mechanism into the new benchmark. If intervals remain wide, report uncertainty and move to the planned benchmark rather than extending the old sample.

Before execution, specify primary contrasts, practical margins, acquisition/new-learning guardrails, independent task blocks and sample size using development variance or explicit conservative assumptions. The old 32-block budget and 98.33% coverage are not automatic requirements for a different contrast family.

## Next major milestone: test useful capacity

Construct a continuous sequence of multiple independently rewarded cue associations, without resetting weights between associations. Probe all previously learned cues without updates. Cross memory load with controlled cue similarity, while keeping a separate noise sensitivity and reversal condition. Compare exposure per association and total learning budget explicitly: increasing memory count must not silently become decreasing training per memory.

Candidate development levels could be 2, 4, 8 and 16 cue pairs, with low/high prototype overlap. Choose a manageable final grid before confirmation; these levels are proposals. Report performance versus load, forgetting versus memory age, intervening-task acquisition, reversal speed and noisy-cue recognition. Any capacity threshold needs a prospective definition.

Include native K4/K6, direct-PN delta and a same-N randomized sparse representation with declared degree/contact constraints. Give models the same observations, reward access and development budget, and report their different parameter/compute costs. An oracle with true cue identity may validate task learnability, but is not a fair biological-performance comparator.

Reserve a distinct regimen, such as nonlinear compound-cue discrimination, for transfer after selection; changing cue seeds alone is insufficient. Load/similarity tests themselves extend the associative assay and should not be called general intelligence or unrestricted adaptation tests.

## Most promising alternative: use existing cells more evenly

The baseline's 38.8% never-active features motivates a small homeostatic threshold or gain intervention at N73. Fit any calibration on unlabeled development stimuli and freeze it for held-out evaluation. If continuing unsupervised adaptation is desired, declare that as a separate algorithm and account for its data access. Compare with global K/eta tuning and a matched sham or shuffled calibration; do not optimize cell participation against evaluation rewards.

Measure whether participation becomes more even AND whether memory performance improves. Maximizing participation is not itself the scientific target. Compensatory variability and activity equalization already have close computational precedent, so novelty would lie in the controlled comparison and transfer, not in inventing homeostasis. [Abdelrahman et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34845010/).

If performance errors instead implicate particular input collisions, test bounded rewiring against random edits with equal edit/search budgets and weight-only tuning. If growth is revisited, include a construction that preserves the ancestor's feature map/readout at initialization, then enables new features. Global top-K growth currently allows new cells to displace old winners; added capacity and representational disruption should be separately visible. A gated preservation control is a modeling intervention, not a physiological claim.

## Literature and scientific positioning

Expansion-layer theory already links learning to representation dimension and noise sensitivity. This supports a load/geometry analysis, while narrowing novelty claims for sparse expansion itself. [Litwin-Kumar et al., 2017](https://www.sciencedirect.com/science/article/pii/S0896627317300545).

A 2026 experimental study reports that sleep deprivation increases KC activity/odor overlap and impairs similar-odor pattern separation while sparing classical conditioning. That differs from this synthetic intervention and does not contradict its measured retention result. It makes cue similarity a particularly informative challenge to the idea that increasing participation is broadly helpful. This review inspected the indexed primary article summary; full-text retrieval encountered an access challenge, so no detailed methodological reproduction is claimed. [Chen et al., 2026](https://pubmed.ncbi.nlm.nih.gov/41844155/).

Developmental compensation after population manipulation motivates testing coordinated wiring/activity adjustments rather than expecting arbitrary added cells to work automatically. [Elkahlah et al., 2020](https://elifesciences.org/articles/52278v1). Structural perturbation of the fly olfactory circuit also has direct prior computational work; the project's contribution must extend beyond showing that edits change a task score. [Xie and Ocker preprint](https://arxiv.org/abs/2509.19351).

The strongest plausible paper would explain when activity regulation versus population expansion improves a capability/resource frontier, with strong simple baselines and independent task/circuit evidence. The present work supports a narrower assay-specific result. A defensible negative account of failed scaling and its mechanisms is also useful; a positive growth or evolution story is not a prerequisite.

**Concrete next action:** draft one prospective N73 mechanism protocol and one persistent-memory benchmark specification, including direct-PN/randomized baselines, measured update diagnostics, and a decision gate for activity homeostasis. Finish those designs before launching another campaign.
