use chrono::Duration;
use sea_orm::*;
use serde::{Deserialize, Serialize};
use tauri::State;

use crate::commands::common::DeleteResult;
use crate::commands::utils::{parse_date, to_date_string, to_datetime_string};
use crate::db::models::weight;

// ==================== Request/Response Models ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WeightCreate {
    pub measured_date: String, // YYYY-MM-DD
    pub weight: f64,
    pub note: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WeightUpdate {
    pub measured_date: String,
    pub weight: f64,
    pub note: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct WeightResponse {
    pub id: i32,
    pub measured_date: String,
    pub weight: f64,
    pub note: Option<String>,
    pub created_at: String,
}

impl From<weight::Model> for WeightResponse {
    fn from(weight: weight::Model) -> Self {
        Self {
            id: weight.id,
            measured_date: to_date_string(&weight.measured_date),
            weight: weight.weight,
            note: weight.note,
            created_at: to_datetime_string(&weight.created_at),
        }
    }
}

// ==================== Tauri Commands ====================

/// Get weight records for the last N days
#[tauri::command]
pub async fn get_weights(
    days: Option<i64>,
    db: State<'_, DatabaseConnection>,
) -> Result<Vec<WeightResponse>, String> {
    let days = days.unwrap_or(7);
    let start_date = chrono::Local::now().date_naive() - Duration::days(days);

    let weights = weight::Entity::find()
        .filter(weight::Column::MeasuredDate.gte(start_date))
        .order_by_desc(weight::Column::MeasuredDate)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(weights.into_iter().map(WeightResponse::from).collect())
}

/// Get a specific weight record by ID
#[tauri::command]
pub async fn get_weight_by_id(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<WeightResponse, String> {
    let weight = weight::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Weight record not found")?;

    Ok(WeightResponse::from(weight))
}

/// Get weight record for a specific date
#[tauri::command]
pub async fn get_weight_by_date(
    date: String,
    db: State<'_, DatabaseConnection>,
) -> Result<WeightResponse, String> {
    let target_date = parse_date(&date)?;

    let weight = weight::Entity::find()
        .filter(weight::Column::MeasuredDate.eq(target_date))
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or(format!("No weight record found for {}", date))?;

    Ok(WeightResponse::from(weight))
}

/// Create a new weight record
#[tauri::command(rename_all = "camelCase")]
pub async fn create_weight(
    weight_data: WeightCreate,
    db: State<'_, DatabaseConnection>,
) -> Result<WeightResponse, String> {
    let measured_date = parse_date(&weight_data.measured_date)?;

    // Check if weight for this date already exists
    let existing = weight::Entity::find()
        .filter(weight::Column::MeasuredDate.eq(measured_date))
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?;

    if existing.is_some() {
        return Err(format!(
            "Weight record for {} already exists",
            weight_data.measured_date
        ));
    }

    let new_weight = weight::ActiveModel {
        measured_date: Set(measured_date),
        weight: Set(weight_data.weight),
        note: Set(weight_data.note),
        ..Default::default()
    };

    let result = new_weight
        .insert(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(WeightResponse::from(result))
}

/// Update an existing weight record by ID
#[tauri::command(rename_all = "camelCase")]
pub async fn update_weight(
    id: i32,
    weight_data: WeightUpdate,
    db: State<'_, DatabaseConnection>,
) -> Result<WeightResponse, String> {
    let existing = weight::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Weight record not found")?;

    let new_date = parse_date(&weight_data.measured_date)?;

    // Check if trying to change date to one that already exists
    if new_date != existing.measured_date {
        let duplicate = weight::Entity::find()
            .filter(weight::Column::MeasuredDate.eq(new_date))
            .one(&*db)
            .await
            .map_err(|e| e.to_string())?;

        if duplicate.is_some() {
            return Err(format!(
                "Weight record for {} already exists",
                weight_data.measured_date
            ));
        }
    }

    let mut active: weight::ActiveModel = existing.into();
    active.measured_date = Set(new_date);
    active.weight = Set(weight_data.weight);
    active.note = Set(weight_data.note);

    let result = active.update(&*db).await.map_err(|e| e.to_string())?;

    Ok(WeightResponse::from(result))
}

/// Update weight record for a specific date
#[tauri::command(rename_all = "camelCase")]
pub async fn update_weight_by_date(
    date: String,
    weight_data: WeightUpdate,
    db: State<'_, DatabaseConnection>,
) -> Result<WeightResponse, String> {
    let target_date = parse_date(&date)?;

    let existing = weight::Entity::find()
        .filter(weight::Column::MeasuredDate.eq(target_date))
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or(format!("No weight record found for {}", date))?;

    let new_date = parse_date(&weight_data.measured_date)?;

    // If trying to change the date, check if new date already exists
    if new_date != target_date {
        let duplicate = weight::Entity::find()
            .filter(weight::Column::MeasuredDate.eq(new_date))
            .one(&*db)
            .await
            .map_err(|e| e.to_string())?;

        if duplicate.is_some() {
            return Err(format!(
                "Weight record for {} already exists",
                weight_data.measured_date
            ));
        }
    }

    let mut active: weight::ActiveModel = existing.into();
    active.measured_date = Set(new_date);
    active.weight = Set(weight_data.weight);
    active.note = Set(weight_data.note);

    let result = active.update(&*db).await.map_err(|e| e.to_string())?;

    Ok(WeightResponse::from(result))
}

/// Delete a weight record by ID
#[tauri::command]
pub async fn delete_weight(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<DeleteResult, String> {
    let result = weight::Entity::delete_by_id(id)
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    if result.rows_affected == 0 {
        return Err("Weight record not found".to_string());
    }

    Ok(DeleteResult {
        message: "Weight record deleted successfully".to_string(),
    })
}

/// Delete weight record for a specific date
#[tauri::command]
pub async fn delete_weight_by_date(
    date: String,
    db: State<'_, DatabaseConnection>,
) -> Result<DeleteResult, String> {
    let target_date = parse_date(&date)?;

    let weight = weight::Entity::find()
        .filter(weight::Column::MeasuredDate.eq(target_date))
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or(format!("No weight record found for {}", date))?;

    weight::Entity::delete_by_id(weight.id)
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DeleteResult {
        message: format!("Weight record for {} deleted successfully", date),
    })
}
