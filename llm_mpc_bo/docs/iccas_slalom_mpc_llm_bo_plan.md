# ICCAS 6p Plan: LLM-Assisted BO for MPC Tuning in CarMaker-Simulink Slalom

작성일: 2026-06-04

## 0. 결론

ICCAS 6페이지 논문 방향은 다음으로 잡는다.

> CarMaker-Simulink co-simulation 환경에서 저마찰 slalom 주행을 대상으로 MPC 횡방향 제어기의 튜닝 파라미터를 최적화하고, pure BO와 LLM-assisted BO의 sample efficiency를 비교한다.

핵심 주장은 다음 정도로 제한한다.

> LLM은 MPC 제어기 자체를 대체하지 않고, 초기 후보 생성과 탐색 영역 개입을 통해 Bayesian optimization의 초기 탐색 효율을 보조한다. 실제 성능 판정은 CarMaker-Simulink simulation metric과 BO acquisition에 의해 수행된다.

이 방향은 기존 KSAE 논문의 "LLM-CarMaker decision loop"보다 제어/최적화 논문으로 더 방어적이다. 또한 낮은 난이도의 국제학회 6페이지 논문에는 충분하다.

2026-06-06 구현 진행 후 확정한 범위:

- 제어기 자체는 특별한 4WS/4WID/game-theory/dynamics novelty를 주장하지 않는다.
- 논문 핵심은 `standard slalom MPC controller`의 튜닝 자동화다.
- 차량동역학 모델은 MPC 상태/목적함수 정의를 위한 최소 수준으로 유지한다.
- 성공한 nominal slalom trajectory를 reference path로 사용하고, low-friction 조건에서 MPC tuning 자동화 성능을 검증한다.
- 4WS/4WID coordination 논문류는 관련연구/평가지표 근거로만 참고하고, 구현 방법론으로 채택하지 않는다.

## 1. 문제정의

### 1.1 대상 문제

대상은 CarMaker 기본 제공 slalom 계열 예제를 활용한 횡방향 차량제어 성능 최적화다.

- Plant: IPG CarMaker vehicle model, road, tire, sensor/vehicle dynamics.
- Controller: Simulink MPC lateral controller.
- Scenario: CarMaker 기본 slalom 또는 유사 lane-change/steering maneuver TestRun.
- Harsh condition: 노면 마찰계수 또는 tire-road friction scale을 낮춰 baseline MPC 튜닝이 흔들리도록 만든다.
- Optimization target: MPC weight, horizon, constraint margin 등 제어기 파라미터.

문제는 다음 black-box optimization으로 정의한다.

```text
minimize    J(theta)
subject to  theta in bounded tuning space
            CarMaker-Simulink simulation is executable
            vehicle does not violate hard safety constraints
```

여기서 `theta`는 MPC tuning parameter vector이고, `J(theta)`는 slalom tracking error, steering effort, steering smoothness, yaw stability, cone/lane violation penalty를 합친 scalar objective다.

### 1.2 연구 질문

1. Pure BO는 제한된 simulation budget 안에서 MPC 튜닝 성능을 얼마나 개선하는가?
2. LLM warm-start는 LHS 초기 샘플보다 빠른 early-stage improvement를 만드는가?
3. LLM이 실패 로그를 보고 search region 또는 candidate shortlist에 개입하면 pure BO보다 적은 반복으로 feasible high-performance tuning을 찾는가?
4. 저마찰 harsh slalom 조건에서 LLM-assisted BO의 장점이 nominal condition보다 잘 드러나는가?

### 1.3 논문 제목 후보

- LLM-Assisted Bayesian Optimization for MPC Parameter Tuning in CarMaker-Simulink Slalom Maneuvers
- Simulator-Validated LLM-Guided Bayesian Optimization of an MPC Lateral Controller under Low-Friction Slalom Conditions
- Closed-Loop MPC Tuning in CarMaker-Simulink Using LLM-Assisted Bayesian Optimization

