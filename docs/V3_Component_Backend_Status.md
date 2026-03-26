# V3 Component Backend Status

기준일: 2026-03-26

목표:
- V3 프런트엔드는 V2와 동일한 UX를 유지한다.
- 백엔드는 Python으로 재구성한다.
- 동작은 V2와 최대한 동일하게 유지하되, 내부 구현은 더 단순하고 유지보수 가능하게 만든다.

이 문서는 현재 코드 기준으로 각 프런트 컴포넌트/페이지가 어떤 기능을 요구하는지, 어떤 API가 필요한지, Python 백엔드에서 어디까지 붙어 있는지를 정리한다.

상태 표기:
- `완료`: 프런트와 백엔드가 실제로 연결되어 있음
- `부분`: 일부는 연결되었지만 localStorage, TODO, 동작 차이, 누락 기능이 남아 있음
- `미구현`: 프런트는 있으나 백엔드가 사실상 비어 있음

## 1. Shell / Desktop

| 영역 | 주요 파일 | 기능 | 필요 API / 연동 | 현재 상태 | 메모 |
|---|---|---|---|---|---|
| 루트 레이아웃 | `v3/apps/frontend/src/routes/+layout.svelte` | 타이틀바, 사이드바, 라우트 컨테이너, 채팅 위젯, dialog/toast host | `window.desktop.window.*`, `POST /api/settings/db/sync-shutdown` | 완료 | 종료 시 `minimizeToTray` 설정 반영. 위젯 복원 기능은 제거 결정 주석 반영 |
| 타이틀바 | `v3/apps/frontend/src/lib/components/TitleBar.svelte` | 최소화/최대화/닫기/위젯모드 | `window.desktop.window.minimize/toggleMaximize/close` | 완료 | Electron preload 의존 |
| 사이드바 | `v3/apps/frontend/src/lib/components/Sidebar.svelte` | 메인 네비게이션 | 라우팅만 필요 | 완료 | 백엔드 의존 없음 |
| UI 상태 | `v3/apps/frontend/src/lib/stores/uiStore.ts` | 채팅 열림 상태, 뷰 모드, 위젯 모드, 현재 대화 | 없음 | 완료 | 브라우저 상태 중심 |
| 창 설정 저장소 | `v3/apps/frontend/src/lib/stores/settingsStore.ts` | `minimizeToTray` 로드/저장 | `GET/PUT /api/settings/app` | 완료 | localStorage 캐시 + backend 저장 |

## 2. Dashboard

| 영역 | 주요 파일 | 기능 | 필요 API / 연동 | 현재 상태 | 메모 |
|---|---|---|---|---|---|
| 대시보드 홈 | `v3/apps/frontend/src/routes/+page.svelte` | 환영 화면, 시계, 기본 안내 | 없음 | 부분 | 화면은 존재하지만 실제 앱 상태 카드/요약 데이터는 아직 없음 |

## 3. AI Chat / Conversations

| 영역 | 주요 파일 | 기능 | 필요 API / 연동 | 현재 상태 | 메모 |
|---|---|---|---|---|---|
| 채팅 위젯 쉘 | `v3/apps/frontend/src/lib/components/AIChatWidget.svelte` | 채팅/기록/설정 전환, 트리거 모니터링 토글 | `triggerMonitor`, `carmakerStore`, `window.desktop.window.close` | 완료 | 프런트 동작 기준으로는 붙어 있음 |
| 채팅 본체 | `v3/apps/frontend/src/lib/components/ChatView.svelte` | 채팅 전송, 응답 표시, 액션 태그 파싱, 대화 불러오기 | `POST /api/chat`, `GET /api/settings/chat`, `GET /api/conversations/:id`, `GET /api/conversations/:id/messages` | 부분 | 기본 채팅은 됨. 응답 후 map/action 후처리 parity는 추가 검증 필요 |
| 대화 기록 | `v3/apps/frontend/src/lib/components/ChatHistoryView.svelte` | 대화 목록, 제목 변경, 삭제 | `GET /api/conversations`, `PUT /api/conversations/:id`, `DELETE /api/conversations/:id` | 완료 | 새 대화 생성은 `POST /api/chat`의 부수효과로만 발생 |
| 위젯 내 채팅 설정 | `v3/apps/frontend/src/lib/components/ChatSettingsView.svelte` | 기본 캐릭터/템플릿 설정 | `GET /api/characters`, `GET /api/prompt-templates`, `GET/PUT /api/settings/chat` | 완료 | 라우트 페이지와 중복 UI 존재 |

