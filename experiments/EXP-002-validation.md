# EXP-002 learning-rule validation handoff

Updated 2026-09-12. **R02 passed by author-runtime comparison; the measured baseline is complete.** GNU Octave 11.3.0 executed the prepared supplied-input MATLAB fixture, and all 256 updates matched within 6.66e-16. See the [runtime record](../research/exp002_r02_runtime.json), [21-test validation](../research/exp002_baseline_validation.json) and [baseline results](EXP-002-baseline-results.md). The original 13-test evidence below documents the earlier bounded milestone; its report is preserved unchanged.

## Evidence

The [machine-readable report](../research/exp002_validation.json) records 13 passing tests, exact code/input hashes, CPython 3.12.14, NumPy 2.3.5, validation seeds and detailed outcomes. Validation ran in a project venv inheriting the installed bundled NumPy; a clean dependency installation and the colleague's target environment have not been tested.

| Check | Observed result | Interpretation limit |
|---|---|---|
| 256 supplied 20-KC/two-cue updates against a separate 50-digit Decimal oracle | Maximum absolute q/DAN/weight error 4.44e-16, below 1e-10; 115 positive-to-zero weight crossings | Python equation adaptation, not author-code execution |
| Feedback versus delta with rate matching | Exact agreement on 166 eligible trace steps at gamma=0.1, eta=0.001 versus 0.002; explicit off-regime counterexamples differ | Each comparison starts from the same pre-state; whole trajectories need not agree after off-regime updates |
| Feedback regime diagnostics | Both DAN drives positive in 217/256 fixture updates (84.77%) | Fixture-specific; must be measured anew in any scientific assay |
| D05 loader and encoder | Archive/CSV hashes, axis IDs, 40×73 shape, raw totals, normalized columns, four active KCs and coding sum 10 verified | Mature larval feature circuit, two synthetic outputs |
| Toy acquisition and reversal | Feedback and delta each exceed 0.9999 preferred probability after each phase | Forced balanced choices, two features, coding sum 1, eta=0.1; implementation sanity only |
| Shuffled-reward toy | Per-seed mean preference within 0.1 of chance and pooled mean within 0.05, for both learners | Five validation seeds, eta=0.01; bounded sanity check, not a statistical demonstration of no learning |
| Chronology | Pre-feedback probabilities, chosen-action-only update and unchosen-outcome counterfactual agree | No development/confirmation task exposure |
| Checkpoint and probes | 60 exact state/trace restore comparisons across both families and five seeds; probes leave weights, RNG and records unchanged | One-episode checkpoint, not the future resource-accounted block runner |
| Author harness preparation | Pinned DAN/eq8 source section preserved; original file unchanged; sentinel trial retains all 256 updates | Wrapper generated and inspected; no MATLAB/Octave execution |

The stored full Python equation trace is regenerated under versioned `results/validation/exp002_equation_trace.json`; its hash is in the report. The versioned [input fixture](../tests/fixtures/bennett_eq8_256.json) supplies both cues, initial weights, all choices and both outcome columns. It contains reversals and occasional outcome flips, bypassing language-specific RNG. It uses eta=0.01 to exercise clipping; the separate prescribed rate-matching fixture uses 0.001/0.002. No fixture setting is a selected EXP-002 hyperparameter.

## Run the bounded checks

From the repository root, with Python 3.12 available:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-validation.txt
.venv/Scripts/python.exe tools/fetch_validation_assets.py
.venv/Scripts/python.exe tools/validate_exp002.py
.venv/Scripts/python.exe tools/validate_foundation.py
```

The fetcher retrieves only the two public inputs in the existing asset audit and refuses hash mismatches. No source or dataset is silently updated. It uses the network only when a verified cached copy is absent. D020 includes the existing raw-source cache and generated author source in the private repository, preserving upstream attribution and license notices. `validate_exp002.py` rejects development/confirmation seeds through the episode API; it has no campaign or GPU option. The initial loader test caught the source CSV's newline convention; the parser now explicitly uses `newline=""`, as the original audit did. All tests were rerun after that repair.

## Author-code route, now executed

The pinned [Bennett source](https://github.com/BrainsOnBoard/paper_RPEs_in_drosophila_mb/blob/7ec52afb9bd7bb748d94d60dea9f483645a2ce8e/mb_mv_a.m) initializes random weights, chooses actions internally, and deliberately omits the last update. The [preparation tool](../tools/prepare_bennett_reference.py) preserves the DAN and eq8 statements while injecting supplied inputs, removing unused RNG seeding, renaming the function, and adding a 257th sentinel trial. Comparisons use pre-update values/DAN rates at trials 1–256 and weights at indices 2–257. Preparation hashes and the exact modifications are saved with the generated files. The source is GPL-3.0, attributed in the generated wrapper; the private snapshot includes the original source, modified wrapper and license notice.

```powershell
.venv/Scripts/python.exe tools/prepare_bennett_reference.py
Push-Location results/validation/bennett_author
# Only with an available compatible runtime; preserve its version/output log.
octave-cli --version
octave-cli --quiet run_reference.m
Pop-Location
.venv/Scripts/python.exe tools/compare_bennett_reference.py results/validation/bennett_author/author_trace.csv --runtime "actual runtime and version"
```

Equivalent execution of `run_reference.m` in an already available MATLAB is possible but untested. No software purchase is needed or proposed. The comparator refuses wrong dimensions/nonfinite values and checks every q, d and weight with absolute tolerance 1e-10. A numerical match alone does not authenticate provenance: retain runtime output, preparation manifest and trace together. The comparator does not automatically change the reproduction register.

## Equation review and gate status

The vectorized learner uses `q=(w_plus-w_minus)·s`; the scalar Decimal oracle separately computes each cue's M+ and M− dot products, rectifies each DAN drive, and builds both new weight vectors from their old values. Hand-calculated fixtures check reward sign, zero projection and simultaneous updates. The eq8 difference equals twice the prediction error when `abs(r-q) <= gamma*sum(s)`, including the rectification boundary; outside it, equivalence fails in general. Both strict-positive occupancy and inclusive rate-match occupancy are recorded.

The original bounded milestone used independently formulated arithmetic implementations in one agent session, without an independent person or second-agent review. The later milestone closes R02 through the alternative author-runtime route: portable GNU Octave executes the preserved DAN/eq8 statements. Runtime output, exact commands, source/archive/executable hashes and the resulting trace are retained. This passes isolated equation validation; full published scientific findings remain unreproduced.

## Next concrete action

R02 and the measured learning baseline are complete. Next validate growth operators and variable-size assay reuse for EXP-003, retaining the native baseline. The baseline implementation now includes episode-specific streams, direct-PN comparison, participation/rank diagnostics, frozen selection, resource counters and atomic episode/block recovery. See [protocol 1.1](EXP-002-baseline-protocol.md) for commands and scope; use fresh development data for structural experiments.

The [target hardware record](../research/target_hardware.json) preserves the colleague's reported 64 GB RAM, RTX 5090 32 GB and Ryzen 7 9800X3D. The user corrected the memory type to DDR5; OS/storage/software are unknown. No target access, hardware probe or benchmark occurred. A separate measured pilot is skipped; future scientific runs must still record their actual environment and resource use.
