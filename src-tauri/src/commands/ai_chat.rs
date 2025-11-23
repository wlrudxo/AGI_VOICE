use sea_orm::*;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tauri::State;

use crate::ai::{build_full_prompt, save_claude_md, ClaudeCLIManager, Message as PromptMessage};
use crate::commands::settings::load_settings;
use crate::db::models::{character, command_template, conversation, message, prompt_template};
use crate::db::AiChatDb;

// ==================== Request/Response Models ====================

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
    #[serde(default)]
    pub exclude_history: bool,
    #[serde(default)]
    pub no_save: bool, // Don't save conversation/messages to DB
}

fn default_model() -> String {
    "sonnet".to_string()
}

fn default_role() -> String {
    "user".to_string()
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ChatResponse {
    pub conversation_id: i32,
    pub responses: Vec<String>,
    pub actions: Vec<serde_json::Value>,
}

// ==================== Helper Functions ====================

async fn get_or_create_conversation(
    request: &ChatRequest,
    db: &DatabaseConnection,
) -> Result<(conversation::Model, i32, i32, String), String> {
    if let Some(conv_id) = request.conversation_id {
        // 기존 대화 로드
        let conv = conversation::Entity::find_by_id(conv_id)
            .one(db)
            .await
            .map_err(|e| e.to_string())?
            .ok_or("Conversation not found")?;

        Ok((
            conv.clone(),
            conv.character_id,
            conv.prompt_template_id,
            conv.user_info.unwrap_or_default(),
        ))
    } else {
        // 새 대화 생성
        let character_id = request
            .character_id
            .ok_or("character_id is required for new conversation")?;
        let prompt_template_id = request
            .prompt_template_id
            .ok_or("prompt_template_id is required for new conversation")?;

        let title = request
            .title
            .clone()
            .unwrap_or_else(|| format!("Chat {}", chrono::Local::now().format("%Y-%m-%d %H:%M")));

        let now = chrono::Utc::now().naive_utc();
        let new_conv = conversation::ActiveModel {
            character_id: Set(character_id),
            prompt_template_id: Set(prompt_template_id),
            user_info: Set(request.user_info.clone()),
            title: Set(Some(title)),
            created_at: Set(now),
            updated_at: Set(now),
            ..Default::default()
        };

        let conv = new_conv
            .insert(db)
            .await
            .map_err(|e| e.to_string())?;

        Ok((
            conv.clone(),
            character_id,
            prompt_template_id,
            request.user_info.clone().unwrap_or_default(),
        ))
    }
}

async fn load_conversation_context(
    db: &DatabaseConnection,
    conversation_id: i32,
    character_id: i32,
    prompt_template_id: i32,
) -> Result<
    (
        character::Model,
        prompt_template::Model,
        Vec<PromptMessage>,
        Vec<String>,
    ),
    String,
> {
    // 캐릭터 조회
    let character = character::Entity::find_by_id(character_id)
        .one(db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Character not found")?;

    // 프롬프트 템플릿 조회
    let prompt_template = prompt_template::Entity::find_by_id(prompt_template_id)
        .one(db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Prompt template not found")?;

    // 이전 대화 이력 조회 (최근 20개)
    let previous_messages_db = message::Entity::find()
        .filter(message::Column::ConversationId.eq(conversation_id))
        .order_by_asc(message::Column::CreatedAt)
        .limit(20)
        .all(db)
        .await
        .map_err(|e| e.to_string())?;

    let previous_messages: Vec<PromptMessage> = previous_messages_db
        .into_iter()
        .map(|msg| {
            // UTC → KST 변환 (+9시간)
            use chrono::Duration;
            let kst_time = msg.created_at.and_utc() + Duration::hours(9);
            let timestamp = Some(kst_time.format("%Y-%m-%d %a %H:%M").to_string());

            PromptMessage {
                role: msg.role,
                content: msg.content,
                timestamp,
            }
        })
        .collect();

    // 명령어 템플릿 조회 (활성화된 것만)
    let command_templates = command_template::Entity::find()
        .filter(command_template::Column::IsActive.eq(1))
        .order_by_asc(command_template::Column::Id)
        .all(db)
        .await
        .map_err(|e| e.to_string())?;

    let command_info_list: Vec<String> =
        command_templates.into_iter().map(|t| t.content).collect();

    Ok((
        character,
        prompt_template,
        previous_messages,
        command_info_list,
    ))
}

async fn execute_claude_request(
    character: &character::Model,
    prompt_template: &prompt_template::Model,
    user_info: &str,
    command_info_list: &[String],
    previous_messages: &[PromptMessage],
    request_message: &str,
    model: &str,
    workspace_dir: Option<&std::path::Path>,
    system_context: Option<&str>,
    user_name: &str,
    final_message: &str,
    exclude_history: bool,
) -> Result<String, String> {
    // 프롬프트 조립
    let (claude_md_content, full_user_message) = build_full_prompt(
        &prompt_template.content,
        &character.prompt_content,
        user_info,
        command_info_list,
        previous_messages,
        request_message,
        Some(final_message).filter(|s| !s.is_empty()),
        system_context,
        user_name,
        &character.name,
        exclude_history,
    );

    // 🐛 디버깅: CLAUDE.md 내용 출력
    println!("\n========== 📝 CLAUDE.md Content ==========");
    println!("{}", claude_md_content);
    println!("==========================================\n");

    // 🐛 디버깅: 전체 유저 메시지 출력
    println!("\n========== 📤 Full User Message ==========");
    println!("{}", full_user_message);
    println!("==========================================\n");

    // CLAUDE.md 저장
    save_claude_md(&claude_md_content, workspace_dir).map_err(|e| e.to_string())?;

    // Claude CLI 실행
    let manager = ClaudeCLIManager::new(workspace_dir.map(|p| p.to_path_buf()));
    let raw_response = manager
        .chat(&full_user_message, model)
        .await
        .map_err(|e| e.to_string())?;

    // 🐛 디버깅: Claude 응답 전체 출력
    println!("\n========== 🤖 Claude Response (Full) ==========");
    println!("{}", raw_response);
    println!("===============================================\n");

    Ok(raw_response)
}

// ==================== No-Save Chat Handler ====================

async fn handle_no_save_chat(
    request: ChatRequest,
    db: &DatabaseConnection,
) -> Result<ChatResponse, String> {
    println!("🔒 No-save mode: Conversation will not be saved to DB");

    // Get character and template IDs (required)
    let character_id = request
        .character_id
        .ok_or("character_id is required for no-save chat")?;
    let prompt_template_id = request
        .prompt_template_id
        .ok_or("prompt_template_id is required for no-save chat")?;

    // Load character and template
    let character = character::Entity::find_by_id(character_id)
        .one(db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Character not found")?;

    let prompt_template = prompt_template::Entity::find_by_id(prompt_template_id)
        .one(db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Prompt template not found")?;

    // Load active command templates
    let command_templates = command_template::Entity::find()
        .filter(command_template::Column::IsActive.eq(true))
        .order_by_asc(command_template::Column::Id)
        .all(db)
        .await
        .map_err(|e| e.to_string())?;

    let command_info_list: Vec<String> = command_templates
        .into_iter()
        .map(|ct| ct.content)
        .collect();

    println!(
        "✅ Loaded context: character={}, template={}, commands={}",
        character.name,
        prompt_template.name,
        command_info_list.len()
    );

    // Get workspace directory
    let workspace_dir = match load_settings() {
        Ok(settings) if !settings.claude_workspace_dir.is_empty() => {
            let path = PathBuf::from(&settings.claude_workspace_dir);
            println!("✅ Using workspace directory: {}", path.display());
            Some(path)
        }
        _ => {
            let appdata = std::env::var("APPDATA").unwrap_or_else(|_| {
                std::env::var("HOME").unwrap_or_else(|_| ".".to_string())
            });
            let default_path = PathBuf::from(appdata).join("AGI_Voice_V2");

            if let Err(e) = std::fs::create_dir_all(&default_path) {
                println!("⚠️ Failed to create workspace directory: {}", e);
            }

            println!("✅ Using default workspace directory: {}", default_path.display());
            Some(default_path)
        }
    };

    // Execute Claude request (no previous messages)
    let raw_response = execute_claude_request(
        &character,
        &prompt_template,
        &request.user_info.unwrap_or_default(),
        &command_info_list,
        &Vec::new(), // No previous messages
        &request.message,
        &request.model,
        workspace_dir.as_deref(),
        request.system_context.as_deref(),
        &request.user_name.unwrap_or_default(),
        &request.final_message.unwrap_or_default(),
        true, // Always exclude history for no-save mode
    )
    .await?;

    println!("✅ Got response from Claude ({} chars) - NOT SAVED", raw_response.len());

    // Return response without saving to DB (use dummy conversation_id = -1)
    Ok(ChatResponse {
        conversation_id: -1, // Indicates no conversation was created
        responses: vec![raw_response],
        actions: vec![],
    })
}

// ==================== Tauri Command ====================

#[tauri::command]
pub async fn chat(
    request: ChatRequest,
    db: State<'_, AiChatDb>,
) -> Result<ChatResponse, String> {
    println!("📥 Chat request: {:?}", request.message);

    // Check if no_save mode (temporary conversation)
    if request.no_save {
        return handle_no_save_chat(request, &db.0).await;
    }

    // 1. Conversation 로드/생성
    let (conversation, character_id, prompt_template_id, user_info) =
        get_or_create_conversation(&request, &db.0).await?;

    println!("✅ Conversation ID: {}", conversation.id);

    // 2. 대화 컨텍스트 로드
    let (character, prompt_template, previous_messages, command_info_list) =
        load_conversation_context(&db.0, conversation.id, character_id, prompt_template_id).await?;

    println!(
        "✅ Loaded context: character={}, template={}, messages={}, commands={}",
        character.name,
        prompt_template.name,
        previous_messages.len(),
        command_info_list.len()
    );

    // 2.5. Settings에서 workspace_dir 로드 (없으면 %APPDATA%\AGI_Voice_V2 기본값)
    let workspace_dir = match load_settings() {
        Ok(settings) if !settings.claude_workspace_dir.is_empty() => {
            let path = PathBuf::from(&settings.claude_workspace_dir);
            println!("✅ Using workspace directory: {}", path.display());
            Some(path)
        }
        _ => {
            // 기본값: %APPDATA%\AGI_Voice_V2
            let appdata = std::env::var("APPDATA").unwrap_or_else(|_| {
                std::env::var("HOME").unwrap_or_else(|_| ".".to_string())
            });
            let default_path = PathBuf::from(appdata).join("AGI_Voice_V2");

            // 디렉토리 생성 (없으면)
            if let Err(e) = std::fs::create_dir_all(&default_path) {
                println!("⚠️ Failed to create workspace directory: {}", e);
            }

            println!("✅ Using default workspace directory: {}", default_path.display());
            Some(default_path)
        }
    };

    // 3. Claude CLI 실행
    let raw_response = execute_claude_request(
        &character,
        &prompt_template,
        &user_info,
        &command_info_list,
        &previous_messages,
        &request.message,
        &request.model,
        workspace_dir.as_deref(),
        request.system_context.as_deref(),
        &request.user_name.unwrap_or_default(),
        &request.final_message.unwrap_or_default(),
        request.exclude_history,
    )
    .await?;

    println!("✅ Got response from Claude ({} chars)", raw_response.len());

    // 4. 메시지 DB 저장
    let msg_timestamp = chrono::Utc::now().naive_utc();

    if request.role == "user" {
        // user 역할: user 메시지 + assistant 응답 모두 저장
        let user_msg = message::ActiveModel {
            conversation_id: Set(conversation.id),
            role: Set("user".to_string()),
            content: Set(request.message.clone()),
            created_at: Set(msg_timestamp),
            ..Default::default()
        };
        let saved_user = user_msg.insert(&db.0).await.map_err(|e| {
            println!("❌ Failed to save user message: {}", e);
            e.to_string()
        })?;
        println!("✅ User message saved: ID={}, conv_id={}", saved_user.id, saved_user.conversation_id);
    } else {
        println!("⏭️ Skipping user message save (role={})", request.role);
    }

    // assistant 응답은 항상 저장 (user든 system이든)
    let assistant_msg = message::ActiveModel {
        conversation_id: Set(conversation.id),
        role: Set("assistant".to_string()),
        content: Set(raw_response.clone()),
        created_at: Set(msg_timestamp),
        ..Default::default()
    };
    let saved_assistant = assistant_msg
        .insert(&db.0)
        .await
        .map_err(|e| {
            println!("❌ Failed to save assistant message: {}", e);
            e.to_string()
        })?;

    println!("✅ Assistant message saved: ID={}, conv_id={}, content_len={}",
        saved_assistant.id, saved_assistant.conversation_id, saved_assistant.content.len());

    // 저장 후 검증: 해당 대화의 메시지 수 확인
    let message_count = message::Entity::find()
        .filter(message::Column::ConversationId.eq(conversation.id))
        .count(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    println!("✅ Total messages in conversation {}: {}", conversation.id, message_count);

    // 5. 원본 응답 그대로 반환 (파싱은 Frontend에서)
    Ok(ChatResponse {
        conversation_id: conversation.id,
        responses: vec![raw_response],
        actions: vec![],
    })
}

#[tauri::command]
pub async fn chat_health() -> Result<serde_json::Value, String> {
    Ok(serde_json::json!({
        "status": "ok",
        "service": "ai_chat"
    }))
}
