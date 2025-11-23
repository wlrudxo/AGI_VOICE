# AI 채팅 시스템 개선 계획

## 현재 상태 분석

### AGI_VOICE_V2 현재 구현
- ✅ 기본 AI 채팅 시스템 (대화 생성/저장/불러오기)
- ✅ Dynamic prompt system (Character + System Message + Commands)
- ✅ Message role 지원 (`user`, `assistant`)
- ✅ Action parser/executor 스텁 (구현 대기 중)
- ⚠️ System message는 `role` 필드로 구분 가능하나 UI/백엔드에서 미활용
- ⚠️ AI 명령어 기반 정보 제공 미구현
- ⚠️ 일회용 메시지 모드 미구현
- ⚠️ AI 명령 파싱 스텁만 존재 (자율주행 도메인 태그 미정의)

### AI_Diet_V2 참조 구현
- ✅ System/User 메시지 분리 (DB 저장 제어)
- ✅ 일회용 메시지 (`role: 'system'` 사용)
- ✅ AI 명령 파싱 완전 구현 (Tag 기반 CRUD)
- ✅ 단순 액션 실행 구조 (응답에서 태그 파싱 → 순차 실행 → 완료)

---

## 구현 계획

### 1. System/User 메시지 시스템

**목표**: 사용자가 일반 메시지와 시스템 메시지를 동시에 보낼 수 있도록 지원

#### Backend 수정 (Rust)

**파일**: `src-tauri/src/commands/ai_chat.rs`

**변경 사항**:
- ✅ 이미 `role` 필드 존재 (line 30)
- ✅ 이미 `system_context` 필드 존재 (line 29)
- ✅ `role == "system"`일 때 DB 저장 스킵 로직 **추가 필요**

**구현 내용** (AI_Diet_V2의 `ai_chat.rs:299-332` 참조):
```rust
// line ~299: Message 저장 로직
if request.role == "user" {
    // User 메시지만 DB에 저장
    let user_msg = message::ActiveModel {
        conversation_id: Set(conversation.id),
        role: Set("user".to_string()),
        content: Set(request.message.clone()),
        created_at: Set(Utc::now().naive_utc()),
        id: NotSet,
    };
    user_msg.insert(&*db).await
        .map_err(|e| format!("Failed to save user message: {}", e))?;
} else {
    println!("⏭️ Skipping user message save (role={})", request.role);
}

// Assistant 응답은 항상 저장
let assistant_msg = message::ActiveModel {
    conversation_id: Set(conversation.id),
    role: Set("assistant".to_string()),
    content: Set(raw_response.clone()),
    created_at: Set(Utc::now().naive_utc()),
    id: NotSet,
};
assistant_msg.insert(&*db).await
    .map_err(|e| format!("Failed to save assistant message: {}", e))?;
```

#### Frontend 수정 (Svelte)

**파일**: `src/lib/components/ChatView.svelte`

**변경 사항**:
1. **System message 필터링** (line ~122)
   - 대화 기록 로드 시 `role === 'system'` 메시지 제외
   - AI_Diet_V2의 `ChatView.svelte:122-159` 참조

```typescript
async function loadConversation(selectedId) {
    // ... existing code
    const parsedMessages = [];
    for (const msg of messagesData) {
        if (msg.role === 'system') continue;  // ✅ System message 제외
        // ... parse assistant/user messages
    }
    messages = parsedMessages;
}
```

2. **Follow-up request에서 `role: 'system'` 사용** (이미 구현됨)
   - 현재 코드에는 READ follow-up 로직이 스텁 상태
   - AI_Diet_V2의 `ChatView.svelte:249-264` 참조

---

### 2. AI 정보 제공 (명령어 기반)

**목표**: AI가 필요한 정보를 태그로 요청하면 프론트엔드에서 실행

**단순화된 아키텍처**:
- LLM이 알아서 판단: 정보 필요 → `<read_map|id:5>` 포함
- 시스템은 응답에서 태그만 파싱하여 순차 실행 (READ든 CUD든 동일)
- **READ 최적화**: 응답에 포함된 모든 READ 태그를 먼저 모아서 한 번에 실행 → 결과를 system message로 일괄 전송 → AI가 받아서 최종 응답 생성
- CUD는 순차 실행 (재요청 없음)

