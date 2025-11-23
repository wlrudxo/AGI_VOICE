use tauri::State;
use tokio::sync::{Mutex, RwLock};
use std::sync::Arc;
use crate::carmaker::{CarMakerClient, TelemetryData, ConnectionStatus};

/// CarMaker connection state
pub struct CarMakerState {
    pub client: Arc<Mutex<Option<CarMakerClient>>>,
    pub connection_status: Arc<RwLock<ConnectionStatus>>,
    pub latest_telemetry: Arc<RwLock<Option<TelemetryData>>>,
    pub monitoring_active: Arc<RwLock<bool>>,
}

impl CarMakerState {
    pub fn new() -> Self {
        Self {
            client: Arc::new(Mutex::new(None)),
            connection_status: Arc::new(RwLock::new(ConnectionStatus {
                connected: false,
                host: "localhost".to_string(),
                port: 16660,
                last_error: None,
            })),
            latest_telemetry: Arc::new(RwLock::new(None)),
            monitoring_active: Arc::new(RwLock::new(false)),
        }
    }
}

/// Connect to CarMaker APO server
#[tauri::command]
pub async fn connect_carmaker(
    host: String,
    port: u16,
    state: State<'_, CarMakerState>,
) -> Result<ConnectionStatus, String> {
    let mut client_lock = state.client.lock().await;
    let mut status_lock = state.connection_status.write().await;

    // Create new client
    let mut client = CarMakerClient::new(host.clone(), port);

    // Try to connect
    match client.connect().await {
        Ok(_) => {
            *status_lock = ConnectionStatus {
                connected: true,
                host: host.clone(),
                port,
                last_error: None,
            };
            *client_lock = Some(client);
            Ok(status_lock.clone())
        }
        Err(e) => {
            *status_lock = ConnectionStatus {
                connected: false,
                host: host.clone(),
                port,
                last_error: Some(e.clone()),
            };
            Err(e)
        }
    }
}

/// Disconnect from CarMaker
#[tauri::command]
pub async fn disconnect_carmaker(
    state: State<'_, CarMakerState>,
) -> Result<ConnectionStatus, String> {
    let mut client_lock = state.client.lock().await;
    let mut status_lock = state.connection_status.write().await;

    if let Some(mut client) = client_lock.take() {
        client.disconnect();
    }

    *status_lock = ConnectionStatus {
        connected: false,
        host: status_lock.host.clone(),
        port: status_lock.port,
        last_error: None,
    };

    // Stop monitoring if active
    let mut monitoring = state.monitoring_active.write().await;
    *monitoring = false;

    Ok(status_lock.clone())
}

/// Get connection status
#[tauri::command]
pub async fn get_connection_status(
    state: State<'_, CarMakerState>,
) -> Result<ConnectionStatus, String> {
    let status = state.connection_status.read().await;
    Ok(status.clone())
}

/// Get vehicle telemetry data
#[tauri::command]
pub async fn get_vehicle_status(
    state: State<'_, CarMakerState>,
) -> Result<TelemetryData, String> {
    let mut client_lock = state.client.lock().await;

    if let Some(client) = client_lock.as_mut() {
        let telemetry = client.read_essential_quantities().await?;

        // Update cached telemetry
        let mut telemetry_lock = state.latest_telemetry.write().await;
        *telemetry_lock = Some(telemetry.clone());

        Ok(telemetry)
    } else {
        Err("Not connected to CarMaker".to_string())
    }
}

/// Execute a vehicle control command
#[tauri::command]
pub async fn execute_vehicle_command(
    command: String,
    state: State<'_, CarMakerState>,
) -> Result<String, String> {
    let mut client_lock = state.client.lock().await;

    if let Some(client) = client_lock.as_mut() {
        client.execute_command(&command).await
    } else {
        Err("Not connected to CarMaker".to_string())
    }
}

/// Set gas pedal value
#[tauri::command]
pub async fn set_gas(
    value: f64,
    duration: Option<i32>,
    state: State<'_, CarMakerState>,
) -> Result<String, String> {
    let mut client_lock = state.client.lock().await;

    if let Some(client) = client_lock.as_mut() {
        client.set_gas(value, duration).await
    } else {
        Err("Not connected to CarMaker".to_string())
    }
}

/// Set brake pedal value
#[tauri::command]
pub async fn set_brake(
    value: f64,
    duration: Option<i32>,
    state: State<'_, CarMakerState>,
) -> Result<String, String> {
    let mut client_lock = state.client.lock().await;

    if let Some(client) = client_lock.as_mut() {
        client.set_brake(value, duration).await
    } else {
        Err("Not connected to CarMaker".to_string())
    }
}

/// Set steering angle
#[tauri::command]
pub async fn set_steer(
    value: f64,
    duration: Option<i32>,
    state: State<'_, CarMakerState>,
) -> Result<String, String> {
    let mut client_lock = state.client.lock().await;

    if let Some(client) = client_lock.as_mut() {
        client.set_steer(value, duration).await
    } else {
        Err("Not connected to CarMaker".to_string())
    }
}

/// Set target speed
#[tauri::command]
pub async fn set_target_speed(
    speed_kmh: f64,
    state: State<'_, CarMakerState>,
) -> Result<String, String> {
    let mut client_lock = state.client.lock().await;

    if let Some(client) = client_lock.as_mut() {
        let speed_ms = speed_kmh / 3.6;
        client.set_target_speed(speed_ms).await
    } else {
        Err("Not connected to CarMaker".to_string())
    }
}

/// Start simulation
#[tauri::command]
pub async fn start_simulation(
    state: State<'_, CarMakerState>,
) -> Result<String, String> {
    let mut client_lock = state.client.lock().await;

    if let Some(client) = client_lock.as_mut() {
        client.start_sim().await
    } else {
        Err("Not connected to CarMaker".to_string())
    }
}

/// Stop simulation
#[tauri::command]
pub async fn stop_simulation(
    state: State<'_, CarMakerState>,
) -> Result<String, String> {
    let mut client_lock = state.client.lock().await;

    if let Some(client) = client_lock.as_mut() {
        client.stop_sim().await
    } else {
        Err("Not connected to CarMaker".to_string())
    }
}

/// Check if monitoring is active
#[tauri::command]
pub async fn is_monitoring_active(
    state: State<'_, CarMakerState>,
) -> Result<bool, String> {
    let monitoring = state.monitoring_active.read().await;
    Ok(*monitoring)
}

/// Set monitoring state
#[tauri::command]
pub async fn set_monitoring_state(
    active: bool,
    state: State<'_, CarMakerState>,
) -> Result<bool, String> {
    let mut monitoring = state.monitoring_active.write().await;
    *monitoring = active;
    Ok(*monitoring)
}
