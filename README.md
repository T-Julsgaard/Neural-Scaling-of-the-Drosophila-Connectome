# Neural Scaling of the Drosophila Connectome

**Research foundation • 11 September 2026 • no scientific experiments run.**

We investigate which changes to a Drosophila-derived neural system improve computational or adaptive capabilities, and whether biological organization gives an advantage over suitable alternatives. The foundation contains a dated research synthesis, a 70-source bibliography, source/data audits, competing branches, and three detailed experiment handoffs. It does not contain a simulator or experimental results.

Start with [STATE_OF_ART.md](STATE_OF_ART.md) for the evidence and [RESEARCH_BRANCHES.md](RESEARCH_BRANCHES.md) for the resulting choices. The recommended next milestone is validation for [EXP-002: fixed-wiring adaptation](experiments/EXP-002.md). [EXP-001: intrinsic capacity](experiments/EXP-001.md) is an independent alternative. [EXP-003: structured growth](experiments/EXP-003.md) reuses the validated learning assay.

```mermaid
flowchart LR
    A[Verified research foundation] --> B[Selected reproduction and pilot]
    B --> C[Reusable experimental pipeline]
    C --> D[Controlled growth or alternative branch]
    D --> E[Adult and cross-dataset validation]
    E --> F[Justified larger or embodied experiments]
    B --> G[Revise or stop with evidence]
    D --> G
```

## Authoritative records

| Purpose | Record |
|---|---|
| Scientific purpose and working principles | [PROJECT_CHARTER](PROJECT_CHARTER.md) |
| Six-area synthesis and open research map | [STATE_OF_ART](STATE_OF_ART.md) |
| Claim status and counterevidence | [CLAIMS_LEDGER](CLAIMS_LEDGER.md) |
| Data versions, access, filters and limitations | [DATA_PROVENANCE](DATA_PROVENANCE.md) |
| Software commits, licenses, readiness | [SOFTWARE_AUDIT](SOFTWARE_AUDIT.md) |
| Competing hypotheses and ranking | [RESEARCH_BRANCHES](RESEARCH_BRANCHES.md), [NOVEL_IDEAS](NOVEL_IDEAS.md) |
| Experiment status and handoffs | [EXPERIMENTS](EXPERIMENTS.md), [BENCHMARK_SPEC](BENCHMARK_SPEC.md) |
| Published-work validation status | [REPRODUCTIONS](REPRODUCTIONS.md) |
| Failures and null-result attribution | [FAILED_PATHS](FAILED_PATHS.md) |
| Decisions, gaps and next actions | [DECISIONS](DECISIONS.md), [OPEN_QUESTIONS](OPEN_QUESTIONS.md), [ROADMAP](ROADMAP.md) |
| Session continuity | [RESEARCH_LOG](RESEARCH_LOG.md) |
| Source discovery and original-brief audit | [SEARCH_LOG](research/SEARCH_LOG.md), [BRIEF_AUDIT](research/BRIEF_AUDIT.md) |
| Bibliographic database | [Readable bibliography](research/BIBLIOGRAPHY.md), [JSON](research/references.json), [BibTeX](research/references.bib) |

The original [initial prompt](<Initial Research Prompt for Astra — Scaling the Drosophila Connectome.md>) and [master brief](ASTRA_MASTER_RESEARCH_BRIEF.md.md) are preserved unchanged. Their instructions are source material; the user's approved plan governs this work. Original hashes are in the brief audit.

## What is established, and what remains open

The source inspection pinned 11 repository commits and checked small data inputs. It found a real provider-version mismatch, incompatible current simulator dependencies, and indexing/young-cell issues in the larval supplement. These have changed the handoffs. The bibliography records actual read depth; full methods were not available for every source. Some adult export licenses/access details, recent preprint claims and code trees remain unresolved and are explicitly provisional.

The learning/growth handoffs use a 73-mature-KC larval-derived feature circuit with two synthetic output units. The capacity handoff uses a tiny tiled visual graph. Their limits are deliberate: neither directly tests adult whole-brain scaling. A later adult/cross-dataset validation is required before that interpretation.

The target is the user's separate 64 GB workstation. Its exact GPU/VRAM, storage and software environment are not yet verified. Resource estimates in the specs are analytical envelopes; no timings or performance outcomes have been measured. All three candidates are CPU-first and require a measured validation block before scheduling.

## Session protocol

At start, read this page, ROADMAP, DECISIONS, OPEN_QUESTIONS and the latest RESEARCH_LOG entry. Follow links to the affected claim, branch, source or experiment. At end, update only the authoritative records affected, document substantive changes and record one concrete next action. Never convert a proposed experiment into a historical result or silently replace pinned inputs.

## Audit tools

With Python available, run `python tools/validate_foundation.py` for offline record/link/hash checks. `python tools/inspect_reference_data.py` additionally requires the ignored source cache, recoverable by the bounded public download tools. `audit_public_sources.py` and `audit_research_assets.py` require public network access and inspect upstream material without executing it. `refresh_bibliography.py` verifies DOI metadata and regenerates readable/BibTeX views. These are research-record tools, not an experimental platform.

On the actual Windows experiment workstation, [collect_target_hardware.ps1](tools/collect_target_hardware.ps1) can capture CPU/RAM/GPU/VRAM, disk space and basic software information. It has not been run on the target; its output still requires identifying the machine as the intended workstation.

## Foundation acceptance record

| Criterion | Evidence / status |
|---|---|
| Consequential statements traceable or explicitly unresolved |34 claim propositions; semantic recovery of master references; source IDs and read depths |
| Six areas synthesized and competing branches examined | STATE_OF_ART; six branches with counterarguments and inexpensive falsification |
| Dataset/software candidates audited | Pin/access/limits registers;11 commits; small input checks; provisional adult fields visibly unresolved |
| Three implementer handoffs with two distinct approaches | EXP-001/002/003; common statistical/task contract and resource assumptions |
| Work reconstructable across sessions | Canonical records, bibliography, original hashes, audit scripts, local Git |
| Evidence-based progression and stop conditions | ROADMAP and per-experiment decision rules |
| Search stopping condition | Two post-revision targeted rounds without shortlist-changing evidence; scope and gaps documented |

The research foundation is ready for selection of a reproduction/pilot. Its open questions are explicit handoff limits, not completed experiments or a guarantee of originality.
