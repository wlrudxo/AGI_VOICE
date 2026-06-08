# ICCAS 2026 Paper Writing Guide

## 기본 방향

본 논문은 CarMaker-Simulink 기반 주행 시뮬레이션에서 MPC 제어기 튜닝을 자동화하고, 제한된 시뮬레이션 예산 안에서 탐색 방법의 효율을 비교하는 연구로 작성한다.

핵심 메시지는 다음과 같다.

- MPC 제어기 구조 자체가 새로운 것이 아니라, 고정된 MPC 제어기의 가중치 튜닝을 대상으로 한다.
- 각 후보 파라미터는 한 번의 시뮬레이션으로 평가되며, 결과는 하나의 목적함수 값으로 환산된다.
- 비교 대상은 무작위/공간충진 탐색, Bayesian Optimization, LLM 기반 후보 제안, 그리고 LLM-assisted BO이다.
- LLM은 차량을 직접 제어하는 저수준 제어기가 아니라, 실험 결과를 해석하고 다음 탐색 후보 또는 탐색 영역을 제안하는 보조 최적화 모듈로 설명한다.

논문은 최대 6페이지 제한을 고려하여, 구현 세부사항보다 문제 정의, 수식화, 실험 프로토콜, 결과 비교에 집중한다.

## 작성 원칙

### 피해야 할 것

- 실제 코드 파일명, 함수명, 내부 변수명, CLI 옵션명을 본문에 길게 나열하지 않는다.
- 특정 random seed, 파일 경로, MATLAB engine 이름, 로컬 PC 환경명 등 재현 로그 수준의 세부 구현은 본문에 쓰지 않는다.
- section/subsection을 과도하게 늘리지 않는다.
- 강화학습을 주요 비교군으로 넣지 않는다. 본 연구는 state-action policy learning이 아니라 static controller-parameter tuning이다.
- LLM이 직접 steering command를 생성하는 것처럼 쓰지 않는다.

### 써야 할 것

- 튜닝 문제를 수식으로 명확히 정의한다.
- 평가 목적함수를 수식으로 제시한다.
- 탐색 방법별 차이를 같은 예산 조건에서 비교한다.
- LLM의 역할은 `reasoning-guided optimizer assistance`로 제한한다.
- 구현 상세는 “자동화된 시뮬레이션 평가 파이프라인” 수준으로 추상화한다.

## 권장 논문 구조

6페이지 제한을 고려하여 본문은 5개 section 정도로 제한한다.

```text
1. Introduction
2. Problem Formulation and Simulation-Based Objective
3. LLM-Assisted Bayesian Optimization Framework
4. Experimental Setup
5. Results and Discussion
6. Conclusion
```

Related work는 별도 section으로 길게 두기보다 Introduction 후반 또는 각 section 첫 문단에 짧게 녹인다. 필요하면 `Related Work`를 독립 section으로 만들 수 있지만, 6페이지 제한에서는 우선순위를 낮춘다.

## Section별 작성 지침

### 1. Introduction

목표: 연구 필요성과 기여를 짧고 명확하게 제시한다.

포함할 내용:

- 고정된 MPC 제어기도 실제 주행 시뮬레이션에서는 가중치 튜닝이 성능에 큰 영향을 준다.
- 고충실도 시뮬레이션은 한 번의 평가 비용이 크므로, 무작정 많은 후보를 평가하기 어렵다.
- BO는 비미분 black-box 목적함수에 적합하지만, 초기 후보와 탐색 영역 설정이 결과에 영향을 준다.
- LLM은 실험 로그와 결과를 해석하여 탐색을 보조할 수 있다.

기여점 예시:

```text
1. CarMaker-Simulink 기반 MPC weight tuning 문제를 black-box optimization 문제로 정식화하였다.
2. pylon hit, tracking error, yaw response, steering smoothness를 포함한 fail-closed objective를 정의하였다.
3. 동일한 simulation budget에서 LHC/random, BO, LLM-only, LLM-assisted BO를 비교하는 실험 프로토콜을 제안하였다.
```

### 2. Problem Formulation and Simulation-Based Objective

목표: 연구 문제를 코드가 아니라 수식으로 설명한다.

MPC weight vector는 다음처럼 표현한다.

