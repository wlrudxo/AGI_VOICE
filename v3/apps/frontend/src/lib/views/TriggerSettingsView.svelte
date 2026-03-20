<script>
  import Icon from '@iconify/svelte';

  const placeholderItems = [
    '트리거 CRUD UI 이식',
    'Python trigger runtime 연동',
    'AI action sequence 연동',
    'trigger log / cooldown 상태 표시',
  ];
</script>

<div class="trigger-settings">
  <div class="page-header">
    <div>
      <h1>트리거 설정</h1>
      <p class="page-description">
        이 화면은 자리와 구성을 먼저 맞춰둔 상태입니다. 다음 단계에서 Python trigger runtime과
        연결됩니다.
      </p>
    </div>
  </div>

  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:atom-bold-duotone" width="24" height="24" />
      Pending Migration
    </h2>

    <div class="placeholder-list">
      {#each placeholderItems as item}
        <div class="placeholder-item text-secondary">{item}</div>
      {/each}
    </div>
  </section>
</div>

<style>
  .trigger-settings {
    max-width: 800px;
    margin: 0 auto;
  }

  .placeholder-list {
    display: grid;
    gap: 0.75rem;
  }

  .placeholder-item {
    padding: 0.875rem 1rem;
    border-radius: 0.75rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
  }
</style>
