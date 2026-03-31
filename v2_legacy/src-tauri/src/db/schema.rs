// Database schema initialization
// Creates all tables if they don't exist

use sea_orm::{ConnectionTrait, DatabaseConnection, DbErr, Statement};

/// Initialize database schema
/// Creates all tables if they don't exist
pub async fn init_schema(db: &DatabaseConnection) -> Result<(), DbErr> {
    let backend = db.get_database_backend();

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
