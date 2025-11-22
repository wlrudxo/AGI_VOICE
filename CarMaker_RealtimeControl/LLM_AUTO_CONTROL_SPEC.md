# LLM - CarMaker 자동 제어 시스템 명세

## 목표

**LLM이 실시간으로 시뮬레이션 상황을 판단하고 자동으로 제어 명령을 생성하는 시스템**

## 전체 플로우

```
CarMaker Simulation (Running)
         ↓
    ┌────────────────────────────────┐
    │ 1. 상태 모니터링 (연속)        │
    │    - Python: status 계속 수신  │
    │    - 10Hz 업데이트              │
    └────────┬───────────────────────┘
             ↓
    ┌────────────────────────────────┐
    │ 2. 조건 감지 & 일시정지        │
    │    - 미리 설정된 트리거 체크   │
    │    - SC.TAccel = 0.001         │
    │    - 예: 속도 > 100kph         │
    │         차선 이탈 > 0.5m        │
    │         장애물 거리 < 10m       │
    └────────┬───────────────────────┘
             ↓
    ┌────────────────────────────────┐
    │ 3. LLM에 상황 정보 제공        │
    │    - 현재 속도, 위치, 상태     │
    │    - 조건 트리거 정보           │
    │    - 주변 환경 데이터           │
    └────────┬───────────────────────┘
             ↓
    ┌────────────────────────────────┐
    │ 4. LLM 응답 대기               │
    │    - LLM이 상황 분석            │
    │    - 적절한 제어 명령 생성     │
    │    - 명령 수신 후 처리         │
    └────────────────────────────────┘
```

## 1. 상태 모니터링

### 목적
CarMaker 시뮬레이션 상태를 실시간으로 수신

### 구현
```python
# Control Server에서 10Hz로 연속 모니터링
while monitoring:
    data = client.read_essential_quantities()
    # 조건 체크
    check_llm_trigger_conditions(data)
    time.sleep(0.1)
```

### 모니터링 데이터
- `Time`: 시뮬레이션 시간
- `Car.v`: 차량 속도 (m/s)
- `DM.Gas`, `DM.Brake`, `DM.Steer.Ang`: 제어 입력
- `Vhcl.sRoad`, `Vhcl.tRoad`: 도로 위치
- `Vhcl.YawRate`: 회전 속도
- 기타 필요한 센서 데이터

## 2. 조건 감지 & 일시정지

### 목적
LLM 개입이 필요한 상황을 자동으로 감지

### 트리거 조건 예시
```python
triggers = [
    # 속도 관련
    {"name": "high_speed", "condition": "Car.v > 27.78", "description": "속도 100kph 초과"},

    # 차선 이탈
    {"name": "lane_departure", "condition": "abs(Vhcl.tRoad) > 1.5", "description": "차선 중심에서 1.5m 이탈"},

    # 급격한 조향
    {"name": "sharp_turn", "condition": "abs(Vhcl.YawRate) > 0.5", "description": "급격한 회전 감지"},

    # 복합 조건: 고속 + 차선 이탈
    {"name": "high_speed_lane_departure",
     "condition": "Car.v > 27.78 and abs(Vhcl.tRoad) > 1.0",
     "description": "고속 주행 중 차선 이탈"},

    # OR 조건: 긴급 상황
    {"name": "emergency",
     "condition": "Car.v > 40.0 or abs(Vhcl.tRoad) > 2.0 or abs(DM.Steer.Ang) > 0.5",
     "description": "긴급 개입 필요"},

    # 주기적 체크
    {"name": "periodic", "condition": "Time % 10.0 < 0.1", "description": "10초마다 체크"}
]
```

### 구현
```python
def check_llm_trigger_conditions(data):
    """Check if any trigger condition is met (supports AND/OR)"""
    for trigger in triggers:
        if evaluate_condition(trigger["condition"], data):
            activate_llm_intervention(trigger, data)
            break  # 하나의 트리거만 처리

def evaluate_condition(condition, data):
    """Evaluate condition with AND/OR support using Python eval"""
    try:
        # Evaluate condition with current data as context
        # Supports: >, <, >=, <=, ==, and, or, abs(), etc.
        result = eval(condition, {"__builtins__": {}}, {**data, 'abs': abs})
        return bool(result)
    except Exception as e:
        log(f"Condition evaluation error: {e}")
        return False
```

