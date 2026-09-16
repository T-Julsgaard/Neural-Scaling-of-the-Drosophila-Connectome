import csv
import io
import tarfile
import unittest
import numpy as np
from exp008.data import load_projection, CACHE, ARCHIVE, PREFIX, OUT
from exp008.memory import D, N, KLOW, KHIGH, ACTIVE, LOW, HIGH, rng, task, digest, random_projection
from exp008.homeostasis import candidates, METHODS, encode, fit, calibration_pool, sequence, summarize, probe
from exp007 import homeostasis as previous
from exp007 import memory as previous_tasks


class TransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p, cls.provenance = load_projection()
        cls.priority = rng('validation', 1, 99).permutation(N)

    def test_anatomy_against_total_edge_table(self):
        with np.load(OUT/'projection.npz') as a:
            counts = a['counts']; pi = {int(v): i for i,v in enumerate(a['pn_ids'])}; ki = {int(v): i for i,v in enumerate(a['kc_ids'])}
        total = np.zeros_like(counts)
        with tarfile.open(CACHE/ARCHIVE) as arc:
            rows = csv.DictReader(io.TextIOWrapper(arc.extractfile(PREFIX+'traced-total-connections.csv')))
            for row in rows:
                pre,post = int(row['bodyId_pre']),int(row['bodyId_post'])
                if pre in pi and post in ki: total[pi[pre],ki[post]] += int(row['weight'])
        self.assertTrue((counts <= total).all())
        self.assertEqual(counts.shape,(D,N)); self.assertEqual(counts.sum(),85151)
        self.assertEqual(np.count_nonzero(counts),4878)
        np.testing.assert_allclose(self.p.sum(0),1)
        self.assertTrue((counts.sum(0)>0).all()); self.assertTrue((counts.sum(1)>0).all())

    def test_topk_exact_reference_and_ties(self):
        for u in (rng('validation',2,1).random((13,D)), np.zeros((4,D)), np.ones((3,D))):
            for k in (KLOW,KHIGH):
                theta = np.zeros(N)
                actual = encode(u,self.p,self.priority,k,theta)
                expected = previous.encode(u,self.p,self.priority,k,theta)
                np.testing.assert_array_equal(actual,expected)
                np.testing.assert_allclose(actual.sum(-1),10)
                np.testing.assert_allclose((actual*actual).sum(-1),100/k)
                np.testing.assert_array_equal(actual,encode(u,self.p,self.priority,k,np.full(N,.02)))

    def test_larval_sequence_regression(self):
        from exp002.data import load_projection as larval
        p = larval()[0]; priority=np.arange(73)
        t=previous_tasks.task('validation',31,6,2,'total',4)
        cfg=[dict(k=6,strength=0.,eta=.003,temperature=.1)]
        actual=sequence(t,'ordinary',p,priority,np.zeros(73),cfg)
        expected=previous.sequence(t,'ordinary',p,priority,np.zeros(73),cfg)
        for key in actual: np.testing.assert_array_equal(actual[key],expected[key])

    def test_scalar_adult_sequence(self):
        t=task('validation',3,HIGH,2,'per_pair',4)
        t['obs']=[v[:,:3] for v in t['obs']]; t['outcomes']=[v[:,:3] for v in t['outcomes']]; t['uniforms']=[v[:,:3] for v in t['uniforms']]
        cfg=dict(k=KHIGH,strength=0.,eta=.004,temperature=.2)
        actual=sequence(t,'ordinary',self.p,self.priority,np.zeros(N),[cfg])
        plus=np.full(N,.1);minus=plus.copy(); history=[]
        for phase in range(2):
            for i in (range(2) if phase==0 else range(0,2,2)):
                for j in range(3):
                    x=previous.encode(t['obs'][phase][i,j],self.p,self.priority,KHIGH,np.zeros(N))
                    q=[sum((plus-minus)*v) for v in x]
                    p0=1/(1+np.exp(np.clip((q[1]-q[0])/.2,-700,700)))
                    chosen=int(t['uniforms'][phase][i,j]>=p0)
                    delta=.004*x[chosen]*(t['outcomes'][phase][i,j,chosen]-q[chosen])
                    plus=np.maximum(0,plus+delta);minus=np.maximum(0,minus-delta)
                if phase==0:
                    h=[]
                    for pair in range(i+1):
                        obs=previous.encode(t['probes'][0,pair],self.p,self.priority,KHIGH,np.zeros(N))
                        vals=[]
                        for x in obs:
                            q=[sum((plus-minus)*v) for v in x]
                            p0=1/(1+np.exp(np.clip((q[1]-q[0])/.2,-700,700)))
                            vals.append(p0 if t['labels'][pair]==0 else 1-p0)
                        h.append(np.mean(vals))
                    history.append(h)
        np.testing.assert_allclose(actual['final'][:,0],np.stack((plus,minus)),rtol=1e-12,atol=1e-14)
        for i,h in enumerate(history): np.testing.assert_allclose(actual['history'][0,0,i,:i+1],h,atol=1e-13)
        np.testing.assert_array_equal(actual['boundaries'][1:,0],actual['boundaries'][:-1,1])
        self.assertEqual(actual['chosen'].sum(),2*3*KHIGH)

    def test_calibration_and_sham(self):
        u=calibration_pool()[:256]
        theta,rec=fit(self.p,u,self.priority,.25)
        self.assertLess(abs(theta.sum()),1e-9)
        self.assertLessEqual(abs(theta).max(),rec['bound']+1e-12)
        before,after,target=map(np.array,(rec['before'],rec['after'],rec['target']))
        self.assertLess(np.mean((after-target)**2),np.mean((before-target)**2))
        np.testing.assert_array_equal(np.sort(theta),np.sort(theta[self.priority]))

    def test_streams_and_task_exposure(self):
        a,b=calibration_pool(),calibration_pool(True)
        self.assertEqual(a.shape,(4096,D));self.assertNotEqual(digest(a),digest(b))
        t=task('validation',5,HIGH,16,'total',4)
        self.assertNotEqual(digest(a),digest(t['obs'][0]))
        self.assertEqual(t['obs'][0].shape,(16,32,2,D))
        np.testing.assert_array_equal(t['p'].sum(-1),ACTIVE)
        np.testing.assert_array_equal((t['p'][:,0]*t['p'][:,1]).sum(-1),HIGH)
        self.assertEqual(len(np.unique(t['p'].reshape(-1,D),axis=0)),32)
        smaller=task('validation',5,HIGH,4,'per_pair',4)
        larger=task('validation',5,HIGH,16,'per_pair',4)
        np.testing.assert_array_equal(smaller['obs'][0],larger['obs'][0][:4])

    def test_budgets_and_update_mapping(self):
        for m in METHODS:
            grid=candidates(m);self.assertEqual(len(grid),32)
            self.assertEqual(len({tuple(c.values()) for c in grid}),32)
        for old_k,new_k in ((4,KLOW),(6,KHIGH)):
            self.assertAlmostEqual(.01*100/old_k,.08*100/new_k)
        self.assertEqual(KLOW,round(N*4/73));self.assertEqual(KHIGH,round(N*6/73))

    def test_oracle_metrics_replay_and_readonly(self):
        t=task('validation',6,LOW,4,'per_pair',4)
        cfg=[dict(k=0,strength=0.,eta=.003,temperature=.1)]
        a=sequence(t,'oracle',self.p,self.priority,np.zeros(N),cfg)
        b=sequence(t,'oracle',self.p,self.priority,np.zeros(N),cfg)
        for k in a:np.testing.assert_array_equal(a[k],b[k])
        self.assertGreater(summarize(a)[0,0],.95)
        self.assertAlmostEqual(summarize(a)[0,3],0)
        plus,minus=np.ones((1,N)),np.zeros((1,N)); before=digest(plus,minus)
        x=encode(t['probes'][0],self.p,self.priority,KHIGH,np.zeros(N))
        probe(plus,minus,x,[.1],t['labels']);self.assertEqual(before,digest(plus,minus))

    def test_null_invariants(self):
        # Small graph tests switching independently; full adult graphs are checked in prepare.
        p=previous_tasks.rng('validation',66,8).random((9,17));p[p<.7]=0
        q,rec=random_projection(p,rng('validation',7,9))
        np.testing.assert_array_equal(np.sort(p,axis=0),np.sort(q,axis=0))
        np.testing.assert_array_equal((p>0).sum(1),(q>0).sum(1))
        self.assertEqual(rec['accepted'],40*np.count_nonzero(p))
