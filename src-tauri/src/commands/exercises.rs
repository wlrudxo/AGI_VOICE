use sea_orm::*;
use serde::{Deserialize, Serialize};
use tauri::State;

use crate::commands::common::DeleteResult;
use crate::commands::utils::{parse_date, to_date_string, to_datetime_string};
use crate::db::models::exercise;

// ==================== Request/Response Models ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ExerciseCreate {
    pub exercise_date: String, // YYYY-MM-DD
    pub exercise_name: String,
    pub duration: i32, // minutes
    pub calories: Option<i32>,
    pub category: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ExerciseUpdate {
    pub exercise_date: String,
    pub exercise_name: String,
    pub duration: i32,
    pub calories: Option<i32>,
    pub category: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ExerciseResponse {
    pub id: i32,
    pub exercise_date: String,
    pub exercise_name: String,
    pub duration: i32,
    pub calories: Option<i32>,
    pub category: Option<String>,
    pub created_at: String,
}

impl From<exercise::Model> for ExerciseResponse {
    fn from(exercise: exercise::Model) -> Self {
        Self {
            id: exercise.id,
            exercise_date: to_date_string(&exercise.exercise_date),
            exercise_name: exercise.exercise_name,
            duration: exercise.duration,
            calories: exercise.calories,
            category: exercise.category,
            created_at: to_datetime_string(&exercise.created_at),
        }
    }
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ExerciseStats {
    pub date: String,
    pub total_duration: i32,
    pub total_calories: i32,
    pub exercise_count: usize,
}

// ==================== Tauri Commands ====================

/// Get all exercises or exercises for a specific date
#[tauri::command(rename_all = "camelCase")]
pub async fn get_exercises(
    exercise_date: Option<String>,
    db: State<'_, DatabaseConnection>,
) -> Result<Vec<ExerciseResponse>, String> {
    let mut query = exercise::Entity::find();

    if let Some(date_str) = exercise_date {
        let date = parse_date(&date_str)?;
        query = query.filter(exercise::Column::ExerciseDate.eq(date));
    }

    let exercises = query
        .order_by_desc(exercise::Column::ExerciseDate)
        .order_by_desc(exercise::Column::CreatedAt)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(exercises.into_iter().map(ExerciseResponse::from).collect())
}

/// Get a specific exercise by ID
#[tauri::command]
pub async fn get_exercise_by_id(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<ExerciseResponse, String> {
    let exercise = exercise::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Exercise record not found")?;

    Ok(ExerciseResponse::from(exercise))
}

/// Get all exercises for a specific date
#[tauri::command]
pub async fn get_exercises_by_date(
    date: String,
    db: State<'_, DatabaseConnection>,
) -> Result<Vec<ExerciseResponse>, String> {
    let target_date = parse_date(&date)?;

    let exercises = exercise::Entity::find()
        .filter(exercise::Column::ExerciseDate.eq(target_date))
        .order_by_asc(exercise::Column::CreatedAt)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(exercises.into_iter().map(ExerciseResponse::from).collect())
}

/// Get exercise statistics for a specific date
#[tauri::command]
pub async fn get_exercise_stats(
    date: Option<String>,
    db: State<'_, DatabaseConnection>,
) -> Result<ExerciseStats, String> {
    let target_date = if let Some(date_str) = date {
        parse_date(&date_str)?
    } else {
        chrono::Local::now().date_naive()
    };

    let exercises = exercise::Entity::find()
        .filter(exercise::Column::ExerciseDate.eq(target_date))
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    let total_duration: i32 = exercises.iter().map(|e| e.duration).sum();
    let total_calories: i32 = exercises.iter().map(|e| e.calories.unwrap_or(0)).sum();

    Ok(ExerciseStats {
        date: target_date.to_string(),
        total_duration,
        total_calories,
        exercise_count: exercises.len(),
    })
}

/// Create a new exercise record
#[tauri::command]
pub async fn create_exercise(
    exercise: ExerciseCreate,
    db: State<'_, DatabaseConnection>,
) -> Result<ExerciseResponse, String> {
    let exercise_date = parse_date(&exercise.exercise_date)?;

    let new_exercise = exercise::ActiveModel {
        exercise_date: Set(exercise_date),
        exercise_name: Set(exercise.exercise_name),
        duration: Set(exercise.duration),
        calories: Set(exercise.calories),
        category: Set(exercise.category),
        ..Default::default()
    };

    let result = new_exercise
        .insert(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(ExerciseResponse::from(result))
}

/// Update an existing exercise record
#[tauri::command]
pub async fn update_exercise(
    id: i32,
    exercise: ExerciseUpdate,
    db: State<'_, DatabaseConnection>,
) -> Result<ExerciseResponse, String> {
    let existing = exercise::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Exercise record not found")?;

    let exercise_date = parse_date(&exercise.exercise_date)?;

    let mut active: exercise::ActiveModel = existing.into();
    active.exercise_date = Set(exercise_date);
    active.exercise_name = Set(exercise.exercise_name);
    active.duration = Set(exercise.duration);
    active.calories = Set(exercise.calories);
    active.category = Set(exercise.category);

    let result = active.update(&*db).await.map_err(|e| e.to_string())?;

    Ok(ExerciseResponse::from(result))
}

/// Delete an exercise record by ID
#[tauri::command]
pub async fn delete_exercise(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<DeleteResult, String> {
    let result = exercise::Entity::delete_by_id(id)
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    if result.rows_affected == 0 {
        return Err("Exercise record not found".to_string());
    }

    Ok(DeleteResult {
        message: "Exercise record deleted successfully".to_string(),
    })
}

/// Delete all exercises for a specific date
#[tauri::command]
pub async fn delete_exercises_by_date(
    date: String,
    db: State<'_, DatabaseConnection>,
) -> Result<DeleteResult, String> {
    let target_date = parse_date(&date)?;

    let exercises = exercise::Entity::find()
        .filter(exercise::Column::ExerciseDate.eq(target_date))
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    if exercises.is_empty() {
        return Err(format!("No exercise records found for {}", date));
    }

    let count = exercises.len();

    exercise::Entity::delete_many()
        .filter(exercise::Column::ExerciseDate.eq(target_date))
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DeleteResult {
        message: format!("{} exercise record(s) deleted for {}", count, date),
    })
}
