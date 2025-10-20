<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { dbWatcher } from '$lib/stores/dbWatcher.svelte';
  import { invoke } from '@tauri-apps/api/core';

  interface DashboardData {
    date: string;
    weight: { weight: number } | null;
    meals: {
      totalCalories: number;
      totalProtein: number;
      totalCarbs: number;
      totalFat: number;
    };
    exercises: {
      totalCalories: number;
      totalDuration: number;
    };
    currentMissions: any[];
  }

  interface WeekDayData {
    date: string;
    weight: number | null;
    meals: {
      items: string[];
      totalCalories: number;
      byType: Record<string, string[]>;
    };
    exercises: {
      items: string[];
      totalDuration: number;
    };
  }

  interface WeekData {
    startDate: string;
    endDate: string;
    days: number;
    dailyData: WeekDayData[];
  }

  let dashboardData = $state<DashboardData | null>(null);
  let weekData = $state<WeekData | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);

  // 새벽 4시 기점으로 오늘 날짜 계산
  function getEffectiveToday(): Date {
    const now = new Date();
    const hour = now.getHours();

    // 0시~4시 사이면 전날로 처리
    if (hour < 4) {
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      return yesterday;
    }

    return now;
  }

  async function fetchDashboard() {
    try {
      loading = true;
      const effectiveToday = getEffectiveToday();
      const todayStr = effectiveToday.toISOString().split('T')[0];

      const [todayData, weeklyData] = await Promise.all([
        invoke<DashboardData>('get_dashboard', { targetDate: todayStr }),
        invoke<WeekData>('get_weekly_dashboard', { days: 7 })
      ]);

      dashboardData = todayData;
      weekData = weeklyData;
      error = null;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error';
      console.error('Dashboard fetch error:', err);
    } finally {
      loading = false;
    }
  }

  // 날짜를 MM/DD 형식으로 변환
  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  }

  // 요일 변환
  function getWeekday(dateStr: string): string {
    const date = new Date(dateStr);
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    return weekdays[date.getDay()];
  }

  // 날짜와 요일을 한 줄로 포맷
  function formatDateWithWeekday(dateStr: string): string {
    const date = new Date(dateStr);
    const formatted = `${date.getMonth() + 1}/${date.getDate()}`;
    const weekday = getWeekday(dateStr);
    return `${formatted} (${weekday})`;
  }

  // meal_type을 한글로 변환
  const mealTypeLabels: Record<string, string> = {
    breakfast: '아침',
    lunch: '점심',
    dinner: '저녁',
    snack: '간식',
    supplement: '보충제'
  };

  // 식사 타입 순서 고정 (아침 → 점심 → 저녁 → 간식 → 보충제)
  const mealTypeOrder = ['breakfast', 'lunch', 'dinner', 'snack', 'supplement'];

  let unsubscribe: (() => void) | null = null;

  onMount(() => {
    fetchDashboard();

    // DB 변경 감지 시작
    dbWatcher.startWatching();

    // DB 변경 감지 시 자동 새로고침
    unsubscribe = dbWatcher.onChange(() => {
      console.log('🔄 Dashboard auto-refreshing due to DB change...');
      fetchDashboard();
    });
  });

  onDestroy(() => {
    if (unsubscribe) {
      unsubscribe();
    }
  });
</script>

