function trial = run_slalom_mpc_trial(params, runId, opts)
% Run one Slalom MPC trial and return the BO objective summary.
%
% Example:
%   params = struct('q_y', 10, 'q_psi', 3, 'q_r', 0.2, ...
%       'r_delta', 0.1, 'r_d_delta', 2);
%   trial = run_slalom_mpc_trial(params, 'manual_qy10');
%   trial.J
%
% Normalized BO vector input is also accepted:
%   trial = run_slalom_mpc_trial([0.6 0.5 0.4 0.3 0.6], 'bo_trial_001');

if nargin < 1 || isempty(params)
    params = struct();
end
if nargin < 2 || strlength(string(runId)) == 0
    runId = char(datetime('now', 'Format', 'yyyyMMdd_HHmmss'));
end
if nargin < 3 || isempty(opts)
    opts = struct();
end

repoRoot = get_opt(opts, 'repoRoot', 'E:\GitProject\AGI_VOICE');
cmProjectSrcDir = get_opt(opts, 'cmProjectSrcDir', 'E:\CarMakerProject\AGI\src_cm4sl');
mdl = get_opt(opts, 'model', 'UserSteer');
resultsMatPath = get_opt(opts, 'resultsMatPath', fullfile(cmProjectSrcDir, 'Results.mat'));
trialRoot = get_opt(opts, 'trialRoot', fullfile(repoRoot, 'llm_mpc_bo', 'results', 'trials'));
initScript = fullfile(repoRoot, 'llm_mpc_bo', 'simulink', 'init_slalom_mpc.m');
simulinkDir = fullfile(repoRoot, 'llm_mpc_bo', 'simulink');
scriptsDir = fullfile(repoRoot, 'llm_mpc_bo', 'scripts');

if isnumeric(params)
    normalizedX = double(params(:)');
    params = decode_slalom_mpc_theta(normalizedX);
else
    normalizedX = [];
end

safeRunId = matlab.lang.makeValidName(char(runId));
outputDir = fullfile(trialRoot, safeRunId);
if ~exist(outputDir, 'dir')
    mkdir(outputDir);
end

addpath(simulinkDir);
addpath(scriptsDir);

if exist(cmProjectSrcDir, 'dir')
    cd(cmProjectSrcDir);
else
    error('CarMaker src_cm4sl directory not found: %s', cmProjectSrcDir);
end

if exist('cmenv', 'file')
    cmenv;
else
    warning('cmenv was not found on the MATLAB path. Continuing with current environment.');
end

evalin('base', sprintf("run('%s')", initScript));
mpcobj = apply_slalom_mpc_params(params);

if ~bdIsLoaded(mdl)
    open_system(mdl);
end

if exist(resultsMatPath, 'file')
    beforeInfo = dir(resultsMatPath);
    beforeDatenum = beforeInfo.datenum;
else
    beforeDatenum = -Inf;
end

fprintf('[run_slalom_mpc_trial] runId=%s\n', safeRunId);
fprintf('[run_slalom_mpc_trial] params=%s\n', jsonencode(params));
fprintf('[run_slalom_mpc_trial] sim model=%s\n', mdl);

simStart = datetime('now');
simOut = sim(mdl);
simEnd = datetime('now');
assignin('base', 'simOut', simOut);

if ~exist(resultsMatPath, 'file')
    error('Results.mat was not created: %s', resultsMatPath);
end
afterInfo = dir(resultsMatPath);
if afterInfo.datenum <= beforeDatenum
    error('Results.mat timestamp did not advance. Old/new datenum: %.12f / %.12f', beforeDatenum, afterInfo.datenum);
end

summary = analyze_results_mat(resultsMatPath, outputDir);

trial = struct();
trial.runId = safeRunId;
trial.params = params;
trial.normalizedX = normalizedX;
trial.outputDir = outputDir;
trial.resultsMatPath = resultsMatPath;
trial.simStart = char(simStart);
trial.simEnd = char(simEnd);
trial.summary = summary;
trial.J = summary.objective.JFailClosed;
trial.status = summary.objective.ergStatus;
trial.NViolation = summary.objective.NViolation;
trial.crashOrSimFail = summary.objective.crashOrSimFail;

save(fullfile(outputDir, 'trial.mat'), 'trial');
write_text(fullfile(outputDir, 'trial_summary.json'), jsonencode(trial, PrettyPrint=true));

fprintf('[run_slalom_mpc_trial] J=%g status=%s violations=%d\n', trial.J, trial.status, trial.NViolation);
end

function value = get_opt(opts, name, defaultValue)
if isfield(opts, name) && ~isempty(opts.(name))
    value = opts.(name);
else
    value = defaultValue;
end
end

function write_text(path, text)
fid = fopen(path, 'w');
if fid < 0
    error('Failed to open output file: %s', path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s\n', text);
end
