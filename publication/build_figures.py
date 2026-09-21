"""Read archived results, verify aggregates and draw the report figures. No training."""
from pathlib import Path
import sys, os, json, hashlib, csv
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_ROOT = ROOT if (ROOT/'results/exp011/analysis.json').exists() else HERE/'evidence'
sys.path.append(str(ROOT / '.cache/baseline-plot-deps'))
os.environ['MPLCONFIGDIR'] = str(HERE / 'qa/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = HERE / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
(HERE/'evidence').mkdir(exist_ok=True)
inputs = {}
def read(rel):
    p = DATA_ROOT / rel
    raw = p.read_bytes()
    inputs[rel] = hashlib.sha256(raw).hexdigest()
    dst = HERE/'evidence'/rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(raw)
    return json.loads(raw)

a7 = read('results/exp007_confirmation/analysis.json')
a8 = read('results/exp008_confirmation/analysis.json')
g7 = read('results/exp007_confirmation/geometry.json')
g8 = read('results/exp008_confirmation/geometry.json')
a9 = read('results/exp009/analysis.json')
b = read('results/exp010/analysis.json')
c = read('results/exp011/analysis.json')
fixed = read('results/exp011/fixed_rate_controls.json')
secondary = read('results/exp011/secondary_calibration.json')
selection = read('results/exp011/selection.json')
bs = [read(p.relative_to(DATA_ROOT).as_posix()) for p in sorted((DATA_ROOT/'results/exp010/confirmation').glob('block_*.json'))]
cs = [read(p.relative_to(DATA_ROOT).as_posix()) for p in sorted((DATA_ROOT/'results/exp011/confirmation').glob('block_*.json'))]
assert len(bs) == len(cs) == 24

def interval(x):
    x = np.asarray(x)
    mean = x.mean(); half = 2.0686576104190406*x.std(ddof=1)/np.sqrt(len(x))
    return dict(mean=float(mean), lower=float(mean-half), upper=float(mean+half))
checks=[]
def verify(name, actual, expected):
    for k,v in actual.items():
        assert abs(v-expected[k]) < 1e-10, (name,k,v,expected[k])
    checks.append(name)
def bvals(model, field='score', index=0):
    return np.array([np.mean([r['representations'][rep]['models'][model][field][index] if field=='score' else r['representations'][rep]['models'][model][field] for rep in ('native','calibrated')]) for r in bs])
etas=[1/2400,1/600,1/150,2/75]
def cvals(schedule, field='old', rep=None, anchor=False):
    reps = [rep] if rep else ['native','calibrated']
    if rep=='random': reps=['random1','random2','random3']
    def model(rp):
        if schedule=='offline': return 'offline_'+str([1e-6,1e-4,.01,.1].index(selection['lambdas'][rp]))
        return schedule+'_'+str(2 if anchor else etas.index(selection['etas'][rp][schedule]))
    return np.array([np.mean([r['representations'][rp]['models'][model(rp)][field] for rp in reps]) for r in cs])
verify('B offline old', interval(bvals('offline_full_0')), b['offline'])
verify('B supervised old', interval(bvals('supervised')), b['supervised'])
verify('B paired gap', interval(bvals('offline_full_0')-bvals('supervised')), b['primary_gap'])
verify('B acquisition loss', interval(bvals('supervised','forgetting_old')), b['forgetting'])
ct=c['tables']['native_calibrated']
verify('C offline old',interval(cvals('offline')),ct['offline']['old'])
verify('C blocked old',interval(cvals('blocked')),ct['blocked']['old'])
verify('C paired gap',interval(cvals('offline')-cvals('blocked')),c['primary_gap'])
verify('C acquisition loss',interval(cvals('blocked','forgetting')),c['primary_forgetting'])
for schedule in fixed['native_calibrated']:
    for endpoint in ['old','new']:
        verify('C fixed '+schedule+' '+endpoint,interval(cvals(schedule,endpoint,anchor=True)),fixed['native_calibrated'][schedule][endpoint])
for endpoint in ['old','new']:
    verify('C fixed paired '+endpoint,interval(cvals('replay10',endpoint,anchor=True)-cvals('local10',endpoint,anchor=True)),fixed['replay10_minus_local10'][endpoint])
    verify('C calibration '+endpoint,interval(cvals('blocked',endpoint,'calibrated')-cvals('blocked',endpoint,'native')),secondary['calibrated_minus_native_blocked'][endpoint])
for rep in ['native','calibrated','random','direct','polynomial']:
    for schedule in ['blocked','offline']:
        for ep in ['old','new']:
            verify('C '+rep+' '+schedule+' '+ep,interval(cvals(schedule,ep,rep)),c['tables'][rep][schedule][ep])
for r in cs:
    for rep in ['native','calibrated']:
        assert r['representations'][rep]['models']['blocked_0']['clips']==0
checks.append('C selected native and calibrated blocked clipping counts are zero in all 24 blocks')

NAVY='#173C51'; TEAL='#00877D'; ORANGE='#C96B36'; GRAY='#7C8991'; LIGHT='#DDE5E8'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10.5,'axes.titleweight':'bold','axes.labelsize':9,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#A9B5BB','axes.labelcolor':NAVY,'xtick.color':NAVY,'ytick.color':NAVY,'text.color':NAVY,'grid.color':'#E5EAED','svg.fonttype':'none','pdf.fonttype':42})
def title(ax,letter,text): ax.set_title(letter+'  '+text,loc='left',pad=13)
def err(ax, value, pos, color, horizontal=False, marker='o'):
    mean=value['mean']*100
    lo,hi=value.get('interval',[value.get('lower'),value.get('upper')])
    e=np.array([[mean-lo*100],[hi*100-mean]])
    if horizontal: ax.errorbar(mean,pos,xerr=e,fmt=marker,color=color,capsize=3,ms=6,lw=1.5)
    else: ax.errorbar(pos,mean,yerr=e,fmt=marker,color=color,capsize=3,ms=6,lw=1.5)
def save(fig,name):
    for ext in ['pdf','svg','png']: fig.savefig(OUT/(name+'.'+ext),dpi=320,facecolor='white',bbox_inches='tight',pad_inches=.13)
    plt.close(fig)

# Figure 1: effects, descriptive profiles and matched-count participation.
fig=plt.figure(figsize=(7.3,8.05))
gs=fig.add_gridspec(3,2,height_ratios=[1.05,1.3,1.3],hspace=.85,wspace=.48)
ax=fig.add_subplot(gs[0,:]); title(ax,'A','Calibration versus ordinary tuning')
ax.axvspan(-3,3,color='#E5F2EE',zorder=0); ax.axvline(0,color=GRAY,lw=.8)
for y,(label,a,n) in enumerate([('Adult',a8,24),('Larval',a7,32)]):
    v=a['primary']['ordinary']; err(ax,v,y,TEAL,True)
    ax.text(4.05,y,f"{100*v['mean']:+.2f}  [{100*v['interval'][0]:.2f}, {100*v['interval'][1]:.2f}]",va='center',fontsize=9)
ax.set(xlim=(-4,10),ylim=(-.6,1.6),yticks=[0,1],yticklabels=['Adult   n = 24','Larval  n = 32'],xlabel='Calibrated minus ordinary retention (percentage points)')
ax.set_xticks([-3,0,3]); ax.text(.01,1.05,'Shaded band: ±3 pp practical equivalence   |   98.333333% paired intervals',transform=ax.transAxes,fontsize=8)
for col,(label,a,g,k,n) in enumerate([('Larval',a7,g7,6,32),('Adult',a8,g8,48,24)]):
    condition='6_per_pair_16_False' if col==0 else '16_per_pair_16_False'
    if condition not in a['profiles']:
        condition=next(k for k in a['profiles'] if k.endswith('_per_pair_16_False') and not k.startswith('5_'))
    ax=fig.add_subplot(gs[1,col]); title(ax,chr(66+col),label+' memory profile')
    for j,(method,color) in enumerate([('ordinary',NAVY),('homeostasis',TEAL)]):
        for i,ep in enumerate(['retention','new_learning','worst_pair']): err(ax,a['profiles'][condition][method][ep],i+(-.12 if j==0 else .12),color)
    ax.set(ylim=(0,106),xticks=[0,1,2],xticklabels=['Mean\nretention','New\nlearning','Worst\npair'],ylabel='Preferred-choice probability (%)')
    ax.axhline(50,color=GRAY,lw=.8,ls=':'); ax.grid(axis='y',alpha=.5)
    ax=fig.add_subplot(gs[2,col]); title(ax,chr(68+col),label+' participation at fixed K')
    base='baseline6' if col==0 else 'baseline48'
    if condition+'_'+base not in g:
        base=next(s[len(condition)+1:] for s in g if s.startswith(condition+'_baseline'))
    vals=[g[condition+'_'+m]['unused_presented'] for m in [base,'homeostasis']]
    for i,v in enumerate(vals):
        err(ax,v,i,[NAVY,TEAL][i]); ax.text(i,v['mean']*100+5,f"{v['mean']*100:.2f}%",ha='center',fontsize=9)
    ax.set(xlim=(-.55,1.55),ylim=(0,55),xticks=[0,1],xticklabels=[f'Uncalibrated\nK = {k}',f'Calibrated\nK = {k}'],ylabel='Unused presented cells (%)'); ax.grid(axis='y',alpha=.5)
fig.legend(handles=[Line2D([0],[0],color=NAVY,marker='o',label='Ordinary / uncalibrated'),Line2D([0],[0],color=TEAL,marker='o',label='Calibrated')],loc='lower center',bbox_to_anchor=(.5,-.04),ncol=2,frameon=False)
save(fig,'figure_1_calibration')

fig=plt.figure(figsize=(7.3,8.05)); gs=fig.add_gridspec(3,2,height_ratios=[1.05,1.5,1.05],hspace=.85,wspace=.48)
ax=fig.add_subplot(gs[0,0]); title(ax,'A','Pair-memory diagnostic')
for i,(model,label,color) in enumerate([('chosen','Chosen\nonline',NAVY),('offline_chosen_0','Chosen\noffline',TEAL),('supervised','Full\nonline',NAVY),('offline_full_0','Full\noffline',TEAL)]): err(ax,interval(bvals(model)),i,color)
ax.set(ylim=(45,104),xticks=range(4),xticklabels=['Chosen\nonline','Chosen\noffline','Full\nonline','Full\noffline'],ylabel='Old-pair accuracy (%)'); ax.axhline(50,c=GRAY,ls=':',lw=.8)
ax=fig.add_subplot(gs[0,1]); title(ax,'B','XOR acquisition and final retention')
for j,v in enumerate(zip(cvals('blocked','acquisition'),cvals('blocked'),cvals('offline'))): ax.plot(range(3),np.array(v)*100,color=GRAY,alpha=.22,lw=.7)
for i,v in enumerate([interval(cvals('blocked','acquisition')),ct['blocked']['old'],ct['offline']['old']]): err(ax,v,i,[NAVY,ORANGE,TEAL][i])
ax.set(ylim=(-3,104),xticks=range(3),xticklabels=['Acquisition','Blocked\nfinal old','Offline\nold'],ylabel='Old-context accuracy (%)'); ax.axhline(50,c=GRAY,ls=':',lw=.8)
ax=fig.add_subplot(gs[1,:]); title(ax,'C','XOR controls retain the counterevidence')
reps=['native','calibrated','random','direct','polynomial']
for i,rp in enumerate(reps):
    for j,(method,ep,color,marker) in enumerate([('blocked','old',ORANGE,'o'),('offline','old',TEAL,'s'),('blocked','new',NAVY,'^')]): err(ax,c['tables'][rp][method][ep],i+(j-1)*.18,color,marker=marker)
ax.set(ylim=(-5,106),xticks=range(5),xticklabels=['Native\n73 features','Calibrated\n73 features','Random sparse\n73 features','Direct linear\n40 features','Quadratic\n861 features'],ylabel='Classification accuracy (%)'); ax.grid(axis='y',alpha=.5)
ax.legend(handles=[Line2D([0],[0],color=x,marker=m,ls='',label=t) for x,m,t in [(ORANGE,'o','Blocked old'),(TEAL,'s','Offline old'),(NAVY,'^','Blocked new')]],loc='lower center',bbox_to_anchor=(.5,-.48),ncol=3,frameon=False)
ax=fig.add_subplot(gs[2,0]); title(ax,'D','Secondary calibration effect')
for y,ep in enumerate(['new','old']): err(ax,secondary['calibrated_minus_native_blocked'][ep],y,TEAL,True)
ax.set(yticks=[0,1],yticklabels=['New','Old'],ylim=(-.6,1.6),xlim=(-5,24),xlabel='Calibrated minus native (pp)'); ax.axvline(0,c=GRAY,lw=.8)
ax=fig.add_subplot(gs[2,1]); title(ax,'E','Offline recovery under noise')
for i,values in enumerate([(b['offline'],interval(bvals('offline_full_0',index=3))),(ct['offline']['old'],ct['offline']['high_old'])]):
    for j,v in enumerate(values): err(ax,v,i+(j-.5)*.22,[TEAL,ORANGE][j])
ax.set(ylim=(65,103),xticks=[0,1],xticklabels=['Pairs\n0.1 / 0.3 SD','XOR\n0.05 / 0.2 SD'],ylabel='Old accuracy (%)')
ax.legend(handles=[Line2D([0],[0],color=x,marker='o',ls='',label=t) for x,t in [(TEAL,'Low noise'),(ORANGE,'High noise')]],frameon=False,fontsize=8,loc='lower left')
save(fig,'figure_2_readout')

fig=plt.figure(figsize=(7.3,7.45)); gs=fig.add_gridspec(3,2,height_ratios=[1.3,.9,1.15],hspace=.9,wspace=.5)
schedules=['blocked','shuffled','local10','replay10']
for col,ep in enumerate(['old','new']):
    ax=fig.add_subplot(gs[0,col]); title(ax,chr(65+col),('Old' if ep=='old' else 'New')+' context at common rate')
    for i,s in enumerate(schedules):
        vals=cvals(s,ep,anchor=True); jitter=np.linspace(-.1,.1,len(vals))
        ax.scatter(i+jitter,100*vals,s=8,color=GRAY,alpha=.3,zorder=1)
        err(ax,fixed['native_calibrated'][s][ep],i,TEAL if s=='replay10' else NAVY)
    ax.set(xticks=range(4),xticklabels=['Blocked','Shuffled','Local10','Replay10'],ylabel='Accuracy (%)',ylim=(-3,104)); ax.grid(axis='y',alpha=.4)
ax=fig.add_subplot(gs[1,0]); title(ax,'C','Matched-update old benefit')
err(ax,fixed['replay10_minus_local10']['old'],0,TEAL,True)
ax.set(ylim=(-.8,.8),yticks=[],xlim=(-5,75),xlabel='Replay10 minus local10 (pp)'); ax.axvline(0,c=GRAY,lw=.8)
ax.text(.5,.84,'+56.68  [46.97, 66.39] pp',transform=ax.transAxes,ha='center',fontsize=9)
ax=fig.add_subplot(gs[1,1]); title(ax,'D','Matched-update new cost')
err(ax,fixed['replay10_minus_local10']['new'],0,ORANGE,True)
ax.set(ylim=(-.8,.8),yticks=[],xlim=(-2,.5),xlabel='Replay10 minus local10 (pp)'); ax.axvline(0,c=GRAY,lw=.8)
ax.text(.5,.84,'−0.89  [−1.44, −0.33] pp',transform=ax.transAxes,ha='center',fontsize=9)
ax=fig.add_subplot(gs[2,:]); ax.axis('off'); title(ax,'E','Identical unique data and learning rate with different access')
rows=[['Blocked','256','256','Current example'],['Shuffled','256','256','Both contexts available'],['Local10','256','2,560','Current context only'],['Replay10','256','2,560','Both contexts revisited']]
tab=ax.table(cellText=rows,colLabels=['Schedule','Unique examples','Updates','Permitted training access'],colWidths=[.17,.21,.14,.48],cellLoc='left',loc='center',bbox=[0,0,1,.96])
tab.auto_set_font_size(False); tab.set_fontsize(8.5)
for (r,cl),cell in tab.get_celld().items():
    cell.set_edgecolor(LIGHT); cell.PAD=.12
    if r==0: cell.set_facecolor(NAVY); cell.set_text_props(color='white',weight='bold')
    else: cell.set_facecolor('white' if r%2 else '#F2F6F7')
save(fig,'figure_3_schedules')

# Export all plotted/statistical summaries, with original endpoints and provenance.
rows=[]
def flatten(v,path,source):
    if isinstance(v,dict):
        if 'mean' in v and ('interval' in v or 'lower' in v):
            lo,hi=v.get('interval',[v.get('lower'),v.get('upper')])
            exp=source.split('/')[1]
            conf='98.333333% primary three-contrast family' if '/primary/' in '/'+path+'/' and exp in ['exp007_confirmation','exp008_confirmation'] else '95% descriptive'
            if exp=='exp009' and path in ['primary','uncompensated','compensated']: conf='95% paired-bootstrap primary reference'
            if exp=='exp010' and path in ['primary_gap','offline','supervised','forgetting']: conf='95% primary conjunction; conditional Student-t'
            if exp=='exp011' and (path in ['primary_gap','primary_forgetting'] or path.startswith('tables/native_calibrated/offline/old') or path.startswith('tables/native_calibrated/blocked/old')): conf='95% primary conjunction; conditional Student-t'
            if 'guardrails/' in path: conf='one-sided alpha .05/12'
            rows.append(dict(source=source,sha256=inputs[source],key=path,mean=v['mean'],lower=lo,upper=hi,scale='original proportions unless geometry/count',interval_status=conf,n=32 if exp=='exp007_confirmation' else 24,unit='task block conditional on fixed anatomy'))
        else:
            for k,x in v.items(): flatten(x,path+'/'+k if path else k,source)
for src in list(inputs):
    if src.endswith(('analysis.json','geometry.json','fixed_rate_controls.json','secondary_calibration.json')): flatten(json.loads((DATA_ROOT/src).read_text()),'',src)
with (HERE/'figure_source_data.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
(HERE/'input_manifest.json').write_text(json.dumps(inputs,indent=2),encoding='utf-8')
(HERE/'numerical_checks.json').write_text(json.dumps({'checks_passed':checks,'n_checks':len(checks),'scope':'Read-only reaggregation of B/C block summaries; historical paired bootstrap intervals retained for EXP-007/008/009. No training replay in report production.','matplotlib':matplotlib.__version__,'numpy':np.__version__},indent=2),encoding='utf-8')
print('Figures built; independent block-summary checks:',len(checks))
