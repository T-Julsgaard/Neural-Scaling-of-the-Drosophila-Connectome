# Shared benchmark and analysis contract — version 1

## EXP-011 compound-task extension — 2026-09-15

Two-context XOR, continuous factors/nuisance, 256 matched labeled observations, 24 independent evaluation blocks and direct/random/quadratic controls. Shuffled/local10/replay10 distinguish order, computation and historical access with the qualifications in [EXP-011](experiments/EXP-011-results.md). This is fresh-observation interpolation, not unseen-quadrant extrapolation.

Status: **EXP-002 measured baseline completed under the prospective [version 1.1 addendum](experiments/EXP-002-baseline-protocol.md)**: ten development and twenty confirmation blocks. This shared contract still applies to the three [candidate experiments](EXPERIMENTS.md). Numerical thresholds are project decisions, not established biological thresholds. D022 authorized measured baseline execution; the addendum resolves episode streams, direct-PN normalization and pre-return retention selection without changing primary hypotheses, margins or confirmation seeds. [Measured results](experiments/EXP-002-baseline-results.md).

## Claims and resource matching

Report a vector of capability outcomes alongside a resource vector. Never combine them into a single “FlyIQ” score. Separate:

1. **Scale effect:** performance change between sizes under a specified growth rule.
2. **Organization effect:** performance difference between growth/architecture rules at the same size under stated matching conditions.

Record N (modeled neural units), E (distinct directed weighted pairs), S (sum of raw anatomical contact estimates, when meaningful), free trainable parameters, persistent state bytes, peak process memory, stored bytes, forward steps, learning updates, readout fit operations, wall time, and measured energy only if a meter is available. Estimated operations are not joules. Synthetic output units and fixed adapters count in resources. Report graph construction/search cost as well as inference cost.

## Randomness and data separation

Use NumPy `Generator(PCG64)` with an explicit version in the environment lock (validation and baseline use NumPy 2.3.5). Derive streams using `SeedSequence([experiment_number, stage_code, block_seed, replicate, component])`; stage codes: 0 validation, 1 development, 2 confirmation. Component codes: 1 graph, 2 stimulus/prototype, 3 observation noise, 4 outcome table, 5 action uniforms, 6 weight initialization, 7 bootstrap. Pair stimulus, outcome-table and action-uniform streams across arms. Each learner sees only the outcome of its own chosen action; pairing does not expose unchosen rewards. The original validation episode keeps its original streams. The baseline runner appends episode index to components 2–5, shares component-1 graph priority within each block, and appends `[32, post_update_trial_count, round(sigma*1000)]` after episode for probe noise. These extensions were specified before development in protocol 1.1.

Development block seeds: 100–109. Confirmation block seeds: 1000–1019. Five validation seeds: 0–4. Never reuse confirmation seeds for configuration selection. A block is an independent task/input and randomness bundle, **not an independent animal**. Graph variants within a block are nested replicates, not extra independent biological samples. Fixed reference anatomy remains one specimen or consensus circuit.

Freeze code, graph/config hashes, hypotheses, primary contrasts, and development-selected settings before generating confirmation outcomes. Debug with validation/development data. If a bug invalidates confirmation, retain the failed run, state the reason, increment the protocol version, and use a new confirmation seed range; do not selectively remove disappointing seeds.

## Statistical analysis

Aggregate task episodes within each block, then graph replicates within each block, before comparing paired block means. Use 10,000 paired block-bootstrap resamples and percentile intervals. Report all 20 block values and effect sizes; bootstrap intervals with 20 blocks are approximate and do not substitute for biological replication.

There are three declared primary contrasts across this foundation's proposed experiments: EXP-001 native minus signed-degree null; EXP-002 feedback learner minus reward-only; EXP-003 structured 1.5× growth minus its degree-matched growth null. Use **98.33% two-sided intervals** for these three contrasts (Bonferroni familywise coverage approximately 95%). Secondary comparisons have 95% intervals and are explicitly exploratory. The separate scale contrast in EXP-003 is secondary until replicated in an independently preregistered study. Do not tune which contrast is primary after viewing confirmation results.

Report uncertainty around a practical minimum effect, not just a null test. “Support” means the lower primary interval exceeds the specified minimum. “Evidence against a practically useful benefit in this assay” means the upper interval is below that minimum; an interval spanning it is inconclusive. An interval below zero supports harm relative to that comparator. Equivalence requires the whole interval to lie within the stated ±margin. Failure of an organization hypothesis does not refute scale effects.

## Shared larval learning assay (EXP-002 and EXP-003)

Data: [D05](DATA_PROVENANCE.md), source S64 hash and `PN_left` / `KC_mature_left` indices from [reference_data_audit.json](research/reference_data_audit.json). Use raw C[p,k] counts, positive edges only. Target-normalize `P[p,k] = C[p,k] / sum_p C[p,k]`. All mature KCs have nonzero input; assert this. PN inputs are nonnegative dimensionless rates. No recurrence, measured physiology, real MBONs, or explicit dopamine neurons are claimed. Two synthetic valence output units form a learning-rule assay.