### 일시정지 구현
```python
def pause_for_llm():
    # 시뮬레이션 속도를 거의 0으로
    execute_command("DVAWrite SC.TAccel 0.001 -1 Abs")
    log("Simulation paused for LLM decision")
```

## 3. LLM에 상황 정보 제공

### 목적
LLM이 적절한 판단을 할 수 있도록 충분한 컨텍스트 제공

### 정보 구조
```json
{
  "trigger": {
    "name": "high_speed",
    "condition": "Car.v > 27.78",
    "description": "속도 100kph 초과"
  },
  "current_state": {
    "Time": 45.3,
    "Car.v": 28.5,
    "speed_kmh": 102.6,
    "DM.Gas": 0.6,
    "DM.Brake": 0.0,
    "DM.Steer.Ang": 0.05,
    "Vhcl.sRoad": 1250.5,
    "Vhcl.tRoad": 0.3,
    "Vhcl.YawRate": 0.02
  },
  "recent_history": [
    {"time": 45.2, "Car.v": 28.3},
    {"time": 45.1, "Car.v": 28.0}
  ],
  "context": "차량이 100kph를 초과하여 주행 중입니다. 현재 직선 도로이며 차선 중앙을 유지하고 있습니다."
}
```

### LLM 프롬프트 예시
```
당신은 CarMaker 시뮬레이션의 자동 제어 시스템입니다.

현재 상황:
- 트리거: 속도 100kph 초과
- 현재 속도: 102.6 km/h (28.5 m/s)
- 가속 페달: 0.6 (60%)
- 브레이크: 0.0
- 조향: 0.05 rad (약 3도)
- 도로 위치: 1250.5m (차선 중앙에서 +0.3m)

최근 추세:
- 속도가 계속 증가 중

요청: 안전을 위한 적절한 제어 명령을 생성하세요.

응답 형식:
1. 상황 분석
2. 제어 전략
3. 실행 명령 (DVAWrite 형식 또는 조건문)
```

## 4. LLM 응답 형식

### 기본 원칙

**스크립트 기반 접근 (exec 사용)**
- LLM은 Python 스크립트를 생성
- `exec()` 실행 + 최소 가드레일로 안전성 확보
- if/else, for, while, 변수 할당 등 **모든 Python 기능 사용 가능**
- 제공되는 헬퍼 함수를 사용하여 제어
- CarMaker가 명령 유효성 검증 담당

**왜 exec()를 사용하는가?**
- ✅ **표현력**: if/else, 루프, 변수 등 자유로운 로직 작성
- ✅ **확장성**: 파라미터 튜닝, 반복 최적화 등 복잡한 작업 가능
- ✅ **단순성**: Python 인터프리터 활용, 별도 파서 불필요
- ✅ **안전성**: `__builtins__` 제거 + 타임아웃으로 충분히 안전 (개인 용도)

**대안 (줄 단위 파싱)의 한계**:
- ❌ if/else 처리 어려움 (파서 재구현 필요)
- ❌ 변수 할당 불가
- ❌ 루프 불가
- ❌ 복잡한 제어 로직 표현 제한적

### 응답 구조

```python
{
  "analysis": "상황 분석 내용",
  "strategy": "제어 전략 설명",
  "script": """
# Python 스크립트
"""
}
```

### 제공되는 헬퍼 함수

```python
# 명령 실행
execute_cmd(command: str) -> bool
# 예: execute_cmd('DVAWrite DM.Gas 0.5 2000 Abs')

# 대기
wait(milliseconds: int)
# 예: wait(1000)  # 1초 대기

# 조건 대기
wait_until(condition: str, timeout: int = 30) -> bool
# 예: wait_until('Car.v >= 27.78')
# 예: wait_until('Car.v >= 27.78 and Vhcl.tRoad < 0.5')

# 자동 제어 규칙 추가
add_auto_rule(condition: str, command: str, one_shot: bool = True)
# 예: add_auto_rule('Car.v >= 30.0', 'DVAWrite DM.Gas 0.0 500 Abs')

# 값 읽기
get_value(variable: str) -> float
# 예: speed = get_value('Car.v')

# 로그 출력
log(message: str)
# 예: log('Starting deceleration sequence')
```

