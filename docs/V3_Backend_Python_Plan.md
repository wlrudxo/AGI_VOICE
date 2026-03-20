# AGI Voice V3 Plan

> 목적: V2의 사용자 경험과 UI를 유지한 채, 백엔드를 Rust/Tauri 중심 구조에서 Python 중심 구조로 재구성한다.
> 기준일: 2026-03-20

---

## 1. 핵심 목표

### 1.1 반드시 지킬 것

- 프론트엔드 UI는 바꾸지 않는다.
- 화면 구조, 라우트, 컴포넌트 레이아웃, 스타일, 사용자 플로우를 유지한다.
- 사용자 입장에서 기능 위치와 동작 방식이 달라지지 않아야 한다.
- 개발 중 프론트 수정은 즉시 반영되어야 한다.
- 백엔드 수정도 자동 재시작으로 바로 반영되어야 한다.

### 1.2 이번 V3의 본질

V3는 "새 앱 디자인"이 아니라 "백엔드 파이썬화"다.

즉, 아래를 목표로 한다.

- 프론트: 최대한 재사용
- 데스크톱 셸: Electron으로 교체
- 앱 코어 로직: Python으로 이동
- 실시간 제어, AI, DB, 트리거, 설정 관리를 Python 서비스가 담당

### 1.3 비목표

- UI 리디자인
- 정보 구조 변경
- 사용성 변경
- 기능 대거 삭제/재배치
- Electron main process에 비즈니스 로직 누적

---

## 2. 왜 이 방향인가

현재 V2는 프론트는 이미 웹 스택이지만, 실제 앱 서비스 레이어는 Rust/Tauri가 많이 담당하고 있다.

Rust가 맡고 있는 핵심 영역:

- AI 채팅 orchestration
- SQLite CRUD
- CarMaker TCP 제어
- 트리거 상태와 실행
- 설정, 백업, 파일 경로 관리
- Tauri IPC 표면 전체

장기 연구용 프로젝트 관점에서 문제는 다음과 같다.

- 기능을 자주 붙이고 구조를 자주 바꾸게 됨
- 외부 Python 생태계 활용이 중요함
- 실험 코드, 스크립트, 데이터 처리, LLM 연동이 계속 늘어남
- Rust/Tauri는 배포는 좋지만 연구 개발 루프는 상대적으로 무거움

따라서 V3는 Electron 자체가 목적이 아니라, Python을 시스템 중심으로 두는 것이 목적이다.

---

## 3. V3 아키텍처 원칙

### 3.1 목표 구조

```text
Frontend (SvelteKit/Vite)
    ->
Electron Renderer
    ->
Preload Bridge
    ->
Electron Main (thin shell only)
    ->
Python App Service
    ->
SQLite / CarMaker / Claude CLI / Embeddings / Trigger Engine
```

### 3.2 역할 분리

#### Frontend

- 기존 화면 유지
- 기존 상태 관리와 UI 컴포넌트 최대한 유지
- Tauri `invoke()` 직접 호출 제거
- 대신 API adapter 또는 preload bridge만 호출

#### Electron Main

- 창 생성
- 트레이
- 글로벌 단축키
- 파일 열기/저장 dialog
- Python 프로세스 시작/종료 감시
- preload bridge 연결

주의:

- Electron main은 앱 로직을 가지지 않는다.
- DB 처리, 트리거 판단, CarMaker 제어는 넣지 않는다.

#### Python App Service

- 앱의 실제 백엔드
- 비즈니스 로직의 단일 진실 공급원
- DB CRUD
- AI 채팅 orchestration
- CarMaker 연결 관리
- Trigger 엔진
- 설정/백업/복원
- 실시간 telemetry/event push

---

## 4. 기술 선택

### 4.1 유지

- SvelteKit
- 기존 UI 컴포넌트
- Vite 개발 서버
- SQLite

### 4.2 교체

