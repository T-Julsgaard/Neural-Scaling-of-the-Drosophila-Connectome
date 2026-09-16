"""Prospective freeze, bounded execution and evidence gates for EXP-004."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import json
import math
import shutil
import subprocess
import time
import unittest
import numpy as np
from exp002.campaign import atomic_json, read_json, environment, now, text_hash
from exp002.data import ROOT, sha256
from exp003.growth import load_base
from .inputs import STAGES, grid
from .engine import execute_block, retained_bytes


def folder(stage):
    if stage not in ('development','evaluation'):
        raise ValueError('Invalid campaign stage')
    return ROOT/f'results/exp004_{stage}'


def snapshot():
    files = [*ROOT.glob('exp002/*.py'), *ROOT.glob('exp003/*.py'), *ROOT.glob('exp004/*.py'),
             *ROOT.glob('tests/test_*.py'), ROOT/'tools/run_activity_diagnostic.py',
             ROOT/'experiments/EXP-004-protocol.md']
    return {p.relative_to(ROOT).as_posix(): text_hash(p) for p in sorted(files)}


def verify_prior():
    # Preserve all prior scientific code and the audited confirmation summaries.
    prior = read_json(ROOT/'results/exp003_confirmation/contract.json')['contract']
    for name, expected in prior['code_snapshot'].items():
        if text_hash(ROOT/name) != expected:
            raise ValueError('Prior frozen source changed: '+name)
    audit_path = ROOT/'research/runs/EXP-003-confirmation.json'
    audit = read_json(audit_path)
    if audit['status'] != 'completed_and_audited':
        raise ValueError('Prior confirmation not audited')
    for name, item in audit['files'].items():
        if not name.endswith('.npz') and (sha256(ROOT/name) != item['sha256'] or (ROOT/name).stat().st_size != item['bytes']):
            raise ValueError('Prior audited summary changed: '+name)
    return {'audit_sha256': sha256(audit_path), 'contract_sha256': sha256(ROOT/'results/exp003_confirmation/contract.json')}


def planning():
    old = read_json(ROOT/'results/exp003_confirmation/analysis.json')
    # Historical paired SDs are context only; factorial missing cells did not exist.
    historical = {}
    for key, value in old['paired_contrasts'].items():
        if 'retention_after' in value:
            historical[key] = float(np.std(value['retention_after']['block_values'], ddof=1))
    report = read_json(ROOT/'results/exp003_confirmation/report.json')
    return {'created_utc': now(), 'evaluation_blocks': 32, 'conditions': 896, 'episodes': 17920,
            'planning_sd_assumption': .07, 'z': 2.394,
            'expected_half_widths_by_sd': {str(sd): 2.394*sd/math.sqrt(32) for sd in (.04,.07,.10)},
            'approximate_80percent_detectable_effect': (2.394+.842)*.07/math.sqrt(32),
            'historical_retention_contrast_sds_context_only': historical,
            'wall_seconds_proxy': report['wall_seconds_this_invocation']*17920/report['episode_batches'],
            'retained_bytes_proxy': report['retained_bytes_before_report']*17920/report['episode_batches'],
            'free_disk_bytes': shutil.disk_usage(ROOT).free,
            'limits': 'Assumed factorial SD; no power guarantee. Wall proxy excludes new audit.'}


def validate():
    if any((folder(s)/'contract.json').exists() for s in ('development','evaluation')):
        raise ValueError('Cannot replace validation after freeze')
    prior = verify_prior()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests'), pattern='test_*.py', top_level_dir=str(ROOT)))
    record = {'status': 'passed' if result.wasSuccessful() and not result.skipped else 'failed',
              'tests_run': result.testsRun, 'failures': [str(t)+tb for t,tb in result.failures+result.errors],
              'created_utc': now(), 'code_snapshot': snapshot(), 'environment': environment(), 'prior': prior}
    atomic_json(ROOT/'research/exp004_validation.json', record)
    atomic_json(ROOT/'research/exp004_planning.json', planning())
    if record['status'] != 'passed':
        raise ValueError('Preflight failed')
    return record


def freeze(stage):
    output = folder(stage)
    validation_path = ROOT/'research/exp004_validation.json'
    validation = read_json(validation_path)
    if validation['status'] != 'passed' or validation['code_snapshot'] != snapshot() or validation['environment'] != environment():
        raise ValueError('Code/environment is not validated')
    prerequisite = None
    if stage == 'evaluation':
        audit_path = ROOT/'research/runs/EXP-004-development.json'
        audit = read_json(audit_path)
        if audit['status'] != 'completed_and_audited':
            raise ValueError('Development audit required')
        for name, item in audit['files'].items():
            if sha256(ROOT/name) != item['sha256'] or (ROOT/name).stat().st_size != item['bytes']:
                raise ValueError('Development artifact changed: '+name)
        prerequisite = {'audit_sha256': sha256(audit_path), 'resources': audit['resources']}
    design = {'protocol': 'EXP-004-1.1', 'stage': stage, 'blocks': list(STAGES[stage][1]),
              'seed_root': 5, 'conditions_per_block': 28, 'episodes_per_condition': 20,
              'code_snapshot': snapshot(), 'environment': environment(), 'source': load_base().provenance,
              'validation_sha256': sha256(validation_path), 'planning_sha256': sha256(ROOT/'research/exp004_planning.json'),
              'development': prerequisite, 'selected': [c.id for c in grid()],
              'git_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    path = output/'contract.json'
    if path.exists():
        if read_json(path)['contract'] != design:
            raise ValueError('Frozen contract mismatch')
    else:
        output.mkdir(parents=True, exist_ok=True)
        if any(output.glob('block_*')):
            raise ValueError('Artifacts without contract')
        atomic_json(path, {'frozen_utc': now(), 'contract': design})
    return sha256(path)


def run(stage, workers=3):
    if workers not in (1,2,3):
        raise ValueError('Use at most three workers')
    output = folder(stage)
    contract_hash = freeze(stage)
    if (output/'report.json').exists():
        report = read_json(output/'report.json')
        if report['contract_sha256'] != contract_hash:
            raise ValueError('Report contract mismatch')
        return report
    start, utc = time.perf_counter(), now()
    invocation = output/f'invocation_{time.time_ns()}.json'
    atomic_json(invocation, {'started_utc': utc, 'status': 'started', 'workers': workers, 'contract_sha256': contract_hash})
    blocks = []
    try:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(execute_block, output, stage, b, contract_hash): b for b in STAGES[stage][1]}
            for future in as_completed(futures):
                blocks.append(future.result())
                if time.perf_counter()-start > 7*86400:
                    raise RuntimeError('Seven-day limit')
                print(json.dumps({'stage': stage, 'blocks_complete': len(blocks), 'of': len(futures)}), flush=True)
    except BaseException as error:
        atomic_json(output/f'failure_{time.time_ns()}.json', {'created_utc': now(), 'error': repr(error)})
        raise
    rows = [r for b in blocks for r in b['conditions']]
    retained = retained_bytes(output)
    if retained >= 10*1024**3:
        raise RuntimeError('Artifact limit')
    report = {'status': 'complete', 'stage': stage, 'blocks': len(blocks), 'conditions': len(rows),
              'episode_batches': len(rows)*20, 'configuration_episodes': sum(len(r['config_ids'])*20 for r in rows),
              'excluded_episodes': 0, 'numerical_failures': 0, 'started_utc': utc, 'completed_utc': now(),
              'contract_sha256': contract_hash, 'environment': environment(), 'workers': workers,
              'wall_seconds_this_invocation': time.perf_counter()-start,
              'summed_worker_cpu_seconds': sum(r['resources']['cpu_seconds'] for r in rows),
              'max_worker_peak_memory_bytes': max(r['resources']['peak_worker_memory_bytes'] for r in rows),
              'retained_bytes_before_report': retained,
              'block_summary_sha256': {str(b['block']): sha256(output/f"block_{b['block']}/summary.json") for b in blocks}}
    atomic_json(output/'report.json', report)
    atomic_json(invocation, {'started_utc': utc, 'completed_utc': now(), 'status': 'complete', 'workers': workers,
                             'wall_seconds': time.perf_counter()-start, 'contract_sha256': contract_hash})
    print(json.dumps(report), flush=True)
    return report
