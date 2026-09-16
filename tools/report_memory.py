"""Rebuild descriptive figures, tables and provenance from audited EXP-006 arrays."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[1]/'.cache/baseline-plot-deps'))
os.environ['MPLCONFIGDIR'] = str(Path(__file__).resolve().parents[1]/'.cache/matplotlib')
import csv
import json
import platform
import subprocess
import numpy as np
from exp006.campaign import ROOT, read, write, folder, interval
from exp006.memory import FAMILIES, LOADS, OVERLAPS, REGIMES, METRICS
from exp002.data import sha256


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    target = folder('confirmation')
    analysis = read(target/'analysis.json'); contract = read(target/'contract.json')
    assert read(target/'audit.json')['status'] == 'passed'
    data = [np.load(target/f'block_{b}.npz') for b in contract['blocks']]
    names = {'native4': 'Native K4', 'native6': 'Native K6', 'direct': 'Direct input', 'random4': 'Random K4', 'random6': 'Random K6', 'oracle': 'Identity oracle'}
    colors = ['#a27521', '#1764ab', '#16866a', '#b99860', '#76a4cc']
    for regime in REGIMES:
        fig, axes = plt.subplots(2, 2, figsize=(10.5, 7), sharex=True, sharey=True)
        for row, metric in enumerate(('retention', 'noise_retention')):
            for col, overlap in enumerate(OVERLAPS):
                ax = axes[row, col]
                for family, color in zip(FAMILIES[:5], colors):
                    stats = [analysis['profiles'][f's{overlap}_{regime}_l{load}'][family][metric] for load in LOADS]
                    means = np.array([a['mean'] for a in stats])*100
                    bounds = np.array([a['interval'] for a in stats])*100
                    ax.plot(LOADS, means, 'o--' if family.startswith('random') else 'o-', color=color, label=names[family], linewidth=1.7, markersize=4)
                    ax.fill_between(LOADS, bounds[:, 0], bounds[:, 1], color=color, alpha=.08)
                ax.axhline(80, color='#777777', linestyle=':', linewidth=1)
                ax.set_title(f'Overlap {overlap}/10 · noise {0.1 if row == 0 else 0.3}')
                ax.set_xticks(LOADS); ax.set_ylim(45, 101); ax.grid(alpha=.15)
                if row == 1: ax.set_xlabel('Sequential cue pairs')
                if col == 0: ax.set_ylabel('Final preferred-choice probability (%)')
        fig.legend(*axes[0, 0].get_legend_handles_labels(), loc='lower center', ncol=5, frameon=False)
        fig.suptitle('Persistent memory · '+('128 presentations per pair' if regime == 'per_pair' else '512 acquisition presentations total'))
        fig.tight_layout(rect=(0, .05, 1, .96))
        fig.savefig(target/f'retention_{regime}.png', dpi=170)
        plt.close(fig)
    rows = []; age_rows = []; geometry = {}
    for s in OVERLAPS:
        for regime in REGIMES:
            for load in LOADS:
                key = f's{s}_{regime}_l{load}'
                for family in FAMILIES:
                    for metric in METRICS:
                        stats = analysis['profiles'][key][family][metric]
                        rows.append([s, regime, load, family, metric, stats['mean'], *stats['interval']])
                    reps = range(3 if family.startswith('random') else 1)
                    for pair in range(load):
                        forgetting = []; retention = []
                        for a in data:
                            h = np.mean([a[f'{key}_{family}_{r}_history'][0, 0] for r in reps], axis=0)
                            forgetting.append(h[pair, pair]-h[-1, pair]); retention.append(h[-1, pair])
                        age_rows.append([s, regime, load, family, pair, load-1-pair, (load-1-pair)*(128 if regime == 'per_pair' else 512//load), np.mean(retention), np.mean(forgetting), *interval(forgetting)['interval']])
                    vals = []
                    for a in data:
                        repvalues = []
                        for r in reps:
                            prefix = f'{key}_{family}_{r}_'
                            cosine = a[prefix+'cosine']
                            within = np.mean([cosine[2*i, 2*i+1] for i in range(load)])
                            mask = np.arange(2*load)[:, None]//2 != np.arange(2*load)[None]//2
                            repvalues.append([within, cosine[mask].mean(), float(a[prefix+'stability']), float(a[prefix+'unused']), np.mean(cosine[mask] > 1-1e-12)])
                        vals.append(np.mean(repvalues, axis=0))
                    geometry[key+'_'+family] = {m: interval(np.array(vals)[:, i]) for i, m in enumerate(('within_pair_cosine', 'between_memory_cosine', 'noise_01_stability', 'unused_fraction', 'between_memory_identical_fraction'))}
                overlaps = np.array([a[key+'_input_overlap'] for a in data])
                mask = np.arange(2*load)[:, None]//2 != np.arange(2*load)[None]//2
                geometry[key+'_inputs'] = {'within_pair_intersection': s, 'across_memory_intersection_mean': float(overlaps[:, mask].mean()), 'across_memory_min': float(overlaps[:, mask].min()), 'across_memory_max': float(overlaps[:, mask].max())}
    for name, header, values in [('profiles.csv', ['overlap', 'regime', 'load', 'family', 'metric', 'mean', 'lower95', 'upper95'], rows), ('memory_age.csv', ['overlap', 'regime', 'load', 'family', 'pair', 'subsequent_pairs', 'subsequent_presentations', 'retention', 'forgetting', 'forgetting_lower95', 'forgetting_upper95'], age_rows)]:
        with (target/name).open('w', newline='') as f:
            w = csv.writer(f); w.writerow(header); w.writerows(values)
    write(target/'geometry.json', geometry)
    for stage in ('development', 'confirmation'):
        d = folder(stage); c = read(d/'contract.json')
        records = [read(d/f'block_{b}.json') for b in c['blocks']]
        git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
        payload = {'experiment': 'EXP-006', 'protocol_version': '2026-09-14', 'stage': stage, 'status': 'completed', 'start_utc': c['created_utc'], 'end_utc': __import__('time').strftime('%Y-%m-%dT%H:%M:%SZ', __import__('time').gmtime()), 'code_commit': git.stdout.strip(), 'dirty_worktree': True, 'source_hashes': c['source'], 'environment': {k: c[k] for k in ('python', 'numpy', 'platform', 'executable')}, 'hardware': {'processor': platform.processor(), 'logical_processors': os.cpu_count(), 'hardware_id': 'current-local-session; not colleague workstation', 'CIM_inventory': 'access denied; no hardware model inferred'}, 'configuration_sha256': sha256(d/'contract.json'), 'seed_derivation': '[6006, stage 1 development / 2 confirmation, block, component, suffix]; full derivation frozen in exp006/memory.py', 'planned_blocks': len(c['blocks']), 'completed_blocks': len(records), 'condition_sequences_per_block': 16, 'experimental_families': list(FAMILIES[:5]), 'random_circuits_per_block': 3, 'tuning_candidates_per_family': 8 if stage == 'development' else 1, 'checkpoint_paths_hashes': {f'block_{r["block"]}.npz': r['sha256'] for r in records}, 'validation': str((ROOT/'research/exp006_validation.json').relative_to(ROOT)), 'audit': read(d/'audit.json'), 'exclusions': [], 'scientific_failures': [], 'infrastructure_notes': ['WindowsApps Python alias unavailable; used bundled CPython before generating samples.', 'CIM hardware query denied; environment and process resource counters recorded.'], 'compute': {'sum_block_wall_seconds': sum(r['wall_seconds'] for r in records), 'sum_block_cpu_seconds': sum(r['cpu_seconds'] for r in records), 'peak_worker_memory_bytes': max(r['peak_memory_bytes'] for r in records), 'npz_bytes': sum(p.stat().st_size for p in d.glob('*.npz')), 'workers': 3, 'audit_replay_cost_included': False}, 'analysis': 'results/exp006_confirmation/analysis.json' if stage == 'confirmation' else 'results/exp006_development/selection.json', 'limitations': ['One static larval circuit and synthetic clustered cue families.', 'Only bounded tuning; no unique causal mediation identified.', 'Randomized circuit mixing diagnostics do not establish uniform sampling.', 'Bootstrap confidence bounds are approximate; extreme simultaneous tails use 200000 resamples.'], 'followup_decision': 'Use observed persistent-memory limit to design priority 3 homeostasis; growth remains conditional.'}
        payload['protocol_deviations'] = ['Preflight stream-independence test constructed prototypes for development block100/overlap6 and confirmation block1000/overlap6 before stage freeze. No learner, reward stream or performance evaluation was run on those fixtures before the stages. No confirmation-driven selection or exclusions.']
        payload['report_source_sha256'] = sha256(Path(__file__))
        payload['artifact_hashes'] = {p.relative_to(ROOT).as_posix(): sha256(p) for p in d.glob('*') if p.is_file() and p.suffix != '.npz'}
        write(ROOT/f'research/runs/EXP-006-{stage}.json', payload)
    for a in data: a.close()
    print(json.dumps({'geometry_hard_native4': geometry['s6_per_pair_l16_native4'], 'geometry_hard_native6': geometry['s6_per_pair_l16_native6']}))


if __name__ == '__main__': main()
