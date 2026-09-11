# Research branch portfolio

Updated 2026-09-11. All hypotheses are untested internally. Rankings are **judgments about decision value**, not measured success probabilities. Closest work and contrary evidence are synthesized in [STATE_OF_ART.md](STATE_OF_ART.md); experiment details are authoritative in their specifications.

| Branch | Hypothesis and closest work | Counterargument / cheap falsification | Dependencies and status |
|---|---|---|---|
| B1 Fixed topology, dynamics and plasticity | Better dynamics or feedback learning can improve adaptation without growth. Shiu S07, Lappalainen S08, Bennett S10, Abdelrahman S68 | A generic delta rule or normalization explains gains; feedback may be algebraically equivalent after rate rescaling. Compare competent equal-access learners before enlarging | Small source-equation validation and larval feature assay. **Shortlisted EXP-002**; does not become a mandatory first stage for every branch |
| B2 Sparse structural intervention | A few targeted new/rewired edges can improve a bottleneck more cheaply than adding cells. Xie S20 is close structural-perturbation precedent | Target selection overfits the benchmark, or optimized weights reproduce the same gain. Compare targeted versus random edits with equal edit and search budgets; freeze candidates before held-out tasks | Valid baseline, interpretable bottleneck and weight-only comparator. **Preserved, deferred** until diagnostic error patterns identify an intervention; 2–5 additional days for a bounded screen |
| B3 Structured circuit growth | Population expansion under a wiring prior can improve adaptive representations. Elkahlah S12, Ellis S13, Litwin-Kumar S14, Xie S20, Abdelrahman S68 | Random features, output parameters, winner-count steps or activity compensation explain the improvement. Clone, uniform and degree-null controls plus fixed readout | Learning assay and static growth audit. **Shortlisted EXP-003**; 4–7 days after baseline, CPU-scale tests |
| B4 Intrinsic computational capacity | Native organization affects recoverable input-history functions beyond low-order graph properties. Dambre S15, conn2res S16, Morra S17/S18, Costi S67 | Degree, signed weights, stability normalization or readout access suffice; negative topology result S19 narrows confidence | Tiny pinned visual graph and independent recurrence validation. **Shortlisted EXP-001**; 3–6 days, no body model |
| B5 Generative/developmental/evolutionary or coupled modules | Compact wiring rules or module interactions improve robust capability per resource. HyperNCA S32, generative graphs S33/S34, POET S35, central complex S29 | Huge search budget or task curriculum, rather than rule, creates gains; topology fit need not imply function | External held-out task battery, search-cost accounting, module I/O contract. **Deferred**, 2–6 weeks for a bounded pilot once baseline exists; potentially longer search |
| B6 Cross-modal access and compensation | Reusing existing features across modalities offers gains without cell growth. S58/S62; inaccessible S26 remains unresolved | Better access to cues is extra information, not improved intrinsic capacity; specialization trades against another modality | Two independently controllable input modalities and sensory-information-matched baselines. **Literature-motivated reserve**, not in first three |

## Candidate selection

Scores 1–5 (higher is better). Information, falsifiability, evidence and readiness have weight1; affordability has weight1.5. Formula `I+F+E+R+1.5*A`. These ordinal scores make the judgment inspectable; they do not imply precise quantitative utility.

| Candidate | Information | Falsifiability | Evidence quality | Readiness | Affordability | Weighted score | Rank |
|---|---:|---:|---:|---:|---:|---:|---:|
| EXP-002 fixed-wiring adaptation | 4 | 5 | 4 | 5 | 5 | 25.5 | 1 |
| EXP-001 intrinsic capacity | 5 | 5 | 4 | 4 | 4 | 24 | 2 |
| EXP-003 controlled growth | 5 | 5 | 3 | 4 | 4 | 23 | 3 |
| Sparse targeted rewiring now | 4 | 4 | 3 | 2 | 4 | 19 | 4 |
| Cross-modal coupling now | 4 | 3 | 3 | 2 | 2 | 15 | 5 |
| Whole-body developmental evolution now | 5 | 2 | 2 | 1 | 1 | 11.5 | 6 |

EXP-001 and EXP-002 are independent approaches: fixed recurrent dynamics with a fitted readout versus online adaptive learning in a sparse feedforward representation. EXP-003 adds an explicit structural-growth question while reusing a validated assay. This reuse reduces engineering cost but makes its conclusions conditional on that assay; the roadmap requires an independent adult/task validation before broad conclusions.

Start with EXP-002's equation and task validation. EXP-001 can instead be selected first if intrinsic capacity becomes the priority; no scientific dependency forces it behind plasticity. EXP-003 depends on a validated learner, not on a positive biological-advantage result. Re-rank if source access, numerical validation, measured cost or new contrary evidence changes these assumptions.

## Deferred and rejected commitments

We reject a guaranteed “larger means smarter” premise, an automatic BANC-first commitment, and a single simulator as the scientific definition of the project. We defer uniform whole-brain doubling, body-first benchmarking and unconstrained evolutionary search because their first results would entangle too many causes. These are decisions, **not failed experiments**; see [DECISIONS.md](DECISIONS.md).
