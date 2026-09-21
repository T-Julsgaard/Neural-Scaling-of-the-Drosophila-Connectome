"""Descriptive report artifacts derived from audited EXP-008 checkpoints."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[1]/'.cache/baseline-plot-deps'))
os.environ['MPLCONFIGDIR'] = str(Path(__file__).resolve().parents[1]/'.cache/matplotlib')
import csv
import json
import subprocess
import numpy as np
from exp008.campaign import ROOT, folder, read, write, interval, CONDITIONS, SHIFT, REPORT, NAMES
from exp002.data import sha256


def plot_comparison(out, a):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    previous = read(ROOT/'results/exp007_confirmation/analysis.json')['primary']['ordinary']
    current = a['primary']['ordinary']
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.axvspan(-3, 3, color='#dbeafe', alpha=.8, label='Prespecified equivalence band')
    ax.axvline(0, color='#475569', linewidth=1)
    ax.text(0, 1.52, 'Prespecified +/-3 pp equivalence band', ha='center', fontsize=10, color='#475569')
    for y, value, color in ((1, previous, '#64748b'), (0, current, '#0369a1')):
        mean = 100*value['mean']; lo,hi = np.array(value['interval'])*100
        ax.errorbar(mean,y,xerr=[[mean-lo],[hi-mean]],fmt='o',color=color,capsize=5,markersize=7)
        ax.annotate(f'{mean:+.2f} [{lo:+.2f}, {hi:+.2f}] pp', (mean,y), xytext=(0,15), textcoords='offset points', ha='center', fontsize=10)
    ax.set_yticks([1,0],['Larval projection / EXP-007','Adult gamma-main / EXP-008'])
    limits = np.array([previous['interval'],current['interval']])*100
    ax.set_xlim(min(-5,limits.min()-2),max(5,limits.max()+2));ax.set_ylim(-.6,1.7)
    ax.set_xlabel('Calibrated minus ordinary tuning: retention difference (percentage points)')
    ax.set_title('Transfer of the bounded participation procedure')
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.15)
    fig.text(.5,.015,'98.333333% paired intervals; different anatomies and declared transfer adapters',ha='center',fontsize=9,color='#475569')
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/'transfer_comparison.png',dpi=180);plt.close(fig)


def main(plot=True):
    out = folder('confirmation'); a = read(out/'analysis.json'); c = read(out/'contract.json')
    assert read(out/'audit.json')['status'] == 'passed'
    raw = [np.load(out/f'block_{b}.npz') for b in c['blocks']]
    geometry = {}; rows = []; ages = []
    for ci, cond in enumerate(CONDITIONS+SHIFT):
        key = '_'.join(map(str, cond)); load = cond[2]
        for method in REPORT:
            for metric in NAMES:
                v = a['profiles'][key][method][metric]
                rows.append([*cond, method, metric, v['mean'], *v['interval']])
            values = []; histories = []
            for block in raw:
                reps = []; hrep = []
                for rep in range(3 if ('random' in method or 'sham' in method) else 1):
                    prefix = f'c{ci}_{method}_g0_r{rep}_'
                    counts = block[prefix+'presented']; chosen = block[prefix+'chosen'][0]
                    diag = block[prefix+'diagnostics'][0]
                    cosine = block[prefix+'cosine']; mask = np.arange(2*load)[:, None]//2 != np.arange(2*load)[None]//2
                    gap = block[prefix+'rank_gaps']
                    reps.append([np.mean(counts == 0), counts.sum()**2/(counts@counts), np.mean(chosen == 0), chosen.sum()**2/(chosen@chosen), block[prefix+'stability'].mean(), cosine[mask].mean(), np.mean(cosine[mask] > 1-1e-12), diag[0]/(diag[4]*len(counts)*2), diag[1]/diag[4], diag[2]/max(diag[3], 1), *gap])
                    hrep.append(block[prefix+'history'][0, 0])
                values.append(np.mean(reps, axis=0)); histories.append(np.mean(hrep, axis=0))
            labels = ['unused_presented', 'effective_presented', 'unused_chosen', 'effective_chosen', 'noise_stability', 'cross_memory_cosine', 'collision_fraction', 'clipped_coordinate_fraction', 'update_norm', 'old_pair_margin_abs_change', 'clean_rank_gap', 'noisy_rank_gap']
            geometry[key+'_'+method] = {name: interval(np.array(values)[:, i]) for i, name in enumerate(labels) if np.isfinite(np.array(values)[:, i]).all()}
            h = np.array(histories)
            for pair in range(load):
                v = interval(h[:, -1, pair]); f = interval(h[:, pair, pair]-h[:, -1, pair])
                ages.append([*cond, method, pair, (load-1-pair)*(128 if cond[1] == 'per_pair' else 512//load), v['mean'], *v['interval'], f['mean'], *f['interval']])
    write(out/'geometry.json', geometry)
    for name, header, vals in [('profiles.csv', ['overlap', 'regime', 'load', 'shift', 'method', 'metric', 'mean', 'lower95', 'upper95'], rows), ('memory_age.csv', ['overlap', 'regime', 'load', 'shift', 'method', 'pair', 'subsequent_presentations', 'retention', 'lower95', 'upper95', 'forgetting', 'lower95_forgetting', 'upper95_forgetting'], ages)]:
        with (out/name).open('w', newline='') as f:
            w = csv.writer(f); w.writerow(header); w.writerows(vals)
    for r in raw: r.close()
    resources = {}
    for stage in ('development', 'confirmation'):
        d = folder(stage); contract = read(d/'contract.json'); records = [read(d/f'block_{b}.json') for b in contract['blocks']]
        resource = dict(cpu_seconds=sum(v['cpu_seconds'] for v in records), summed_worker_wall_seconds=sum(v['wall_seconds'] for v in records), peak_worker_bytes=max(v['peak_memory_bytes'] for v in records), checkpoint_bytes=sum(p.stat().st_size for p in d.glob('*.npz')))
        resources[stage] = resource
        try:
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        except Exception: commit = None
        write(ROOT/f'research/runs/EXP-008-{stage}.json', dict(experiment='EXP-008', stage=stage, status='completed', blocks=len(contract['blocks']), source_hashes=contract['source'], code_commit=commit, dirty_worktree=True, environment={**{k: contract[k] for k in ('python', 'numpy', 'platform', 'executable')}, 'hardware_id': os.environ.get('COMPUTERNAME'), 'logical_cpu_count': os.cpu_count(), 'execution_location': 'current local desktop, not the separately reported colleague workstation'}, resources=resource, started_utc=contract['created_utc'], ended_utc=max(v['completed_utc'] for v in records), planned_blocks=contract['blocks'], completed_blocks=contract['blocks'], seed_namespace=8008, checkpoint_hashes={str(b):read(d/f'block_{b}.json')['sha256'] for b in contract['blocks']}, failures=[], exclusions=[], protocol_version='1.0', anatomy_sha256=read(ROOT/'results/exp008_anatomy/record.json')['projection_sha256'], validation_sha256=contract['validation_sha256'], contract_sha256=sha256(d/'contract.json'), audit_sha256=sha256(d/'audit.json'), calibration_sha256=contract['calibration_sha256'], results='experiments/EXP-008-results.md'))
    write(out/'resources.json', resources)
    if plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        names = {'ordinary': 'Ordinary tuning', 'homeostasis': 'Calibrated K48', 'sham': 'Shuffled offsets', 'direct': 'Direct input'}
        colors = ['#64748b', '#0369a1', '#b45309', '#15803d']
        for regime in ('per_pair', 'total'):
            fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.2), sharex=True)
            for row, metric in enumerate(('retention', 'worst_pair')):
                for col, overlap in enumerate((5, 16)):
                    ax = axes[row, col]
                    for (method, label), color in zip(names.items(), colors):
                        stats = [a['profiles'][f'{overlap}_{regime}_{load}_False'][method][metric] for load in (4, 16)]
                        mean = np.array([v['mean'] for v in stats])*100; bounds = np.array([v['interval'] for v in stats])*100
                        ax.plot((4, 16), mean, 'o-', color=color, label=label, linewidth=1.8, markersize=4)
                        ax.fill_between((4, 16), bounds[:, 0], bounds[:, 1], color=color, alpha=.1)
                    ax.set_title(f'Overlap {overlap}/26 · '+('mean retention' if row == 0 else 'worst pair per sequence'))
                    ax.axhline(80 if row == 0 else 50, color='#999', linestyle=':', linewidth=1)
                    ax.set_xticks((4, 16)); ax.set_ylim((45, 101) if row == 0 else (0, 101)); ax.grid(alpha=.15)
                    if col == 0: ax.set_ylabel('Preferred-choice probability (%)')
                    if row == 1: ax.set_xlabel('Sequential cue pairs')
            fig.legend(*axes[0, 0].get_legend_handles_labels(), loc='lower center', ncol=4, frameon=False)
            fig.suptitle('EXP-008 · '+('128 presentations per pair' if regime == 'per_pair' else '512 acquisition presentations total'))
            fig.tight_layout(rect=(0, .05, 1, .96)); fig.savefig(out/f'retention_{regime}.png', dpi=160); plt.close(fig)
    if plot: plot_comparison(out, a)
    print(json.dumps(dict(resources=resources, hard_geometry={m: geometry['16_per_pair_16_False_'+m] for m in ('baseline_high', 'homeostasis', 'sham')})), flush=True)


if __name__ == '__main__': main('--no-plot' not in sys.argv)
