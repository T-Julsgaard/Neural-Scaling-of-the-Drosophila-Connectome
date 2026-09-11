# Shared benchmark and analysis contract — version 1

Status: **scientific protocol specified; bounded EXP-002 implementation checks executed**. No development or confirmation campaign has run. This contract applies to the three [candidate experiments](EXPERIMENTS.md). Numerical thresholds are prospective project decisions, not established biological thresholds. D016 changes the EXP-002 hardware-pilot workflow, not its hypothesis, selection budget, metrics or confirmation seeds.

## Claims and resource matching

Report a vector of capability outcomes alongside a resource vector. Never combine them into a single “FlyIQ” score. Separate:

1. **Scale effect:** performance change between sizes under a specified growth rule.
2. **Organization effect:** performance difference between growth/architecture rules at the same size under stated matching conditions.

Record N (modeled neural units), E (distinct directed weighted pairs), S (sum of raw anatomical contact estimates, when meaningful), free trainable parameters, persistent state bytes, peak process memory, stored bytes, forward steps, learning updates, readout fit operations, wall time, and measured energy only if a meter is available. Estimated operations are not joules. Synthetic output units and fixed adapters count in resources. Report graph construction/search cost as well as inference cost.

## Randomness and data separation

Use NumPy `Generator(PCG64)` with an explicit version in the environment lock (bounded validation uses NumPy 2.3.5). Derive streams using `SeedSequence([experiment_number, stage_code, block_seed, replicate, component])`; stage codes: 0 validation, 1 development, 2 confirmation. Component codes: 1 graph, 2 stimulus/prototype, 3 observation noise, 4 outcome table, 5 action uniforms, 6 weight initialization, 7 bootstrap. Pair stimulus, outcome-table and action-uniform streams across arms. Each learner sees only the outcome of its own chosen action; pairing does not expose unchosen rewards. The current runner handles one validation episode per family/seed. Its independent A/B probe stream extends component 3 with `[32, current_trial, round(sigma*1000)]`; a future multi-episode runner must document episode-specific derivation before development begins.

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

Every future completed block writes an atomic checkpoint containing configuration, graph hash, seed derivation, current episode/trial, weights/state, RNG states, elapsed resource counters, and output schema version. Verify resumed versus uninterrupted validation runs before a long job. Save per-trial scalar metrics, not all neural states by default; retain full-state diagnostic traces only for validation seeds 0–4. Cap each pilot campaign at 10 GB initially. Stop scheduling new blocks when free target-disk space would fall below 20 GB; preserve checkpoint and request a revised storage plan. These are future implementation requirements, not an installed runner.

## Target-machine gate

The user reports a colleague's 64 GB PC with RTX 5090 32 GB and Ryzen 7 9800X3D. The user corrected the memory type to DDR5; free storage and OS/Python/driver versions remain unverified. [Hardware provenance](research/target_hardware.json) records that correction. The current session is not the verified target. **The user skipped the separate measured workstation pilot for EXP-002 (D016).** No target benchmark is required for this bounded validation milestone, and no timings are promoted to commitments. Future scientific runs still record their actual environment and resource counters. All three candidates have CPU-first designs. If a future run exceeds 16 GB memory or projects above seven days, first stream matrices/reduce parallelism and inspect the algorithm. Any scientific reduction in seeds, tasks or controls requires a recorded protocol revision **before** confirmation. Paid compute requires a measured limitation and explicit benefit/cost proposal.
