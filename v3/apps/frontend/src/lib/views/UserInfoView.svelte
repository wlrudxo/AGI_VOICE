<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { dialogStore } from '../stores/dialogStore.svelte.js';
  import HelpModal from '../components/HelpModal.svelte';

  let userName = $state('');
  let userInfo = $state('');
  let isSaving = $state(false);
  let lastSaved = $state(null);
  let showHelpModal = $state(false);

  const USER_NAME_KEY = 'agi_voice_user_name';
  const USER_INFO_KEY = 'agi_voice_user_info';

  function loadUserInfo() {
    const savedName = localStorage.getItem(USER_NAME_KEY);
    const savedInfo = localStorage.getItem(USER_INFO_KEY);

    if (savedName) userName = savedName;
    if (savedInfo) userInfo = savedInfo;
    if (savedName || savedInfo) lastSaved = new Date();
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

    <div class="textarea-wrapper">
      <label for="userInfo" class="form-label">
        <Icon icon="solar:document-text-bold-duotone" width="20" height="20" />
        사용자 정보
      </label>
      <textarea
        id="userInfo"
        bind:value={userInfo}
        placeholder="연구 분야, 관심사, 사용 환경 등을 자유롭게 작성하세요..."
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
  title="변수 치환 시스템 도움말"
  onClose={() => (showHelpModal = false)}
>
  <section class="help-section">
    <h4>🔄 변수 치환 시스템이란?</h4>
    <p class="help-desc">
      프롬프트에서 특정 변수를 사용하면 실제 대화 시 자동으로 실제 값으로 치환됩니다.
    </p>
  </section>

  <section class="help-section">
    <h4>📋 사용 가능한 변수</h4>
    <div class="command-example">
      <code>&#123;&#123;user&#125;&#125;</code>
      <p>사용자 이름으로 대체됩니다.</p>
    </div>
    <div class="command-example">
      <code>&#123;&#123;char&#125;&#125;</code>
      <p>선택된 캐릭터 이름으로 대체됩니다.</p>
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

  .content-card {
    background: var(--color-surface);
    border-radius: 0.75rem;
    padding: 2rem;
    box-shadow: var(--shadow-sm);
  }

  .input-section {
    margin-bottom: 2rem;
  }

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
</style>
