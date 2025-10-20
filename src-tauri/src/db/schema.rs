// Database schema initialization
// Creates all tables if they don't exist

use sea_orm::{ConnectionTrait, DatabaseConnection, DbErr, Statement};

/// Initialize database schema
/// Creates all tables if they don't exist
pub async fn init_schema(db: &DatabaseConnection) -> Result<(), DbErr> {
    let backend = db.get_database_backend();

    // Create weights table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measured_date TEXT NOT NULL UNIQUE,
            weight REAL NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    // Create meals table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_name TEXT NOT NULL,
            calories INTEGER,
            protein REAL,
            carbs REAL,
            fat REAL,
            created_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    // Create exercises table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_date TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            duration INTEGER NOT NULL,
            calories INTEGER,
            category TEXT,
            created_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    // Create ai_missions table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS ai_missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            ai_comment TEXT,
            completion_comment TEXT,
            deadline TEXT,
            created_at TEXT NOT NULL,
            start_date TEXT,
            completed_at TEXT
        )
        "#.to_string(),
    )).await?;

    // Create prompt_templates table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    // Create characters table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            prompt_content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    // Create conversations table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            prompt_template_id INTEGER NOT NULL,
            user_info TEXT,
            title TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    // Create messages table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    // Create command_templates table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS command_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    println!("✅ Database schema initialized successfully");

    Ok(())
}
