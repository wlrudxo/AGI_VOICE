import { createCarMakerApi } from './carmakerApi';
import { resolveBackendConfig } from './backend';

const STORAGE_KEY = 'agi_voice_v3_carmaker_settings';

function formatError(error) {
  return error instanceof Error ? error.message : String(error);
}

class CarMakerStore {
  backendUrl = $state('');
  backendSource = $state('unknown');

  host = $state('localhost');
  port = $state('16660');
  isConnected = $state(false);
  connectionStatus = $state(null);

  duration = $state('2000');
  controlMode = $state('Abs');

  isMonitoring = $state(false);
  monitorData = $state({});
  telemetry = $state(null);
  telemetryError = $state('');
  privateMonitorInterval = null;
  privateIsRequesting = false;

  watchedTrafficObjects = $state([]);

  healthState = $state('idle');
  healthMessage = $state('');
  lastCommandResult = $state('');
  busy = $state(false);
  logMessages = $state([]);

  api;

  constructor() {
    const backendConfig = resolveBackendConfig();
    this.backendUrl = backendConfig.baseUrl;
    this.backendSource = backendConfig.source;
    this.api = createCarMakerApi(this.backendUrl);
    this.loadPersistedSettings();
  }

  addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [`[${timestamp}] ${message}`, ...this.logMessages].slice(0, 100);
  }

  clearLogs() {
    this.logMessages = [];
  }

  loadPersistedSettings() {
    if (typeof localStorage === 'undefined') {
      return;
    }

    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return;
      }

      const stored = JSON.parse(raw);
      this.host = typeof stored.host === 'string' ? stored.host : this.host;
      this.port = typeof stored.port === 'string' ? stored.port : this.port;
      this.duration = typeof stored.duration === 'string' ? stored.duration : this.duration;
      this.controlMode =
        typeof stored.controlMode === 'string' ? stored.controlMode : this.controlMode;
    } catch (error) {
      console.warn('Failed to load persisted CarMaker settings', error);
    }
  }

  persistSettings() {
    if (typeof localStorage === 'undefined') {
      return;
    }

    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          host: this.host,
          port: this.port,
          duration: this.duration,
          controlMode: this.controlMode,
        })
      );
    } catch (error) {
      console.warn('Failed to persist CarMaker settings', error);
    }
  }

  async refreshHealth() {
    this.healthState = 'loading';
    this.healthMessage = '';

    try {
      const result = await this.api.health();
      this.healthState = result?.status ?? 'ok';
      this.healthMessage = result?.service ? `${result.service} ready` : 'ready';
    } catch (error) {
      this.healthState = 'error';
      this.healthMessage = formatError(error);
    }
  }

  async checkConnectionStatus() {
    const wasConnected = this.isConnected;

    try {
      const status = await this.api.getStatus();
      this.connectionStatus = status;
      this.isConnected = Boolean(status?.connected);
      this.host = status?.host ?? this.host;
      this.port = String(status?.port ?? this.port);
      this.watchedTrafficObjects = await this.api.getWatchedObjects();

      if (this.isConnected && !wasConnected) {
        this.addLog('✓ Connection restored from backend');
      }

      if (!this.isConnected) {
        this.stopPollingLoop();
        this.isMonitoring = false;
      }
    } catch (error) {
      this.isConnected = false;
      this.isMonitoring = false;
      this.stopPollingLoop();
      this.watchedTrafficObjects = [];
      this.connectionStatus = {
        connected: false,
        host: this.host,
        port: Number(this.port),
        lastError: formatError(error),
      };
      this.addLog(`✗ Status check failed: ${formatError(error)}`);
    }
  }

  async refreshMonitoringState() {
    try {
      this.isMonitoring = await this.api.getMonitoring();
    } catch (error) {
      this.isMonitoring = false;
      this.addLog(`✗ Monitoring state error: ${formatError(error)}`);
    }
  }

  async refreshTelemetry() {
    try {
      this.telemetryError = '';
      const telemetry = await this.api.getTelemetry();
      this.telemetry = telemetry;
      this.monitorData = telemetry?.rawData ?? {};
      return telemetry;
    } catch (error) {
      this.telemetryError = formatError(error);
      this.addLog(`✗ Telemetry error: ${this.telemetryError}`);
      throw error;
    }
  }

  async initialize() {
    await Promise.all([
      this.refreshHealth(),
      this.checkConnectionStatus(),
      this.refreshMonitoringState(),
    ]);

    if (this.isConnected) {
      try {
        await this.refreshTelemetry();
      } catch {
        // Leave the last telemetry error in state.
      }
    }

    if (this.isMonitoring) {
      this.startPollingLoop();
    }
  }

  async connect() {
    this.busy = true;
    try {
      this.addLog(`Connecting to ${this.host}:${this.port}...`);
      const status = await this.api.connect(this.host, this.port);
      this.connectionStatus = status;
      this.isConnected = Boolean(status?.connected);
      this.host = status?.host ?? this.host;
      this.port = String(status?.port ?? this.port);
      this.watchedTrafficObjects = await this.api.getWatchedObjects();
      this.persistSettings();
      this.addLog('✓ Connected to CarMaker');
      await this.refreshTelemetry();
      return true;
    } catch (error) {
      this.isConnected = false;
      this.connectionStatus = {
        connected: false,
        host: this.host,
        port: Number(this.port),
        lastError: formatError(error),
      };
      this.addLog(`✗ Connection failed: ${formatError(error)}`);
      return false;
    } finally {
      this.busy = false;
    }
  }

  async disconnect() {
    this.busy = true;
    try {
      if (this.isMonitoring) {
        await this.stopMonitoring();
      }
      const status = await this.api.disconnect();
      this.connectionStatus = status;
      this.isConnected = false;
      this.isMonitoring = false;
      this.monitorData = {};
      this.telemetry = null;
      this.telemetryError = '';
      this.watchedTrafficObjects = [];
      this.addLog('✓ Disconnected from CarMaker');
      return true;
    } catch (error) {
      this.addLog(`✗ Disconnect failed: ${formatError(error)}`);
      return false;
    } finally {
      this.busy = false;
    }
  }

  startPollingLoop() {
    this.stopPollingLoop();
    this.privateMonitorInterval = window.setInterval(async () => {
      if (this.privateIsRequesting) {
        return;
      }

      this.privateIsRequesting = true;
      try {
        await this.refreshTelemetry();
      } catch {
        // refreshTelemetry already captures state and logs.
      } finally {
        this.privateIsRequesting = false;
      }
    }, 100);
  }

  stopPollingLoop() {
    if (this.privateMonitorInterval !== null) {
      clearInterval(this.privateMonitorInterval);
      this.privateMonitorInterval = null;
    }
    this.privateIsRequesting = false;
  }

  async startMonitoring() {
    this.busy = true;
    try {
      this.isMonitoring = await this.api.setMonitoring(true);
      if (this.isMonitoring) {
        this.startPollingLoop();
        await this.refreshTelemetry();
        this.addLog('✓ Started monitoring');
      }
    } catch (error) {
      this.addLog(`✗ Failed to start monitoring: ${formatError(error)}`);
    } finally {
      this.busy = false;
    }
  }

  async stopMonitoring() {
    this.busy = true;
    try {
      this.stopPollingLoop();
      this.isMonitoring = false;
      await this.api.setMonitoring(false);
      this.addLog('✓ Stopped monitoring');
    } catch (error) {
      this.addLog(`✗ Failed to stop monitoring: ${formatError(error)}`);
    } finally {
      this.busy = false;
    }
  }

  async toggleMonitoring() {
    if (this.isMonitoring) {
      await this.stopMonitoring();
    } else {
      await this.startMonitoring();
    }
  }

  async executeCommand(command) {
    try {
      const result = await this.api.executeCommand(command);
      this.lastCommandResult = String(result);
      this.addLog(`✓ Command executed: ${command}`);
      await this.checkConnectionStatus();
      try {
        await this.refreshTelemetry();
      } catch {
        // Leave telemetry error in store state.
      }
      return result;
    } catch (error) {
      const message = formatError(error);
      this.lastCommandResult = message;
      this.addLog(`✗ Command failed: ${message}`);
      throw error;
    }
  }

  async writeControl(variable, value, duration = Number(this.duration), mode = this.controlMode) {
    return this.executeCommand(`DVAWrite ${variable} ${value} ${duration} ${mode}`);
  }

  async setGas(value, duration = Number(this.duration)) {
    try {
      const result = await this.api.setGas(value, duration);
      this.addLog(`✓ Gas set to ${value}`);
      return result;
    } catch (error) {
      this.addLog(`✗ Gas command failed: ${formatError(error)}`);
      throw error;
    }
  }

  async setBrake(value, duration = Number(this.duration)) {
    try {
      const result = await this.api.setBrake(value, duration);
      this.addLog(`✓ Brake set to ${value}`);
      return result;
    } catch (error) {
      this.addLog(`✗ Brake command failed: ${formatError(error)}`);
      throw error;
    }
  }

  async setSteer(value, duration = Number(this.duration)) {
    try {
      const result = await this.api.setSteer(value, duration);
      this.addLog(`✓ Steer set to ${value}`);
      return result;
    } catch (error) {
      this.addLog(`✗ Steer command failed: ${formatError(error)}`);
      throw error;
    }
  }

  async setLaneOffset(value, duration = Number(this.duration), mode = this.controlMode) {
    try {
      const result = await this.writeControl('DM.LaneOffset', value, duration, mode);
      this.addLog(`✓ Lane offset set to ${value}`);
      return result;
    } catch (error) {
      this.addLog(`✗ Lane offset command failed: ${formatError(error)}`);
      throw error;
    }
  }

  async setTargetVelocity(value, duration = Number(this.duration), mode = this.controlMode) {
    try {
      const result = await this.writeControl('DM.v.Trgt', value, duration, mode);
      this.addLog(`✓ Target velocity set to ${value}`);
      return result;
    } catch (error) {
      this.addLog(`✗ Target velocity command failed: ${formatError(error)}`);
      throw error;
    }
  }

  async pauseSimulation() {
    const wasMonitoring = this.isMonitoring;

    try {
      if (wasMonitoring) {
        await this.stopMonitoring();
        this.addLog('→ Monitoring paused (prevent timeout in low-speed mode)');
      }

      await this.executeCommand('DVAWrite SC.TAccel 0.001 30000 Abs');
      this.addLog('✓ Simulation paused (time scale = 0.001)');
      return wasMonitoring;
    } catch (error) {
      this.addLog(`✗ Failed to pause simulation: ${formatError(error)}`);
      throw error;
    }
  }

  async resumeSimulation(restartMonitoring = false) {
    try {
      await this.executeCommand('DVAWrite SC.TAccel 1.0 30000 Abs');
      this.addLog('✓ Simulation resumed (time scale = 1.0)');

      if (restartMonitoring) {
        await this.startMonitoring();
        this.addLog('→ Monitoring resumed');
      }
    } catch (error) {
      this.addLog(`✗ Failed to resume simulation: ${formatError(error)}`);
      throw error;
    }
  }

  async emergencyDecelerate(duration = 5000) {
    try {
      await this.setGas(0.0, duration);
      await this.setBrake(1.0, duration);
      this.addLog('⚠️ Emergency deceleration activated');
    } catch (error) {
      this.addLog(`✗ Emergency deceleration failed: ${formatError(error)}`);
      throw error;
    }
  }

  async resetAllControls() {
    this.addLog('🔄 Resetting all vehicle control commands...');

    const resetCommands = [
      { variable: 'DM.Gas', value: 0 },
      { variable: 'DM.Brake', value: 0 },
      { variable: 'DM.Steer.Ang', value: 0 },
      { variable: 'DM.v.Trgt', value: 0 },
      { variable: 'DM.LaneOffset', value: 0 },
    ];

    let successCount = 0;
    for (const cmd of resetCommands) {
      try {
        await this.executeCommand(`DVAWrite ${cmd.variable} ${cmd.value} 1 Abs`);
        successCount += 1;
      } catch (error) {
        this.addLog(`  ✗ Failed to reset ${cmd.variable}: ${formatError(error)}`);
      }
    }

    this.addLog(`✓ Reset completed: ${successCount}/${resetCommands.length} commands`);
    return { successCount, totalCount: resetCommands.length };
  }

  async refreshWatchedTrafficObjects() {
    try {
      this.watchedTrafficObjects = await this.api.getWatchedObjects();
      return this.watchedTrafficObjects;
    } catch (error) {
      this.addLog(`✗ Watched object refresh failed: ${formatError(error)}`);
      throw error;
    }
  }

  async addWatchedTrafficObject(index) {
    try {
      this.watchedTrafficObjects = await this.api.addWatchedObject(index);
      this.addLog(`✓ Added traffic object T${Number(index).toString().padStart(2, '0')} to watch list`);
      try {
        await this.refreshTelemetry();
      } catch {
        // Leave telemetry error in store state.
      }
      return this.watchedTrafficObjects;
    } catch (error) {
      this.addLog(`✗ Add watched object failed: ${formatError(error)}`);
      throw error;
    }
  }

  async removeWatchedTrafficObject(index) {
    try {
      this.watchedTrafficObjects = await this.api.removeWatchedObject(index);
      this.addLog(`✓ Removed traffic object T${Number(index).toString().padStart(2, '0')} from watch list`);
      try {
        await this.refreshTelemetry();
      } catch {
        // Leave telemetry error in store state.
      }
      return this.watchedTrafficObjects;
    } catch (error) {
      this.addLog(`✗ Remove watched object failed: ${formatError(error)}`);
      throw error;
    }
  }

  async clearWatchedTrafficObjects() {
    try {
      this.watchedTrafficObjects = await this.api.clearWatchedObjects();
      this.addLog('✓ Cleared all watched traffic objects');
      try {
        await this.refreshTelemetry();
      } catch {
        // Leave telemetry error in store state.
      }
      return this.watchedTrafficObjects;
    } catch (error) {
      this.addLog(`✗ Clear watched objects failed: ${formatError(error)}`);
      throw error;
    }
  }

  cleanup() {
    this.stopPollingLoop();
  }

  destroy() {
    this.cleanup();
  }
}

export const carmakerStore = new CarMakerStore();
