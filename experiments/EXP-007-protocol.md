# EXP-007 prospective protocol: balanced participation

2026-09-14, version 1.0. User authorized implementation, development and fresh confirmation of priority 3. Historical EXP-002–006 code/results remain unchanged. This protocol precedes development and confirmation task generation and rewarded selection.

## Task and intervention

Copy EXP-006 task/learner mechanics into namespace 7007: loads2/4/8/16, overlaps2/6, 128 presentations per pair or 512 total, noise .1/.3, persistent weights, reversal of alternating pairs, all-memory probes. Reset only between complete sequences. Paired observations, potential rewards and choice uniforms, with realized feedback determined by chosen actions. Main hard condition: load16, overlap6, 128 per pair, final retention at noise .1.

N73, full146-weight opponent delta readout, initial weights .1. Per-cue top-K outputs have total activity10 and squared norm100/K. Score z=uP-theta before winner selection. Native anatomical projection fixed. One fixed priority permutation, independent of task streams. Three null anatomies preserve binary PN/KC degrees and KC contact multisets using EXP-006's 40 accepted switches/edge. These anatomies and calibrations are prepared once and frozen before development; inference is conditional on these four anatomies, not across random-anatomy populations.

Unlabeled calibration pool: 64 independent cores for each overlap, each with 16 pairs and noise .1 (4096 observations); separate calibration-validation pool with the same construction, distinct namespace. No labels, rewards, task-specific evaluation cores or confirmation inputs enter fitting. Baseline participation p0 from fit pool. Targets (1-lambda)*p0+lambda*K/N, lambda=.25 or .5 at K6. Bound=.25 times median positive drive SD. 100 batch steps, step size .5 times that SD. Project each update onto zero-mean box [-bound,bound] by bisection. Fixed iteration budget, no reward-dependent fit stopping. Record imbalance, clamp fraction, clean/noisy rank margins and calibration-validation participation. K4 offsets remain zero. Three independently shuffled copies of each native offset vector; average sham replicas within blocks. Offset permutation does not preserve achieved participation and cannot uniquely identify mediation.

## Equal total development budgets

Eight main learning rates: (.01/3)*2**j for j=-4,-3,-2,-1,0,1, plus .01,.015. This extends 16-fold below EXP-006's lower boundary. Temperatures .1,.2. All adaptive experimental methods receive exactly32 rewarded candidate evaluations per development task:

- Ordinary native: K4/K6 x eight rates x two temperatures.
- Homeostasis: K6 x lambda .25/.5 x eight rates x two temperatures.
- Shuffled: same32 candidates as homeostasis; three fixed permutations averaged before selecting.
- Random ordinary: K4/K6 x eight rates x two temperatures, averaged over three fixed null anatomies.
- Random homeostasis: K6 x lambda .25/.5 x eight rates x two temperatures, averaged over the same nulls.
- Direct: 16 geometric rates from (.01/3)/16 through .015, each at two temperatures.

Oracle gets the direct grid for pipeline validation only. The native uncalibrated K6 reference is the best of the16 K6 candidates already inside ordinary search, not another search. Fixed-setting homeostasis and sham reuse selected lambda with this K6 reference's eta/T; they get no extra selection. No condition-specific settings. Selection maximizes equal-weight mean of retention, new learning, noisy retention, reversed-pair and unchanged-pair retention across all16 development conditions and eight development blocks, tie tolerance1e-12 picks earliest. Tail outcomes are reported and guarded in confirmation, not additional selection criteria.

Primary comparisons: tuned homeostasis minus (1) contemporary tuned K6 reference, (2) equal-budget ordinary K4/K6, (3) equal-budget shuffled calibration, on hard-condition mean retention. Fixed-setting comparisons are descriptive and separate intervention from tuning. Calibration itself adds73 fitted values (72 independent) and unsupervised exposure; report those resources. No online adaptation, gain sweep, growth, or new anatomy transfer in this experiment.

## Confirmation and inference

Eight development blocks100–107. After completed audited development, choose confirmation size solely by precision: max paired SD of the three primary contrasts, multiplied by1.25; n=ceil((2.40*inflatedSD/.025)**2), rounded up to a multiple of8, bounded24–64. Record uncapped recommendation and achieved projected precision; resource cap can leave uncertainty. No effect-size or significance-based sample extension. Freeze selected candidates, n, source/runtime/calibration hashes before confirmation generation. Fresh blocks1000 onward. Validation uses its own stage and never constructs development/confirmation fixtures.

Three primary two-sided paired block-bootstrap intervals at98.333333% (Bonferroni family alpha .05), 50,000 draws. A practically established gain requires lower bound >.03. Positive lower bound >0 establishes a directional gain only. Primary equivalence would require the entire interval within ±.03. Inferential unit is task block, averaging sham/null replicas first.

Four guardrails for homeostasis against each of the same three comparators: new learning, reversed pairs, unchanged pairs after reversal, worst-pair retention; hard condition. One-sided lower bounds with alpha .05/12 (100,000 draws). Noninferiority requires each lower bound >-.03. Do not call a nonsignificant deficit harmless. Fractions below chance and mean worst-pair profiles are also reported; tail improvement requires its own evidence. Other intervals are descriptive95%.

Capacity: simultaneously lower-bound retention and new learning >.80 at noise .1, all lower loads must pass. Seven experimental reported models x two overlaps x two regimes x four loads x two endpoints=224 checks, one-sided Bonferroni family95%, 200,000 bootstrap draws. Approximate bootstrap certification, not theoretical capacity or assurance for each individual memory.

Held-out distribution shift: after selection, additionally test load16/per-pair at both overlaps with the first20 PN channels attenuated by.5 in all training/probe/reversal observations and clean prototypes. Same labels and reward stream. No calibration refitting or selection uses this condition. This changes input statistics, not just seeds, and may reduce information; report direct/oracle controls. Shift comparisons are descriptive, not another primary success gate. No cross-circuit generalization claim.

## Instrumentation and checks

Save per-pair learning/probe histories, reversal, weight-boundary continuity hashes, final weights, clean cue cosine/collisions, noise stability, winner score gaps, presented participation, actual chosen-update participation, clipping, update norm, old-pair margin perturbations and below-chance fraction. Frozen offsets ensure no representational drift. Input/label/task digests paired across all arms. Correct-choice probability, not realized reward rate, is the endpoint.

Preflight: independent scalar update/sequence reference, zero-offset equivalence to EXP-006 encoding/learning, fixed-K/norm and global-offset invariance, calibration bounds/direction/sham multiset, independent streams, shift transformation, persistent boundaries and read-only probes, metric definitions, random graph invariants, oracle adequacy, reproducibility. Entire validation block exact replay before development; every checkpoint audited/recomputed and one entire development/confirmation block replayed. Source/runtime drift fails closed. Atomic checkpoints and checksums support resume. Stop on nonfinite state, validation failure, >2GB outputs or resource failure; no performance exclusions. Local CPU only, maximum three workers; measure runtime and memory before launching. Preserve failed attempts and protocol amendments. Report uncertainty and negative results without further tuning.
