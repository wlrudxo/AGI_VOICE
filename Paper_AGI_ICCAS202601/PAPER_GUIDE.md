# ICCAS 2026 Paper Writing Guide

## 기본 방향

본 논문은 CarMaker-Simulink 기반 주행 시뮬레이션에서 MPC 제어기 튜닝을 자동화하고, 제한된 시뮬레이션 예산 안에서 탐색 방법의 효율을 비교하는 연구로 작성한다.

핵심 메시지는 다음과 같다.

- MPC 제어기 구조 자체가 새로운 것이 아니라, 고정된 MPC 제어기의 가중치 튜닝을 대상으로 한다.
- 각 후보 파라미터는 한 번의 시뮬레이션으로 평가되며, 결과는 하나의 목적함수 값으로 환산된다.
- 비교 대상의 중심은 무작위/공간충진 탐색, Bayesian Optimization, LLM-based 후보 제안이다.
- Sobol은 optimizer baseline이 아니라 4D search landscape audit 용도로 사용한다.
- BO-advised LLM은 메인 성능 주장보다, naive hybrid가 BO exploration과 충돌할 수 있음을 보여주는 preliminary diagnostic으로 둔다.
- LLM은 차량을 직접 제어하는 저수준 제어기가 아니라, 실험 결과를 해석하고 다음 탐색 후보 또는 탐색 영역을 제안하는 보조 최적화 모듈로 설명한다.
- 현재 핵심 메시지는 "LLM-based는 물리적으로 그럴듯한 feasible region에 빠르게 도달하고 local refinement를 잘하지만, BO/Sobol은 LLM이 잘 고르지 않는 비직관 feasible local region을 발견할 수 있다"이다.
- 단순 LLM+BO 결합은 자동으로 좋아지지 않으며, LLM이 BO proposal의 gatekeeper가 되면 비직관 exploration을 약화시킬 수 있다는 cautionary finding을 discussion에 둔다.
- 현재 주 실험은 nominal slalom, 4D MPC weight tuning이다. 내부 로그의 `V61` 같은 시나리오 식별자는 논문 본문에 직접 쓰지 않는다. `q_r`은 0으로 고정하고, `q_y`, `q_\psi`, `r_\delta`, `r_{\Delta\delta}`만 탐색한다.

논문은 최대 6페이지 제한을 고려하여, 구현 세부사항보다 문제 정의, 수식화, 실험 프로토콜, 결과 비교에 집중한다.

## 작성 원칙

### 피해야 할 것

- 실제 코드 파일명, 함수명, 내부 변수명, CLI 옵션명을 본문에 길게 나열하지 않는다.
- 특정 random seed, 파일 경로, MATLAB engine 이름, 로컬 PC 환경명 등 재현 로그 수준의 세부 구현은 본문에 쓰지 않는다.
- `bo_0049`, `lhc_0050` 같은 run identifier도 논문 본문 표에는 쓰지 않는다. 이런 식별자는 별도 결과 보고서나 실험 로그에만 남긴다.
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
3. Calibration Search Framework
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
2. road departure, evaluated pylon hit, lateral/heading tracking error를 포함한 scalar objective를 정의하고, yaw/steering metric은 진단용으로 기록하였다.
3. 동일한 simulation budget에서 LHC/random, BO, LLM-based를 비교하고, Sobol audit으로 feasible local-region 구조를 분석하였다.
4. BO-advised LLM preliminary run을 통해 naive gatekeeping hybrid의 한계를 관찰하였다.
```

### 2. Problem Formulation and Simulation-Based Objective

목표: 연구 문제를 코드가 아니라 수식으로 설명한다.

현재 원고의 MPC tuning vector는 다음처럼 표현한다.

```latex
\theta =
\left[
q_y,\,
q_\psi,\,
r_\delta,\,
r_{\Delta\delta}
\right]^\top
```

본문에서는 각 항의 의미만 설명한다.

```text
q_y: lateral tracking error weight
q_\psi: heading error weight
r_\delta: steering effort weight
r_{\Delta\delta}: steering-rate smoothness weight
```

`q_r`은 MPC output-weight matrix에는 남아 있지만, 현재 formal comparison에서는 `q_r=0`으로 고정한다고 설명한다. `q_r`을 튜닝 변수처럼 쓰지 않는다.

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
100 I_{\mathrm{fail}}
+ 10 N_{\mathrm{pylon}}
+ 4\,\mathrm{RMSE}(e_y)
+ 0.5\,\|e_y\|_{\infty}
+ 5\,\mathrm{RMSE}(e_\psi).
```

본문에서는 각 항을 다음처럼 설명한다.

- `I_fail`: road departure에 대한 penalty
- `N_pylon`: evaluated pylon contact count, entry contact는 무시
- `e_y`: lateral tracking error
- `e_psi`: heading error
- `r`, `delta`, `Delta delta`: objective에는 0 weight이고 진단/plot용 metric으로만 기록

현재 코드에서는 별도 normalization 없이 위 계수를 그대로 사용한다.

### 3. Calibration Search Framework

목표: 알고리즘 구조를 설명한다.

포함할 내용:

