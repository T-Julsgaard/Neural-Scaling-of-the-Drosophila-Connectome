# EXP-003 confirmation protocol 1.0

2026-09-12. The user explicitly authorized freezing and running the untouched confirmation campaign with all controls. This supersedes the development addendum's earlier execution-only restriction. Hypotheses, margins and sample budget remain those of EXP-003 and BENCHMARK_SPEC.

## Frozen design

Use generic delta, eta=0.01, temperature=0.1, exactly as selected by the audited ten-block development stage. No configuration search or confirmation-driven selection. Run all 20 independent task blocks 1000–1019, three nested graph replicates 0–2, all sizes 73,80,91,110,146, and all clone/structured/uniform/degree-null arms. Retain the exploratory whole-uniform arm at every size. Evaluate the native main N73 baseline once per block and reuse it.

Preserve all 80 unique representation conditions per block from development: 49 main, 15 whole-uniform, 9 fixed-four at N110 (clone/structured/null), and 7 bottleneck (native N73 once; structured/null N110). Fixed-four N73 reuses the identical full native baseline. The bottleneck has 32 features and 64 trainable weights at both sizes. Include the frozen eta=0,T=.2 native control beside the selected configuration. Total: 1,600 conditions, 32,000 reset episodes, 32,400 configuration-episodes. Every episode has 384 trials, ten reversal and ten interference episodes per condition. No exclusions or optional stopping based on results.

## Streams and immutable implementation

Use the exact development stream namespace `SeedSequence([3,stage,block,domain,replicate,size,component,*suffix])` with **stage=2**, blocks 1000–1019. All domains, components, suffixes, pairing, graph construction, winner ties, float64 encoding, schedules, metrics, probes and weight resets remain as specified in the development protocol. The separate confirmation adapters are a source-identical copy except for stage bounds, the singleton configuration and removal of development selection. Tests use only stage 0 blocks 0–4; never generate reserved confirmation inputs before contract freeze. The development runner remains unable to generate confirmation inputs.

Freeze protocol, executable and test hashes, analysis code, input provenance, environment, validation evidence, development audit/contract/selection digests and the complete condition design before starting. Verify the audited development artifacts before validation. Resume must reject changed code, settings, environment, source, graphs, checkpoints or saved artifacts. Retain failed attempts. If a scientific bug invalidates confirmation, preserve it and prospectively revise the protocol and seed range rather than reusing exposed blocks.

## Inference and decisions

Average episodes within task family, then three graph replicates within each block. The unit of uncertainty is the **20 task blocks**, not episodes, graphs, cells or animals. Use 10,000 paired percentile block-bootstrap resamples from stage 2, block 1000, domain 2, component 7. Reuse the same resampling indices across contrasts. Primary: structured minus degree-null early reversal at N110, full readout, proportional sparsity; two-sided **98.33%** interval (tail probabilities .00835 and .99165) and practical minimum +.05. Lower bound above +.05 supports the planned advantage; upper bound below +.05 is evidence against a practically useful advantage in this assay; otherwise inconclusive. Do not relabel another contrast primary.

All other profiles/contrasts have 95% intervals and are secondary exploratory analyses, including scale changes N110/N146 versus each arm's N73, structured-minus-null under both controls, and the control scale changes. Report acquisition with the predeclared −.02 noninferiority margin (lower 95% bound above −.02), early reversal, return adaptation, pre/post-interference retention, robustness at noise 0,.1,.3, learning curves, cell/readout ranks, unused fractions, duplicate columns, dimensions and measured costs. Preserve all 20 block values for scalar estimates and paired changes. Native baseline reuse never increases sample size.

Prefer structured growth only if the primary practical criterion passes and controls support the interpretation. Deprioritize this wiring prior if the primary upper bound is below +.05. A useful scale effect across reversal and retention/robustness without major acquisition loss can motivate prospective adult/cross-dataset validation regardless of organization results; explicitly state dependence on sparsity/readout and keep scale secondary. No universal power law, cognition, evolutionary-search or biological replication claim follows.

## Execution, resource limits and audit

Use at most three CPU workers and the frozen development episode/checkpoint algorithm. Stop on numerical, graph invariant or null mixing failure; below 20 GiB free disk; 10 GiB retained campaign artifacts; or seven active days. Record failures and preserve resumable state. No paid compute. Estimate runtime/storage from development per-condition resource counters at N73 and N146, then record actual current-session wall/CPU time, maximum individual worker peak memory (not total concurrent RAM), retained bytes and environment. The colleague's workstation and energy use remain unmeasured.

Preflight: `python tools/validate_growth_confirmation.py`. Freeze/run/resume: `python tools/run_growth_confirmation.py --workers 3`. Audit: `python tools/audit_growth_confirmation.py`, verifying complete condition identities, deterministic graph regeneration, input pairing, episode hashes, frozen control traces and all recomputed metrics. Report: `python tools/report_growth_confirmation.py`; publish conclusions only after the complete audit. Do not inspect partial outcomes to change this plan.
