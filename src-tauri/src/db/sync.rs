// Database synchronization module

use chrono::Local;
use std::fs;
use std::path::{Path, PathBuf};

/// Get the backup directory path
/// Returns: %APPDATA%/agi_voice_v2/backups
fn get_backup_dir() -> Result<PathBuf, String> {
    let app_dir = crate::db::get_app_data_dir()?;
    Ok(app_dir.join("backups"))
}

/// Get sync folder path from settings
/// Returns configured sync folder or None
fn get_sync_folder_from_settings() -> Option<PathBuf> {
    // Read from config.json
    let config_path = crate::db::get_app_data_dir()
        .ok()?
        .join("config.json");

    if !config_path.exists() {
        return None;
    }

    let content = fs::read_to_string(&config_path).ok()?;
    let settings: serde_json::Value = serde_json::from_str(&content).ok()?;

    let sync_folder = settings.get("databaseFilePath")?.as_str()?;

    if sync_folder.is_empty() {
        return None;
    }

    Some(PathBuf::from(sync_folder))
}

/// Create a backup of the current database
/// Returns the path to the created backup file
pub fn create_backup() -> Result<PathBuf, String> {
    let db_path = crate::db::get_db_path()?;

    if !db_path.exists() {
        return Err("Database file does not exist".to_string());
    }

    // Create backup directory if it doesn't exist
    let backup_dir = get_backup_dir()?;
    if !backup_dir.exists() {
        fs::create_dir_all(&backup_dir)
            .map_err(|e| format!("Failed to create backup directory: {}", e))?;
    }

    // Generate backup filename with timestamp
    let timestamp = Local::now().format("%Y%m%d_%H%M%S");
    let backup_filename = format!("agi_voice_backup_{}.db", timestamp);
    let backup_path = backup_dir.join(backup_filename);

    // Copy database to backup
    fs::copy(&db_path, &backup_path)
        .map_err(|e| format!("Failed to create backup: {}", e))?;

    println!("✅ Backup created: {}", backup_path.display());

    Ok(backup_path)
}

/// Clean up old backups (keep only the latest N backups)
fn cleanup_old_backups(keep_count: usize) -> Result<(), String> {
    let backup_dir = get_backup_dir()?;

    if !backup_dir.exists() {
        return Ok(());
    }

    // Get all backup files
    let mut backups: Vec<PathBuf> = fs::read_dir(&backup_dir)
        .map_err(|e| format!("Failed to read backup directory: {}", e))?
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.path())
        .filter(|path| {
            path.is_file() &&
            path.file_name()
                .and_then(|n| n.to_str())
                .map(|n| n.starts_with("agi_voice_backup_") && n.ends_with(".db"))
                .unwrap_or(false)
        })
        .collect();

    // Sort by modification time (newest first)
    backups.sort_by(|a, b| {
        let a_time = fs::metadata(a).and_then(|m| m.modified()).ok();
        let b_time = fs::metadata(b).and_then(|m| m.modified()).ok();
        b_time.cmp(&a_time)
    });

    // Remove old backups (keep only the latest `keep_count`)
    for backup_to_remove in backups.iter().skip(keep_count) {
        fs::remove_file(backup_to_remove)
            .map_err(|e| format!("Failed to remove old backup: {}", e))?;
        println!("🗑️  Removed old backup: {}", backup_to_remove.display());
    }

    Ok(())
}

/// Export database to specified path
pub fn export_db(destination: &Path) -> Result<(), String> {
    let db_path = crate::db::get_db_path()?;

    if !db_path.exists() {
        return Err("Database file does not exist".to_string());
    }

    // Ensure parent directory exists
    if let Some(parent) = destination.parent() {
        if !parent.exists() {
            fs::create_dir_all(parent)
                .map_err(|e| format!("Failed to create destination directory: {}", e))?;
        }
    }

    // Copy database to destination
    fs::copy(&db_path, destination)
        .map_err(|e| format!("Failed to export database: {}", e))?;

    println!("✅ Database exported to: {}", destination.display());

    Ok(())
}

/// Import database from specified path
/// Creates a backup before importing
pub fn import_db(source: &Path) -> Result<(), String> {
    if !source.exists() {
        return Err("Source database file does not exist".to_string());
    }

    if !source.is_file() {
        return Err("Source path is not a file".to_string());
    }

    let db_path = crate::db::get_db_path()?;

    // Create backup of current database if it exists
    if db_path.exists() {
        create_backup()?;
        println!("📦 Current database backed up before import");
    }

    // Copy source to database location
    fs::copy(source, &db_path)
        .map_err(|e| format!("Failed to import database: {}", e))?;

    println!("✅ Database imported from: {}", source.display());

    Ok(())
}