### 채팅 관련 백엔드 메모

- 구현 파일:
  - `v3/services/python-api/app/api/routes/chat.py`
  - `v3/services/python-api/app/api/routes/conversations.py`
  - `v3/services/python-api/app/services/chat.py`
- 현재 구현:
  - Claude CLI 호출
  - `CLAUDE.md` 생성
  - 대화/메시지 JSON 저장
  - conversation list/load/update/delete
- 남은 리스크:
  - 스트리밍 응답 없음
  - workspace 경로가 app settings의 `claudeWorkspaceDir`를 실제로 완전히 따르지 않음
  - V2 수준의 후처리 parity는 추가 검증 필요

## 4. AI Settings

| 영역 | 주요 파일 | 기능 | 필요 API / 연동 | 현재 상태 | 메모 |
|---|---|---|---|---|---|
| AI 설정 개요 | `v3/apps/frontend/src/routes/ai-settings/+page.svelte` | 현재 선택된 캐릭터/템플릿/모델 표시 및 저장 | `GET /api/prompt-templates`, `GET /api/characters`, `GET/PUT /api/settings/chat` | 완료 | |
| 채팅 설정 | `v3/apps/frontend/src/routes/ai-settings/chat-settings/+page.svelte` | 기본 캐릭터/템플릿/모델 선택 | `GET /api/characters`, `GET /api/prompt-templates`, `GET/PUT /api/settings/chat` | 완료 | |
| 시스템 메시지 | `v3/apps/frontend/src/routes/ai-settings/system-messages/+page.svelte` | 프롬프트 템플릿 CRUD | `GET/POST /api/prompt-templates`, `PUT/DELETE /api/prompt-templates/:id` | 완료 | |
| 캐릭터 | `v3/apps/frontend/src/routes/ai-settings/characters/+page.svelte` | 캐릭터 CRUD | `GET/POST /api/characters`, `PUT/DELETE /api/characters/:id` | 완료 | |
| 명령어 템플릿 | `v3/apps/frontend/src/routes/ai-settings/commands/+page.svelte` | 명령어 템플릿 CRUD, 활성/비활성 토글 | `GET/POST /api/command-templates`, `PUT/DELETE /api/command-templates/:id`, `POST /api/command-templates/:id/toggle` | 완료 | 활성 템플릿은 chat prompt에 주입됨 |
| 유저 정보 | `v3/apps/frontend/src/routes/ai-settings/user-info/+page.svelte` | 사용자 프로필/설명 저장 | localStorage | 부분 | 백엔드 미연결. 현재는 클라이언트 저장 후 chat에서 읽음 |
| 최종 메시지 | `v3/apps/frontend/src/routes/ai-settings/final-message/+page.svelte` | 최종 체크리스트 저장 | localStorage | 부분 | 백엔드 미연결. 현재는 클라이언트 저장 후 chat에서 읽음 |

### AI Settings 관련 백엔드 메모

- 구현 파일:
  - `v3/services/python-api/app/api/routes/characters.py`
  - `v3/services/python-api/app/api/routes/prompt_templates.py`
  - `v3/services/python-api/app/api/routes/command_templates.py`
  - `v3/services/python-api/app/api/routes/settings.py`
  - `v3/services/python-api/app/services/ai_catalog.py`
  - `v3/services/python-api/app/services/command_templates.py`
  - `v3/services/python-api/app/services/settings.py`
- 현재 구현:
  - JSON 기반 CRUD와 기본 seed 데이터
  - chat settings 저장
- 남은 리스크:
  - `user-info`, `final-message`는 아직 서버 소유 데이터가 아님
  - 개별 조회(`GET by id`)는 없어도 UI는 돌아가지만 API 표면은 V2보다 얇음

## 5. Autonomous Driving / CarMaker

