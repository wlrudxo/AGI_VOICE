function summary = analyze_results_mat(inputPath, outputDir, deltaCmdMode, ergSummaryPath, verbose)
% Analyze Simulink To File output saved as Results.mat.
%
% Usage:
%   analyze_results_mat('E:\CarMakerProject\AGI\src_cm4sl\Results.mat', ...
%       'E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest')
%
%   % For older files where delta_cmd was logged before the Gain(-1) block:
%   analyze_results_mat('E:\CarMakerProject\AGI\src_cm4sl\Results.mat', ...
%       'E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest', ...
%       'pre_gain')
%
% deltaCmdMode:
%   'applied'  - data.delta_cmd is the actual steering command applied to CarMaker.
%   'pre_gain' - data.delta_cmd is before the Gain(-1) block; applied command is -delta_cmd.
%
% If ergSummaryPath is omitted, this script finds the latest matching CarMaker
% ERG and runs scripts/erg_drive_summary.py before computing the BO objective.

if nargin < 1 || strlength(string(inputPath)) == 0
    inputPath = 'E:\CarMakerProject\AGI\src_cm4sl\Results.mat';
end
if nargin < 2 || strlength(string(outputDir)) == 0
    outputDir = 'E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest';
end
if nargin < 3 || strlength(string(deltaCmdMode)) == 0
    deltaCmdMode = 'applied';
end
if nargin < 4
    ergSummaryPath = '';
end
if nargin < 5
    verbose = true;
end
deltaCmdMode = lower(string(deltaCmdMode));
if ~ismember(deltaCmdMode, ["applied", "pre_gain"])
    error('deltaCmdMode must be either "applied" or "pre_gain".');
end

if ~exist(inputPath, 'file')
    error('Input MAT file not found: %s', inputPath);
end
if ~exist(outputDir, 'dir')
    mkdir(outputDir);
end

loaded = load(inputPath);
if ~isfield(loaded, 'data')
    error('Expected variable "data" was not found in %s', inputPath);
end

data = loaded.data;
signalAliases = struct();
signalAliases.s = {'s'};
signalAliases.t = {'t'};
signalAliases.t_ref = {'t_ref'};
signalAliases.devang = {'devang'};
signalAliases.psi_ref = {'psi_ref'};
signalAliases.yawrate = {'yawrate'};
signalAliases.v = {'v'};
signalAliases.delta_cmd = {'delta_cmd', 'applied_delta_cmd', 'signal1'};
signalAliases.steer_manual = {'steer_manual'};
required = fieldnames(signalAliases);
for i = 1:numel(required)
    if isempty(resolve_signal_name(data, signalAliases.(required{i})))
        error('Required signal "%s" is missing. Tried: %s', required{i}, strjoin(signalAliases.(required{i}), ', '));
    end
end

sTs = get_signal(data, signalAliases.s);
baseTime = double(sTs.Time(:));
if isempty(baseTime)
    error('data.s has no time samples.');
end

signals = struct();
for i = 1:numel(required)
    name = required{i};
    ts = get_signal(data, signalAliases.(name));
    signals.(name) = align_timeseries(ts, baseTime);
end
summarySignalNames = struct();
for i = 1:numel(required)
    name = required{i};
    summarySignalNames.(name) = resolve_signal_name(data, signalAliases.(name));
end

e_t = signals.t - signals.t_ref;
e_psi = signals.devang - signals.psi_ref;
logged_delta_cmd = signals.delta_cmd;
if deltaCmdMode == "pre_gain"
    applied_delta_cmd = -logged_delta_cmd;
else
    applied_delta_cmd = logged_delta_cmd;
end
steer_manual = signals.steer_manual;
applied_delta_rate = rate_from_time(baseTime, applied_delta_cmd);

T = table( ...
    baseTime, ...
    signals.s, ...
    signals.t, ...
    signals.t_ref, ...
    e_t, ...
    signals.devang, ...
    signals.psi_ref, ...
    e_psi, ...
    signals.yawrate, ...
    signals.v, ...
    logged_delta_cmd, ...
    applied_delta_cmd, ...
    applied_delta_rate, ...
    steer_manual, ...
    'VariableNames', { ...
        'Time', 's', 't', 't_ref', 'e_t', 'devang', 'psi_ref', ...
        'e_psi', 'yawrate', 'v', 'delta_cmd_logged', 'applied_delta_cmd', 'applied_delta_rate', 'steer_manual' ...
    } ...
);

