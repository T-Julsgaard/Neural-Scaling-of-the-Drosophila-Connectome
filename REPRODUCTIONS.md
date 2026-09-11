# Reproduction and validation register

Updated 2026-09-11. **All scientific reproductions are NOT RUN.** Downloading source, reading methods and auditing a matrix are not reproductions.

| ID | Target | Exact artifact / procedure | Acceptance and limitation | State |
|---|---|---|---|---|
| R01 | EXP-001 implementation validation | Pinned flyvis graph constructor versus independent parser at extent1/no-fill; independent 4-node recurrence; delay/readout/null fixtures | Exact node/edge identity; float64 recurrence ≤10^-10; exact-delay R²>0.99; null invariants. Does not reproduce flyvis physiology or a published topology effect | NOT RUN; source inspected |
| R02 | Bennett eq8 mechanism | MATLAB `mb_mv_a.m` pinned in software audit; fixed provided activity/choice/outcome trace, 256 updates | Per-step q/d/weights ≤10^-10. If author runtime unavailable, independent analytic validation is labelled adaptation validation, not reproduction | NOT RUN; equations/source inspected |
| R03 | Growth construction and assay reuse | D05 subset; three growth replicates; N=73 identity; degree/count/lineage constraints; EXP-002 checks | Exact declared invariants and baseline trace equality; adequate null mixing. No published effect size is being reproduced | NOT RUN |
| R04 | Shiu publication baseline | Original v630 configuration at pinned source; paper's chosen stimulation/output validation | Select figure and quantitative acceptance tolerance from complete reproduction assets before implementation. v783 is a separate port | Deferred; source inspected; not a first-three dependency |
| R05 | Lappalainen physiological model | Published task-optimized model/ensemble and independent neural-response comparisons | Must use original parameters/task/data and figure-specific criteria. A generic tanh reservoir does not pass this reproduction | Deferred |
| R06 | Xie perturbation result | Paper subset and output mapping, author code at pinned commit | Resolve 18 modeled outputs versus19 unthresholded connected MBON columns and access/license before choosing a figure | Deferred; code tree not retrieved |
| R07 | Costi reservoir findings | ESA GitLab source linked by paper; original thresholds/tasks and hybrid controls | Audit actual input data semantics and normalization; choose original reported comparison before implementation | Deferred; methods excerpts inspected, runtime source unaudited |

## Failure attribution

If a target fails, first classify: source/data unavailable; environment/runtime incompatibility; implementation mismatch; underspecified method; numerical instability; insufficient statistics; or robust disagreement after faithful implementation. Only the last category can bear directly on the reported scientific result. Record evidence for the classification, repair attempts, unresolved alternatives and conditions for revisiting in [FAILED_PATHS.md](FAILED_PATHS.md).

A faithful original reproduction and a scientifically improved control experiment answer different questions. Preserve both configurations rather than silently changing an author's method and calling the result a failed reproduction.
