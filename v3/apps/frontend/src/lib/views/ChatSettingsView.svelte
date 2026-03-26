<script>
  import Icon from '@iconify/svelte';
</script>

<div class="page-container">
  <div class="page-header">
    <div>
      <h1>채팅 설정</h1>
      <p>현재 V3에서는 채팅 기본값을 메인 설정 화면에서 관리합니다.</p>
    </div>
  </div>

  <div class="card">
    <div class="empty-state">
      <Icon icon="solar:settings-bold-duotone" width="56" height="56" />
      <p>캐릭터, 프롬프트 템플릿, Trigger AI 기본값은 좌측 `설정` 메뉴에서 조정하세요.</p>
    </div>
  </div>
</div>

<style>
  .card {
    padding: 2rem;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
  }

  .empty-state {
    display: flex;
    min-height: 280px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    text-align: center;
    color: var(--color-text-muted);
  }
</style>
