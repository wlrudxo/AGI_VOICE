# AI Chat System 구현 계획

## 목차
1. [System/User 메시지 시스템](#1-systemuser-메시지-시스템)
2. [AI 정보 제공 (명령어 기반)](#2-ai-정보-제공-명령어-기반-자동-system-메시지)
3. [일회용 메시지 모드](#3-일회용-메시지-모드-대화기록-포함-안-함)
4. [AI 명령 파싱 시스템](#4-ai-명령-파싱-시스템-현재-placeholder-구현)
5. [구현 우선순위](#구현-우선순위)
6. [예상 파일 변경 목록](#예상-파일-변경-목록)

---

## 현재 시스템 분석 요약

### 메시지 플로우
1. **Frontend → Backend**: `ChatView.svelte`에서 `invoke('chat', { request })` 호출
2. **Backend 처리**:
   - Conversation 생성/로드
   - Character, Prompt Template, Command Templates 로드
   - CLAUDE.md 파일 생성 (System Message + Character + User Info)
   - Full User Message 조합 (Commands + History + Input + Final Message)
   - Claude CLI 실행
3. **Backend → Frontend**: Raw response 반환
4. **Frontend 처리**:
   - Response 파싱 (현재는 stub)
   - READ actions 실행 → 결과를 system message로 재전송
   - CUD actions 실행
   - DB 변경 감지 및 자동 새로고침

### 데이터베이스 구조
- **ai_chat.db**: Generic AI conversation system
  - `prompt_templates`: System messages
  - `characters`: Character prompts
  - `command_templates`: Command definitions (활성화/비활성화 가능)
  - `conversations`: Chat sessions
  - `messages`: Chat history (role: "user" | "assistant" | "system")
- **sumo_maps.db**: Autonomous driving map data

### 현재 구현 상태
- ✅ 완전한 conversation CRUD 시스템
- ✅ Dynamic prompt assembly (templates, characters, commands)
- ✅ 2-pass response processing (READ → 재전송 → CUD)
- ✅ Database auto-refresh (2s polling)
- ⚠️ Parser/Executor는 placeholder (stub 구현)

---

## 1. System/User 메시지 시스템

### 목표
User와 System 메시지를 구분하여 처리:
- **User Message**: 대화기록에 저장됨
- **System Message**: 대화기록에 저장 안 됨 (AI에게 임시 전달만)

### 현재 상태
- ✅ `messages` 테이블에 `role` 필드 있음 (`"user"` | `"assistant"` | `"system"`)
- ✅ Backend에서 system role 지원 (`ChatRequest.role` 필드)
- ✅ READ action 후속 요청에서 `role: 'system'` 사용 중
- ❌ System 메시지 DB 저장 방지 로직 없음 (현재는 모두 저장됨)

### 구현 변경사항

#### Backend (Rust)
**파일**: `src-tauri/src/commands/ai_chat.rs`

**위치**: Line 302-350 (Save Messages 부분)

```rust
// 현재 코드:
if request.role == "user" {
    let user_message = message::ActiveModel {
        conversation_id: Set(conversation.id),
        role: Set("user".to_string()),
        content: Set(request.message.clone()),
        created_at: Set(now.clone()),
    };
    user_message.insert(&**db).await.map_err(|e| e.to_string())?;
}

// 변경 후:
// System role 메시지는 저장하지 않음 (AI에게만 전달)
if request.role == "user" {
    let user_message = message::ActiveModel {
        conversation_id: Set(conversation.id),
        role: Set("user".to_string()),
        content: Set(request.message.clone()),
        created_at: Set(now.clone()),
    };
    user_message.insert(&**db).await.map_err(|e| e.to_string())?;
}
// system role인 경우: 저장하지 않고 AI에게만 전달
// (아무 작업도 하지 않음)
```

#### Frontend (Svelte)
**파일**: `src/lib/components/ChatView.svelte`

**변경 1**: State 추가
```typescript
let messageType = $state<'user' | 'system'>('user');  // 메시지 타입 선택
```

**변경 2**: UI에 Message Type Toggle 추가
```svelte
<!-- Message Type Toggle (입력창 위에 배치) -->
<div class="message-type-toggle mb-4">
  <label class="inline-flex items-center mr-4">
    <input
      type="radio"
      bind:group={messageType}
      value="user"
      class="mr-2"
    />
    <span class="text-sm">User Message (대화기록 저장)</span>
  </label>
  <label class="inline-flex items-center">
    <input
      type="radio"
      bind:group={messageType}
      value="system"
      class="mr-2"
    />
    <span class="text-sm">System Message (임시 전달만)</span>
  </label>
</div>
```

**변경 3**: `sendMessage()` 함수 수정
```typescript
async function sendMessage() {
    if (!inputMessage.trim()) return;
    if (!characterId || !promptTemplateId) {
        messages = [...messages, {
            role: 'error',
            content: 'Character와 Prompt Template을 선택해주세요.',
            timestamp: new Date().toLocaleString('ko-KR')
        }];
        return;
    }

    isLoading = true;

    try {
        // User info 로드
        const userInfo = localStorage.getItem('agi_voice_user_info') || '';
        const userName = localStorage.getItem('agi_voice_user_name') || 'User';
        const finalMessage = localStorage.getItem('agi_voice_final_message') || '';

        const requestBody = {
            conversationId,
            characterId,
            promptTemplateId,
            userInfo,
            userName,
            finalMessage,
            message: inputMessage,
            model: "sonnet",
            role: messageType  // ✅ "user" 또는 "system"
        };

        // System 메시지는 화면에만 표시 (DB 저장 안 됨)
        if (messageType === 'system') {
            messages = [...messages, {
                role: 'system',
                content: inputMessage,
                timestamp: new Date().toLocaleString('ko-KR'),
                isTemporary: true  // 임시 메시지 표시용
            }];
        } else {
            // User 메시지는 일반적으로 표시
            messages = [...messages, {
                role: 'user',
                content: inputMessage,
                timestamp: new Date().toLocaleString('ko-KR')
            }];
        }

        inputMessage = '';

        const data = await invoke('chat', { request: requestBody });

        // ... (기존 로직 계속)
```

**변경 4**: 메시지 표시 UI 수정 (System 메시지 구분)
```svelte
{#each messages as message}
    {#if message.role === 'user'}
        <div class="flex justify-end mb-4">
            <div class="bg-primary text-white rounded-lg px-4 py-2 max-w-[70%]">
                <div class="text-sm">{message.content}</div>
                <div class="text-xs opacity-70 mt-1">{message.timestamp}</div>
            </div>
        </div>
    {:else if message.role === 'system'}
        <!-- ✅ System 메시지 표시 (회색 배경, 이탤릭) -->
        <div class="flex justify-end mb-4">
            <div class="bg-gray-400 text-white rounded-lg px-4 py-2 max-w-[70%] italic">
                <div class="text-xs opacity-70 mb-1">
                    🔒 System Message (임시)
                </div>
                <div class="text-sm">{message.content}</div>
                <div class="text-xs opacity-70 mt-1">{message.timestamp}</div>
            </div>
        </div>
    {:else if message.role === 'assistant'}
        <!-- 기존 assistant 메시지 표시 -->
```

---

## 2. AI 정보 제공 (명령어 기반 자동 System 메시지)

### 목표
AI가 특정 명령어를 말하면 → 해당 정보를 자동으로 system message로 전송

### 예시 시나리오
1. **User**: "현재 설정된 캐릭터가 뭐야?"
2. **AI**: "사용자 정보를 확인하겠습니다. [INFO:user_info]"
3. **System** (자동): `userInfo` 데이터를 system message로 전송
4. **AI**: "현재 사용자 정보는 다음과 같습니다: [받은 정보 기반 자연어 응답]"

### 명령어 태그 형식
```
AI 응답: "사용자 정보가 필요합니다. [INFO:user_info]"
→ Frontend 감지 → userInfo 자동 전송 → AI 재응답

지원 명령어:
- [INFO:user_info] → localStorage의 user_info 전송
- [INFO:current_time] → 현재 시간 전송
- [INFO:conversation_count] → 총 대화 개수
- [INFO:active_commands] → 활성화된 command templates 목록
```

### 구현 방식

#### Frontend (Svelte)
**파일**: `src/lib/components/ChatView.svelte`

**추가 1**: 명령어 핸들러 정의
```typescript
// 명령어 정의 (확장 가능한 구조)
const AUTO_INFO_COMMANDS: Record<string, () => string | Promise<string>> = {
    'user_info': () => localStorage.getItem('agi_voice_user_info') || '사용자 정보 없음',

    'current_time': () => {
        const now = new Date();
        return now.toLocaleString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            weekday: 'long'
        });
    },

    'conversation_count': async () => {
        const convs = await invoke('get_conversations');
        return `총 대화 ${convs.length}개`;
    },

    'active_commands': async () => {
        const cmds = await invoke('get_command_templates', { isActive: 1 });
        return `활성 명령어: ${cmds.map(c => c.name).join(', ')}`;
    },

    'character_info': async () => {
        if (!characterId) return '캐릭터 선택 안 됨';
        const char = await invoke('get_character_by_id', { id: characterId });
        return `현재 캐릭터: ${char.name}`;
    },

    'prompt_template_info': async () => {
        if (!promptTemplateId) return 'Prompt Template 선택 안 됨';
        const template = await invoke('get_prompt_template_by_id', { id: promptTemplateId });
        return `현재 System Message: ${template.name}`;
    }
};
```

**추가 2**: 명령어 감지 함수
```typescript
// AI 응답에서 명령어 패턴 감지
function detectInfoCommands(response: string): string[] {
    const pattern = /\[INFO:(\w+)\]/g;  // [INFO:명령어] 형식
    const matches = [...response.matchAll(pattern)];
    return matches.map(m => m[1]);
}
```

**추가 3**: `processResponse()` 함수 수정
```typescript
async function processResponse(rawResponse: string, userMessage: string, hasDbChange = false) {
    // ✅ 0단계: 명령어 감지 및 자동 system message 전송
    const detectedCommands = detectInfoCommands(rawResponse);

    if (detectedCommands.length > 0) {
        console.log('Detected info commands:', detectedCommands);

        // 명령어에 해당하는 정보 수집
        const infoResults = await Promise.all(
            detectedCommands.map(async cmd => {
                const handler = AUTO_INFO_COMMANDS[cmd];
                if (!handler) {
                    console.warn(`Unknown info command: ${cmd}`);
                    return `[${cmd}]: 지원하지 않는 명령어입니다.`;
                }
                try {
                    const result = await handler();
                    return `[${cmd}]:\n${result}`;
                } catch (error) {
                    console.error(`Error executing info command ${cmd}:`, error);
                    return `[${cmd}]: 정보 조회 실패`;
                }
            })
        );

        const systemContext = infoResults.join('\n\n');

        console.log('Sending auto-info as system message:', systemContext);

        // 화면에 system message 표시
        messages = [...messages, {
            role: 'system',
            content: `[자동 정보 제공]\n${systemContext}`,
            timestamp: new Date().toLocaleString('ko-KR'),
            isTemporary: true
        }];

        // 자동으로 system message로 재전송
        const followUpRequest = {
            conversationId,
            characterId,
            promptTemplateId,
            userInfo: localStorage.getItem('agi_voice_user_info') || '',
            userName: localStorage.getItem('agi_voice_user_name') || 'User',
            finalMessage: localStorage.getItem('agi_voice_final_message') || '',
            message: `다음은 요청하신 정보입니다:\n\n${systemContext}`,
            model: "sonnet",
            role: "system"  // System message로 전송
        };

        try {
            const followUpData = await invoke('chat', { request: followUpRequest });
            // 재귀 호출로 후속 응답 처리
            await processResponse(followUpData.responses[0], systemContext, hasDbChange);
        } catch (error) {
            console.error('Error sending auto-info follow-up:', error);
            messages = [...messages, {
                role: 'error',
                content: '정보 제공 후 AI 응답 실패',
                timestamp: new Date().toLocaleString('ko-KR')
            }];
        }

        return;  // 명령어 처리 후 종료
    }

    // ✅ 1단계: 기존 로직 (파싱, READ/CUD 실행)
    const { textSegments, actionSegments } = parseWithSegments(rawResponse);

    // 텍스트 세그먼트 표시
    textSegments.forEach(segment => {
        messages = [...messages, {
            role: 'assistant',
            content: segment.content,
            timestamp: new Date().toLocaleString('ko-KR')
        }];
    });

    // ... (기존 READ/CUD 로직)
}
```

**명령어 확장 방법**:
```typescript
// 새 명령어 추가 시:
AUTO_INFO_COMMANDS['map_count'] = async () => {
    const maps = await invoke('get_maps', { /* filters */ });
    return `총 맵 ${maps.length}개`;
};
```

---

## 3. 일회용 메시지 모드 (대화기록 포함 안 함)

### 목표
메시지는 DB에 저장되지만, AI에게 전송 시 이전 대화기록을 포함하지 않음

### 사용 사례
- 독립적인 질문/답변 (이전 대화 맥락 불필요)
- 테스트용 메시지
- Context 오염 방지

### 현재 상태
- ✅ Backend에서 conversation history를 항상 로드 (최근 20개)
- ❌ "일회용 모드" 플래그 없음

### 구현 방식

#### Backend (Rust)
**파일**: `src-tauri/src/commands/ai_chat.rs`

**변경 1**: `ChatRequest` 구조체에 필드 추가
```rust
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChatRequest {
    pub conversation_id: Option<i32>,
    pub character_id: i32,
    pub prompt_template_id: i32,
    pub user_info: String,
    pub user_name: String,
    pub final_message: String,
    pub message: String,
    #[serde(default = "default_model")]
    pub model: String,
    #[serde(default = "default_role")]
    pub role: String,

    #[serde(default)]  // ✅ 새 필드: 대화기록 제외 플래그
    pub exclude_history: bool,
}
```

**변경 2**: `chat` 함수 수정 (Line 106-176)
```rust
// 이전 메시지 로드
let previous_messages = if request.exclude_history {
    // ✅ 일회용 모드: 빈 배열
    vec![]
} else {
    // ✅ 일반 모드: 최근 20개 메시지 로드
    Message::find()
        .filter(message::Column::ConversationId.eq(conversation.id))
        .filter(message::Column::Role.ne("system"))  // system 메시지 제외
        .order_by_asc(message::Column::CreatedAt)
        .limit(20)
        .all(&**db)
        .await
        .map_err(|e| e.to_string())?
};

println!("Loaded {} previous messages (exclude_history: {})",
         previous_messages.len(),
         request.exclude_history);
```

#### Frontend (Svelte)
**파일**: `src/lib/components/ChatView.svelte`

**변경 1**: State 추가
```typescript
let excludeHistory = $state(false);  // 일회용 모드 토글
```

**변경 2**: UI Toggle 추가
```svelte
<!-- Chat Options (입력창 위에 배치) -->
<div class="chat-options mb-4 flex items-center gap-4">
  <!-- Message Type Toggle -->
  <div class="message-type-toggle">
    <!-- ... (기능 1의 UI) ... -->
  </div>

  <!-- Exclude History Toggle -->
  <label class="toggle-switch inline-flex items-center">
    <input
      type="checkbox"
      bind:checked={excludeHistory}
      class="sr-only"
    />
    <span class="toggle-switch-track">
      <span class="toggle-switch-thumb"></span>
    </span>
    <span class="ml-2 text-sm">일회용 메시지 (이전 대화 제외)</span>
  </label>
</div>
```

**변경 3**: `sendMessage()` 함수 수정
```typescript
async function sendMessage() {
    if (!inputMessage.trim()) return;
    if (!characterId || !promptTemplateId) {
        messages = [...messages, {
            role: 'error',
            content: 'Character와 Prompt Template을 선택해주세요.',
            timestamp: new Date().toLocaleString('ko-KR')
        }];
        return;
    }

    isLoading = true;

    try {
        const userInfo = localStorage.getItem('agi_voice_user_info') || '';
        const userName = localStorage.getItem('agi_voice_user_name') || 'User';
        const finalMessage = localStorage.getItem('agi_voice_final_message') || '';

        const requestBody = {
            conversationId,
            characterId,
            promptTemplateId,
            userInfo,
            userName,
            finalMessage,
            message: inputMessage,
            model: "sonnet",
            role: messageType,
            excludeHistory  // ✅ Backend로 전달
        };

        // ... (기존 로직)
```

**동작 설명**:
- `excludeHistory = true`:
  - 메시지는 DB 저장됨
  - Claude에게 보낼 때 `Previous Exchanges` 섹션이 비어있음
  - 응답은 현재 입력만 기반으로 생성됨
- `excludeHistory = false`:
  - 기존 동작 (최근 20개 메시지 포함)

---

## 4. AI 명령 파싱 시스템 (현재 Placeholder 구현)

### 목표
AI 응답에서 특정 패턴/태그를 파싱하여 프론트/백엔드 액션 실행

### 현재 상태
- ✅ Parser/Executor 아키텍처 존재 (`src/lib/actions/`)
- ✅ 2-pass 시스템 준비됨 (READ → 재전송 → CUD)
- ❌ 실제 태그 파싱 로직 없음 (stub)
- ❌ 액션 실행 미구현 (throws error)

### AI_Diet_V2 구현 참고
AI_Diet_V2에서 동일한 시스템이 이미 완전히 구현되어 있음. 해당 구현을 참고하여 AGI_VOICE_V2에 맞게 적용 가능.

**AI_Diet_V2 구현 특징**:
- 간단한 태그 형식: `<action_type|field:value|field:value>`
- Entity 타입이 action_type에 내장 (예: `meal`, `update_meal`, `delete_meal`)
- READ 결과를 자연어 문자열로 포맷팅 (executor에서 처리)
- Action 타입별로 개별 함수 구현 (확장성 높음)
- 한글 → 영어 매핑 자동 처리 (meal_type, mission_status)

### 태그 형식 정의 (AGI_VOICE_V2)

**2가지 태그 형식 옵션**:

#### 옵션 1: AI_Diet_V2 스타일 (간단, 추천)
```
<entity_type|field:value|field:value>
<action_entity|field:value|field:value>

예시:
<read_conversation|id:123>
<conversation|characterId:1|promptTemplateId:2|title:New Chat>  # create
<update_conversation|id:123|title:Updated Title>
<delete_conversation|id:456>
```

**장점**:
- 태그 형식이 간단하고 AI가 이해하기 쉬움
- AI_Diet_V2 코드를 거의 그대로 사용 가능
- Entity 타입과 작업이 하나의 단어로 표현 (read_meal, update_meal)

**단점**:
- CREATE는 operation이 생략됨 (entity만 써야 함)
- Entity가 많아지면 action 타입도 많아짐

#### 옵션 2: 계획안 스타일 (명시적)
```
<operation|entity|field1:value1|field2:value2>

예시:
<read|conversation|id:123>
<create|conversation|characterId:1|promptTemplateId:2|title:New Chat>
<update|map|id:123|name:Updated Name|category:intersection>
<delete|conversation|id:456>
```

**장점**:
- Operation이 명시적으로 분리되어 구조가 명확
- CRUD 패턴이 일관성 있음

**단점**:
- 태그가 길어짐
- AI_Diet_V2 코드를 많이 수정해야 함

**권장사항**: **옵션 1 (AI_Diet_V2 스타일)** 사용
- 이미 검증된 구현이 있음
- 코드 재사용성이 높음
- 태그가 간결하여 AI 응답 길이 절약

**파라미터 타입 자동 변환** (AI_Diet_V2에서 검증됨):
- 숫자: `"123"` → `123` (parseInt/parseFloat)
- Boolean: `"true"` → `true` (문자열 비교)
- 문자열: `"Hello"` → `"Hello"` (기본값)

### 구현 상세

#### Parser 구현 (AI_Diet_V2 스타일 권장)
**파일**: `src/lib/actions/parser.ts`

**AI_Diet_V2에서 검증된 구현 패턴**:

```typescript
export interface Action {
    operation: 'create' | 'read' | 'update' | 'delete';
    type: string;  // Entity type (conversation, character, map, etc.)
    data: Record<string, any>;
}

export interface ParsedSegment {
    type: 'text' | 'action';
    content?: string;    // 텍스트 세그먼트의 내용
    action?: Action;     // 액션 세그먼트의 액션 데이터
    label?: string;      // 액션 표시용 레이블 (예: "대화 조회")
}

/**
 * AI 응답에서 액션 태그를 파싱
 * @param response AI 응답 텍스트
 * @returns 파싱된 액션 배열
 *
 * AI_Diet_V2 검증된 패턴:
 * - 정규식: /<([^|>]+)(?:\|([^>]+))?>/g (유연한 파싱)
 * - action_type 기반으로 operation 추론
 * - Entity별 개별 함수로 처리 (확장성)
 */
export function parseActions(response: string): Action[] {
    const actions: Action[] = [];
    const tagPattern = /<([^|>]+)(?:\|([^>]+))?>/g;  // AI_Diet_V2 패턴
    let match;

    while ((match = tagPattern.exec(response)) !== null) {
        const actionType = match[1].trim();  // 예: "read_conversation", "conversation"
        const fieldsStr = match[2]?.trim();  // 예: "id:123|title:Test"

        const fields = parseFields(fieldsStr);
        const action = processAction(actionType, fields);

        if (action) {
            actions.push(action);
        }
    }

    return actions;
}

/**
 * 응답을 태그 위치 기준으로 분할하여 순서대로 반환
 * AI_Diet_V2 검증: 텍스트와 액션을 올바른 순서로 표시
 */
export function parseWithSegments(response: string): ParsedSegment[] {
    const segments: ParsedSegment[] = [];
    const tagPattern = /<([^|>]+)(?:\|([^>]+))?>/g;
    let lastEnd = 0;
    let match;

    while ((match = tagPattern.exec(response)) !== null) {
        // 태그 이전 텍스트 추가
        if (match.index > lastEnd) {
            const textBefore = response.substring(lastEnd, match.index).trim();
            if (textBefore) {
                segments.push({
                    type: 'text',
                    content: textBefore
                });
            }
        }

        // 태그 파싱
        const actionType = match[1].trim();
        const fieldsStr = match[2]?.trim();
        const fields = parseFields(fieldsStr);
        const action = processAction(actionType, fields);

        if (action) {
            segments.push({
                type: 'action',
                action: action,
                label: getActionLabel(actionType)  // 사용자 표시용
            });
        }

        lastEnd = match.index + match[0].length;
    }

    // 마지막 태그 이후 텍스트 추가
    if (lastEnd < response.length) {
        const textAfter = response.substring(lastEnd).trim();
        if (textAfter) {
            segments.push({
                type: 'text',
                content: textAfter
            });
        }
    }

    return segments;
}

/**
 * 파라미터 문자열을 객체로 변환
 * @param paramsStr "key1:value1|key2:value2" 형식
 *
 * AI_Diet_V2 검증: 콜론(:)이 value에 포함될 수 있음 (URL 등)
 * 예: "url:https://example.com" → { url: "https://example.com" }
 */
function parseFields(fieldsStr?: string): Record<string, string> {
    const fields: Record<string, string> = {};
    if (!fieldsStr) return fields;

    for (const part of fieldsStr.split('|')) {
        if (part.includes(':')) {
            const [key, ...valueParts] = part.split(':');
            fields[key.trim()] = valueParts.join(':').trim();  // 콜론 재결합
        }
    }

    return fields;
}

/**
 * 액션 타입별 처리
 * AI_Diet_V2 패턴: Entity별로 개별 함수 호출
 */
function processAction(actionType: string, fields: Record<string, string>): Action | null {
    // ==================== CREATE ====================
    if (actionType === 'conversation') {
        return createConversation(fields);
    } else if (actionType === 'character') {
        return createCharacter(fields);
    } else if (actionType === 'map') {
        return createMap(fields);
    }

    // ==================== UPDATE ====================
    else if (actionType === 'update_conversation') {
        return updateConversation(fields);
    } else if (actionType === 'update_character') {
        return updateCharacter(fields);
    } else if (actionType === 'update_map') {
        return updateMap(fields);
    }

    // ==================== DELETE ====================
    else if (actionType === 'delete_conversation') {
        return deleteConversation(fields);
    } else if (actionType === 'delete_character') {
        return deleteCharacter(fields);
    } else if (actionType === 'delete_map') {
        return deleteMap(fields);
    }

    // ==================== READ ====================
    else if (actionType === 'read_conversation') {
        return readConversation(fields);
    } else if (actionType === 'read_character') {
        return readCharacter(fields);
    } else if (actionType === 'read_map') {
        return readMap(fields);
    }

    return null;
}

// ==================== 개별 Entity 처리 함수 예시 ====================

function createConversation(fields: Record<string, string>): Action {
    return {
        operation: 'create',
        type: 'conversation',
        data: {
            characterId: fields.characterId ? parseInt(fields.characterId) : null,
            promptTemplateId: fields.promptTemplateId ? parseInt(fields.promptTemplateId) : null,
            title: fields.title || null,
            userInfo: fields.userInfo || null
        }
    };
}

function updateConversation(fields: Record<string, string>): Action {
    const data: Record<string, any> = { id: parseInt(fields.id) };

    if (fields.title) data.title = fields.title;
    if (fields.characterId) data.characterId = parseInt(fields.characterId);
    if (fields.promptTemplateId) data.promptTemplateId = parseInt(fields.promptTemplateId);
    if (fields.userInfo) data.userInfo = fields.userInfo;

    return {
        operation: 'update',
        type: 'conversation',
        data
    };
}

function deleteConversation(fields: Record<string, string>): Action {
    return {
        operation: 'delete',
        type: 'conversation',
        data: {
            id: parseInt(fields.id)
        }
    };
}

function readConversation(fields: Record<string, string>): Action {
    return {
        operation: 'read',
        type: 'conversation',
        data: {
            id: fields.id ? parseInt(fields.id) : null
        }
    };
}

/**
 * AI 응답을 텍스트와 액션으로 분리
 */
export function parseWithSegments(response: string): ParsedSegment[] {
    const segments: ParsedSegment[] = [];
    const tagPattern = /<(create|read|update|delete)\|(\w+)\|([^>]+)>/g;

    let lastIndex = 0;
    let match;

    while ((match = tagPattern.exec(response)) !== null) {
        // 태그 이전 텍스트
        if (match.index > lastIndex) {
            const textContent = response.substring(lastIndex, match.index).trim();
            if (textContent) {
                segments.push({
                    type: 'text',
                    content: textContent
                });
            }
        }

        // 액션 태그
        const [fullMatch, operation, type, paramsStr] = match;
        segments.push({
            type: 'action',
            content: fullMatch,
            action: {
                operation: operation as Action['operation'],
                type,
                data: parseParams(paramsStr)
            }
        });

        lastIndex = tagPattern.lastIndex;
    }

    // 남은 텍스트
    if (lastIndex < response.length) {
        const textContent = response.substring(lastIndex).trim();
        if (textContent) {
            segments.push({
                type: 'text',
                content: textContent
            });
        }
    }

    return segments;
}

/**
 * 액션 타입의 한글 레이블 반환
 */
export function getActionLabel(actionType: string): string {
    const labels: Record<string, string> = {
        conversation: '대화',
        character: '캐릭터',
        prompt_template: '시스템 메시지',
        command_template: '명령어',
        map: '맵',
        map_scenario: '맵 시나리오'
    };
    return labels[actionType] || actionType;
}

/**
 * 응답에서 액션 태그 제거 (텍스트만 추출)
 */
export function removeActionTags(response: string): string {
    const tagPattern = /<(create|read|update|delete)\|\w+\|[^>]+>/g;
    return response.replace(tagPattern, '').trim();
}
```

#### Executor 구현 (AI_Diet_V2 스타일 권장)
**파일**: `src/lib/actions/executor.ts`

**AI_Diet_V2 검증된 핵심 원칙**:
- READ 작업은 **자연어 문자열**로 결과 반환 (AI가 이해하기 쉬움)
- CUD 작업은 객체 반환 (Frontend에서 표시용)
- Entity별로 개별 함수 구현 (ENTITY_COMMANDS 매핑 불필요)
- READ 결과 포맷팅은 executor에서 처리 (formatter는 summary만)

```typescript
import { invoke } from '@tauri-apps/api/core';
import type { Action } from './parser';

export interface ActionResult {
    success: boolean;
    action: Action;
    result?: any;      // READ: string, CUD: object
    error?: string;
}

/**
 * 액션 리스트 실행 (순차 실행)
 * AI_Diet_V2 검증: 병렬 실행보다 순차 실행이 안정적
 */
export async function executeActions(actions: Action[]): Promise<ActionResult[]> {
    const results: ActionResult[] = [];

    for (const action of actions) {
        try {
            const result = await executeSingleAction(action);
            results.push({
                success: true,
                action,
                result
            });
        } catch (error: any) {
            results.push({
                success: false,
                action,
                error: error.message || String(error)
            });
        }
    }

    return results;
}

/**
 * 단일 액션 실행
 */
async function executeSingleAction(action: Action): Promise<any> {
    const { operation, type, data } = action;

    if (operation === 'create') {
        return await executeCreate(type, data);
    } else if (operation === 'read') {
        return await executeRead(type, data);  // 문자열 반환
    } else if (operation === 'update') {
        return await executeUpdate(type, data);
    } else if (operation === 'delete') {
        return await executeDelete(type, data);
    } else {
        throw new Error(`Unknown operation: ${operation}`);
    }
}

// ==================== CREATE ====================

async function executeCreate(type: string, data: Record<string, any>): Promise<any> {
    if (type === 'conversation') {
        return await invoke('create_conversation', { data });
    } else if (type === 'character') {
        return await invoke('create_character', { data });
    } else if (type === 'map') {
        return await invoke('create_map', { request: data });
    } else {
        throw new Error(`Unknown type for create: ${type}`);
    }
}

// ==================== READ (자연어 문자열 반환) ====================

async function executeRead(type: string, data: Record<string, any>): Promise<string> {
    if (type === 'conversation') {
        return await readConversation(data);
    } else if (type === 'character') {
        return await readCharacter(data);
    } else if (type === 'map') {
        return await readMap(data);
    } else {
        throw new Error(`Unknown type for read: ${type}`);
    }
}

/**
 * Conversation 조회
 * AI_Diet_V2 패턴: 자연어 형식으로 결과 포맷팅
 */
async function readConversation(data: Record<string, any>): Promise<string> {
    if (data.id) {
        try {
            const conv: any = await invoke('get_conversation_by_id', { id: data.id });
            return `[대화 #${conv.id}] ${conv.title || '제목 없음'}\n` +
                   `- 캐릭터 ID: ${conv.characterId}\n` +
                   `- Prompt Template ID: ${conv.promptTemplateId}\n` +
                   `- 메시지 개수: ${conv.messageCount || 0}개\n` +
                   `- 생성일: ${conv.createdAt}`;
        } catch (error) {
            return `ID ${data.id}인 대화를 찾을 수 없습니다.`;
        }
    } else {
        // 전체 조회
        try {
            const convs: any[] = await invoke('get_conversations');
            if (convs.length === 0) {
                return '등록된 대화가 없습니다.';
            }

            const lines = [`📋 전체 대화 (${convs.length}개):`];
            for (const conv of convs.slice(0, 10)) {  // 최근 10개만
                lines.push(`  - [${conv.id}] ${conv.title || '제목 없음'} (메시지 ${conv.messageCount}개)`);
            }
            return lines.join('\n');
        } catch (error) {
            return '대화를 조회할 수 없습니다.';
        }
    }
}

/**
 * Map 조회 예시
 */
async function readMap(data: Record<string, any>): Promise<string> {
    if (data.id) {
        try {
            const map: any = await invoke('get_map_by_id', { id: data.id });
            return `[맵 #${map.id}] ${map.name}\n` +
                   `- 설명: ${map.description || '없음'}\n` +
                   `- 카테고리: ${map.category || '미지정'}\n` +
                   `- 난이도: ${map.difficulty || '미지정'}\n` +
                   `- Embedding: ${map.embeddingId ? '완료' : '미완료'}`;
        } catch (error) {
            return `ID ${data.id}인 맵을 찾을 수 없습니다.`;
        }
    } else {
        // 필터 조회
        try {
            const maps: any[] = await invoke('get_maps', {
                category: data.category || null,
                searchQuery: data.search || null,
                onlyEmbedded: data.onlyEmbedded || false
            });

            if (maps.length === 0) {
                return '조건에 맞는 맵이 없습니다.';
            }

            const lines = [`🗺️ 맵 목록 (${maps.length}개):`];
            for (const map of maps.slice(0, 10)) {
                lines.push(`  - [${map.id}] ${map.name} (${map.category || '카테고리 없음'})`);
            }
            return lines.join('\n');
        } catch (error) {
            return '맵을 조회할 수 없습니다.';
        }
    }
}

// ==================== UPDATE ====================

async function executeUpdate(type: string, data: Record<string, any>): Promise<any> {
    const id = data.id;
    delete data.id;  // ID는 별도 파라미터로 전달

    if (type === 'conversation') {
        return await invoke('update_conversation', { id, data });
    } else if (type === 'character') {
        return await invoke('update_character', { id, data });
    } else if (type === 'map') {
        return await invoke('update_map', { id, data: data });
    } else {
        throw new Error(`Unknown type for update: ${type}`);
    }
}

// ==================== DELETE ====================

async function executeDelete(type: string, data: Record<string, any>): Promise<any> {
    if (type === 'conversation') {
        await invoke('delete_conversation', { id: data.id });
        return { message: `Conversation #${data.id} deleted` };
    } else if (type === 'character') {
        await invoke('delete_character', { id: data.id });
        return { message: `Character #${data.id} deleted` };
    } else if (type === 'map') {
        await invoke('delete_map', { id: data.id });
        return { message: `Map #${data.id} deleted` };
    } else {
        throw new Error(`Unknown type for delete: ${type}`);
    }
}
```

**핵심 포인트 (AI_Diet_V2 검증)**:
- READ 함수는 항상 `Promise<string>` 반환 (자연어 형식)
- CUD 함수는 `Promise<any>` 반환 (객체)
- try-catch로 에러 처리하여 친절한 에러 메시지 제공
- ID 조회와 전체 조회를 분기 처리
- 결과가 없을 때도 자연어 메시지 반환

#### Formatter 구현 (AI_Diet_V2 스타일)
**파일**: `src/lib/actions/formatter.ts`

**AI_Diet_V2 검증된 패턴**:
- READ 결과는 이미 executor에서 포맷팅되어 문자열로 반환됨
- Formatter는 **결과들을 결합**하는 역할만 수행
- CUD 결과는 summary만 생성 (사용자 표시용)

```typescript
import type { ActionResult } from './executor';

/**
 * READ 액션 결과들을 system 메시지로 포맷팅
 * AI_Diet_V2: executor에서 이미 자연어로 포맷팅되어 옴
 */
export function formatReadResults(results: ActionResult[]): string {
    const contextParts: string[] = [];

    for (const result of results) {
        if (result.success && result.result) {
            // READ 결과는 이미 executor에서 포맷된 문자열
            contextParts.push(result.result);
        } else if (!result.success) {
            // 실패한 READ도 컨텍스트에 포함
            contextParts.push(`⚠️ 조회 실패: ${result.error}`);
        }
    }

    if (contextParts.length === 0) {
        return '';
    }

    // 구분선으로 각 결과를 구분
    return contextParts.join('\n\n---\n\n');
}

/**
 * 액션 실행 결과 summary (사용자 표시용)
 */
export function formatActionSummary(results: ActionResult[]): string {
    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    if (failureCount === 0) {
        if (successCount === 1) {
            return '✅ 작업이 완료되었습니다.';
        } else {
            return `✅ ${successCount}개의 작업이 완료되었습니다.`;
        }
    } else {
        if (successCount === 0) {
            return `❌ ${failureCount}개의 작업이 실패했습니다.`;
        } else {
            return `⚠️ ${successCount}개 성공, ${failureCount}개 실패`;
        }
    }
}
            results.push({
                action,
                success: false,
                error: error instanceof Error ? error.message : String(error)
            });
        }
    }

    return results;
}

/**
 * 단일 액션 실행
 */
async function executeSingleAction(action: Action): Promise<any> {
    const { operation, type, data } = action;

    // Entity type 검증
    if (!(type in ENTITY_COMMANDS)) {
        throw new Error(`Unknown entity type: ${type}`);
    }

    const commands = ENTITY_COMMANDS[type as EntityType];
    const command = commands[operation];

    if (!command) {
        throw new Error(`Operation ${operation} not supported for ${type}`);
    }

    console.log(`Executing ${operation} on ${type}:`, data);

    // Tauri 명령어 실행
    switch (operation) {
        case 'create':
            return await invoke(command, { data });

        case 'read':
            if (!data.id) {
                throw new Error('READ operation requires "id" field');
            }
            return await invoke(command, { id: data.id });

        case 'update':
            if (!data.id) {
                throw new Error('UPDATE operation requires "id" field');
            }
            const { id, ...updateData } = data;
            return await invoke(command, { id, data: updateData });

        case 'delete':
            if (!data.id) {
                throw new Error('DELETE operation requires "id" field');
            }
            return await invoke(command, { id: data.id });

        default:
            throw new Error(`Unknown operation: ${operation}`);
    }
}

/**
 * READ 작업만 필터링하여 실행
 */
export async function executeReadActions(actions: Action[]): Promise<ActionResult[]> {
    const readActions = actions.filter(a => a.operation === 'read');
    return await executeActions(readActions);
}

/**
 * CUD 작업만 필터링하여 실행 (Create/Update/Delete)
 */
export async function executeCudActions(actions: Action[]): Promise<ActionResult[]> {
    const cudActions = actions.filter(a => a.operation !== 'read');
    return await executeActions(cudActions);
}
```

#### Formatter 구현
**파일**: `src/lib/actions/formatter.ts`

```typescript
import type { ActionResult } from './executor';

/**
 * READ 액션 결과를 AI에게 전달할 형식으로 포맷팅
 */
export function formatReadResults(results: ActionResult[]): string {
    if (results.length === 0) return '';

    const formatted = results.map(r => {
        if (!r.success) {
            return `[ERROR] ${r.action.type} 읽기 실패: ${r.error}`;
        }

        // Entity별 포맷팅
        const data = r.result;
        switch (r.action.type) {
            case 'conversation':
                return formatConversation(data);

            case 'character':
                return formatCharacter(data);

            case 'prompt_template':
                return formatPromptTemplate(data);

            case 'command_template':
                return formatCommandTemplate(data);

            case 'map':
                return formatMap(data);

            case 'map_scenario':
                return formatMapScenario(data);

            default:
                // Fallback: JSON 형식
                return `[${r.action.type}]\n${JSON.stringify(data, null, 2)}`;
        }
    });

    return formatted.join('\n\n---\n\n');
}

// Entity별 포맷팅 함수
function formatConversation(data: any): string {
    return `[대화 정보]
- ID: ${data.id}
- 제목: ${data.title || '제목 없음'}
- 캐릭터 ID: ${data.characterId}
- Prompt Template ID: ${data.promptTemplateId}
- 메시지 개수: ${data.messageCount || 0}개
- 생성일: ${data.createdAt}
- 수정일: ${data.updatedAt}`;
}

function formatCharacter(data: any): string {
    return `[캐릭터 정보]
- ID: ${data.id}
- 이름: ${data.name}
- 프롬프트 내용:
${data.promptContent}
- 생성일: ${data.createdAt}`;
}

function formatPromptTemplate(data: any): string {
    return `[시스템 메시지 정보]
- ID: ${data.id}
- 이름: ${data.name}
- 내용:
${data.content}
- 생성일: ${data.createdAt}`;
}

function formatCommandTemplate(data: any): string {
    return `[명령어 템플릿 정보]
- ID: ${data.id}
- 이름: ${data.name}
- 활성 상태: ${data.isActive ? '활성화' : '비활성화'}
- 내용:
${data.content}
- 생성일: ${data.createdAt}`;
}

function formatMap(data: any): string {
    return `[맵 정보]
- ID: ${data.id}
- 이름: ${data.name}
- 설명: ${data.description || '설명 없음'}
- 카테고리: ${data.category || '미지정'}
- 난이도: ${data.difficulty || '미지정'}
- 태그: ${data.tags || '없음'}
- Embedding 상태: ${data.embeddingId ? '완료' : '미완료'}
- 생성일: ${data.createdAt}`;
}

function formatMapScenario(data: any): string {
    return `[맵 시나리오 정보]
- ID: ${data.id}
- 맵 ID: ${data.mapId}
- 드라이버 수: ${data.drivers || 0}
- 차량 수: ${data.vehicles || 0}
- 생성일: ${data.createdAt}`;
}

/**
 * CUD 액션 결과를 사용자에게 표시할 형식으로 포맷팅
 */
export function formatCudResults(results: ActionResult[]): string {
    if (results.length === 0) return '';

    const formatted = results.map(r => {
        const actionLabel = getActionLabel(r.action.operation);
        const entityLabel = getEntityLabel(r.action.type);

        if (!r.success) {
            return `❌ ${entityLabel} ${actionLabel} 실패: ${r.error}`;
        }

        const resultData = r.result;
        const itemName = resultData?.name || resultData?.title || resultData?.id || '항목';

        return `✅ ${entityLabel} ${actionLabel} 성공: ${itemName}`;
    });

    return formatted.join('\n');
}

function getActionLabel(operation: string): string {
    const labels: Record<string, string> = {
        create: '생성',
        read: '조회',
        update: '수정',
        delete: '삭제'
    };
    return labels[operation] || operation;
}

function getEntityLabel(type: string): string {
    const labels: Record<string, string> = {
        conversation: '대화',
        character: '캐릭터',
        prompt_template: '시스템 메시지',
        command_template: '명령어',
        map: '맵',
        map_scenario: '맵 시나리오'
    };
    return labels[type] || type;
}
```

#### ChatView 통합
**파일**: `src/lib/components/ChatView.svelte`

**변경**: `processResponse()` 함수 완전 구현
```typescript
import { parseWithSegments, parseActions, removeActionTags } from '$lib/actions/parser';
import { executeReadActions, executeCudActions } from '$lib/actions/executor';
import { formatReadResults, formatCudResults } from '$lib/actions/formatter';

async function processResponse(rawResponse: string, userMessage: string, hasDbChange = false) {
    // 0단계: 명령어 감지 (기능 2)
    const detectedCommands = detectInfoCommands(rawResponse);
    if (detectedCommands.length > 0) {
        // ... (기능 2 로직)
        return;
    }

    // 1단계: 응답 파싱
    const segments = parseWithSegments(rawResponse);
    const actions = parseActions(rawResponse);

    console.log('Parsed segments:', segments.length);
    console.log('Parsed actions:', actions);

    // 2단계: 텍스트 세그먼트 표시
    for (const segment of segments) {
        if (segment.type === 'text') {
            messages = [...messages, {
                role: 'assistant',
                content: segment.content,
                timestamp: new Date().toLocaleString('ko-KR')
            }];
        } else if (segment.type === 'action' && segment.action) {
            // 액션 세그먼트는 별도 표시
            const actionLabel = getActionLabel(segment.action.operation);
            const entityLabel = getEntityLabel(segment.action.type);
            messages = [...messages, {
                role: 'action',
                content: `[${actionLabel} ${entityLabel}] ${JSON.stringify(segment.action.data)}`,
                timestamp: new Date().toLocaleString('ko-KR')
            }];
        }
    }

    if (actions.length === 0) {
        isLoading = false;
        return;
    }

    // 3단계: READ 액션 실행
    const readResults = await executeReadActions(actions);

    if (readResults.length > 0) {
        const readContext = formatReadResults(readResults);
        console.log('READ results:', readContext);

        // READ 결과를 system message로 재전송
        const followUpRequest = {
            conversationId,
            characterId,
            promptTemplateId,
            userInfo: localStorage.getItem('agi_voice_user_info') || '',
            userName: localStorage.getItem('agi_voice_user_name') || 'User',
            finalMessage: localStorage.getItem('agi_voice_final_message') || '',
            message: `다음은 조회 결과입니다:\n\n${readContext}`,
            model: "sonnet",
            role: "system"
        };

        try {
            const followUpData = await invoke('chat', { request: followUpRequest });
            // 재귀 호출로 후속 응답 처리
            await processResponse(followUpData.responses[0], readContext, hasDbChange);
        } catch (error) {
            console.error('Error sending READ follow-up:', error);
            messages = [...messages, {
                role: 'error',
                content: 'READ 결과 전달 실패',
                timestamp: new Date().toLocaleString('ko-KR')
            }];
        }
    }

    // 4단계: CUD 액션 실행
    const cudResults = await executeCudActions(actions);

    if (cudResults.length > 0) {
        const cudSummary = formatCudResults(cudResults);
        console.log('CUD results:', cudSummary);

        // CUD 결과 표시
        messages = [...messages, {
            role: 'system',
            content: cudSummary,
            timestamp: new Date().toLocaleString('ko-KR'),
            isTemporary: true
        }];

        // DB 변경 플래그 설정
        hasDbChange = true;
    }

    // 5단계: DB 새로고침
    if (hasDbChange) {
        console.log('Marking database as changed');
        dbWatcher.markAsChanged();
    }

    isLoading = false;
}

function getActionLabel(operation: string): string {
    const labels: Record<string, string> = {
        create: '생성',
        read: '조회',
        update: '수정',
        delete: '삭제'
    };
    return labels[operation] || operation;
}

function getEntityLabel(type: string): string {
    const labels: Record<string, string> = {
        conversation: '대화',
        character: '캐릭터',
        prompt_template: '시스템 메시지',
        command_template: '명령어',
        map: '맵',
        map_scenario: '맵 시나리오'
    };
    return labels[type] || type;
}
```

---

## 구현 우선순위

### Phase 1: 기본 메시지 시스템 (낮은 난이도)
1. **System/User 메시지 구분** (2-3시간)
   - Backend: Line 302-350 수정 (system role 저장 제외)
   - Frontend: Message type toggle UI 추가
   - 테스트: System message가 DB에 저장 안 되는지 확인

2. **일회용 메시지 모드** (2-3시간)
   - Backend: `exclude_history` 플래그 추가
   - Frontend: Toggle UI 추가
   - 테스트: 이전 대화기록이 포함 안 되는지 확인

### Phase 2: 명령 파싱 시스템 (중간 난이도)
3. **AI 명령 파싱 구현** (4-6시간)
   - Parser 태그 정규식 구현
   - Executor Tauri invoke 호출
   - Formatter 결과 포맷팅
   - ChatView 통합
   - 테스트: CREATE/READ/UPDATE/DELETE 모든 작업 확인

### Phase 3: 고급 기능 (중간 난이도)
4. **AI 정보 제공 (자동 System 메시지)** (3-4시간)
   - 명령어 감지 패턴 정의
   - Auto-response handler 구현
   - 확장 가능한 명령어 시스템
   - 테스트: 각 명령어가 올바른 정보를 반환하는지 확인

**총 예상 시간**: 11-16시간

---

## 예상 파일 변경 목록

### Backend (Rust)
- `src-tauri/src/commands/ai_chat.rs`
  - ✅ System message 저장 방지 (Line 302-350)
  - ✅ `exclude_history` 플래그 추가 (Line 106-176)

### Frontend (TypeScript/Svelte)
- `src/lib/components/ChatView.svelte`
  - ✅ Message type toggle UI
  - ✅ Exclude history toggle UI
  - ✅ `sendMessage()` 함수 수정 (messageType, excludeHistory 전달)
  - ✅ System message 표시 UI
  - ✅ `processResponse()` 완전 구현
  - ✅ Info command detection 및 auto-response

- `src/lib/actions/parser.ts`
  - ✅ `parseActions()` 구현
  - ✅ `parseWithSegments()` 구현
  - ✅ `parseParams()`, `parseValue()` helper 함수
  - ✅ `getActionLabel()`, `removeActionTags()` 유틸리티

- `src/lib/actions/executor.ts`
  - ✅ `executeActions()` 구현
  - ✅ `executeSingleAction()` 구현
  - ✅ `executeReadActions()`, `executeCudActions()` 필터 함수
  - ✅ `ENTITY_COMMANDS` 매핑

- `src/lib/actions/formatter.ts`
  - ✅ `formatReadResults()` 구현
  - ✅ `formatCudResults()` 구현
  - ✅ Entity별 포맷팅 함수 (formatConversation, formatCharacter, etc.)

### 총 변경 파일: 5개
- Backend: 1개
- Frontend: 4개

---

## 테스트 시나리오

### 기능 1: System/User 메시지
1. User message 전송 → DB에 저장 확인
2. System message 전송 → DB에 저장 안 됨 확인
3. System message → AI 응답 정상 확인

### 기능 2: AI 정보 제공
1. AI 응답에 `[INFO:user_info]` 포함 → userInfo 자동 전송 확인
2. AI 응답에 `[INFO:current_time]` 포함 → 현재 시간 전송 확인
3. AI 응답에 `[INFO:conversation_count]` 포함 → 대화 개수 전송 확인
4. 미지원 명령어 → 에러 메시지 표시 확인

### 기능 3: 일회용 메시지
1. 일반 모드: 이전 대화 포함 확인
2. 일회용 모드: 이전 대화 제외 확인
3. 일회용 메시지도 DB에 저장되는지 확인

### 기능 4: AI 명령 파싱
1. `<read|conversation|id:1>` → 대화 조회 확인
2. `<create|character|name:Test|promptContent:Hello>` → 캐릭터 생성 확인
3. `<update|map|id:1|name:Updated>` → 맵 수정 확인
4. `<delete|conversation|id:999>` → 존재하지 않는 항목 삭제 시 에러 확인
5. READ → System message 재전송 → AI 자연어 응답 확인
6. CUD → DB 변경 감지 → 자동 새로고침 확인

---

## 추가 고려사항

### 에러 핸들링
- Tauri invoke 실패 시 사용자 친화적 에러 메시지
- Parser 실패 시 원본 응답 표시
- Executor 실패 시 실패한 액션만 표시, 나머지 액션은 계속 실행

### 성능 최적화
- READ 액션은 병렬 실행 (Promise.all)
- CUD 액션은 순차 실행 (DB 트랜잭션 순서 보장)
- 응답 파싱 시 정규식 최적화 (ReDoS 방지)

### 확장성
- 새 Entity 추가 시 `ENTITY_COMMANDS`에만 추가하면 됨
- 새 Info Command 추가 시 `AUTO_INFO_COMMANDS`에만 추가하면 됨
- Tag format 변경 시 parser.ts만 수정하면 됨

### 보안
- Tauri invoke 권한 검증 (tauri.conf.json)
- SQL Injection 방지 (SeaORM이 자동 처리)
- XSS 방지 (Svelte가 자동 이스케이프)

---

## 다음 단계

1. ✅ **구현 계획 검토 및 승인**
2. Phase 1 구현 시작 (System/User 메시지, 일회용 모드)
3. Phase 2 구현 (명령 파싱 시스템)
4. Phase 3 구현 (AI 정보 제공)
5. 통합 테스트 및 버그 수정
6. 문서 업데이트 (CLAUDE.md, README.md)

---

**작성일**: 2025-11-23
**버전**: v1.1 (AI_Diet_V2 참고 반영)
**상태**: 구현 준비 완료

---

## AI_Diet_V2에서 배운 핵심 교훈

### 1. 태그 형식 선택
**권장**: AI_Diet_V2 스타일 (`<action_entity|field:value>`)
- ✅ 간결하고 AI가 이해하기 쉬움
- ✅ 이미 검증된 구현 존재 (코드 재사용)
- ✅ 태그 길이가 짧아 AI 응답 토큰 절약
- ❌ Entity가 많아질수록 action type 증가 (큰 문제 아님)

### 2. READ 결과 포맷팅
**핵심**: Executor에서 자연어 문자열로 포맷팅
- ✅ AI가 바로 이해 가능한 형식
- ✅ Formatter는 결과 결합만 담당 (단순화)
- ✅ 에러 메시지도 자연어로 제공

**예시**:
```typescript
// ✅ Good (AI_Diet_V2)
return `[대화 #${id}] ${title}\n- 메시지 ${count}개\n- 생성일: ${date}`;

// ❌ Bad (구조화된 객체)
return { id, title, messageCount, createdAt };  // AI가 파싱 필요
```

### 3. 구현 패턴
**Entity별 개별 함수 구현** (ENTITY_COMMANDS 매핑 불필요)
- ✅ 확장성 높음 (새 entity 추가 시 함수만 추가)
- ✅ Entity별 로직 커스터마이징 용이
- ✅ 타입 안전성 (명시적 파라미터)

**예시**:
```typescript
// ✅ Good (AI_Diet_V2 패턴)
async function readConversation(data: Record<string, any>): Promise<string> {
    if (data.id) {
        // ID 조회 로직
    } else {
        // 전체 조회 로직 (최근 10개만)
    }
}

// ❌ Bad (제너릭 매핑)
const result = await invoke(ENTITY_COMMANDS[type][operation], data);
// → Entity별 커스터마이징 어려움
```

### 4. processResponse 플로우 (AI_Diet_V2 검증)
```typescript
async function processResponse(rawResponse, userMessage, hasDbChange) {
    // 1. 응답 파싱
    const actions = parseActions(rawResponse);
    const segments = parseWithSegments(rawResponse);

    // 2. 텍스트와 액션 세그먼트 순차 표시
    for (const segment of segments) {
        if (segment.type === 'text') {
            messages.push({ role: 'assistant', content: segment.content });
        } else if (segment.type === 'action') {
            messages.push({ role: 'action', label: segment.label });
            if (segment.label.includes('추가|수정|삭제')) {
                hasDbChange.value = true;  // CUD 감지
            }
        }
    }

    // 3. READ 액션 실행 → system message로 재전송
    const readActions = actions.filter(a => a.operation === 'read');
    if (readActions.length > 0) {
        const readResults = await executeActions(readActions);
        const systemContext = formatReadResults(readResults);

        const followupData = await invoke('chat', {
            message: userMessage,
            systemContext: systemContext,
            role: 'system'  // DB 저장 안 됨
        });

        // 재귀 호출로 후속 응답 처리
        await processResponse(followupData.responses[0], userMessage, hasDbChange);
    }

    // 4. CUD 액션 실행
    const cudActions = actions.filter(a => a.operation !== 'read');
    if (cudActions.length > 0) {
        await executeActions(cudActions);
        hasDbChange.value = true;
    }
}
```

**핵심**:
- ✅ READ/CUD 분리 실행 (READ 먼저, 결과를 system message로 재전송)
- ✅ 재귀 호출로 후속 응답 처리 (깔끔한 구조)
- ✅ DB 변경 감지를 hasDbChange 플래그로 관리
- ✅ System message는 DB 저장 안 됨 (role: 'system')

### 5. 실용적 팁

**필드 파싱 주의사항**:
```typescript
// ✅ Good: 콜론(:)이 value에 포함될 수 있음
const [key, ...valueParts] = part.split(':');
fields[key] = valueParts.join(':');  // "url:https://example.com" 처리

// ❌ Bad: 첫 번째 콜론만 사용
const [key, value] = part.split(':');  // URL 등에서 문제 발생
```

**에러 처리**:
```typescript
// ✅ Good: 친절한 에러 메시지
try {
    const result = await invoke('get_conversation_by_id', { id });
    return `[대화 #${id}] ${result.title}`;
} catch (error) {
    return `ID ${id}인 대화를 찾을 수 없습니다.`;  // 자연어 에러
}

// ❌ Bad: 원본 에러 노출
throw error;  // AI가 이해하기 어려움
```

**결과 개수 제한**:
```typescript
// ✅ Good: 최근 N개만 반환
const lines = [`📋 전체 대화 (${convs.length}개):`];
for (const conv of convs.slice(0, 10)) {  // 최근 10개만
    lines.push(`  - [${conv.id}] ${conv.title}`);
}

// ❌ Bad: 전체 반환
// → 응답이 너무 길어지면 AI 처리 느려짐
```

### 6. 구현 체크리스트

#### Parser (src/lib/actions/parser.ts)
- [ ] `parseActions()`: 태그 정규식 파싱
- [ ] `parseWithSegments()`: 텍스트/액션 분리
- [ ] `parseFields()`: field:value 파싱 (콜론 재결합)
- [ ] `processAction()`: action type → operation 추론
- [ ] Entity별 개별 함수 (create/update/delete/read)
- [ ] `getActionLabel()`: 한글 레이블 반환

#### Executor (src/lib/actions/executor.ts)
- [ ] `executeActions()`: 순차 실행
- [ ] `executeSingleAction()`: operation 분기
- [ ] `executeRead()`: 자연어 문자열 반환
- [ ] Entity별 read 함수 (ID/전체 조회 분기)
- [ ] `executeCreate/Update/Delete()`: Entity 분기
- [ ] 에러 처리 (try-catch, 친절한 메시지)

#### Formatter (src/lib/actions/formatter.ts)
- [ ] `formatReadResults()`: 결과 결합 (구분선)
- [ ] `formatActionSummary()`: 성공/실패 count

#### ChatView (src/lib/components/ChatView.svelte)
- [ ] `processResponse()`: 파싱 → 표시 → READ → 재귀 → CUD
- [ ] Segment별 메시지 표시 (텍스트/액션 구분)
- [ ] hasDbChange 플래그 관리
- [ ] System message 재전송 (role: 'system')

### 7. 코드 참고 위치

**AI_Diet_V2 참고 파일**:
```
C:\Users\kyoungtj\GitProject\AI_Diet_V2\src\lib\actions\
├── parser.ts     # 완전한 파싱 구현 (469줄)
├── executor.ts   # 완전한 실행 구현 (373줄)
└── formatter.ts  # 간단한 포맷팅 (92줄)

C:\Users\kyoungtj\GitProject\AI_Diet_V2\src\lib\components\
└── ChatView.svelte  # processResponse 구현 (Line 205-292)
```

**AGI_VOICE_V2 구현 대상**:
```
C:\Users\kyoungtj\GitProject\AGI_VOICE_V2\src\lib\actions\
├── parser.ts     # 현재 stub → AI_Diet_V2 참고하여 구현
├── executor.ts   # 현재 stub → AI_Diet_V2 참고하여 구현
└── formatter.ts  # 현재 stub → AI_Diet_V2 참고하여 구현

C:\Users\kyoungtj\GitProject\AGI_VOICE_V2\src\lib\components\
└── ChatView.svelte  # processResponse 완성 필요
```

### 8. 예상 구현 난이도

**Easy (2-3시간)**:
- Formatter (거의 복사 가능)
- getActionLabel 등 helper 함수

**Medium (4-6시간)**:
- Parser (AI_Diet_V2 로직 이해 후 Entity만 변경)
- Executor READ 함수 (Entity별 자연어 포맷팅)
- processResponse 통합 (AI_Diet_V2 패턴 적용)

**Hard (없음)**:
- 모든 패턴이 AI_Diet_V2에서 검증됨

**총 예상 시간**: 6-9시간

---

## 최종 권장사항

1. **태그 형식**: AI_Diet_V2 스타일 사용 (`<action_entity|field:value>`)
2. **구현 순서**:
   - Phase 2 먼저 (AI 명령 파싱) → AI_Diet_V2 코드 참고하여 빠르게 구현
   - Phase 1 (System/User 메시지, 일회용 모드) → 간단한 플래그 추가
   - Phase 3 (AI 정보 제공) → 나중에 추가 (필요시)

3. **코드 재사용**:
   - Parser: AI_Diet_V2의 `parseActions`, `parseWithSegments`, `parseFields` 거의 그대로 사용
   - Executor: AI_Diet_V2의 패턴 따라 Entity만 변경 (conversation, character, map)
   - Formatter: AI_Diet_V2 그대로 복사

4. **테스트 전략**:
   - 간단한 태그부터 테스트 (`<read_conversation>`)
   - Entity별로 하나씩 구현 및 테스트
   - READ → 재전송 → AI 응답 플로우 확인
   - CUD → DB 변경 → 자동 새로고침 확인
