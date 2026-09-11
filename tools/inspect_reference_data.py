"""Audit small published inputs; no neural simulation or learning is performed."""
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/research_assets'


def main():
    with zipfile.ZipFile(CACHE / 'eichler_matrix.zip') as archive:
        members = [x for x in archive.namelist() if x.endswith('.csv')]
        assert len(members) == 1
        raw = archive.read(members[0])
    rows = list(csv.reader(io.TextIOWrapper(io.BytesIO(raw), encoding='utf-8-sig', newline='')))
    columns = rows[0][1:]
    labels = [r[0] for r in rows[1:]]
    mismatches = [{'index': i, 'row_label': a, 'column_label': b}
                  for i, (a, b) in enumerate(zip(labels, columns)) if a != b]
    values = [[int(v) for v in r[1:]] for r in rows[1:]]
    assert len(labels) == 387 and all(len(r) == 387 for r in values)
    assert all(v >= 0 for row in values for v in row)
    groups = {
        'PN_left': [i for i, s in enumerate(labels) if ' PN ' in s and s.endswith('left')],
        'KC_left': [i for i, s in enumerate(labels) if ' KC ' in s and s.endswith('left')],
        'MBON_left': [i for i, s in enumerate(labels) if s.startswith('MBON-') and s.endswith('left')],
    }
    pn, kc = groups['PN_left'], groups['KC_left']
    groups['KC_mature_left'] = [i for i in kc if 'young' not in labels[i].lower()]
    assert len(pn) == 40 and len(kc) == 110
    assert all(labels[i] == columns[i] for i in pn + kc + groups['MBON_left'])
    connected = [i for i in groups['MBON_left'] if sum(values[k][i] for k in kc)]
    projection = [values[p][k] for p in pn for k in kc]
    report = {
        'checked_at': '2026-09-11', 'kind': 'static_input_audit_not_experiment',
        'source_id': 'S64', 'csv_member': members[0],
        'csv_sha256': hashlib.sha256(raw).hexdigest(), 'neurons': len(labels),
        'orientation': 'row presynaptic, column postsynaptic; publication convention',
        'id_rule': 'matrix:<zero-based index> for verified PN/KC/MBON subset only; other row/column positions can differ',
        'row_column_label_mismatches': mismatches,
        'duplicate_display_labels': {k: v for k, v in collections.Counter(labels).items() if v > 1},
        'groups': groups, 'kc_receiving_mbon_left': connected,
        'pn_kc_left': {'shape': [40, 110], 'aggregated_edges': sum(v > 0 for v in projection),
                       'synapse_count_sum': sum(projection),
                       'zero_input_kc': [k for k in kc if sum(values[p][k] for p in pn) == 0]},
        'pn_kc_mature_left': {'shape': [40, len(groups['KC_mature_left'])],
                            'aggregated_edges': sum(values[p][k] > 0 for p in pn for k in groups['KC_mature_left']),
                            'synapse_count_sum': sum(values[p][k] for p in pn for k in groups['KC_mature_left'])},
        'nodes': [{'id': f'matrix:{i}', 'matrix_index': i, 'label': s} for i, s in enumerate(labels)],
    }
    (ROOT / 'research/reference_data_audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('neurons', 'pn_kc_left', 'csv_sha256')}))
    assets = json.loads((ROOT / 'research/asset_audit.json').read_text(encoding='utf-8'))
    for asset in assets:
        if asset['name'] in ('fafb_downloads.json', 'banc_downloads.json'):
            data = (CACHE / asset['name']).read_bytes()
            try:
                json.loads(data)
                asset['format_validation'] = 'valid_json'
            except (ValueError, UnicodeDecodeError):
                asset['format_validation'] = 'invalid_manifest_html_response'
                asset['usable_as_dataset_manifest'] = False
    (ROOT / 'research/asset_audit.json').write_text(json.dumps(assets, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
