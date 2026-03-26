use tauri::State;
use crate::triggers::{Trigger, TriggersState, CreateTriggerRequest, UpdateTriggerRequest};

/// Get all triggers
#[tauri::command]
pub async fn get_triggers(state: State<'_, TriggersState>) -> Result<Vec<Trigger>, String> {
    Ok(state.get_all().await)
}

/// Get trigger by ID
#[tauri::command]
pub async fn get_trigger_by_id(id: u32, state: State<'_, TriggersState>) -> Result<Trigger, String> {
    state.get_by_id(id).await
        .ok_or_else(|| format!("Trigger with id {} not found", id))
}

/// Create new trigger
#[tauri::command]
pub async fn create_trigger(
    request: CreateTriggerRequest,
    state: State<'_, TriggersState>,
) -> Result<Trigger, String> {
    let id = state.next_id().await;

    let trigger = Trigger::new(
        id,
        request.name,
        request.expression,
        request.message,
        request.conversation_id,
        request.use_rule_control,
        request.debug_action,
        request.cooldown,
    );

    state.add(trigger).await
}

/// Update trigger
#[tauri::command]
pub async fn update_trigger(
    id: u32,
    request: UpdateTriggerRequest,
    state: State<'_, TriggersState>,
) -> Result<Trigger, String> {
    // Get existing trigger to preserve id and created_at
    let existing = state.get_by_id(id).await
        .ok_or_else(|| format!("Trigger with id {} not found", id))?;

    let updated = Trigger {
        id: existing.id,
        name: request.name,
        is_active: existing.is_active,
        expression: request.expression,
        message: request.message,
        conversation_id: request.conversation_id,
        use_rule_control: request.use_rule_control,
        debug_action: request.debug_action,
        cooldown: request.cooldown,
        created_at: existing.created_at,
        updated_at: chrono::Utc::now(),
    };

    state.update(id, updated).await
}

/// Delete trigger
#[tauri::command]
pub async fn delete_trigger(id: u32, state: State<'_, TriggersState>) -> Result<(), String> {
    state.delete(id).await
}

/// Toggle trigger active state
#[tauri::command]
pub async fn toggle_trigger(id: u32, state: State<'_, TriggersState>) -> Result<Trigger, String> {
    state.toggle(id).await
}

/// Toggle trigger rule control
#[tauri::command]
pub async fn toggle_rule_control(id: u32, state: State<'_, TriggersState>) -> Result<Trigger, String> {
    state.toggle_rule_control(id).await
}
