import "clsx";
import { invoke } from "@tauri-apps/api/core";
import { c as carmakerStore } from "./carmakerStore.svelte.js";
function replaceVariables(expression, vehicleData) {
  let result = expression;
  const sortedKeys = Object.keys(vehicleData).sort((a, b) => b.length - a.length);
  for (const key of sortedKeys) {
    const escapedKey = key.replace(/\./g, "\\.");
    const regex = new RegExp(`\\b${escapedKey}\\b`, "g");
    const value = vehicleData[key];
    if (value !== void 0 && value !== null) {
      result = result.replace(regex, value.toString());
    }
  }
  return result;
}
function evaluateExpression(expression, vehicleData) {
  try {
    const processedExpression = replaceVariables(expression, vehicleData);
    const result = new Function(`
      "use strict";
      const abs = Math.abs;
      const sqrt = Math.sqrt;
      const pow = Math.pow;
      const min = Math.min;
      const max = Math.max;
      return (${processedExpression});
    `)();
    if (typeof result === "boolean") {
      return result;
    } else if (typeof result === "number") {
      return result !== 0;
    } else {
      console.error("Expression evaluation returned non-boolean/number:", result);
      return false;
    }
  } catch (error) {
    console.error("[Expression] Evaluation failed:", error.message);
    console.error("  Expression:", expression);
    console.error("  Processed:", replaceVariables(expression, vehicleData));
    return false;
  }
}
function evaluateTrigger(trigger, vehicleData) {
  if (!trigger.isActive) {
    return false;
  }
  if (!trigger.expression || trigger.expression.trim() === "") {
    return false;
  }
  return evaluateExpression(trigger.expression, vehicleData);
}
function parseVehicleCommands(llmResponse) {
  const codeBlockMatch = llmResponse.match(/```(?:[\w]*)\n([\s\S]*?)\n```/);
  const commandText = codeBlockMatch ? codeBlockMatch[1] : llmResponse;
  const items = parseSequentialCommands(commandText);
  return {
    type: "sequential",
    items
  };
}
function parseSequentialCommands(text) {
  const items = [];
  const lines = text.split("\n").filter((line) => line.trim());
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || trimmed.startsWith("//")) {
      continue;
    }
    const waitMatch = trimmed.match(/^wait\s*\(?(\d+)\)?/i);
    if (waitMatch) {
      items.push({
        type: "wait",
        milliseconds: parseInt(waitMatch[1])
      });
      continue;
    }
    const waitUntilMatch = trimmed.match(/^wait_until\s+(.+?)(?:\s+(\d+))?$/i);
    if (waitUntilMatch) {
      items.push({
        type: "wait_until",
        condition: waitUntilMatch[1].trim(),
        timeout: waitUntilMatch[2] ? parseInt(waitUntilMatch[2]) : 3e4
      });
      continue;
    }
    const commandMatch = trimmed.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*\|\s*(-?\d+)(?:\s*\|\s*(AbsRamp|FacRamp|Abs|Off|Fac))?/i);
    if (commandMatch) {
      const variable = commandMatch[1];
      const value = parseFloat(commandMatch[2]);
      const duration = parseInt(commandMatch[3]);
      const mode = commandMatch[4] || "Abs";
      items.push({
        variable,
        value,
        duration,
        mode
      });
      continue;
    }
    const legacyMatch = trimmed.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)/);
    if (legacyMatch) {
      console.warn(`Legacy format detected (missing duration): ${trimmed}`);
      items.push({
        variable: legacyMatch[1],
        value: parseFloat(legacyMatch[2]),
        duration: 2e3,
        // Default duration
        mode: "Abs"
      });
    }
  }
  return items;
}
async function executeCommandSequence(sequence, logger) {
  const startTime = Date.now();
  const results = [];
  const pendingInfiniteCommands = [];
  const log = (msg) => {
    if (logger) logger(msg);
  };
  try {
    log("  → Sequential execution mode");
    for (let i = 0; i < sequence.items.length; i++) {
      const item = sequence.items[i];
      if ("type" in item && item.type === "wait") {
        log(`    ⏱️  [${i + 1}/${sequence.items.length}] wait ${item.milliseconds}ms`);
        await new Promise((resolve) => setTimeout(resolve, item.milliseconds));
        results.push({ success: true, item, executedAt: Date.now() });
      } else if ("type" in item && item.type === "wait_until") {
        log(`    ⏳ [${i + 1}/${sequence.items.length}] wait_until ${item.condition}`);
        const result = await executeWaitUntil(item, log);
        results.push(result);
        if (result.success && pendingInfiniteCommands.length > 0) {
          log(`    ↻ Resetting ${pendingInfiniteCommands.length} infinite-duration command(s)...`);
          for (const cmd of pendingInfiniteCommands) {
            const resetCmd = { ...cmd, duration: 1 };
            const resetResult = await executeSingleCommand(resetCmd);
            if (resetResult.success) {
              log(`    ✓ Reset: ${cmd.variable} = ${cmd.value} | 1ms (was ${cmd.duration === -1 ? "99999ms effective" : cmd.duration + "ms"})`);
            } else {
              log(`    ✗ Failed to reset: ${cmd.variable}`);
            }
          }
          pendingInfiniteCommands.length = 0;
        }
      } else {
        const cmd = item;
        const result = await executeSingleCommand(cmd);
        results.push(result);
        if (result.success) {
          const displayDuration = cmd.duration === -1 ? "99999ms (infinite)" : `${cmd.duration}ms`;
          log(`    ✓ [${i + 1}/${sequence.items.length}] ${cmd.variable} = ${cmd.value} | ${displayDuration} | ${cmd.mode}`);
          if (cmd.duration === -1) {
            pendingInfiniteCommands.push(cmd);
            log(`    → Tracking infinite-duration command: ${cmd.variable}`);
          }
        } else {
          log(`    ✗ [${i + 1}/${sequence.items.length}] Failed: ${cmd.variable}`);
        }
      }
      if (i < sequence.items.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
    }
    const successCount = results.filter((r) => r.success).length;
    const failureCount = results.filter((r) => !r.success).length;
    return {
      totalItems: results.length,
      successCount,
      failureCount,
      results,
      executionTime: Date.now() - startTime
    };
  } catch (error) {
    log(`  ✗ Execution failed: ${error}`);
    return {
      totalItems: sequence.items.length,
      successCount: 0,
      failureCount: sequence.items.length,
      results: [{ success: false, error: error.message || String(error) }],
      executionTime: Date.now() - startTime
    };
  }
}
async function executeSingleCommand(cmd) {
  try {
    const actualDuration = cmd.duration === -1 ? 99999 : cmd.duration;
    const command = `DVAWrite ${cmd.variable} ${cmd.value} ${actualDuration} ${cmd.mode}`;
    await carmakerStore.executeCommand(command);
    return {
      success: true,
      item: cmd,
      executedAt: Date.now()
    };
  } catch (error) {
    return {
      success: false,
      item: cmd,
      error: error.message || String(error),
      executedAt: Date.now()
    };
  }
}
function parseSimpleCondition(condition) {
  const match = condition.match(/^\s*([A-Za-z0-9._]+)\s*(>=|<=|==|!=|>|<)\s*([0-9.-]+)\s*$/);
  if (!match) {
    return null;
  }
  return {
    variable: match[1],
    operator: match[2],
    value: match[3]
  };
}
function evaluateSimpleCondition(condition, vehicleData) {
  const { variable, operator, value } = condition;
  const actualValue = vehicleData[variable];
  if (actualValue === void 0 || actualValue === null) {
    return false;
  }
  const expectedValue = parseFloat(value);
  if (isNaN(expectedValue)) {
    return false;
  }
  switch (operator) {
    case ">":
      return actualValue > expectedValue;
    case "<":
      return actualValue < expectedValue;
    case ">=":
      return actualValue >= expectedValue;
    case "<=":
      return actualValue <= expectedValue;
    case "==":
      return Math.abs(actualValue - expectedValue) < 1e-4;
    // Float comparison with epsilon
    case "!=":
      return Math.abs(actualValue - expectedValue) >= 1e-4;
    default:
      return false;
  }
}
async function executeWaitUntil(waitCmd, logger) {
  const startTime = Date.now();
  const timeout = waitCmd.timeout || 3e4;
  const log = (msg) => {
    if (logger) logger(msg);
  };
  log(`    ⏳ Waiting for: ${waitCmd.condition} (timeout: ${timeout}ms)`);
  const parsedCondition = parseSimpleCondition(waitCmd.condition);
  if (!parsedCondition) {
    const error = `Invalid condition format: ${waitCmd.condition}`;
    log(`    ✗ ${error}`);
    return {
      success: false,
      item: waitCmd,
      error,
      executedAt: Date.now()
    };
  }
  let iteration = 0;
  while (true) {
    const elapsed = Date.now() - startTime;
    if (elapsed > timeout) {
      const error = `Timeout after ${timeout}ms: ${waitCmd.condition}`;
      log(`    ✗ ${error}`);
      return {
        success: false,
        item: waitCmd,
        error,
        executedAt: Date.now()
      };
    }
    const vehicleData = carmakerStore.monitorData;
    if (Object.keys(vehicleData).length === 0) {
      await new Promise((resolve) => setTimeout(resolve, 100));
      continue;
    }
    if (iteration % 10 === 0) {
      const currentValue = vehicleData[parsedCondition.variable];
      if (currentValue !== void 0) {
        log(`    → ${parsedCondition.variable} = ${currentValue.toFixed(4)} (checking ${parsedCondition.operator} ${parsedCondition.value})`);
      }
    }
    const result = evaluateSimpleCondition(parsedCondition, vehicleData);
    if (result) {
      const currentValue = vehicleData[parsedCondition.variable];
      log(`    ✓ Condition met: ${parsedCondition.variable} = ${currentValue?.toFixed(4)}`);
      return {
        success: true,
        item: waitCmd,
        executedAt: Date.now()
      };
    }
    iteration++;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
}
class TriggerMonitor {
  // Monitoring state
  isMonitoring = false;
  monitorInterval = null;
  // Triggers
  triggers = [];
  // Triggered history (prevent duplicate triggers)
  triggeredIds = /* @__PURE__ */ new Set();
  resetTimeout = null;
  // Execution state (prevent checking during trigger execution)
  isExecuting = false;
  // Logs
  logMessages = [];
  /**
   * Load triggers from backend
   */
  async loadTriggers() {
    try {
      this.triggers = await invoke("get_triggers");
      this.addLog(`✓ Loaded ${this.triggers.length} triggers`);
    } catch (error) {
      this.addLog(`✗ Failed to load triggers: ${error}`);
    }
  }
  /**
   * Start trigger monitoring
   * Checks trigger conditions every 100ms (10Hz)
   */
  async startMonitoring() {
    if (this.isMonitoring) {
      return;
    }
    await this.loadTriggers();
    this.isMonitoring = true;
    this.triggeredIds.clear();
    this.addLog("✓ Started trigger monitoring (10Hz)");
    this.monitorInterval = window.setInterval(
      () => {
        this.checkTriggers();
      },
      100
    );
  }
  /**
   * Stop trigger monitoring
   */
  stopMonitoring() {
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
    this.addLog("✓ Stopped trigger monitoring");
  }
  /**
   * Check all triggers against current vehicle data
   */
  checkTriggers() {
    if (this.isExecuting) {
      return;
    }
    const vehicleData = carmakerStore.monitorData;
    if (Object.keys(vehicleData).length === 0) {
      return;
    }
    for (const trigger of this.triggers) {
      if (!trigger.isActive) {
        continue;
      }
      if (this.triggeredIds.has(trigger.id)) {
        continue;
      }
      const isTriggered = evaluateTrigger(trigger, vehicleData);
      if (isTriggered) {
        this.executeTrigger(trigger, vehicleData);
        this.triggeredIds.add(trigger.id);
        this.scheduleReset(trigger.id, trigger.cooldown);
      }
    }
  }
  /**
   * Execute trigger action
   */
  async executeTrigger(trigger, vehicleData) {
    this.addLog(`⚡ Trigger activated: ${trigger.name}`);
    const dataSnapshot = Object.entries(vehicleData).map(([key, value]) => `${key}=${value.toFixed(4)}`).join(", ");
    this.addLog(`  Vehicle data: ${dataSnapshot}`);
    this.isExecuting = true;
    try {
      await this.executeTriggerActionSequence(trigger, vehicleData);
    } finally {
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
  async executeTriggerActionSequence(trigger, vehicleData) {
    try {
      this.addLog("  → Pausing simulation (time scale = 0.001x)");
      const wasMonitoring = await carmakerStore.pauseSimulation();
      if (trigger.useRuleControl) {
        this.addLog("  → Rule mode: Waiting 1 second...");
        await new Promise((resolve) => setTimeout(resolve, 1e3));
        this.addLog("  → Resuming simulation (time scale = 1.0x)");
        await carmakerStore.resumeSimulation(wasMonitoring);
        if (trigger.debugAction) {
          this.addLog("  → Executing rule-based commands");
          const sequence = parseVehicleCommands(trigger.debugAction);
          const result = await executeCommandSequence(sequence, (msg) => this.addLog(msg));
          this.addLog(`  ✓ Executed ${result.successCount}/${result.totalItems} commands (${result.executionTime}ms)`);
        }
      } else {
        this.addLog("  → LLM mode: Requesting AI response...");
        const llmResponse = await this.requestLLM(trigger, vehicleData);
        this.addLog("  → Resuming simulation (time scale = 1.0x)");
        await carmakerStore.resumeSimulation(wasMonitoring);
        if (llmResponse) {
          this.addLog("  → Parsing LLM response and executing commands");
          const sequence = parseVehicleCommands(llmResponse);
          const result = await executeCommandSequence(sequence, (msg) => this.addLog(msg));
          this.addLog(`  ✓ Executed ${result.successCount}/${result.totalItems} commands (${result.executionTime}ms)`);
        }
      }
      this.addLog("  ✓ Trigger action sequence completed");
    } catch (error) {
      this.addLog(`  ✗ Trigger action failed: ${error}`);
    }
  }
  /**
   * Request LLM response for trigger
   */
  async requestLLM(trigger, vehicleData) {
    try {
      const dataSnapshot = Object.entries(vehicleData).map(([key, value]) => `${key}: ${value.toFixed(4)}`).join("\n");
      const systemContext = `## Current Vehicle Data:
${dataSnapshot}

## Trigger Message:
${trigger.message}`;
      window.dispatchEvent(new CustomEvent("triggerChatMessage", {
        detail: {
          type: "system",
          triggerName: trigger.name,
          content: systemContext
        }
      }));
      const excludeHistory = localStorage.getItem("trigger_exclude_history") !== "false";
      let characterId = localStorage.getItem("trigger_character_id");
      let promptTemplateId = localStorage.getItem("trigger_prompt_template_id");
      const model = localStorage.getItem("trigger_model") || "sonnet";
      if (!characterId || !promptTemplateId) {
        try {
          const chatSettings = await invoke("get_chat_settings");
          if (!characterId && chatSettings.defaultCharacterId) {
            characterId = chatSettings.defaultCharacterId.toString();
          }
          if (!promptTemplateId && chatSettings.defaultPromptTemplateId) {
            promptTemplateId = chatSettings.defaultPromptTemplateId.toString();
          }
        } catch (err) {
          this.addLog("  ⚠ No chat settings found, trigger may fail");
        }
      }
      const request = {
        message: "Trigger activated. Please provide vehicle control response.",
        systemContext,
        role: "system",
        excludeHistory,
        noSave: excludeHistory,
        // Don't save to DB if excludeHistory is true
        model,
        characterId: characterId ? parseInt(characterId) : void 0,
        promptTemplateId: promptTemplateId ? parseInt(promptTemplateId) : void 0
      };
      const response = await invoke("chat", { request });
      if (response.responses && response.responses.length > 0) {
        const llmResponse = response.responses[0];
        this.addLog(`  ✓ LLM response received (${llmResponse.length} chars)`);
        window.dispatchEvent(new CustomEvent("triggerChatMessage", {
          detail: {
            type: "llm_response",
            triggerName: trigger.name,
            content: llmResponse
          }
        }));
        return llmResponse;
      }
      return null;
    } catch (error) {
      this.addLog(`  ✗ LLM request failed: ${error}`);
      window.dispatchEvent(new CustomEvent("triggerChatMessage", {
        detail: {
          type: "error",
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
  scheduleReset(triggerId, delayMs) {
    setTimeout(
      () => {
        this.triggeredIds.delete(triggerId);
        this.addLog(`  Reset trigger: ID ${triggerId}`);
      },
      delayMs
    );
  }
  /**
   * Add log message
   */
  addLog(message) {
    const timestamp = /* @__PURE__ */ (/* @__PURE__ */ new Date()).toLocaleTimeString();
    this.logMessages = [...this.logMessages, `[${timestamp}] ${message}`];
    if (this.logMessages.length > 100) {
      this.logMessages = this.logMessages.slice(-100);
    }
  }
  /**
   * Clear logs
   */
  clearLogs() {
    this.logMessages = [];
  }
  /**
   * Cleanup (called on destroy)
   */
  cleanup() {
    this.stopMonitoring();
  }
}
const triggerMonitor = new TriggerMonitor();
export {
  triggerMonitor as t
};
