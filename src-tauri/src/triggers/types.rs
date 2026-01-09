use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

/// Trigger definition (Expression-based)
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Trigger {
    pub id: u32,
    pub name: String,
    pub is_active: bool,
    pub expression: String, // Expression string (e.g., "Traffic.T01.sRoad - Traffic.T00.sRoad < 100")
    pub message: String,
    pub conversation_id: Option<i64>,
    #[serde(default)] // Default to false if missing
    pub use_rule_control: bool, // Debug mode: skip LLM, execute action directly
    #[serde(default)] // Default to empty string if missing
    pub debug_action: String, // Action in LLM response format (always stored, activated by use_rule_control)
    #[serde(default = "default_cooldown")] // Default to 5000ms if missing
    pub cooldown: u32, // Cooldown time in milliseconds before trigger can fire again
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

fn default_cooldown() -> u32 {
    5000 // 5 seconds default
}

impl Trigger {
    /// Create a new trigger with auto-generated timestamp
    pub fn new(
        id: u32,
        name: String,
        expression: String,
        message: String,
        conversation_id: Option<i64>,
        use_rule_control: bool,
        debug_action: String,
        cooldown: u32,
    ) -> Self {
        let now = Utc::now();
        Self {
            id,
            name,
            is_active: true,
            expression,
            message,
            conversation_id,
            use_rule_control,
            debug_action,
            cooldown,
            created_at: now,
            updated_at: now,
        }
    }
}

/// Triggers data file structure
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TriggersData {
    pub version: String,
    pub triggers: Vec<Trigger>,
}

impl Default for TriggersData {
    fn default() -> Self {
        Self {
            version: "1.0".to_string(),
            triggers: vec![],
        }
    }
}

/// Request to create a trigger
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreateTriggerRequest {
    pub name: String,
    pub expression: String,
    pub message: String,
    pub conversation_id: Option<i64>,
    pub use_rule_control: bool,
    pub debug_action: String,
    #[serde(default = "default_cooldown")]
    pub cooldown: u32,
}

/// Request to update a trigger
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UpdateTriggerRequest {
    pub name: String,
    pub expression: String,
    pub message: String,
    pub conversation_id: Option<i64>,
    pub use_rule_control: bool,
    pub debug_action: String,
    #[serde(default = "default_cooldown")]
    pub cooldown: u32,
}
