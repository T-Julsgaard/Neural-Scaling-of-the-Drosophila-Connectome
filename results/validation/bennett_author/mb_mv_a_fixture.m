% Modified validation wrapper, generated 2026-09-11.
% Bennett, Philippides & Nowotny; BrainsOnBoard/paper_RPEs_in_drosophila_mb
% Source commit 7ec52afb9bd7bb748d94d60dea9f483645a2ce8e; GPL-3.0.
% Original DAN/eq8 arithmetic unchanged; no genetic intervention.
function out = mb_mv_a_fixture(gamma,seed,nt,rs_flag,epskm,varargin)
%
% Mixed valence MB model.
%
% Inputs:
%    gamma - KC->DAN synaptic weight
%     seed - an integer, N, that selects a prime number to seed the random
%            number generator
%       nt - # trials
%  rs_flag - reward schedule ID
%    epskm - learning rate
%
% Outputs:
%  out - struct containing numerous fields (see bottom of script)

%%% Set defaults for optional parameters
intervene_id = 0;
choose1 = false;
no = 2;
period = 100;
nk = 20; % # KCs
lambda = 10;
pr = 'eq8';
%%% Update default parameters with custom options
if nargin>5
  j = 1;
  while j<=numel(varargin)
    if strcmp(varargin{j},'intervene_id')
      % For simulating genetic interventions (e.g. shibire/dTrpA1)
      intervene_id = varargin{j+1}; % Which cell type
      intrvn_type = varargin{j+2}; % 1: multiplicative; 0: additive
      if isscalar(varargin{j+3})
        intrvn_strength = ones(nt,1)*varargin{j+3}; % Strength of intervention
      else
        intrvn_strength = varargin{j+3}; % Strength of intervention
      end;
      j = j + 4;
    elseif strcmp(varargin{j},'choose1')
      % If choose1==true, cue 1 is chosen on every trial.
      choose1 = varargin{j+1}; j = j + 2;
    elseif strcmp(varargin{j},'no')
      % Specify the number of cues
      no = varargin{j+1};
      j = j+2;
    elseif strcmp(varargin{j},'nk')
      % Specify the number of KCs
      nk = varargin{j+1};
      j = j+2;
    elseif strcmp(varargin{j},'period')
      % If using periodic reward schedule: specifiy the period
      period = varargin{j+1};
      j = j+2;
    elseif strcmp(varargin{j},'lambda')
      % Specify constant term in plasticity rule
      lambda = varargin{j+1};
      j = j+2;
    elseif strcmp(varargin{j},'plasticity_rule')
       pr = varargin{j+1}; j = j + 2; % Which learning rule to use
    else
      error('???MB_MV_A: Optional arguments not recognised.');
    end;
  end;
end;

%%%% Reward schedules..............(ID,SD,NT,NO)
if isscalar(rs_flag) % if generating a new reward schedule
  if rs_flag==4
    r = mb_reward_schedules(rs_flag,seed,0.1,nt,2,period);
  else
    r = mb_reward_schedules(rs_flag,seed,0.1,nt,2);
  end;
else % if using a pregenerated reward schedule
  r = rs_flag;
end;

%%% Network setup
sparseness = 1/no; % KC sparseness
% Softmax temperature
T = 0.2;
beta = 1 / T;

%%% Initialise synaptic weights
wkmap = zeros(1,nk,nt); % KC -> M+
wkmav = zeros(1,nk,nt); % KC -> M-
wkmap(:,:,1) = dlmread('initial_plus.csv', ','); 
wkmav(:,:,1) = dlmread('initial_minus.csv', ',');
wkdap = gamma * ones(1,nk); % KC -> D+
wkdav = gamma * ones(1,nk); % KC -> D-
wmapdap = 1; % M+ -> D+
wmavdap = 1; % M- -> D+
wmapdav = 1; % M+ -> D-
wmavdav = 1; % M- -> D-

%%% Generate KC responses to cues
s = zeros(nk,no);
for j=1:no
  s(floor((j-1)*sparseness*nk)+1:floor(j*sparseness*nk),j) = 1;
  s(:,j) = s(:,j) / sum(s(:,j)) * 10;    
