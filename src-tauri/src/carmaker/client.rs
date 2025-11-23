use tokio::net::TcpStream;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::time::{timeout, Duration};
use tokio::sync::Mutex;
use std::collections::HashMap;
use std::sync::Arc;
use super::types::{TelemetryData, ESSENTIAL_QUANTITIES};

/// CarMaker TCP client for APO (Application Programming Option) communication
/// Uses Mutex to prevent concurrent requests (CarMaker APO requires sequential request-response)
pub struct CarMakerClient {
    stream: Option<Arc<Mutex<TcpStream>>>,
    host: String,
    port: u16,
}

impl CarMakerClient {
    /// Create a new CarMaker client
    pub fn new(host: String, port: u16) -> Self {
        Self {
            stream: None,
            host,
            port,
        }
    }

    /// Check if connected to CarMaker
    pub fn is_connected(&self) -> bool {
        self.stream.is_some()
    }

    /// Connect to CarMaker APO server
    pub async fn connect(&mut self) -> Result<(), String> {
        let addr = format!("{}:{}", self.host, self.port);

        let stream = timeout(
            Duration::from_secs(2),
            TcpStream::connect(&addr)
        )
        .await
        .map_err(|_| format!("Connection timeout to {}", addr))?
        .map_err(|e| format!("Failed to connect to {}: {}", addr, e))?;

        self.stream = Some(Arc::new(Mutex::new(stream)));
        Ok(())
    }

    /// Disconnect from CarMaker
    pub fn disconnect(&mut self) {
        self.stream = None;
    }

    /// Send a command to CarMaker and receive response
    /// Uses Mutex lock to ensure sequential request-response (prevents response mixing)
    pub async fn send_command(&mut self, cmd: &str) -> Result<String, String> {
        let stream_arc = self.stream.as_ref()
            .ok_or_else(|| "Not connected to CarMaker".to_string())?
            .clone();

        // Lock the stream for the entire request-response cycle (like Python's with lock:)
        let mut stream = stream_arc.lock().await;

        // Send command (add newline)
        let full_cmd = format!("{}\n", cmd);

        timeout(
            Duration::from_millis(2000),  // Increased to 2s for low-speed simulation compatibility
            stream.write_all(full_cmd.as_bytes())
        )
        .await
        .map_err(|_| "Command send timeout".to_string())?
        .map_err(|e| format!("Failed to send command: {}", e))?;

        // Read response (within the same lock)
        let mut buffer = vec![0u8; 4096];
        let n = timeout(
            Duration::from_millis(2000),  // Increased to 2s for low-speed simulation compatibility
            stream.read(&mut buffer)
        )
        .await
        .map_err(|_| "Response read timeout".to_string())?
        .map_err(|e| format!("Failed to read response: {}", e))?;

        if n == 0 {
            drop(stream);  // Release lock before disconnect
            self.disconnect();
            return Err("Connection closed by CarMaker".to_string());
        }

        let response = String::from_utf8_lossy(&buffer[..n]).trim().to_string();
        Ok(response)
    }

    /// Read a single value from CarMaker
    /// Each read is sequential and locked (via send_command's Mutex)
    pub async fn read_value(&mut self, quantity: &str) -> Result<Option<f64>, String> {
        let cmd = format!("DVARead {}", quantity);
        let response = self.send_command(&cmd).await?;

        // CarMaker response format: "O<value>" for success, "E..." for error
        if response.starts_with('O') {
            let value_str = response[1..].trim();
            if value_str.is_empty() {
                return Ok(None);
            }

            match value_str.parse::<f64>() {
                Ok(val) => Ok(Some(val)),
                Err(_) => Ok(None),
            }
        } else if response.starts_with('E') {
            // Don't treat errors as fatal - just return None (like Python)
            Ok(None)
        } else {
            Ok(None)
        }
    }

