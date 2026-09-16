import copy
import json
import unittest

import numpy as np

from exp002.baseline import BatchEpisode, Config, Task
from exp002.rules import Learner
from exp003.assay import GrowthTask, diagnostics, encode_observations
from exp003.growth import (ARMS, SIZES, allocation, check_matched, degree_shuffle,
                           from_record, grow, load_base)


class GrowthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load_base()
        cls.projection = cls.base.raw / cls.base.raw.sum(axis=0)
        cls.configs = [Config("native", "delta", .01, .1)]

    def test_all_declared_sizes_blocks_replicates_and_invariants(self):
        for block in range(5):
            for replicate in range(3):
                for size in SIZES:
                    graphs = grow(self.base, size, block, replicate)
                    self.assertTrue(check_matched(self.base, graphs))
                    swaps = graphs["degree_null"].record["null_swaps"]
                    self.assertLessEqual(swaps["attempts"], 100 * swaps["edges_added"])
                    self.assertEqual(swaps["successful_swaps"], 10 * swaps["edges_added"])

    def test_allocation_exact_ties_and_published_strata(self):
        np.testing.assert_array_equal(allocation(np.arange(1, 7), 2), [1, 1, 0, 0, 0, 0])
        self.assertEqual(len(self.base.strata), 73)
        self.assertEqual(set(self.base.strata), set(range(1, 7)))
        np.testing.assert_array_equal(allocation(self.base.strata, 73), np.bincount(self.base.strata)[1:])

    def test_lineage_roundtrip_replay_and_reject_corruption(self):
        graphs = grow(self.base, 110, 2, 1)
        replay = grow(self.base, 110, 2, 1)
        for arm, graph in graphs.items():
            record = json.loads(json.dumps(graph.record))
            np.testing.assert_array_equal(from_record(self.base, record).raw, graph.raw)
            self.assertEqual(replay[arm].sha256, graph.sha256)
            bad = copy.deepcopy(record)
            bad["added_nodes"][0]["raw_counts"][0] += 1
            with self.assertRaises(ValueError):
                from_record(self.base, bad)
            bad = copy.deepcopy(record)
            bad["added_nodes"][0]["donor_id"] = "matrix:999"
            with self.assertRaises(ValueError):
                from_record(self.base, bad)

    def test_unmixable_null_is_reported(self):
        added = np.ones((40, 2), dtype=np.int64)
        shuffled, record = degree_shuffle(added, np.random.default_rng(0))
        np.testing.assert_array_equal(shuffled, added)
        self.assertFalse(record["mixing_passed"])
        self.assertEqual(record["successful_swaps"], 0)
        self.assertEqual(record["attempts"], 100 * added.size)

    def test_no_growth_exact_baseline_traces_both_families(self):
        graphs = grow(self.base, 73)
        for episode in (0, 10):
            task = Task(self.projection, "validation", 0, episode)
            baseline = BatchEpisode(task, self.configs)
            baseline.run_until()
            for graph in graphs.values():
                for sparsity in ("proportional", "fixed4"):
                    trial = BatchEpisode(GrowthTask(task, graph, sparsity), self.configs)
                    trial.run_until()
                    for key in ("trace", "probes", "plus", "minus"):
                        np.testing.assert_array_equal(getattr(trial, key), getattr(baseline, key))

    def test_pairing_sparsity_and_independent_bottleneck_calculation(self):
        base_task = Task(self.projection, "validation", 0, 0)
        for size in SIZES:
            graphs = grow(self.base, size)
            priorities = []
            for graph in graphs.values():
                task = GrowthTask(base_task, graph)
                priorities.append(task.priority)
                for key in ("prototypes", "order", "observations", "outcomes", "uniforms", "preferred"):
                    self.assertIs(getattr(task, key), getattr(base_task, key))
                for mode in ("proportional", "fixed4"):
                    a = encode_observations(graph, base_task.observations[:4], task.priority, mode)
                    expected_k = max(1, int(np.floor(.05 * size + .5))) if mode == "proportional" else 4
                    np.testing.assert_array_equal((a > 0).sum(axis=-1), expected_k)
                    np.testing.assert_allclose(a.sum(axis=-1), 10., atol=1e-12, rtol=0)
                    b = encode_observations(graph, base_task.observations[:4], task.priority, mode, True)
                    ids = [int(i.split(":")[1]) for i in self.base.kc_ids] + list(range(size - 73))
                    manual = np.zeros((*a.shape[:-1], 32))
                    for group in range(32):
                        members = [i for i, value in enumerate(ids) if value % 32 == group]
                        if members:
                            manual[..., group] = a[..., members].mean(axis=-1)
                    manual *= 10. / manual.sum(axis=-1, keepdims=True)
                    np.testing.assert_allclose(b, manual, atol=1e-12, rtol=0)
            for p in priorities:
                np.testing.assert_array_equal(p, priorities[0])

    def test_grown_scalar_rule_probes_resume_and_task_identity(self):
        graphs = grow(self.base, 110)
        for episode in (0, 10):
            base_task = Task(self.projection, "validation", 0, episode)
            for mode, bottleneck in (("proportional", False), ("fixed4", False), ("proportional", True)):
                task = GrowthTask(base_task, graphs["structured"], mode, bottleneck)
                complete = BatchEpisode(task, self.configs)
                complete.run_until()
                scalar = Learner.initial("delta", 32 if bottleneck else 110, .01)
                for t, cues in enumerate(complete.activities):
                    p = scalar.probabilities(cues, .1)
                    choice = int(task.uniforms[t] >= p[0])
                    self.assertAlmostEqual(p[task.preferred[t]], complete.trace[0, t, 0], places=10)
                    self.assertEqual(choice, complete.trace[0, t, 1])
                    scalar.update(cues[choice], int(task.outcomes[t, choice]))
                np.testing.assert_allclose(complete.plus[0], scalar.plus, atol=1e-10, rtol=0)
                np.testing.assert_allclose(complete.minus[0], scalar.minus, atol=1e-10, rtol=0)
                for stop in (0, 1, 127, 128, 255, 256, 383):
                    partial = BatchEpisode(task, self.configs)
                    partial.run_until(stop)
                    payload = json.loads(json.dumps(partial.payload()))
                    resumed = BatchEpisode.restore(task, payload)
                    before = (resumed.plus.copy(), resumed.minus.copy(), resumed.trial)
                    resumed.probe(384, .3)
                    np.testing.assert_array_equal(before[0], resumed.plus)
                    np.testing.assert_array_equal(before[1], resumed.minus)
                    self.assertEqual(before[2], resumed.trial)
                    resumed.run_until()
                    for key in ("trace", "probes", "plus", "minus"):
                        np.testing.assert_array_equal(getattr(resumed, key), getattr(complete, key))
                    wrong = GrowthTask(base_task, graphs["uniform"], mode, bottleneck)
                    with self.assertRaisesRegex(ValueError, "task mismatch"):
                        BatchEpisode.restore(wrong, payload)

    def test_diagnostics_distinguish_wiring_and_activity(self):
        graph = grow(self.base, 80)["clone"]
        activity = np.zeros((4, 80))
        activity[:, 0] = [0, 1, 0, 1]
        activity[:, 73] = activity[:, 0]  # No extra linear dimension or pattern.
        d = diagnostics(graph, activity)
        self.assertEqual(d["added_novel_normalized_columns"], 0)
        self.assertEqual(d["added_novel_active_patterns"], 0)
        self.assertEqual(d["added_linear_dimensions_given_native"], 0)
        self.assertAlmostEqual(d["added_never_active_fraction"], 6 / 7)
        activity[:, 74] = [0, 0, 1, 1]
        d = diagnostics(graph, activity)
        self.assertEqual(d["added_novel_active_patterns"], 1)
        self.assertEqual(d["added_linear_dimensions_given_native"], 1)


if __name__ == "__main__":
    unittest.main()