## 2. 실험 환경

### 2.1 CarMaker 기본 예제 활용

우선순위는 기본 제공 TestRun을 최대한 재사용하는 것이다.

1. CarMaker 기본 Slalom TestRun을 찾는다.
2. 기본 Slalom이 없거나 연결이 어렵다면 Double Lane Change, Sine Steering, 또는 lane-change maneuver 예제를 slalom-like 횡방향 추종 문제로 사용한다.
3. 원본 TestRun은 보존하고, 논문용 복제본을 만든다.
4. 복제본에서 road friction 또는 tire-road friction scale을 낮춘다.

권장 scenario set:

| Scenario ID | Speed | Friction | Purpose |
| --- | ---: | ---: | --- |
| S1 Nominal | 50 km/h | mu = 1.0 | 정상 조건 sanity check |
| S2 Low-friction | 50 km/h | mu = 0.6 | 주 실험 조건 |
| S3 Harsh | 60 km/h | mu = 0.5 | robustness 확인 |

ICCAS 6p에서는 S2를 main result로 두고, S1/S3는 보조 표나 appendix성 결과로 넣어도 된다.

### 2.2 CarMaker-Simulink 연결

제어 구조는 다음으로 둔다.

```text
CarMaker vehicle states / path preview
  -> Simulink MPC lateral controller
  -> steering command
  -> CarMaker vehicle model
  -> slalom tracking/stability metrics
  -> BO / LLM-assisted BO loop
```

Simulink MPC는 차량의 횡방향 error, heading error, yaw rate, steering command를 이용해 slalom path를 추종한다. 논문에서는 MPC 내부 수식보다 "tunable parameter를 가진 standard MPC controller"라는 점을 강조한다.

현재 구현 기준:

- CM4SL 기반 `UserSteer.mdl`을 사용한다.
- 효과가 확인된 조향 override 위치는 `VehicleControlUpd` 이후 `CreateBus VhclCtrl.Steering` 내부의 `VhclCtrl Steering Ang`이다.
- `Read CM Dict` 블록으로 `Vhcl.sRoad`, `Vhcl.tRoad` 또는 `Car.Road.Path.DevDist`, `Car.Road.Path.DevAng`, `Car.YawRate`, `Car.v`를 읽는다.
- reference path는 successful `Base mu=1.0` run에서 `s_ref -> t_ref, psi_ref, delta_ff` lookup table로 생성한다.
- PD controller는 MPC 전 신호/부호/lookup/override smoke test로만 사용한다.

### 2.3 기록할 telemetry

최소 필요 telemetry:

- `time`
- vehicle speed `v_x`
- lateral position or road lateral offset `y`, `tRoad`
- reference path lateral position `y_ref`
- lateral error `e_y`
- heading error `e_psi`
- yaw rate `r`
- steering command `delta`
- steering rate `dot_delta`
- path progress `sRoad`
- cone hit, lane departure, off-road, simulation failure flag

CarMaker UAQ 후보:

- `Vhcl.sRoad`
- `Vhcl.tRoad`
- `Car.YawRate` 또는 equivalent yaw-rate signal
- steering angle / driver steering / DVA steering command
- tire slip or road friction related quantities if available

정확한 UAQ 이름은 실제 TestRun과 vehicle model에서 확인 후 확정한다.

## 3. 튜닝 변수

변수 수는 5-7개로 제한한다. 6페이지 논문과 40회 내외 simulation budget에서는 이 정도가 적당하다.

### 3.1 기본 6변수안

| Variable | Meaning | Type | Range | Transform |
| --- | --- | --- | ---: | --- |
| `q_y` | lateral error weight | continuous | 0.1 - 100 | log |
| `q_psi` | heading error weight | continuous | 0.1 - 100 | log |
| `q_r` | yaw-rate weight | continuous | 0.01 - 30 | log |
| `r_delta` | steering input weight | continuous | 0.01 - 10 | log |
| `r_d_delta` | steering rate weight | continuous | 0.01 - 10 | log |
| `delta_max_scale` | steering soft/hard limit scale | continuous | 0.6 - 1.2 | linear |

