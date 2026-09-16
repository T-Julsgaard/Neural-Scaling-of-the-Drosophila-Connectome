# Research branch portfolio

## Current entry conditions — 2026-09-14

EXP-005 mechanism, EXP-006 memory benchmark and EXP-007 participation tests are complete. Foundation rankings below are historical. **EXP-008 adult transfer is complete** (Adult calibration minus ordinary tuning: -0.19 [-1.01, 0.68] pp (98.333333% interval). Transfer classification: equivalent; informative-benchmark gate passed.), with a [specific prediction and transferred procedure](experiments/EXP-008-protocol.md) specified before adult development. Positive intervention results are not a prerequisite.

| Branch | Explicit entry condition | Required discriminator |
|---|---|---|
| Adult validation | Informative benchmark plus a specific finding or limitation; met for EXP-007 | Independent projection, development-only calibration, strong tuning, fresh evaluation and ceiling/floor gate |
| Growth | A demonstrated representation limit makes useful added features plausible | Preserve ancestor features/learned function, measure competition and resource controls; unused cells alone do not qualify |
| Targeted rewiring | Particular input collisions predict which memories fail | Freeze development targets; equal-budget random edits and weight-only tuning |
| Bounded evolution | Selection is challenged by a held-out capability battery with task-family variation | Separate search/evaluation, ancestry/replay and equal-budget random search; a second anatomy in the same assay is insufficient alone |
| EXP-001 recurrent capacity | Distinct recurrent question remains informative; graph/dynamics checks pass | Its own validated task and topology/null comparisons |

Updated 2026-09-13. EXP-002, EXP-003 and EXP-004 are complete. EXP-004 separates a normalized active-count retention benefit from a population penalty under the fixed readout. Foundation rankings remain historical judgments; no automatic whole-brain expansion follows.

| Branch | Hypothesis and closest work | Counterargument / cheap falsification | Dependencies and status |
|---|---|---|---|
| B1 Fixed topology, dynamics and plasticity | Better dynamics or feedback learning can improve adaptation without growth. Shiu S07, Lappalainen S08, Bennett S10, Abdelrahman S68 | Generic learning is a competent alternative; feedback's reversal benefit over reward-only has acquisition/retention costs. Feedback/delta equivalence was not established | **EXP-002 baseline complete.** R02 author runtime and held-out adequacy pass. Generic delta selected on development for structural follow-up. [Results](experiments/EXP-002-baseline-results.md) |
| B2 Sparse structural intervention | A few targeted new/rewired edges can improve a bottleneck more cheaply than adding cells. Xie S20 is close structural-perturbation precedent | Target selection overfits the benchmark, or optimized weights reproduce the same gain. Compare targeted versus random edits with equal edit and search budgets; freeze candidates before held-out tasks | Valid baseline, interpretable bottleneck and weight-only comparator. **Preserved, deferred** until diagnostic error patterns identify an intervention; 2–5 additional days for a bounded screen |
| B3 Structured circuit growth | Population expansion under a wiring prior can improve adaptive representations. Elkahlah S12, Ellis S13, Litwin-Kumar S14, Xie S20, Abdelrahman S68 | EXP-004: K4→K6 helps retention while N73→N110 hurts it under fixed readout; population growth at fixed K6 also hurts with full readout | **EXP-003/004 complete.** Deprioritize the tested wiring prior and further population expansion here. Next normalization/update-size controls at N73. [Results](experiments/EXP-004-results.md) |
| B4 Intrinsic computational capacity | Native organization affects recoverable input-history functions beyond low-order graph properties. Dambre S15, conn2res S16, Morra S17/S18, Costi S67 | Degree, signed weights, stability normalization or readout access suffice; negative topology result S19 narrows confidence | Tiny pinned visual graph and independent recurrence validation. **Shortlisted EXP-001**; 3–6 days, no body model |
| B5 Generative/developmental/evolutionary or coupled modules | Compact wiring rules or module interactions improve robust capability per resource. HyperNCA S32, generative graphs S33/S34, POET S35, central complex S29 | Huge search budget or task curriculum, rather than rule, creates gains; topology fit need not imply function | **Integrated exploratory branch (D021).** Review a bounded lineage pilot at M2/M3 once learner, assay and structural operator are validated. Require ancestry/replay, budget-matched random search and held-out evaluation. Larger development/module work remains deferred; no measured pilot runtime |
| B6 Cross-modal access and compensation | Reusing existing features across modalities offers gains without cell growth. S58/S62; inaccessible S26 remains unresolved | Better access to cues is extra information, not improved intrinsic capacity; specialization trades against another modality | Two independently controllable input modalities and sensory-information-matched baselines. **Literature-motivated reserve**, not in first three |

## Candidate selection

Scores 1–5 (higher is better). Information, falsifiability, evidence and readiness have weight1; affordability has weight1.5. Formula `I+F+E+R+1.5*A`. These ordinal scores make the judgment inspectable; they do not imply precise quantitative utility.

These foundation rankings describe the original candidates. Whole-body developmental evolution is distinct from D021's small lineage pilot, which is not yet specified or scored. The selected working sequence is in [ROADMAP.md](ROADMAP.md); retaining a branch does not mean running all branches concurrently.

| Candidate | Information | Falsifiability | Evidence quality | Readiness | Affordability | Weighted score | Rank |
|---|---:|---:|---:|---:|---:|---:|---:|
| EXP-002 fixed-wiring adaptation | 4 | 5 | 4 | 5 | 5 | 25.5 | 1 |
| EXP-001 intrinsic capacity | 5 | 5 | 4 | 4 | 4 | 24 | 2 |
| EXP-003 controlled growth | 5 | 5 | 3 | 4 | 4 | 23 | 3 |
| Sparse targeted rewiring now | 4 | 4 | 3 | 2 | 4 | 19 | 4 |
| Cross-modal coupling now | 4 | 3 | 3 | 2 | 2 | 15 | 5 |
| Whole-body developmental evolution now | 5 | 2 | 2 | 1 | 1 | 11.5 | 6 |

EXP-001 and EXP-002 are independent approaches: fixed recurrent dynamics with a fitted readout versus online adaptive learning in a sparse feedforward representation. EXP-003 adds an explicit structural-growth question while reusing a validated assay. This reuse reduces engineering cost but makes its conclusions conditional on that assay; the roadmap requires an independent adult/task validation before broad conclusions.

EXP-002 baseline, EXP-003 growth confirmation and EXP-004 activity/population diagnostic are complete. The next informative test holds N73 fixed and separates normalized winner count from activity amplitude/effective updates. EXP-001 and B2/B4/B5 alternatives remain available; no numerical ranking was re-estimated from these outcomes.

## Deferred and rejected commitments

We reject a guaranteed “larger means smarter” premise, an automatic BANC-first commitment, and a single simulator as the scientific definition of the project. We defer uniform whole-brain doubling, body-first benchmarking and unconstrained evolutionary search because their first results would entangle too many causes. These are decisions, **not failed experiments**; see [DECISIONS.md](DECISIONS.md).