```latex
\theta =
\left[
q_y,\,
q_\psi,\,
q_r,\,
r_\delta,\,
r_{\Delta\delta}
\right]^\top
```

본문에서는 각 항의 의미만 설명한다.

```text
q_y: lateral tracking error weight
q_\psi: heading error weight
q_r: yaw-rate-related response weight
r_\delta: steering effort weight
r_{\Delta\delta}: steering-rate smoothness weight
```

탐색 문제는 다음처럼 쓴다.

```latex
\theta^\star =
\arg\min_{\theta \in \Theta} J(\theta)
```

여기서 `J(theta)`는 한 번의 CarMaker-Simulink closed-loop simulation을 수행한 뒤 계산되는 scalar objective라고 설명한다.

목적함수는 너무 복잡하게 쓰지 말고, 항의 의미가 드러나도록 정리한다.

```latex
J(\theta)
=
w_f I_{\mathrm{fail}}
+ w_p N_{\mathrm{pylon}}
+ w_y \mathrm{RMSE}(e_y)
+ w_{\bar{y}} \max |e_y|
+ w_\psi \mathrm{RMSE}(e_\psi)
+ w_r \max |r|
+ w_\delta \mathrm{RMSE}(\delta)
+ w_{\Delta\delta} \mathrm{RMSE}(\Delta\delta).
```

본문에서는 각 항을 다음처럼 설명한다.

- `I_fail`: simulation abort 또는 invalid run에 대한 penalty
- `N_pylon`: pylon contact count
- `e_y`: lateral tracking error
- `e_psi`: heading error
- `r`: yaw rate
- `delta`: steering command
- `Delta delta`: steering command rate or difference

세부 normalization 값은 본문에 모두 쓰지 않아도 된다. 필요하면 table에 대표 scaling만 정리한다.

### 3. LLM-Assisted Bayesian Optimization Framework

목표: 알고리즘 구조를 설명한다.

포함할 내용:

- 각 iteration에서 optimizer가 하나의 후보 `theta_k`를 제안한다.
- 시뮬레이터가 `J(theta_k)`와 주요 metrics를 반환한다.
- BO는 누적 데이터셋을 이용해 surrogate model을 갱신한다.
- LLM-only는 surrogate 없이 실험 기록을 읽고 다음 후보를 제안한다.
- Hybrid BO는 BO 후보와 LLM의 해석/제안을 결합한다.

데이터셋 표현:

```latex
\mathcal{D}_n =
\{(\theta_i, J_i)\}_{i=1}^{n}
```

BO의 surrogate/acquisition은 간단히 쓴다.

```latex
\theta_{n+1}
=
\arg\max_{\theta \in \Theta}
a(\theta;\mathcal{D}_n)
```

여기서 `a`는 expected improvement 또는 유사한 acquisition function으로 설명한다.

LLM 역할은 다음 세 가지 정도로 제한한다.

```text
1. failed or unsafe trial diagnosis
2. promising region suggestion
3. candidate ranking or warm-start proposal
```

코드 실행 방식, 로그 파일명, local folder 구조는 본문에서 제외한다.

### 4. Experimental Setup

목표: 독자가 실험 조건과 비교 공정성을 이해할 수 있게 한다.

포함할 내용:

- 시뮬레이터: CarMaker-Simulink co-simulation
- 시나리오: standard slalom maneuver with pylons
- 차량 제어: steering command through MPC lateral controller
- 고정 조건: MPC structure, prediction/control horizon, steering physical constraints
- 튜닝 대상: 5개 weight only
- 평가 예산: method당 최대 100 simulation trials

탐색 방법은 table로 간단히 정리한다.

```text
Method               Description
IPG Driver           built-in driver/reference baseline
Random Search        random sampling in the same search space
LHC                  space-filling non-adaptive baseline
BO                   initial design + sequential surrogate-based search
LLM-only             LLM proposes candidates from previous results
LLM-assisted BO      BO with LLM-guided diagnosis or region suggestion
```

BO 예산은 다음처럼 개념적으로만 쓴다.

```text
BO uses an initial space-filling design followed by sequential BO updates.
```

본문에는 특정 seed 번호를 쓰지 않는다. 반복 실험 평균을 낼 때는 “multiple independent runs with fixed seeds” 정도로 표현한다.

### 5. Results and Discussion

