<script lang="ts">
  import { onMount } from 'svelte';
  import { weightStore } from '$lib/stores/weights.svelte';
  import { dialogStore } from '$lib/stores/dialogStore.svelte';
  import { invoke } from '@tauri-apps/api/core';

  let measuredDate = $state('');
  let weight = $state('');
  let note = $state('');
  let editingDate = $state<string | null>(null);
  let selectedDate = $state(new Date().toISOString().split('T')[0]);

  interface WeekWeight {
    id: number;
    measuredDate: string;
    weight: number;
    note: string | null;
  }

  let weekWeights = $state<WeekWeight[]>([]);

  onMount(() => {
    weightStore.fetchWeights(30); // Load last 30 days
    measuredDate = getTodayDate();
    fetchWeekWeights();
  });

  function getTodayDate() {
    return new Date().toISOString().split('T')[0];
  }

  async function fetchWeekWeights() {
    try {
      weekWeights = await invoke('get_weights', { days: 7 });
    } catch (err) {
      console.error('Failed to fetch week weights:', err);
    }
  }

  // Auto-fill form when date changes
  function handleDateChange() {
    const existing = weightStore.weights.find(w => w.measuredDate === measuredDate);
    if (existing) {
      // Auto-switch to edit mode
      editingDate = existing.measuredDate;
      weight = existing.weight.toString();
      note = existing.note || '';
    } else {
      // Switch to create mode
      if (editingDate === measuredDate) {
        editingDate = null;
        weight = '';
        note = '';
      }
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();

    if (!measuredDate || !weight) {
      await dialogStore.alert('날짜와 체중을 입력해주세요');
      return;
    }

    try {
      // Check if this date already exists
      const existing = weightStore.weights.find(w => w.measuredDate === measuredDate);

      if (existing) {
        // Update existing
        await weightStore.updateWeightByDate(measuredDate, {
          measuredDate: measuredDate,
          weight: parseFloat(weight),
          note: note || null
        });
      } else {
        // Create new
        await weightStore.createWeight({
          measuredDate: measuredDate,
          weight: parseFloat(weight),
          note: note || null
        });
      }

      // Reset form
      editingDate = null;
      measuredDate = getTodayDate();
      weight = '';
      note = '';

      // Refresh week weights
      fetchWeekWeights();
    } catch (error) {
      await dialogStore.alert(error instanceof Error ? error.message : 'Failed to save weight');
    }
  }

  function handleEdit(w: typeof weightStore.weights[0]) {
    editingDate = w.measuredDate;
    measuredDate = w.measuredDate;
    weight = w.weight.toString();
    note = w.note || '';
  }

  function handleCancelEdit() {
    editingDate = null;
    measuredDate = getTodayDate();
    weight = '';
    note = '';
  }

  async function handleDelete(date: string) {
    const confirmed = await dialogStore.confirm(`${date} 체중 기록을 삭제하시겠습니까?`);
    if (!confirmed) return;

    try {
      await weightStore.deleteWeightByDate(date);
      fetchWeekWeights();
    } catch (error) {
      await dialogStore.alert(error instanceof Error ? error.message : 'Failed to delete weight');
    }
  }

  // 날짜를 MM/DD 형식으로 변환
  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  }
</script>

<div class="max-w-7xl mx-auto">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-primary">
      ⚖️ 체중 관리
    </h1>
  </div>

  {#if weightStore.error}
    <div class="rounded-lg p-4 mb-6 bg-error" style="color: white;">
      <p>{weightStore.error}</p>
    </div>
  {/if}

  <!-- Weekly Weight Trend -->
  {#if weekWeights.length > 0}
    <div class="card rounded-lg p-6 shadow-md mb-6">
      <h2 class="text-xl font-bold mb-4 text-primary">주간 체중 추이 (최근 7일)</h2>
      <div class="grid grid-cols-7 gap-2">
        {#each weekWeights as w}
          <div class="rounded-lg p-3 text-center" style="background-color: var(--color-background); border: 1px solid var(--color-border);">
            <div class="text-xs font-medium mb-1 text-secondary">
              {formatDate(w.measuredDate)}
            </div>
            <div class="text-lg font-bold text-accent">
              {w.weight} kg
            </div>
            {#if w.note}
              <div class="text-xs mt-1 truncate text-muted">
                {w.note}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Input Form -->
    <div class="lg:col-span-1">
      <div class="card rounded-lg p-6 shadow-md">
        <h2 class="text-xl font-bold mb-4 text-primary">
          {editingDate ? '체중 수정' : '체중 기록'}
        </h2>

        <form onsubmit={handleSubmit} class="space-y-4">
          <!-- Date -->
          <div>
            <label for="date" class="block text-sm font-medium mb-1 text-secondary">
              날짜
            </label>
            <input
              id="date"
              type="date"
              bind:value={measuredDate}
              onchange={handleDateChange}
              class="w-full px-4 py-2 rounded-lg border border-default"
              required
            />
          </div>

          <!-- Weight -->
          <div>
            <label for="weight" class="block text-sm font-medium mb-1 text-secondary">
              체중 (kg)
            </label>
            <input
              id="weight"
              type="number"
              step="0.1"
              bind:value={weight}
              placeholder="75.5"
              class="w-full px-4 py-2 rounded-lg border border-default"
              required
            />
          </div>

          <!-- Note -->
          <div>
            <label for="note" class="block text-sm font-medium mb-1 text-secondary">
              메모 (선택)
            </label>
            <input
              id="note"
              type="text"
              bind:value={note}
              placeholder="아침 체중"
              class="w-full px-4 py-2 rounded-lg border border-default"
            />
          </div>

          <div class="flex gap-2">
            <button
              type="submit"
              class="btn-primary"
              disabled={weightStore.loading}
            >
              {weightStore.loading ? '저장 중...' : editingDate ? '수정' : '추가'}
            </button>

            {#if editingDate}
              <button
                type="button"
                onclick={handleCancelEdit}
                class="btn-secondary"
              >
                취소
              </button>
            {/if}
          </div>
        </form>
      </div>
    </div>

    <!-- Weight List -->
    <div class="lg:col-span-2">
      <div class="card rounded-lg p-6 shadow-md">
        <h2 class="text-xl font-bold mb-4 text-primary">체중 기록</h2>

        {#if weightStore.loading && weightStore.weights.length === 0}
          <p class="text-center py-8 text-muted">데이터 로딩 중...</p>
        {:else if weightStore.weights.length === 0}
          <p class="text-center py-8 text-muted">아직 기록이 없습니다. 첫 체중을 기록해보세요!</p>
        {:else}
          <div class="space-y-3">
            {#each weightStore.weights as w (w.id)}
              <div class="p-4 rounded-lg" style="background-color: var(--color-background); border: 1px solid var(--color-border);">
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="flex items-center gap-4">
                      <span class="text-lg font-semibold text-primary">{w.measuredDate}</span>
                      <span class="text-2xl font-bold text-accent">{w.weight} kg</span>
                    </div>
                    {#if w.note}
                      <p class="text-sm mt-1 text-secondary">{w.note}</p>
                    {/if}
                  </div>

                  <div class="flex gap-2">
                    <button
                      onclick={() => handleEdit(w)}
                      class="btn-secondary"
                    >
                      수정
                    </button>
                    <button
                      onclick={() => handleDelete(w.measuredDate)}
                      class="btn-danger"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
