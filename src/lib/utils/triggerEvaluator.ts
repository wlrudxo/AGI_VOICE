/**
 * Trigger Evaluator
 * Evaluates trigger conditions against vehicle telemetry data
 */

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
}

/**
 * Evaluate a single condition against vehicle data
 */
function evaluateCondition(
  condition: TriggerCondition,
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
 * Evaluate trigger against vehicle data
 * @returns true if trigger conditions are met
 */
export function evaluateTrigger(
  trigger: Trigger,
  vehicleData: Record<string, number>
): boolean {
  if (!trigger.isActive) {
    return false; // Skip inactive triggers
  }

  if (trigger.conditions.length === 0) {
    return false; // No conditions to evaluate
  }

  // Evaluate all conditions
  const results = trigger.conditions.map(condition =>
    evaluateCondition(condition, vehicleData)
  );

  // Apply logic operator
  if (trigger.logicOperator === 'AND') {
    return results.every(result => result === true);
  } else if (trigger.logicOperator === 'OR') {
    return results.some(result => result === true);
  }

  return false;
}

/**
 * Find all triggered items from a list of triggers
 */
export function findTriggeredItems(
  triggers: Trigger[],
  vehicleData: Record<string, number>
): Trigger[] {
  return triggers.filter(trigger => evaluateTrigger(trigger, vehicleData));
}
