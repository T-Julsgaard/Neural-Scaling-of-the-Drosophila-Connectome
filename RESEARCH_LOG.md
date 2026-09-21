# Research log

## 2026-09-21 - Academic report production completed

Completed the user-requested professional local report after reviewing the master production document, D assessment, attribution decisions, experiment protocols/results, saved arrays and primary-source context. The [publication package](publication/README.md) contains a 13-page main report, six-page technical supplement, three vector/high-resolution figures, editable Markdown, bibliography, figure-source CSVs, compact evidence, acquisition/rights notes, hashes and a ZIP. The requested report date remains 16 September 2026; production/access dates are recorded separately.

The scientific narrative preserves calibration equivalence, tail guardrail failures, readable-but-forgotten information, XOR calibration counterevidence, random parity, quadratic success, noise degradation, tuning boundaries and the matched-update replay tradeoff. It makes no biological-mechanism, general-scaling or causal compensation-bridge claim. Citation work updated Fly-CL to inspected v2, corrected Xie/Ocker metadata and explicitly qualified inaccessible Robins methods and Zenodo archive metadata. The supplement specifies the exact supplied-model rate grid and 5x versus 4.5x mismatch.

Verification: 43 B/C saved-block aggregate/paired-interval checks and 380 saved-array/summary checks passed. All 19 final pages were visually inspected; an orphan Methods page and a cropped low new-context block were repaired. The versioned [schema-3 record validator](tools/validate_foundation_v3.py) passed while preserving the legacy checker. Its [report](research/validation_report_v3.json) records 11 specifications, ten scientific experiments, source/selection/stage checks, and explicitly bounded historical document changes. Final package integrity and live handoff links are checked separately in the production manifest.

This is report production, not EXP-012, independent scientific validation or a new campaign. Original experimental files and historical snapshots remain intact. No publication, submission, upload or push occurred. Next: Thomas's scientific approval and declarations, followed by independent review and any chosen venue's requirements, as listed in [readiness](publication/readiness.md).

## 2026-09-16 — Master prompt for final report production

Created [the reusable production prompt](research/MASTER_PROMPT_PUBLICATION_REPORT.md) incorporating Session D, the content/attribution follow-up, numerical checkpoints, counterevidence, scope limits, three figures, reproducibility/validator work, render verification and outside-review limits. Thomas confirmed a venue-neutral report and the exact affiliation “Thomas Julsgaard — MSc student in Software Design, IT University of Copenhagen”; no email. Requested report date: 16 September 2026. This turn creates instructions for another instance, not the final report or new experiments. Publication, submission and push remain prohibited.

## 2026-09-16 — Report content and direct attribution follow-up

Reviewed what deserves main-text emphasis and which prior work supplies actual data, code, parameters or conceptual precedent. Added [content/attribution decisions](research/REPORT_CONTENT_AND_ATTRIBUTION.md), revised the [draft](research/EMPIRICAL_REPORT_DRAFT.md) with point-of-use anatomical and learning-rule citations, and clarified figure attribution. Direct dependencies: Eichler larval matrix; Scheffer/Li adult resource/context; Abdelrahman supplied-model/code and PN annotations; Bennett's initial Eq. 8 validation lineage. Later generic delta is not the complete Bennett model. Zou/Fly-CL are related work, without established code reuse.

Priorities: controlled calibration equivalence, intervention size, readable-but-forgotten information, same-update schedule/history controls, memory tails and visible counterevidence. C's secondary calibration benefit stays in the main report; differing signs across experiments do not establish a formal interaction or show that forgetting masked the original intervention's benefit. Rechecked primary source metadata and local code/provenance. No new experiments, scientific-result edits, publication or push. D's artifact index remains its original snapshot; a separate follow-up index covers these document revisions.

## 2026-09-16 — Session D completed: narrow empirical report

User requested critical evidence/literature review and a justified local writing outcome, without new campaigns or publication. Read actual A/B/C protocols, reports, sources, relevant code and saved results, plus EXP-007/008 and current records. C's frozen conjunction passes on saved block arithmetic; it was not assumed from the handoff. Checked primary compensation and Zou/Zang/Ji methods and later adjacent Fly-CL work.

Deliverables: [assessment/claim table](research/SESSION_D_ASSESSMENT.md), [literature audit](research/SESSION_D_LITERATURE_AUDIT.md), [figure plan](research/SESSION_D_FIGURE_PLAN.md), [local empirical report](research/EMPIRICAL_REPORT_DRAFT.md). Decision: modest controlled boundary-case contribution, not a new mechanism or biology paper. Retain negative calibration findings, unestablished worst-memory safety, C's positive secondary calibration result, random parity, quadratic sequential success, privileged offline access and rate-grid limits. No complete explanation of the published/local discrepancy.

New [record check](research/session_d_record_check.json) recomputes B/C primary intervals from saved blocks, checks B/C source/development freezes and chronology, and verifies 72 A/B/C confirmation archive checksums without rerunning learners. This is automated consistency checking, not independent validation. Local Python alias was unavailable; the PowerShell audit initially failed on array-division syntax, was corrected with explicit parentheses and then passed. Historical scientific source, protocols and results were not edited. Legacy validator remains stale; no full-foundation pass claimed.

