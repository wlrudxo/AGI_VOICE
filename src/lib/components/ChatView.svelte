<script lang="ts">
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import { dbWatcher } from '$lib/stores/dbWatcher.svelte';
	import { uiStore } from '$lib/stores/uiStore';
	import Icon from '@iconify/svelte';
	import { marked } from 'marked';
	import { parseActions, parseWithSegments, getActionLabel } from '$lib/actions/parser';
	import { executeActions } from '$lib/actions/executor';
	import { parseVehicleCommands } from '$lib/actions/vehicleCommandParser';
	import { executeCommandSequence } from '$lib/actions/vehicleCommandExecutor';

	// Configure marked for safe rendering
	marked.setOptions({
		breaks: true, // Convert \n to <br>
		gfm: true, // GitHub Flavored Markdown
	});

	// State
	let messages = $state([]);
	let inputMessage = $state('');
	let isLoading = $state(false);
	let messagesContainer;
	let conversationId = $state(null);
	let characterId = $state(null);
	let promptTemplateId = $state(null);
	let claudeModel = $state('sonnet');
	let settingsLoaded = $state(false);

	// 채팅 설정 로드
	async function loadChatSettings() {
		try {
			const settings = await invoke('get_chat_settings');
			characterId = settings.defaultCharacterId;
			promptTemplateId = settings.defaultPromptTemplateId;
			claudeModel = settings.defaultClaudeModel || 'sonnet';

			if (!characterId || !promptTemplateId) {
				console.error('Chat settings not configured');
				messages.push({
					role: 'error',
					content: '⚠️ 채팅 설정이 되어있지 않습니다. AI 설정 > 채팅 설정에서 캐릭터와 템플릿을 선택해주세요.',
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

	// 유저 정보 가져오기
	function getUserInfo() {
		try {
			return localStorage.getItem('agi_voice_user_info') || '';
		} catch (error) {
			console.error('Failed to get user info:', error);
			return '';
		}
	}

	// 유저 이름 가져오기
	function getUserName() {
		try {
			return localStorage.getItem('agi_voice_user_name') || '';
		} catch (error) {
			console.error('Failed to get user name:', error);
			return '';
		}
	}

	// 최종 메시지 가져오기
	function getFinalMessage() {
		try {
			return localStorage.getItem('agi_voice_final_message') || '';
		} catch (error) {
			console.error('Failed to get final message:', error);
			return '';
		}
	}

	// 대화 기록 선택 이벤트 리스너
	function handleSelectConversation(event) {
		const { conversationId: selectedId } = event.detail;

		// null이면 새 대화 시작 (초기화)
		if (selectedId === null) {
			conversationId = null;
			messages = [];
			loadChatSettings();
			// Store에도 저장
			uiStore.setCurrentConversationId(null);
			uiStore.setCurrentConversationTitle(null);
			return;
		}

		// 기존 대화 불러오기
		loadConversation(selectedId);
	}

	// 기존 대화 불러오기
	async function loadConversation(selectedId) {
		try {
			const convData = await invoke('get_conversation_by_id', { id: selectedId });
			const messagesData = await invoke('get_conversation_messages', { id: selectedId, limit: 50 });

			conversationId = selectedId;
			characterId = convData.characterId;
			promptTemplateId = convData.promptTemplateId;

			// Store에도 저장
			uiStore.setCurrentConversationId(selectedId);
			uiStore.setCurrentConversationTitle(convData.title);

			// 메시지 파싱 및 변환
			const parsedMessages = [];
			for (const msg of messagesData) {

				// UTC 시간을 명시적으로 파싱
				// 백엔드에서 'Z'가 없으면 추가하여 UTC로 파싱되도록 함
				let timestampStr = msg.created_at;
				if (timestampStr && !timestampStr.endsWith('Z') && !timestampStr.includes('+')) {
					timestampStr += 'Z';
				}
				const timestamp = timestampStr ? new Date(timestampStr) : new Date();

				if (msg.role === 'assistant') {
					// assistant 메시지는 태그 파싱 (parseWithSegments 사용)
					const segments = parseWithSegments(msg.content);

					for (const segment of segments) {
						if (segment.type === 'text') {
							parsedMessages.push({
								role: 'assistant',
								content: segment.content,
								timestamp
							});
						} else if (segment.type === 'action') {
							parsedMessages.push({
								role: 'action',
								label: segment.label,
								timestamp
							});
						}
					}
				} else {
					// user/error 등은 그대로
					parsedMessages.push({
						role: msg.role,
						content: msg.content,
						timestamp
					});
				}
			}

			messages = parsedMessages;

			scrollToBottom();
		} catch (error) {
			console.error('Failed to load conversation:', error);
			// 404 에러는 조용히 처리 (삭제된 대화)
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

	// 채팅 설정 업데이트 이벤트 핸들러
	function handleSettingsUpdated() {
		loadChatSettings();
	}

	onMount(() => {
		loadChatSettings();

		// Store에 저장된 conversationId가 있으면 해당 대화 로드
		const storedConversationId = $uiStore.currentConversationId;
		if (storedConversationId) {
			loadConversation(storedConversationId);
		}

		window.addEventListener('selectConversation', handleSelectConversation);
		window.addEventListener('chatSettingsUpdated', handleSettingsUpdated);
		return () => {
			window.removeEventListener('selectConversation', handleSelectConversation);
			window.removeEventListener('chatSettingsUpdated', handleSettingsUpdated);
		};
	});

	// Check if vehicle command parsing is enabled
	function isVehicleCommandParsingEnabled() {
		try {
			return localStorage.getItem('carmaker_command_parsing_enabled') === 'true';
		} catch (error) {
			return false;
		}
	}

	// 응답 처리 (재귀 가능)
	async function processResponse(rawResponse, userMessage, hasDbChange) {
		// 1. 응답 파싱
		const actions = parseActions(rawResponse);
		const segments = parseWithSegments(rawResponse);
		const timestamp = new Date();

		// 1.5. Check for vehicle commands if parsing is enabled
		let vehicleCommandsExecuted = false;
		if (isVehicleCommandParsingEnabled()) {
			try {
				const commandSequence = parseVehicleCommands(rawResponse);
				if (commandSequence.commands.length > 0) {
					console.log('🚗 Vehicle commands detected:', commandSequence);

					// Add vehicle command execution message
					messages.push({
						role: 'action',
						label: '🚗 차량 제어 명령 실행',
						timestamp
					});
					scrollToBottom();

					// Execute vehicle commands
					const result = await executeCommandSequence(commandSequence, (msg) => {
						console.log(msg);
					});

					// Add execution result message
					messages.push({
						role: 'assistant',
						content: `✓ 차량 제어 명령 실행 완료: ${result.successCount}/${result.totalCommands} (${result.executionTime}ms)`,
						timestamp: new Date()
					});
					scrollToBottom();
					vehicleCommandsExecuted = true;
				}
			} catch (error) {
				console.error('Vehicle command execution error:', error);
				messages.push({
					role: 'error',
					content: `차량 제어 명령 실행 실패: ${error.message || String(error)}`,
					timestamp: new Date()
				});
			}
		}

		// 2. 응답 표시
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

				if (
					segment.label?.includes('추가') ||
					segment.label?.includes('수정') ||
					segment.label?.includes('삭제')
				) {
					hasDbChange.value = true;
				}
			}
		}
		scrollToBottom();

		// 3. 모든 READ 액션 한 번에 실행
		const readActions = actions.filter(a => a.operation === 'read');
		if (readActions.length > 0) {
			console.log(`🔍 Executing ${readActions.length} READ actions:`, readActions);
			try {
				// 병렬 실행하여 모든 READ 결과 수집
				const readResults = await Promise.all(
					readActions.map(action => executeActions([action]))
				);

				// 결과를 system message로 포맷
				const systemContextParts: string[] = [];
				for (let i = 0; i < readResults.length; i++) {
					const resultArray = readResults[i];
					if (resultArray[0]?.success && resultArray[0]?.result) {
						systemContextParts.push(`[${readActions[i].type}] ${resultArray[0].result}`);
					} else if (!resultArray[0]?.success) {
						systemContextParts.push(`⚠️ 조회 실패: ${resultArray[0]?.error}`);
					}
				}

				if (systemContextParts.length > 0) {
					const systemContext = systemContextParts.join('\n\n---\n\n');

					// AI에게 모든 조회 결과를 한 번에 전달
					const followupRequestBody = {
						conversationId: conversationId,
						message: userMessage,
						model: claudeModel,
						userName: getUserName(),
						systemContext: systemContext,
						role: 'system' // DB 저장 안 함
					};

					const followupData = await invoke('chat', { request: followupRequestBody });
					const followupRawResponse = followupData.responses[0];

					// 최종 응답 표시
					const followupSegments = parseWithSegments(followupRawResponse);
					const followupTimestamp = new Date();
					for (const segment of followupSegments) {
						if (segment.type === 'text') {
							messages.push({
								role: 'assistant',
								content: segment.content,
								timestamp: followupTimestamp
							});
						} else if (segment.type === 'action') {
							messages.push({
								role: 'action',
								label: segment.label,
								timestamp: followupTimestamp
							});
						}
					}
					scrollToBottom();

					// 최종 응답에 CUD 태그가 있으면 실행
					const followupActions = parseActions(followupRawResponse);
					const cudActionsFromFollowup = followupActions.filter(a => a.operation !== 'read');
					if (cudActionsFromFollowup.length > 0) {
						console.log('🔧 Executing CUD actions from follow-up:', cudActionsFromFollowup);
						await executeActions(cudActionsFromFollowup);
						hasDbChange.value = true;
					}
				}
			} catch (readError) {
				console.error('❌ READ execution error:', readError);
				messages.push({
					role: 'error',
					content: `조회 실패: ${readError.message || String(readError)}`,
					timestamp: new Date()
				});
			}
		}

		// 4. CUD 액션 순차 실행 (READ 없는 경우)
		const cudActions = actions.filter(a => a.operation !== 'read');
		if (cudActions.length > 0) {
			console.log('🔧 Executing CUD actions:', cudActions);
			try {
				await executeActions(cudActions);
				hasDbChange.value = true;
			} catch (cudError) {
				console.error('❌ CUD execution error:', cudError);
				messages.push({
					role: 'error',
					content: `액션 실행 실패: ${cudError.message || String(cudError)}`,
					timestamp: new Date()
				});
			}
		}
	}

	// 메시지 전송
	async function sendMessage() {
		const userMessage = inputMessage.trim();
		if (!userMessage || isLoading) return;

		if (!settingsLoaded || !characterId || !promptTemplateId) {
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
				userName: getUserName(),
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
				requestBody.characterId = characterId;
				requestBody.promptTemplateId = promptTemplateId;
				requestBody.userInfo = getUserInfo();
				requestBody.finalMessage = getFinalMessage();
				requestBody.title = newConversationTitle;
			}

			// 1. chat invoke
			const data = await invoke('chat', { request: requestBody });
			const rawResponse = data.responses[0];
			const newConvId = data.conversationId;

			// conversation_id 업데이트
			if (!conversationId && newConvId) {
				conversationId = newConvId;
				uiStore.setCurrentConversationId(newConvId);
				if (newConversationTitle) {
					uiStore.setCurrentConversationTitle(newConversationTitle);
				}
				window.dispatchEvent(
					new CustomEvent('conversationCreated', {
						detail: { conversationId: newConvId }
					})
				);
			}

			// 2. 응답 처리 (재귀적으로)
			const hasDbChange = { value: false };
			await processResponse(rawResponse, userMessage, hasDbChange);

			// 3. DB 변경 알림
			if (hasDbChange.value) {
				console.log('✅ DB modification detected, triggering refresh...');
				dbWatcher.triggerRefresh(100);
			}
		} catch (error) {
			console.error('Chat error:', error);
			messages.push({
				role: 'error',
				content: '오류가 발생했습니다. 다시 시도해주세요.',
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

	function formatTime(date) {
		// Date 객체를 한국 시간으로 변환
		// date가 이미 UTC 기준으로 생성되어 있으므로, 브라우저 로컬 타임존으로 표시
		const hours = date.getHours().toString().padStart(2, '0');
		const minutes = date.getMinutes().toString().padStart(2, '0');
		return `${hours}:${minutes}`;
	}

	// 시간 표시 여부 결정 (연속된 같은 role의 마지막 메시지에만 표시)
	function shouldShowTime(index) {
		// 마지막 메시지면 항상 표시
		if (index === messages.length - 1) return true;

		// 현재 메시지와 다음 메시지의 role 비교
		const currentRole = messages[index].role;
		const nextRole = messages[index + 1]?.role;

		// role이 다르면 현재 메시지가 그룹의 마지막이므로 시간 표시
		return currentRole !== nextRole;
	}
</script>

<div class="chat-view">
	<!-- 메시지 영역 -->
	<div class="messages-container" bind:this={messagesContainer}>
		{#if messages.length === 0}
			<div class="empty-state">
			</div>
		{:else}
			{#each messages as message, index}
				{#if message.role === 'user'}
					<div class="message-wrapper message-wrapper-user">
						{#if shouldShowTime(index)}
							<span class="message-time message-time-user">{formatTime(message.timestamp)}</span>
						{/if}
						<div class="message message-user">
							<div class="message-content">
								<p>{message.content}</p>
							</div>
						</div>
					</div>
				{/if}

				{#if message.role === 'system'}
					<div class="message message-system">
						<div class="message-content">
							<div class="system-indicator">
								<Icon icon="solar:info-circle-bold-duotone" width="16" />
								<span>시스템</span>
							</div>
							<p>{message.content}</p>
						</div>
					</div>
				{/if}

				{#if message.role === 'action'}
					<div class="message message-action">
						<div class="message-content">
							<div class="action-indicator">
								📋 {message.label}
							</div>
						</div>
					</div>
				{/if}

				{#if message.role === 'assistant'}
					<div class="message-wrapper message-wrapper-assistant">
						<div class="message message-assistant">
							<div class="message-content">
								<div class="markdown-content">{@html marked(message.content)}</div>
							</div>
						</div>
						{#if shouldShowTime(index)}
							<span class="message-time message-time-assistant">{formatTime(message.timestamp)}</span>
						{/if}
					</div>
				{/if}

				{#if message.role === 'error'}
					<div class="message-wrapper message-wrapper-user">
						{#if shouldShowTime(index)}
							<span class="message-time message-time-user">{formatTime(message.timestamp)}</span>
						{/if}
						<div class="message message-error">
							<div class="message-content">
								<p>{message.content}</p>
							</div>
						</div>
					</div>
				{/if}
			{/each}

			{#if isLoading}
				<div class="message message-assistant">
					<div class="message-content">
						<div class="loading">
							<span class="dot"></span>
							<span class="dot"></span>
							<span class="dot"></span>
						</div>
					</div>
				</div>
			{/if}
		{/if}
	</div>

	<!-- 입력 영역 -->
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
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
		color: var(--color-text-muted);
	}


	.message-wrapper {
		display: flex;
		flex-direction: row;
		align-items: flex-end;
		gap: 0.25rem;
		max-width: 80%;
	}

	.message-wrapper-user {
		align-self: flex-end;
		flex-direction: row;
	}

	.message-wrapper-assistant {
		align-self: flex-start;
		flex-direction: row;
	}

	.message {
		display: flex;
	}

	.message-user {
		align-self: flex-end;
	}

	.message-user .message-content {
		background: var(--color-chat-user-bg);
		color: white;
		border-radius: 12px 12px 4px 12px;
	}

	.message-assistant {
		align-self: flex-start;
	}

	.message-assistant .message-content {
		background: var(--color-chat-assistant-bg);
		color: var(--color-chat-assistant-text);
		border-radius: 12px 12px 12px 4px;
	}

	.message-system {
		align-self: center;
		max-width: 90%;
	}

	.message-system .message-content {
		background: rgba(100, 116, 139, 0.1);
		color: var(--color-text-secondary);
		border-radius: 8px;
		border: 1px dashed rgba(100, 116, 139, 0.3);
		padding: 0.5rem 0.75rem;
		font-size: 0.85rem;
	}

	.system-indicator {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		font-weight: 600;
		font-size: 0.75rem;
		margin-bottom: 0.25rem;
		opacity: 0.8;
	}

	.message-action {
		align-self: flex-start;
		max-width: 70%;
	}

	.message-action .message-content {
		background: var(--color-chat-action-bg);
		color: var(--color-chat-action-text);
		border-radius: 12px;
		border-left: 3px solid var(--color-chat-action-border);
		padding: 0.5rem 0.75rem;
	}

	.message-error .message-content {
		background: rgba(245, 101, 101, 0.2);
		color: var(--color-error);
		border-radius: 12px;
	}

	.action-indicator {
		font-weight: 600;
		font-size: 0.85rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.message-content {
		padding: 0.75rem 1rem;
		word-wrap: break-word;
		font-size: 0.9rem;
	}

	.message-content p {
		margin: 0;
		line-height: 1.5;
		white-space: pre-wrap;
	}

	/* Markdown 스타일 */
	.markdown-content {
		line-height: 1.6;
		font-size: 0.9rem;
	}

	.markdown-content :global(p) {
		margin: 0 0 0.5rem 0;
	}

	.markdown-content :global(p:last-child) {
		margin-bottom: 0;
	}

	.markdown-content :global(strong) {
		font-weight: 700;
		color: inherit;
	}

	.markdown-content :global(em) {
		font-style: italic;
	}

	.markdown-content :global(code) {
		background: var(--overlay-light);
		padding: 0.15rem 0.4rem;
		border-radius: 4px;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.9em;
	}

	.markdown-content :global(pre) {
		background: var(--overlay-light);
		padding: 0.75rem;
		border-radius: 6px;
		overflow-x: auto;
		margin: 0.5rem 0;
	}

	.markdown-content :global(pre code) {
		background: none;
		padding: 0;
	}

	.markdown-content :global(ul),
	.markdown-content :global(ol) {
		margin: 0.5rem 0;
		padding-left: 1.5rem;
	}

	.markdown-content :global(li) {
		margin: 0.25rem 0;
	}

	.markdown-content :global(blockquote) {
		border-left: 3px solid var(--border-medium);
		padding-left: 0.75rem;
		margin: 0.5rem 0;
		font-style: italic;
		opacity: 0.9;
	}

	.markdown-content :global(h1),
	.markdown-content :global(h2),
	.markdown-content :global(h3),
	.markdown-content :global(h4),
	.markdown-content :global(h5),
	.markdown-content :global(h6) {
		margin: 0.75rem 0 0.5rem 0;
		font-weight: 700;
	}

	.markdown-content :global(h1) {
		font-size: 1.5em;
	}
	.markdown-content :global(h2) {
		font-size: 1.3em;
	}
	.markdown-content :global(h3) {
		font-size: 1.1em;
	}

	.markdown-content :global(a) {
		color: var(--color-chat-user-bg);
		text-decoration: underline;
	}

	.markdown-content :global(hr) {
		border: none;
		border-top: 1px solid var(--border-light);
		margin: 0.75rem 0;
	}

	.message-time {
		display: block;
		font-size: 0.7rem;
		color: var(--color-text-muted);
		white-space: nowrap;
		padding-bottom: 0.25rem;
	}

	.message-time-user {
		text-align: right;
	}

	.message-time-assistant {
		text-align: left;
	}

	.loading {
		display: flex;
		gap: 0.5rem;
	}

	.loading .dot {
		width: 8px;
		height: 8px;
		background: var(--color-text-muted);
		border-radius: 50%;
		animation: bounce 1.4s infinite ease-in-out both;
	}

	.loading .dot:nth-child(1) {
		animation-delay: -0.32s;
	}

	.loading .dot:nth-child(2) {
		animation-delay: -0.16s;
	}

	@keyframes bounce {
		0%,
		80%,
		100% {
			transform: scale(0);
		}
		40% {
			transform: scale(1);
		}
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
