# CarMaker Control System - Architecture

## 개요

GUI, CLI, 제어 로직이 분리된 클린 아키텍처

```
┌─────────────┐         ┌─────────────┐
│   CLI       │         │   GUI       │
│  (Client)   │         │  (Client)   │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │   Socket (7777)       │
       └───────┬───────────────┘
               │
       ┌───────▼────────┐
       │ Control Server │
       │  (Headless)    │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │   CarMaker     │
       │  (Port 16660)  │
       └────────────────┘
```

## 구성 요소

### 1. Control Server (`carmaker_control_server.py`)

**핵심 제어 서버 - 헤드리스 실행 가능**

- CarMaker 연결 관리 (포트 16660)
- 소켓 서버 (포트 7777)
- 모니터링 루프 (10Hz)
- 조건부 제어 및 자동 규칙 처리
- 모든 제어 로직

**특징:**
- GUI 없이 독립 실행 가능
- 여러 클라이언트 동시 접속 지원
- 콜백 기반 확장 가능

### 2. GUI Client (`carmaker_gui.py`)

**순수 Tkinter GUI**

- 제어 서버와 소켓 통신
- 상태 표시 및 모니터링
- 직관적인 제어 인터페이스

**특징:**
- CarMaker 직접 연결 없음
- 제어 서버에만 의존
- 선택적 실행

### 3. CLI Client (`cm_cli.py`)

**명령줄 인터페이스**

- 제어 서버와 소켓 통신
- 스크립트/LLM 통합 용이
- JSON 응답

**특징:**
- 자동화 친화적
- Direct 모드도 지원 (서버 없이)

## 사용 방법

### 방법 1: 서버 + GUI

```bash
# 터미널 1: 제어 서버 실행
python carmaker_control_server.py

# 터미널 2: GUI 실행
python carmaker_gui.py
```

### 방법 2: 서버 + CLI

```bash
# 터미널 1: 제어 서버 실행
python carmaker_control_server.py

# 터미널 2: CLI 명령
python cm_cli.py status
python cm_cli.py cmd "DVAWrite DM.Gas 0.5 2000 Abs"
python cm_cli.py auto "Car.v >= 27.78" "DVAWrite DM.Gas 0.0 500 Abs"
```

### 방법 3: 서버 + GUI + CLI

```bash
# 터미널 1: 제어 서버
python carmaker_control_server.py

# 터미널 2: GUI (모니터링용)
python carmaker_gui.py

# 터미널 3: CLI (자동화 스크립트)
python cm_cli.py auto "Car.v >= 100" "DVAWrite DM.Gas 0.0"
```

## 제어 서버 API

### Socket Protocol (JSON)

#### 연결
```json
{"action": "connect"}
```

#### 명령 실행
```json
{
  "action": "cmd",
  "command": "DVAWrite DM.Gas 0.5 2000 Abs"
}
```

#### 상태 조회
```json
{"action": "status"}
```

#### 조건부 실행
```json
{
  "action": "conditional",
  "condition": "Car.v > 20",
  "command": "DVAWrite DM.Brake 0.3 2000 Abs"
}
```

#### 자동 제어 규칙 추가
```json
{
  "action": "auto_control",
  "condition": "Car.v >= 27.78",
  "command": "DVAWrite DM.Gas 0.0 500 Abs",
  "one_shot": true
}
```

#### 조건 대기
```json
{
  "action": "wait_until",
  "condition": "Car.v >= 100",
  "command": "DVAWrite DM.Gas 0.0",
  "timeout": 30
}
```

#### 모니터링 시작/중지
```json
{"action": "start_monitoring"}
{"action": "stop_monitoring"}
```

## 장점

### 1. 관심사 분리
- GUI: 표시만
- CLI: 명령 전송만
- Server: 제어 로직만

### 2. 유연성
- 헤드리스 실행 가능
- 원격 제어 가능 (서버만 CarMaker 머신에)
- 여러 클라이언트 동시 사용

### 3. 확장성
- 새 클라이언트 추가 용이
- 웹 인터페이스 추가 가능
- 서버 로직 독립적 개선

### 4. 테스트 용이
- 각 컴포넌트 독립 테스트
- 서버 로직 단위 테스트 가능

## 예제 시나리오

### 100kph 가속 후 자동 감속

```bash
# 1. 서버 실행
python carmaker_control_server.py

# 2. GUI에서 연결 & 모니터링 시작
python carmaker_gui.py

# 3. CLI로 자동 제어 설정
python cm_cli.py auto "Car.v >= 27.78" "DVAWrite DM.Gas 0.0 500 Abs"
python cm_cli.py cmd "DVAWrite DM.Gas 0.8 -1 Abs"

# → 속도 100kph 도달 시 자동으로 가속 중지!
```

## 파일 구조

```
CarMaker_RealtimeControl/
├── carmaker_control_server.py  # 제어 서버 (핵심)
├── carmaker_gui.py              # GUI 클라이언트
├── cm_cli.py                    # CLI 클라이언트
├── carmaker_client.py           # CarMaker 통신 라이브러리
└── simple_carmaker_test_gui.py # (구버전 - 통합형)
```

## 마이그레이션

### 기존 코드에서

`simple_carmaker_test_gui.py` - GUI와 제어가 혼재

### 새 구조로

1. **제어 서버**: `carmaker_control_server.py`
2. **GUI**: `carmaker_gui.py`
3. **CLI**: `cm_cli.py` (변경 없음)

## 개발 로드맵

- [ ] 웹 인터페이스 추가
- [ ] 복잡한 조건 지원 (AND/OR)
- [ ] 시나리오 스크립트 기능
- [ ] 데이터 로깅 기능
- [ ] 리플레이 기능
