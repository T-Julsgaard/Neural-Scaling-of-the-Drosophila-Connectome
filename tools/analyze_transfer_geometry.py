"""Paired descriptive contrasts for prespecified hard-condition diagnostics."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from exp008.campaign import ROOT, folder, read, write, interval
from exp002.data import sha256


def main():
    out = folder('confirmation'); c = read(out/'contract.json')
    assert read(out/'audit.json')['status'] == 'passed'
    differences = []
    for b in c['blocks']:
        with np.load(out/f'block_{b}.npz') as a:
            vals = []
            for m in ('homeostasis', 'baseline_high'):
                prefix = f'c5_{m}_g0_r0_'; counts = a[prefix+'presented']; diag = a[prefix+'diagnostics'][0]
                cosine = a[prefix+'cosine']; mask = np.arange(32)[:, None]//2 != np.arange(32)[None]//2
                vals.append(np.array([np.mean(counts == 0), counts.sum()**2/(counts@counts), a[prefix+'stability'].mean(), cosine[mask].mean(), diag[2]/diag[3], *a[prefix+'rank_gaps']]))
            differences.append(vals[0]-vals[1])
    names = ('unused_presented', 'effective_presented', 'noise_stability', 'cross_memory_cosine', 'old_pair_margin_abs_change', 'clean_rank_gap', 'noisy_rank_gap')
    values = {m: interval(np.array(differences)[:, i]) for i, m in enumerate(names)}
    write(out/'geometry_contrasts.json', dict(scope='Prespecified diagnostics; descriptive paired 95% intervals, not causal mediation or new primary tests', contrast='homeostasis minus uncalibrated K48; load16/overlap16/128 per pair', values=values, source_sha256=sha256(Path(__file__))))
    print(values)


if __name__ == '__main__': main()
