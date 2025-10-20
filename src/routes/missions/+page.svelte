<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';

  interface Mission {
    id: number;
    missionTitle: string;
    description: string | null;
    status: string;
    aiComment: string | null;
    completionComment: string | null;
    deadline: string | null;
    createdAt: string;
    completedAt: string | null;
  }

  interface MissionStats {
    total: number;
    completed: number;
    failed: number;
    inProgress: number;
    pending: number;
    achievementRate: number;
  }

  let missions = $state<Mission[]>([]);
  let stats = $state<MissionStats | null>(null);
  let loading = $state(true);
  let filter = $state<string>('all');

  async function fetchMissions() {
    try {
      loading = true;
      const [missionsList, missionStats] = await Promise.all([
        invoke<Mission[]>('get_missions', { status: undefined }),
        invoke<MissionStats>('get_mission_stats')
      ]);

      missions = missionsList;
      stats = missionStats;
    } catch (err) {
      console.error('Failed to fetch missions:', err);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchMissions();
  });

  const statusLabels: Record<string, string> = {
    pending: '대기 중',
    in_progress: '진행 중',
    completed: '완료',
    failed: '실패'
  };

  const statusColors: Record<string, string> = {
    pending: 'var(--color-text-muted)',
    in_progress: 'var(--color-primary)',
    completed: 'var(--color-success)',
    failed: 'var(--color-error)'
  };

  const filteredMissions = $derived(
    filter === 'all'
      ? missions
      : missions.filter(m => m.status === filter)
  );
</script>

<div class="max-w-7xl mx-auto">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-primary">
      🎯 AI 미션
    </h1>
  </div>

  {#if loading}
    <div class="text-center py-12">
      <p class="text-muted">데이터 로딩 중...</p>
    </div>
  {:else if stats}
    <!-- Mission Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="card rounded-lg p-4 shadow-md text-center">
        <p class="text-sm text-secondary">전체 미션</p>
        <p class="text-2xl font-bold mt-1 text-primary">{stats.total}</p>
      </div>
      <div class="card rounded-lg p-4 shadow-md text-center">
        <p class="text-sm text-secondary">진행 중</p>
        <p class="text-2xl font-bold mt-1 text-accent">{stats.inProgress}</p>
      </div>
      <div class="card rounded-lg p-4 shadow-md text-center">
        <p class="text-sm text-secondary">완료</p>
        <p class="text-2xl font-bold mt-1" style="color: var(--color-success);">{stats.completed}</p>
      </div>
      <div class="card rounded-lg p-4 shadow-md text-center">
        <p class="text-sm text-secondary">달성률</p>
        <p class="text-2xl font-bold mt-1 text-accent">{stats.achievementRate}%</p>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="flex gap-2 mb-6">
      <button
        onclick={() => filter = 'all'}
        class="{filter === 'all' ? 'btn-primary' : 'btn-secondary'}"
      >
        전체
      </button>
      <button
        onclick={() => filter = 'in_progress'}
        class="{filter === 'in_progress' ? 'btn-primary' : 'btn-secondary'}"
      >
        진행 중
      </button>
      <button
        onclick={() => filter = 'completed'}
        class="{filter === 'completed' ? 'btn-primary' : 'btn-secondary'}"
      >
        완료
      </button>
      <button
        onclick={() => filter = 'pending'}
        class="{filter === 'pending' ? 'btn-primary' : 'btn-secondary'}"
      >
        대기 중
      </button>
    </div>

    <!-- Missions List -->
    <div>
      <h2 class="text-xl font-bold mb-4 text-primary">
        미션 목록 ({filteredMissions.length}개)
      </h2>
      {#if filteredMissions.length === 0}
        <div class="card rounded-lg p-6 shadow-md">
          <p class="text-muted">해당하는 미션이 없습니다.</p>
        </div>
      {:else}
        <div class="space-y-4">
          {#each filteredMissions as mission}
            <div class="rounded-lg p-6 shadow-md bg-surface" style="border-left: 4px solid {statusColors[mission.status]};">
              <div class="flex justify-between items-start mb-3">
                <h3 class="text-xl font-bold text-primary">{mission.missionTitle}</h3>
                <span class="px-3 py-1 rounded-full text-sm font-medium" style="background-color: {statusColors[mission.status]}; color: white;">
                  {statusLabels[mission.status]}
                </span>
              </div>

              {#if mission.description}
                <p class="text-sm mb-2 text-secondary">{mission.description}</p>
              {/if}

              {#if mission.aiComment}
                <div class="p-3 rounded-lg mb-3" style="background-color: var(--color-primary-bg-light); border-left: 3px solid var(--color-primary);">
                  <p class="text-sm text-primary">💙 Aris: {mission.aiComment}</p>
                </div>
              {/if}

              {#if mission.completionComment}
                <div class="p-3 rounded-lg mb-3" style="background-color: var(--color-background);">
                  <p class="text-sm text-secondary">✨ 완료 평가: {mission.completionComment}</p>
                </div>
              {/if}

              <div class="flex gap-4 text-xs text-muted">
                {#if mission.deadline}
                  <span>📅 마감: {mission.deadline}</span>
                {/if}
                {#if mission.completedAt}
                  <span>✅ 완료: {new Date(mission.completedAt).toLocaleDateString()}</span>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
