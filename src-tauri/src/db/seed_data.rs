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

    let aris = character::ActiveModel {
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

    aris.insert(db).await?;
    println!("✅ Default character (Aris) inserted");

    Ok(())
}

/// Insert default command templates
async fn insert_default_command_templates(db: &DatabaseConnection) -> Result<(), DbErr> {
    let now = Utc::now().naive_utc();

    // Example command template for autonomous driving research
    let example_commands = command_template::ActiveModel {
        id: Set(1),
        name: Set("예제 명령어".to_string()),
        content: Set(r#"## 명령어 템플릿 예제

이 섹션에는 AI가 실행할 수 있는 액션 태그를 정의할 수 있습니다.
자율주행 연구 프로젝트에 맞는 명령어를 추가하세요.

### 태그 형식
<action_type|param1:value1|param2:value2|...>

### 예시 (사용자 정의)
프로젝트 요구사항에 따라 명령어를 정의하고 사용하세요.

참고: 이 명령어 템플릿은 비활성화되어 있습니다."#.to_string()),
        is_active: Set(0),  // Deactivated by default
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
