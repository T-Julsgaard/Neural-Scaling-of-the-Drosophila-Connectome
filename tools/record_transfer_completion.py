"""Synchronize current handoff documents after audited EXP-008 reporting."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from exp008.campaign import ROOT, folder, read, write

def main():
    a=read(folder('confirmation')/'analysis.json');done=read(folder('confirmation')/'completion.json')
    assert done['status']=='completed'
    summary=done['summary']
    link='[EXP-008 results](experiments/EXP-008-results.md)'
    next_action='Next: define a distinct held-out task family to test the limitation beyond this associative assay. Growth, collision-targeted rewiring and evolution retain their explicit entry conditions; no additional campaign is launched.'
    current=f'**Priority 4 complete — EXP-008 audited.** {summary} {link}. {next_action}'
    old_action='Design priority 4: validate the observed retention/participation result in another circuit under equally strong tuning. Freeze the transfer prediction and algorithm before new anatomy-specific development. Growth remains conditional; do not retune or extend EXP-007 confirmation.'
    for name in ('README.md','ROADMAP.md','PROJECT_CHARTER.md'):
        p=ROOT/name;s=p.read_text(encoding='utf-8')
        s=re.sub(r'\*\*Priority 3 complete[^\n]*',lambda _:current,s,count=1)
        s=s.replace(old_action,f'Priority 4 completed: {link}. {next_action}')
        s=s.replace('**Next — validate a specific prediction in another circuit.**','**Complete — validate a specific prediction in another circuit.**')
        s=s.replace('**EXP-002 through EXP-007 complete and audited','**EXP-002 through EXP-008 complete and audited')
        s=s.replace('Start with [EXP-007 results](experiments/EXP-007-results.md). Priorities 1–3 are complete.','Start with '+link+'. Priorities 1–4 are complete.')
        s=s.replace('The participation experiment is complete; the next step is cross-circuit validation of a specific prediction.','Participation and adult cross-circuit validation are complete; task-family generalization remains open.')
        p.write_text(s,encoding='utf-8')
    for name in ('OPEN_QUESTIONS.md','BENCHMARK_SPEC.md'):
        p=ROOT/name;s=p.read_text(encoding='utf-8').replace(old_action,f'Priority 4 completed: {summary} {link}. {next_action}')
        if name=='OPEN_QUESTIONS.md':
            s=re.sub(r'^\| Q04 \|[^\n]*',lambda _:f'| Q04 | Does the participation limitation extend to adult anatomy? | EXP-008 adult gamma-main test complete: {summary} {link} | Broader task/biological extrapolation remains open |',s,flags=re.M)
        p.write_text(s,encoding='utf-8')
    p=ROOT/'RESEARCH_BRANCHES.md';s=p.read_text(encoding='utf-8').replace('**EXP-008 adult transfer is in validation**',f'**EXP-008 adult transfer is complete** ({summary})');p.write_text(s,encoding='utf-8')
    p=ROOT/'EXPERIMENTS.md';s=p.read_text(encoding='utf-8').replace('**Six scientific experiments completed:','**Seven scientific experiments completed:').replace('and EXP-007 homeostasis.**','EXP-007 homeostasis and EXP-008 adult transfer.**')
    s=re.sub(r'^\| EXP-008 \|[^\n]*',lambda _:f"| EXP-008 | [Adult circuit transfer](experiments/EXP-008-protocol.md) | completed / audited | Nine preflight tests; eight development and {a['blocks']} confirmation blocks | {summary} {link} |",s,flags=re.M);p.write_text(s,encoding='utf-8')
    additions={
        'CLAIMS_LEDGER.md':f'## EXP-008 additions — 2026-09-14\n\n{summary} {link}. The transferred procedure uses independently fitted adult offsets and declared activity/input/update mappings. Inference is conditional on one adult gamma-main anatomy and the synthetic assay. It does not establish unique causal mediation, biological homeostasis or general task transfer. Adaptation/tail guardrails remain separate from mean-retention equivalence.',
        'REPRODUCTIONS.md':f'## EXP-008 verification — 2026-09-14\n\nAdult data extraction, independent scalar learner, larval sequence compatibility, nine preflight tests, exact validation replay, all checkpoint audits and one full-block replay per stage passed. Eight development and {a["blocks"]} confirmation blocks. This is new internal circuit-transfer evidence, not reproduction of a published biological effect. {link}.',
        'RESEARCH_LOG.md':f'## 2026-09-14 — Priority 4 adult transfer completed\n\n{summary} {link}. Eight development and {a["blocks"]} fresh confirmation blocks; all nine preflight tests, exact validation replay, checkpoint audits and one replay per stage passed. Protocol and procedure preceded calibration/development; selection/sample size/source were frozen before confirmation. Historical scientific hashes verified. Report includes strong tuning, direct/random/sham baselines, exact-multiset control, negative/inconclusive classification, adequacy and tail gates, and actual resources. Plotting required read escalation for the existing cached Matplotlib installation.\n\n{next_action}',
        'DECISIONS.md':f'## 2026-09-14 — D036: close bounded adult transfer\n\n{summary} {link}. Close EXP-008 after its prospective sample and audits; do not extend confirmation or infer causal anatomy/growth effects from cross-experiment differences. {next_action}'
    }
    for name,section in additions.items():
        p=ROOT/name;s=p.read_text(encoding='utf-8'); heading=section.split('\n',1)[0]
        if heading in s:
            s=re.sub(re.escape(heading)+r'\n.*?(?=\n## |\Z)',lambda _:section+'\n',s,flags=re.S)
        else:
            head,rest=s.split('\n',1);s=head+'\n\n'+section+'\n'+rest
        p.write_text(s,encoding='utf-8')
    p=ROOT/'research/experiment_manifest.json';d=read(p);d['scientific_experiments_completed']=7
    e=next(e for e in d['experiments'] if e['id']=='EXP-008')
    e.update(status='completed',runtime_measured=True,source_ids=['S68','S70'],development_blocks_completed=8,confirmation_blocks_completed=a['blocks'],validation_tests=9,results='experiments/EXP-008-results.md',run='research/runs/EXP-008-confirmation.json',primary=a['primary'],transfer_classification=a['transfer_classification'],informative_gate=a['informative_gate'],next_action=next_action)
    write(p,d)
    print(summary)

if __name__=='__main__':main()