/// Load database from sync folder (if it exists and is newer)
/// Returns Some(PathBuf) if sync folder DB is newer, None otherwise
pub fn load_from_sync_folder() -> Result<Option<PathBuf>, String> {
    let sync_folder = match get_sync_folder_from_settings() {
        Some(folder) => folder,
        None => return Ok(None),
    };

    if !sync_folder.exists() || !sync_folder.is_file() {
        return Ok(None);
    }

    let db_path = crate::db::get_db_path()?;

    // If local DB doesn't exist, use sync folder DB
    if !db_path.exists() {
        println!("📥 Local DB not found, using sync folder DB");
        return Ok(Some(sync_folder));
    }

    // Compare modification times
    let local_metadata = fs::metadata(&db_path)
        .map_err(|e| format!("Failed to get local DB metadata: {}", e))?;
    let sync_metadata = fs::metadata(&sync_folder)
        .map_err(|e| format!("Failed to get sync DB metadata: {}", e))?;

    let local_time = local_metadata.modified()
        .map_err(|e| format!("Failed to get local DB modified time: {}", e))?;
    let sync_time = sync_metadata.modified()
        .map_err(|e| format!("Failed to get sync DB modified time: {}", e))?;

    if sync_time > local_time {
        println!("📥 Sync folder DB is newer, will import");
        Ok(Some(sync_folder))
    } else {
        Ok(None)
    }
}

/// Sync database on shutdown (AppData → sync folder + backup)
pub fn sync_on_shutdown() -> Result<String, String> {
    let mut result = String::new();

    // 1. Create backup
    match create_backup() {
        Ok(backup_path) => {
            result.push_str(&format!("Backup created: {}\n", backup_path.display()));
        }
        Err(e) => {
            result.push_str(&format!("Backup failed: {}\n", e));
        }
    }

    // 2. Cleanup old backups (keep latest 5)
    match cleanup_old_backups(5) {
        Ok(_) => {
            result.push_str("Old backups cleaned up\n");
        }
        Err(e) => {
            result.push_str(&format!("Cleanup failed: {}\n", e));
        }
    }

    // 3. Sync to sync folder if configured
    if let Some(sync_folder) = get_sync_folder_from_settings() {
        let db_path = crate::db::get_db_path()?;

        if db_path.exists() {
            match fs::copy(&db_path, &sync_folder) {
                Ok(_) => {
                    result.push_str(&format!("Synced to: {}\n", sync_folder.display()));
                }
                Err(e) => {
                    result.push_str(&format!("Sync failed: {}\n", e));
                }
            }
        }
    } else {
        result.push_str("No sync folder configured\n");
    }

    Ok(result)
}

/// Sync database immediately (manual sync)
pub fn sync_now() -> Result<String, String> {
    let sync_folder = get_sync_folder_from_settings()
        .ok_or("No sync folder configured")?;

    let db_path = crate::db::get_db_path()?;

    if !db_path.exists() {
        return Err("Database file does not exist".to_string());
    }

    // Ensure parent directory of sync folder exists
    if let Some(parent) = sync_folder.parent() {
        if !parent.exists() {
            return Err(format!("Sync folder parent directory does not exist: {:?}", parent));
        }
    }

    fs::copy(&db_path, &sync_folder)
        .map_err(|e| format!("Failed to sync database: {}", e))?;

    Ok(format!("Database synced to: {}", sync_folder.display()))
}

/// List all available backups
pub fn list_backups() -> Result<Vec<PathBuf>, String> {
    let backup_dir = get_backup_dir()?;

    if !backup_dir.exists() {
        return Ok(vec![]);
    }

    let mut backups: Vec<PathBuf> = fs::read_dir(&backup_dir)
        .map_err(|e| format!("Failed to read backup directory: {}", e))?
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.path())
        .filter(|path| {
            path.is_file() &&
            path.file_name()
                .and_then(|n| n.to_str())
                .map(|n| n.starts_with("agi_voice_backup_") && n.ends_with(".db"))
                .unwrap_or(false)
        })
        .collect();

    // Sort by modification time (newest first)
    backups.sort_by(|a, b| {
        let a_time = fs::metadata(a).and_then(|m| m.modified()).ok();
        let b_time = fs::metadata(b).and_then(|m| m.modified()).ok();
        b_time.cmp(&a_time)
    });

    Ok(backups)
}

/// Restore database from backup
pub fn restore_backup(backup_path: &Path) -> Result<(), String> {
    if !backup_path.exists() {
        return Err("Backup file does not exist".to_string());
    }

    if !backup_path.is_file() {
        return Err("Backup path is not a file".to_string());
    }

    import_db(backup_path)
}
