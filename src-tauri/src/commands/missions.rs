use sea_orm::*;
use serde::{Deserialize, Serialize};
use tauri::State;

use crate::commands::common::DeleteResult;
use crate::commands::utils::{parse_date, to_date_string, to_datetime_string};
use crate::db::models::ai_mission;

// ==================== Request/Response Models ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MissionCreate {
    pub mission_title: String,
    pub description: Option<String>,
    pub ai_comment: Option<String>,
    pub deadline: Option<String>, // YYYY-MM-DD
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MissionUpdate {
    pub mission_title: String,
    pub description: Option<String>,
    pub ai_comment: Option<String>,
    pub deadline: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MissionStatusUpdate {
    pub status: String, // pending/in_progress/completed/failed
    pub completion_comment: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MissionResponse {
    pub id: i32,
    pub mission_title: String,
    pub description: Option<String>,
    pub status: String,
    pub ai_comment: Option<String>,
    pub completion_comment: Option<String>,
    pub deadline: Option<String>,
    pub created_at: String,
    pub start_date: Option<String>,
    pub completed_at: Option<String>,
}

impl From<ai_mission::Model> for MissionResponse {
    fn from(mission: ai_mission::Model) -> Self {
        Self {
            id: mission.id,
            mission_title: mission.mission_title,
            description: mission.description,
            status: mission.status,
            ai_comment: mission.ai_comment,
            completion_comment: mission.completion_comment,
            deadline: mission.deadline.map(|d| to_date_string(&d)),
            created_at: to_datetime_string(&mission.created_at),
            start_date: mission.start_date.map(|dt| to_datetime_string(&dt)),
            completed_at: mission.completed_at.map(|dt| to_datetime_string(&dt)),
        }
    }
}

// ==================== Stats Response ====================

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MissionStats {
    pub total: i64,
    pub completed: i64,
    pub failed: i64,
    pub in_progress: i64,
    pub pending: i64,
    pub achievement_rate: f64,
}

// ==================== Tauri Commands ====================

/// Get mission statistics
#[tauri::command]
pub async fn get_mission_stats(
    db: State<'_, DatabaseConnection>,
) -> Result<MissionStats, String> {
    let total = ai_mission::Entity::find()
        .count(&*db)
        .await
        .map_err(|e| e.to_string())? as i64;

    let completed = ai_mission::Entity::find()
        .filter(ai_mission::Column::Status.eq("completed"))
        .count(&*db)
        .await
        .map_err(|e| e.to_string())? as i64;

    let failed = ai_mission::Entity::find()
        .filter(ai_mission::Column::Status.eq("failed"))
        .count(&*db)
        .await
        .map_err(|e| e.to_string())? as i64;

    let in_progress = ai_mission::Entity::find()
        .filter(ai_mission::Column::Status.eq("in_progress"))
        .count(&*db)
        .await
        .map_err(|e| e.to_string())? as i64;

    let pending = ai_mission::Entity::find()
        .filter(ai_mission::Column::Status.eq("pending"))
        .count(&*db)
        .await
        .map_err(|e| e.to_string())? as i64;

    let achievement_rate = if total > 0 {
        (completed as f64 / total as f64 * 100.0 * 10.0).round() / 10.0
    } else {
        0.0
    };

    Ok(MissionStats {
        total,
        completed,
        failed,
        in_progress,
        pending,
        achievement_rate,
    })
}

/// Get all missions, optionally filtered by status
#[tauri::command]
pub async fn get_missions(
    status: Option<String>,
    db: State<'_, DatabaseConnection>,
) -> Result<Vec<MissionResponse>, String> {
    let mut query = ai_mission::Entity::find();

    if let Some(status_filter) = status {
        query = query.filter(ai_mission::Column::Status.eq(status_filter));
    }

    let missions = query
        .order_by_desc(ai_mission::Column::CreatedAt)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(missions.into_iter().map(MissionResponse::from).collect())
}

/// Get a specific mission by ID
#[tauri::command]
pub async fn get_mission_by_id(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<MissionResponse, String> {
    let mission = ai_mission::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Mission not found")?;

    Ok(MissionResponse::from(mission))
}

/// Create a new mission (always starts as pending)
#[tauri::command]
pub async fn create_mission(
    mission: MissionCreate,
    db: State<'_, DatabaseConnection>,
) -> Result<MissionResponse, String> {
    let deadline = if let Some(date_str) = mission.deadline {
        Some(parse_date(&date_str)?)
    } else {
        None
    };

    let new_mission = ai_mission::ActiveModel {
        mission_title: Set(mission.mission_title),
        description: Set(mission.description),
        status: Set("pending".to_string()), // Always start as pending
        ai_comment: Set(mission.ai_comment),
        deadline: Set(deadline),
        ..Default::default()
    };

    let result = new_mission
        .insert(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(MissionResponse::from(result))
}

/// Update mission details (not status)
#[tauri::command]
pub async fn update_mission(
    id: i32,
    mission: MissionUpdate,
    db: State<'_, DatabaseConnection>,
) -> Result<MissionResponse, String> {
    let existing = ai_mission::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Mission not found")?;

    let deadline = if let Some(date_str) = mission.deadline {
        Some(parse_date(&date_str)?)
    } else {
        None
    };

    let mut active: ai_mission::ActiveModel = existing.into();
    active.mission_title = Set(mission.mission_title);
    active.description = Set(mission.description);
    active.ai_comment = Set(mission.ai_comment);
    active.deadline = Set(deadline);

    let result = active.update(&*db).await.map_err(|e| e.to_string())?;

    Ok(MissionResponse::from(result))
}

/// Update mission status (with automatic timestamp management)
#[tauri::command(rename_all = "camelCase")]
pub async fn update_mission_status(
    id: i32,
    status_update: MissionStatusUpdate,
    db: State<'_, DatabaseConnection>,
) -> Result<MissionResponse, String> {
    let existing = ai_mission::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Mission not found")?;

    let mut active: ai_mission::ActiveModel = existing.clone().into();

    // Set start_date when status changes to in_progress
    if status_update.status == "in_progress" && existing.start_date.is_none() {
        active.start_date = Set(Some(chrono::Local::now().naive_local()));
    }

    active.status = Set(status_update.status.clone());

    if let Some(comment) = status_update.completion_comment {
        active.completion_comment = Set(Some(comment));
    }

    // Set completed_at when status changes to completed or failed
    if status_update.status == "completed" || status_update.status == "failed" {
        active.completed_at = Set(Some(chrono::Local::now().naive_local()));
    }

    let result = active.update(&*db).await.map_err(|e| e.to_string())?;

    Ok(MissionResponse::from(result))
}

/// Delete a mission
#[tauri::command]
pub async fn delete_mission(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<DeleteResult, String> {
    let result = ai_mission::Entity::delete_by_id(id)
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    if result.rows_affected == 0 {
        return Err("Mission not found".to_string());
    }

    Ok(DeleteResult {
        message: "Mission deleted successfully".to_string(),
    })
}
