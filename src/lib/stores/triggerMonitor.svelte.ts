import { invoke } from '@tauri-apps/api/core';
import { carmakerStore } from './carmakerStore.svelte';
import { evaluateTrigger } from '$lib/utils/triggerEvaluator';
import { parseVehicleCommands } from '$lib/actions/vehicleCommandParser';
import { executeCommandSequence, executeRuleCommands } from '$lib/actions/vehicleCommandExecutor';

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

    // Execute trigger action sequence (handles both LLM and Rule modes)
    await this.executeTriggerActionSequence(trigger, vehicleData);
  }

  /**
   * Execute trigger action sequence
   * 1. Trigger detected
   * 2. Pause simulation (time scale = 0.001x - ultra slow motion)
   * 3. LLM mode: Request LLM and wait for response / Rule mode: Wait 1 second
   * 4. Resume simulation (time scale = 1.0x) + Execute commands
   */
  private async executeTriggerActionSequence(trigger: Trigger, vehicleData: Record<string, number>): Promise<void> {
    try {
      // Step 1: Pause simulation (ultra-slow motion)
      this.addLog('  → Pausing simulation (time scale = 0.001x)');
      const wasMonitoring = await carmakerStore.pauseSimulation();

      if (trigger.useRuleControl) {
        // Rule mode: Wait 1 second
        this.addLog('  → Rule mode: Waiting 1 second...');
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Resume simulation and execute rule action
        this.addLog('  → Resuming simulation (time scale = 1.0x)');
        await carmakerStore.resumeSimulation(wasMonitoring);

        // Execute rule-based commands (parse debugAction)
        if (trigger.debugAction) {
          this.addLog('  → Executing rule-based commands');
          const result = await executeRuleCommands(trigger.debugAction, (msg) => this.addLog(msg));
          this.addLog(`  ✓ Executed ${result.successCount}/${result.totalCommands} commands (${result.executionTime}ms)`);
        }
      } else {
        // LLM mode: Request LLM and wait for response
        this.addLog('  → LLM mode: Requesting AI response...');
        const llmResponse = await this.requestLLM(trigger, vehicleData);

        // Resume simulation
        this.addLog('  → Resuming simulation (time scale = 1.0x)');
        await carmakerStore.resumeSimulation(wasMonitoring);

        // Parse and execute LLM response
        if (llmResponse) {
          this.addLog('  → Parsing LLM response and executing commands');
          const sequence = parseVehicleCommands(llmResponse);
          const result = await executeCommandSequence(sequence, (msg) => this.addLog(msg));
          this.addLog(`  ✓ Executed ${result.successCount}/${result.totalCommands} commands (${result.executionTime}ms)`);
        }
      }

      this.addLog('  ✓ Trigger action sequence completed');
    } catch (error: any) {
      this.addLog(`  ✗ Trigger action failed: ${error}`);
    }
  }

  /**
   * Request LLM response for trigger
   */
  private async requestLLM(trigger: Trigger, vehicleData: Record<string, number>): Promise<string | null> {
    try {
      // Build vehicle data snapshot
      const dataSnapshot = Object.entries(vehicleData)
        .map(([key, value]) => `${key}: ${value.toFixed(4)}`)
        .join('\n');

      // Build system context with trigger message and vehicle data
      const systemContext = `# Trigger Activated: ${trigger.name}

## Current Vehicle Data:
${dataSnapshot}

## Trigger Message:
${trigger.message}

**Instructions**: Analyze the current vehicle state and respond with vehicle control commands in the format:
\`\`\`
DM.Gas = <value>
DM.Brake = <value>
DM.Steer.Ang = <value>
\`\`\`

Provide appropriate control values (0.0 to 1.0 for Gas/Brake, rad for Steer.Ang) based on the situation.`;

      // Dispatch event to ChatView (system message)
      window.dispatchEvent(new CustomEvent('triggerChatMessage', {
        detail: {
          type: 'system',
          triggerName: trigger.name,
          content: systemContext
        }
      }));

      // Load trigger AI settings from localStorage
      const excludeHistory = localStorage.getItem('trigger_exclude_history') !== 'false'; // Default: true
      let characterId = localStorage.getItem('trigger_character_id');
      let promptTemplateId = localStorage.getItem('trigger_prompt_template_id');
      const model = localStorage.getItem('trigger_model') || 'sonnet';

      // If no trigger settings, fallback to default chat settings
      if (!characterId || !promptTemplateId) {
        try {
          const chatSettings: any = await invoke('get_chat_settings');
          if (!characterId && chatSettings.defaultCharacterId) {
            characterId = chatSettings.defaultCharacterId.toString();
          }
          if (!promptTemplateId && chatSettings.defaultPromptTemplateId) {
            promptTemplateId = chatSettings.defaultPromptTemplateId.toString();
          }
        } catch (err) {
          this.addLog('  ⚠ No chat settings found, trigger may fail');
        }
      }

      // Build request
      const request: any = {
        message: 'Trigger activated. Please provide vehicle control response.',
        systemContext: systemContext,
        role: 'system',
        excludeHistory: excludeHistory,
        model: model
      };

      // Add conversationId if exists (continue conversation)
      if (trigger.conversationId) {
        request.conversationId = trigger.conversationId;
      } else {
        // New conversation requires characterId and promptTemplateId
        if (characterId) request.characterId = parseInt(characterId);
        if (promptTemplateId) request.promptTemplateId = parseInt(promptTemplateId);
      }

      // Call AI chat with trigger conversation
      const response: any = await invoke('chat', { request });

      if (response.responses && response.responses.length > 0) {
        const llmResponse = response.responses[0];
        this.addLog(`  ✓ LLM response received (${llmResponse.length} chars)`);

        // Dispatch event to ChatView (LLM response)
        window.dispatchEvent(new CustomEvent('triggerChatMessage', {
          detail: {
            type: 'llm_response',
            triggerName: trigger.name,
            content: llmResponse
          }
        }));

        return llmResponse;
      }

      return null;
    } catch (error: any) {
      this.addLog(`  ✗ LLM request failed: ${error}`);

      // Dispatch error event
      window.dispatchEvent(new CustomEvent('triggerChatMessage', {
        detail: {
          type: 'error',
          triggerName: trigger.name,
          content: `LLM 요청 실패: ${error}`
        }
      }));

      return null;
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
