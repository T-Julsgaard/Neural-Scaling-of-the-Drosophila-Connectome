# Experiment registry

Updated 2026-09-11. **Zero scientific hypothesis experiments completed.** EXP-002 bounded implementation checks ran and passed; they do not establish H2 or assay adequacy. Static data/schema and source audits are recorded separately. Proposed IDs are stable; never recycle an ID for a different hypothesis.

| ID | Specification | Status | Dependencies | Primary contrast / next action |
|---|---|---|---|---|
| EXP-001 | [Wiring, capacity and normalization](experiments/EXP-001.md) | proposed / specified | R01; target resource measurement | Native minus signed-degree null; validate graph parser and recurrence |
| EXP-002 | [Fixed-wiring adaptive headroom](experiments/EXP-002.md) | validation / automated checks passed | R02 independent review or author-runtime comparison; measured pilot skipped by user | Feedback minus reward-only remains untested; [validation evidence](experiments/EXP-002-validation.md) and next gate |
| EXP-003 | [Structured population growth](experiments/EXP-003.md) | proposed / specified | R03 and validated EXP-002 assay | Structured minus degree-matched added-edge null at N=110; validate growth invariants |

Common authoritative rules: [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md). Rankings: [RESEARCH_BRANCHES.md](RESEARCH_BRANCHES.md). Machine-readable handoff summaries: [experiment_manifest.json](research/experiment_manifest.json). Markdown specifications govern scientific detail; JSON summaries are for indexing and consistency checks, not an executable platform configuration.

## Future run record

Create `research/runs/<run_id>.json` plus a brief interpretation linked here. Required fields: experiment/protocol version, status, start/end timestamp, code commit, source hashes and versions, environment lock and hardware ID, configuration hash, complete seed derivation, planned versus completed blocks, checkpoint paths/hashes, metrics and uncertainty, compute/storage counters, validation status, exclusions/failures, interpretation, limitations, and follow-up decision. Keep results under ignored `results/`; commit compact summaries and manifests. Never mark a planned run completed because a script exists.

Statuses: proposed → implementing → validation → running → completed; alternatives blocked, invalidated, abandoned. An invalidated run retains its configuration and reason. Scientific null results remain completed; infrastructure failure is not evidence against a hypothesis.
