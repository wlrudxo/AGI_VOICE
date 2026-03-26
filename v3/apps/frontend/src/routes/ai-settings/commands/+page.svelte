<script>
	import { onMount } from 'svelte';
	import { requestJson } from '$lib/backend';
	import Icon from '@iconify/svelte';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';

	let templates = $state([]);
	let isLoading = $state(false);
	let error = $state('');

	// 편집/생성 모달
	let showModal = $state(false);
	let editingTemplate = $state(null);
	let formData = $state({
		name: '',
		content: '',
		isActive: 1
	});

	// 명령어 템플릿 목록 조회
	async function loadTemplates() {
		isLoading = true;
		error = '';
		try {
			templates = await requestJson('/api/command-templates');
		} catch (err) {
			error = err.message;
		} finally {
			isLoading = false;
		}
	}

	// 새 템플릿 추가
	function openCreateModal() {
		editingTemplate = null;
		formData = {
			name: '',
			content: '',
			isActive: 1
		};
		showModal = true;
	}

	// 템플릿 수정
	function openEditModal(template) {
		editingTemplate = template;
		formData = {
			name: template.name,
			content: template.content,
			isActive: template.isActive
		};
		showModal = true;
	}

	// 모달 닫기
	function closeModal() {
		showModal = false;
		editingTemplate = null;
		formData = {
			name: '',
			content: '',
			isActive: 1
		};
	}

	// 템플릿 저장 (생성 또는 수정)
	async function saveTemplate() {
		if (!formData.name.trim() || !formData.content.trim()) {
			await dialogStore.alert('이름과 내용을 입력해주세요.');
			return;
		}

		try {
			if (editingTemplate) {
				await requestJson(`/api/command-templates/${editingTemplate.id}`, {
					method: 'PUT',
					body: formData
				});
			} else {
				await requestJson('/api/command-templates', { method: 'POST', body: formData });
			}

			await loadTemplates();
			closeModal();
		} catch (err) {
			await dialogStore.alert(`저장 실패: ${err.message}`);
		}
	}

	// 활성화/비활성화 토글
	async function toggleActive(template) {
		try {
			await requestJson(`/api/command-templates/${template.id}/toggle`, { method: 'POST' });
			await loadTemplates();
		} catch (err) {
			await dialogStore.alert(`토글 실패: ${err.message}`);
		}
	}

	// 템플릿 삭제
	async function deleteTemplate(id) {
		const confirmed = await dialogStore.confirm('정말 삭제하시겠습니까?');
		if (!confirmed) return;

		try {
			await requestJson(`/api/command-templates/${id}`, { method: 'DELETE' });
			await loadTemplates();
		} catch (err) {
			await dialogStore.alert(`삭제 실패: ${err.message}`);
		}
	}

	onMount(() => {
		loadTemplates();
	});
