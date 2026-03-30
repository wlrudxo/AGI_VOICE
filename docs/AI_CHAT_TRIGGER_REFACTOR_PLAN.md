# AI Chat / Trigger 문제 정리 및 개선 계획

## 목적

이 문서는 V3의 `AI 채팅`, `트리거`, `액션 실행`, `CarMaker 제어` 경계를 다시 정리하기 위한 기준 문서다.

기준은 다음과 같다.

- 사용자 동작은 유지한다
- V2에서 가져온 기능은 유지하되, 구조 부채는 V3에서 해소한다
- 특히 `트리거 -> LLM -> 액션 실행` 흐름을 단독 책임 구조로 재편한다


## 현재 결론

현재 문제의 핵심은 기능 부족보다 `책임 과밀`과 `중복 구현`이다.

특히:

- `TriggerService`가 너무 많은 책임을 갖고 있다
- `ChatService`와 `TriggerService` 사이에 orchestration이 중복된다
- 프런트에서도 `ChatView`와 `triggerMonitor`가 상태/이벤트/표현을 중복 관리한다
- V2에서부터 있던 구조 부채가 V3의 `HTTP + thread + subprocess + polling` 환경에서 더 크게 드러난다

목표 구조는 다음과 같다.

- `ChatService`: 프롬프트 조립 + Claude 호출 + 선택적 대화 저장
- `ActionService`: LLM 응답 파싱 + 차량 명령 실행 + cancel/reset 지원
- `TriggerRuntime`: 모니터링 + 표현식 평가 + cooldown + queue
- `TriggerExecutor`: trigger 1건 실행 orchestration

즉:

`트리거 런타임`이 발동을 감지하고  
`채팅 기능`으로 입력/응답을 만들고  
`액션 기능`으로 실행한다


## 현재 확인된 문제

### P0. 구조적 과밀

1. `TriggerService`가 상태기계, cooldown, pause/resume, LLM 호출, 액션 실행, 로그, 이벤트 송출을 전부 담당
   - 파일: [triggers.py](/mnt/e/gitproject/agi_voice_v2/v3/services/python-api/app/services/triggers.py)
   - 결과:
     - reset 시 상태 누수
     - cancel 상태 누수
     - cooldown / monitoring / execution 상호 간섭
     - 작은 수정도 회귀로 이어짐

2. `ChatService`와 `TriggerService`가 LLM orchestration을 중복 구현
   - 일반 채팅은 [chat.py](/mnt/e/gitproject/agi_voice_v2/v3/services/python-api/app/services/chat.py)
   - 트리거는 [triggers.py](/mnt/e/gitproject/agi_voice_v2/v3/services/python-api/app/services/triggers.py) 에서 다시 프롬프트/로그/이벤트 처리
   - 결과:
     - `Request Input`, `Trigger AI Input` 같은 중복 로그
     - 일반 채팅과 트리거 채팅이 같은 LLM 호출인데도 경로가 다름

3. `ChatView.svelte` 과부하
   - 파일: [ChatView.svelte](/mnt/e/gitproject/agi_voice_v2/v3/apps/frontend/src/lib/components/ChatView.svelte)
   - 현재 책임:
     - 설정 로드
     - 대화 선택/로드
     - 메시지 렌더링
     - trigger 이벤트 반영
     - 액션/명령 파싱 결과 렌더링
   - 결과:
     - UI 변경과 상태 변경이 강결합
     - 로그 표현 요구사항 수정이 어려움


### P0. 중복 구현

1. 프런트 표현식 평가기 데드코드
   - `expressionEvaluator.ts`
   - 실제 trigger 판정은 backend [triggers.py](/mnt/e/gitproject/agi_voice_v2/v3/services/python-api/app/services/triggers.py) 에서 수행

2. 프런트 커맨드 파싱 중복
   - `vehicleCommandParser.ts`
   - `vehicleCommandExecutor.ts`
   - 동일/유사 regex 규칙이 분산

3. Trigger 타입 정의 중복
   - [triggerMonitor.svelte.ts](/mnt/e/gitproject/agi_voice_v2/v3/apps/frontend/src/lib/stores/triggerMonitor.svelte.ts)
   - [triggers/+page.svelte](/mnt/e/gitproject/agi_voice_v2/v3/apps/frontend/src/routes/autonomous-driving/triggers/+page.svelte)
   - backend [schemas/triggers.py](/mnt/e/gitproject/agi_voice_v2/v3/services/python-api/app/schemas/triggers.py)

4. 프런트 이벤트 기반 통신 중복
   - `selectConversation`
   - `chatSettingsUpdated`
   - `triggerChatMessage`
   - `conversationCreated`
   - store 대신 window custom event 남용

5. 프런트 액션 파싱/실행 책임도 분산
   - `parser.ts` + `executor.ts` : READ/CUD 액션
   - `vehicleCommandParser.ts` + `vehicleCommandExecutor.ts` : 차량 제어 액션
   - 동일한 "LLM 출력 해석 -> 실행" 문제를 두 갈래로 다룸


### P0. 상태 관리 문제

