# AGI Voice V3 API Mapping

> 목적: V2 프론트엔드가 현재 의존하는 Tauri command 및 plugin API를 V3의 Python backend / Electron preload 구조로 매핑한다.
> 기준: UI/UX 무변경, 프론트 화면 재사용, 백엔드 Python화
> 기준일: 2026-03-20

---

## 1. 문서 목적

이 문서는 V3 이관에서 가장 중요한 계약 문서다.

핵심 역할:

- 현재 프론트가 호출하는 Tauri API를 전부 목록화
- 각 호출이 어느 화면/스토어에서 사용되는지 명시
- V3에서 그것이 Python HTTP API인지, WebSocket인지, Electron preload인지 결정
- 우선순위를 정해 실제 이관 순서를 만든다

이 문서의 기준 원칙:

- 프론트 화면은 유지
- 프론트 로직도 최대한 유지
- 데이터 접근층만 교체
- Tauri 전용 기능은 preload bridge로 이동
- 앱 로직은 Python으로 이동

---

## 2. V3 통신 계층 원칙

### 2.1 Python HTTP API로 갈 것

- CRUD
- 설정 조회/저장
- 채팅 요청
- CarMaker connect/disconnect/command
- 일회성 작업

### 2.2 Python WebSocket으로 갈 것

- telemetry stream
- trigger log stream
- backend event stream
- long-running task progress

### 2.3 Electron preload로 갈 것

- 창 크기/위치/표시/숨김/포커스
- 전체화면 토글
- dialog open/save
- 파일 읽기
- 글로벌 단축키 등록
- 앱 종료/최소화 관련 셸 기능

---

## 3. 프론트 사용 Tauri Command 목록

아래 표는 현재 `src/` 기준 실제 사용 중인 `invoke()` 호출을 기준으로 정리했다.

## 3.1 CarMaker / Autonomous Driving

| V2 Tauri Command | 사용 위치 | V3 대상 | 통신 방식 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `connect_carmaker` | `src/lib/stores/carmakerStore.svelte.ts` | `POST /api/carmaker/connect` | HTTP | P0 | host, port 전달 |
| `disconnect_carmaker` | `src/lib/stores/carmakerStore.svelte.ts` | `POST /api/carmaker/disconnect` | HTTP | P0 | |
| `get_connection_status` | `src/lib/stores/carmakerStore.svelte.ts` | `GET /api/carmaker/status` | HTTP | P0 | 초기 복구용 |
| `get_vehicle_status` | `src/lib/stores/carmakerStore.svelte.ts` | `/ws/telemetry` 또는 `GET /api/carmaker/telemetry` | WebSocket 우선 | P0 | 현재는 10Hz polling, V3는 push 권장 |
| `execute_vehicle_command` | `src/lib/stores/carmakerStore.svelte.ts`, `src/routes/autonomous-driving/manual-control/+page.svelte` | `POST /api/carmaker/command` | HTTP | P0 | raw command 실행 |
| `set_gas` | `src/lib/stores/carmakerStore.svelte.ts`, `src/routes/autonomous-driving/manual-control/+page.svelte` | `POST /api/carmaker/control/gas` | HTTP | P0 | |
| `set_brake` | `src/lib/stores/carmakerStore.svelte.ts`, `src/routes/autonomous-driving/manual-control/+page.svelte` | `POST /api/carmaker/control/brake` | HTTP | P0 | |
| `set_steer` | `src/routes/autonomous-driving/manual-control/+page.svelte` | `POST /api/carmaker/control/steer` | HTTP | P0 | |
| `set_target_speed` | 프론트 직접 사용 없음 | `POST /api/carmaker/control/target-speed` | HTTP | P2 | backend parity용 |
| `start_simulation` | 프론트 직접 사용 없음 | `POST /api/carmaker/simulation/start` | HTTP | P1 | 내부 사용 가능성 있음 |
| `stop_simulation` | 프론트 직접 사용 없음 | `POST /api/carmaker/simulation/stop` | HTTP | P1 | 내부 사용 가능성 있음 |
| `set_monitoring_state` | `src/lib/stores/carmakerStore.svelte.ts` | 제거 또는 `POST /api/carmaker/monitoring` | HTTP | P1 | V3에서는 ws connect/disconnect로 대체 권장 |
| `is_monitoring_active` | 프론트 직접 사용 없음 | `GET /api/carmaker/monitoring` | HTTP | P2 | parity용 |
| `add_watched_traffic_object` | `src/lib/stores/carmakerStore.svelte.ts` | `POST /api/carmaker/watched-objects` | HTTP | P0 | |
| `remove_watched_traffic_object` | `src/lib/stores/carmakerStore.svelte.ts` | `DELETE /api/carmaker/watched-objects/{index}` | HTTP | P0 | |
| `get_watched_traffic_objects` | `src/lib/stores/carmakerStore.svelte.ts` | `GET /api/carmaker/watched-objects` | HTTP | P0 | |
| `clear_watched_traffic_objects` | `src/lib/stores/carmakerStore.svelte.ts` | `DELETE /api/carmaker/watched-objects` | HTTP | P0 | |

