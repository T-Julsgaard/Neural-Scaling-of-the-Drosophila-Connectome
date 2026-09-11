# Research log

## 2026-09-11 — EXP-002 bounded learning-rule validation

**Request:** continue with EXP-002 learning-rule validation and skip the measured workstation pilot. The target is a colleague's PC, reported as 64 GB DDR4 RAM, RTX 5090 32 GB and Ryzen 7 9800X3D. Recorded those facts as user-reported, with the DDR4/AMD-DDR5 discrepancy unresolved. No target hardware probe or benchmark ran.

**Implemented:** NumPy float64 frozen/reward-only/feedback/delta rules; hash-checked D05 40-PN/73-mature-KC loader and sparse encoder; a validation-only chronological episode for both task families; chosen-action-only updates; copied-state A/B probes; atomic, digest-checked episode checkpoints; 256 supplied 20-KC/two-cue equation fixture; a separate scalar Decimal oracle and analytic/toy checks. Added bounded source recovery, source-preserving MATLAB harness preparation and an explicit trace comparator. Dependencies are recorded for CPython 3.12.14/NumPy 2.3.5; the local venv reuses bundled packages and is not a target clean-install test.

**Results:** Thirteen automated tests passed. Maximum equation-trace error was 4.44e-16 versus the 1e-10 tolerance; feedback/delta rate matching agreed exactly on 166 eligible supplied-trace steps; 60 checkpoint restore points matched full state and scalar traces. Probe nonmutation, chronology, hash/orientation/normalization, sparse ties, numerical guards, deterministic toy reversal and shuffled-reward controls passed. These are implementation checks on validation data, not H2 findings, biological evidence or a floor/ceiling assessment. The initial CSV newline error was repaired and all checks rerun.

**Gate and limits:** MATLAB/Octave was not found in the inspected locations. The author wrapper preserves the original DAN/eq8 section and uses a 257th sentinel because the source omits its last update; it has not executed. No independent person/agent reviewed the equation adaptation. R02's automated checks pass, while its independent-review/author-runtime gate remains open. No development/confirmation blocks, full published reproduction, GPU benchmark or paid compute ran. The full campaign runner, statistical analysis and resource accounting remain future work.

**Evidence:** [validation handoff](experiments/EXP-002-validation.md), [machine-readable results](research/exp002_validation.json), [target report](research/target_hardware.json), D016–D018. The two original documents remain unchanged.

**Next concrete action:** independent review of the equation adaptation or execution of the prepared author trace, followed by development-only assay implementation. Skip the separate workstation pilot as requested.

## 2026-09-11 — Foundation implementation

**Request:** implement the approved research foundation, preserving an open branch portfolio and stopping before experimental-platform construction or simulations. Read the initial prompt before the master brief; treat document recommendations as material to assess. Target the separate 64 GB workstation, not this session's GPU.

**Work completed:** initialized local Git; preserved source documents; audited consequential propositions and reconstructed nonportable master citations semantically; surveyed six research areas and adjacent terminology; inspected decision-critical methods and selected code; pinned 11 software commits; downloaded and hashed bounded small source assets; created a 70-source JSON/BibTeX bibliography with read-depth status; wrote branch ranking, three experiment specifications, shared benchmark/statistics contract, continuity and roadmap records.

**Findings that changed decisions:** BANC has relevant missing sensory structures; MaleCNS provider versions differ; Shiu defaults to v630; current FlyGym/flybody requirements conflict. Literature already contains direct fly reservoir/hybrid controls and compensatory-variability models. The larval supplement has 14 row/column ordering mismatches outside the chosen subset, duplicate labels,37 young left KCs and 27 with no selected PN input. Pilot learning therefore uses73 mature cells and synthetic valence outputs, with adult validation deferred explicitly. Feedback learning can reduce algebraically to generic error learning in a regime; the handoff diagnoses that equivalence.

**Checks completed:** static source/data inspection, reference metadata verification and repository validation are recorded in [validation_report.json](research/validation_report.json). No neural simulation, learning experiment, upstream scientific reproduction, simulator installation or paid compute was performed. Original document SHA256 values remain the preservation criterion.

Final integrity checks passed for 22 generated Markdown documents, 67 local links, 70 bibliography entries, all research JSON, Python audit-script syntax and the unexecuted PowerShell hardware-collection script. Git's staged copies of both originals match their working bytes exactly. New files pass the whitespace check; original Markdown hard-break whitespace is intentionally preserved. Repository-specific line-ending attributes protect the supplied documents from checkout conversion.

**Access limits:** recent S25/S26/S53 full texts unavailable; two code-tree API requests rate-limited; anonymous Codex API returned HTML. The affected claims and candidates remain unresolved. Search saturation was reset after late close-prior-work discoveries; two subsequent targeted rounds did not change the shortlist.

**Current understanding:** the first scientific contribution should discriminate organization from normalization, learning and added resources. A validated negative result is useful. Small larval/visual assays can establish methods but do not substantiate an adult whole-brain claim.

**Next concrete action:** select the recommended EXP-002 validation milestone, capture the actual target workstation specifications, and implement R02 plus the smallest task/chronology fixtures. Do not begin a full confirmation run until validation, measured sizing and development-only configuration selection pass. EXP-001 remains an independent alternative.