#### Command Templates 활용

**현재 상태**:
- ✅ `command_templates` 테이블 존재
- ✅ 활성화된 템플릿만 AI에게 전송 (`is_active=1`)
- ✅ Prompt builder에서 템플릿 조합 (`src-tauri/src/ai/prompt_builder.rs`)

**추가 필요 사항**:
- 자율주행 도메인용 Command Template 정의
- Executor에서 모든 action 순차 실행

#### Parser 구현 (완전 구현)

**파일**: `src/lib/actions/parser.ts`

**AI_Diet_V2 코드 그대로 적용 가능** (`parser.ts:48-216`):
```typescript
export function parseActions(response: string): Action[] {
    const actions: Action[] = [];
    const tagPattern = /<([^|>]+)(?:\|([^>]+))?>/g;
    let match;

    while ((match = tagPattern.exec(response)) !== null) {
        const actionType = match[1].trim();
        const fieldsStr = match[2]?.trim();
        const fields = parseFields(fieldsStr);
        const action = processAction(actionType, fields);
        if (action) actions.push(action);
    }
    return actions;
}

export function parseWithSegments(response: string): ParsedSegment[] {
    // Text와 action tag를 분리하여 반환
    // AI_Diet_V2 코드 완전 복사 가능
}

function parseFields(fieldsStr?: string): Record<string, string> {
    // "field:value|field:value" 파싱
}
```

#### Executor 구현 (자율주행 도메인 적용)

**파일**: `src/lib/actions/executor.ts`

