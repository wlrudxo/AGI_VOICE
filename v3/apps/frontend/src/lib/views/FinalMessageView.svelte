<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { dialogStore } from '../stores/dialogStore.svelte.js';
  import HelpModal from '../components/HelpModal.svelte';

  let finalMessage = $state('');
  let isSaving = $state(false);
  let lastSaved = $state(null);
  let showHelpModal = $state(false);

  const STORAGE_KEY = 'agi_voice_final_message';
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

<HelpModal
  bind:visible={showHelpModal}
  title="최종 메시지 도움말"
  onClose={() => (showHelpModal = false)}
>
  <section class="help-section">
    <h4>📋 최종 메시지란?</h4>
    <p class="help-desc">
      AI가 응답을 생성하기 직전에 마지막으로 참고할 체크리스트입니다.
    </p>
  </section>

  <section class="help-section">
    <h4>📝 기본 템플릿</h4>
    <div class="example-card">
      <pre>{DEFAULT_TEMPLATE}</pre>
    </div>
  </section>
</HelpModal>

<style>
  .page-container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .title-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
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
</style>
