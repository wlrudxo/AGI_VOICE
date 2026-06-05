# ICCAS 6p Research Ideas: CarMaker Automation + LLM

작성일: 2026-06-04

## 검토한 기준 자료

- Obsidian AI 최적화 문서
  - `work/ai-auto-calibration/research_context.md`
  - `work/ai-auto-calibration/2026-05-29_llm-optimizer-role-separation.md`
  - `work/ai-auto-calibration/2026-05-29_reference-literature-map.md`
  - `work/ai-auto-calibration/2026-05-29_hev-rulebasedmap-problem-definition.md`
  - `work/ai-auto-calibration/2026-05-29_ecu-map-calibration-workflow.md`
  - `wiki/concepts/ai-based-closed-loop-optimization.md`
  - `wiki/methods/llm-bo-hybrid-optimization-for-closed-loop-experiments.md`
  - `wiki/methods/llm-fidelity-gated-bayesian-optimization.md`
  - `wiki/methods/llm-preference-guided-bayesian-optimization.md`
  - `wiki/methods/smooth-calibration-map-generation.md`
  - `wiki/synthesis/racing-auto-calibration-map-generation.md`
- AutoCalibration 연구계획
  - `C:\Users\user\OneDrive\Lab\2026 AutoCalibration\연구계획.md`
- 기존 KSAE 논문
  - `E:\GitProject\AGI_VOICE\Paper_AGI_KSAE202601\[한양대] KSAE202601_AGI_LLM.pdf`

## 현재 KSAE 논문의 출발점

기존 KSAE 논문은 CarMaker에서 LLM 에이전트를 직접 차량 제어 의사결정에 연결한 1차 시스템 논문이다. 핵심 구현은 다음이다.

- CarMaker TCP 통신 기반 UAQ/DVA 실시간 상태 읽기 및 제어 입력 쓰기.
- 트리거 조건 만족 시 시뮬레이션 time scale을 낮추고 LLM 판단을 요청하는 구조.
- LLM 자연어 출력을 차량 제어 명령으로 바꾸는 통합 명령 포맷.
- Rule-based, LLM Single-shot, LLM Feedback Loop 비교.
- 도심 보행자 긴급 회피 시나리오에서 Feedback Loop가 1차 실패 원인을 분석하고 제어 파라미터를 보정하는 self-correction 가능성 제시.

ICCAS 6페이지로 개발할 때는 "LLM이 잘 운전한다"보다 "CarMaker 자동화 환경에서 LLM 판단을 검증 가능하고 반복 가능한 closed-loop workflow로 바꿨다"가 더 방어적이다.

## 논문 방향을 잡는 원칙

1. LLM을 수치 optimizer 또는 safety-critical controller로 과장하지 않는다.
2. CarMaker는 ground-truth validator로 둔다.
3. LLM output은 실행 전 schema, bounds, safety rule로 제한한다.
4. 비교군은 단순해야 한다: Rule-based, LLM single-shot, LLM feedback, LLM+optimizer 중 2-4개.
5. 결과는 성공/실패 장면보다 metric table이 중요하다: 충돌 여부, 최소 TTC, 차선 이탈, 제어 effort, 반복 횟수, 수정 전후 성능.
6. 6페이지 논문이면 구현 가능한 한 시나리오를 깊게 파는 편이 낫다.

## 추천 우선순위

### 1순위: LLM Feedback 기반 CarMaker 시나리오 자동 재시도 및 파라미터 보정

#### 한 줄 주제

CarMaker 사고/실패 로그를 LLM이 해석하고, 제동/조향/트리거 파라미터를 자동 보정해 같은 시나리오를 반복 재실행하는 closed-loop decision calibration system.

#### 왜 좋나

기존 KSAE 논문의 가장 강한 부분이 Feedback Loop self-correction이다. ICCAS에서는 이것을 "한 번의 피드백"에서 "자동 재시도 루프"로 확장하면 자연스럽다. AutoCalibration 문서의 핵심인 LLM = loop manager, simulator = validator 구조와도 정확히 맞다.

