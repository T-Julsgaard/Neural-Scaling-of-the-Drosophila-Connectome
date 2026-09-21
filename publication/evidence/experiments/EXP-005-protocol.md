# EXP-005: bounded N73 activity mechanism

Prospective version 1.0, 2026-09-13. Freeze source and this protocol before development. Evaluation settings must be selected and hashed before evaluation inputs are generated. No extensions based on results. Existing EXP-002/003/004 artifacts and source remain untouched.

## Questions and conditions

Use audited 40x73 projection, full 73-feature delta readout (146 nonnegative weights), initial weights .1, historical chosen-action reward assay and 384-trial reset episodes. K is exact. Activity a is constant per winner. Historical K4 has a=2.5, eta=.01, T=.1; K6 has a=10/6, eta=.01, T=.1.

Four core conditions: historical K4/K6, K4 eta=.01*2/3, K6 eta=.015. The latter two match nominal same-cue sensitivity 2 eta K a² at 1/3 and 1/2 respectively. Add K4 a=10/6 and K6 a=2.5 at eta=.01; add K4 a=sqrt((100/6)/4) and K6 a=sqrt(25/6) at eta=.01 (norm matches). All main conditions retain initial .1 weights; clipping is measured, not assumed negligible. Frozen controls at each K.

Equal tuning: each K at total activity 10 gets eta={.01/3,.02/3,.01,.015} x T={.1,.2}, eight candidates. Select highest mean of acquisition, early reversal, post-interference retention and late intervening-cue learning on six development blocks. Ties within 1e-6 choose smaller eta then larger T. Evaluate only selected candidates plus the eight fixed conditions and two frozen controls. No evaluation reselection.

## Streams, sample and inference

Fresh PCG64 SeedSequence root 6, stage 0 validation, 1 development (blocks 100..105), 2 evaluation (1000..1031); otherwise historical exogenous task construction. Twenty episodes/block, ten reversal and ten interference. Blocks, not episodes or configurations, are independent units. Paired comparisons use identical observations, potential rewards, choice uniforms and tie priorities. Weights reset per episode; this is not cumulative memory capacity.

Four primary post-interference retention contrasts: historical K6-K4, slow-update-matched K6-K4, fast-update-matched K6-K4, tuned K6-K4. Use 20,000 paired block-bootstrap draws, simultaneous-family Bonferroni coverage 98.75% each. ±3 percentage points practical equivalence band. N=32 gives approximate half-width 2.65 pp at assumed paired SD .06 and z=2.498; SD .10 gives 4.42 pp. These are planning assumptions, not a power guarantee. No automatic additional sampling if inconclusive.

Report secondary 95% intervals for acquisition (last 32 of first phase), early reversal (first 32 of second phase), new learning (first and last 32 of interference phase), old-cue probes before/after interference, retention change, and final noise .3. Tuned practical recoverability requires the tuned retention interval inside ±3 pp AND the secondary acquisition, reversal, new-learning and noise intervals inside ±3 pp; otherwise state which part is unresolved. Secondary intervals do not supply a familywise superiority claim. Do not infer absence from nonsignificance.

## Mechanism instrumentation and validation

Save trial-level preferred probabilities, selected-cue q changes, predicted unclipped q changes, change on unchosen cue and old prototype cues, weight update norms, clipping occurrence, actual/predicted update coefficient, and final weights. Save independent noisy old/new probes at phase boundaries and .3 final probes. Geometry: same-cue cosine repeatability (successive independent noise samples), across-cue and old/new cosine overlap, never-used fraction and per-cell presentation counts. Geometry is descriptive, not causal mediation evidence.

Validation before freeze: compare historical K4 engine with existing BatchEpisode, scalar clipped recurrence with batched engine, encoding winner/norm identities, stream independence, frozen chance, exact scaled-amplitude replay with inverse-scaled initial weights and eta/a² (including clipping), interrupted-block resumption and corruption rejection. Fixed-action replay uses alternating choices and exogenous rewards, independent of learned choices; compare all eight fixed conditions on one validation interference episode. Replay is explanatory, not evaluation evidence.

## Resources, audit and endpoint

CPU only, up to three local processes, 2 GiB artifacts, minimum 5 GiB free, two-hour stage cap. Record Python/NumPy/environment, wall/CPU and worker peak memory. Save complete blocks atomically as checkpoints; resumption validates contract and raw hashes. On numerical failure stop and retain evidence; no exclusions. Audit all raw files, recompute block metrics and analysis, regenerate task hashes and replay one full evaluation block deterministically. Preserve protocol/code snapshots. Run relevant existing and new tests.

Finish this mechanism milestone even with a narrow negative or unresolved result. Next priority is persistent memory load x cue similarity with native K4/K6, direct-input and same-N randomized sparse baselines. More growth requires a diagnosed capacity limitation; homeostasis follows the benchmark.
