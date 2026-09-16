# Data provenance and access audit

## EXP-011 synthetic task provenance — 2026-09-15

Fresh root-11011 stage-separated synthetic compound-task streams; no new anatomical data. Reuses the hashed EXP-007 calibration archive and the three fixed randomized projections used by B. No evaluation-specific calibration. Inputs, labels, channel permutations and schedule indices are locally archived under results/exp011. [Protocol](experiments/EXP-011-protocol.md).

## Session A source bundle — 2026-09-15

[Source audit](research/SESSION_A_SOURCE_AUDIT.md) pins Abdelrahman et al. repository commit 9f3f7e9e85117febef1ad32e3152c830570f74d3, supplied fitted MAT instance, Hallem-Olsen PN table, MATLAB methods/noise/evaluator, published PDF, SI and Dataset S1. [Hash manifest](research/exp009_source_audit.json). GPL license and original bytes retained. One supplied calibrated instance is conditioning information, not a newly sampled animal. Saved labels are not reused for new learning. New prototype/noise/label streams and training-only scaling are declared in EXP-009. Source code says 4.5x while saved weights are 5x; no silent correction.

## 2026-09-14 adult execution input

D08 is now pinned for EXP-008: hemibrain:v1.1 exported traced adjacency archive, primary ROI CA(R), positive contacts from the author monoglomerular PN ID list to type KCg-m. The [anatomy manifest](results/exp008_anatomy/record.json) records source hashes, annotation commit, all IDs/exclusions, terms and normalization. 104 PNs, 590 KCs, 4,878 edges, 85,151 contacts. Every selected ROI count was checked against its total-neuron-pair count. The underlying [adult study](https://elifesciences.org/articles/62576#data-availability) states CC-BY; its [archive record](https://api.figshare.com/v2/articles/12818645) specifies CC BY 4.0. PN annotation repository is GPL-3.0; retain both attributions. The downloaded positional KC exclusion file is not applied without its original ID ordering. Source non-cropped traced filtering and residual completeness limits are explicit. Raw archive stays local; this is an adult subcircuit, not all adult MB inputs. Earlier dated audit below is historical.

Checked **2026-09-11**. Publication access, metadata access, file download, schema inspection, and experimental use are separate states. No dataset has been used in a completed experiment. Public availability does not imply an unrestricted license.

## Candidate register

| ID / provider | Release and access | Data meaning / constraints | Rights and readiness |
|---|---|---|---|
| D01 FlyWire / Princeton / consortium | FAFB v783 listed by [Codex](https://codex.flywire.ai/faq); connectivity archive [Zenodo 10676866](https://zenodo.org/records/10676866); [annotations](https://github.com/flyconnectome/flywire_annotations) separately pinned | Adult female brain; aggregate neuron-pair connectivity differs from individual synapse tables; snapshot, proofreading and edge thresholds must accompany every export | Archive landing page verified; bulk data not downloaded. Record license from the selected archive file/release before redistribution. Annotation repo API did not identify a license. Later adult validation candidate |
| D02 FlyWire publication reproduction | v630 in [Shiu source](https://github.com/philshiu/Drosophila_brain_model); v783 alternative explicitly supported | Reproduction must use original v630 configuration and matching completeness table; changing to v783 is a port | Source inspected, data not downloaded; license of code is MIT, not a blanket data license |
| D03 BANC / consortium | v888 in [Codex FAQ](https://codex.flywire.ai/faq); publication archive [10.7910/DVN/7WTH1N](https://doi.org/10.7910/DVN/7WTH1N) referenced by [paper](https://www.nature.com/articles/s41586-026-10735-w) | Brain and cord; missing visual structures and damaged sensory inputs limit whole-animal claims; circuit completeness is local | Publication and provider description verified; archive access path taken from paper, bulk export/license not verified. Deferred, not handoff input |
| D04 Janelia MaleCNS | [Project](https://male-cns.janelia.org/) advertises v1.0; [downloads](https://male-cns.janelia.org/download/) | Distinct from Codex's MCNS v0.9. Provider-specific counts/thresholds cannot be merged | Release/access documentation verified; exact downloadable objects, hashes and per-file license must be captured before use. Cross-animal candidate |
| D05 Eichler larval MB | [2017 supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnature23455/MediaObjects/41586_2017_BFnature23455_MOESM3_ESM.zip), Supplementary Table 1 | 387×387 integer matrix, presynaptic rows / postsynaptic columns; aggregate contact counts. Selected 40 PN and 73 mature KC left projection; no threshold beyond positive count | Download and schema checked; publisher supplement associated with [open-access paper](https://www.nature.com/articles/nature23455). Preserve attribution and verify any third-party exception before redistributing raw data. Only hashes/derived index manifest committed |
| D06 TuragaLab flyvis | `fib25-fib19_v2.2.json` at commit in [software audit](SOFTWARE_AUDIT.md) | Consensus local visual wiring, tiled by code. Offsets, cell types and fractional synapse estimates; not an individual whole-brain export | Downloaded/schema inspected; MIT repository. Primary EXP-001 input, cite originating paper and code |
| D07 NT prediction / ground truth | [Eckstein paper](https://www.sciencedirect.com/science/article/pii/S0092867424003076), [ground-truth repo](https://github.com/flyconnectome/drosophila_neurotransmitters) at pinned commit | Ground truth, predictions, receptor expression and effective sign are different fields; type/cell mapping may be uncertain | Repository CC-BY-4.0 metadata verified. Coverage, confidence and release must be retained with predictions |
| D08 adult MB hemibrain | [Li et al.](https://elifesciences.org/articles/62576) and its data availability / neuPrint route | Adult MB with compartment and feedback organization; valuable independent adult validation; not a larval substitute | Paper inspected; exact graph export/release and licensing remain selection-stage checks; not execution-ready input |

Broader brain, cord and organism comparisons are literature leads rather than silently added datasets. No bulk adult download was required for this milestone. D05/D06 are the execution shortlist; unresolved access/licensing fields keep D01–D04/D08 provisional.

## Concrete findings from file inspection

The machine-readable [reference audit](research/reference_data_audit.json) is authoritative for D05 indices and counts. CSV SHA256: `b9d06b052b0c4b91a7221b3dde9552b670bb81c034d0d3ed7fdb5e4a3b2cfc4b`.

- Header-excluded indices are zero-based. Duplicate KC display labels must never be dictionary keys.
- Fourteen row/column labels differ at the same position outside the selected PN/KC/MBON subsets. Do not assume global positional identity or infer a full-network adjacency without reconciling them.
- All 40 selected PN and 110 left KC indices align between axes. Of 110 KCs, 37 are labelled young; 27 have zero input from this selected PN set. Every one of the 73 mature KCs has positive input.
- The 40×110 projection has **386 nonzero aggregated edges and 2,215 anatomical contacts**. These are different quantities. Mature-subset totals are recorded separately in JSON.
- The selected 40×73 mature projection has **365 aggregated edges and 2,188 contacts**. Learning-rule normalization changes weights, not those raw provenance counts.
- Nineteen left MBON columns have some left-KC input in the unthresholded supplement. That does not automatically reproduce Xie's 18 selected modeled outputs. EXP-002/003 use two explicitly synthetic valence units, avoiding an invented correspondence.

The two attempted anonymous Codex download API calls returned HTML sign-in responses despite `.json` cache names. The [asset audit](research/asset_audit.json) marks them `invalid_manifest_html_response` and unusable as manifests. A successful HTTP response is not verified data access. Use documented archives or authenticated provider exports later.

## Mandatory transformation record

Every future run must store source URL, access date, provider version, annotation commit, source SHA256, code commit, subset IDs, axis convention, excluded nodes, self-edge policy, duplicate-edge aggregation, thresholds, sign assignment, and missing-value handling. Keep raw contact totals alongside normalized weights. An edge is a distinct ordered neuron pair; a synapse/contact is a reconstructed event counted within that pair. D06 estimated counts are not necessarily integers.

For EXP-001 retain positive estimated-count offsets and source-provided edge signs, use `extent=1`, and **disable gap filling** (`n_syn_fill=0`). Tiling and boundary truncation are explicit modeling choices. For EXP-002/003 use `KC_mature_left` and `PN_left` from the pinned manifest; exclude young KCs before model construction; preserve positive counts without further filtering. The specs define normalization separately.

## Rechecking

Run `tools/audit_public_sources.py` for provider metadata, `tools/audit_research_assets.py` for bounded public files, then `tools/inspect_reference_data.py` for static validation. They require Python and public-network access; no upstream code is executed. Re-audits may reveal new commits: preserve the currently selected hashes in experiment manifests and review changes before replacing them. D020 includes the existing research-source cache in the private repository at the user's request; URLs and hashes also make these inputs recoverable. This private snapshot does not change third-party source terms or resolve access/license questions for future datasets.
