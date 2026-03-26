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
  private pollInterval: number | null = null;
  private lastEventId = 0;

  async loadTriggers(): Promise<void> {
    try {
      this.triggers = await requestJson<Trigger[]>('/api/triggers');
      this.isMonitoring = await requestJson<boolean>('/api/triggers/monitoring');
      this.logMessages = await requestJson<string[]>('/api/triggers/logs');
      await this.pollEvents();
      if (this.isMonitoring) {
        this.startPolling();
      }
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
      this.startPolling();
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
      this.stopPolling();
    } catch (error) {
      this.addLog(`✗ Failed to stop trigger monitoring: ${String(error)}`);
    }
  }

  clearLogs(): void {
    this.logMessages = [];
  }

  private startPolling(): void {
    if (this.pollInterval !== null) {
      return;
    }

    this.pollInterval = window.setInterval(() => {
      void this.pollRuntimeState();
    }, 500);
  }

  private stopPolling(): void {
    if (this.pollInterval !== null) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  private async pollRuntimeState(): Promise<void> {
    try {
      const [monitoring, logs] = await Promise.all([
        requestJson<boolean>('/api/triggers/monitoring'),
        requestJson<string[]>('/api/triggers/logs'),
      ]);

      this.isMonitoring = monitoring;
      this.logMessages = logs;
      await this.pollEvents();

      if (!monitoring) {
        this.stopPolling();
      }
    } catch (error) {
      this.addLog(`✗ Failed to poll trigger runtime: ${String(error)}`);
    }
  }

  private async pollEvents(): Promise<void> {
    const events = await requestJson<Array<{
      id: number;
      type: string;
      triggerName: string;
      content: string;
    }>>(`/api/triggers/events?since_id=${this.lastEventId}`);

    for (const event of events) {
      this.lastEventId = Math.max(this.lastEventId, event.id);
      window.dispatchEvent(
        new CustomEvent('triggerChatMessage', {
          detail: {
            type: event.type,
            triggerName: event.triggerName,
            content: event.content,
          },
        }),
      );
    }
  }

  addLog(message: string): void {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`].slice(-100);
  }
}

export const triggerMonitor = new TriggerMonitor();
