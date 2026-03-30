<script>
	import { onMount } from 'svelte';
	import { requestJson } from '$lib/backend';
	import { dbWatcher } from '$lib/stores/dbWatcher.svelte';
	import { uiStore } from '$lib/stores/uiStore';
	import { autonomousDrivingSettingsStore } from '$lib/stores/autonomousDrivingSettingsStore';
	import { chatBus } from '$lib/stores/chatBus';
	import { parseWithSegments } from '$lib/actions/parser';
	import { fetchChatSettings, fetchConversation } from '$lib/chat/chatConversation';
	import { processChatResponse } from '$lib/chat/chatResponseOrchestrator';
	import ChatMessageList from '$lib/components/ChatMessageList.svelte';

	// State
	let messages = $state([]);
	let inputMessage = $state('');
	let isLoading = $state(false);
	let messagesContainer;
	let conversationId = $state(null);
	let promptTemplateId = $state(null);
	let claudeModel = $state('sonnet');
	let settingsLoaded = $state(false);
	let lastSelectionVersion = 0;
	let lastSettingsVersion = 0;
	let lastTriggerEventVersion = 0;
	let collapsedVehicleData = $state({});

	function toggleVehicleData(index) {
		collapsedVehicleData[index] = collapsedVehicleData[index] === false ? true : false;
	}

	async function loadChatSettings() {
		try {
			const settings = await fetchChatSettings();
			promptTemplateId = settings.promptTemplateId;
			claudeModel = settings.claudeModel;

			if (!promptTemplateId) {
				console.error('Chat settings not configured');
				messages.push({
					role: 'error',
					content: '⚠️ 채팅 설정이 되어있지 않습니다. AI 설정 > 채팅 설정에서 시스템 메시지 템플릿을 선택해주세요.',
					timestamp: new Date()
				});
			}
			settingsLoaded = true;
		} catch (error) {
			console.error('Failed to load chat settings:', error);
			messages.push({
				role: 'error',
				content: '설정을 불러오는데 실패했습니다.',
				timestamp: new Date()
			});
			settingsLoaded = true;
		}
	}

	function handleSelectConversation(selectedId) {
		if (selectedId === null) {
			conversationId = null;
			messages = [];
			loadChatSettings();
			uiStore.setCurrentConversationId(null);
			uiStore.setCurrentConversationTitle(null);
			return;
		}

		loadConversation(selectedId);
	}

	async function loadConversation(selectedId) {
		try {
			const conversation = await fetchConversation(selectedId);
			conversationId = conversation.conversationId;
			promptTemplateId = conversation.promptTemplateId;
			messages = conversation.messages;
			uiStore.setCurrentConversationId(selectedId);
			uiStore.setCurrentConversationTitle(conversation.title);
			scrollToBottom();
		} catch (error) {
			console.error('Failed to load conversation:', error);
			if (error.toString().includes('not found')) {
				console.warn(`Conversation ${selectedId} not found, clearing stored ID`);
				uiStore.setCurrentConversationId(null);
				uiStore.setCurrentConversationTitle(null);
				return;
			}
			messages.push({
				role: 'error',
				content: '대화를 불러오는데 실패했습니다.',
				timestamp: new Date()
			});
		}
	}

	function handleSettingsUpdated() {
		loadChatSettings();
	}

	function handleTriggerChatMessage(detail) {
		const { type, triggerName, content } = detail;
		const timestamp = new Date();

		if (type === 'system') {
			messages.push({
				role: 'action',
				label: `🤖 LLM 입력 (${triggerName})`,
				timestamp
			});
			messages.push({
				role: 'user',
				content: `[Trigger: ${triggerName}]\n\n${content}`,
				timestamp
			});
			isLoading = true;
		} else if (type === 'llm_response') {
			isLoading = false;
			messages.push({
				role: 'action',
				label: `🤖 LLM 출력 (${triggerName})`,
				timestamp
			});
			const segments = parseWithSegments(content);
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
		} else if (type === 'error') {
			isLoading = false;
			messages.push({
				role: 'error',
				content: content,
				timestamp
			});
		}

		scrollToBottom();
	}

	onMount(() => {
		loadChatSettings();

		const storedConversationId = $uiStore.currentConversationId;
		if (storedConversationId) {
			loadConversation(storedConversationId);
		}

		const unsubscribeSelection = chatBus.conversationSelection.subscribe((state) => {
			if (state.version === 0 || state.version === lastSelectionVersion) {
				return;
			}
			lastSelectionVersion = state.version;
			handleSelectConversation(state.id);
		});
		const unsubscribeSettings = chatBus.chatSettingsVersion.subscribe((version) => {
			if (version === 0 || version === lastSettingsVersion) {
				return;
			}
			lastSettingsVersion = version;
			handleSettingsUpdated();
		});
		const unsubscribeTrigger = chatBus.triggerChatEvent.subscribe((state) => {
			if (!state.event || state.version === 0 || state.version === lastTriggerEventVersion) {
				return;
			}
			lastTriggerEventVersion = state.version;
			handleTriggerChatMessage(state.event);
		});
		return () => {
			unsubscribeSelection();
			unsubscribeSettings();
			unsubscribeTrigger();
		};
	});

	function isVehicleCommandParsingEnabled() {
		return autonomousDrivingSettingsStore.getCurrentState().vehicleCommandParsingEnabled;
	}

	async function sendMessage() {
		const userMessage = inputMessage.trim();
		if (!userMessage || isLoading) return;

		if (!settingsLoaded || !promptTemplateId) {
			messages.push({
				role: 'error',
				content: '채팅 설정을 먼저 완료해주세요.',
				timestamp: new Date()
			});
			return;
		}

		messages.push({
			role: 'user',
			content: userMessage,
			timestamp: new Date()
		});
		inputMessage = '';
		isLoading = true;
		scrollToBottom();

		try {
			const requestBody = {
				message: userMessage,
				model: claudeModel,
				role: 'user'
			};

			let newConversationTitle = null;

			if (conversationId) {
				requestBody.conversationId = conversationId;
			} else {
				const now = new Date();
				const year = now.getFullYear();
				const month = String(now.getMonth() + 1).padStart(2, '0');
				const day = String(now.getDate()).padStart(2, '0');
				const hours = String(now.getHours()).padStart(2, '0');
				const minutes = String(now.getMinutes()).padStart(2, '0');
				newConversationTitle = `${year}.${month}.${day}. ${hours}:${minutes}`;
				requestBody.promptTemplateId = promptTemplateId;
				requestBody.title = newConversationTitle;
			}

			const data = await requestJson('/api/chat', { method: 'POST', body: requestBody });
			const rawResponse = data.responses[0];
			const newConvId = data.conversationId;

			if (!conversationId && newConvId) {
				conversationId = newConvId;
				uiStore.setCurrentConversationId(newConvId);
				if (newConversationTitle) {
					uiStore.setCurrentConversationTitle(newConversationTitle);
				}
				chatBus.notifyConversationChanged();
			}

			const hasDbChange = { value: false };
			await processChatResponse({
				rawResponse,
				userMessage,
				conversationId,
				claudeModel,
				vehicleCommandParsingEnabled: isVehicleCommandParsingEnabled(),
				appendMessage: (message) => {
					messages.push(message);
				},
				scrollToBottom,
				hasDbChange
			});

			if (hasDbChange.value) {
				console.log('✅ DB modification detected, triggering refresh...');
				dbWatcher.triggerRefresh(100);
			}
		} catch (error) {
			console.error('Chat error:', error);
			messages.push({
				role: 'error',
				content: `오류가 발생했습니다. ${error instanceof Error ? error.message : String(error)}`,
				timestamp: new Date()
			});
		} finally {
			isLoading = false;
		}
	}

	function handleKeydown(event) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	function scrollToBottom() {
		setTimeout(() => {
			if (messagesContainer) {
				messagesContainer.scrollTop = messagesContainer.scrollHeight;
			}
		}, 100);
	}