권장 시작은 이 6변수다. Horizon까지 넣으면 mixed discrete optimization이 되므로, 첫 논문에서는 제외하는 편이 안정적이다.

현재 MPC 구현에서는 `delta_cmd = delta_ff + u_mpc` 구조를 우선한다. 따라서 BO가 직접 튜닝할 대상은 steering command 자체가 아니라 tracking/stability/correction smoothness trade-off다.

초기 구현 변수 해석:

| Variable | Current role |
| --- | --- |
| `q_y` | `e_t = t - t_ref` 추종 가중치 |
| `q_psi` | `e_psi = devang - psi_ref` 추종 가중치 |
| `q_r` | yaw-rate 억제 가중치 |
| `r_delta` | MPC correction steering `u_mpc` 크기 가중치 |
| `r_d_delta` | correction 변화율 가중치 |
| `delta_max_scale` | steering/correction saturation scale |

### 3.2 확장 8변수안

실험 자동화가 충분하면 다음 두 변수를 추가한다.

| Variable | Meaning | Type | Range | Transform |
| --- | --- | --- | ---: | --- |
| `N_p` | prediction horizon | integer | 10 - 30 | linear |
| `N_c` | control horizon | integer | 3 - 10 | linear |

다만 `N_p`, `N_c`는 simulation compile/update 비용을 키울 수 있고, BO 구현도 약간 복잡해진다. ICCAS 최소 논문에서는 6변수안을 우선한다.

### 3.3 변수 정규화

BO 내부에서는 모든 변수를 `[0, 1]`로 정규화한다.

```text
x_i in [0, 1]
theta_i = inverse_transform(x_i)
```

log-scale 변수는 다음처럼 변환한다.

```text
theta = 10 ^ (log10(lb) + x * (log10(ub) - log10(lb)))
```

## 4. 목적함수와 reward

논문에서는 BO이므로 reward보다 cost/objective `J`를 최소화한다고 쓰는 편이 깔끔하다. 필요하면 reward는 `R = -J`로 정의한다.

### 4.1 Raw metrics

한 simulation에서 다음 값을 계산한다.

```text
RMSE_y       = sqrt(mean(e_y^2))
MAX_y        = max(abs(e_y))
RMSE_delta   = sqrt(mean(delta^2))
RMSE_d_delta = sqrt(mean(dot_delta^2))
MAX_r        = max(abs(yaw_rate))
MAX_beta     = max(abs(sideslip))     optional
T_complete   = completed slalom time  optional
N_violation  = cone hit + lane departure + off-road events
```

### 4.2 Objective definition

권장 scalar objective:

```text
J =
  1.00 * norm(RMSE_y)
+ 0.60 * norm(MAX_y)
+ 0.20 * norm(RMSE_delta)
+ 0.30 * norm(RMSE_d_delta)
+ 0.30 * norm(MAX_r)
+ 5.00 * N_violation
+ 20.0 * I_crash_or_sim_fail
```

정규화 기준값:

| Metric | Normalization |
| --- | ---: |
| `RMSE_y` | 0.50 m |
| `MAX_y` | 1.50 m |
| `RMSE_delta` | 0.20 rad |
| `RMSE_d_delta` | 0.80 rad/s |
| `MAX_r` | 0.80 rad/s |

따라서 실제 계산은 다음과 같다.

```text
norm(RMSE_y)       = RMSE_y / 0.50
norm(MAX_y)        = MAX_y / 1.50
norm(RMSE_delta)   = RMSE_delta / 0.20
norm(RMSE_d_delta) = RMSE_d_delta / 0.80
norm(MAX_r)        = MAX_r / 0.80
```

이 값들은 첫 baseline run 후 너무 크거나 작으면 조정한다. 논문에는 "normalization constants were selected from baseline maneuver scales"라고 쓰면 된다.