### 이관 메모

- V2는 `get_vehicle_status`를 프론트에서 10Hz polling 하고 있음.
- V3에서는 UI는 유지하되 내부 구현은 WebSocket 구독 방식으로 바꾸는 것이 바람직하다.
- 단, 초기 parity 확보 단계에서는 polling API로 먼저 복제해도 된다.

---

## 3.2 Trigger

| V2 Tauri Command | 사용 위치 | V3 대상 | 통신 방식 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `get_triggers` | `src/routes/autonomous-driving/triggers/+page.svelte`, `src/lib/stores/triggerMonitor.svelte.ts` | `GET /api/triggers` | HTTP | P0 | |
| `get_trigger_by_id` | 프론트 직접 사용 없음 | `GET /api/triggers/{id}` | HTTP | P2 | parity용 |
| `create_trigger` | `src/routes/autonomous-driving/triggers/+page.svelte` | `POST /api/triggers` | HTTP | P0 | |
| `update_trigger` | `src/routes/autonomous-driving/triggers/+page.svelte` | `PUT /api/triggers/{id}` | HTTP | P0 | |
| `delete_trigger` | `src/routes/autonomous-driving/triggers/+page.svelte` | `DELETE /api/triggers/{id}` | HTTP | P0 | |
| `toggle_trigger` | `src/routes/autonomous-driving/triggers/+page.svelte` | `POST /api/triggers/{id}/toggle` | HTTP | P0 | |
| `toggle_rule_control` | `src/routes/autonomous-driving/triggers/+page.svelte` | `POST /api/triggers/{id}/toggle-rule-control` | HTTP | P0 | |

### 이관 메모

- V2는 trigger evaluation 일부를 프론트에서 수행하고 있다.
- V3에서는 CRUD만 프론트에서 호출하고, 평가/실행은 Python 서버가 담당한다.
- 따라서 V3 추가 API가 필요하다:
  - `GET /ws/triggers/logs`
  - `GET /api/triggers/runtime-status`
  - `POST /api/triggers/runtime/start`
  - `POST /api/triggers/runtime/stop`

---

## 3.3 Chat / Conversation / AI Settings

