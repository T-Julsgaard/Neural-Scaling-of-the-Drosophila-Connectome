# Next research sessions: explanation and paper decision

## Execution status — 2026-09-16

**Sessions A–D complete.** D selected a [narrow empirical report](EMPIRICAL_REPORT_DRAFT.md); see [assessment and claim table](SESSION_D_ASSESSMENT.md), [literature audit](SESSION_D_LITERATURE_AUDIT.md) and [figure plan](SESSION_D_FIGURE_PLAN.md). C passes its numerical prediction, with limited transfer and familiar explanation. No complete causal compensation bridge or major discovery is established. No new campaign. Next, if pursued: figure/artifact preparation and scientific review. Submission/publication/push remain unauthorized. This supersedes older execution-status text; the original plan is preserved.

## Execution status — 2026-09-15

Sessions A, B and C are complete. [C report](../experiments/EXP-011-results.md); [D handoff](SESSION_D_HANDOFF.md). The original plan below is retained. D has not started; no publication is authorized.

2026-09-14. User-requested plan following [the paper assessment](PAPER_ASSESSMENT_2026-09-14.md). The original priorities 1–4 remain complete. The new milestones are **A–D**, to avoid reusing those numbers. This document specifies future work; creating it does not launch experiments or create tasks.

## Recommendation on prompts

Use four sequential prompts, one per milestone, in the same project. They can be follow-up messages in the same conversation. Each execution prompt below requests the complete milestone, including necessary protocol, implementation, development, conditional fresh confirmation, audit and reporting. Do not stop merely to ask whether the user wanted a protocol or execution: the pasted execution prompt answers that.

The split is a research decision: later choices depend on earlier evidence. It is not a claim that one long task is technically impossible. One master prompt could execute the same gates, but separate milestone conclusions make changes of direction easier to inspect. Do not launch all four concurrently.

Plan for four main milestones and, if needed, one additional session to complete a difficult reproduction or mechanism implementation. These are work packages, not guaranteed token, wall-time or discovery budgets. A milestone may need a continuation after an interruption. Resume verified checkpoints rather than restarting or replacing an evaluation sample.

Official prompting guidance was consulted for autonomous follow-through and explicit constraints: [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model). The scientific sequence and recommendation to split into four prompts are project-specific judgments, not an OpenAI requirement.

## The question this sequence should answer

**Why did partial participation calibration fail to improve our memory benchmark, and can that explanation predict another result?**

Candidate explanations remain open: baseline normalization already supplies useful compensation; bounded offsets change recruitment too little or sacrifice stability; information is difficult to recover from the sparse features; or the online learner overwrites otherwise usable information. Multiple causes may coexist. The sequence must allow the conclusion that the current result is a limited consequence of an established model property.

## Common execution contract for A–C

- Read the current README, roadmap, decisions, open questions, latest research log, this plan and relevant previous session conclusions. Inspect actual reports/code; do not rely on conversation summaries alone. Allocate new experiment/run IDs only after checking existing records.
- Preserve EXP-002–008 and any later frozen results. Historical evaluation results may motivate hypotheses but are not fresh confirmation. Label exploratory reanalysis; do not pool it into new primary evidence.
- Specify the question, scope, controls, endpoint, practical margins, uncertainty unit, precision rule, resource caps and stopping conditions before new evaluation. Freeze the tested model/protocol before development as appropriate, and selected settings/sample size before confirmation. Validation fixtures must not draw confirmation inputs.
- Use fresh independent task blocks, paired inputs where valid, held-out noisy probes and no evaluation-driven selection, calibration or sample extension. Record calibration/data access, trainable/fitted parameters and computational costs.
- Use the existing CPU pipeline and recovery mechanisms where suitable. Measure a small validation workload and set numerical compute/storage caps before a campaign; no unbounded search or new infrastructure project. Local/free resources remain the default. Paid compute and publication are outside these prompts.
- Complete authorized reversible work without routine permission questions. Stop dependent work on a real unresolved source, validity or resource barrier, explain it, and finish independent analysis. Do not make a positive outcome a condition for honestly completing a study.
- Close each milestone with one report containing findings, uncertainty, the gate decision, actual resources, artifact locations and an exact next handoff. Update the affected authoritative records and research log. Save any interrupted state with completed run IDs, frozen settings, remaining work and the next command/action.

## Session A — Establish a trustworthy comparison with a published benefit

