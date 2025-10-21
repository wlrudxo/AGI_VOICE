# RAG 통합 계획: AI 기반 맵 생성 시스템

**작성일**: 2025-10-21
**목적**: 기존 AI 채팅 시스템에 RAG(Retrieval-Augmented Generation)를 통합하여 유사 맵을 참고한 새 맵 생성 기능 구현

---

## 📋 개요

### 핵심 개념

- **목적**: 맵 **추천**이 아니라 **새 맵 생성**
- **RAG 역할**: 유사한 기존 맵을 찾아서 **참고 자료**로 제공
- **실행 조건**: Map 생성 페이지에서 RAG on/off 스위치로 제어
- **결과**: AI가 참고 자료를 보고 **새로운** 맵 생성 → Map 생성 창에 auto-fill

### 시스템 구성

```
[Map 생성 페이지]
  ├─ RAG 참고 활성화 [on/off 스위치]
  ├─ 사용자 입력: "교차로가 있는 3차선 도로 맵 만들어줘"
  └─ AI 채팅 전송 (useRag: true)
      ↓
[AI 채팅 처리 - 2-Pass System]
  ├─ 1st Pass: <read_map_rag|query:교차로 3차선> 실행
  │   └─ RAG 검색 → 유사 맵 3-5개 찾기 (nodeXml, edgeXml 포함)
  ├─ 2nd Pass: 참고 자료를 보고 **새 맵** 생성
  │   └─ <create_map|name:...|description:...|nodeXml:...|edgeXml:...>
  └─ 프론트엔드 파싱 → Map 생성 페이지 auto-fill
```

---

## 🎯 활용 기술

### 기존 시스템

1. **AI 채팅 시스템** (`src-tauri/src/commands/ai_chat.rs`)
   - Dynamic Prompt System (Command Templates)
   - 2-Pass System (READ 액션 → system_context 피드백)
   - Tag-based Actions (`<type|field:value>` 파싱 및 실행)

2. **RAG 시스템** (`src-tauri/src/ai/embeddings.rs`)
   - `search_similar_maps(query, top_k)` API
   - FAISS 벡터 검색 (Python 연동)
   - 반환 데이터: mapId, mapName, description, category, difficulty, tags, similarityScore

3. **액션 시스템** (`src/lib/actions/`)
   - `parser.js`: 태그 파싱
   - `executor.js`: READ 액션 실행
   - `formatter.js`: 결과 포맷팅

---

## 🔧 구현 계획

### 1. Map 생성 페이지 UI 수정

**파일**: `src/routes/map-settings/generator/+page.svelte`

**추가 기능**:
- RAG 참고 활성화 체크박스
- 맵 설명 입력 텍스트박스
- "AI로 맵 생성" 버튼

**코드**:

```svelte
<script>
  // 기존 코드...

  // RAG 설정
  let ragEnabled = $state(false);
  let ragQuery = $state('');

  // AI 채팅으로 맵 생성 요청
  async function generateMapWithAI() {
    if (!ragQuery.trim()) {
      saveMessage = { type: 'error', text: '맵 설명을 입력해주세요.' };
      return;
    }

    try {
      // AI 채팅 호출 (RAG 활성화 플래그 전달)
      const response = await invoke('chat', {
        request: {
          conversationId: null, // 새 대화
          characterId: chatSettings.characterId,
          promptTemplateId: chatSettings.promptTemplateId,
          message: ragQuery,
          model: 'sonnet',
          useRag: ragEnabled  // RAG 활성화 플래그
        }
      });

      // 응답 파싱 (create_map 액션 찾기)
      const actions = parseActions(response.responses[0]);
      const createMapAction = actions.find(a => a.type === 'create_map');

      if (createMapAction) {
        // Auto-fill
        mapName = createMapAction.name;
        mapDescription = createMapAction.description;
        mapTags = createMapAction.tags?.join(', ') || '';
        nodeXml = createMapAction.nodeXml;
        edgeXml = createMapAction.edgeXml;

        // 자동 파싱
        parseXml();

        saveMessage = { type: 'success', text: 'AI가 맵을 생성했습니다!' };
      } else {
        saveMessage = { type: 'error', text: 'AI 응답에서 맵 정보를 찾을 수 없습니다.' };
      }

    } catch (error) {
      console.error('AI map generation error:', error);
      saveMessage = { type: 'error', text: `AI 생성 실패: ${error}` };
    }
  }
</script>

<!-- UI -->
<div class="ai-generation-section">
  <h3>
    <Icon icon="solar:magic-stick-bold-duotone" width="24" height="24" />
    AI로 맵 생성
  </h3>

  <div class="input-group">
    <label>
      <input type="checkbox" bind:checked={ragEnabled} />
      RAG 참고 활성화 (기존 유사 맵 참고)
    </label>
  </div>

  <div class="input-group">
    <label>맵 설명</label>
    <textarea
      bind:value={ragQuery}
      placeholder="예: 신호등이 있는 4거리 교차로 맵을 만들어줘"
      rows="3"
    ></textarea>
  </div>

  <button class="btn-primary" onclick={generateMapWithAI}>
    <Icon icon="solar:magic-stick-bold" width="20" height="20" />
    AI로 맵 생성
  </button>
</div>
```

