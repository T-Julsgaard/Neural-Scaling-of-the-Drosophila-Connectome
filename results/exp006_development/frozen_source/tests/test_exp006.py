import unittest
import numpy as np
from exp006.memory import *


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.p = load_projection()[0]
        self.priority = np.arange(73)

    def test_prototype_overlap_unique(self):
        for s in OVERLAPS:
            p, labels = prototypes('validation', 0, s)
            np.testing.assert_array_equal(p.sum(-1), 10)
            np.testing.assert_array_equal((p[:, 0]*p[:, 1]).sum(-1), s)
            self.assertEqual(len(np.unique(p.reshape(32, 40), axis=0)), 32)
            cross = p.reshape(32, 40) @ p.reshape(32, 40).T
            self.assertTrue((cross >= s).all())
            self.assertEqual(set(labels), {0, 1})

    def test_exposure_and_prefix_pairing(self):
        a = task('validation', 0, 6, 2, 'per_pair', 4)
        b = task('validation', 0, 6, 16, 'total', 4)
        np.testing.assert_array_equal(a['obs'][0][:, :32], b['obs'][0][:2])
        np.testing.assert_array_equal(a['outcomes'][0][:, :32], b['outcomes'][0][:2])
        np.testing.assert_array_equal(a['uniforms'][0][:, :32], b['uniforms'][0][:2])
        np.testing.assert_array_equal(a['probes'], b['probes'][:, :2])
        self.assertEqual(b['count']*16, 512)
        self.assertEqual(a['count']*2, 256)

    def test_independent_stages(self):
        self.assertFalse(np.array_equal(prototypes('development', 100, 6)[0], prototypes('confirmation', 1000, 6)[0]))

    def test_null_preserves_contacts_degrees(self):
        q, m = random_projection(self.p, rng('validation', 0, 8))
        np.testing.assert_array_equal(np.sort(q, axis=0), np.sort(self.p, axis=0))
        np.testing.assert_array_equal((q > 0).sum(0), (self.p > 0).sum(0))
        np.testing.assert_array_equal((q > 0).sum(1), (self.p > 0).sum(1))
        self.assertEqual(m['accepted'], 40*m['edges'])
        self.assertFalse(np.array_equal(q, self.p))

    def test_scalar_batch_update_reference(self):
        r = rng('validation', 0, 19)
        x = r.random((2, 40)); plus = r.random((2, 40)); minus = r.random((2, 40))
        eta, temp = [.003, .01], [.1, .2]
        a, b = update(plus, minus, x, np.array([1, -1]), .6, eta, temp)
        for c in range(2):
            q = [sum((plus[c, n]-minus[c, n])*x[j, n] for n in range(40)) for j in range(2)]
            prob0 = 1/(1+np.exp((q[1]-q[0])/temp[c]))
            choice = int(.6 >= prob0)
            delta = eta[c]*x[choice]*([1, -1][choice]-q[choice])
            np.testing.assert_allclose(a[c], np.maximum(0, plus[c]+delta), atol=1e-14)
            np.testing.assert_allclose(b[c], np.maximum(0, minus[c]-delta), atol=1e-14)

    def test_probe_read_only_and_preference(self):
        p = np.array([[1., 0.]])
        m = np.zeros_like(p); x = np.array([[[[1., 0.], [0., 1.]]]])
        before = digest(p, m)
        a = probe(p, m, x, [.1], [0]); b = probe(p, m, x, [.1], [1])
        self.assertGreater(a.item(), .99)
        np.testing.assert_allclose(a+b, 1)
        self.assertEqual(before, digest(p, m))

    def test_persistence_replay_and_scalar_sequence(self):
        t = task('validation', 0, 6, 2, 'total', 4)
        a = sequence(t, 'native6', self.p, self.priority, GRID[:2])
        b = sequence(t, 'native6', self.p, self.priority, GRID[:2])
        for k in a: np.testing.assert_array_equal(a[k], b[k])
        self.assertEqual(a['boundaries'][1, 0], a['boundaries'][0, 1])
        self.assertNotEqual(a['boundaries'][0, 0], a['boundaries'][0, 1])
        for i in range(2):
            scalar = sequence(t, 'native6', self.p, self.priority, [GRID[i]])
            np.testing.assert_allclose(a['history'][i], scalar['history'][0], atol=1e-14)
            np.testing.assert_allclose(a['final'][:, i], scalar['final'][:, 0], atol=1e-14)

    def test_oracle_task_adequacy(self):
        t = task('validation', 1, 6, 4, 'per_pair', 4)
        a = sequence(t, 'oracle', self.p, self.priority, [GRID[0]])
        self.assertGreater(metrics(a)[0, 0], .8)
        self.assertGreater(metrics(a)[0, 5], .8)
        self.assertGreater(metrics(a)[0, 6], .8)
        u = t['p']; ids = np.arange(8).reshape(4, 2)
        np.testing.assert_array_equal(encode(u, 'oracle', self.p, self.priority, ids), encode(u*0, 'oracle', self.p, self.priority, ids))

    def test_encoding_and_metrics(self):
        u = task('validation', 0, 2, 2, 'per_pair', 4)['p']
        for k in (4, 6):
            x = encode(u, f'native{k}', self.p, self.priority)
            np.testing.assert_array_equal((x > 0).sum(-1), k)
            np.testing.assert_allclose(x.sum(-1), 10)
        h = np.array([[[[.9, np.nan], [.6, .8]], [[.8, np.nan], [.5, .7]]]])
        r = np.array([[[.7, .6], [.6, .5]]])
        np.testing.assert_allclose(metrics({'history': h, 'reverse': r})[0], [.7, .6, .85, .15, .6, .7, .6, .6])


if __name__ == '__main__': unittest.main()
