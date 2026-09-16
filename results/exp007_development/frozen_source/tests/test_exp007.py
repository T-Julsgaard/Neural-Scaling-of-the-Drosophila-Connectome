import unittest
import numpy as np
from exp002.data import load_projection
from exp006 import memory as old
from exp007.homeostasis import *
from exp007.campaign import specs, CONDITIONS, REPORT


class HomeostasisTests(unittest.TestCase):
    def setUp(self):
        self.p = load_projection()[0]; self.priority = np.arange(73)
        self.cfg = dict(k=6, strength=0., eta=.001, temperature=.1)

    def test_encoder_equivalence_norm_invariance(self):
        u = rng('validation', 7, 20).random((10, 40))
        for k in (4, 6):
            x = encode(u, self.p, self.priority, k, np.zeros(73))
            np.testing.assert_array_equal(x, old.encode(u, 'native'+str(k), self.p, self.priority))
            np.testing.assert_array_equal(x, encode(u, self.p, self.priority, k, np.ones(73)*.02))
            np.testing.assert_allclose(x.sum(-1), 10)
            np.testing.assert_allclose((x*x).sum(-1), 100/k)
            np.testing.assert_array_equal((x > 0).sum(-1), k)

    def test_box_and_compensation(self):
        u = calibration_pool()[:512]
        theta, rec = fit(self.p, u, self.priority, .5)
        self.assertLess(abs(theta.sum()), 1e-10)
        self.assertLessEqual(abs(theta).max(), rec['bound']+1e-12)
        before, after, target = map(np.array, (rec['before'], rec['after'], rec['target']))
        self.assertLess(np.mean((after-target)**2), np.mean((before-target)**2))
        shuffled_theta = theta[rng('validation', 7, 21).permutation(73)]
        np.testing.assert_array_equal(np.sort(theta), np.sort(shuffled_theta))
        self.assertFalse(np.array_equal(theta, shuffled_theta))

    def test_pool_separation(self):
        a, b = calibration_pool(), calibration_pool(True)
        self.assertEqual(a.shape, (4096, 40)); self.assertNotEqual(digest(a), digest(b))
        self.assertNotEqual(digest(a), digest(task('validation', 0, 6, 16, 'per_pair')['obs'][0]))

    def test_candidate_budget_lower_boundary(self):
        for method in METHODS:
            grid = candidates(method)
            self.assertEqual(len(grid), 32)
            self.assertEqual(len({tuple(v.values()) for v in grid}), 32)
            self.assertLessEqual(min(c['eta'] for c in grid), (.01/3)/16+1e-14)
        self.assertEqual(sum(c['k'] == 6 for c in candidates('ordinary')), 16)

    def test_zero_offset_sequence_equivalence(self):
        t = task('validation', 7, 6, 2, 'per_pair', 4)
        configs = [self.cfg, {**self.cfg, 'eta': .003}]
        new = sequence(t, 'ordinary', self.p, self.priority, np.zeros(73), configs)
        reference = old.sequence(t, 'native6', self.p, self.priority, [(c['eta'], c['temperature']) for c in configs])
        for name in ('history', 'reverse', 'prereversal', 'final', 'boundaries', 'cosine'):
            np.testing.assert_array_equal(new[name], reference[name])
        np.testing.assert_array_equal(new['boundaries'][1:, 0], new['boundaries'][:-1, 1])
        self.assertEqual(int(new['presented'].sum()), 2*128*2*6)
        np.testing.assert_array_equal(new['chosen'].sum(-1), 2*128*6)

    def test_scalar_chosen_update_margin(self):
        r = rng('validation', 6, 22); x = r.random((2, 73))
        plus, minus = r.random((1, 73))+.5, r.random((1, 73))+.5
        eta, temp, uniform = .0001, .1, .7
        p0 = 1/(1+np.exp((sum((plus[0]-minus[0])*x[1])-sum((plus[0]-minus[0])*x[0]))/temp))
        chosen = int(uniform >= p0)
        a, b = old.update(plus, minus, x, np.array([1., -1.]), uniform, [eta], [temp])
        change = eta*x[chosen]*([1., -1.][chosen]-sum((plus[0]-minus[0])*x[chosen]))
        np.testing.assert_allclose(a[0], plus[0]+change, atol=1e-14)
        np.testing.assert_allclose(b[0], minus[0]-change, atol=1e-14)
        pairdiff = r.random(73)-r.random(73)
        self.assertAlmostEqual(float(((a-b)-(plus-minus))@pairdiff), 2*float(change@pairdiff), places=12)

    def test_shift_and_task_invariants(self):
        t = task('validation', 8, 6, 16, 'per_pair', 4); q = shifted(t)
        np.testing.assert_array_equal(q['p'][..., :20], .5*t['p'][..., :20])
        np.testing.assert_array_equal(q['p'][..., 20:], t['p'][..., 20:])
        np.testing.assert_array_equal(q['labels'], t['labels'])
        np.testing.assert_array_equal(t['p'].sum(-1), 10)
        np.testing.assert_array_equal((t['p'][:, 0]*t['p'][:, 1]).sum(-1), 6)
        self.assertEqual(len(np.unique(t['p'].reshape(-1, 40), axis=0)), 32)
        t2 = task('validation', 8, 6, 8, 'per_pair', 4)
        np.testing.assert_array_equal(t2['obs'][0], t['obs'][0][:8])

    def test_metrics_replay_oracle(self):
        t = task('validation', 9, 2, 2, 'per_pair', 4)
        cfg = dict(k=0, strength=0., eta=.003, temperature=.1)
        a = sequence(t, 'oracle', self.p, self.priority, np.zeros(73), [cfg])
        b = sequence(t, 'oracle', self.p, self.priority, np.zeros(73), [cfg])
        for name in a: np.testing.assert_array_equal(a[name], b[name])
        v = summarize(a)[0]
        self.assertGreater(v[0], .95); self.assertAlmostEqual(v[3], 0.)
        self.assertEqual(v[7], 0.)

    def test_null_preservation(self):
        q, meta = random_projection(self.p, rng('validation', 11, 8))
        np.testing.assert_array_equal(np.sort(q, axis=0), np.sort(self.p, axis=0))
        np.testing.assert_array_equal((q > 0).sum(1), (self.p > 0).sum(1))
        self.assertEqual(meta['accepted'], 40*np.count_nonzero(self.p))

    def test_probe_read_only(self):
        t = task('validation', 12, 2, 2, 'per_pair', 4)
        x = encode(t['probes'][0], self.p, self.priority, 6, np.zeros(73))
        a, b = np.ones((1, 73)), np.zeros((1, 73)); before = digest(a, b)
        values = probe(a, b, x, [.1], t['labels'])
        self.assertEqual(before, digest(a, b)); self.assertTrue(((values >= 0) & (values <= 1)).all())
