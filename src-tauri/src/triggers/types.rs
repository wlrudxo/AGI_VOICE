use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

/// Trigger condition
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TriggerCondition {
    pub variable: String,
    pub operator: String,
    pub value: String,
}

/// Trigger definition
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Trigger {
    pub id: u32,
    pub name: String,
    pub is_active: bool,
    pub conditions: Vec<TriggerCondition>,
    pub logic_operator: String, // "AND" or "OR"
    pub message: String,
    pub conversation_id: Option<i64>,
    #[serde(default)] // Default to false if missing
    pub use_rule_control: bool, // Debug mode: skip LLM, execute action directly
    #[serde(default)] // Default to empty string if missing
    pub debug_action: String, // Action in LLM response format (always stored, activated by use_rule_control)
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl Trigger {
    /// Create a new trigger with auto-generated timestamp
    pub fn new(
        id: u32,
        name: String,
        conditions: Vec<TriggerCondition>,
        logic_operator: String,
        message: String,
        conversation_id: Option<i64>,
        use_rule_control: bool,
        debug_action: String,
    ) -> Self {
        let now = Utc::now();
        Self {
            id,
            name,
            is_active: true,
            conditions,
            logic_operator,
            message,
            conversation_id,
            use_rule_control,
            debug_action,
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
    pub conditions: Vec<TriggerCondition>,
    pub logic_operator: String,
    pub message: String,
    pub conversation_id: Option<i64>,
    pub use_rule_control: bool,
    pub debug_action: String,
}

/// Request to update a trigger
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UpdateTriggerRequest {
    pub name: String,
    pub conditions: Vec<TriggerCondition>,
    pub logic_operator: String,
    pub message: String,
    pub conversation_id: Option<i64>,
    pub use_rule_control: bool,
    pub debug_action: String,
}
