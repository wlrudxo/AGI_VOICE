import { toastStore } from './toastStore.svelte';
import { requestJson } from '$lib/backend';

interface TelemetryData {
  rawData: Record<string, number>;
}

interface ConnectionStatus {
  connected: boolean;
  host: string;
  port: number;
  lastError?: string | null;
}

class CarMakerStore {
  host = $state('localhost');
  port = $state('16660');
  isConnected = $state(false);

  duration = $state('2000');
  controlMode = $state('Abs');

  isMonitoring = $state(false);
  monitorData = $state<Record<string, number>>({});
  monitorInterval: number | null = null;
  private isRequesting = false;

  watchedTrafficObjects = $state<number[]>([]);
  logMessages = $state<string[]>([]);

  async checkConnectionStatus(): Promise<void> {
    try {
      const status = await requestJson<ConnectionStatus>('/api/carmaker/status');
      this.isConnected = status.connected;
      this.host = status.host;
      this.port = status.port.toString();

      if (this.isConnected) {
        this.addLog('✓ Connection restored from backend');
      }

      this.watchedTrafficObjects = await requestJson<number[]>('/api/carmaker/watched-objects');
      this.isMonitoring = await requestJson<boolean>('/api/carmaker/monitoring');
    } catch (error) {
      this.isConnected = false;
      console.error('Failed to check connection status:', error);
    }
  }

  async connect(): Promise<boolean> {
    try {
      this.addLog(`Connecting to ${this.host}:${this.port}...`);
      const status = await requestJson<ConnectionStatus>('/api/carmaker/connect', {
        method: 'POST',
        body: {
          host: this.host,
          port: parseInt(this.port, 10),
        },
      });
      this.isConnected = status.connected;
      this.addLog('✓ Connected to CarMaker');
      toastStore.success('CarMaker 연결됨');
      return true;
    } catch (error) {
      this.addLog(`✗ Connection failed: ${String(error)}`);
      this.isConnected = false;
      toastStore.error('서버 연결 실패');
      return false;
    }
  }

  async disconnect(): Promise<boolean> {
    try {
      if (this.isMonitoring) {
        await this.stopMonitoring();
      }
      await requestJson<ConnectionStatus>('/api/carmaker/disconnect', {
        method: 'POST',
      });
      this.isConnected = false;
      this.monitorData = {};
      this.watchedTrafficObjects = [];
      this.addLog('✓ Disconnected from CarMaker');
      return true;
    } catch (error) {
      this.addLog(`✗ Disconnect error: ${String(error)}`);
      return false;
    }
  }

  async toggleMonitoring(): Promise<void> {
    if (this.isMonitoring) {
      await this.stopMonitoring();
    } else {
      await this.startMonitoring();
    }
  }

  async startMonitoring(): Promise<void> {
    try {
      await requestJson<boolean>('/api/carmaker/monitoring', {
        method: 'POST',
        body: { active: true },
      });
      this.syncMonitoringStateFromBackend(true, '✓ Started monitoring');
    } catch (error) {
      this.addLog(`✗ Failed to start monitoring: ${String(error)}`);
    }
  }

  async stopMonitoring(): Promise<void> {
    try {
      this.syncMonitoringStateFromBackend(false, '✓ Stopped monitoring');
      void requestJson<boolean>('/api/carmaker/monitoring', {
        method: 'POST',
        body: { active: false },
      }).catch(() => {});
    } catch (error) {
      this.addLog(`✗ Failed to stop monitoring: ${String(error)}`);
    }
  }

