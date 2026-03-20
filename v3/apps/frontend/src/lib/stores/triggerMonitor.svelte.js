import { createTriggerApi } from '../triggerApi.js';

class TriggerMonitor {
  isMonitoring = $state(false);
  triggers = $state([]);
  logMessages = $state([]);
  syncInterval = null;

  api = createTriggerApi();

  addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`].slice(-100);
  }

  async loadTriggers() {
    this.triggers = await this.api.getTriggers();
    await this.syncRuntimeState();
    return this.triggers;
  }

  async createTrigger(request) {
    const trigger = await this.api.createTrigger(request);
    this.triggers = [...this.triggers, trigger];
    this.addLog(`✓ Trigger created: ${trigger.name}`);
    return trigger;
  }

  async updateTrigger(id, request) {
    const updated = await this.api.updateTrigger(id, request);
    this.triggers = this.triggers.map((trigger) => (trigger.id === id ? updated : trigger));
    this.addLog(`✓ Trigger updated: #${id}`);
    return updated;
  }

  async toggleActive(id) {
    const updated = await this.api.toggleTrigger(id);
    this.triggers = this.triggers.map((trigger) => (trigger.id === id ? updated : trigger));
    return updated;
  }

  async toggleRuleControl(id) {
    const updated = await this.api.toggleRuleControl(id);
    this.triggers = this.triggers.map((trigger) => (trigger.id === id ? updated : trigger));
    return updated;
  }

  async deleteTrigger(id) {
    const deleted = this.triggers.find((trigger) => trigger.id === id);
    await this.api.deleteTrigger(id);
    this.triggers = this.triggers.filter((trigger) => trigger.id !== id);
    if (deleted) {
      this.addLog(`✓ Trigger deleted: ${deleted.name}`);
    }
  }

  async startMonitoring() {
    if (this.isMonitoring) {
      return;
    }

    await this.loadTriggers();
    this.isMonitoring = await this.api.setMonitoring(true);
    await this.syncLogs();
    this.startSyncLoop();
  }

  async stopMonitoring() {
    this.isMonitoring = await this.api.setMonitoring(false);
    this.stopSyncLoop();
    await this.syncLogs();
  }

  async clearLogs() {
    this.logMessages = await this.api.clearLogs();
  }

  async syncRuntimeState() {
    this.isMonitoring = await this.api.getMonitoring();
    await this.syncLogs();
    if (this.isMonitoring) {
      this.startSyncLoop();
    } else {
      this.stopSyncLoop();
    }
  }

  async syncLogs() {
    this.logMessages = await this.api.getLogs();
  }

  startSyncLoop() {
    if (this.syncInterval !== null) {
      return;
    }

    this.syncInterval = window.setInterval(async () => {
      try {
        await this.syncRuntimeState();
      } catch (error) {
        this.addLog(`✗ Trigger runtime sync failed: ${error}`);
      }
    }, 500);
  }

  stopSyncLoop() {
    if (this.syncInterval !== null) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }
}

export const triggerMonitor = new TriggerMonitor();
