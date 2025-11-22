# CarMaker Real-Time Control Migration Plan

**Target Project**: AGI_VOICE_V2
**Source System**: CarMaker_RealtimeControl (Python-based)
**Migration Date**: 2025-11-22
**Status**: Planning Phase

---

## Executive Summary

This document outlines the migration plan for integrating CarMaker real-time vehicle control capabilities into the AGI_VOICE_V2 application. The integration will transform AGI_VOICE_V2 from a SUMO map-focused autonomous driving research tool into a comprehensive platform supporting both SUMO map generation and CarMaker real-time vehicle control with LLM-based autonomous interventions.

**Key Integration Points**:
- Python-based CarMaker APO client bridge via Rust subprocess management
- **File-based storage** (JSON configs + logs, no database)
- Dedicated UI section for real-time vehicle monitoring and control
- AI chat integration for natural language vehicle commands
- LLM trigger-based autonomous intervention system

---

## Architecture Overview

### Current AGI_VOICE_V2 Architecture

```
Frontend (Svelte 5 + Tauri)
    ↓
Backend (Rust + SeaORM)
    ├─ AiChatDb (ai_chat.db) - Generic AI conversation system
    └─ MapDb (sumo_maps.db) - SUMO map data
    ↓
External Services
    └─ Claude CLI (subprocess) - AI integration
```

### Proposed Architecture with CarMaker Integration

```
Frontend (Svelte 5 + Tauri)
    ↓
Backend (Rust)
    ├─ AiChatDb (ai_chat.db) - Generic AI conversation system
    ├─ MapDb (sumo_maps.db) - SUMO map data
    └─ CarMaker State (in-memory) - Real-time vehicle control ← NEW
    ↓
Local Storage
    ├─ carmaker_config.json - CarMaker connection settings ← NEW
    ├─ llm_triggers.json - LLM trigger configurations ← NEW
    ├─ carmaker_control.log - Command/event logs ← NEW
    └─ llm_interventions.log - LLM intervention logs (JSON Lines) ← NEW
    ↓
External Services
    ├─ Claude CLI (subprocess) - AI integration
    └─ Python CarMaker Bridge (subprocess) - APO client ← NEW
        └─ CarMaker APO (TCP socket :16660)
```

### Integration Strategy

**Option A: Python Subprocess Bridge** (RECOMMENDED)
- Keep Python CarMaker client as-is
- Rust spawns Python subprocess for CarMaker communication
- JSON-based IPC between Rust and Python
- Leverage existing Python code (minimal rewrite)

**Option B: Native Rust Rewrite**
- Rewrite CarMaker APO client in Rust
- Direct TCP socket communication from Rust
- Higher maintenance cost (CarMaker protocol changes)
- Not recommended unless performance critical

**Decision**: Use Option A (Python Bridge) for faster development and code reuse.

---

## Data Storage Strategy

### Why No Database?

**Rationale**:
- **Real-time system**: Data is transient, no need for persistent storage
- **Simplicity**: Avoid database overhead for temporary data
- **Performance**: In-memory state is faster than DB queries
- **Portability**: JSON files are easier to backup/share
- **Original design**: CarMaker Python system uses files, not DB

### Storage Architecture

#### 1. In-Memory State (Rust Tauri State)

```rust
// src-tauri/src/carmaker/state.rs
pub struct CarMakerState {
    pub current_session: RwLock<Option<SessionInfo>>,
    pub latest_telemetry: RwLock<TelemetryData>,
    pub command_history: RwLock<VecDeque<CommandRecord>>, // Last 100 commands
    pub connection_status: RwLock<ConnectionStatus>,
}

pub struct SessionInfo {
    pub name: String,
    pub start_time: DateTime<Utc>,
    pub carmaker_host: String,
    pub carmaker_port: u16,
}

pub struct TelemetryData {
    pub timestamp: DateTime<Utc>,
    pub sim_time: f64,
    pub car_v: f64,
    pub dm_gas: f64,
    pub dm_brake: f64,
    pub dm_steer_ang: f64,
    pub car_ax: f64,
    pub car_ay: f64,
    pub vhcl_t_road: f64,
    // Full UAQ data
    pub raw_data: serde_json::Value,
}

pub struct CommandRecord {
    pub timestamp: DateTime<Utc>,
    pub command: String,
    pub result: String,
    pub command_type: CommandType, // Manual/Auto/LLM
}
```

**Usage**:
- Frontend queries Tauri commands for current state
- No persistence needed (data is real-time)
- Command history keeps last 100 entries in memory
- Circular buffer pattern for telemetry history (optional)

#### 2. Configuration Files (JSON)

**File**: `carmaker_config.json`
```json
{
  "carmakerHost": "localhost",
  "carmakerPort": 16660,
  "telemetryUpdateRate": 100,
  "maxCommandHistory": 100,
  "pythonPath": "python",
  "pythonScriptPath": "./CarMaker_RealtimeControl/carmaker_llm_control.py"
}
```

**File**: `llm_triggers.json`
```json
{
  "triggers": [
    {
      "id": "trigger_1",
      "name": "Speed over 60 km/h",
      "condition": "Car_v > 16.67",
      "description": "Triggered when vehicle speed exceeds 60 km/h",
      "isActive": true,
      "priority": 5
    }
  ]
}
```

