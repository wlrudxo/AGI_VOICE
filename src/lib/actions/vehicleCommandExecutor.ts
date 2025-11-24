/**
 * Vehicle Command Executor
 * Executes vehicle control commands via CarMaker
 *
 * Executes all commands sequentially with optional wait delays
 */

import { carmakerStore } from '$lib/stores/carmakerStore.svelte';
import type { VehicleCommand, SequenceItem, CommandSequence } from './vehicleCommandParser';

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
 */
export async function executeCommandSequence(
  sequence: CommandSequence,
  logger?: (message: string) => void
): Promise<ExecutionLog> {
  const startTime = Date.now();
  const results: ExecutionResult[] = [];

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
        // Wait until command (not implemented yet)
        log(`    ⏳ [${i + 1}/${sequence.items.length}] wait_until ${item.condition} (not implemented)`);
        results.push({
          success: false,
          item,
          error: 'wait_until not implemented yet',
          executedAt: Date.now()
        });
      } else {
        // Vehicle command
        const cmd = item as VehicleCommand;
        const result = await executeSingleCommand(cmd);
        results.push(result);

        if (result.success) {
          log(`    ✓ [${i + 1}/${sequence.items.length}] ${cmd.variable} = ${cmd.value} | ${cmd.duration}ms | ${cmd.mode}`);
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
