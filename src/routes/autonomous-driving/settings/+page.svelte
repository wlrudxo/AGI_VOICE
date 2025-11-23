<script lang="ts">
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { carmakerStore } from '$lib/stores/carmakerStore.svelte';

  const controlModes = ['Abs', 'Off', 'Fac', 'AbsRamp', 'FacRamp'];

  let saving = $state(false);
  let message = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  // Check connection status on mount (for page reload)
  onMount(async () => {
    await carmakerStore.checkConnectionStatus();
  });

  async function connect() {
    const success = await carmakerStore.connect();
    if (success) {
      message = { type: 'success', text: `${carmakerStore.host}:${carmakerStore.port}에 연결되었습니다.` };
      setTimeout(() => { message = null; }, 3000);
    } else {
      message = { type: 'error', text: '연결에 실패했습니다.' };
      setTimeout(() => { message = null; }, 3000);
    }
  }

  async function disconnect() {
    const success = await carmakerStore.disconnect();
    if (success) {
      message = { type: 'success', text: 'CarMaker와의 연결이 해제되었습니다.' };
      setTimeout(() => { message = null; }, 3000);
    }
  }

  async function saveSettings() {
    try {
      saving = true;
      message = null;

      // TODO: Save settings to backend (if needed)
      console.log('Settings saved:', {
        host: carmakerStore.host,
        port: carmakerStore.port,
        duration: carmakerStore.duration,
        controlMode: carmakerStore.controlMode
      });

      message = { type: 'success', text: '설정이 저장되었습니다.' };

      // 3초 후 메시지 제거
      setTimeout(() => {
        message = null;
      }, 3000);
    } catch (err: any) {
      console.error('Failed to save settings:', err);
      message = { type: 'error', text: err.message || '설정 저장에 실패했습니다.' };
    } finally {
      saving = false;
    }
  }
</script>

<div class="autonomous-settings">
  <div class="page-header">
    <div>
      <h1>⚙️ 자율주행 설정</h1>
      <p class="page-description">CarMaker 제어와 관련된 설정을 관리합니다.</p>
    </div>
  </div>

  <!-- CarMaker Connection Section -->
  <div class="settings-form">
    <div class="form-section">
      <h2 class="section-title">
        <Icon icon="solar:link-circle-bold-duotone" width="20" height="20" />
        <span>CarMaker Connection</span>
      </h2>

      <div class="connection-controls">
        <div class="input-group">
          <label for="host">Host:</label>
          <input
            id="host"
            type="text"
            bind:value={carmakerStore.host}
            disabled={carmakerStore.isConnected}
            class="input-field"
          />
        </div>
        <div class="input-group">
          <label for="port">Port:</label>
          <input
            id="port"
            type="text"
            bind:value={carmakerStore.port}
            disabled={carmakerStore.isConnected}
            class="input-field"
          />
        </div>
        <button
          class="btn-primary"
          disabled={carmakerStore.isConnected}
          onclick={connect}
        >
          Connect
        </button>
        <button
          class="btn-secondary"
          disabled={!carmakerStore.isConnected}
          onclick={disconnect}
        >
          Disconnect
        </button>
        <div class="status-indicator">
          <span class="status-dot" class:connected={carmakerStore.isConnected}></span>
          <span class="text-secondary">
            {carmakerStore.isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </div>
  </div>

  <!-- Control Settings Section -->
  <div class="settings-form">
    <div class="form-section">
      <h2 class="section-title">
        <Icon icon="solar:settings-minimalistic-bold-duotone" width="20" height="20" />
        <span>Control Settings</span>
      </h2>

      <div class="settings-controls">
        <div class="input-group">
          <label for="duration">Duration (ms):</label>
          <input
            id="duration"
            type="text"
            bind:value={carmakerStore.duration}
            class="input-field"
          />
        </div>
        <div class="input-group">
          <label for="mode">Control Mode:</label>
          <select id="mode" bind:value={carmakerStore.controlMode} class="select-field">
            {#each controlModes as mode}
              <option value={mode}>{mode}</option>
            {/each}
          </select>
        </div>
      </div>
    </div>
  </div>

  <!-- 메시지 & 저장 버튼 -->
  {#if message}
    <div class="message" class:success={message.type === 'success'} class:error={message.type === 'error'}>
      {message.text}
    </div>
  {/if}

  <div class="form-actions">
    <button type="button" class="btn-primary" onclick={saveSettings} disabled={saving}>
      <Icon icon="solar:diskette-bold-duotone" width="20" height="20" />
      <span>{saving ? '저장 중...' : '설정 저장'}</span>
    </button>
  </div>
</div>

<style>
  .autonomous-settings {
    max-width: 800px;
    margin: 0 auto;
  }

  .settings-form {
    background: var(--color-surface);
    border-radius: 0.75rem;
    padding: 2rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.5rem;
  }

  .form-section {
    margin-bottom: 2rem;
  }

  .form-section:last-child {
    margin-bottom: 0;
  }

  /* Settings Controls */
  .connection-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .settings-controls {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
  }

  .input-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .input-group label {
    font-weight: 600;
    color: var(--color-text-secondary);
  }

  .message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
    font-weight: 500;
  }

  .message.success {
    background: #d1fae5;
    color: #065f46;
  }

  .message.error {
    background: #fee2e2;
    color: #991b1b;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
  }
</style>
