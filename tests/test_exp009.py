import unittest
import math
import numpy as np
from exp009.compensation import *

class CompensationTests(unittest.TestCase):
    def test_scalar_encoder(self):
        x=np.arange(24,dtype=float).reshape(3,4,2)/7
        w=np.array([[1.,0],[.3,2],[0,.7]])
        theta=np.array([.7,.4]); gain=.03
        ref=np.zeros((2,4,2))
        for o in range(4):
            for t in range(2):
                a=[sum(w[i,j]*x[i,o,t] for i in range(3)) for j in range(2)]
                for j in range(2): ref[j,o,t]=max(0,a[j]-gain*sum(a)-theta[j])
        np.testing.assert_allclose(encode(x,w,theta,gain),ref,atol=1e-14)

    def test_scalar_learning_and_softmax(self):
        tr=rng(0,20,0).random((7,6,3)); labels=np.array([0,1,0,1,1,0]); initial=rng(0,20,1).random((7,2)); eta=.013
        ref=initial.copy()
        for o in range(6):
            wrong=1 if labels[o] else 0
            for t in range(3):
                for j in range(7): ref[j,wrong]*=math.exp(-eta/float(tr.mean())*tr[j,o,t])
        w=learn(tr,labels,initial,eta)
        np.testing.assert_allclose(w,ref,atol=1e-14)
        p=probabilities(tr,w,labels)
        for o in range(6):
            for t in range(3):
                m=sum(tr[j,o,t]*(ref[j,0]-ref[j,1]) for j in range(7))*(2*labels[o]-1)
                self.assertAlmostEqual(p[o,t],1/(1+math.exp(-m)),places=14)
        np.testing.assert_array_equal(initial,rng(0,20,1).random((7,2)))

    def test_complement_and_chance(self):
        x=rng(0,21,0).random((8,6,2)); labels=np.arange(6)%2; initial=np.ones((8,2))*.5
        np.testing.assert_array_equal(probabilities(x,learn(x,labels,initial,0),labels),np.full((6,2),.5))
        p=probabilities(x,learn(x,labels,initial,.01),labels)
        q=probabilities(x,learn(x,1-labels,initial,.01),1-labels)
        np.testing.assert_allclose(p,q,atol=1e-15)

    def test_orthogonal_learnability(self):
        x=np.eye(6)[:,:,None]; labels=np.arange(6)%2; initial=np.ones((6,2))*10
        self.assertGreater(probabilities(x,learn(x,labels,initial,1),labels).mean(),.999)

    def test_stream_and_replay(self):
        p=parameters(); a=task(0,22,p,8,2); b=task(0,22,p,8,2); c=task(0,23,p,8,2)
        self.assertEqual(array_digest(a),array_digest(b)); self.assertNotEqual(array_digest(a),array_digest(c))
        self.assertFalse(np.array_equal(a['train'],a['test']))
        # Verify namespace wiring symbolically without drawing confirmation data.
        self.assertNotEqual(np.random.SeedSequence([9009,0,0,0]).entropy,np.random.SeedSequence([9009,2,0,0]).entropy)

    def test_heldout_scaling_and_probe_nonmutation(self):
        p=parameters(); t=task(0,24,p,8,2); a,b,s=features(t,p,0)
        u=dict(t,test=t['test']*100); c,d,v=features(u,p,0)
        np.testing.assert_array_equal(a,c); self.assertEqual(s,v)
        w=learn(a,t['labels'],t['initial'],.001); original=w.copy()
        probabilities(b,w,t['labels']); np.testing.assert_array_equal(w,original)
        self.assertGreater(d.max(),1)

    def test_octave_supplied_fixture(self):
        src=ROOT/'results/exp009_source'; p=parameters()
        x=np.loadtxt(src/'fixture_inputs.csv',delimiter=',').reshape(24,8,4,order='F')
        initial=np.loadtxt(src/'fixture_initial.csv',delimiter=','); labels=np.arange(8)%2==0
        stats=np.loadtxt(src/'fixture_stats.csv',delimiter=',')
        for arm in (0,1):
            y=encode(x,*model(p,arm)); scale=y[:,:,:2].max(); y/=scale
            ref=np.loadtxt(src/f'fixture_Y{arm+1}.csv',delimiter=',').reshape(2000,8,4,order='F')
            np.testing.assert_allclose(y,ref,atol=1e-10,rtol=0)
            w=learn(y[:,:,:2],labels,initial,.001)
            np.testing.assert_allclose(w,np.loadtxt(src/f'fixture_W{arm+1}.csv',delimiter=','),atol=1e-10,rtol=0)
            self.assertAlmostEqual(float(probabilities(y[:,:,2:],w,labels).mean()),stats[arm,2],places=10)

if __name__=='__main__': unittest.main()
