<script lang="ts">
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import Icon from '@iconify/svelte';
	import HelpModal from '$lib/components/HelpModal.svelte';

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
	let showHelpModal = $state(false);

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
			<div class="title-row">
				<h1>채팅 설정</h1>
				<button class="btn-icon help-btn" onclick={() => (showHelpModal = true)}>
					<Icon icon="solar:question-circle-bold" width="20" height="20" />
				</button>
			</div>
			<p class="page-description">AI 채팅에서 사용할 기본 캐릭터와 시스템 템플릿을 선택하세요.</p>
		</div>
		<button class="btn-primary" onclick={saveSettings} disabled={saving || loading}>
			<Icon icon="solar:diskette-bold" width="20" height="20" />
			{saving ? '저장 중...' : '저장'}
		</button>
	</div>

	{#if loading}
		<div class="loading-state">
			<Icon icon="solar:ufo-2-duotone" width="48" class="spin" />
			<p>설정 로딩 중...</p>
		</div>
	{:else}
		<div class="settings-form">
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
		</div>

	{/if}
</div>

<!-- Help Modal -->
<HelpModal
	bind:visible={showHelpModal}
	title="채팅 설정 도움말"
	onClose={() => (showHelpModal = false)}
>
	<section class="help-section">
		<h4>⚙️ 채팅 설정이란?</h4>
		<p class="help-desc">
			AI 채팅 위젯에서 사용할 기본 캐릭터와 시스템 템플릿을 설정합니다.
			이 설정은 새로운 대화를 시작할 때 자동으로 적용됩니다.
		</p>
	</section>

	<section class="help-section">
		<h4>📋 설정 구성 요소</h4>

		<div class="command-example">
			<code>시스템 템플릿</code>
			<p>
				AI의 역할과 행동 방식을 정의하는 프롬프트입니다.
				예: "자율주행 연구 전문가", "일반 AI 어시스턴트" 등
			</p>
		</div>

		<div class="command-example">
			<code>캐릭터</code>
			<p>
				AI의 말투, 성격, 톤을 정의합니다.
				예: "Aris (Blue Archive)" - 친근하고 격려적인 톤
			</p>
		</div>
	</section>

	<section class="help-section">
		<h4>🔄 설정 적용 방법</h4>
		<ol class="help-list">
			<li><strong>시스템 템플릿</strong>과 <strong>캐릭터</strong>를 선택합니다.</li>
			<li><strong>설정 저장</strong> 버튼을 클릭합니다.</li>
			<li>채팅 위젯에서 새 대화를 시작하면 자동으로 적용됩니다.</li>
			<li>기존 대화는 설정 변경의 영향을 받지 않습니다.</li>
		</ol>
	</section>

	<section class="help-section">
		<h4>💡 Tip</h4>
		<ul class="help-list">
			<li>캐릭터와 템플릿은 <strong>AI 설정</strong> 메뉴에서 추가/수정/삭제할 수 있습니다.</li>
			<li>시스템 템플릿에서는 변수 치환을 지원합니다 (예: <code>&#123;&#123;user&#125;&#125;</code>, <code>&#123;&#123;char&#125;&#125;</code>).</li>
			<li>설정 변경은 즉시 채팅 위젯에 반영됩니다.</li>
		</ul>
	</section>
</HelpModal>

<style>
	.chat-settings-page {
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
