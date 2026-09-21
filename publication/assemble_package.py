"""Assemble the compact local publication bundle from an intact research repository."""
from pathlib import Path
import hashlib, json, re, shutil, zipfile
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def main():
    paths = [
        'research/reference_data_audit.json', 'research/exp009_source_audit.json',
        'research/exp009_additional_source_checks.json', 'research/exp009_artifacts.json',
        'research/exp010_artifacts.json', 'research/exp011_artifacts.json',
        'research/experiment_manifest.json', 'research/validation_report_v3.json',
        'research/session_d_record_check.json', 'research/session_d_artifacts.json',
        'research/report_attribution_artifacts.json',
        'results/exp007_calibration/record.json', 'results/exp008_calibration/record.json',
        'results/exp008_anatomy/record.json', 'results/exp009/selection.json',
        'results/exp009/validation.json', 'results/exp010/selection.json',
        'results/exp010/audit.json', 'results/exp011/audit.json',
        'tools/validate_foundation_v3.py',
    ]
    for exp in ('exp010', 'exp011'):
        for stage in ('validation', 'development', 'confirmation'):
            paths.append(f'results/{exp}/{stage}/contract.json')
    for exp in range(3, 12):
        paths.extend(p.relative_to(ROOT).as_posix() for p in (ROOT / 'experiments').glob(f'EXP-{exp:03d}-*.md'))
    provenance = {}
    for name in sorted(set(paths)):
        src = ROOT / name
        dst = HERE / 'evidence' / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        provenance[name] = digest(src)
        assert digest(dst) == provenance[name]
    licenses = HERE / 'licenses'
    licenses.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'research/sources/exp009/author/LICENSE', licenses / 'CompensatoryVariability-LICENSE.txt')
    source_licenses = json.loads((ROOT / 'research/source_license_manifest.json').read_text())
    ben = next(r for r in source_licenses if r['repository'] == 'BrainsOnBoard/paper_RPEs_in_drosophila_mb')
    assert digest(ROOT / ben['path']) == ben['sha256']
    shutil.copyfile(ROOT / ben['path'], licenses / 'Bennett-model-LICENSE.txt')
    write_json(HERE / 'provenance_manifest.json', provenance)
    inputs = json.loads((HERE / 'input_manifest.json').read_text())
    for name, expected in inputs.items():
        assert digest(HERE / 'evidence' / name) == expected, name
        assert digest(ROOT / name) == expected, name
    assert json.loads((HERE / 'numerical_checks.json').read_text())['n_checks'] == 43
    assert json.loads((HERE / 'raw_array_checks.json').read_text())['checks_count'] == 380
    assert json.loads((ROOT / 'research/validation_report_v3.json').read_text())['status'] == 'passed'
    pdfs = {}
    for name, n in [('academic_report.pdf', 13), ('technical_supplement.pdf', 6)]:
        reader = PdfReader(HERE / name)
        assert len(reader.pages) == n
        assert reader.metadata.author == 'Thomas Julsgaard'
        assert 'Bounded participation calibration and memory retention' in reader.metadata.title
        texts = [p.extract_text() for p in reader.pages]
        assert all(len(t) > 400 for t in texts)
        assert not any('\ufffd' in t or '\u25a0' in t for t in texts)
        pdfs[name] = {'pages': n, 'author': reader.metadata.author, 'title': reader.metadata.title}
    # New live handoff links are checked separately from frozen historical documents.
    link_count = 0
    documents = list(HERE.glob('*.md')) + [ROOT / n for n in ['README.md', 'ROADMAP.md', 'RESEARCH_LOG.md', 'DECISIONS.md']]
    for path in documents:
        for link in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' in link or link.startswith(('#', 'mailto:')):
                continue
            target = link.strip('<>').split('#')[0]
            assert (path.parent / target).exists(), (path, target)
            link_count += 1
    record = {
        'production_date': '2026-09-21', 'report_date': '2026-09-16',
        'status': 'passed', 'scope': 'Local publication production; not independent scientific validation',
        'pdfs': pdfs, 'visual_review': 'All 19 pages inspected; final changed pages re-inspected',
        'figure_input_hashes_verified': len(inputs), 'additional_provenance_copies_verified': len(provenance),
        'paired_summary_checks': 43, 'saved_array_and_summary_checks': 380,
        'live_handoff_local_links_checked': link_count,
        'repository_validation': 'evidence/research/validation_report_v3.json',
        'remaining_external_actions': ['Venue-specific author approval and declarations before submission', 'Independent scientific review', 'Venue decision if journal submission is pursued'],
    }
    write_json(HERE / 'production_checks.json', record)
    files = []
    for path in sorted(HERE.rglob('*')):
        rel = path.relative_to(HERE)
        if not path.is_file() or rel.parts[0] in ('qa', '__pycache__'):
            continue
        if path.name in ('output_manifest.json', 'report_package.zip', 'report_package.sha256') or path.suffix == '.pyc':
            continue
        files.append(path)
    output = {p.relative_to(HERE).as_posix(): digest(p) for p in files}
    write_json(HERE / 'output_manifest.json', {'date': '2026-09-21', 'algorithm': 'SHA-256', 'files': output})
    bundle = HERE / 'report_package.zip'
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files + [HERE / 'output_manifest.json']:
            archive.write(path, 'publication/' + path.relative_to(HERE).as_posix())
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        for name, expected in output.items():
            assert hashlib.sha256(archive.read('publication/' + name)).hexdigest() == expected
    (HERE / 'report_package.sha256').write_text(digest(bundle) + '  report_package.zip\n', encoding='ascii')
    print(json.dumps({'files': len(output), 'zip_bytes': bundle.stat().st_size, 'checks': record}, indent=2))

if __name__ == '__main__':
    main()