<div class="max-w-7xl mx-auto">

  {#if loading}
    <div class="text-center py-12">
      <p class="text-muted">데이터 로딩 중...</p>
    </div>
  {:else if error}
    <div class="rounded-lg p-6 shadow-md bg-error text-white">
      <p>오류: {error}</p>
    </div>
  {:else if dashboardData}
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="card rounded-lg p-6 shadow-md">
        <div class="text-3xl mb-2">⚖️</div>
        <h3 class="text-sm font-medium text-secondary">현재 체중</h3>
        <p class="text-2xl font-bold mt-2 text-primary">
          {dashboardData.weight?.weight ?? '--'} kg
        </p>
      </div>

      <div class="card rounded-lg p-6 shadow-md">
        <div class="text-3xl mb-2">🍽️</div>
        <h3 class="text-sm font-medium text-secondary">오늘 섭취 칼로리</h3>
        <p class="text-2xl font-bold mt-2 text-primary">
          {dashboardData.meals.totalCalories} kcal
        </p>
      </div>

      <div class="card rounded-lg p-6 shadow-md">
        <div class="text-3xl mb-2">💪</div>
        <h3 class="text-sm font-medium text-secondary">오늘 소모 칼로리</h3>
        <p class="text-2xl font-bold mt-2 text-primary">
          {dashboardData.exercises.totalCalories} kcal
        </p>
      </div>

      <div class="card rounded-lg p-6 shadow-md">
        <div class="text-3xl mb-2">🎯</div>
        <h3 class="text-sm font-medium text-secondary">진행 중인 미션</h3>
        <p class="text-2xl font-bold mt-2 text-primary">
          {dashboardData.currentMissions.length}개
        </p>
      </div>
    </div>

    <!-- Current Missions -->
    {#if dashboardData.currentMissions.length > 0}
      <div class="mb-8">
        <h2 class="text-xl font-bold mb-4 text-primary">진행 중인 미션</h2>
        <div class="space-y-3">
          {#each dashboardData.currentMissions as mission}
            <div class="bg-surface rounded-lg p-4 shadow-md border-l-4 border-primary">
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-primary">{mission.missionTitle}</h3>
                {#if mission.deadline}
                  <p class="text-xs text-muted whitespace-nowrap ml-4">마감: {mission.deadline}</p>
                {/if}
              </div>
              {#if mission.description}
                <p class="text-sm text-secondary">{mission.description}</p>
              {/if}
              {#if mission.aiComment}
                <p class="text-sm mt-2 text-secondary">💙 {mission.aiComment}</p>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Weekly Meals -->
    {#if weekData}
      <div class="mb-8">
        <h2 class="text-xl font-bold mb-4 text-primary">🍽️ 주간 식단 (최근 7일)</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          {#each weekData.dailyData as day}
            <div class="card rounded-lg p-3 shadow-md flex flex-col">
              <div class="text-center mb-3">
                <div class="text-xs font-medium text-secondary">
                  {formatDateWithWeekday(day.date)}
                </div>
              </div>

              <div class="flex flex-col flex-grow">
                {#if day.meals.items.length > 0}
                  <div class="space-y-2 flex-grow">
                    {#each mealTypeOrder as mealType}
                      {#if day.meals.byType[mealType] && day.meals.byType[mealType].length > 0}
                        <div class="space-y-1">
                          <div class="text-xs font-semibold text-accent">
                            {mealTypeLabels[mealType] || mealType}
                          </div>
                          {#each day.meals.byType[mealType] as meal}
                            <div class="text-xs truncate pl-2 text-secondary">
                              • {meal}
                            </div>
                          {/each}
                        </div>
                      {/if}
                    {/each}
                  </div>
                  <div class="text-xs font-bold mt-auto pt-2 text-center text-primary">
                    {day.meals.totalCalories} kcal
                  </div>
                {:else}
                  <div class="text-xs text-center text-muted">기록 없음</div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>

      <!-- Weekly Exercises -->
      <div class="mb-8">
        <h2 class="text-xl font-bold mb-4 text-primary">💪 주간 운동 (최근 7일)</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          {#each weekData.dailyData as day}
            <div class="card rounded-lg p-3 shadow-md">
              <div class="text-center mb-3">
                <div class="text-xs font-medium text-secondary">
                  {formatDateWithWeekday(day.date)}
                </div>
              </div>

              <div>
                {#if day.exercises.items.length > 0}
                  <div class="space-y-1">
                    {#each day.exercises.items as exercise}
                      <div class="text-xs truncate text-secondary">
                        • {exercise}
                      </div>
                    {/each}
                  </div>
                  <div class="text-xs font-bold mt-2 text-center text-primary">
                    {day.exercises.totalDuration}분
                  </div>
                {:else}
                  <div class="text-xs text-center text-muted">기록 없음</div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>