**Structure**:
- `id`: Unique trigger identifier
- `name`: Human-readable trigger name
- `condition`: Python expression for evaluation (use underscores: `Car_v` not `Car.v`)
- `description`: Trigger description
- `isActive`: Enable/disable trigger
- `priority`: Execution priority (1-10, higher = more important)

#### 3. Log Files

**File**: `carmaker_control.log` (Text log)
```
2025-11-22 10:30:45.123 [INFO] CarMaker connected to localhost:16660
2025-11-22 10:30:50.456 [CMD] DVAWrite DM.Gas 0.5 2000 Abs
2025-11-22 10:30:50.478 [RESULT] Command executed successfully
2025-11-22 10:31:00.789 [ERROR] Connection lost to CarMaker APO
```

**File**: `llm_interventions.log` (JSON Lines format)
```jsonl
{"timestamp":"2025-11-22T10:32:15.123Z","triggerId":"trigger_1","triggerName":"Speed over 60 km/h","condition":"Car_v > 16.67","telemetry":{"carV":18.5,"dmGas":0.7},"llmAnalysis":"Vehicle speed exceeding limit","llmStrategy":"Reduce throttle gradually","llmScript":"execute_cmd('DVAWrite DM.Gas 0.3 2000 Abs')","executionStatus":"success","executionDurationMs":1250}
{"timestamp":"2025-11-22T10:35:20.456Z","triggerId":"trigger_2","triggerName":"Emergency brake","condition":"Car_ax < -5.0","telemetry":{"carV":25.0,"carAx":-6.2},"llmAnalysis":"Hard braking detected","llmStrategy":"Stabilize vehicle","llmScript":"execute_cmd('DVAWrite DM.Brake 0.0 1000 Abs')","executionStatus":"timeout","executionDurationMs":30000}
```

**Log Format**:
- JSON Lines (one JSON object per line)
- Easy to parse and append
- Can be imported into analysis tools
- Timestamped for chronological order

---

## Backend Implementation (Rust)

### 1. Python Bridge Layer

**File**: `src-tauri/src/carmaker/python_bridge.rs`

```rust
use std::process::{Command, Stdio};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct CarMakerRequest {
    pub action: String,  // "status", "cmd", "wait_until"
    pub params: serde_json::Value,
}

#[derive(Serialize, Deserialize)]
pub struct CarMakerResponse {
    pub success: bool,
    pub data: serde_json::Value,
    pub error: Option<String>,
}

pub struct PythonBridge {
    python_path: String,
    script_path: String,
}

impl PythonBridge {
    pub fn new(python_path: String, script_path: String) -> Self {
        Self { python_path, script_path }
    }

    pub async fn execute(&self, request: CarMakerRequest) -> Result<CarMakerResponse, String> {
        // Spawn Python subprocess
        // Pass JSON via stdin, receive JSON via stdout
        // Timeout handling (30s default)
        // Error handling and logging
    }

    pub async fn get_status(&self) -> Result<serde_json::Value, String> {
        let request = CarMakerRequest {
            action: "status".to_string(),
            params: serde_json::json!({}),
        };
        let response = self.execute(request).await?;
        Ok(response.data)
    }

    pub async fn execute_cmd(&self, cmd: String) -> Result<String, String> {
        let request = CarMakerRequest {
            action: "cmd".to_string(),
            params: serde_json::json!({ "command": cmd }),
        };
        let response = self.execute(request).await?;
        Ok(response.data.to_string())
    }
}
```

**Rationale**:
- Reuse existing Python CarMaker client code
- JSON-based IPC for structured communication
- Async/await for non-blocking Tauri commands
- Centralized error handling

### 2. Tauri Commands

**File**: `src-tauri/src/commands/carmaker_control.rs`

