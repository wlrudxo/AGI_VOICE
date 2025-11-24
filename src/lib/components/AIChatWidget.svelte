<script>
	import { uiStore } from '$lib/stores/uiStore';
	import { triggerMonitor } from '$lib/stores/triggerMonitor.svelte';
	import { carmakerStore } from '$lib/stores/carmakerStore.svelte';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';
	import Icon from '@iconify/svelte';
	import ChatView from './ChatView.svelte';
	import ChatHistoryView from './ChatHistoryView.svelte';
	import ChatSettingsView from './ChatSettingsView.svelte';
	import { getCurrentWindow } from '@tauri-apps/api/window';

	const appWindow = getCurrentWindow();

	// View mode from store
	let viewMode = $derived($uiStore.chatViewMode);
	let currentTitle = $derived($uiStore.currentConversationTitle);
	let isWidgetMode = $derived($uiStore.isWidgetMode);
	let isExpanded = $derived($uiStore.isChatExpanded);

	// Trigger monitoring state
	let isTriggerMonitoring = $derived(triggerMonitor.isMonitoring);

	function closeWidget() {
		uiStore.setChatOpen(false);
	}

	function exitWidgetMode() {
		uiStore.setWidgetMode(false);
	}

	async function closeApp() {
		await appWindow.close();
	}

	function switchToHistory() {
		uiStore.setChatViewMode('history');
	}

	function switchToChat() {
		uiStore.setChatViewMode('chat');
	}

	function switchToSettings() {
		uiStore.setChatViewMode('settings');
	}

	function startNewChat() {
		// 새 대화 이벤트 발생
		window.dispatchEvent(
			new CustomEvent('selectConversation', {
				detail: { conversationId: null }
			})
		);
		uiStore.setChatViewMode('chat');
	}

	function handleSelectConversation(conversationId) {
		// 대화 선택 후 채팅 뷰로 전환
		switchToChat();
	}

	function toggleSize() {
		uiStore.setChatExpanded(!isExpanded);
	}

	async function toggleTriggerMonitoring() {
		// Check if vehicle command parsing is enabled
		const parsingEnabled = localStorage.getItem('carmaker_command_parsing_enabled') === 'true';
		if (!parsingEnabled) {
			await dialogStore.alert('먼저 자율주행 설정에서 "AI CarMaker Control"을 활성화해주세요.', '알림');
			return;
		}

		// Check CarMaker connection
		if (!carmakerStore.isConnected) {
			await dialogStore.alert('CarMaker에 먼저 연결해주세요.\n\n경로: 자율주행 > 설정', 'CarMaker 연결 필요');
			return;
		}

		// Check vehicle monitoring
		if (!carmakerStore.isMonitoring) {
			await dialogStore.alert('먼저 차량 모니터링을 시작해주세요.\n\n경로: 자율주행 > 차량 제어', '차량 모니터링 필요');
			return;
		}

		// Toggle monitoring
		if (isTriggerMonitoring) {
			triggerMonitor.stopMonitoring();
		} else {
			await triggerMonitor.startMonitoring();
		}
	}
</script>