Next: if pursuing the narrow report, finish figures/portable artifact packaging, repair the record-validator schema and obtain outside scientific scrutiny. No new campaign is essential for restricted claims. A lower-rate repair is specified only for an optional stronger online-optimization claim and was not run. No publication, submission, commit or push. This entry supersedes historical pending-D and B/C deferral instructions below.

## Current Session C status — 2026-09-15

The prospective prediction is supported: useful nonlinear distinctions remain readable from frozen sparse representations while the tuned sequential readout loses previously learned associations. Native/calibrated offline old-context accuracy 95.67 [92.91, 98.44]%; tuned sequential accuracy 51.73 [41.24, 62.21]%; paired gap 43.95 [34.23, 53.67] pp; acquisition-to-final loss 45.86 [35.78, 55.93] pp (95% intervals, 24 fresh blocks). [EXP-011 report](experiments/EXP-011-results.md). C is complete; D has not started. Current user authorization supersedes the historical C deferral below. Next action only when requested: D per [handoff](research/SESSION_D_HANDOFF.md). No publication.

## 2026-09-15 — Session B completed and audited

Offline full-outcome old-pair accuracy 96.97% versus fully supervised online 76.72%; paired difference 20.26 pp [16.46, 24.05] (95%, 24 fresh task blocks, native/calibrated average). Frozen-feature information remains linearly recoverable despite sequential readout forgetting in this fixed larval assay. Offline is an explanatory diagnostic with different fitting/history access, not an equal-budget competitor or capacity bound. Five validation tests; six development tasks; all 31 validation/development/confirmation blocks replayed. B gate passed; C is explicitly deferred by the user. [EXP-010 report](experiments/EXP-010-results.md). No normalization factorial, stronger compensation, new anatomy, growth, paid compute or C task was run. Next action: retain the frozen prediction for a later explicitly requested Session C; stop now.

## 2026-09-15 — Session A completed at decision gate

User authorized the full milestone and later requested continuation after a token interruption. Read current records and actual code/reports; selected Abdelrahman Figure 4B2, c=1, threshold compensation versus random. Pinned source, SI, published numerical data and one supplied fitted model. Preserved a 5x saved-weight versus 4.5x source discrepancy. Wrote prospective EXP-009 protocol; implemented independent fresh tasks and training-only scaling, with author equations and supplied fitted parameters.

Seven tests passed; max author-runtime error 1.17e-15. Four development blocks selected eta .001/.001778; fixed 24 confirmation blocks completed. All 152 readout evaluations replayed exactly and 82,263 historical files verified. Compensation improves correct-valence choice probability by 8.58 pp [8.13, 9.03] (95% paired task-block interval). Positive-control gate passed; **not exact Figure 4 reproduction**. No fresh optimizer/ensemble or biological replication.

Historical hash snapshot began before validation but finished after confirmation; final verification passed and no old scientific files were edited. The token continuation reused saved runs/settings. Literature/source preparation, file-hash I/O and reporting are separate from measured model costs. [Report](experiments/EXP-009-results.md), [run](research/runs/EXP-009-positive-control.json).

Stop at A. Next: [Session B diagnostic](research/SESSION_B_HANDOFF.md), prioritizing normalization/limited compensation and representation-versus-readout loss with matched supervision and norm controls. Session B has not launched; earlier immediate task-family expansion recommendations are superseded by the A–D gates.

## 2026-09-14 — Bounded follow-up session plan

User requested the next-session plan and advice on one long prompt versus multiple prompts. Created [sessions A–D](research/NEXT_SESSIONS_PLAN_2026-09-14.md): one published positive-control comparison; representation/learning diagnostics and a bounded explanatory bridge; a conditional prospective new-task prediction; and a critical manuscript decision. These new labels preserve the completed original priorities 1–4. Recommended four sequential execution prompts, with one optional additional completion/repair session and explicit scientific stopping gates. Prompts include full milestone execution so protocol preparation is not mistaken for the final deliverable.

No experiment or new task was launched. Next concrete action: execute Session A when its execution prompt is issued. The plan does not promise novelty, impose an outcome, or authorize publishing. The paper assessment remains the evidence basis.

## 2026-09-14 — Findings and paper-worthiness assessment after priority 4

User requested an honest synthesis and assessment of surprise, novelty and paper potential. Reviewed EXP-005–008 reports, EXP-007/008 protocols, selected learner/calibration/input code and saved diagnostics, and checked close primary literature. The [paper assessment](research/PAPER_ASSESSMENT_2026-09-14.md) identifies a plausible narrow computational negative-result contribution, not an established new biological mechanism or scaling law. The homeostasis recommendation failed its practical-benefit test; adult equivalence prospectively extends that bounded limitation. Recruitment changes, tail failures, direct-input strength, existing normalization and modest adult intervention/headroom all limit interpretation.

A particularly close prior work is Zou, Zang and Ji's 2025 sparse-expansion continual-learning preprint; its primary PDF was inspected and recorded in SEARCH_LOG. No exact duplicate of the bounded two-anatomy calibration result was identified, but priority is unproven. Suggested paper-strengthening work is a positive-control bridge, a representation-versus-online-learning diagnostic and a distinct task with justified expansion demand. No new campaign, repeated full artifact audit or historical claim modification. Next concrete action: choose the narrow manuscript claim and specify its most discriminating bridge experiment before further execution.

## 2026-09-14 — Priority 4 adult transfer completed

