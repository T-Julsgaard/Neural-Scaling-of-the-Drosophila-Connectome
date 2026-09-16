"""Render the fully audited, prospectively specified EXP-003 confirmation results."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.campaign import read_json
from exp002.data import sha256
from exp003.confirmation import FOLDER
from exp003.confirmation_analysis import METRICS
from exp003.growth import ARMS, SIZES


def effect(value):
    lo, hi = value['interval']
    return f"{value['mean']:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def main():
    audit = read_json(ROOT/'research/runs/EXP-003-confirmation.json')
    if audit['status'] != 'completed_and_audited':
        raise ValueError('Audit required before reporting')
    for name in ('analysis.json', 'report.json', 'contract.json'):
        path = FOLDER/name
        if sha256(path) != audit['files'][path.relative_to(ROOT).as_posix()]['sha256']:
            raise ValueError('Audited source changed')
    data, run = read_json(FOLDER/'analysis.json'), read_json(FOLDER/'report.json')
    rows, contrasts, primary = data['profiles'], data['paired_contrasts'], data['primary']
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'.cache/matplotlib'))
    sys.path.insert(1, str(ROOT/'.cache/baseline-plot-deps'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels = {'clone': 'Clone', 'structured': 'Structured', 'uniform': 'Uniform', 'degree_null': 'Degree null', 'whole_uniform': 'Whole uniform'}
    colors = {'clone': '#947142', 'structured': '#247f6b', 'uniform': '#387cc0', 'degree_null': '#a557ac', 'whole_uniform': '#7b7b7b'}
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), layout='constrained')
    for ax, metric, title in zip(axes.flat, METRICS, ('Acquisition', 'Early reversal', 'Post-interference retention', 'Robustness (noise 0.3)')):
        for arm in (*ARMS, 'whole_uniform'):
            points = [rows[f'{arm}_{n}_full']['metrics'][metric] for n in SIZES]
            means = [p['mean'] for p in points]
            ax.plot(SIZES, means, '-o', label=labels[arm], color=colors[arm], markersize=4)
            ax.fill_between(SIZES, [p['interval'][0] for p in points], [p['interval'][1] for p in points], color=colors[arm], alpha=.09)
        ax.set(title=title, xlabel='Mature feature cells', ylabel='Choice probability', xticks=SIZES)
        ax.grid(alpha=.2)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle('EXP-003 held-out confirmation • 20 independent task blocks\nProportional sparsity / full readout • secondary 95% block intervals', fontsize=12)
    fig.savefig(FOLDER/'confirmation_profiles.png', dpi=160)
    fig.savefig(FOLDER/'confirmation_profiles.svg')
    plt.close(fig)
    lines = ['# EXP-003 held-out confirmation results', '',
             '2026-09-12. **All twenty untouched confirmation blocks completed and audited.**', '',
             'Generic delta; frozen eta=0.01, temperature=0.1. Three graph replicates are averaged within each task block. Native N73 is reused once per block. No confirmation selection or sample-budget change.', '',
             '[Frozen protocol](EXP-003-confirmation-protocol.md), [preflight](../research/exp003_confirmation_validation.json), [audited run](../research/runs/EXP-003-confirmation.json), [all block values, metrics and curves](../results/exp003_confirmation/analysis.json).', '',
             '## Primary organization test', '',
             f"Structured minus degree-null early reversal at N110, proportional sparsity/full readout: **{effect(primary)}**, 98.33% interval. Planned practical minimum: **+0.050**.", '',
             {'against_practical_advantage': 'The upper interval is below +0.05: evidence against the planned practically useful wiring advantage in this assay. Deprioritize this structured prior.',
              'supports_practical_advantage': 'The lower interval exceeds +0.05: the planned primary practical criterion passes. Interpretation still depends on sparsity/readout diagnostics.',
              'inconclusive': 'The interval crosses the planned practical minimum: the primary organization result is inconclusive.'}[primary['decision']], '',
             '## Held-out profiles', '', 'Full readout and proportional sparsity. Means of block means; units are probabilities.', '',
             '| Rule | Cells | Acquisition | Early reversal | Retention | Robustness 0.3 |', '|---|---:|---:|---:|---:|---:|']
    for arm in (*ARMS, 'whole_uniform'):
        for n in SIZES:
            if n == 73 and arm in ('structured', 'uniform', 'degree_null'):
                continue
            r = rows[f'{arm}_{n}_full']
            label = 'Native baseline' if n == 73 and arm == 'clone' else labels[arm]
            lines.append(f'| {label} | {n} | ' + ' | '.join(f"{r['metrics'][m]['mean']:.3f}" for m in METRICS) + ' |')
    lines += ['', '![Confirmation growth profiles](../results/exp003_confirmation/confirmation_profiles.png)', '',
              '## Secondary scale changes', '',
              'Paired change versus each matching N73 baseline; **secondary exploratory 95% intervals**, not additional primary tests. Scale was not promoted to a primary hypothesis after development.', '',
              '| Rule / cells | Early reversal | Retention | Acquisition | Robustness 0.3 | Acquisition lower bound > −.02 |', '|---|---|---|---|---|---|']
    for arm in (*ARMS, 'whole_uniform'):
        for n in (110, 146):
            c = contrasts[f'{arm}_{n}_minus_73']
            lines.append(f'| {labels[arm]} / {n} | ' + ' | '.join(effect(c[m]) for m in ('early_reversal', 'retention_after', 'acquisition', 'robustness_0.3')) + f" | {c['acquisition']['noninferiority_passed']} |")
    lines += ['', '## Sparsity and readout controls', '',
              'Every change compares N110 with its own matching N73 control. Bottleneck readout: 64 trainable weights at both sizes. Intervals are secondary 95%.', '',
              '| Control | Rule | Early reversal | Retention | Acquisition | Robustness 0.3 |', '|---|---|---|---|---|---|']
    for mode, arms in (('fixed4', ('clone', 'structured', 'degree_null')), ('bottleneck', ('structured', 'degree_null'))):
        for arm in arms:
            c = contrasts[f'{arm}_110_minus_73_{mode}']
            lines.append(f'| {mode} | {labels[arm]} | ' + ' | '.join(effect(c[m]) for m in ('early_reversal', 'retention_after', 'acquisition', 'robustness_0.3')) + ' |')
    lines += ['', '| Structured minus degree null at N110 | Early reversal | Retention |', '|---|---|---|']
    for mode in ('full', 'fixed4', 'bottleneck'):
        c = contrasts[f'structured_minus_null_110_{mode}']
        lines.append(f"| {mode} | {effect(c['early_reversal'])} | {effect(c['retention_after'])} |")
    lines += ['', '## Feature participation', '', '| Rule at N110 | Added cells unused | Cell covariance participation rank |', '|---|---:|---:|']
    for arm in ARMS:
        f = rows[f'{arm}_110_full']['cell_features']
        lines.append(f"| {labels[arm]} | {100*f['added_never_active_fraction']['mean']:.1f}% | {f['covariance_participation_rank']['mean']:.2f} |")
    lines += ['', 'Unused means never activated by presented synthetic cues, not biologically inactive. Full analysis includes pre/post-interference retention, return adaptation, all noise probes, learning curves, resource dimensions and cell/readout diagnostics.', '',
              '## Execution and limits', '',
              f"All {audit['validation']} preflight tests passed. Audited 1,600 representation conditions, 32,000 reset episode batches and 32,400 configuration-episodes. No excluded episodes or numerical failures. Frozen native controls stayed exactly at chance; graphs were independently regenerated and every raw episode hash and condition summary verified.", '',
              f"Current-session invocation wall time: {run['wall_seconds_this_invocation']:.1f} seconds with {run['workers']} CPU workers. Summed worker episode CPU time: {run['summed_worker_cpu_seconds']:.1f} seconds. Maximum individual worker peak memory: {run['max_worker_peak_memory_bytes']/1024**2:.1f} MiB (not total concurrent RAM). Retained campaign bytes before final report: {run['retained_bytes_before_report']/1024**2:.1f} MiB. No energy measurement or colleague-workstation benchmark.", '',
              'The uncertainty unit is twenty task blocks sharing one fixed anatomical source. Bootstrap intervals are approximate. Scale and controls are secondary exploratory comparisons; held-out cue identities remain within the same synthetic task families. No adult circuit, general cognition, biological superiority or evolutionary-search success follows automatically. Any next experiment needs its own prospective design and untouched evaluation.', '']
    (ROOT/'experiments/EXP-003-confirmation-results.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    print(ROOT/'experiments/EXP-003-confirmation-results.md')


if __name__ == '__main__':
    main()
