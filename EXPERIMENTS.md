# Experiment registry

## Session D review complete — 2026-09-16

D is an assessment/writing milestone, not EXP-012. A/B/C completed evidence is retained; C's frozen prediction is supported with the limitations in the [D assessment](research/SESSION_D_ASSESSMENT.md). Deliverable: [narrow empirical report](research/EMPIRICAL_REPORT_DRAFT.md) and [figure plan](research/SESSION_D_FIGURE_PLAN.md). No new experiments or reruns. The next step is optional figure/artifact preparation and outside scientific review, not a campaign; older pending-session instructions below are historical.

## Current Session C status — 2026-09-15

The prospective prediction is supported: useful nonlinear distinctions remain readable from frozen sparse representations while the tuned sequential readout loses previously learned associations. Native/calibrated offline old-context accuracy 95.67 [92.91, 98.44]%; tuned sequential accuracy 51.73 [41.24, 62.21]%; paired gap 43.95 [34.23, 53.67] pp; acquisition-to-final loss 45.86 [35.78, 55.93] pp (95% intervals, 24 fresh blocks). [EXP-011 report](experiments/EXP-011-results.md). C is complete; D has not started. Current user authorization supersedes the historical C deferral below. Next action only when requested: D per [handoff](research/SESSION_D_HANDOFF.md). No publication.

## EXP-010 / Session B — complete, 2026-09-15

Offline full-outcome old-pair accuracy 96.97% versus fully supervised online 76.72%; paired difference 20.26 pp [16.46, 24.05] (95%, 24 fresh task blocks, native/calibrated average). Frozen-feature information remains linearly recoverable despite sequential readout forgetting in this fixed larval assay. Offline is an explanatory diagnostic with different fitting/history access, not an equal-budget competitor or capacity bound. Five validation tests; six development tasks; all 31 validation/development/confirmation blocks replayed. B gate passed; C is explicitly deferred by the user. [EXP-010 report](experiments/EXP-010-results.md).

## EXP-009 / Session A — complete, 2026-09-15

[Protocol](experiments/EXP-009-protocol.md) and [report](experiments/EXP-009-results.md): seven validation tests, author-runtime comparison, four development and 24 confirmation blocks, all archives replayed. Compensation improves correct-valence choice probability by 8.58 pp [8.13, 9.03] (95% paired task-block interval). Gate passed; author-parameter adaptation, not exact published reproduction. Next: [Session B](research/SESSION_B_HANDOFF.md).
Updated 2026-09-14. **Seven scientific experiments completed: EXP-002 baseline, EXP-003 confirmation, EXP-004 activity/population diagnostic, EXP-005 mechanism controls, EXP-006 persistent memory, EXP-007 homeostasis and EXP-008 adult transfer.** EXP-005 supports a K6 retention benefit after matched updates and equal tuning. EXP-006 passes nine preflight tests and audits of six development/32 confirmation blocks; [results](experiments/EXP-006-results.md). EXP-004 supports a normalized active-count retention benefit and a fixed-readout population penalty. Proposed IDs remain stable; never recycle an ID.