**Plain-language question:** Can we reproduce a situation where balancing activity helps, and identify how that situation differs from ours?

Start with Abdelrahman, Vasilaki and Lin (2021), the closest compensation precedent identified in the [homeostasis research](ACTIVITY_HOMEOSTASIS_RESEARCH_2026-09-14.md). Inspect the actual methods, equations and available author code. Select one bounded positive comparison, such as a precisely identified compensation-versus-uncompensated result from Figure 4, after determining what can be faithfully implemented. Record the specific panel, data, distributions, learning procedure and expected qualitative effect before execution.

Reproduce that comparison with pinned source/version and inspectable tests, including a comparison against author outputs or an independent numerical reference where available. Set a prospective criterion for whether the positive control is adequate; do not keep searching implementations until one happens to give the desired sign. If exact reproduction is impossible because essential source/data are unavailable, label an independently constructed positive control as such. If validation or the expected effect fails, preserve the result and diagnose the mismatch without claiming the reference has been refuted.

Create a compact difference table against our model: raw/per-cell-normalized input weights, graded versus fixed-amplitude top-K responses, compensation range/target, noise source, task structure, learning rule and training schedule. Identify at most two plausible differences for Session B. Design the comparison so a published regime and the local pipeline can be connected without changing everything at once.

**Completion:** a bounded reproduction/positive-control report, exact source/equation mapping, results and limitations, and a ranked pair of candidate explanations. This is not a reproduction of the whole paper.

**Gate:** A validated positive effect permits a controlled bridge in B. If it remains unavailable or unvalidated, B can still investigate our pipeline, but the paper must not claim to explain or overturn the published effect.

## Session B — Determine where memory is lost

**Plain-language question:** Does the model lose useful information while encoding a cue, or can it still represent the information but overwrite it during learning?

Use a bounded development diagnostic on frozen direct-input, native sparse, calibrated sparse and appropriate random representations. Compare the existing online learner with an offline fitted linear readout evaluated on held-out noisy observations. The offline model has different training access; it is an explanatory diagnostic, not a fair online competitor or a proven capacity upper bound. Match targets and training observations where possible, and explicitly control access to labels/unchosen outcomes. A matched fully supervised online condition may be needed to distinguish feedback access from batch fitting and learning schedule.

Measure clean/noisy separability, conditioning/rank where informative, and how each new update changes the preference between old cue pairs. Good offline performance with poor online performance supports a learning-procedure limitation. Poor performance for both motivates a representation/noise limitation but does not prove information is irretrievably destroyed; the readout class and fitting quality also matter. Distinguish nonnegativity/clipping constraints from feature information.

If A provides a validated positive control, vary at most two nominated factors between its regime and ours, using a small factorial when interaction is plausible. Separate changes in feature norms/effective update scale from changes in representation. Stronger compensation may be used as an explicitly nonphysiological diagnostic, with a fixed prospective range and data separation; do not describe it as proven biological homeostasis.

Use development to select one explanation and one discriminating prediction. Freeze the comparison and prediction, then run fresh bounded confirmation if the diagnostic is valid and sufficiently discriminating. Do not merely confirm a post-hoc correlation between participation and retention.

**Completion:** evidence favoring a specific cause, a mixture of causes or an unresolved limitation; a concise prediction with a possible falsifying outcome; and an audited report. Report a negative or familiar explanation without inventing novelty.

**Gate:** An informative result permits C. If B cannot supply a testable prediction or a valid diagnostic, skip speculative expansion and proceed to D with the narrower evidence; prescribe a targeted repair only if it addresses an identified problem.

## Session C — Test a prediction outside the original task

**Plain-language question:** Does our explanation work on a different learning problem?

Choose one distinct task family based on B's prediction before inspecting its evaluation outcomes. A candidate is nonlinear compound-cue discrimination: the reward depends on a combination of features, and that rule must generalize to unseen combinations or observations. Define the task so simply memorizing unique cue IDs is insufficient. Verify in development that a known capable diagnostic model can solve it, that direct-input linear performance behaves as expected, and that the tested sparse representation can express the relevant distinction. A task being nonlinear alone does not guarantee that our specific representation can solve it.

Carry over the intervention procedure, including declared rules for any permitted calibration or development tuning. Preserve a genuinely held-out task evaluation. Include ordinary tuning, direct inputs and a comparable random sparse representation. Match observations, feedback and search opportunities for performance competitors; label privileged diagnostics separately. Retain old-memory retention, new learning and harmful tradeoffs where the task permits.