writetable(T, fullfile(outputDir, 'aligned_signals.csv'));

active = isfinite(e_t) & isfinite(applied_delta_cmd) & abs(e_t) > 0.05 & abs(applied_delta_cmd) > 0.01;
manualActive = isfinite(e_t) & isfinite(steer_manual) & abs(e_t) > 0.05 & abs(steer_manual) > 0.01;

summary = struct();
summary.generated = char(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss'));
summary.inputPath = char(inputPath);
summary.outputDir = char(outputDir);
summary.samples = numel(baseTime);
summary.timeStart = baseTime(1);
summary.timeEnd = baseTime(end);
summary.duration = baseTime(end) - baseTime(1);
summary.finalS = signals.s(end);
summary.finalV = signals.v(end);
summary.finalT = signals.t(end);
summary.finalTRef = signals.t_ref(end);
summary.finalET = e_t(end);
summary.finalDevAng = signals.devang(end);
summary.finalPsiRef = signals.psi_ref(end);
summary.finalEPsi = e_psi(end);

summary.metrics = struct();
summary.metrics.maxAbsET = max(abs(e_t), [], 'omitnan');
summary.metrics.rmseET = sqrt(mean(e_t.^2, 'omitnan'));
summary.metrics.maxAbsEPsi = max(abs(e_psi), [], 'omitnan');
summary.metrics.rmseEPsi = sqrt(mean(e_psi.^2, 'omitnan'));
summary.deltaCmdMode = char(deltaCmdMode);
summary.signalNames = summarySignalNames;
summary.metrics.maxAbsLoggedDeltaCmd = max(abs(logged_delta_cmd), [], 'omitnan');
summary.metrics.rmseLoggedDeltaCmd = sqrt(mean(logged_delta_cmd.^2, 'omitnan'));
summary.metrics.maxAbsAppliedDeltaCmd = max(abs(applied_delta_cmd), [], 'omitnan');
summary.metrics.rmseAppliedDeltaCmd = sqrt(mean(applied_delta_cmd.^2, 'omitnan'));
summary.metrics.maxAbsAppliedDeltaRate = max(abs(applied_delta_rate), [], 'omitnan');
summary.metrics.rmseAppliedDeltaRate = sqrt(mean(applied_delta_rate.^2, 'omitnan'));
summary.metrics.maxAbsSteerManual = max(abs(steer_manual), [], 'omitnan');
summary.metrics.rmseSteerManual = sqrt(mean(steer_manual.^2, 'omitnan'));
summary.metrics.maxAbsYawRate = max(abs(signals.yawrate), [], 'omitnan');
summary.metrics.meanSpeed = mean(signals.v, 'omitnan');

summary.signDiagnosis = struct();
summary.signDiagnosis.activeSamples = nnz(active);
summary.signDiagnosis.corrETLoggedDeltaCmd = corr_or_nan(e_t(active), logged_delta_cmd(active));
summary.signDiagnosis.loggedSameSignFraction = fraction((e_t(active) .* logged_delta_cmd(active)) > 0);
summary.signDiagnosis.loggedOppositeSignFraction = fraction((e_t(active) .* logged_delta_cmd(active)) < 0);
summary.signDiagnosis.appliedCorrETDeltaCmd = corr_or_nan(e_t(active), applied_delta_cmd(active));
summary.signDiagnosis.appliedSameSignFraction = fraction((e_t(active) .* applied_delta_cmd(active)) > 0);
summary.signDiagnosis.appliedOppositeSignFraction = fraction((e_t(active) .* applied_delta_cmd(active)) < 0);
summary.signDiagnosis.manualActiveSamples = nnz(manualActive);
summary.signDiagnosis.corrETSteerManual = corr_or_nan(e_t(manualActive), steer_manual(manualActive));
summary.signDiagnosis.manualSameSignFraction = fraction((e_t(manualActive) .* steer_manual(manualActive)) > 0);
summary.signDiagnosis.manualOppositeSignFraction = fraction((e_t(manualActive) .* steer_manual(manualActive)) < 0);
summary.signDiagnosis.likelySignIssueLogged = false;
summary.signDiagnosis.likelySignIssueApplied = false;

if ~isnan(summary.signDiagnosis.corrETLoggedDeltaCmd) && ~isnan(summary.signDiagnosis.loggedSameSignFraction)
    summary.signDiagnosis.likelySignIssueLogged = ...
        summary.signDiagnosis.corrETLoggedDeltaCmd > 0.5 && summary.signDiagnosis.loggedSameSignFraction > 0.75;
end
if ~isnan(summary.signDiagnosis.appliedCorrETDeltaCmd) && ~isnan(summary.signDiagnosis.appliedSameSignFraction)
    summary.signDiagnosis.likelySignIssueApplied = ...
        summary.signDiagnosis.appliedCorrETDeltaCmd > 0.5 && summary.signDiagnosis.appliedSameSignFraction > 0.75;
end

summary.events = struct();
summary.events.firstAbsETGt0p1 = first_event(baseTime, signals.s, e_t, abs(e_t) > 0.1);
summary.events.firstAbsETGt0p5 = first_event(baseTime, signals.s, e_t, abs(e_t) > 0.5);
summary.events.firstAbsAppliedDeltaCmdGt0p1 = first_event(baseTime, signals.s, applied_delta_cmd, abs(applied_delta_cmd) > 0.1);
summary.events.firstSGe280 = first_event(baseTime, signals.s, e_t, signals.s >= 280);
summary.events.firstSGe300 = first_event(baseTime, signals.s, e_t, signals.s >= 300);

erg = load_or_create_erg_summary(outputDir, ergSummaryPath);
summary.erg = erg;
summary.objective = compute_bo_objective(summary.metrics, erg);

signalInfo = struct();
fields = fieldnames(data);
for i = 1:numel(fields)
    name = fields{i};
    ts = data.(name);
    info = struct();
    info.class = class(ts);
    if isa(ts, 'timeseries')
        info.samples = numel(ts.Time);
        info.timeStart = double(ts.Time(1));
        info.timeEnd = double(ts.Time(end));
        info.dataSize = size(ts.Data);
    end
    signalInfo.(name) = info;
end
summary.signalInfo = signalInfo;

jsonText = jsonencode(summary, PrettyPrint=true);
write_text(fullfile(outputDir, 'summary.json'), jsonText);
write_markdown(fullfile(outputDir, 'summary.md'), summary);
write_plots(outputDir, T, summary);

if verbose
    fprintf('%s\n', jsonText);
end
end

function name = resolve_signal_name(data, candidates)
name = '';
for i = 1:numel(candidates)
    candidate = candidates{i};
    if isfield(data, candidate)
        name = candidate;
        return;
    end
end
end

function ts = get_signal(data, candidates)
name = resolve_signal_name(data, candidates);
if isempty(name)
    error('Signal not found. Tried: %s', strjoin(candidates, ', '));
end
ts = data.(name);
end

function y = align_timeseries(ts, baseTime)
if ~isa(ts, 'timeseries')
    error('Expected timeseries, got %s.', class(ts));
end
t = double(ts.Time(:));
x = double(ts.Data(:));
if numel(t) ~= numel(x)
    error('Timeseries %s has mismatched time/data lengths.', ts.Name);
end
if numel(t) == numel(baseTime) && max(abs(t - baseTime), [], 'omitnan') < 1e-9
    y = x;
else
    y = interp1(t, x, baseTime, 'linear', 'extrap');
end
end

function rate = rate_from_time(time, value)
time = double(time(:));
value = double(value(:));
rate = zeros(size(value));
if numel(value) < 2
    return;
end
dt = diff(time);
dv = diff(value);
valid = isfinite(dt) & abs(dt) > eps;
stepRate = zeros(size(dv));
stepRate(valid) = dv(valid) ./ dt(valid);
rate(1) = stepRate(1);
rate(2:end) = stepRate;
end

function value = corr_or_nan(a, b)
if numel(a) < 3 || numel(b) < 3 || std(a, 'omitnan') == 0 || std(b, 'omitnan') == 0
    value = NaN;
    return;
end
c = corrcoef(a, b, 'Rows', 'complete');
value = c(1, 2);
end

function value = fraction(mask)
if isempty(mask)
    value = NaN;
else
    value = nnz(mask) / numel(mask);
end
end

function event = first_event(time, s, value, mask)
idx = find(mask, 1, 'first');
event = struct('found', false, 'time', NaN, 's', NaN, 'value', NaN);
if ~isempty(idx)
    event.found = true;
    event.time = time(idx);
    event.s = s(idx);
    event.value = value(idx);
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

function write_markdown(path, summary)
lines = {
    '# Results.mat Analysis'
    ''
    sprintf('- Input: `%s`', summary.inputPath)
    sprintf('- Generated: `%s`', summary.generated)
    sprintf('- Time: `%.4f` to `%.4f` s, samples `%d`', summary.timeStart, summary.timeEnd, summary.samples)
    sprintf('- Final s/v/t/e_t: `%.4f` m, `%.4f` m/s, `%.4f` m, `%.4f` m', summary.finalS, summary.finalV, summary.finalT, summary.finalET)
    ''
    '## Metrics'
    ''
    sprintf('- maxAbs(e_t): `%.6g`', summary.metrics.maxAbsET)
    sprintf('- rmse(e_t): `%.6g`', summary.metrics.rmseET)
    sprintf('- maxAbs(e_psi): `%.6g`', summary.metrics.maxAbsEPsi)
    sprintf('- rmse(e_psi): `%.6g`', summary.metrics.rmseEPsi)
    sprintf('- delta command mode: `%s`', summary.deltaCmdMode)
    sprintf('- maxAbs(delta_cmd logged): `%.6g`', summary.metrics.maxAbsLoggedDeltaCmd)
    sprintf('- rmse(delta_cmd logged): `%.6g`', summary.metrics.rmseLoggedDeltaCmd)
    sprintf('- maxAbs(applied_delta_cmd): `%.6g`', summary.metrics.maxAbsAppliedDeltaCmd)
    sprintf('- rmse(applied_delta_cmd): `%.6g`', summary.metrics.rmseAppliedDeltaCmd)
    sprintf('- maxAbs(applied_delta_rate): `%.6g`', summary.metrics.maxAbsAppliedDeltaRate)
    sprintf('- rmse(applied_delta_rate): `%.6g`', summary.metrics.rmseAppliedDeltaRate)
    sprintf('- maxAbs(steer_manual): `%.6g`', summary.metrics.maxAbsSteerManual)
    sprintf('- rmse(steer_manual): `%.6g`', summary.metrics.rmseSteerManual)
    sprintf('- maxAbs(yawrate): `%.6g`', summary.metrics.maxAbsYawRate)
    sprintf('- mean speed: `%.6g`', summary.metrics.meanSpeed)
    ''
    '## Sign Diagnosis'
    ''
    sprintf('- likely sign issue logged: `%d`', summary.signDiagnosis.likelySignIssueLogged)
    sprintf('- likely sign issue applied: `%d`', summary.signDiagnosis.likelySignIssueApplied)
    sprintf('- active samples: `%d`', summary.signDiagnosis.activeSamples)
    sprintf('- corr(e_t, delta_cmd logged): `%.6g`', summary.signDiagnosis.corrETLoggedDeltaCmd)
    sprintf('- same-sign fraction e_t*delta_cmd logged: `%.6g`', summary.signDiagnosis.loggedSameSignFraction)
    sprintf('- opposite-sign fraction e_t*delta_cmd logged: `%.6g`', summary.signDiagnosis.loggedOppositeSignFraction)
    sprintf('- corr(e_t, applied_delta_cmd): `%.6g`', summary.signDiagnosis.appliedCorrETDeltaCmd)
    sprintf('- same-sign fraction e_t*applied_delta_cmd: `%.6g`', summary.signDiagnosis.appliedSameSignFraction)
    sprintf('- opposite-sign fraction e_t*applied_delta_cmd: `%.6g`', summary.signDiagnosis.appliedOppositeSignFraction)
    sprintf('- corr(e_t, steer_manual): `%.6g`', summary.signDiagnosis.corrETSteerManual)
    ''
    '## BO Objective'
    ''
    sprintf('- J continuous: `%.6g`', summary.objective.JContinuous)
    sprintf('- J fail-closed: `%.6g`', summary.objective.JFailClosed)
    sprintf('- objective used: `%s`', summary.objective.objectiveUsed)
    sprintf('- pylon hits: `%d`', summary.objective.pylonHits)
    sprintf('- collision detected/count: `%d` / `%d`', summary.objective.collisionDetected, summary.objective.collisionCount)
    sprintf('- crash/sim fail: `%d`', summary.objective.crashOrSimFail)
    sprintf('- ERG status: `%s`', summary.objective.ergStatus)
    sprintf('- cost terms: simFail `%.6g`, collision `%.6g`, pylon `%.6g`, tracking `%.6g`, control `%.6g`', ...
        summary.objective.costTerms.simFailPenalty, ...
        summary.objective.costTerms.collisionPenalty, ...
        summary.objective.costTerms.pylonPenalty, ...
        summary.objective.costTerms.trackingCost, ...
        summary.objective.costTerms.controlCost)
    ''
    '## Events'
    ''
    event_line('first_abs_e_t_gt_0p1', summary.events.firstAbsETGt0p1)
    event_line('first_abs_e_t_gt_0p5', summary.events.firstAbsETGt0p5)
    event_line('first_abs_applied_delta_cmd_gt_0p1', summary.events.firstAbsAppliedDeltaCmdGt0p1)
    event_line('first_s_ge_280', summary.events.firstSGe280)
    event_line('first_s_ge_300', summary.events.firstSGe300)
};
write_text(path, strjoin(lines, newline));
end

function write_plots(outputDir, T, summary)
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1200 850]);
tiledlayout(fig, 4, 1, 'TileSpacing', 'compact', 'Padding', 'compact');