</script>

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>명령어 템플릿</h1>
			<p class="page-description">AI에게 전달할 명령어 정보를 관리합니다. 활성화된 템플릿만 전송됩니다.</p>
		</div>
		<button class="btn-primary" onclick={openCreateModal}>
			<Icon icon="solar:add-circle-bold-duotone" width="20" height="20" />
			<span>새 템플릿</span>
		</button>
	</div>

	{#if isLoading}
		<div class="loading-state">
			<Icon icon="solar:ufo-2-duotone" width="48" class="spin" />
			<p>로딩 중...</p>
		</div>
	{:else if error}
		<div class="alert-error">{error}</div>
	{:else if templates.length === 0}
		<div class="empty-state">
			<Icon icon="solar:document-bold-duotone" width="64" class="empty-state-icon" />
			<p>등록된 명령어 템플릿이 없습니다.</p>
			<button class="btn-secondary" onclick={openCreateModal}>템플릿 추가하기</button>
		</div>
	{:else}
		<div class="templates-list">
			{#each templates as template}
				<div class="template-card" class:inactive={template.isActive === 0}>
					<div class="template-header">
						<div class="template-title">
							<h3>{template.name}</h3>
							<span class="badge" class:badge-success={template.isActive === 1} class:badge-neutral={template.isActive === 0}>
								{template.isActive === 1 ? '활성화' : '비활성화'}
							</span>
						</div>
						<div class="template-actions">
							<button class="btn-icon" onclick={() => toggleActive(template)} title="활성화 토글">
								<Icon
									icon={template.isActive === 1
										? 'solar:eye-bold-duotone'
										: 'solar:eye-closed-bold-duotone'}
									width="20"
									height="20"
								/>
							</button>
							<button class="btn-icon" onclick={() => openEditModal(template)} title="수정">
								<Icon icon="solar:pen-bold-duotone" width="20" height="20" />
							</button>
							<button
								class="btn-icon danger"
								onclick={() => deleteTemplate(template.id)}
								title="삭제"
							>
								<Icon icon="solar:trash-bin-trash-bold-duotone" width="20" height="20" />
							</button>
						</div>
					</div>
					<div class="template-content">
						<pre>{template.content}</pre>
					</div>
					<div class="template-footer">
						<span class="date">생성: {new Date(template.created_at).toLocaleString('ko-KR')}</span>
						<span class="date">수정: {new Date(template.updated_at).toLocaleString('ko-KR')}</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- 모달 -->
{#if showModal}
	<div class="modal-overlay" onclick={closeModal}>
		<div class="modal-content" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>{editingTemplate ? '템플릿 수정' : '새 템플릿'}</h2>
				<button class="btn-text" onclick={closeModal}>
					<Icon icon="solar:close-circle-bold-duotone" width="24" height="24" />
				</button>
			</div>

			<div class="modal-body">
				<div class="form-group">
					<label for="name" class="form-label">템플릿 이름</label>
					<input
						type="text"
						id="name"
						bind:value={formData.name}
						placeholder="예: 식단 관리 명령어"
						class="input-field w-full"
					/>
				</div>

				<div class="form-group">
					<label for="content" class="form-label">명령어 내용</label>
					<textarea
						id="content"
						bind:value={formData.content}
						placeholder="AI에게 전달할 명령어 정보를 입력하세요..."
						rows="15"
						class="textarea-field w-full"
					></textarea>
				</div>

				<div class="form-group checkbox">
					<label>
						<input type="checkbox" checked={formData.isActive == 1} onchange={(e) => formData.isActive = e.target.checked ? 1 : 0} />
						<span>활성화</span>
					</label>
				</div>
			</div>

			<div class="modal-footer">
				<button class="btn-secondary" onclick={closeModal}>취소</button>
				<button class="btn-primary" onclick={saveTemplate}>저장</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.page-container {
		max-width: 1200px;
		margin: 0 auto;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 2rem;
	}

	.templates-list {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.template-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 0.75rem;
		padding: 1.5rem;
		transition: all 0.2s;
	}

	.template-card:hover {
		box-shadow: var(--shadow-md);
	}

	.template-card.inactive {
		opacity: 0.6;
		background: var(--color-surface-hover);
	}

	.template-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.template-title {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.template-title h3 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.template-actions {
		display: flex;
		gap: 0.5rem;
	}

	.template-content {
		margin-bottom: 1rem;
		background: var(--color-background);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
		padding: 1rem;
		max-height: 300px;
		overflow-y: auto;
	}

	.template-content pre {
		margin: 0;
		font-family: 'Courier New', monospace;
		font-size: 0.875rem;
		line-height: 1.6;
		white-space: pre-wrap;
		word-wrap: break-word;
		color: var(--color-text-secondary);
	}

	.template-footer {
		display: flex;
		gap: 1.5rem;
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	/* 모달 */
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: var(--overlay-medium);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}

	.modal-content {
		background: var(--color-surface);
		border-radius: 0.75rem;
		width: 90%;
		max-width: 800px;
		max-height: 90vh;
		display: flex;
		flex-direction: column;
		box-shadow: var(--shadow-xl);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid var(--color-border);
	}

	.modal-header h2 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.modal-body {
		padding: 1.5rem;
		overflow-y: auto;
	}

	.form-group.checkbox label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
	}

	.form-group.checkbox input[type='checkbox'] {
		width: 1.25rem;
		height: 1.25rem;
		cursor: pointer;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 1rem;
		padding: 1.5rem;
		border-top: 1px solid var(--color-border);
	}
</style>