#### 가능한 contribution

- CarMaker failure log를 structured feedback으로 변환하는 loop 설계.
- LLM이 제어 명령 자체가 아니라 제어 파라미터 후보를 수정하는 안전한 구조.
- 실패 원인 분류: insufficient braking, excessive steering, lane departure, late trigger, over-conservative stop.
- 재시도 횟수 제한과 fail-closed 조건을 둔 자동 실험 루프.

#### 실험 설계

- 시나리오: 기존 도심 무단횡단/AEB 기반 회피 시나리오.
- 변수: brake target, steering angle, trigger TTC, command duration, wait condition.
- 비교군:
  - Rule-based fixed command.
  - LLM single-shot.
  - LLM feedback one-step.
  - LLM auto-retry loop, 최대 3회.
- 지표:
  - collision 여부.
  - minimum distance 또는 minimum TTC.
  - lane departure 여부.
  - max yaw rate.
  - command count.
  - 성공까지 필요한 trial 수.

#### 6p 구성

1. Introduction: LLM 직접 제어의 한계와 시뮬레이션 검증 루프 필요성.
2. System: CarMaker trigger, command parser, failure feedback, retry manager.
3. Method: LLM prompt/schema, parameter bounds, fail-closed rules.
4. Experiment: pedestrian emergency avoidance.
5. Results: trial별 command 변화와 metric table.
6. Conclusion: LLM self-correction을 검증 가능한 simulator loop로 제한했을 때의 가능성.

#### 리스크

- LLM stochasticity 때문에 같은 prompt에서 결과가 흔들릴 수 있다.
- 이를 줄이려면 temperature를 낮추고, 출력 형식을 JSON/command schema로 강제해야 한다.

#### 판정

가장 추천한다. 기존 구현 자산을 가장 많이 재사용하고, ICCAS 6페이지에 충분히 들어가며, 실험 결과를 만들기 쉽다.

### 2순위: LLM-Assisted Trigger Condition Tuning for CarMaker Emergency Scenarios

#### 한 줄 주제

LLM이 CarMaker telemetry와 이전 실패 결과를 해석해 emergency trigger 조건을 보정하고, rule-based controller의 작동 타이밍을 자동 튜닝하는 방법.

#### 왜 좋나

기존 논문은 trigger가 사전에 정의된 조건이었다. 후속 논문에서는 LLM이 "언제 판단을 시작해야 하는가"를 보정하게 만들 수 있다. 이는 vehicle control을 LLM이 직접 하는 것보다 안전하고, 실제 적용 문제에 가깝다.

#### 가능한 contribution

- LLM을 controller가 아니라 trigger calibration assistant로 제한.
- 상태 변수 기반 trigger 조건 자동 수정: speed, distance, TTC, pedestrian relative position, deceleration threshold.
- late trigger와 early trigger의 trade-off 분석.

#### 실험 설계

- 같은 pedestrian crossing scenario에서 초기 속도 또는 보행자 출현 타이밍을 3-5개로 변화.
- 비교군:
  - fixed TTC trigger.
  - hand-tuned trigger.
  - LLM-tuned trigger.
- 지표:
  - collision rate.
  - false trigger count.
  - minimum TTC.
  - braking comfort, max deceleration.
  - scenario coverage.

#### 6p 구성

핵심 그림은 "telemetry -> trigger evaluation -> LLM failure analysis -> updated trigger rule -> CarMaker rerun" 하나면 충분하다.

#### 리스크

- 너무 단순하면 engineering tuning report처럼 보일 수 있다.
- 논문성을 높이려면 late/early trigger failure taxonomy와 여러 scenario variant가 필요하다.

#### 판정

구현 난이도 낮고 방어적이다. 다만 1순위보다 novelty가 조금 약하다.

### 3순위: LLM Preference-Guided Bayesian Optimization for Emergency Maneuver Parameters

#### 한 줄 주제