nexttile;
plot(T.Time, T.t, 'k-', 'LineWidth', 1.1); hold on;
plot(T.Time, T.t_ref, 'b--', 'LineWidth', 1.0);
plot(T.Time, T.e_t, 'r-', 'LineWidth', 0.9);
grid on;
ylabel('lat [m]');
legend({'t', 't\_ref', 'e\_t'}, 'Location', 'best');
title(sprintf('Results.mat analysis (%s, %.3f s)', summary.deltaCmdMode, summary.duration), 'Interpreter', 'none');

nexttile;
plot(T.Time, T.devang, 'k-', 'LineWidth', 1.0); hold on;
plot(T.Time, T.psi_ref, 'b--', 'LineWidth', 1.0);
plot(T.Time, T.e_psi, 'r-', 'LineWidth', 0.9);
grid on;
ylabel('heading [rad]');
legend({'devang', 'psi\_ref', 'e\_psi'}, 'Location', 'best');

nexttile;
plot(T.Time, T.applied_delta_cmd, 'r-', 'LineWidth', 1.0); hold on;
plot(T.Time, T.steer_manual, 'k--', 'LineWidth', 0.8);
plot(T.Time, T.applied_delta_rate, 'Color', [0.2 0.5 0.9], 'LineWidth', 0.7);
grid on;
ylabel('steer / rate');
legend({'applied delta cmd', 'manual steer', 'applied delta rate'}, 'Location', 'best');