end;

s = dlmread('activities.csv', ',');
provided_choices = dlmread('choices.csv', ',');

%%% Allocate memory for firing rates
dap = zeros(nt,1);
dav = zeros(nt,1);
map = zeros(nt,no);
mav = zeros(nt,no);
go = zeros(nt,no);
nogo = zeros(nt,no);
decision = zeros(nt,1);
sr = 0;
probs = zeros(no,1);

%%% Run simulation
for j=1:nt  % Loop over trials
  % Compute MBON firing rates and reward predictions (mdiff)
  for stim=1:no
    map(j,stim) = wkmap(:,:,j) * s(:,stim);
    mav(j,stim) = wkmav(:,:,j) * s(:,stim);
        
    % For "genetic" interventions
    if any(intervene_id==1)
      map(j,stim) = max(0,intrvn_type * map(j,stim) * intrvn_strength(j) + (1-intrvn_type) * (map(j,stim) + intrvn_strength(j)));
    end;
    if any(intervene_id==2)
      mav(j,stim) = max(0,intrvn_type * mav(j,stim) * intrvn_strength(j) + (1-intrvn_type) * (mav(j,stim) + intrvn_strength(j)));
    end;
    
    % Positive value    
    go(j,stim) = map(j,stim);
    % Negative value
    nogo(j,stim) = mav(j,stim);      
  end;        
  
  decision(j) = provided_choices(j) + 1;

  % Compute DAN firing rates
  dap(j) = max(0,wkdap * s(:,decision(j)) - wmapdap * map(j,decision(j)) + wmavdap * mav(j,decision(j)) + r(j,decision(j)));
  dav(j) = max(0,wkdav * s(:,decision(j)) - wmavdav * mav(j,decision(j)) + wmapdav * map(j,decision(j)) - r(j,decision(j)));   
  
  % For "genetic" interventions
  if any(intervene_id==3)
    dap(j) = max(0,intrvn_type * dap(j) * intrvn_strength(j) + (1-intrvn_type) * (dap(j) + intrvn_strength(j)));
  end;
  if any(intervene_id==4)
    dav(j) = max(0,intrvn_type * dav(j) * intrvn_strength(j) + (1-intrvn_type) * (dav(j) + intrvn_strength(j)));
  end;
  
  % Update KC->MBON weights (except on last trial)
  if j<nt
    if strcmp(pr,'eq8')
      wkmap(:,:,j+1) = max(0,wkmap(:,:,j) + epskm * s(:,decision(j))' .* (dap(j) - dav(j)));
      wkmav(:,:,j+1) = max(0,wkmav(:,:,j) + epskm * s(:,decision(j))' .* (dav(j) - dap(j)));
    elseif strcmp(pr,'eq7')
%       wkmap(:,:,j+1) = max(0,wkmap(:,:,j) + epskm * s(:,decision(j))' .* (wkdav * s(:,decision(j)) - dav(j)));
%       wkmav(:,:,j+1) = max(0,wkmav(:,:,j) + epskm * s(:,decision(j))' .* (wkdap * s(:,decision(j)) - dap(j)));
      wkmap(:,:,j+1) = max(0,wkmap(:,:,j) + epskm * s(:,decision(j))' .* (lambda + wkdap * s(:,decision(j)) - dav(j)));
      wkmav(:,:,j+1) = max(0,wkmav(:,:,j) + epskm * s(:,decision(j))' .* (lambda + wkdap * s(:,decision(j)) - dap(j)));
    end;
  end;
  
  % Update summed reward and RPE
  sr = sr + r(j,decision(j));
end;

%%% Creater output struct
out.map = map;
out.mav = mav;
out.dap = dap;
out.dav = dav;
out.go = go;
out.nogo = nogo;
out.wkmap = wkmap;
out.wkmav = wkmav;
out.decision = decision;
n1 = decision==1; n2 = decision==2; 
out.pi = (n1-n2) ./ (n1+n2);
out.r = r;
out.s = s;
out.sr = sr;
