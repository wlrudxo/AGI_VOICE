use std::fs;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::RwLock;
use tauri::AppHandle;
use super::types::{Trigger, TriggersData};

/// Triggers state (in-memory + file persistence)
pub struct TriggersState {
    pub data: Arc<RwLock<TriggersData>>,
    pub file_path: PathBuf,
}

impl TriggersState {
    /// Create new TriggersState with file path
    pub fn new(app_handle: &AppHandle) -> Result<Self, String> {
        // Retain handle for API parity (unused here)
        let _ = app_handle;

        // Get app data directory (unified AppData/Roaming/AGI_VOICE)
        let app_data_dir = crate::db::get_app_data_dir()
            .map_err(|e| format!("Failed to get app data dir: {}", e))?;

        // Ensure directory exists
        fs::create_dir_all(&app_data_dir)
            .map_err(|e| format!("Failed to create app data dir: {}", e))?;

        let file_path = app_data_dir.join("triggers.json");

        // Load existing data or create new
        let data = if file_path.exists() {
            Self::load_from_file(&file_path)?
        } else {
            TriggersData::default()
        };

        Ok(Self {
            data: Arc::new(RwLock::new(data)),
            file_path,
        })
    }

    /// Load triggers from JSON file
    fn load_from_file(path: &PathBuf) -> Result<TriggersData, String> {
        let content = fs::read_to_string(path)
            .map_err(|e| format!("Failed to read triggers file: {}", e))?;

        serde_json::from_str(&content)
            .map_err(|e| format!("Failed to parse triggers file: {}", e))
    }

    /// Save triggers to JSON file
    pub async fn save_to_file(&self) -> Result<(), String> {
        let data = self.data.read().await;
        let json = serde_json::to_string_pretty(&*data)
            .map_err(|e| format!("Failed to serialize triggers: {}", e))?;

        fs::write(&self.file_path, json)
            .map_err(|e| format!("Failed to write triggers file: {}", e))?;

        Ok(())
    }

    /// Get all triggers
    pub async fn get_all(&self) -> Vec<Trigger> {
        let data = self.data.read().await;
        data.triggers.clone()
    }

    /// Get trigger by ID
    pub async fn get_by_id(&self, id: u32) -> Option<Trigger> {
        let data = self.data.read().await;
        data.triggers.iter().find(|t| t.id == id).cloned()
    }

    /// Add new trigger
    pub async fn add(&self, trigger: Trigger) -> Result<Trigger, String> {
        let mut data = self.data.write().await;
        data.triggers.push(trigger.clone());
        drop(data);

        self.save_to_file().await?;
        Ok(trigger)
    }

    /// Update trigger
    pub async fn update(&self, id: u32, updated: Trigger) -> Result<Trigger, String> {
        let mut data = self.data.write().await;

        let index = data.triggers.iter().position(|t| t.id == id)
            .ok_or_else(|| format!("Trigger with id {} not found", id))?;

        data.triggers[index] = updated.clone();
        drop(data);

        self.save_to_file().await?;
        Ok(updated)
    }

    /// Delete trigger
    pub async fn delete(&self, id: u32) -> Result<(), String> {
        let mut data = self.data.write().await;

        let index = data.triggers.iter().position(|t| t.id == id)
            .ok_or_else(|| format!("Trigger with id {} not found", id))?;

        data.triggers.remove(index);
        drop(data);

        self.save_to_file().await?;
        Ok(())
    }

    /// Toggle trigger active state
    pub async fn toggle(&self, id: u32) -> Result<Trigger, String> {
        let mut data = self.data.write().await;

        let trigger = data.triggers.iter_mut().find(|t| t.id == id)
            .ok_or_else(|| format!("Trigger with id {} not found", id))?;

        trigger.is_active = !trigger.is_active;
        trigger.updated_at = chrono::Utc::now();

        let updated = trigger.clone();
        drop(data);

        self.save_to_file().await?;
        Ok(updated)
    }

    /// Toggle trigger rule control
    pub async fn toggle_rule_control(&self, id: u32) -> Result<Trigger, String> {
        let mut data = self.data.write().await;

        let trigger = data.triggers.iter_mut().find(|t| t.id == id)
            .ok_or_else(|| format!("Trigger with id {} not found", id))?;

        trigger.use_rule_control = !trigger.use_rule_control;
        trigger.updated_at = chrono::Utc::now();

        let updated = trigger.clone();
        drop(data);

        self.save_to_file().await?;
        Ok(updated)
    }

    /// Get next available ID
    pub async fn next_id(&self) -> u32 {
        let data = self.data.read().await;
        data.triggers.iter().map(|t| t.id).max().unwrap_or(0) + 1
    }
}
