# Software audit

## EXP-011 validation and replay — 2026-09-15

Five tests and 31 block replays passed; 11218 arrays compared exactly and 460 historical files unchanged. Bundled NumPy CPU runtime. Automated self-audit, not independent validation. [Report](experiments/EXP-011-results.md).

## EXP-010 validation — 2026-09-15

Five tests passed; existing delta arithmetic, ridge augmented least-squares equivalence, signed/nonnegative decomposition, orthogonal learning, scale equivalence, stream/access isolation and author order invariance checked. All 31 blocks and saved arrays replay exactly; 70 historical scientific files unchanged. Bundled SciPy was absent; before any task execution, the t critical value for fixed n=24 replaced that optional dependency. [EXP-010 report](experiments/EXP-010-results.md).

## Session A selected compensation dependency — 2026-09-15

The previous deferral of Abdelrahman's repository is superseded for EXP-009 only. Pinned commit 9f3f7e9e85117febef1ad32e3152c830570f74d3, GPL-3.0 source retained, GNU Octave 11.3.0 supplied-input reference executed. NumPy implements SI Eq.3/20/21 and author noise lookup; no execution/validation of the joint calibration optimizer. [Audit](research/SESSION_A_SOURCE_AUDIT.md), [validation](results/exp009/validation.json).
Checked 2026-09-11 through public GitHub metadata and selected source inspection. Exact JSON records: [software_metadata.json](research/software_metadata.json), [asset_audit.json](research/asset_audit.json). A recent push is a maintenance signal, not a guarantee of support. Subsequent EXP-002 validation used a project venv with the installed bundled NumPy; no upstream runtime or scientific reproduction ran. [Validation environment and evidence](experiments/EXP-002-validation.md).

| Candidate | Pinned commit | License reported | Last push / inspection / decision |
|---|---|---|---|
| [flyvis](https://github.com/TuragaLab/flyvis) | `92b3845cc426dd309a1a0e1b3890156c42e14021` | MIT | 2026-08-18; README, requirements, dynamics, graph constructor and wiring inspected. Use small graph input; physiological reproduction is separate |
| [FlyGym](https://github.com/NeLy-EPFL/flygym) | `38c8ec61034cd59bc5ba0de20688d4a3c0000d60` | Apache-2.0 | 2026-08-24; README and pyproject inspected. Later embodiment |
| [Shiu model](https://github.com/philshiu/Drosophila_brain_model) | `91bdd1e7dcf193f3e7ca5a8933497fcef63b7960` | MIT | 2024-09-14; README/model inspected. Later whole-brain validation |
| [conn2res](https://github.com/netneurolab/conn2res) | `3ccb7074261c910847dcd0164b00ff3b02bade90` | BSD-3-Clause | 2024-12-20; reservoir source/README inspected. Reference implementation for capacity assay |
| [flybody](https://github.com/TuragaLab/flybody) | `d015e9bfe441bd90ae431bac24c55cb74bdbce26` | Apache-2.0 | 2026-02-07; README/pyproject inspected. Later embodiment |
| [Bennett](https://github.com/BrainsOnBoard/paper_RPEs_in_drosophila_mb) | `7ec52afb9bd7bb748d94d60dea9f483645a2ce8e` | GPL-3.0 | 2021-02-10; MATLAB learning functions/reward schedules inspected. EXP-002 mechanism validation |
| [FlyWire annotations](https://github.com/flyconnectome/flywire_annotations) | `8587524c1748ce5ef2080822a2fc890fc03bf597` | Not identified by API | 2026-07-21; README inspected. Pin independently from graph; resolve rights before redistribution |
| [NT ground truth](https://github.com/flyconnectome/drosophila_neurotransmitters) | `a9417412c8a70fcc9f80a65ca5bc6064eba07be3` | CC-BY-4.0 | 2026-06-23; README inspected. Annotation reference |
| [Topology sensitivity](https://github.com/nalin-dhiman/Connectome-Constrained-Neural-Networks) | `336e0d12a6edd92a7340cfffb71985a3879055ce` | MIT | 2026-04-07; README and canonical config inspected. Negative-control reference |
| [Xie](https://github.com/kxie2022/mushroom-body-research) | `fbcb29ac684a244c012daa3708b7f1d238542c05` | Not identified | 2024-09-01; metadata verified, tree API rate-limited. Paper methods read; implementation readiness unresolved |
| [NeuroGym](https://github.com/neurogym/neurogym) | `a32cfa759ced1edbf3d1d7b207260e45a8f8c2d9` | Apache-2.0 | 2026-03-31; documentation/partial metadata, tree rate-limited. Optional future task suite |

The two rate-limited records retain `unresolved` audit status even though their commit and repository metadata were retrieved. This must not be interpreted as a verified code tree. Costi's [ESA GitLab repository](https://gitlab.com/EuropeanSpaceAgency/fly_connectome) and Abdelrahman's [compensatory-variability repository](https://github.com/aclinlab/CompensatoryVariability) are newly identified prior-work resources; they are **not shortlisted runtime dependencies**, and release/license/runtime audits remain deferred until a reproduction of those studies is selected.

## Environment findings

- flyvis declares Python >=3.9,<3.13. Its current dynamics and graph machinery should be isolated from a lightweight NumPy reference implementation when validating equivalence.
- Current inspected FlyGym 2.1.0 declares Python >=3.12,<3.15, NumPy >=2,<3, MuJoCo >=3.9,<3.10; optional accelerated dependencies also have version bounds.
- flybody declares Python >=3.10 and NumPy ==1.26.4. These NumPy requirements conflict with current FlyGym. Use separate environments or the documented [FlyBody-model integration tutorial](https://neuromechfly.org/tutorials/5b_using_flybody_model/), not an untested combined installation.
- Shiu's Brian2 reproduction defaults to v630; the alternate v783 files are named in the source. Preserve original configuration when reproducing publication results.
- Bennett's author implementation is MATLAB; its README identifies tested historical MATLAB versions and some toolbox-dependent analyses. The archived code DOI is [10.5281/zenodo.4531420](https://doi.org/10.5281/zenodo.4531420). A small independent Python implementation of the equations is a feasible local route, with golden traces from the author routine through an available compatible runtime before interpretation. Do not require purchase of MATLAB; report compatibility failures as implementation issues.

## Later platform requirements

Use independent interfaces for data loading, dynamics, interventions, task adapters, and evaluation. A loader returns stable IDs plus an oriented weighted graph and provenance. Dynamics expose reset/step/state/checkpoint. An intervention produces a graph and change manifest. A task supplies observations and chronological feedback. Evaluation owns splits, readout fitting, metrics, and resource accounting. These are requirements, not a chosen software framework.

Start the selected pilot with Python, NumPy/SciPy, and a small deterministic runner in an isolated environment; freeze exact package versions after an installation smoke test on the target workstation. Do not provision body simulation, accelerator packages, or a database service merely to build the foundation.

## EXP-002 validation implementation update

The bounded implementation needs only NumPy, pinned to 2.3.5 in [requirements-validation.txt](requirements-validation.txt), and the Python standard library. It ran with CPython 3.12.14 in `.venv` using `--system-site-packages` to reuse the bundled dependency without modifying global packages. This is not evidence of a clean install on the colleague's PC. MATLAB, `octave` and `octave-cli` were absent from PATH; no matching installation was found in the common Program Files/tool directories inspected. This is a scoped availability check, not proof that no executable exists anywhere on disk. The author comparison is prepared; its numerical statements are preserved at the pinned hash. No author runtime was installed or executed. D016 skips the separate measured workstation pilot.
