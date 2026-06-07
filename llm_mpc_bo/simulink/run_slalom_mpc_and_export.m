% Run the currently configured CarMaker/UserSteer Simulink model and export sigsOut.
%
% Typical MATLAB usage:
%   cd('E:\CarMakerProject\AGI\src_cm4sl')
%   cmenv
%   run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\init_slalom_mpc.m')
%   open_system('UserSteer')
%   run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\run_slalom_mpc_and_export.m')
%
% The script writes:
%   E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\sigsOut_latest\*.csv
%   E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\sigsOut_latest\sigsOut_latest.mat
%   E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\sigsOut_latest_analysis\diagnosis.*

agiVoiceRoot = 'E:\GitProject\AGI_VOICE';
cmProjectSrcDir = 'E:\CarMakerProject\AGI\src_cm4sl';
simulinkDir = fullfile(agiVoiceRoot, 'llm_mpc_bo', 'simulink');
exportDir = fullfile(agiVoiceRoot, 'llm_mpc_bo', 'results', 'processed', 'sigsOut_latest');
analysisDir = fullfile(agiVoiceRoot, 'llm_mpc_bo', 'results', 'processed', 'sigsOut_latest_analysis');
analyzerScript = fullfile(agiVoiceRoot, 'llm_mpc_bo', 'scripts', 'analyze_sigsout_mpc.py');

if exist(cmProjectSrcDir, 'dir')
    cd(cmProjectSrcDir);
end

addpath(simulinkDir);

if ~exist(exportDir, 'dir')
    mkdir(exportDir);
end
if ~exist(analysisDir, 'dir')
    mkdir(analysisDir);
end

mdl = 'UserSteer';
if ~bdIsLoaded(mdl)
    open_system(mdl);
end

% Make the export deterministic even when the model was opened in a fresh
% MATLAB session rather than the user's already configured interactive session.
set_param(mdl, 'SignalLogging', 'on');
set_param(mdl, 'SignalLoggingName', 'sigsOut');
set_param(mdl, 'ReturnWorkspaceOutputs', 'on');

fprintf('[run_slalom_mpc_and_export] Simulating model: %s\n', mdl);
simOut = sim(mdl);

% Prefer Dataset returned by simOut. Fall back to common logging names in both
% simOut and base workspace for models configured differently by hand.
sigsOut = [];
candidateNames = {'sigsOut', 'logsout'};

for k = 1:numel(candidateNames)
    try
        candidate = simOut.get(candidateNames{k});
        if isa(candidate, 'Simulink.SimulationData.Dataset')
            sigsOut = candidate;
            break;
        end
    catch
    end
end

if isempty(sigsOut)
    for k = 1:numel(candidateNames)
        try
            candidate = evalin('base', candidateNames{k});
            if isa(candidate, 'Simulink.SimulationData.Dataset')
                sigsOut = candidate;
                break;
            end
        catch
        end
    end
end

if isempty(sigsOut) || ~isa(sigsOut, 'Simulink.SimulationData.Dataset')
    available = "";
    try
        available = strjoin(string(simOut.who), ", ");
    catch
    end
    error('sigsOut was not found as a Simulink.SimulationData.Dataset. Available simOut variables: %s', available);
end

% Keep the variables visible for interactive MATLAB debugging.
assignin('base', 'simOut', simOut);
assignin('base', 'sigsOut', sigsOut);

% Keep the latest directory deterministic, but only after a valid new
% Dataset exists so a failed run does not erase the previous useful export.
oldCsv = dir(fullfile(exportDir, '*.csv'));
for i = 1:numel(oldCsv)
    delete(fullfile(exportDir, oldCsv(i).name));
end
oldMat = fullfile(exportDir, 'sigsOut_latest.mat');
if exist(oldMat, 'file')
    delete(oldMat);
end

fprintf('[run_slalom_mpc_and_export] Exporting %d signals to %s\n', sigsOut.numElements, exportDir);

for i = 1:sigsOut.numElements
    sig = sigsOut{i};
    rawName = sig.Name;
    if strlength(string(rawName)) == 0
        rawName = sprintf('signal_%02d', i);
    end
    name = matlab.lang.makeValidName(rawName);
    ts = sig.Values;

    time = ts.Time(:);
    data = ts.Data;
    data = data(:);

    if numel(time) ~= numel(data)
        warning('Skipping signal %d (%s): Time/Data lengths differ (%d vs %d).', i, rawName, numel(time), numel(data));
        continue;
    end

    T = table(time, data, 'VariableNames', {'Time', 'Value'});
    outPath = fullfile(exportDir, sprintf('%02d_%s.csv', i, name));
    writetable(T, outPath);
end

save(fullfile(exportDir, 'sigsOut_latest.mat'), 'sigsOut', 'simOut');

% Run Python diagnosis when a Windows Python launcher is available.
if exist(analyzerScript, 'file')
    cmd = sprintf('py -3 "%s" --input-dir "%s" --output-dir "%s"', analyzerScript, exportDir, analysisDir);
    fprintf('[run_slalom_mpc_and_export] Running analyzer: %s\n', cmd);
    [status, output] = system(cmd);
    if status ~= 0
        warning('Python analyzer failed with status %d. Output:\n%s', status, output);
    else
        fprintf('%s\n', output);
    end
else
    warning('Analyzer script not found: %s', analyzerScript);
end

fprintf('[run_slalom_mpc_and_export] Done.\n');

clear agiVoiceRoot cmProjectSrcDir simulinkDir exportDir analysisDir analyzerScript;
clear oldCsv oldMat mdl simOut sigsOut sig rawName name ts time data T outPath;
clear i k cmd status output candidate candidateNames available;
