"""Offline integrity checks for the research record, not scientific tests."""
import hashlib
import json
from pathlib import Path
import re
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = {
    'Initial Research Prompt for Astra — Scaling the Drosophila Connectome.md': '69eff8e8c9adc9b8669778f9949a1b7d1fe1d5eb0c5e43ff5f66e03ff5872317',
    'ASTRA_MASTER_RESEARCH_BRIEF.md.md': '4318599c2e83e48a62577938fbd38f6055036de56842eee22aba93b9b29ac0cb',
}
REQUIRED = ['README.md', 'PROJECT_CHARTER.md', 'STATE_OF_ART.md', 'RESEARCH_LOG.md',
            'FAILED_PATHS.md', 'NOVEL_IDEAS.md', 'EXPERIMENTS.md', 'DECISIONS.md',
            'OPEN_QUESTIONS.md', 'ROADMAP.md', 'CLAIMS_LEDGER.md', 'DATA_PROVENANCE.md',
            'REPRODUCTIONS.md', 'BENCHMARK_SPEC.md', 'RESEARCH_BRANCHES.md', 'SOFTWARE_AUDIT.md']


def main():
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            errors.append('Missing ' + name)
    hashes = {}
    for name, expected in ORIGINALS.items():
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        hashes[name] = digest
        if digest != expected:
            errors.append('Original changed: ' + name)
    refs = json.loads((ROOT / 'research/references.json').read_text(encoding='utf-8'))
    source_ids = {r['id'] for r in refs}
    if len(source_ids) != len(refs):
        errors.append('Duplicate bibliography IDs')
    bib = (ROOT / 'research/references.bib').read_text(encoding='utf-8')
    for r in refs:
        if not all(r.get(k) for k in ('id', 'title', 'author', 'year', 'kind', 'url', 'read_depth', 'accessed')):
            errors.append('Incomplete reference ' + r['id'])
        if '@misc{' + r['id'] + ',' not in bib:
            errors.append('Missing BibTeX ' + r['id'])
        if r['internally_reproduced']:
            errors.append('Unexpected reproduced claim ' + r['id'])
    manifest = json.loads((ROOT / 'research/experiment_manifest.json').read_text(encoding='utf-8'))
    assert len(manifest['experiments']) == 3
    for e in manifest['experiments']:
        expected_status = 'validation' if e['id'] == 'EXP-002' else 'proposed'
        if e['status'] != expected_status or e['runtime_measured'] or not (ROOT / e['spec']).is_file():
            errors.append('Invalid handoff state ' + e['id'])
        if set(e['source_ids']) - source_ids:
            errors.append('Unknown handoff source ' + e['id'])
    validation = json.loads((ROOT / 'research/exp002_validation.json').read_text(encoding='utf-8'))
    if validation['status'] != 'passed' or validation['failures'] or validation['skipped']:
        errors.append('EXP-002 bounded validation did not fully pass')
    if validation['development_blocks'] or validation['confirmation_blocks']:
        errors.append('Unexpected EXP-002 scientific campaign')
    if validation['author_code_reproduction'] != 'not_run' or validation['independent_reviewer'] != 'not_performed':
        errors.append('Review/reproduction status changed; update the integrity contract explicitly')
    for name, expected in validation['code_snapshot_sha256'].items():
        if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_text(encoding='utf-8').encode('utf-8')).hexdigest() != expected:
            errors.append('Stale EXP-002 validation snapshot: ' + name)
    target = json.loads((ROOT / 'research/target_hardware.json').read_text(encoding='utf-8'))
    if target['verified_on_target'] or target['target_access_performed'] or target['target_benchmarks']:
        errors.append('Unexpected target execution claim')
    for key, value in (('reported_ram_gb', 'ram_gb'), ('cpu', 'cpu'), ('gpu', 'gpu'), ('vram_gb', 'gpu_vram_gb')):
        if manifest['target'][key] != target['reported'][value]:
            errors.append('Target manifest disagrees with reported ' + value)
    report_path = ROOT / 'research/validation_report.json'
    # The generated report is a legitimate forward link while this script runs.
    docs = [p for p in ROOT.glob('*.md') if p.name not in ORIGINALS]
    docs += list((ROOT / 'research').glob('*.md')) + list((ROOT / 'experiments').glob('*.md'))
    links = 0
    for path in docs:
        content = path.read_text(encoding='utf-8')
        if 'cite' in content:
            errors.append('Nonportable citation in ' + path.name)
        for source_id in re.findall(r'\bS\d{2}\b', content):
            if source_id not in source_ids:
                errors.append('Unknown citation ' + source_id + ' in ' + path.name)
        for target in re.findall(r'\]\(([^)]+)\)', content):
            target = target.strip('<>')
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            target = urllib.parse.unquote(target.split('#')[0])
            resolved = (path.parent / target).resolve()
            links += 1
            if not resolved.exists() and resolved != report_path:
                errors.append('Broken local link: ' + str(path.relative_to(ROOT)) + ' -> ' + target)
    data = json.loads((ROOT / 'research/reference_data_audit.json').read_text(encoding='utf-8'))
    if len(data['groups']['KC_mature_left']) != 73 or len(data['groups']['PN_left']) != 40:
        errors.append('Reference subset counts changed')
    if len(data['row_column_label_mismatches']) != 14:
        errors.append('Reference axis audit changed')
    report = {'date': '2026-09-11', 'kind': 'offline_record_integrity_not_scientific_validation',
              'status': 'passed' if not errors else 'failed', 'errors': errors,
              'markdown_documents_checked': len(docs), 'local_links_checked': links,
              'bibliographic_sources': len(refs), 'experiment_specifications': 3,
              'original_sha256': hashes, 'scientific_experiments_run': 0,
              'exp002_bounded_validation': validation['status'],
              'exp002_validation_tests': validation['tests_run'],
              'note': 'Zero scientific campaigns; bounded learning-rule and toy/episode checks ran separately',
              'limits': ['Does not verify remote URL availability', 'Does not run upstream code or neural models',
                         'Does not establish scientific reproduction or target hardware performance']}
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('original_sha256', 'limits')}, ensure_ascii=True))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
