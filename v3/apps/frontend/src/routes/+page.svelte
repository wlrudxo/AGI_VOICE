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
      <h2 class="text-primary">AI 채팅</h2>
      <p class="text-secondary">
        Claude CLI 기반 대화형 AI 어시스턴트 시스템
      </p>
      <ul class="feature-list">
        <li><strong>동적 프롬프트</strong>: 시스템 메시지 + 캐릭터 + 명령어 조합</li>
        <li><strong>대화 관리</strong>: 히스토리 저장 및 컨텍스트 유지</li>
        <li><strong>변수 치환</strong>: 사용자 정보 및 캐릭터 자동 적용</li>
        <li><strong>위젯 모드</strong>: 컴팩트 채팅 전용 인터페이스</li>
      </ul>
    </div>

    <div class="info-card">
      <h2 class="text-primary">자율주행</h2>
      <p class="text-secondary">
        CarMaker 연동 실시간 차량 제어 및 모니터링
      </p>
      <ul class="feature-list">
        <li><strong>실시간 제어</strong>: 가스/브레이크/조향각 직접 제어</li>
        <li><strong>차량 모니터링</strong>: 13개 신호 실시간 추적</li>
        <li><strong>트리거 시스템</strong>: 조건 기반 자동 응답 및 제어</li>
        <li><strong>AI 연동</strong>: LLM 기반 주행 판단 및 규칙 제어</li>
      </ul>
    </div>

    <div class="info-card">
      <h2 class="text-primary">Map 생성</h2>
      <p class="text-secondary">
        SUMO 교통 시뮬레이션 맵 생성 및 관리
      </p>
      <ul class="feature-list">
        <li><strong>맵 편집기</strong>: 노드/엣지 XML 기반 시각적 생성</li>
        <li><strong>맵 라이브러리</strong>: 저장된 맵 검색 및 관리</li>
        <li><strong>임베딩 시스템</strong>: OpenAI 벡터화 준비 (Phase 2)</li>
        <li><strong>RAG 검색</strong>: 자연어 기반 유사 맵 추천 (Phase 3)</li>
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
