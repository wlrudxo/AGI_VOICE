#![allow(non_snake_case)]

use sea_orm::*;
use serde::{Deserialize, Serialize};
use tauri::State;

use chrono::Utc;
use crate::commands::common::{DeleteResult, HealthResponse};
use crate::db::models::character;
use crate::db::AiChatDb;

// ==================== Request/Response Models ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CharacterCreate {
    pub name: String,
    pub prompt_content: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CharacterUpdate {
    pub name: String,
    pub prompt_content: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CharacterResponse {
    pub id: i32,
    pub name: String,
    pub prompt_content: String,
    pub created_at: String,
    pub updated_at: String,
}

impl From<character::Model> for CharacterResponse {
    fn from(character: character::Model) -> Self {
        Self {
            id: character.id,
            name: character.name,
            prompt_content: character.prompt_content,
            created_at: character.created_at.to_string(),
            updated_at: character.updated_at.to_string(),
        }
    }
}

// ==================== Tauri Commands ====================

/// Get all characters
#[tauri::command]
pub async fn get_characters(
    db: State<'_, AiChatDb>,
) -> Result<Vec<CharacterResponse>, String> {
    let characters = character::Entity::find()
        .all(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(characters
        .into_iter()
        .map(CharacterResponse::from)
        .collect())
}

/// Get a specific character by ID
#[tauri::command]
pub async fn get_character_by_id(
    id: i32,
    db: State<'_, AiChatDb>,
) -> Result<CharacterResponse, String> {
    let character = character::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Character not found")?;

    Ok(CharacterResponse::from(character))
}

/// Create a new character
#[tauri::command]
pub async fn create_character(
    characterData: CharacterCreate,
    db: State<'_, AiChatDb>,
) -> Result<CharacterResponse, String> {
    let now = Utc::now().naive_utc();

    let new_character = character::ActiveModel {
        name: Set(characterData.name),
        prompt_content: Set(characterData.prompt_content),
        created_at: Set(now),
        updated_at: Set(now),
        ..Default::default()
    };

    let result = new_character
        .insert(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(CharacterResponse::from(result))
}

/// Update an existing character
#[tauri::command]
pub async fn update_character(
    id: i32,
    characterData: CharacterUpdate,
    db: State<'_, AiChatDb>,
) -> Result<CharacterResponse, String> {
    let now = Utc::now().naive_utc();

    let existing = character::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Character not found")?;

    let mut active: character::ActiveModel = existing.into();
    active.name = Set(characterData.name);
    active.prompt_content = Set(characterData.prompt_content);
    active.updated_at = Set(now);

    let result = active.update(&db.0).await.map_err(|e| e.to_string())?;

    Ok(CharacterResponse::from(result))
}

/// Delete a character
#[tauri::command]
pub async fn delete_character(
    id: i32,
    db: State<'_, AiChatDb>,
) -> Result<DeleteResult, String> {
    let character = character::Entity::find_by_id(id)
        .one(&db.0)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Character not found")?;

    character::Entity::delete_by_id(character.id)
        .exec(&db.0)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DeleteResult {
        message: "Character deleted successfully".to_string(),
    })
}

/// Characters health check
#[tauri::command]
pub async fn characters_health() -> Result<HealthResponse, String> {
    Ok(HealthResponse {
        status: "ok".to_string(),
        service: "characters".to_string(),
    })
}
