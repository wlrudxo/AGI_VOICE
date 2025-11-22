# CarMaker Integration Plan

**Project**: AGI_VOICE_V2
**Target**: CarMaker Real-Time Control Integration
**Approach**: Rust-Only, File-Based, No Database
**Date**: 2025-11-22

---

## Overview

AGI_VOICE_V2에 CarMaker 실시간 차량 제어 기능을 통합합니다.
- **Rust 전용**: Python 브리지 없이 Rust로 직접 CarMaker APO 통신
- **파일 기반**: JSON 설정 + 로그 파일 (DB 불필요)
- **메모리 상태**: 실시간 텔레메트리는 메모리에만 유지

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Svelte 5)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │ Manual Ctrl  │  │  Triggers    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ▼ Tauri IPC
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Rust)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          CarMaker State (In-Memory)                  │   │
│  │  - Latest Telemetry                                  │   │
│  │  - Command History (VecDeque, 100 max)              │   │
│  │  - Connection Status                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          CarMaker Client (TCP Socket)                │   │
│  │  - APO Protocol Implementation                       │   │
│  │  - DVARead / DVAWrite Commands                       │   │
│  │  - Tcl Eval Batch Reads                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          LLM Monitor (Optional)                      │   │
│  │  - Trigger Evaluation (10Hz)                         │   │
│  │  - Claude CLI Integration                            │   │
│  │  - Intervention Execution                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 File System Storage                         │
│  - carmaker_config.json      (연결 설정)                    │
│  - llm_triggers.json         (트리거 설정)                  │
│  - carmaker_control.log      (명령 로그)                    │
│  - llm_interventions.log     (개입 로그, JSON Lines)        │
└─────────────────────────────────────────────────────────────┘
                            ▼
                   CarMaker APO (TCP :16660)