### 4.3 Hard fail handling

다음이면 objective를 큰 값으로 둔다.

```text
J = 50 + 10 * N_violation
```

Hard fail 조건:

- simulation crash.
- controller infeasible.
- vehicle leaves test area.
- slalom course completion failure.
- steering command NaN/Inf.
- CarMaker-Simulink communication failure.

이 처리는 safety-critical simulation에서 fail-closed behavior로 설명한다.

## 5. 비교군

### 5.1 Baseline A: Manual MPC

기본 Simulink MPC 튜닝값 또는 엔지니어가 임의 설정한 안정적인 초기값.

역할:

- optimization 전 기준 성능.
- 논문 trajectory/time-series 비교 기준.

### 5.2 Baseline B: Pure BO

Pure BO는 LLM 없이 수행한다.

Algorithm:

1. Latin Hypercube Sampling으로 `n_init = 10`개 초기 후보 생성.
2. 각 후보를 CarMaker-Simulink에서 평가.
3. GP surrogate 학습.
4. Expected Improvement acquisition으로 다음 후보 선택.
5. 총 `N_total = 40`회까지 반복.

권장 설정:

| Item | Value |
| --- | ---: |
| `n_init` | 10 |
| `n_bo` | 30 |
| `N_total` | 40 |
| Acquisition | Expected Improvement |
| Surrogate | Gaussian Process |
| Kernel | Matern 5/2 or squared exponential |
| Noise | small fixed nugget or estimated noise |
| Random seeds | 3 seeds if time permits, otherwise 1 seed with clear limitation |

ICCAS 6p에서는 1 seed도 가능하지만, 가능하면 3 seed의 mean/std를 넣는 편이 좋다.

### 5.3 Proposed C: LLM Warm-Start + BO

LLM이 초기 후보 일부를 생성하고, 나머지는 LHS로 채운다.

Algorithm:

1. LLM prompt에 MPC 변수 의미, bounds, slalom/low-friction 조건, objective 구성요소를 제공한다.
2. LLM이 `n_llm_init = 4`개의 초기 후보를 JSON으로 제안한다.
3. Schema/bounds validator가 후보를 검사한다.
4. invalid 후보는 clipping하지 말고 재요청 또는 LHS fallback한다.
5. 나머지 `n_lhs_init = 6`개는 LHS로 생성한다.
6. 이후는 pure BO와 동일하게 EI 기반 BO를 수행한다.

총 budget은 pure BO와 동일하게 `N_total = 40`으로 맞춘다.

중요:

- LLM 후보는 ground truth로 취급하지 않는다.
- BO 초기 dataset에 들어가는 warm-start sample일 뿐이다.
- invalid output은 실패로 세지 말고 generation failure로 따로 기록한다.

### 5.4 Proposed D: LLM Intervention + BO

LLM이 BO loop 중간에 개입한다. 단, LLM이 최종 후보를 직접 결정하지 않고 BO의 후보 선택을 보조한다.

개입 주기:

```text
after iterations 10, 20, 30
```

LLM에 제공할 정보:

- 현재 best theta.
- 현재 best metric summary.
- 최근 5개 trial의 theta와 metric.
- failure cases: lane departure, excessive steering, high yaw rate 등.
- 변수별 bounds.

LLM output schema:

```json
{
  "diagnosis": "short failure analysis",
  "promisingRegion": {
    "q_y": [0.2, 0.8],
    "q_psi": [0.2, 0.9],
    "q_r": [0.1, 0.7],
    "r_delta": [0.2, 0.8],
    "r_d_delta": [0.3, 1.0],
    "delta_max_scale": [0.6, 1.0]
  },
  "avoidRegionReason": "short text",
  "confidence": 0.0
}
```

여기서 interval은 normalized `[0,1]` coordinate 기준이다.

개입 방식은 두 가지 중 하나로 단순화한다.

