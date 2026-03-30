<script lang="ts">
	import { onMount } from 'svelte';
	import { requestJson } from '$lib/backend';
	import Icon from '@iconify/svelte';
	import HelpModal from '$lib/components/HelpModal.svelte';
	import { chatBus } from '$lib/stores/chatBus';

	interface PromptTemplate {
		id: number;
		name: string;
		content: string;
	}

	interface CommandTemplate {
		id: number;
		name: string;
		content: string;
		isActive: number;
	}

	interface ChatSettings {
		defaultPromptTemplateId: number | null;
		defaultClaudeModel: string;
	}

	let promptTemplates = $state<PromptTemplate[]>([]);
	let commandTemplates = $state<CommandTemplate[]>([]);
	let settings = $state<ChatSettings>({
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

			const [templatesData, commandTemplatesData] = await Promise.all([
				requestJson<PromptTemplate[]>('/api/prompt-templates'),
				requestJson<CommandTemplate[]>('/api/command-templates')
			]);
			promptTemplates = templatesData;
			commandTemplates = commandTemplatesData;

			// 현재 설정 가져오기
			try {
				const settingsData = await requestJson<ChatSettings>('/api/settings/chat');
				settings = settingsData;
			} catch (err) {
				// 설정이 없으면 기본값 설정 (첫 번째 항목 선택)
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

			if (!settings.defaultPromptTemplateId) {
				message = { type: 'error', text: '시스템 템플릿을 선택해주세요.' };
				return;
			}

			console.log('💾 Saving chat settings:', settings);
			await requestJson('/api/settings/chat', { method: 'PUT', body: settings });
			console.log('✅ Chat settings saved successfully');

			message = { type: 'success', text: '설정이 저장되었습니다.' };

			chatBus.notifyChatSettingsUpdated();

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

	async function toggleCommandTemplate(template: CommandTemplate) {
		try {
			await requestJson(`/api/command-templates/${template.id}/toggle`, { method: 'POST' });
			commandTemplates = commandTemplates.map((item) =>
				item.id === template.id
					? { ...item, isActive: item.isActive === 1 ? 0 : 1 }
					: item
			);
			message = {
				type: 'success',
				text: `"${template.name}" 템플릿이 ${template.isActive === 1 ? '비활성화' : '활성화'}되었습니다.`
			};
			setTimeout(() => {
				message = null;
			}, 2500);
		} catch (err: any) {
			console.error('❌ Failed to toggle command template:', err);
			message = { type: 'error', text: err.message || '명령어 템플릿 상태 변경에 실패했습니다.' };
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
			<p class="page-description">AI 채팅에서 사용할 시스템 템플릿과 명령어 템플릿을 제어합니다.</p>
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

			<div class="form-group">
				<div class="form-label">
					<Icon icon="solar:code-bold-duotone" width="20" height="20" />
					<span>명령어 템플릿</span>
				</div>
				<div class="command-template-list">
					{#if commandTemplates.length === 0}
						<div class="empty-command-templates">등록된 명령어 템플릿이 없습니다.</div>
					{:else}
						{#each commandTemplates as template}
							<div class="command-template-row">
								<div class="command-template-meta">
									<div class="command-template-name">{template.name}</div>
									<div class="command-template-summary">
										{template.content.split('\n')[0]}
									</div>
								</div>
								<label class="toggle-switch ml-4">
									<input
										type="checkbox"
										checked={template.isActive === 1}
										onchange={() => toggleCommandTemplate(template)}
									/>
									<div class="toggle-switch-track">
										<div class="toggle-switch-thumb"></div>
									</div>
								</label>
							</div>
						{/each}
					{/if}
				</div>
				<p class="text-xs mt-2 text-muted">
					활성화된 명령어 템플릿만 AI 채팅 프롬프트에 포함됩니다. 내용 편집은 명령어 템플릿 페이지에서 합니다.
				</p>
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
			AI 채팅 위젯에서 사용할 기본 시스템 템플릿을 설정하고,
			실제로 프롬프트에 포함할 명령어 템플릿을 켜고 끕니다.
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
			<code>명령어 템플릿</code>
			<p>
				AI가 참고할 실행 규칙과 액션 형식을 정의합니다.
				예: "자율주행 제어", "자율주행 맵 관리"
			</p>
		</div>

	</section>

	<section class="help-section">
		<h4>🔄 설정 적용 방법</h4>
		<ol class="help-list">
			<li><strong>시스템 템플릿</strong>을 선택합니다.</li>
			<li>사용할 <strong>명령어 템플릿</strong>을 활성화합니다.</li>
			<li><strong>설정 저장</strong> 버튼을 클릭합니다.</li>
			<li>채팅 위젯에서 새 대화를 시작하면 자동으로 적용됩니다.</li>
			<li>기존 대화는 설정 변경의 영향을 받지 않습니다.</li>
		</ol>
	</section>

	<section class="help-section">
		<h4>💡 Tip</h4>
		<ul class="help-list">
			<li>시스템 템플릿과 명령어 템플릿은 <strong>AI 설정</strong> 메뉴에서 관리할 수 있습니다.</li>
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

	.command-template-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.command-template-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.875rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: 0.75rem;
		background: var(--color-surface-secondary, rgba(255,255,255,0.5));
	}

	.command-template-meta {
		min-width: 0;
		flex: 1;
	}

	.command-template-name {
		font-weight: 600;
		color: var(--color-text-primary);
		margin-bottom: 0.25rem;
	}

	.command-template-summary {
		font-size: 0.875rem;
		color: var(--color-text-secondary);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.empty-command-templates {
		padding: 1rem;
		border: 1px dashed var(--color-border);
		border-radius: 0.75rem;
		color: var(--color-text-secondary);
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
