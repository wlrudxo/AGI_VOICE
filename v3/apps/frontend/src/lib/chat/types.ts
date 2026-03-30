export interface ChatMessage {
	role: 'user' | 'assistant' | 'action' | 'error' | 'system';
	content?: string;
	label?: string;
	timestamp: Date;
}
