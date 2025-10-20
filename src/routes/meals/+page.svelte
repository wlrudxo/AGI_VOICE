<script lang="ts">
  import { onMount } from 'svelte';
  import { dialogStore } from '$lib/stores/dialogStore.svelte';
  import { invoke } from '@tauri-apps/api/core';

  interface Meal {
    id: number;
    mealDate: string;
    mealType: string;
    foodName: string;
    calories: number | null;
    protein: number | null;
    carbs: number | null;
    fat: number | null;
  }

  interface MealStats {
    totalCalories: number;
    totalProtein: number;
    totalCarbs: number;
    totalFat: number;
  }

  let meals = $state<Meal[]>([]);
  let stats = $state<MealStats | null>(null);
  let loading = $state(true);
  let selectedDate = $state(new Date().toISOString().split('T')[0]);

  // Form state
  let formData = $state({
    mealDate: new Date().toISOString().split('T')[0],  // 직접 계산 (selectedDate는 $effect에서 동기화)
    mealType: 'lunch',
    foodName: '',
    calories: null as number | null,
    protein: null as number | null,
    carbs: null as number | null,
    fat: null as number | null
  });
  let submitting = $state(false);

  async function fetchMeals() {
    try {
      loading = true;
      const [mealsData, statsData] = await Promise.all([
        invoke('get_meals', { mealDate: selectedDate }),
        invoke('get_meal_stats', { targetDate: selectedDate })
      ]);

      meals = mealsData as Meal[];
      stats = statsData as MealStats;
    } catch (err) {
      console.error('Failed to fetch meals:', err);
    } finally {
      loading = false;
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();

    if (!formData.foodName.trim()) {
      await dialogStore.alert('음식 이름을 입력해주세요.');
      return;
    }

    try {
      submitting = true;
      await invoke('create_meal', { meal: formData });

      // Reset form
      formData = {
        mealDate: selectedDate,
        mealType: 'lunch',
        foodName: '',
        calories: null,
        protein: null,
        carbs: null,
        fat: null
      };

      // Refresh meals
      await fetchMeals();
    } catch (err) {
      console.error('Failed to create meal:', err);
      await dialogStore.alert('식사 기록에 실패했습니다.');
    } finally {
      submitting = false;
    }
  }

  async function deleteMeal(id: number) {
    const confirmed = await dialogStore.confirm('이 식사 기록을 삭제하시겠습니까?');
    if (!confirmed) {
      return;
    }

    try {
      await invoke('delete_meal', { id });

      // Refresh meals
      await fetchMeals();
    } catch (err) {
      console.error('Failed to delete meal:', err);
      await dialogStore.alert('식사 기록 삭제에 실패했습니다.');
    }
  }

  // Update form date when selectedDate changes
  $effect(() => {
    formData.mealDate = selectedDate;
  });

  onMount(() => {
    fetchMeals();
  });

  const mealTypeLabels: Record<string, string> = {
    breakfast: '아침',
    lunch: '점심',
    dinner: '저녁',
    snack: '간식',
    supplement: '보충제'
  };
</script>

<div class="max-w-7xl mx-auto">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-primary">
      🍽️ 식단 관리
    </h1>
    <input
      type="date"
      bind:value={selectedDate}
      onchange={() => fetchMeals()}
      class="px-3 py-2 rounded-lg border border-default"
    />
  </div>

  {#if loading}
    <div class="text-center py-12">
      <p class="text-muted">데이터 로딩 중...</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Input Form -->
      <div class="lg:col-span-1">
        <div class="card rounded-lg p-6 shadow-md">
          <h2 class="text-xl font-bold mb-4 text-primary">식사 기록</h2>

          <form onsubmit={handleSubmit} class="space-y-4">
            <!-- Date -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                날짜 *
              </label>
              <input
                type="date"
                bind:value={formData.mealDate}
                class="w-full px-3 py-2 rounded-lg border border-default"
                required
              />
            </div>

            <!-- Meal Type -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                식사 종류
              </label>
              <select
                bind:value={formData.mealType}
                class="w-full px-3 py-2 rounded-lg border border-default"
              >
                <option value="breakfast">아침</option>
                <option value="lunch">점심</option>
                <option value="dinner">저녁</option>
                <option value="snack">간식</option>
                <option value="supplement">보충제</option>
              </select>
            </div>

            <!-- Food Name -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                음식 이름 *
              </label>
              <input
                type="text"
                bind:value={formData.foodName}
                placeholder="예: 닭가슴살 샐러드"
                class="w-full px-3 py-2 rounded-lg border border-default"
                required
              />
            </div>

            <!-- Calories -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                칼로리 (kcal)
              </label>
              <input
                type="number"
                bind:value={formData.calories}
                placeholder="예: 300"
                class="w-full px-3 py-2 rounded-lg border border-default"
                min="0"
              />
            </div>

            <!-- Protein -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                단백질 (g)
              </label>
              <input
                type="number"
                bind:value={formData.protein}
                placeholder="예: 30"
                class="w-full px-3 py-2 rounded-lg border border-default"
                min="0"
                step="0.1"
              />
            </div>

            <!-- Carbs -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                탄수화물 (g)
              </label>
              <input
                type="number"
                bind:value={formData.carbs}
                placeholder="예: 20"
                class="w-full px-3 py-2 rounded-lg border border-default"
                min="0"
                step="0.1"
              />
            </div>

            <!-- Fat -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                지방 (g)
              </label>
              <input
                type="number"
                bind:value={formData.fat}
                placeholder="예: 10"
                class="w-full px-3 py-2 rounded-lg border border-default"
                min="0"
                step="0.1"
              />
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              disabled={submitting}
              class="btn-primary w-full"
            >
              {submitting ? '기록 중...' : '식사 기록하기'}
            </button>
          </form>
        </div>
      </div>

      <!-- Meal List & Stats -->
      <div class="lg:col-span-2">
        <!-- Nutrition Stats -->
        {#if stats}
          <div class="card rounded-lg p-6 shadow-md mb-6">
            <h2 class="text-xl font-bold mb-4 text-primary">오늘의 영양소</h2>
            <div class="grid grid-cols-4 gap-4">
              <div class="text-center">
                <p class="text-sm text-secondary">칼로리</p>
                <p class="text-2xl font-bold mt-1 text-accent">
                  {stats.totalCalories} kcal
                </p>
              </div>
              <div class="text-center">
                <p class="text-sm text-secondary">단백질</p>
                <p class="text-2xl font-bold mt-1 text-accent">
                  {stats.totalProtein.toFixed(1)} g
                </p>
              </div>
              <div class="text-center">
                <p class="text-sm text-secondary">탄수화물</p>
                <p class="text-2xl font-bold mt-1 text-accent">
                  {stats.totalCarbs.toFixed(1)} g
                </p>
              </div>
              <div class="text-center">
                <p class="text-sm text-secondary">지방</p>
                <p class="text-2xl font-bold mt-1 text-accent">
                  {stats.totalFat.toFixed(1)} g
                </p>
              </div>
            </div>
          </div>
        {/if}

        <!-- Meal List -->
        <div class="card rounded-lg p-6 shadow-md">
          <h2 class="text-xl font-bold mb-4 text-primary">식사 목록</h2>
          {#if meals.length === 0}
            <p class="text-muted">이 날짜에 기록된 식사가 없습니다.</p>
          {:else}
            <div class="space-y-3">
              {#each meals as meal}
                <div class="p-4 rounded-lg" style="background-color: var(--color-background); border: 1px solid var(--color-border);">
                  <div class="flex justify-between items-start">
                    <div class="flex-1">
                      <span class="inline-block px-2 py-1 rounded text-xs font-medium mb-2 bg-primary" style="color: white;">
                        {mealTypeLabels[meal.mealType] || meal.mealType}
                      </span>
                      <h3 class="font-bold text-primary">{meal.foodName}</h3>
                      <div class="flex gap-3 mt-2 text-sm text-secondary">
                        {#if meal.calories}<span>🔥 {meal.calories} kcal</span>{/if}
                        {#if meal.protein}<span>🥩 단백질 {meal.protein}g</span>{/if}
                        {#if meal.carbs}<span>🍚 탄수 {meal.carbs}g</span>{/if}
                        {#if meal.fat}<span>🧈 지방 {meal.fat}g</span>{/if}
                      </div>
                    </div>
                    <button
                      onclick={() => deleteMeal(meal.id)}
                      class="btn-danger ml-3"
                      title="삭제"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>