nexttile;
plot(T.Time, T.s, 'k-', 'LineWidth', 1.0); hold on;
yyaxis right;
plot(T.Time, T.v, 'b-', 'LineWidth', 0.9);
grid on;
xlabel('time [s]');
ylabel('v [m/s]');
yyaxis left;
ylabel('s [m]');
legend({'sRoad', 'v'}, 'Location', 'best');

exportgraphics(fig, fullfile(outputDir, 'time_signals.png'), 'Resolution', 160);
close(fig);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1000 500]);
plot(T.s, T.t, 'k-', 'LineWidth', 1.1); hold on;
plot(T.s, T.t_ref, 'b--', 'LineWidth', 1.0);
grid on;
xlabel('sRoad [m]');
ylabel('lateral position [m]');
legend({'t', 't\_ref'}, 'Location', 'best');
title('Path tracking by road distance');
exportgraphics(fig, fullfile(outputDir, 'sroad_tracking.png'), 'Resolution', 160);
close(fig);
end

function erg = load_or_create_erg_summary(outputDir, ergSummaryPath)
erg = struct();
erg.available = false;
erg.path = '';
erg.status = 'unknown';
erg.pylonHitCount = 0;
erg.collisionDetected = false;
erg.collisionCount = 0;
erg.crashOrSimFail = false;
erg.durationS = NaN;
erg.distanceM = NaN;

