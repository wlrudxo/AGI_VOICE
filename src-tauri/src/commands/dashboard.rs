use chrono::{Duration, Local, NaiveDate, Timelike};
use sea_orm::*;
use serde::Serialize;
use std::collections::HashMap;
use tauri::State;

use crate::commands::utils::parse_date;
use crate::db::models::{ai_mission, exercise, meal, weight};

// Re-use response types from other modules
use super::exercises::ExerciseResponse;
use super::meals::MealResponse;
use super::missions::MissionResponse;

// ==================== Response Models ====================

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DashboardWeightData {
    pub measured_date: String,
    pub weight: f64,
    pub note: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DashboardMealsData {
    pub total_calories: i32,
    pub total_protein: f64,
    pub total_carbs: f64,
    pub total_fat: f64,
    pub meal_count: usize,
    pub meals: Vec<MealResponse>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DashboardExercisesData {
    pub total_duration: i32,
    pub total_calories: i32,
    pub exercise_count: usize,
    pub exercises: Vec<ExerciseResponse>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DashboardTodayResponse {
    pub date: String,
    pub weight: Option<DashboardWeightData>,
    pub meals: DashboardMealsData,
    pub exercises: DashboardExercisesData,
    pub current_missions: Vec<MissionResponse>,
}

// ==================== Week Response Models ====================

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DashboardWeekMealsData {
    pub items: Vec<String>,
    pub total_calories: i32,
    pub by_type: HashMap<String, Vec<String>>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DashboardWeekExercisesData {
    pub items: Vec<String>,
    pub total_duration: i32,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DashboardDayData {
    pub date: String,
    pub weight: Option<f64>,
    pub meals: DashboardWeekMealsData,
    pub exercises: DashboardWeekExercisesData,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DashboardWeekResponse {
    pub start_date: String,
    pub end_date: String,
    pub days: i32,
    pub daily_data: Vec<DashboardDayData>,
}

// ==================== Helper Functions ====================

/// Get effective today (considering 4am cutoff)
fn get_effective_today() -> NaiveDate {
    let now = Local::now();
    if now.hour() < 4 {
        // 0am-4am: treat as previous day
        (now - Duration::days(1)).date_naive()
    } else {
        now.date_naive()
    }
}

// ==================== Tauri Commands ====================

/// Get today's dashboard summary
#[tauri::command(rename_all = "camelCase")]
pub async fn get_dashboard(
    target_date: Option<String>,
    db: State<'_, DatabaseConnection>,
) -> Result<DashboardTodayResponse, String> {
    let target_date = if let Some(date_str) = target_date {
        parse_date(&date_str)?
    } else {
        Local::now().date_naive()
    };

    // Weight - most recent weight (on or before target_date)
    let weight_record = weight::Entity::find()
        .filter(weight::Column::MeasuredDate.lte(target_date))
        .order_by_desc(weight::Column::MeasuredDate)
        .one(&*db)
        .await
        .map_err(|e| e.to_string())?;

    let weight_data = weight_record.map(|w| DashboardWeightData {
        measured_date: w.measured_date.to_string(),
        weight: w.weight,
        note: w.note,
    });

    // Meals
    let meals = meal::Entity::find()
        .filter(meal::Column::MealDate.eq(target_date))
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    let total_calories: i32 = meals.iter().map(|m| m.calories.unwrap_or(0)).sum();
    let total_protein: f64 = meals.iter().map(|m| m.protein.unwrap_or(0.0)).sum();
    let total_carbs: f64 = meals.iter().map(|m| m.carbs.unwrap_or(0.0)).sum();
    let total_fat: f64 = meals.iter().map(|m| m.fat.unwrap_or(0.0)).sum();

    let meals_data = DashboardMealsData {
        total_calories,
        total_protein,
        total_carbs,
        total_fat,
        meal_count: meals.len(),
        meals: meals.into_iter().map(MealResponse::from).collect(),
    };

    // Exercises
    let exercises = exercise::Entity::find()
        .filter(exercise::Column::ExerciseDate.eq(target_date))
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    let total_duration: i32 = exercises.iter().map(|e| e.duration).sum();
    let total_ex_calories: i32 = exercises.iter().map(|e| e.calories.unwrap_or(0)).sum();

    let exercises_data = DashboardExercisesData {
        total_duration,
        total_calories: total_ex_calories,
        exercise_count: exercises.len(),
        exercises: exercises.into_iter().map(ExerciseResponse::from).collect(),
    };

    // Current missions (pending and in_progress)
    let current_missions = ai_mission::Entity::find()
        .filter(ai_mission::Column::Status.is_in(["pending", "in_progress"]))
        .order_by_asc(ai_mission::Column::Deadline)
        .all(&*db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DashboardTodayResponse {
        date: target_date.to_string(),
        weight: weight_data,
        meals: meals_data,
        exercises: exercises_data,
        current_missions: current_missions
            .into_iter()
            .map(MissionResponse::from)
            .collect(),
    })
}

/// Get weekly dashboard summary (date-based aggregated data)
#[tauri::command]
pub async fn get_weekly_dashboard(
    days: Option<i32>,
    db: State<'_, DatabaseConnection>,
) -> Result<DashboardWeekResponse, String> {
    let days = days.unwrap_or(7);
    let end_date = get_effective_today();
    let start_date = end_date - Duration::days((days - 1) as i64);

    let mut daily_data = Vec::new();

    for i in 0..days {
        let current_date = start_date + Duration::days(i as i64);

        // Weight
        let weight_record = weight::Entity::find()
            .filter(weight::Column::MeasuredDate.eq(current_date))
            .one(&*db)
            .await
            .map_err(|e| e.to_string())?;

        let weight_value = weight_record.map(|w| w.weight);

        // Meals
        let meals = meal::Entity::find()
            .filter(meal::Column::MealDate.eq(current_date))
            .all(&*db)
            .await
            .map_err(|e| e.to_string())?;

        let meal_items: Vec<String> = meals.iter().map(|m| m.food_name.clone()).collect();
        let meal_total_calories: i32 = meals.iter().map(|m| m.calories.unwrap_or(0)).sum();

        // Meal type별 분류
        let mut meal_by_type: HashMap<String, Vec<String>> = HashMap::new();
        for meal in &meals {
            meal_by_type
                .entry(meal.meal_type.clone())
                .or_insert_with(Vec::new)
                .push(meal.food_name.clone());
        }

        // Exercises
        let exercises = exercise::Entity::find()
            .filter(exercise::Column::ExerciseDate.eq(current_date))
            .all(&*db)
            .await
            .map_err(|e| e.to_string())?;

        let exercise_items: Vec<String> =
            exercises.iter().map(|e| e.exercise_name.clone()).collect();
        let exercise_total_duration: i32 = exercises.iter().map(|e| e.duration).sum();

        daily_data.push(DashboardDayData {
            date: current_date.to_string(),
            weight: weight_value,
            meals: DashboardWeekMealsData {
                items: meal_items,
                total_calories: meal_total_calories,
                by_type: meal_by_type,
            },
            exercises: DashboardWeekExercisesData {
                items: exercise_items,
                total_duration: exercise_total_duration,
            },
        });
    }

    Ok(DashboardWeekResponse {
        start_date: start_date.to_string(),
        end_date: end_date.to_string(),
        days,
        daily_data,
    })
}