```rust
use tauri::State;
use crate::carmaker::python_bridge::PythonBridge;
use crate::carmaker::state::CarMakerState;
use std::fs;

#[tauri::command]
pub async fn get_vehicle_status(
    bridge: State<'_, PythonBridge>,
    state: State<'_, CarMakerState>
) -> Result<serde_json::Value, String> {
    let telemetry = bridge.get_status().await?;

    // Update in-memory state
    *state.latest_telemetry.write().unwrap() = telemetry.clone();

    Ok(telemetry)
}

#[tauri::command]
pub async fn execute_carmaker_cmd(
    cmd: String,
    bridge: State<'_, PythonBridge>,
    state: State<'_, CarMakerState>
) -> Result<String, String> {
    let result = bridge.execute_cmd(cmd.clone()).await?;

    // Log command to file
    let log_entry = format!(
        "{} [CMD] {}\n{} [RESULT] {}\n",
        chrono::Utc::now().format("%Y-%m-%d %H:%M:%S%.3f"),
        cmd,
        chrono::Utc::now().format("%Y-%m-%d %H:%M:%S%.3f"),
        result
    );
    fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open("carmaker_control.log")
        .and_then(|mut f| std::io::Write::write_all(&mut f, log_entry.as_bytes()))
        .ok();

    // Add to command history (keep last 100)
    let mut history = state.command_history.write().unwrap();
    history.push_back(CommandRecord {
        timestamp: chrono::Utc::now(),
        command: cmd,
        result: result.clone(),
        command_type: CommandType::Manual,
    });
    if history.len() > 100 {
        history.pop_front();
    }

    Ok(result)
}

#[tauri::command]
pub async fn get_llm_triggers() -> Result<Vec<LlmTrigger>, String> {
    // Read from llm_triggers.json
    let contents = fs::read_to_string("llm_triggers.json")
        .map_err(|e| format!("Failed to read triggers: {}", e))?;

    let config: TriggersConfig = serde_json::from_str(&contents)
        .map_err(|e| format!("Failed to parse triggers: {}", e))?;

    Ok(config.triggers)
}

#[tauri::command]
pub async fn save_llm_triggers(triggers: Vec<LlmTrigger>) -> Result<(), String> {
    // Write to llm_triggers.json
    let config = TriggersConfig { triggers };
    let json = serde_json::to_string_pretty(&config)
        .map_err(|e| format!("Failed to serialize triggers: {}", e))?;

    fs::write("llm_triggers.json", json)
        .map_err(|e| format!("Failed to write triggers: {}", e))?;

    Ok(())
}

#[tauri::command]
pub async fn get_command_history(
    state: State<'_, CarMakerState>
) -> Result<Vec<CommandRecord>, String> {
    let history = state.command_history.read().unwrap();
    Ok(history.iter().cloned().collect())
}

#[tauri::command]
pub async fn get_intervention_logs(limit: Option<usize>) -> Result<Vec<InterventionLog>, String> {
    // Read llm_interventions.log (JSON Lines format)
    let contents = fs::read_to_string("llm_interventions.log")
        .unwrap_or_default();

    let logs: Vec<InterventionLog> = contents
        .lines()
        .rev() // Reverse for newest first
        .take(limit.unwrap_or(100))
        .filter_map(|line| serde_json::from_str(line).ok())
        .collect();

    Ok(logs)
}
```

### 3. Helper Types

**File**: `src-tauri/src/carmaker/types.rs`

```rust
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LlmTrigger {
    pub id: String,
    pub name: String,
    pub condition: String,
    pub description: String,
    pub is_active: bool,
    pub priority: i32,
}

#[derive(Serialize, Deserialize)]
pub struct TriggersConfig {
    pub triggers: Vec<LlmTrigger>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InterventionLog {
    pub timestamp: DateTime<Utc>,
    pub trigger_id: String,
    pub trigger_name: String,
    pub condition: String,
    pub telemetry: serde_json::Value,
    pub llm_analysis: String,
    pub llm_strategy: String,
    pub llm_script: String,
    pub execution_status: String,
    pub execution_duration_ms: u64,
    pub execution_error: Option<String>,
}

#[derive(Clone, Debug)]
pub enum CommandType {
    Manual,
    Auto,
    Llm,
}
```

---

## Frontend Implementation (Svelte)

### 1. Routing Structure

Add new route section for CarMaker control:

```
src/routes/
├── carmaker-control/                 ← NEW
│   ├── +layout.svelte                # Sub-sidebar layout
│   ├── +page.svelte                  # Redirect to dashboard
│   ├── dashboard/+page.svelte        # Real-time monitoring dashboard
│   ├── manual-control/+page.svelte   # Manual control interface
│   ├── triggers/+page.svelte         # LLM trigger configuration
│   └── interventions/+page.svelte    # LLM intervention logs (from file)
```

### 2. Component Design

#### A. CarMakerDashboard.svelte
**Purpose**: Real-time vehicle status monitoring

**Features**:
- Connection status indicator (CarMaker APO)
- Real-time telemetry display (10Hz update)
  - Speed (m/s and km/h)
  - Gas, Brake, Steering positions
  - Acceleration (Ax, Ay)
  - Position and road time
- Simulation control buttons (Start/Stop/Pause)
- Session management (start/end session)
- Time-series charts (speed, acceleration over time)

**Implementation**:
```svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';

  let telemetry = $state({
    carV: 0,
    dmGas: 0,
    dmBrake: 0,
    dmSteerAng: 0,
    carAx: 0,
    carAy: 0,
    vhclTRoad: 0,
  });

  let updateInterval = null;

  async function fetchTelemetry() {
    const data = await invoke('get_vehicle_status');
    telemetry = data;
  }

  onMount(() => {
    fetchTelemetry();
    updateInterval = setInterval(fetchTelemetry, 100); // 10Hz
  });

  onDestroy(() => {
    if (updateInterval) clearInterval(updateInterval);
  });
</script>

<div class="dashboard">
  <div class="telemetry-grid">
    <div class="metric">
      <span class="text-muted">Speed</span>
      <span class="text-primary">{telemetry.carV.toFixed(2)} m/s</span>
      <span class="text-secondary">({(telemetry.carV * 3.6).toFixed(1)} km/h)</span>
    </div>
    <!-- More metrics... -->
  </div>
</div>
```

#### B. ManualControlPanel.svelte
**Purpose**: Manual vehicle control interface

**Features**:
- Slider controls for Gas, Brake, Steering
- Preset speed buttons (50, 60, 70, 80, 100 km/h)
- Emergency brake button
- Command input textbox (advanced users)
- Command history log