#### Option D1: candidate shortlist reranking

1. EI로 candidate pool 256개를 만든다.
2. LLM promising region 안에 있는 후보에 작은 bonus를 준다.
3. 최종 후보는 adjusted EI가 가장 큰 점으로 선택한다.

예:

```text
score(x) = EI(x) * (1 + alpha * I[x in LLM_region] * confidence)
alpha = 0.5
```

#### Option D2: bounded EI

LLM이 제안한 promising region 내부에서 EI acquisition을 최적화한다. 단, confidence가 낮으면 global EI로 fallback한다.

권장:

- 처음 논문 구현은 D1이 더 안전하다.
- D2는 LLM이 틀리면 탐색을 좁혀 suboptimal region에 갇힐 수 있다.

## 6. BO 구현 상세

### 6.1 Pure BO pseudocode

```text
D = []
X_init = LatinHypercube(n=10, dim=6)
for x in X_init:
    theta = decode(x)
    y = run_carmaker_simulink(theta)
    D.append(x, y)

for k = 11..40:
    gp = fit_gp(D)
    x_next = argmax ExpectedImprovement(gp, bounds=[0,1]^6)
    theta_next = decode(x_next)
    y_next = run_carmaker_simulink(theta_next)
    D.append(x_next, y_next)
```

### 6.2 LLM warm-start + intervention pseudocode

```text
D = []
X_llm = request_llm_warm_start(problem_definition, bounds, n=4)
X_llm = validate_or_fallback(X_llm)
X_lhs = LatinHypercube(n=6, dim=6)
X_init = X_llm + X_lhs

for x in X_init:
    y = run_carmaker_simulink(decode(x))
    D.append(x, y)

llm_region = None
for k = 11..40:
    gp = fit_gp(D)

    if k in {11, 21, 31}:
        summary = summarize_recent_trials(D)
        llm_region = request_llm_region(summary, bounds)
        llm_region = validate_region_or_none(llm_region)

    candidate_pool = maximize_or_sample_EI(gp, n_pool=256)
    x_next = select_by_EI_with_optional_llm_bonus(candidate_pool, llm_region)
    y_next = run_carmaker_simulink(decode(x_next))
    D.append(x_next, y_next)
```

### 6.3 Iteration budget

권장 최종 budget:

| Stage | Count |
| --- | ---: |
| LHS or LLM/LHS initial design | 10 |
| BO iterations | 30 |
| Total per method | 40 |
| Methods | 3-4 |
| Main scenario | 1 |
| Optional seeds | 3 |

최소 실험량:

```text
Manual baseline: 1
Pure BO: 40
LLM warm-start + BO: 40
LLM intervention + BO: 40
Total: 121 simulations for one scenario
```

시간이 부족하면 proposed는 warm-start와 intervention을 합쳐 하나만 실행한다.

최소 논문용 구성:

```text
Manual baseline
Pure BO, 40 evals
LLM-assisted BO, 40 evals
```

## 7. LLM prompt 설계

### 7.1 Warm-start prompt 요지

```text
You are assisting MPC tuning for a CarMaker-Simulink low-friction slalom.
The controller is already implemented. You must only suggest bounded tuning parameters.
Do not invent new controller logic.

Variables:
- q_y: lateral error weight, log scale, range ...
- q_psi: heading error weight, ...
...

Objective penalizes lateral tracking error, max lateral error, steering effort,
steering rate, yaw rate, cone/lane violation, and simulation failure.

Suggest 4 diverse initial candidates likely to be stable under low friction.
Return JSON only.
```

### 7.2 Intervention prompt 요지

```text
Here are the recent CarMaker-Simulink trials.
Each trial includes normalized parameter vector and metrics.
Diagnose whether failures are caused by under-tracking, excessive steering,
insufficient yaw damping, or overly aggressive steering-rate behavior.

Return one promising search region in normalized coordinates.
Do not select the final candidate. BO will select the final candidate using EI.
Return JSON only.
```

