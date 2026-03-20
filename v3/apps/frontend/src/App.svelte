<script>
  import { onMount } from 'svelte';
  import { carmakerStore } from './lib/carmakerStore.svelte.js';

  let commandInput = $state('DVARead Car.v');
  let watchedInput = $state('0');

  function formatJson(value) {
    return JSON.stringify(value, null, 2);
  }

  function safeTelemetryText() {
    return carmakerStore.telemetry
      ? formatJson(carmakerStore.telemetry.rawData ?? carmakerStore.telemetry)
      : '{ }';
  }

  async function connect() {
    await carmakerStore.connect();
  }

  async function disconnect() {
    await carmakerStore.disconnect();
  }

  async function refreshStatus() {
    await carmakerStore.checkConnectionStatus();
  }

  async function refreshHealth() {
    await carmakerStore.refreshHealth();
  }

  async function refreshWatchedObjects() {
    try {
      await carmakerStore.refreshWatchedTrafficObjects();
    } catch {
      // Store already flattened and logged the error.
    }
  }

  async function toggleMonitoring() {
    await carmakerStore.toggleMonitoring();
  }

  async function sendCommand() {
    try {
      await carmakerStore.executeCommand(commandInput);
    } catch {
      // Store already flattened and logged the error.
    }
  }

  async function addWatchedObject() {
    try {
      await carmakerStore.addWatchedTrafficObject(watchedInput);
    } catch {
      // Store already flattened and logged the error.
    }
  }

  async function removeWatchedObject(index) {
    try {
      await carmakerStore.removeWatchedTrafficObject(index);
    } catch {
      // Store already flattened and logged the error.
    }
  }

  async function clearWatchedObjects() {
    try {
      await carmakerStore.clearWatchedTrafficObjects();
    } catch {
      // Store already flattened and logged the error.
    }
  }

  onMount(() => {
    void carmakerStore.initialize();

    return () => {
      carmakerStore.destroy();
    };
  });
</script>

<svelte:head>
  <title>AGI Voice V3 Diagnostic Frontend</title>
  <meta
    name="description"
    content="V3 frontend diagnostic surface for the Python CarMaker API."
  />
</svelte:head>

