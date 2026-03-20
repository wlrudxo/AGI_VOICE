<script>
  import { onMount } from 'svelte';
  import { createCarMakerApi } from './lib/carmakerApi';
  import { resolveBackendConfig } from './lib/backend';

  const backendConfig = resolveBackendConfig();
  let api = createCarMakerApi(backendConfig.baseUrl);

  let backendSource = backendConfig.source;
  let backendUrl = backendConfig.baseUrl;
  let healthState = 'idle';
  let healthMessage = '';
  let connectionStatus = null;
  let monitoringActive = false;
  let connectHost = 'localhost';
  let connectPort = '16660';
  let commandInput = 'DVARead Car.v';
  let commandResult = '';
  let telemetry = null;
  let telemetryError = '';
  let watchedObjects = [];
  let watchedInput = '0';
  let busy = false;
  let logMessages = [];
  let telemetryTimer = null;

  function pushLog(message) {
    logMessages = [`${new Date().toLocaleTimeString()} ${message}`, ...logMessages].slice(0, 8);
  }

  function formatJson(value) {
    return JSON.stringify(value, null, 2);
  }

  function formatError(error) {
    return error instanceof Error ? error.message : String(error);
  }

  function safeTelemetryText() {
    return telemetry ? formatJson(telemetry.rawData ?? telemetry) : '{ }';
  }

  async function refreshHealth() {
    healthState = 'loading';
    healthMessage = '';

    try {
      const result = await api.health();
      healthState = result?.status ?? 'ok';
      healthMessage = result?.service ? `${result.service} ready` : 'ready';
    } catch (error) {
      healthState = 'error';
      healthMessage = formatError(error);
    }
  }

  async function refreshStatus() {
    try {
      connectionStatus = await api.getStatus();
    } catch (error) {
      connectionStatus = {
        connected: false,
        host: connectHost,
        port: Number(connectPort),
        lastError: formatError(error),
      };
    }
  }

  async function refreshMonitoring() {
    try {
      monitoringActive = await api.getMonitoring();
    } catch (error) {
      monitoringActive = false;
      pushLog(`monitoring error: ${formatError(error)}`);
    }
  }

  async function refreshWatchedObjects() {
    try {
      watchedObjects = await api.getWatchedObjects();
    } catch (error) {
      watchedObjects = [];
      pushLog(`watched objects error: ${formatError(error)}`);
    }
  }

  async function refreshTelemetry() {
    try {
      telemetryError = '';
      telemetry = await api.getTelemetry();
    } catch (error) {
      telemetryError = formatError(error);
    }
  }

  function stopTelemetryTimer() {
    if (telemetryTimer !== null) {
      clearInterval(telemetryTimer);
      telemetryTimer = null;
    }
  }

  function startTelemetryTimer() {
    stopTelemetryTimer();
    telemetryTimer = window.setInterval(() => {
      void refreshTelemetry();
    }, 1000);
  }

  async function initialize() {
    await Promise.all([
      refreshHealth(),
      refreshStatus(),
      refreshMonitoring(),
      refreshWatchedObjects(),
      refreshTelemetry(),
    ]);

    if (monitoringActive) {
      startTelemetryTimer();
    }
  }

  async function connect() {
    busy = true;
    try {
      const result = await api.connect(connectHost, connectPort);
      connectionStatus = result;
      pushLog(`connected to ${result.host}:${result.port}`);
      await refreshTelemetry();
    } catch (error) {
      pushLog(`connect failed: ${formatError(error)}`);
      await refreshStatus();
    } finally {
      busy = false;
    }
  }

  async function disconnect() {
    busy = true;
    try {
      connectionStatus = await api.disconnect();
      monitoringActive = false;
      stopTelemetryTimer();
      pushLog('disconnected');
    } catch (error) {
      pushLog(`disconnect failed: ${formatError(error)}`);
    } finally {
      busy = false;
      await refreshStatus();
    }
  }

  async function toggleMonitoring() {
    busy = true;
    try {
      monitoringActive = await api.setMonitoring(!monitoringActive);
      if (monitoringActive) {
        startTelemetryTimer();
        await refreshTelemetry();
      } else {
        stopTelemetryTimer();
      }
      pushLog(`monitoring ${monitoringActive ? 'enabled' : 'disabled'}`);
    } catch (error) {
      pushLog(`monitoring toggle failed: ${formatError(error)}`);
    } finally {
      busy = false;
    }
  }

  async function sendCommand() {
    busy = true;
    try {
      commandResult = String(await api.executeCommand(commandInput));
      pushLog(`command ok: ${commandInput}`);
      await Promise.all([refreshStatus(), refreshTelemetry()]);
    } catch (error) {
      commandResult = formatError(error);
      pushLog(`command failed: ${commandResult}`);
    } finally {
      busy = false;
    }
  }

  async function addWatchedObject() {
    busy = true;
    try {
      watchedObjects = await api.addWatchedObject(watchedInput);
      pushLog(`watched object added: ${watchedInput}`);
      await refreshTelemetry();
    } catch (error) {
      pushLog(`add watched object failed: ${formatError(error)}`);
    } finally {
      busy = false;
    }
  }

  async function removeWatchedObject(index) {
    busy = true;
    try {
      watchedObjects = await api.removeWatchedObject(index);
      pushLog(`watched object removed: ${index}`);
      await refreshTelemetry();
    } catch (error) {
      pushLog(`remove watched object failed: ${formatError(error)}`);
    } finally {
      busy = false;
    }
  }

  async function clearWatchedObjects() {
    busy = true;
    try {
      watchedObjects = await api.clearWatchedObjects();
      pushLog('watched objects cleared');
      await refreshTelemetry();
    } catch (error) {
      pushLog(`clear watched objects failed: ${formatError(error)}`);
    } finally {
      busy = false;
    }
  }

  onMount(() => {
    void initialize();

    return () => {
      stopTelemetryTimer();
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
        Placeholder UI with a real backend adapter. Use this to verify the Python CarMaker API
        before the full V2 UI is migrated.
      </p>
    </div>
    <div class="hero-badges">
      <span class="badge">Backend: {backendUrl}</span>
      <span class="badge">Source: {backendSource}</span>
      <span class:ok={healthState === 'ok'} class:error={healthState === 'error'} class="badge">
        Health: {healthState}
      </span>
    </div>
  </section>

  <section class="grid">
    <article class="panel">
      <div class="panel-head">
        <h2>Health</h2>
        <button class="btn ghost" on:click={refreshHealth} disabled={busy}>Refresh</button>
      </div>
      <p class="muted">{healthMessage || 'Waiting for backend response.'}</p>
      <dl class="kv">
        <div>
          <dt>Connected</dt>
          <dd>{connectionStatus?.connected ? 'yes' : 'no'}</dd>
        </div>
        <div>
          <dt>Host</dt>
          <dd>{connectionStatus?.host ?? connectHost}</dd>
        </div>
        <div>
          <dt>Port</dt>
          <dd>{connectionStatus?.port ?? connectPort}</dd>
        </div>
        <div>
          <dt>Last Error</dt>
          <dd>{connectionStatus?.lastError ?? 'none'}</dd>
        </div>
      </dl>
    </article>

    <article class="panel">
      <div class="panel-head">
        <h2>Connect</h2>
        <div class="inline-actions">
          <button class="btn" on:click={connect} disabled={busy}>Connect</button>
          <button class="btn ghost" on:click={disconnect} disabled={busy}>Disconnect</button>
        </div>
      </div>
      <div class="form-row">
        <label>
          Host
          <input bind:value={connectHost} />
        </label>
        <label>
          Port
          <input bind:value={connectPort} inputmode="numeric" />
        </label>
      </div>
      <div class="mini-actions">
        <button class="btn ghost" on:click={refreshStatus} disabled={busy}>Refresh status</button>
        <button class="btn ghost" on:click={refreshWatchedObjects} disabled={busy}>Load watched</button>
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <h2>Monitoring</h2>
        <button class="btn" on:click={toggleMonitoring} disabled={busy}>
          {monitoringActive ? 'Stop' : 'Start'}
        </button>
      </div>
      <p class="muted">
        In-memory compatibility flag, backed by the Python API. Telemetry refreshes every second
        while active.
      </p>
      <div class="status-line">
        <span class:ok={monitoringActive} class:warn={!monitoringActive} class="pill">
          {monitoringActive ? 'active' : 'idle'}
        </span>
      </div>
    </article>

    <article class="panel panel-wide">
      <div class="panel-head">
        <h2>Command</h2>
        <button class="btn" on:click={sendCommand} disabled={busy}>Run</button>
      </div>
      <input class="command" bind:value={commandInput} placeholder="DVARead Car.v" />
      <pre class="output">{commandResult || 'Command result will appear here.'}</pre>
    </article>

    <article class="panel panel-wide">
      <div class="panel-head">
        <h2>Watched Objects</h2>
        <div class="inline-actions">
          <button class="btn ghost" on:click={clearWatchedObjects} disabled={busy}>Clear</button>
          <button class="btn ghost" on:click={refreshWatchedObjects} disabled={busy}>Refresh</button>
        </div>
      </div>
      <div class="form-row">
        <label>
          Index
          <input bind:value={watchedInput} inputmode="numeric" />
        </label>
        <div class="button-stack">
          <button class="btn" on:click={addWatchedObject} disabled={busy}>Add</button>
        </div>
      </div>
      <div class="chip-row">
        {#if watchedObjects.length === 0}
          <span class="muted">No watched traffic objects.</span>
        {:else}
          {#each watchedObjects as index}
            <button class="chip" on:click={() => removeWatchedObject(index)} disabled={busy}>
              T{String(index).padStart(2, '0')}
            </button>
          {/each}
        {/if}
      </div>
    </article>

    <article class="panel panel-wide">
      <div class="panel-head">
        <h2>Telemetry</h2>
        <button class="btn ghost" on:click={refreshTelemetry} disabled={busy}>Refresh</button>
      </div>
      {#if telemetryError}
        <p class="error-text">{telemetryError}</p>
      {/if}
      <div class="kv compact">
        <div>
          <dt>Time</dt>
          <dd>{telemetry?.time ?? '—'}</dd>
        </div>
        <div>
          <dt>Car.v</dt>
          <dd>{telemetry?.carV ?? '—'}</dd>
        </div>
        <div>
          <dt>DM.Gas</dt>
          <dd>{telemetry?.dmGas ?? '—'}</dd>
        </div>
        <div>
          <dt>Traffic.nObjs</dt>
          <dd>{telemetry?.trafficNObjs ?? '—'}</dd>
        </div>
      </div>
      <pre class="output">{safeTelemetryText()}</pre>
    </article>

    <article class="panel">
      <div class="panel-head">
        <h2>Log</h2>
      </div>
      <ul class="log">
        {#each logMessages as item}
          <li>{item}</li>
        {/each}
      </ul>
    </article>
  </section>
</main>
