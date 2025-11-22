use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use tauri::State;

use crate::commands::common::HealthResponse;
use crate::db::AiChatDb;

// ==================== Settings Models ====================

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Settings {
    pub claude_workspace_dir: String,
    pub database_file_path: String,
    pub database_backup_enabled: bool,
    pub default_character_id: Option<i32>,
    pub default_prompt_template_id: Option<i32>,
    pub keep_conversation_prompts: bool,
    pub default_claude_model: String,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            claude_workspace_dir: String::new(),
            database_file_path: String::new(),
            database_backup_enabled: true,
            default_character_id: None,
            default_prompt_template_id: None,
            keep_conversation_prompts: true,
            default_claude_model: "sonnet".to_string(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChatSettings {
    pub default_character_id: Option<i32>,
    pub default_prompt_template_id: Option<i32>,
    pub default_claude_model: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DbTimestamp {
    pub timestamp: Option<String>,
    pub unix_timestamp: Option<f64>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DbInfo {
    pub path: String,
    pub size_bytes: u64,
    pub size_mb: f64,
    pub last_modified: Option<String>,
    pub backups: Vec<BackupInfo>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct BackupInfo {
    pub path: String,
    pub filename: String,
    pub size_bytes: u64,
    pub size_mb: f64,
    pub created_at: Option<String>,
}

// ==================== Helper Functions ====================

fn get_config_path() -> std::path::PathBuf {
    // Config is now at AppData/agi_voice_v2/config.json
    crate::db::get_app_data_dir()
        .map(|dir| dir.join("config.json"))
        .unwrap_or_else(|_| {
            // Fallback to backend/config.json if AppData path fails
            std::env::current_dir()
                .unwrap()
                .join("backend")
                .join("config.json")
        })
}

fn get_db_path() -> std::path::PathBuf {
    // DB is now at AppData/agi_voice_v2/agi_voice.db
    crate::db::get_db_path()
        .unwrap_or_else(|_| {
            // Fallback to project root if AppData path fails
            std::env::current_dir()
                .unwrap()
                .join("agi_voice.db")
        })
}

pub fn load_settings() -> Result<Settings, String> {
    let config_path = get_config_path();

    if config_path.exists() {
        let content = fs::read_to_string(&config_path)
            .map_err(|e| format!("Failed to read config file: {}", e))?;

        let settings: Settings = serde_json::from_str(&content)
            .map_err(|e| format!("Failed to parse config file: {}", e))?;

        Ok(settings)
    } else {
        Ok(Settings::default())
    }
}

fn save_settings(settings: &Settings) -> Result<(), String> {
    let config_path = get_config_path();
    println!("💾 Saving settings to: {:?}", config_path);

    // Create parent directory if it doesn't exist
    if let Some(parent) = config_path.parent() {
        println!("📁 Creating parent directory: {:?}", parent);
        fs::create_dir_all(parent)
            .map_err(|e| format!("Failed to create config directory: {}", e))?;
    }

    let content = serde_json::to_string_pretty(settings)
        .map_err(|e| format!("Failed to serialize settings: {}", e))?;

    println!("📝 Writing config file...");
    fs::write(&config_path, content)
        .map_err(|e| format!("Failed to write config file: {}", e))?;

    println!("✅ Settings saved successfully to {:?}", config_path);
    Ok(())
}

// ==================== Tauri Commands ====================

/// Get current settings
#[tauri::command]
pub async fn get_settings() -> Result<Settings, String> {
    load_settings()
}

/// Update settings
#[tauri::command]
pub async fn update_settings(settings: Settings) -> Result<Settings, String> {
    // Validate Claude workspace directory
    if !settings.claude_workspace_dir.is_empty() {
        let path = Path::new(&settings.claude_workspace_dir);
        if !path.exists() {
            return Err(format!(
                "Directory does not exist: {}",
                settings.claude_workspace_dir
            ));
        }
        if !path.is_dir() {
            return Err(format!(
                "Path is not a directory: {}",
                settings.claude_workspace_dir
            ));
        }
    }

    // Validate database file path
    if !settings.database_file_path.is_empty() {
        let db_path = Path::new(&settings.database_file_path);
        let parent_dir = db_path.parent().ok_or("Invalid database path")?;

        // Check if parent directory exists
        if !parent_dir.exists() {
            return Err(format!("Parent directory does not exist: {:?}", parent_dir));
        }

        // If file exists, check if it's a file
        if db_path.exists() && !db_path.is_file() {
            return Err(format!(
                "Path exists but is not a file: {}",
                settings.database_file_path
            ));
        }
    }

    save_settings(&settings)?;
    Ok(settings)
}

/// Settings health check
#[tauri::command]
pub async fn settings_health() -> Result<HealthResponse, String> {
    Ok(HealthResponse {
        status: "ok".to_string(),
        service: "settings".to_string(),
    })
}

/// Get chat settings
#[tauri::command]
pub async fn get_chat_settings() -> Result<ChatSettings, String> {
    let settings = load_settings()?;
    Ok(ChatSettings {
        default_character_id: settings.default_character_id,
        default_prompt_template_id: settings.default_prompt_template_id,
        default_claude_model: settings.default_claude_model,
    })
}

/// Update chat settings
#[tauri::command(rename_all = "camelCase")]
pub async fn update_chat_settings(chat_settings: ChatSettings) -> Result<ChatSettings, String> {
    println!("🔧 Received chat settings: {:?}", chat_settings);

    let mut settings = load_settings()?;
    println!("📄 Current settings before update: {:?}", settings);

    settings.default_character_id = chat_settings.default_character_id;
    settings.default_prompt_template_id = chat_settings.default_prompt_template_id;
    settings.default_claude_model = chat_settings.default_claude_model.clone();

    println!("📝 Saving settings: {:?}", settings);
    save_settings(&settings)?;

    println!("✅ Chat settings saved successfully");
    Ok(chat_settings)
}

/// Get database timestamp
#[tauri::command]
pub async fn get_db_timestamp(
    _db: State<'_, AiChatDb>,
) -> Result<DbTimestamp, String> {
    let db_path = get_db_path();

    if db_path.exists() {
        let metadata = fs::metadata(&db_path)
            .map_err(|e| format!("Failed to get DB metadata: {}", e))?;

        let modified = metadata
            .modified()
            .map_err(|e| format!("Failed to get modified time: {}", e))?;

        let duration = modified
            .duration_since(std::time::UNIX_EPOCH)
            .map_err(|e| format!("Failed to get duration: {}", e))?;

        let unix_timestamp = duration.as_secs_f64();

        // Convert to ISO 8601 format
        let datetime: chrono::DateTime<chrono::Local> = modified.into();
        let timestamp = datetime.to_rfc3339();

        Ok(DbTimestamp {
            timestamp: Some(timestamp),
            unix_timestamp: Some(unix_timestamp),
        })
    } else {
        Ok(DbTimestamp {
            timestamp: None,
            unix_timestamp: None,
        })
    }
}

/// Sync database on shutdown (local → remote + backup)
/// Replaces FastAPI /api/shutdown endpoint
#[tauri::command]
pub async fn sync_db_on_shutdown() -> Result<String, String> {
    crate::db::sync::sync_on_shutdown()
        .map_err(|e| format!("DB sync failed: {}", e))
}

// ==================== Database Management Commands ====================

/// Export database to specified path
#[tauri::command]
pub async fn export_db(destination: String) -> Result<String, String> {
    let dest_path = Path::new(&destination);
    crate::db::sync::export_db(dest_path)?;
    Ok(format!("Database exported to: {}", destination))
}

/// Import database from specified path
#[tauri::command]
pub async fn import_db(source: String) -> Result<String, String> {
    let source_path = Path::new(&source);
    crate::db::sync::import_db(source_path)?;
    Ok(format!("Database imported from: {}", source))
}

/// Get database information
#[tauri::command]
pub async fn get_db_info() -> Result<DbInfo, String> {
    let db_path = get_db_path();

    if !db_path.exists() {
        return Err("Database file does not exist".to_string());
    }

    // Get database file metadata
    let metadata = fs::metadata(&db_path)
        .map_err(|e| format!("Failed to get DB metadata: {}", e))?;

    let size_bytes = metadata.len();
    let size_mb = size_bytes as f64 / 1_048_576.0;

    let modified = metadata.modified().ok();
    let last_modified = modified.map(|m| {
        let datetime: chrono::DateTime<chrono::Local> = m.into();
        datetime.to_rfc3339()
    });

    // Get backups
    let backup_paths = crate::db::sync::list_backups()
        .map_err(|e| format!("Failed to list backups: {}", e))?;

    let mut backups = Vec::new();
    for backup_path in backup_paths {
        if let Ok(backup_metadata) = fs::metadata(&backup_path) {
            let backup_size_bytes = backup_metadata.len();
            let backup_size_mb = backup_size_bytes as f64 / 1_048_576.0;

            let created_at = backup_metadata.modified().ok().map(|m| {
                let datetime: chrono::DateTime<chrono::Local> = m.into();
                datetime.to_rfc3339()
            });

            let filename = backup_path
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("unknown")
                .to_string();

            backups.push(BackupInfo {
                path: backup_path.to_string_lossy().to_string(),
                filename,
                size_bytes: backup_size_bytes,
                size_mb: backup_size_mb,
                created_at,
            });
        }
    }

    Ok(DbInfo {
        path: db_path.to_string_lossy().to_string(),
        size_bytes,
        size_mb,
        last_modified,
        backups,
    })
}

/// Manually sync database now
#[tauri::command]
pub async fn sync_db_now() -> Result<String, String> {
    crate::db::sync::sync_now()
}

/// Restore database from backup
#[tauri::command(rename_all = "camelCase")]
pub async fn restore_backup(backup_path: String) -> Result<String, String> {
    let path = Path::new(&backup_path);
    crate::db::sync::restore_backup(path)?;
    Ok(format!("Database restored from: {}", backup_path))
}
