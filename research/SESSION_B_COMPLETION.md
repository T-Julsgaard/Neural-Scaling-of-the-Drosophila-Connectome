# After Session B — saved gate, no Session C execution

2026-09-15. Session B / EXP-010 is complete. Read [report](../experiments/EXP-010-results.md), [selection](../results/exp010/selection.json), [analysis](../results/exp010/analysis.json) and [audit](../results/exp010/audit.json).

Offline full-outcome old-pair accuracy 96.97% versus fully supervised online 76.72%; paired difference 20.26 pp [16.46, 24.05] (95%, 24 fresh task blocks, native/calibrated average).

## Saved explanation and falsifier

Within the fixed K6 larval pair-memory regime, sequential learning loses useful old preferences although a signed linear readout can recover them from the same frozen features. Full outcome supervision alone does not close the deficit. The operational prediction was frozen and confirmed: offline old accuracy >=80%, offline-versus-full-online paired lower CI >5 pp, and online acquisition-to-final loss lower CI >5 pp. Failure of any criterion would have falsified it. Keep access, clipping, scale, replay and numerical-fitting distinctions from the report.

The later transfer hypothesis is that a distinct validated task with shared sparse features and sequential acquisition will show an offline-versus-online gap even under matched supervision. A task on which a well-fitted held-out linear readout also fails, or supervised online retains as well as offline, would count against that generalization. This is a candidate for later prospective C design, not a frozen new-task protocol and not evidence of transfer. No task family or success-favoring evaluation has been selected.

## Boundary

C is permitted by the B gate but the user explicitly deferred it. Do not start C, D, speculative expansion or another campaign from this handoff alone. If later authorized, C must first choose one distinct task family and validate learnability; do not reuse these confirmation tasks to tune it. If the user instead requests D, use the narrower familiar sequential-interference result without inventing novelty. A repair should address demonstrated update interference, with matched feedback and resource accounting; added anatomy or stronger compensation is not justified by B.

## Recovery

All 31 EXP-010 blocks are archived, source-hashed and exactly replayed. Preserve EXP-002–009 scientific artifacts and all confirmation samples. The archive contains per-update pair-margin changes, fitting coefficients, choices, stochastic outcomes, noise probes, contracts, selection, regularizers and resource records. Raw NPZ files are locally retained and Git-ignored; compact records are versionable. Source freeze predates stages and prediction freeze predates confirmation. No external publication or push occurred.