| V2 Tauri Command | 사용 위치 | V3 대상 | 통신 방식 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `chat` | `src/lib/components/ChatView.svelte`, `src/lib/stores/triggerMonitor.svelte.ts` | `POST /api/chat` | HTTP | P0 | 핵심 API |
| `get_chat_settings` | `src/lib/components/ChatView.svelte`, `src/routes/ai-settings/+page.svelte`, `src/routes/autonomous-driving/settings/+page.svelte`, `src/lib/stores/triggerMonitor.svelte.ts` | `GET /api/settings/chat` | HTTP | P0 | |
| `update_chat_settings` | `src/lib/components/ChatSettingsView.svelte`, `src/routes/ai-settings/+page.svelte`, `src/routes/ai-settings/chat-settings/+page.svelte` | `PUT /api/settings/chat` | HTTP | P0 | |
| `get_conversations` | `src/lib/components/ChatHistoryView.svelte` | `GET /api/conversations` | HTTP | P0 | |
| `get_conversation_by_id` | `src/lib/components/ChatView.svelte` | `GET /api/conversations/{id}` | HTTP | P0 | |
| `get_conversation_messages` | `src/lib/components/ChatView.svelte` | `GET /api/conversations/{id}/messages` | HTTP | P0 | |
| `create_conversation` | 프론트 직접 사용 없음 | `POST /api/conversations` | HTTP | P1 | `chat` 내부 생성 가능 |
| `update_conversation` | `src/lib/components/ChatHistoryView.svelte` | `PUT /api/conversations/{id}` | HTTP | P0 | 제목 변경 |
| `delete_conversation` | `src/lib/components/ChatHistoryView.svelte` | `DELETE /api/conversations/{id}` | HTTP | P0 | |
| `get_prompt_templates` | `src/routes/ai-settings/+page.svelte`, `src/routes/ai-settings/system-messages/+page.svelte` | `GET /api/prompt-templates` | HTTP | P0 | |
| `get_prompt_template_by_id` | 프론트 직접 사용 없음 | `GET /api/prompt-templates/{id}` | HTTP | P2 | |
| `create_prompt_template` | `src/routes/ai-settings/system-messages/+page.svelte` | `POST /api/prompt-templates` | HTTP | P0 | |
| `update_prompt_template` | `src/routes/ai-settings/system-messages/+page.svelte` | `PUT /api/prompt-templates/{id}` | HTTP | P0 | |
| `delete_prompt_template` | `src/routes/ai-settings/system-messages/+page.svelte` | `DELETE /api/prompt-templates/{id}` | HTTP | P0 | |
| `get_characters` | `src/routes/ai-settings/+page.svelte`, `src/routes/ai-settings/characters/+page.svelte` | `GET /api/characters` | HTTP | P0 | |
| `get_character_by_id` | 프론트 직접 사용 없음 | `GET /api/characters/{id}` | HTTP | P2 | |
| `create_character` | `src/routes/ai-settings/characters/+page.svelte` | `POST /api/characters` | HTTP | P0 | |
| `update_character` | `src/routes/ai-settings/characters/+page.svelte` | `PUT /api/characters/{id}` | HTTP | P0 | |
| `delete_character` | `src/routes/ai-settings/characters/+page.svelte` | `DELETE /api/characters/{id}` | HTTP | P0 | |
| `get_command_templates` | `src/routes/ai-settings/commands/+page.svelte` | `GET /api/command-templates` | HTTP | P0 | |
| `get_command_template_by_id` | 프론트 직접 사용 없음 | `GET /api/command-templates/{id}` | HTTP | P2 | |
| `create_command_template` | `src/routes/ai-settings/commands/+page.svelte` | `POST /api/command-templates` | HTTP | P0 | |
| `update_command_template` | `src/routes/ai-settings/commands/+page.svelte` | `PUT /api/command-templates/{id}` | HTTP | P0 | |
| `toggle_command_template` | `src/routes/ai-settings/commands/+page.svelte` | `POST /api/command-templates/{id}/toggle` | HTTP | P0 | |
| `delete_command_template` | `src/routes/ai-settings/commands/+page.svelte` | `DELETE /api/command-templates/{id}` | HTTP | P0 | |

### 이관 메모

- `chat`는 V3의 가장 중요한 계약이다.
- 초기에는 스트리밍 없이 단일 응답으로 parity를 맞춰도 되지만, 장기적으로는 streaming 대응 가능 구조로 설계하는 것이 좋다.

---

## 3.4 App Settings / DB Management

| V2 Tauri Command | 사용 위치 | V3 대상 | 통신 방식 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `get_settings` | 프론트 직접 사용 흔적 미확인 | `GET /api/settings/app` | HTTP | P1 | settings store 확인 필요 |
| `update_settings` | `src/routes/app-settings/+page.svelte` | `PUT /api/settings/app` | HTTP | P0 | |
| `settings_health` | 프론트 직접 사용 없음 | `GET /api/health/settings` | HTTP | P3 | |
| `get_db_timestamp` | `src/lib/stores/dbWatcher.svelte.ts` | 제거 또는 `GET /api/runtime/db-timestamp` | HTTP | P1 | V3에서는 event push로 대체 검토 |
| `sync_db_on_shutdown` | `src/routes/+layout.svelte` | `POST /api/runtime/shutdown-sync` | HTTP 또는 preload wrapper | P1 | 앱 종료 직전 호출 |
| `export_db` | `src/routes/app-settings/+page.svelte` | `POST /api/db/export` | HTTP | P1 | dialog는 preload |
| `import_db` | `src/routes/app-settings/+page.svelte` | `POST /api/db/import` | HTTP | P1 | 파일 선택은 preload |
| `restore_backup` | `src/routes/app-settings/+page.svelte` | `POST /api/db/restore-backup` | HTTP | P1 | |
| `get_db_info` | 프론트 직접 사용 흔적 미확인 | `GET /api/db/info` | HTTP | P2 | |
| `sync_db_now` | 프론트 직접 사용 흔적 미확인 | `POST /api/db/sync` | HTTP | P2 | |

