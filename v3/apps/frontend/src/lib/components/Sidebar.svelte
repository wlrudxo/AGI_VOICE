<script>
  import Icon from '@iconify/svelte';
  import Tooltip from './Tooltip.svelte';
  import { uiStore } from '../stores/uiStore.js';

  let { sectionDefaults = {} } = $props();

  const navItems = [
    { id: 'dashboard', name: '대시보드', icon: 'solar:widget-2-bold-duotone' },
    { id: 'autonomous-driving', name: '자율주행', icon: 'solar:wheel-bold-duotone' },
    { id: 'map-settings', name: 'Map 생성', icon: 'solar:map-point-wave-bold-duotone' },
    { id: 'ai-settings', name: 'AI 설정', icon: 'solar:settings-minimalistic-bold-duotone' },
    { id: 'app-settings', name: '앱 설정', icon: 'solar:settings-bold-duotone' },
  ];

  let collapsed = $derived($uiStore.isSidebarCollapsed);
  let isChatOpen = $derived($uiStore.isChatOpen);
  let activeSection = $derived($uiStore.activeSection);

  function selectSection(itemId) {
    uiStore.setSection(itemId, sectionDefaults[itemId] ?? null);
  }
</script>

<aside class="sidebar bg-sidebar" class:collapsed>
  <nav class="nav-section">
    {#each navItems as item}
      {#if collapsed}
        <Tooltip text={item.name} position="right">
          <button
            class="nav-item collapsed"
            class:active={activeSection === item.id}
            onclick={() => selectSection(item.id)}
          >
            <Icon icon={item.icon} width="24" height="24" />
          </button>
        </Tooltip>
      {:else}
        <button class="nav-item" class:active={activeSection === item.id} onclick={() => selectSection(item.id)}>
          <Icon icon={item.icon} width="24" height="24" />
          <span class="nav-label">{item.name}</span>
        </button>
      {/if}
    {/each}
  </nav>

  <div class="chat-buttons-section">
    {#if collapsed}
      <Tooltip text="AI 채팅" position="right">
        <button class="chat-toggle-btn" class:active={isChatOpen} onclick={() => uiStore.toggleChat()}>
          <Icon icon="solar:chat-round-dots-bold-duotone" width="24" height="24" />
        </button>
      </Tooltip>
    {:else}
      <button class="chat-toggle-btn" class:active={isChatOpen} onclick={() => uiStore.toggleChat()}>
        <Icon icon="solar:chat-round-dots-bold-duotone" width="24" height="24" />
        <span class="chat-label">AI 채팅</span>
      </button>
    {/if}
  </div>

  <div class="toggle-section">
    <button class="toggle-btn" onclick={() => uiStore.toggleSidebar()}>
      <Icon
        icon={collapsed ? 'solar:alt-arrow-right-bold-duotone' : 'solar:alt-arrow-left-bold-duotone'}
        width="24"
        height="24"
      />
    </button>
  </div>
</aside>

<style>
  .sidebar {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 40px;
    left: 0;
    height: calc(100vh - 40px);
    width: 14rem;
    padding: 1rem;
    border-right: 1px solid var(--border-light);
    transition: width 300ms ease-in-out;
    overflow-x: visible;
    overflow-y: auto;
    background: var(--color-sidebar-bg);
  }

  .sidebar.collapsed {
    width: 5.5rem;
  }

  .nav-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-sidebar-text);
    text-decoration: none;
    transition: all 200ms;
    cursor: pointer;
    white-space: nowrap;
    background: transparent;
    border: none;
  }

  .nav-item.collapsed {
    justify-content: center;
    width: 3.5rem;
    height: 3.5rem;
  }

  .nav-item:hover {
    background-color: var(--color-sidebar-hover);
  }

  .nav-item.active {
    background-color: var(--color-sidebar-active);
    font-weight: 600;
  }

  .nav-label,
  .chat-label {
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .chat-buttons-section {
    margin-top: auto;
    padding-top: 1rem;
  }

  .chat-toggle-btn {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    width: 100%;
    padding: 0.75rem;
    border: none;
    border-radius: 0.5rem;
    background: transparent;
    color: var(--color-sidebar-text);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 200ms;
  }

  .sidebar.collapsed .chat-toggle-btn {
    justify-content: center;
    width: 3.5rem;
    height: 3.5rem;
  }

  .chat-toggle-btn:hover {
    background-color: var(--color-sidebar-hover);
  }

  .chat-toggle-btn.active {
    background-color: var(--color-sidebar-active);
    font-weight: 600;
  }

  .toggle-section {
    padding-top: 1rem;
    position: relative;
    z-index: 10;
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3.5rem;
    height: 3.5rem;
    border: 1px solid var(--border-light);
    border-radius: 0.5rem;
    background: var(--color-sidebar-bg);
    color: var(--color-sidebar-text);
    cursor: pointer;
    transition: all 200ms;
  }

  .toggle-btn:hover {
    background-color: var(--color-sidebar-hover);
    border-color: var(--color-primary);
  }
</style>
