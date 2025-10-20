#![allow(non_snake_case)]

use sea_orm::*;
use serde::{Deserialize, Serialize};
use tauri::State;

use crate::commands::common::{DeleteResult, HealthResponse};
use crate::db::models::prompt_template;
use crate::db::AiChatDb;

// ==================== Request/Response Models ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PromptTemplateCreate {
    pub name: String,
    pub content: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PromptTemplateUpdate {
    pub name: String,
    pub content: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PromptTemplateResponse {
    pub id: i32,
    pub name: String,
    pub content: String,
    pub created_at: String,
    pub updated_at: String,
}

impl From<prompt_template::Model> for PromptTemplateResponse {
    fn from(template: prompt_template::Model) -> Self {
        Self {
            id: template.id,
            name: template.name,
            content: template.content,
            created_at: template.created_at.to_string(),
            updated_at: template.updated_at.to_string(),
        }
    }
}

// ==================== Tauri Commands ====================

/// Get all prompt templates
#[tauri::command]
pub async fn get_prompt_templates(
    db: State<'_, AiChatDb>,
) -> Result<Vec<PromptTemplateResponse>, String> {
    let templates = prompt_template::Entity::find()
        .all(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(templates
        .into_iter()
        .map(PromptTemplateResponse::from)
        .collect())
}

/// Get a specific prompt template by ID
#[tauri::command]
pub async fn get_prompt_template_by_id(
    id: i32,
    db: State<'_, AiChatDb>,
) -> Result<PromptTemplateResponse, String> {
    let template = prompt_template::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Prompt template not found")?;

    Ok(PromptTemplateResponse::from(template))
}

/// Create a new prompt template
#[tauri::command]
pub async fn create_prompt_template(
    templateData: PromptTemplateCreate,
    db: State<'_, AiChatDb>,
) -> Result<PromptTemplateResponse, String> {
    let new_template = prompt_template::ActiveModel {
        name: Set(templateData.name),
        content: Set(templateData.content),
        ..Default::default()
    };

    let result = new_template
        .insert(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(PromptTemplateResponse::from(result))
}

/// Update an existing prompt template
#[tauri::command]
pub async fn update_prompt_template(
    id: i32,
    templateData: PromptTemplateUpdate,
    db: State<'_, AiChatDb>,
) -> Result<PromptTemplateResponse, String> {
    let existing = prompt_template::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Prompt template not found")?;

    let mut active: prompt_template::ActiveModel = existing.into();
    active.name = Set(templateData.name);
    active.content = Set(templateData.content);

    let result = active.update(&db.0).await.map_err(|e| e.to_string())?;

    Ok(PromptTemplateResponse::from(result))
}

/// Delete a prompt template
#[tauri::command]
pub async fn delete_prompt_template(
    id: i32,
    db: State<'_, AiChatDb>,
) -> Result<DeleteResult, String> {
    let template = prompt_template::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Prompt template not found")?;

    prompt_template::Entity::delete_by_id(template.id)
        .exec(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DeleteResult {
        message: "Prompt template deleted successfully".to_string(),
    })
}

/// Prompt templates health check
#[tauri::command]
pub async fn prompt_templates_health() -> Result<HealthResponse, String> {
    Ok(HealthResponse {
        status: "ok".to_string(),
        service: "prompt_templates".to_string(),
    })
}
