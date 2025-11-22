# CarMaker Python 제어 시스템 통합 가이드

본 문서는 CarMaker를 Python으로 제어하는 시스템을 실제 프로그램에 이식하기 위한 가이드입니다.

---

## 목차
1. [CarMaker 정보 취득/제어 Python 사용](#1-carmaker-정보-취득제어-python-사용)
2. [텍스트 기반 제어 시스템](#2-텍스트-기반-제어-시스템)
3. [조건부 정지 및 제어명령 재생](#3-조건부-정지-및-제어명령-재생)

---

## 1. CarMaker 정보 취득/제어 Python 사용

### 1.1 핵심 구조

```
CarMaker APO (port 16660)
    ↕ TCP Socket
CarMakerClient (carmaker_client.py)
    ↕
Your Application
```

### 1.2 기본 사용법

#### 연결 및 정보 취득

```python
from carmaker_client import CarMakerClient

# 1. 클라이언트 생성
client = CarMakerClient(host='localhost', port=16660)

# 2. 연결
success, msg = client.connect()
if not success:
    print(f"Connection failed: {msg}")
    return

# 3. 정보 취득 (최적화된 방식)
data = client.read_essential_quantities()

# 4. 데이터 사용
ego_speed = data.get('Car.v', 0.0)  # m/s
ego_sRoad = data.get('Vhcl.sRoad', 0.0)  # m
traffic_count = data.get('Traffic.nObjs', 0)

# 앞 차량 정보 (있는 경우)
front_vehicle_speed = data.get('Traffic.T00.LongVel', None)
front_vehicle_sRoad = data.get('Traffic.T00.sRoad', None)
```

#### 제어 명령 전송

```python
# 방법 1: 직접 제어 (간단한 명령)
client.set_control('gas', 0.5, duration=2000, mode='Abs')
client.set_control('brake', 0.3, duration=1000, mode='Abs')

# 방법 2: DVAWrite 직접 사용 (유연함)
success, response = client.execute_command("DVAWrite DM.Gas 0.5 2000 Abs")
success, response = client.execute_command("DVAWrite DM.v.Trgt 27.78 -1 Abs")

# 방법 3: 시뮬레이션 제어
client.execute_command("StartSim")
client.execute_command("StopSim")
client.execute_command("DVAWrite SC.TAccel 0.001 30000 Abs")  # 일시정지
```

### 1.3 성능 최적화된 정보 취득

**현재 구현된 최적화 방식**:

```python
# carmaker_client.py의 read_essential_quantities() 동작:
# 1. ego vehicle 정보 (12개 변수)
# 2. Traffic.nObjs (첫 번째만 읽고 캐싱)
# 3. 모든 차량의 sRoad 읽기 (경량)
# 4. ego 기준 앞/뒤 차량만 상세 정보
# → 총 56개 변수, 약 1초 소요 (시뮬레이션 0.01초 샘플타임 기준)
```

**성능 수치**:
- 기존 모든 차량 정보: 334개 변수 → 7초
- 최적화 후: 56개 변수 → **1초**
- **83% 감소**

### 1.4 수집되는 정보

#### Ego Vehicle (항상 수집)
```python
data = {
    'Time': 10.5,              # 시뮬레이션 시간 (s)
    'DM.Gas': 0.0,             # 가스 페달 (0-1)
    'DM.Brake': 0.0,           # 브레이크 페달 (0-1)
    'DM.Steer.Ang': 0.0,       # 조향각 (rad)
    'DM.GearNo': 3,            # 기어
    'Car.v': 27.78,            # 속도 (m/s)
    'Vhcl.YawRate': 0.0,       # 요 레이트 (rad/s)
    'Vhcl.Steer.Ang': 0.0,     # 휠 조향각 (rad)
    'Vhcl.sRoad': 150.0,       # 도로 좌표 S (m)
    'Vhcl.tRoad': 0.0,         # 횡방향 위치 T (m)
    'DM.v.Trgt': 27.78,        # 목표 속도 (m/s)
    'DM.LaneOffset': 0.0,      # 차선 오프셋 (m)
}
```

#### Traffic (앞/뒤 차량만 상세)
```python
# 앞 차량이 T05, 뒤 차량이 T12라고 가정
data = {
    'Traffic.nObjs': 32,       # 전체 차량 수

    # 앞 차량 (T05)
    'Traffic.T05.tx': 120.5,   # 위치 X (m)
    'Traffic.T05.ty': 3.5,     # 위치 Y (m)
    'Traffic.T05.v_0.x': 25.0, # 속도 X (m/s)
    'Traffic.T05.v_0.y': 0.0,  # 속도 Y (m/s)
    'Traffic.T05.LongVel': 25.0,  # 종방향 속도 (m/s)
    'Traffic.T05.sRoad': 170.0,   # 도로 좌표 (m)
    'Traffic.T05.tRoad': 0.2,     # 횡방향 거리 (m)

    # 뒤 차량 (T12)
    'Traffic.T12.tx': 100.3,
    'Traffic.T12.ty': 3.4,
    # ... 동일한 구조
}
```

### 1.5 주의사항

**1. 시뮬레이션 샘플타임 영향**
```python
# CarMaker 샘플타임 = 0.01초 (100Hz)
# 각 DVARead는 최소 0.01초 소요
# 56개 변수 × 0.01초 ≈ 0.56초 + 네트워크 오버헤드 = 약 1초
```

**2. 타임아웃 설정**
```python
# 타임아웃은 "최대 대기시간"일 뿐, 줄인다고 빨라지지 않음
# 응답이 빠르면: 0.01초에 반환 (타임아웃 무관)
# 응답이 느리면: 타임아웃까지 대기 후 에러
# 권장: 0.3초 (안정적)
```

**3. 연결 끊김 처리**
```python
if not client.connected:
    success, msg = client.connect()
    if not success:
        # 재연결 실패 처리
        pass
```

**4. 스레드 안전성**
```python
# CarMakerClient는 내부적으로 threading.Lock 사용
# 여러 스레드에서 동시 호출 가능
with client.lock:
    response = client.send_command("...")
```

### 1.6 실제 이식 시 체크리스트

- [ ] CarMaker APO 포트 확인 (기본 16660)
- [ ] 네트워크 방화벽 설정 (원격 연결 시)
- [ ] 시뮬레이션 샘플타임 확인 (성능에 영향)
- [ ] 필요한 UAQ 변수만 추가 (`ego_quantities`, `traffic_obj_quantities` 수정)
- [ ] 에러 처리 및 재연결 로직 구현
- [ ] 로깅 시스템 통합

---

## 2. 텍스트 기반 제어 시스템

### 2.1 개요

텍스트 명령으로 CarMaker를 제어하는 시스템입니다. CLI, GUI, LLM 등 다양한 인터페이스에서 사용 가능합니다.

### 2.2 명령 형식

#### 기본 CarMaker 명령

```python
# DVAWrite: 변수 쓰기
"DVAWrite <Name> <Value> [Duration] [Mode]"

# DVARead: 변수 읽기
"DVARead <Name>"

# 시뮬레이션 제어
"StartSim"
"StopSim"
"GetSimStatus"
```

#### 예제 명령

```python
# 가스 페달 50%, 2초간 유지
"DVAWrite DM.Gas 0.5 2000 Abs"

# 목표 속도 100km/h (27.78m/s), 무한 유지
"DVAWrite DM.v.Trgt 27.78 -1 Abs"

# 시뮬레이션 일시정지 (30초간)
"DVAWrite SC.TAccel 0.001 30000 Abs"

# 시뮬레이션 재개
"DVAWrite SC.TAccel 1.0 -1 Abs"

# 브레이크 30%, 1초간
"DVAWrite DM.Brake 0.3 1000 Abs"
```

### 2.3 구현 방법

#### 단일 명령 실행

```python
from carmaker_client import CarMakerClient

client = CarMakerClient()
client.connect()

# 명령 실행
success, response = client.execute_command("DVAWrite DM.Gas 0.5 2000 Abs")

if success:
    print(f"Success: {response}")
else:
    print(f"Error: {response}")
```

#### 배치 명령 실행

```python
# 파일에서 명령 읽기
commands_text = """
# 가속 테스트
DVAWrite DM.Gas 0.7 3000 Abs
DVAWrite DM.Brake 0.0 100 Abs

# 속도 유지
DVAWrite DM.v.Trgt 27.78 -1 Abs
"""

results = client.execute_batch_commands(commands_text)

for cmd, success, response in results:
    print(f"{cmd}: {response}")
```

#### CLI 인터페이스 사용

```bash
# 단일 명령
python cm_cli.py cmd "DVAWrite DM.Gas 0.5 2000 Abs"

# 상태 조회
python cm_cli.py status

# 조건부 실행
python cm_cli.py wait_until "Car_v >= 27.78" "DVAWrite DM.Brake 0.3 2000 Abs" 30
```

### 2.4 GUI 통합

```python
import tkinter as tk
from carmaker_control_server import CarMakerControlServer

# Control Server 사용 (GUI + CLI 동시 지원)
server = CarMakerControlServer()
server.connect_carmaker()

# GUI에서 텍스트 입력 → 명령 실행
def execute_command_from_gui():
    command = cmd_entry.get().strip()
    if command:
        server.execute_command(command)
        # 결과는 log callback으로 전달됨
```

### 2.5 LLM 통합

```python
# LLM이 생성한 Python 스크립트 실행
script = """
execute_cmd('DVAWrite DM.Gas 0.5 2000 Abs')
wait(2.0)
execute_cmd('DVAWrite DM.Brake 0.3 1000 Abs')
log('Braking applied')
"""

# llm_integration.py의 ScriptExecutor 사용
from llm_integration import ScriptExecutor

executor = ScriptExecutor(server)
success, result = executor.execute_script(script)
```

### 2.6 명령 검증

```python
def validate_command(cmd):
    """명령 유효성 검사"""
    cmd = cmd.strip()

    # 빈 명령
    if not cmd:
        return False, "Empty command"

    # 주석
    if cmd.startswith('#') or cmd.startswith('//'):
        return True, "Comment (skipped)"

    # DVAWrite 검증
    if cmd.startswith("DVAWrite"):
        parts = cmd.split()
        if len(parts) < 3:
            return False, "DVAWrite requires at least Name and Value"

        # 값이 숫자인지 확인
        try:
            float(parts[2])
        except ValueError:
            return False, f"Invalid value: {parts[2]}"

    return True, "Valid"

# 사용 예
valid, msg = validate_command("DVAWrite DM.Gas 0.5 2000 Abs")
if valid:
    client.execute_command(command)
```

### 2.7 실제 이식 시 체크리스트

- [ ] 명령 히스토리 저장 (undo/redo 기능)
- [ ] 명령 템플릿 시스템 (자주 쓰는 명령 저장)
- [ ] 명령 유효성 검사 (실행 전 검증)
- [ ] 에러 처리 및 사용자 피드백
- [ ] 명령 로깅 (디버깅 및 분석용)
- [ ] 권한 관리 (위험한 명령 제한)

---

## 3. 조건부 정지 및 제어명령 재생

### 3.1 개요

특정 조건이 만족되면 시뮬레이션을 일시정지하고, 제어명령을 받아 재생하는 시스템입니다.

### 3.2 핵심 개념

```
모니터링 루프 (10Hz)
    ↓
조건 평가 (매 루프)
    ↓
조건 만족? → YES → 시뮬레이션 일시정지
                  ↓
                제어명령 대기
                  ↓
                명령 실행
                  ↓
                시뮬레이션 재개
```

### 3.3 조건 평가 시스템

#### 조건 문법

```python
# 변수명: 점(.)을 언더스코어(_)로 변환
# Car.v → Car_v
# Vhcl.tRoad → Vhcl_tRoad

# 지원 연산자: >, <, >=, <=, ==, and, or
# 지원 함수: abs(), min(), max()

# 예제
"Car_v > 27.78"                              # 속도 100km/h 초과
"Car_v >= 27.78 and abs(Vhcl_tRoad) > 1.0"  # 속도 100km/h 이상 AND 횡방향 1m 초과
"DM_Gas > 0.5 or DM_Brake > 0.3"            # 가스 50% 초과 OR 브레이크 30% 초과
```

#### 조건 평가 구현

```python
def evaluate_condition(condition, data):
    """
    조건식 평가

    Args:
        condition: 조건식 (예: "Car_v > 27.78")
        data: 데이터 딕셔너리 (예: {'Car.v': 28.0, ...})

    Returns:
        bool: 조건 만족 여부
    """
    # 1. 변수명 변환: Car.v → Car_v
    eval_data = {}
    for key, value in data.items():
        clean_key = key.replace('.', '_')
        eval_data[clean_key] = value if value is not None else 0.0

    # 2. 안전한 eval (제한된 내장 함수)
    try:
        result = eval(
            condition,
            {"__builtins__": {}},  # 내장 함수 제거
            {**eval_data, 'abs': abs, 'min': min, 'max': max}
        )
        return bool(result)
    except Exception as e:
        print(f"Condition error: {condition} | {e}")
        return False

# 사용 예
data = {'Car.v': 30.0, 'Vhcl.tRoad': 1.5}
if evaluate_condition("Car_v > 27.78 and abs(Vhcl_tRoad) > 1.0", data):
    print("Condition met!")
```

### 3.4 Auto Control Rule 시스템

#### 규칙 추가

```python
from carmaker_control_server import CarMakerControlServer

server = CarMakerControlServer()
server.connect_carmaker()
server.start_monitoring()

# 규칙 추가: 속도 100km/h 초과 시 브레이크
server.add_auto_control_rule(
    condition="Car_v > 27.78",
    command="DVAWrite DM.Brake 0.5 2000 Abs",
    one_shot=True  # 한 번만 실행
)

# 규칙 추가: 횡방향 위치 1m 초과 시 조향
server.add_auto_control_rule(
    condition="abs(Vhcl_tRoad) > 1.0",
    command="DVAWrite DM.Steer.Ang -0.1 1000 Abs",
    one_shot=False  # 조건 만족시마다 실행
)
```

#### 규칙 관리

```python
# 모든 규칙 제거
server.clear_auto_control_rules()

# 현재 규칙 확인
print(f"Active rules: {len(server.auto_control_rules)}")
```

### 3.5 시뮬레이션 일시정지/재개

#### 수동 제어

```python
# 일시정지 (시간 가속도 0.001로 설정, 30초간)
client.execute_command("DVAWrite SC.TAccel 0.001 30000 Abs")

# 제어명령 실행
client.execute_command("DVAWrite DM.Gas 0.5 2000 Abs")

# 재개 (시간 가속도 1.0으로 복원)
client.execute_command("DVAWrite SC.TAccel 1.0 -1 Abs")
```

#### LLM 통합 (자동 일시정지/재개)

```python
from llm_integration import LLMIntegrationLayer

# LLM 레이어 초기화
llm_layer = LLMIntegrationLayer(server, manual_mode=False)

# 트리거 로드
llm_layer.load_triggers('llm_triggers.json')

# 모니터링 시작 (트리거 감지 시 자동으로 일시정지)
llm_layer.start_monitoring()

# 트리거 예제 (llm_triggers.json)
"""
{
  "triggers": [
    {
      "name": "high_speed_lateral_deviation",
      "condition": "Car_v > 27.78 and abs(Vhcl_tRoad) > 1.0",
      "description": "High speed with large lateral deviation"
    }
  ]
}
"""
```

### 3.6 Failsafe 제어 함수

LLM 스크립트에서 사용 가능한 안전한 제어 함수:

```python
# 1. maintain_and_wait_until: 명령을 유지하며 조건 대기
maintain_and_wait_until(
    'DVAWrite DM.v.Trgt 19.44 200 Abs',  # 명령 (0.2초마다 재전송)
    'Car_v >= 19.44',                     # 종료 조건
    30000                                 # 최대 대기 시간 (ms)
)

# 2. maintain_for: 명령을 특정 시간동안 유지
maintain_for(
    'DVAWrite DM.v.Trgt 13.89 200 Abs',  # 명령
    3000                                  # 유지 시간 (ms)
)

# 3. wait_until: 조건 대기 (제어 없음)
wait_until('Car_v <= 13.89', 10000)

# 4. execute_cmd: 단일 명령 실행
execute_cmd('DVAWrite DM.Brake 0.3 2000 Abs')

# 5. wait: 시간 대기
wait(2.0)  # 2초 대기
```

### 3.7 안전 보장 메커니즘

```python
# llm_integration.py의 _pause_simulation_and_execute()

def execute_intervention(script):
    """트리거 발생 시 자동으로 일시정지/재개"""
    try:
        # 1. 시뮬레이션 일시정지
        client.execute_command("DVAWrite SC.TAccel 0.001 30000 Abs")

        # 2. 스크립트 실행 (타임아웃 30초)
        executor.execute_script(script)

    finally:
        # 3. 항상 재개 (에러 발생해도 실행)
        client.execute_command("DVAWrite SC.TAccel 1.0 -1 Abs")
```

**안전 장치**:
1. **Finally 블록**: 스크립트 실패해도 시뮬레이션 재개
2. **타임아웃**: 무한 루프 방지 (30초)
3. **Heartbeat 패턴**: maintain_* 함수는 0.2초마다 재전송, 스크립트 종료 시 자동 중단
4. **Restricted 실행**: `__builtins__` 제거로 import/open/eval 차단

### 3.8 CLI에서 조건부 실행

```bash
# wait_until: 조건 만족 시 명령 실행
python cm_cli.py wait_until "Car_v >= 27.78" "DVAWrite DM.Brake 0.3 2000 Abs" 30

# 동작:
# 1. 매 0.1초마다 Car_v 체크
# 2. Car_v >= 27.78 만족하면 브레이크 명령 실행
# 3. 최대 30초 대기
```

### 3.9 실제 이식 시 체크리스트

- [ ] 조건식 검증 (문법 오류 사전 체크)
- [ ] 타임아웃 설정 (무한 대기 방지)
- [ ] 재개 실패 시 대비책 (수동 재개 버튼)
- [ ] 로깅 (조건 만족 이력, 실행 명령 기록)
- [ ] 트리거 우선순위 (여러 조건 동시 만족 시)
- [ ] 사용자 알림 (일시정지/재개 시 UI 표시)
- [ ] 긴급 정지 버튼 (강제 중단)

---

## 4. 성능 최적화 가이드

### 4.1 현재 성능 수치

| 항목 | 기존 | 최적화 후 | 개선율 |
|------|------|-----------|--------|
| 읽는 변수 수 | 334개 | 56개 | 83% ↓ |
| 읽기 시간 | 7초 | 1초 | 86% ↓ |
| Traffic 정보 | 전체 32대 | 앞/뒤 2대 | - |

### 4.2 최적화 기법

**1. 스마트 필터링**
```python
# 모든 차량의 sRoad만 읽기 (경량)
# → ego 기준 앞/뒤 차량 찾기
# → 해당 2대만 상세 정보 읽기
```

**2. 캐싱**
```python
# Traffic.nObjs는 첫 번째만 읽고 재사용
# 재연결 시 자동 리셋
```

**3. 필요한 정보만 수집**
```python
# traffic_obj_quantities에서 불필요한 항목 제거
# 예: State, tz, v_0.z 제외
```

### 4.3 추가 최적화 방안

**더 줄이고 싶다면**:
```python
# 1. 앞 차량만 (뒤 차량 제외)
#    → 56개 → 약 46개 변수

# 2. 트래픽 정보 최소화
self.traffic_obj_quantities = [
    'tx', 'ty',      # 위치만
    'LongVel',       # 속도만
]
#    → 56개 → 약 49개 변수

# 3. ego 정보 줄이기
#    → 필수 항목만 (Time, Car.v, Vhcl.sRoad 등)
```

---

## 5. 에러 처리 가이드

### 5.1 연결 에러

```python
def robust_connect(client, max_retries=3):
    """재시도 로직이 있는 연결"""
    for i in range(max_retries):
        success, msg = client.connect()
        if success:
            return True, msg

        print(f"Connection attempt {i+1}/{max_retries} failed: {msg}")
        time.sleep(1)

    return False, "Max retries exceeded"
```

### 5.2 명령 실행 에러

```python
def safe_execute(client, command):
    """에러 처리가 있는 명령 실행"""
    if not client.connected:
        return False, "Not connected"

    success, response = client.execute_command(command)

    if not success:
        # 에러 로깅
        print(f"Command failed: {command} → {response}")

        # 특정 에러 처리
        if "timeout" in response.lower():
            # 재시도
            success, response = client.execute_command(command)

    return success, response
```

### 5.3 데이터 에러

```python
def safe_get_data(data, key, default=0.0):
    """안전한 데이터 추출"""
    value = data.get(key, default)

    if value is None:
        return default

    return value

# 사용 예
speed = safe_get_data(data, 'Car.v', 0.0)
```

---

## 6. 배포 체크리스트

### 6.1 환경 설정

- [ ] Python 3.8 이상 설치
- [ ] 필요한 패키지 설치: `tkinter` (GUI 사용 시)
- [ ] CarMaker APO 활성화 확인
- [ ] 네트워크 방화벽 설정 (원격 연결 시)

### 6.2 코드 통합

- [ ] `carmaker_client.py` 복사
- [ ] `carmaker_control_server.py` 복사 (서버 기능 필요 시)
- [ ] 필요한 UAQ 문서 복사 (`docs/UAQ_*.md`)
- [ ] 로깅 시스템 통합
- [ ] 에러 처리 강화

### 6.3 테스트

- [ ] 연결 테스트 (connect/disconnect)
- [ ] 정보 취득 테스트 (read_essential_quantities)
- [ ] 제어 명령 테스트 (DVAWrite)
- [ ] 조건부 실행 테스트 (auto control rules)
- [ ] 성능 테스트 (읽기 시간 측정)
- [ ] 에러 처리 테스트 (연결 끊김, 타임아웃 등)

### 6.4 문서화

- [ ] API 문서 작성
- [ ] 사용자 매뉴얼 작성
- [ ] 트러블슈팅 가이드 작성
- [ ] 예제 코드 작성

---

## 7. 추가 리소스

### 7.1 참고 파일

- `carmaker_client.py`: 핵심 클라이언트 구현
- `carmaker_control_server.py`: 서버 및 auto control 구현
- `llm_integration.py`: LLM 통합 및 스크립트 실행
- `docs/UAQ_Complete_Reference.md`: 전체 UAQ 변수 목록
- `solution_proposal.md`: 데이터 동기화 문제 분석

### 7.2 예제

- `carmaker_gui.py`: GUI 통합 예제
- `cm_cli.py`: CLI 통합 예제
- `test_llm_integration.py`: LLM 통합 테스트
- `example_commands.txt`: 명령 예제

### 7.3 CarMaker APO 문서

- CarMaker Reference Manual Chapter 26: User Accessible Quantities
- CarMaker APO (Application Programming Option) Guide

---

## 8. 자주 묻는 질문 (FAQ)

### Q1. 읽기 속도를 더 빠르게 할 수 있나요?

**A**: 현재 1초는 거의 최적입니다. CarMaker의 시뮬레이션 샘플타임(0.01초)으로 인해 각 DVARead가 최소 0.01초씩 소요됩니다. 더 빠르게 하려면:
- 변수 개수를 더 줄이기 (예: 앞 차량만)
- 읽는 정보를 최소화 (위치, 속도만)

### Q2. 배치 읽기(Eval)는 왜 지원하지 않나요?

**A**: CarMaker APO에서 `Eval` 명령이 지원되지 않습니다. IPG의 권장사항도 "read one quantity at a time"입니다.

### Q3. 파이프라이닝은 가능한가요?

**A**: 이론적으로 가능하지만, solution_proposal.md에서 경고한 "Pipeline Desynchronization" 위험이 있습니다. 안정성을 위해 sequential 방식을 권장합니다.

### Q4. Traffic.nObjs가 변경되면 어떻게 하나요?

**A**: 재연결하거나 `client.cached_nObjs = None`으로 캐시를 리셋하면 다시 읽습니다.

### Q5. 조건식에서 사용 가능한 함수는?

**A**: 기본적으로 `abs()`, `min()`, `max()`만 허용합니다. 보안상 제한적으로 운영합니다.

---

## 9. 마무리

본 가이드는 CarMaker Python 제어 시스템을 실제 프로그램에 이식하기 위한 핵심 내용을 담고 있습니다.

**핵심 요약**:
1. **정보 취득/제어**: `carmaker_client.py` 사용, 최적화된 방식으로 1초 내 56개 변수 수집
2. **텍스트 기반 제어**: DVAWrite 명령으로 간단하고 유연한 제어
3. **조건부 정지/재개**: Auto control rules + LLM 통합으로 자동화

**성공적인 이식을 위한 조언**:
- 단계적으로 통합 (먼저 기본 연결, 그 다음 제어, 마지막 자동화)
- 충분한 테스트 (특히 에러 상황)
- 로깅 및 모니터링 강화
- 문서화 철저히

추가 질문이나 이슈는 코드 주석 및 CLAUDE.md를 참고하세요.
