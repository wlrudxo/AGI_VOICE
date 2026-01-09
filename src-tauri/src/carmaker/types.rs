use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Telemetry data from CarMaker
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TelemetryData {
    /// Simulation time (s)
    pub time: Option<f64>,
    /// Gas pedal position (0-1)
    pub dm_gas: Option<f64>,
    /// Brake pedal position (0-1)
    pub dm_brake: Option<f64>,
    /// Steering wheel angle (rad)
    pub dm_steer_ang: Option<f64>,
    /// Gear number
    pub dm_gear_no: Option<f64>,
    /// Vehicle velocity (m/s)
    pub car_v: Option<f64>,
    /// Yaw rate
    pub vhcl_yaw_rate: Option<f64>,
    /// Steering angle
    pub vhcl_steer_ang: Option<f64>,
    /// Road position S (m)
    pub vhcl_s_road: Option<f64>,
    /// Lateral position T (m)
    pub vhcl_t_road: Option<f64>,
    /// Target speed (m/s)
    pub dm_v_trgt: Option<f64>,
    /// Lane offset
    pub dm_lane_offset: Option<f64>,
    /// Ego vehicle position X in global frame (m)
    pub car_tx: Option<f64>,
    /// Ego vehicle position Y in global frame (m)
    pub car_ty: Option<f64>,
    /// AEB system active (braking)
    pub aeb_is_active: Option<f64>,
    /// Number of traffic objects
    pub traffic_n_objs: Option<f64>,
    /// Raw data (all quantities)
    pub raw_data: HashMap<String, f64>,
}

impl Default for TelemetryData {
    fn default() -> Self {
        Self {
            time: None,
            dm_gas: None,
            dm_brake: None,
            dm_steer_ang: None,
            dm_gear_no: None,
            car_v: None,
            vhcl_yaw_rate: None,
            vhcl_steer_ang: None,
            vhcl_s_road: None,
            vhcl_t_road: None,
            dm_v_trgt: None,
            dm_lane_offset: None,
            car_tx: None,
            car_ty: None,
            aeb_is_active: None,
            traffic_n_objs: None,
            raw_data: HashMap::new(),
        }
    }
}

/// CarMaker connection status
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ConnectionStatus {
    pub connected: bool,
    pub host: String,
    pub port: u16,
    pub last_error: Option<String>,
}

/// Essential quantities to read from CarMaker
pub const ESSENTIAL_QUANTITIES: &[&str] = &[
    "Time",
    "DM.Gas",
    "DM.Brake",
    "DM.Steer.Ang",
    "DM.GearNo",
    "Car.v",
    "Vhcl.YawRate",
    "Vhcl.Steer.Ang",
    "Vhcl.sRoad",
    "Vhcl.tRoad",
    "DM.v.Trgt",
    "DM.LaneOffset",
    "Car.tx",
    "Car.ty",
    "LongCtrl.AEB.IsActive",
];