### 7.3 LLM 안전장치

- JSON schema validation.
- Bounds validation.
- Invalid response retry maximum 2.
- Retry 실패 시 LHS/global EI fallback.
- LLM이 objective weight를 임의 변경하지 못하게 한다.
- LLM은 Simulink model 구조를 수정하지 못하게 한다.

## 8. 예상 결과

### 8.1 기대되는 정량 결과 패턴

예상 패턴은 다음이다.

| Method | Expected behavior |
| --- | --- |
| Manual baseline | stable but larger lateral error, or fails in low friction |
| Pure BO | after 20-30 evaluations, finds better tracking/smoother steering |
| LLM warm-start + BO | better best objective in first 10-15 evaluations |
| LLM intervention + BO | fewer unsafe trials, faster recovery from bad search regions |

논문에서 가장 좋은 그림:

```text
x-axis: simulation evaluations
y-axis: best-so-far objective J
curves: Pure BO vs LLM-assisted BO
```

주장 가능한 결과:

- LLM-assisted BO reaches the final pure-BO performance with fewer evaluations.
- LLM warm-start improves early-stage sample efficiency.
- LLM intervention reduces repeated exploration of overly aggressive steering regions.
- Final best performance may be similar, but search efficiency is improved.

주의:

- LLM-assisted가 최종 objective에서 항상 이겨야 할 필요는 없다.
- 6p 논문에서는 early-stage sample efficiency와 unsafe trial reduction만 보여도 충분하다.

### 8.2 예상 표

| Method | Best J | RMSE_y | MAX_y | RMSE_delta | RMSE_d_delta | MAX_yaw_rate | Violations | Eval to target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Manual | TBD | TBD | TBD | TBD | TBD | TBD | TBD | - |
| Pure BO | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| LLM warm-start + BO | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| LLM intervention + BO | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

### 8.3 예상 time-series 그림

최종 best controller 3개를 비교한다.

- baseline manual.
- pure BO best.
- LLM-assisted BO best.

그림:

1. path tracking trajectory.
2. lateral error over time.
3. steering command over time.
4. yaw rate over time.

## 9. 논문 구성안

### 9.1 6페이지 배분

| Section | Page budget | Content |
| --- | ---: | --- |
| Introduction | 0.75 | MPC tuning need, expensive simulation, BO and LLM motivation |
| System Overview | 1.00 | CarMaker-Simulink loop, slalom low-friction scenario, MPC tunable parameters |
| Method | 1.50 | objective, pure BO, LLM warm-start/intervention, validation |
| Experiment | 0.75 | scenario, variables, bounds, budget, comparison methods |
| Results | 1.25 | convergence, metric table, trajectory/time-series |
| Conclusion | 0.50 | findings and limitations |

### 9.2 Contribution 문장

논문 contribution은 세 개로 제한한다.

1. A CarMaker-Simulink closed-loop optimization framework for MPC lateral controller tuning under low-friction slalom conditions.
2. A bounded LLM-assisted BO strategy where the LLM provides warm-start candidates and search-region guidance while EI-based BO selects simulator-validated candidates.
3. A comparative evaluation against pure LHS+EI BO using tracking, stability, steering smoothness, violation, and sample-efficiency metrics.

## 10. Wiki 기반 방향 검토

검토한 Obsidian wiki 기준으로 이 방향은 타당하다.

### 10.1 AI-based closed-loop optimization 관점

해당 wiki의 핵심은 AI 후보 생성, simulator validation, feedback update를 분리하는 것이다. 본 주제는 이 구조와 맞다.

```text
Candidate space: MPC tuning parameters
Surrogate/acquisition: GP + EI BO
Validation: CarMaker-Simulink slalom simulation
Feedback: objective and failure metrics
LLM role: warm-start, failure interpretation, preference region
```

### 10.2 LLM/BO hybrid 관점

