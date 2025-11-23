# AI Chat System 구현 계획 (정리본)

AI_Diet v2에서 검증된 플로우와 태그 형식을 그대로 우선 적용하고, 겹치는 내용을 제거한 압축 버전입니다.

## 방향성
- 태그 형식: `<action_entity|field:value|field:value>` (AI_Diet v2 동일).
- 플로우: 응답 파싱 → READ 실행 후 system message 재전송 → CUD 실행 → DB 갱신.
- 목표: 최소 변경으로 동작 일원화, 유지보수성 확보.

## 현재 상태 요약
- ✅ Conversation CRUD, 동적 프롬프트 조립(캐릭터/템플릿/명령어), READ→재전송→CUD 2-pass 골격, DB auto-refresh.
- ⚠️ Parser/Executor/Formatter, ChatView 통합은 stub 상태.

## 구현 우선순위
1) **명령 파싱/실행(AI_Diet v2 이식)**  
   - `src/lib/actions/parser.ts`: 태그 파싱/세그먼트 분리 구현.  
   - `src/lib/actions/executor.ts`: READ/CUD 실행 로직(자연어 포맷 반환) 구현.  
   - `src/lib/actions/formatter.ts`: READ/CUD 포맷터.  
   - `src/lib/components/ChatView.svelte`: `processResponse` 통합(세그먼트 표시 → READ follow-up → CUD → DB 갱신).

2) **System/User 분리 & 일회용 모드**  
   - `src-tauri/src/commands/ai_chat.rs`: `role: 'system'` DB 미저장, `exclude_history` 지원.  
   - `ChatView.svelte`: message type 토글, exclude history 토글, 전송 페이로드 포함.

3) **자동 정보 제공([INFO:...] → system 재전송)**  
   - `ChatView.svelte`: `[INFO:cmd]` 감지, handler(AUTO_INFO_COMMANDS) 실행 후 system message 자동 전송.

## 태그 형식 (AI_Diet v2)
```
<read_conversation|id:123>
<conversation|characterId:1|promptTemplateId:2|title:새 대화>        # create
<update_conversation|id:123|title:제목 수정>
<delete_conversation|id:456>
```
- 필드 값에 콜론 포함 시 `split` 후 재결합(로그/URL 안전).
- 새 엔티티 추가 시 action 엔티티명만 확장.

## 동작 흐름 (processResponse)
1. 태그 파싱 → 텍스트/액션 세그먼트 화면 표시.  
2. READ 액션 병렬 실행 → 자연어 컨텍스트 포맷 → `role: 'system'`으로 재전송 → 재귀 처리.  
3. CUD 액션 순차 실행 → 요약 메시지 표시 → DB 변경 플래그 세팅.  
4. DB 변경 시 watcher 갱신 호출.  
5. `[INFO:...]` 발견 시 우선 처리: 정보 수집 → system follow-up → 재귀.

## 파일별 핵심 구현 메모
- `parser.ts`: `parseActions`, `parseWithSegments`, `parseFields`, `parseValue`, `getActionLabel`, `removeActionTags`.
- `executor.ts`: `executeReadActions`(병렬), `executeCudActions`(순차), 엔티티별 READ/CUD 함수, 친절한 자연어 에러 메시지.
- `formatter.ts`: READ 결과 조합, CUD 성공/실패 요약.
- `ChatView.svelte`: `processResponse` 완성, message type/exclude history 토글, system 메시지 UI 구분.
- `ai_chat.rs`: system role 미저장, `exclude_history` 시 이전 메시지 로드 생략.

## 테스트 시나리오 (핵심만)
- 태그 파싱: `<read_conversation>`, `<update_map|id:1|name:X>` 등 정상 분리.  
- READ→재전송: READ 결과가 system 메시지로 다시 전달되고 후속 응답 수신.  
- CUD: 생성/수정/삭제 성공 시 요약 표시, 실패 시 자연어 에러.  
- System/User: system 전송 시 DB 미저장, user 전송 시 저장.  
- 일회용: `exclude_history=true`일 때 이전 대화 미포함.  
- INFO 명령어: `[INFO:user_info]`, `[INFO:current_time]` 등 자동 재전송.

## 참고
- AI_Diet v2 코드 베이스: `C:\Users\kyoungtj\GitProject\AI_Diet_V2\src\lib\actions\` 및 `ChatView.svelte` 구현 그대로 참조.***
