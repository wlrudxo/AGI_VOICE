<script>
  import Icon from '@iconify/svelte';
  import Tooltip from './Tooltip.svelte';

  let {
    title = '',
    icon = '',
    items = [],
    activeItem = '',
    onSelect = () => {},
    children,
  } = $props();

  let isCollapsed = $state(false);
</script>

<div class="sub-sidebar-layout" style={isCollapsed ? '--sub-sidebar-width: 5.5rem;' : ''}>
  <aside class="sub-sidebar" class:collapsed={isCollapsed}>
    <div class="sub-sidebar-header" class:collapsed={isCollapsed}>
      <Icon icon={icon} width="24" height="24" />
      {#if !isCollapsed}
        <h2>{title}</h2>
      {/if}
    </div>

    <nav class="sub-nav">
      {#each items as item}
        {#if isCollapsed}
          <Tooltip text={item.label} position="right">
            <button
              class="sub-nav-item collapsed"
              class:active={activeItem === item.id}
              onclick={() => onSelect(item.id)}
            >
              <Icon icon={item.icon} width="20" height="20" />
            </button>
          </Tooltip>
        {:else}
          <button class="sub-nav-item" class:active={activeItem === item.id} onclick={() => onSelect(item.id)}>
            <Icon icon={item.icon} width="20" height="20" />
            <span>{item.label}</span>
          </button>
        {/if}
      {/each}
    </nav>

    <div class="sub-sidebar-footer">
      <button class="sub-sidebar-toggle-btn" onclick={() => (isCollapsed = !isCollapsed)}>
        <Icon
          icon={isCollapsed ? 'solar:alt-arrow-right-bold-duotone' : 'solar:alt-arrow-left-bold-duotone'}
          width="24"
          height="24"
        />
      </button>
    </div>
  </aside>

  <main class="sub-content">
    {@render children?.()}
  </main>
</div>
