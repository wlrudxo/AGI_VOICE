%% ERG 파일에서 핵심 신호 추출 → core.mat 저장 + 핵심 수치 출력
clear; clc; close all;

%% 파일 선택
[ergFileName, ergPath] = uigetfile('*.erg', 'ERG 파일 선택');
if isequal(ergFileName, 0)
    disp('ERG 파일 선택이 취소되었습니다.');
    return;
end
ergFile = fullfile(ergPath, ergFileName);
fprintf('선택된 ERG 파일: %s\n', ergFile);

%% 데이터 로드
fprintf('\n데이터 로드 중...\n');
data = cmread(ergFile);
fieldNames = fieldnames(data);
fprintf('총 %d개 신호 발견\n', length(fieldNames));

%% 핵심 신호 목록 (논문용)
coreSignals = {
    'Time'
    'Car_v'
    'Car_ax'
    'Car_ay'
    'Car_Fr1_tx'
    'Car_Fr1_ty'
    'Car_Fr1_tz'
    'Car_Pitch'
    'Car_Roll'
    'Car_Yaw'
    'Car_YawRate'
    'DM_Gas'
    'DM_Brake'
    'DM_Steer_Ang'
    'Steer_WhlAng'
    'Brake_Hyd_Sys_pMC'
    'Car_FzFL'
    'Car_FzFR'
    'Car_FzRL'
    'Car_FzRR'
};

%% 핵심 신호 추출
saveData = struct();
missing = {};

for i = 1:length(coreSignals)
    sig = coreSignals{i};
    if isfield(data, sig) && isfield(data.(sig), 'data')
        saveData.(sig) = data.(sig).data;
    else
        missing{end+1} = sig; %#ok<SAGROW>
    end
end

fprintf('\n추출된 신호: %d개\n', length(fieldnames(saveData)));
if ~isempty(missing)
    fprintf('[누락] %s\n', strjoin(missing, ', '));
end

%% 저장
[~, baseName] = fileparts(ergFileName);
scriptPath = fileparts(mfilename('fullpath'));
if isempty(scriptPath), scriptPath = pwd; end

matFileName = fullfile(scriptPath, [baseName '_core.mat']);
save(matFileName, '-struct', 'saveData');
fprintf('\n저장: %s\n', matFileName);

%% 핵심 수치 출력
fprintf('\n========================================\n');
fprintf('핵심 수치\n');
fprintf('========================================\n');
fprintf('  최대 감속도:   %.2f m/s^2\n', min(saveData.Car_ax));
fprintf('  최대 조향각:   %.1f deg\n',   max(abs(rad2deg(saveData.DM_Steer_Ang))));
fprintf('  최종 속도:     %.1f km/h\n',  saveData.Car_v(end) * 3.6);
fprintf('  샘플 수:       %d\n',         length(saveData.Time));
fprintf('  시뮬 시간:     %.1f s\n',     saveData.Time(end));
fprintf('========================================\n');