1. `monitoring` 상태가 프런트와 백엔드에 중복 존재
   - CarMaker monitoring
   - Trigger monitoring
   - frontend local mirrored state

2. 3중 polling 구조
   - `dbWatcher`
   - `carmakerStore`
   - `triggerMonitor`
   - 결과:
     - 상태 동기화 지연
     - 로그/이벤트/상태가 따로 놀기 쉬움

3. trigger 실행 정책이 명확한 런타임 모델 없이 점진 patch로 누적
   - `_is_executing`
   - `_cooldowns`
   - `_blocked_until`
   - `_cancel_event`
   - reset-control
   - 결과:
     - 동시실행 금지 / 큐잉 가능 요구를 자연스럽게 표현하지 못함


### P1. 설계 부채

1. `reset-control`이 CarMaker + Trigger 양쪽을 직접 묶음
   - 파일: [carmaker.py](/mnt/e/gitproject/agi_voice_v2/v3/services/python-api/app/api/routes/carmaker.py)
   - 현재는 실용적이지만 장기적으로는 orchestration 계층으로 이동해야 함

2. 로그 체계가 불명확
   - backend terminal logs
   - trigger logs
   - chat UI live event
   - conversation persistence
   - 같은 데이터를 4경로로 다루는 중

3. timestamp / timezone / localStorage prefix 불일치
   - 즉시 blocker는 아니지만 정리 필요

4. 로그 체계가 4갈래로 분산
   - backend terminal logs
   - trigger log panel
   - chat UI live event
   - conversation persistence
   - 같은 LLM 입출력이 경로마다 다르게 표현됨


## V2에서 이어진 문제

다음은 V3만의 문제라기보다, V2에서 이미 있던 구조 부채다.

- trigger 평가/실행이 한 모듈에 과도하게 집중됨
- 일반 채팅 / no-save 채팅 / trigger 채팅이 공통 유스케이스로 추상화되지 않음
- 액션 파싱/실행 로직이 한 군데로 수렴되지 않음
- 프런트가 window 이벤트로 상태를 많이 전달함

즉 현재 문제는:

- `V3가 이상해서 새로 생긴 문제`
가 아니라
- `V2의 설계 부채가 V3에서 더 크게 증폭된 문제`
로 보는 것이 맞다


## 목표 아키텍처

### 1. ChatService

책임:

- 시스템 메시지 선택
- 명령어 템플릿 결합
- history 결합
- Claude 호출
- 응답 반환
- 선택적으로 conversation 저장

제안 API 예시:

```python
chat_service.generate_response(request: ChatRequest) -> ChatResponse
chat_service.generate_ephemeral(request: ChatRequest) -> ChatResponse
```

핵심:

- 일반 채팅
- trigger용 no-save 채팅
- 나중에 loop 개선 시 trigger 결과를 conversation에 append

를 동일 서비스의 옵션 차이로 처리


### 2. ActionService

책임:

- LLM 응답에서 제어 명령 파싱
- 차량 제어 명령 실행
- wait / wait_until 처리
- cancel 지원
- reset 지원

제안 API 예시:

```python
action_service.parse(text: str) -> ActionPlan
action_service.execute(plan: ActionPlan, cancel_token: CancelToken) -> ActionResult
action_service.reset() -> ResetResult
```

핵심:

- 지금 `triggers.py`에 있는 command sequence 로직을 이동
- 수동 실행 / trigger 실행 / 후속 loop 모두 재사용


### 3. TriggerRuntime

책임:

- telemetry polling
- expression 평가
- cooldown
- dedupe
- queue
- worker 1개 유지

정책:

- 동시 실행 금지
- 큐잉 가능
- 같은 trigger 중복 enqueue 정책은 configurable

제안 구조:

```python
enqueue(trigger_activation)
worker_loop()
```


### 4. TriggerExecutor

책임:

- trigger 1건 실행 orchestration
- snapshot 생성
- ChatService 호출
- ActionService 호출
- pause/resume 제어
- 실행 결과 로그/이벤트 생성

즉 `TriggerService`의 실제 실행 유스케이스를 분리한다


## 구현 원칙

1. 트리거는 orchestration만 한다
2. LLM 호출은 ChatService 단일 경로로 통일한다
3. 액션 파싱/실행은 ActionService 단일 경로로 통일한다
4. reset은 Action/Runtime 계층이 책임지게 하고, API route는 호출만 한다
5. UI는 live event와 persistence를 섞어 다루지 않는다


## 단계별 개선 계획

### Phase 0. 정리 작업

- 프런트 데드코드 제거
  - `expressionEvaluator.ts`
  - `triggerEvaluator.ts` 미사용 export
  - `formatter.ts` 미사용 포맷터
- 추가 데드코드 제거
  - `vehicleCommandExecutor.ts` 의 `executeRuleCommands()`
  - `TriggerService` 별칭 메서드
    - `get_all()`
    - `get_by_id()`
    - `create()`
    - `update()`
    - `delete()`
    - `toggle_active()`
  - 미연동 테스트 정리
    - `vehicleCommandParser.test.ts`
- Trigger 타입 정의 단일화
- vehicle command parsing 로직 단일화

산출물:

- 중복/미사용 코드 제거
- 타입/파서 단일 소스 정리


