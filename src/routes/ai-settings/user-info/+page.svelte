<script>
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { dialogStore } from '$lib/stores/dialogStore.svelte';

	// State
	let userName = $state('');
	let userInfo = $state('');
	let isSaving = $state(false);
	let lastSaved = $state(null);

	// LocalStorage 키
	const USER_NAME_KEY = 'agi_voice_user_name';
	const USER_INFO_KEY = 'agi_voice_user_info';

	function loadUserInfo() {
		const savedName = localStorage.getItem(USER_NAME_KEY);
		const savedInfo = localStorage.getItem(USER_INFO_KEY);

		if (savedName) {
			userName = savedName;
		}
		if (savedInfo) {
			userInfo = savedInfo;
		}
		if (savedName || savedInfo) {
			lastSaved = new Date();
		}
	}

	async function saveUserInfo() {
		isSaving = true;
		try {
			localStorage.setItem(USER_NAME_KEY, userName);
			localStorage.setItem(USER_INFO_KEY, userInfo);
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
		loadUserInfo();
	});
</script>

<div class="page-container">
	<div class="page-header">
		<div>
			<h1>유저 정보</h1>
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
			<label for="userName">
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
			<label for="userInfo">
				<Icon icon="solar:document-text-bold-duotone" width="20" height="20" />
				사용자 정보
			</label>
			<textarea
				id="userInfo"
				bind:value={userInfo}
				placeholder="예:&#10;- 연구 분야: 자율주행 시스템 개발&#10;- 관심 주제: SLAM, 경로 계획, 센서 퓨전&#10;- 사용 센서: LiDAR, 카메라, IMU&#10;- 개발 환경: ROS2, Python, C++&#10;- 목표: 실시간 맵 생성 및 주행 판단 알고리즘 최적화&#10;&#10;자유롭게 작성하세요..."
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
				<strong>💡 변수 치환 시스템:</strong>
				<p>
					시스템 메시지, 캐릭터 프롬프트, 명령어 템플릿에서 다음 변수를 사용할 수 있습니다:
				</p>
				<ul>
					<li><code>&#123;&#123;user&#125;&#125;</code> → 사용자 이름으로 대체됩니다</li>
					<li><code>&#123;&#123;char&#125;&#125;</code> → 선택된 캐릭터 이름으로 대체됩니다</li>
				</ul>
				<p class="example">
					예시: "You are in a text messaging conversation with
					<code>&#123;&#123;user&#125;&#125;</code>. Respond as <code>&#123;&#123;char&#125;&#125;</code>
					would."
				</p>
			</div>
		</div>
	</div>
</div>

<style>
	.page-container {
		max-width: 900px;
		margin: 0 auto;
	}



	.content-card {
		background: white;
		border-radius: 0.75rem;
		padding: 2rem;
		box-shadow: var(--shadow-sm);
	}

	.input-section {
		margin-bottom: 2rem;
	}

	.input-section label,
	.textarea-wrapper label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #374151;
		font-size: 0.95rem;
	}

	.input-field {
		width: 100%;
		padding: 0.75rem 1rem;
		border: 1px solid #d1d5db;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-family: inherit;
		transition: all 0.2s;
	}

	.input-field:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: var(--focus-ring);
	}

	.input-hint {
		margin: 0.5rem 0 0 0;
		font-size: 0.875rem;
		color: var(--color-text-secondary);
	}

	.input-hint code {
		background: #f3f4f6;
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		font-family: 'Courier New', monospace;
		font-size: 0.85rem;
		color: #667eea;
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
		font-family: inherit;
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
		background: #dbeafe;
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		font-family: 'Courier New', monospace;
		font-size: 0.85rem;
		color: #1e40af;
	}

	.hint-box .example {
		margin-top: 0.75rem;
		padding: 0.75rem;
		background: var(--overlay-white-medium);
		border-radius: 0.375rem;
		font-style: italic;
	}
</style>