LLM/BO hybrid 문서의 BORA식 구조는 LLM이 warm-start, progress interpretation, candidate selector로 들어갈 수 있다고 정리한다. 본 논문에서는 LLM을 더 보수적으로 둔다.

- 직접 optimizer로 쓰지 않는다.
- 최종 candidate는 EI 기반 BO가 고른다.
- LLM은 초기 후보와 search region preference만 제공한다.

이는 6페이지 논문에서 가장 방어적인 설계다.

### 10.3 LLM-preference-guided BO 관점

LGBO식 아이디어는 LLM output을 point/region/confidence로 제한하고, BO posterior/acquisition의 통제권을 유지하는 것이다. 본 논문의 LLM intervention은 이를 단순화한 형태다.

```text
LLM region suggestion
  -> EI candidate pool bonus
  -> simulator-validated evaluation
```

수식적으로 GP mean shift까지 구현하지 않아도, 낮은 난이도 ICCAS 논문에서는 "LLM-guided acquisition reranking"으로 충분히 설명 가능하다.

### 10.4 TuRBO 관점

MPC tuning 변수 수가 6개이면 TuRBO까지는 필요 없다. TuRBO는 수십 차원 calibration map이나 large parameterization으로 확장할 때 future work로 두는 편이 좋다.

## 11. 구현 체크리스트

### 11.1 Scenario

- [ ] CarMaker 기본 Slalom TestRun 확인.
- [ ] 기본 Slalom이 없으면 Double Lane Change/Sine Steering 예제로 대체.
- [ ] TestRun 복제본 생성.
- [ ] friction scale 낮춘 low-friction variant 생성.
- [ ] baseline controller로 simulation completion 확인.

### 11.2 Simulink MPC

- [ ] lateral MPC controller 연결.
- [ ] tuning parameters를 workspace/config에서 주입 가능하게 구성.
- [ ] 6변수안을 우선 구현.
- [ ] controller infeasibility/failure flag 기록.

### 11.3 Evaluation script

- [ ] theta -> Simulink parameter update.
- [ ] CarMaker simulation run.
- [ ] result log extraction.
- [ ] raw metrics 계산.
- [ ] scalar objective `J` 계산.
- [ ] failure penalty 처리.

### 11.4 BO

- [ ] LHS generator.
- [ ] GP surrogate.
- [ ] EI acquisition.
- [ ] candidate pool or acquisition optimizer.
- [ ] best-so-far log 저장.

### 11.5 LLM-assisted BO

- [ ] warm-start prompt.
- [ ] intervention prompt.
- [ ] JSON schema validator.
- [ ] invalid/fallback handling.
- [ ] LLM region bonus selection.

### 11.6 Paper artifacts

- [ ] architecture diagram.
- [ ] optimization flow diagram.
- [ ] convergence plot.
- [ ] metric comparison table.
- [ ] trajectory/time-series plot.
- [ ] best parameter table.

## 12. 최종 논문 방향

가장 현실적인 최종 방향:

```text
Main experiment:
  Low-friction slalom, 6 MPC tuning variables, 40 evaluation budget.

Comparison:
  Manual baseline
  Pure BO = 10 LHS + 30 EI
  LLM-assisted BO = 4 LLM warm-start + 6 LHS + 30 EI with 3 region interventions

Claim:
  LLM-assisted BO improves early sample efficiency and reduces unsafe/aggressive
  tuning trials, while preserving simulator-validated BO candidate selection.
```

이 정도면 ICCAS 6페이지 논문으로 충분히 구성 가능하다. 결과가 약할 경우에는 최종 성능 우위 대신 다음 두 지표를 강조한다.

- target objective 도달까지 필요한 simulation 횟수.
- violation 또는 simulation failure를 낸 trial 수.

즉 "LLM이 더 좋은 제어기를 만들었다"보다 "LLM guidance가 BO의 초기 탐색 비용과 위험한 후보 반복을 줄였다"로 claim을 잡는 것이 안전하다.
