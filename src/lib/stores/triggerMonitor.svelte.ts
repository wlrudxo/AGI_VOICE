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
   * Execute trigger action sequence
   * 1. Trigger detected
   * 2. Pause simulation (time scale = 0.001x - ultra slow motion)
   * 3. LLM mode: Request LLM and wait for response / Rule mode: Wait 1 second
   * 4. Resume simulation (time scale = 1.0x) + Execute commands
   */
  private async executeEmergencyDeceleration(trigger: Trigger): Promise<void> {
    try {
      // Step 1: Pause simulation (ultra-slow motion)
      this.addLog('  → Pausing simulation (time scale = 0.001x)');
      const wasMonitoring = await carmakerStore.pauseSimulation();

      if (trigger.useRuleControl) {
        // Step 2: Rule mode - Wait 1 second
        this.addLog('  → Rule mode: Waiting 1 second...');
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Step 3: Resume simulation and execute rule action
        this.addLog('  → Resuming simulation (time scale = 1.0x)');
        await carmakerStore.resumeSimulation(wasMonitoring);

        // Execute rule-based commands (parse debugAction)
        if (trigger.debugAction) {
          this.addLog('  → Executing rule-based commands');
          await this.executeRuleCommands(trigger.debugAction);
        }
      } else {
        // LLM mode (to be implemented)
        this.addLog('  → LLM mode: Not yet implemented');
        await new Promise(resolve => setTimeout(resolve, 1000));
        await carmakerStore.resumeSimulation(wasMonitoring);
      }

      this.addLog('  ✓ Trigger action sequence completed');
    } catch (error: any) {
      this.addLog(`  ✗ Trigger action failed: ${error}`);
    }
  }

  /**
   * Execute rule-based commands from debugAction
   * Parse format: "DM.Gas = 0.5\nDM.Brake = 0.0\n..."
   */
  private async executeRuleCommands(debugAction: string): Promise<void> {
    const lines = debugAction.split('\n').filter(line => line.trim());

    for (const line of lines) {
      const match = line.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*$/);
      if (match) {
        const [_, variable, value] = match;
        const command = `DVAWrite ${variable} ${value} 2000 Abs`;
        try {
          await carmakerStore.executeCommand(command);
          this.addLog(`    ✓ ${variable} = ${value}`);
        } catch (error: any) {
          this.addLog(`    ✗ Failed: ${variable} = ${value}`);
        }
      }
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
