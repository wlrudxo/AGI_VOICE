<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    text?: string;
    position?: 'top' | 'bottom' | 'left' | 'right';
    children?: Snippet;
  }

  let { text = '', position = 'right', children }: Props = $props();

  let showTooltip = $state(false);
  let wrapperElement: HTMLElement;
  let tooltipStyle = $state('');

  function updateTooltipPosition() {
    if (!wrapperElement || !showTooltip) return;

    const rect = wrapperElement.getBoundingClientRect();

    if (position === 'right') {
      tooltipStyle = `
        position: fixed;
        left: ${rect.right + 8}px;
        top: ${rect.top + rect.height / 2}px;
        transform: translateY(-50%);
      `;
    }
  }

  $effect(() => {
    if (showTooltip) {
      updateTooltipPosition();
    }
  });
</script>

<div
  bind:this={wrapperElement}
  class="tooltip-wrapper"
  onmouseenter={() => {
    showTooltip = true;
    setTimeout(updateTooltipPosition, 0);
  }}
  onmouseleave={() => showTooltip = false}
  role="tooltip"
>
  {@render children?.()}
</div>

{#if showTooltip && text}
  <div class="tooltip" style={tooltipStyle}>
    {text}
  </div>
{/if}

<style>
  .tooltip-wrapper {
    position: relative;
    display: inline-block;
  }

  .tooltip {
    position: fixed;
    z-index: 9999;
    padding: 0.5rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    white-space: nowrap;
    pointer-events: none;
    background: #1e293b;
    color: white;
    box-shadow: var(--shadow-tooltip);
  }
</style>
