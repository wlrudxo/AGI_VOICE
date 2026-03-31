import "clsx";
import { invoke } from "@tauri-apps/api/core";
class ToastStore {
  toasts = [];
  nextId = 0;
  /**
   * 토스트 추가
   */
  add(message, type = "info", duration = 3e3) {
    const id = this.nextId++;
    this.toasts.push({ id, type, message, duration });
    if (duration > 0) {
      setTimeout(
        () => {
          this.remove(id);
        },
        duration
      );
    }
    return id;
  }
  /**
   * 토스트 제거
   */
  remove(id) {
    this.toasts = this.toasts.filter((t) => t.id !== id);
  }
  /**
   * 성공 토스트
   */
  success(message, duration = 3e3) {
    return this.add(message, "success", duration);
  }
  /**
   * 에러 토스트
   */
  error(message, duration = 4e3) {
    return this.add(message, "error", duration);
  }
  /**
   * 경고 토스트
   */
  warning(message, duration = 3500) {
    return this.add(message, "warning", duration);
  }
  /**
   * 정보 토스트
   */
  info(message, duration = 3e3) {
    return this.add(message, "info", duration);
  }
  /**
   * 모든 토스트 제거
   */
  clear() {
    this.toasts = [];
  }
}
const toastStore = new ToastStore();
class CarMakerStore {
  // Connection settings
  host = "localhost";
  port = "16660";
  isConnected = false;
  // Control settings
  duration = "2000";
  controlMode = "Abs";
  // Monitor state
  isMonitoring = false;
  monitorData = {};
  // rawData with CarMaker signal names (e.g., "DM.Gas", "Car.v")
  monitorInterval = null;
  isRequesting = false;
  // Prevent request overlap
  // Watched traffic objects (manually added by user)
  watchedTrafficObjects = [];
  // Log messages
  logMessages = [];
  /**
   * Check connection status from backend (for page reload)
   */
  async checkConnectionStatus() {
    try {
      const status = await invoke("get_connection_status");
      this.isConnected = status.connected;
      this.host = status.host;
      this.port = status.port.toString();
      if (this.isConnected) {
        this.addLog("✓ Connection restored from backend");
      }
      const watched = await invoke("get_watched_traffic_objects");
      this.watchedTrafficObjects = watched;
    } catch (error) {
      this.isConnected = false;
      console.error("Failed to check connection status:", error);
    }
  }
  /**
   * Connect to CarMaker
   */
  async connect() {
    try {
      this.addLog(`Connecting to ${this.host}:${this.port}...`);
      await invoke("connect_carmaker", { host: this.host, port: parseInt(this.port) });
      this.isConnected = true;
      this.addLog("✓ Connected to CarMaker");
      toastStore.success("CarMaker 연결됨");
      return true;
    } catch (error) {
      this.addLog(`✗ Connection failed: ${error}`);
      this.isConnected = false;
      toastStore.error("서버 연결 실패");
      return false;
    }
  }
  /**
   * Disconnect from CarMaker
   */
  async disconnect() {
    try {
      if (this.isMonitoring) {
        await this.stopMonitoring();
      }
      await invoke("disconnect_carmaker");
      this.isConnected = false;
      this.addLog("✓ Disconnected from CarMaker");
      return true;
    } catch (error) {
      this.addLog(`✗ Disconnect error: ${error}`);
      return false;
    }
  }
  /**
   * Toggle monitoring state
   */
  async toggleMonitoring() {
    if (this.isMonitoring) {
      await this.stopMonitoring();
    } else {
      await this.startMonitoring();
    }
  }
  /**
   * Start monitoring
   */
  async startMonitoring() {
    try {
      await invoke("set_monitoring_state", { active: true });
      this.isMonitoring = true;
      this.addLog("✓ Started monitoring");
      this.monitorInterval = window.setInterval(
        async () => {
          if (this.isRequesting) {
            return;
          }
          this.isRequesting = true;
          try {
            const telemetry = await invoke("get_vehicle_status");
            this.monitorData = telemetry.rawData || {};
          } catch (error) {
            console.error("Monitoring error:", error);
          } finally {
            this.isRequesting = false;
          }
        },
        100
      );
    } catch (error) {
      this.addLog(`✗ Failed to start monitoring: ${error}`);
    }
  }
  /**
   * Stop monitoring
   */
  async stopMonitoring() {
    try {
      if (this.monitorInterval !== null) {
        clearInterval(this.monitorInterval);
        this.monitorInterval = null;
      }
      this.isRequesting = false;
      this.isMonitoring = false;
      this.addLog("✓ Stopped monitoring");
      invoke("set_monitoring_state", { active: false }).catch(() => {
      });
    } catch (error) {
      this.addLog(`✗ Failed to stop monitoring: ${error}`);
    }
  }
  /**
   * Add log message
   */
  addLog(message) {
    const timestamp = /* @__PURE__ */ (/* @__PURE__ */ new Date()).toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`];
    if (this.logMessages.length > 100) {
      this.logMessages = this.logMessages.slice(-100);
    }
  }
  /**
   * Execute a custom CarMaker command
   */
  async executeCommand(command) {
    try {
      const result = await invoke("execute_vehicle_command", { command });
      this.addLog(`✓ Command executed: ${command}`);
      return result;
    } catch (error) {
      this.addLog(`✗ Command failed: ${error}`);
      throw error;
    }
  }
  /**
   * Clear logs
   */
  clearLogs() {
    this.logMessages = [];
  }
  /**
   * Pause simulation (set time acceleration to 0.001x)
   * Automatically stops monitoring to prevent timeouts
   */
  async pauseSimulation() {
    try {
      const wasMonitoring = this.isMonitoring;
      if (wasMonitoring) {
        await this.stopMonitoring();
        this.addLog("→ Monitoring paused (prevent timeout in low-speed mode)");
      }
      await this.executeCommand("DVAWrite SC.TAccel 0.001 30000 Abs");
      this.addLog("✓ Simulation paused (time scale = 0.001)");
      return wasMonitoring;
    } catch (error) {
      this.addLog(`✗ Failed to pause simulation: ${error}`);
      throw error;
    }
  }
  /**
   * Resume simulation (set time acceleration to 1.0x)
   * @param restartMonitoring - Whether to restart monitoring (default: false)
   */
  async resumeSimulation(restartMonitoring = false) {
    try {
      await this.executeCommand("DVAWrite SC.TAccel 1.0 30000 Abs");
      this.addLog("✓ Simulation resumed (time scale = 1.0)");
      if (restartMonitoring) {
        await this.startMonitoring();
        this.addLog("→ Monitoring resumed");
      }
    } catch (error) {
      this.addLog(`✗ Failed to resume simulation: ${error}`);
      throw error;
    }
  }
  /**
   * Emergency deceleration (for trigger activation)
   * Immediately sets brake to maximum and gas to 0
   * @param duration - Duration in milliseconds (default: 5000ms)
   */
  async emergencyDecelerate(duration = 5e3) {
    try {
      await invoke("set_gas", { value: 0, duration });
      await invoke("set_brake", { value: 1, duration });
      this.addLog("⚠️ Emergency deceleration activated");
    } catch (error) {
      this.addLog(`✗ Emergency deceleration failed: ${error}`);
      throw error;
    }
  }
  /**
   * Reset all vehicle control commands
   * Sends all DM.* commands with 1ms duration to reset state
   * Used to cancel running wait_until or AI scripts
   */
  async resetAllControls() {
    this.addLog("🔄 Resetting all vehicle control commands...");
    const resetCommands = [
      { variable: "DM.Gas", value: 0 },
      { variable: "DM.Brake", value: 0 },
      { variable: "DM.Steer.Ang", value: 0 },
      { variable: "DM.v.Trgt", value: 0 },
      { variable: "DM.LaneOffset", value: 0 }
    ];
    let successCount = 0;
    for (const cmd of resetCommands) {
      try {
        await this.executeCommand(`DVAWrite ${cmd.variable} ${cmd.value} 1 Abs`);
        successCount++;
      } catch (error) {
        this.addLog(`  ✗ Failed to reset ${cmd.variable}: ${error}`);
      }
    }
    this.addLog(`✓ Reset completed: ${successCount}/${resetCommands.length} commands`);
    return { successCount, totalCount: resetCommands.length };
  }
  /**
   * Add a traffic object to watch list
   * @param index - Traffic object index (0 for T00, 1 for T01, etc.)
   */
  async addWatchedTrafficObject(index) {
    try {
      const result = await invoke("add_watched_traffic_object", { index });
      this.watchedTrafficObjects = result;
      this.addLog(`✓ Added traffic object T${index.toString().padStart(2, "0")} to watch list`);
    } catch (error) {
      this.addLog(`✗ Failed to add traffic object: ${error}`);
    }
  }
  /**
   * Remove a traffic object from watch list
   * @param index - Traffic object index
   */
  async removeWatchedTrafficObject(index) {
    try {
      const result = await invoke("remove_watched_traffic_object", { index });
      this.watchedTrafficObjects = result;
      this.addLog(`✓ Removed traffic object T${index.toString().padStart(2, "0")} from watch list`);
    } catch (error) {
      this.addLog(`✗ Failed to remove traffic object: ${error}`);
    }
  }
  /**
   * Clear all watched traffic objects
   */
  async clearWatchedTrafficObjects() {
    try {
      const result = await invoke("clear_watched_traffic_objects");
      this.watchedTrafficObjects = result;
      this.addLog("✓ Cleared all watched traffic objects");
    } catch (error) {
      this.addLog(`✗ Failed to clear traffic objects: ${error}`);
    }
  }
  /**
   * Cleanup (called on destroy)
   */
  cleanup() {
    if (this.monitorInterval !== null) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = null;
    }
  }
}
const carmakerStore = new CarMakerStore();
export {
  carmakerStore as c,
  toastStore as t
};