**Implementation**:
```svelte
<script>
  import { invoke } from '@tauri-apps/api/core';

  let gasValue = $state(0);
  let brakeValue = $state(0);
  let steerValue = $state(0);

  async function sendGasCommand() {
    const cmd = `DVAWrite DM.Gas ${gasValue} 2000 Abs`;
    await invoke('execute_carmaker_cmd', { cmd });
  }

  async function setTargetSpeed(speedKmh) {
    const speedMs = speedKmh / 3.6;
    const cmd = `DVAWrite DM.v.Trgt ${speedMs} -1 Abs`;
    await invoke('execute_carmaker_cmd', { cmd });
  }
</script>

<div class="control-panel">
  <div class="slider-control">
    <label>Gas Pedal</label>
    <input type="range" min="0" max="1" step="0.01" bind:value={gasValue} />
    <button onclick={sendGasCommand}>Apply</button>
  </div>

  <div class="speed-presets">
    <button onclick={() => setTargetSpeed(50)}>50 km/h</button>
    <button onclick={() => setTargetSpeed(60)}>60 km/h</button>
    <button onclick={() => setTargetSpeed(100)}>100 km/h</button>
  </div>
</div>
```

#### C. LlmTriggerManager.svelte
**Purpose**: Manage LLM trigger configurations

**Features**:
- List of all triggers with enable/disable toggles
- Create new trigger dialog (name, condition, description)
- Edit/delete existing triggers
- Condition syntax helper (Car_v > 16.67)
- Test trigger evaluation (dry-run mode)

**Implementation**:
```svelte
<script>
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';

  let triggers = $state([]);

  async function loadTriggers() {
    triggers = await invoke('get_llm_triggers');
  }

  async function toggleTrigger(triggerId, isActive) {
    await invoke('update_llm_trigger', {
      id: triggerId,
      isActive: !isActive
    });
    loadTriggers();
  }

  onMount(loadTriggers);
</script>

<div class="trigger-list">
  {#each triggers as trigger}
    <div class="trigger-card">
      <h3>{trigger.name}</h3>
      <code>{trigger.condition}</code>
      <p class="text-secondary">{trigger.description}</p>
      <label>
        <input
          type="checkbox"
          checked={trigger.isActive}
          onchange={() => toggleTrigger(trigger.id, trigger.isActive)}
        />
        Active
      </label>
    </div>
  {/each}
</div>
```

#### D. InterventionLog.svelte
**Purpose**: Display LLM intervention history from log file

**Features**:
- Read from `llm_interventions.log` (JSON Lines format)
- Chronological list of interventions (newest first)
- Expandable cards showing:
  - Trigger condition
  - Telemetry snapshot at trigger time
  - LLM analysis and strategy
  - Generated control script
  - Execution status (success/failed/timeout)
  - Execution duration
- Filter by trigger, status, date range
- Export to CSV for analysis
- Pagination (load 100 entries at a time)

### 3. Store Integration

**File**: `src/lib/stores/carmakerStore.svelte.ts`

```typescript
import { invoke } from '@tauri-apps/api/core';

interface TelemetryData {
  carV: number;
  dmGas: number;
  dmBrake: number;
  dmSteerAng: number;
  carAx: number;
  carAy: number;
  vhclTRoad: number;
  simTime: number;
}

export const carmakerStore = (() => {
  let latestTelemetry = $state<TelemetryData | null>(null);
  let connectionStatus = $state<'connected' | 'disconnected'>('disconnected');
  let commandHistory = $state<CommandRecord[]>([]);

  async function fetchTelemetry() {
    try {
      const data = await invoke('get_vehicle_status');
      latestTelemetry = data;
      connectionStatus = 'connected';
    } catch (e) {
      connectionStatus = 'disconnected';
    }
  }

  async function loadCommandHistory() {
    try {
      commandHistory = await invoke('get_command_history');
    } catch (e) {
      console.error('Failed to load command history:', e);
    }
  }

  async function executeCommand(cmd: string) {
    await invoke('execute_carmaker_cmd', { cmd });
    await loadCommandHistory(); // Refresh history
  }

  return {
    get latestTelemetry() { return latestTelemetry; },
    get connectionStatus() { return connectionStatus; },
    get commandHistory() { return commandHistory; },
    fetchTelemetry,
    loadCommandHistory,
    executeCommand,
  };
})();
```

---

## AI Integration (Claude CLI)

### 1. Vehicle Control Command Templates

Create new command templates in `ai_chat.db` for CarMaker control:

**Template Name**: "CarMaker Vehicle Control Commands"

**Template Content**:
```markdown
# CarMaker Control Commands

You can control the simulated vehicle using these tag formats:

## Basic Control Tags

<vehicle_cmd|action:set_speed|value:60|unit:kmh>
- Sets target speed to 60 km/h

<vehicle_cmd|action:set_gas|value:0.5|duration:2000>
- Sets gas pedal to 50% for 2 seconds

<vehicle_cmd|action:set_brake|value:0.3|duration:2000>
- Sets brake pedal to 30% for 2 seconds

<vehicle_cmd|action:emergency_brake>
- Immediately applies full brake

## Advanced Control Tags

<vehicle_cmd|action:maintain_speed|value:70|unit:kmh|until:Car_v >= 19.44>
- Maintains 70 km/h until condition is met (failsafe pattern)

<vehicle_cmd|action:raw_command|cmd:DVAWrite DM.Gas 0.5 2000 Abs>
- Execute raw CarMaker APO command

## Query Tags

<vehicle_query|action:get_status>
- Get current vehicle telemetry

<vehicle_query|action:get_session_info>
- Get current session information

## Response Format

Always respond with:
1. Analysis of current vehicle state
2. Recommended action with tags
3. Safety considerations
```