  addLog(message: string): void {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`];
    if (this.logMessages.length > 100) {
      this.logMessages = this.logMessages.slice(-100);
    }
  }

  syncMonitoringStateFromBackend(active: boolean, logMessage?: string): void {
    if (!active && this.monitorInterval !== null) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = null;
    }

    if (!active) {
      this.isRequesting = false;
    }

    const changed = this.isMonitoring !== active;
    this.isMonitoring = active;

    if (active && this.monitorInterval === null) {
      this.monitorInterval = window.setInterval(async () => {
        if (this.isRequesting) {
          return;
        }

        this.isRequesting = true;
        try {
          const telemetry = await requestJson<TelemetryData>('/api/carmaker/telemetry');
          this.monitorData = telemetry.rawData || {};
        } catch (error) {
          console.error('Monitoring error:', error);
        } finally {
          this.isRequesting = false;
        }
      }, 100);
    }

    if (logMessage && changed) {
      this.addLog(logMessage);
    }
  }

  async executeCommand(command: string): Promise<string> {
    try {
      const result = await requestJson<string>('/api/carmaker/command', {
        method: 'POST',
        body: { command },
      });
      this.addLog(`✓ Command executed: ${command}`);
      return result;
    } catch (error) {
      this.addLog(`✗ Command failed: ${String(error)}`);
      throw error;
    }
  }

  async pauseSimulation(): Promise<boolean> {
    try {
      const wasMonitoring = this.isMonitoring;
      if (wasMonitoring) {
        await this.stopMonitoring();
        this.addLog('→ Monitoring paused (prevent timeout in low-speed mode)');
      }
      await this.executeCommand('DVAWrite SC.TAccel 0.001 30000 Abs');
      this.addLog('✓ Simulation paused (time scale = 0.001)');
      return wasMonitoring;
    } catch (error) {
      this.addLog(`✗ Failed to pause simulation: ${String(error)}`);
      throw error;
    }
  }

  async resumeSimulation(restartMonitoring = false): Promise<void> {
    try {
      await this.executeCommand('DVAWrite SC.TAccel 1.0 30000 Abs');
      this.addLog('✓ Simulation resumed (time scale = 1.0)');
      if (restartMonitoring) {
        await this.startMonitoring();
        this.addLog('→ Monitoring resumed');
      }
    } catch (error) {
      this.addLog(`✗ Failed to resume simulation: ${String(error)}`);
      throw error;
    }
  }

  async resetAllControls(): Promise<{ successCount: number; totalCount: number }> {
    this.addLog('🔄 Resetting all vehicle control commands...');

    const resetCommands = [
      { variable: 'DM.Gas', value: 0 },
      { variable: 'DM.Brake', value: 0 },
      { variable: 'DM.Steer.Ang', value: 0 },
      { variable: 'DM.v.Trgt', value: 0 },
      { variable: 'DM.LaneOffset', value: 0 },
    ];

    let successCount = 0;
    for (const command of resetCommands) {
      try {
        await this.executeCommand(`DVAWrite ${command.variable} ${command.value} 1 Abs`);
        successCount += 1;
      } catch (error) {
        this.addLog(`  ✗ Failed to reset ${command.variable}: ${String(error)}`);
      }
    }

    this.addLog(`✓ Reset completed: ${successCount}/${resetCommands.length} commands`);
    return { successCount, totalCount: resetCommands.length };
  }

  async addWatchedTrafficObject(index: number): Promise<void> {
    try {
      const result = await requestJson<number[]>('/api/carmaker/watched-objects', {
        method: 'POST',
        body: { index },
      });
      this.watchedTrafficObjects = result;
      this.addLog(`✓ Added traffic object T${index.toString().padStart(2, '0')} to watch list`);
    } catch (error) {
      this.addLog(`✗ Failed to add traffic object: ${String(error)}`);
    }
  }

  async removeWatchedTrafficObject(index: number): Promise<void> {
    try {
      const result = await requestJson<number[]>(
        `/api/carmaker/watched-objects/${index}`,
        { method: 'DELETE' }
      );
      this.watchedTrafficObjects = result;
      this.addLog(
        `✓ Removed traffic object T${index.toString().padStart(2, '0')} from watch list`
      );
    } catch (error) {
      this.addLog(`✗ Failed to remove traffic object: ${String(error)}`);
    }
  }

  async clearWatchedTrafficObjects(): Promise<void> {
    try {
      const result = await requestJson<number[]>('/api/carmaker/watched-objects', {
        method: 'DELETE',
      });
      this.watchedTrafficObjects = result;
      this.addLog('✓ Cleared all watched traffic objects');
    } catch (error) {
      this.addLog(`✗ Failed to clear traffic objects: ${String(error)}`);
    }
  }
}

export const carmakerStore = new CarMakerStore();
