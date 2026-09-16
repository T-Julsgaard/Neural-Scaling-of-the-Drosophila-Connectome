"""Update current project handoffs only after EXP-007 audited reporting."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from exp007.campaign import ROOT, read, write, folder
from exp002.data import sha256


def edit(name, function):
    p = ROOT/name; p.write_text(function(p.read_text(encoding='utf-8')), encoding='utf-8')


def prepend(name, heading, text):
    edit(name, lambda old: old if text in old else old.replace(heading, heading+'\n\n'+text, 1))


def main():
    a = read(folder('confirmation')/'analysis.json'); dev = read(folder('development')/'selection.json')
    assert read(folder('confirmation')/'audit.json')['status'] == 'passed'
    assert read(ROOT/'results/exp007_matched_sham/analysis.json')['status'] == 'passed'
    report = (ROOT/'experiments/EXP-007-results.md').read_text(encoding='utf-8')
    summary = report.split('## Prespecified conclusion\n\n')[1].split('\n\n')[0]
    evidence = '[EXP-007 results](experiments/EXP-007-results.md)'
    next_action = 'Design priority 4: validate the observed retention/participation result in another circuit under equally strong tuning. Freeze the transfer prediction and algorithm before new anatomy-specific development. Growth remains conditional; do not retune or extend EXP-007 confirmation.'
    update = f'**Priority 3 complete — EXP-007 audited.** {summary} {evidence}. {next_action}'
    prepend('README.md', '# Neural Scaling of the Drosophila Connectome', update)
    edit('README.md', lambda t: t.replace('**EXP-002 through EXP-006 complete and audited', '**EXP-002 through EXP-007 complete and audited').replace('Next: balanced participation across existing cells; growth stays conditional.', 'The resulting participation test is now complete in EXP-007; growth stays conditional.').replace('The next step is calibrated participation across existing cells.', 'The participation experiment is complete; the next step is cross-circuit validation of a specific prediction.'))
    edit('README.md', lambda t: '\n'.join('Start with '+evidence+'. Priorities 1–3 are complete. '+next_action if line.startswith('Start with [EXP-006]') else line for line in t.split('\n')))
    prepend('ROADMAP.md', '# Evidence-gated roadmap', update)
    edit('ROADMAP.md', lambda t: '\n'.join(('3. **Complete — balanced participation across existing cells.** '+summary+' '+evidence+'.') if line.startswith('3. **Next — balanced participation') else ('4. **Next — validate a specific prediction in another circuit.** '+next_action) if line.startswith('4. **Then — validate a specific prediction') else ('Next concrete action: '+next_action) if line.startswith('Next concrete action: design and freeze priority 3') else line for line in t.split('\n')).replace('Next is priority 3 homeostasis;', 'Priority 3 is now complete in EXP-007;').replace('proceed to homeostasis before broader transfer or more growth', 'EXP-007 completes homeostasis; prepare cross-circuit validation before more growth'))
    edit('PROJECT_CHARTER.md', lambda t: t.split('## Current milestone\n')[0]+'## Current milestone\n\n'+update+'\n\n## Governance and continuity\n'+t.split('## Governance and continuity\n')[1])
    edit('OPEN_QUESTIONS.md', lambda t: '\n'.join('Next action: '+next_action+' '+evidence+'.' if line.startswith('Next action: design priority 3') else line for line in t.split('\n')))
    prepend('CLAIMS_LEDGER.md', '# Claims ledger', '## EXP-007 additions — 2026-09-14\n\n'+summary+' '+evidence+'.\n\nThe lower learning-rate boundary was extended 16-fold, with 32 unique candidate settings per method. Native ordinary and calibrated K6 selected the same interior rate (.006667). Cell recruitment, behavioral gain, practical gain and adaptation/tail guardrails are separate claims. Results concern bounded frozen offsets in one normalized larval circuit; they do not establish biological homeostasis, online adaptation, all possible calibrations or second-anatomy transfer. The exact-multiset shuffle is a disclosed development-informed, pre-confirmation secondary addendum.')
    prepend('RESEARCH_LOG.md', '# Research log', '## 2026-09-14 — EXP-007 completes priority 3\n\nUser authorized the research handoff, explicitly retaining stronger ordinary tuning. Implemented bounded unlabeled offsets, equal 32-setting searches (rates down to .000208333), persistent memory, shuffled/null/direct controls and held-out PN gain shift. Ten preflight tests, exact validation replay, eight development blocks and '+str(a['blocks'])+' fresh confirmation blocks passed audits and stage replays. The precision rule used development variance to request '+str(dev['precision']['uncapped_n'])+' blocks before rounding to '+str(a['blocks'])+'. No outcome-based confirmation extension.\n\n'+summary+' '+evidence+'.\n\nDevelopment selected different calibration strengths for the calibrated and optimized sham arms. A transparent addendum froze an additional exact-multiset sham before confirmation, with no extra search and descriptive inference only; all supplemental blocks audited and one replayed. The PN attenuation shift is invertible at input level and tests encoder/learner sensitivity, not raw-information destruction. No model-source changes occurred after development freeze. No subagents, paid compute, growth or second anatomy were used.\n\n'+next_action)
    row = '| EXP-007 | [Participation homeostasis](experiments/EXP-007-protocol.md) | completed / audited | Ten preflight tests; eight development and '+str(a['blocks'])+' confirmation blocks; matched-sham addendum | '+summary+' '+evidence+' |'
    edit('EXPERIMENTS.md', lambda t: t.replace('**Five scientific experiments completed:', '**Six scientific experiments completed:').replace('and EXP-006 persistent memory.**', 'EXP-006 persistent memory and EXP-007 homeostasis.**') if row in t else t.replace('**Five scientific experiments completed:', '**Six scientific experiments completed:').replace('and EXP-006 persistent memory.**', 'EXP-006 persistent memory and EXP-007 homeostasis.**').replace('\n\nCommon authoritative rules:', '\n'+row+'\n\nCommon authoritative rules:'))
    decision = '| D034 (2026-09-14) | Close EXP-007; advance to scoped cross-circuit validation | '+summary+' '+next_action+' '+evidence+' |'
    edit('DECISIONS.md', lambda t: t if decision in t else t+'\n'+decision+'\n')
    benchmark = '## EXP-007 completed participation extension\n\n'+summary+' '+evidence+'. The [frozen protocol](experiments/EXP-007-protocol.md) extends ordinary tuning below EXP-006\'s boundary and separates primary retention, practical margin, adaptation/tail noninferiority and capacity certification. A [matched-sham addendum](experiments/EXP-007-matched-sham-addendum.md) was frozen after development and before confirmation. Historical benchmark results remain unchanged. '+next_action
    edit('BENCHMARK_SPEC.md', lambda t: t if benchmark in t else t+'\n'+benchmark+'\n')
    manifest = read(ROOT/'research/experiment_manifest.json')
    manifest['experiments'] = [e for e in manifest['experiments'] if e['id'] != 'EXP-007']+[dict(id='EXP-007', status='completed', spec='experiments/EXP-007-protocol.md', source_ids=['S64', 'S68'], runtime_measured=True, next_action=next_action, development_blocks_completed=8, confirmation_blocks_completed=a['blocks'], validation_tests=10, results='experiments/EXP-007-results.md', run='research/runs/EXP-007-confirmation.json', primary=a['primary'], matched_sham_addendum='experiments/EXP-007-matched-sham-addendum.md')]
    manifest['scientific_experiments_completed'] = sum(e['status'] == 'completed' for e in manifest['experiments'])
    write(ROOT/'research/experiment_manifest.json', manifest)
    validation = read(ROOT/'research/validation_report.json')
    validation['scientific_experiments_run'] = manifest['scientific_experiments_completed']
    validation['exp007_confirmation_blocks'] = a['blocks']
    validation['exp007_validation_tests'] = 10
    validation['exp007_record'] = 'research/exp007_validation.json'
    validation['exp007_scope_note'] = 'Appended from EXP-007 audited records; historical foundation checks were not rerun in this completion step.'
    write(ROOT/'research/validation_report.json', validation)
    for stage in ('development', 'confirmation'):
        path = ROOT/f'research/runs/EXP-007-{stage}.json'; record = read(path)
        record['completion_record_source_sha256'] = sha256(Path(__file__))
        write(path, record)
    print(summary, flush=True)


if __name__ == '__main__': main()
