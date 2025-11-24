/**
 * Vehicle Command Parser Tests
 * Test the unified parsing format
 */

import { parseVehicleCommands } from './vehicleCommandParser';
import type { VehicleCommand, WaitCommand, WaitUntilCommand } from './vehicleCommandParser';

// Test cases
const testCases = [
  {
    name: 'Simple command with duration and mode',
    input: `\`\`\`
DM.Gas = 0.8 | 1000 | Abs
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { variable: 'DM.Gas', value: 0.8, duration: 1000, mode: 'Abs' }
      ]
    }
  },
  {
    name: 'Command without mode (defaults to Abs)',
    input: `\`\`\`
DM.Brake = 0.5 | 2000
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { variable: 'DM.Brake', value: 0.5, duration: 2000, mode: 'Abs' }
      ]
    }
  },
  {
    name: 'Multiple commands with wait',
    input: `\`\`\`
DM.Gas = 0.8 | 1000 | Abs
wait 500
DM.Brake = 0.2 | 2000
wait 1000
DM.Gas = 0.0 | 500
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { variable: 'DM.Gas', value: 0.8, duration: 1000, mode: 'Abs' },
        { type: 'wait', milliseconds: 500 },
        { variable: 'DM.Brake', value: 0.2, duration: 2000, mode: 'Abs' },
        { type: 'wait', milliseconds: 1000 },
        { variable: 'DM.Gas', value: 0.0, duration: 500, mode: 'Abs' }
      ]
    }
  },
  {
    name: 'Commands with wait_until (default timeout)',
    input: `\`\`\`
DM.Gas = 0.8 | 1000
wait_until Car.v >= 27.78
DM.Gas = 0.0 | 500
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { variable: 'DM.Gas', value: 0.8, duration: 1000, mode: 'Abs' },
        { type: 'wait_until', condition: 'Car.v >= 27.78', timeout: 30000 },
        { variable: 'DM.Gas', value: 0.0, duration: 500, mode: 'Abs' }
      ]
    }
  },
  {
    name: 'wait_until with custom timeout',
    input: `\`\`\`
wait_until DM.Brake < 0.1 5000
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { type: 'wait_until', condition: 'DM.Brake < 0.1', timeout: 5000 }
      ]
    }
  },
  {
    name: 'wait_until with different operators',
    input: `\`\`\`
wait_until Car.v >= 27.78
wait_until DM.Brake <= 0.5
wait_until Vhcl.tRoad == 0.0
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { type: 'wait_until', condition: 'Car.v >= 27.78', timeout: 30000 },
        { type: 'wait_until', condition: 'DM.Brake <= 0.5', timeout: 30000 },
        { type: 'wait_until', condition: 'Vhcl.tRoad == 0.0', timeout: 30000 }
      ]
    }
  },
  {
    name: 'Commands with comments',
    input: `\`\`\`
# Emergency deceleration
DM.Gas = 0.0 | 500 | Abs
// Apply brake
DM.Brake = 1.0 | 3000 | Abs
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { variable: 'DM.Gas', value: 0.0, duration: 500, mode: 'Abs' },
        { variable: 'DM.Brake', value: 1.0, duration: 3000, mode: 'Abs' }
      ]
    }
  },
  {
    name: 'Legacy format (fallback)',
    input: `\`\`\`
DM.Gas = 0.5
DM.Brake = 0.2
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { variable: 'DM.Gas', value: 0.5, duration: 2000, mode: 'Abs' },
        { variable: 'DM.Brake', value: 0.2, duration: 2000, mode: 'Abs' }
      ]
    }
  },
  {
    name: 'Different control modes',
    input: `\`\`\`
DM.Gas = 0.5 | 1000 | Fac
DM.Brake = 0.3 | 2000 | AbsRamp
DM.Steer.Ang = 0.1 | 1500 | Off
\`\`\``,
    expected: {
      type: 'sequential',
      items: [
        { variable: 'DM.Gas', value: 0.5, duration: 1000, mode: 'Fac' },
        { variable: 'DM.Brake', value: 0.3, duration: 2000, mode: 'AbsRamp' },
        { variable: 'DM.Steer.Ang', value: 0.1, duration: 1500, mode: 'Off' }
      ]
    }
  }
];

// Run tests
console.log('=== Vehicle Command Parser Tests ===\n');

let passCount = 0;
let failCount = 0;

for (const testCase of testCases) {
  console.log(`Test: ${testCase.name}`);

  try {
    const result = parseVehicleCommands(testCase.input);

    // Compare result with expected
    const resultStr = JSON.stringify(result, null, 2);
    const expectedStr = JSON.stringify(testCase.expected, null, 2);

    if (resultStr === expectedStr) {
      console.log('  ✅ PASS\n');
      passCount++;
    } else {
      console.log('  ❌ FAIL');
      console.log('  Expected:', expectedStr);
      console.log('  Got:', resultStr);
      console.log();
      failCount++;
    }
  } catch (error: any) {
    console.log('  ❌ ERROR:', error.message);
    console.log();
    failCount++;
  }
}

console.log(`\n=== Results: ${passCount} passed, ${failCount} failed ===`);

// Export for use in browser console
if (typeof window !== 'undefined') {
  (window as any).testVehicleCommandParser = () => {
    console.log('Run tests from Node.js or use the test cases directly');
  };
}
