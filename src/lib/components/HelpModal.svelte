<script lang="ts">
  import Icon from '@iconify/svelte';

  interface Props {
    visible: boolean;
    title?: string;
    onClose: () => void;
  }

  let { visible = $bindable(), title = '도움말', onClose }: Props = $props();

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (visible && e.key === 'Escape') {
      onClose();
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if visible}
  <div class="modal-backdrop" onclick={handleBackdropClick} role="presentation">
    <div class="modal-container" role="dialog" aria-modal="true">
      <div class="modal-header">
        <h3 class="modal-title">
          <Icon icon="solar:book-bold-duotone" width="24" height="24" />
          {title}
        </h3>
        <button class="btn-icon close-btn" onclick={onClose} title="닫기">
          <Icon icon="solar:close-circle-bold" width="24" height="24" />
        </button>
      </div>

      <div class="modal-content">
        <slot />
      </div>

      <div class="modal-footer">
        <button class="btn-primary" onclick={onClose}>닫기</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--overlay-medium);
    animation: fadeIn 0.15s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .modal-container {
    background: var(--color-surface);
    border-radius: 0.75rem;
    box-shadow: var(--shadow-dialog);
    width: 90%;
    max-width: 700px;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
    animation: scaleIn 0.15s ease-out;
  }

  @keyframes scaleIn {
    from {
      transform: scale(0.95);
      opacity: 0;
    }
    to {
      transform: scale(1);
      opacity: 1;
    }
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--color-border);
    flex-shrink: 0;
  }

  .modal-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .close-btn {
    opacity: 0.7;
    transition: opacity 0.2s;
  }

  .close-btn:hover {
    opacity: 1;
  }

  .modal-content {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--color-border);
    display: flex;
    justify-content: flex-end;
    background: var(--color-background);
    flex-shrink: 0;
  }

  /* Help content styles (available for slotted content) */
  :global(.help-section) {
    margin-bottom: 2rem;
  }

  :global(.help-section:last-child) {
    margin-bottom: 0;
  }

  :global(.help-section h4) {
    margin: 0 0 1rem 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  :global(.help-desc) {
    margin: 0 0 1rem 0;
    color: var(--color-text-secondary);
    line-height: 1.6;
  }

  :global(.command-example) {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 0.875rem 1rem;
    margin-bottom: 0.75rem;
  }

  :global(.command-example:last-child) {
    margin-bottom: 0;
  }

  :global(.command-example.highlight) {
    border-color: var(--color-primary);
    background: var(--color-primary-bg-light);
  }

  :global(.command-example code) {
    display: block;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
    color: var(--color-primary);
    font-weight: 600;
    margin-bottom: 0.375rem;
  }

  :global(.command-example p) {
    margin: 0;
    font-size: 0.875rem;
    color: var(--color-text-secondary);
  }

  :global(.param-table) {
    display: flex;
    flex-direction: column;
    gap: 0.625rem;
  }

  :global(.param-row) {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 1rem;
    padding: 0.75rem;
    background: var(--color-background);
    border-radius: 0.375rem;
    border: 1px solid var(--color-border);
  }

  :global(.param-name) {
    font-family: 'Courier New', monospace;
    font-weight: 600;
    color: var(--color-primary);
    font-size: 0.875rem;
  }

  :global(.param-desc) {
    color: var(--color-text-secondary);
    font-size: 0.875rem;
    line-height: 1.6;
  }

  :global(.param-desc strong) {
    color: var(--color-text-primary);
    font-weight: 600;
  }
</style>
