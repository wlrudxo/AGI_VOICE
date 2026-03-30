import { requestJson } from '$lib/backend';
import { parseWithSegments } from '$lib/actions/parser';

export async function fetchChatSettings() {
	const settings = await requestJson('/api/settings/chat');
	return {
		promptTemplateId: settings.defaultPromptTemplateId,
		claudeModel: settings.defaultClaudeModel || 'sonnet'
	};
}

export async function fetchConversation(selectedId) {
	const convData = await requestJson(`/api/conversations/${selectedId}`);
	const messagesData = await requestJson(`/api/conversations/${selectedId}/messages?limit=50`);

	const messages = [];
	for (const msg of messagesData) {
		let timestampStr = msg.created_at;
		if (timestampStr && !timestampStr.endsWith('Z') && !timestampStr.includes('+')) {
			timestampStr += 'Z';
		}
		const timestamp = timestampStr ? new Date(timestampStr) : new Date();

		if (msg.role === 'assistant') {
			const segments = parseWithSegments(msg.content);
			for (const segment of segments) {
				if (segment.type === 'text') {
					messages.push({
						role: 'assistant',
						content: segment.content,
						timestamp
					});
				} else if (segment.type === 'action') {
					messages.push({
						role: 'action',
						label: segment.label,
						timestamp
					});
				}
			}
			continue;
		}

		messages.push({
			role: msg.role,
			content: msg.content,
			timestamp
		});
	}

	return {
		conversationId: selectedId,
		promptTemplateId: convData.promptTemplateId,
		title: convData.title,
		messages
	};
}
