# V3 Parity Audit

기준일: 2026-03-26

목적:
- `V3 = V2의 동작을 유지한 Python + Electron 포팅`이라는 기준으로 현재 구현 상태를 다시 점검한다.
- 코드 구조 유사성은 목표가 아니다.
- 개선/최적화는 parity가 닫힌 뒤에 한다.

판정 기준:
- `동일`: 사용자/프런트 기준으로 V2와 거의 같은 동작
- `부분 동일`: 주 흐름은 되지만 edge case, 세부 semantics, 저장 원본, 타이밍 차이가 남아 있음
- `미구현`: 프런트는 있어도 실제 backend 동작이 비어 있거나 핵심 흐름이 빠져 있음
- `의도적 차이`: 사용자가 승인했거나, V3에서 의도적으로 제거/단순화한 차이

---

## 1. 전체 요약

현재 상태를 한 줄로 요약하면:

- 프런트는 거의 V2 parity
- 백엔드는 핵심 도메인 대부분이 Python으로 포팅됨
- 남은 일은 `Trigger runtime semantics`, `Map/RAG semantics`, 일부 `App/Electron shell semantics`의 세부 parity 마감

대략적인 체감 진척:

| 도메인 | 상태 |
|---|---|
| Frontend shell / routes / UI | 동일에 가까움 |
| Electron shell | 부분 동일 |
| CarMaker | 동일에 가까움 |
| Chat / Conversations | 부분 동일 |
| AI Settings / Catalog | 동일에 가까움 |
| Trigger runtime | 의도적 차이 + parity 보강 필요 |
| App Settings / DB sync | 부분 동일 |
| Maps CRUD | 부분 동일 |
| Maps RAG / Embeddings | 부분 동일 |

---

## 2. Frontend / Shell

### 2.1 라우트 / 레이아웃 / 디자인

상태: `동일`

현재 V3 프런트는 SvelteKit 기준으로 V2 shell과 page 구조를 거의 그대로 가져온 상태다.

주요 근거:
- `v3/apps/frontend/src/routes/+layout.svelte`
- `v3/apps/frontend/src/routes/+page.svelte`
- `v3/apps/frontend/src/routes/ai-settings/**`
- `v3/apps/frontend/src/routes/autonomous-driving/**`
- `v3/apps/frontend/src/routes/map-settings/**`

메모:
- 사용자 기준으로는 V2와 거의 같은 화면 구조
- 현재 목표에서는 프런트 자체는 큰 gap보다 backend 연결 세부가 더 중요함

### 2.2 Electron 창 / tray / close

상태: `부분 동일`

구현됨:
- 커스텀 타이틀바
- native title/menu 제거
- tray restore
- close 시 shutdown sync
- `minimizeToTray` local 설정 반영

남은 gap:
- 일부 V2 close/minimize path의 세부 타이밍과 정책은 더 점검 필요
- shell 레벨의 완전한 parity보다는 현재는 핵심 동작 위주로 맞춰져 있음
- tray 메뉴에서 V2의 `위젯` 항목이 없음

의도적 차이:
- widget restore 기능 제거
  - 근거: `v3/apps/frontend/src/routes/+layout.svelte`
  - 제거 결정 주석 기록됨

사용자 승인 차이:
- `Ctrl+Shift+A` 글로벌 단축키 미구현 유지

---

## 3. CarMaker

상태: `동일에 가까움`

구현됨:
- 연결/해제
- telemetry 조회
- monitoring on/off
- watched traffic objects
- raw command 실행
- gas/brake/steer/target speed
- start/stop/pause/resume 관련 UI 흐름

주요 파일:
- `v3/services/python-api/app/services/carmaker.py`
- `v3/services/python-api/app/api/routes/carmaker.py`
- `v3/apps/frontend/src/lib/stores/carmakerStore.svelte.ts`
- `v3/apps/frontend/src/routes/autonomous-driving/vehicle-control/+page.svelte`
- `v3/apps/frontend/src/routes/autonomous-driving/manual-control/+page.svelte`

남은 gap:
- Trigger 실행이 V2처럼 `carmakerStore.pauseSimulation()/resumeSimulation()` 경로를 타지 않음
- 즉 trigger 유발 pause/resume이 UI monitoring 상태/로그에 완전히 반영되지는 않음

정리:
- 단독 CarMaker 제어는 사실상 V2와 거의 동등
- `trigger와 결합된 CarMaker semantics`가 남은 핵심 gap

---

## 4. Chat / Conversations

