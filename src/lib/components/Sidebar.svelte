<script lang="ts">
  import { page } from '$app/stores';
  import { uiStore } from '$lib/stores/uiStore';
  import Icon from '@iconify/svelte';
  import Tooltip from './Tooltip.svelte';

  interface NavItem {
    name: string;
    path: string;
    icon: string;
  }

  const navItems: NavItem[] = [
    { name: '대시보드', path: '/', icon: 'solar:widget-2-bold-duotone' },
    { name: '자율주행', path: '/autonomous-driving', icon: 'solar:wheel-bold-duotone' },
    { name: 'Map 생성', path: '/map-settings', icon: 'solar:map-point-wave-bold-duotone' },
    { name: 'AI 설정', path: '/ai-settings', icon: 'solar:settings-minimalistic-bold-duotone' },
    { name: '설정', path: '/settings', icon: 'solar:settings-bold-duotone' }
  ];

  $: currentPath = $page.url.pathname;
  $: collapsed = $uiStore.isSidebarCollapsed;
  $: isChatOpen = $uiStore.isChatOpen;

  function isActive(itemPath: string): boolean {
    if (itemPath === '/') {
      return currentPath === '/';
    }
    return currentPath.startsWith(itemPath);
  }

  function toggleSidebar() {
    uiStore.toggleSidebar();
  }

  function toggleChat() {
    uiStore.toggleChat();
  }
</script>

<aside
  class="sidebar bg-sidebar"
  class:collapsed
>
  <!-- Logo (removed) -->

  <!-- Navigation -->
  <nav class="nav-section">
    {#each navItems as item}
      {#if collapsed}
        <Tooltip text={item.name} position="right">
          <a
            href={item.path}
            class="nav-item"
            class:active={isActive(item.path)}
            class:collapsed
          >
            <Icon icon={item.icon} width="24" height="24" />
          </a>
        </Tooltip>
      {:else}
        <a
          href={item.path}
          class="nav-item"
          class:active={isActive(item.path)}
        >
          <Icon icon={item.icon} width="24" height="24" />
          <span class="nav-label">{item.name}</span>
        </a>
      {/if}
    {/each}
  </nav>

  <!-- Chat Button Section -->
  <div class="chat-buttons-section">
    <!-- AI 채팅 버튼 -->
    {#if collapsed}
      <Tooltip text="AI 채팅" position="right">
        <button
          class="chat-toggle-btn"
          class:active={isChatOpen}
          on:click={toggleChat}
        >
          <Icon icon="solar:chat-round-dots-bold-duotone" width="24" height="24" />
        </button>
      </Tooltip>
    {:else}
      <button
        class="chat-toggle-btn"
        class:active={isChatOpen}
        on:click={toggleChat}
      >
        <Icon icon="solar:chat-round-dots-bold-duotone" width="24" height="24" />
        <span class="chat-label">AI 채팅</span>
      </button>
    {/if}
  </div>

  <!-- Toggle Button -->
  <div class="toggle-section">
    <button class="toggle-btn" on:click={toggleSidebar}>
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
  }

  .sidebar.collapsed {
    width: 5.5rem;
  }

  /* Navigation */
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

  .nav-label {
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* Chat Buttons Section */
  .chat-buttons-section {
    margin-top: auto;
    padding-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
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

  .chat-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* Toggle Button */
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
