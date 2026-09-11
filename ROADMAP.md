# Evidence-gated roadmap

Updated 2026-09-11. Phases are milestones, not a guaranteed calendar or a fixed order of scientific hypotheses. Negative results can complete a milestone successfully.

| Milestone | Deliverable and entry condition | Continue / revise / stop |
|---|---|---|
| M0 Research foundation | This dated synthesis, source/data audits, branch portfolio, three specifications, continuity records | **Core deliverables complete with explicit unresolved fields.** No experiment run. Reopen research if a gap changes selection or a new claim |
| M1 Selected reproduction and discriminating pilot | Select EXP-002 (recommended) or EXP-001; record actual workstation; provision isolated environment; pass R02 or R01; measure a validation block | Continue when equations/data/task checks pass and assay avoids floor/ceiling. Revise if source assumptions or task validity fail. Stop interpretation if reproduction/validation is unresolved |
| M2 Reusable experimental pipeline | Extract only proven common needs from M1: loading, dynamics, interventions, task adapters, evaluation, checkpoint/resume and bounded outputs | Continue when resumed runs match uninterrupted validation and a frozen confirmation run is reconstructable. Avoid body/plugin/general-framework work without a concrete task |
| M3 Justified expansion | Execute another independent approach and EXP-003 if its learning dependency passes; keep resources and confirmation outcomes separate | Continue growth if a useful capability effect survives controls. If biological prior loses, preserve any scale result and use simpler architectures. If precise null effects persist, stop that branch |
| M4 Adult/cross-dataset validation | Choose adult circuit and independent specimen/type mapping based on discovered effect; verify export/license/hash; use new tasks/seeds | Continue if effect survives circuit/animal/task change. Otherwise narrow claims to the original assay; do not relabel failed transfer as universal success |
| M5 Larger or embodied investigations | A specific question requiring whole-brain, module coupling, developmental search or body simulation; measured local bottleneck if compute changes | Compare matched controllers/search budgets and biological observations. Paid/HPC proposal only after local measurement and expected benefit/cost. Stop if complexity adds no decision value |

## Immediate handoff

Implement R02 and the EXP-002 validation fixtures first if the recommended branch is selected. Target1–2 days to inspect/install/validate an isolated small path, then reassess; this is an effort estimate, not a promise of successful reproduction. The full EXP-002 specification estimates3–5 implementation days. Preserve the distinction between a passed analytic adaptation check and an author-code reproduction.

Only after validation should a development sweep choose hyperparameters. Freeze the protocol and then run confirmation. Budget revisions must precede confirmation, with a rationale and updated seed ranges if an earlier confirmation was invalidated. EXP-001 is independent and can be pursued next or first; EXP-003 must reuse a validated assay, not merely copied code.

## Larger-scale stopping criteria

Stop or redesign a branch when a practical-effect upper interval remains below its threshold across justified controls, observed gains are entirely attributable to an unwanted resource/adapter change, transfer repeatedly fails, or measured cost makes the next experiment less informative than an alternative. An inconclusive interval warrants a prospective information/power and cost calculation, not automatic larger runs.

Before any long run, record target hardware/environment, peak memory, extrapolated wall time, storage growth, checkpoint interval, resumption test, and a stop condition. Local/free resources remain the default. GPU acceleration is optional and must be justified by measured throughput rather than the description “top-end.”
