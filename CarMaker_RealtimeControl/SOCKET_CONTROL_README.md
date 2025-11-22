# CarMaker Socket-based Control System

## 개요

GUI를 서버로 실행하고, CLI로 명령을 전송하는 시스템입니다.

**구조:**
```
  LLM/사용자
      ↓
    CLI (명령 전송)
      ↓
  Python GUI (소켓 서버 + 조건 처리)
      ↓
   CarMaker
```

## 사용 방법

### 1단계: GUI 서버 실행 (계속 실행)

```bash
python simple_carmaker_test_gui.py
```

- GUI가 실행되면서 자동으로 소켓 서버 시작 (localhost:7777)
- CarMaker와 연결
- 모니터링 시작

### 2단계: CLI로 명령 전송

**기본 명령 실행:**
```bash
# 상태 조회
python cm_cli.py status

# CarMaker 명령 실행
python cm_cli.py cmd "DVAWrite DM.Gas 0.5 2000 Abs"
python cm_cli.py cmd "StartSim"
python cm_cli.py cmd "StopSim"
```

**조건부 명령 실행:**
```bash
# 속도가 20 m/s 이상이면 브레이크
python cm_cli.py conditional "Car.v > 20" "DVAWrite DM.Brake 0.3 2000 Abs"

# 속도가 0.001 m/s 이하면 로그
python cm_cli.py conditional "Car.v <= 0.001" "DVARead Time"

# 가속 중 특정 조건
python cm_cli.py conditional "DM.Gas >= 0.5" "DVAWrite DM.v.Trgt 30.0 -1 Abs"
```

## 작동 모드

CLI는 자동으로 GUI 서버를 감지합니다:

- **GUI Server 모드** (기본): GUI가 실행 중이면 자동으로 소켓 통신
- **Direct 모드**: GUI 없이 CarMaker 직접 연결

강제 모드 지정:
```bash
# GUI 서버 강제 사용
python cm_cli.py --gui cmd "DVAWrite DM.Gas 0.5"

# 직접 연결 강제
python cm_cli.py --direct cmd "DVAWrite DM.Gas 0.5"
```

## 지원 기능

### 1. 단순 명령 (cmd)
- CarMaker의 모든 DVA 명령 실행
- StartSim, StopSim 등 시뮬레이션 제어

### 2. 상태 조회 (status)
- 차량의 모든 주요 데이터 조회
- JSON 형식으로 반환

### 3. 조건부 실행 (conditional)
- 실시간 데이터 기반 조건 체크
- 조건이 맞으면 명령 실행

**지원 연산자:**
- `>`, `<`, `>=`, `<=`, `==`

**조건 형식:**
```
"변수명 연산자 값"
예: "Car.v > 20"
```

## 응답 형식

모든 응답은 JSON 형식:

```json
{
  "success": true,
  "result": "OK",
  "command": "DVAWrite DM.Gas 0.5 2000 Abs",
  "_mode": "GUI Server"
}
```

조건부 명령:
```json
{
  "success": true,
  "result": "Condition met (25.3 > 20). Executed: OK",
  "_mode": "GUI Server",
  "condition": "Car.v > 20"
}
```

## 예제 시나리오

### 시나리오 1: 가속 후 조건부 브레이크
```bash
# 터미널 1: GUI 실행
python simple_carmaker_test_gui.py

# 터미널 2: 시뮬레이션 시작 & 가속
python cm_cli.py cmd "StartSim"
python cm_cli.py cmd "DVAWrite DM.Gas 0.8 5000 Abs"

# 속도가 30 m/s 이상이면 브레이크
python cm_cli.py conditional "Car.v >= 30" "DVAWrite DM.Brake 0.5 3000 Abs"
```

### 시나리오 2: 반복 모니터링
```bash
# 터미널에서 반복 실행 (Linux/Mac)
while true; do
  python cm_cli.py status | jq '.Car.v, .speed_kmh'
  sleep 1
done

# Windows (PowerShell)
while ($true) {
  python cm_cli.py status
  Start-Sleep -Seconds 1
}
```

## 장점

1. **GUI 한 번만 실행**: CarMaker 연결 유지
2. **CLI로 자유로운 제어**: 스크립트, LLM 등에서 쉽게 호출
3. **조건부 로직**: GUI에서 실시간 모니터링하며 조건 처리
4. **유연성**: Direct 모드와 Server 모드 전환 가능

## 제한사항 (현재 프로토타입)

- 조건 형식이 단순함 (복잡한 AND/OR 미지원)
- while/for 반복문 미지원
- 에러 핸들링 기본적 수준

## 향후 개선 가능성

1. 복잡한 조건 지원 (AND, OR, 괄호)
2. 반복 명령 (while, for)
3. 대기 명령 (wait_until)
4. 비동기 명령 큐
5. 웹소켓 지원 (실시간 스트리밍)

## 문제 해결

**"GUI server communication error"**
- GUI가 실행 중인지 확인
- 포트 7777이 사용 가능한지 확인

**"Conditional commands require GUI server"**
- conditional 명령은 GUI 서버 모드에서만 동작
- GUI를 먼저 실행하세요

**"Connection failed"**
- CarMaker가 실행 중인지 확인
- 포트 16660 확인 (CarMaker APO 포트)