</script>

<div class="chat-view">
	<div class="messages-container" bind:this={messagesContainer}>
		<ChatMessageList
			{messages}
			{isLoading}
			{collapsedVehicleData}
			onToggleVehicleData={toggleVehicleData}
		/>
	</div>

	<div class="input-container">
		<input
			type="text"
			bind:value={inputMessage}
			onkeydown={handleKeydown}
			placeholder="메시지를 입력하세요..."
			disabled={isLoading}
		/>
		<button class="btn-primary" onclick={sendMessage} disabled={!inputMessage.trim() || isLoading}>
			{#if isLoading}
				⏳
			{:else}
				전송
			{/if}
		</button>
	</div>
</div>

<style>
	.chat-view {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.messages-container {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
	}

	.input-container {
		display: flex;
		gap: 0.5rem;
		padding: 1rem;
		border-top: 1px solid var(--color-border);
		background: var(--color-surface);
	}

	.input-container input {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid var(--color-border-dark);
		border-radius: 8px;
		font-size: 0.9rem;
		outline: none;
		transition: border-color 0.2s;
		background: var(--color-surface);
		color: var(--color-text-primary);
	}

	.input-container input:focus {
		border-color: var(--color-chat-user-bg);
	}

	.input-container input:disabled {
		background: var(--color-background);
		cursor: not-allowed;
		opacity: 0.5;
	}


	.messages-container::-webkit-scrollbar {
		width: 6px;
	}

	.messages-container::-webkit-scrollbar-track {
		background: var(--color-surface);
	}

	.messages-container::-webkit-scrollbar-thumb {
		background: var(--color-border-dark);
		border-radius: 3px;
	}

	.messages-container::-webkit-scrollbar-thumb:hover {
		background: var(--color-text-muted);
	}
</style>