목표: 최종 실험 결과가 나오면 6페이지 안에 들어갈 핵심 결과만 제시한다.

필수 figure/table:

```text
Fig. 1: Overall framework diagram
Fig. 2: Slalom scenario and evaluation signals
Fig. 3: Best objective vs. iteration
Fig. 4: Best trajectory and steering comparison
Table 1: Search space and tuned MPC weights
Table 2: Method comparison summary
```

결과에서 강조할 것:

- pylon hit를 0으로 줄이는지
- 같은 trial budget에서 best objective가 얼마나 빨리 감소하는지
- BO가 LHC/random 대비 early-stage sample efficiency를 보이는지
- LLM-assisted BO가 unsafe/repeated bad trials를 줄이는지
- LLM-only가 BO만큼 안정적인지는 별도로 판단한다

결과 해석은 다음 순서로 쓴다.

```text
1. completion and safety: SIM_END, pylon hits
2. tracking quality: RMSE/max lateral error
3. control smoothness: steering command/rate
4. sample efficiency: convergence curve
5. method-level interpretation
```

### 6. Conclusion

목표: 기여와 한계를 짧게 요약한다.

포함할 내용:

- simulator-in-the-loop MPC tuning framework를 구축했다.
- pylon hit와 tracking/control metrics를 포함한 objective로 비교했다.
- BO와 LLM-assisted BO의 sample efficiency를 평가했다.
- 한계: 단일 시나리오, 고정 MPC 구조, 시뮬레이션 기반 검증
- 향후 연구: low-friction stress test, more driving scenarios, policy-learning formulation if RL is considered

## 수식 사용 지침

최소한 아래 수식은 넣는 것이 좋다.

1. 튜닝 벡터

```latex
\theta =
\left[
q_y,\,
q_\psi,\,
q_r,\,
r_\delta,\,
r_{\Delta\delta}
\right]^\top
```

2. black-box optimization problem

```latex
\theta^\star =
\arg\min_{\theta \in \Theta} J(\theta)
```

3. dataset

```latex
\mathcal{D}_n =
\{(\theta_i, J_i)\}_{i=1}^{n}
```

4. acquisition-based next candidate

```latex
\theta_{n+1}
=
\arg\max_{\theta \in \Theta}
a(\theta;\mathcal{D}_n)
```

5. objective function

```latex
J(\theta)
=
w_f I_{\mathrm{fail}}
+ w_p N_{\mathrm{pylon}}
+ w_y \mathrm{RMSE}(e_y)
+ w_{\bar{y}} \max |e_y|
+ w_\psi \mathrm{RMSE}(e_\psi)
+ w_r \max |r|
+ w_\delta \mathrm{RMSE}(\delta)
+ w_{\Delta\delta} \mathrm{RMSE}(\Delta\delta)
```

수식은 연구를 깔끔하게 보이게 하되, 너무 많은 세부 구현항을 넣어 읽기 어렵게 만들지 않는다.

## 지면 배분

최대 6페이지 기준 권장 분량:

```text
Abstract + title block: 0.4 p
1. Introduction: 0.8 p
2. Problem Formulation: 0.9 p
3. Framework: 1.1 p
4. Experimental Setup: 0.9 p
5. Results and Discussion: 1.5 p
6. Conclusion: 0.4 p
References: remaining space
```

Related work는 Introduction과 각 section의 첫 문단에 압축해서 넣는다.

## 용어 통일

```text
Bayesian Optimization (BO)
Large Language Model (LLM)
Model Predictive Control (MPC)
Latin Hypercube Sampling (LHC)
simulator-in-the-loop
black-box optimization
pylon hit
lateral tracking error
steering smoothness
fail-closed objective
```

## 현재 초안 수정 방향

현재 `ICCAS202601.tex` 초안은 구조를 넓게 잡아둔 상태다. 실제 6페이지 논문으로 줄일 때는 다음처럼 압축한다.

- `Related Work`는 독립 section에서 빼고 Introduction 또는 Framework 앞부분으로 흡수한다.
- `Problem Formulation`과 `Objective`는 하나의 section으로 합친다.
- `Optimization Methods`는 Framework section 안의 subsection으로 줄인다.
- `Preliminary Results`는 최종 실험 후 `Results and Discussion`으로 교체한다.
- 구현 파일명, CLI명, local path, seed 번호는 제거한다.
