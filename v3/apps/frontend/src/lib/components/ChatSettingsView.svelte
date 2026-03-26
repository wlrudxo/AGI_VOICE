<script lang="ts">
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import { requestJson } from '$lib/backend';

	interface Character {
		id: number;
		name: string;
		promptContent: string;
	}

	interface PromptTemplate {
		id: number;
		name: string;
		content: string;
	}

	interface ChatSettings {
		defaultCharacterId: number | null;
		defaultPromptTemplateId: number | null;
		defaultClaudeModel: string;
	}

	let characters = $state<Character[]>([]);
	let promptTemplates = $state<PromptTemplate[]>([]);
	let settings = $state<ChatSettings>({
		defaultCharacterId: null,
		defaultPromptTemplateId: null,
		defaultClaudeModel: 'sonnet'
	});

	let loading = $state(true);
	let saving = $state(false);
	let message = $state<{ type: 'success' | 'error'; text: string } | null>(null);

	async function loadData() {
		try {
			loading = true;

			// 캐릭터 목록 가져오기
			characters = await requestJson<Character[]>('/api/characters');

			// 프롬프트 템플릿 목록 가져오기
			promptTemplates = await requestJson<PromptTemplate[]>('/api/prompt-templates');

			// 현재 설정 가져오기
			try {
				const data = await requestJson<ChatSettings>('/api/settings/chat');
				settings = data;
			} catch (err) {
				// 설정이 없으면 기본값 설정 (첫 번째 항목 선택)
				if (characters.length > 0) {
					settings.defaultCharacterId = characters[0].id;
				}
				if (promptTemplates.length > 0) {
					settings.defaultPromptTemplateId = promptTemplates[0].id;
				}
			}
		} catch (err) {
			console.error('Failed to load data:', err);
			message = { type: 'error', text: '데이터를 불러오는데 실패했습니다.' };
		} finally {
			loading = false;
		}
	}

	async function saveSettings() {
		try {
			saving = true;
			message = null;

			if (!settings.defaultCharacterId || !settings.defaultPromptTemplateId) {
				message = { type: 'error', text: '캐릭터와 템플릿을 모두 선택해주세요.' };
				return;
			}

			await requestJson('/api/settings/chat', { method: 'PUT', body: settings });

			message = { type: 'success', text: '설정이 저장되었습니다.' };

			// 채팅 위젯에 설정 변경 알림
			window.dispatchEvent(new CustomEvent('chatSettingsUpdated'));

			// 3초 후 메시지 제거
			setTimeout(() => {
				message = null;
			}, 3000);
		} catch (err: any) {
			console.error('Failed to save settings:', err);
			message = { type: 'error', text: err || '설정 저장에 실패했습니다.' };
		} finally {
			saving = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<div class="chat-settings-view">
	{#if loading}
		<div class="loading-state">
			<p>설정 로딩 중...</p>
		</div>
	{:else}
		<form onsubmit={(e) => { e.preventDefault(); saveSettings(); }} class="settings-form">
			<!-- 시스템 템플릿 선택 -->
			<div class="form-group">
				<label for="template">
					<Icon icon="solar:document-text-bold-duotone" width="20" height="20" />
					<span>시스템 템플릿</span>
				</label>
				<select
					id="template"
					bind:value={settings.defaultPromptTemplateId}
					required
				>
					<option value={null}>템플릿을 선택하세요</option>
					{#each promptTemplates as template}
						<option value={template.id}>
							{template.name}
						</option>
					{/each}
				</select>
			</div>

			<!-- 캐릭터 선택 -->
			<div class="form-group">
				<label for="character">
					<Icon icon="solar:user-bold-duotone" width="20" height="20" />
					<span>캐릭터</span>
				</label>
				<select
					id="character"
					bind:value={settings.defaultCharacterId}
					required
				>
					<option value={null}>캐릭터를 선택하세요</option>
					{#each characters as character}
						<option value={character.id}>
							{character.name}
						</option>
					{/each}
				</select>
			</div>

			<!-- 메시지 -->
			{#if message}
				<div class="message" class:success={message.type === 'success'} class:error={message.type === 'error'}>
					{message.text}
				</div>
			{/if}

			<!-- 저장 버튼 -->
			<div class="form-actions">
				<button type="submit" class="btn-primary" disabled={saving}>
					<Icon icon="solar:diskette-bold-duotone" width="20" height="20" />
					<span>{saving ? '저장 중...' : '설정 저장'}</span>
				</button>
			</div>
		</form>
	{/if}
</div>

<style>
	.chat-settings-view {
		display: flex;
		flex-direction: column;
		height: 100%;
		overflow-y: auto;
		padding: 1rem;
		background: var(--color-background);
	}

	.loading-state {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: var(--color-text-muted);
	}

	.settings-form {
		background: var(--color-surface);
		border-radius: 0.75rem;
		padding: 1.5rem;
		box-shadow: var(--shadow-sm);
		margin-bottom: 1rem;
	}

	.form-group {
		margin-bottom: 1.5rem;
	}

	.form-group:last-of-type {
		margin-bottom: 0;
	}

	.form-group label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-weight: 600;
		color: var(--color-text-primary);
		margin-bottom: 0.75rem;
		font-size: 0.9rem;
	}

	.form-group select {
		width: 100%;
		padding: 0.75rem 1rem;
		border: 1px solid var(--color-border-dark);
		border-radius: 0.5rem;
		font-size: 0.9rem;
		color: var(--color-text-primary);
		background: var(--color-surface);
		cursor: pointer;
		transition: all 0.2s;
	}

	.form-group select:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: var(--focus-ring);
	}

	.message {
		padding: 0.875rem;
		border-radius: 0.5rem;
		margin-bottom: 1.25rem;
		font-weight: 500;
		font-size: 0.875rem;
	}

	.message.success {
		background: rgba(72, 187, 120, 0.2);
		color: var(--color-success);
	}

	.message.error {
		background: rgba(245, 101, 101, 0.2);
		color: var(--color-error);
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		margin-top: 1.5rem;
	}

	.form-actions .btn-primary {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.chat-settings-view::-webkit-scrollbar {
		width: 6px;
	}

	.chat-settings-view::-webkit-scrollbar-track {
		background: var(--color-surface);
	}

	.chat-settings-view::-webkit-scrollbar-thumb {
		background: var(--color-border-dark);
		border-radius: 3px;
	}

	.chat-settings-view::-webkit-scrollbar-thumb:hover {
		background: var(--color-text-muted);
	}
</style>
