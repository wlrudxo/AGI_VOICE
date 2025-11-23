<script lang="ts">
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import Icon from '@iconify/svelte';

	interface Character {
		id: number;
		name: string;
		prompt_content: string;
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
			const charactersData = await invoke<Character[]>('get_characters');
			characters = charactersData;

			// 프롬프트 템플릿 목록 가져오기
			const templatesData = await invoke<PromptTemplate[]>('get_prompt_templates');
			promptTemplates = templatesData;

			// 현재 설정 가져오기
			try {
				const settingsData = await invoke<ChatSettings>('get_chat_settings');
				settings = settingsData;
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

			console.log('💾 Saving chat settings:', settings);
			await invoke('update_chat_settings', { chatSettings: settings });
			console.log('✅ Chat settings saved successfully');

			message = { type: 'success', text: '설정이 저장되었습니다.' };

			// 채팅 위젯에 설정 변경 알림
			window.dispatchEvent(new CustomEvent('chatSettingsUpdated'));

			// 3초 후 메시지 제거
			setTimeout(() => {
				message = null;
			}, 3000);
		} catch (err: any) {
			console.error('❌ Failed to save settings:', err);
			message = { type: 'error', text: err.message || '설정 저장에 실패했습니다.' };
		} finally {
			saving = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<div class="chat-settings-page">
	<div class="page-header">
		<div>
			<h1>채팅 설정</h1>
			<p class="page-description">AI 채팅에서 사용할 기본 캐릭터와 시스템 템플릿을 선택하세요.</p>
		</div>
	</div>

	{#if loading}
		<div class="loading-state">
			<Icon icon="solar:ufo-2-duotone" width="48" class="spin" />
			<p>설정 로딩 중...</p>
		</div>
	{:else}
		<form onsubmit={(e) => { e.preventDefault(); saveSettings(); }} class="settings-form">
			<!-- 시스템 템플릿 선택 -->
			<div class="form-group">
				<label for="template" class="form-label">
					<Icon icon="solar:document-text-bold-duotone" width="20" height="20" />
					<span>시스템 템플릿</span>
				</label>
				<select
					id="template"
					bind:value={settings.defaultPromptTemplateId}
					required
					class="select-field w-full"
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
				<label for="character" class="form-label">
					<Icon icon="solar:user-bold-duotone" width="20" height="20" />
					<span>캐릭터</span>
				</label>
				<select
					id="character"
					bind:value={settings.defaultCharacterId}
					required
					class="select-field w-full"
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
				<div class:alert-success={message.type === 'success'} class:alert-error={message.type === 'error'}>
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

		<!-- 안내 카드 -->
		<div class="info-card">
			<h3>
				<Icon icon="solar:info-circle-bold-duotone" width="20" height="20" />
				설정 안내
			</h3>
			<ul>
				<li>• <strong>시스템 템플릿</strong>: AI의 역할과 행동 방식을 정의하는 프롬프트입니다.</li>
				<li>• <strong>캐릭터</strong>: AI 채팅 위젯에서 사용할 캐릭터를 선택합니다.</li>
				<li>• 설정은 자동으로 채팅 위젯에 적용됩니다.</li>
				<li>• 캐릭터와 템플릿은 AI 설정 메뉴에서 관리할 수 있습니다.</li>
			</ul>
		</div>
	{/if}
</div>

<style>
	.chat-settings-page {
		max-width: 800px;
		margin: 0 auto;
	}

	.page-header {
		margin-bottom: 2rem;
	}


	.settings-form {
		background: var(--color-surface);
		border-radius: 0.75rem;
		padding: 2rem;
		box-shadow: var(--shadow-sm);
		margin-bottom: 1.5rem;
	}

	.form-group:last-of-type {
		margin-bottom: 0;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		margin-top: 2rem;
	}

	.info-card {
		background: var(--color-surface);
		border-radius: 0.75rem;
		padding: 1.5rem;
		box-shadow: var(--shadow-sm);
	}

	.info-card h3 {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text-primary);
		margin: 0 0 1rem 0;
	}

	.info-card ul {
		list-style: none;
		padding: 0;
		margin: 0;
		color: var(--color-text-secondary);
	}

	.info-card li {
		margin-bottom: 0.5rem;
		line-height: 1.6;
	}

	.info-card li:last-child {
		margin-bottom: 0;
	}
</style>