### 2. Frontend Action Parser Extension

**File**: `src/lib/actions/parser.ts` (extend existing parser)

```typescript
export interface VehicleAction {
  type: 'vehicle_cmd' | 'vehicle_query';
  action: string;
  params: Record<string, any>;
}

export function parseVehicleActions(text: string): VehicleAction[] {
  const regex = /<vehicle_(cmd|query)\|([^>]+)>/g;
  const actions: VehicleAction[] = [];

  let match;
  while ((match = regex.exec(text)) !== null) {
    const type = `vehicle_${match[1]}` as 'vehicle_cmd' | 'vehicle_query';
    const params = parseKeyValuePairs(match[2]);
    actions.push({ type, action: params.action, params });
  }

  return actions;
}
```

### 3. Frontend Action Executor Extension

**File**: `src/lib/actions/executor.ts` (extend existing executor)

```typescript
import { invoke } from '@tauri-apps/api/core';

export async function executeVehicleAction(action: VehicleAction): Promise<string> {
  switch (action.action) {
    case 'set_speed':
      const speedMs = action.params.unit === 'kmh'
        ? parseFloat(action.params.value) / 3.6
        : parseFloat(action.params.value);
      const cmd = `DVAWrite DM.v.Trgt ${speedMs} -1 Abs`;
      await invoke('execute_carmaker_cmd', { cmd });
      return `Speed set to ${action.params.value} ${action.params.unit}`;

    case 'set_gas':
      const gasCmd = `DVAWrite DM.Gas ${action.params.value} ${action.params.duration || 2000} Abs`;
      await invoke('execute_carmaker_cmd', { cmd: gasCmd });
      return `Gas pedal set to ${action.params.value}`;

    case 'get_status':
      const status = await invoke('get_vehicle_status');
      return JSON.stringify(status, null, 2);

    // More actions...
  }
}
```

---

## LLM Autonomous Intervention System

### 1. Python LLM Integration Layer

**File**: `CarMaker_RealtimeControl/carmaker_llm_integration.py` (modify existing)

Add JSON-RPC interface for Rust bridge:

```python
import json
import sys

def handle_request(request_json):
    """Handle JSON request from Rust bridge"""
    request = json.loads(request_json)
    action = request['action']
    params = request['params']

    if action == 'status':
        return get_vehicle_status()
    elif action == 'cmd':
        return execute_command(params['command'])
    elif action == 'check_triggers':
        return check_triggers(params['triggers'])
    elif action == 'execute_intervention':
        return execute_llm_script(params['script'])

if __name__ == '__main__':
    # Read JSON from stdin
    request_line = sys.stdin.readline()
    response = handle_request(request_line)
    # Write JSON to stdout
    print(json.dumps(response))
```

### 2. Rust LLM Monitor Loop

**File**: `src-tauri/src/carmaker/llm_monitor.rs`

```rust
use tokio::time::{interval, Duration};
use crate::carmaker::python_bridge::PythonBridge;
use std::fs;
use std::sync::Arc;
use tokio::sync::Mutex;

pub struct LlmMonitor {
    bridge: Arc<PythonBridge>,
    is_running: Arc<Mutex<bool>>,
}

impl LlmMonitor {
    pub async fn start_monitoring(&self) {
        let mut interval = interval(Duration::from_millis(100)); // 10Hz

        loop {
            interval.tick().await;

            // 1. Fetch active triggers from JSON file
            let triggers = match self.load_triggers().await {
                Ok(t) => t,
                Err(_) => continue,
            };

            // 2. Get current vehicle status
            let status = match self.bridge.get_status().await {
                Ok(s) => s,
                Err(_) => continue,
            };

            // 3. Check trigger conditions
            for trigger in triggers.iter().filter(|t| t.is_active) {
                if self.evaluate_condition(&trigger.condition, &status) {
                    // 4. Trigger detected - pause simulation
                    self.pause_simulation().await.ok();

                    // 5. Get LLM intervention
                    let intervention = match self.request_llm_intervention(&trigger, &status).await {
                        Ok(i) => i,
                        Err(_) => {
                            self.resume_simulation().await.ok();
                            continue;
                        }
                    };

                    // 6. Execute intervention script
                    let result = self.execute_intervention(&intervention).await;

                    // 7. Log intervention to file (JSON Lines)
                    self.log_intervention(&trigger, &status, &intervention, &result).await.ok();

                    // 8. Resume simulation
                    self.resume_simulation().await.ok();
                }
            }
        }
    }

    async fn load_triggers(&self) -> Result<Vec<LlmTrigger>, String> {
        let contents = fs::read_to_string("llm_triggers.json")
            .map_err(|e| format!("Failed to read triggers: {}", e))?;

        let config: TriggersConfig = serde_json::from_str(&contents)
            .map_err(|e| format!("Failed to parse triggers: {}", e))?;

        Ok(config.triggers)
    }

    async fn log_intervention(
        &self,
        trigger: &LlmTrigger,
        status: &serde_json::Value,
        intervention: &LlmIntervention,
        result: &InterventionResult,
    ) -> Result<(), String> {
        let log_entry = InterventionLog {
            timestamp: chrono::Utc::now(),
            trigger_id: trigger.id.clone(),
            trigger_name: trigger.name.clone(),
            condition: trigger.condition.clone(),
            telemetry: status.clone(),
            llm_analysis: intervention.analysis.clone(),
            llm_strategy: intervention.strategy.clone(),
            llm_script: intervention.script.clone(),
            execution_status: result.status.clone(),
            execution_duration_ms: result.duration_ms,
            execution_error: result.error.clone(),
        };

        // Append JSON line to log file
        let json_line = serde_json::to_string(&log_entry)
            .map_err(|e| format!("Failed to serialize log: {}", e))?;

        fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open("llm_interventions.log")
            .and_then(|mut f| {
                use std::io::Write;
                writeln!(f, "{}", json_line)
            })
            .map_err(|e| format!("Failed to write log: {}", e))?;

        Ok(())
    }

    async fn request_llm_intervention(
        &self,
        trigger: &LlmTrigger,
        status: &serde_json::Value
    ) -> Result<LlmIntervention, String> {
        // Build prompt for Claude CLI
        let prompt = format!(
            "Trigger: {}\nCondition: {}\nVehicle State: {}\n\nAnalyze the situation and provide control strategy.",
            trigger.name, trigger.condition, status
        );

        // Execute Claude CLI (reuse existing AI chat system)
        let response = self.execute_claude_cli(&prompt).await?;

        // Parse LLM response for intervention script
        Ok(parse_llm_intervention(response))
    }
}
```

