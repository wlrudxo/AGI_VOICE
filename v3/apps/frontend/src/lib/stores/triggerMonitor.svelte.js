const STORAGE_KEY = 'agi-voice-v3.triggers';

function loadStoredTriggers() {
  if (typeof localStorage === 'undefined') {
    return [];
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return [];
    }

    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function persistTriggers(triggers) {
  if (typeof localStorage === 'undefined') {
    return;
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(triggers));
}

class TriggerMonitor {
  isMonitoring = $state(false);
  triggers = $state([]);
  logMessages = $state([]);

  constructor() {
    this.triggers = loadStoredTriggers();
  }

  addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`].slice(-100);
  }

  async loadTriggers() {
    this.triggers = loadStoredTriggers();
    return this.triggers;
  }

  async createTrigger(request) {
    const now = new Date().toISOString();
    const nextId = this.triggers.reduce((max, trigger) => Math.max(max, trigger.id), 0) + 1;
    const trigger = {
      id: nextId,
      name: request.name,
      isActive: true,
      expression: request.expression,
      message: request.message,
      conversationId: request.conversationId ?? null,
      useRuleControl: request.useRuleControl ?? false,
      debugAction: request.debugAction ?? '',
      cooldown: request.cooldown ?? 5000,
      createdAt: now,
      updatedAt: now,
    };

    this.triggers = [...this.triggers, trigger];
    persistTriggers(this.triggers);
    this.addLog(`✓ Trigger created: ${trigger.name}`);
    return trigger;
  }

  async updateTrigger(id, request) {
    const now = new Date().toISOString();
    this.triggers = this.triggers.map((trigger) =>
      trigger.id === id
        ? {
            ...trigger,
            name: request.name,
            expression: request.expression,
            message: request.message,
            debugAction: request.debugAction ?? '',
            cooldown: request.cooldown ?? trigger.cooldown,
            useRuleControl: request.useRuleControl ?? trigger.useRuleControl,
            conversationId: request.conversationId ?? trigger.conversationId ?? null,
            updatedAt: now,
          }
        : trigger
    );

    persistTriggers(this.triggers);
    this.addLog(`✓ Trigger updated: #${id}`);
  }

  async toggleActive(id) {
    this.triggers = this.triggers.map((trigger) =>
      trigger.id === id
        ? { ...trigger, isActive: !trigger.isActive, updatedAt: new Date().toISOString() }
        : trigger
    );

    persistTriggers(this.triggers);
  }

  async toggleRuleControl(id) {
    this.triggers = this.triggers.map((trigger) =>
      trigger.id === id
        ? { ...trigger, useRuleControl: !trigger.useRuleControl, updatedAt: new Date().toISOString() }
        : trigger
    );

    persistTriggers(this.triggers);
  }

  async deleteTrigger(id) {
    const deleted = this.triggers.find((trigger) => trigger.id === id);
    this.triggers = this.triggers.filter((trigger) => trigger.id !== id);
    persistTriggers(this.triggers);
    if (deleted) {
      this.addLog(`✓ Trigger deleted: ${deleted.name}`);
    }
  }

  async startMonitoring() {
    if (this.isMonitoring) {
      return;
    }

    await this.loadTriggers();
    this.isMonitoring = true;
    this.addLog('✓ Started trigger monitoring (local stub)');
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