Adult calibration minus ordinary tuning: -0.19 [-1.01, 0.68] pp (98.333333% interval). Transfer classification: equivalent; informative-benchmark gate passed. [EXP-008 results](experiments/EXP-008-results.md). Eight development and 24 fresh confirmation blocks; all nine preflight tests, exact validation replay, checkpoint audits and one replay per stage passed. Protocol and procedure preceded calibration/development; selection/sample size/source were frozen before confirmation. Historical scientific hashes verified. Report includes strong tuning, direct/random/sham baselines, exact-multiset control, negative/inconclusive classification, adequacy and tail gates, and actual resources. Plotting required read escalation for the existing cached Matplotlib installation.

Next: define a distinct held-out task family to test the limitation beyond this associative assay. Growth, collision-targeted rewiring and evolution retain their explicit entry conditions; no additional campaign is launched.

## 2026-09-14 — Priority 4 adult transfer initiated

User authorized data selection, implementation, checks, development and fresh confirmation. Selected the EXP-007 limitation (calibration did not add useful retention beyond ordinary tuning) as a prospective equivalence prediction, not a proven mechanism. [EXP-008 protocol](experiments/EXP-008-protocol.md) was written after anatomy-only inspection and before calibration/rewarded development/evaluation. Adult hemibrain:v1.1 CA(R) contacts from pinned monoglomerular PN annotations to KCg-m yield 104 x 590, 4,878 edges and 85,151 contacts. Subtype chosen for olfactory circuit and bounded size before performance. Preserve activity fractions, nominal update scale, independent calibration pools, strong direct/random/sham controls, negative/inconclusive outcomes and a ceiling/floor adequacy gate. Nine preflight tests passed; full validation underway. Historical scientific files are pinned in [preservation manifest](research/exp008_historical_hashes.json).

Public shell network requests required sandbox escalation and succeeded; the 45 MB public source archive was downloaded locally. The author repository's positional KC exclusions could not safely map to body IDs and were not applied; the archive's non-cropped traced-neuron filter is retained. No paid compute, upstream code execution or evolutionary search.

## 2026-09-14 — EXP-007 completes priority 3

User authorized the research handoff, explicitly retaining stronger ordinary tuning. Implemented bounded unlabeled offsets, equal 32-setting searches (rates down to .000208333), persistent memory, shuffled/null/direct controls and held-out PN gain shift. Ten preflight tests, exact validation replay, eight development blocks and 32 fresh confirmation blocks passed audits and stage replays. The precision rule used development variance to request 26 blocks before rounding to 32. No outcome-based confirmation extension.

Homeostasis and ordinary tuning are practically equivalent within the prespecified ±3-point retention band in the primary condition. Calibrated K6 retains 79.28% versus 79.55% for ordinary tuning; difference -0.27 [-1.67, 1.13] pp (98.333333%). [EXP-007 results](experiments/EXP-007-results.md).

Development selected different calibration strengths for the calibrated and optimized sham arms. A transparent addendum froze an additional exact-multiset sham before confirmation, with no extra search and descriptive inference only; all supplemental blocks audited and one replayed. The PN attenuation shift is invertible at input level and tests encoder/learner sensitivity, not raw-information destruction. No model-source changes occurred after development freeze. No subagents, paid compute, growth or second anatomy were used.

Design priority 4: validate the observed retention/participation result in another circuit under equally strong tuning. Freeze the transfer prediction and algorithm before new anatomy-specific development. Growth remains conditional; do not retune or extend EXP-007 confirmation.

## 2026-09-14 — Priority 3 activity-homeostasis research

Completed user-requested targeted research, grounded in EXP-005/006 and the current encoder. [Research and design handoff](research/ACTIVITY_HOMEOSTASIS_RESEARCH_2026-09-14.md) recommends bounded, partial per-cell offsets before fixed-K winner selection, development-only calibration, shuffled assignment controls and equal total tuning budgets. Abdelrahman et al. provides close precedent and highlights imperfect transfer and threshold-range limitations; 2026 KC/APL evidence further cautions against assuming interacting homeostatic rules cooperate.

Clarified that unused-cell measurements depend on task exposure and include both presented choices; useful persistent retention and worst-memory behavior are the target. Fixed K/amplitude preserves feature norm, but actual pair-margin interference still needs measurement. Calibration adds fitted parameters and data costs. Existing lower-load results cannot certify capacity for a new calibrated model. No learning experiment, implementation change or new performance result occurred; priority 3's experimental gate remains open. Next: freeze EXP-007 design, controls, margins and validation before fresh development/confirmation.

## 2026-09-14 — EXP-006 closes persistent-memory milestone

User authorized roadmap priority 2. Implemented and froze a continuous-memory challenge: loads2/4/8/16, shared core2/6, constant-per-pair/constant-total exposure, native K4/K6, direct input, three degree/contact-matched random circuits per block, oracle validation. Retained weights throughout acquisition/reversal; probed every old pair without updates. Nine preflight tests and exact validation replay passed; six development blocks selected global settings from equal eight-candidate grids; 32 confirmation blocks completed and audited without exclusions. No subagents or additional interventions.

