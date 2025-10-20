<script lang="ts">
  import { onMount } from 'svelte';
  import { dialogStore } from '$lib/stores/dialogStore.svelte';
  import { invoke } from '@tauri-apps/api/core';

  interface Exercise {
    id: number;
    exerciseDate: string;
    exerciseName: string;
    duration: number;
    calories: number | null;
    category: string | null;
  }

  interface ExerciseStats {
    totalDuration: number;
    totalCalories: number;
  }

  let exercises = $state<Exercise[]>([]);
  let stats = $state<ExerciseStats | null>(null);
  let loading = $state(true);
  let selectedDate = $state(new Date().toISOString().split('T')[0]);

  // Form state
  let formData = $state({
    exerciseDate: new Date().toISOString().split('T')[0],  // 직접 계산 (selectedDate는 $effect에서 동기화)
    exerciseName: '',
    duration: null as number | null,
    calories: null as number | null,
    category: ''
  });
  let submitting = $state(false);

  async function fetchExercises() {
    try {
      loading = true;
      const [exercisesData, statsData] = await Promise.all([
        invoke('get_exercises', { exerciseDate: selectedDate }),
        invoke('get_exercise_stats', { targetDate: selectedDate })
      ]);

      exercises = exercisesData as Exercise[];
      stats = statsData as ExerciseStats;
    } catch (err) {
      console.error('Failed to fetch exercises:', err);
    } finally {
      loading = false;
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();

    if (!formData.exerciseName.trim()) {
      await dialogStore.alert('운동 이름을 입력해주세요.');
      return;
    }

    if (!formData.duration || formData.duration <= 0) {
      await dialogStore.alert('운동 시간을 입력해주세요.');
      return;
    }

    try {
      submitting = true;
      await invoke('create_exercise', {
        exercise: {
          exerciseDate: formData.exerciseDate,
          exerciseName: formData.exerciseName,
          duration: formData.duration,
          calories: formData.calories,
          category: formData.category || null
        }
      });

      // Reset form
      formData = {
        exerciseDate: selectedDate,
        exerciseName: '',
        duration: null,
        calories: null,
        category: ''
      };

      // Refresh exercises
      await fetchExercises();
    } catch (err) {
      console.error('Failed to create exercise:', err);
      await dialogStore.alert('운동 기록에 실패했습니다.');
    } finally {
      submitting = false;
    }
  }

  async function deleteExercise(id: number) {
    const confirmed = await dialogStore.confirm('이 운동 기록을 삭제하시겠습니까?');
    if (!confirmed) {
      return;
    }

    try {
      await invoke('delete_exercise', { id });

      // Refresh exercises
      await fetchExercises();
    } catch (err) {
      console.error('Failed to delete exercise:', err);
      await dialogStore.alert('운동 기록 삭제에 실패했습니다.');
    }
  }

  // Update form date when selectedDate changes
  $effect(() => {
    formData.exerciseDate = selectedDate;
  });

  onMount(() => {
    fetchExercises();
  });

  const categoryLabels: Record<string, string> = {
    '근력': '근력',
    '유산소': '유산소',
    '이두': '이두',
    '삼두': '삼두',
    '가슴': '가슴',
    '등': '등',
    '어깨': '어깨',
    '하체': '하체',
    '복근': '복근',
    '스트레칭': '스트레칭',
    '기타': '기타'
  };
</script>

<div class="max-w-7xl mx-auto">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-primary">
      💪 운동 관리
    </h1>
    <input
      type="date"
      bind:value={selectedDate}
      onchange={() => fetchExercises()}
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
          <h2 class="text-xl font-bold mb-4 text-primary">운동 기록</h2>

          <form onsubmit={handleSubmit} class="space-y-4">
            <!-- Date -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                날짜 *
              </label>
              <input
                type="date"
                bind:value={formData.exerciseDate}
                class="w-full px-3 py-2 rounded-lg border border-default"
                required
              />
            </div>

            <!-- Exercise Name -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                운동 이름 *
              </label>
              <input
                type="text"
                bind:value={formData.exerciseName}
                placeholder="예: 벤치프레스"
                class="w-full px-3 py-2 rounded-lg border border-default"
                required
              />
            </div>

            <!-- Duration -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                운동 시간 (분) *
              </label>
              <input
                type="number"
                bind:value={formData.duration}
                placeholder="예: 45"
                class="w-full px-3 py-2 rounded-lg border border-default"
                min="1"
                required
              />
            </div>

            <!-- Calories -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                소모 칼로리 (kcal)
              </label>
              <input
                type="number"
                bind:value={formData.calories}
                placeholder="예: 300"
                class="w-full px-3 py-2 rounded-lg border border-default"
                min="0"
              />
            </div>

            <!-- Category -->
            <div>
              <label class="block text-sm font-medium mb-2 text-secondary">
                운동 카테고리
              </label>
              <select
                bind:value={formData.category}
                class="w-full px-3 py-2 rounded-lg border border-default"
              >
                <option value="">선택 안함</option>
                {#each Object.entries(categoryLabels) as [key, label]}
                  <option value={key}>{label}</option>
                {/each}
              </select>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              disabled={submitting}
              class="btn-primary w-full"
            >
              {submitting ? '기록 중...' : '운동 기록하기'}
            </button>
          </form>
        </div>
      </div>

      <!-- Exercise List & Stats -->
      <div class="lg:col-span-2">
        <!-- Exercise Stats -->
        {#if stats}
          <div class="card rounded-lg p-6 shadow-md mb-6">
            <h2 class="text-xl font-bold mb-4 text-primary">오늘의 운동</h2>
            <div class="grid grid-cols-2 gap-4">
              <div class="text-center">
                <p class="text-sm text-secondary">총 운동 시간</p>
                <p class="text-2xl font-bold mt-1 text-accent">
                  {stats.totalDuration} 분
                </p>
              </div>
              <div class="text-center">
                <p class="text-sm text-secondary">소모 칼로리</p>
                <p class="text-2xl font-bold mt-1 text-accent">
                  {stats.totalCalories} kcal
                </p>
              </div>
            </div>
          </div>
        {/if}

        <!-- Exercise List -->
        <div class="card rounded-lg p-6 shadow-md">
          <h2 class="text-xl font-bold mb-4 text-primary">운동 목록</h2>
          {#if exercises.length === 0}
            <p class="text-muted">이 날짜에 기록된 운동이 없습니다.</p>
          {:else}
            <div class="space-y-3">
              {#each exercises as exercise}
                <div class="p-4 rounded-lg" style="background-color: var(--color-background); border: 1px solid var(--color-border);">
                  <div class="flex justify-between items-start">
                    <div class="flex-1">
                      {#if exercise.category}
                        <span class="inline-block px-2 py-1 rounded text-xs font-medium mb-2 bg-primary" style="color: white;">
                          {exercise.category}
                        </span>
                      {/if}
                      <h3 class="font-bold text-primary">{exercise.exerciseName}</h3>
                      <div class="flex gap-3 mt-2 text-sm text-secondary">
                        <span>⏱️ {exercise.duration}분</span>
                        {#if exercise.calories}
                          <span>🔥 {exercise.calories} kcal</span>
                        {/if}
                      </div>
                    </div>
                    <button
                      onclick={() => deleteExercise(exercise.id)}
                      class="btn-danger ml-3 !px-3 !py-1 text-sm"
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
