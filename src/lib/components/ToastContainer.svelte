<script lang="ts">
  import { toastStore } from '$lib/stores/toastStore.svelte';
  import Icon from '@iconify/svelte';

  const icons: Record<string, string> = {
    success: 'solar:check-circle-bold',
    error: 'solar:close-circle-bold',
    warning: 'solar:danger-triangle-bold',
    info: 'solar:info-circle-bold'
  };
</script>

<div class="toast-container">
  {#each toastStore.toasts as toast (toast.id)}
    <div class="toast toast-{toast.type}" role="alert">
      <Icon icon={icons[toast.type]} width="20" height="20" />
      <span class="toast-message">{toast.message}</span>
      <button class="toast-close" onclick={() => toastStore.remove(toast.id)}>
        <Icon icon="solar:close-circle-linear" width="16" height="16" />
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    top: 4rem;
    right: 1rem;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    pointer-events: none;
  }

  .toast {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    pointer-events: auto;
    animation: slideIn 0.3s ease-out;
    max-width: 360px;
    min-width: 200px;
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  .toast-success {
    background: var(--color-success, #10b981);
    color: white;
  }

  .toast-error {
    background: var(--color-error, #ef4444);
    color: white;
  }

  .toast-warning {
    background: var(--color-warning, #f59e0b);
    color: white;
  }

  .toast-info {
    background: var(--color-info, #3b82f6);
    color: white;
  }

  .toast-message {
    flex: 1;
    font-size: 0.875rem;
    font-weight: 500;
    line-height: 1.4;
  }

  .toast-close {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    opacity: 0.7;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.2s;
  }

  .toast-close:hover {
    opacity: 1;
  }
</style>