Primary hard retention K6-K4 +7.60 pp [4.68,10.43]; noise advantage +6.06 [3.61,8.31]; K6 load16-load2 -18.22 [-22.21,-14.05]; K6 high-low similarity -0.02 [-5.21,5.13], all 98.75%. Initial learning remains high. Average-capacity criterion: native K6 through8, direct through16. Worst-memory losses are severe. Native K6 versus random K6 hard retention remains inconclusive.

Disclosed timing deviation: a preflight stream test generated one development and one confirmation prototype fixture before stage freeze, without learning/performance inspection. WindowsApps Python failed before samples; bundled Python worked. CIM inventory denied; process/platform counters recorded. Plot cache required read escalation. Frozen EXP-002–005 sources/results preserved; source-hashed EXP-006 code/results retained. See [results](experiments/EXP-006-results.md), [protocol](experiments/EXP-006-protocol.md), [run](research/runs/EXP-006-confirmation.json).

Close priority2. Next: separately calibrated homeostasis versus global tuning and shuffled calibration; retain mean/worst memory, new learning, reversal and noise. No immediate growth or transfer, no retuning of completed confirmation.

## 2026-09-13 — EXP-005 closes bounded activity mechanism milestone

The user authorized completion of roadmap priority 1 and requested findings, next action and any change of course. Created and froze EXP-005 before development: eight fixed amplitude/update/norm settings, equal eight-candidate tuning per K, frozen controls, six development and 32 evaluation blocks on fresh root 6. Twenty reset episodes per block. Created the prospective EXP-006 benchmark design before evaluation.

21 preflight tests passed after repairing a checkpoint JSON-envelope reader mismatch before campaign execution. Both campaigns completed and audited with raw hashes, task regeneration, metric recomputation and exact full-block replay. No exclusions or campaign failures. No subagents or external reviewer. Old source/protocol/results were preserved.

Protocol timing deviation: preflight instantiated one development and one evaluation task to compare hashes before freeze, contrary to the literal input-generation timing rule. No learner or performance evaluation used those tasks before the declared stages; no evaluation-based tuning or sample replacement occurred. The report and run record disclose this distinction.

Historical K6-K4 retention +4.25 pp [2.71,5.90]; slow matched and tuned +3.78 [2.39,5.27]; fast matched +3.91 [2.17,5.74] (four primary 98.75% intervals). Positive residual after equal tuning; neither practical equivalence nor an effect definitely above +3 pp is established. New learning improves on secondary online measures. Actual matched coefficients are .33258/.33276; geometry shows greater within-cue repeatability but slightly greater between-cue overlap. Stability and participation are candidate contributors, not proven mediation.

Close priority 1 without further sampling. Roadmap order stays: persistent memory/load/similarity with restored baselines, then homeostasis, then a specific circuit transfer; growth/rewiring/evolution conditional. See [report](experiments/EXP-005-results.md), [run](research/runs/EXP-005-evaluation.json), [next design](experiments/EXP-006-design.md).


## 2026-09-13 - Independent next-steps assessment

**Request:** assess the project independently, considering alternatives beyond the two proposed follow-ups. Reviewed charter, roadmap, decisions, branches, baseline/growth/activity reports, saved EXP-004 estimates, encoder/readout and learner implementations, and targeted primary literature. No new learning campaign or repeat raw-artifact audit.

**Findings:** direct-PN delta remains a competitive historical comparator; reset episodes do not test cumulative memory load; constant total activity changes squared feature norm and effective updates; the ID-based fixed readout changes native coefficients with population size. Full-readout population costs prevent attributing all harm to that adapter. Saved exploratory N73/full estimates show K6's before-interference advantage +0.52 pp [-0.28, 1.22], post-interference +6.54 [4.73, 8.46], and difference in retention change +6.03 [4.15, 8.00] (existing 95% intervals). No primary claim was changed or newly inferred from these secondary estimates.

**Recommendation:** bound the N73 mechanism work, design a persistent-memory load/similarity benchmark now, restore direct-PN and randomized-encoder comparisons, and prioritize activity homeostasis before unguided growth/search. Retain adult transfer, targeted rewiring, EXP-001 and bounded evolution with explicit entry conditions. The [assessment](research/NEXT_STEPS_ASSESSMENT_2026-09-13.md) records analytical update-matching controls, evidence, external-source scope and decision gates. ROADMAP links the recommendation; existing scientific protocols/results remain unchanged.

**Next concrete action:** draft the N73 mechanism protocol and persistent-memory benchmark specification before another campaign. Neither design nor its execution is claimed complete.

## 2026-09-13 - EXP-004 completed, audited and interpreted

**Final record checks:** offline integrity passed for 34 Markdown documents, 180 local links, four experiment specifications and all three completed experiment records. Frozen scientific snapshots remain unchanged; new experiment/reporting tools compile and Git whitespace checks pass. Corrected the foundation checker’s legacy date/note metadata to reflect the current verification date.

**Completion:** EXP-004 completed and audited: 32 fresh evaluation blocks, 17,920 episodes and 47 passed preflight tests. Under the fixed 32-feature readout, increasing normalized active count K4→K6 improves retention +5.37 pp [3.89,6.97], while population growth N73→N110 reduces it -5.03 pp [-7.27,-2.86] (primary 98.333333% intervals). Four separate development blocks/2,240 episodes were audited first. Evaluation had 896 conditions and 19,200 configuration-episodes; no exclusions or numerical failures. Full audit took 182.1 seconds, verifying every raw artifact, task, graph, condition summary, frozen control and planned analysis.

