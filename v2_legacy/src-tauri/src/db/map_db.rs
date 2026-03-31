use sea_orm::{ConnectionTrait, Database, DatabaseConnection, DbErr, Statement};
use std::fs;
use std::path::PathBuf;

/// Get sumo_maps.db path (in app data directory)
pub fn get_map_db_path() -> Result<PathBuf, String> {
    let app_dir = crate::db::get_app_data_dir()?;
    Ok(app_dir.join("sumo_maps.db"))
}

/// Initialize SUMO maps database
pub async fn init_map_db() -> Result<DatabaseConnection, DbErr> {
    // Get AppData directory
    let app_dir = crate::db::get_app_data_dir()
        .map_err(|e| DbErr::Custom(format!("Failed to get app data directory: {}", e)))?;

    // Ensure AppData directory exists
    if !app_dir.exists() {
        fs::create_dir_all(&app_dir)
            .map_err(|e| DbErr::Custom(format!("Failed to create app data directory: {}", e)))?;
        println!("📁 Created app data directory: {}", app_dir.display());
    }

    let db_path = get_map_db_path().map_err(|e| DbErr::Custom(e))?;

    println!("📂 Map DB path: {:?}", db_path);

    let db_url = format!("sqlite://{}?mode=rwc", db_path.display());
    let db = Database::connect(&db_url).await?;

    println!("✅ Map database connected");

    // Create tables
    create_tables(&db).await?;

    Ok(db)
}

/// Create database tables
async fn create_tables(db: &DatabaseConnection) -> Result<(), DbErr> {
    let backend = db.get_database_backend();

    // Create maps table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS maps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            node_xml TEXT NOT NULL,
            edge_xml TEXT NOT NULL,
            tags TEXT,
            category TEXT NOT NULL DEFAULT 'general',
            difficulty TEXT NOT NULL DEFAULT 'medium',
            metadata TEXT,
            is_embedded INTEGER NOT NULL DEFAULT 0,
            embedded_at TEXT,
            embedding_model TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        "#.to_string(),
    )).await?;

    println!("✅ Maps table created");

    // Create map_scenarios table
    db.execute(Statement::from_string(
        backend,
        r#"
        CREATE TABLE IF NOT EXISTS map_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            drivers TEXT,
            vehicles TEXT,
            traffic_config TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE
        )
        "#.to_string(),
    )).await?;

    println!("✅ Map scenarios table created");

    Ok(())
}
