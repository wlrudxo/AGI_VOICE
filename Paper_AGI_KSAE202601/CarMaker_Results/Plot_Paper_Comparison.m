%% 논문용 3-way 비교 그래프
%% Figure 1: X-Y 궤적
%% Figure 2: 제어 입력 (조향 + 제동)
%% Figure 3: 차량 속도
clear; clc; close all;

%% ====================================================================
%% 파일명 입력
%% ====================================================================
dataPath = fileparts(mfilename('fullpath'));
if isempty(dataPath), dataPath = pwd; end

fname_rule   = 'AEB_Rule_core.mat';
fname_single = 'AEB_LLM_Single_core.mat';
fname_loop   = 'AEB_LLM_Loop_core.mat';

%% ====================================================================
%% 데이터 로드
%% ====================================================================
d_rule   = load(fullfile(dataPath, fname_rule));
d_single = load(fullfile(dataPath, fname_single));
d_loop   = load(fullfile(dataPath, fname_loop));

fprintf('Rule-based:    %s (%d samples)\n', fname_rule,   length(d_rule.Time));
fprintf('Single-shot:   %s (%d samples)\n', fname_single, length(d_single.Time));
fprintf('Feedback Loop: %s (%d samples)\n', fname_loop,   length(d_loop.Time));

%% ====================================================================
%% 시간 트림 (12초까지)
%% ====================================================================
tMax = 11.5;
d_rule   = trimData(d_rule,   tMax);
d_single = trimData(d_single, tMax);
d_loop   = trimData(d_loop,   tMax);

%% ====================================================================
%% 단위 변환
%% ====================================================================
v_rule   = d_rule.Car_v   * 3.6;
v_single = d_single.Car_v * 3.6;
v_loop   = d_loop.Car_v   * 3.6;

steer_rule   = rad2deg(d_rule.DM_Steer_Ang);
steer_single = rad2deg(d_single.DM_Steer_Ang);
steer_loop   = rad2deg(d_loop.DM_Steer_Ang);

%% ====================================================================
%% 스타일 설정
%% ====================================================================
c_rule   = [0.5 0.5 0.5];   % 회색
c_single = [0.85 0.33 0.1]; % 주황
c_loop   = [0.0 0.45 0.74]; % 파랑

lw = 1.5;
fs = 10;
labels = {'Rule-based (AEB)', 'LLM Single-shot', 'LLM Feedback Loop'};
outDir = fileparts(dataPath);  % Paper_AGI_KSAE202601 폴더

%% ====================================================================
%% Figure 1: 궤적 (X=종방향, Y=횡방향) — 가로로 긴 1-column 그림
%% ====================================================================
fig1 = figure('Units', 'centimeters', 'Position', [2 2 16 7]);
hold on; box on;

% 건물 영역 (97.5~98.5)
fill([20 60 60 20], [97.5 97.5 98.5 98.5], [0.70 0.65 0.60], 'EdgeColor', 'none', 'FaceAlpha', 0.8);
text(40, 98, 'Building', 'FontSize', fs-2, 'Color', [1 1 1], 'HorizontalAlignment', 'center', 'FontWeight', 'bold');

% 보행자도로 (94.5~97.5)
fill([20 60 60 20], [94.5 94.5 97.5 97.5], [0.88 0.92 0.88], 'EdgeColor', 'none', 'FaceAlpha', 0.4);
text(40, 96, 'Sidewalk', 'FontSize', fs-2, 'Color', [0.35 0.45 0.35], 'HorizontalAlignment', 'center');

% 도로 경계 (실선, 굵게)
plot([20 60], [88.5 88.5], '-', 'Color', [0.15 0.15 0.15], 'LineWidth', 2.0);
plot([20 60], [94.5 94.5], '-', 'Color', [0.15 0.15 0.15], 'LineWidth', 2.0);
plot([20 60], [97.5 97.5], '-', 'Color', [0.15 0.15 0.15], 'LineWidth', 1.5);