**Primary and secondary:** interaction -0.04 pp [-2.99865,2.98647] has unresolved direction and only barely meets the ±3 pp practical band. Full-readout N73/K6 versus K4 retention +6.54 pp [4.73,8.46] and reversal +4.41 pp [2.32,6.49]; population growth at fixed K6 reduces retention -3.47 pp [-4.65,-2.36] (secondary 95%). The fixed-readout diagonal is +0.35 pp [-1.90,2.73], so EXP-003's earlier fixed-readout gain was not clearly reproduced. C41's prior qualified population-scaling status is refined accordingly; C43/C44 record the new primary evidence. No prior sample was changed.

**Recovery and resources:** preserved the version-1.0 development storage race; repeated development under root 5 before evaluation. Evaluation resumed unchanged after an execution-wrapper switch and a checkpoint PermissionError; all three invocations are retained. Total recorded invocation wall time 3281.9 s; retained-episode CPU 4007.7 s (excludes discarded uncheckpointed work), maximum individual worker peak 85.9 MiB, retained campaign 361.1 MiB before reporting. No target-workstation or energy measurement.

**Decision D030 / next concrete action:** Next specify a fresh N73-only diagnostic separating winner count from activity per winner and effective learning-update size, with explicit normalization and learning-rate-matched controls. N73/K6 is a promising same-assay candidate; a new task family is needed before broader adaptation claims. Do not extend completed samples or prioritize population expansion from this evidence. Total activity was fixed, so active count is not isolated from per-cell amplitude/effective learning. A new task family is required for general-adaptation claims. No subsequent normalization, adult or evolutionary experiment was executed.

**Evidence:** [results and inspected figure](experiments/EXP-004-results.md), [audited run](research/runs/EXP-004-evaluation.json), [analysis](results/exp004_evaluation/analysis.json), [execution recovery](research/exp004_execution_recovery.json). Original briefs and prior frozen scientific sources remain unchanged.


## 2026-09-13 - EXP-004 final-block recovery after second usage interruption

**Orientation:** 31 of 32 evaluation blocks completed while the conversation was interrupted. The runner recorded a Windows PermissionError replacing a checkpoint in block 1009, then waited for queued workers to finish. All completed blocks remain saved. The frozen scientific source still matches the 47-test validation; no result interpretation has occurred.

**Recovery:** retained the failure record, closed the interrupted invocation using its recorded failure timestamp, and resumed the same protocol/streams from hash-verified checkpoints with local access. The full audit is queued after the final block completes. No exclusions, parameter changes, sample changes or new scientific implementation. Runtime reporting includes all three invocations and distinguishes retained-episode CPU from discarded uncheckpointed work.

## 2026-09-13 - EXP-004 resumed after usage interruption

**Orientation:** protocol-1.1 development completed while the conversation was interrupted: four blocks, 112 conditions, 2,240 episodes and 2,400 configuration-episodes, all audited with no exclusions/numerical failures. Development wall time was 324.9 seconds, summed worker episode CPU 427.8 seconds and audit 32.7 seconds. All 47 validation tests still match the current frozen source. The failed version-1.0 infrastructure attempt remains preserved.

**Continuation:** verified saved evidence and recorded the [fresh development resource update](research/exp004_resource_update.json), then froze and launched the unchanged 32-block evaluation, followed automatically by its audit. No evaluation had run before this continuation. No outcomes were used to change settings, primary contrasts or sample budget. The new evaluation uses root-5 streams and 17,920 reset episodes.

**Execution-wrapper recovery:** after eight complete blocks, slow checkpoint/filesystem operations prompted a timing comparison. Local-access checkpoint reads were substantially faster. Verified the exact helper/runner/worker process identities, stopped only those processes, marked the interrupted invocation and resumed the identical frozen code under local access with all checkpoints preserved. Resume requires raw hash and summary verification; no streams, sample or scientific files changed. [Recovery record](research/exp004_execution_recovery.json). Report each invocation and summed recorded wall time; retained-episode CPU excludes discarded uncheckpointed work.

## 2026-09-12 - EXP-004 prospective activity/population diagnostic

**Request:** continue the recommended milestone isolating active-cell count from population size on fresh evaluation data.

**Design and freeze:** [EXP-004 protocol](experiments/EXP-004-protocol.md), D028. Cross N73/N110 with K4/K6, full/32-feature readouts, structured/degree-null growth, three nested graphs and shared native controls: 28 conditions per block. Retention active-count/population main effects and interaction under fixed readout are three prespecified primary contrasts, each with a 98.333333% interval. Four engineering-development blocks precede 32 evaluation blocks. New root-4 random streams separate this experiment from EXP-003. No parameter selection, sample adaptation or old-block extension.

**Precision and resources:** explicit planning SD .07 gives primary half-width approximately .0296 at N=32 and approximate 80% detectable effect .0400; these are assumptions, not guaranteed power. Historical retention paired SDs are retained as context only. Wall/storage proxies use EXP-003 measurements. At most three CPU workers, disk/artifact caps, atomic episode checkpoints and audited stage gates. No colleague-machine benchmark or paid compute.

