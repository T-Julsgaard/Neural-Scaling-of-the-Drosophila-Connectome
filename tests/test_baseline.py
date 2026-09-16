import copy
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from exp002.baseline import (BatchEpisode, Config, STAGES, Task, block_metrics, development_configs,
                            feature_statistics, feature_summary, interval, rng, select_configs)
from exp002.campaign import atomic_json, execute_block, read_json
from exp002.data import load_projection
from exp002.rules import Learner


class BaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projection, _ = load_projection()

    def test_batched_trajectories_match_scalar_rule(self):
        # All search settings, both representations, both task families.
        for ep in (0, 10):
            task = Task(self.projection, "validation", 2, ep)
            for rep in ("native", "pn"):
                configs = [c for c in development_configs() if c.representation == rep]
                batch = BatchEpisode(task, configs)
                batch.run_until()
                for i, c in enumerate(configs):
                    scalar = Learner.initial(c.arm, batch.activities.shape[-1], c.eta)
                    probs, choices = [], []
                    for t, cues in enumerate(batch.activities):
                        p = scalar.probabilities(cues, c.temperature)
                        choice = int(task.uniforms[t] >= p[0])
                        probs.append(p[task.preferred[t]])
                        choices.append(choice)
                        d = scalar.update(cues[choice], int(task.outcomes[t, choice]))
                        np.testing.assert_allclose(batch.trace[i, t, 3:6], [d["q"], d["d_plus"], d["d_minus"]], atol=1e-10, rtol=0)
                        # At each probe point independently average scalar probabilities.
                        if t in (127, 255, 383):
                            sigmas = (.1,) if t < 383 else (0., .1, .3)
                            for sigma in sigmas:
                                activity = task.probe_activities(rep, t+1, sigma)
                                expected = np.mean([scalar.probabilities(s, c.temperature)[task.preferred[0]] for s in activity])
                                j = (0 if t == 127 else 1) if t < 383 else {0.: 2, .1: 3, .3: 4}[sigma]
                                self.assertAlmostEqual(batch.probes[i, j], expected, places=10)
                    np.testing.assert_array_equal(batch.trace[i, :, 1], choices)
                    np.testing.assert_allclose(batch.trace[i, :, 0], probs, atol=1e-10, rtol=0)
                    np.testing.assert_allclose(batch.plus[i], scalar.plus, atol=1e-10, rtol=0)
                    np.testing.assert_allclose(batch.minus[i], scalar.minus, atol=1e-10, rtol=0)

    def test_tasks_are_paired_separated_and_chronological(self):
        tasks = [Task(self.projection, "validation", 0, ep) for ep in (0, 1, 10)]
        a = tasks[0]
        self.assertEqual(a.digest(), Task(self.projection, "validation", 0, 0).digest())
        self.assertNotEqual(a.digest(), tasks[1].digest())
        for t in tasks:
            np.testing.assert_array_equal(t.priority, a.priority)
            self.assertTrue(np.all(t.prototypes.sum(axis=1) == 10))
            self.assertFalse(np.array_equal(t.prototypes[0], t.prototypes[1]))
        np.testing.assert_array_equal(a.preferred[:128], a.preferred[256:])
        self.assertTrue(np.all(a.preferred[128:256] != a.preferred[:128]))
        self.assertTrue(np.all(tasks[2].preferred == tasks[2].preferred[0]))
        for stage, bad in (("validation", 100), ("development", 1000), ("confirmation", 100)):
            with self.assertRaises(ValueError):
                rng(stage, bad, 2)
        self.assertEqual(len({value[0] for value in STAGES.values()}), 3)
        self.assertFalse(set(STAGES["development"][1]) & set(STAGES["confirmation"][1]))

    def test_unchosen_outcomes_and_probes_cannot_change_learning(self):
        task = Task(self.projection, "validation", 0, 0)
        config = [Config("native", "delta", .001, .2)]
        a = BatchEpisode(task, config)
        alternate = copy.deepcopy(task)
        choice = int(task.uniforms[0] >= .5)
        alternate.outcomes[0, 1-choice] *= -1
        b = BatchEpisode(alternate, config)
        a.step()
        b.step()
        np.testing.assert_array_equal(a.plus, b.plus)
        np.testing.assert_array_equal(a.trace, b.trace)
        a.run_until(128)
        before = a.payload()
        for sigma in (0., .1, .3):
            self.assertTrue(np.all((a.probe(128, sigma) >= 0) & (a.probe(128, sigma) <= 1)))
        self.assertEqual(before, a.payload())

    def test_mid_episode_restore_matches_uninterrupted(self):
        for ep in (0, 10):
            task = Task(self.projection, "validation", 1, ep)
            configs = [Config("native", arm, .001, .2) for arm in ("delta", "feedback", "reward_only")]
            full = BatchEpisode(task, configs)
            full.run_until()
            resumed = BatchEpisode(task, configs)
            for trial in (0, 1, 127, 128, 255, 256, 383):
                resumed.run_until(trial)
                payload = json.loads(json.dumps(resumed.payload(), allow_nan=False))
                resumed = BatchEpisode.restore(task, payload)
                self.assertEqual(payload, resumed.payload())
            resumed.run_until()
            np.testing.assert_array_equal(resumed.trace, full.trace)
            np.testing.assert_array_equal(resumed.probes, full.probes)
            np.testing.assert_array_equal(resumed.plus, full.plus)

    def test_block_resume_and_integrity(self):
        configs = [Config("native", "frozen", 0., .2), Config("native", "delta", .001, .2)]
        contract = {"configs": [asdict(c) for c in configs], "test": "validation only"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            partial = execute_block(root / "resumed", "validation", 0, configs, contract, episode_limit=1)
            self.assertEqual(partial["next_episode"], 1)
            restored = execute_block(root / "resumed", "validation", 0, configs, contract)
            full = execute_block(root / "full", "validation", 0, configs, contract)
            self.assertEqual(restored["metrics"], full["metrics"])
            self.assertEqual(restored["features"], full["features"])
            self.assertTrue(all(x == .5 for x in restored["metrics"]["reversal_curve"][0]))
            with self.assertRaisesRegex(ValueError, "contract mismatch"):
                execute_block(root / "resumed", "validation", 0, configs, {"changed": True})
            artifact = root / "resumed/block_0/episode_00.npz"
            with artifact.open("ab") as f:
                f.write(b"corrupt")
            with self.assertRaisesRegex(ValueError, "artifact changed"):
                execute_block(root / "resumed", "validation", 0, configs, contract)
            path = root / "envelope.json"
            atomic_json(path, {"value": 1})
            envelope = json.loads(path.read_text())
            envelope["payload"]["value"] = 2
            path.write_text(json.dumps(envelope))
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                read_json(path)

    def test_metrics_use_correct_windows_and_families(self):
        trace = np.zeros((20, 1, 384, 10))
        probes = np.zeros((20, 1, 5))
        trace[:, :, 96:128, 0] = .8
        trace[:10, :, 128:160, 0] = .3
        trace[10:, :, 128:160, 0] = .99  # Must not contaminate reversal.
        probes[10:, :, 0], probes[10:, :, 1] = .9, .7
        probes[:, :, 2:] = [.85, .8, .6]
        m = block_metrics(trace, probes)
        for key, value in (("acquisition", .8), ("early_reversal", .3), ("retention_after", .7),
                           ("retention_change", -.2), ("selection_score", .6), ("robustness_0.3", .6)):
            self.assertAlmostEqual(m[key][0], value)
        with self.assertRaises(ValueError):
            block_metrics(trace[:19], probes[:19])

    def test_selection_ties_and_block_intervals(self):
        configs = development_configs()
        selected = select_configs(configs, {c.id: .5 for c in configs})
        self.assertTrue(all(c["eta"] == .0001 and c["temperature"] == .5 for c in selected.values()))
        result = interval([.5] * 10, "development")
        self.assertEqual(result["interval"], [.5, .5])
        a = np.arange(10) / 10
        # Paired equal arms have identically zero differences despite between-block variation.
        self.assertEqual(interval(a-a, "development")["interval"], [0., 0.])

    def test_feature_diagnostics_and_direct_pn_normalization(self):
        task = Task(self.projection, "validation", 0, 0)
        native, pn = task.activities("native"), task.activities("pn")
        self.assertTrue(np.all((native > 0).sum(axis=-1) == 4))
        np.testing.assert_allclose(native.sum(axis=-1), 10)
        np.testing.assert_allclose(pn.sum(axis=-1), 10)
        self.assertEqual(pn.shape, (384, 2, 40))
        stats = feature_statistics(np.array([[1., 0., 0.], [0., 1., 0.]]))
        summary = feature_summary(stats)
        self.assertAlmostEqual(summary["covariance_participation_rank"], 1.)
        self.assertEqual(summary["participation"], [.5, .5, 0.])
        self.assertEqual(summary["never_active_fraction"], 1/3)


if __name__ == "__main__":
    unittest.main()