- Tauri -> Electron
- Rust backend -> Python backend
- Tauri IPC -> preload bridge + HTTP/WebSocket

### 4.3 Python 권장 스택

- API: FastAPI
- ASGI server: uvicorn
- 설정: pydantic-settings
- 데이터 모델: pydantic
- DB: SQLAlchemy 또는 초기엔 sqlite 직접 접근
- 실시간 통신: WebSocket
- 백그라운드 작업: asyncio

---

## 5. 개발 경험 목표

### 5.1 프론트 자동 반영

- Vite dev server HMR 사용
- 컴포넌트/스타일 수정 즉시 반영

### 5.2 백엔드 자동 반영

- `uvicorn --reload` 사용
- Python 코드 저장 시 자동 재시작

### 5.3 Electron 자동 반영

- Electron main/preload는 자동 재시작 도구 사용
- renderer는 Vite가 즉시 반영

### 5.4 기대 효과

- UI 수정: 즉시 반영
- 백엔드 API 수정: 저장 후 자동 재시작
- Rust 빌드/링크 대기 제거
- 연구용 기능 추가 속도 향상

---

## 6. 절대 유지할 사용자 경험 계약

V3에서 아래는 바뀌면 안 된다.

- 메뉴 구조
- 페이지 라우트
- 버튼 위치와 의미
- 주요 입력 폼 구조
- 채팅 사용 흐름
- 자율주행 화면 동선
- 트리거 관리 방식
- 맵 관리 기본 흐름
- 설정 화면 항목 의미

허용되는 변경:

- 내부 API 호출 방식
- 개발/배포 구조
- 백엔드 구현 언어
- 로컬 파일 저장 위치 일부 조정
- 내부 상태 관리 구현

---

## 7. 기능별 이관 원칙

### 7.1 CarMaker

우선순위: 최상

이유:

- 이미 Python 자산이 존재함
- 실시간 연구 기능의 핵심임
- Rust보다 Python에서 실험/확장이 쉬움

목표:

- Python 서비스가 CarMaker 세션을 직접 관리
- telemetry는 WebSocket push 또는 polling API 제공
- 차량 제어 명령은 Python API에서 실행
- watched traffic object 관리도 Python이 담당

### 7.2 Trigger

우선순위: 최상

원칙:

- trigger 평가와 실행 orchestration을 Python으로 이동
- 프론트는 CRUD와 로그 표시만 담당
- trigger firing, pause/resume, command execution, LLM request는 서버 측 처리

이유:

- UI 탭 상태와 분리 가능
- 장기적으로 headless 자동화에 유리
- 실시간 처리 일관성 확보

### 7.3 Chat / AI

우선순위: 상

목표:

- conversation/message CRUD를 Python으로 이동
- prompt assembly를 Python이 담당
- Claude CLI 또는 향후 다른 모델 호출도 Python에서 담당
- 장기적으로 AI 기능 확장 중심축을 Python으로 통일

### 7.4 Settings / Backup

우선순위: 상

목표:

- 설정 저장/로드를 Python 서비스가 담당
- 백업/복원도 Python에서 수행
- Electron은 파일 선택만 담당

### 7.5 Maps / Embeddings

우선순위: 중

목표:

- map CRUD 이관
- embeddings 관련 Python 자산 재사용
- 장기적으로 RAG/벡터 검색은 Python 중심으로 정리

---

## 8. 프론트엔드 이관 전략

### 8.1 원칙

프론트 화면은 유지하되, 데이터 접근 계층만 바꾼다.

즉:

- 페이지를 다시 만들지 않는다.
- UI 컴포넌트를 다시 디자인하지 않는다.
- `@tauri-apps/api/*` 의존을 제거한다.
- API adapter 층을 도입한다.

### 8.2 해야 할 일

- `invoke()` 직접 호출 지점 목록화
- 기능별 adapter 모듈 생성
- Tauri window/dialog/fs 기능은 preload bridge로 치환
- 나머지 앱 기능은 Python API 호출로 치환

