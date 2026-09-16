import unittest
import numpy as np
from tools import run_readout_diagnostic as d
from exp009.compensation import learn

class DiagnosticTests(unittest.TestCase):
    def test_existing_scalar_update(self):
        r = np.random.default_rng(110)
        x = r.random((2, 7)); y = np.array([1., -1.]); u = .37
        p = r.random(7); m = r.random(7)
        a, b = d.update(p[None], m[None], x, y, u, [d.ETA], [.1])
        prob = np.exp(-np.logaddexp(0, (x[1]-x[0])@(p-m)/.1))
        chosen = int(u >= prob); ch = d.ETA*x[chosen]*(y[chosen]-(p-m)@x[chosen])
        np.testing.assert_allclose(a[0], np.maximum(0, p+ch), atol=1e-15)
        np.testing.assert_allclose(b[0], np.maximum(0, m-ch), atol=1e-15)

    def test_ridge_augmented_and_nonnegative(self):
        r = np.random.default_rng(111); x = r.normal(size=(40, 9)); y = r.normal(size=40)
        w, _ = d.ridge(x, y, .01)
        ref = np.linalg.lstsq(np.concatenate([x, np.sqrt(.4)*np.eye(9)]), np.r_[y, np.zeros(9)], rcond=None)[0]
        np.testing.assert_allclose(w, ref, atol=1e-12)
        np.testing.assert_allclose(x@w, x@np.maximum(w,0)-x@np.maximum(-w,0), atol=1e-12)

    def test_orthogonal_and_scale(self):
        x = np.eye(8); y = np.tile([1.,-1.],4)
        w, _ = d.ridge(x,y,1e-6); self.assertTrue(np.all(x@w*y > 0))
        w2,_ = d.ridge(3*x,y,9e-6); np.testing.assert_allclose(3*x@w2,x@w,atol=1e-12)
        # Function-equivalent unclipped update when x -> c*x, w -> w/c, eta -> eta/c^2.
        v=np.arange(8)/20; z=x[0]; e=.02
        a=v+2*e*z*(1-v@z); b=v/3+2*e/9*(3*z)*(1-(v/3)@(3*z))
        np.testing.assert_allclose(a,3*b,atol=1e-12)

    def test_streams_and_online_access(self):
        a=d.get_task('validation',100000); b=d.get_task('validation',100001)
        self.assertNotEqual(d.digest(a['obs'][0]),d.digest(b['obs'][0]))
        self.assertNotEqual(d.digest(a['obs'][0]),d.digest(a['probes']))
        x=np.tile(np.eye(4).reshape(2,1,2,4),(1,4,1,1)); y=np.tile([1.,-1.],(2,4,1)); u=np.full((2,4),.1)
        r=d.online(x,y,u,x[:,0],np.zeros(2,int),'chosen')
        changed=y.copy()
        for i in range(2):
            for j in range(4): changed[i,j,1-r['choices'][i,j]] *= -1
        rr=d.online(x,changed,u,x[:,0],np.zeros(2,int),'chosen')
        np.testing.assert_array_equal(r['w'],rr['w'])
        self.assertEqual(len(r['changes']),8)
        full=d.online(x,y,u,x[:,0],np.zeros(2,int),'supervised')
        self.assertEqual(len(full['changes']),16)
        self.assertTrue(np.all(d.margins(full['w'],x[:,0],np.zeros(2,int))>0))

    def test_author_order_invariance(self):
        r=np.random.default_rng(112); x=r.random((7,8,3)); labels=np.arange(8)%2; initial=r.random((7,2)); order=r.permutation(8)
        a=learn(x,labels,initial,.001); b=learn(x[:,order],labels[order],initial,.001)
        np.testing.assert_allclose(a,b,atol=1e-15)

if __name__ == '__main__': unittest.main()