### 3. Safety Guarantees

Implement safety mechanisms from original system:

1. **Simulation Pause/Resume**:
   - Automatically pause simulation before LLM intervention
   - Use `try/finally` to ensure resume even on errors

2. **Timeout Protection**:
   - All LLM interventions timeout after 30 seconds
   - Return control to simulation on timeout

3. **Heartbeat Pattern**:
   - Failsafe functions send commands every 200ms
   - Stops automatically if script fails or times out

4. **Restricted Execution**:
   - Python scripts execute in restricted environment
   - No `import`, `open`, `eval` allowed
   - Only allowed functions: `execute_cmd`, `wait`, `wait_until`, `get_value`, `log`

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Backend**:
- [ ] Create in-memory state structure (`CarMakerState`)
- [ ] Create JSON config files (`carmaker_config.json`, `llm_triggers.json`)
- [ ] Create Python bridge layer (`python_bridge.rs`)
- [ ] Implement basic Tauri commands (status, cmd)
- [ ] Add file logging utilities (text log + JSON Lines)

**Frontend**:
- [ ] Create route structure (`/carmaker-control/*`)
- [ ] Implement basic dashboard page (connection status)
- [ ] Add sidebar menu item for CarMaker Control

**Python**:
- [ ] Modify `carmaker_llm_control.py` for JSON-RPC interface
- [ ] Add stdin/stdout JSON communication
- [ ] Test bridge communication (Rust ↔ Python)

**Deliverables**:
- Basic connection to CarMaker APO via Python bridge
- Dashboard displaying connection status
- Ability to execute raw commands from frontend
- Command logging to file

### Phase 2: Manual Control Interface (Week 3-4)

**Frontend**:
- [ ] Implement `ManualControlPanel.svelte`
  - Gas, Brake, Steering sliders
  - Speed preset buttons
  - Command input textbox
- [ ] Implement real-time telemetry display (10Hz updates)
  - Speed, acceleration, position metrics
  - Time-series charts (Chart.js or D3.js)
- [ ] Command history display (from in-memory state)

**Backend**:
- [ ] Implement telemetry state updates (in-memory)
- [ ] Implement command history tracking (VecDeque, last 100)
- [ ] Add structured logging to files

**Deliverables**:
- Fully functional manual control interface
- Real-time telemetry monitoring
- Command history tracking (in-memory, last 100 entries)

### Phase 3: AI Integration (Week 5-6)

**Backend**:
- [ ] Create vehicle control command templates in `ai_chat.db`
- [ ] Extend action parser for vehicle tags (`<vehicle_cmd>`, `<vehicle_query>`)
- [ ] Extend action executor for vehicle actions

**Frontend**:
- [ ] Integrate AI chat widget with CarMaker dashboard
- [ ] Add vehicle control tags to command template UI
- [ ] Display vehicle status in chat responses (formatted)

**AI**:
- [ ] Test natural language vehicle commands
  - "Accelerate to 70 km/h"
  - "Apply brakes gently"
  - "Maintain 60 km/h until road time exceeds 10 seconds"

**Deliverables**:
- Natural language vehicle control via AI chat
- Tag-based command execution
- Status query integration

### Phase 4: LLM Autonomous Intervention (Week 7-8)

**Backend**:
- [ ] Implement trigger file I/O (load/save `llm_triggers.json`)
- [ ] Implement LLM monitor loop (`llm_monitor.rs`)
- [ ] Add trigger condition evaluation
- [ ] Implement simulation pause/resume
- [ ] Add intervention logging (JSON Lines format)

**Frontend**:
- [ ] Implement `LlmTriggerManager.svelte`
  - Create/edit/delete triggers (updates JSON file)
  - Enable/disable toggles
  - Condition syntax helper
- [ ] Implement `InterventionLog.svelte`
  - Read from `llm_interventions.log`
  - Chronological intervention list
  - Expandable details (analysis, script, status)
  - Filter and export options