상태: `부분 동일`

구현됨:
- 채팅 요청
- Claude CLI 호출
- conversation/message SQLite 저장
- conversation list/load/update/delete
- trigger chat event 표시
- command templates prompt 주입

주요 파일:
- `v3/services/python-api/app/services/chat.py`
- `v3/services/python-api/app/services/ai_chat_db.py`
- `v3/services/python-api/app/api/routes/chat.py`
- `v3/services/python-api/app/api/routes/conversations.py`
- `v3/apps/frontend/src/lib/components/ChatView.svelte`
- `v3/apps/frontend/src/lib/components/ChatHistoryView.svelte`

이미 맞춘 parity:
- 기존 conversation은 저장된 `character_id`, `prompt_template_id`, `user_info`를 사용
- 새 conversation / `no_save`는 explicit ids 요구

남은 gap:
- streaming 없음
- action/map/vehicle command 후처리의 세부 semantics 재검증 필요
- Claude subprocess 결과와 에러 처리의 V2 세부 차이는 추가 점검 필요
- V2의 별도 `create_conversation` 명령에 해당하는 독립 API는 없고, 현재는 `/api/chat` 흐름에 사실상 묶여 있음

정리:
- 대화 저장/불러오기 자체는 안정적
- “응답을 받은 뒤 무엇을 어떻게 실행/반영하느냐”가 남은 검증 포인트

---

## 5. AI Settings / Catalog

상태: `동일에 가까움`

구현됨:
- chat settings
- characters CRUD
- prompt templates CRUD
- command templates CRUD
- user-info / final-message settings

주요 파일:
- `v3/services/python-api/app/services/ai_catalog.py`
- `v3/services/python-api/app/services/command_templates.py`
- `v3/services/python-api/app/services/settings.py`
- `v3/apps/frontend/src/routes/ai-settings/**`

이미 맞춘 parity:
- AI catalog 저장소가 SQLite 기반으로 이동
- prompt context도 backend 소유 설정으로 이동

남은 gap:
- V2 세부 편집 UX의 edge case 정도만 남아 있음
- V2에 있던 `get by id` 성격의 catalog API는 일부 빠져 있음
- 기능 단위 parity 관점에서는 우선순위 낮음

---

## 6. Trigger Runtime

상태: `의도적 차이 + parity 보강 필요`

구현됨:
- trigger CRUD
- active/rule-control toggle
- backend monitoring runtime
- cooldown
- rule mode
- LLM mode
- logs
- trigger chat events

주요 파일:
- `v3/services/python-api/app/services/triggers.py`
- `v3/services/python-api/app/api/routes/triggers.py`
- `v3/apps/frontend/src/lib/stores/triggerMonitor.svelte.ts`
- `v3/apps/frontend/src/routes/autonomous-driving/triggers/+page.svelte`

구조적 차이:
- V2는 trigger 정의 CRUD만 backend(Tauri)에 있고, 실제 평가/LLM 실행은 renderer 쪽이 수행
- V3는 trigger runtime 전체를 backend로 이동
- 즉 이 도메인은 단순 parity가 아니라 `책임 이동이 있는 포팅`이다

최근 맞춘 parity:
- clear logs가 backend 원본까지 실제 삭제
- fresh reload 시 과거 trigger chat events replay 방지

남은 핵심 gap:
- trigger 실행 중 CarMaker monitoring pause/resume semantics
  - V2는 frontend carmakerStore 경로를 타서 UI 상태와 로그까지 바뀜
  - V3는 backend가 직접 `SC.TAccel`만 조작
- trigger LLM payload와 settings source의 세부 parity
  - V2는 browser-local 기반이 강했고
  - V3는 backend settings 기준
- event transport가 polling 기반이라 V2의 same-session 즉시 dispatch와 타이밍 차이 존재

주의:
- 일부는 V3 구조상 backend authoritative가 더 낫지만,
- 현재 기준은 “더 낫다”가 아니라 “V2와 동일하냐”이므로 아직 `부분 동일`이다

판정 이유:
- 구조는 의도적으로 달라졌지만
- 사용자 체감 동작은 더 맞춰야 하므로 `완료`로 보지 않는다

---

## 7. App Settings / DB Sync / Backup

상태: `부분 동일`

구현됨:
- app settings 저장
- DB info
- export/import
- sync now
- shutdown sync
- backup restore
- startup sync folder import-if-newer
- Claude workspace 경로 설정 반영