| 영역 | 주요 파일 | 기능 | 필요 API / 연동 | 현재 상태 | 메모 |
|---|---|---|---|---|---|
| CarMaker store | `v3/apps/frontend/src/lib/stores/carmakerStore.svelte.ts` | 연결, 상태, 모니터링, telemetry, watched object, 명령 실행 | `/api/carmaker/status`, `/connect`, `/disconnect`, `/monitoring`, `/telemetry`, `/command`, `/watched-objects`, `/control/*` | 완료 | 자율주행 핵심 store |
| 차량 제어 | `v3/apps/frontend/src/routes/autonomous-driving/vehicle-control/+page.svelte` | 상태 표시, 시뮬레이션 start/stop/pause/resume, 모니터링, watched object 관리 | `carmakerStore`, `triggerMonitor` | 완료 | |
| 수동 제어 | `v3/apps/frontend/src/routes/autonomous-driving/manual-control/+page.svelte` | gas/brake/steer/raw command 전송 | `POST /api/carmaker/control/gas`, `/brake`, `/steer`, `/api/carmaker/command` | 완료 | |
| 트리거 설정 | `v3/apps/frontend/src/routes/autonomous-driving/triggers/+page.svelte` | trigger CRUD, active/rule-control 토글 | `GET/POST /api/triggers`, `PUT/DELETE /api/triggers/:id`, `POST /api/triggers/:id/toggle`, `POST /api/triggers/:id/toggle-rule-control` | 완료 | |
| 트리거 런타임 store | `v3/apps/frontend/src/lib/stores/triggerMonitor.svelte.ts` | monitoring on/off, logs, trigger list | `GET/POST /api/triggers/monitoring`, `GET/DELETE /api/triggers/logs`, `GET /api/triggers` | 완료 | runtime은 Python 백엔드가 수행 |
| 자율주행 설정 | `v3/apps/frontend/src/routes/autonomous-driving/settings/+page.svelte` | CarMaker 연결값, duration, controlMode, trigger AI 관련 UI | CarMaker 연결은 `carmakerStore`, AI 목록은 `/api/characters`, `/api/prompt-templates`, `/api/settings/chat` | 부분 | 연결은 실제 동작. 나머지 설정 다수가 localStorage/console 수준이라 backend 소유화 필요 |

### Autonomous 관련 백엔드 메모

- 구현 파일:
  - `v3/services/python-api/app/api/routes/carmaker.py`
  - `v3/services/python-api/app/api/routes/triggers.py`
  - `v3/services/python-api/app/services/carmaker.py`
  - `v3/services/python-api/app/services/triggers.py`
- 현재 구현:
  - TCP 기반 CarMaker 연결/명령/telemetry
  - trigger CRUD와 10Hz 백엔드 모니터링
  - cooldown, rule control, LLM trigger flow
- 남은 리스크:
  - WebSocket 없이 polling 중심
  - autonomous-driving/settings의 일부 설정은 아직 Python 설정 모델로 안 내려감

## 6. Map Settings / RAG

| 영역 | 주요 파일 | 기능 | 필요 API / 연동 | 현재 상태 | 메모 |
|---|---|---|---|---|---|
| Map Generator | `v3/apps/frontend/src/routes/map-settings/generator/+page.svelte` | 맵 생성/수정/삭제, XML 에디터, 시각화 | `GET /api/maps/:id`, `POST /api/maps`, `PUT /api/maps/:id`, `DELETE /api/maps/:id` | 미구현 | 프런트는 준비됐지만 백엔드 surface 부재 |
| Map Library | `v3/apps/frontend/src/routes/map-settings/library/+page.svelte` | 맵 목록, 삭제, 임베딩 생성, 전체 임베딩 빌드 | `GET /api/maps`, `DELETE /api/maps/:id`, `POST /api/maps/:id/embed`, `POST /api/maps/embeddings/build-all` | 미구현 | route 내부 TODO도 남아 있음 |
| RAG Test | `v3/apps/frontend/src/routes/map-settings/rag-test/+page.svelte` | 맵 검색 테스트 | `GET /api/maps/search` | 미구현 | |
| Map UI 컴포넌트 | `v3/apps/frontend/src/lib/components/MapCanvas.svelte`, `MapCard.svelte` | 시각화/카드 표시 | route 페이지에서 데이터 공급 | 완료 | UI 컴포넌트 자체는 사용 가능 |