```

---

## Tech Stack

### Backend (Rust)
- **TCP Socket**: `tokio::net::TcpStream` (CarMaker APO 통신)
- **Async Runtime**: `tokio` (비동기 I/O)
- **Serialization**: `serde` + `serde_json` (JSON 처리)
- **State**: `Arc<RwLock<T>>` (멀티스레드 상태 공유)
- **Logging**: `tracing` 또는 `log` crate

### Frontend (Svelte)
- **Framework**: Svelte 5 (runes syntax)
- **Tauri IPC**: `invoke()` commands
- **Real-time Updates**: `setInterval()` (10Hz 폴링)

### AI Integration
- **Claude CLI**: Subprocess 실행 (기존 시스템 재사용)
- **Prompt Assembly**: 텍스트 파일 기반

---

## Data Storage

### JSON Config Files

**`carmaker_config.json`**
```json
{
  "host": "localhost",
  "port": 16660,
  "updateRate": 100,
  "reconnectDelay": 5000
}
```

**`llm_triggers.json`**
```json
{
  "triggers": [
    {
      "id": "speed_limit",
      "name": "Speed over 60 km/h",
      "condition": "Car_v > 16.67",
      "isActive": true,
      "priority": 5
    }
  ]
}
```

### Log Files

**`carmaker_control.log`** (Text)
```
2025-11-22 10:30:45 [INFO] Connected to CarMaker
2025-11-22 10:30:50 [CMD] DVAWrite DM.Gas 0.5 2000 Abs
2025-11-22 10:30:51 [RESULT] OK
```

**`llm_interventions.log`** (JSON Lines)
```jsonl
{"timestamp":"2025-11-22T10:32:15Z","triggerId":"speed_limit","condition":"Car_v > 16.67","telemetry":{"carV":18.5},"llmAnalysis":"...","llmScript":"...","status":"success","durationMs":1250}
```

---

## Module Structure

```
src-tauri/src/
├── carmaker/
│   ├── mod.rs              # Module exports
│   ├── client.rs           # TCP socket client (APO protocol)
│   ├── state.rs            # In-memory state (CarMakerState)
│   ├── types.rs            # Data types (TelemetryData, etc.)
│   ├── monitor.rs          # LLM monitor loop (optional)
│   └── config.rs           # Config file I/O
├── commands/
│   └── carmaker_control.rs # Tauri commands
└── main.rs / lib.rs
```

---

## Core Components

### 1. CarMaker TCP Client

**Responsibilities**:
- CarMaker APO 서버에 TCP 연결 (기본: localhost:16660)
- DVARead, DVAWrite, StartSim, StopSim 등 명령 실행
- Tcl Eval 배치 읽기 (데이터 동기화 문제 해결)

**Key Methods**:
```rust
impl CarMakerClient {
    async fn connect(host: &str, port: u16) -> Result<Self>;
    async fn execute_command(&mut self, cmd: &str) -> Result<String>;
    async fn read_telemetry(&mut self) -> Result<TelemetryData>;
    async fn write_value(&mut self, name: &str, value: f64) -> Result<()>;
}
```

**APO Protocol**:
- 명령: `DVARead Car.v\n`
- 응답: `27.78\n` (단일 값)
- 배치: `Eval {list $Qu(Time) $Qu(Car.v) $Qu(DM.Gas)}`
- 응답: `"10.5 27.78 0.5"` (공백 구분)

### 2. In-Memory State

**Structure**:
```rust
pub struct CarMakerState {
    pub telemetry: Arc<RwLock<TelemetryData>>,
    pub command_history: Arc<RwLock<VecDeque<CommandRecord>>>,
    pub connection_status: Arc<RwLock<ConnectionStatus>>,
}
```

**Usage**:
- Frontend는 Tauri command로 상태 조회
- 백그라운드 태스크가 10Hz로 텔레메트리 업데이트
- 명령 이력은 최근 100개만 메모리 유지

### 3. Tauri Commands

```rust
#[tauri::command]
async fn get_vehicle_status(state: State<'_, CarMakerState>) -> Result<TelemetryData>;

#[tauri::command]
async fn execute_carmaker_cmd(cmd: String, state: State<'_, CarMakerState>) -> Result<String>;

#[tauri::command]
async fn get_triggers() -> Result<Vec<LlmTrigger>>;

#[tauri::command]
async fn save_triggers(triggers: Vec<LlmTrigger>) -> Result<()>;

#[tauri::command]
async fn get_intervention_logs(limit: usize) -> Result<Vec<InterventionLog>>;
```

### 4. LLM Monitor (Optional)

**Responsibilities**:
- 10Hz로 트리거 조건 평가
- 트리거 발동 시:
  1. 시뮬레이션 일시정지
  2. Claude CLI 호출 (상황 분석 요청)
  3. 생성된 스크립트 실행
  4. 로그 파일 기록
  5. 시뮬레이션 재개

**Safety**:
- 30초 타임아웃
- try/finally로 시뮬레이션 재개 보장
- 에러 발생 시 즉시 정지

---

## Data Flow

### Manual Control
```
User Input (Frontend)
  ▼
invoke('execute_carmaker_cmd', {cmd})
  ▼
Rust: CarMakerClient.execute_command(cmd)
  ▼
CarMaker APO (TCP)
  ▼
Result → Log File → Command History (VecDeque)
  ▼
Frontend (success/error message)
```

### Real-Time Telemetry
```
Background Task (Tokio, 10Hz)
  ▼
CarMakerClient.read_telemetry()
  ▼
Update CarMakerState.telemetry (RwLock)
  ▼
Frontend: setInterval(() => invoke('get_vehicle_status'), 100)
  ▼
UI Update (Speed, Gas, Brake, etc.)
```

### LLM Intervention
```
LLM Monitor Loop (10Hz)
  ▼
Load llm_triggers.json
  ▼
Evaluate Conditions (Car_v > 16.67)
  ▼
Trigger Match → Pause Simulation
  ▼
Build Prompt → Execute Claude CLI
  ▼
Parse Response → Execute Commands
  ▼
Log to llm_interventions.log (JSON Lines)
  ▼
Resume Simulation
```

---

## Frontend Routes

```
/carmaker-control/
  ├── dashboard          # 실시간 모니터링 (텔레메트리 표시)
  ├── manual-control     # 수동 제어 (Gas/Brake/Steering 슬라이더)
  ├── triggers           # LLM 트리거 설정 (CRUD)
  └── interventions      # LLM 개입 로그 (파일에서 읽기)
```

---

## Implementation Phases

### Phase 1: CarMaker TCP Client (Rust)
- TCP 소켓 연결 구현
- DVARead, DVAWrite 명령 구현
- Tcl Eval 배치 읽기 구현
- 에러 처리 및 재연결 로직

### Phase 2: Tauri Integration
- In-memory state 구조체 생성
- Tauri commands 구현 (status, cmd)
- JSON 파일 I/O (config, triggers)
- 로그 파일 쓰기 유틸리티

### Phase 3: Frontend UI
- Dashboard 페이지 (텔레메트리 표시)
- Manual Control 페이지 (슬라이더)
- 10Hz 실시간 업데이트 구현

### Phase 4: LLM Integration
- Trigger 설정 UI
- LLM Monitor loop 구현
- Claude CLI 통합
- Intervention log 표시

### Phase 5: AI Chat Integration
- Vehicle control command templates
- Tag parser 확장 (`<vehicle_cmd>`, `<vehicle_query>`)
- Action executor 확장

---

## Key Decisions

### Why Rust-Only?
- **성능**: 직접 TCP 통신이 Python 브리지보다 빠름
- **단순성**: 서브프로세스 관리 불필요
- **타입 안전성**: Rust 타입 시스템 활용
- **유지보수**: 단일 언어로 관리

### Why No Database?
- **실시간 시스템**: 데이터는 일시적, 저장 불필요
- **성능**: 메모리 상태가 DB 쿼리보다 빠름
- **단순성**: SeaORM/마이그레이션 불필요
- **이식성**: JSON 파일이 DB보다 이동 쉬움

### Why File-Based Logging?
- **간단함**: `std::fs` 사용, append-only
- **분석 용이**: JSON Lines는 표준 포맷
- **성능**: 비동기 쓰기, 실시간 루프 차단 없음

---

## CarMaker APO Protocol Reference

### Essential Commands
```
StartSim                                    # 시뮬레이션 시작
StopSim                                     # 시뮬레이션 정지
DVARead <Name>                              # 단일 값 읽기
DVAWrite <Name> <Value> [Duration] [Mode]  # 값 쓰기
Eval {list $Qu(Time) $Qu(Car.v) ...}       # 배치 읽기
```

### Essential Quantities (UAQ)
- `Time` - 시뮬레이션 시간 (s)
- `Car.v` - 속도 (m/s)
- `DM.Gas` - 가스 페달 (0-1)
- `DM.Brake` - 브레이크 페달 (0-1)
- `DM.Steer.Ang` - 조향각 (rad)
- `Car.ax` - 종방향 가속도 (m/s²)
- `Car.ay` - 횡방향 가속도 (m/s²)

### Speed Conversions
- 50 km/h = 13.89 m/s
- 60 km/h = 16.67 m/s
- 100 km/h = 27.78 m/s

---

## Risk Mitigation

### TCP Connection Issues
- **자동 재연결**: 연결 끊김 감지 시 5초 후 재시도
- **타임아웃**: 모든 TCP 읽기/쓰기 3초 타임아웃
- **UI 표시**: 연결 상태 명확히 표시

### Data Synchronization
- **Tcl Eval 사용**: 단일 요청으로 모든 값 읽기 (원본 시스템 문제 해결)
- **Atomic 업데이트**: RwLock으로 텔레메트리 전체 업데이트

### LLM Safety
- **타임아웃**: 30초 제한
- **Finally 블록**: 시뮬레이션 재개 보장
- **에러 로깅**: 모든 개입 결과 기록

---

## Success Criteria

- [ ] CarMaker APO 연결 성공 (Rust TCP)
- [ ] 실시간 텔레메트리 표시 (10Hz)
- [ ] 수동 제어 작동 (Gas/Brake/Steering)
- [ ] LLM 트리거 시스템 작동
- [ ] AI 채팅으로 차량 제어 가능
- [ ] 모든 로그 파일에 정상 기록

---

**Version**: 1.0
**Status**: Ready for Implementation