| ID | Specification | Status | Dependencies | Primary contrast / next action |
|---|---|---|---|---|
| EXP-008 | [Adult circuit transfer](experiments/EXP-008-protocol.md) | completed / audited | Nine preflight tests; eight development and 24 confirmation blocks | Adult calibration minus ordinary tuning: -0.19 [-1.01, 0.68] pp (98.333333% interval). Transfer classification: equivalent; informative-benchmark gate passed. [EXP-008 results](experiments/EXP-008-results.md) |
| EXP-001 | [Wiring, capacity and normalization](experiments/EXP-001.md) | proposed / specified | R01; target resource measurement | Native minus signed-degree null; validate graph parser and recurrence |
| EXP-002 | [Fixed-wiring adaptive headroom](experiments/EXP-002.md) | completed / measured baseline | R02 PASS by author runtime; 21 tests PASS; colleague pilot skipped | Feedback minus reward-only early reversal +0.7207, 98.33% interval [0.6819,0.7593]; [results and tradeoffs](experiments/EXP-002-baseline-results.md) |
| EXP-003 | [Structured population growth](experiments/EXP-003.md) | completed / audited confirmation | R03; 40 preflight tests; ten development and twenty confirmation blocks | Primary structured-minus-null reversal -0.009 [-0.023,+0.007], 98.33%; planned +.05 advantage rejected. Conditional retention prompted the now-completed EXP-004 diagnostic. [Results](experiments/EXP-003-confirmation-results.md) |
| EXP-004 | [Active count versus population](experiments/EXP-004.md) | completed / audited evaluation | 47 tests; four audited development and 32 evaluation blocks; root 5 | Fixed-readout retention: active count +5.37 pp [3.89,6.97]; population -5.03 pp [-7.27,-2.86], primary 98.333333%. Next N73 normalization/update-size diagnostic. [Results](experiments/EXP-004-results.md) |
| EXP-005 | [Activity mechanism at N73](experiments/EXP-005.md) | completed / audited | 21 preflight tests; six development and 32 evaluation blocks; root 6 | Tuned K6-K4 retention +3.78 pp [2.39,5.27], primary 98.75%. [Results](experiments/EXP-005-results.md) |
| EXP-006 | [Persistent-memory load and similarity](experiments/EXP-006-protocol.md) | completed / audited | Nine preflight tests; six development and 32 confirmation blocks | K6-K4 hard retention +7.60 pp [4.68,10.43], primary 98.75%; average criterion through 8 pairs for K6, 16 for direct input. [Results](experiments/EXP-006-results.md) |
| EXP-007 | [Participation homeostasis](experiments/EXP-007-protocol.md) | completed / audited | Ten preflight tests; eight development and 32 confirmation blocks; matched-sham addendum | Homeostasis and ordinary tuning are practically equivalent within the prespecified ±3-point retention band in the primary condition. Calibrated K6 retains 79.28% versus 79.55% for ordinary tuning; difference -0.27 [-1.67, 1.13] pp (98.333333%). [EXP-007 results](experiments/EXP-007-results.md) |

Common authoritative rules: [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md). Rankings: [RESEARCH_BRANCHES.md](RESEARCH_BRANCHES.md). Machine-readable handoff summaries: [experiment_manifest.json](research/experiment_manifest.json). Markdown specifications govern scientific detail; JSON summaries are for indexing and consistency checks, not an executable platform configuration.

## Completed and future run records

[EXP-004-evaluation-v1.1](research/runs/EXP-004-evaluation.json) records 32 audited blocks and 17,920 episodes. [Development](research/runs/EXP-004-development.json) records four audited blocks and 2,240 episodes. Infrastructure failures/restarts are preserved in the [recovery record](research/exp004_execution_recovery.json) and report; no episodes were excluded.

[EXP-003-confirmation-v1.0](research/runs/EXP-003-confirmation.json) records twenty complete blocks, 32,000 episodes, unchanged selected settings and the full audit.

[EXP-002-baseline-v1.1](research/runs/EXP-002-baseline.json) contains both completed stages. [EXP-003-development-v1.0](research/runs/EXP-003-development.json) records ten audited development blocks, 800 representation conditions and 16,000 episode batches. Raw NPZ files remain local and Git-ignored, with hashes in their run records. EXP-003 confirmation is complete; evolutionary search has not run.

Create `research/runs/<run_id>.json` plus a brief interpretation linked here. Required fields: experiment/protocol version, status, start/end timestamp, code commit, source hashes and versions, environment lock and hardware ID, configuration hash, complete seed derivation, planned versus completed blocks, checkpoint paths/hashes, metrics and uncertainty, compute/storage counters, validation status, exclusions/failures, interpretation, limitations, and follow-up decision. D020 includes the existing bounded `results/validation/` artifacts in the private repository; future large campaign results remain ignored, with compact summaries and manifests committed. Never mark a planned run completed because a script exists.

Statuses: proposed → implementing → validation → running → completed; alternatives blocked, invalidated, abandoned. An invalidated run retains its configuration and reason. Scientific null results remain completed; infrastructure failure is not evidence against a hypothesis.
