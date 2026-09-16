import unittest
import numpy as np
from tools import run_compound_transfer as c

class CompoundTests(unittest.TestCase):
    def test_analytic_xor(self):
        x=np.array([[1,0,1,0],[1,0,0,1],[0,1,1,0],[0,1,0,1]],float);y=np.array([1,-1,-1,1.])
        w,_=c.ridge(x,y,.01);np.testing.assert_allclose(x@w,0,atol=1e-12)
        q=c.polynomial(x);v,_=c.ridge(q,y,.01)
        self.assertTrue(np.all((q@v)*y>0))

    def test_ridge_reference(self):
        r=np.random.default_rng(19);x=r.normal(size=(20,7));y=r.normal(size=20)
        w,_=c.ridge(x,y,.01)
        v=np.linalg.lstsq(np.r_[x,np.sqrt(.2)*np.eye(7)],np.r_[y,np.zeros(7)],rcond=None)[0]
        np.testing.assert_allclose(w,v,atol=1e-12)

    def test_update_reference_and_probe_noninterference(self):
        x=np.array([[[1.,2]],[[2.,1]]]);y=np.array([[1.],[-1.]])
        p=np.full(2,.1);m=p.copy()
        for z,t in zip(x[:,0],y[:,0]):
            delta=.1*z*(t-z@(p-m));p=np.maximum(0,p+delta);m=np.maximum(0,m-delta)
        a=c.learn(x,y,.1,'blocked',np.arange(2))
        np.testing.assert_allclose(a['w'],p-m,atol=1e-15)
        frozen=a['w'].copy();c.acc(a['w'],x,y);np.testing.assert_array_equal(a['w'],frozen)
        np.testing.assert_array_equal(c.learn(x,y,.1,'blocked',np.arange(2))['w'],frozen)

    def test_schedule_accounting(self):
        sh=np.random.default_rng(8).permutation(256)
        for mode in c.MODES:
            ix=c.schedule(mode,sh);n=10 if mode.endswith('10') else 1
            np.testing.assert_array_equal(np.bincount(ix,minlength=256),np.full(256,n))
        self.assertTrue(np.all(c.schedule('local10',sh)[:1280]<128))
        self.assertTrue(np.any(c.schedule('replay10',sh)[256:]<128))

    def test_stream_balance_and_features(self):
        a=c.task('validation',0);b=c.task('validation',1)
        self.assertFalse(np.array_equal(a['train'],b['train']))
        self.assertFalse(np.array_equal(a['train'],a['probes'][:,:128]))
        self.assertTrue(np.all(a['labels'].sum(1)==0))
        self.assertTrue(np.all(a['probe_labels'].sum(1)==0))
        with np.load(c.CAL) as z: cal=dict(z)
        for rep in c.REPS:
            x,px,hx,scale=c.features(a,rep,cal)
            self.assertAlmostEqual(float(np.mean(np.sum(x*x,-1))),100/6,places=10)
            aa=dict(a);aa['probes']=np.zeros_like(a['probes']);aa['high']=np.ones_like(a['high'])
            xx,_,_,ss=c.features(aa,rep,cal)
            np.testing.assert_array_equal(xx,x);self.assertEqual(ss,scale)

if __name__=='__main__':unittest.main()
