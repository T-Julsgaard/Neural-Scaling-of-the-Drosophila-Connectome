# EXP-003: controlled growth validation

2026-09-12. **R03 passed.** The four main growth operators and variable-size learning adapter are validated. Growth benefit and the structured-versus-null hypothesis remain untested: this work used validation seeds only, with zero development or confirmation blocks.

The [machine-readable record](../research/exp003_validation.json), [validation contract](EXP-003-validation-protocol.md), and [saved diagnostics](../results/validation/exp003/diagnostics.json) preserve the evidence. The existing EXP-002 code and baseline artifacts remain unchanged.

## What passed

All **29 tests** passed: 21 existing baseline tests plus eight new growth tests. Across **300 graph instances**, all five sizes (73,80,91,110,146), five validation blocks and three graph replicates satisfied the declared constraints. Clone, structured resampling, uniform resampling and the degree-matched null preserve every native column, shared donor choices, donor contact-count multisets and nonzero inputs. Nulls preserve added PN out-degree and KC in-degree and achieved their full target of ten successful swaps per added edge. A deliberately unmixable test graph correctly reports mixing failure.

The full no-growth traces, probes and final weights agree exactly with EXP-002 for all main arms and both task families. Grown full and bottleneck learners agree with the scalar update rule, probes do not change weights, and JSON checkpoint recovery agrees exactly at seven interruption points around learning-phase boundaries. Checkpoints reject a different graph. Tests independently calculate the fixed-four-active-cells and 32-feature readout controls. Explicit donor/partner/count records reconstruct the graphs without random sampling.

## Representation diagnostics

Measurements use **one validation task block**, all 20 episodes and three nested graph replicates. Each graph sees 15,360 cue presentations. N=73 is reused once. The 58 diagnostic configurations cover the full proportional-sparsity grid plus fixed-four controls at N=110. These describe representations under this task distribution; graph replicates are not three independent task blocks.

Mean over the three graph replicates; baseline is evaluated once. Proportional sparsity activates four cells at N=73, six at N=110, and seven at N=146.

| Cells | Growth rule | Added cells unused | Effective feature rank | Distinct added input columns |
|---|---|---:|---:|---:|
| 73 | Native baseline | n/a | 16.43 | 0.0 / 0 |
| 110 | clone | 40.5% | 16.33 | 0.0 / 37 |
| 110 | structured | 33.3% | 20.07 | 35.0 / 37 |
| 110 | uniform | 30.6% | 20.19 | 35.7 / 37 |
| 110 | degree null | 33.3% | 19.54 | 35.7 / 37 |
| 146 | clone | 41.6% | 15.58 | 0.0 / 73 |
| 146 | structured | 39.7% | 21.23 | 68.7 / 73 |
| 146 | uniform | 39.3% | 22.01 | 70.0 / 73 |
| 146 | degree null | 41.6% | 22.67 | 70.3 / 73 |

At N=110, fixed-four sparsity leaves 53.2% of clone, 52.3% of structured and 46.8% of null added cells unused; corresponding effective ranks are 16.01, 18.69 and 19.54. Under proportional sparsity, structured and null have equal mean added-cell participation, and uniform growth also adds diverse inputs. There is no basis here for preferring the biological prior.

The native baseline in this particular validation block has 45.2% unused cells. The earlier 38.8% was a mean across twenty different EXP-002 confirmation blocks; the two numbers describe different task samples. Null graphs retained 17.3%-37.9% of their original added-edge locations after shuffling, across the retained sizes/replicates.

Distinct inputs or activity patterns make a growth rule worth testing for learning benefit; they do not establish that benefit. Rank added relative to native activity is measured within the grown encoder: competition can change the native features too. Clones can produce distinct activity patterns through winner competition and tie ordering despite adding no distinct normalized input columns. Neither unused cells nor additional rank measures biological capacity.

## Scope and next step

Two complete learning smoke episodes per diagnostic configuration, plus 14 bottleneck episodes, remained finite. Their scores are retained for implementation auditing and are not capability estimates. Packed activity, graph counts, traces, probes, final weights and lineage are retained with hashes. The separate audit command recovers the activity and recomputes every diagnostic row.

The complete run, including the 29-test suite and diagnostic measurements, took **187.2 seconds** on the current-session CPU, with **133.9 MiB** peak process memory and **3.95 MiB** retained artifacts (61 files). These are measured validation costs, not a forecast for a tuned confirmation campaign or measurements of the colleague's workstation. The follow-up audit verified all file hashes and recomputed all 58 diagnostic rows from the saved activity.

Next: implement and freeze EXP-003's fresh development and recovery protocol, including experiment-specific input streams and the shared nine-setting eta/temperature selection across main arms and sizes. Carry forward generic delta from EXP-002 development. Keep fixed sparsity and the 32-feature readout controls; implement the specified exploratory whole-base uniform replacement before a campaign that includes it. Then measure reversal, retention, acquisition and robustness on development tasks, freeze the selected configuration, and use untouched confirmation blocks for growth claims. Do not select a preferred growth rule from these representation diagnostics alone. The bounded evolution branch remains available under the roadmap's M2/M3 review conditions.

Run `python tools/audit_growth.py` to audit retained evidence. Run `python tools/validate_foundation.py` for project-record integrity. Reproduction uses fresh destinations as specified in the validation contract; it does not overwrite this run.
