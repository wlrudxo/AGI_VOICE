/**
 * Vehicle Command Parser
 * Parses LLM responses and extracts vehicle control commands
 */

export interface VehicleCommand {
  variable: string;
  value: number;
  duration?: number;
  mode?: string;
}

export interface CommandSequence {
  type: 'simple' | 'sequential' | 'script';
  commands: VehicleCommand[];
  script?: string;
  delay?: number;
}

/**
 * Parse LLM response and extract vehicle commands
 */
export function parseVehicleCommands(llmResponse: string): CommandSequence {
  // Try to extract code block first
  const codeBlockMatch = llmResponse.match(/```(?:[\w]*)\n([\s\S]*?)\n```/);
  const commandText = codeBlockMatch ? codeBlockMatch[1] : llmResponse;

  // Check if it's a Rust script
  if (commandText.includes('fn ') || commandText.includes('let ')) {
    return {
      type: 'script',
      commands: [],
      script: commandText
    };
  }

  // Parse simple/sequential commands
  const commands = parseSimpleCommands(commandText);

  // Detect sequential mode (has delay keywords or numbered steps)
  const isSequential = /step|wait|delay|then|\d+\./i.test(llmResponse);

  return {
    type: isSequential ? 'sequential' : 'simple',
    commands
  };
}

/**
 * Parse simple command format: "DM.Gas = 0.5"
 */
function parseSimpleCommands(text: string): VehicleCommand[] {
  const commands: VehicleCommand[] = [];
  const lines = text.split('\n').filter(line => line.trim());

  for (const line of lines) {
    // Match: "DM.Gas = 0.5" or "DM.Gas = 0.5 (2000ms)" or "DM.Gas = 0.5 | 2000 | Abs"
    const basicMatch = line.match(/^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)/);
    if (basicMatch) {
      const variable = basicMatch[1];
      const value = parseFloat(basicMatch[2]);

      // Extract optional duration and mode
      const durationMatch = line.match(/(\d+)\s*ms/i);
      const modeMatch = line.match(/\|\s*(Abs|Off|Fac|AbsRamp|FacRamp)/i);

      commands.push({
        variable,
        value,
        duration: durationMatch ? parseInt(durationMatch[1]) : 2000,
        mode: modeMatch ? modeMatch[1] : 'Abs'
      });
    }
  }

  return commands;
}

/**
 * Extract delay information from sequential commands
 */
export function extractDelays(llmResponse: string): number[] {
  const delays: number[] = [];
  const delayMatches = llmResponse.matchAll(/wait\s+(\d+(?:\.\d+)?)\s*(s|ms|sec|second)/gi);

  for (const match of delayMatches) {
    const value = parseFloat(match[1]);
    const unit = match[2].toLowerCase();

    // Convert to milliseconds
    if (unit === 's' || unit === 'sec' || unit === 'second') {
      delays.push(value * 1000);
    } else {
      delays.push(value);
    }
  }

  return delays;
}
