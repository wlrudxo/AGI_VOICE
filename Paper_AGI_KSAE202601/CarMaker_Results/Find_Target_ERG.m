%% ERG 파일 일괄 검색: DM_Brake max=0.5 & Car_Fr1_ty max>94 찾기
clear; clc;

%% 검색 경로
searchPath = 'E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260108';
ergFiles = dir(fullfile(searchPath, '*.erg'));
fprintf('총 %d개 ERG 파일 발견\n\n', length(ergFiles));

%% 검색
results = {};
for i = 1:length(ergFiles)
    ergFile = fullfile(searchPath, ergFiles(i).name);
    try
        data = cmread(ergFile);

        % 필요 신호 존재 확인
        if ~isfield(data, 'DM_Brake') || ~isfield(data, 'Car_Fr1_ty')
            continue;
        end

        brakeMax = max(data.DM_Brake.data);
        tyMax    = max(data.Car_Fr1_ty.data);

        % 조건: DM_Steer_Ang 최대값(양수)이 +1.4 rad 근처 (±0.15)
        steerMax_pos = max(data.DM_Steer_Ang.data);  % 양수 최대값
        if abs(steerMax_pos - 1.4) < 0.15
            % 추가 수치
            vEnd     = data.Car_v.data(end) * 3.6;
            axMin    = min(data.Car_ax.data);
            steerMax = max(abs(rad2deg(data.DM_Steer_Ang.data)));

            fprintf('[MATCH] %s\n', ergFiles(i).name);
            fprintf('  Brake max=%.2f, ty max=%.2f, v_end=%.1f km/h, ax_min=%.2f, steer_max=%.1f deg\n\n', ...
                    brakeMax, tyMax, vEnd, axMin, steerMax);

            results{end+1} = ergFiles(i).name; %#ok<SAGROW>
        end
    catch
        % 읽기 실패 무시
    end

    % 진행률 (50개마다)
    if mod(i, 50) == 0
        fprintf('  ... %d/%d 검색 중\n', i, length(ergFiles));
    end
end

fprintf('\n========================================\n');
fprintf('검색 완료: %d개 매치 / %d개 전체\n', length(results), length(ergFiles));
fprintf('========================================\n');
