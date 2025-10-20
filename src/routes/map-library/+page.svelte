<script>
	import { onMount, onDestroy } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import Icon from '@iconify/svelte';
	import MapCard from '$lib/components/MapCard.svelte';
	import { dbWatcher } from '$lib/stores/dbWatcher.svelte';

	// State
	let maps = $state([]);
	let loading = $state(true);
	let error = $state(null);

	// Filter state
	let categoryFilter = $state('all');
	let embeddedFilter = $state('all');
	let searchQuery = $state('');

	// Filtered maps
	let filteredMaps = $derived.by(() => {
		let result = maps;

		// Category filter
		if (categoryFilter !== 'all') {
			result = result.filter(m => m.category === categoryFilter);
		}

		// Embedded filter
		if (embeddedFilter !== 'all') {
			const isEmbedded = embeddedFilter === 'embedded';
			result = result.filter(m => m.isEmbedded === (isEmbedded ? 1 : 0));
		}

		// Search filter
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			result = result.filter(m =>
				m.name.toLowerCase().includes(query) ||
				m.description.toLowerCase().includes(query)
			);
		}

		return result;
	});

	// Load maps from database
	async function loadMaps() {
		try {
			loading = true;
			error = null;

			const response = await invoke('get_maps', {
				query: null
			});

			maps = response;
			console.log('✅ Loaded maps:', maps.length);
		} catch (e) {
			console.error('❌ Failed to load maps:', e);
			error = e;
		} finally {
			loading = false;
		}
	}

	// Handle map selection
	function handleSelectMap(map) {
		console.log('Map selected:', map.id);
		// TODO: Navigate to map detail page or open edit modal
	}

	// Handle map deletion
	async function handleDeleteMap(map) {
		if (!confirm(`"${map.name}" 맵을 삭제하시겠습니까?`)) {
			return;
		}

		try {
			await invoke('delete_map', { id: map.id });
			console.log('✅ Map deleted:', map.id);
			await loadMaps(); // Reload after deletion
		} catch (e) {
			console.error('❌ Failed to delete map:', e);
			alert(`맵 삭제 실패: ${e}`);
		}
	}

	// Get unique categories
	let categories = $derived.by(() => {
		const cats = new Set(maps.map(m => m.category));
		return Array.from(cats).sort();
	});

	// Auto-refresh setup
	let unsubscribe = null;

	onMount(() => {
		loadMaps();
		dbWatcher.startWatching();
		unsubscribe = dbWatcher.onChange(() => {
			console.log('🔄 DB changed, reloading maps...');
			loadMaps();
		});
	});

	onDestroy(() => {
		if (unsubscribe) unsubscribe();
	});
</script>

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>Map 라이브러리</h1>
			<p class="subtitle">저장된 SUMO 맵을 조회하고 관리합니다.</p>
		</div>
		<div class="header-actions">
			<a href="/map-generator" class="btn-primary">
				<Icon icon="solar:add-circle-bold" width="20" height="20" />
				새 맵 생성
			</a>
		</div>
	</div>

	<!-- Filters -->
	<div class="filters-section">
		<div class="filter-group">
			<Icon icon="solar:magnifer-bold-duotone" width="20" height="20" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="맵 이름 또는 설명 검색..."
				class="search-input"
			/>
		</div>

		<div class="filter-group">
			<Icon icon="solar:widget-5-bold" width="20" height="20" />
			<select bind:value={categoryFilter} class="filter-select">
				<option value="all">모든 카테고리</option>
				{#each categories as category}
					<option value={category}>{category}</option>
				{/each}
			</select>
		</div>

		<div class="filter-group">
			<Icon icon="solar:database-bold-duotone" width="20" height="20" />
			<select bind:value={embeddedFilter} class="filter-select">
				<option value="all">모든 상태</option>
				<option value="embedded">임베딩 완료</option>
				<option value="not_embedded">임베딩 대기</option>
			</select>
		</div>

		<div class="stats-badge">
			<Icon icon="solar:map-point-bold" width="16" height="16" />
			<span>{filteredMaps.length}개 맵</span>
		</div>
	</div>

	<!-- Content -->
	<div class="content-section">
		{#if loading}
			<div class="loading-state">
				<Icon icon="solar:refresh-bold" width="48" height="48" class="spin" />
				<p>맵 로딩 중...</p>
			</div>
		{:else if error}
			<div class="error-state">
				<Icon icon="solar:danger-triangle-bold" width="48" height="48" />
				<p>맵 로딩 실패: {error}</p>
				<button class="btn-secondary" onclick={loadMaps}>
					<Icon icon="solar:refresh-bold" width="20" height="20" />
					다시 시도
				</button>
			</div>
		{:else if filteredMaps.length === 0}
			<div class="empty-state">
				<Icon icon="solar:map-point-bold-duotone" width="64" height="64" />
				<h3>맵이 없습니다</h3>
				<p>
					{searchQuery || categoryFilter !== 'all' || embeddedFilter !== 'all'
						? '검색 조건에 맞는 맵이 없습니다.'
						: '첫 번째 맵을 생성해보세요!'}
				</p>
				<a href="/map-generator" class="btn-primary">
					<Icon icon="solar:add-circle-bold" width="20" height="20" />
					맵 생성하기
				</a>
			</div>
		{:else}
			<div class="maps-grid">
				{#each filteredMaps as map (map.id)}
					<MapCard
						{map}
						onSelect={handleSelectMap}
						onDelete={handleDeleteMap}
					/>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.page-container {
		max-width: 1400px;
		padding: 2rem;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 2rem;
	}

	.page-header h1 {
		margin: 0;
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-text-primary);
	}

	.subtitle {
		margin: 0.5rem 0 0 0;
		color: var(--color-text-secondary);
		font-size: 1rem;
	}

	.header-actions {
		display: flex;
		gap: 1rem;
	}

	.filters-section {
		display: flex;
		gap: 1rem;
		margin-bottom: 2rem;
		flex-wrap: wrap;
		align-items: center;
		background: white;
		padding: 1.25rem;
		border-radius: 0.75rem;
		box-shadow: var(--shadow-sm);
	}

	.filter-group {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: var(--color-text-secondary);
	}

	.search-input {
		padding: 0.625rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		font-size: 0.9rem;
		min-width: 300px;
		background: var(--color-background);
	}

	.search-input:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--focus-ring);
	}

	.filter-select {
		padding: 0.625rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		font-size: 0.9rem;
		background: var(--color-background);
		cursor: pointer;
	}

	.filter-select:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--focus-ring);
	}

	.stats-badge {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.875rem;
		background: var(--color-primary-bg-light);
		color: var(--color-primary);
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		margin-left: auto;
	}

	.content-section {
		min-height: 400px;
	}

	.maps-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 1.5rem;
	}

	/* Loading state */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		color: var(--color-text-secondary);
	}

	.loading-state :global(.spin) {
		animation: spin 1s linear infinite;
		color: var(--color-primary);
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	.loading-state p {
		margin-top: 1rem;
		font-size: 1rem;
	}

	/* Error state */
	.error-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		color: var(--color-error);
	}

	.error-state p {
		margin: 1rem 0;
		font-size: 1rem;
	}

	/* Empty state */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		color: var(--color-text-secondary);
	}

	.empty-state h3 {
		margin: 1rem 0 0.5rem 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.empty-state p {
		margin-bottom: 1.5rem;
		font-size: 1rem;
	}

	.empty-state :global(svg) {
		color: var(--color-text-muted);
	}
</style>
