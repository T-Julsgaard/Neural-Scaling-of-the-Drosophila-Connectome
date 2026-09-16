"""GPL-3.0-or-later. Adapted from Abdelrahman et al. (2021), pinned in source audit.

SI equations 3, 20, 21; authors' Bhandawat lookup. Frozen fitted parameters;
new independent task streams and training-only scales are project adaptations.
"""
from pathlib import Path
import hashlib
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RATES=10.**np.array([-5,-4,-3,-2.75,-2.5,-2.25,-2,-1,0,1])
SD=np.array([2.929936306,6.904458599,8.687898089,10.31847134,11.2611465,11.69426752,11.69426752,10.70063694,9.78343949,9.732484076,8.866242038,8.687898089,7.363057325,8.152866242,10.67515924,9.910828025])

def rng(stage,block,stream):
    if stage not in (0,1,2): raise ValueError('Unknown stage')
    return np.random.default_rng(np.random.SeedSequence([9009,stage,block,stream]))

def parameters():
    with np.load(ROOT/'research/sources/exp009/parameters.npz') as z:
        return {k:z[k] for k in z.files}

def task(stage,block,p,odors=100,trials=15):
    table=p['hallem'][:110].T
    ix=rng(stage,block,0).integers(0,110,(24,odors))
    raw=table[np.arange(24)[:,None],ix]
    nearest=np.argmin(abs(raw[:,:,None]-np.arange(10,311,20)),axis=2)
    sd=SD[nearest]
    def observations(stream):
        x=np.maximum(0,raw[:,:,None]+sd[:,:,None]*rng(stage,block,stream).normal(size=(24,odors,trials)))
        return np.maximum(0,x*p['pn_scale'][0]+p['pn_scale'][1])
    labels=np.zeros(odors,dtype=int)
    labels[rng(stage,block,3).permutation(odors)[:odors//2]]=1
    return dict(prototypes=raw,train=observations(1),test=observations(2),labels=labels,initial=rng(stage,block,4).random((2000,2)))

def encode(x,w,theta,gain):
    shape=x.shape
    a=w.T@x.reshape(shape[0],-1)
    y=np.maximum(0,a-gain*a.sum(0)-theta[:,None])
    if not np.isfinite(y).all(): raise FloatingPointError('Nonfinite response')
    return y.reshape(w.shape[1],*shape[1:])

def model(p,arm):
    return ((p['thisW'],p['thetaS'],p['APLgains'].ravel()[0]) if arm==0 else
            (p['thisW_Kennedy'],p['theta_Activity_homeo'],p['APLgains'].ravel()[4]))

def features(t,p,arm):
    train=encode(t['train'],*model(p,arm))
    scale=float(train.max())
    if scale<=0: raise ValueError('No training activity')
    train/=scale
    test=encode(t['test'],*model(p,arm))/scale
    return train,test,scale

def learn(train,labels,initial,eta):
    # Aggregated sufficient statistics equal the product of per-odor exponentials.
    mu=float(train.mean())
    if mu<=0: raise ValueError('No activity')
    sums=train.sum(2)
    weights=initial.copy()
    for valence in (0,1):
        wrong=1 if valence==1 else 0
        weights[:,wrong]*=np.exp(-eta/mu*sums[:,labels==valence].sum(1))
    return weights

def probabilities(test,weights,labels):
    margin=np.einsum('not,n->ot',test,weights[:,0]-weights[:,1])
    signed=margin*(2*labels[:,None]-1)
    # Stable sigmoid, including high-rate underflow and extreme toy margins.
    return np.exp(-np.logaddexp(0,-signed))

def evaluate(t,p,rates):
    saved={k:v for k,v in t.items()}
    scores=[]; profiles=[]
    for arm in (0,1):
        tr,te,scale=features(t,p,arm)
        arm_scores=[]
        for j,eta in enumerate(rates[arm]):
            w=learn(tr,t['labels'],t['initial'],eta)
            prob=probabilities(te,w,t['labels'])
            saved[f'weights_{arm}_{j}']=w
            saved[f'probabilities_{arm}_{j}']=prob
            arm_scores.append(float(prob.mean()))
        means=te.mean((1,2)); counts=(te>0).mean((1,2))
        profiles.append(dict(coding_level=float((te>0).mean()),unused_fraction=float((counts==0).mean()),
                             mean_activity_cv=float(means.std()/means.mean()),
                             effective_mean_activity_cells=float(means.sum()**2/(means@means)),
                             mean_squared_norm=float((te*te).sum(0).mean()),scale=scale,train_mean=float(tr.mean())))
        saved[f'scale_{arm}']=np.array(scale)
        scores.append(arm_scores)
    return saved,dict(scores=scores,profiles=profiles)

def array_digest(t):
    h=hashlib.sha256()
    for k,v in sorted(t.items()):
        h.update(k.encode()); h.update(str(v.shape).encode()); h.update(v.tobytes())
    return h.hexdigest()
