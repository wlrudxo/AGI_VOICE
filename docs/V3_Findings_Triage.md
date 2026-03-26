# V3 Findings Triage

기준일: 2026-03-26

목적:
- CLAUDE가 제시한 parity audit findings를 그대로 채택하지 않고, 실제 코드 기준으로 `유효 / 보류 / 기각`을 구분한다.
- 이후 수정 우선순위를 정하는 기준 문서로 사용한다.

분류 기준:
- `유효`: 실제 parity bug 또는 사용자-visible 차이로 판단
- `보류`: 가능성은 있으나 재현/환경 검증 필요
- `기각`: 코드 근거상 성립하지 않거나 이미 의도적으로 제외된 항목

---

## 1. 유효

### F-A1. Trigger resume duration mismatch

상태: `유효`, `즉시 수정`

내용:
- V2 resume는 `DVAWrite SC.TAccel 1.0 30000 Abs`
- V3 trigger runtime은 `DVAWrite SC.TAccel 1.0 1000 Abs`

근거:
- V2: `src/lib/stores/carmakerStore.svelte.ts`
- V3: `v3/services/python-api/app/services/triggers.py`

영향:
- trigger 실행 후 시뮬레이션 정상 속도 유지 시간이 V2보다 짧다.

처리:
- 수정 진행

### F-A2. Trigger event delivery delay

상태: `유효`, `단기 보류`

내용:
- V2는 trigger chat event를 즉시 browser event로 dispatch
- V3는 backend queue -> 500ms polling -> dispatch

영향:
- trigger 발동/LLM 응답이 채팅 UI에 최대 500ms 늦게 보일 수 있음

메모:
- 구조적으로 backend runtime 이동의 부산물
- parity gap은 맞지만, 기능 실패보다 UX 차이에 가까움

### F-A3. Trigger settings source moved from localStorage to backend settings

상태: `유효`, `의도적 차이`

내용:
- V2는 renderer localStorage 기준
- V3는 backend `settings.json` 기준

영향:
- V2 사용자가 V3로 올 때 trigger AI 설정이 자동 이관되지 않음
- 다중 창/리로드 일관성은 오히려 개선됨

메모:
- parity bug보다는 migration gap

### F-A4. Conversation history timestamps passed to Claude differ

상태: `해결`

내용:
- V2는 prompt history에 KST 포맷 문자열 사용
- V3는 DB raw UTC timestamp 사용

근거:
- V2: `src-tauri/src/commands/ai_chat.rs`
- V3: `v3/services/python-api/app/services/chat.py`

영향:
- Claude가 시간 맥락을 읽을 때 9시간 차이가 생길 수 있음

### F-A5. Backend URL fallback defaults to `8010`

상태: `해결`

내용:
- Electron 경유 실행은 preload가 backend URL을 주입하므로 문제 없음
- 하지만 브라우저 단독 개발 시 fallback이 `8010`에 고정

근거:
- `v3/apps/frontend/src/lib/backend.ts`

영향:
- Electron 없이 프런트만 띄우는 개발자 흐름에서 오연결 가능

---

## 2. 보류

### F-B1. `asyncio.run()` in trigger daemon thread

상태: `보류`

CLAUDE 주장:
- FastAPI event loop과 nested되어 `RuntimeError` 가능

현재 판단:
- `asyncio.run()`은 같은 스레드의 기존 event loop와 충돌하는 것이지,
  daemon monitoring thread에서 새 event loop를 만드는 것 자체는 가능하다.
- 즉 “즉시 버그”로 단정할 수는 없음.

필요한 것:
- 실제 trigger LLM mode runtime에서 재현 테스트
- Claude subprocess와 thread-local event loop 조합 검증

현재 확인:
- 현 개발 환경에서 `threading.Thread` 내부 `asyncio.run()` + `asyncio.create_subprocess_exec()` 최소 재현은 성공했다.
- 따라서 이 항목은 `확정 버그`가 아니라 `플랫폼별 검증 필요`로 유지한다.
- 특히 Windows/Electron 배포 환경에서만 추가 확인이 필요하다.

### F-B2. Cooldown semantics on monitoring restart

상태: `보류`

내용:
- V2는 `setTimeout`, V3는 `_cooldowns` dict
- monitoring restart 시 재발동 타이밍이 완전히 같은지 추가 검증 필요

영향:
- edge case 성격

### F-B3. Timestamp storage format difference

상태: `보류`

내용:
- V2는 `YYYY-MM-DD HH:MM:SS`
- V3는 ISO 8601 UTC string

영향:
- SQLite `datetime()` 정렬은 대체로 둘 다 처리 가능
- 실제 import/mixed dataset에서만 문제가 되는지 검증 필요

---

## 3. 기각

### F-C1. Maps `name UNIQUE` parity claim

상태: `기각`

CLAUDE 주장:
- V2 maps table은 `name UNIQUE`

실제:
- V2 schema는 `name TEXT NOT NULL`
- UNIQUE 없음

근거:
- `src-tauri/src/db/map_db.rs`

결론:
- V3에서 UNIQUE 제거는 parity 방향이 맞고, 해당 finding은 잘못된 전제에 기반함

### F-C2. `no_save` behavior mismatch

상태: `기각`

내용:
- CLAUDE도 최종적으로 실질 차이 없다고 재분류
- 현재 수정 우선순위 아님

### F-C3. `create_conversation` payload mismatch

상태: `기각 또는 해소`

내용:
- 독립 create endpoint는 이미 V3에 추가함
- frontend 기본 흐름은 원래도 `/chat` 중심이라 사용자-visible bug는 아님

### F-C4. `Ctrl+Shift+A` missing

상태: `기각`

이유:
- 사용자 승인으로 제외된 항목

---

## 4. 다음 처리 순서

### P0
- Trigger resume duration mismatch 수정 반영 확인

### P1
- Trigger LLM mode 실제 runtime 검증
- Trigger event delay를 polling에서 줄일지, parity 허용 차이로 둘지 결정

### P2
- cooldown restart edge case 검증

---

## 5. 결론

CLAUDE findings 중 일부는 유효하지만, 그대로 전부 채택하면 안 된다.

현재 기준:
- 바로 고칠 가치가 높은 것은 `trigger resume duration`
- 실제 재현 후 판단해야 하는 것은 `asyncio.run`, `cooldown`, `timestamp mixed-format`
- 틀린 finding은 `maps UNIQUE`였다

즉 다음 작업은:
1. 명백한 parity bug부터 수정
2. 남은 항목은 재현 기반으로 판단