### 이관 메모

- `dbWatcher` 기반 polling은 V3에서 유지할 수도 있으나, 장기적으로는 WebSocket event 또는 store invalidation으로 교체하는 편이 낫다.
- 다만 UI 무변경 목표 때문에 초기엔 `get_db_timestamp`를 유지해도 된다.

---

## 3.5 Map / RAG / Embeddings

| V2 Tauri Command | 사용 위치 | V3 대상 | 통신 방식 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `create_map` | `src/routes/map-settings/generator/+page.svelte`, `src/routes/map-settings/library/+page.svelte`, `src/lib/actions/executor.ts` | `POST /api/maps` | HTTP | P1 | |
| `get_maps` | `src/routes/map-settings/library/+page.svelte`, `src/lib/actions/executor.ts` | `GET /api/maps` | HTTP | P1 | 검색/필터 포함 |
| `get_map_by_id` | `src/routes/map-settings/generator/+page.svelte`, `src/lib/actions/executor.ts` | `GET /api/maps/{id}` | HTTP | P1 | |
| `update_map` | `src/routes/map-settings/generator/+page.svelte`, `src/lib/actions/executor.ts` | `PUT /api/maps/{id}` | HTTP | P1 | |
| `delete_map` | `src/routes/map-settings/generator/+page.svelte`, `src/routes/map-settings/library/+page.svelte`, `src/lib/actions/executor.ts` | `DELETE /api/maps/{id}` | HTTP | P1 | |
| `get_map_count` | `src/lib/actions/executor.ts` | `GET /api/maps/count` | HTTP | P2 | |
| `embed_map` | `src/routes/map-settings/library/+page.svelte` | `POST /api/maps/{id}/embed` | HTTP | P2 | long task 가능 |
| `search_similar_maps` | `src/routes/map-settings/rag-test/+page.svelte` | `POST /api/maps/search-similar` | HTTP | P2 | |
| `build_all_embeddings` | `src/routes/map-settings/library/+page.svelte` | `POST /api/embeddings/build-all` | HTTP | P2 | progress event 필요 가능 |
| `embeddings_health` | 프론트 직접 사용 없음 | `GET /api/health/embeddings` | HTTP | P3 | |
| `maps_health` | 프론트 직접 사용 없음 | `GET /api/health/maps` | HTTP | P3 | |

### 이관 메모

- Maps/RAG는 핵심 제품 기능이지만 V3 1차 컷오버에서 CarMaker/Trigger/Chat보다 뒤로 둔다.
- Python 자산 재사용성이 높아 장기적으로는 오히려 더 유리하다.

---

## 4. 프론트 사용 Tauri Plugin API 목록

이 항목들은 Python이 아니라 Electron preload bridge가 담당해야 한다.

## 4.1 Window API

| V2 API | 사용 위치 | V3 대상 | 구현 위치 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `getCurrentWindow()` | `src/routes/+layout.svelte`, `src/lib/components/TitleBar.svelte`, `src/lib/components/AIChatWidget.svelte` | `window.desktop.getCurrentWindow()` 또는 기능별 wrapper | Electron preload | P0 | 직접 호환 wrapper 권장 |
| `currentMonitor()` | `src/routes/+layout.svelte` | `window.desktop.currentMonitor()` | Electron preload | P0 | 위젯 위치 계산 |
| `outerSize()` / `outerPosition()` | `src/routes/+layout.svelte` | preload window API | Electron preload | P0 | |
| `setSize()` / `setPosition()` | `src/routes/+layout.svelte` | preload window API | Electron preload | P0 | |
| `show()` / `hide()` / `setFocus()` | `src/routes/+layout.svelte` | preload window API | Electron preload | P0 | |
| `close()` | `src/routes/+layout.svelte`, `src/lib/components/TitleBar.svelte` | preload window API | Electron preload | P0 | |
| `isFullscreen()` / `setFullscreen()` | `src/routes/+layout.svelte` | preload window API | Electron preload | P1 | |
| `listen()` | `src/routes/+layout.svelte` | `window.desktop.on(event, cb)` | Electron preload | P0 | tray restore/widget 이벤트 |
| `onCloseRequested()` | `src/routes/+layout.svelte` | `window.desktop.onCloseRequested(cb)` | Electron preload | P0 | 앱 종료 제어 |