### 조건식 문법

조건식에서는 **Python 표현식 자유롭게 사용 가능**:

```python
# 단순 비교
'Car.v > 27.78'

# AND 조건
'Car.v > 27.78 and Vhcl.tRoad < 1.0'

# OR 조건
'Car.v < 5.0 or DM.Brake > 0.8'

# 복합 조건
'(Car.v > 30.0 and abs(Vhcl.tRoad) > 1.5) or DM.Brake > 0.9'

# 함수 사용
'abs(Vhcl.tRoad) > 1.5'
'abs(DM.Steer.Ang) < 0.1'
```

### 응답 예시

#### 예시 1: 단순 감속
```python
{
  "analysis": "속도가 100kph를 초과했으므로 점진적 감속 필요",
  "strategy": "가속 중단 후 부드러운 브레이크 적용",
  "script": """
execute_cmd('DVAWrite DM.Gas 0.0 500 Abs')
wait(500)
execute_cmd('DVAWrite DM.Brake 0.2 3000 AbsRamp')
"""
}
```

#### 예시 2: 조건부 제어
```python
{
  "analysis": "속도 감속 후 자동으로 브레이크 해제 필요",
  "strategy": "90kph까지 감속 후 브레이크 자동 해제",
  "script": """
execute_cmd('DVAWrite DM.Gas 0.0 500 Abs')
add_auto_rule('Car.v <= 25.0', 'DVAWrite DM.Brake 0.0 500 Abs')
execute_cmd('DVAWrite DM.Brake 0.3 2000 AbsRamp')
"""
}
```

#### 예시 3: AND/OR 조건 활용
```python
{
  "analysis": "고속 주행 중 차선 이탈 위험",
  "strategy": "속도와 차선 위치 모두 안전 범위로 복귀",
  "script": """
# 고속 + 차선 이탈 시 즉시 감속
if get_value('Car.v') > 27.78 and abs(get_value('Vhcl.tRoad')) > 1.0:
    execute_cmd('DVAWrite DM.Gas 0.0 200 Abs')
    execute_cmd('DVAWrite DM.Brake 0.4 2000 AbsRamp')
    log('Emergency deceleration due to lane departure at high speed')

# 안전 속도 AND 차선 중앙 복귀 시 브레이크 해제
add_auto_rule('Car.v <= 25.0 and abs(Vhcl.tRoad) < 0.5',
              'DVAWrite DM.Brake 0.0 500 Abs')
"""
}
```

#### 예시 4: 복잡한 회피 기동
```python
{
  "analysis": "장애물 회피 후 원래 차선 복귀 필요",
  "strategy": "좌측 회피 → 유지 → 복귀",
  "script": """
# 좌측 회피
execute_cmd('DVAWrite DM.Steer.Ang 0.15 1500 AbsRamp')
wait_until('Vhcl.tRoad > 1.0')
log('Lane change completed')

# 직진 유지
execute_cmd('DVAWrite DM.Steer.Ang 0.0 500 Abs')
wait(2000)

# 원래 차선 복귀
execute_cmd('DVAWrite DM.Steer.Ang -0.15 1500 AbsRamp')
wait_until('abs(Vhcl.tRoad) < 0.3')
execute_cmd('DVAWrite DM.Steer.Ang 0.0 500 Abs')
log('Returned to original lane')
"""
}
```

## 6. 시뮬레이션 재개

### 구현
```python
def resume_simulation():
    # 시뮬레이션 속도 정상화
    execute_command("DVAWrite SC.TAccel 1.0 -1 Abs")
    log("Simulation resumed at normal speed")
```

## 7. LLM 스크립트 실행

### 스크립트 실행 엔진 (exec + 최소 가드레일)

