<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Icon from '@iconify/svelte';
	import { requestJson } from '$lib/backend';

	// State
	let templates = $state([]);
	let characters = $state([]);
	let isLoading = $state(true);
	let settings = $state({
		default_character_id: null,
		default_prompt_template_id: null
	});

	// 데이터 로드
	async function loadData() {
		isLoading = true;
		try {
			const [templatesData, charactersData, settingsData] = await Promise.all([
				requestJson('/api/prompt-templates'),
				requestJson('/api/characters'),
				requestJson('/api/settings/chat').catch(() => null)
			]);

			templates = templatesData;
			characters = charactersData;

			if (settingsData) {
				settings = settingsData;
			}
		} catch (error) {
			console.error('Failed to load data:', error);
		} finally {
			isLoading = false;
		}
	}

	async function handleTemplateChange(event) {
		const id = parseInt(event.target.value);
		settings.default_prompt_template_id = id;
		await saveSettings();
	}

	async function handleCharacterChange(event) {
		const id = parseInt(event.target.value);
		settings.default_character_id = id;
		await saveSettings();
	}

	async function saveSettings() {
		try {
			await requestJson('/api/settings/chat', { method: 'PUT', body: settings });
		} catch (error) {
			console.error('Failed to save settings:', error);
		}
	}

	function navigateTo(path) {
		goto(path);
	}

	onMount(() => {
		loadData();
	});
</script>

<div class="settings-home">
	<div class="page-header">
		<h1>AI 설정</h1>
		<p class="page-description">AI 채팅에 사용할 템플릿과 캐릭터를 선택하세요.</p>
	</div>

	{#if isLoading}
		<div class="loading-state">
			<Icon icon="solar:ufo-2-duotone" width="48" class="spin" />
			<p>로딩 중...</p>
		</div>
	{:else}
		<!-- 현재 선택 -->
		<div class="selection-card">
			<h2>현재 설정</h2>

			<div class="selection-grid">
				<!-- 템플릿 선택 -->
				<div class="selection-item">
					<label for="template-select" class="form-label">
						<Icon icon="solar:document-text-bold-duotone" width="20" height="20" />
						시스템 메시지 템플릿
					</label>
					<select
						id="template-select"
						value={settings.default_prompt_template_id}
						onchange={handleTemplateChange}
						class="select-field w-full"
					>
						{#if templates.length === 0}
							<option value="">템플릿이 없습니다</option>
						{:else}
							{#each templates as template}
								<option value={template.id}>{template.name}</option>
							{/each}
						{/if}
					</select>
					<p class="form-hint">AI의 기본 역할과 행동 방식을 정의합니다.</p>
				</div>

				<!-- 캐릭터 선택 -->
				<div class="selection-item">
					<label for="character-select" class="form-label">
						<Icon icon="solar:user-bold-duotone" width="20" height="20" />
						캐릭터
					</label>
					<select
						id="character-select"
						value={settings.default_character_id}
						onchange={handleCharacterChange}
						class="select-field w-full"
					>
						{#if characters.length === 0}
							<option value="">캐릭터가 없습니다</option>
						{:else}
							{#each characters as character}
								<option value={character.id}>{character.name}</option>
							{/each}
						{/if}
					</select>
					<p class="form-hint">AI의 성격과 말투를 정의합니다.</p>
				</div>
			</div>
		</div>

		<!-- 빠른 관리 메뉴 -->
		<div class="quick-actions">
			<h2>빠른 관리</h2>
			<div class="actions-grid">
				<button class="action-card" onclick={() => navigateTo('/ai-settings/system-messages')}>
					<Icon icon="solar:document-text-bold-duotone" width="32" height="32" />
					<h3>시스템 메시지</h3>
					<p>{templates.length}개 템플릿</p>
				</button>

				<button class="action-card" onclick={() => navigateTo('/ai-settings/characters')}>
					<Icon icon="solar:user-bold-duotone" width="32" height="32" />
					<h3>캐릭터</h3>
					<p>{characters.length}개 캐릭터</p>
				</button>

				<button class="action-card" onclick={() => navigateTo('/ai-settings/user-info')}>
					<Icon icon="solar:users-group-rounded-bold-duotone" width="32" height="32" />
					<h3>유저 정보</h3>
					<p>개인화 설정</p>
				</button>

				<button class="action-card" onclick={() => navigateTo('/ai-settings/final-message')}>
					<Icon icon="solar:check-read-bold-duotone" width="32" height="32" />
					<h3>최종 메시지</h3>
					<p>체크리스트</p>
				</button>
			</div>
		</div>

		<!-- 정보 박스 -->
		<div class="info-box">
			<Icon icon="solar:lightbulb-bolt-bold-duotone" width="24" height="24" />
			<div>
				<strong>💡 사용 방법</strong>
				<p>
					위에서 선택한 템플릿과 캐릭터가 AI 채팅에 적용됩니다.
					유저 정보와 최종 메시지는 각 탭에서 직접 입력하세요.
				</p>
			</div>
		</div>
	{/if}
</div>

<style>
	.settings-home {
		max-width: 1000px;
	}



	.selection-card {
		background: var(--color-surface);
		border-radius: 0.75rem;
		padding: 2rem;
		box-shadow: var(--shadow-sm);
		margin-bottom: 2rem;
	}

	.selection-card h2 {
		margin: 0 0 1.5rem 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.selection-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 2rem;
	}

	.quick-actions {
		margin-bottom: 2rem;
	}

	.quick-actions h2 {
		margin: 0 0 1.5rem 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.actions-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
	}

	.action-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 0.75rem;
		padding: 1.5rem;
		text-align: center;
		cursor: pointer;
		transition: all 0.2s;
	}

	.action-card:hover {
		transform: translateY(-2px);
		box-shadow: var(--shadow-md);
		border-color: var(--color-primary);
	}

	.action-card h3 {
		margin: 0.75rem 0 0.5rem 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.action-card p {
		margin: 0;
		font-size: 0.875rem;
		color: var(--color-text-secondary);
	}

	.info-box {
		display: flex;
		gap: 1rem;
		padding: 1.5rem;
		background: var(--color-info-bg-light);
		border: 1px solid var(--color-info);
		border-radius: 0.5rem;
		color: var(--color-info-text);
	}

	.info-box strong {
		display: block;
		margin-bottom: 0.5rem;
	}

	.info-box p {
		margin: 0;
		line-height: 1.6;
	}
</style>
