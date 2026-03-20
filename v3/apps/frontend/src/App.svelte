<script>
  import SettingsView from './lib/views/SettingsView.svelte';
  import ManualControlView from './lib/views/ManualControlView.svelte';
  import VehicleControlView from './lib/views/VehicleControlView.svelte';

  let activeView = $state('vehicle-control');

  const views = [
    { id: 'vehicle-control', label: '차량 제어' },
    { id: 'manual-control', label: '메뉴얼 제어' },
    { id: 'settings', label: '자율주행 설정' },
  ];
</script>

<svelte:head>
  <title>AGI Voice V3 Autonomous Driving</title>
  <meta
    name="description"
    content="V3 autonomous driving frontend backed by the Python CarMaker API."
  />
</svelte:head>

<div class="shell app-shell">
  <header class="view-header card">
    <div>
      <p class="eyebrow">AGI Voice V3</p>
      <h1>Autonomous Driving</h1>
      <p class="page-description">V2 UI를 유지한 채 Python backend로 이식 중인 프런트 슬라이스입니다.</p>
    </div>
    <nav class="view-switcher" aria-label="V3 view switcher">
      {#each views as view}
        <button
          class:active={activeView === view.id}
          class="view-tab"
          onclick={() => {
            activeView = view.id;
          }}
        >
          {view.label}
        </button>
      {/each}
    </nav>
  </header>

  {#if activeView === 'vehicle-control'}
    <VehicleControlView />
  {:else if activeView === 'manual-control'}
    <ManualControlView />
  {:else if activeView === 'settings'}
    <SettingsView />
  {/if}
</div>
