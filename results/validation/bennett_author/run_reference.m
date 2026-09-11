% Run from this generated directory in a compatible MATLAB/Octave runtime.
r = dlmread('rewards.csv', ',');
out = mb_mv_a_fixture(0.1, 1, 257, r, 0.01, 'nk', 20, 'plasticity_rule', 'eq8');
trace = zeros(256, 44);
for j = 1:256
    trace(j,:) = [out.map(j,:)-out.mav(j,:), out.dap(j), out.dav(j), out.wkmap(:,:,j+1), out.wkmav(:,:,j+1)];
end
dlmwrite('author_trace.csv', trace, 'delimiter', ',', 'precision', '%.17g');
