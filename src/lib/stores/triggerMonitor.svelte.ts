import { invoke } from '@tauri-apps/api/core';
import { carmakerStore } from './carmakerStore.svelte';
import { evaluateTrigger } from '$lib/utils/triggerEvaluator';
import { parseVehicleCommands } from '$lib/actions/vehicleCommandParser';
import { executeCommandSequence, executeRuleCommands } from '$lib/actions/vehicleCommandExecutor';

interface Trigger {
  id: number;
  name: string;
  isActive: boolean;
  expression: string; // Expression string (e.g., "Traffic.T01.sRoad - Traffic.T00.sRoad < 100")
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

  // Execution state (prevent checking during trigger execution)
  private isExecuting = false;

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
    // Skip if already executing a trigger
    if (this.isExecuting) {
      return;
    }

    const vehicleData = carmakerStore.monitorData;

    // Skip if no vehicle data available
    if (Object.keys(vehicleData).length === 0) {
      return;
    }

    for (const trigger of this.triggers) {
      // Skip if not active
      if (!trigger.isActive) {
        continue;
      }

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

    // Set executing flag to prevent other triggers during execution
    this.isExecuting = true;

    try {
      // Execute trigger action sequence (handles both LLM and Rule modes)
      await this.executeTriggerActionSequence(trigger, vehicleData);
    } finally {
      // Always clear executing flag
      this.isExecuting = false;
    }
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

**Instructions**: Analyze the current vehicle state and respond with vehicle control commands.

**Required Format** (use code block):
\`\`\`
DM.Gas = <value> | <duration_ms>
DM.Brake = <value> | <duration_ms>
DM.Steer.Ang = <value> | <duration_ms>
DM.v.Trgt = <value> | <duration_ms>
DM.LaneOffset = <value> | <duration_ms>
wait <milliseconds>
wait_until <condition>
\`\`\`

**Format Rules**:
- Each command: \`variable = value | duration\`
- **duration is REQUIRED** (milliseconds)
  - Positive value: Command is active for specified duration
  - **-1 (infinite)**: Command remains active until reset by \`wait_until\`
- Use \`wait <ms>\` for explicit delays between commands
- Use \`wait_until <condition>\` to wait for vehicle state (supports: >, <, >=, <=, ==, !=)
  - When condition is met, all commands with \`duration=-1\` are **automatically reset**
- All commands execute sequentially (top to bottom)

**Duration -1 Pattern** (Recommended for Conditional Control):
\`\`\`
DM.Gas = 0.0 | -1       # Hold gas at 0 indefinitely
DM.Brake = 0.5 | -1     # Hold brake at 0.5 indefinitely
wait_until Car.v <= 3.0 # Wait until speed drops to 3 m/s
                        # System auto-resets Gas and Brake when condition is met
DM.Brake = 0.0 | 100    # Now apply new brake command
\`\`\`

**Important Notes**:
- **CarMaker commands execute in parallel**, not sequentially
- To ensure sequential execution: use \`wait <duration>\` equal to or greater than previous command duration
- **Prefer duration=-1 + wait_until pattern** for condition-based control (simpler and more reliable)
- Only use -1 for **DM.* (vehicle control)** commands, NOT for SC.* (simulation control)

**Example 1 - Fixed Duration**:
\`\`\`
DM.Gas = 0.8 | 1000
wait 1000               # Wait for Gas to complete
DM.Brake = 0.3 | 2000
\`\`\`

**Example 2 - Conditional Control (Recommended)**:
\`\`\`
DM.Gas = 0.0 | -1       # Stop accelerating (hold)
DM.Brake = 0.5 | -1     # Apply brake (hold)
wait_until Car.v <= 3.0 # Wait until slow enough (auto-reset Gas/Brake)
DM.Brake = 0.0 | 100    # Release brake
wait 200
DM.Steer.Ang = 0.35 | 2000
\`\`\`

**Value Ranges**:
- Gas/Brake: 0.0 to 1.0
- Steer.Ang: radians (typically -0.5 to 0.5)
- v.Trgt: m/s (target speed, e.g., 13.89 for 50 km/h)
- LaneOffset: meters (lateral offset from lane center, e.g., 0.5 for left, -0.5 for right)

**Additional Examples**:

**Example 3 - Speed Control**:
\`\`\`
DM.v.Trgt = 13.89 | 5000   # Set target speed to 50 km/h
wait_until Car.v >= 13.0   # Wait until speed reaches ~47 km/h
DM.v.Trgt = 0.0 | 1000     # Reset target speed
\`\`\`

**Example 4 - Lane Change**:
\`\`\`
DM.LaneOffset = 0.5 | 3000  # Move 0.5m to the left
wait 3000
DM.LaneOffset = 0.0 | 2000  # Return to lane center
\`\`\`

**Example 5 - Combined Control**:
\`\`\`
DM.Gas = 0.8 | 2000           # Accelerate
DM.LaneOffset = 0.5 | 3000    # Change lane while accelerating
wait_until Car.v >= 20.0      # Wait until speed reaches 20 m/s
DM.v.Trgt = 20.0 | -1         # Maintain speed at 20 m/s
wait_until DM.LaneOffset >= 0.45  # Wait until lane change completes
\`\`\`

Provide appropriate control values based on the situation.`;

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
        noSave: excludeHistory, // Don't save to DB if excludeHistory is true
        model: model,
        characterId: characterId ? parseInt(characterId) : undefined,
        promptTemplateId: promptTemplateId ? parseInt(promptTemplateId) : undefined
      };

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
