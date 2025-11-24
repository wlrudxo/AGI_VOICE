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

    /// Read multiple values from CarMaker in a single batch request
    /// Returns HashMap with variable names as keys and values as Option<f64>
    pub async fn read_values_batch(&mut self, quantities: &[&str]) -> Result<HashMap<String, Option<f64>>, String> {
        if quantities.is_empty() {
            return Ok(HashMap::new());
        }

        // Build batch command: "DVARead var1 var2 var3 ..."
        let cmd = format!("DVARead {}", quantities.join(" "));
        let response = self.send_command(&cmd).await?;

        let mut results = HashMap::new();

        // CarMaker response format: "O<value1> <value2> <value3> ..." for success
        if response.starts_with('O') {
            let values_str = response[1..].trim();
            let values: Vec<&str> = values_str.split_whitespace().collect();

            // Map values back to variable names
            for (i, &quantity) in quantities.iter().enumerate() {
                if i < values.len() {
                    let value = values[i].parse::<f64>().ok();
                    results.insert(quantity.to_string(), value);
                } else {
                    results.insert(quantity.to_string(), None);
                }
            }
        } else {
            // Error or no response - return None for all quantities
            for &quantity in quantities.iter() {
                results.insert(quantity.to_string(), None);
            }
        }

        Ok(results)
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

    /// Read all essential quantities from CarMaker using batch DVARead
    /// Strategy (same as Python implementation):
    /// 1. Batch read: Ego quantities + Traffic.nObjs (1 request)
    /// 2. If traffic exists: Batch read all traffic data (1 request per batch)
    pub async fn read_essential_quantities(&mut self) -> Result<TelemetryData, String> {
        let mut data = TelemetryData::default();
        let mut raw_data = HashMap::new();

        // Step 1: Batch read ego quantities + Traffic.nObjs
        let mut batch_vars: Vec<&str> = ESSENTIAL_QUANTITIES.to_vec();
        batch_vars.push("Traffic.nObjs");

        let batch_results = self.read_values_batch(&batch_vars).await?;

        // Process ego quantities
        for &quantity in ESSENTIAL_QUANTITIES.iter() {
            if let Some(&value_opt) = batch_results.get(quantity) {
                if let Some(value) = value_opt {
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
            }
        }

        // Process Traffic.nObjs
        let n_objs = if let Some(&value_opt) = batch_results.get("Traffic.nObjs") {
            if let Some(value) = value_opt {
                data.traffic_n_objs = Some(value);
                raw_data.insert("Traffic.nObjs".to_string(), value);
                value as i32
            } else {
                0
            }
        } else {
            0
        };

        // Step 2: If traffic exists, batch read all traffic data
        if n_objs > 0 {
            // Traffic object quantities (same as Python)
            const TRAFFIC_OBJ_QUANTITIES: &[&str] = &[
                "tx", "ty", "v_0.x", "v_0.y", "LongVel", "sRoad", "tRoad"
            ];

            // Build all traffic variable names (T00 ~ T{nObjs-1})
            let mut traffic_vars: Vec<String> = Vec::new();
            for i in 0..n_objs {
                let obj_name = format!("T{:02}", i);
                for &qty in TRAFFIC_OBJ_QUANTITIES.iter() {
                    let var = format!("Traffic.{}.{}", obj_name, qty);
                    traffic_vars.push(var);
                }
            }

            // Convert to &str for batch read
            let traffic_vars_refs: Vec<&str> = traffic_vars.iter().map(|s| s.as_str()).collect();

            // Batch read all traffic data in one request
            if !traffic_vars_refs.is_empty() {
                match self.read_values_batch(&traffic_vars_refs).await {
                    Ok(traffic_results) => {
                        for (var, value_opt) in traffic_results {
                            if let Some(value) = value_opt {
                                raw_data.insert(var, value);
                            }
                        }
                    }
                    Err(e) => {
                        eprintln!("Failed to read traffic data: {}", e);
                    }
                }
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
