# 논문 작성지침

## 기본 정보

- **제목**: LLM 에이전트를 활용한 CarMaker 자율주행 시뮬레이션 판단 전략
- **학회**: 한국자동차공학회 (KSAE) 2026 춘계학술대회
- **파일**: `KSAE202601.tex`
- **템플릿 참고**: `KSAE_Korean.pdf` (Tire Tread Depth 논문)
- **목표 분량**: 5~6페이지 (2단 레이아웃)
- **언어**: 한국어 본문 + 영문 Abstract/Keywords/Table caption

---

## 논문 구조

### 1. 서론 (~0.7p)

**목표**: 연구 동기와 기여점 명확히 제시

- 자율주행 의사결정의 기존 접근법 (rule-based, reinforcement learning) 한계
  - Rule-based: 복잡한 시나리오 대응 어려움, 규칙 설계 비용
  - RL: 학습 시간, reward 설계 어려움, 일반화 한계
- LLM의 자연어 추론 능력을 차량 제어에 활용하는 동기
  - 상황 이해 및 판단의 유연성
  - 프롬프트 기반 행동 변경 (재학습 불필요)
- **기여점 3가지**:
  1. 트리거 기반 LLM-CarMaker 실시간 연동 시스템 제안
  2. LLM 출력을 차량 제어 명령으로 변환하는 통합 명령 포맷 설계
  3. 동적 프롬프트 시스템을 통한 모듈식 의사결정 전략

### 2. 시스템 아키텍처 (~1.5p)

**목표**: 전체 시스템과 핵심 모듈 설명

#### 2.1 전체 시스템 개요
- **Fig.1** (2-column 폭): 시스템 구성도
  - 구성요소: Tauri Desktop App ↔ CarMaker TCP ↔ LLM (Claude CLI)
  - 데이터 흐름: 텔레메트리 수집 → 트리거 감지 → LLM 판단 → 명령 실행
- 주요 모듈: 트리거 모니터, 명령 파서, 명령 실행기, 프롬프트 빌더

#### 2.2 트리거 기반 제어 루프
- **Fig.2**: 트리거 제어 플로우차트
  - 10Hz 폴링으로 차량 텔레메트리 모니터링
  - 조건 평가 (예: `Car.v >= 27.78`, `Car.ax < -5.0`)
  - 트리거 발동 시: 시뮬레이션 일시정지 (time scale → 0.001x)
  - LLM에 차량 상태 스냅샷 전달 → 판단 요청
  - 응답 파싱 → 명령 실행 → 시뮬레이션 재개 (time scale → 1.0x)
  - 쿨다운 5초 (중복 발동 방지)

#### 2.3 통합 명령 포맷
- LLM 출력을 차량 제어로 변환하는 명령 체계 설명
- 명령 형식:
  ```
  DM.Gas = <value> | <duration_ms>
  DM.Brake = <value> | <duration_ms>
  DM.Steer.Ang = <value> | <duration_ms>
  wait <milliseconds>
  wait_until <condition>
  ```
- 설계 원칙: 단순성 (LLM이 생성하기 쉬운 포맷), 순차 실행, 조건부 대기 지원

### 3. 실험 환경 및 방법 (~1.5p)

**목표**: 재현 가능한 실험 설정 기술

#### 3.1 시뮬레이션 환경
- **Fig.3**: CarMaker 시뮬레이션 스크린샷 또는 시나리오 도식
- CarMaker 버전, 차량 모델, 도로 환경 명시
- TCP 통신 기반 실시간 제어 방식

#### 3.2 동적 프롬프트 설계
- **Table 1**: 프롬프트 구성 요소

| 구성 요소 | 역할 | 예시 |
|-----------|------|------|
| System Message | AI 기본 행동 정의 | "자율주행 판단 전문가로서..." |
| Character | 판단 성향/톤 설정 | "안전 우선 보수적 판단" |
| Command Template | 명령 포맷 지시 | "DM.Gas = value \| duration 형식으로..." |
| User Info | 차량/환경 컨텍스트 | 차량 제원, 도로 조건 |
| Vehicle State | 실시간 텔레메트리 | 속도, 가속도, 조향각 스냅샷 |

- 프롬프트 조합 방식: DB 저장 → 런타임 조립 → Claude CLI 전달
- 모듈식 설계의 장점: 시나리오별 프롬프트 교체 가능

#### 3.3 평가 시나리오 및 지표
- 시나리오 정의 (2개):
  - **S1 — 추월 (트리거 검증)**: 저속 선행 차량 추월. 트리거 → LLM 판단 → 차선변경/가속/복귀. 시스템 기본 동작 검증 목적.
  - **S2 — 긴급 추돌 회피 (3-way 비교)**: 선행 차량 급정지 상황에서 세 가지 방식 비교:
    - **Rule-based**: 사전 정의된 고정 제동 규칙
    - **LLM Single-shot**: 트리거 발동 → LLM 1회 판단 → 명령 실행
    - **LLM Feedback Loop**: LLM 판단 → 실행 → 변화된 상태 재전달 → 추가 판단 반복
- 평가 지표:
  - LLM 응답 시간 (ms)
  - 명령 파싱 성공률 (%)
  - 충돌 회피 성공률 (%)
  - 최대 감속도 (m/s²)
  - 최소 차간 거리 (m)

### 4. 실험 결과 (~1.5p)

**목표**: S1 트리거 검증 + S2 3-way 비교 분석