CarMaker 회피 시나리오에서 BO가 제동/조향 파라미터를 탐색하고, LLM은 실패 로그를 바탕으로 유망 영역 preference를 제공하는 hybrid optimization.

#### 왜 좋나

Obsidian의 LLM-BO hybrid, LGBO, LABO 축과 직접 연결된다. LLM이 최종 후보를 고르지 않고 "조향이 과도하니 steering range를 낮춰라", "제동이 부족하니 brake/duration 영역을 키워라" 같은 preference를 주고, 실제 후보 선택은 BO 또는 grid/surrogate가 담당한다.

#### 가능한 contribution

- LLM preference를 수치 탐색의 soft prior로 쓰는 CarMaker 적용 사례.
- LLM-only, BO-only, LLM+BO 비교.
- 자동차 시뮬레이션에서 semantic failure analysis가 black-box search를 줄일 수 있음을 보임.

#### 실험 설계

- 변수:
  - brake level: 0-1.
  - steering angle: -1.5 to 1.5 rad.
  - steering duration.
  - brake delay.
- 목적함수:
  - collision penalty.
  - lane departure penalty.
  - minimum distance reward.
  - yaw rate / control effort penalty.
- 비교군:
  - random search.
  - BO-only 또는 surrogateopt.
  - LLM direct suggestion.
  - LLM-guided BO.
- 지표:
  - success within N evaluations.
  - best objective after N trials.
  - number of unsafe trials.

#### 6p 구성

ICCAS 6p에서는 BO 수식은 최소화하고, system diagram과 convergence plot 하나, best maneuver table 하나로 충분하다.

#### 리스크

- BO 구현과 반복 CarMaker 실행 자동화가 필요하다.
- LLM-guided BO가 BO-only보다 항상 이긴다는 보장이 없다.
- 결과가 안 좋으면 "LLM preference가 unsafe trials를 줄였다"로 claim을 바꿀 수 있게 지표를 설계해야 한다.

#### 판정

논문성은 가장 좋지만 구현 부담이 1순위보다 크다. 실험 자동화가 이미 잘 되어 있으면 강력한 선택이다.

### 4순위: CarMaker Scenario Report Agent for Automated Safety Evaluation

#### 한 줄 주제

CarMaker 시뮬레이션 결과를 LLM이 자동 분석하여 실패 원인, 위험 이벤트, 제어 입력 문제, 다음 테스트 시나리오를 보고서로 생성하는 safety evaluation assistant.

#### 왜 좋나

실제 적용성은 높다. ICCAS가 너무 빡세지 않다면, LLM+CarMaker 자동화의 실용 논문으로 충분히 가능하다. 특히 AGI_VOICE의 UI/backend가 실험 로그와 연동된다면 demo가 쉽다.

#### 가능한 contribution

- CarMaker telemetry/event log를 LLM-readable structured summary로 변환.
- Rule-based template report와 LLM report 비교.
- 실패 원인과 next-test recommendation의 human evaluation.

#### 실험 설계

- 5-10개 시나리오: pedestrian crossing, sudden braking, lane change, obstacle avoidance 등.
- 각 시나리오에서 성공/실패 케이스를 만들고 LLM이 report 작성.
- 평가:
  - event detection accuracy.
  - failure cause classification.
  - recommendation usefulness, 5점 척도.
  - report generation time.

#### 리스크

- 제어/최적화보다 report automation에 가까워 연구 기여가 약해 보일 수 있다.
- 실험 평가는 사람 평가가 필요할 수 있다.

#### 판정

실용 데모로는 좋지만, "연구 개발" 느낌은 1-3순위보다 약하다.

### 5순위: LLM-Managed Scenario Coverage Expansion for CarMaker AD Testing

#### 한 줄 주제

LLM이 사고/near-miss 결과를 보고 다음 CarMaker scenario parameter set을 생성하여 edge case coverage를 확장하는 자동 테스트 생성 loop.

#### 왜 좋나

자율주행에서 scenario coverage는 중요한 문제다. 기존 KSAE 논문의 "다양한 자율주행 시나리오로 검증 확대"라는 향후 연구를 바로 논문 주제로 바꿀 수 있다.

