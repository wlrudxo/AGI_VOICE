#!/bin/bash
# 100 kph까지 가속 후 0까지 감속 시나리오

echo "======================================"
echo "시나리오: 100 kph까지 가속 후 정지"
echo "======================================"

# 초기 상태
echo -e "\n[초기 상태]"
python cm_cli.py status | grep -E "speed_kmh|Car.v"

# 1단계: 가속 시작
echo -e "\n[1단계] 가속 시작 (Gas 0.8)"
python cm_cli.py cmd "DVAWrite DM.Gas 0.8 -1 Abs"

# 2단계: 100 kph (27.78 m/s) 도달까지 대기 후 가속 중지
echo -e "\n[2단계] 100 kph 도달 대기..."
python cm_cli.py wait_until "Car.v >= 27.78" "DVAWrite DM.Gas 0.0 500 Abs" 60

# 3단계: 브레이크 시작
echo -e "\n[3단계] 브레이크 시작 (Brake 0.5)"
python cm_cli.py cmd "DVAWrite DM.Brake 0.5 -1 Abs"

# 4단계: 거의 정지 (1 kph = 0.278 m/s) 까지 대기 후 브레이크 해제
echo -e "\n[4단계] 정지 대기..."
python cm_cli.py wait_until "Car.v <= 0.278" "DVAWrite DM.Brake 0.0 500 Abs" 60

# 최종 상태
echo -e "\n[최종 상태]"
python cm_cli.py status | grep -E "speed_kmh|Car.v"

echo -e "\n======================================"
echo "시나리오 완료!"
echo "======================================"