### 8.3 프론트 목표 상태

```text
Route/Page
    ->
Store / Action
    ->
Frontend API Adapter
    ->
window.app.* or fetch/ws
```

이렇게 되면 이후 데스크톱 셸 교체나 웹 버전 추가도 쉬워진다.

---

## 9. 데이터베이스 전략

### 9.1 기본 원칙

- 가능하면 기존 SQLite 스키마를 초기에 유지한다.
- V3 초반에는 "동작 복제"를 우선한다.
- schema 정리는 parity 확보 후 한다.

### 9.2 이유

- UI 무변경 목표와 충돌하지 않음
- 데이터 migration 리스크 감소
- 기존 CRUD 흐름을 빠르게 복제 가능

### 9.3 단계

1. 기존 테이블/컬럼/제약 정리
2. Python 모델 정의
3. 읽기/쓰기 동작 복제
4. parity 확보 후 schema 정리 여부 판단

---

## 10. API 설계 원칙

### 10.1 계약 우선

새 Python 백엔드는 기존 Tauri command surface를 기준으로 설계한다.

초기 목표는 "UI가 기대하는 요청/응답 형태를 최대한 유지"하는 것이다.

### 10.2 통신 분리

#### HTTP

- CRUD
- 설정
- 백업/복원
- 일회성 명령

#### WebSocket

- telemetry stream
- trigger logs
- backend event stream
- long-running task progress

### 10.3 에러 규약

- 사용자 표시용 메시지와 내부 로그를 분리
- API 응답 포맷 통일
- connection error, validation error, runtime error 구분

---

## 11. 권장 폴더 구조

```text
AGI_VOICE_V3/
├── apps/
│   ├── desktop-electron/
│   └── frontend/
├── services/
│   └── python-api/
├── packages/
│   └── shared-contracts/
├── scripts/
└── docs/
```

### 11.1 frontend

- 기존 SvelteKit UI 이식
- UI/UX 무변경 원칙 적용

### 11.2 desktop-electron

- Electron main
- preload bridge
- packaging

### 11.3 python-api

- `app/api`
- `app/chat`
- `app/carmaker`
- `app/triggers`
- `app/settings`
- `app/db`
- `app/maps`
- `app/embeddings`

### 11.4 shared-contracts

- API schema
- TypeScript 타입
- 예제 payload

---

## 12. 단계별 실행 계획

## Phase 0. 명세 고정

목표:

- 현재 V2 기능 목록 확정
- 반드시 유지할 UX 명문화
- Tauri command 목록을 API 계약 초안으로 정리

산출물:

- 기능 목록
- 화면별 dependency 목록
- API 명세 초안
- parity 체크리스트

완료 기준:

- V3에서 반드시 재현해야 할 기능 범위가 확정됨

## Phase 1. 뼈대 구축

목표:

- Electron shell 기본 구성
- Python API 기본 구성
- frontend dev 서버 연동
- 개발 모드 자동반영 환경 구성

산출물:

- Electron dev 실행
- FastAPI dev 실행
- Vite renderer 연동
- 기본 health check

완료 기준:

- 프론트, Electron, Python 3개 프로세스가 개발 모드에서 함께 돈다

## Phase 2. CarMaker 이관

목표:

- CarMaker 연결/상태/명령/telemetry를 Python으로 이관

산출물:

- connect/disconnect/status API
- telemetry stream
- vehicle command API
- watched traffic object API

완료 기준:

- 기존 vehicle-control UI를 거의 그대로 붙여 동작 가능

## Phase 3. Trigger 이관

목표:

- trigger CRUD와 실행 엔진을 Python으로 이관

산출물:

- trigger REST API
- trigger evaluator loop
- trigger execution/log stream
- pause/resume simulation orchestration

완료 기준:

- 기존 trigger UI에서 생성/활성화/실행이 동작

## Phase 4. Chat / Settings / Conversation 이관

