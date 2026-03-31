<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';
	import HelpModal from '$lib/components/HelpModal.svelte';

	// State
	let finalMessage = $state('');
	let isSaving = $state(false);
	let lastSaved = $state(null);
	let showHelpModal = $state(false);

	// LocalStorage 키
	const STORAGE_KEY = 'agi_voice_final_message';

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
			<div class="title-row">
				<h1>최종 메시지</h1>
				<button class="btn-icon help-btn" onclick={() => (showHelpModal = true)}>
					<Icon icon="solar:question-circle-bold" width="20" height="20" />
				</button>
			</div>
			<p class="page-description">AI 응답 생성 전 마지막으로 체크할 사항을 입력하세요.</p>
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
				class="textarea-field w-full"
			></textarea>
		</div>

		{#if lastSaved}
			<div class="save-info">
				<Icon icon="solar:check-circle-bold-duotone" width="16" height="16" />
				마지막 저장: {lastSaved.toLocaleString('ko-KR')}
			</div>
		{/if}

	</div>
</div>

<!-- Help Modal -->
<HelpModal
	bind:visible={showHelpModal}
	title="최종 메시지 도움말"
	onClose={() => (showHelpModal = false)}
>
	<section class="help-section">
		<h4>📋 최종 메시지란?</h4>
		<p class="help-desc">
			AI가 응답을 생성하기 직전에 마지막으로 참고할 체크리스트입니다.
			응답의 품질, 형식, 톤 등을 검증하는 지침을 작성할 수 있습니다.
		</p>
	</section>

	<section class="help-section">
		<h4>💡 Tip: 최종 메시지 활용법</h4>

		<div class="command-example">
			<code>응답 형식 검증</code>
			<p>
				태그 형식, 날짜 형식, 데이터 구조 등이 올바른지 확인하도록 지시합니다.
				예: "Check if all required tags are properly formatted"
			</p>
		</div>

		<div class="command-example">
			<code>응답 톤 확인</code>
			<p>
				친근함, 격려, 전문성 등 응답의 톤이 적절한지 확인합니다.
				예: "Ensure the response is clear and professional"
			</p>
		</div>

		<div class="command-example">
			<code>데이터 유효성 검사</code>
			<p>
				자율주행 관련 기술 정보, 계산 결과 등의 정확성을 검증합니다.
				예: "Verify technical accuracy of autonomous driving concepts"
			</p>
		</div>

		<div class="command-example">
			<code>추가 지침</code>
			<p>
				참고 자료 제공, 예시 포함 등 추가적인 응답 개선 지침을 작성합니다.
				예: "Provide relevant references or examples when appropriate"
			</p>
		</div>
	</section>

	<section class="help-section">
		<h4>📝 기본 템플릿</h4>
		<p class="help-desc">초기화 버튼을 클릭하면 아래 기본 템플릿으로 복원됩니다.</p>

		<div class="example-box">
			<pre>{DEFAULT_TEMPLATE}</pre>
		</div>
	</section>

	<section class="help-section">
		<h4>🎯 사용 시나리오</h4>

		<div class="example-card">
			<h5>자율주행 연구 프로젝트</h5>
			<p>
				"- Verify all SUMO XML tags are properly closed<br/>
				- Ensure vehicle parameters are within realistic ranges<br/>
				- Include simulation time estimates when relevant<br/>
				- Provide references to SUMO documentation"
			</p>
		</div>

		<div class="example-card">
			<h5>일반 AI 채팅</h5>
			<p>
				"- Use a friendly and encouraging tone<br/>
				- Break down complex concepts into simple steps<br/>
				- Provide actionable examples<br/>
				- End with a positive note"
			</p>
		</div>
	</section>

	<section class="help-section">
		<h4>⚠️ 주의사항</h4>
		<ul class="help-list">
			<li>너무 복잡한 체크리스트는 응답 생성 시간을 증가시킬 수 있습니다.</li>
			<li>명확하고 구체적인 지침을 작성하세요.</li>
			<li>최종 메시지는 모든 대화에 적용됩니다.</li>
		</ul>
	</section>
</HelpModal>

<style>
	.page-container {
		max-width: 1200px;
		margin: 0 auto;
	}

	/* Title Row with Help Button */
	.title-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	/* help-btn 스타일은 app.css에 정의됨 */

	.example-card {
		background: var(--color-background);
		padding: 1rem;
		border-radius: 0.5rem;
		margin-top: 0.75rem;
	}

	.example-card h5 {
		margin: 0 0 0.5rem 0;
		font-size: 0.9rem;
		font-weight: 600;
		color: var(--color-primary);
	}

	.example-card p {
		margin: 0;
		color: var(--color-text-secondary);
		line-height: 1.8;
	}



	.header-actions {
		display: flex;
		gap: 1rem;
	}

	.content-card {
		background: var(--color-surface);
		border-radius: 0.75rem;
		padding: 2rem;
		box-shadow: var(--shadow-sm);
	}

	.textarea-wrapper {
		margin-bottom: 1rem;
	}

	.textarea-wrapper textarea {
		min-height: 300px;
	}

	.save-info {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: var(--color-success-bg-light);
		border: 1px solid var(--color-success);
		border-radius: 0.5rem;
		color: var(--color-success-text);
		font-size: 0.875rem;
		margin-bottom: 1.5rem;
	}

	.hint-box {
		display: flex;
		gap: 1rem;
		padding: 1.5rem;
		background: var(--color-info-bg-light);
		border: 1px solid var(--color-info);
		border-radius: 0.5rem;
		color: var(--color-info-text);
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
		background: var(--color-background);
		border: 1px solid var(--color-border);
		border-radius: 0.5rem;
	}

	.example-box h3 {
		margin: 0 0 1rem 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-primary);
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