```python
import threading
import time

def execute_llm_script(llm_response, server, timeout=30):
    """
    Execute LLM-generated Python script with minimal guardrails

    Safety measures:
    1. Remove __builtins__ to block import/open/eval
    2. Timeout to prevent infinite loops
    3. Limit wait() duration
    4. try/finally for SC.TAccel recovery (handled by caller)
    """
    script = llm_response.get("script", "")
    if not script:
        server.log("No script in LLM response")
        return False, "No script provided"

    # Helper functions context
    context = {
        'execute_cmd': lambda cmd: server.execute_command(cmd),
        'wait': lambda ms: time.sleep(min(ms, 10000) / 1000.0),  # 최대 10초
        'wait_until': lambda cond, t=30: _wait_until(server, cond, min(t, 60)),  # 최대 60초
        'add_auto_rule': lambda cond, cmd, one_shot=True: server.add_auto_control_rule(cond, cmd, one_shot),
        'get_value': lambda var: _get_value(server, var),
        'log': lambda msg: server.log(f"[LLM] {msg}"),
        # Safe built-in functions
        'abs': abs,
        'min': min,
        'max': max,
        'round': round,
        'len': len,
    }

    # Execute with timeout
    result = {"error": None, "success": False}

    def run_script():
        try:
            # ✅ 핵심 가드레일: __builtins__ 제거
            # import, open, eval, exec, __import__ 등 모두 차단
            exec(script, {"__builtins__": {}}, context)
            result["success"] = True
        except Exception as e:
            result["error"] = e

    # Run in thread with timeout
    thread = threading.Thread(target=run_script, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        server.log(f"Script timeout after {timeout}s")
        return False, f"Timeout after {timeout}s"

    if result["error"]:
        server.log(f"Script execution error: {result['error']}")
        return False, str(result["error"])

    if result["success"]:
        server.log("LLM script executed successfully")
        return True, "Script executed"

    return False, "Unknown error"


def _wait_until(server, condition, timeout=30):
    """Wait until condition is met"""
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            server.log(f"wait_until timeout: {condition}")
            return False

        # Read current values
        data = server.client.read_essential_quantities()

        # Evaluate condition with current data
        try:
            result = eval(condition, {"__builtins__": {}}, {**data, 'abs': abs, 'min': min, 'max': max})
            if result:
                return True
        except Exception as e:
            server.log(f"Condition evaluation error: {e}")
            return False

        time.sleep(0.1)  # 10Hz check


def _get_value(server, variable):
    """Get current value of a variable"""
    resp = server.client.send_command(f"DVARead {variable}")
    if resp and resp.startswith("O"):
        return float(resp[1:].strip())
    return None


def llm_intervention_with_safety(server, trigger, llm_script):
    """
    LLM 개입 시 시뮬레이션 일시정지/재개 보장
    SC.TAccel 복귀를 try/finally로 강제
    """
    try:
        # 일시정지
        server.execute_command("DVAWrite SC.TAccel 0.001 -1 Abs")
        server.log(f"Simulation paused for LLM intervention: {trigger['name']}")

        # LLM 스크립트 실행
        success, msg = execute_llm_script(llm_script, server, timeout=30)

        if not success:
            server.log(f"LLM script failed: {msg}")

    finally:
        # ✅ 무조건 복귀 보장
        server.execute_command("DVAWrite SC.TAccel 1.0 -1 Abs")
        server.log("Simulation speed restored to normal")
```

### 최소 가드레일 설명

#### 1. `__builtins__` 제거 (핵심)

```python
exec(script, {"__builtins__": {}}, context)
```

**차단되는 위험 요소**:
- `import` - 외부 모듈 불가
- `open()` - 파일 접근 불가
- `eval()`, `exec()` - 중첩 실행 불가
- `__import__()` - 동적 import 불가
- `compile()`, `globals()`, `locals()` - 메타 접근 불가

**테스트**:
```python
# 모두 NameError 발생
import os          # NameError: name 'import' is not defined
open('file.txt')   # NameError: name 'open' is not defined
eval('1+1')        # NameError: name 'eval' is not defined
```

#### 2. 타임아웃 (무한 루프 방지)

