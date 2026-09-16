import inspect
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from exp002.baseline import BatchEpisode, Config
from exp003 import development as old
from exp003 import confirmation_inputs as new
from exp003.confirmation import execute_condition
from exp003.confirmation_analysis import interval, bootstrap_indices, profile
from exp003.growth import load_base


class ConfirmationTests(unittest.TestCase):
    def test_adapters_are_exact_frozen_copies(self):
        # All scientific functions/classes are literally unchanged, including globals' use.
        for name in ('rebuild', 'graphs_for', 'Inputs', 'encode_fast', 'EpisodeTask', 'conditions'):
            self.assertEqual(inspect.getsource(getattr(old, name)), inspect.getsource(getattr(new, name)))
        from exp003 import campaign, confirmation
        for name in ('summarize_condition', 'execute_condition', 'execute_block'):
            self.assertEqual(inspect.getsource(getattr(campaign, name)), inspect.getsource(getattr(confirmation, name)))
        self.assertEqual(new.STAGES, {'validation': (0, range(5)), 'confirmation': (2, range(1000, 1020))})
        self.assertEqual(new.grid(), [Config('native', 'delta', .01, .1)])

    def test_stage_zero_graph_task_and_selected_traces_equal(self):
        base = load_base()
        for ep in (0, 10):
            a, b = old.Inputs('validation', 0, ep), new.Inputs('validation', 0, ep)
            self.assertEqual(a.digest(), b.digest())
            for n in (73, 110, 146):
                ga, gb = old.graphs_for(base, 'validation', 0, n, 0), new.graphs_for(base, 'validation', 0, n, 0)
                for arm in ga:
                    self.assertEqual(ga[arm].sha256, gb[arm].sha256)
                for mode in ('full', 'fixed4', 'bottleneck'):
                    ta, tb = old.EpisodeTask(a, ga['structured'], mode), new.EpisodeTask(b, gb['structured'], mode)
                    self.assertEqual(ta.digest(), tb.digest())
                    x, y = BatchEpisode(ta, new.grid()), BatchEpisode(tb, new.grid())
                    x.run_until(); y.run_until()
                    np.testing.assert_array_equal(x.trace, y.trace)
                    np.testing.assert_array_equal(x.probes, y.probes)
        for stage, block in (('development', 100), ('confirmation', 999), ('confirmation', 1020)):
            with self.assertRaises(ValueError):
                new.Inputs(stage, block, 0)
        with self.assertRaises(ValueError):
            old.Inputs('confirmation', 1000, 0)

    def test_twenty_block_bootstrap_and_nesting(self):
        indices = bootstrap_indices('validation', 0)
        a = np.arange(20)/100
        estimate = interval(a, .9833, indices)
        np.testing.assert_allclose(estimate['interval'], np.quantile(a[indices].mean(axis=1), [.00835, .99165]))
        self.assertEqual(interval(np.zeros(20), indices=indices)['interval'], [0., 0.])
        with self.assertRaises(ValueError):
            interval(np.zeros(60), indices=indices)
        # One shared native baseline, three grown graphs; episodes/graphs cannot inflate n.
        row = {'size': 73, 'arm': 'clone', 'mode': 'full', 'metrics': {'acquisition': [.5]},
               'cell_features': {k: 0 for k in ('never_active_fraction', 'native_never_active_fraction',
                'added_never_active_fraction', 'covariance_participation_rank', 'duplicate_normalized_columns')},
               'readout_features': {'covariance_participation_rank': 1}, 'edges': 100, 'contacts': 200, 'readout_weights': 146}
        with patch('exp003.confirmation_analysis.bootstrap_indices', return_value=indices):
            result = profile([[row] for _ in range(20)], 73, 'structured', 'fixed4', 0)
            self.assertEqual(result['metrics']['acquisition']['block_values'], [.5]*20)
            grown = [{**row, 'size': 110, 'arm': 'structured', 'metrics': {'acquisition': [p]}} for p in (.3, .6, .9)]
            result = profile([grown for _ in range(20)], 110, 'structured', 'full', 0)
            np.testing.assert_allclose(result['metrics']['acquisition']['block_values'], .6)
            with self.assertRaises(ValueError):
                profile([grown[:2] for _ in range(20)], 110, 'structured', 'full', 0)

    def test_confirmation_adapter_recovery_and_control(self):
        base = load_base()
        row = new.conditions(base, 'validation', 0)[0]
        inputs = [new.Inputs('validation', 0, ep) for ep in range(20)]
        configs = new.grid() + [Config('native', 'frozen', 0., .2)]
        with tempfile.TemporaryDirectory() as folder:
            execute_condition(folder, row, inputs, configs, 'test', episode_limit=1)
            result = execute_condition(folder, row, inputs, configs, 'test')
            self.assertEqual(result['metrics']['acquisition'][1], .5)
            self.assertEqual(result['config_ids'], [c.id for c in configs])
            with self.assertRaises(ValueError):
                execute_condition(folder, row, inputs, configs, 'changed')
            path = Path(folder)/row['id']/'episode_00.npz'
            with path.open('ab') as f:
                f.write(b'corrupted')
            with self.assertRaises(ValueError):
                execute_condition(folder, row, inputs, configs, 'test')


if __name__ == '__main__':
    unittest.main()
