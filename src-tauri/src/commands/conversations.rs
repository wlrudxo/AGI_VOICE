use sea_orm::*;
use serde::{Deserialize, Serialize};
use tauri::State;

use crate::commands::common::{DeleteResult, HealthResponse};
use crate::db::models::{conversation, message};

// ==================== Request/Response Models ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ConversationCreate {
    pub character_id: i32,
    pub prompt_template_id: i32,
    pub user_info: Option<String>,
    pub title: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ConversationUpdate {
    pub title: Option<String>,
    pub user_info: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ConversationResponse {
    pub id: i32,
    pub character_id: i32,
    pub prompt_template_id: i32,
    pub user_info: Option<String>,
    pub title: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

impl From<conversation::Model> for ConversationResponse {
    fn from(conversation: conversation::Model) -> Self {
        Self {
            id: conversation.id,
            character_id: conversation.character_id,
            prompt_template_id: conversation.prompt_template_id,
            user_info: conversation.user_info,
            title: conversation.title,
            created_at: conversation.created_at.and_utc().to_rfc3339(),
            updated_at: conversation.updated_at.and_utc().to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ConversationWithCount {
    pub id: i32,
    pub character_id: i32,
    pub prompt_template_id: i32,
    pub user_info: Option<String>,
    pub title: Option<String>,
    pub created_at: String,
    pub updated_at: String,
    pub message_count: i64,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MessageResponse {
    pub id: i32,
    pub conversation_id: i32,
    pub role: String,
    pub content: String,
    pub created_at: String,
}

impl From<message::Model> for MessageResponse {
    fn from(message: message::Model) -> Self {
        Self {
            id: message.id,
            conversation_id: message.conversation_id,
            role: message.role,
            content: message.content,
            created_at: message.created_at.to_string(),
        }
    }
}

// ==================== Tauri Commands ====================

/// Get all conversations (with message count)
#[tauri::command]
pub async fn get_conversations(
    db: State<'_, DatabaseConnection>,
) -> Result<Vec<ConversationWithCount>, String> {
    let conversations = conversation::Entity::find()
        .order_by_desc(conversation::Column::UpdatedAt)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    let mut result = Vec::new();

    for conv in conversations {
        // Count messages for this conversation
        let message_count = message::Entity::find()
            .filter(message::Column::ConversationId.eq(conv.id))
            .count(&*db)
            .await
            .map_err(|e| e.to_string())?;

        result.push(ConversationWithCount {
            id: conv.id,
            character_id: conv.character_id,
            prompt_template_id: conv.prompt_template_id,
            user_info: conv.user_info,
            title: conv.title,
            created_at: conv.created_at.and_utc().to_rfc3339(),
            updated_at: conv.updated_at.and_utc().to_rfc3339(),
            message_count: message_count as i64,
        });
    }

    Ok(result)
}

/// Get a specific conversation by ID
#[tauri::command]
pub async fn get_conversation_by_id(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<ConversationResponse, String> {
    let conversation = conversation::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Conversation not found")?;

    Ok(ConversationResponse::from(conversation))
}

/// Get messages for a conversation (latest N messages)
#[tauri::command]
pub async fn get_conversation_messages(
    id: i32,
    limit: Option<i32>,
    db: State<'_, DatabaseConnection>,
) -> Result<Vec<MessageResponse>, String> {
    // Check if conversation exists
    let _conversation = conversation::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Conversation not found")?;

    let limit = limit.unwrap_or(50);

    let messages = message::Entity::find()
        .filter(message::Column::ConversationId.eq(id))
        .order_by_asc(message::Column::CreatedAt)
        .limit(limit as u64)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(messages.into_iter().map(MessageResponse::from).collect())
}

/// Create a new conversation
#[tauri::command(rename_all = "camelCase")]
pub async fn create_conversation(
    conversation_data: ConversationCreate,
    db: State<'_, DatabaseConnection>,
) -> Result<ConversationResponse, String> {
    let new_conversation = conversation::ActiveModel {
        character_id: Set(conversation_data.character_id),
        prompt_template_id: Set(conversation_data.prompt_template_id),
        user_info: Set(conversation_data.user_info),
        title: Set(conversation_data.title),
        ..Default::default()
    };

    let result = new_conversation
        .insert(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(ConversationResponse::from(result))
}

/// Update a conversation (title and user_info only)
#[tauri::command(rename_all = "camelCase")]
pub async fn update_conversation(
    id: i32,
    conversation_data: ConversationUpdate,
    db: State<'_, DatabaseConnection>,
) -> Result<ConversationResponse, String> {
    let existing = conversation::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Conversation not found")?;

    let mut active: conversation::ActiveModel = existing.into();

    if let Some(title) = conversation_data.title {
        active.title = Set(Some(title));
    }

    if let Some(user_info) = conversation_data.user_info {
        active.user_info = Set(Some(user_info));
    }

    let result = active.update(&*db).await.map_err(|e| e.to_string())?;

    Ok(ConversationResponse::from(result))
}

/// Delete a conversation (and its messages)
#[tauri::command]
pub async fn delete_conversation(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<DeleteResult, String> {
    let conversation = conversation::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Conversation not found")?;

    // Delete related messages first
    message::Entity::delete_many()
        .filter(message::Column::ConversationId.eq(id))
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    // Delete conversation
    conversation::Entity::delete_by_id(conversation.id)
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DeleteResult {
        message: "Conversation deleted successfully".to_string(),
    })
}

/// Conversations health check
#[tauri::command]
pub async fn conversations_health() -> Result<HealthResponse, String> {
    Ok(HealthResponse {
        status: "ok".to_string(),
        service: "conversations".to_string(),
    })
}
