<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';

	// State
	let finalMessage = $state('');
	let isSaving = $state(false);
	let lastSaved = $state(null);

	// LocalStorage 키
	const STORAGE_KEY = 'ai_diet_final_message';

	// 기본 템플릿
	const DEFAULT_TEMPLATE = `## Final Checkout

- Check if all required tags are properly formatted
- Ensure the response is clear and professional
- Verify technical accuracy of autonomous driving concepts
- Provide relevant references or examples when appropriate`;

	function loadFinalMessage() {
		const saved = localStorage.getItem(STORAGE_KEY);
		if (saved) {
			finalMessage = saved;
			lastSaved = new Date();
		} else {
			finalMessage = DEFAULT_TEMPLATE;
		}
	}

	async function saveFinalMessage() {
		isSaving = true;
		try {
			localStorage.setItem(STORAGE_KEY, finalMessage);
			lastSaved = new Date();
			setTimeout(() => {
				isSaving = false;
			}, 500);
		} catch (error) {
			console.error('Failed to save final message:', error);
			await dialogStore.alert('저장 실패');
			isSaving = false;
		}
	}

	async function resetToDefault() {
		const confirmed = await dialogStore.confirm('기본 템플릿으로 초기화하시겠습니까?');
		if (confirmed) {
			finalMessage = DEFAULT_TEMPLATE;
		}
	}

	onMount(() => {
		loadFinalMessage();
	});
</script>

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>최종 메시지</h1>
			<p class="subtitle">AI 응답 생성 전 마지막으로 체크할 사항을 입력하세요.</p>
		</div>
		<div class="header-actions">
			<button class="btn-secondary" onclick={resetToDefault}>
				<Icon icon="solar:refresh-bold" width="20" height="20" />
				초기화
			</button>
			<button class="btn-primary" onclick={saveFinalMessage} disabled={isSaving}>
				<Icon icon="solar:diskette-bold" width="20" height="20" />
				{isSaving ? '저장 중...' : '저장'}
			</button>
		</div>
	</div>

	<div class="content-card">
		<div class="textarea-wrapper">
			<textarea
				bind:value={finalMessage}
				placeholder="최종 체크 사항을 입력하세요..."
			></textarea>
		</div>

		{#if lastSaved}
			<div class="save-info">
				<Icon icon="solar:check-circle-bold-duotone" width="16" height="16" />
				마지막 저장: {lastSaved.toLocaleString('ko-KR')}
			</div>
		{/if}

		<div class="hint-box">
			<Icon icon="solar:lightbulb-bolt-bold-duotone" width="20" height="20" />
			<div>
				<strong>💡 Tip:</strong> 최종 메시지는 AI가 응답을 생성하기 전에 마지막으로 확인할 사항입니다.
				<ul>
					<li>응답 형식 검증 (태그, 날짜 형식 등)</li>
					<li>응답 톤 확인 (친근함, 격려 등)</li>
					<li>데이터 유효성 검사</li>
					<li>추가 지침 사항</li>
				</ul>
			</div>
		</div>

		<div class="example-box">
			<h3>기본 템플릿</h3>
			<pre>{DEFAULT_TEMPLATE}</pre>
		</div>
	</div>
</div>

<style>
	.page-container {
		max-width: 900px;
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
		color: #1f2937;
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

	.content-card {
		background: white;
		border-radius: 0.75rem;
		padding: 2rem;
		box-shadow: var(--shadow-sm);
	}

	.textarea-wrapper {
		margin-bottom: 1rem;
	}

	textarea {
		width: 100%;
		min-height: 300px;
		padding: 1rem;
		border: 1px solid #d1d5db;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-family: 'Consolas', 'Monaco', monospace;
		line-height: 1.6;
		resize: vertical;
	}

	textarea:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: var(--focus-ring);
	}

	.save-info {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: #f0fdf4;
		border: 1px solid #86efac;
		border-radius: 0.5rem;
		color: #166534;
		font-size: 0.875rem;
		margin-bottom: 1.5rem;
	}

	.hint-box {
		display: flex;
		gap: 1rem;
		padding: 1.5rem;
		background: #eff6ff;
		border: 1px solid #bfdbfe;
		border-radius: 0.5rem;
		color: #1e40af;
		margin-bottom: 1.5rem;
	}

	.hint-box strong {
		display: block;
		margin-bottom: 0.5rem;
	}

	.hint-box ul {
		margin: 0.5rem 0 0 0;
		padding-left: 1.5rem;
	}

	.hint-box li {
		margin: 0.25rem 0;
	}

	.example-box {
		padding: 1.5rem;
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 0.5rem;
	}

	.example-box h3 {
		margin: 0 0 1rem 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: #374151;
	}

	.example-box pre {
		margin: 0;
		font-family: 'Consolas', 'Monaco', monospace;
		font-size: 0.875rem;
		line-height: 1.6;
		color: var(--color-text-secondary);
		white-space: pre-wrap;
	}
</style>
