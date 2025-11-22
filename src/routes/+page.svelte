<script lang="ts">
  import { onMount } from 'svelte';

  let currentTime = $state('');

  function updateTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    currentTime = `${hours}:${minutes}:${seconds}`;
  }

  onMount(() => {
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  });
</script>

<div class="dashboard">
  <div class="welcome-section">
    <h1 class="text-primary">AGI Voice</h1>
    <p class="text-secondary">자율주행 연구를 위한 AI 어시스턴트</p>
    <div class="current-time text-muted">{currentTime}</div>
  </div>

  <div class="info-section">
    <div class="info-card">
      <h2 class="text-primary">시작하기</h2>
      <p class="text-secondary">
        오른쪽 하단의 AI 채팅 버튼을 클릭하여 대화를 시작하세요.
      </p>
      <ul class="feature-list">
        <li>자율주행 맵 생성 연구</li>
        <li>주행 판단 알고리즘 분석</li>
        <li>최신 연구 동향 및 문헌 검색</li>
        <li>데이터 분석 및 인사이트 제공</li>
      </ul>
    </div>

    <div class="info-card">
      <h2 class="text-primary">주요 기능</h2>
      <p class="text-secondary">
        AI 설정 메뉴에서 시스템 동작을 커스터마이징할 수 있습니다.
      </p>
      <ul class="feature-list">
        <li><strong>시스템 메시지</strong>: AI 기본 동작 정의</li>
        <li><strong>캐릭터</strong>: AI 페르소나 설정</li>
        <li><strong>명령어</strong>: 커스텀 액션 정의</li>
        <li><strong>대화 히스토리</strong>: 이전 대화 기록 관리</li>
      </ul>
    </div>

    <div class="info-card">
      <h2 class="text-primary">프로젝트 정보</h2>
      <p class="text-secondary">
        이 프로젝트는 범용 AI 채팅 시스템을 기반으로 합니다.
      </p>
      <ul class="feature-list">
        <li><strong>Frontend</strong>: Tauri + SvelteKit + Svelte 5</li>
        <li><strong>Backend</strong>: Rust + SeaORM + SQLite</li>
        <li><strong>AI</strong>: Claude CLI Integration</li>
        <li><strong>Database</strong>: ai_chat.db (Generic & Reusable)</li>
      </ul>
    </div>
  </div>
</div>

<style>
  .dashboard {
    padding: 3rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  .welcome-section {
    text-align: center;
    margin-bottom: 4rem;
  }

  .welcome-section h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }

  .welcome-section p {
    font-size: 1.25rem;
    margin-bottom: 1rem;
  }

  .current-time {
    font-size: 2rem;
    font-weight: 300;
    font-family: 'Courier New', monospace;
  }

  .info-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
  }

  .info-card {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 2rem;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .info-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }

  .info-card h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }

  .info-card p {
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  .feature-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .feature-list li {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--color-border);
    color: var(--color-text-secondary);
  }

  .feature-list li:last-child {
    border-bottom: none;
  }

  .feature-list li strong {
    color: var(--color-text-primary);
    font-weight: 600;
  }
</style>
