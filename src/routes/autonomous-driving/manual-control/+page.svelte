<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import Icon from '@iconify/svelte';

  // Driver inputs
  let gasValue = $state(0.0);
  let brakeValue = $state(0.0);
  let steerValue = $state(0.0);

  // Text command
  let commandInput = $state('');

  // Log
  let logMessages: string[] = $state([]);

  async function sendControl(controlType: string, value: number) {
    try {
      const duration = 2000; // Default 2 seconds
      let result: string;

      if (controlType === 'Gas') {
        result = await invoke('set_gas', { value, duration });
      } else if (controlType === 'Brake') {
        result = await invoke('set_brake', { value, duration });
      } else if (controlType === 'Steer.Ang') {
        result = await invoke('set_steer', { value, duration });
      } else {
        throw new Error(`Unknown control type: ${controlType}`);
      }

      addLog(`✓ ${controlType} = ${value.toFixed(2)}`);
    } catch (error: any) {
      addLog(`✗ ${controlType} failed: ${error}`);
    }
  }

  async function executeCommand() {
    if (!commandInput.trim()) return;

    try {
      const result = await invoke('execute_vehicle_command', { command: commandInput });
      addLog(`✓ ${commandInput} → ${result}`);
      commandInput = '';
    } catch (error: any) {
      addLog(`✗ Command failed: ${error}`);
    }
  }

  function addLog(message: string) {
    const timestamp = new Date().toLocaleTimeString();
    logMessages = [...logMessages, `[${timestamp}] ${message}`];

    // Keep last 100 messages
    if (logMessages.length > 100) {
      logMessages = logMessages.slice(-100);
    }
  }
</script>

<div class="manual-control">
  <div class="page-header">
    <div>
      <h1>🎮 메뉴얼 제어</h1>
      <p class="page-description">차량을 수동으로 제어하고 명령을 실행합니다.</p>
    </div>
  </div>

  <!-- Driver Inputs -->
  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:steering-wheel-bold-duotone" width="24" height="24" />
      Driver Inputs
    </h2>

    <!-- Gas -->
    <div class="control-row">
      <label class="control-label">Gas (0-1):</label>
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        bind:value={gasValue}
        class="slider"
      />
      <span class="value-display">{gasValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Gas', gasValue)}>
        Set
      </button>
    </div>

    <!-- Brake -->
    <div class="control-row">
      <label class="control-label">Brake (0-1):</label>
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        bind:value={brakeValue}
        class="slider"
      />
      <span class="value-display">{brakeValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Brake', brakeValue)}>
        Set
      </button>
    </div>

    <!-- Steering -->
    <div class="control-row">
      <label class="control-label">Steer (-1~1):</label>
      <input
        type="range"
        min="-1"
        max="1"
        step="0.01"
        bind:value={steerValue}
        class="slider"
      />
      <span class="value-display">{steerValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Steer.Ang', steerValue)}>
        Set
      </button>
    </div>
  </section>

  <!-- Text Command Input -->
  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:code-bold-duotone" width="24" height="24" />
      Text Command Input
    </h2>
    <div class="command-input-group">
      <input
        type="text"
        bind:value={commandInput}
        placeholder="Enter command..."
        class="input-field command-input"
        onkeydown={(e) => e.key === 'Enter' && executeCommand()}
      />
      <button class="btn-primary" onclick={executeCommand}>
        Execute
      </button>
    </div>
  </section>

  <!-- Log Section -->
  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:document-text-bold-duotone" width="24" height="24" />
      Log
    </h2>
    <div class="log-container">
      {#if logMessages.length === 0}
        <p class="text-muted">No logs yet...</p>
      {:else}
        {#each logMessages as message}
          <div class="log-message text-secondary">{message}</div>
        {/each}
      {/if}
    </div>
  </section>
</div>

<style>
  .manual-control {
    max-width: 1400px;
    margin: 0 auto;
  }

  /* Section Styles - use rounded corners and shadow */
  .section {
    border-radius: 0.75rem;
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
  }

  /* Control Row (Sliders) */
  .control-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .control-label {
    min-width: 120px;
    font-weight: 500;
    color: var(--color-text-secondary);
  }

  .value-display {
    min-width: 50px;
    text-align: right;
    font-family: 'Courier New', monospace;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  /* Additional button styles */
  .btn-set {
    min-width: 60px;
  }

  /* Command Input */
  .command-input-group {
    display: flex;
    gap: 0.5rem;
  }

  .command-input {
    flex: 1;
  }
</style>