#### 4.1 S1: 추월 — 트리거 검증
- **Fig.4**: 추월 시나리오 차량 상태 변화 (속도, 횡방향 위치)
  - 트리거 발동 시점, LLM 명령 실행 구간 표시
- LLM이 생성한 추월 명령 시퀀스 예시
- 트리거-LLM-실행 파이프라인 정상 동작 확인

#### 4.2 S2: 긴급 추돌 회피 — 3-way 비교
- **Fig.5**: 세 가지 방식 비교 그래프 (Rule / Single-shot / Feedback Loop 중첩)
- **Table 2**: 제어 방식별 정량 비교

| 평가 지표 | Rule-based | LLM Single-shot | LLM Feedback Loop |
|-----------|-----------|-----------------|-------------------|
| 충돌 회피 성공률 (%) | - | - | - |
| 최대 감속도 (m/s²) | - | - | - |
| 최소 차간 거리 (m) | - | - | - |
| LLM 응답 시간 (ms) | --- | - | - |
| LLM 호출 횟수 | --- | 1 | - |

- 핵심 비교: Single-shot vs Feedback Loop의 판단 품질 차이

#### 4.3 논의
- 트리거 기반 일시정지 전략의 효과 (LLM 지연 → 안전성 영향 제거)
- Feedback Loop의 점진적 판단 개선 효과
- Feedback Loop의 트레이드오프: 총 응답 시간 증가, 일시정지 시간 연장
- 프롬프트 구성 변경에 따른 판단 차이

### 5. 결론 (~0.5p)

- 주요 성과 요약 (3개 기여점 재확인)
- 한계:
  - LLM 응답 지연 (실시간 제어 제약)
  - 시뮬레이션 환경에서만 검증
  - 단일 LLM (Claude) 기반 실험
- 향후 연구:
  - 실차/HiL 환경 확장
  - 멀티모달 입력 (카메라, LiDAR 데이터) 통합
  - 다중 LLM 비교 및 경량 모델 적용

---

## Figure/Table 목록

| # | 유형 | 내용 | 크기 |
|---|------|------|------|
| Fig.1 | 시스템 구성도 | 전체 아키텍처 (트리거→LLM→제어) | 2-column 폭 |
| Fig.2 | 플로우차트 | 트리거 제어 루프 상세 | 1-column 폭 |
| Fig.3 | 스크린샷/도식 | CarMaker 시뮬레이션 환경 | 1-column 폭 |
| Fig.4 | 시계열 그래프 | S1 추월: 속도, 횡방향 위치 | 1-column 폭 |
| Fig.5 | 비교 그래프 | S2 추돌회피: Rule vs Single vs Feedback | 1-column 폭 |
| Table 1 | 표 | 프롬프트 구성 요소 | 1-column 폭 |
| Table 2 | 표 | S2 제어 방식별 정량 비교 | 1-column 폭 |

---

## 작성 규칙

### 형식
- LaTeX 템플릿: `elsarticle` 클래스, 2단 레이아웃, 9pt
- 한국어 본문 + 영문 Abstract, Keywords, Table caption, Figure caption(한글)
- 수식 번호: `\label{eq:xxx}` + `Eq.~\ref{eq:xxx}`
- 그림/표 참조: `Figure~\ref{fig_xxx}`, `Table~\ref{tab_xxx}`
- 참고문헌: `elsarticle-num` 스타일 (번호순)

### 용어 통일
| 용어 | 사용 | 비사용 |
|------|------|--------|
| LLM | 대규모 언어모델 (LLM) | 대형 언어모델, 거대 언어모델 |
| CarMaker | CarMaker | 카메이커, carmaker |
| 트리거 | 트리거 | 트리거링, trigger |
| 시뮬레이션 | 시뮬레이션 | 시뮬레이팅 |
| 프롬프트 | 프롬프트 | 프람프트 |
| 텔레메트리 | 텔레메트리 | 원격 측정 |
| 에이전트 | 에이전트 | 에이전트 시스템 |

### Keywords (영문+한문 병기)
```
Large language model(대규모 언어모델) \sep
Autonomous driving(자율주행) \sep
CarMaker simulation(CarMaker 시뮬레이션) \sep
Trigger-based control(트리거 기반 제어) \sep
Vehicle decision-making(차량 의사결정) \sep
Dynamic prompt system(동적 프롬프트 시스템)
```

### 참고문헌 방향 (최소 8~12편)
- LLM for autonomous driving (최신 2023-2025)
- CarMaker simulation 관련
- Rule-based / RL 기반 자율주행 의사결정
- Prompt engineering 관련
- 자동차공학회 기존 논문 (국내 관련 연구)

---

## 프로젝트 코드 참조

논문 작성 시 실제 구현 내용 참조할 파일:

| 논문 내용 | 참조 파일 |
|-----------|----------|
| 트리거 모니터링 | `src/lib/stores/triggerMonitor.svelte.ts` |
| 명령 파서 | `src/lib/actions/vehicleCommandParser.ts` |
| 명령 실행기 | `src/lib/actions/vehicleCommandExecutor.ts` |
| CarMaker 통신 | `src/lib/stores/carmakerStore.svelte.ts` |
| 프롬프트 빌더 | `src-tauri/src/ai/prompt_builder.rs` |
| Claude CLI 연동 | `src-tauri/src/ai/claude_cli.rs` |
| 트리거 조건 평가 | `src/lib/utils/triggerEvaluator.ts` |