#### 가능한 contribution

- LLM이 scenario parameter를 생성하되, CarMaker 실행 가능 schema로 제한.
- 실패가 난 조건 주변을 더 촘촘히 탐색하는 adaptive scenario generation.
- 사고율/near-miss율이 높은 조건 발견.

#### 실험 설계

- 변수:
  - ego speed.
  - pedestrian speed.
  - occlusion distance.
  - road friction.
  - initial relative distance.
- 비교군:
  - random scenario sampling.
  - grid sampling.
  - LLM-guided scenario generation.
- 지표:
  - discovered failure cases.
  - unique scenario clusters.
  - simulation budget 대비 near-miss discovery rate.

#### 리스크

- CarMaker scenario parameterization과 자동 실행이 필요하다.
- LLM이 생성한 scenario가 물리적으로 말이 안 되면 schema/validator가 필수다.

#### 판정

좋은 주제지만, 현재 "제어 의사결정" 논문에서 한 단계 더 시스템 테스트 쪽으로 이동한다.

### 6순위: LLM-Based Explanation and Repair of Unified Command Format Failures

#### 한 줄 주제

LLM 차량 제어 명령이 schema 오류, bounds 초과, 실행 불가능 조건을 만들 때 이를 자동 검출하고 수정하는 command validation and repair framework.

#### 왜 좋나

LLM을 차량 제어에 쓰는 가장 큰 실무 문제는 출력 안정성이다. 기존 KSAE 논문의 통합 명령 포맷을 후속 논문 중심으로 만들 수 있다.

#### 가능한 contribution

- command grammar/schema 정의.
- invalid command 자동 검출.
- LLM self-repair와 deterministic repair 비교.
- 실행 전 safety bounds 적용.

#### 실험 설계

- 여러 prompt/scenario에서 LLM 명령 생성.
- 일부러 복잡한 task를 주어 invalid command 유도.
- repair 전후 실행 성공률, safety violation, parsing failure 측정.

#### 리스크

- vehicle behavior보다 software safety 논문에 가까워진다.
- ICCAS에서 automotive control contribution이 약해 보일 수 있다.

#### 판정

보조 논문 또는 section으로는 좋다. 단독 주제로는 약간 좁다.

### 7순위: HEV Rule-Based Map Calibration with LLM Experiment Manager

#### 한 줄 주제

DP/ECMS target을 기반으로 HEV engine ON/OFF/torque rule map을 만들고, LLM이 simulation failure와 map smoothness를 해석하는 Auto Calibration workflow.

#### 왜 좋나

AutoCalibration 연구계획과 가장 직접적으로 맞는다. ON_LUT, OFF_LUT, Trq_LUT 문제정의가 이미 정리되어 있고, 최종 산출물이 ECU-compatible map이라는 점이 명확하다.

#### 가능한 contribution

- DP/ECMS target -> rule-based LUT fitting -> CarMaker/Simulink validation.
- LLM이 map failure를 분류: chattering, torque mismatch, SOC imbalance, smoothness violation.
- optimizer는 low-dimensional map parameter만 조정.

#### 실험 설계

- 실제 HEV model과 target data가 있어야 한다.
- 비교군:
  - supervised fitting only.
  - optimizer-only correction.
  - LLM-managed optimizer correction.
- 지표:
  - engine on mismatch.
  - torque tracking error.
  - chattering count.
  - fuel/SOC metric.
  - map smoothness.

#### 리스크

- 현재 AGI_VOICE의 CarMaker 자율주행 논문과 거리가 있다.
- HEV 모델/데이터 준비가 논문 일정의 병목이 될 수 있다.

#### 판정

큰 연구 방향으로는 좋지만, ICCAS 6페이지 단기 개발 주제로는 준비물이 많다.

## 최종 추천 조합

### 가장 현실적인 ICCAS 논문

제목 후보:

> Closed-Loop Self-Correction of LLM-Based Driving Decisions in CarMaker Simulation

