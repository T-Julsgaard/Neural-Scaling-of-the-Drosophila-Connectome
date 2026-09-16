"""Frozen factorial contrasts; task blocks are the only uncertainty units."""
import numpy as np
from .inputs import STAGES, stream

COVERAGE = 1 - .05/3


def factorial(a, b, c, d):
    return {"active_count": ((b-a)+(d-c))/2,
            "population": ((c-a)+(d-b))/2,
            "interaction": (d-c)-(b-a),
            "active_at_73": b-a, "active_at_110": d-c,
            "population_at_4": c-a, "population_at_6": d-b,
            "diagonal": d-a}


def interval(values, indices, coverage=.95):
    values = np.asarray(values, dtype=float)
    if values.shape != (indices.shape[1],) or not np.isfinite(values).all():
        raise ValueError("Expected one finite scalar per task block")
    tail = (1-coverage)/2
    bounds = np.quantile(values[indices].mean(axis=1), [tail, 1-tail]).tolist()
    return {"mean": float(values.mean()), "interval": bounds, "coverage": coverage,
            "block_values": values.tolist(), "half_width": (bounds[1]-bounds[0])/2}


def analyze(blocks, stage):
    expected = list(STAGES[stage][1])
    if len(blocks) != len(expected):
        raise ValueError("All planned blocks required")
    indices = stream(stage, expected[0], 2, 7).integers(0, len(blocks), (10000, len(blocks)))
    profiles, contrasts, primary = {}, {}, {}
    for arm in ("structured", "degree_null"):
        for readout in ("full", "bottleneck"):
            cells = {}
            for n, k in ((73,4), (73,6), (110,4), (110,6)):
                mode = f"{readout}_k{k}"
                selected = [[r for r in b if (r['size'],r['arm'],r['mode']) ==
                             (n, 'clone' if n == 73 else arm, mode)] for b in blocks]
                if any(len(r) != (1 if n == 73 else 3) for r in selected):
                    raise ValueError("Missing or duplicated replicate")
                metrics, values = {}, {}
                for metric in selected[0][0]['metrics']:
                    a = np.array([np.mean([r['metrics'][metric][0] for r in rows], axis=0) for rows in selected])
                    if metric.endswith('curve'):
                        metrics[metric] = {'mean': a.mean(axis=0).tolist(), 'block_values': a.tolist()}
                    else:
                        metrics[metric] = interval(a, indices)
                        values[metric] = a
                features = {}
                for prefix in ('cell_features', 'readout_features'):
                    features[prefix] = {}
                    for key in ('never_active_fraction', 'native_never_active_fraction',
                                'added_never_active_fraction', 'covariance_participation_rank',
                                'duplicate_normalized_columns'):
                        if key not in selected[0][0][prefix]:
                            continue
                        if selected[0][0][prefix][key] is not None:
                            a = [np.mean([r[prefix][key] for r in rows]) for rows in selected]
                            features[prefix][key] = interval(a, indices)
                profiles[f'{arm}_{n}_{mode}'] = {'metrics': metrics, **features,
                    'readout_weights': selected[0][0]['readout_weights'],
                    'edges_mean': float(np.mean([r['edges'] for rows in selected for r in rows])),
                    'contacts_mean': float(np.mean([r['contacts'] for rows in selected for r in rows]))}
                cells[n,k] = values
            for metric in cells[73,4]:
                values = factorial(*(cells[n,k][metric] for n,k in ((73,4),(73,6),(110,4),(110,6))))
                for name, a in values.items():
                    key = f'{arm}_{readout}_{name}'
                    contrasts.setdefault(key, {})[metric] = interval(a, indices)
                    if metric == 'acquisition':
                        contrasts[key][metric]['noninferiority_margin'] = -.02
                        contrasts[key][metric]['noninferiority_passed'] = contrasts[key][metric]['interval'][0] > -.02
                    if arm == 'structured' and readout == 'bottleneck' and metric == 'retention_after' and name in ('active_count','population','interaction'):
                        estimate = interval(a, indices, COVERAGE)
                        lo, hi = estimate['interval']
                        estimate.update({'metric': metric, 'practical_band': [-.03,.03],
                            'direction': 'positive' if lo > 0 else 'negative' if hi < 0 else 'unresolved',
                            'within_practical_band': lo > -.03 and hi < .03})
                        primary[name] = estimate
    for mode in ('full_k4','full_k6','bottleneck_k4','bottleneck_k6'):
        a, b = (profiles[f'{arm}_110_{mode}']['metrics'] for arm in ('structured','degree_null'))
        contrasts[f'structured_minus_null_{mode}'] = {m: interval(np.array(a[m]['block_values'])-np.array(b[m]['block_values']), indices)
                                                     for m in a if not m.endswith('curve')}
    return {'stage': stage, 'independent_blocks': expected, 'primary': primary,
            'profiles': profiles, 'secondary_contrasts': contrasts, 'bootstrap_resamples': 10000,
            'limits': ['One fixed anatomy; task-block uncertainty only',
                       'K changes per-winner activity at constant total activity',
                       'Secondary intervals are exploratory; same synthetic task families']}