candidate = string(ergSummaryPath);
if strlength(candidate) == 0
    defaultCandidate = fullfile(outputDir, 'latest_erg_summary.json');
    latestErg = find_latest_erg();
    if strlength(latestErg) > 0
        run_erg_summary(latestErg, outputDir, defaultCandidate);
        candidate = string(defaultCandidate);
    elseif exist(defaultCandidate, 'file')
        candidate = string(defaultCandidate);
    end
end
if strlength(candidate) == 0 || ~exist(candidate, 'file')
    return;
end

raw = jsondecode(fileread(candidate));
erg.available = true;
erg.path = char(candidate);
if isfield(raw, 'pylonHitCount')
    erg.pylonHitCount = raw.pylonHitCount;
end
if isfield(raw, 'collisionDetected')
    erg.collisionDetected = logical(raw.collisionDetected);
end
if isfield(raw, 'collisionCount')
    erg.collisionCount = raw.collisionCount;
end
if isfield(raw, 'sessionLog') && isfield(raw.sessionLog, 'status')
    erg.status = raw.sessionLog.status;
elseif isfield(raw, 'status')
    erg.status = raw.status;
end
if isfield(raw, 'durationS')
    erg.durationS = raw.durationS;
end
if isfield(raw, 'finalSRoadM')
    erg.distanceM = raw.finalSRoadM;
