import { requestJson } from '$lib/backend';
import { parseActions, parseWithSegments } from '$lib/actions/parser';
import { executeActions } from '$lib/actions/executor';
import { parseVehicleCommands } from '$lib/actions/vehicleCommandParser';
import { executeCommandSequence } from '$lib/actions/vehicleCommandExecutor';
import type { ChatMessage } from '$lib/chat/types';

interface ProcessChatResponseOptions {
	rawResponse: string;
	userMessage: string;
	conversationId: number | null;
	claudeModel: string;
	vehicleCommandParsingEnabled: boolean;
	appendMessage: (message: ChatMessage) => void;
	scrollToBottom: () => void;
	hasDbChange: { value: boolean };
}

function appendSegments(rawResponse: string, timestamp: Date, appendMessage: (message: ChatMessage) => void) {
	const segments = parseWithSegments(rawResponse);
	for (const segment of segments) {
		if (segment.type === 'text') {
			appendMessage({
				role: 'assistant',
				content: segment.content,
				timestamp
			});
			continue;
		}

		appendMessage({
			role: 'action',
			label: segment.label,
			timestamp
		});
	}
}

export async function processChatResponse({
	rawResponse,
	userMessage,
	conversationId,
	claudeModel,
	vehicleCommandParsingEnabled,
	appendMessage,
	scrollToBottom,
	hasDbChange
}: ProcessChatResponseOptions): Promise<void> {
	const actions = parseActions(rawResponse);
	const timestamp = new Date();

	let commandSequence = null;
	if (vehicleCommandParsingEnabled) {
		try {
			commandSequence = parseVehicleCommands(rawResponse);
			if (commandSequence.items.length === 0) {
				commandSequence = null;
			}
		} catch (error) {
			console.error('Vehicle command parsing error:', error);
		}
	}

	appendSegments(rawResponse, timestamp, appendMessage);
	scrollToBottom();

	const readActions = actions.filter((action) => action.operation === 'read');
	if (readActions.length > 0) {
		try {
			const readResults = await Promise.all(readActions.map((action) => executeActions([action])));
			const systemContextParts: string[] = [];

			for (let index = 0; index < readResults.length; index += 1) {
				const resultArray = readResults[index];
				if (resultArray[0]?.success && resultArray[0]?.result) {
					systemContextParts.push(`[${readActions[index].type}] ${resultArray[0].result}`);
				} else if (!resultArray[0]?.success) {
					systemContextParts.push(`⚠️ 조회 실패: ${resultArray[0]?.error}`);
				}
			}

			if (systemContextParts.length > 0) {
				const systemContext = systemContextParts.join('\n\n---\n\n');
				const followupData = await requestJson('/api/chat', {
					method: 'POST',
					body: {
						conversationId,
						message: userMessage,
						model: claudeModel,
						systemContext,
						role: 'system'
					}
				});
				const followupRawResponse = followupData.responses[0];
				appendSegments(followupRawResponse, new Date(), appendMessage);
				scrollToBottom();

				const followupActions = parseActions(followupRawResponse);
				const cudActionsFromFollowup = followupActions.filter((action) => action.operation !== 'read');
				if (cudActionsFromFollowup.length > 0) {
					await executeActions(cudActionsFromFollowup);
					hasDbChange.value = true;
				}
			}
		} catch (readError: any) {
			appendMessage({
				role: 'error',
				content: `조회 실패: ${readError.message || String(readError)}`,
				timestamp: new Date()
			});
		}
	}

	const cudActions = actions.filter((action) => action.operation !== 'read');
	if (cudActions.length > 0) {
		try {
			await executeActions(cudActions);
			hasDbChange.value = true;
		} catch (cudError: any) {
			appendMessage({
				role: 'error',
				content: `액션 실행 실패: ${cudError.message || String(cudError)}`,
				timestamp: new Date()
			});
		}
	}

	if (commandSequence) {
		appendMessage({
			role: 'action',
			label: '🚗 차량 제어 명령 실행',
			timestamp: new Date()
		});
		scrollToBottom();

		try {
			await executeCommandSequence(commandSequence, (message) => {
				console.log(message);
			});
		} catch (error: any) {
			appendMessage({
				role: 'error',
				content: `차량 제어 명령 실행 실패: ${error.message || String(error)}`,
				timestamp: new Date()
			});
		}
	}
}
