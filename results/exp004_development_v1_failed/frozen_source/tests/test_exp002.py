import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from exp002.assay import ValidationEpisode, stream
from exp002.data import ROOT, encode, load_projection
from exp002.rules import ARMS, Learner
from tests.decimal_reference import reference_trace

FIXTURE_PATH = ROOT / "tests/fixtures/bennett_eq8_256.json"
EVIDENCE = {}


def fixture_trace(fixture):
    model = Learner("feedback", fixture["eta"], fixture["initial_plus"], fixture["initial_minus"], fixture["gamma"])
    trace = []
    for choice, rewards in zip(fixture["choices"], fixture["rewards"]):
        values = model.values(fixture["activities"]).tolist()
        before = np.concatenate((model.plus, model.minus))
        diagnostic = model.update(fixture["activities"][choice], rewards[choice])
        after = np.concatenate((model.plus, model.minus))
        trace.append({"values": values, **diagnostic, "plus": model.plus.tolist(), "minus": model.minus.tolist(),
                      "weight_hits_zero": int(np.count_nonzero((before > 0) & (after == 0)))})
    return trace


class RuleTests(unittest.TestCase):
    def test_author_wrapper_preserves_eq8_and_final_update(self):
        from tools.prepare_bennett_reference import prepare, SOURCE_HASH
        original = ROOT / ".cache/research_assets/bennett/mb_mv_a.m"
        before = original.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = prepare(tmp)
            modified = (path / "mb_mv_a_fixture.m").read_text()
            source = before.decode()
            # Preserve the author's entire DAN/update section, including guards.
            segment = source[source.index("  % Compute DAN firing rates"):source.index("  % Update summed reward")]
            self.assertIn(segment, modified)
            self.assertEqual(np.loadtxt(path / "rewards.csv", delimiter=",").shape, (257, 2))
            self.assertEqual(np.loadtxt(path / "activities.csv", delimiter=",").shape, (20, 2))
            self.assertEqual(manifest["compared_updates"], 256)
            self.assertIn("j+1", (path / "run_reference.m").read_text())
        self.assertEqual(original.read_bytes(), before)
        EVIDENCE["author_wrapper"] = {"source_sha256": SOURCE_HASH, "arithmetic_source_preserved": True,
            "runtime_executed": False, "author_trials_with_sentinel": 257, "compared_updates": 256}

    def test_hand_computed_steps(self):
        # s=[1,0], equal .1 weights, r=+1 -> D+=(.1+1), D-=0.
        for arm, expected in (("frozen", .1), ("reward_only", .11), ("delta", .11), ("feedback", .111)):
            m = Learner.initial(arm, 2, eta=.01)
            d = m.update([1, 0], 1)
            np.testing.assert_allclose(m.plus, [expected, .1], rtol=0, atol=1e-15)
            np.testing.assert_allclose(m.minus, [.2-expected, .1], rtol=0, atol=1e-15)
            self.assertEqual(d["q"], 0)
            self.assertEqual(d["d_plus"], 1.1)
            self.assertEqual(d["d_minus"], 0)
        m = Learner("feedback", .1, [.01, .2], [.5, .2])
        # q=-.49, gamma*sum=.1, r=-1 -> D+=0,D-=.61.
        d = m.update([1, 0], -1)
        np.testing.assert_allclose(m.plus, [0, .2], rtol=0, atol=1e-15)
        np.testing.assert_allclose(m.minus, [.561, .2], rtol=0, atol=1e-15)
        self.assertAlmostEqual(d["q"], -.49)
        self.assertAlmostEqual(d["d_minus"], .61)

    def test_256_step_decimal_oracle(self):
        fixture = json.loads(FIXTURE_PATH.read_text())
        actual, expected = fixture_trace(fixture), reference_trace(fixture)
        self.assertEqual(len(actual), 256)
        max_error = 0.
        for a, e in zip(actual, expected):
            for key in ("values", "d_plus", "d_minus", "plus", "minus"):
                error = float(np.max(np.abs(np.asarray(a[key]) - np.asarray(e[key]))))
                max_error = max(max_error, error)
                self.assertLessEqual(error, 1e-10, key)
        positive = sum(a["both_strictly_positive"] for a in actual)
        match = sum(a["rate_match_regime"] for a in actual)
        zero_hits = sum(a["weight_hits_zero"] for a in actual)
        self.assertGreater(positive, 0)
        self.assertLess(match, 256)
        self.assertGreater(zero_hits, 0)
        chosen_q = np.array([a["q"] for a in actual])
        self.assertLess(chosen_q.min(), 0)
        self.assertGreater(chosen_q.max(), 0)
        EVIDENCE["equation_trace"] = {"trials": 256, "max_absolute_error": max_error,
            "both_strictly_positive_fraction": positive / 256, "rate_match_regime_fraction": match / 256,
            "weight_zero_crossings": zero_hits, "fixture_sha256": hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()}

    def test_rate_matching_including_boundary_and_failure_outside(self):
        errors = []
        # Equal initial conditions on each case prevent accumulated off-regime divergence.
        for reward in (-1, 1):
            for q in (-2., -1., 0., 1., 2.):
                s = np.ones(10)
                plus, minus = np.full(10, .3 + q/20), np.full(10, .3 - q/20)
                feedback = Learner("feedback", .001, plus, minus)
                delta = Learner("delta", .002, plus, minus)
                d = feedback.update(s, reward)
                delta.update(s, reward)
                error = float(max(np.max(abs(feedback.plus-delta.plus)), np.max(abs(feedback.minus-delta.minus))))
                if abs(reward-q) <= 1:
                    self.assertAlmostEqual(d["drive"], 2*(reward-d["q"]), places=12)
                    self.assertLessEqual(error, 1e-10)
                    errors.append(error)
                else:
                    self.assertGreater(error, 1e-5)
        fixture = json.loads(FIXTURE_PATH.read_text())
        # At the specified gamma=.1, compare each eligible update from identical
        # pre-state. Do not compare trajectories after off-regime steps diverge.
        local_errors = []
        f = Learner.initial("feedback", 20, .001)
        for choice, rewards in zip(fixture["choices"], fixture["rewards"]):
            d = Learner("delta", .002, f.plus, f.minus)
            diag = f.update(fixture["activities"][choice], rewards[choice])
            d.update(fixture["activities"][choice], rewards[choice])
            if diag["rate_match_regime"]:
                error = float(max(np.max(abs(f.plus-d.plus)), np.max(abs(f.minus-d.minus))))
                self.assertLessEqual(error, 1e-10)
                local_errors.append(error)
        self.assertGreater(len(local_errors), 0)
        # Supplementary fixture keeps the entire stream in the equivalence regime.
        f = Learner.initial("feedback", 20, .001, gamma=1)
        d = Learner.initial("delta", 20, .002, gamma=1)
        for choice, rewards in zip(fixture["choices"], fixture["rewards"]):
            diag = f.update(fixture["activities"][choice], rewards[choice])
            d.update(fixture["activities"][choice], rewards[choice])
            self.assertTrue(diag["rate_match_regime"])
            np.testing.assert_allclose(f.plus, d.plus, atol=1e-10, rtol=0)
            np.testing.assert_allclose(f.minus, d.minus, atol=1e-10, rtol=0)
        EVIDENCE["rate_matching"] = {"gamma_0_1_one_step_cases": len(errors), "maximum_error": max(errors),
            "gamma_0_1_eligible_trace_steps": len(local_errors), "gamma_0_1_trace_max_error": max(local_errors),
            "gamma_1_multistep_fixture_only": 256, "outside_regime_difference_detected": True}

    def test_probability_and_failure_guards(self):
        m = Learner("delta", .001, [1e5, 0], [0, 1e5])
        np.testing.assert_array_equal(m.probabilities(np.eye(2), .1), [1, 0])
        for arm in ARMS:
            np.testing.assert_array_equal(Learner.initial(arm, 2).probabilities(np.eye(2), .2), [.5, .5])
        for t in (0, -1, np.nan, np.inf):
            with self.assertRaises(ValueError):
                m.probabilities(np.eye(2), t)
        for s in ([np.nan, 1], [-1, 0], [1, 2, 3]):
            with self.assertRaises(ValueError):
                m.update(s, 1)
        with self.assertRaises(ValueError):
            m.update([1, 0], 0)
        n = Learner("reward_only", 1e6, [1e6, 0], [0, 0])
        old = n.plus.copy()
        with self.assertRaises(FloatingPointError):
            n.update([1, 0], 1)
        np.testing.assert_array_equal(n.plus, old)


class DataAndEpisodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projection, cls.provenance = load_projection()

    def test_data_orientation_identity_normalization_and_sparse_ties(self):
        p, provenance = self.projection, self.provenance
        self.assertEqual(p.shape, (40, 73))
        self.assertEqual(len(set(provenance["pn_ids"] + provenance["kc_ids"])), 113)
        np.testing.assert_allclose(p.sum(axis=0), 1, rtol=0, atol=1e-14)
        # Tiny asymmetric matrix gives an independently obvious orientation winner.
        tiny = np.array([[1., 0., .2], [0., 1., .8]])
        np.testing.assert_array_equal(encode(tiny, [1, 0], [2, 1, 0]), [10, 0, 0])
        for seed in range(5):
            priority = stream(seed, 1).permutation(73)
            s = encode(p, np.zeros(40), priority)
            self.assertEqual(np.count_nonzero(s), 4)
            self.assertEqual(s.sum(), 10.)
            np.testing.assert_array_equal(np.flatnonzero(s), np.sort(np.argsort(priority)[:4]))
        EVIDENCE["data"] = provenance

    def test_reject_changed_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "altered.zip"
            path.write_bytes(b"invalid input")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                load_projection(path)

    def test_task_schedules_and_chronology(self):
        for family in ("reversal", "interference"):
            e = ValidationEpisode(self.projection, family=family)
            np.testing.assert_array_equal(e.prototypes.sum(axis=1), [10]*4)
            self.assertFalse(np.array_equal(e.prototypes[0], e.prototypes[1]))
            preferred = [int(e.order[e.preferred(t)]) for t in (0, 127, 128, 255, 256, 383)]
            self.assertEqual(preferred, [0, 0, 1, 1, 0, 0] if family == "reversal" else [0]*6)
            clone = copy.deepcopy(e)
            cues = clone._present(0, clone.noise, .1)
            expected_p = clone.learner.probabilities(cues, clone.temperature)
            chosen = int(clone.uniforms[0] >= expected_p[0])
            with patch.object(e.learner, "update", wraps=e.learner.update) as update:
                record = e.step()
                update.assert_called_once()
                np.testing.assert_array_equal(update.call_args.args[0], cues[chosen])
                self.assertEqual(update.call_args.args[1], int(clone.rewards[0, chosen]))
            self.assertEqual(record["preferred_probability"], float(expected_p[e.preferred(0)]))
            # The unchosen outcome cannot affect this step's state or record.
            clone.rewards[0, 1-chosen] *= -1
            # Restore the RNG consumed above before stepping the counterfactual episode.
            clone.noise = stream(0, 3)
            self.assertEqual(clone.step(), record)
            np.testing.assert_array_equal(clone.learner.plus, e.learner.plus)

    def test_pairing_reset_and_validation_seed_isolation(self):
        a, b = [ValidationEpisode(self.projection, arm=arm, seed=4) for arm in ("delta", "feedback")]
        for key in ("prototypes", "uniforms", "rewards", "priority", "order"):
            np.testing.assert_array_equal(getattr(a, key), getattr(b, key))
        a.run_until(128)
        c = ValidationEpisode(self.projection, seed=4)
        np.testing.assert_array_equal(c.learner.plus, np.full(73, .1))
        for seed in (100, 1000):
            with self.assertRaises(ValueError):
                ValidationEpisode(self.projection, seed=seed)

    def test_probe_nonmutation_and_checkpoint_resume(self):
        checks = 0
        for family in ("reversal", "interference"):
            for seed in range(5):
                uninterrupted = ValidationEpisode(self.projection, family=family, seed=seed)
                uninterrupted.run_until(384)
                episode = ValidationEpisode(self.projection, family=family, seed=seed)
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "checkpoint.json"
                    for trial in (1, 127, 128, 255, 256, 383):
                        episode.run_until(trial)
                        before = episode.payload()
                        for sigma in (0., .1, .3):
                            self.assertTrue(0 <= episode.probe(sigma) <= 1)
                        self.assertEqual(episode.payload(), before)
                        episode.checkpoint(path)
                        episode = ValidationEpisode.restore(path, self.projection)
                        self.assertEqual(episode.payload(), before)
                        checks += 1
                    episode.run_until(384)
                self.assertEqual(episode.payload(), uninterrupted.payload())
        EVIDENCE["checkpoint_and_probes"] = {"families": 2, "validation_seeds": list(range(5)),
            "roundtrips": checks, "complete_state_and_scalar_traces_equal": True, "probe_sigmas": [0., .1, .3]}

    def test_checkpoint_corruption_and_graph_mismatch(self):
        e = ValidationEpisode(self.projection)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.json"
            e.checkpoint(path)
            with self.assertRaisesRegex(ValueError, "graph mismatch"):
                ValidationEpisode.restore(path, self.projection + 1)
            envelope = json.loads(path.read_text())
            envelope["payload"]["plus"][0] += 1
            path.write_text(json.dumps(envelope))
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                ValidationEpisode.restore(path, self.projection)