end
erg.crashOrSimFail = ~strcmp(string(erg.status), "SIM_END");
end

function latestErg = find_latest_erg()
latestErg = "";
root = 'E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6';
if ~exist(root, 'dir')
    return;
end
files = dir(fullfile(root, '**', '*.erg'));
if isempty(files)
    return;
end
names = string({files.name});
keep = contains(names, 'LLM_MPC_BO_ICCAS_Slalom18m_UserSteer_CM4SL');
files = files(keep);
if isempty(files)
    return;
end
[~, idx] = max([files.datenum]);
latestErg = string(fullfile(files(idx).folder, files(idx).name));
end

function run_erg_summary(ergPath, outputDir, jsonPath)
repoRoot = 'E:\GitProject\AGI_VOICE';
scriptPath = fullfile(repoRoot, 'llm_mpc_bo', 'scripts', 'erg_drive_summary.py');
csvPath = fullfile(outputDir, 'latest_erg_drive_log.csv');
sessionLog = latest_session_log();

if ~exist(scriptPath, 'file')
    warning('ERG summary script not found: %s', scriptPath);
    return;
end

cmd = sprintf('py -3 "%s" "%s" --json "%s" --csv "%s" --downsample 20', ...
    scriptPath, ergPath, jsonPath, csvPath);
if strlength(sessionLog) > 0
    cmd = sprintf('%s --session-log "%s"', cmd, sessionLog);
end
[status, output] = system(cmd);
if status ~= 0
    warning('ERG summary command failed with status %d:\n%s', status, output);
end
end

function logPath = latest_session_log()
logPath = "";
logDir = 'E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\Log';
if ~exist(logDir, 'dir')
    return;
end
files = dir(fullfile(logDir, '*.log'));
if isempty(files)
    return;
end
[~, idx] = max([files.datenum]);
logPath = string(fullfile(files(idx).folder, files(idx).name));
end

