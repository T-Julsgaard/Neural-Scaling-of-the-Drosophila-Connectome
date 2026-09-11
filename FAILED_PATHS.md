# Failed paths and negative results

Updated 2026-09-11. **There are no internally completed or failed scientific experiments.** Example experiment EXP-0047 in the master brief is illustrative text, not a result from this project.

## Research-access and validation issues actually observed

| Record | Observation | Classification / resolution | Scientific implication |
|---|---|---|---|
| A01 | Anonymous Codex download requests returned HTML sign-in pages | Data-access issue; marked invalid manifests in asset audit; archive/provider paths retained | No evidence about dataset quality or a neural hypothesis |
| A02 | GitHub tree requests for Xie/NeuroGym hit rate limits | Partial source audit; commits/metadata retained, tree readiness unresolved | No failed reproduction |
| A03 | Full-text retrieval of recent S25/S26/S53 preprints failed | Indexed excerpt/metadata only; methods claims unresolved | These sources cannot support strong causal or numerical conclusions here |
| A04 | Initial assumption of globally aligned supplementary-matrix row/column order failed | Static validation caught14 mismatched labels; selected PN/KC subset alignment explicitly checked | Requires axis-aware loading. No experiment was invalidated because none ran |
| A05 | Public HTTP requests were blocked in the default shell network sandbox | Read-only public-source audit succeeded using authorized escalation | Environment access condition, not a scientific failure |
| A06 | No MATLAB/Octave runtime found on PATH or in the common installation directories inspected | Runtime availability issue; deterministic author wrapper prepared, scalar Decimal and analytic checks passed. Independent review or author execution still needed for R02 | Not a failed Bennett reproduction; no author runtime ran |
| A07 | Initial EXP-002 loader failed on the source CSV newline convention | Implementation defect caught before data tests; explicitly set `newline=""` as in the original audit and reran the suite successfully | No scientific run or hypothesis outcome was invalidated |

## Future negative-result template

Record ID; linked experiment/run/config; intended hypothesis; actual observations with uncertainty; whether validation passed; implementation alternatives ruled out; scientific interpretation and limits; resources spent; decision; conditions to revisit. A null organization effect can coexist with a positive scale effect. Preserve parameter-dependent failures rather than selecting a favorable regime without disclosure.

External negative evidence is synthesized in [STATE_OF_ART.md](STATE_OF_ART.md) and [CLAIMS_LEDGER.md](CLAIMS_LEDGER.md). Deferred ideas belong in [RESEARCH_BRANCHES.md](RESEARCH_BRANCHES.md), not in an invented history of failed runs.