### Map 관련 백엔드 메모

- 현재 `v3/services/python-api/app/api/routes/maps.py`에는 `/maps/health`만 존재한다.
- `v3/services/python-api/app/services/` 아래에 maps service가 없다.
- 결론: Map/RAG는 현재 프런트만 복사된 상태이며, 실제 Python 구현은 사실상 `0%`에 가깝다.

## 7. App Settings / Data Management

| 영역 | 주요 파일 | 기능 | 필요 API / 연동 | 현재 상태 | 메모 |
|---|---|---|---|---|---|
| 앱 설정 | `v3/apps/frontend/src/routes/app-settings/+page.svelte` | 창 설정, DB info, export/import/restore/sync, Claude workspace, 기본 모델 | `GET/PUT /api/settings/app`, `GET /api/settings/db/info`, `POST /api/settings/db/export`, `POST /api/settings/db/import`, `POST /api/settings/db/sync`, `POST /api/settings/db/restore` | 부분 | 핵심은 붙어 있음. 파일 선택은 아직 native dialog 대신 `prompt()` 사용 |

### App Settings 관련 백엔드 메모

- 구현 파일:
  - `v3/services/python-api/app/api/routes/settings.py`
  - `v3/services/python-api/app/services/settings.py`
- 현재 구현:
  - app/chat/trigger-ai settings 저장
  - data_dir 기준 DB 정보 조회
  - export/import/sync/restore/shutdown-sync
- 동작 차이:
  - V2의 SQLite 중심 관리와 달리 V3는 `data_dir ZIP snapshot` 방식
  - `databaseBackupEnabled`, `claudeWorkspaceDir` 같은 설정은 저장되지만 일부는 서비스 레벨에서 완전 집행되지 않음

## 8. 현재 백엔드 도메인별 요약

| 도메인 | 현재 수준 | 핵심 파일 | 비고 |
|---|---|---|---|
| Chat | 부분~강함 | `app/services/chat.py` | 실제 Claude 호출과 conversation 저장 존재 |
| Conversations | 완료 | `app/api/routes/conversations.py` | list/load/update/delete 가능 |
| CarMaker | 강함 | `app/services/carmaker.py` | 연결/telemetry/명령 실행 구현됨 |
| Triggers | 강함 | `app/services/triggers.py` | 10Hz runtime, rule/LLM 실행 존재 |
| AI Catalog | 완료 | `app/services/ai_catalog.py` | characters/prompt templates CRUD |
| Command Templates | 완료 | `app/services/command_templates.py` | CRUD + toggle |
| Settings | 부분~강함 | `app/services/settings.py` | 저장과 snapshot 기능 있음 |
| Maps / RAG | 미구현 | `app/api/routes/maps.py` | health 외 실질 기능 없음 |

## 9. 우선순위 제안

### P0
- `Map Settings` 전체 백엔드 구현
  - `/api/maps`
  - `/api/maps/:id`
  - `/api/maps/:id/embed`
  - `/api/maps/embeddings/build-all`
  - `/api/maps/search`

### P1
- `autonomous-driving/settings`의 localStorage/console 기반 설정을 Python 설정 모델로 이전
- `user-info`, `final-message`를 backend 소유 데이터로 전환
- `claudeWorkspaceDir`를 chat service 실제 작업 디렉토리에 반영

### P2
- DB 관리 UX를 Electron dialog 기반으로 전환
- polling 기반 일부 흐름을 WebSocket/SSE로 개선
- chat 후처리 parity 재검증

## 10. 구현 원칙

- 프런트 UX는 더 이상 바꾸지 않는다.
- 프런트에서 이미 호출 중인 경로를 기준으로 Python API를 채운다.
- 가능하면 새 API를 만들기보다, 프런트가 현재 기대하는 경로와 payload shape를 맞춘다.
- 설정/카탈로그/대화는 JSON 저장에서 시작하되, 추후 SQLite로 옮길 필요가 있으면 서비스 내부만 교체한다.
- `Map/RAG`는 현재 가장 큰 공백이므로 독립 도메인으로 우선 구현한다.
