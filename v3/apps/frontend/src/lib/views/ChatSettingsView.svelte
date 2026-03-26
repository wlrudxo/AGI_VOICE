<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import HelpModal from '../components/HelpModal.svelte';
  import { createSettingsApi } from '../settingsApi.js';

  const settingsApi = createSettingsApi();

  let characters = $state([]);
  let promptTemplates = $state([]);
  let settings = $state({
    defaultCharacterId: null,
    defaultPromptTemplateId: null,
    defaultClaudeModel: 'sonnet',
  });

  let loading = $state(true);
  let saving = $state(false);
  let message = $state(null);
  let showHelpModal = $state(false);

  async function loadData() {
    try {
      loading = true;
      const [charactersData, templatesData, settingsData] = await Promise.all([
        settingsApi.getCharacters(),
        settingsApi.getPromptTemplates(),
        settingsApi.getChatSettings(),
      ]);

      characters = charactersData;
      promptTemplates = templatesData;
      settings = {
        defaultCharacterId:
          settingsData.defaultCharacterId ?? charactersData[0]?.id ?? null,
        defaultPromptTemplateId:
          settingsData.defaultPromptTemplateId ?? templatesData[0]?.id ?? null,
        defaultClaudeModel: settingsData.defaultClaudeModel ?? 'sonnet',
      };
    } catch (error) {
      console.error('Failed to load chat settings:', error);
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

      await settingsApi.updateChatSettings(settings);
      message = { type: 'success', text: '설정이 저장되었습니다.' };
      window.dispatchEvent(new CustomEvent('chatSettingsUpdated'));
      setTimeout(() => {
        message = null;
      }, 3000);
    } catch (error) {
      message = {
        type: 'error',
        text: error instanceof Error ? error.message : '설정 저장에 실패했습니다.',
      };
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
            <option value={template.id}>{template.name}</option>
          {/each}
        </select>
      </div>

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
            <option value={character.id}>{character.name}</option>
          {/each}
        </select>
      </div>

      {#if message}
        <div class:alert-success={message.type === 'success'} class:alert-error={message.type === 'error'}>
          {message.text}
        </div>
      {/if}
    </div>
  {/if}
</div>

<HelpModal
  bind:visible={showHelpModal}
  title="채팅 설정 도움말"
  onClose={() => (showHelpModal = false)}
>
  <section class="help-section">
    <h4>⚙️ 채팅 설정이란?</h4>
    <p class="help-desc">
      AI 채팅 위젯에서 사용할 기본 캐릭터와 시스템 템플릿을 설정합니다. 이 설정은 새로운
      대화를 시작할 때 자동으로 적용됩니다.
    </p>
  </section>

  <section class="help-section">
    <h4>📋 설정 구성 요소</h4>
    <div class="command-example">
      <code>시스템 템플릿</code>
      <p>AI의 역할과 행동 방식을 정의하는 프롬프트입니다.</p>
    </div>
    <div class="command-example">
      <code>캐릭터</code>
      <p>AI의 말투, 성격, 톤을 정의합니다.</p>
    </div>
  </section>

  <section class="help-section">
    <h4>🔄 설정 적용 방법</h4>
    <ol class="help-list">
      <li><strong>시스템 템플릿</strong>과 <strong>캐릭터</strong>를 선택합니다.</li>
      <li><strong>설정 저장</strong> 버튼을 클릭합니다.</li>
      <li>새 대화를 시작하면 자동으로 적용됩니다.</li>
    </ol>
  </section>
</HelpModal>

<style>
  .chat-settings-page {
    max-width: 1200px;
    margin: 0 auto;
  }

  .title-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .settings-form {
    background: var(--color-surface);
    border-radius: 0.75rem;
    padding: 2rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.5rem;
  }
</style>
