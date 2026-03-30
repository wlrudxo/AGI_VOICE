# Metacognitive Agentic Research Plan

## One-Line Thesis

목표 달성을 위해 연구 반복수행 개선을 스스로 운영하는 agent 시스템을 구축하고,
자율주행 safety filter 생성/개선을 대표 application으로 검증한다.


## Background

기존 LLM 기반 자율주행 연구는 주로 다음 중 하나에 집중한다.

- high-level planning
- verbal reflection
- retrieval-based answering
- controller parameter suggestion

이 경우 LLM은 대체로 사람이 설계한 고정 파이프라인 안에서 하나의 역할만 수행한다.

하지만 실제 연구 workflow는 다르다.

- 목표를 받는다
- 현재 상태와 결과를 관찰한다
- 무엇을 바꿀지 결정한다
- 수정안을 적용한다
- 다시 실행한다
- 결과를 평가한다
- 필요하면 다시 수정한다

즉 중요한 것은 단일 응답 생성기가 아니라, 목표 달성을 위해 반복개선 루프를 스스로 운영하는 agent 시스템이다.


## Core Research Problem

고충실도 시뮬레이터에서 LLM agent가 주어진 tool/skill만으로:

- 관측
- 개입
- 제어
- 규칙 설정
- 반복 실행
- 결과 평가
- 수정

를 조합하여, 목표 지향적 연구 반복개선 루프를 스스로 구성하고 운영할 수 있는가?


## Main Idea

CarMaker 기능을 skill로 노출하고, LLM agent가 이를 사용해 고정된 절차가 아니라 상황 의존적으로 루프를 운영하게 한다.

이때 시스템의 핵심은 다음이다.

- 사람이 세부 루프를 하드코딩하지 않는다
- agent가 어떤 skill을 언제 호출할지 결정한다
- agent가 자신의 이전 실행 결과를 보고 다음 수정 방향을 정한다
- 이 자기평가와 수정의 2차 루프를 metacognitive process로 정의한다


## Operational Definition of Metacognition

본 연구에서 metacognition은 다음을 의미한다.

- agent가 자기 산출물(규칙, 개입 전략, safety filter)의 수행 결과를 감시한다
- 시뮬레이터 metric에 기반해 그 산출물의 질을 평가한다
- 그 평가 결과에 따라 유지, 수정, 폐기를 결정한다

즉,

- 1차 수준: 규칙 생성과 실행
- 2차 수준: 생성한 규칙의 자기평가와 수정

으로 나뉘며, 본 연구는 이 2차 수준을 명시적으로 시스템에 포함한다.


## System Contribution

### 1. Skillized High-Fidelity Simulation Substrate

CarMaker 기반 기능을 agent가 호출 가능한 skill 집합으로 통합한다.

예시 skill 범주:

- observation
  - telemetry 조회
  - object watch 추가/제거
  - scenario state 조회
- intervention
  - pause/resume
  - reset/restart
  - rerun
- control
  - command 전송
  - tactical override 적용
- rule management
  - rule 생성
  - rule 수정
  - rule 활성/비활성
  - rule 저장
- evaluation
  - TTC, collision risk, lane departure, completion time 등 metric 수집
  - run result 요약

핵심은 단순 API 래핑이 아니라, 반복개선 workflow를 실행 가능한 최소 행동 단위로 skill을 구성하는 것이다.


### 2. Agent-Orchestrated Iterative Improvement Loop

LLM agent는 다음을 스스로 결정한다.

- 어떤 신호를 추가로 관측할지
- 언제 실험을 중단할지
- 어떤 규칙을 생성/수정할지
- 어떤 결과를 근거로 다음 반복을 수행할지

즉, 시스템은 fixed pipeline이 아니라 agent-directed loop orchestration을 지원한다.


### 3. Goal-Driven Research Automation

연구자는 세부 제어 절차 대신 목표를 부여한다.

예:

- "앞차를 안전하게 추월해라"
- "충돌 없이 차선 변경을 수행해라"
- "현재 failure pattern을 줄여라"

그 후 agent는 skill을 사용하여 실험-평가-수정-재실행 과정을 자율적으로 수행한다.


## Application Contribution

### Metacognitive Safety Filter Synthesis and Refinement

제안 시스템의 대표 application으로 safety filter 생성/개선을 사용한다.

설정:

- base driver는 블랙박스 또는 수정이 어려운 기존 driver
- LLM agent는 base driver 위에 얹히는 safety filter를 생성
- filter는 조건 -> 행동 형태의 tactical/safety rule 집합

예시:

- `if rear_left_ttc < threshold then block_lane_change`
- `if front_gap shrinks rapidly then throttle_inhibit + mild_brake`
- `if overtake timeout exceeds bound then abort_and_return`

여기서 메타인지는 다음 루프에 걸린다.

- 생성한 rule 실행
- simulator-grounded metric으로 자기 rule 평가
- rule 수정 또는 확정
- 누적된 rule set을 다음 실행에 반영


## Why Safety Filter Is a Good Validation Task

safety filter는 다음 이유로 application 검증 task로 적절하다.