### Phase 1. ActionService 분리

대상:

- [triggers.py](/mnt/e/gitproject/agi_voice_v2/v3/services/python-api/app/services/triggers.py)
  - `_parse_command_sequence`
  - `_execute_command_sequence`
  - `_execute_vehicle_command`
  - `_execute_wait_until`
- 프런트 액션 실행 경계 재정의
  - `parser.ts`
  - `executor.ts`
  - `vehicleCommandParser.ts`
  - `vehicleCommandExecutor.ts`

목표:

- trigger 외부에서도 재사용 가능한 액션 실행기 구성
- `reset-control`도 Action 계층 책임으로 이동

방향:

- 백엔드:
  - `ActionService.parse()`
  - `ActionService.execute()`
  - `ActionService.reset()`
- 프런트:
  - UI는 "실행 가능한 액션을 표시/요청"하는 역할만 담당
  - 실제 차량 제어 실행은 장기적으로 backend ActionService로 수렴
  - 단기적으로는 기존 프런트 parser/executor를 유지하되, 단일 parser 모듈 기준으로 정리


### Phase 2. TriggerExecutor 분리

대상:

- trigger 1건 실행 플로우
  - pause
  - monitoring pause/resume
  - LLM 요청
  - action 실행
  - 예외/취소 처리

목표:

- `TriggerService`에서 실제 실행 유스케이스 제거
- `reset-control`의 강결합을 이 단계에서 해소

포함 항목:

- pause/resume orchestration
- LLM 요청
- ActionService 호출
- cancel token 연결
- reset 시:
  - TriggerRuntime stop
  - ActionService reset
  - CarMaker monitoring state 복구


### Phase 3. TriggerRuntime queue 도입

목표:

- 동시 실행 금지
- 큐잉 가능
- reset/cancel 정책 명확화

구현 항목:

- activation queue
- worker loop
- dedupe 정책
- cooldown을 runtime policy로 이동
- 실행 중에는 신규 활성화를 queue로 적재
- 같은 trigger 중복 적재 정책 명시
  - 기본안: `trigger_id` 기준 dedupe


### Phase 4. ChatService 정리

목표:

- 일반 채팅과 trigger 채팅의 중복 제거
- 로그 포맷 정리
- prompt 조립 책임 정리
- trigger용 ephemeral 채팅과 일반 저장 채팅을 옵션 차이로 통합

로그 정리 원칙:

- backend terminal:
  - 디버그 모드에서만 상세 LLM 입출력
- trigger log panel:
  - 실행 단계/상태 전이 중심
- chat UI:
  - 사용자에게 보여줄 live message만
- conversation persistence:
  - 저장 정책이 있는 경우에만 append

후속 옵션:

- trigger 결과를 대화 기록에 append 가능하게 설계


### Phase 5. 프런트 정리

대상:

- [ChatView.svelte](/mnt/e/gitproject/agi_voice_v2/v3/apps/frontend/src/lib/components/ChatView.svelte)
- [triggerMonitor.svelte.ts](/mnt/e/gitproject/agi_voice_v2/v3/apps/frontend/src/lib/stores/triggerMonitor.svelte.ts)

목표:

- ChatView 분리 단위 명확화
  - conversation state / loading
  - action parsing / execution orchestration
  - message renderer
  - trigger live event adapter
- window custom event 축소
- store 중심 통신으로 정리

세부 분리안:

- `useConversationState`
  - 설정 로드
  - 대화 선택/로드
  - 전송 상태
- `useChatActions`
  - assistant 응답 후 액션 파싱/실행
- `ChatMessageList`
  - 렌더링 전용
- `TriggerChatAdapter`
  - trigger live event -> chat UI 반영


## 우선순위

### 즉시

1. 데드코드 제거
2. Trigger 타입 단일화
3. 커맨드 파싱 단일화

### 단기

4. ActionService 분리
5. TriggerExecutor 분리
6. ChatView 분리

### 중기

7. TriggerRuntime queue 도입
8. live event / persistence 경계 정리
9. polling 구조 개선

polling 개선 범위:

- 단기:
  - 다중 polling endpoint를 하나의 runtime/status endpoint로 통합 검토
- 중기:
  - trigger logs / trigger events는 SSE 우선 검토
  - 양방향 필요성이 생길 때만 WebSocket 고려


## 보류 항목

다음은 지금 당장 구조개선의 1순위는 아니다.

- WebSocket 전환
- timestamp / timezone 통일
- localStorage prefix 정리
- Rust/V2 쪽 historical cleanup

이 항목들은 현재 구조 분리 이후에 처리하는 편이 안전하다.


## 최종 방향

현재 V3의 AI 채팅/트리거 문제는 개별 버그를 계속 패치해서 끝날 성격이 아니다.

정답은:

- 기능을 `단독 책임 서비스`로 나누고
- 트리거는 그 서비스들을 `조합하는 런타임`으로 축소하는 것

이다.

즉 앞으로의 구현 방향은:

`ChatService`
→ `ActionService`
→ `TriggerExecutor`
→ `TriggerRuntime`

순으로 재구성하는 것이 맞다.
