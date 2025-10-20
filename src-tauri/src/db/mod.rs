use sea_orm::{Database, DatabaseConnection, DbErr};
use std::fs;
use std::path::PathBuf;

pub mod models;
pub mod sync;
pub mod seed_data;
pub mod schema;

/// Get the application data directory path
/// Returns: %APPDATA%/ai_diet_v2 on Windows, ~/.local/share/ai_diet_v2 on Linux, ~/Library/Application Support/ai_diet_v2 on macOS
pub fn get_app_data_dir() -> Result<PathBuf, String> {
    let data_dir = dirs::data_dir()
        .ok_or("Failed to get system data directory")?;

    let app_dir = data_dir.join("ai_diet_v2");

    Ok(app_dir)
}

/// Get the database file path in AppData
/// Returns: %APPDATA%/ai_diet_v2/ai_diet.db
pub fn get_db_path() -> Result<PathBuf, String> {
    let app_dir = get_app_data_dir()?;
    Ok(app_dir.join("ai_diet.db"))
}

/// Get the old database path (project root)
/// This is used for migration from old location to AppData
fn get_old_db_path() -> PathBuf {
    // Tauri dev mode runs from src-tauri directory
    // Go up one level to project root
    let mut path = std::env::current_dir().expect("Failed to get current directory");
    path.push("..");  // Go to project root
    path.join("ai_diet.db")
}

/// Migrate old database from project root to AppData
/// If old DB exists and new DB doesn't, copy it
fn migrate_old_db() -> Result<bool, String> {
    let old_db_path = get_old_db_path();
    let new_db_path = get_db_path()?;

    // If old DB exists and new DB doesn't exist
    if old_db_path.exists() && !new_db_path.exists() {
        println!("🔄 Migrating database from {} to {}", old_db_path.display(), new_db_path.display());

        fs::copy(&old_db_path, &new_db_path)
            .map_err(|e| format!("Failed to migrate database: {}", e))?;

        println!("✅ Database migrated successfully");
        return Ok(true);
    }

    Ok(false)
}

/// Initialize database connection
///
/// Connects to SQLite database at AppData/ai_diet_v2/ai_diet.db
/// Creates the file if it doesn't exist (mode=rwc)
/// Migrates old database from project root if it exists
pub async fn init_db() -> Result<DatabaseConnection, DbErr> {
    // Debug: Print current working directory
    let current_dir = std::env::current_dir().expect("Failed to get current directory");
    println!("🔍 Current working directory: {}", current_dir.display());

    // Get AppData directory path
    let app_dir = get_app_data_dir()
        .map_err(|e| DbErr::Custom(format!("Failed to get app data directory: {}", e)))?;

    println!("🔍 Application data directory: {}", app_dir.display());

    // Ensure AppData directory exists
    if !app_dir.exists() {
        fs::create_dir_all(&app_dir)
            .map_err(|e| DbErr::Custom(format!("Failed to create app data directory: {}", e)))?;
        println!("📁 Created app data directory: {}", app_dir.display());
    }

    // Get database file path
    let db_path = get_db_path()
        .map_err(|e| DbErr::Custom(format!("Failed to get database path: {}", e)))?;

    println!("🔍 Database path: {}", db_path.display());

    // Migrate old database if it exists
    migrate_old_db()
        .map_err(|e| DbErr::Custom(format!("Failed to migrate old database: {}", e)))?;

    // Check sync folder for newer database (if configured)
    if let Ok(Some(sync_db_path)) = sync::load_from_sync_folder() {
        println!("📥 Importing newer database from sync folder");
        sync::import_db(&sync_db_path)
            .map_err(|e| DbErr::Custom(format!("Failed to import from sync folder: {}", e)))?;
    }

    // Build SQLite connection URL
    // Use absolute path with mode=rwc (read-write-create)
    let db_url = format!("sqlite://{}?mode=rwc", db_path.display());
    println!("🔍 Database URL: {}", db_url);

    // Connect to database
    let db = Database::connect(&db_url).await?;

    println!("✅ Database connected successfully");

    // Initialize database schema (create tables if they don't exist)
    schema::init_schema(&db).await?;

    // Insert seed data on first run
    if seed_data::is_first_run(&db).await? {
        println!("🌱 First run detected, inserting seed data...");
        seed_data::insert_seed_data(&db).await?;
    }

    Ok(db)
}
