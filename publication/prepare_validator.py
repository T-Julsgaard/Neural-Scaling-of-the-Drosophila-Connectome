"""Create the schema-3 successor without editing the preserved legacy checker."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
src=(ROOT/'tools/validate_foundation.py').read_text(encoding='utf-8')
def replace(old,new):
    global src
    assert old in src, old
    src=src.replace(old,new,1)
replace('"""Offline integrity checks for the research record, not scientific tests."""','"""Schema-3 successor to validate_foundation.py. Retains legacy scientific checks and adds EXP-010/011. No training or historical-output writes."""')
replace("    assert len(manifest['experiments']) == (6 if mechanism_complete else 4) + int((ROOT/'experiments/EXP-007-protocol.md').exists()) + int((ROOT/'experiments/EXP-008-protocol.md').exists()) + int(compensation_complete)","""    ids = [e['id'] for e in manifest['experiments']]
    if manifest['schema_version'] != 3 or len(ids) != 11 or len(set(ids)) != 11 or set(ids) != {f'EXP-{i:03}' for i in range(1,12)}:
        errors.append('Schema-3 experiment ID set/count mismatch')
    if manifest['scientific_experiments_completed'] != 10:
        errors.append('Schema-3 completion count mismatch')""")
replace("    for e in manifest['experiments']:\n        expected_status", """    for e in manifest['experiments']:
        if e['id'] in ('EXP-010','EXP-011'):
            number = int(e['id'][-3:])
            folder = ROOT/f'results/exp{number:03}'
            try:
                if not all(k in e for k in ('id','status','spec','results','prediction_passed')):
                    raise ValueError('Missing schema-3 fields')
                if e['status'] != 'completed_audited' or not (ROOT/e['spec']).is_file() or not (ROOT/e['results']).is_file():
                    raise ValueError('Invalid completion status or links')
                selection = json.loads((folder/'selection.json').read_text())
                analysis = json.loads((folder/'analysis.json').read_text())
                audit = json.loads((folder/'audit.json').read_text())
                if e['prediction_passed'] != analysis['prediction_passed'] or not audit['passed'] or audit['blocks'] != 31 or selection['n'] != 24:
                    raise ValueError('Outcome/status mismatch')
                if number == 11 and e['classification'] != analysis['classification']:
                    raise ValueError('Classification mismatch')
                for name, expected in audit['source'].items():
                    if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
                        raise ValueError('Frozen scientific source drift: '+name)
                for name, expected in selection['source'].items():
                    if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
                        raise ValueError('Selection source drift: '+name)
                for name, expected in selection['development_hashes'].items():
                    if hashlib.sha256((folder/'development'/name).read_bytes()).hexdigest() != expected:
                        raise ValueError('Development selection input drift: '+name)
                for stage, count in [('validation',1),('development',6),('confirmation',24)]:
                    contract_path = folder/stage/'contract.json'
                    contract = json.loads(contract_path.read_text())
                    contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
                    records = sorted((folder/stage).glob('block_*.json'))
                    if len(records) != count or len(contract['blocks']) != count:
                        raise ValueError('Stage count mismatch: '+stage)
                    if len(set(contract['blocks'])) != count:
                        raise ValueError('Duplicate block IDs')
                    actual_ids = {int(p.stem.split('_')[-1]) for p in records}
                    if actual_ids != set(contract['blocks']):
                        raise ValueError('Stage block ID mismatch: '+stage)
                    for name, expected in contract['source'].items():
                        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
                            raise ValueError('Contract source drift: '+name)
                    if stage == 'confirmation':
                        pinned_selection_matches = (contract['selection'] == selection) if number == 10 else (contract['selection_sha256'] == hashlib.sha256((folder/'selection.json').read_bytes()).hexdigest())
                        if selection['created_utc'] >= contract['created_utc'] or not pinned_selection_matches:
                            raise ValueError('Selection chronology/hash mismatch')
                    for p in records:
                        rec=json.loads(p.read_text())
                        if rec['contract_sha256'] != contract_hash or rec['sha256'] != hashlib.sha256(p.with_suffix('.npz').read_bytes()).hexdigest():
                            raise ValueError('Checkpoint drift: '+str(p.relative_to(ROOT)))
                artifacts=json.loads((ROOT/f'research/exp{number:03}_artifacts.json').read_text())
                for name,item in artifacts.items():
                    p=ROOT/name
                    raw=p.read_bytes()
                    if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
                        if name == 'research/SESSION_D_HANDOFF.md':
                            # Verify both the dated D successor and exact pre-D bytes.
                            successor=json.loads((ROOT/'research/session_d_artifacts.json').read_text())['files'][name]
                            historical=re.sub(br'\\*\\*Superseded 2026-09-16:\\*\\*[^\\r\\n]*(?:\\r?\\n){2}',b'',raw).replace(b'\\n\\n',b'\\r\\n\\r\\n',1)
                            if hashlib.sha256(raw).hexdigest()!=successor['sha256'] or len(raw)!=successor['bytes'] or hashlib.sha256(historical).hexdigest()!=item['sha256'] or len(historical)!=item['bytes']:
                                raise ValueError('Historical handoff content or successor drift: '+name)
                            historical_live_document_changes.append(dict(experiment=e['id'],file=name,frozen_sha256=item['sha256'],current_sha256=successor['sha256'],reason='Exact historical bytes reconstructed by removing the dated D supersession paragraph and restoring the original title line endings; current bytes match the dated D manifest.'))
                        else:
                            raise ValueError('Artifact drift: '+name)
            except (OSError, ValueError, KeyError) as exc:
                errors.append(e['id']+' integrity: '+str(exc))
            continue
        expected_status""")
replace("if manifest['scientific_experiments_completed'] != 1 + int(confirmation_complete) + int(activity_complete) + int(mechanism_complete) + int(memory_complete) + int(homeostasis_complete) + int(transfer_complete) + int(compensation_complete):", "if manifest['scientific_experiments_completed'] != 3 + int(confirmation_complete) + int(activity_complete) + int(mechanism_complete) + int(memory_complete) + int(homeostasis_complete) + int(transfer_complete) + int(compensation_complete):")
replace("report_path = ROOT / 'research/validation_report.json'", "report_path = ROOT / 'research/validation_report_v3.json'")
replace("'scientific_experiments_run': 1 + int(confirmation_complete)", "'scientific_experiments_run': 3 + int(confirmation_complete)")
replace("'note': 'Offline verification of preserved experimental artifacts, frozen source and current handoff records'", "'note': 'Schema-3 successor retains legacy checks and adds B/C IDs, status, source, selection, stage chronology and artifact checks; no training executed'")
(ROOT/'tools/validate_foundation_v3.py').write_text(src,encoding='utf-8',newline='\n')
print('Created schema-3 successor; legacy source untouched')
