"""Regenerate every graph/task and recompute metrics from all raw episodes."""
import json
import time
import numpy as np
from exp002.campaign import atomic_json, now, read_json
from exp002.data import ROOT, sha256
from exp002.baseline import Config
from .campaign import folder as stage_folder, freeze
from .engine import summarize_condition
from .inputs import STAGES, conditions, Inputs, EpisodeTask, grid
from .analysis import analyze
from exp003.growth import load_base


def audit(stage):
    started = time.perf_counter()
    FOLDER = stage_folder(stage)
    contract_hash = freeze(stage)
    report = read_json(FOLDER/'report.json')
    count = len(STAGES[stage][1])
    if report['status'] != 'complete' or report['contract_sha256'] != contract_hash:
        raise ValueError('Incomplete/mismatched report')
    if report['blocks'] != count or report['excluded_episodes'] or report['numerical_failures']:
        raise ValueError('Unexpected count/exclusions/failures')
    blocks, files, episodes, config_episodes, rows_total = [], {}, 0, 0, 0
    base = load_base()
    def remember(path):
        files[path.relative_to(ROOT).as_posix()] = {'sha256': sha256(path), 'bytes': path.stat().st_size}
    for b in STAGES[stage][1]:
        folder = FOLDER/f'block_{b}'
        summary = read_json(folder/'summary.json')
        if report['block_summary_sha256'][str(b)] != sha256(folder/'summary.json') or summary['block'] != b or summary['contract_sha256'] != contract_hash:
            raise ValueError('Block identity/hash mismatch')
        inputs = [Inputs(stage, b, ep) for ep in range(20)]
        input_hashes = [i.digest() for i in inputs]
        if summary['input_hashes'] != input_hashes:
            raise ValueError('Input pairing mismatch')
        expected = conditions(base, stage, b)
        if [r['id'] for r in summary['conditions']] != [r['id'] for r in expected]:
            raise ValueError('Missing/duplicated/reordered conditions')
        for row, condition in zip(summary['conditions'], expected):
            local = folder/row['id']
            graph = condition['graph']
            if read_json(local/'graph.json') != graph.record or row['graph_sha256'] != graph.sha256:
                raise ValueError('Graph regeneration mismatch')
            configs = grid()
            if row['size'] == 73 and row['mode'].startswith('full'):
                configs += [Config('native', 'frozen', 0., .2)]
            from dataclasses import asdict
            identity = {'contract_sha256': contract_hash, 'graph_sha256': graph.sha256,
                        'condition': row['id'], 'mode': row['mode'], 'inputs': input_hashes,
                        'configs': [asdict(c) for c in configs]}
            state = read_json(local/'checkpoint.json')
            ids = [c.id for c in configs]
            if state['identity'] != identity or state['next_episode'] != 20 or len(state['artifacts']) != 20 or state['config_ids'] != ids:
                raise ValueError('Checkpoint identity/chronology mismatch')
            for ep, item in enumerate(state['artifacts']):
                path = local/item['file']
                task = EpisodeTask(inputs[ep], graph, row['mode'])
                if item['file'] != f'episode_{ep:02d}.npz' or sha256(path) != item['sha256'] or item['task_hash'] != task.digest():
                    raise ValueError('Episode artifact identity/hash mismatch')
                with np.load(path, allow_pickle=False) as data:
                    if str(data['task_hash']) != task.digest() or str(data['inputs_hash']) != input_hashes[ep]:
                        raise ValueError('Saved episode input mismatch')
                    np.testing.assert_array_equal(data['config_ids'], ids)
                    if data['trace'].shape[:2] != (len(configs), 384) or data['probes'].shape != (len(configs), 5):
                        raise ValueError('Incomplete trace/probes')
                    for key in ('trace', 'probes', 'plus', 'minus'):
                        if not np.isfinite(data[key]).all():
                            raise ValueError('Nonfinite episode')
                    for key in ('plus', 'minus'):
                        if (data[key] < 0).any() or (data[key] > 1e6).any():
                            raise ValueError('Invalid weights')
                    if len(configs) == 2:
                        np.testing.assert_array_equal(data['trace'][1, :, 0], .5)
                        np.testing.assert_array_equal(data['probes'][1], .5)
                        np.testing.assert_array_equal(data['plus'][1], .1)
                        np.testing.assert_array_equal(data['minus'][1], .1)
                remember(path)
                episodes += 1
                config_episodes += len(configs)
            recalculated = summarize_condition(local, state, condition)
            if row != recalculated or read_json(local/'summary.json') != recalculated:
                raise ValueError('Metrics/features differ from raw artifacts')
            for name in ('graph.json', 'checkpoint.json', 'summary.json'):
                remember(local/name)
            rows_total += 1
        blocks.append(summary['conditions'])
        remember(folder/'summary.json')
        print(json.dumps({'audited_blocks': len(blocks), 'episodes': episodes}), flush=True)
    if (rows_total, episodes, config_episodes) != (count*28, count*560, count*600):
        raise ValueError('Unexpected campaign counts')
    for key, value in (('conditions', rows_total), ('episode_batches', episodes), ('configuration_episodes', config_episodes)):
        if report[key] != value:
            raise ValueError('Resource report count mismatch')
    analysis = analyze(blocks, stage)
    analysis['contract_sha256'] = contract_hash
    atomic_json(FOLDER/'analysis.json', analysis)
    for name in ('contract.json', 'report.json', 'analysis.json'):
        remember(FOLDER/name)
    record = {'run_id': f'EXP-004-{stage}-v1.0', 'status': 'completed_and_audited', 'audited_utc': now(),
              'validation': read_json(ROOT/'research/exp004_validation.json')['tests_run'],
              'blocks': count, 'graph_conditions': rows_total, 'episode_batches': episodes,
              'configuration_episodes': config_episodes, 'excluded_episodes': 0, 'numerical_failures': 0,
              'resources': report, 'primary': analysis['primary'], 'files': files,
              'audit_seconds': time.perf_counter()-started, 'limits': analysis['limits']}
    atomic_json(ROOT/f'research/runs/EXP-004-{stage}.json', record)
    print(json.dumps({k: record[k] for k in ('status','blocks','episode_batches','audit_seconds')}), flush=True)
    return record