class ToyTests(unittest.TestCase):
    def test_separable_acquisition_and_reversal(self):
        scores = {}
        # Forced balanced exposure isolates the update rule from exploration luck.
        for arm in ("feedback", "delta"):
            m = Learner.initial(arm, 2, eta=.1)
            activities = np.eye(2)
            for t in range(128):
                choice = t % 2
                m.update(activities[choice], 1 if choice == 0 else -1)
            acquisition = float(m.probabilities(activities, .2)[0])
            for t in range(128):
                choice = t % 2
                m.update(activities[choice], 1 if choice == 1 else -1)
            reversal = float(m.probabilities(activities, .2)[1])
            self.assertGreater(acquisition, .95)
            self.assertGreater(reversal, .95)
            scores[arm] = {"acquisition": acquisition, "reversal": reversal}
        EVIDENCE["separable_toy"] = {"eta": .1, "temperature": .2, "trials_per_phase": 128,
            "coding_sum": 1, "forced_choices": True, "scores": scores, "scope": "implementation sanity fixture, not D05 performance"}

    def test_shuffled_rewards_remove_stable_cue_preference(self):
        summaries = {}
        for arm in ("feedback", "delta"):
            seed_scores = []
            for seed in range(5):
                rng = stream(seed, 4)
                # Shuffle a balanced schedule independently of the offered cue.
                rewards = rng.permutation(np.tile([-1, 1], 2048))
                m = Learner.initial(arm, 2, eta=.01)
                scores = []
                for t, r in enumerate(rewards):
                    if t >= 2048:
                        scores.append(float(m.probabilities(np.eye(2), .2)[0]))
                    m.update(np.eye(2)[t % 2], int(r))
                seed_scores.append(float(np.mean(scores)))
            self.assertTrue(all(abs(s-.5) < .1 for s in seed_scores), seed_scores)
            self.assertLess(abs(np.mean(seed_scores)-.5), .05)
            summaries[arm] = seed_scores
        EVIDENCE["shuffled_reward_toy"] = {"seed_scores": summaries, "eta": .01,
            "temperature": .2, "trials": 4096, "scored_trials": [2048, 4095],
            "acceptance": "Each seed mean within 0.1 of chance; across-seed mean within 0.05",
            "scope": "Balanced forced-choice toy; no hypothesis inference"}


if __name__ == "__main__":
    unittest.main()