% 차선 중앙선 (점선)
plot([20 60], [91.5 91.5], '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 1.0);

% 궤적 (X=ty 종방향, Y=tx 횡방향)
plotTrajGrad(d_rule.Car_Fr1_ty,   d_rule.Car_Fr1_tx,   c_rule,   lw);
% Single: lateral 최대 지점(충돌)까지만 표시
[~, idxMaxLat_traj] = max(d_single.Car_Fr1_tx);
plotTrajGrad(d_single.Car_Fr1_ty(1:idxMaxLat_traj), d_single.Car_Fr1_tx(1:idxMaxLat_traj), c_single, lw);
plotTrajGrad(d_loop.Car_Fr1_ty,   d_loop.Car_Fr1_tx,   c_loop,   lw);

% 시작점
plot(d_rule.Car_Fr1_ty(1), d_rule.Car_Fr1_tx(1), 'ko', 'MarkerSize', 7, 'MarkerFaceColor', 'k');

% Rule 끝점 — Collision 표시
plot(d_rule.Car_Fr1_ty(end), d_rule.Car_Fr1_tx(end), 'x', 'Color', [0.8 0 0], 'MarkerSize', 10, 'LineWidth', 2.5);
text(d_rule.Car_Fr1_ty(end)-0.5, d_rule.Car_Fr1_tx(end)+0.5, 'Collision', ...
     'FontSize', fs-2, 'Color', [0.8 0 0], 'FontWeight', 'bold', 'HorizontalAlignment', 'left');

% Single — Lateral 최대 지점에서 Collision 표시
[~, idxMaxLat] = max(d_single.Car_Fr1_tx);
plot(d_single.Car_Fr1_ty(idxMaxLat), d_single.Car_Fr1_tx(idxMaxLat), 'x', 'Color', [0.8 0 0], 'MarkerSize', 10, 'LineWidth', 2.5);
text(d_single.Car_Fr1_ty(idxMaxLat), d_single.Car_Fr1_tx(idxMaxLat)-0.7, 'Collision', ...
     'FontSize', fs-2, 'Color', [0.8 0 0], 'FontWeight', 'bold', 'HorizontalAlignment', 'center');

% Loop 끝점
plot(d_loop.Car_Fr1_ty(end), d_loop.Car_Fr1_tx(end), 's', 'Color', c_loop, 'MarkerSize', 7, 'MarkerFaceColor', c_loop);

% AEB Trigger — 조향각이 처음 크게 변하는 시점
steerThresh = 5;  % deg
idxAction_s = find(abs(steer_single) > steerThresh, 1, 'first');
if ~isempty(idxAction_s)
    ax_act = d_single.Car_Fr1_ty(idxAction_s);
    ay_act = d_single.Car_Fr1_tx(idxAction_s);
    plot(ax_act, ay_act, 'd', 'Color', [0.1 0.6 0.1], 'MarkerSize', 9, 'MarkerFaceColor', [0.2 0.8 0.2], 'LineWidth', 1.2);
    text(ax_act-0.5, ay_act+0.5, 'AEB Trigger', 'FontSize', fs-2, 'Color', [0.1 0.5 0.1], 'FontWeight', 'bold', 'HorizontalAlignment', 'left');
end

h1 = plot(NaN, NaN, '-', 'Color', c_rule,   'LineWidth', lw);
h2 = plot(NaN, NaN, '-', 'Color', c_single, 'LineWidth', lw);
h3 = plot(NaN, NaN, '-', 'Color', c_loop,   'LineWidth', lw);
legend([h1 h2 h3], labels, 'Location', 'best', 'FontSize', fs-2);

xlabel('Longitudinal [m]', 'FontSize', fs);
ylabel('Lateral [m]', 'FontSize', fs);
xlim([20 60]);
ylim([88 98.5]);
set(gca, 'FontSize', fs, 'XDir', 'reverse');

saveFig(fig1, outDir, 'Fig_Trajectory');
fprintf('\nFig1 (궤적) 저장 완료\n');

%% ====================================================================
%% Figure 2: 제어 입력 (조향 + 제동)
%% ====================================================================
fig2 = figure('Units', 'centimeters', 'Position', [12 2 9 10]);

% (a) 조향각
subplot(2,1,1);
hold on; grid on; box on;
plot(d_rule.Time,   steer_rule,   '-', 'Color', c_rule,   'LineWidth', lw);
plot(d_single.Time, steer_single, '-', 'Color', c_single, 'LineWidth', lw);
plot(d_loop.Time,   steer_loop,   '-', 'Color', c_loop,   'LineWidth', lw);
ylabel('Steering [deg]', 'FontSize', fs);
title('(a) Steering angle', 'FontSize', fs);
legend(labels, 'Location', 'best', 'FontSize', fs-3);
xlim([0 11.5]);
set(gca, 'FontSize', fs-1);

% (b) 제동
subplot(2,1,2);
hold on; grid on; box on;
plot(d_rule.Time,   d_rule.DM_Brake,   '-', 'Color', c_rule,   'LineWidth', lw);
plot(d_single.Time, d_single.DM_Brake, '-', 'Color', c_single, 'LineWidth', lw);
plot(d_loop.Time,   d_loop.DM_Brake,   '-', 'Color', c_loop,   'LineWidth', lw);
ylabel('Brake [-]', 'FontSize', fs);
xlabel('Time [s]', 'FontSize', fs);
title('(b) Brake input', 'FontSize', fs);
ylim([-0.05 1.05]);
xlim([0 11.5]);
set(gca, 'FontSize', fs-1);

saveFig(fig2, outDir, 'Fig_ControlInput');
fprintf('Fig2 (제어) 저장 완료\n');

%% ====================================================================
%% Figure 3: 차량 응답 (속도 + 요레이트)
%% ====================================================================
yawrate_rule   = rad2deg(d_rule.Car_YawRate);
yawrate_single = rad2deg(d_single.Car_YawRate);
yawrate_loop   = rad2deg(d_loop.Car_YawRate);

fig3 = figure('Units', 'centimeters', 'Position', [22 2 9 10]);

% (a) 속도
subplot(2,1,1);
hold on; grid on; box on;
plot(d_rule.Time,   v_rule,   '-', 'Color', c_rule,   'LineWidth', lw);
plot(d_single.Time, v_single, '-', 'Color', c_single, 'LineWidth', lw);
plot(d_loop.Time,   v_loop,   '-', 'Color', c_loop,   'LineWidth', lw);
ylabel('Velocity [km/h]', 'FontSize', fs);
title('(a) Vehicle speed', 'FontSize', fs);
legend(labels, 'Location', 'best', 'FontSize', fs-3);
xlim([0 11.5]);
set(gca, 'FontSize', fs-1);

% (b) 요레이트
subplot(2,1,2);
hold on; grid on; box on;
plot(d_rule.Time,   yawrate_rule,   '-', 'Color', c_rule,   'LineWidth', lw);
plot(d_single.Time, yawrate_single, '-', 'Color', c_single, 'LineWidth', lw);
plot(d_loop.Time,   yawrate_loop,   '-', 'Color', c_loop,   'LineWidth', lw);
ylabel('Yaw rate [deg/s]', 'FontSize', fs);
xlabel('Time [s]', 'FontSize', fs);
title('(b) Yaw rate', 'FontSize', fs);
xlim([0 11.5]);
set(gca, 'FontSize', fs-1);

saveFig(fig3, outDir, 'Fig_VehicleResponse');
fprintf('Fig3 (차량응답) 저장 완료\n');

%% ====================================================================
%% 핵심 수치 출력
%% ====================================================================
fprintf('\n========================================\n');
fprintf('논문용 비교표 (t <= %.1f s)\n', tMax);
fprintf('========================================\n');
fprintf('%-24s | %-14s | %-14s | %-14s\n', '', 'Rule-based', 'Single-shot', 'Feedback Loop');
fprintf('%-24s-+-%-14s-+-%-14s-+-%-14s\n', '------------------------', '--------------', '--------------', '--------------');
fprintf('%-24s | %-14s | %-14s | %-14s\n', '제동 입력',       'AEB only',      '0.5',           '0.6');
fprintf('%-24s | %-14s | %-14s | %-14s\n', '조향 입력 [rad]', '---',           '1.4',           '1.0');
fprintf('%-24s | %-14s | %-14s | %-14s\n', '충돌 여부',       '보행자 충돌',    '건물 충돌',      '회피 성공');
fprintf('%-24s | %-14.2f | %-14.2f | %-14.2f\n', '최대 감속도 [m/s^2]', min(d_rule.Car_ax), min(d_single.Car_ax), min(d_loop.Car_ax));
fprintf('========================================\n');

%% ====================================================================
%% 로컬 함수
%% ====================================================================
function d = trimData(d, tMax)
    idx = d.Time <= tMax;
    fnames = fieldnames(d);
    for i = 1:length(fnames)
        f = fnames{i};
        if isnumeric(d.(f)) && length(d.(f)) == length(idx)
            d.(f) = d.(f)(idx);
        end
    end
end

function saveFig(fig, outDir, name)
    exportgraphics(fig, fullfile(outDir, [name '.png']), 'Resolution', 300);
    exportgraphics(fig, fullfile(outDir, [name '.eps']), 'ContentType', 'vector');
    savefig(fig, fullfile(outDir, [name '.fig']));
end

function plotTrajGrad(x, y, baseColor, lw)
    n = length(x);
    nSeg = 20;
    idx = round(linspace(1, n, nSeg+1));
    for i = 1:nSeg
        alpha = i / nSeg;
        segColor = 1 - alpha * (1 - baseColor);
        range = idx(i):idx(i+1);
        plot(x(range), y(range), '-', 'Color', segColor, 'LineWidth', lw);
    end
end
