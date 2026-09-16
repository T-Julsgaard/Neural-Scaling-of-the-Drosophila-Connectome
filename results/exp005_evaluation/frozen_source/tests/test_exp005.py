import unittest
from dataclasses import replace
import numpy as np
from exp002.baseline import BatchEpisode, Config
from exp002.data import load_projection
from exp005.mechanism import Inputs, Setting, episode, encode, fixed, stream


class MechanismTests(unittest.TestCase):
    def test_legacy_engine(self):
        task = Inputs('validation',0,10)
        projection,_ = load_projection()
        class Adapter:
            def __getattr__(self,name): return getattr(task,name)
            def activities(self,representation): return encode(projection,task.observations,task.priority,4)*2.5
            def probe_activities(self,representation,trial,sigma):
                return encode(projection,task.probe_observations(trial,sigma),task.priority,4)*2.5
        old = BatchEpisode(Adapter(),[Config('native','delta',.01,.1)])
        old.run_until()
        new = episode(task,[fixed()[0]])
        np.testing.assert_allclose(new['trace'][0,:,:4],old.trace[0,:,:4],atol=2e-14,rtol=0)
        np.testing.assert_allclose(new['plus'],old.plus,atol=2e-14,rtol=0)
        np.testing.assert_allclose(new['probes'][0,:3],old.probes[0,[0,1,4]],atol=2e-14,rtol=0)

    def test_scaled_clipped_replay(self):
        c = fixed()[0]
        scale = 2/3
        scaled = replace(c,id='scaled',amplitude=c.amplitude*scale,eta=c.eta/scale**2,initial=c.initial/scale)
        raw = episode(Inputs('validation',0,10),[c,scaled],True)
        np.testing.assert_allclose(raw['trace'][0,:,0:8],raw['trace'][1,:,0:8],atol=3e-14,rtol=0)
        self.assertGreater(raw['trace'][0,:,9].sum(),0)
        np.testing.assert_allclose(raw['plus'][0],raw['plus'][1]*scale,atol=3e-14,rtol=0)

    def test_scalar_clipped_recurrence(self):
        task = Inputs('validation',1,1)
        settings = fixed()
        raw = episode(task,settings,True)
        projection,_ = load_projection()
        for i,c in enumerate(settings):
            plus,minus = np.full(73,.1),np.full(73,.1)
            x = encode(projection,task.observations,task.priority,c.k)*c.amplitude
            for t in range(384):
                s=x[t,t%2]
                q=float(np.dot(plus-minus,s))
                self.assertAlmostEqual(q,raw['trace'][i,t,3],places=12)
                d=c.eta*s*(task.outcomes[t,t%2]-q)
                plus,minus=np.maximum(0,plus+d),np.maximum(0,minus-d)
            np.testing.assert_allclose(plus,raw['plus'][i],atol=2e-14,rtol=0)

    def test_encoding_and_streams(self):
        task=Inputs('validation',0,0)
        projection,_=load_projection()
        for c in fixed():
            x=encode(projection,task.observations,task.priority,c.k)*c.amplitude
            np.testing.assert_array_equal((x>0).sum(axis=-1),c.k)
            np.testing.assert_allclose((x*x).sum(axis=-1),c.k*c.amplitude**2)
        self.assertNotEqual(task.digest(),Inputs('validation',0,1).digest())
        self.assertNotEqual(Inputs('development',100,0).digest(),Inputs('evaluation',1000,0).digest())
        with self.assertRaises(ValueError): stream('development',1000,1)

    def test_frozen(self):
        raw=episode(Inputs('validation',0,10),[Setting('frozen',6,10/6,0)])
        np.testing.assert_array_equal(raw['trace'][...,0],.5)
        np.testing.assert_array_equal(raw['probes'],.5)

    def test_checkpoint_corruption(self):
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from pathlib import Path
        from exp005.campaign import block
        from exp002.campaign import atomic_json
        from exp002.data import sha256
        with TemporaryDirectory() as tmp:
            target=Path(tmp)
            atomic_json(target/'contract.json',{'blocks':[0]})
            h=sha256(target/'contract.json')
            (target/'block_0.npz').write_bytes(b'checkpoint')
            record={'contract_sha256':h,'sha256':sha256(target/'block_0.npz')}
            atomic_json(target/'block_0.json',record)
            with patch('exp005.campaign.folder',return_value=target),patch('exp005.campaign.verify'):
                self.assertEqual(block('validation',0,h),record)
                (target/'block_0.npz').write_bytes(b'corrupt')
                with self.assertRaises(ValueError): block('validation',0,h)