---

### 2. Command Template 작성

**위치**: AI 설정 > 명령어 관리 페이지에서 추가

**템플릿 이름**: `map_generation`

**내용**:

```markdown
## 맵 생성 명령어

사용자가 새로운 SUMO 맵 생성을 요청하면:

### 1. RAG 참고가 활성화된 경우
먼저 유사한 맵을 검색하세요:

<read_map_rag|query:사용자 요청을 요약한 검색 쿼리>

검색된 맵들을 **참고**하여 사용자 요청에 맞는 **새로운** 맵을 생성하세요.

**중요**: 기존 맵을 복사하지 말고, 구조와 형식을 참고하여 새롭게 만드세요.

### 2. 맵 생성 형식

<create_map|
  name:맵_이름_영문_숫자|
  description:맵 설명 (한글, 상세하게)|
  tags:태그1,태그2,태그3|
  nodeXml:<?xml version="1.0" encoding="UTF-8"?>
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
  <node id="노드ID" x="X좌표" y="Y좌표" type="타입"/>
  ...
</nodes>|
  edgeXml:<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
  <edge id="엣지ID" from="시작노드" to="끝노드" priority="우선순위" numLanes="차선수" speed="속도"/>
  ...
</edges>
>

### 3. 생성 규칙

**필수 사항**:
- `nodeXml`과 `edgeXml`은 반드시 **완전한 XML**이어야 합니다
- node의 `id`와 edge의 `from`/`to`가 일치해야 합니다
- speed 단위는 m/s입니다 (예: 50km/h = 13.89m/s, 80km/h = 22.22m/s)
- 맵 이름(`name`)은 영문, 숫자, 언더스코어만 사용하세요
- 태그에 파이프(|) 문자를 사용하지 마세요

**XML 구조**:
- Node 타입: `priority`, `traffic_light`, `right_before_left` 등
- Edge priority: 1-4 (숫자가 높을수록 우선순위 높음)
- numLanes: 차선 수 (1-4)

### 4. 응답 형식

생성한 맵에 대해 간단히 설명해주세요:
- 어떤 구조인지
- 어떤 특징이 있는지
- 어떤 시나리오에 적합한지
```

---

### 3. 프론트엔드 액션 파서 확장

**파일**: `src/lib/actions/parser.js`

**추가 패턴**:

```javascript
export function parseActions(text) {
  const actions = [];

  // 1. read_map_rag 패턴
  const ragPattern = /<read_map_rag\|query:([^>]+)>/g;
  let match;

  while ((match = ragPattern.exec(text)) !== null) {
    actions.push({
      type: 'read_map_rag',
      query: match[1].trim(),
      raw: match[0]
    });
  }

  // 2. create_map 패턴 (멀티라인 지원)
  const createMapPattern = /<create_map\|([\s\S]*?)>/g;

  while ((match = createMapPattern.exec(text)) !== null) {
    const fields = {};
    const content = match[1];

    // 필드 파싱 (key:value 형식)
    // XML 내부의 파이프는 무시
    const parts = content.split(/\|(?![^<]*>)/);

    for (const part of parts) {
      const colonIndex = part.indexOf(':');
      if (colonIndex === -1) continue;

      const key = part.substring(0, colonIndex).trim();
      const value = part.substring(colonIndex + 1).trim();

      fields[key] = value;
    }

    actions.push({
      type: 'create_map',
      name: fields.name,
      description: fields.description,
      tags: fields.tags?.split(',').map(t => t.trim()),
      nodeXml: fields.nodeXml,
      edgeXml: fields.edgeXml,
      raw: match[0]
    });
  }

  return actions;
}

export function getActionLabel(action) {
  switch (action.type) {
    case 'read_map_rag':
      return `🔍 유사 맵 검색: "${action.query}"`;
    case 'create_map':
      return `🗺️ 맵 생성: "${action.name}"`;
    default:
      return action.type;
  }
}
```

---