주요 파일:
- `v3/services/python-api/app/services/settings.py`
- `v3/services/python-api/app/api/routes/settings.py`
- `v3/apps/frontend/src/routes/app-settings/+page.svelte`
- `v3/apps/frontend/src/lib/stores/settingsStore.ts`

이미 맞춘 parity:
- `ai_chat.db` 기준 DB 관리 semantics 회귀
- backup 생성/정리/sync shutdown 흐름 회귀
- `minimizeToTray`는 V2처럼 local-only 유지

남은 gap:
- 경로 선택/운영 UX의 세부 예외 흐름 검증
- shell close / tray quit / restore 전 경로 전체 회귀 테스트 필요

---

## 8. Maps CRUD

상태: `부분 동일`

구현됨:
- create/read/update/delete
- get by id
- count
- edit flow
- embed single
- build all embeddings
- embeddings health

주요 파일:
- `v3/services/python-api/app/services/maps.py`
- `v3/services/python-api/app/api/routes/maps.py`
- `v3/apps/frontend/src/routes/map-settings/generator/+page.svelte`
- `v3/apps/frontend/src/routes/map-settings/library/+page.svelte`

최근 맞춘 parity:
- duplicate name 허용
- update의 `null` optional field는 “변경 안 함” 처리
- delete missing id는 success no-op
- build-all 결과 숫자 의미를 V2 쪽으로 조정
- legacy unique schema 자동 마이그레이션

남은 gap:
- update/edit 이후 embedding semantics의 세부 검증
- 프런트 전체 흐름 기준으로 추가 edge case 점검 필요

---

## 9. Maps RAG / Embeddings

상태: `부분 동일`

현재 구현:
- `/api/maps/:id/embed`
- `/api/maps/embeddings/build-all`
- `/api/maps/embeddings/health`
- `/api/maps/search`

주요 파일:
- `v3/services/python-api/app/services/maps.py`
- `MapGenerator/build_all_embeddings.py`
- `MapGenerator/search_maps.py`
- `v3/apps/frontend/src/routes/map-settings/rag-test/+page.svelte`

핵심 차이:
- V2는 OpenAI embeddings + FAISS
- V3는 현재 SQLite FTS 기반 검색
- 따라서 `shape parity`는 높지만 `검색 엔진 parity`는 아직 낮다

프런트-visible parity 조정:
- 임베딩 index가 없으면 먼저 build하라는 에러를 주도록 맞춤
- build 결과 shape는 프런트가 기대하는 형태와 맞춤

남은 본질적 gap:
- 검색 ranking / recall / distance semantics는 V2와 다름
- 즉 `API shape`는 비슷해졌지만 `검색 엔진 자체`는 아직 완전 parity가 아님

정리:
- Maps CRUD보다 RAG가 더 큰 남은 도메인

---

## 10. 의도적 차이

아래는 현재 parity bug로 보지 않기로 한 항목들이다.

| 항목 | 처리 |
|---|---|
| widget restore | 제거 결정, 코드 주석 기록 |
| `Ctrl+Shift+A` restore shortcut | 사용자 요청으로 제외 |
| trigger runtime backend 이동 | V3 구조상 의도적 차이. 다만 사용자 체감 실행 semantics는 계속 V2에 맞춘다 |

---

## 11. 남은 작업 우선순위

### P0
- Trigger pause/resume + CarMaker monitoring semantics parity
- Trigger LLM payload/settings source parity 재검증

### P1
- Maps RAG semantics parity
  - 현재 FTS 기반 구현을 유지할지
  - V2식 embeddings/FAISS semantics를 더 직접 재현할지 결정 필요

### P2
- Chat 후처리 parity 종합 점검
  - action parsing
  - vehicle command execution
  - map action side effects

### P3
- App/Electron shell 운영 edge case 회귀 테스트
  - tray
  - close
  - shutdown sync
  - startup sync

---

## 12. 결론

현재 V3는 `새 앱`이 아니라 `거의 포팅 완료된 V2 Python/Electron판`에 가깝다.

남은 일은 “기능이 있느냐 없느냐”보다:
- trigger가 V2처럼 정확히 움직이는가
- map/RAG가 V2처럼 검색/임베딩되는가
- 종료/동기화가 V2처럼 안전하게 동작하는가

이 세 축의 parity를 닫는 일이다.

즉 지금 단계에서 맞는 전략은:

1. 구조 개선 보류
2. parity gap만 닫기
3. parity 완료 후 Python/Electron 구조 최적화 시작