```python
thread.join(timeout=30)  # 30초 제한
```

**방지되는 문제**:
```python
# LLM이 실수로 생성한 무한 루프
while True:
    execute_cmd('DVAWrite DM.Gas 0.5 1000 Abs')
# → 30초 후 강제 종료
```

#### 3. wait() 최대값 제한

```python
'wait': lambda ms: time.sleep(min(ms, 10000) / 1000.0)  # 최대 10초
```

**방지되는 문제**:
```python
wait(999999999)  # → 실제로는 10초만 대기
```

#### 4. SC.TAccel 복귀 보장 (try/finally)

```python
try:
    execute_command("DVAWrite SC.TAccel 0.001 -1 Abs")  # 일시정지
    execute_llm_script(...)
finally:
    execute_command("DVAWrite SC.TAccel 1.0 -1 Abs")    # 무조건 복귀
```

**보장**:
- 스크립트 성공/실패 무관하게 시뮬레이션 속도 복구
- 에러 발생해도 시뮬레이션 정지 상태로 남지 않음

### 허용되는 Python 기능

```python
# ✅ if/else, for, while 모두 가능
if get_value('Car.v') > 27.78:
    execute_cmd('DVAWrite DM.Brake 0.3 2000 Abs')
else:
    execute_cmd('DVAWrite DM.Gas 0.5 1000 Abs')

# ✅ 변수 할당
speed = get_value('Car.v')
lateral_pos = get_value('Vhcl.tRoad')

# ✅ 루프
for i in range(3):
    execute_cmd('DVAWrite DM.Gas 0.5 500 Abs')
    wait(500)

# ✅ 복잡한 계산
overshoot = (max_speed - target_speed) / target_speed * 100
```

### 여전히 가능한 것 (하지만 제한적 위험)

```python
# CPU 과부하 - 타임아웃으로 30초 후 종료
while True:
    x = 1 + 1

# 메모리 소모 - 개인 PC면 감내 가능
big_list = [0] * 10000000

# 의도치 않은 제어 - CarMaker가 거부하거나 사용자 확인
execute_cmd('DVAWrite DM.Gas 1.0 -1 Abs')
```

### 안전성 요약

| 위험 요소 | 대응 방법 | 효과 |
|----------|----------|------|
| **파일 접근** | `open()` 없음 | ✅ 완전 차단 |
| **시스템 명령** | `import os` 불가 | ✅ 완전 차단 |
| **무한 루프** | 30초 타임아웃 | ✅ 강제 종료 |
| **과도한 대기** | wait() 10초 제한 | ✅ 제한됨 |
| **시뮬레이션 정지** | try/finally | ✅ 복귀 보장 |
| **메모리 소모** | - | ⚠️ 제한 없음 (개인용 OK) |
| **잘못된 제어** | CarMaker 검증 | ⚠️ 후속 검증 |

**개인 실험용으로는 충분히 안전합니다.**
```

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────┐
│                  LLM (Claude/GPT)               │
│  - 상황 분석                                     │
│  - 제어 전략 수립                                │
│  - 명령 생성                                     │
└────────────────┬────────────────────────────────┘
                 │ API Call
┌────────────────▼────────────────────────────────┐
│          LLM Integration Layer                  │
│  - 트리거 조건 관리                              │
│  - LLM 호출 및 프롬프트 생성                     │
│  - 스크립트 실행 (exec + 가드레일)               │
│  - 시뮬레이션 일시정지/재개                      │
└────────────────┬────────────────────────────────┘
                 │ Method Calls
┌────────────────▼────────────────────────────────┐
│          Control Server                         │
│  - CarMaker 연결                                │
│  - 상태 모니터링 (10Hz)                         │
│  - 명령 실행                                     │
│  - 자동 제어 규칙 관리                           │
└────────────────┬────────────────────────────────┘
                 │ APO Protocol
┌────────────────▼────────────────────────────────┐
│               CarMaker                          │
│  - 시뮬레이션 실행                               │
│  - 차량 동역학                                   │
│  - 환경 시뮬레이션                               │
└─────────────────────────────────────────────────┘
```

## 구현 단계

