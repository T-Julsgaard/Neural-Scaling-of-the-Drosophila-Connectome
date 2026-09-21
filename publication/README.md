# Academic report package

**Bounded participation calibration and memory retention**  
Thomas Julsgaard - MSc student in Software Design, IT University of Copenhagen  
Report date: 16 September 2026. Production and checks: 21 September 2026.

The completed report synthesizes the existing experiments; no new training or confirmation samples were generated. This package accompanies the public research release. It has not been submitted to a journal or independently peer reviewed. Start with the main report below; the [complete repository and saved-array release](https://github.com/T-Julsgaard/Neural-Scaling-of-the-Drosophila-Connectome) provide the wider project and scientific replay materials.

## Read and edit

- [Main report](academic_report.pdf): 13 pages, including three original scientific figures.
- [Technical supplement](technical_supplement.pdf): six pages of equations, settings, provenance and limitations.
- Editable manuscripts: [report.md](report.md) and [supplement.md](supplement.md).
- [Reference database](references.bib), [claim audit](claim_audit.md) and [readiness and author actions](readiness.md).
- [Figure directory](figures): vector PDF/SVG and 320-dpi PNG exports for all three figures.
- [Source-number table](figure_source_data.csv) and [calibration block data](calibration_block_data.csv).
- [Attribution, source acquisition and rights](ATTRIBUTION.md).

`report_package.zip` is a compact copy of the finished package, excluding rendering intermediates and local caches. `output_manifest.json` inventories package files with SHA-256 checksums; `report_package.sha256` verifies the ZIP. `verify_package.py` checks the extracted package. Raw training checkpoints, anatomical bulk files, third-party source archives and a Python environment are not inside this ZIP.

## Rebuild the publication

The editable source format is deliberately small: Markdown headings, paragraphs, simple tables, numbered references, figure links and explicit `<!-- PAGE -->` page boundaries. `build_report.py` renders it using ReportLab and merges vector figure PDFs with pypdf. The numbered bibliography in the manuscripts is the rendered authority; `references.bib` is an accompanying reusable database, not an automatically resolved citation engine. Keep the two in agreement when editing.

Production used Windows, CPython 3.12.14, NumPy 2.3.5, Matplotlib 3.10.7, ReportLab 4.4.9, pypdf 6.10.0, pypdfium2 5.13.0 and Pillow 12.3.0. Exact direct dependencies are in [requirements.txt](requirements.txt). The report renderer also uses Cambria and Calibri from `C:/Windows/Fonts`; these proprietary fonts are not redistributed. On another OS, explicitly substitute installed fonts in `build_report.py` and recheck pagination. Figures use Matplotlib's bundled DejaVu Sans.

From the extracted publication directory, in an environment with those dependencies:

```powershell
python verify_package.py
python build_figures.py
python build_report.py
```

`build_figures.py` reads the original project's `results/` when present; otherwise it reads the bundled `evidence/results/`. It checks 43 saved-block summaries/paired intervals, writes the three figures, and refreshes source-number and input-hash files. It does not train models. The script's optional local `.cache/baseline-plot-deps` fallback was used for Matplotlib on the production machine; a normal installed Matplotlib works without it. Run from any working directory: paths are resolved relative to the scripts.

`build_report.py` needs the three figure PDFs (already included) and both Markdown files. It produces the two final PDFs and page PNGs/contact sheets under `qa/`. Inspect every page after an edit. PDF metadata records author, title and the distinct report/production dates. Timestamp metadata can change binary output hashes even when the scientific content is unchanged; original hashes identify the delivered files, not a claim of bitwise deterministic PDF builds.

## Verification and reproduction boundaries

The self-contained figure rebuild uses 58 archived JSON inputs, including all 24 B and all 24 C confirmation summaries. A rebuild from an extracted ZIP passed without the original results directory; its source CSV and input/check records were byte-identical ([portability check](portable_rebuild_check.json)). The exact input list and hashes are in [input_manifest.json](input_manifest.json). Additional provenance copies and their hashes are in [provenance_manifest.json](provenance_manifest.json). Files under `evidence/` retain original repository-relative paths. Frozen Markdown copies there are historical records; their relative links refer to the full research repository and may point outside this compact bundle. Local Git attributes preserve delivered bytes rather than converting line endings behind the hash manifests.

The separate `audit_numerics.py` requires the original research repository and its saved NPZ arrays. It performs 380 read-only checks of calibration means, tails, acquisition, participation, bounds and supplied-model summaries. It exports the block CSV and [raw-array check record](raw_array_checks.json), whose exact NPZ paths and hashes identify raw files excluded from this compact ZIP but supplied in the full repository release. This is arithmetic verification, not training replay or independent scientific replication.

The schema-3 foundation validator is retained at `tools/validate_foundation_v3.py` in the full repository, with a copy under `evidence/tools/` here. Run it only from the full repository with its existing runtime and complete archives. [Its result](evidence/research/validation_report_v3.json) passed checks for all 11 specifications and ten completed scientific experiments. It preserves the legacy checker, validates B/C source/selection/stage contracts and records two exact historical-document changes explicitly. `prepare_validator.py` is a production helper for generating that versioned successor, not required for rebuilding the report. The complete repository, original data and frozen sources are required for scientific replay; this compact package does not pretend otherwise.

`assemble_package.py` is a repository-only packaging helper: it copies selected provenance, checks PDF/input integrity, writes manifests and the ZIP. Run it after rebuilding and completing visual review. Rebuilding intentionally invalidates the original output manifest until packaging is rerun. The final local production status and remaining external actions are in `readiness.md`.
