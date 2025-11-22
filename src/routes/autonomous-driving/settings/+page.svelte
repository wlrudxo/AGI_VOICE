<script lang="ts">
  import Icon from '@iconify/svelte';

  // Control settings
  let duration = $state('2000');
  let controlMode = $state('Abs');
  const controlModes = ['Abs', 'Off', 'Fac', 'AbsRamp', 'FacRamp'];

  let saving = $state(false);
  let message = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  async function saveSettings() {
    try {
      saving = true;
      message = null;

      // TODO: Save settings to backend
      console.log('Settings saved:', { duration, controlMode });

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
    <h1>⚙️ 자율주행 설정</h1>
    <p class="page-description">CarMaker 제어와 관련된 설정을 관리합니다.</p>
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
            bind:value={duration}
            class="input-field"
          />
        </div>
        <div class="input-group">
          <label for="mode">Control Mode:</label>
          <select id="mode" bind:value={controlMode} class="select-field">
            {#each controlModes as mode}
              <option value={mode}>{mode}</option>
            {/each}
          </select>
        </div>
      </div>

      <!-- 메시지 -->
      {#if message}
        <div class="message" class:success={message.type === 'success'} class:error={message.type === 'error'}>
          {message.text}
        </div>
      {/if}

      <!-- 저장 버튼 -->
      <div class="form-actions">
        <button type="button" class="btn-primary" onclick={saveSettings} disabled={saving}>
          <Icon icon="solar:diskette-bold-duotone" width="20" height="20" />
          <span>{saving ? '저장 중...' : '설정 저장'}</span>
        </button>
      </div>
    </div>
  </div>

  <!-- TODO: CarMaker 연결 설정, 트리거 민감도 등 추가 -->
</div>

<style>
  .autonomous-settings {
    max-width: 800px;
    margin: 0 auto;
  }

  .page-header {
    margin-bottom: 2rem;
  }

  .page-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-text-primary);
    margin: 0 0 0.5rem 0;
  }

  .page-description {
    color: var(--color-text-secondary);
    margin: 0;
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

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 1.5rem 0;
  }

  /* Settings Controls */
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

  .input-field {
    padding: 0.75rem 1rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    background: var(--color-surface);
    color: var(--color-text-primary);
    font-size: 1rem;
    transition: all 0.2s;
  }

  .input-field:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: var(--focus-ring);
  }

  .select-field {
    padding: 0.75rem 1rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    background: var(--color-surface);
    color: var(--color-text-primary);
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .select-field:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: var(--focus-ring);
  }

  .message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-top: 1.5rem;
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
    margin-top: 1.5rem;
  }
</style>
