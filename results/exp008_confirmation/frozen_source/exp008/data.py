"""Auditable hemibrain v1.1 olfactory PN -> gamma-main KC extraction."""
import csv
import io
import json
import tarfile
from pathlib import Path
import numpy as np
from exp002.data import ROOT, sha256

CACHE = ROOT/'.cache/exp008'
OUT = ROOT/'results/exp008_anatomy'
ARCHIVE = 'exported-traced-adjacencies-v1.1.tar.gz'
PREFIX = 'exported-traced-adjacencies-v1.1/'

def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    annotations = list(csv.DictReader((CACHE/'monoglom_PNs_v1.1.csv').open()))
    pn = {int(r['bodyId']): r for r in annotations}
    assert len(pn) == len(annotations)
    with tarfile.open(CACHE/ARCHIVE) as archive:
        def rows(name):
            return csv.DictReader(io.TextIOWrapper(archive.extractfile(PREFIX+name)))
        neurons = {int(r['bodyId']): r for r in rows('traced-neurons.csv')}
        assert set(pn) <= set(neurons)
        for i, r in pn.items():
            assert r['type'] == neurons[i]['type']
        kc = sorted(i for i, r in neurons.items() if r['type'] == 'KCg-m')
        inputs = sorted(pn)
        pi, ki = {v:i for i,v in enumerate(inputs)}, {v:i for i,v in enumerate(kc)}
        counts = np.zeros((len(inputs), len(kc)), dtype=np.int64)
        selected_rows = 0
        for r in rows('traced-roi-connections.csv'):
            pre, post = int(r['bodyId_pre']), int(r['bodyId_post'])
            if pre in pi and post in ki and r['roi'] == 'CA(R)':
                weight = int(r['weight']); assert weight > 0 and pre != post
                counts[pi[pre], ki[post]] += weight; selected_rows += 1
        archive_readme = archive.extractfile(PREFIX+'README').read().decode()
    keep_p, keep_k = counts.sum(1)>0, counts.sum(0)>0
    removed_p = [i for i,b in zip(inputs,keep_p) if not b]
    removed_k = [i for i,b in zip(kc,keep_k) if not b]
    inputs = [i for i,b in zip(inputs,keep_p) if b]
    kc = [i for i,b in zip(kc,keep_k) if b]
    counts = counts[keep_p][:,keep_k]
    p = counts/counts.sum(0)
    np.savez_compressed(OUT/'projection.npz', counts=counts, projection=p, pn_ids=inputs, kc_ids=kc)
    rec = dict(provider='Janelia FlyEM hemibrain', release='hemibrain:v1.1', accessed='2026-09-14',
        archive_url='https://storage.googleapis.com/hemibrain/v1.1/'+ARCHIVE,
        archive_sha256=sha256(CACHE/ARCHIVE), archive_readme=archive_readme,
        annotation_repository='https://github.com/aclinlab/CompensatoryVariability',
        annotation_commit=(CACHE/'annotation_commit.txt').read_text().strip(),
        annotation_path='connectome/data/monoglom_PNs_v1.1.csv', annotation_sha256=sha256(CACHE/'monoglom_PNs_v1.1.csv'),
        source_terms='Hemibrain CC-BY (Li et al. data availability; Figshare archive CC BY 4.0); author annotation repository GPL-3.0. Preserve both attributions; no upstream code executed.',
        extraction='Presynaptic rows, postsynaptic columns. Listed monoglomerular PNs -> type exactly KCg-m; CA(R) primary ROI; positive contacts only; duplicate rows summed. Exclude zero-input KCs and zero-output PNs; sort numeric body IDs. Normalize each KC column to one. No sign inference; selected PN contacts modeled excitatory.',
        missing='Missing type/ID mismatches fail; absent edges zero. Other sensory inputs, regions, KCs and untraced/cropped neurons omitted by design/source.',
        exclusion_note='Author KCstoExclude.csv contains positional indices, not body IDs, and is NOT applied without its original ordering. Source archive already selects non-cropped traced neurons; residual completeness is a limitation.',
        pn_ids=inputs, kc_ids=kc, pn_types=[pn[i]['type'] for i in inputs],
        zero_output_pn_ids=removed_p, zero_input_kc_ids=removed_k,
        shape=list(p.shape), selected_roi_rows=selected_rows, edges=int(np.count_nonzero(counts)), contacts=int(counts.sum()),
        projection_sha256=sha256(OUT/'projection.npz'), parser_sha256=sha256(Path(__file__)))
    (OUT/'record.json').write_text(json.dumps(rec, indent=2)+'\n')
    print(json.dumps({k:rec[k] for k in ('shape','edges','contacts','zero_input_kc_ids','zero_output_pn_ids')}))
    return p, rec

def load_projection():
    rec = json.loads((OUT/'record.json').read_text())
    assert sha256(OUT/'projection.npz') == rec['projection_sha256']
    assert sha256(Path(__file__)) == rec['parser_sha256']
    with np.load(OUT/'projection.npz') as a:
        return a['projection'], rec

if __name__ == '__main__': prepare()
