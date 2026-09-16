% Session A: extract supplied author parameters; original files remain intact.
base = '.cache/session_a/author/';
out = 'results/exp009_source/';
if ~exist(out,'dir'), mkdir(out); end
s = load([base 'Data_submitted_fly_wNoise11.mat']);
fields = {'thisW','thisW_Kennedy','thetaS','theta_Activity_homeo','APLgains'};
for k=1:numel(fields)
  dlmwrite([out fields{k} '.csv'],s.(fields{k}),',','precision',17);
end
h = load([base 'Compens_variab_rescue_Perf/data/hallem_olsen.mat']);
dlmwrite([out 'hallem.csv'],h.hallem_olsen,',','precision',17);
dlmwrite([out 'author_clean.csv'],s.PNtrials(:,:,1),',','precision',17);
PN=h.hallem_olsen(1:110,:)';
for i=1:24, [prob,bins]=hist(PN(i,:),100); binsAll(i,:)=bins; end
maxRespBinPerPN=max(binsAll,[],2);
maxRespPNsRescaledPerPN=max(s.PNtrials(:,:,1),[],2);
PNsAboveBestFit=true(24,1);
iterations=0;
while sum(PNsAboveBestFit)
  p=polyfit(maxRespBinPerPN(PNsAboveBestFit),maxRespPNsRescaledPerPN(PNsAboveBestFit),1);
  PNsAboveBestFit=maxRespPNsRescaledPerPN > (maxRespBinPerPN*p(1)+p(2)+0.000001);
  iterations=iterations+1;
  if iterations>30, error('Scale recovery cap'); end
end
dlmwrite([out 'pn_scale.csv'],p,',','precision',17);
addpath([base 'Compens_variab_rescue_Perf']);
% Non-evaluation supplied fixture: first 8 odors, first 4 trials, train 2.
X=s.PNtrials(:,1:8,1:4); n=2000;
dlmwrite([out 'fixture_inputs.csv'],reshape(X,24,[]),',','precision',17);
initial=reshape(mod(1:4000,97)/97,2000,2);
dlmwrite([out 'fixture_initial.csv'],initial,',','precision',17);
classAction1=[1 3 5 7];
stats=[];
for arm=1:2
  if arm==1, W=s.thisW; theta=s.thetaS; gain=s.APLgains(1);
  else, W=s.thisW_Kennedy; theta=s.theta_Activity_homeo; gain=s.APLgains(5); end
  A=W'*reshape(X,24,[]);
  Y=((A-gain*repmat(sum(A,1),n,1)-theta)>0).*(A-gain*repmat(sum(A,1),n,1)-theta);
  Y=reshape(Y,n,8,4);
  tr=Y(:,:,1:2); scaler=max(tr(:)); Y=Y/scaler; tr=Y(:,:,1:2);
  op=initial; eta=.001;
  for odor=1:8
    delta=exp(-(eta/mean(tr(:)))*sum(tr(:,odor,:),3));
    if any(classAction1==odor), op(:,2)=op(:,2).*delta;
    else, op(:,1)=op(:,1).*delta; end
  end
  prob=testingModels_accuracies_function(1,op,classAction1,4,2,Y);
  dlmwrite([out sprintf('fixture_Y%d.csv',arm)],reshape(Y,n,[]),',','precision',17);
  dlmwrite([out sprintf('fixture_W%d.csv',arm)],op,',','precision',17);
  stats(arm,:)=[scaler mean(tr(:)) prob];
  % Source-only calibration audit; no new labels or tasks.
  Ac=W'*reshape(s.PNtrials(:,:,1:15),24,[]);
  Yc=max(0,Ac-gain*sum(Ac,1)-theta);
  mu=mean(Yc,2);
  calibration(arm,:)=[mean(Yc(:)>0) mean(mean(Ac-theta>0)) min(mu) max(mu) mean(mu) std(mu) mean(abs(mu-.51)<.51*.06)];
end
dlmwrite([out 'fixture_stats.csv'],stats,',','precision',17);
dlmwrite([out 'calibration_audit.csv'],calibration,',','precision',17);
disp(stats); disp(calibration); disp(p);