**Validation:** 46 tests passed in the final preflight, including independent exact-K scalar encoding, legacy trace compatibility, factorial algebra/nesting, paired conditions, new stream root, recovery and corruption rejection. An earlier 45-test preflight passed before adding the final nesting test and correcting pre-freeze audit/report plumbing; the final 46-test record is authoritative. Prior frozen scientific code and audited summary hashes were verified unchanged.

**Current action:** fresh development execution and full raw-artifact audit, followed by the already specified untouched evaluation and its audit. Results are not yet claimed here. Count interventions keep total activity 10, so activity per winner and effective learning dynamics also change; biological count-only causality is outside this design.

**Pre-evaluation infrastructure revision:** the version-1.0 development retained-byte scan raced another worker's atomic temporary-file rename and stopped. Its artifacts, frozen source, original validation and failure are archived at `results/exp004_development_v1_failed/`. D029/protocol 1.1 handles only disappeared paths, adds a race regression test and repeats the complete preflight/development using root 5. No evaluation inputs had been generated, and learner, contrast definitions and 32-block budget were unchanged. The failed attempt is not evidence about either scientific hypothesis.

## 2026-09-12 - EXP-003 held-out confirmation completed and audited

**Scope and continuity:** completed the user's authorized confirmation campaign, including after the conversation's token interruption. The process continued without restarting, retuning, dropping controls or changing its frozen scientific files. D026 authorized this stage; D027 records the resulting decision. Historical development evidence and C41/C42's earlier descriptive/unsupported statuses remain in the development entry below.

**Execution:** 40 preflight tests passed; contract frozen at 14:39:24 UTC before stage-2 inputs. All twenty blocks 1000–1019, three nested graph replicates, five sizes and all sparsity/readout/whole-uniform controls completed: 1,600 conditions, 32,000 episode batches, 32,400 configuration-episodes. No exclusions, numerical failures or execution failure files. Wall time 2,149.5 seconds with three CPU workers; summed worker episode CPU 3,986.9 seconds, peak individual worker 142.5 MiB, retained artifacts before report 669.4 MiB. No target-workstation or energy claim.

**Audit:** all 32,000 episodes passed hash/identity/finite-value checks; graphs regenerated from the frozen seeds; every condition summary recomputed; frozen controls stayed exactly at chance. The audit took 485.7 seconds. The report/figures were rendered using the existing plotting package with sandbox access resolved; scientific NumPy remained 2.3.5.

**Primary:** structured minus degree-null reversal at N110 is -0.009 [-0.023, +0.007] (98.33%). Its upper bound is below +.05: evidence against the planned practical organization advantage. Deprioritize this prior, without claiming every small wiring effect is absent.

**Secondary:** structured N110 minus native N73 retention +0.034 [+0.017, +0.053], acquisition +0.010 [+0.006, +0.013], robustness .3 +0.007 [+0.002, +0.014]; early reversal +0.017 [-0.012, +0.048] remains uncertain. Uniform/null retention gains are similar or larger. Retention survives the fixed readout at +0.045 [+0.018, +0.073] but disappears with fixed-four activity at -0.020 [-0.042, +0.005]. All these intervals are secondary exploratory 95%. The whole-uniform N110 exploratory reversal gain is retained but never promoted to primary.

**Interpretation and next action:** fruitful evidence for a conditional retention benefit and against the proposed practically useful wiring prior; no clear main-arm reversal scaling or general adaptive-capacity improvement. Specify a prospective active-count-versus-population diagnostic with fixed readout controls, fresh streams and precision/resource budgeting before broader/adult transfer. No new sample expansion or evolutionary pilot was executed.

**Evidence:** [confirmation report](experiments/EXP-003-confirmation-results.md), [run audit](research/runs/EXP-003-confirmation.json), [frozen protocol](experiments/EXP-003-confirmation-protocol.md), [full analysis](results/exp003_confirmation/analysis.json).

## 2026-09-12 - EXP-003 confirmation authorized and frozen

**Request:** continue the recommended plan by freezing and running untouched confirmation blocks with every sparsity/readout control, and assess whether the work is fruitful.

**Prospective design:** [confirmation protocol 1.0](experiments/EXP-003-confirmation-protocol.md), D026. The audited development setting remains generic delta eta=.01/T=.1; blocks 1000–1019, all five sizes, three nested graphs and all 80 conditions per block. The primary organization contrast retains its +.05 margin and 98.33% interval; scale remains secondary. No partial outcomes drive execution or analysis choices.

**Preflight:** all 18,417 recorded development artifacts matched their hashes; 40 tests passed in 107.5 seconds, including source-identical scientific adapters, stage-zero trace agreement, checkpoint/control checks and twenty-block inference. Original development code, protocol and artifacts are preserved. [Resource estimate](research/exp003_confirmation_resource_estimate.json) uses measured N73/N146 development conditions. The current workspace had about 36 GiB free before execution.

**Freeze:** 2026-09-12T14:39:24.576315+00:00, before generating any confirmation inputs. [Frozen contract](results/exp003_confirmation/contract.json). Three CPU workers launched; outcomes remain uninterpreted pending twenty-block completion and audit.

## 2026-09-12 - EXP-003 fresh development completed

**Request:** freeze and run EXP-003 development to test whether added representations improve adaptation and retention.

