<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';
	import { invoke } from '@tauri-apps/api/core';

	// State
	let templates = $state([]);
	let isLoading = $state(true);
	let editingTemplate = $state(null);
	let formData = $state({ name: '', content: '' });
	let showForm = $state(false);

	// API 호출
	async function loadTemplates() {
		isLoading = true;
		try {
			templates = await invoke('get_prompt_templates');
		} catch (error) {
			console.error('Failed to load templates:', error);
		} finally {
			isLoading = false;
		}
	}

	async function saveTemplate() {
		try {
			if (editingTemplate) {
				// 수정
				await invoke('update_prompt_template', {
					id: editingTemplate.id,
					templateData: formData
				});
			} else {
				// 생성
				await invoke('create_prompt_template', { templateData: formData });
			}
			await loadTemplates();
			resetForm();
		} catch (error) {
			console.error('Failed to save template:', error);
			await dialogStore.alert('저장 실패');
		}
	}

	async function deleteTemplate(id) {
		const confirmed = await dialogStore.confirm('정말 삭제하시겠습니까?');
		if (!confirmed) return;

		try {
			await invoke('delete_prompt_template', { id });
			await loadTemplates();
		} catch (error) {
			console.error('Failed to delete template:', error);
			await dialogStore.alert('삭제 실패');
		}
	}

	function startEdit(template) {
		editingTemplate = template;
		formData = { name: template.name, content: template.content };
		showForm = true;
	}

	function startCreate() {
		editingTemplate = null;
		formData = { name: '', content: '' };
		showForm = true;
	}

	function resetForm() {
		editingTemplate = null;
		formData = { name: '', content: '' };
		showForm = false;
	}

	onMount(() => {
		loadTemplates();
	});
</script>

<div class="page-container">
	<div class="page-header">
		<h1>시스템 메시지 템플릿</h1>
		<button class="btn-primary" onclick={startCreate}>
			<Icon icon="solar:add-circle-bold" width="20" height="20" />
			새 템플릿
		</button>
	</div>

	{#if isLoading}
		<div class="loading">로딩 중...</div>
	{:else if showForm}
		<!-- 폼 -->
		<div class="form-card">
			<div class="form-header">
				<h2>{editingTemplate ? '템플릿 수정' : '새 템플릿 생성'}</h2>
				<button class="btn-text" onclick={resetForm}>
					<Icon icon="solar:close-circle-bold" width="24" height="24" />
				</button>
			</div>

			<div class="form-body">
				<div class="form-group">
					<label for="name">템플릿 이름</label>
					<input
						type="text"
						id="name"
						bind:value={formData.name}
						placeholder="예: 자율주행 연구 시스템"
					/>
				</div>

				<div class="form-group">
					<label for="content">시스템 메시지</label>
					<textarea
						id="content"
						bind:value={formData.content}
						rows="20"
						placeholder="시스템 메시지를 입력하세요..."
					></textarea>
					<p class="hint">AI의 역할, 성격, 행동 방식을 정의하는 메시지입니다.</p>
				</div>

				<div class="form-actions">
					<button class="btn-secondary" onclick={resetForm}>취소</button>
					<button class="btn-primary" onclick={saveTemplate}>저장</button>
				</div>
			</div>
		</div>
	{:else}
		<!-- 목록 -->
		<div class="templates-grid">
			{#each templates as template}
				<div class="template-card">
					<div class="template-header">
						<h3>{template.name}</h3>
						<div class="template-actions">
							<button class="btn-icon" onclick={() => startEdit(template)}>
								<Icon icon="solar:pen-bold" width="20" height="20" />
							</button>
							<button class="btn-icon danger" onclick={() => deleteTemplate(template.id)}>
								<Icon icon="solar:trash-bin-trash-bold" width="20" height="20" />
							</button>
						</div>
					</div>
					<div class="template-content">
						{template.content.substring(0, 200)}...
					</div>
					<div class="template-footer">
						<span class="template-meta">
							생성: {new Date(template.created_at).toLocaleDateString('ko-KR')}
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
		color: var(--color-text-secondary);
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 1rem;
		margin-top: 2rem;
		padding-top: 1.5rem;
		border-top: 1px solid #e5e7eb;
	}

	.templates-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
		gap: 1.5rem;
	}

	.template-card {
		background: white;
		border-radius: 0.75rem;
		padding: 1.5rem;
		box-shadow: var(--shadow-sm);
		transition: transform 0.2s, box-shadow 0.2s;
	}

	.template-card:hover {
		transform: translateY(-2px);
		box-shadow: var(--shadow-md);
	}

	.template-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1rem;
	}

	.template-header h3 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #1f2937;
		flex: 1;
	}

	.template-actions {
		display: flex;
		gap: 0.25rem;
	}

	.template-content {
		color: var(--color-text-secondary);
		line-height: 1.6;
		margin-bottom: 1rem;
		font-size: 0.9rem;
		white-space: pre-wrap;
	}

	.template-footer {
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	.template-meta {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}
</style>