function objective = compute_bo_objective(metrics, erg)
pylonHits = 0;
collisionDetected = false;
collisionCount = 0;
crashOrSimFail = false;
ergStatus = 'unknown';
if isfield(erg, 'available') && erg.available
    pylonHits = erg.pylonHitCount;
    if isfield(erg, 'collisionDetected')
        collisionDetected = logical(erg.collisionDetected);
    end
    if isfield(erg, 'collisionCount')
        collisionCount = erg.collisionCount;
    end
    crashOrSimFail = erg.crashOrSimFail;
    ergStatus = erg.status;
end

RMSE_y = metrics.rmseET;
MAX_y = metrics.maxAbsET;
RMSE_psi = metrics.rmseEPsi;
RMSE_delta = metrics.rmseAppliedDeltaCmd;
RMSE_d_delta = metrics.rmseAppliedDeltaRate;
MAX_r = metrics.maxAbsYawRate;

norm_RMSE_y = 0.50;
norm_MAX_y = 2.00;
norm_RMSE_psi = 0.10;
norm_MAX_r = 0.70;
norm_RMSE_delta = 3.00;
norm_RMSE_d_delta = 10.0;

simFailPenalty = 100.0 * double(crashOrSimFail);
collisionPenalty = 50.0 * double(collisionDetected) + 25.0 * double(collisionCount);
pylonPenalty = 10.0 * double(pylonHits);
trackingCost = ...
    2.00 * RMSE_y / norm_RMSE_y + ...
    1.00 * MAX_y / norm_MAX_y + ...
    0.50 * RMSE_psi / norm_RMSE_psi + ...
    0.30 * MAX_r / norm_MAX_r;
controlCost = ...
    0.10 * RMSE_delta / norm_RMSE_delta + ...
    0.05 * RMSE_d_delta / norm_RMSE_d_delta;

JContinuous = ...
    simFailPenalty + ...
    collisionPenalty + ...
    pylonPenalty + ...
    trackingCost + ...
    controlCost;

if crashOrSimFail
    JFailClosed = JContinuous;
    objectiveUsed = 'fail_closed';
else
    JFailClosed = JContinuous;
    objectiveUsed = 'continuous';
end

objective = struct();
objective.JContinuous = JContinuous;
objective.JFailClosed = JFailClosed;
objective.objectiveUsed = objectiveUsed;
objective.NViolation = pylonHits;
objective.pylonHits = pylonHits;
objective.collisionDetected = collisionDetected;
objective.collisionCount = collisionCount;
objective.crashOrSimFail = crashOrSimFail;
objective.ergStatus = ergStatus;
objective.components = struct( ...
    'RMSE_y', RMSE_y, ...
    'MAX_y', MAX_y, ...
    'RMSE_psi', RMSE_psi, ...
    'RMSE_delta', RMSE_delta, ...
    'RMSE_d_delta', RMSE_d_delta, ...
    'MAX_yaw_rate', MAX_r ...
);
objective.costTerms = struct( ...
    'simFailPenalty', simFailPenalty, ...
    'collisionPenalty', collisionPenalty, ...
    'pylonPenalty', pylonPenalty, ...
    'trackingCost', trackingCost, ...
    'controlCost', controlCost ...
);
objective.normalization = struct( ...
    'RMSE_y', norm_RMSE_y, ...
    'MAX_y', norm_MAX_y, ...
    'RMSE_psi', norm_RMSE_psi, ...
    'MAX_yaw_rate', norm_MAX_r, ...
    'RMSE_delta', norm_RMSE_delta, ...
    'RMSE_d_delta', norm_RMSE_d_delta ...
);
objective.weights = struct( ...
    'simFail', 100.0, ...
    'collisionDetected', 50.0, ...
    'collisionCount', 25.0, ...
    'pylonHit', 10.0, ...
    'RMSE_y', 2.00, ...
    'MAX_y', 1.00, ...
    'RMSE_psi', 0.50, ...
    'MAX_yaw_rate', 0.30, ...
    'RMSE_delta', 0.10, ...
    'RMSE_d_delta', 0.05 ...
);
end

function line = event_line(name, event)
if event.found
    line = sprintf('- `%s`: time `%.4f`, s `%.4f`, value `%.6g`', name, event.time, event.s, event.value);
else
    line = sprintf('- `%s`: n/a', name);
end
end