**Python**:
- [ ] Integrate LLM intervention execution
- [ ] Implement failsafe control functions
- [ ] Add timeout protection

**Deliverables**:
- Functional trigger-based autonomous intervention system
- LLM-generated control scripts
- Intervention logging to JSON Lines file

### Phase 5: Testing & Refinement (Week 9-10)

**Testing**:
- [ ] Unit tests for Python bridge
- [ ] Integration tests for Tauri commands
- [ ] End-to-end tests for AI chat integration
- [ ] Safety tests for LLM intervention system
  - Timeout handling
  - Error recovery
  - Simulation pause/resume

**Refinement**:
- [ ] Performance optimization (telemetry polling)
- [ ] UI/UX improvements based on testing
- [ ] Error handling and user feedback
- [ ] Documentation updates

**Documentation**:
- [ ] Update CLAUDE.md with CarMaker integration
- [ ] Update ARCHITECTURE.md with new components
- [ ] Create user guide for CarMaker control features
- [ ] Document UAQ quantities and command reference

**Deliverables**:
- Production-ready CarMaker integration
- Comprehensive test coverage
- Updated documentation

---

## Technical Considerations

### 1. Performance

**Telemetry Polling Rate**:
- Original system: 10Hz (100ms interval)
- Consideration: Svelte reactive updates may be expensive at 10Hz
- **Recommendation**: Start with 10Hz, optimize if UI lag observed

**In-Memory State**:
- Telemetry updates at 10Hz (in-memory only, no disk I/O)
- Command history: VecDeque with max 100 entries (circular buffer)
- No performance overhead from database writes
- Fast access for real-time UI updates

**Log File Writes**:
- Command logs: Append-only, buffered writes
- Intervention logs: JSON Lines format, one write per intervention (infrequent)
- No performance impact on real-time control loop

### 2. Error Handling

**Python Bridge Failures**:
- Subprocess crash: Auto-restart with exponential backoff
- Timeout: Log error, return user-friendly message
- Invalid JSON: Validate schema before parsing

**CarMaker APO Connection**:
- Connection lost: Show disconnect indicator, attempt reconnection
- Command timeout: Retry once, then fail gracefully
- Invalid response: Log raw response for debugging

**LLM Intervention Errors**:
- Script execution failure: Log error, resume simulation immediately
- Timeout: Cancel script, log intervention as "timeout", resume simulation
- Invalid LLM response: Skip intervention, log parsing error

### 3. Security

**Python Subprocess Execution**:
- Validate all JSON inputs before passing to Python
- Set subprocess timeout (30s default)
- Capture stderr for error logging
- No arbitrary code execution (only predefined actions)

**LLM Script Execution**:
- Restricted `__builtins__` in Python exec()
- Whitelist allowed functions only
- No file I/O, network access, or system calls
- Timeout protection (30s max)

### 4. Naming Conventions

Follow AGI_VOICE_V2 conventions:

**Backend (Rust)**:
- Structs: `#[serde(rename_all = "camelCase")]`
- JSON fields: `camelCase` (for serialization)
- File names: `snake_case` (`carmaker_config.json`, `llm_triggers.json`)

**Frontend (TypeScript)**:
- All fields: `camelCase`
- Variable names: `sessionId`, `telemetryData`, `triggerCondition`

**JSON Files**:
- Field names: `camelCase` (matches frontend/Rust serialization)
- Example: `{"triggerId": "...", "isActive": true}`

### 5. Data Synchronization

**Original Issue**: Sequential DVARead commands can desynchronize

**Solution**: Use Tcl Eval batch read (from `solution_proposal.md`)
```python
# Single request for all quantities
response = client.send_command("Eval {list $Qu(Time) $Qu(DM.Gas) $Qu(Car.v) ...}")
# Returns: "10.5 0.0 27.78 ..." (space-separated)
values = response.split()
```

**Implementation**:
- Modify `carmaker_client.py` to use batch read
- Update Python bridge to return structured JSON
- Ensure atomic telemetry snapshots

---

## Migration Checklist

### Pre-Migration
- [ ] Review AGI_VOICE_V2 codebase structure
- [ ] Review CarMaker_RealtimeControl system architecture
- [ ] Set up CarMaker APO test environment
- [ ] Verify Claude CLI integration works
- [ ] Plan file storage structure (completed in this document)

### File System Setup
- [ ] Create JSON config files (`carmaker_config.json`, `llm_triggers.json`)
- [ ] Add default example triggers
- [ ] Set up log file paths
- [ ] Test file read/write operations

### Backend Development
- [ ] Implement in-memory state structure (`CarMakerState`)
- [ ] Implement Python bridge layer
- [ ] Create Tauri commands for vehicle control
- [ ] Implement file-based configuration I/O
- [ ] Implement trigger system (JSON file-based)
- [ ] Implement LLM monitor loop
- [ ] Implement logging utilities (text + JSON Lines)

### Frontend Development
- [ ] Create route structure and layouts
- [ ] Implement dashboard page
- [ ] Implement manual control panel
- [ ] Implement trigger manager
- [ ] Implement intervention log
- [ ] Create stores for CarMaker state

### AI Integration
- [ ] Create vehicle control command templates
- [ ] Extend action parser for vehicle tags
- [ ] Extend action executor for vehicle commands
- [ ] Test natural language vehicle control