핵심 내용:

- 기존 KSAE의 LLM Feedback Loop를 자동 재시도/파라미터 보정 loop로 확장.
- LLM은 실패 원인 분석과 제어 파라미터 보정만 담당.
- CarMaker는 제어 결과를 검증하고 metric을 산출.
- Rule-based, Single-shot, One-step feedback, Auto-retry feedback 비교.

이 주제는 기존 구현 자산과 가장 잘 맞고, 6페이지 논문으로 완성하기 쉽다.

### 조금 더 연구스럽게 보이게 하는 확장

1순위 주제에 3순위의 "간단한 optimizer"를 약하게 붙인다.

예:

```text
LLM proposes correction direction
bounded local search tests 3 candidate parameter sets
CarMaker metric selects the best candidate
```

이렇게 하면 "LLM이 임의로 제어값을 바꿨다"가 아니라 "LLM-guided closed-loop parameter search"가 된다. BO까지 구현하지 않아도, small candidate batch search로 충분히 ICCAS급 실험은 만들 수 있다.

## 추천 실험 minimum viable set

### Scenario

- 기존 AEB pedestrian emergency avoidance.
- ego speed 3조건: 50, 60, 65 km/h.
- pedestrian timing 2조건.
- 총 6개 scenario variant.

### Methods

1. Rule-based AEB only.
2. LLM single-shot command.
3. LLM feedback one-step.
4. Proposed LLM auto-retry parameter correction.

### Metrics

- Collision: yes/no.
- Lane departure: yes/no.
- Minimum distance to pedestrian.
- Maximum yaw rate.
- Maximum deceleration.
- Number of LLM calls.
- Number of trials to success.

### Main table

| Method | Collision rate | Lane departure rate | Mean min distance | Mean max yaw rate | Trials to success |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rule-based | TBD | TBD | TBD | TBD | - |
| Single-shot | TBD | TBD | TBD | TBD | 1 |
| One-step feedback | TBD | TBD | TBD | TBD | 2 |
| Proposed auto-retry | TBD | TBD | TBD | TBD | <= 3 |

### Main figure

- System architecture figure.
- Vehicle trajectory comparison.
- Trial-by-trial correction example:
  - trial 1: steering too large -> lane departure.
  - trial 2: steering reduced, braking increased -> stable avoidance.
  - trial 3 if needed: trigger timing adjusted.

## 논문 claim 문장 후보

강한 claim:

> The proposed loop converts LLM-based driving decisions into a simulator-validated parameter correction process, allowing the agent to identify failure causes and improve maneuver parameters under bounded safety constraints.

보수적인 claim:

> The results suggest that LLM feedback is more useful as a high-level failure analysis and parameter correction module than as an unconstrained low-level controller.

한글 요지:

> LLM을 직접 제어기로 쓰기보다, CarMaker 검증 결과를 해석하고 제한된 제어 파라미터를 보정하는 에이전트로 쓰는 것이 더 안정적이고 재현 가능한 구조다.

## 피해야 할 방향

- LLM이 자율주행 제어를 "해결"했다고 주장.
- 1개 시나리오 1회 성공만으로 generalization 주장.
- LLM-only가 BO나 rule-based보다 항상 우수하다고 주장.
- CarMaker 일시정지를 실시간 제어 가능성으로 과장.
- map cell 전체를 LLM이나 BO가 직접 최적화하는 방향.

## 다음 액션

1. 기존 KSAE 실험 코드에서 scenario rerun을 자동화할 수 있는지 확인한다.
2. command output을 JSON 또는 고정 command grammar로 제한한다.
3. failure summary schema를 만든다.
4. 6개 scenario variant를 만들고 baseline 결과를 먼저 저장한다.
5. auto-retry loop의 최대 반복 횟수와 fail-closed 조건을 정한다.
6. 결과가 좋으면 1순위 논문으로 진행하고, 결과가 약하면 4순위 report agent 또는 6순위 command repair 쪽으로 claim을 좁힌다.