    /// Write a value to CarMaker
    pub async fn write_value(
        &mut self,
        quantity: &str,
        value: f64,
        duration: Option<i32>,
        mode: Option<&str>,
    ) -> Result<String, String> {
        let duration_str = duration.map(|d| d.to_string()).unwrap_or_else(|| "2000".to_string());
        let mode_str = mode.unwrap_or("Abs");

        let cmd = format!("DVAWrite {} {:.4} {} {}", quantity, value, duration_str, mode_str);
        self.send_command(&cmd).await
    }

    /// Execute a raw CarMaker command
    pub async fn execute_command(&mut self, command: &str) -> Result<String, String> {
        if command.trim().is_empty() {
            return Err("Empty command".to_string());
        }

        let response = self.send_command(command).await?;

        if response.starts_with('E') {
            Err(format!("CarMaker error: {}", response))
        } else {
            Ok(response)
        }
    }

    /// Read all essential quantities from CarMaker
    /// Reads sequentially with Mutex lock to prevent response mixing (like Python implementation)
    pub async fn read_essential_quantities(&mut self) -> Result<TelemetryData, String> {
        let mut data = TelemetryData::default();
        let mut raw_data = HashMap::new();

        // Sequential read of essential quantities (like Python's for loop)
        for &quantity in ESSENTIAL_QUANTITIES.iter() {
            match self.read_value(quantity).await {
                Ok(Some(value)) => {
                    raw_data.insert(quantity.to_string(), value);

                    // Map to TelemetryData fields
                    match quantity {
                        "Time" => data.time = Some(value),
                        "DM.Gas" => data.dm_gas = Some(value),
                        "DM.Brake" => data.dm_brake = Some(value),
                        "DM.Steer.Ang" => data.dm_steer_ang = Some(value),
                        "DM.GearNo" => data.dm_gear_no = Some(value),
                        "Car.v" => data.car_v = Some(value),
                        "Vhcl.YawRate" => data.vhcl_yaw_rate = Some(value),
                        "Vhcl.Steer.Ang" => data.vhcl_steer_ang = Some(value),
                        "Vhcl.sRoad" => data.vhcl_s_road = Some(value),
                        "Vhcl.tRoad" => data.vhcl_t_road = Some(value),
                        "DM.v.Trgt" => data.dm_v_trgt = Some(value),
                        "DM.LaneOffset" => data.dm_lane_offset = Some(value),
                        _ => {}
                    }
                }
                Ok(None) => {
                    // Value is None (empty response or error) - continue to next quantity
                }
                Err(e) => {
                    // Log error but continue reading other quantities (like Python)
                    eprintln!("Failed to read {}: {}", quantity, e);
                }
            }
        }

        // Read Traffic.nObjs separately
        match self.read_value("Traffic.nObjs").await {
            Ok(Some(value)) => {
                data.traffic_n_objs = Some(value);
                raw_data.insert("Traffic.nObjs".to_string(), value);
            }
            _ => {
                // Ignore error or None
            }
        }

        data.raw_data = raw_data;
        Ok(data)
    }

    /// Set gas pedal
    pub async fn set_gas(&mut self, value: f64, duration: Option<i32>) -> Result<String, String> {
        self.write_value("DM.Gas", value, duration, Some("Abs")).await
    }

    /// Set brake pedal
    pub async fn set_brake(&mut self, value: f64, duration: Option<i32>) -> Result<String, String> {
        self.write_value("DM.Brake", value, duration, Some("Abs")).await
    }

    /// Set steering angle
    pub async fn set_steer(&mut self, value: f64, duration: Option<i32>) -> Result<String, String> {
        self.write_value("DM.Steer.Ang", value, duration, Some("Abs")).await
    }

    /// Set target speed
    pub async fn set_target_speed(&mut self, speed_ms: f64) -> Result<String, String> {
        self.write_value("DM.v.Trgt", speed_ms, Some(-1), Some("Abs")).await
    }

    /// Start simulation
    pub async fn start_sim(&mut self) -> Result<String, String> {
        self.execute_command("StartSim").await
    }

    /// Stop simulation
    pub async fn stop_sim(&mut self) -> Result<String, String> {
        self.execute_command("StopSim").await
    }
}
