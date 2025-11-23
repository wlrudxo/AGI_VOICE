/**
 * Vehicle Command Executor
 * Executes vehicle control commands via CarMaker
 */

import { carmakerStore } from '$lib/stores/carmakerStore.svelte';
import type { VehicleCommand, CommandSequence } from './vehicleCommandParser';

export interface ExecutionResult {
  success: boolean;
  command?: VehicleCommand;
  error?: string;
  executedAt?: number;
}

export interface ExecutionLog {
  totalCommands: number;
  successCount: number;
  failureCount: number;
  results: ExecutionResult[];
  executionTime: number;
}

/**
 * Execute vehicle command sequence
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
    if (sequence.type === 'script') {
      // Rust script execution (Phase 3 - not implemented yet)
      log('  → Script mode not yet implemented');
      return {
        totalCommands: 0,
        successCount: 0,
        failureCount: 1,
        results: [{ success: false, error: 'Script execution not implemented' }],
        executionTime: Date.now() - startTime
      };
    } else if (sequence.type === 'sequential') {
      // Sequential execution with delays
      log('  → Sequential execution mode');
      for (let i = 0; i < sequence.commands.length; i++) {
        const cmd = sequence.commands[i];
        const result = await executeSingleCommand(cmd);
        results.push(result);

        if (result.success) {
          log(`    ✓ [${i + 1}/${sequence.commands.length}] ${cmd.variable} = ${cmd.value}`);
        } else {
          log(`    ✗ [${i + 1}/${sequence.commands.length}] Failed: ${cmd.variable}`);
        }

        // Delay between commands (default 200ms)
        if (i < sequence.commands.length - 1) {
          await new Promise(resolve => setTimeout(resolve, sequence.delay || 200));
        }
      }
    } else {
      // Simple parallel execution
      log('  → Simple execution mode');
      const execResults = await Promise.all(
        sequence.commands.map(cmd => executeSingleCommand(cmd))
      );
      results.push(...execResults);

      execResults.forEach((result, i) => {
        const cmd = sequence.commands[i];
        if (result.success) {
          log(`    ✓ ${cmd.variable} = ${cmd.value}`);
        } else {
          log(`    ✗ Failed: ${cmd.variable}`);
        }
      });
    }

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    return {
      totalCommands: results.length,
      successCount,
      failureCount,
      results,
      executionTime: Date.now() - startTime
    };
  } catch (error: any) {
    log(`  ✗ Execution failed: ${error}`);
    return {
      totalCommands: sequence.commands.length,
      successCount: 0,
      failureCount: sequence.commands.length,
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
    const duration = cmd.duration || 2000;
    const mode = cmd.mode || 'Abs';
    const command = `DVAWrite ${cmd.variable} ${cmd.value} ${duration} ${mode}`;

    await carmakerStore.executeCommand(command);

    return {
      success: true,
      command: cmd,
      executedAt: Date.now()
    };
  } catch (error: any) {
    return {
      success: false,
      command: cmd,
      error: error.message || String(error),
      executedAt: Date.now()
    };
  }
}

/**
 * Execute rule-based commands (from debugAction)
 * Simple text parsing: "DM.Gas = 0.5\nDM.Brake = 0.0"
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
    const match = line.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*$/);
    if (match) {
      const variable = match[1];
      const value = parseFloat(match[2]);

      try {
        const command = `DVAWrite ${variable} ${value} 2000 Abs`;
        await carmakerStore.executeCommand(command);
        results.push({ success: true, command: { variable, value } });
        log(`    ✓ ${variable} = ${value}`);
      } catch (error: any) {
        results.push({
          success: false,
          command: { variable, value },
          error: error.message || String(error)
        });
        log(`    ✗ Failed: ${variable} = ${value}`);
      }
    }
  }

  const successCount = results.filter(r => r.success).length;
  const failureCount = results.filter(r => !r.success).length;

  return {
    totalCommands: results.length,
    successCount,
    failureCount,
    results,
    executionTime: Date.now() - startTime
  };
}