**구현 내용** (AI_Diet_V2의 `executor.ts` 참조):
```typescript
async function executeRead(type: string, data: Record<string, any>): Promise<string> {
    if (type === 'map') {
        if (data.id) {
            const map: any = await invoke('get_map_by_id', { id: data.id });
            return `[맵 #${map.id}] ${map.name}: ${map.description || '설명 없음'}
카테고리: ${map.category || 'N/A'}, 난이도: ${map.difficulty || 'N/A'}
태그: ${map.tags || '없음'}`;
        } else if (data.category) {
            const maps: any[] = await invoke('get_maps', {
                category: data.category,
                hasEmbedding: null,
                searchQuery: null
            });
            return `📁 ${data.category} 카테고리 맵 (${maps.length}개):
${maps.map((m: any) => `  - [#${m.id}] ${m.name}`).join('\n')}`;
        }
        return '맵 조회를 위해 ID 또는 카테고리를 지정해주세요.';
    }

    if (type === 'dashboard') {
        const count = await invoke('get_map_count');
        return `📊 대시보드 현황:
총 맵 개수: ${count}개`;
    }

    throw new Error(`Unknown read type: ${type}`);
}

async function executeCreate(type: string, data: Record<string, any>): Promise<any> {
    if (type === 'map') {
        return await invoke('create_map', { request: data });
    }
    throw new Error(`Unknown create type: ${type}`);
}

async function executeUpdate(type: string, data: Record<string, any>): Promise<any> {
    if (type === 'map') {
        return await invoke('update_map', { id: data.id, request: data });
    }
    throw new Error(`Unknown update type: ${type}`);
}

async function executeDelete(type: string, data: Record<string, any>): Promise<any> {
    if (type === 'map') {
        return await invoke('delete_map', { id: data.id });
    }
    throw new Error(`Unknown delete type: ${type}`);
}
```

#### ~~Formatter 구현~~ (불필요 - 삭제)

**제거 이유**: 재요청이 없으므로 READ 결과를 system message로 포맷팅할 필요 없음
- READ 결과는 UI에 표시하거나 로그로만 활용

---

### 3. 일회용 메시지 모드

**목표**: 대화 기록은 남지만 AI 전송 시 이전 대화 포함 안 함

#### 구현 방법 1: `role: 'system'` 활용 (간단)

**현재 구조 활용**:
- `role: 'system'`으로 보내면 DB에 저장 안 됨 (구현 필요)
- 이미 follow-up에서 사용 중

**한계**: 대화 기록이 아예 안 남음 (요구사항: 기록은 남되 AI에게 안 보냄)

#### 구현 방법 2: `exclude_history` 플래그 (권장)

**Backend 수정**:

**파일**: `src-tauri/src/commands/ai_chat.rs`

```rust
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChatRequest {
    // ... existing fields
    pub exclude_history: Option<bool>,  // ✅ 추가
}
```

**파일**: `src-tauri/src/ai/prompt_builder.rs`

```rust
pub fn build_full_prompt(
    // ... existing params
    exclude_history: bool,  // ✅ 추가
) -> Result<(String, String), String> {
    // ... existing code

    // Previous messages 섹션
    if !exclude_history && !previous_messages.is_empty() {
        full_message.push_str("<--Previous Exchanges Start-->\n");
        // ... format messages
        full_message.push_str("<--Previous Response End-->\n\n");
    } else {
        full_message.push_str("이번 요청은 이전 대화 기록 없이 처리합니다.\n\n");
    }

    // ... rest of code
}
```

**Frontend 수정**:

**파일**: `src/lib/components/ChatView.svelte`

```typescript
let excludeHistory = $state(false);  // ✅ UI toggle

async function sendMessage() {
    const requestBody = {
        message: userMessage,
        excludeHistory: excludeHistory,  // ✅ 추가
        // ... other fields
    };
    // ... rest of code
}
```

**UI 추가**:
```svelte
<div class="flex items-center gap-2 mb-2">
    <label class="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" bind:checked={excludeHistory} class="toggle-switch" />
        <span class="text-sm text-secondary">일회용 모드 (대화 기록 제외)</span>
    </label>
</div>
```

---

### 4. AI 명령 파싱 - 단순 구현

**목표**: AI 응답에서 태그를 파싱하고 순차 실행 (READ/CUD 구분 없이)

#### Response Processing Flow (단순화)

**파일**: `src/lib/components/ChatView.svelte`

**단순 구조 (READ 일괄 처리)**:
```typescript
async function processResponse(rawResponse) {
    // 1. Parse actions and segments
    const actions = parseActions(rawResponse);
    const segments = parseWithSegments(rawResponse);
    const timestamp = new Date();

    // 2. Display all text segments
    for (const segment of segments) {
        if (segment.type === 'text') {
            messages.push({ role: 'assistant', content: segment.content, timestamp });
        } else if (segment.type === 'action') {
            messages.push({ role: 'action', label: segment.label, timestamp });
        }
    }
    scrollToBottom();

    // 3. 모든 READ 액션 한 번에 실행
    const readActions = actions.filter(a => a.operation === 'read');
    if (readActions.length > 0) {
        try {
            // 병렬 실행하여 모든 READ 결과 수집
            const readResults = await Promise.all(
                readActions.map(action => executeAction(action))
            );

            // 결과를 system message로 포맷
            const systemContext = readResults
                .filter(r => r)
                .map((r, i) => `[${readActions[i].type}] ${r}`)
                .join('\n\n');

            if (systemContext) {
                // AI에게 모든 조회 결과를 한 번에 전달
                const requestBody = {
                    conversationId: conversationId,
                    message: userMessage,  // 원본 사용자 메시지
                    model: claudeModel,
                    userName: getUserName(),
                    systemContext: systemContext,  // 모든 READ 결과
                    role: 'system'  // DB 저장 안 함
                };

                const data = await invoke('chat', { request: requestBody });
                const finalResponse = data.responses[0];

                // 최종 응답 표시
                messages.push({
                    role: 'assistant',
                    content: finalResponse,
                    timestamp: new Date()
                });
                scrollToBottom();

                // 최종 응답에 CUD 태그가 있으면 실행
                const finalActions = parseActions(finalResponse);
                const cudActions = finalActions.filter(a => a.operation !== 'read');
                for (const action of cudActions) {
                    await executeAction(action);
                }
            }
        } catch (error) {
            console.error('READ execution error:', error);
            messages.push({
                role: 'error',
                content: `조회 실패: ${error.message}`,
                timestamp: new Date()
            });
        }
    }

    // 4. CUD 액션 순차 실행 (READ 없는 경우)
    const cudActions = actions.filter(a => a.operation !== 'read');
    let hasDbChange = false;
    for (const action of cudActions) {
        try {
            await executeAction(action);
            hasDbChange = true;
        } catch (error) {
            console.error('Action execution error:', error);
            messages.push({
                role: 'error',
                content: `액션 실행 실패: ${error.message}`,
                timestamp: new Date()
            });
        }
    }

    // 5. Trigger DB refresh if needed
    if (hasDbChange) {
        dbWatcher.triggerRefresh(100);
    }
}

async function sendMessage() {
    const userMessage = inputMessage.trim();
    if (!userMessage || isLoading) return;

    // Add user message to UI
    messages.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date()
    });
    inputMessage = '';
    isLoading = true;
    scrollToBottom();

    try {
        const requestBody = {
            message: userMessage,
            model: claudeModel,
            userName: getUserName(),
            role: 'user'
        };

        // Handle conversation ID
        if (conversationId) {
            requestBody.conversationId = conversationId;
        } else {
            requestBody.characterId = characterId;
            requestBody.promptTemplateId = promptTemplateId;
            requestBody.userInfo = getUserInfo();
            requestBody.finalMessage = getFinalMessage();
            requestBody.title = newConversationTitle;
        }

        // Send chat request
        const data = await invoke('chat', { request: requestBody });
        const rawResponse = data.responses[0];

        if (!conversationId && data.conversationId) {
            conversationId = data.conversationId;
            uiStore.setCurrentConversationId(data.conversationId);
        }

        // Process response (단순 실행, 재요청 없음)
        await processResponse(rawResponse);
    } catch (error) {
        console.error('Chat error:', error);
        messages.push({
            role: 'error',
            content: '오류가 발생했습니다.',
            timestamp: new Date()
        });
    } finally {
        isLoading = false;
    }
}
```

#### Command Template 예시 (자율주행 도메인)

**DB 삽입 예시** (Seed data):
```sql
INSERT INTO command_templates (name, content, is_active, created_at, updated_at) VALUES
('자율주행 맵 관리', '
## 맵 관리 명령어

사용자가 맵 정보를 요청하거나 맵을 생성/수정/삭제하려 할 때 다음 태그를 사용하세요:

### 조회 (READ)
- 특정 맵 조회: `<read_map|id:123>`
- 카테고리별 조회: `<read_map|category:urban>`
- 대시보드 현황: `<read_dashboard>`

### 생성 (CREATE)
- 새 맵 생성: `<map|name:맵이름|description:설명|category:도시|difficulty:medium|tags:테스트,실험>`

### 수정 (UPDATE)
- 맵 정보 수정: `<update_map|id:123|name:새이름|difficulty:hard>`

### 삭제 (DELETE)
- 맵 삭제: `<delete_map|id:123>`

**사용법**:
1. 정보가 필요하면 READ 태그 사용 → 시스템이 모든 READ를 모아서 한 번에 조회 후 결과 전달
2. 조회 결과를 받으면 그 정보를 바탕으로 최종 응답 생성 (CUD 태그 포함 가능)
3. 예시 흐름:
   - User: "맵 3번 확인하고 삭제해줘"
   - AI 1차 응답: `<read_map|id:3>` "조회 중입니다..."
   - System: READ 실행 → "맵 #3: 도시맵 (카테고리: urban)"을 system message로 전달
   - AI 2차 응답: "도시맵을 확인했습니다. 삭제하겠습니다" `<delete_map|id:3>`
   - System: DELETE 실행
', 1, datetime('now'), datetime('now'));
```

---

## 구현 순서

### Phase 1: System Message 분리 (30분)
1. ✅ Backend: `role == "system"` 시 DB 저장 스킵 로직 추가
2. ✅ Frontend: 대화 기록 로드 시 system message 필터링

### Phase 2: Parser/Executor 구현 (45분)
1. ✅ `parser.ts` - AI_Diet_V2 코드 참조 (태그 파싱, 세그먼트 분리)
2. ✅ `executor.ts` - 자율주행 도메인 CRUD 구현
   - `read_map`, `read_dashboard`
   - `map` (create), `update_map`, `delete_map`
3. ❌ `formatter.ts` - 불필요 (재요청 없음)

### Phase 3: Response Processing Flow 구현 (30분)
1. ✅ `ChatView.svelte` - `processResponse()` 단순 구현
   - 태그 파싱 → 세그먼트 표시 → 액션 순차 실행
2. ✅ Action indicator UI 개선

### Phase 4: 일회용 메시지 모드 (30분)
1. ✅ Backend: `exclude_history` 플래그 추가
2. ✅ Prompt builder: 플래그 기반 히스토리 제외 로직
3. ✅ Frontend: UI toggle 추가

### Phase 5: Command Template 정의 (30분)
1. ✅ 자율주행 도메인용 command template 작성
2. ✅ DB seed data 추가
3. ✅ UI에서 활성화/비활성화 테스트

---

## 테스트 시나리오

### 1. System Message 테스트
- [ ] 일반 메시지: DB에 user/assistant 모두 저장됨
- [ ] System 메시지: assistant만 저장됨 (user 저장 안 됨)
- [ ] 대화 기록 로드 시 system 메시지 제외됨

### 2. AI 정보 제공 테스트
- [ ] "맵 목록 보여줘" → AI: `<read_map|category:urban>` → READ 실행 → system message 전달 → AI 최종 응답 "urban 카테고리에 3개 맵이 있습니다..."
- [ ] "맵 ID 5, 7 정보 알려줘" → AI: `<read_map|id:5>` `<read_map|id:7>` → 두 READ 한번에 실행 → system message 전달 → AI 최종 응답

### 3. 일회용 메시지 테스트
- [ ] Toggle ON: 이전 대화 없이 AI 응답 (단, DB에는 저장됨)
- [ ] Toggle OFF: 이전 대화 포함하여 AI 응답

### 4. AI 명령 파싱 테스트
- [ ] CREATE: "도시 맵 만들어줘" → AI: `<map|name:도시맵|category:urban>` → DB 저장
- [ ] UPDATE: "맵 3번 난이도 올려줘" → AI: `<update_map|id:3|difficulty:hard>` → DB 수정
- [ ] DELETE: "맵 7번 삭제" → AI: `<delete_map|id:7>` → DB 삭제
- [ ] 복합 (READ → CUD):
  - "맵 3번 확인하고 삭제해줘"
  - AI 1차: `<read_map|id:3>`
  - System: READ 실행 → system message 전달
  - AI 2차: "도시맵 확인했습니다" `<delete_map|id:3>`
  - System: DELETE 실행

---

## 예상 변경 파일 목록

### Backend (Rust)
- `src-tauri/src/commands/ai_chat.rs` - System message 저장 스킵, exclude_history 파라미터
- `src-tauri/src/ai/prompt_builder.rs` - exclude_history 기반 히스토리 제외

### Frontend (TypeScript/Svelte)
- `src/lib/actions/parser.ts` - ✅ 완전 구현 (AI_Diet_V2 참조)
- `src/lib/actions/executor.ts` - ✅ 자율주행 도메인 CRUD 구현
- ~~`src/lib/actions/formatter.ts`~~ - ❌ 제거 (불필요)
- `src/lib/components/ChatView.svelte` - processResponse (단순화), sendMessage, loadConversation 수정

### Database
- `src-tauri/src/db/seed_data.rs` - Command template 추가

---

## 참조 코드 위치 (AI_Diet_V2)

| 기능 | 파일 경로 | 라인 |
|------|----------|------|
| System message 저장 스킵 | `src-tauri/src/commands/ai_chat.rs` | 299-332 |
| Parser 완전 구현 | `src/lib/actions/parser.ts` | 48-216 |
| Executor READ 구현 | `src/lib/actions/executor.ts` | 79-233 |
| Executor CUD 구현 | `src/lib/actions/executor.ts` | 63-75, 238-373 |
| System message 필터링 | `src/lib/components/ChatView.svelte` | 122-159 |
| Command template 로드 | `src-tauri/src/commands/ai_chat.rs` | 156-161 |

---

## 완료 기준

- [x] 현재 구현 분석 완료
- [x] AI_Diet_V2 참조 코드 분석 완료
- [x] 구현 계획 작성 완료
- [ ] Phase 1-5 모든 기능 구현
- [ ] 모든 테스트 시나리오 통과
- [ ] 자율주행 도메인 Command Template 정의 및 활성화

**예상 총 작업 시간**: 2.5시간 (단순화로 1시간 절약)
