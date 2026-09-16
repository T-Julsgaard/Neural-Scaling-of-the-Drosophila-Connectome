"""Package pinned public sources and audit supplied parameters, without new tasks."""
from pathlib import Path
import hashlib
import json
import shutil
import datetime
import numpy as np
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, x): p.write_text(json.dumps(x, indent=2)+'\n', encoding='utf-8')

def main():
    cache = ROOT/'.cache/session_a'
    dst = ROOT/'research/sources/exp009'
    dst.mkdir(parents=True, exist_ok=True)
    for p in (cache/'author').rglob('*'):
        if p.is_file():
            q = dst/'author'/p.relative_to(cache/'author')
            q.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p,q)
    for source,name in [(cache/'paper.pdf','paper.pdf'),(cache/'supplementary/pnas.2102158118.sapp.pdf','supplement.pdf'),(cache/'supplementary/pnas.2102158118.sd01.xlsx','dataset.xlsx'),(cache/'commit.json','commit.json'),(cache/'tree.json','tree.json')]:
        shutil.copyfile(source,dst/name)
    out=ROOT/'results/exp009_source'
    fields=['thisW','thisW_Kennedy','thetaS','theta_Activity_homeo','APLgains','hallem','author_clean','pn_scale']
    arrays={f:np.loadtxt(out/(f+'.csv'),delimiter=',') for f in fields}
    np.savez_compressed(dst/'parameters.npz',**arrays)
    ratio=arrays['thisW_Kennedy'][arrays['thisW']>0]/arrays['thisW'][arrays['thisW']>0]
    book=openpyxl.load_workbook(dst/'dataset.xlsx',data_only=True)
    s=book['Fig 4']
    data=np.array([[s.cell(r,c).value for c in (9,13)] for r in range(3,23)])
    write(ROOT/'research/exp009_source_audit.json',dict(
        created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        commit='9f3f7e9e85117febef1ad32e3152c830570f74d3',
        paper='https://doi.org/10.1073/pnas.2102158118',
        supplement_mirror='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8670477/supplementaryFiles',
        panel='Figure 4B2, random red versus threshold-compensated magenta, c=1',
        dataset_cells=['Fig 4!I3:I22','Fig 4!M3:M22'],
        published_rows=data.tolist(),published_means=data.mean(0).tolist(),
        published_paired_mean_difference=float(np.diff(data,axis=1).mean()),
        same_connectivity=bool(np.array_equal(arrays['thisW']>0,arrays['thisW_Kennedy']>0)),
        compensated_weight_scale_minmax=[float(ratio.min()),float(ratio.max())],
        calibration_columns=['coding_level','coding_level_no_inhibition','min_mean_activity','max_mean_activity','mean_activity','sd_mean_activity','fraction_within_target_tolerance'],
        calibration=np.loadtxt(out/'calibration_audit.csv',delimiter=',').tolist(),
        source_files={str(p.relative_to(ROOT)):sha(p) for p in dst.rglob('*') if p.is_file()},
        failures=['PMC browser challenge','restricted shell sockets; public download escalation succeeded','master branch 422/404; main resolved and pinned','PNAS supplement challenge; Europe PMC mirror succeeded','scipy absent; existing Octave used for MAT extraction','web PDF screenshot cache miss; local pdfplumber render inspected','Octave exit printed execution_exception warning but exit status 0; numerical artifacts verified separately'],
        limitations=['One author-fitted instance, not twenty independently regenerated networks','Saved fitting history and random seeds absent','Figure 4 rate-selection recipe not identified in inspected methods/script; equal prospective development tuning is adaptation','Calibration optimizer source inspected, not executed or validated']))
    historical={}
    for name in ['exp002','exp003','exp004','exp005','exp006','exp007','exp008','experiments','results','research/runs']:
        for p in (ROOT/name).rglob('*'):
            if p.is_file() and '__pycache__' not in str(p) and 'exp009' not in str(p).lower() and 'EXP-009' not in p.name and p.suffix != '.tmp':
                historical[str(p.relative_to(ROOT))]=sha(p)
    write(ROOT/'research/exp009_historical_hashes.json',historical)
    print(json.dumps({'published_means':data.mean(0).tolist(),'published_difference':float(np.diff(data,axis=1).mean()),'weight_scale':[ratio.min(),ratio.max()],'historical_files':len(historical)}))

if __name__=='__main__': main()