For each cue, generate a 40-dimensional binary prototype with exactly 10 active PNs, uniformly without replacement. Generate independent prototype pairs per episode; allow overlap but reject identical pairs. Add independent normal noise σ=0.1 to every coordinate and clip to [0,1] on each presentation. Compute `z=P.T@u`. Select `k=max(1,floor(0.05*N+0.5))` largest z, break ties with a fixed random per-neuron priority drawn once per graph. Set selected KC activity to `10/k`, others zero. This is an idealized global sparsity constraint, not an implemented APL neuron. Record mean and per-cell participation, covariance effective rank, and fraction never active across the episode collection.

Each episode contains 384 two-choice trials. Offer both cues in each trial, compute their values before feedback, and choose by stable softmax with temperature T (subtract maximum before exponentiation). Reward is +1 with probability 0.8 for the currently preferred cue and 0.2 for the other; otherwise −1. Independently draw both latent cue outcomes in advance for pairing, reveal only the chosen one.

Two equally weighted task families:

- **Reversal:** cue A preferred for trials 0–127, B for 128–255, A for 256–383.
- **Interference/retention:** A/B pair, A preferred, trials 0–127; independent C/D pair, C preferred, trials 128–255; return to A/B without changed preference, trials 256–383.

Randomly permute cue labels per episode. Reset learning weights between episodes but preserve them across all phases of an episode. Ten episodes per family per block (20 episodes total), each with fresh prototypes and stochastic sequences. Development and confirmation use disjoint streams and prototypes. This tests adaptation to new cue identities within specified task families, not arbitrary new tasks or zero-shot reward inference.

Online plasticity is allowed after each revealed confirmation reward. All graph construction, learning rules, learning rates, temperature, and preprocessing are frozen. No confirmation-driven threshold calibration or hyperparameter search. Probe evaluations copy the current state, use 32 fresh noisy presentations of the relevant pair, average probability of choosing its currently preferred cue, and apply **no updates**. Discard probe state, retain episode state.

Metrics:

- Primary adaptive score: mean preferred-choice probability during trials 128–159 of reversal episodes, computed from the actual pre-choice softmax probabilities.
- Acquisition: corresponding mean during trials 96–127.
- Return adaptation: trials 256–287 of reversal episodes.
- Retention: frozen A/B probe after trial 127 versus after trial 255 in interference episodes; report the difference.
- Robustness: at the final state, probes with σ=0.0,0.1,0.3; no learning during probes.
- Learning curves: 16-trial bins, reward, choice probability, active-cell participation and weight ranges. Show family-specific results.

Weights initialize to `w_plus=w_minus=0.1` for every feature. Both output units count as parameters. No arbitrary upper clipping is permitted; nonnegativity projection is specified by the rules. NaN/Inf or any absolute weight above 10^6 triggers a recorded numerical failure, not a discarded episode. Fix the cause before confirmation; report numerical failure rates if they arise under a frozen protocol.

## Storage and checkpoints

The baseline runner writes atomic per-episode artifacts and digest-checked block checkpoints containing configuration, graph/source hashes, seed derivation, the next episode, final-state artifact references, elapsed counters and schema version. No live state or RNG crosses an episode reset; interrupted episodes replay deterministically. Mid-episode state restoration and block resumption matched uninterrupted validation. Save per-trial scalar metrics, not all neural states by default; retain full-state diagnostic traces only for validation seeds 0–4. Cap each pilot campaign at 10 GB initially. Stop scheduling new blocks when free disk space would fall below 20 GB; preserve completed checkpoints before revising the storage plan. Future structural runners must retain these verified recovery properties.

## Target-machine gate

The user reports a colleague's 64 GB PC with RTX 5090 32 GB and Ryzen 7 9800X3D. The user corrected the memory type to DDR5; free storage and OS/Python/driver versions remain unverified. [Hardware provenance](research/target_hardware.json) records that correction. The current session is not the verified target. **The user skipped the separate measured workstation pilot for EXP-002 (D016).** No target benchmark is required for this bounded validation milestone, and no timings are promoted to commitments. Future scientific runs still record their actual environment and resource counters. All three candidates have CPU-first designs. If a future run exceeds 16 GB memory or projects above seven days, first stream matrices/reduce parallelism and inspect the algorithm. Any scientific reduction in seeds, tasks or controls requires a recorded protocol revision **before** confirmation. Paid compute requires a measured limitation and explicit benefit/cost proposal.

## EXP-007 completed participation extension

Homeostasis and ordinary tuning are practically equivalent within the prespecified ±3-point retention band in the primary condition. Calibrated K6 retains 79.28% versus 79.55% for ordinary tuning; difference -0.27 [-1.67, 1.13] pp (98.333333%). [EXP-007 results](experiments/EXP-007-results.md). The [frozen protocol](experiments/EXP-007-protocol.md) extends ordinary tuning below EXP-006's boundary and separates primary retention, practical margin, adaptation/tail noninferiority and capacity certification. A [matched-sham addendum](experiments/EXP-007-matched-sham-addendum.md) was frozen after development and before confirmation. Historical benchmark results remain unchanged. Priority 4 completed: Adult calibration minus ordinary tuning: -0.19 [-1.01, 0.68] pp (98.333333% interval). Transfer classification: equivalent; informative-benchmark gate passed. [EXP-008 results](experiments/EXP-008-results.md). Next: define a distinct held-out task family to test the limitation beyond this associative assay. Growth, collision-targeted rewiring and evolution retain their explicit entry conditions; no additional campaign is launched.
