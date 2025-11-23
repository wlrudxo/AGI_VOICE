// Seed data module
// Inserts default data on first run

use sea_orm::{ActiveModelTrait, DatabaseConnection, DbErr, EntityTrait, PaginatorTrait, Set};
use chrono::Utc;

use crate::db::models::{
    prompt_template::{self, Entity as PromptTemplate},
    character::{self, Entity as Character},
    command_template::{self, Entity as CommandTemplate},
};

/// Check if database is empty (first run)
pub async fn is_first_run(db: &DatabaseConnection) -> Result<bool, DbErr> {
    let prompt_count = PromptTemplate::find().count(db).await?;
    let char_count = Character::find().count(db).await?;
    let command_count = CommandTemplate::find().count(db).await?;

    Ok(prompt_count == 0 && char_count == 0 && command_count == 0)
}

/// Insert default prompt templates
async fn insert_default_prompt_templates(db: &DatabaseConnection) -> Result<(), DbErr> {
    let now = Utc::now().naive_utc();

    let default_prompt = prompt_template::ActiveModel {
        id: Set(1),
        name: Set("기본 시스템 메시지".to_string()),
        content: Set(r#"당신은 자율주행 연구를 돕는 AI 어시스턴트입니다.

사용자의 자율주행 관련 질문에 답변하고, 맵 생성 및 주행 판단에 대한 연구를 지원합니다.

주요 역할:
1. 자율주행 기술에 대한 설명과 조언
2. 맵 생성 알고리즘에 대한 논의
3. 주행 판단 로직 분석 및 개선 제안
4. 연구 데이터 분석 및 인사이트 제공
5. 관련 문헌 및 최신 기술 동향 설명

응답 시 주의사항:
- 전문적이면서도 이해하기 쉽게 설명하세요.
- 필요시 수식이나 알고리즘을 제시하세요.
- 안전성과 윤리적 측면을 고려하세요."#.to_string()),
        created_at: Set(now),
        updated_at: Set(now),
    };

    default_prompt.insert(db).await?;
    println!("✅ Default prompt template inserted");

    Ok(())
}

/// Insert default characters
async fn insert_default_characters(db: &DatabaseConnection) -> Result<(), DbErr> {
    let now = Utc::now().naive_utc();

    let default_character = character::ActiveModel {
        id: Set(1),
        name: Set("Research Assistant".to_string()),
        prompt_content: Set(r#"# Character: Professional Research Assistant

## 기본 설정
- 역할: 자율주행 연구 어시스턴트
- 성격: 전문적, 논리적, 친절함
- 특징: 명확한 설명, 근거 기반 답변, 최신 연구 동향 파악

## 말투 특징
- 존댓말 사용 (~입니다, ~해요)
- 전문 용어를 적절히 사용하되 쉽게 풀어 설명
- 논리적이고 체계적인 답변 구조

## 대화 예시
"자율주행 맵 생성에 대해 질문하셨군요. SLAM 알고리즘을 기반으로 설명드리겠습니다."
"주행 판단 로직에서 안전성이 최우선입니다. 센서 융합 기법을 고려해보시는 것은 어떨까요?"
"최신 연구에 따르면 Transformer 기반 경로 예측 모델의 정확도가 향상되고 있습니다."

## 역할
자율주행 연구를 전문적으로 지원하는 AI 어시스턴트입니다.
명확한 설명과 근거 기반 조언을 제공합니다."#.to_string()),
        created_at: Set(now),
        updated_at: Set(now),
    };

    default_character.insert(db).await?;
    println!("✅ Default character inserted");

    Ok(())
}

/// Insert default command templates
async fn insert_default_command_templates(db: &DatabaseConnection) -> Result<(), DbErr> {
    let now = Utc::now().naive_utc();

    // 1. 자율주행 맵 관리 명령어 (활성화)
    let map_management_commands = command_template::ActiveModel {
        id: Set(1),
        name: Set("자율주행 맵 관리".to_string()),
        content: Set(r#"## 자율주행 맵 관리 명령어

당신은 SUMO 자율주행 시뮬레이션 맵을 관리할 수 있습니다.
사용자가 맵 생성, 조회, 수정, 삭제를 요청하면 아래 태그를 사용하세요.

### 📋 READ 명령어 (정보 조회)

사용자가 맵 정보를 물어보면 READ 태그를 사용하여 DB를 조회하세요.
시스템이 자동으로 정보를 가져와서 다시 전달합니다.

**맵 전체 조회:**
<read_map>

**특정 맵 ID로 조회:**
<read_map|id:123>

**카테고리별 조회:**
<read_map|category:도심>
<read_map|category:고속도로>

**이름으로 검색:**
<read_map|name:강남역>

**대시보드 현황 조회:**
<read_dashboard>

### ✏️ CREATE 명령어 (맵 생성)

사용자가 새 맵을 만들어달라고 하면 이 태그를 사용하세요.

**기본 형식:**
<map|name:맵이름|description:설명|category:카테고리|difficulty:난이도>

**예시:**
<map|name:강남역 교차로|description:복잡한 4거리 교차로|category:도심|difficulty:어려움>
<map|name:고속도로 진출입로|description:IC 진출입 구간|category:고속도로|difficulty:보통|tags:합류,분기>

**필수 필드:** name
**선택 필드:** description, category, difficulty, tags, nodeXml, edgeXml, metadata

### 🔄 UPDATE 명령어 (맵 수정)

기존 맵을 수정할 때 사용하세요.

**형식:**
<update_map|id:맵ID|수정할필드:새값|...>

**예시:**
<update_map|id:5|name:강남역 사거리|difficulty:매우어려움>
<update_map|id:3|category:도심|tags:신호등,횡단보도>

**필수 필드:** id
**선택 필드:** name, description, category, difficulty, tags, nodeXml, edgeXml

### 🗑️ DELETE 명령어 (맵 삭제)

맵을 삭제할 때 사용하세요.

**형식:**
<delete_map|id:맵ID>

**예시:**
<delete_map|id:7>

### 💡 사용 가이드

1. **먼저 조회하기**: 사용자가 "맵 있어?" 같은 질문을 하면 `<read_map>`이나 `<read_dashboard>`로 먼저 조회하세요.

2. **자연스러운 대화**: 태그만 던지지 말고 설명과 함께 사용하세요.
   예: "강남역 교차로 맵을 생성하겠습니다. <map|name:강남역 교차로|description:복잡한 4거리|category:도심>"

3. **확인 후 삭제**: 삭제 전에는 꼭 해당 맵을 조회해서 확인한 후 삭제하세요.

4. **READ 결과 기다리기**: READ 태그를 사용하면 시스템이 정보를 가져와서 다시 알려줍니다. 그 정보를 바탕으로 답변하세요.

5. **여러 작업 동시 수행**: 한 응답에 여러 태그를 사용할 수 있습니다.
   예: "현재 맵을 확인하겠습니다. <read_dashboard> 그리고 새로운 맵을 추가할게요. <map|name:테스트맵|category:도심>"#.to_string()),
        is_active: Set(1),  // Active by default
        created_at: Set(now),
        updated_at: Set(now),
    };

    map_management_commands.insert(db).await?;
    println!("✅ Map management command template inserted (active)");

    // 2. 예제 명령어 (비활성화)
    let example_commands = command_template::ActiveModel {
        id: Set(2),
        name: Set("예제 명령어 템플릿".to_string()),
        content: Set(r#"## 예제 명령어 템플릿

이 템플릿은 참고용입니다. 프로젝트 요구사항에 맞게 새로운 명령어 템플릿을 추가하세요.

### 태그 형식
<action_type|field:value|field:value|...>

### 사용자 정의 명령어 예시

프로젝트에서 필요한 도메인별 명령어를 정의하세요:
- 센서 데이터 관리
- 주행 시나리오 생성
- 성능 지표 분석
- 실험 결과 기록

참고: 이 명령어 템플릿은 비활성화되어 있습니다."#.to_string()),
        is_active: Set(0),  // Deactivated
        created_at: Set(now),
        updated_at: Set(now),
    };

    example_commands.insert(db).await?;
    println!("✅ Example command template inserted (inactive)");

    Ok(())
}

/// Insert all seed data
pub async fn insert_seed_data(db: &DatabaseConnection) -> Result<(), DbErr> {
    println!("🌱 Inserting seed data...");

    insert_default_prompt_templates(db).await?;
    insert_default_characters(db).await?;
    insert_default_command_templates(db).await?;

    println!("✅ All seed data inserted successfully");

    Ok(())
}
