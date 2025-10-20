use sea_orm::*;
use serde::{Deserialize, Serialize};
use tauri::State;

use crate::commands::common::DeleteResult;
use crate::commands::utils::{parse_date, to_date_string, to_datetime_string};
use crate::db::models::meal;

// ==================== Request/Response Models ====================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MealCreate {
    pub meal_date: String, // YYYY-MM-DD
    pub meal_type: String,
    pub food_name: String,
    pub calories: Option<i32>,
    pub protein: Option<f64>,
    pub carbs: Option<f64>,
    pub fat: Option<f64>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MealUpdate {
    pub meal_date: String,
    pub meal_type: String,
    pub food_name: String,
    pub calories: Option<i32>,
    pub protein: Option<f64>,
    pub carbs: Option<f64>,
    pub fat: Option<f64>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MealResponse {
    pub id: i32,
    pub meal_date: String,
    pub meal_type: String,
    pub food_name: String,
    pub calories: Option<i32>,
    pub protein: Option<f64>,
    pub carbs: Option<f64>,
    pub fat: Option<f64>,
    pub created_at: String,
}

impl From<meal::Model> for MealResponse {
    fn from(meal: meal::Model) -> Self {
        Self {
            id: meal.id,
            meal_date: to_date_string(&meal.meal_date),
            meal_type: meal.meal_type,
            food_name: meal.food_name,
            calories: meal.calories,
            protein: meal.protein,
            carbs: meal.carbs,
            fat: meal.fat,
            created_at: to_datetime_string(&meal.created_at),
        }
    }
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MealStats {
    pub date: String,
    pub total_calories: i32,
    pub total_protein: f64,
    pub total_carbs: f64,
    pub total_fat: f64,
    pub meal_count: usize,
}

// ==================== Tauri Commands ====================

/// Get all meals or meals for a specific date
#[tauri::command(rename_all = "camelCase")]
pub async fn get_meals(
    meal_date: Option<String>,
    db: State<'_, DatabaseConnection>,
) -> Result<Vec<MealResponse>, String> {
    let mut query = meal::Entity::find();

    if let Some(date_str) = meal_date {
        let date = parse_date(&date_str)?;
        query = query.filter(meal::Column::MealDate.eq(date));
    }

    let meals = query
        .order_by_desc(meal::Column::MealDate)
        .order_by_desc(meal::Column::CreatedAt)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(meals.into_iter().map(MealResponse::from).collect())
}

/// Get a specific meal by ID
#[tauri::command]
pub async fn get_meal_by_id(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<MealResponse, String> {
    let meal = meal::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Meal record not found")?;

    Ok(MealResponse::from(meal))
}

/// Get all meals for a specific date
#[tauri::command]
pub async fn get_meals_by_date(
    date: String,
    db: State<'_, DatabaseConnection>,
) -> Result<Vec<MealResponse>, String> {
    let target_date = parse_date(&date)?;

    let meals = meal::Entity::find()
        .filter(meal::Column::MealDate.eq(target_date))
        .order_by_asc(meal::Column::MealType)
        .order_by_asc(meal::Column::CreatedAt)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(meals.into_iter().map(MealResponse::from).collect())
}

/// Get meal statistics for a specific date
#[tauri::command(rename_all = "camelCase")]
pub async fn get_meal_stats(
    target_date: Option<String>,
    db: State<'_, DatabaseConnection>,
) -> Result<MealStats, String> {
    let target_date = if let Some(date_str) = target_date {
        parse_date(&date_str)?
    } else {
        chrono::Local::now().date_naive()
    };

    let meals = meal::Entity::find()
        .filter(meal::Column::MealDate.eq(target_date))
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    let total_calories: i32 = meals.iter().map(|m| m.calories.unwrap_or(0)).sum();
    let total_protein: f64 = meals.iter().map(|m| m.protein.unwrap_or(0.0)).sum();
    let total_carbs: f64 = meals.iter().map(|m| m.carbs.unwrap_or(0.0)).sum();
    let total_fat: f64 = meals.iter().map(|m| m.fat.unwrap_or(0.0)).sum();

    Ok(MealStats {
        date: target_date.to_string(),
        total_calories,
        total_protein: (total_protein * 10.0).round() / 10.0,
        total_carbs: (total_carbs * 10.0).round() / 10.0,
        total_fat: (total_fat * 10.0).round() / 10.0,
        meal_count: meals.len(),
    })
}

/// Create a new meal record
#[tauri::command]
pub async fn create_meal(
    meal: MealCreate,
    db: State<'_, DatabaseConnection>,
) -> Result<MealResponse, String> {
    let meal_date = parse_date(&meal.meal_date)?;

    let new_meal = meal::ActiveModel {
        meal_date: Set(meal_date),
        meal_type: Set(meal.meal_type),
        food_name: Set(meal.food_name),
        calories: Set(meal.calories),
        protein: Set(meal.protein),
        carbs: Set(meal.carbs),
        fat: Set(meal.fat),
        ..Default::default()
    };

    let result = new_meal
        .insert(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(MealResponse::from(result))
}

/// Update an existing meal record
#[tauri::command]
pub async fn update_meal(
    id: i32,
    meal: MealUpdate,
    db: State<'_, DatabaseConnection>,
) -> Result<MealResponse, String> {
    let existing = meal::Entity::find_by_id(id)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?
        .ok_or("Meal record not found")?;

    let meal_date = parse_date(&meal.meal_date)?;

    let mut active: meal::ActiveModel = existing.into();
    active.meal_date = Set(meal_date);
    active.meal_type = Set(meal.meal_type);
    active.food_name = Set(meal.food_name);
    active.calories = Set(meal.calories);
    active.protein = Set(meal.protein);
    active.carbs = Set(meal.carbs);
    active.fat = Set(meal.fat);

    let result = active.update(&*db).await.map_err(|e| e.to_string())?;

    Ok(MealResponse::from(result))
}

/// Delete a meal record by ID
#[tauri::command]
pub async fn delete_meal(
    id: i32,
    db: State<'_, DatabaseConnection>,
) -> Result<DeleteResult, String> {
    let result = meal::Entity::delete_by_id(id)
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    if result.rows_affected == 0 {
        return Err("Meal record not found".to_string());
    }

    Ok(DeleteResult {
        message: "Meal record deleted successfully".to_string(),
    })
}

/// Delete all meals for a specific date
#[tauri::command]
pub async fn delete_meals_by_date(
    date: String,
    db: State<'_, DatabaseConnection>,
) -> Result<DeleteResult, String> {
    let target_date = parse_date(&date)?;

    let meals = meal::Entity::find()
        .filter(meal::Column::MealDate.eq(target_date))
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    if meals.is_empty() {
        return Err(format!("No meal records found for {}", date));
    }

    let count = meals.len();

    meal::Entity::delete_many()
        .filter(meal::Column::MealDate.eq(target_date))
        .exec(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DeleteResult {
        message: format!("{} meal record(s) deleted for {}", count, date),
    })
}
