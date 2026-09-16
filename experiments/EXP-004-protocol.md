# EXP-004 active-count versus population protocol 1.1

2026-09-12. Prospective follow-up authorized by the user's request to continue the EXP-003 active-count/population milestone. EXP-003 code, protocols, evaluation blocks and conclusions remain immutable.

## Question and factorial design

Cross population N in {73,110} with exact winner count K in {4,6}, and readout in {full,32-feature bottleneck}. At N110 use structured and matched degree-null growth, three nested graph replicates each. At N73 evaluate the native graph once per K/readout and share that baseline across arms. This gives 28 unique conditions per task block. Reuse each graph, tie priority and episode input across K/readout interventions. This directly fills the missing N73/K6 and N110/K4/bottleneck cells.

Keep the audited generic delta learner, eta=.01, temperature=.1, total KC activity 10, output initialization .1, 384 trials, ten reversal and ten interference reset episodes per condition, existing probes and task-family definitions. Full readout has 2N learned weights; bottleneck has 64 at either size. Use the existing deterministic 32-bin projection and normalize its output to total activity 10. Exact K is measured before this projection. Report total activity and realized winner count validation. Increasing K also decreases activity per winner (10/K); conclusions concern this normalized encoder intervention, not an isolated physiological effect of cell count or a fixed effective learning rate. Population changes also alter winner competition and the bottleneck mapping.

## Fresh streams and stages

Use a new SeedSequence root 5, with [5,stage,block,domain,replicate,size,component,*suffix]. Validation stage 0 blocks 0â€“4; development stage 1 blocks 100â€“103; evaluation stage 2 blocks 1000â€“1031. Reusing numerical block labels under root 5 does not reuse EXP-003's root-3 streams. No evaluation generation before validated code and the evaluation contract are frozen. Development is a four-block engineering/resource check, with no hyperparameter selection or sample-size adaptation. Audit all development artifacts before evaluation freeze. Numerical or scientific failures stop the run; preserve failures and use a new protocol/namespace if exposed evaluation is invalidated.

## Primary inference

Post-interference retention is primary. In the structured-growth, fixed-readout factorial, let a=Y(73,4), b=Y(73,6), c=Y(110,4), d=Y(110,6). Prespecify three contrasts: active-count main effect ((b-a)+(d-c))/2; population main effect ((c-a)+(d-b))/2; interaction (d-c)-(b-a). Positive interaction means the benefit of increasing K is larger at N110. All three receive two-sided 98.333333% paired percentile block-bootstrap intervals (Bonferroni nominal family coverage 95%; bootstrap approximation is not exact familywise control). Use 10,000 shared resamples from root 5/stage 2/block 1000/domain 2/component 7. Average episodes within family and graph replicates within block; only the 32 independent task blocks enter uncertainty. One fixed anatomical source is not 32 biological replicates.

For each primary contrast, an interval wholly above/below zero supports the corresponding direction; an interval wholly within [-.03,+.03] supports a small effect within this prospective practical band; otherwise practical size is unresolved. Report directional and practical-band conclusions separately. Lack of significance never establishes absence. An active-count effect alone cannot establish that population is irrelevant; inspect interaction and fixed-K simple effects.

All fixed-N K changes, fixed-K N changes, original diagonal (110,6)-(73,4), full-readout and degree-null factorials, and structured-minus-null N110 contrasts are secondary exploratory 95% intervals. Report acquisition (lower interval >-.02 as secondary noninferiority), early reversal, return adaptation, retention before/after interference, all robustness probes, learning curves, participation/rank diagnostics and resource dimensions. Do not promote a favorable secondary result. No broad adaptation, adult transfer, biological superiority or unique wiring claim follows.

## Precision and resource budget

Choose 32 evaluation blocks prospectively, before fresh development data. For an assumed paired block SD .07, normal planning z=2.394 yields half-width .0296 for each primary interval; with SD .04/.10 the corresponding widths are .0169/.0423. Approximate 80% power requires an effect about (2.394+.842)*.07/sqrt(32)=.0400. This is a precision-oriented diagnostic, not a guarantee of detecting a 3-point effect or resolving interaction. The .07 is an explicit planning assumption, not a measured variance of the previously unobserved factorial contrasts. Record historical EXP-003 paired SDs as context; do not substitute those old observations into new inference. Report achieved widths even if wider than targeted. No optional stopping or post-evaluation sample expansion.

Four development blocks: 112 conditions/2,240 episodes. Thirty-two evaluation blocks: 896 conditions/17,920 episodes. Two extra frozen learners per block (native K4/K6 full readout) add 40 configuration-episodes per block. EXP-003's measured 2,149.5 s/32,000 episodes gives an evaluation wall proxy about 1,204 s plus graph/I/O overhead and audit; retained-byte proxy about 375 MiB. This is current-session CPU planning, not the colleague's machine or an energy measurement. Record fresh development resource measurements before evaluation.

At most 3 CPU workers, no paid compute, at least 20 GiB free disk, 10 GiB retained per stage, seven active days per invocation/block. Atomic episode checkpoints; resume checks contract, all scientific code/test/analysis/protocol hashes, source, environment, task identities, graphs and saved artifacts. Record interrupted invocations and exceptions. Raw NPZ stays local, with a complete hash manifest. Regenerate graphs/tasks, verify every raw hash, recompute summaries and analysis, and check frozen controls at chance before publishing conclusions. Preserve all prior work.

## Execution

`tools/run_activity_diagnostic.py` provides validate, development, audit-development, evaluation and audit-evaluation commands. Validation exercises only stage-zero inputs and includes scalar encoder checks, legacy compatibility at corresponding K, crossed pairing, explicit stream isolation, factorial algebra, frozen-control recovery and corruption rejection. Freeze development only after validation; freeze evaluation only after development audit. No interpretation from partial evaluation outcomes.

## Infrastructure revision before evaluation

Protocol 1.0 development stopped when a concurrent artifact scan observed a temporary file just before another worker atomically renamed it. Preserve that attempt, its frozen source, validation and failure in `results/exp004_development_v1_failed/`. No evaluation inputs were generated. Version 1.1 tolerates only FileNotFoundError during storage scans (other errors still stop); a regression test exercises the race. Repeat validation and all four development blocks using new root 5, then freeze evaluation. Scientific settings, sample budget and contrast definitions are unchanged. No failed-run outcomes enter inference.
