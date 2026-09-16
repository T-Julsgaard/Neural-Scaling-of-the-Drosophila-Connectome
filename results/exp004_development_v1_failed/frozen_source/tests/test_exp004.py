import inspect
from pathlib import Path
import tempfile
import unittest
import numpy as np
from exp002.baseline import BatchEpisode, Config
from exp003 import confirmation_inputs as old
from exp003.growth import load_base
from exp004 import inputs as new
from exp004.analysis import analyze, factorial, interval
from exp004.engine import execute_condition


class ActivityDiagnosticTests(unittest.TestCase):
    def test_encoder_scalar_oracle_exact_count_and_mass(self):
        graph = new.graphs_for(load_base(), 'validation', 0, 110, 0)['structured']
        rng = np.random.default_rng(83)
        observations = np.vstack((np.zeros(40), np.ones(40), rng.uniform(size=(8,40))))
        priority = rng.permutation(110)
        for k in (4,6):
            encoded = new.encode_fast(graph, observations, priority, k)
            reference = np.zeros_like(encoded)
            for t,u in enumerate(observations):
                drive = graph.projection.T@u
                winners = sorted(range(110), key=lambda i: (-drive[i], priority[i]))[:k]
                reference[t,winners] = 10/k
            np.testing.assert_array_equal(encoded, reference)
            np.testing.assert_array_equal(np.count_nonzero(encoded,axis=1), k)
            np.testing.assert_allclose(encoded.sum(axis=1), 10, rtol=0, atol=2e-14)
            b = new.encode_fast(graph, observations, priority, k, True)
            self.assertEqual(b.shape,(10,32))
            np.testing.assert_allclose(b.sum(axis=1),10,rtol=0,atol=2e-14)
        with self.assertRaises(ValueError):
            new.encode_fast(graph, observations, priority, 5)

    def test_legacy_encoder_and_episode_compatibility(self):
        base = load_base()
        for n in (73,110):
            graph = old.graphs_for(base,'validation',0,n,0)['structured']
            inputs = old.Inputs('validation',0,10)
            for mode,k in (('full',4 if n==73 else 6),('fixed4',4),('bottleneck',4 if n==73 else 6)):
                legacy = old.EpisodeTask(inputs,graph,mode)
                # Old inputs+graph isolate encoder equivalence; priorities copied explicitly.
                task = new.EpisodeTask(inputs,graph,('bottleneck' if mode=='bottleneck' else 'full')+f'_k{k}')
                task.priority = legacy.priority.copy()
                np.testing.assert_array_equal(task.activities('native'),legacy.activities('native'))
                a,b=BatchEpisode(task,new.grid()),BatchEpisode(legacy,new.grid())
                a.run_until(); b.run_until()
                np.testing.assert_array_equal(a.trace,b.trace)
                np.testing.assert_array_equal(a.probes,b.probes)

    def test_crossed_pairing_and_fresh_streams(self):
        base=load_base()
        rows=new.conditions(base,'validation',0)
        self.assertEqual(len(rows),28)
        self.assertEqual(len({r['id'] for r in rows}),28)
        inputs=new.Inputs('validation',0,0)
        self.assertNotEqual(inputs.digest(),old.Inputs('validation',0,0).digest())
        self.assertFalse(np.array_equal(new.stream('validation',0,0,2).random(20), old.stream('validation',0,0,2).random(20)))
        for start in range(0,28,4):
            tasks=[new.EpisodeTask(inputs,r['graph'],r['mode']) for r in rows[start:start+4]]
            self.assertEqual(len({t.graph.sha256 for t in tasks}),1)
            self.assertEqual(len({t.inputs.digest() for t in tasks}),1)
            for t in tasks:
                np.testing.assert_array_equal(t.priority,tasks[0].priority)
            self.assertEqual(len({t.digest() for t in tasks}),4)
        # Validate boundaries without generating reserved evaluation inputs.
        self.assertEqual(new.STAGES['evaluation'],(2,range(1000,1032)))
        for stage,b in (('evaluation',999),('evaluation',1032),('development',104)):
            with self.assertRaises(ValueError):
                new.Inputs(stage,b,0)

    def test_factorial_algebra_and_block_intervals(self):
        a=np.arange(32)/100
        result=factorial(a,a+.06,a+.02,a+.08)
        np.testing.assert_allclose(result['active_count'],.06)
        np.testing.assert_allclose(result['population'],.02)
        np.testing.assert_allclose(result['interaction'],0,atol=1e-16)
        interaction=factorial(a,a+.02,a+.01,a+.08)
        np.testing.assert_allclose(interaction['interaction'],.05)
        idx=np.random.default_rng(9).integers(0,32,(10000,32))
        estimate=interval(a,idx,1-.05/3)
        np.testing.assert_allclose(estimate['interval'],np.quantile(a[idx].mean(axis=1),[.05/6,1-.05/6]))
        with self.assertRaises(ValueError):
            interval(np.zeros(96),idx)

    def test_resume_frozen_control_and_corruption(self):
        row=new.conditions(load_base(),'validation',0)[1] # native K6 full
        inputs=[new.Inputs('validation',0,ep) for ep in range(20)]
        configs=new.grid()+[Config('native','frozen',0.,.2)]
        with tempfile.TemporaryDirectory() as directory:
            execute_condition(directory,row,inputs,configs,'test',episode_limit=1)
            result=execute_condition(directory,row,inputs,configs,'test')
            self.assertEqual(result['metrics']['retention_after'][1],.5)
            self.assertEqual(result['readout_weights'],146)
            with self.assertRaises(ValueError):
                execute_condition(directory,row,inputs,configs,'changed')
            p=Path(directory)/row['id']/'episode_00.npz'
            with p.open('ab') as f:
                f.write(b'corrupted')
            with self.assertRaises(ValueError):
                execute_condition(directory,row,inputs,configs,'test')

    def test_analysis_nesting_and_missing_cells(self):
        rows=[]
        for n in (73,110):
            for arm in (('clone',) if n==73 else ('structured','degree_null')):
                for rep in range(1 if n==73 else 3):
                    for readout in ('full','bottleneck'):
                        for k in (4,6):
                            value=.5+.02*(n==110)+.06*(k==6)
                            if n==110:
                                value += (rep-1)*.01
                            rows.append({'size':n,'arm':arm,'mode':f'{readout}_k{k}',
                                         'metrics':{'retention_after':[value],'acquisition':[value]},
                                         'cell_features':{'never_active_fraction':.2},
                                         'readout_features':{'never_active_fraction':.1},
                                         'readout_weights':64 if readout=='bottleneck' else 2*n,
                                         'edges':100,'contacts':200})
        result=analyze([rows for _ in range(5)],'validation')
        self.assertAlmostEqual(result['primary']['active_count']['mean'],.06)
        self.assertAlmostEqual(result['primary']['population']['mean'],.02)
        self.assertEqual(len(result['primary']['population']['block_values']),5)
        with self.assertRaises(ValueError):
            analyze([rows[:-1] for _ in range(5)],'validation')


if __name__=='__main__':
    unittest.main()