State the predicted direction or conditional boundary before confirmation. A negative prediction is acceptable. Use the smallest predeclared challenge set needed to distinguish hypotheses; do not select tasks because they favor anatomical models. No new anatomy, whole-brain model, population-growth campaign or evolutionary search is needed for this milestone.

**Completion:** an audited prediction test on a distinct task family, with a pass/fail/inconclusive result and explicit scope. If the new task is uninformative, report that instead of calling it successful transfer.

## Session D — Decide what paper the evidence supports

**Plain-language question:** Have we learned something other researchers need to know, and exactly what can we claim?

Critically audit the central claim, data separation, selective reporting, comparator strength, intervention size, resource accounting and source provenance. Recheck primary literature around the actual explanation, particularly Abdelrahman's compensation work and Zou, Zang and Ji's sparse-expansion continual-learning study. Distinguish biological experiments, published computational results, preprints and our own measurements. Do not claim worldwide priority from a search that found no duplicate.

Produce a claim-to-evidence table, a figure plan and a manuscript decision:

| Outcome | Deliverable |
|---|---|
| A useful explanation survives a prospective new-task prediction and adds to prior work | Draft a focused computational manuscript, with the explanatory result central and prior experiments as support. |
| The bounded two-anatomy result remains useful but its explanation is familiar or transfer fails | Draft a narrower empirical/negative-result report, explicitly limiting novelty and scope. |
| Essential validity/novelty gaps leave insufficient scientific value | Write a candid closure/revision memo identifying the exact gap; do not manufacture a paper claim. |

A draft is a local reviewable artifact, not a journal submission or public upload. One further session is reasonable for a named repair or writing task if it has clear decision value. Do not automatically start another experiment whenever the desired story fails.

## Copy-paste execution prompts

Use the prompts one at a time, after reviewing the previous milestone's conclusion. Each references this file for the full scientific and continuity contract.

### Prompt A

> Execute Session A in research/NEXT_SESSIONS_PLAN_2026-09-14.md through its bounded reproduction or positive-control test and final report. Read the current project records first. Inspect the closest published compensation result, select one precise comparison, and carry out the necessary source audit, protocol, implementation, validation and bounded run. Identify the key differences from our model and prepare Session B's handoff. Preserve failures and distinguish exact reproduction from independent adaptation. Do not stop at a proposal or ask whether I want execution; this prompt authorizes the complete milestone using local/free resources. Stop at Session A's decision gate.

### Prompt B

> Execute Session B in research/NEXT_SESSIONS_PLAN_2026-09-14.md using Session A's saved findings. Determine whether our limitation is in the representation, the learning procedure, or both. Complete the bounded offline/online diagnostics and, where justified, the controlled bridge and fresh confirmation. Make feedback access, normalization, update scale and fitting differences explicit. Save a testable prediction for Session C, or a clear explanation of why no valid prediction is available. Follow the plan's controls and gates; complete the milestone rather than only drafting its protocol.

### Prompt C

> Execute Session C in research/NEXT_SESSIONS_PLAN_2026-09-14.md, conditional on Session B's gate. Select one distinct task family that can test the saved prediction, validate learnability, freeze the prediction and protocol, and complete development, fresh evaluation, audit and reporting. Retain strong ordinary, direct-input and random-representation baselines. Do not choose tasks from favorable evaluation results or claim transfer from new seeds alone. If the gate is not met, explain the limitation and prepare Session D's handoff rather than running an uninformative experiment.

### Prompt D

> Execute Session D in research/NEXT_SESSIONS_PLAN_2026-09-14.md. Critically review the completed evidence and closest primary literature, then decide what claim is defensible and potentially novel. Produce the claim-to-evidence table and figure plan, and write a focused manuscript draft, a narrower empirical report, or a candid closure memo as warranted. Be explicit about limitations and negative results. Do not launch another campaign or publish anything. Finish with a plain-language assessment of what we discovered and whether the paper is worth pursuing.

### If a milestone is interrupted

> Continue Session [A/B/C/D] from the saved project handoff and verified checkpoints. Preserve the frozen protocol, settings and evaluation sample. Complete only the remaining authorized work and report the milestone's decision; do not restart completed experiments.

## Success for this sequence

Success is a trustworthy explanation and a justified paper decision, including a defensible conclusion that the evidence is too narrow or familiar. Novelty is an outcome to evaluate, not a requirement the experiments must be made to satisfy.
