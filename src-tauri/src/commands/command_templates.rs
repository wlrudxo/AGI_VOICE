use sea_orm::*;
use serde::{Deserialize, Serialize};
use tauri::State;

use chrono::Utc;
use crate::commands::common::{DeleteResult, HealthResponse};
use crate::db::models::command_template;
use crate::db::AiChatDb;

// ==================== Request/Response Models ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CommandTemplateCreate {
    pub name: String,
    pub content: String,
    pub is_active: i32,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CommandTemplateUpdate {
    pub name: String,
    pub content: String,
    pub is_active: i32,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CommandTemplateResponse {
    pub id: i32,
    pub name: String,
    pub content: String,
    pub is_active: i32,
    pub created_at: String,
    pub updated_at: String,
}

impl From<command_template::Model> for CommandTemplateResponse {
    fn from(template: command_template::Model) -> Self {
        Self {
            id: template.id,
            name: template.name,
            content: template.content,
            is_active: template.is_active,
            created_at: template.created_at.to_string(),
            updated_at: template.updated_at.to_string(),
        }
    }
}

// ==================== Tauri Commands ====================

/// Get all command templates (optionally filter by is_active)
#[tauri::command]
pub async fn get_command_templates(
    is_active: Option<i32>,
    db: State<'_, AiChatDb>,
) -> Result<Vec<CommandTemplateResponse>, String> {
    let mut query = command_template::Entity::find();

    if let Some(active_status) = is_active {
        query = query.filter(command_template::Column::IsActive.eq(active_status));
    }

    let templates = query
        .order_by_desc(command_template::Column::CreatedAt)
        .all(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(templates
        .into_iter()
        .map(CommandTemplateResponse::from)
        .collect())
}

/// Get a specific command template by ID
#[tauri::command]
pub async fn get_command_template_by_id(
    id: i32,
    db: State<'_, AiChatDb>,
) -> Result<CommandTemplateResponse, String> {
    let template = command_template::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Command template not found")?;

    Ok(CommandTemplateResponse::from(template))
}

/// Create a new command template
#[tauri::command(rename_all = "camelCase")]
pub async fn create_command_template(
    template_data: CommandTemplateCreate,
    db: State<'_, AiChatDb>,
) -> Result<CommandTemplateResponse, String> {
    let now = Utc::now().naive_utc();

    let new_template = command_template::ActiveModel {
        name: Set(template_data.name),
        content: Set(template_data.content),
        is_active: Set(template_data.is_active),
        created_at: Set(now),
        updated_at: Set(now),
        ..Default::default()
    };

    let result = new_template
        .insert(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(CommandTemplateResponse::from(result))
}

/// Update an existing command template
#[tauri::command(rename_all = "camelCase")]
pub async fn update_command_template(
    id: i32,
    template_data: CommandTemplateUpdate,
    db: State<'_, AiChatDb>,
) -> Result<CommandTemplateResponse, String> {
    let now = Utc::now().naive_utc();

    let existing = command_template::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Command template not found")?;

    let mut active: command_template::ActiveModel = existing.into();
    active.name = Set(template_data.name);
    active.content = Set(template_data.content);
    active.is_active = Set(template_data.is_active);
    active.updated_at = Set(now);

    let result = active.update(&db.0).await.map_err(|e| e.to_string())?;

    Ok(CommandTemplateResponse::from(result))
}

/// Toggle command template active status
#[tauri::command]
pub async fn toggle_command_template(
    id: i32,
    db: State<'_, AiChatDb>,
) -> Result<CommandTemplateResponse, String> {
    let existing = command_template::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Command template not found")?;

    let mut active: command_template::ActiveModel = existing.clone().into();

    // Toggle: 0 -> 1, 1 -> 0
    active.is_active = Set(if existing.is_active == 0 { 1 } else { 0 });

    let result = active.update(&db.0).await.map_err(|e| e.to_string())?;

    Ok(CommandTemplateResponse::from(result))
}

/// Delete a command template
#[tauri::command]
pub async fn delete_command_template(
    id: i32,
    db: State<'_, AiChatDb>,
) -> Result<DeleteResult, String> {
    let template = command_template::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Command template not found")?;

    command_template::Entity::delete_by_id(template.id)
        .exec(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DeleteResult {
        message: "Command template deleted successfully".to_string(),
    })
}

/// Command templates health check
#[tauri::command]
pub async fn command_templates_health() -> Result<HealthResponse, String> {
    Ok(HealthResponse {
        status: "ok".to_string(),
        service: "command_templates".to_string(),
    })
}
