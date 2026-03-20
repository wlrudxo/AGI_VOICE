<script>
  import Icon from '@iconify/svelte';
  import Tooltip from './lib/components/Tooltip.svelte';
  import SettingsView from './lib/views/SettingsView.svelte';
  import ManualControlView from './lib/views/ManualControlView.svelte';
  import TriggerSettingsView from './lib/views/TriggerSettingsView.svelte';
  import VehicleControlView from './lib/views/VehicleControlView.svelte';

  let activeView = $state('vehicle-control');
  let isCollapsed = $state(false);

  const views = [
    { id: 'vehicle-control', icon: 'solar:widget-2-bold-duotone', label: '차량 제어' },
    { id: 'manual-control', icon: 'solar:gameboy-bold-duotone', label: '메뉴얼 제어' },
    { id: 'triggers', icon: 'solar:atom-bold-duotone', label: '트리거 설정' },
    { id: 'settings', icon: 'solar:settings-bold-duotone', label: '설정' },
  ];

  function toggleSubSidebar() {
    isCollapsed = !isCollapsed;
  }
</script>

<svelte:head>
  <title>AGI Voice V3 Autonomous Driving</title>
  <meta
    name="description"
    content="V3 autonomous driving frontend backed by the Python CarMaker API."
  />
</svelte:head>

<div class="sub-sidebar-layout" style={isCollapsed ? '--sub-sidebar-width: 5.5rem;' : ''}>
  <aside class="sub-sidebar" class:collapsed={isCollapsed}>
    <div class="sub-sidebar-header" class:collapsed={isCollapsed}>
      <Icon icon="solar:wheel-bold-duotone" width="24" height="24" />
      {#if !isCollapsed}
        <h2>자율주행</h2>
      {/if}
    </div>

    <nav class="sub-nav" aria-label="Autonomous Driving Views">
      {#each views as view}
        {#if isCollapsed}
          <Tooltip text={view.label} position="right">
            <button
              class="sub-nav-item collapsed"
              class:active={activeView === view.id}
              onclick={() => (activeView = view.id)}
            >
              <Icon icon={view.icon} width="20" height="20" />
            </button>
          </Tooltip>
        {:else}
          <button
            class="sub-nav-item"
            class:active={activeView === view.id}
            onclick={() => (activeView = view.id)}
          >
            <Icon icon={view.icon} width="20" height="20" />
            <span>{view.label}</span>
          </button>
        {/if}
      {/each}
    </nav>

    <div class="sub-sidebar-footer">
      <button class="sub-sidebar-toggle-btn" onclick={toggleSubSidebar}>
        <Icon
          icon={isCollapsed ? 'solar:alt-arrow-right-bold-duotone' : 'solar:alt-arrow-left-bold-duotone'}
          width="24"
          height="24"
        />
      </button>
    </div>
  </aside>

  <main class="sub-content">
    {#if activeView === 'vehicle-control'}
      <VehicleControlView />
    {:else if activeView === 'manual-control'}
      <ManualControlView />
    {:else if activeView === 'triggers'}
      <TriggerSettingsView />
    {:else if activeView === 'settings'}
      <SettingsView />
    {/if}
  </main>
</div>