### 4. 액션 실행기 확장

**파일**: `src/lib/actions/executor.js`

**추가 로직**:

```javascript
import { invoke } from '@tauri-apps/api/core';

export async function executeActions(actions) {
  const results = [];

  for (const action of actions) {
    if (action.type === 'read_map_rag') {
      console.log(`🔍 Executing RAG search: "${action.query}"`);

      try {
        // 1. RAG 검색 실행
        const searchResults = await invoke('search_similar_maps', {
          query: action.query,
          topK: 5
        });

        console.log(`✅ Found ${searchResults.length} similar maps`);

        // 2. 전체 맵 데이터 로드 (NodeXML, EdgeXML 포함)
        const fullMaps = await Promise.all(
          searchResults.map(r => invoke('get_map_by_id', { id: r.mapId }))
        );

        // 3. 참고 자료 포맷팅
        const formatted = searchResults.map((r, i) => {
          const fullMap = fullMaps[i];

          return `
### 참고 맵 ${i + 1}: ${r.mapName}
**유사도**: ${(r.similarityScore * 100).toFixed(1)}%

**메타데이터**:
- 카테고리: ${r.category}
- 난이도: ${r.difficulty}
- 설명: ${r.description}
- 태그: ${r.tags.join(', ')}

**Node XML** (참고용):
\`\`\`xml
${fullMap.nodeXml}
\`\`\`

**Edge XML** (참고용):
\`\`\`xml
${fullMap.edgeXml}
\`\`\`
`;
        }).join('\n\n---\n\n');

        results.push({
          type: 'read_map_rag',
          query: action.query,
          result: `### 🔍 RAG 검색 결과 (참고 자료)

${formatted}

---

**지침**: 위 맵들의 구조와 형식을 참고하여 사용자 요청에 맞는 **새로운** 맵을 생성하세요.
기존 맵을 그대로 복사하지 말고, 사용자가 요청한 특징을 반영하여 독창적으로 만드세요.`
        });

      } catch (error) {
        console.error('RAG search failed:', error);
        results.push({
          type: 'read_map_rag',
          query: action.query,
          error: error.toString()
        });
      }
    }
  }

  return results;
}
```

---

### 5. 백엔드 수정 (선택 사항)

**파일**: `src-tauri/src/commands/ai_chat.rs`

**ChatRequest에 필드 추가**:

```rust
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChatRequest {
    pub conversation_id: Option<i32>,
    pub character_id: Option<i32>,
    pub prompt_template_id: Option<i32>,
    pub user_info: Option<String>,
    pub user_name: Option<String>,
    pub final_message: Option<String>,
    pub title: Option<String>,
    pub message: String,
    #[serde(default = "default_model")]
    pub model: String,
    pub system_context: Option<String>,
    #[serde(default = "default_role")]
    pub role: String,

    // 새로 추가: RAG 활성화 플래그
    pub use_rag: Option<bool>,
}
```

**처리 방법**:

Option 1: 프론트엔드에서만 처리
- `useRag=true`일 때 사용자 메시지 앞에 `[RAG 참고 활성화]\n\n` 추가
- AI가 이를 보고 `<read_map_rag>` 사용 판단

Option 2: 백엔드에서 처리
- `useRag=true`일 때 특정 Command Template 자동 활성화
- 또는 프롬프트에 RAG 지침 자동 추가

**추천**: Option 1 (프론트엔드 처리) - 더 유연하고 간단함

---

## 📊 전체 실행 플로우

### 사용 시나리오

1. **사용자**: Map 생성 페이지 접속
2. **사용자**: "RAG 참고 활성화" 체크박스 ON
3. **사용자**: 텍스트박스에 "신호등이 있는 4거리 교차로 만들어줘" 입력
4. **사용자**: [AI로 맵 생성] 버튼 클릭

### 시스템 처리

```
[프론트엔드]
  ├─ invoke('chat', { message: "신호등...", useRag: true })
  └─ 대기...

[백엔드 - 1st Pass]
  ├─ Command Template 로드 (map_generation)
  ├─ AI 응답: "<read_map_rag|query:신호등 4거리 교차로>"
  └─ 프론트엔드로 반환

[프론트엔드]
  ├─ parseActions() → read_map_rag 액션 감지
  ├─ executeActions()
  │   ├─ invoke('search_similar_maps', { query: "신호등 4거리 교차로", topK: 5 })
  │   ├─ 결과: [crossroad_01, signal_junction_02, ...]
  │   ├─ invoke('get_map_by_id', { id: 1 }) × 5
  │   └─ 참고 자료 포맷팅 (nodeXml, edgeXml 포함)
  └─ invoke('chat', { systemContext: "RAG 검색 결과...", role: 'system' })

