<script lang="ts">
  type DialogType = 'confirm' | 'alert';

  let visible = $state(false);
  let dialogType = $state<DialogType>('alert');
  let title = $state('');
  let message = $state('');
  let resolveCallback: ((value: boolean) => void) | null = null;

  export function confirm(msg: string, titleText: string = '확인'): Promise<boolean> {
    return new Promise((resolve) => {
      dialogType = 'confirm';
      title = titleText;
      message = msg;
      visible = true;
      resolveCallback = resolve;
    });
  }

  export function alert(msg: string, titleText: string = '알림'): Promise<boolean> {
    return new Promise((resolve) => {
      dialogType = 'alert';
      title = titleText;
      message = msg;
      visible = true;
      resolveCallback = resolve;
    });
  }

  function handleConfirm() {
    if (resolveCallback) {
      resolveCallback(true);
    }
    close();
  }

  function handleCancel() {
    if (resolveCallback) {
      resolveCallback(false);
    }
    close();
  }

  function close() {
    visible = false;
    resolveCallback = null;
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      handleCancel();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (!visible) return;

    if (e.key === 'Escape') {
      handleCancel();
    } else if (e.key === 'Enter' && dialogType === 'alert') {
      handleConfirm();
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if visible}
  <div
    class="dialog-backdrop"
    onclick={handleBackdropClick}
    onkeydown={(e) => e.key === 'Escape' && handleCancel()}
    role="presentation"
  >
    <div class="dialog-container" role="dialog" aria-labelledby="dialog-title" aria-modal="true">
      <div class="dialog-header">
        <h3 id="dialog-title" class="dialog-title">{title}</h3>
      </div>

      <div class="dialog-content">
        <p class="dialog-message">{message}</p>
      </div>

      <div class="dialog-footer">
        {#if dialogType === 'confirm'}
          <button class="btn-secondary" onclick={handleCancel}>
            취소
          </button>
          <button class="btn-primary" onclick={handleConfirm}>
            확인
          </button>
        {:else}
          <button class="btn-primary" onclick={handleConfirm}>
            확인
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .dialog-backdrop {
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

  .dialog-container {
    background: var(--color-surface);
    border-radius: 0.75rem;
    box-shadow: var(--shadow-dialog);
    width: 90%;
    max-width: 400px;
    overflow: hidden;
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

  .dialog-header {
    padding: 1.25rem 1.5rem 1rem;
    border-bottom: 1px solid var(--color-border);
  }

  .dialog-title {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .dialog-content {
    padding: 1.5rem;
  }

  .dialog-message {
    margin: 0;
    font-size: 0.9375rem;
    line-height: 1.6;
    color: var(--color-text-secondary);
    white-space: pre-wrap;
  }

  .dialog-footer {
    padding: 1rem 1.5rem 1.25rem;
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    background: var(--color-background);
  }

  .dialog-footer button {
    min-width: 5rem;
  }
</style>
