import { requestJson } from '$lib/backend';

interface Trigger {
  id: number;
  name: string;
  isActive: boolean;
  expression: string;
  message: string;
  conversationId?: number | null;
  useRuleControl: boolean;
  debugAction: string;
  cooldown: number;
  createdAt: string;
  updatedAt: string;
}

class TriggerMonitor {
  isMonitoring = $state(false);
  triggers = $state<Trigger[]>([]);
  logMessages = $state<string[]>([]);

  async loadTriggers(): Promise<void> {
    try {
      this.triggers = await requestJson<Trigger[]>('/api/triggers');
      this.isMonitoring = await requestJson<boolean>('/api/triggers/monitoring');
      this.logMessages = await requestJson<string[]>('/api/triggers/logs');
      this.addLog(`✓ Loaded ${this.triggers.length} triggers`);
    } catch (error) {
      this.addLog(`✗ Failed to load triggers: ${String(error)}`);
    }
  }

  async startMonitoring(): Promise<void> {
    if (this.isMonitoring) {
      return;
    }

    await this.loadTriggers();
    try {
      this.isMonitoring = await requestJson<boolean>('/api/triggers/monitoring', {
        method: 'POST',
        body: { active: true },
      });
      this.addLog('✓ Started trigger monitoring');
    } catch (error) {
      this.addLog(`✗ Failed to start trigger monitoring: ${String(error)}`);
    }
  }

  async stopMonitoring(): Promise<void> {
    try {
      this.isMonitoring = await requestJson<boolean>('/api/triggers/monitoring', {
        method: 'POST',
        body: { active: false },
      });
      this.addLog('✓ Stopped trigger monitoring');
    } catch (error) {
      this.addLog(`✗ Failed to stop trigger monitoring: ${String(error)}`);
    }
  }

  clearLogs(): void {
    this.logMessages = [];
  }

  addLog(message: string): void {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`].slice(-100);
  }
}

export const triggerMonitor = new TriggerMonitor();
