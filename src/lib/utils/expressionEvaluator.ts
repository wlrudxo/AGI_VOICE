/**
 * Expression Evaluator
 * Safely evaluates mathematical and logical expressions with vehicle data
 */

/**
 * Supported operators and functions
 */
const OPERATORS = {
  // Arithmetic
  '+': (a: number, b: number) => a + b,
  '-': (a: number, b: number) => a - b,
  '*': (a: number, b: number) => a * b,
  '/': (a: number, b: number) => a / b,
  '%': (a: number, b: number) => a % b,

  // Comparison
  '>': (a: number, b: number) => a > b,
  '<': (a: number, b: number) => a < b,
  '>=': (a: number, b: number) => a >= b,
  '<=': (a: number, b: number) => a <= b,
  '==': (a: number, b: number) => Math.abs(a - b) < 0.0001,
  '!=': (a: number, b: number) => Math.abs(a - b) >= 0.0001,

  // Logical
  '&&': (a: boolean, b: boolean) => a && b,
  '||': (a: boolean, b: boolean) => a || b,
};

const FUNCTIONS = {
  'abs': (x: number) => Math.abs(x),
  'sqrt': (x: number) => Math.sqrt(x),
  'pow': (x: number, y: number) => Math.pow(x, y),
  'min': (...args: number[]) => Math.min(...args),
  'max': (...args: number[]) => Math.max(...args),
};

/**
 * Tokenize expression into tokens
 */
function tokenize(expression: string): string[] {
  // Remove whitespace and split by operators/parentheses while keeping them
  const tokens: string[] = [];
  let current = '';

  for (let i = 0; i < expression.length; i++) {
    const char = expression[i];

    // Skip whitespace
    if (char === ' ') {
      if (current) {
        tokens.push(current);
        current = '';
      }
      continue;
    }

    // Handle operators (check for two-char operators first)
    if (i < expression.length - 1) {
      const twoChar = char + expression[i + 1];
      if (['>=', '<=', '==', '!=', '&&', '||'].includes(twoChar)) {
        if (current) {
          tokens.push(current);
          current = '';
        }
        tokens.push(twoChar);
        i++; // Skip next character
        continue;
      }
    }

    // Handle single-char operators and parentheses
    if (['+', '-', '*', '/', '%', '>', '<', '(', ')', ','].includes(char)) {
      if (current) {
        tokens.push(current);
        current = '';
      }
      tokens.push(char);
    } else {
      current += char;
    }
  }

  if (current) {
    tokens.push(current);
  }

  return tokens;
}

/**
 * Replace variables in expression with their values
 */
function replaceVariables(
  expression: string,
  vehicleData: Record<string, number>
): string {
  let result = expression;

  // Sort keys by length (descending) to handle nested variable names correctly
  // e.g., "Traffic.T01" should be matched before "Traffic"
  const sortedKeys = Object.keys(vehicleData).sort((a, b) => b.length - a.length);

  for (const key of sortedKeys) {
    // Create regex that matches the variable name as a whole word
    // Escape dots in variable names (e.g., "Traffic.T01.sRoad")
    const escapedKey = key.replace(/\./g, '\\.');
    const regex = new RegExp(`\\b${escapedKey}\\b`, 'g');
    const value = vehicleData[key];

    if (value !== undefined && value !== null) {
      result = result.replace(regex, value.toString());
    }
  }

  return result;
}

/**
 * Safely evaluate a mathematical/logical expression
 * @param expression - Expression string (e.g., "Traffic.T01.sRoad - Traffic.T00.sRoad < 100")
 * @param vehicleData - Vehicle telemetry data
 * @returns Evaluation result (boolean or number)
 */
export function evaluateExpression(
  expression: string,
  vehicleData: Record<string, number>
): boolean {
  try {
    // Step 1: Replace variables with their values
    const processedExpression = replaceVariables(expression, vehicleData);

    // Step 2: Evaluate using Function constructor (safer than eval)
    // Wrap in try-catch to handle any evaluation errors
    const result = new Function(`
      "use strict";
      const abs = Math.abs;
      const sqrt = Math.sqrt;
      const pow = Math.pow;
      const min = Math.min;
      const max = Math.max;
      return (${processedExpression});
    `)();

    // Step 3: Convert result to boolean if needed
    if (typeof result === 'boolean') {
      return result;
    } else if (typeof result === 'number') {
      // Truthy check for numbers (0 = false, non-zero = true)
      return result !== 0;
    } else {
      console.error('Expression evaluation returned non-boolean/number:', result);
      return false;
    }
  } catch (error: any) {
    console.error('[Expression] Evaluation failed:', error.message);
    console.error('  Expression:', expression);
    console.error('  Processed:', replaceVariables(expression, vehicleData));
    return false;
  }
}

/**
 * Validate expression syntax (basic check)
 */
export function validateExpression(expression: string): { valid: boolean; error?: string } {
  try {
    // Check for balanced parentheses
    let depth = 0;
    for (const char of expression) {
      if (char === '(') depth++;
      if (char === ')') depth--;
      if (depth < 0) {
        return { valid: false, error: 'Unbalanced parentheses' };
      }
    }
    if (depth !== 0) {
      return { valid: false, error: 'Unbalanced parentheses' };
    }

    // Check for empty expression
    if (!expression.trim()) {
      return { valid: false, error: 'Empty expression' };
    }

    // More validation could be added here

    return { valid: true };
  } catch (error: any) {
    return { valid: false, error: error.message };
  }
}

/**
 * Get all variable names used in an expression
 */
export function extractVariables(expression: string): string[] {
  const tokens = tokenize(expression);
  const variables: Set<string> = new Set();

  for (const token of tokens) {
    // Check if token is a variable (contains dots or starts with letter)
    if (/^[A-Za-z][A-Za-z0-9._]*$/.test(token) && !Object.keys(FUNCTIONS).includes(token)) {
      variables.add(token);
    }
  }

  return Array.from(variables);
}