**Protocol and execution:** protocol 1.0 froze independent experiment-3 streams, ten development blocks 100-109, three nested graph replicates, five sizes, four main rules, whole-base uniform resampling, fixed-four sparsity and 32-feature readout controls. All 36 preflight tests passed. The run completed 800 representation conditions, 16,000 reset episode batches and 144,200 configuration-episodes with no exclusions or numerical failures. One Windows checkpoint commit returned access denied after writing an episode; the saved episode matched an independent replay exactly and the unchanged contract resumed from the previous checkpoint. The raw audit subsequently verified all episode hashes, identities, metrics and feature summaries.

**Selection:** the prospective equal-weight score across all 20 main size/rule combinations selected generic delta eta=.01, temperature=.1. This matches the fixed EXP-002 sensitivity setting independently. Confirmation blocks remain untouched.

**Development findings:** with proportional sparsity and full readouts, structured growth from 73 to 110 cells changed early reversal by +.024 (descriptive 95% interval [.007,.040]) and post-interference retention by +.024 [.011,.038], without a clear acquisition loss. Uniform growth was comparable. Structured minus degree-null reversal at 110 was only +.002 [-.014,.019], providing no development basis for the structured prior's +.05 target. Fixed-four sparsity changed structured reversal by -.015 [-.044,.009] and retention by -.060 [-.089,-.027], showing that extra active units matter. With a fixed 32-feature readout, structured retention changed +.069 [.007,.137] but reversal remained imprecise at +.008 [-.024,.042]. At N110, 32.8% of structured added cells were unused versus 37.1% for clones, and cell covariance participation rank was 20.52 versus 17.20.

**Evidence and limits:** [result report](experiments/EXP-003-development-results.md), [run record](research/runs/EXP-003-development.json), [protocol](experiments/EXP-003-development-protocol.md). The blocks both selected and evaluated the setting; all intervals are descriptive. No H3, biological-superiority, adult-circuit or evolutionary result is claimed.

**Decision:** freeze eta=.01/T=.1 for held-out confirmation and preserve every control. Test the modest scale signal; do not prefer structured over uniform or degree-null wiring. The development result also satisfies the M2 technical prerequisite for a later bounded lineage pilot, without replacing confirmation as the immediate experimental step.

## 2026-09-12 - EXP-003 controlled growth validation (R03)

**Request:** continue with controlled growth validation and track added-cell participation and useful representations.

**Completed:** separate exp003 package preserves frozen EXP-002 code. Clone, stratum-conditioned resampling, uniform resampling and degree-matched null growth reconstruct from explicit donor lineage. Variable-size assay adapter reuses paired validation inputs; fixed-four sparsity and 32-feature readout controls are implemented. All 29 combined tests passed, including 300 graph invariant checks, exact N=73 traces, scalar learning agreement, frozen probes and checkpoint recovery around phase transitions. Nulls reached ten successful swaps per added edge. No development or confirmation blocks were run.

**Measured diagnostics:** one validation block, 20 episodes, three nested graph replicates; baseline reused once. At N=110 proportional sparsity, structured added cells were 33.3% unused and covariance participation rank was 20.07, versus native rank 16.43 in this block. Uniform and degree-null growth also yielded diverse activity; cloning added no distinct normalized input columns. Fixed-four sparsity left 52.3% of structured added cells unused. These are representation diagnostics, not demonstrated learning gains or biological advantage. Native inactivity of 45.2% in this block differs from the prior twenty-confirmation-block mean of 38.8% because the task samples differ.

**Evidence:** [R03 results](experiments/EXP-003-validation-results.md), [record](research/exp003_validation.json), [contract](experiments/EXP-003-validation-protocol.md). Full run 187.2 seconds, peak process memory 133.9 MiB, 3.95 MiB retained. Separate audit verified 61 artifacts and recomputed all 58 diagnostic rows. All baseline code/artifact hashes remain intact. No commits or pushes performed in this validation session.

**Next:** freeze fresh EXP-003 development seeds, shared eta/T selection and campaign recovery; implement the optional full-native uniform-replacement comparator before including it. Test learning benefit with sparsity/readout controls, then freeze untouched confirmation. Do not rank growth rules by this single validation block. Evolution remains the bounded B5 branch under the existing roadmap.

## 2026-09-12 — Validated and measured learning baseline

**Request:** execute the immediate validated, measured learning-baseline milestone. D022 extends the previous bounded-only scope to development and conditional frozen confirmation; the separate colleague-PC pilot remains skipped.

**Validation:** downloaded official portable GNU Octave 11.3.0 into the ignored cache and executed the source-preserving author fixture. All 256 supplied updates agreed within 6.66e-16 (tolerance 1e-10), closing R02 by author-runtime comparison. This is equation-level validation, not published biological-finding reproduction. The full suite passed 21 tests, covering original equations/data/toys and new batched/scalar trajectories, probes, stage separation, episode/block recovery and corruption detection.

**Implementation and protocol:** added a batched CPU runner that shares only exogenous task inputs across configurations, permits chosen-action updates only, resets weights between episodes and retains independent frozen probes. Prospective protocol 1.1 fixed episode streams, direct-PN normalization, pre-return retention selection, configuration freezing and bounded recovery. New scalar traces are compressed per episode, with atomic digest-checked checkpoints, graph/source/config hashes, resource counters and a complete local artifact manifest.

