export interface Trigger {
  id: number;
  name: string;
  isActive: boolean;
  expression: string;
  message: string;
  conversationId?: number | null;
  useRuleControl: boolean;
  debugAction: string;
  cooldown: number;
  createdAt: string;
  updatedAt: string;
}
