<script>
	import { invoke } from '@tauri-apps/api/core';
	import Icon from '@iconify/svelte';

	// State
	let query = $state('');
	let topK = $state(5);
	let results = $state([]);
	let loading = $state(false);
	let error = $state(null);

	// Search maps using RAG
	async function handleSearch() {
		if (!query.trim()) {
			error = '검색어를 입력하세요.';
			return;
		}

		try {
			loading = true;
			error = null;
			results = [];

			console.log('🔍 Searching maps with query:', query);
			const searchResults = await invoke('search_similar_maps', {
				query: query.trim(),
				topK: topK
			});

			results = searchResults;
			console.log('✅ Found results:', results.length);
		} catch (e) {
			console.error('❌ Failed to search maps:', e);
			error = e;
		} finally {
			loading = false;
		}
	}

	// Handle Enter key
	function handleKeyPress(event) {
		if (event.key === 'Enter' && !loading) {
			handleSearch();
		}
	}
</script>

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>RAG 테스트</h1>
			<p class="subtitle">자연어 검색으로 유사한 맵을 찾습니다.</p>
		</div>
	</div>

	<!-- Search Input -->
	<div class="search-section">
		<div class="search-input-group">
			<Icon icon="solar:magnifer-bold-duotone" width="24" height="24" />
			<input
				type="text"
				bind:value={query}
				onkeypress={handleKeyPress}
				placeholder="예: 교차로가 있는 복잡한 도로"
				class="search-input"
				disabled={loading}
			/>
			<button class="btn-primary" onclick={handleSearch} disabled={loading || !query.trim()}>
				{#if loading}
					<Icon icon="solar:refresh-bold" width="20" height="20" class="spin" />
					검색 중...
				{:else}
					<Icon icon="solar:magnifer-bold" width="20" height="20" />
					검색
				{/if}
			</button>
		</div>

		<div class="search-options">
			<label>
				<span>상위 결과 개수:</span>
				<input
					type="number"
					bind:value={topK}
					min="1"
					max="20"
					class="number-input"
					disabled={loading}
				/>
			</label>
		</div>
	</div>

	<!-- Results Section -->
	<div class="results-section">
		{#if error}
			<div class="error-state">
				<Icon icon="solar:danger-triangle-bold" width="48" height="48" />
				<p>검색 실패: {error}</p>
			</div>
		{:else if loading}
			<div class="loading-state">
				<Icon icon="solar:refresh-bold" width="48" height="48" class="spin" />
				<p>검색 중...</p>
			</div>
		{:else if results.length === 0}
			<div class="empty-state">
				<Icon icon="solar:magnifer-zoom-in-bold-duotone" width="64" height="64" />
				<h3>검색 결과가 없습니다</h3>
				<p>검색어를 입력하고 검색 버튼을 눌러주세요.</p>
			</div>
		{:else}
			<div class="results-header">
				<h3>{results.length}개의 유사한 맵을 찾았습니다</h3>
			</div>

			<div class="results-list">
				{#each results as result, index (result.mapId)}
					<div class="result-card">
						<div class="result-rank">#{index + 1}</div>
						<div class="result-content">
							<div class="result-header">
								<h4>{result.mapName}</h4>
								<div class="result-badges">
									<span class="badge category">{result.category}</span>
									<span class="badge difficulty">{result.difficulty}</span>
								</div>
							</div>

							<p class="result-description">{result.description}</p>

							{#if result.tags && result.tags.length > 0}
								<div class="result-tags">
									{#each result.tags as tag}
										<span class="tag">{tag}</span>
									{/each}
								</div>
							{/if}

							<div class="result-footer">
								<div class="score-info">
									<Icon icon="solar:star-bold" width="16" height="16" />
									<span>유사도: {(result.similarityScore * 100).toFixed(1)}%</span>
								</div>
								<div class="distance-info">
									<Icon icon="solar:target-bold" width="16" height="16" />
									<span>거리: {result.distance.toFixed(4)}</span>
								</div>
								<div class="embedding-status">
									{#if result.isEmbedded}
										<Icon icon="solar:check-circle-bold" width="16" height="16" class="embedded" />
										<span class="embedded">임베딩 완료</span>
									{:else}
										<Icon icon="solar:close-circle-bold" width="16" height="16" class="not-embedded" />
										<span class="not-embedded">임베딩 대기</span>
									{/if}
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.page-container {
		max-width: 1200px;
		padding: 2rem;
	}

	.page-header {
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

	/* Search Section */
	.search-section {
		background: white;
		padding: 1.5rem;
		border-radius: 0.75rem;
		box-shadow: var(--shadow-sm);
		margin-bottom: 2rem;
	}

	.search-input-group {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1rem;
		color: var(--color-text-secondary);
	}

	.search-input {
		flex: 1;
		padding: 0.875rem 1.25rem;
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		font-size: 1rem;
		background: var(--color-background);
	}

	.search-input:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--focus-ring);
	}

	.search-input:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.search-options {
		display: flex;
		gap: 1rem;
	}

	.search-options label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		color: var(--color-text-secondary);
	}

	.number-input {
		width: 5rem;
		padding: 0.5rem;
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
		font-size: 0.875rem;
		text-align: center;
	}

	.number-input:focus {
		outline: none;
		border-color: var(--color-primary);
	}

	/* Results Section */
	.results-section {
		min-height: 400px;
	}

	.results-header {
		margin-bottom: 1.5rem;
	}

	.results-header h3 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.results-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.result-card {
		background: white;
		border-radius: 0.75rem;
		padding: 1.5rem;
		box-shadow: var(--shadow-sm);
		display: flex;
		gap: 1rem;
		transition: all 0.2s;
	}

	.result-card:hover {
		box-shadow: var(--shadow-md);
	}

	.result-rank {
		flex-shrink: 0;
		width: 2.5rem;
		height: 2.5rem;
		border-radius: 50%;
		background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		font-size: 0.875rem;
	}

	.result-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.result-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
	}

	.result-header h4 {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.result-badges {
		display: flex;
		gap: 0.5rem;
	}

	.badge {
		padding: 0.25rem 0.75rem;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 600;
	}

	.badge.category {
		background: var(--color-primary-bg-light);
		color: var(--color-primary);
	}

	.badge.difficulty {
		background: var(--color-surface-hover);
		color: var(--color-text-secondary);
	}

	.result-description {
		margin: 0;
		color: var(--color-text-secondary);
		line-height: 1.6;
	}

	.result-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.tag {
		padding: 0.375rem 0.75rem;
		background: var(--color-background);
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
		font-size: 0.75rem;
		color: var(--color-text-secondary);
	}

	.result-footer {
		display: flex;
		gap: 1.5rem;
		align-items: center;
		padding-top: 0.75rem;
		border-top: 1px solid var(--color-border);
		font-size: 0.875rem;
	}

	.score-info,
	.distance-info,
	.embedding-status {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		color: var(--color-text-secondary);
	}

	.score-info :global(svg) {
		color: #f59e0b;
	}

	.distance-info :global(svg) {
		color: var(--color-primary);
	}

	.embedding-status :global(svg.embedded) {
		color: var(--color-success);
	}

	.embedding-status :global(svg.not-embedded) {
		color: var(--color-error);
	}

	.embedding-status .embedded {
		color: var(--color-success);
	}

	.embedding-status .not-embedded {
		color: var(--color-error);
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
		margin: 0;
		font-size: 1rem;
	}

	.empty-state :global(svg) {
		color: var(--color-text-muted);
	}
</style>
