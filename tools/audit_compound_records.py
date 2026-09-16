"""Scoped C record verification without changing the historical foundation checker."""
import re
import numpy as np
from tools import run_compound_transfer as c

def main():
    artifacts=c.read(c.ROOT/'research/exp011_artifacts.json')
    for name,rec in artifacts.items():
        p=c.ROOT/name;assert c.sha(p)==rec['sha256'] and p.stat().st_size==rec['bytes'],name
    audit=c.read(c.OUT/'audit.json');assert audit['passed'] and audit['blocks']==31
    assert audit['source']==c.sources()
    selection=c.read(c.OUT/'selection.json');contract=c.read(c.OUT/'confirmation/contract.json')
    assert selection['n']==24 and selection['created_utc']<contract['created_utc']
    assert contract['selection_sha256']==c.sha(c.OUT/'selection.json')
    assert c.read(c.OUT/'preservation.json')['created_utc']<c.read(c.OUT/'validation/contract.json')['created_utc']
    for name,h in c.read(c.OUT/'preservation.json')['files'].items():assert c.sha(c.ROOT/name)==h,name
    stages=[]
    for stage,n in [('validation',1),('development',6),('confirmation',24)]:
        ct=c.read(c.OUT/stage/'contract.json');assert ct['blocks']==list(range(n))
        assert len(list((c.OUT/stage).glob('block_*.json')))==n
        stages.append((stage,n))
    manifest=c.read(c.ROOT/'research/experiment_manifest.json')
    ids=[e['id'] for e in manifest['experiments']]
    assert len(ids)==len(set(ids))==11 and set(ids)=={f'EXP-{i:03}' for i in range(1,12)}
    assert manifest['scientific_experiments_completed']==10
    for ident in ('EXP-010','EXP-011'):
        e=next(e for e in manifest['experiments'] if e['id']==ident)
        assert e['status']=='completed_audited' and (c.ROOT/e['spec']).is_file() and (c.ROOT/e['results']).is_file()
    records=[c.read(c.OUT/'confirmation'/f'block_{b:03}.json')['representations'] for b in range(24)]
    fixed=c.read(c.OUT/'fixed_rate_controls.json')
    for mode in c.MODES:
        for field in ('old','new'):
            values=np.array([[r[rep]['models'][mode+'_2'][field] for rep in c.REPS[:2]] for r in records]).mean(1)
            assert c.interval(values)==fixed['native_calibrated'][mode][field]
    for field in ('old','new'):
        values=np.array([[r[rep]['models']['replay10_2'][field]-r[rep]['models']['local10_2'][field] for rep in c.REPS[:2]] for r in records]).mean(1)
        assert c.interval(values)==fixed['replay10_minus_local10'][field]
    cal=c.read(c.OUT/'secondary_calibration.json')['calibrated_minus_native_blocked']
    assert selection['etas']['native']['blocked']==selection['etas']['calibrated']['blocked']==c.ETAS[0]
    for field in ('old','new','overall'):
        assert c.interval([r['calibrated']['models']['blocked_0'][field]-r['native']['models']['blocked_0'][field] for r in records])==cal[field]
    assert all(r[rep]['models']['blocked_0']['clips']==0 for r in records for rep in c.REPS[:2])
    docs=list(c.ROOT.glob('*.md'))+list((c.ROOT/'experiments').glob('*.md'))+list((c.ROOT/'research').glob('*.md'))
    broken=[];links=0
    for p in docs:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            target=target.strip('<>').split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'):continue
            from urllib.parse import unquote
            links+=1
            if not (p.parent/unquote(target)).exists():broken.append([str(p.relative_to(c.ROOT)),target])
    assert not broken,broken
    report=dict(passed=True,created_utc=c.stamp(),scientific_audit='audit.json',stages=stages,artifact_hashes_checked=len(artifacts),historical_files_checked=460,markdown_documents=len(docs),local_links=links,legacy_foundation_status='not passed: obsolete manifest count/schema supports through EXP-009; source unchanged',scope='C records, derived secondary controls, artifact/source hashes, stage timing and local links; not full legacy foundation validation')
    c.write(c.OUT/'record_audit.json',report);print(report)

if __name__=='__main__':main()