<div class="chat-widget" class:fullscreen-widget={isWidgetMode} class:expanded={isExpanded}>
	<!-- 헤더 -->
	<div class="chat-header">
		<div class="header-title">
			{#if viewMode === 'chat'}
				<span class="title-text">{currentTitle || '새 채팅'}</span>
			{:else if viewMode === 'history'}
				<span class="title-text">대화기록</span>
			{:else if viewMode === 'settings'}
				<span class="title-text">채팅 설정</span>
			{/if}
		</div>
		<div class="header-actions">
			<!-- 자율주행 모니터링 토글 (채팅 뷰일 때만 표시) -->
			{#if viewMode === 'chat'}
				<button
					class="icon-btn trigger-toggle"
					class:active={isTriggerMonitoring}
					onclick={toggleTriggerMonitoring}
					title={isTriggerMonitoring ? '트리거 모니터링 중지' : '트리거 모니터링 시작'}
				>
					<Icon icon="solar:driving-bold-duotone" width="20" height="20" />
				</button>
			{/if}
			{#if isWidgetMode}
				{#if viewMode === 'chat'}
					<button class="icon-btn" onclick={switchToSettings} title="설정">
						<Icon icon="solar:settings-bold-duotone" width="20" height="20" />
					</button>
					<button class="icon-btn" onclick={switchToHistory} title="대화 기록">
						<Icon icon="solar:history-bold-duotone" width="20" height="20" />
					</button>
				{:else if viewMode === 'history'}
					<button class="icon-btn" onclick={startNewChat} title="새 대화">
						<Icon icon="solar:add-circle-bold-duotone" width="20" height="20" />
					</button>
					<button class="icon-btn" onclick={switchToChat} title="채팅으로 돌아가기">
						<Icon icon="solar:chat-round-bold-duotone" width="20" height="20" />
					</button>
				{:else if viewMode === 'settings'}
					<button class="icon-btn" onclick={switchToChat} title="채팅으로 돌아가기">
						<Icon icon="solar:chat-round-bold-duotone" width="20" height="20" />
					</button>
				{/if}
				<button class="icon-btn" onclick={exitWidgetMode} title="전체 화면으로">
					<Icon icon="solar:maximize-bold-duotone" width="20" height="20" />
				</button>
				<button class="icon-btn close" onclick={closeApp} title="앱 닫기">
					<Icon icon="solar:close-circle-bold" width="20" height="20" />
				</button>
			{:else}
				<button class="icon-btn" onclick={toggleSize} title={isExpanded ? '크기 축소' : '크기 확대'}>
					<Icon icon={isExpanded ? "solar:minimize-square-bold-duotone" : "solar:maximize-square-bold-duotone"} width="20" height="20" />
				</button>
				{#if viewMode === 'chat'}
					<button class="icon-btn" onclick={switchToSettings} title="설정">
						<Icon icon="solar:settings-bold-duotone" width="20" height="20" />
					</button>
					<button class="icon-btn" onclick={switchToHistory} title="대화 기록">
						<Icon icon="solar:history-bold-duotone" width="20" height="20" />
					</button>
				{:else if viewMode === 'history'}
					<button class="icon-btn" onclick={startNewChat} title="새 대화">
						<Icon icon="solar:add-circle-bold-duotone" width="20" height="20" />
					</button>
					<button class="icon-btn" onclick={switchToChat} title="채팅으로 돌아가기">
						<Icon icon="solar:chat-round-bold-duotone" width="20" height="20" />
					</button>
				{:else if viewMode === 'settings'}
					<button class="icon-btn" onclick={switchToChat} title="채팅으로 돌아가기">
						<Icon icon="solar:chat-round-bold-duotone" width="20" height="20" />
					</button>
				{/if}
				<button class="icon-btn" onclick={closeWidget} title="닫기">
					<Icon icon="solar:close-circle-bold" width="20" height="20" />
				</button>
			{/if}
		</div>
	</div>

	<!-- 뷰 컨텐츠 -->
	<div class="widget-content">
		<div class="view-container" class:hidden={viewMode !== 'chat'}>
			<ChatView />
		</div>
		<div class="view-container" class:hidden={viewMode !== 'history'}>
			<ChatHistoryView onSelectConversation={handleSelectConversation} />
		</div>
		<div class="view-container" class:hidden={viewMode !== 'settings'}>
			<ChatSettingsView />
		</div>
	</div>
</div>

<style>
	.chat-widget {
		display: flex;
		flex-direction: column;
		width: 450px;
		height: 700px;
		background: var(--color-surface);
		border-radius: 12px;
		box-shadow: var(--shadow-md);
		overflow: hidden;
		transition: width 0.3s ease, height 0.3s ease;
	}

	.chat-widget.expanded {
		width: 640px;
		height: 800px;
	}

	.chat-widget.fullscreen-widget {
		width: 100%;
		height: 100%;
		border-radius: 0;
		box-shadow: none;
	}

	.chat-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.5rem 0.75rem;
		background: linear-gradient(135deg, #5b9cf5 0%, #3b7dd8 100%);
		color: white;
	}

	.header-title {
		flex: 1;
		min-width: 0;
	}

	.title-text {
		font-size: 0.95rem;
		font-weight: 600;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		display: block;
	}

	.header-actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-shrink: 0;
	}

	.icon-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		background: transparent;
		border: none;
		color: white;
		cursor: pointer;
		padding: 0.25rem;
		border-radius: 6px;
		transition: all 0.2s;
	}

	.icon-btn:hover {
		background: var(--overlay-white-light);
	}

	.icon-btn.close:hover {
		background: var(--color-close-hover);
	}

	.icon-btn.trigger-toggle {
		border: 2px solid rgba(255, 255, 255, 0.5);
		background: rgba(255, 255, 255, 0.15);
		padding: 0.375rem;
	}

	.icon-btn.trigger-toggle.active {
		background: rgba(72, 187, 120, 0.5);
		border-color: rgba(255, 255, 255, 0.9);
		box-shadow: 0 0 8px rgba(72, 187, 120, 0.6);
	}

	.icon-btn.trigger-toggle:hover {
		background: rgba(255, 255, 255, 0.25);
		border-color: rgba(255, 255, 255, 0.7);
	}

	.icon-btn.trigger-toggle.active:hover {
		background: rgba(72, 187, 120, 0.6);
		border-color: rgba(255, 255, 255, 1);
	}

	.widget-content {
		flex: 1;
		overflow: hidden;
		position: relative;
	}

	.view-container {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column;
	}

	.view-container.hidden {
		display: none;
	}
</style>
