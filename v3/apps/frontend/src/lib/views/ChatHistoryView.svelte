<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { createChatApi } from '../chatApi.js';

  let { onSelectConversation = () => {} } = $props();

  const chatApi = createChatApi();

  let conversations = $state([]);
  let isLoading = $state(false);

  async function loadConversations() {
    try {
      isLoading = true;
      conversations = await chatApi.getConversations();
    } catch {
      conversations = [];
    } finally {
      isLoading = false;
    }
  }

  function handleConversationCreated() {
    loadConversations();
  }

  function selectConversation(conversationId) {
    window.dispatchEvent(
      new CustomEvent('selectConversation', {
        detail: { conversationId },
      })
    );
    onSelectConversation(conversationId);
  }

  function formatDate(dateStr) {
    const dbDate = new Date(dateStr);
    const now = new Date();
    const diff = now - dbDate;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) {
      return '방금 전';
    }
    if (minutes < 60) {
      return `${minutes}분 전`;
    }
    if (hours < 24) {
      return `${hours}시간 전`;
    }
    if (days < 7) {
      return `${days}일 전`;
    }
    return dbDate.toLocaleDateString('ko-KR', {
      timeZone: 'Asia/Seoul',
    });
  }

  onMount(() => {
    loadConversations();
    window.addEventListener('conversationCreated', handleConversationCreated);
    return () => {
      window.removeEventListener('conversationCreated', handleConversationCreated);
    };
  });
</script>

<div class="history-view">
  <div class="history-toolbar">
    <button
      class="btn-secondary"
      onclick={() => {
        window.dispatchEvent(
          new CustomEvent('selectConversation', {
            detail: { conversationId: null },
          })
        );
        onSelectConversation(null);
      }}
    >
      새 대화
    </button>
  </div>

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
          <button class="conversation-item" onclick={() => selectConversation(conversation.id)}>
            <div class="conversation-title">{conversation.title || '제목 없음'}</div>
            <div class="conversation-meta">
              <span class="conversation-date">{formatDate(conversation.updatedAt)}</span>
              <span class="conversation-separator">•</span>
              <span class="conversation-messages">메시지 {conversation.messageCount || 0}개</span>
            </div>
          </button>
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

  .history-toolbar {
    display: flex;
    justify-content: flex-end;
    padding: 1rem 1rem 0;
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

  .hint {
    margin-top: 0.5rem;
    font-size: 0.9rem;
  }

  .conversation-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .conversation-item {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    padding: 1rem;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
  }

  .conversation-item:hover {
    background: var(--color-surface-hover);
    border-color: var(--color-primary);
  }

  .conversation-title {
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .conversation-meta {
    display: flex;
    gap: 0.4rem;
    color: var(--color-text-muted);
    font-size: 0.85rem;
  }
</style>
