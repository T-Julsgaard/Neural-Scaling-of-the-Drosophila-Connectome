# EXP-006: original persistent-memory benchmark design

Status update 2026-09-14: executed and audited under the [final frozen protocol](EXP-006-protocol.md). See [results](EXP-006-results.md). The prospective design below is retained as history.

2026-09-13 prospective design; final confirmation protocol and sample are not frozen. Build after EXP-005. No memory-load results have been inspected.

Train sequential cue pairs with independently assigned preferences and chosen-action stochastic reward. Retain weights across every pair in a sequence. Probe all learned pairs without feedback or updates after each training block. Reset only between independent sequences. Cross 2/4/8/16 pairs with prototype intersection 2/6 of ten active inputs (40 inputs total); enforce the intended overlaps explicitly and report all pairwise overlaps, including across memories. Use separate development and confirmation roots.

Run both 128 presentations per pair and 512 total presentations divided equally among pairs as separately labelled exposure regimes. Probe at noise .1 and .3; reverse a prespecified subset after learning and probe both reversed and unchanged pairs. Report new learning, forgetting by memory age, mean/worst-pair retention, reversal and noise tolerance. Candidate capacity definition: largest tested load with lower confidence bound above .8 average retention and adequate new learning; validate and freeze this definition and its precision plan before confirmation. No interpolation beyond tested loads.

Compare native N73 K4/K6 (carry forward EXP-005 tuning candidates, retune fairly on this benchmark), direct-PN delta (80 learned weights), and N73 randomized sparse projection (146 weights). Randomization must preserve native per-cell contact multiset and PN/KC binary degrees with audited mixing; use several independently randomized circuits within each task block and average before inference. Give every model identical observations, potential rewards, reward access and equal development search budget. Account for learned parameters, encoding operations and training exposure. A cue-identity oracle is a task validation control only.

Validate no resets between memories, no learning during probes, cue overlap and labels, exposure accounting, paired streams, scalar/batch equivalence and replay. Choose bounded final grid, search budget, new-learning guardrail, block count, primary load/similarity contrasts and multiplicity before generating confirmation. Use EXP-005's findings to formulate predictions, not as benchmark results.

Gate: if existing-cell participation limits useful capacity, test frozen development-calibrated threshold/gain homeostasis against global tuning and shuffled calibration. If collisions predict failure, consider targeted rewiring. Test growth only when additional features plausibly address a demonstrated limit. Transfer a specific frozen prediction to another circuit afterward.
