# Reproducing the research

Read the [main report](publication/academic_report.pdf) and [technical supplement](publication/technical_supplement.pdf) first. This guide describes the public research release dated 21 September 2026. Commands run from the repository root unless stated otherwise.

## 1. Verify or rebuild the publication

The delivered PDFs, editable Markdown, vector figures, source-number CSVs, provenance, scripts and compact JSON evidence are in [publication/](publication/README.md). This layer does not need the full experiment arrays.

```sh
python publication/verify_package.py
python -m venv .venv
```

Activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in a POSIX shell, then install the pinned dependencies:

```sh
python -m pip install -r publication/requirements.txt
python publication/build_figures.py
python publication/build_report.py
```

Production used CPython 3.12.14 and NumPy 2.3.5. Figure rebuilding verifies 43 summary/interval checks. The renderer uses Windows Cambria/Calibri; these font files are not distributed. On another system, explicitly substitute installed fonts in the renderer and inspect all 19 pages for pagination and layout. Rebuilding can change PDF metadata and hashes. The original manifest identifies delivered bytes; rerun `publication/assemble_package.py` only when deliberately assembling a new package from the full repository after visual review.

## 2. Restore the complete saved evidence

The [academic report release](https://github.com/T-Julsgaard/Neural-Scaling-of-the-Drosophila-Connectome/releases/tag/academic-report-2026-09-21) supplies all 71,114 previously Git-ignored NPZ files under `results/`. These include earlier campaigns and failed development paths as well as report-critical calibration, anatomy and confirmation arrays. Code, source freezes, JSON summaries and contracts are already in Git. No new samples were generated for release.

Download every `saved-arrays-*.zip` asset into `.cache/public-release/`. With GitHub CLI installed:

```sh
gh release download academic-report-2026-09-21 --repo T-Julsgaard/Neural-Scaling-of-the-Drosophila-Connectome --pattern "saved-arrays-*.zip" --pattern SHA256SUMS --dir .cache/public-release
python tools/reproduction_archive.py verify
python tools/reproduction_archive.py restore
```

The tool uses only Python's standard library. It verifies each archive and every member against [the committed manifest](research/reproduction_archive_manifest.json), restores original repository-relative paths, and refuses to replace differing local evidence. ZIP parts are independent archives; do not concatenate them. Allow roughly 10 GB of free space for downloads plus restored arrays. Repeating restoration is safe when existing bytes match. `--directory PATH` selects another download location.

An ordinary GitHub source ZIP or clone does **not** include these release assets. The much smaller `publication/report_package.zip` contains the publication layer only.

## 3. Check records and reported numbers

With the arrays restored, install the numerical dependency and run:

```sh
python -m pip install -r requirements-validation.txt
python tools/validate_foundation_v3.py
python publication/audit_numerics.py
```

The schema-3 validator checks the research records, source hashes, contracts and saved evidence. The legacy `validate_foundation.py` is retained as historical code and does not cover all 11 specifications. `audit_numerics.py` performs 380 arithmetic checks against saved arrays and exports the calibration block table. These commands refresh their check records; use a disposable clone if you want the release checkout to remain byte-identical. Arithmetic verification does not retrain models or establish independent replication.

## 4. Replay experiments and inspect the methods

The original protocols and result reports are indexed in [EXPERIMENTS.md](EXPERIMENTS.md). Each specifies task construction, seeds, candidate settings, selection rules, confirmation blocks, endpoints and limitations. Shared implementations live in `exp002/` through `exp009/`; the later diagnostics are implemented in their tools.

For example, the report's B and C diagnostic replay commands are:

```sh
python tools/run_readout_diagnostic.py audit
python tools/run_compound_transfer.py audit
```

These recompute validation, development and confirmation arrays against the archived results and verify preserved dependencies. They write updated audit records; C also refreshes its analysis timestamp. Run them in a separate restored clone. The original records report about seven minutes for B and two minutes for C on the production CPU, not a performance guarantee. They require the pinned numerical environment; exact floating-point replay can differ across libraries or platforms. Existing frozen stages intentionally reject incompatible sources or settings. Consult each protocol before launching a new campaign, and keep new outputs separate from the released evidence.

The original experiments are CPU assays. The colleague's proposed GPU workstation in historical planning records is not a runtime requirement. An independently installed GNU Octave is needed only to repeat the author MATLAB reference fixtures; `tools/run_bennett_reference.py --octave PATH` accepts an explicit executable. Installed runtimes are not part of the release.

## Source recovery and attribution

- The small pinned larval/source inputs are retained under `.cache/research_assets/`, with audits and original license files. `python tools/fetch_validation_assets.py` can recover the two bounded validation inputs and checks their hashes.
- Adult raw adjacency and annotation downloads are recoverable using `python tools/fetch_transfer_data.py`. It checks the pinned URLs and SHA-256 values from `results/exp008_anatomy/record.json`; the derived projection itself is in the saved-array release.
- The supplied compensation source, model parameters and author reference artifacts are in `research/sources/exp009/` and `results/exp009_source/`, with their upstream attribution and GPL license.
- Original source terms, exact commits, selection/exclusion rules and access limitations are documented in [DATA_PROVENANCE.md](DATA_PROVENANCE.md), [SOFTWARE_AUDIT.md](SOFTWARE_AUDIT.md) and [publication/ATTRIBUTION.md](publication/ATTRIBUTION.md).

Network recovery depends on upstream availability. Hashes identify the original bytes and prevent silent substitution. Git attributes preserve exact file bytes, including historical line endings, so a clone can satisfy the recorded hashes. Proprietary fonts, credentials, personal settings, installed Python/Octave environments and disposable caches are not distributed. Historical execution paths remain in frozen scientific records to preserve their checksums.
