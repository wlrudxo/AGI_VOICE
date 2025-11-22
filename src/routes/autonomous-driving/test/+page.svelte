<script lang="ts">
  import Icon from '@iconify/svelte';
</script>

<div class="test">
  <h1 class="text-primary page-title">테스트</h1>

  <div class="placeholder-content">
    <Icon icon="solar:test-tube-bold-duotone" width="64" height="64" class="placeholder-icon" />
    <p class="text-secondary">자율주행 테스트 페이지</p>
    <p class="text-muted">Coming soon...</p>
  </div>
</div>

<style>
  .test {
    max-width: 1400px;
    margin: 0 auto;
  }

  .page-title {
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
