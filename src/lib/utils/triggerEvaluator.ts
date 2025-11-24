/**
 * Trigger Evaluator
 * Evaluates trigger conditions using expression-based evaluation
 */

import { evaluateExpression } from './expressionEvaluator';

interface Trigger {
  id: number;
  name: string;
  isActive: boolean;
  expression: string; // Single expression string (e.g., "Traffic.T01.sRoad - Traffic.T00.sRoad < 100")
  message: string;
  conversationId?: number;
  useRuleControl: boolean;
  debugAction: string;
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

  if (!trigger.expression || trigger.expression.trim() === '') {
    return false; // No expression to evaluate
  }

  // Evaluate expression using expression evaluator
  return evaluateExpression(trigger.expression, vehicleData);
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
