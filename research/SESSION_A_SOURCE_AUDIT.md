# Session A source and equation audit

2026-09-15. See [frozen EXP-009 protocol](../experiments/EXP-009-protocol.md), [numeric source audit](exp009_source_audit.json) and [pinned source bundle](sources/exp009/author/README.md). This audit distinguishes published values, supplied author parameters, validated arithmetic and newly measured adaptation results.

## Selected published result

Abdelrahman, Vasilaki and Lin, *Compensatory variability in network parameters enhances memory performance in the Drosophila mushroom body*, PNAS 118, e2102158118 (2021), [DOI](https://doi.org/10.1073/pnas.2102158118). Published PDF obtained from [White Rose](https://eprints.whiterose.ac.uk/id/eprint/181348/1/Abdelrahman%20Lin%20Proceedings%20of%20the%20National%20Academy%20of%20Sciences%202021.pdf). Supplement and Dataset S1 obtained through [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8670477/supplementaryFiles), after direct PNAS access returned a challenge. Figure 4 and its complete caption were rendered and visually inspected locally; SI computational methods and the corresponding author source were read.

Figure **4B2**, c=1: red random model versus magenta threshold-compensated model (mechanism schematic 4A4). Dataset S1 `Fig 4!I3:I22` and `M3:M22` contain twenty paired model values. Means are **53.3492%** and **63.3565%**, a published paired mean difference of **+10.0073 percentage points**. These are extracted author results, not reproduced observations. The panel caption reports 20 random-connectivity instances and corrected paired statistical comparisons. It does not identify the supplied MAT file as any particular spreadsheet row; no such mapping is asserted.

Author repository: [aclinlab/CompensatoryVariability](https://github.com/aclinlab/CompensatoryVariability/tree/9f3f7e9e85117febef1ad32e3152c830570f74d3), pinned commit **9f3f7e9e85117febef1ad32e3152c830570f74d3**. README maps `Compens_variab_rescue_Perf` to Figure 4, despite that script's stale header referring to Figure 5. Original GPL-3.0 license is retained. The paper is CC BY. Bundled source bytes and SHA256 are preserved, with derived numeric arrays in `parameters.npz`. The author data's repository context is retained; no separate upstream-data license is inferred from the paper license.

## Equation and implementation mapping

Line numbers refer to the pinned `Compens_variab_rescue_Perf/compensatoryVar_rescuePerf.m`, unless another file is named.

| Component | Published specification / author implementation | EXP-009 implementation and status |
|---|---|---|
| PN distribution | SI Eq.1 describes ORN-to-PN transformation. First 110 rows of supplied `hallem_olsen` are already PN rates; script lines 31,38-90 uses them and reconstructs the stored synthetic odors | Resample each of 24 PN marginals independently from those 110 rows, as described in SI methods. Do not apply Eq.1 again. New independent prototypes; original script's reused histogram-based prototype set is not regenerated exactly |
| PN scale | Lines 38-90 recover an affine factor from MATLAB histogram maxima and supplied clean first trials; lines 226 rescales all original PN trials to [0,5] | Octave executes the source recovery arithmetic with a 30-iteration safety cap. Fixed recovered slope 0.031805... and negligible intercept are applied to fresh inputs; no evaluation-fitted rescaling |
| Noise | SI Eq.2 describes Gaussian variability; source lines 214-225 uses `getPNStdevBhandawat`, additive SD from nearest mean-rate bin and clips negative raw rates | Same 16-bin lookup and Gaussian rule; all 15 training trials are noisy rather than retaining one clean first trial. Independently held-out 15 noisy probes |
| Random projection | SI methods: 2,000 KCs, rounded/clipped Normal(6,1.7) claws in [2,11], sample 24 PNs with replacement, sum duplicates; lognormal weights mu=-.0507, sigma=.3527, thresholds CV=5.6/21.5. Lines 122-180 | Use original saved projection and thresholds; these distribution parameters document provenance, not newly sampled anatomy. Exactly the same nonzero connectivity in both arms |
| Response | SI Eq.3: rectified excitation minus pseudo-feedforward APL inhibition minus scaled threshold. Lines 1382-1389; saved theta arrays already include global Ctheta | `exp009.compensation.encode`; vectorized float64. Compared to Octave source arithmetic on supplied inputs. No top-K or fixed total activity |
| Global sparsity fitting | SI Eqs.5-19: adjust threshold scale and APL gain to target CL=.2 without inhibition and .1 with inhibition | Use saved `thetaS`, `APLgains(1)` and saved compensated parameters. No new fit; optimizer convergence trajectory not validated |
| Threshold compensation | SI Eqs.60-65; Eq.65 is delta theta_j = eta*Ctheta*(mean activity_j - A0), including silent KCs. Script lines 1065-1201, target .51 +/-6%, simultaneous coding constraints | Use supplied `theta_Activity_homeo`, `thisW_Kennedy`, `APLgains(5)`. Audit achieved calibration target on original first 15 trials. Does not reproduce the optimization |
| Output learning | SI Eq.20, source lines 1556-1687: multiplicative depression of wrong-valence output, normalized eta by mean training activity; source initializes uniform random readout weights | `learn` sums training sufficient statistics and applies the mathematically equivalent product of exponentials. Scalar trial-by-trial and Octave per-odor implementations agree. Full labels, both valences learned, no chosen-action gate or error-dependent update |
| Feature scaling | Lines 1524-1533 rescales each arm's entire response tensor to [0,1] | Global maximum learned from training trials only. Output test responses can exceed 1. No minimum subtraction needed because responses include zeros. This is a declared adaptation |
| Decision | SI Eq.21; unmodified `testingModels_accuracies_function.m`, c=1 | `probabilities` uses stable sigmoid of signed output difference, averages probability of correct valence, no Bernoulli sampling. Octave comparison uses the untouched evaluator |
| Rate selection | Script lines 27,1477-1497 enumerate ten rates, two c values. A complete mapping of selected rates to Figure 4 spreadsheet values was not identified | Four new development blocks select one rate per arm from the identical ten-rate grid, c fixed at1, then settings and n frozen. Equal search opportunities; no claim to reproduce original figure optimization |

## Supplied model audit and unresolved discrepancy

The saved MAT file has **5 times** the uncompensated excitatory weights in `thisW_Kennedy` (max deviation from a constant factor is rounding precision). The current source at line1071 specifies **4.5 times**. This is a real mismatch between the distributed fitted artifact and current script. It was identified by the numeric parameter audit, not repaired. EXP-009 uses the saved artifact verbatim. Its result cannot validate regeneration from current source, or isolate a theta-only intervention. The first progress update mentioned 4.5 from source; this was corrected when the supplied values were checked.

Original calibration responses, computed without using new task outcomes:

| Measure | Uncompensated | Compensated |
|---|---:|---:|
| Fraction of active KCs, average over original calibration inputs | .109998 | .094217 |
| Coding level with inhibition removed | .200014 | .207007 |
| Mean activity across cells | .339373 | .515396 |
| SD of per-cell mean activity | .902917 | .001163 |
| Minimum / maximum per-cell mean activity | 0 / 10.908374 | .509241 / .519085 |
| Cells within .51 +/-6% | 1.65% | 100% |

The supplied compensated state achieves the mean-activity and coding tolerances. Its no-inhibition/inhibition coding ratio is about2.1971, close to the upper 2.2 tolerance. The baseline is close to the upper .11 coding tolerance. These bounds were reported, not tightened post hoc. The original labels exist in the MAT file but were not reused for new learning.

## Reproduction classification and failures

**Completed:** extraction of the published numerical contrast; inspection of methods/source; validation of Eq.3/20/21 arithmetic using supplied inputs and author evaluator; fresh held-out positive-control test conditional on one author-fitted model. **Not completed or claimed:** exact Figure 4 panel reproduction, independent regeneration of twenty models, validation of the joint homeostatic optimizer, equality to published means, biological replication, or causal isolation of thresholds from global gain/inhibition changes.

Source assets are available for more extensive work. The exact calibrated ensemble, full optimizer history, RNG seeds and figure rate-selection mapping are not in the inspected tree. This milestone chose a bounded supplied-parameter adaptation rather than inventing missing settings or making the complex uncapped multi-model script its runtime contract. No unfavorable experiment was discarded to find a positive sign.

Access failures were restricted shell sockets, a nonexistent `master` branch, PMC/PNAS web challenges, and a web screenshot cache miss. Resolved using authorized public downloads, pinned `main`, Europe PMC and a local PDF render. SciPy was absent; existing Octave handled MAT data. Octave emitted an exit-cleanup warning with status0; all fixture files were independently verified numerically. These are access/runtime observations, not failed scientific reproductions. Historical-results hashing is accounted for separately from experimental computation.