### Testing
- [ ] Unit tests for Python bridge
- [ ] Integration tests for Tauri commands
- [ ] End-to-end tests for AI chat
- [ ] Safety tests for LLM interventions
- [ ] Performance tests for telemetry polling

### Documentation
- [ ] Update CLAUDE.md
- [ ] Update ARCHITECTURE.md
- [ ] Create user guide
- [ ] Document UAQ reference integration

### Deployment
- [ ] Build production binary
- [ ] Test on Windows/macOS/Linux
- [ ] Verify CarMaker APO compatibility
- [ ] Release notes and changelog

---

## Risk Assessment

### High Risk
1. **Python Bridge Stability**
   - Risk: Subprocess crashes or hangs
   - Mitigation: Auto-restart, timeout protection, extensive error logging

2. **CarMaker APO Compatibility**
   - Risk: CarMaker version differences, API changes
   - Mitigation: Test with multiple CarMaker versions, document compatibility

3. **LLM Intervention Safety**
   - Risk: Unsafe control scripts from LLM
   - Mitigation: Restricted execution environment, timeout protection, manual review mode

### Medium Risk
1. **Performance (10Hz Telemetry)**
   - Risk: UI lag, high CPU usage
   - Mitigation: Batch database writes, optimize Svelte reactivity, profiling

2. **Data Synchronization**
   - Risk: Sequential DVARead desync issue
   - Mitigation: Use Tcl Eval batch read (documented solution)

### Low Risk
1. **JSON File Format Changes**
   - Risk: Future changes may break compatibility
   - Mitigation: Version JSON schema, provide migration scripts

2. **Naming Convention Consistency**
   - Risk: Mix of snake_case and camelCase
   - Mitigation: Strict linting rules, code review

3. **Log File Growth**
   - Risk: Log files grow indefinitely
   - Mitigation: Add log rotation, archive old logs, or provide cleanup utility

---

## Success Criteria

### Functional Requirements
- [ ] Real-time vehicle telemetry display (10Hz)
- [ ] Manual control interface (Gas, Brake, Steering)
- [ ] Natural language vehicle control via AI chat
- [ ] LLM autonomous intervention system with triggers
- [ ] Session and intervention logging
- [ ] Trigger configuration UI

### Non-Functional Requirements
- [ ] UI response time < 100ms for user actions
- [ ] Telemetry update rate = 10Hz (±10ms jitter)
- [ ] LLM intervention latency < 5 seconds
- [ ] Log file writes don't block real-time operations
- [ ] No UI freezes or crashes during operation
- [ ] JSON config file updates < 50ms

### Safety Requirements
- [ ] All LLM interventions timeout after 30s
- [ ] Simulation auto-resumes on intervention failure
- [ ] Emergency brake accessible at all times
- [ ] Connection loss shows clear indicator
- [ ] Manual override always available

---

## Appendix

### A. CarMaker UAQ Quick Reference

**Essential Quantities for Telemetry**:
- `Time` - Simulation time (s)
- `Car.v` - Vehicle velocity (m/s)
- `DM.Gas` - Gas pedal position (0-1)
- `DM.Brake` - Brake pedal position (0-1)
- `DM.Steer.Ang` - Steering wheel angle (rad)
- `Car.ax` - Longitudinal acceleration (m/s²)
- `Car.ay` - Lateral acceleration (m/s²)
- `Vhcl.tRoad` - Road time (s)
- `Car.tx` - X position (m)
- `Car.ty` - Y position (m)

Full reference: `CarMaker_RealtimeControl/docs/UAQ_Complete_Reference.md`

### B. Python Bridge JSON Schema

**Request**:
```json
{
  "action": "status" | "cmd" | "wait_until" | "check_triggers" | "execute_intervention",
  "params": {
    "command": "string (for cmd action)",
    "condition": "string (for wait_until)",
    "timeout": "number (milliseconds)",
    "triggers": "array (for check_triggers)",
    "script": "string (for execute_intervention)"
  }
}
```

**Response**:
```json
{
  "success": true | false,
  "data": {
    "Time": 10.5,
    "Car.v": 27.78,
    "DM.Gas": 0.5,
    ...
  },
  "error": "string (optional)"
}
```

### C. Condition Expression Syntax

**Variable Naming**:
- CarMaker UAQ: `Car.v`, `DM.Gas` (dots)
- Condition expressions: `Car_v`, `DM_Gas` (underscores)
- Automatic conversion in `_evaluate_condition_expr()`

**Supported Operators**:
- Comparison: `>`, `<`, `>=`, `<=`, `==`, `!=`
- Logical: `and`, `or`, `not`
- Functions: `abs()`, `min()`, `max()`

**Examples**:
```python
"Car_v > 27.78"  # Speed exceeds 100 km/h
"Car_v > 16.67 and abs(Vhcl_tRoad) > 1.0"  # Speed > 60 km/h AND on road > 1s
"DM_Gas > 0.8 or DM_Brake > 0.5"  # High gas OR high brake
```

---

**Document Version**: 2.0
**Last Updated**: 2025-11-22
**Author**: Claude Code
**Status**: Draft - File-Based Architecture (No Database)
**Change Log**:
- v2.0: Removed database dependency, switched to JSON config files + log files
- v1.0: Initial draft with database architecture
