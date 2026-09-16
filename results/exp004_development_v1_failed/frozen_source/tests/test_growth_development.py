import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from exp002.baseline import BatchEpisode, Config, Task
from exp002.campaign import atomic_json, read_json
from exp002.rules import Learner
from exp003.assay import encode_observations
from exp003.campaign import execute_condition
from exp003.development import (EpisodeTask, Inputs, conditions, encode_fast, graphs_for, grid,
                                 rebuild, select_shared, stream)
from exp003.growth import ARMS, SIZES, load_base


class GrowthDevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load_base()

    def test_fresh_streams_pairing_schedules_and_stage_guard(self):
        hashes = set()
        for block in (0, 1):
            for ep in (0, 1, 10, 11):
                inputs = Inputs("validation", block, ep)
                self.assertNotIn(inputs.digest(), hashes)
                hashes.add(inputs.digest())
                self.assertEqual(inputs.digest(), Inputs("validation", block, ep).digest())
                original = Task(self.base.raw / self.base.raw.sum(axis=0), "validation", block, ep)
                self.assertNotEqual(inputs.digest(), original.digest())
                np.testing.assert_array_equal(inputs.prototypes.sum(axis=1), 10)
                np.testing.assert_array_equal(inputs.preferred[256:], inputs.preferred[0])
                np.testing.assert_array_equal(inputs.preferred[128:256], 1-inputs.preferred[0] if ep < 10 else inputs.preferred[0])
                expected = np.random.Generator(np.random.PCG64(np.random.SeedSequence([3, 0, block, 0, 0, 0, 5, ep]))).random(384)
                np.testing.assert_array_equal(inputs.uniforms, expected)
                graphs = graphs_for(self.base, "validation", block, 110, 0)
                tasks = [EpisodeTask(inputs, graph) for graph in graphs.values()]
                for task in tasks:
                    self.assertIs(task.observations, inputs.observations)
                    self.assertIs(task.outcomes, inputs.outcomes)
                    np.testing.assert_array_equal(task.priority, tasks[0].priority)
        for stage, block in (("confirmation", 1000), ("development", 0), ("validation", 100)):
            with self.assertRaises(ValueError):
                Inputs(stage, block, 0)

    def test_campaign_graphs_reconstruct_and_whole_base_is_paired(self):
        for block in (0, 1):
            for rep in range(3):
                replacement = None
                for size in SIZES:
                    graphs = graphs_for(self.base, "validation", block, size, rep)
                    for arm, graph in graphs.items():
                        replay = rebuild(self.base, json.loads(json.dumps(graph.record)))
                        np.testing.assert_array_equal(replay.raw, graph.raw)
                        np.testing.assert_array_equal(np.sort(graph.raw, axis=0)[:, :73], np.sort(self.base.raw, axis=0))
                        if arm != "whole_uniform":
                            np.testing.assert_array_equal(graph.raw[:, :73], self.base.raw)
                    whole = graphs["whole_uniform"].raw
                    np.testing.assert_array_equal(whole[:, 73:], graphs["uniform"].raw[:, 73:])
                    if replacement is not None:
                        np.testing.assert_array_equal(whole[:, :73], replacement)
                    replacement = whole[:, :73]
                    bad = copy.deepcopy(graphs["structured"].record)
                    bad["block"] = 100
                    with self.assertRaises(ValueError):
                        rebuild(self.base, bad)
        rows = conditions(self.base, "validation", 0)
        self.assertEqual(len(rows), 80)
        self.assertEqual(sum(r["mode"] == "full" and r["arm"] in ARMS for r in rows), 49)
        self.assertEqual(sum(r["arm"] == "whole_uniform" for r in rows), 15)

    def test_fast_encoding_exact_scalar_equivalence_including_ties(self):
        inputs = Inputs("validation", 0, 0)
        observations = np.concatenate([inputs.observations[:20].reshape(-1, 40), inputs.prototypes,
                                       np.zeros((1, 40)), np.ones((1, 40)),
                                       inputs.probe_observations(384, 0).reshape(-1, 40)])
        for size in SIZES:
            for graph in graphs_for(self.base, "validation", 0, size, 0).values():
                task = EpisodeTask(inputs, graph)
                for sparsity, bottleneck in (("proportional", False), ("fixed4", False), ("proportional", True)):
                    expected = encode_observations(graph, observations, task.priority, sparsity, bottleneck)
                    actual = encode_fast(graph, observations, task.priority, sparsity, bottleneck)
                    np.testing.assert_array_equal(actual, expected)

    def test_no_growth_identity_and_grown_scalar_probes_resume(self):
        for ep in (0, 10):
            inputs = Inputs("validation", 0, ep)
            reference = None
            for arm, graph in graphs_for(self.base, "validation", 0, 73, 0).items():
                if arm == "whole_uniform":
                    continue
                batch = BatchEpisode(EpisodeTask(inputs, graph), grid())
                batch.run_until()
                if reference is not None:
                    np.testing.assert_array_equal(batch.trace, reference.trace)
                    np.testing.assert_array_equal(batch.probes, reference.probes)
                reference = batch
            graph = graphs_for(self.base, "validation", 0, 110, 0)["structured"]
            for mode in ("full", "fixed4", "bottleneck"):
                task = EpisodeTask(inputs, graph, mode)
                configs = [grid()[8]]
                batch = BatchEpisode(task, configs)
                batch.run_until()
                scalar = Learner.initial("delta", batch.plus.shape[-1], configs[0].eta)
                probe_index = 0
                for t, cues in enumerate(batch.activities):
                    p = scalar.probabilities(cues, configs[0].temperature)
                    choice = int(task.uniforms[t] >= p[0])
                    self.assertEqual(choice, batch.trace[0, t, 1])
                    self.assertAlmostEqual(p[task.preferred[t]], batch.trace[0, t, 0], places=10)
                    scalar.update(cues[choice], int(task.outcomes[t, choice]))
                    if t+1 in (128, 256, 384):
                        for sigma in ((.1,) if t+1 < 384 else (0., .1, .3)):
                            probe = task.probe_activities("native", t+1, sigma)
                            p = np.mean([scalar.probabilities(c, configs[0].temperature)[task.preferred[0]] for c in probe])
                            self.assertAlmostEqual(p, batch.probes[0, probe_index], places=10)
                            probe_index += 1
                np.testing.assert_allclose(batch.plus[0], scalar.plus, atol=1e-10, rtol=0)
                for stop in (0, 127, 128, 255, 256, 383):
                    partial = BatchEpisode(task, configs)
                    partial.run_until(stop)
                    weights = partial.plus.copy()
                    partial.probe(384, .3)
                    np.testing.assert_array_equal(weights, partial.plus)
                    restored = BatchEpisode.restore(task, json.loads(json.dumps(partial.payload())))
                    restored.run_until()
                    np.testing.assert_array_equal(restored.trace, batch.trace)
                    np.testing.assert_array_equal(restored.probes, batch.probes)
                    changed = EpisodeTask(inputs, graph, "fixed4" if mode == "full" else "full")
                    with self.assertRaises(ValueError):
                        BatchEpisode.restore(changed, partial.payload())

    def test_unchosen_rewards_do_not_change_learning(self):
        inputs = Inputs("validation", 0, 0)
        graph = graphs_for(self.base, "validation", 0, 110, 0)["uniform"]
        batch = BatchEpisode(EpisodeTask(inputs, graph), [grid()[6]])
        batch.run_until()
        modified = copy.deepcopy(inputs)
        choices = batch.trace[0, :, 1].astype(int)
        modified.outcomes[np.arange(384), 1-choices] *= -1
        other = BatchEpisode(EpisodeTask(modified, graph), [grid()[6]])
        other.run_until()
        np.testing.assert_array_equal(batch.trace, other.trace)

    def test_episode_replay_after_uncheckpointed_write_and_corruption(self):
        inputs = [Inputs("validation", 0, ep) for ep in range(20)]
        row = conditions(self.base, "validation", 0)[0]
        configs = [grid()[6], Config("native", "frozen", 0., .2)]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            execute_condition(root / "resumed", row, inputs, configs, "contract", episode_limit=1)
            def crash(path, value):
                if Path(path).name == "checkpoint.json" and value["next_episode"] == 2:
                    raise RuntimeError("injected crash after artifact write")
                atomic_json(path, value)
            with patch("exp003.campaign.atomic_json", side_effect=crash):
                with self.assertRaisesRegex(RuntimeError, "injected crash"):
                    execute_condition(root / "resumed", row, inputs, configs, "contract", episode_limit=2)
            recovered = execute_condition(root / "resumed", row, inputs, configs, "contract")
            fresh = execute_condition(root / "fresh", row, inputs, configs, "contract")
            for key in ("metrics", "cell_features", "readout_features", "config_ids"):
                self.assertEqual(recovered[key], fresh[key])
            self.assertEqual(recovered["metrics"]["acquisition"][1], .5)
            with self.assertRaises(ValueError):
                execute_condition(root / "resumed", row, inputs, configs, "changed")
            artifact = root / "resumed" / row["id"] / "episode_00.npz"
            with artifact.open("ab") as f:
                f.write(b"changed")
            with self.assertRaisesRegex(ValueError, "artifact changed"):
                execute_condition(root / "resumed", row, inputs, configs, "contract")

    def test_selection_weights_sizes_and_arms_not_unique_graphs(self):
        rows = conditions(self.base, "validation", 0)
        for row in rows:
            scores = np.zeros(9)
            scores[0] = 1. if row["size"] == 73 else 0.
            scores[1] = 0. if row["size"] == 73 else .1
            if row["arm"] == "whole_uniform" or row["mode"] != "full":
                scores[8] = 1000.  # Controls must never enter shared selection.
            row["metrics"] = {"selection_score": scores.tolist()}
        selected = select_shared([rows, copy.deepcopy(rows)])
        self.assertEqual(selected["index"], 0)
        np.testing.assert_allclose(selected["scores"][:2], [.2, .08], atol=1e-12, rtol=0)
        for row in rows:
            row["metrics"]["selection_score"] = [1.] * 9
        self.assertEqual(select_shared([rows])["config_id"], grid()[2].id)


if __name__ == "__main__":
    unittest.main()