- base driver를 직접 재학습하지 않고도 외부 보완이 가능하다
- 규칙이 해석 가능하다
- 생성/검증/수정 루프를 명확히 설계할 수 있다
- 동일 시스템이 다른 maneuver에도 확장될 가능성을 보여주기 쉽다


## Research Questions

### RQ1

고충실도 시뮬레이터 기능을 skill화하면, LLM agent가 목표 지향적 반복개선 workflow를 스스로 구성하고 운영할 수 있는가?


### RQ2

agent-directed iterative loop는 사람이 고정한 one-shot 또는 static pipeline보다 더 효과적인 개선을 달성하는가?


### RQ3

제안 시스템은 safety filter 생성/개선 task에서 base driver 단독, hand-crafted rule, one-shot LLM rule generation보다 더 나은 안전성과 임무 성공률을 보이는가?


## Hypothesis

- H1: skillized simulation substrate는 agent의 closed-loop experimentation을 가능하게 한다
- H2: metacognitive self-evaluation이 없는 one-shot rule generation보다 iterative refinement가 더 좋다
- H3: 누적된 safety filter rule set은 base driver의 residual risk를 줄인다


## Proposed Workflow

1. 목표와 시나리오를 입력으로 받는다
2. agent가 필요한 skill 호출 계획을 세운다
3. observation skill로 현재 상태와 관련 객체를 파악한다
4. base driver 실행 결과를 수집한다
5. 위험상황 또는 failure pattern을 감지한다
6. rule management skill로 보완 규칙 또는 safety filter 후보를 생성한다
7. intervention/control skill로 수정된 실행을 수행한다
8. evaluation skill로 결과 metric을 수집한다
9. agent가 자기 규칙의 질을 평가한다
10. 규칙을 수정, 확정, 폐기 중 하나로 처리한다
11. 필요 시 다음 반복을 수행한다


## Metrics for Self-Evaluation

초기 버전에서는 다음 축을 사용한다.

- safety
  - collision
  - TTC min
  - AEB activation
- stability
  - lane departure
  - steering oscillation
  - harsh brake
- task completion
  - success/failure
  - elapsed time
- intervention quality
  - unnecessary override
  - over-conservative behavior

이 metric은 agent의 metacognitive monitoring에 사용된다.


## Experimental Design

### Base Comparisons

- base driver only
- base driver + hand-crafted safety rules
- base driver + one-shot LLM rule generation
- base driver + metacognitive iterative safety filter refinement


### System-Level Comparisons

- fixed human-designed loop
- agent-orchestrated loop


### Ablations

- no self-evaluation
- no rule accumulation
- no signal selection
- no rule reuse
- no intervention skills


## Scope Control

이번 단계에서 하지 않는 것:

- full co-evolution of adversarial environment and agent
- RL reward shaping
- end-to-end driver retraining
- 모든 maneuver 동시 지원

이번 단계에서 하는 것:

- 동일 또는 소수의 고정 시나리오
- 반복개선 loop 구현
- safety filter를 통한 유효성 검증


## Relation to the Other Research Track

별도 꼭지로 진행 중인 `RAG 기반 적대적 주행환경 생성`과의 관계는 다음과 같다.

- adversarial environment generation:
  - agent를 깨뜨리는 환경 생성
- metacognitive agentic improvement system:
  - 깨진 agent를 반복개선하는 연구 시스템

즉 프로그램 수준에서는:

- attack: adversarial scenario generation
- defense: metacognitive iterative improvement

구조를 이룬다.


## Expected Paper Framing

### Main Paper Message

우리는 시뮬레이터 기반 skill을 활용하여 목표 달성을 위한 연구 반복수행 개선 루프를 스스로 운영하는 agent 시스템을 제안하고, safety filter 생성/개선을 통해 그 유효성을 검증한다.


### Suggested Title Directions

- Metacognitive Agentic Research System for Iterative Driving Improvement
- Skillized Simulation Substrate for Goal-Driven Agentic Driving Research
- Metacognitive Iterative Improvement with Skill-Based High-Fidelity Simulation


## Near-Term Implementation Plan

### Phase 1

- skill taxonomy 확정
- observation / intervention / control / rule / evaluation skill 최소 집합 정의


### Phase 2

- 동일 시나리오에서 반복개선 loop 구현
- base driver + rule injection 구조 완성


### Phase 3

- self-evaluation metric summary 구현
- rule 확정/수정/폐기 decision loop 구현


### Phase 4

- safety filter application 실험
- baseline 비교
- 실패 사례 분석


## Immediate Next Decisions

- 첫 maneuver를 무엇으로 할지 결정
  - overtake
  - lane change
  - emergency avoidance
- rule schema를 얼마나 제한할지 결정
- self-evaluation summary 포맷을 어떻게 정할지 결정
- agent loop 종료 조건을 어떻게 둘지 결정


## Current Recommendation

첫 실험은 overtake 또는 lane change 중 하나로 제한하고,

- base driver는 고정
- safety filter rule schema는 단순한 조건 -> 행동 형태로 제한
- iterative improvement loop가 실제로 닫히는지 먼저 검증

하는 것이 가장 현실적이다.