<main class="shell">
  <section class="hero">
    <div>
      <p class="eyebrow">AGI Voice V3</p>
      <h1>Diagnostic Frontend</h1>
      <p class="copy">
        Placeholder UI with a real CarMaker store slice. Use this to verify the Python CarMaker
        API before the full V2 UI is migrated.
      </p>
    </div>
    <div class="hero-badges">
      <span class="badge">Backend: {carmakerStore.backendUrl}</span>
      <span class="badge">Source: {carmakerStore.backendSource}</span>
      <span
        class:ok={carmakerStore.healthState === 'ok'}
        class:error={carmakerStore.healthState === 'error'}
        class="badge"
      >
        Health: {carmakerStore.healthState}
      </span>
    </div>
  </section>

  <section class="grid">
    <article class="panel">
      <div class="panel-head">
        <h2>Health</h2>
        <button class="btn ghost" onclick={refreshHealth} disabled={carmakerStore.busy}>Refresh</button>
      </div>
      <p class="muted">{carmakerStore.healthMessage || 'Waiting for backend response.'}</p>
      <dl class="kv">
        <div>
          <dt>Connected</dt>
          <dd>{carmakerStore.connectionStatus?.connected ? 'yes' : 'no'}</dd>
        </div>
        <div>
          <dt>Host</dt>
          <dd>{carmakerStore.connectionStatus?.host ?? carmakerStore.host}</dd>
        </div>
        <div>
          <dt>Port</dt>
          <dd>{carmakerStore.connectionStatus?.port ?? carmakerStore.port}</dd>
        </div>
        <div>
          <dt>Last Error</dt>
          <dd>{carmakerStore.connectionStatus?.lastError ?? 'none'}</dd>
        </div>
      </dl>
    </article>

    <article class="panel">
      <div class="panel-head">
        <h2>Connect</h2>
        <div class="inline-actions">
          <button class="btn" onclick={connect} disabled={carmakerStore.busy}>Connect</button>
          <button class="btn ghost" onclick={disconnect} disabled={carmakerStore.busy}>Disconnect</button>
        </div>
      </div>
      <div class="form-row">
        <label>
          Host
          <input bind:value={carmakerStore.host} />
        </label>
        <label>
          Port
          <input bind:value={carmakerStore.port} inputmode="numeric" />
        </label>
      </div>
      <div class="mini-actions">
        <button class="btn ghost" onclick={refreshStatus} disabled={carmakerStore.busy}>Refresh status</button>
        <button class="btn ghost" onclick={refreshWatchedObjects} disabled={carmakerStore.busy}>Load watched</button>
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <h2>Monitoring</h2>
        <button class="btn" onclick={toggleMonitoring} disabled={carmakerStore.busy}>
          {carmakerStore.isMonitoring ? 'Stop' : 'Start'}
        </button>
      </div>
      <p class="muted">
        V2-style store semantics: 10Hz polling, overlap guard, rawData propagation, and cleanup on
        disconnect/unmount.
      </p>
      <div class="status-line">
        <span class:ok={carmakerStore.isMonitoring} class:warn={!carmakerStore.isMonitoring} class="pill">
          {carmakerStore.isMonitoring ? 'active' : 'idle'}
        </span>
      </div>
    </article>

    <article class="panel panel-wide">
      <div class="panel-head">
        <h2>Command</h2>
        <button class="btn" onclick={sendCommand} disabled={carmakerStore.busy}>Run</button>
      </div>
      <input class="command" bind:value={commandInput} placeholder="DVARead Car.v" />
      <pre class="output">{carmakerStore.lastCommandResult || 'Command result will appear here.'}</pre>
    </article>

    <article class="panel panel-wide">
      <div class="panel-head">
        <h2>Watched Objects</h2>
        <div class="inline-actions">
          <button class="btn ghost" onclick={clearWatchedObjects} disabled={carmakerStore.busy}>Clear</button>
          <button class="btn ghost" onclick={refreshWatchedObjects} disabled={carmakerStore.busy}>Refresh</button>
        </div>
      </div>
      <div class="form-row">
        <label>
          Index
          <input bind:value={watchedInput} inputmode="numeric" />
        </label>
        <div class="button-stack">
          <button class="btn" onclick={addWatchedObject} disabled={carmakerStore.busy}>Add</button>
        </div>
      </div>
      <div class="chip-row">
        {#if carmakerStore.watchedTrafficObjects.length === 0}
          <span class="muted">No watched traffic objects.</span>
        {:else}
          {#each carmakerStore.watchedTrafficObjects as index}
            <button class="chip" onclick={() => removeWatchedObject(index)}>
              T{String(index).padStart(2, '0')} x
            </button>
          {/each}
        {/if}
      </div>
    </article>

    <article class="panel panel-wide">
      <div class="panel-head">
        <h2>Telemetry</h2>
        <div class="inline-actions">
          <button class="btn ghost" onclick={() => carmakerStore.refreshTelemetry()} disabled={carmakerStore.busy}>
            Refresh
          </button>
        </div>
      </div>
      {#if carmakerStore.telemetryError}
        <p class="error-text">{carmakerStore.telemetryError}</p>
      {/if}
      <div class="kv compact">
        <div>
          <dt>Car.v</dt>
          <dd>{carmakerStore.telemetry?.carV ?? 'n/a'}</dd>
        </div>
        <div>
          <dt>DM.Gas</dt>
          <dd>{carmakerStore.telemetry?.dmGas ?? 'n/a'}</dd>
        </div>
        <div>
          <dt>DM.Brake</dt>
          <dd>{carmakerStore.telemetry?.dmBrake ?? 'n/a'}</dd>
        </div>
        <div>
          <dt>Traffic.nObjs</dt>
          <dd>{carmakerStore.telemetry?.trafficNObjs ?? 'n/a'}</dd>
        </div>
      </div>
      <pre class="output">{safeTelemetryText()}</pre>
    </article>

    <article class="panel panel-wide">
      <div class="panel-head">
        <h2>Store Log</h2>
        <button class="btn ghost" onclick={() => carmakerStore.clearLogs()} disabled={carmakerStore.busy}>Clear</button>
      </div>
      <ul class="log">
        {#if carmakerStore.logMessages.length === 0}
          <li>No log messages yet.</li>
        {:else}
          {#each carmakerStore.logMessages as message}
            <li>{message}</li>
          {/each}
        {/if}
      </ul>
    </article>
  </section>
</main>
