import { createTriggerApi } from '../triggerApi.js';

class TriggerMonitor {
  isMonitoring = $state(false);
  triggers = $state([]);
  logMessages = $state([]);

  constructor() {
    this.api = createTriggerApi();
  }

  addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`].slice(-100);
  }

  async loadTriggers() {
    try {
      this.triggers = await this.api.getTriggers();
      this.addLog(`✓ Loaded ${this.triggers.length} triggers`);
      return this.triggers;
    } catch (error) {
      this.addLog(`✗ Failed to load triggers: ${error}`);
      throw error;
    }
  }

  async createTrigger(request) {
    const trigger = await this.api.createTrigger(request);
    await this.loadTriggers();
    this.addLog(`✓ Trigger created: ${trigger.name}`);
    return trigger;
  }

  async updateTrigger(id, request) {
    const trigger = await this.api.updateTrigger(id, request);
    await this.loadTriggers();
    this.addLog(`✓ Trigger updated: ${trigger.name}`);
    return trigger;
  }

  async toggleActive(id) {
    const trigger = await this.api.toggleTrigger(id);
    await this.loadTriggers();
    return trigger;
  }

  async toggleRuleControl(id) {
    const trigger = await this.api.toggleRuleControl(id);
    await this.loadTriggers();
    return trigger;
  }

  async deleteTrigger(id) {
    await this.api.deleteTrigger(id);
    await this.loadTriggers();
    this.addLog(`✓ Trigger deleted: #${id}`);
  }

  async startMonitoring() {
    if (this.isMonitoring) {
      return;
    }

    await this.loadTriggers();
    this.isMonitoring = true;
    this.addLog('✓ Started trigger monitoring (frontend runtime pending)');
  }

  stopMonitoring() {
    this.isMonitoring = false;
    this.addLog('✓ Stopped trigger monitoring');
  }

  clearLogs() {
    this.logMessages = [];
  }
}

export const triggerMonitor = new TriggerMonitor();
