<script>
  import Icon from '@iconify/svelte';
  import { uiStore } from '../stores/uiStore.js';
  import ChatView from '../views/ChatView.svelte';
  import ChatHistoryView from '../views/ChatHistoryView.svelte';
  import ChatSettingsView from '../views/ChatSettingsView.svelte';

  let viewMode = $derived($uiStore.chatViewMode);
  let isExpanded = $derived($uiStore.isChatExpanded);

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
    window.dispatchEvent(
      new CustomEvent('selectConversation', {
        detail: { conversationId: null },
      })
    );
    uiStore.setChatViewMode('chat');
  }
</script>

<div class="chat-widget" class:expanded={isExpanded}>
  <div class="chat-header">
    <div class="header-title">
      {#if viewMode === 'chat'}
        <span class="title-text">새 채팅</span>
      {:else if viewMode === 'history'}
        <span class="title-text">대화기록</span>
      {:else}
        <span class="title-text">채팅 설정</span>
      {/if}
    </div>

    <div class="header-actions">
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
      {:else}
        <button class="icon-btn" onclick={switchToChat} title="채팅으로 돌아가기">
          <Icon icon="solar:chat-round-bold-duotone" width="20" height="20" />
        </button>
      {/if}
      <button class="icon-btn" onclick={() => uiStore.setChatExpanded(!isExpanded)} title="크기 조절">
        <Icon icon={isExpanded ? 'solar:minimize-square-bold-duotone' : 'solar:maximize-square-bold-duotone'} width="20" height="20" />
      </button>
      <button class="icon-btn" onclick={() => uiStore.setChatOpen(false)} title="닫기">
        <Icon icon="solar:close-circle-bold" width="20" height="20" />
      </button>
    </div>
  </div>

  <div class="widget-content">
    <div class="view-container" class:hidden={viewMode !== 'chat'}>
      <ChatView />
    </div>
    <div class="view-container" class:hidden={viewMode !== 'history'}>
      <ChatHistoryView onSelectConversation={switchToChat} />
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

  .widget-content {
    flex: 1;
    min-height: 0;
  }

  .view-container {
    height: 100%;
  }

  .view-container.hidden {
    display: none;
  }
</style>
