import { invoke } from '@tauri-apps/api/core';
import { carmakerStore } from './carmakerStore.svelte';
import { evaluateTrigger } from '$lib/utils/triggerEvaluator';

interface TriggerCondition {
  variable: string;
  operator: string;
  value: string;
}

interface Trigger {
  id: number;
  name: string;
  isActive: boolean;
  conditions: TriggerCondition[];
  logicOperator: 'AND' | 'OR';
  message: string;
  conversationId?: number;
  useRuleControl: boolean;
  debugAction: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Trigger Monitor Store
 * Monitors vehicle data and executes triggers when conditions are met
 */
class TriggerMonitor {
  // Monitoring state
  isMonitoring = $state(false);
  monitorInterval: number | null = null;

  // Triggers
  triggers = $state<Trigger[]>([]);

  // Triggered history (prevent duplicate triggers)
  private triggeredIds = new Set<number>();
  private resetTimeout: number | null = null;

  // Logs
  logMessages = $state<string[]>([]);

  /**
   * Load triggers from backend
   */
  async loadTriggers(): Promise<void> {
    try {
      this.triggers = await invoke('get_triggers');
      this.addLog(`✓ Loaded ${this.triggers.length} triggers`);
    } catch (error: any) {
      this.addLog(`✗ Failed to load triggers: ${error}`);
    }
  }

  /**
   * Start trigger monitoring
   * Checks trigger conditions every 100ms (10Hz)
   */
  async startMonitoring(): Promise<void> {
    if (this.isMonitoring) {
      return; // Already monitoring
    }

    // Load triggers first
    await this.loadTriggers();

    this.isMonitoring = true;
    this.triggeredIds.clear();
    this.addLog('✓ Started trigger monitoring (10Hz)');

    // Monitor every 100ms (10Hz)
    this.monitorInterval = window.setInterval(() => {
      this.checkTriggers();
    }, 100);
  }

  /**
   * Stop trigger monitoring
   */
  stopMonitoring(): void {
    if (this.monitorInterval !== null) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = null;
    }

    if (this.resetTimeout !== null) {
      clearTimeout(this.resetTimeout);
      this.resetTimeout = null;
    }

    this.isMonitoring = false;
    this.triggeredIds.clear();
    this.addLog('✓ Stopped trigger monitoring');
  }

  /**
   * Check all triggers against current vehicle data
   */
  private checkTriggers(): void {
    const vehicleData = carmakerStore.monitorData;

    // Skip if no vehicle data available
    if (Object.keys(vehicleData).length === 0) {
      return;
    }

    for (const trigger of this.triggers) {
      // Skip if already triggered (prevent duplicate execution)
      if (this.triggeredIds.has(trigger.id)) {
        continue;
      }

      // Evaluate trigger condition
      const isTriggered = evaluateTrigger(trigger, vehicleData);

      if (isTriggered) {
        this.executeTrigger(trigger, vehicleData);
        this.triggeredIds.add(trigger.id);

        // Reset triggered state after 5 seconds
        this.scheduleReset(trigger.id, 5000);
      }
    }
  }

  /**
   * Execute trigger action
   */
  private async executeTrigger(
    trigger: Trigger,
    vehicleData: Record<string, number>
  ): Promise<void> {
    this.addLog(`⚡ Trigger activated: ${trigger.name}`);

    // Log vehicle data snapshot
    const dataSnapshot = Object.entries(vehicleData)
      .map(([key, value]) => `${key}=${value.toFixed(4)}`)
      .join(', ');
    this.addLog(`  Vehicle data: ${dataSnapshot}`);

    if (trigger.useRuleControl) {
      // Rule control mode: Execute emergency deceleration directly
      await this.executeEmergencyDeceleration(trigger);
    } else {
      // LLM mode: Will be implemented in next phase
      this.addLog('  LLM mode not yet implemented (use rule control for now)');
    }
  }

  /**
   * Execute emergency deceleration
   */
  private async executeEmergencyDeceleration(trigger: Trigger): Promise<void> {
    try {
      this.addLog('  → Executing emergency deceleration...');
      await carmakerStore.emergencyDecelerate(5000);
      this.addLog('  ✓ Emergency deceleration completed');
    } catch (error: any) {
      this.addLog(`  ✗ Emergency deceleration failed: ${error}`);
    }
  }

  /**
   * Schedule trigger reset
   */
  private scheduleReset(triggerId: number, delayMs: number): void {
    setTimeout(() => {
      this.triggeredIds.delete(triggerId);
      this.addLog(`  Reset trigger: ID ${triggerId}`);
    }, delayMs);
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
   * Clear logs
   */
  clearLogs(): void {
    this.logMessages = [];
  }

  /**
   * Cleanup (called on destroy)
   */
  cleanup(): void {
    this.stopMonitoring();
  }
}

export const triggerMonitor = new TriggerMonitor();
