<script>
	import Icon from '@iconify/svelte';

	// Props
	let { map, onSelect = null, onEdit = null, onDelete = null, onEmbed = null } = $props();

	// Parse tags if JSON string
	let parsedTags = $derived.by(() => {
		if (!map.tags) return [];
		try {
			return JSON.parse(map.tags);
		} catch {
			return [];
		}
	});

	// Format date
	function formatDate(dateString) {
		const date = new Date(dateString);
		return date.toLocaleDateString('ko-KR', {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit'
		});
	}

	// Handle card click
	function handleClick() {
		if (onSelect) {
			onSelect(map);
		}
	}

	// Handle edit click
	function handleEdit(event) {
		event.stopPropagation();
		if (onEdit) {
			onEdit(map);
		}
	}

	// Handle delete click
	function handleDelete(event) {
		event.stopPropagation();
		if (onDelete) {
			onDelete(map);
		}
	}

	// Handle embed click
	function handleEmbed(event) {
		event.stopPropagation();
		if (onEmbed) {
			onEmbed(map);
		}
	}
</script>

<div class="map-card" onclick={handleClick} role="button" tabindex="0">
	<div class="card-header">
		<div class="card-title">
			<Icon icon="solar:map-point-bold-duotone" width="20" height="20" />
			<h3>{map.name}</h3>
		</div>
		{#if map.isEmbedded}
			<span class="badge embedded">
				<Icon icon="solar:database-bold-duotone" width="14" height="14" />
				임베딩 완료
			</span>
		{/if}
	</div>

	<p class="description">{map.description}</p>

	<div class="meta-row">
		<span class="meta-item">
			<Icon icon="solar:widget-5-bold" width="16" height="16" />
			{map.category}
		</span>
		<span class="meta-item">
			<Icon icon="solar:chart-bold" width="16" height="16" />
			{map.difficulty}
		</span>
	</div>

	{#if parsedTags.length > 0}
		<div class="tags">
			{#each parsedTags as tag}
				<span class="tag">{tag}</span>
			{/each}
		</div>
	{/if}

	<div class="card-footer">
		<span class="date">{formatDate(map.createdAt)}</span>
		<div class="action-buttons">
			{#if !map.isEmbedded && onEmbed}
				<button class="embed-btn" onclick={handleEmbed} title="임베딩 생성">
					<Icon icon="solar:database-bold" width="18" height="18" />
				</button>
			{/if}
			<button class="edit-btn" onclick={handleEdit} title="수정">
				<Icon icon="solar:pen-bold" width="18" height="18" />
			</button>
			<button class="delete-btn" onclick={handleDelete} title="삭제">
				<Icon icon="solar:trash-bin-trash-bold" width="18" height="18" />
			</button>
		</div>
	</div>
</div>

<style>
	.map-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 0.75rem;
		padding: 1.25rem;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: var(--shadow-sm);
	}

	.map-card:hover {
		border-color: var(--color-primary);
		box-shadow: var(--shadow-md);
		transform: translateY(-2px);
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 0.75rem;
	}

	.card-title {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.card-title h3 {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.badge.embedded {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.25rem 0.5rem;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		background: var(--color-success-bg-light);
		color: var(--color-success);
	}

	.description {
		margin: 0 0 0.75rem 0;
		font-size: 0.875rem;
		color: var(--color-text-secondary);
		line-height: 1.5;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.meta-row {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 0.75rem;
	}

	.meta-item {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.8rem;
		color: var(--color-text-muted);
	}

	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
		margin-bottom: 0.75rem;
	}

	.tag {
		padding: 0.25rem 0.5rem;
		background: var(--color-background);
		border: 1px solid var(--color-border);
		border-radius: 0.375rem;
		font-size: 0.75rem;
		color: var(--color-text-secondary);
	}

	.card-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 0.75rem;
		border-top: 1px solid var(--color-border);
	}

	.date {
		font-size: 0.8rem;
		color: var(--color-text-muted);
	}

	.action-buttons {
		display: flex;
		gap: 0.5rem;
	}

	.embed-btn {
		padding: 0.375rem;
		background: transparent;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		color: var(--color-text-muted);
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.embed-btn:hover {
		background: var(--color-success-bg-light);
		color: var(--color-success);
	}

	.edit-btn,
	.delete-btn {
		padding: 0.375rem;
		background: transparent;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		color: var(--color-text-muted);
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.edit-btn:hover {
		background: var(--color-primary-bg-light);
		color: var(--color-primary);
	}

	.delete-btn:hover {
		background: var(--color-error-bg-light);
		color: var(--color-error);
	}
</style>
