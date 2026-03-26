import { invoke } from '@tauri-apps/api/core';
import { toastStore } from './toastStore.svelte';

/**
 * CarMaker Telemetry Data (from Rust backend)
 */
interface TelemetryData {
  time?: number | null;
  dmGas?: number | null;
  dmBrake?: number | null;
  dmSteerAng?: number | null;
  dmGearNo?: number | null;
  carV?: number | null;
  vhclYawRate?: number | null;
  vhclSteerAng?: number | null;
  vhclSRoad?: number | null;
  vhclTRoad?: number | null;
  dmVTrgt?: number | null;
  dmLaneOffset?: number | null;
  trafficNObjs?: number | null;
  rawData: Record<string, number>;
}

/**
 * Global CarMaker connection state store
 * Shared across all autonomous driving tabs
 */
class CarMakerStore {
  // Connection settings
  host = $state('localhost');
  port = $state('16660');
  isConnected = $state(false);

  // Control settings
  duration = $state('2000');
  controlMode = $state('Abs');

  // Monitor state
  isMonitoring = $state(false);
  monitorData = $state<Record<string, number>>({});  // rawData with CarMaker signal names (e.g., "DM.Gas", "Car.v")
  monitorInterval: number | null = null;
  private isRequesting = false; // Prevent request overlap

  // Watched traffic objects (manually added by user)
  watchedTrafficObjects = $state<number[]>([]);

  // Log messages
  logMessages = $state<string[]>([]);

  /**
   * Check connection status from backend (for page reload)
   */
  async checkConnectionStatus(): Promise<void> {
    try {
      const status = await invoke('get_connection_status') as any;
      this.isConnected = status.connected;
      this.host = status.host;
      this.port = status.port.toString();

      if (this.isConnected) {
        this.addLog('✓ Connection restored from backend');
      }

      // Load watched traffic objects
      const watched = await invoke('get_watched_traffic_objects') as number[];
      this.watchedTrafficObjects = watched;
    } catch (error: any) {
      this.isConnected = false;
      console.error('Failed to check connection status:', error);
    }
  }

  /**
   * Connect to CarMaker
   */
  async connect(): Promise<boolean> {
    try {
      this.addLog(`Connecting to ${this.host}:${this.port}...`);
      await invoke('connect_carmaker', { host: this.host, port: parseInt(this.port) });
      this.isConnected = true;
      this.addLog('✓ Connected to CarMaker');
      toastStore.success('CarMaker 연결됨');
      return true;
    } catch (error: any) {
      this.addLog(`✗ Connection failed: ${error}`);
      this.isConnected = false;
      toastStore.error('서버 연결 실패');
      return false;
    }
  }

  /**
   * Disconnect from CarMaker
   */
  async disconnect(): Promise<boolean> {
    try {
      if (this.isMonitoring) {
        await this.stopMonitoring();
      }
      await invoke('disconnect_carmaker');
      this.isConnected = false;
      this.addLog('✓ Disconnected from CarMaker');
      return true;
    } catch (error: any) {
      this.addLog(`✗ Disconnect error: ${error}`);
      return false;
    }
  }

  /**
   * Toggle monitoring state
   */
  async toggleMonitoring(): Promise<void> {
    if (this.isMonitoring) {
      await this.stopMonitoring();
    } else {
      await this.startMonitoring();
    }
  }

  /**
   * Start monitoring
   */
  async startMonitoring(): Promise<void> {
    try {
      await invoke('set_monitoring_state', { active: true });
      this.isMonitoring = true;
      this.addLog('✓ Started monitoring');

      // Start 10Hz polling with request overlap prevention
      this.monitorInterval = window.setInterval(async () => {
        // Skip if previous request is still running (prevents request accumulation)
        if (this.isRequesting) {
          return;
        }

        this.isRequesting = true;
        try {
          const telemetry = await invoke('get_vehicle_status') as TelemetryData;
          // Use rawData which contains actual CarMaker signal names (e.g., "DM.Gas", "Car.v")
          this.monitorData = telemetry.rawData || {};
        } catch (error: any) {
          console.error('Monitoring error:', error);
        } finally {
          this.isRequesting = false;
        }
      }, 100); // 10Hz = 100ms
    } catch (error: any) {
      this.addLog(`✗ Failed to start monitoring: ${error}`);
    }
  }

  /**
   * Stop monitoring
   */
  async stopMonitoring(): Promise<void> {
    try {
      // IMPORTANT: Clear interval FIRST to stop polling immediately
      if (this.monitorInterval !== null) {
        clearInterval(this.monitorInterval);
        this.monitorInterval = null;
      }

      // Reset request flag (last request will complete on its own)
      this.isRequesting = false;

      this.isMonitoring = false;
      this.addLog('✓ Stopped monitoring');

      // Update backend state (fire and forget, no await)
      invoke('set_monitoring_state', { active: false }).catch(() => {});
    } catch (error: any) {
      this.addLog(`✗ Failed to stop monitoring: ${error}`);
    }
  }

