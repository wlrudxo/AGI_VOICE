@echo off
REM 100 kph까지 가속 후 0까지 감속 시나리오

echo ======================================
echo 시나리오: 100 kph까지 가속 후 정지
echo ======================================

REM 초기 상태
echo.
echo [초기 상태]
python cm_cli.py status

REM 1단계: 가속 시작
echo.
echo [1단계] 가속 시작 (Gas 0.8)
python cm_cli.py cmd "DVAWrite DM.Gas 0.8 -1 Abs"

REM 2단계: 100 kph (27.78 m/s) 도달까지 대기 후 가속 중지
echo.
echo [2단계] 100 kph 도달 대기...
python cm_cli.py wait_until "Car.v >= 27.78" "DVAWrite DM.Gas 0.0 500 Abs" 60

REM 3단계: 브레이크 시작
echo.
echo [3단계] 브레이크 시작 (Brake 0.5)
python cm_cli.py cmd "DVAWrite DM.Brake 0.5 -1 Abs"

REM 4단계: 거의 정지 (1 kph = 0.278 m/s) 까지 대기 후 브레이크 해제
echo.
echo [4단계] 정지 대기...
python cm_cli.py wait_until "Car.v <= 0.278" "DVAWrite DM.Brake 0.0 500 Abs" 60

REM 최종 상태
echo.
echo [최종 상태]
python cm_cli.py status

echo.
echo ======================================
echo 시나리오 완료!
echo ======================================
pause
