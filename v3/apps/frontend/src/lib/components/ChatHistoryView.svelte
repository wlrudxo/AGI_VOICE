<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';
	import { requestJson } from '$lib/backend';

	// Props
	let { onSelectConversation = (id) => {} } = $props();

	// State
	let conversations = $state([]);
	let isLoading = $state(false);
	let editingId = $state(null);
	let editingTitle = $state('');

	// 대화 목록 로드
	async function loadConversations() {
		try {
			isLoading = true;
			conversations = await requestJson('/api/conversations');
		} catch (error) {
			console.error('❌ Failed to load conversations:', error);
		} finally {
			isLoading = false;
		}
	}

	// 새 대화 생성 이벤트 리스너
	function handleConversationCreated(event) {
		loadConversations();
	}

	onMount(() => {
		loadConversations();
		window.addEventListener('conversationCreated', handleConversationCreated);
		return () => {
			window.removeEventListener('conversationCreated', handleConversationCreated);
		};
	});

	// 대화 선택
	function selectConversation(conversationId) {
		window.dispatchEvent(
			new CustomEvent('selectConversation', {
				detail: { conversationId }
			})
		);
		onSelectConversation(conversationId);
	}

	// 이름 변경 시작
	function startEdit(conversation) {
		editingId = conversation.id;
		editingTitle = conversation.title;
	}

	// 이름 변경 취소
	function cancelEdit() {
		editingId = null;
		editingTitle = '';
	}

	// 이름 변경 저장
	async function saveEdit(conversationId) {
		try {
			await requestJson(`/api/conversations/${conversationId}`, {
				method: 'PUT',
				body: { title: editingTitle }
			});

			await loadConversations();
			cancelEdit();
		} catch (error) {
			console.error('Failed to update conversation title:', error);
		}
	}

	// 대화 삭제
	async function deleteConversation(conversationId) {
		const confirmed = await dialogStore.confirm('이 대화를 삭제하시겠습니까?');
		if (!confirmed) {
			return;
		}

		try {
			await requestJson(`/api/conversations/${conversationId}`, { method: 'DELETE' });
			await loadConversations();
		} catch (error) {
			console.error('Failed to delete conversation:', error);
		}
	}

	// 날짜 포맷
	function formatDate(dateStr) {
		const dbDate = new Date(dateStr);
		const now = new Date();
		const diff = now - dbDate;
		const minutes = Math.floor(diff / 60000);
		const hours = Math.floor(diff / 3600000);
		const days = Math.floor(diff / 86400000);

		if (minutes < 1) {
			return '방금 전';
		} else if (minutes < 60) {
			return `${minutes}분 전`;
		} else if (hours < 24) {
			return `${hours}시간 전`;
		} else if (days < 7) {
			return `${days}일 전`;
		} else {
			return dbDate.toLocaleDateString('ko-KR', {
				timeZone: 'Asia/Seoul'
			});
		}
	}
</script>

<div class="history-view">
	<!-- 목록 영역 -->
	<div class="history-container">
		{#if isLoading}
			<div class="loading-state">
				<p>로딩 중...</p>
			</div>
		{:else if conversations.length === 0}
			<div class="empty-state">
				<Icon icon="solar:chat-line-bold-duotone" width="64" height="64" />
				<p>저장된 대화가 없습니다</p>
				<p class="hint">AI 채팅을 시작해보세요!</p>
			</div>
		{:else}
			<div class="conversation-list">
				{#each conversations as conversation}
					<div class="conversation-item">
						{#if editingId === conversation.id}
							<!-- 편집 모드 -->
							<div class="edit-mode">
								<input
									type="text"
									bind:value={editingTitle}
									class="edit-input"
									onkeydown={(e) => {
										if (e.key === 'Enter') saveEdit(conversation.id);
										if (e.key === 'Escape') cancelEdit();
									}}
								/>
								<div class="edit-actions">
									<button class="btn-icon" onclick={() => saveEdit(conversation.id)}>
										<Icon icon="solar:check-circle-bold" width="20" height="20" />
									</button>
									<button class="btn-icon danger" onclick={cancelEdit}>
										<Icon icon="solar:close-circle-bold" width="20" height="20" />
									</button>
								</div>
							</div>
						{:else}
							<!-- 일반 모드 -->
							<button
								class="conversation-content"
								onclick={() => selectConversation(conversation.id)}
							>
								<div class="conversation-title">{conversation.title || '제목 없음'}</div>
								<div class="conversation-meta">
									<span class="conversation-date">{formatDate(conversation.createdAt)}</span>
									<span class="conversation-separator">•</span>
									<span class="conversation-messages">메시지 {conversation.messageCount || 0}개</span>
								</div>
							</button>
							<div class="conversation-actions">
								<button class="btn-icon" onclick={() => startEdit(conversation)}>
									<Icon icon="solar:pen-bold-duotone" width="18" height="18" />
								</button>
								<button
									class="btn-icon danger"
									onclick={() => deleteConversation(conversation.id)}
								>
									<Icon icon="solar:trash-bin-trash-bold-duotone" width="18" height="18" />
								</button>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.history-view {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.history-container {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
	}

	.loading-state,
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
		color: var(--color-text-muted);
	}

	.empty-state :global(svg) {
		color: var(--color-border);
		margin-bottom: 1rem;
	}

	.empty-state .hint {
		margin-top: 0.5rem;
		font-size: 0.9rem;
		color: var(--color-text-muted);
	}

	.conversation-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.conversation-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		transition: all 0.2s;
	}

	.conversation-item:hover {
		background: var(--color-surface-hover);
		border-color: var(--color-primary);
	}

	.conversation-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 0.25rem;
		background: transparent;
		border: none;
		padding: 0;
		cursor: pointer;
		text-align: left;
	}

	.conversation-title {
		font-weight: 600;
		color: var(--color-text-primary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		max-width: 250px;
	}

	.conversation-meta {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.conversation-actions {
		display: flex;
		gap: 0.25rem;
	}

	/* 편집 모드 */
	.edit-mode {
		flex: 1;
		display: flex;
		gap: 0.5rem;
	}

	.edit-input {
		flex: 1;
		padding: 0.5rem;
		border: 2px solid var(--color-primary);
		border-radius: 6px;
		font-size: 0.875rem;
		outline: none;
		background: var(--color-surface);
		color: var(--color-text-primary);
	}

	.edit-actions {
		display: flex;
		gap: 0.25rem;
	}

	.history-container::-webkit-scrollbar {
		width: 6px;
	}

	.history-container::-webkit-scrollbar-track {
		background: var(--color-surface);
	}

	.history-container::-webkit-scrollbar-thumb {
		background: var(--color-border-dark);
		border-radius: 3px;
	}

	.history-container::-webkit-scrollbar-thumb:hover {
		background: var(--color-text-muted);
	}
</style>