  /**
   * Add log message
   */
  addLog(message: string): void {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`];

    // Keep last 100 messages
    if (this.logMessages.length > 100) {
      this.logMessages = this.logMessages.slice(-100);
    }
  }

  /**
   * Execute a custom CarMaker command
   */
  async executeCommand(command: string): Promise<string> {
    try {
      const result = await invoke('execute_vehicle_command', { command }) as string;
      this.addLog(`✓ Command executed: ${command}`);
      return result;
    } catch (error: any) {
      this.addLog(`✗ Command failed: ${error}`);
      throw error;
    }
  }

  /**
   * Clear logs
   */
  clearLogs(): void {
    this.logMessages = [];
  }

  /**
   * Pause simulation (set time acceleration to 0.001x)
   * Automatically stops monitoring to prevent timeouts
   */
  async pauseSimulation(): Promise<void> {
    try {
      // Save monitoring state and stop monitoring to avoid timeouts
      const wasMonitoring = this.isMonitoring;
      if (wasMonitoring) {
        await this.stopMonitoring();
        this.addLog('→ Monitoring paused (prevent timeout in low-speed mode)');
      }

      // Set time acceleration to 0.001 (nearly paused) for 30 seconds
      await this.executeCommand('DVAWrite SC.TAccel 0.001 30000 Abs');
      this.addLog('✓ Simulation paused (time scale = 0.001)');

      return wasMonitoring;
    } catch (error: any) {
      this.addLog(`✗ Failed to pause simulation: ${error}`);
      throw error;
    }
  }

  /**
   * Resume simulation (set time acceleration to 1.0x)
   * @param restartMonitoring - Whether to restart monitoring (default: false)
   */
  async resumeSimulation(restartMonitoring: boolean = false): Promise<void> {
    try {
      // Set time acceleration to 1.0 (normal speed) for 30 seconds
      await this.executeCommand('DVAWrite SC.TAccel 1.0 30000 Abs');
      this.addLog('✓ Simulation resumed (time scale = 1.0)');

      // Resume monitoring if requested
      if (restartMonitoring) {
        await this.startMonitoring();
        this.addLog('→ Monitoring resumed');
      }
    } catch (error: any) {
      this.addLog(`✗ Failed to resume simulation: ${error}`);
      throw error;
    }
  }

  /**
   * Emergency deceleration (for trigger activation)
   * Immediately sets brake to maximum and gas to 0
   * @param duration - Duration in milliseconds (default: 5000ms)
   */
  async emergencyDecelerate(duration: number = 5000): Promise<void> {
    try {
      // Set gas to 0
      await invoke('set_gas', { value: 0.0, duration });
      // Set brake to maximum
      await invoke('set_brake', { value: 1.0, duration });
      this.addLog('⚠️ Emergency deceleration activated');
    } catch (error: any) {
      this.addLog(`✗ Emergency deceleration failed: ${error}`);
      throw error;
    }
  }

  /**
   * Reset all vehicle control commands
   * Sends all DM.* commands with 1ms duration to reset state
   * Used to cancel running wait_until or AI scripts
   */
  async resetAllControls(): Promise<{ successCount: number; totalCount: number }> {
    this.addLog('🔄 Resetting all vehicle control commands...');

    const resetCommands = [
      { variable: 'DM.Gas', value: 0 },
      { variable: 'DM.Brake', value: 0 },
      { variable: 'DM.Steer.Ang', value: 0 },
      { variable: 'DM.v.Trgt', value: 0 },
      { variable: 'DM.LaneOffset', value: 0 }
    ];

    let successCount = 0;
    for (const cmd of resetCommands) {
      try {
        await this.executeCommand(`DVAWrite ${cmd.variable} ${cmd.value} 1 Abs`);
        successCount++;
      } catch (error: any) {
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
  async addWatchedTrafficObject(index: number): Promise<void> {
    try {
      const result = await invoke('add_watched_traffic_object', { index }) as number[];
      this.watchedTrafficObjects = result;
      this.addLog(`✓ Added traffic object T${index.toString().padStart(2, '0')} to watch list`);
    } catch (error: any) {
      this.addLog(`✗ Failed to add traffic object: ${error}`);
    }
  }

  /**
   * Remove a traffic object from watch list
   * @param index - Traffic object index
   */
  async removeWatchedTrafficObject(index: number): Promise<void> {
    try {
      const result = await invoke('remove_watched_traffic_object', { index }) as number[];
      this.watchedTrafficObjects = result;
      this.addLog(`✓ Removed traffic object T${index.toString().padStart(2, '0')} from watch list`);
    } catch (error: any) {
      this.addLog(`✗ Failed to remove traffic object: ${error}`);
    }
  }

  /**
   * Clear all watched traffic objects
   */
  async clearWatchedTrafficObjects(): Promise<void> {
    try {
      const result = await invoke('clear_watched_traffic_objects') as number[];
      this.watchedTrafficObjects = result;
      this.addLog('✓ Cleared all watched traffic objects');
    } catch (error: any) {
      this.addLog(`✗ Failed to clear traffic objects: ${error}`);
    }
  }

  /**
   * Cleanup (called on destroy)
   */
  cleanup(): void {
    if (this.monitorInterval !== null) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = null;
    }
  }
}

export const carmakerStore = new CarMakerStore();