---

## 4.2 Dialog API

| V2 API | 사용 위치 | V3 대상 | 구현 위치 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `open()` | `src/routes/app-settings/+page.svelte`, `src/routes/map-settings/generator/+page.svelte` | `window.desktop.dialog.open()` | Electron preload | P0 | |
| `save()` | `src/routes/app-settings/+page.svelte` | `window.desktop.dialog.save()` | Electron preload | P0 | |

---

## 4.3 File System API

| V2 API | 사용 위치 | V3 대상 | 구현 위치 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `readTextFile()` | `src/routes/map-settings/generator/+page.svelte` | `window.desktop.fs.readTextFile(path)` | Electron preload | P0 | |

---

## 4.4 Global Shortcut API

| V2 API | 사용 위치 | V3 대상 | 구현 위치 | 우선순위 | 비고 |
|---|---|---|---|---|---|
| `register()` | `src/routes/+layout.svelte` | `window.desktop.shortcuts.register(accelerator, cb)` | Electron preload | P0 | `Ctrl+Shift+A` |

---

## 5. 프론트 adapter 계층 권장 구조

V3에서는 프런트가 아래 계층만 호출하도록 정리한다.

```text
routes/components/stores
    ->
lib/api/*
    ->
1) window.desktop.*     # Electron shell 기능
2) window.backend.*     # preload bridge를 통한 backend wrapper
3) fetch/ws             # 직접 Python API 호출
```

권장 구현:

```text
src/lib/api/chat.ts
src/lib/api/carmaker.ts
src/lib/api/triggers.ts
src/lib/api/settings.ts
src/lib/api/maps.ts
src/lib/api/runtime.ts
src/lib/desktop/window.ts
src/lib/desktop/dialog.ts
src/lib/desktop/fs.ts
src/lib/desktop/shortcuts.ts
```

### 원칙

- 페이지/스토어에서 `fetch`, `ipcRenderer`, preload를 직접 부르지 않는다.
- 반드시 adapter를 거친다.
- 이 레이어가 V2의 `invoke()` 대체물이다.

---

## 6. 우선순위 기준

### P0

컷오버 전 반드시 있어야 하는 것

- CarMaker 제어 핵심
- Trigger CRUD/실행 핵심
- Chat
- Chat settings
- Characters / Prompt templates / Command templates CRUD
- Window/dialog/fs/global shortcut preload 기능

### P1

초기 실사용 전에는 필요하지만 1차 골격보다 뒤로 밀 수 있는 것

- App settings
- DB export/import/restore
- sync on shutdown
- Maps CRUD

### P2

parity 또는 확장성을 위해 필요하지만 1차 V3 개발에서 후순위 가능한 것

- map count
- embeddings
- trigger by id
- command template by id
- extra runtime status APIs

### P3

health check류, 내부 관리용

- `*_health`

---

## 7. 추천 이행 순서

1. preload bridge부터 만든다
2. CarMaker API를 Python으로 만든다
3. 기존 `carmakerStore`를 adapter 기반으로 교체한다
4. Trigger runtime을 Python으로 옮긴다
5. Chat/Conversation/Settings API를 옮긴다
6. AI settings CRUD를 옮긴다
7. Maps/RAG를 옮긴다
8. DB backup/restore와 shutdown sync를 정리한다

---

## 8. 추가로 필요한 V3 전용 API

V2를 단순 복제하는 것만으로는 부족하고, V3에서는 아래 전용 API가 있으면 구조가 더 깔끔해진다.

| V3 전용 API | 목적 | 방식 |
|---|---|---|
| `/ws/telemetry` | CarMaker telemetry push | WebSocket |
| `/ws/triggers/logs` | trigger 실행 로그 push | WebSocket |
| `/ws/runtime/events` | 앱 전반 이벤트 push | WebSocket |
| `/api/runtime/health` | 전체 런타임 상태 확인 | HTTP |
| `/api/runtime/shutdown-sync` | 종료 직전 sync | HTTP |

---

## 9. 최종 판단

이 프로젝트에서 V3 매핑의 본질은 다음 한 줄로 요약된다.

`Tauri command surface를 Python API + Electron preload로 분해하되, 프론트가 기대하는 동작 계약은 유지한다.`

즉:

- 앱 로직은 Python으로 간다
- 셸 기능은 Electron preload로 간다
- 프론트 화면과 사용 흐름은 유지한다