**Measured results:** ten development blocks selected native delta (eta 0.01, temperature 0.1) for structural follow-up. Twenty confirmation blocks, 400 task episodes per setting, passed the acquisition/headroom criterion. Native delta acquisition 0.9748 [0.9715,0.9781], early reversal 0.7428 [0.7215,0.7647], post-interference retention 0.9162 [0.8907,0.9394]; intervals are 95% block bootstrap. Feedback minus reward-only reversal +0.7207 [0.6819,0.7593] at 98.33% supports H2's narrow primary contrast, but acquisition noninferiority fails and retention is worse on average. Feedback/delta equivalence is not established. No episodes excluded and no numerical failures occurred.

**Diagnostics and resources:** average 38.8% of native features never activated per block under these synthetic cues; mean feature covariance participation rank 18.18. This is not biological inactivity. Development used 2,764,800 learning updates and 89.49 active wall seconds; confirmation used 1,075,200 updates and 162.83 seconds. Peak working set below 88 MiB. Batched current-session timings are not per-rule comparisons or colleague-machine benchmarks. Matplotlib plots were visually inspected. Runtime and plotting dependencies remain local ignored caches; compact records/plots are versionable, raw NPZ traces remain local with hashes. Nothing was pushed in this session.

**Evidence:** [Results](experiments/EXP-002-baseline-results.md), [run record](research/runs/EXP-002-baseline.json), [R02 execution](research/exp002_r02_runtime.json), [tests](research/exp002_baseline_validation.json). Original bounded-validation report remains historical; current evidence is separate. Original briefs and upstream source bytes are unchanged.

**Final audit:** verified all 600 retained episode archives against checkpoint hashes, recomputed block metrics from the stored traces, checked frozen-control probabilities and finite outputs, and retained the frozen validation evidence. All 670 campaign artifacts are indexed (128,554,775 bytes). Offline record, source/hash and local-link integrity checks passed. Continuation after the user's token-limit message resumed these final checks without rerunning development or confirmation.

**Next concrete action:** validate R03 growth algorithms and variable-size assay reuse for EXP-003 using validation data. Retain generic delta from development selection and participation/sparsity controls; EXP-003 must use its own fresh development and confirmation, without tuning on the completed EXP-002 confirmation outcomes.

## 2026-09-11 — Mission alignment and selected course

**Request:** user delegated the choice of course after comparing the project with the ambition of evolving a more capable fly-derived digital nervous system, while asking to retain alternative ideas.

**Decision:** keep evolution within this project as an integrated exploratory B5 branch. Prioritize R02 and EXP-002 assay adequacy, then controlled structural interventions with EXP-003 as the default. Review a small lineage pilot at M2/M3 once the learner, assay and at least one structural operator are validated. Whole-body or adult simulation and a positive biological-advantage result are not prerequisites for that review. Preserve alternative branches and revise priorities on evidence.

**Records:** updated charter, README, roadmap, branch portfolio and D021. The roadmap now describes ancestry/replay, budget-matched search controls, held-out evaluation and an eventual runnable scientific artifact. The pilot remains a planning outline requiring a frozen experiment specification before execution. Existing experiment protocols and validation status are unchanged; no scientific campaign or new literature review ran in this session.

**Next concrete action:** resolve R02 through independent equation review or prepared author-runtime comparison, then implement development-only assay adequacy evaluation. Use that evidence to decide whether the present representation is suitable for structural experiments.

## 2026-09-11 — Private GitHub repository and DDR5 correction

**Request:** create a private GitHub repository, commit and push all project progress, retain this exact working folder, and add no assistant contributor. User corrected the target RAM from DDR4 to DDR5.

**Work:** created [T-Julsgaard/Neural-Scaling-of-the-Drosophila-Connectome](https://github.com/T-Julsgaard/Neural-Scaling-of-the-Drosophila-Connectome) and verified private visibility before uploading files. The existing repository and history remain in the original working directory. The publication snapshot adds all cached research sources and current generated validation artifacts; local `.venv` dependencies and Python bytecode remain excluded. Original source/artifact bytes are protected from Git newline conversion. Eight pinned upstream license notices are preserved with their sources, including the GPL notice beside the generated Bennett wrapper. Existing commits use only the user's identity and contain no assistant co-author trailers.

**Records:** corrected current hardware statements to user-confirmed 64 GB DDR5 while preserving the historical typo/correction trail. No target-machine inspection or benchmark occurred. Reran all 13 bounded validation tests successfully after updating the source-packaging helper; no development or confirmation campaign ran. [Source license provenance](research/source_license_manifest.json) and [source/artifact snapshot](research/project_snapshot.json) document the included material.

**Next concrete action:** after verifying the pushed commit and complete remote file tree, return to R02's independent-review/author-runtime gate. The measured workstation pilot remains skipped.

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


## Public research release preparation — 2026-09-21

The author requested committing and publishing the complete project, with the academic report as the primary entry point. The root README now leads with the report and supplement, while RESEARCH_HISTORY.md preserves its prior status narrative. REPRODUCIBILITY.md distinguishes publication rebuilding, original-evidence verification and scientific replay. All Git-ignored saved NPZ result arrays are packaged as checksummed release assets; machine runtimes and disposable caches remain excluded. CITATION.cff and RIGHTS.md clarify citation and existing source terms without inventing a blanket license. No scientific campaign, sample, selection or manuscript finding was changed for this release.
