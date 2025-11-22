<script lang="ts">
  import Icon from '@iconify/svelte';
</script>

<div class="stop-conditions">
  <h1 class="text-primary page-title">
    <Icon icon="solar:stop-bold-duotone" width="32" height="32" />
    정지조건
  </h1>

  <div class="placeholder-content">
    <Icon icon="solar:stop-bold-duotone" width="64" height="64" class="placeholder-icon" />
    <p class="text-secondary">정지조건 설정 페이지</p>
    <p class="text-muted">Coming soon...</p>
  </div>
</div>

<style>
  .stop-conditions {
    max-width: 1400px;
    margin: 0 auto;
  }

  .page-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 2rem;
  }

  .placeholder-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    gap: 1rem;
  }

  .placeholder-content :global(.placeholder-icon) {
    color: var(--color-primary);
    opacity: 0.5;
  }
</style>
