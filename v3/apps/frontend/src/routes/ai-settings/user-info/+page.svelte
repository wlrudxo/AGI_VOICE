<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';
	import { promptContextStore } from '$lib/stores/promptContextStore';
	import HelpModal from '$lib/components/HelpModal.svelte';

	// State
	let userName = $state('');
	let userInfo = $state('');
	let isSaving = $state(false);
	let lastSaved = $state(null);
	let showHelpModal = $state(false);

	async function loadUserInfo() {
		const settings = await promptContextStore.loadSettings();
		userName = settings.userName;
		userInfo = settings.userInfo;
		if (settings.userName || settings.userInfo) {
			lastSaved = new Date();
		}
	}

	async function saveUserInfo() {
		isSaving = true;
		try {
			// Decision record:
			// V2는 localStorage를 직접 사용했지만, V3는 ChatView와 설정 페이지가 같은 값을 보도록
			// prompt context를 백엔드 단일 원본으로 이동했다.
			await promptContextStore.saveSettings({
				...promptContextStore.getCurrentState(),
				userName,
				userInfo,
			});
			lastSaved = new Date();
			setTimeout(() => {
				isSaving = false;
			}, 500);
		} catch (error) {
			console.error('Failed to save user info:', error);
			await dialogStore.alert('저장 실패');
			isSaving = false;
		}
	}

	onMount(() => {
		void loadUserInfo();
	});
</script>

<div class="page-container">
	<div class="page-header">
		<div>
			<div class="title-row">
				<h1>유저 정보</h1>
				<button class="btn-icon help-btn" onclick={() => (showHelpModal = true)}>
					<Icon icon="solar:question-circle-bold" width="20" height="20" />
				</button>
			</div>
			<p class="page-description">AI가 참고할 사용자 정보를 입력하세요.</p>
		</div>
		<button class="btn-primary" onclick={saveUserInfo} disabled={isSaving}>
			<Icon icon="solar:diskette-bold" width="20" height="20" />
			{isSaving ? '저장 중...' : '저장'}
		</button>
	</div>

	<div class="content-card">
		<!-- User Name Input -->
		<div class="input-section">
			<label for="userName" class="form-label">
				<Icon icon="solar:user-bold-duotone" width="20" height="20" />
				사용자 이름
			</label>
			<input
				id="userName"
				type="text"
				bind:value={userName}
				placeholder="예: 홍길동"
				class="input-field"
			/>
			<p class="input-hint">
				프롬프트에서 <code>&#123;&#123;user&#125;&#125;</code>로 사용됩니다.
			</p>
		</div>

		<!-- User Info Textarea -->
		<div class="textarea-wrapper">
			<label for="userInfo" class="form-label">
				<Icon icon="solar:document-text-bold-duotone" width="20" height="20" />
				사용자 정보
			</label>
			<textarea
				id="userInfo"
				bind:value={userInfo}
				placeholder="예:&#10;- 연구 분야: 자율주행 시스템 개발&#10;- 관심 주제: SLAM, 경로 계획, 센서 퓨전&#10;- 사용 센서: LiDAR, 카메라, IMU&#10;- 개발 환경: ROS2, Python, C++&#10;- 목표: 실시간 맵 생성 및 주행 판단 알고리즘 최적화&#10;&#10;자유롭게 작성하세요..."
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
	title="변수 치환 시스템 도움말"
	onClose={() => (showHelpModal = false)}
>
	<section class="help-section">
		<h4>🔄 변수 치환 시스템이란?</h4>
		<p class="help-desc">
			프롬프트에서 특정 변수를 사용하면 실제 대화 시 자동으로 실제 값으로 치환됩니다.
			이를 통해 동적이고 개인화된 AI 대화를 구성할 수 있습니다.
		</p>
	</section>

	<section class="help-section">
		<h4>📋 사용 가능한 변수</h4>

		<div class="command-example">
			<code>&#123;&#123;user&#125;&#125;</code>
			<p>
				사용자 이름으로 대체됩니다.
				예: "홍길동" 입력 시 → "Hello &#123;&#123;user&#125;&#125;!" → "Hello 홍길동!"
			</p>
		</div>

		<div class="command-example">
			<code>&#123;&#123;char&#125;&#125;</code>
			<p>
				선택된 캐릭터 이름으로 대체됩니다.
				예: "Research Assistant" 선택 시 → "Respond as &#123;&#123;char&#125;&#125;" → "Respond as Research Assistant"
			</p>
		</div>
	</section>

	<section class="help-section">
		<h4>💡 사용 예시</h4>

		<div class="example-card">
			<h5>시스템 메시지에서 사용</h5>
			<p>
				"You are in a text messaging conversation with <code>&#123;&#123;user&#125;&#125;</code>.
				Respond as <code>&#123;&#123;char&#125;&#125;</code> would, using a friendly and encouraging tone."
			</p>
		</div>

		<div class="example-card">
			<h5>실제 치환 결과</h5>
			<p>
				사용자: "홍길동", 캐릭터: "Research Assistant" 선택 시<br/>
				→ "You are in a text messaging conversation with <strong>홍길동</strong>.
				Respond as <strong>Research Assistant</strong> would, using a professional and friendly tone."
			</p>
		</div>
	</section>

	<section class="help-section">
		<h4>🎯 변수 사용 위치</h4>
		<ul class="help-list">
			<li><strong>시스템 메시지</strong>: AI의 역할과 행동 정의</li>
			<li><strong>캐릭터 프롬프트</strong>: 캐릭터 성격과 말투 정의</li>
			<li><strong>명령어 템플릿</strong>: 명령어 실행 시 참고 정보</li>
		</ul>
	</section>

	<section class="help-section">
		<h4>📝 사용자 정보 활용</h4>
		<p class="help-desc">
			<strong>사용자 정보</strong> 필드는 변수로 치환되지 않지만,
			프롬프트 시스템에 포함되어 AI가 사용자의 맥락을 이해하는 데 도움을 줍니다.
		</p>
		<ul class="help-list">
			<li>연구 분야, 관심사, 사용 환경 등을 입력</li>
			<li>AI가 더 맞춤화된 답변 제공</li>
			<li>대화 품질 향상</li>
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



	.content-card {
		background: var(--color-surface);
		border-radius: 0.75rem;
		padding: 2rem;
		box-shadow: var(--shadow-sm);
	}

	.input-section {
		margin-bottom: 2rem;
	}

	/* Labels use .form-label from app.css */

	.input-hint {
		margin: 0.5rem 0 0 0;
		font-size: 0.875rem;
		color: var(--color-text-secondary);
	}

	.input-hint code {
		background: var(--color-surface-hover);
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		font-family: 'Courier New', monospace;
		font-size: 0.85rem;
		color: var(--color-primary);
	}

	.textarea-wrapper {
		margin-bottom: 1rem;
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

	.hint-box p {
		margin: 0.5rem 0;
	}

	.hint-box code {
		background: var(--color-surface);
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		font-family: 'Courier New', monospace;
		font-size: 0.85rem;
		color: var(--color-info-text);
	}

	.hint-box .example {
		margin-top: 0.75rem;
		padding: 0.75rem;
		background: var(--overlay-white-medium);
		border-radius: 0.375rem;
		font-style: italic;
	}
</style>