- 각 iteration에서 optimizer가 하나의 후보 `theta_k`를 제안한다.
- 시뮬레이터가 `J(theta_k)`와 주요 metrics를 반환한다.
- BO는 누적 데이터셋을 이용해 surrogate model을 갱신한다.
- LLM-based는 surrogate 없이 실험 기록을 읽고 다음 후보를 제안한다.
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
- 튜닝 대상: 4개 weight only (`q_r=0` fixed)
- 평가 예산: method/run당 50 simulation trials

탐색 방법은 table로 간단히 정리한다.

```text
Method               Description
IPG Driver           built-in driver/reference baseline
Random Search        random sampling in the same search space
LHC                  space-filling non-adaptive baseline
BO                   initial design + sequential surrogate-based search
LLM-based            LLM proposes candidates from previous results
BO-advised LLM      BO with LLM-guided diagnosis or region suggestion
```

BO 예산은 다음처럼 쓴다.

```text
BO uses a 15-trial initial design followed by sequential BO updates under a 50-trial budget.
```

본문에는 특정 seed 번호를 쓰지 않는다. 반복 실험 평균을 낼 때는 “multiple independent repetitions” 또는 “independent runs under matched stochastic settings” 정도로 표현한다.

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
- LLM-based가 feasible zero-hit region을 얼마나 빨리 찾는지
- BO가 LLM-based보다 낮은 objective local region을 찾는지
- BO-advised LLM가 LLM-based의 feasibility와 BO의 global exploration을 동시에 살리는지
- BO-advised LLM의 BO proposal accept/modify/reject 비율과 각 action의 결과가 어떤지

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
- pylon hit와 lateral/heading tracking metrics를 포함한 objective로 비교하고, control metrics는 진단용으로 기록했다.
- BO와 LLM-based의 sample efficiency를 평가했다. BO-advised LLM은 diagnostic case로만 보고한다.
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
r_\delta,\,
r_{\Delta\delta}
\right]^\top
```

`q_r=0` fixed라는 문장을 바로 붙인다.

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
100 I_{\mathrm{fail}}
+ 10 N_{\mathrm{pylon}}
+ 4\,\mathrm{RMSE}(e_y)
+ 0.5\,\|e_y\|_{\infty}
+ 5\,\mathrm{RMSE}(e_\psi)
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
steering diagnostics
scalar objective
```

## 현재 초안 수정 방향

현재 `ICCAS202601.tex` 초안은 nominal slalom 4D baseline 결과와 BO-advised LLM diagnostic 결과를 반영한 상태다. 실제 6페이지 논문으로 줄일 때는 다음처럼 압축한다.

- `Related Work`는 독립 section에서 빼고 Introduction 또는 Framework 앞부분으로 흡수한다.
- `Problem Formulation`과 `Objective`는 하나의 section으로 합친다.
- `Optimization Methods`는 Framework section 안의 subsection으로 줄인다.
- `Results and Discussion`은 현재 baseline 결과를 유지하되, Hybrid 결과가 나오면 method-level summary와 best-trial table을 갱신한다.
- 구현 파일명, CLI명, local path, seed 번호는 제거한다.

## 현재 결과 요약 반영 기준

현재 논문에 반영할 수 있는 핵심 결과는 다음과 같다. 논문 본문에는 seed 번호나 run identifier를 쓰지 말고, 아래 숫자를 method-level aggregate로만 사용한다.

```text
Nominal 4D entry-ignored slalom MPC, 50 trials/run
BO: 5 independent runs, 250 trials, 4 successes, best J = 0.739914
LHC: 5 independent runs, 250 trials, 1 success, best J = 1.378332
Random: 5 independent runs, 250 trials, 0 successes, best J = 11.169761
LLM-based: 5 independent runs, 250 trials, 101 successes, best J = 1.176372
BO-advised LLM: 1 diagnostic run, 50 trials, 0 successes, best J = 11.398445
```

해석은 다음 선을 넘지 않는다.

- LLM-based는 5회 중 4회에서 feasible zero-hit solution을 빠르게 찾았지만, 1회는 one-hit local pocket에 머물렀다.
- BO는 성공률은 낮지만 현재 best objective를 찾았다.
- LLM-based는 성공하거나 near-feasible point를 찾은 뒤 같은 local region 주변을 exploit하는 경향이 있었다.
- BO-advised LLM은 naive gatekeeping hybrid가 BO exploration과 충돌할 수 있음을 보여주는 preliminary diagnostic으로 둔다.

## Zero-Hit Local Region Table 계획

논문 결과 section에는 method별 best만 나열하기보다, 모든 pylon-free trial을
4D log-scaled weight space에서 묶은 local region table을 추가하는 방향이 좋다.
중복되는 zero-hit point는 대표점만 제시한다.

현재 결과 기준:

```text
zero-hit points:
BO 4, LHC 1, Random 0, LLM-based 101, Sobol 2, BO-advised LLM 0
total 108
```

대표 local regions:

```text
R1 BO aggressive high-heading
  found by: BO
  rep J: 0.7399
  weights: q_y=13.321, q_psi=89.758, r_delta=0.0114, r_d_delta=0.0126

R2 LLM-based high-heading
  found by: LLM-based, BO
  zero-hit pts: 102
  rep J: 1.1764
  weights: q_y=80.000, q_psi=45.765, r_delta=0.1000, r_d_delta=0.8000

R3 low-heading mid-penalty
  found by: BO, LHC, Sobol
  zero-hit pts: 3
  rep J: 1.3714
  weights: q_y=56.001, q_psi=0.0459, r_delta=0.3501, r_d_delta=0.9510

R4 Sobol low-heading low-penalty
  found by: Sobol
  rep J: 1.3736
  weights: q_y=7.915, q_psi=0.0414, r_delta=0.0685, r_d_delta=0.1134

R5 BO low-heading high-q_y
  found by: BO
  rep J: 1.3848
  weights: q_y=86.585, q_psi=0.0406, r_delta=0.0209, r_d_delta=1.7583
```

해석:

- LLM-based는 high-heading local region을 조밀하게 exploitation했다.
- BO는 LLM-based region과 다른 aggressive high-heading best를 찾았다.
- BO/LHC/Sobol은 low-heading feasible local regions를 발견했다.
- Axis-wise local tolerance scan도 완료했다. 각 대표점에서 한 변수만
  `+-0.1, +-0.2, +-0.3, +-0.4` decade 움직이고 나머지 변수는 고정한 33회
  scan이다. 이는 full 4D robustness volume이 아니라 local sensitivity
  evidence로만 사용한다.
- 요약 결과:
  - R1 BO aggressive high-heading: best J=0.6993, zero-hit 9/33. `q_y`,
    `q_psi`는 민감하고, `r_delta`, `r_d_delta`는 lower-bound 방향에서만
    zero-hit 유지.
  - R2 LLM-based high-heading: best J=1.1764, zero-hit 2/33. 중심점 주변이
    좁고 `q_psi -0.1 decade`만 추가 zero-hit.
  - R3 low-heading mid-penalty: best J=1.3714, zero-hit 9/33. `q_psi`는
    `+-0.4 decade` 전체 허용, 나머지 축은 민감.
  - R4 Sobol low-heading low-penalty: best J=1.3736, zero-hit 9/33. R3와
    동일하게 `q_psi` 둔감, 나머지 축 민감.
  - R5 BO low-heading high-q_y: best J=1.3847, zero-hit 17/33. `q_psi`와
    `r_delta`는 `+-0.4 decade` 전체 허용, `q_y`와 `r_d_delta`는 민감.
- 논문에서는 "single basin" 같은 표현보다 separated local minimum areas with
  different local sensitivities라고 쓴다. R1은 sharp high-performance point,
  R5는 wider but higher-cost local minimum area로 설명 가능하다.

### 시나리오/목적함수 구조 해석 메모

이 결과는 모든 MPC tuning 문제에 일반화하기보다, 현재 slalom 시나리오와
목적함수 구조의 특성 안에서 해석한다.

- 현재 slalom은 연속 pylon 회피 문제라 steering timing의 작은 변화가 뒤쪽
  pylon contact로 증폭될 수 있다.
- 목적함수는 lateral/heading tracking error 같은 연속 지표와 pylon hit 같은
  discrete event penalty를 함께 포함한다.
- 따라서 objective landscape는 smooth한 단일 bowl 형태라기보다, 여러
  separated high-performing local minimum areas와 sharp optimum을 포함하는
  non-smooth closed-loop simulation objective로 해석하는 것이 적절하다.
- R1 BO best는 현재까지 가장 낮은 objective를 보였지만, 축방향 tolerance scan
  초기 결과상 `q_y`, `q_\psi` perturbation에 매우 민감하고 control penalty는
  lower-bound 부근에서만 pylon-free 성능이 유지되는 sharp solution으로 보인다.
- LLM-based는 물리적으로 그럴듯한 feasible region에 빠르게 도달하고 local
  refinement를 잘하지만, 이런 sharp/non-intuitive optimum이나 떨어진 local
  minimum area를 충분히 exploration하지 못할 수 있다.
- BO는 sample budget과 초기 design에 의존하지만, LLM이 직관적으로 잘 고르지
  않는 비직관적 high-performing region을 발견할 수 있다.

Discussion/Conclusion에서는 다음 정도로 제한적으로 주장한다.

```text
These findings do not imply that BO or LLM-based tuning is universally superior.
Rather, in an event-driven slalom calibration problem with discrete pylon-contact
penalties and sharp high-performing regions, LLM-based tuning can rapidly reach
physically plausible feasible settings but may concentrate around intuitive local
minimum areas. BO can discover less intuitive high-performance settings, although
their local tolerance may be narrow. Different control problems with smoother
objectives or wider feasible regions may lead to different method-level behavior.
```

## BO-Advised LLM 실험계획

Hybrid 실험은 다음처럼 쓴다.

```text
budget: 50 trials/run
trials 1-15: automatic LHC initialization
trials 16-50: BO proposal + LLM accept/modify/reject decision
```

보고할 추가 지표:

- BO proposal acceptance rate
- modification rate
- rejection rate
- action type별 success count와 best objective
- feasible local-region diversity
