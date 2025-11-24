/**
 * Vehicle Command Parser
 * Parses LLM responses and extracts vehicle control commands
 *
 * Unified Format (inspired by CarMaker_RealtimeControl Python implementation):
 * ```
 * DM.Gas = 0.8 | 1000
 * wait 500
 * DM.Brake = 0.2 | 2000
 * wait_until Car.v <= 13.89
 * DM.Gas = 0.0 | 500
 * ```
 *
 * Rules:
 * - Format: variable = value | duration
 * - duration is REQUIRED (in milliseconds)
 * - All commands execute sequentially
 * - wait <ms> adds explicit delay
 * - wait_until <condition> waits for condition (supports: >, <, >=, <=, ==, !=)
 *
 * Technical Notes:
 * - Mode is internally set to 'Abs' (absolute value) for all commands
 * - Parser supports multiple modes (Abs, Off, Fac, AbsRamp, FacRamp) but they are
 *   hidden from LLM interface to ensure predictable behavior
 * - LLM should only use the simplified format without specifying mode
 */

export interface VehicleCommand {
  variable: string;
  value: number;
  duration: number;
  mode: string;
}

export interface WaitCommand {
  type: 'wait';
  milliseconds: number;
}

export interface WaitUntilCommand {
  type: 'wait_until';
  condition: string;
  timeout?: number;
}

export type SequenceItem = VehicleCommand | WaitCommand | WaitUntilCommand;

export interface CommandSequence {
  type: 'sequential';
  items: SequenceItem[];
}

/**
 * Parse LLM response and extract vehicle commands
 * Always returns sequential execution
 */
export function parseVehicleCommands(llmResponse: string): CommandSequence {
  // Try to extract code block first
  const codeBlockMatch = llmResponse.match(/```(?:[\w]*)\n([\s\S]*?)\n```/);
  const commandText = codeBlockMatch ? codeBlockMatch[1] : llmResponse;

  // Parse all commands and wait statements
  const items = parseSequentialCommands(commandText);

  return {
    type: 'sequential',
    items
  };
}

/**
 * Parse commands in unified format
 * Format: variable = value | duration [| mode]
 * Also supports: wait <ms>, wait_until <condition>
 */
function parseSequentialCommands(text: string): SequenceItem[] {
  const items: SequenceItem[] = [];
  const lines = text.split('\n').filter(line => line.trim());

  for (const line of lines) {
    const trimmed = line.trim();

    // Skip comments and empty lines
    if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith('//')) {
      continue;
    }

    // Check for wait command: "wait 500" or "wait(500)"
    const waitMatch = trimmed.match(/^wait\s*\(?(\d+)\)?/i);
    if (waitMatch) {
      items.push({
        type: 'wait',
        milliseconds: parseInt(waitMatch[1])
      });
      continue;
    }

    // Check for wait_until command: "wait_until Car.v <= 13.89"
    const waitUntilMatch = trimmed.match(/^wait_until\s+(.+?)(?:\s+(\d+))?$/i);
    if (waitUntilMatch) {
      items.push({
        type: 'wait_until',
        condition: waitUntilMatch[1].trim(),
        timeout: waitUntilMatch[2] ? parseInt(waitUntilMatch[2]) : 30000
      });
      continue;
    }

    // Parse vehicle command: "DM.Gas = 0.8 | 1000 | Abs"
    // Required: variable = value | duration
    // Optional: | mode (longer patterns first to avoid partial matching)
    const commandMatch = trimmed.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*\|\s*(\d+)(?:\s*\|\s*(AbsRamp|FacRamp|Abs|Off|Fac))?/i);

    if (commandMatch) {
      const variable = commandMatch[1];
      const value = parseFloat(commandMatch[2]);
      const duration = parseInt(commandMatch[3]);
      const mode = commandMatch[4] || 'Abs'; // Default mode

      items.push({
        variable,
        value,
        duration,
        mode
      });
      continue;
    }

    // Fallback: Try to parse old format without duration (default 2000ms)
    const legacyMatch = trimmed.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)/);
    if (legacyMatch) {
      console.warn(`Legacy format detected (missing duration): ${trimmed}`);
      items.push({
        variable: legacyMatch[1],
        value: parseFloat(legacyMatch[2]),
        duration: 2000, // Default duration
        mode: 'Abs'
      });
    }
  }

  return items;
}