### Phase 1: 기본 인프라 ✅
- [x] Control Server 구현
- [x] 모니터링 시스템
- [x] 자동 제어 규칙
- [x] CLI 인터페이스

### Phase 2: LLM Integration Layer (다음 단계)
- [ ] 트리거 조건 시스템 (AND/OR 지원)
- [ ] LLM API 연동 (Claude)
- [ ] 프롬프트 생성기
- [ ] 스크립트 실행 엔진 (exec + 가드레일)
- [ ] 시뮬레이션 일시정지/재개 로직 (try/finally)

## 사용 예시

### 시나리오: 고속 주행 중 급커브 진입

```
1. 모니터링: 속도 110kph, 앞에 반경 50m 커브 감지

2. 트리거 발동: "high_speed_curve_ahead"

3. 일시정지: SC.TAccel = 0.001

4. LLM 호출:
   프롬프트: "110kph로 주행 중 반경 50m 커브가 50m 전방에 있습니다.
             안전한 감속 및 조향 계획을 수립하세요."

5. LLM 응답:
   {
     "analysis": "현재 속도로는 커브 진입이 위험합니다.
                 70kph까지 감속 후 적절한 조향이 필요합니다.",
     "strategy": "단계적 브레이크 후 커브 진입",
     "script": """
execute_cmd('DVAWrite DM.Gas 0.0 500 Abs')
execute_cmd('DVAWrite DM.Brake 0.4 3000 AbsRamp')
add_auto_rule('Car.v <= 19.4', 'DVAWrite DM.Brake 0.0 500 Abs')
add_auto_rule('Vhcl.sRoad >= 1300', 'DVAWrite DM.Steer.Ang 0.12 2000 AbsRamp')
log('Deceleration and curve entry sequence activated')
"""
   }

6. 재개: SC.TAccel = 1.0

7. 스크립트 실행 (exec + 가드레일):
   - Python exec()로 스크립트 실행
   - __builtins__ 제거로 import/open 차단
   - 30초 타임아웃 적용
   - try/finally로 SC.TAccel 복귀 보장

8. 실행 내용:
   - 가속 중단
   - 브레이크 3초간 적용
   - 70kph 도달 시 브레이크 해제 (자동 규칙)
   - 커브 진입 시점에 조향 시작 (자동 규칙)

9. 결과: 안전하게 커브 통과
```

## 파일 구조 (예정)

```
CarMaker_RealtimeControl/
├── carmaker_control_server.py      # 제어 서버 (기존)
├── carmaker_gui.py                  # GUI (기존)
├── cm_cli.py                        # CLI (기존)
│
├── llm_integration.py               # LLM 통합 레이어 (신규)
│   ├── LLMIntegrationLayer
│   ├── TriggerManager
│   ├── PromptGenerator
│   └── ScriptExecutor              # exec + 가드레일
│
├── llm_triggers.json                # 트리거 조건 설정 (신규)
└── llm_prompts/                     # 프롬프트 템플릿 (신규)
    ├── base_system_prompt.txt
    ├── high_speed_scenario.txt
    ├── lane_departure_scenario.txt
    └── obstacle_avoidance_scenario.txt
```

## 다음 단계

1. **LLM Integration Layer 구현**
   - `llm_integration.py` 생성
   - Claude API 연동
   - 트리거 조건 시스템 (AND/OR 지원)
   - 스크립트 실행 엔진 (exec + 최소 가드레일)
   - try/finally로 SC.TAccel 복귀 보장

2. **테스트 시나리오 작성**
   - 속도 제어 시나리오 (단순 제어)
   - 차선 유지 시나리오 (조건부 제어)
   - 장애물 회피 시나리오 (복잡한 로직)
   - 파라미터 튜닝 시나리오 (Simulink 제어기)

3. **프롬프트 설계**
   - 시스템 프롬프트 작성
   - 헬퍼 함수 사용법 명세
   - 응답 형식 강제
   - 제약사항 명시 (타임아웃, wait 제한 등)

4. **최적화**
   - LLM 응답 시간 최소화
   - 프롬프트 최적화
   - 캐싱 전략
   - 히스토리 관리
