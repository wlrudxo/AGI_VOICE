<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { invoke } from '@tauri-apps/api/core';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';

	// State
	let characters = $state([]);
	let isLoading = $state(true);
	let editingCharacter = $state(null);
	let formData = $state({ name: '', promptContent: '' });
	let showForm = $state(false);

	// API 호출
	async function loadCharacters() {
		isLoading = true;
		try {
			characters = await invoke('get_characters');
		} catch (error) {
			console.error('Failed to load characters:', error);
		} finally {
			isLoading = false;
		}
	}

	async function saveCharacter() {
		try {
			if (editingCharacter) {
				// 수정
				await invoke('update_character', {
					id: editingCharacter.id,
					character_data: formData
				});
			} else {
				// 생성
				await invoke('create_character', { character_data: formData });
			}
			await loadCharacters();
			resetForm();
		} catch (error) {
			console.error('Failed to save character:', error);
			await dialogStore.alert('저장 실패');
		}
	}

	async function deleteCharacter(id) {
		const confirmed = await dialogStore.confirm('정말 삭제하시겠습니까?');
		if (!confirmed) return;

		try {
			await invoke('delete_character', { id });
			await loadCharacters();
		} catch (error) {
			console.error('Failed to delete character:', error);
			await dialogStore.alert('삭제 실패');
		}
	}

	function startEdit(character) {
		editingCharacter = character;
		formData = { name: character.name, promptContent: character.promptContent };
		showForm = true;
	}

	function startCreate() {
		editingCharacter = null;
		formData = { name: '', promptContent: '' };
		showForm = true;
	}

	function resetForm() {
		editingCharacter = null;
		formData = { name: '', promptContent: '' };
		showForm = false;
	}

	onMount(() => {
		loadCharacters();
	});
</script>

<div class="page-container">
	<div class="page-header">
		<h1>캐릭터 관리</h1>
		<button class="btn-primary" onclick={startCreate}>
			<Icon icon="solar:add-circle-bold" width="20" height="20" />
			새 캐릭터
		</button>
	</div>

	{#if isLoading}
		<div class="loading">로딩 중...</div>
	{:else if showForm}
		<!-- 폼 -->
		<div class="form-card">
			<div class="form-header">
				<h2>{editingCharacter ? '캐릭터 수정' : '새 캐릭터 생성'}</h2>
				<button class="btn-text" onclick={resetForm}>
					<Icon icon="solar:close-circle-bold" width="24" height="24" />
				</button>
			</div>

			<div class="form-body">
				<div class="form-group">
					<label for="name">캐릭터 이름</label>
					<input
						type="text"
						id="name"
						bind:value={formData.name}
						placeholder="예: Aris (블루 아카이브)"
					/>
				</div>

				<div class="form-group">
					<label for="promptContent">캐릭터 프롬프트</label>
					<textarea
						id="promptContent"
						bind:value={formData.promptContent}
						rows="20"
						placeholder="캐릭터의 성격, 말투, 특징 등을 입력하세요..."
					></textarea>
					<p class="hint">캐릭터의 성격, 말투, 행동 패턴을 정의합니다.</p>
				</div>

				<div class="form-actions">
					<button class="btn-secondary" onclick={resetForm}>취소</button>
					<button class="btn-primary" onclick={saveCharacter}>저장</button>
				</div>
			</div>
		</div>
	{:else}
		<!-- 목록 -->
		<div class="characters-grid">
			{#each characters as character}
				<div class="character-card">
					<div class="character-header">
						<div class="character-avatar">
							<Icon icon="solar:user-bold-duotone" width="32" height="32" />
						</div>
						<div class="character-info">
							<h3>{character.name}</h3>
							<div class="character-actions">
								<button class="btn-icon" onclick={() => startEdit(character)}>
									<Icon icon="solar:pen-bold" width="20" height="20" />
								</button>
								<button class="btn-icon danger" onclick={() => deleteCharacter(character.id)}>
									<Icon icon="solar:trash-bin-trash-bold" width="20" height="20" />
								</button>
							</div>
						</div>
					</div>
					<div class="character-content">
						{character.promptContent.substring(0, 200)}...
					</div>
					<div class="character-footer">
						<span class="character-meta">
							생성: {new Date(character.created_at).toLocaleDateString('ko-KR')}
						</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.page-container {
		max-width: 1200px;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
	}

	.page-header h1 {
		margin: 0;
		font-size: 2rem;
		font-weight: 700;
		color: #1f2937;
	}

	.loading {
		text-align: center;
		padding: 3rem;
		color: var(--color-text-secondary);
	}

	.form-card {
		background: white;
		border-radius: 0.75rem;
		box-shadow: var(--shadow-sm);
	}

	.form-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.form-header h2 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: #1f2937;
	}

	.form-body {
		padding: 1.5rem;
	}

	.form-group {
		margin-bottom: 1.5rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #374151;
	}

	.form-group input,
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-family: inherit;
	}

	.form-group textarea {
		resize: vertical;
		font-family: 'Consolas', 'Monaco', monospace;
		line-height: 1.6;
	}

	.hint {
		margin-top: 0.5rem;
		font-size: 0.875rem;
		color: #6b7280;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 1rem;
		margin-top: 2rem;
		padding-top: 1.5rem;
		border-top: 1px solid #e5e7eb;
	}

	.characters-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
		gap: 1.5rem;
	}

	.character-card {
		background: white;
		border-radius: 0.75rem;
		padding: 1.5rem;
		box-shadow: var(--shadow-sm);
		transition: transform 0.2s, box-shadow 0.2s;
	}

	.character-card:hover {
		transform: translateY(-2px);
		box-shadow: var(--shadow-md);
	}

	.character-header {
		display: flex;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.character-avatar {
		width: 3rem;
		height: 3rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 0.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		flex-shrink: 0;
	}

	.character-info {
		flex: 1;
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.character-info h3 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #1f2937;
	}

	.character-actions {
		display: flex;
		gap: 0.25rem;
	}

	.character-content {
		color: var(--color-text-secondary);
		line-height: 1.6;
		margin-bottom: 1rem;
		font-size: 0.9rem;
		white-space: pre-wrap;
	}

	.character-footer {
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	.character-meta {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}
</style>
