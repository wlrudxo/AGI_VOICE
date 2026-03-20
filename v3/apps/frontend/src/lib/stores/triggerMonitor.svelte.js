class TriggerMonitor {
  isMonitoring = $state(false);
  triggers = $state([]);
  logMessages = $state([]);
  interval = null;

  addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`].slice(-100);
  }

  async loadTriggers() {
    this.triggers = [];
  }

  async startMonitoring() {
    if (this.isMonitoring) {
      return;
    }

    await this.loadTriggers();
    this.isMonitoring = true;
    this.addLog('✓ Started trigger monitoring (stub)');
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
