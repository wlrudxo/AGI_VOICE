/**
 * Vehicle Command Executor
 * Executes vehicle control commands via CarMaker
 *
 * Executes all commands sequentially with optional wait delays
 */

import { carmakerStore } from '$lib/stores/carmakerStore.svelte';
import type { VehicleCommand, SequenceItem, CommandSequence, WaitUntilCommand } from './vehicleCommandParser';

/**
 * Parsed condition for wait_until evaluation
 */
interface ParsedCondition {
  variable: string;
  operator: string;
  value: string;
}

export interface ExecutionResult {
  success: boolean;
  item?: SequenceItem;
  error?: string;
  executedAt?: number;
}

export interface ExecutionLog {
  totalItems: number;
  successCount: number;
  failureCount: number;
  results: ExecutionResult[];
  executionTime: number;
}

/**
 * Execute vehicle command sequence
 * All commands execute sequentially (no parallel execution)
 *
 * Special handling for duration=-1:
 * - Commands with duration=-1 are tracked
 * - When wait_until is encountered and condition is met, all pending -1 commands
 *   are automatically reset by sending the same command with duration=1ms
 * - This releases control back to autonomous driving algorithm
 */
export async function executeCommandSequence(
  sequence: CommandSequence,
  logger?: (message: string) => void
): Promise<ExecutionLog> {
  const startTime = Date.now();
  const results: ExecutionResult[] = [];
  const pendingInfiniteCommands: VehicleCommand[] = []; // Track duration=-1 commands

  const log = (msg: string) => {
    if (logger) logger(msg);
  };

  try {
    log('  → Sequential execution mode');

    // Execute all items sequentially
    for (let i = 0; i < sequence.items.length; i++) {
      const item = sequence.items[i];

      // Execute based on item type
      if ('type' in item && item.type === 'wait') {
        // Wait command
        log(`    ⏱️  [${i + 1}/${sequence.items.length}] wait ${item.milliseconds}ms`);
        await new Promise(resolve => setTimeout(resolve, item.milliseconds));
        results.push({ success: true, item, executedAt: Date.now() });
      } else if ('type' in item && item.type === 'wait_until') {
        // Wait until command
        log(`    ⏳ [${i + 1}/${sequence.items.length}] wait_until ${item.condition}`);
        const result = await executeWaitUntil(item, log);
        results.push(result);

        // If wait_until succeeded, reset all pending infinite commands
        if (result.success && pendingInfiniteCommands.length > 0) {
          log(`    ↻ Resetting ${pendingInfiniteCommands.length} infinite-duration command(s)...`);

          for (const cmd of pendingInfiniteCommands) {
            // Send same command with 1ms duration to reset
            const resetCmd: VehicleCommand = { ...cmd, duration: 1 };
            const resetResult = await executeSingleCommand(resetCmd);

            if (resetResult.success) {
              log(`    ✓ Reset: ${cmd.variable} = ${cmd.value} | 1ms (was -1ms)`);
            } else {
              log(`    ✗ Failed to reset: ${cmd.variable}`);
            }
          }

          // Clear pending commands after reset
          pendingInfiniteCommands.length = 0;
        }
      } else {
        // Vehicle command
        const cmd = item as VehicleCommand;
        const result = await executeSingleCommand(cmd);
        results.push(result);

        if (result.success) {
          log(`    ✓ [${i + 1}/${sequence.items.length}] ${cmd.variable} = ${cmd.value} | ${cmd.duration}ms | ${cmd.mode}`);

          // Track commands with duration=-1
          if (cmd.duration === -1) {
            pendingInfiniteCommands.push(cmd);
            log(`    → Tracking infinite-duration command: ${cmd.variable}`);
          }
        } else {
          log(`    ✗ [${i + 1}/${sequence.items.length}] Failed: ${cmd.variable}`);
        }
      }

      // Small delay between commands (50ms) to prevent command flooding
      if (i < sequence.items.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 50));
      }
    }

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    return {
      totalItems: results.length,
      successCount,
      failureCount,
      results,
      executionTime: Date.now() - startTime
    };
  } catch (error: any) {
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

/**
 * Execute single vehicle command
 */
async function executeSingleCommand(cmd: VehicleCommand): Promise<ExecutionResult> {
  try {
    const command = `DVAWrite ${cmd.variable} ${cmd.value} ${cmd.duration} ${cmd.mode}`;

    await carmakerStore.executeCommand(command);

    return {
      success: true,
      item: cmd,
      executedAt: Date.now()
    };
  } catch (error: any) {
    return {
      success: false,
      item: cmd,
      error: error.message || String(error),
      executedAt: Date.now()
    };
  }
}

/**
 * Parse simple condition string
 * Supports: "Car.v >= 27.78", "DM.Brake < 0.1", etc.
 */
function parseSimpleCondition(condition: string): ParsedCondition | null {
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

/**
 * Evaluate a simple condition against vehicle data
 */
function evaluateSimpleCondition(
  condition: ParsedCondition,
  vehicleData: Record<string, number>
): boolean {
  const { variable, operator, value } = condition;

  // Get actual value from vehicle data
  const actualValue = vehicleData[variable];
  if (actualValue === undefined || actualValue === null) {
    return false; // Variable not available
  }

  // Parse expected value
  const expectedValue = parseFloat(value);
  if (isNaN(expectedValue)) {
    return false; // Invalid value format
  }

  // Evaluate operator
  switch (operator) {
    case '>':
      return actualValue > expectedValue;
    case '<':
      return actualValue < expectedValue;
    case '>=':
      return actualValue >= expectedValue;
    case '<=':
      return actualValue <= expectedValue;
    case '==':
      return Math.abs(actualValue - expectedValue) < 0.0001; // Float comparison with epsilon
    case '!=':
      return Math.abs(actualValue - expectedValue) >= 0.0001;
    default:
      return false; // Unknown operator
  }
}

/**
 * Execute wait_until command
 * Polls vehicle data at 10Hz (100ms) until condition is met or timeout
 */
async function executeWaitUntil(
  waitCmd: WaitUntilCommand,
  logger?: (msg: string) => void
): Promise<ExecutionResult> {
  const startTime = Date.now();
  const timeout = waitCmd.timeout || 30000; // Default 30s timeout

  const log = (msg: string) => {
    if (logger) logger(msg);
  };

  log(`    ⏳ Waiting for: ${waitCmd.condition} (timeout: ${timeout}ms)`);

  // Parse condition
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
    // Check timeout
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

    // Get current vehicle data from carmakerStore
    const vehicleData = carmakerStore.monitorData;

    // Skip if no data available yet
    if (Object.keys(vehicleData).length === 0) {
      await new Promise(resolve => setTimeout(resolve, 100));
      continue;
    }

    // Log current value every 1 second (10 iterations at 100ms)
    if (iteration % 10 === 0) {
      const currentValue = vehicleData[parsedCondition.variable];
      if (currentValue !== undefined) {
        log(`    → ${parsedCondition.variable} = ${currentValue.toFixed(4)} (checking ${parsedCondition.operator} ${parsedCondition.value})`);
      }
    }

    // Evaluate condition
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

    // Wait 100ms before next check (10Hz polling)
    await new Promise(resolve => setTimeout(resolve, 100));
  }
}

/**
 * Execute rule-based commands (from debugAction)
 * Supports both legacy format and new unified format
 */
export async function executeRuleCommands(
  debugAction: string,
  logger?: (message: string) => void
): Promise<ExecutionLog> {
  const startTime = Date.now();
  const results: ExecutionResult[] = [];
  const lines = debugAction.split('\n').filter(line => line.trim());

  const log = (msg: string) => {
    if (logger) logger(msg);
  };

  for (const line of lines) {
    const trimmed = line.trim();

    // Try new format first: "DM.Gas = 0.5 | 2000 | Abs"
    // Note: Longer patterns first to avoid partial matching
    const newFormatMatch = trimmed.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*\|\s*(\d+)(?:\s*\|\s*(AbsRamp|FacRamp|Abs|Off|Fac))?/i);
    if (newFormatMatch) {
      const variable = newFormatMatch[1];
      const value = parseFloat(newFormatMatch[2]);
      const duration = parseInt(newFormatMatch[3]);
      const mode = newFormatMatch[4] || 'Abs';

      try {
        const command = `DVAWrite ${variable} ${value} ${duration} ${mode}`;
        await carmakerStore.executeCommand(command);
        results.push({ success: true, item: { variable, value, duration, mode } });
        log(`    ✓ ${variable} = ${value} | ${duration}ms | ${mode}`);
      } catch (error: any) {
        results.push({
          success: false,
          item: { variable, value, duration, mode },
          error: error.message || String(error)
        });
        log(`    ✗ Failed: ${variable} = ${value}`);
      }
      continue;
    }

    // Fallback to legacy format: "DM.Gas = 0.5"
    const legacyMatch = trimmed.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*$/);
    if (legacyMatch) {
      const variable = legacyMatch[1];
      const value = parseFloat(legacyMatch[2]);

      try {
        const command = `DVAWrite ${variable} ${value} 2000 Abs`;
        await carmakerStore.executeCommand(command);
        results.push({ success: true, item: { variable, value, duration: 2000, mode: 'Abs' } });
        log(`    ✓ ${variable} = ${value} (legacy format, 2000ms Abs)`);
      } catch (error: any) {
        results.push({
          success: false,
          item: { variable, value, duration: 2000, mode: 'Abs' },
          error: error.message || String(error)
        });
        log(`    ✗ Failed: ${variable} = ${value}`);
      }
    }
  }

  const successCount = results.filter(r => r.success).length;
  const failureCount = results.filter(r => !r.success).length;

  return {
    totalItems: results.length,
    successCount,
    failureCount,
    results,
    executionTime: Date.now() - startTime
  };
}