[백엔드 - 2nd Pass]
  ├─ 참고 자료를 previous_messages에 추가
  ├─ AI가 유사 맵 구조 분석
  ├─ 새로운 맵 생성
  └─ 응답: "<create_map|name:signal_crossroad_01|description:...|nodeXml:...|edgeXml:...>"

[프론트엔드]
  ├─ parseActions() → create_map 액션 감지
  ├─ 맵 생성 폼에 auto-fill:
  │   ├─ mapName = "signal_crossroad_01"
  │   ├─ mapDescription = "..."
  │   ├─ nodeXml = "<?xml..."
  │   └─ edgeXml = "<?xml..."
  ├─ parseXml() → SVG 미리보기 생성
  └─ 성공 메시지 표시

[사용자]
  ├─ 생성된 맵 확인 (SVG 미리보기)
  ├─ 필요시 수정
  └─ [DB 저장] 버튼 클릭
```

---

## 🔍 주요 설계 결정

### 왜 2-Pass System을 사용하는가?

1. **토큰 절약**: RAG 결과(XML 포함)를 CLAUDE.md에 넣지 않고 system_context로 전달
2. **유연성**: AI가 필요할 때만 `<read_map_rag>` 요청 가능
3. **기존 시스템 활용**: 이미 구현된 READ 액션 패턴 재사용

### create_map vs 직접 생성

- **create_map 태그 사용**: AI가 생성한 맵을 프론트엔드가 검증 및 수정 가능
- **직접 DB 저장 안함**: 사용자가 확인 후 저장 (안전성)

### RAG on/off 스위치

- **사용자 선택권**: 참고 없이 순수 AI 생성도 가능
- **비용 절감**: RAG 불필요한 경우 2nd Pass 생략

---

## ✅ 체크리스트

### 개발 순서

- [ ] 1. Command Template 작성 (`map_generation`)
- [ ] 2. 액션 파서 확장 (`read_map_rag`, `create_map` 패턴)
- [ ] 3. 액션 실행기 확장 (RAG 검색 + 포맷팅)
- [ ] 4. Map 생성 페이지 UI 추가 (RAG 스위치, AI 생성 버튼)
- [ ] 5. ChatView 2-Pass 로직 활용 (기존 코드 재사용)
- [ ] 6. Map 생성 페이지 auto-fill 로직 구현
- [ ] 7. 테스트
  - [ ] RAG OFF: 순수 AI 생성
  - [ ] RAG ON: 유사 맵 참고하여 생성
  - [ ] XML 파싱 및 SVG 렌더링
  - [ ] DB 저장

### 테스트 시나리오

1. **RAG OFF 테스트**:
   - 입력: "단순한 2차선 직선 도로 만들어줘"
   - 기대: AI가 참고 없이 직선 도로 생성

2. **RAG ON 테스트**:
   - 입력: "신호등이 있는 교차로 만들어줘"
   - 기대: crossroad_01 같은 맵 참고하여 새 교차로 생성

3. **복잡한 요청**:
   - 입력: "3차선 도로와 진입 램프가 있는 고속도로 진입 구간"
   - 기대: merge_lane_01, three_lane_road_01 참고하여 생성

---

## 🚀 향후 확장 가능성

1. **다중 맵 생성**: 한 번에 여러 맵 변형 생성
2. **시나리오 생성**: 맵과 함께 차량/운전자 시나리오 자동 생성
3. **맵 수정**: 기존 맵을 불러와서 AI로 수정
4. **자동 임베딩**: 생성 후 자동으로 임베딩 생성
5. **피드백 루프**: 사용자 평가를 기반으로 RAG 검색 개선

---

## 📚 참고 파일

### 핵심 파일

- `src/routes/map-settings/generator/+page.svelte` - Map 생성 페이지
- `src/lib/components/ChatView.svelte` - AI 채팅 UI
- `src/lib/actions/parser.js` - 액션 파싱
- `src/lib/actions/executor.js` - 액션 실행
- `src-tauri/src/commands/ai_chat.rs` - AI 채팅 백엔드
- `src-tauri/src/ai/embeddings.rs` - RAG 검색 API
- `src-tauri/src/ai/prompt_builder.rs` - 프롬프트 조립

### 관련 문서

- `CLAUDE.md` - 프로젝트 가이드
- `MapGenerator/map_descriptions.txt` - 샘플 맵 설명

---

**작성자**: Claude Code
**최종 수정**: 2025-10-21