목표:

- AI 채팅과 설정 관리를 Python으로 이관

산출물:

- settings API
- conversation/message CRUD
- prompt assembly
- Claude 호출 래퍼

완료 기준:

- 기존 채팅 화면 UX 그대로 동작

## Phase 5. Maps / Embeddings 이관

목표:

- map CRUD와 RAG/embedding 기능 이관

완료 기준:

- 기존 map UI가 새 백엔드와 동작

## Phase 6. 안정화 / 컷오버

목표:

- V2 대비 기능 parity 검증
- packaging 안정화
- 문서화

완료 기준:

- V2 없이 V3만으로 일상 연구 사용 가능

---

## 13. 마이그레이션 우선순위

### 13.1 가장 먼저 할 것

- CarMaker
- Trigger
- 설정/기본 실행 구조

### 13.2 그 다음

- Chat
- Conversation/Message CRUD

### 13.3 마지막

- Maps
- Embeddings
- 백업/복원 polish

---

## 14. 성공 기준

### 14.1 사용자 관점

- 기존 사용자 기준 "앱이 달라졌다"는 느낌이 없어야 한다.
- 동일한 화면에서 동일한 방식으로 작업할 수 있어야 한다.
- 기존 주요 기능이 모두 동작해야 한다.

### 14.2 개발자 관점

- UI 수정 시 즉시 반영된다.
- Python 코드 수정 시 자동 재시작된다.
- CarMaker 관련 기능 추가 속도가 빨라진다.
- AI/자동화/스크립팅 실험이 쉬워진다.
- 이후 기능 추가 시 Rust/Tauri 병목이 없다.

### 14.3 아키텍처 관점

- Electron은 thin shell이다.
- 비즈니스 로직이 Python에 집중된다.
- 프론트는 backend-agnostic에 가까워진다.
- 실시간 이벤트와 CRUD 경계가 명확하다.

---

## 15. 주요 리스크

### 15.1 UI 무변경 원칙 훼손

리스크:

- 이관 중 프론트 코드를 과하게 정리하다가 UX가 변질될 수 있음

대응:

- UI 리팩터링 금지
- adapter 계층만 추가
- parity 체크리스트 기준으로 검증

### 15.2 Trigger 책임 분산

리스크:

- 현재 일부 로직이 프론트에 남아 있어 Python 이관 시 경계가 꼬일 수 있음

대응:

- Trigger는 이번에 명확히 서버 책임으로 재정의

### 15.3 Electron main 비대화

리스크:

- 편하다는 이유로 main process에 로직을 넣기 시작할 수 있음

대응:

- main은 창/트레이/프로세스 관리만 담당

### 15.4 Python reload 중 상태 유실

리스크:

- 개발 모드에서 connection/session state가 자주 날아갈 수 있음

대응:

- reconnect 전략
- 상태 복구 설계
- dev와 production 동작 차이 명시

### 15.5 패키징 복잡도

리스크:

- Electron + Python bundling은 새 복잡도를 만든다

대응:

- 초기에는 dev 우선
- packaging은 parity 확보 후 정리

---

## 16. 의사결정 요약

- V3의 목표는 UI 변경이 아니라 백엔드 Python화다.
- 프론트는 최대한 그대로 유지한다.
- Electron은 shell이다.
- Python이 시스템 중심이다.
- CarMaker와 Trigger를 최우선 이관 대상으로 잡는다.
- 초기 목표는 "더 예쁜 구조"가 아니라 "기존 UX 유지 + 연구 확장성 확보"다.

---

## 17. 다음 액션

바로 시작할 작업 순서:

1. V2의 Tauri command 목록을 V3 API 명세 초안으로 정리
2. 프론트의 `invoke()` 사용 지점을 기능별로 분류
3. V3 repo 구조 생성
4. Electron + FastAPI + Vite 개발 모드 뼈대 구축
5. CarMaker 기능부터 Python 서비스로 이식 시작

