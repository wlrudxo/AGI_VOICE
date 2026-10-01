# Can We Automate Scientific Reasoning in Closed-Loop Experiments Using LLMs? - 세미나 정리

## 1. 논문의 질문

이 논문은 closed-loop scientific experiment에서 LLM이 단순한 설명 도구가 아니라, 실제 실험 후보를 고르는 optimizer 또는 Bayesian optimization(BO)의 보조 reasoning engine으로 쓸 수 있는지를 평가한다.

핵심 비교 대상은 다음 세 가지다.

- BO-only: 전통적인 Bayesian optimization만 사용
- LLM/BO hybrid, BORA: LLM warm-start, LLM intervention, BO 후보 중 LLM-guided subset selection을 조합
- LLM-only: BO 없이 LLM reasoning이 직접 다음 실험 조건을 제안

평가는 실제 wet-lab이 아니라 in silico ground-truth model에서 수행했다. 이 선택은 실제 실험성을 낮추는 한계가 있지만, 동일 조건에서 20회 반복 최적화와 outlier 분석을 가능하게 한다는 장점이 있다.

## 2. 실험 상황 A: 10-D Photocatalytic Hydrogen Evolution

### 실험 문제

목표는 photocatalyst mixture의 hydrogen evolution rate(HER, mmol h^-1)를 최대화하는 것이다. 최대 가능한 HER은 28.37 mmol h^-1이다.

입력 변수는 10개다.

- Photocatalyst: P10
- Dyes: Acid Red 871, Methylene Blue, Rhodamine B1
- Bases: NaOH, sodium disilicate
- Salt: NaCl
- Surfactants: PVP, SDS
- Sacrificial agent: L-cysteine

제약 조건은 P10을 제외한 액체 성분 총량이 5 mL 이하라는 것이다. P10은 최소 1 mg 이상이며, 나머지 9개 변수는 0-5 mL 범위에서 선택된다.

### 기본 hybrid 조건

- 15 batches x 10 experiments = 총 150 experiments
- 20 repeat runs
- 처음 5 batches, 즉 50 experiments는 LLM warm-start
- 이후 BORA가 BO-only action, LLM intervention, LLM-guided BO subset selection을 전환
- 비교 모델: o4-mini, o3, gpt-5-mini, gpt-5, gemini-2.5-flash

### Hybrid 결과

| 조건 | 25회 후 평균 HER | 150회 후 평균 HER | 150회 후 STD | 최적점 도달 횟수 |
|---|---:|---:|---:|---:|
| BO-only | 0.6 | 11.6 | 4.4 | 0/20 |
| o4-mini/BO | 7.5 | 20.2 | 4.4 | 1/20 |
| gemini-2.5-flash/BO | 11.3 | 20.7 | 4.9 | 2/20 |
| gpt-5-mini/BO | 12.5 | 21.5 | 2.8 | 0/20 |
| gpt-5/BO | 7.5 | 25.1 | 4.2 | 9/20 |
| o3/BO | 10.5 | 25.3 | 2.9 | 4/20 |

가장 중요한 결과는 모든 LLM/BO hybrid가 BO-only를 이겼다는 점이다. 특히 BO-only는 초반 50회 random/exploration 단계에서 HER이 거의 0에 가까운 조합을 많이 평가했다. 반면 LLM은 문헌과 화학적 reasoning을 바탕으로 다음과 같은 rule을 빠르게 만들었다.

- dyes는 이 시스템에서 유해할 가능성이 높다.
- SDS/PVP 같은 surfactant는 계면을 막아 HER을 낮출 수 있다.
- P10, L-cysteine, base, NaCl 조합이 중요하다.
- 5 mL liquid budget 안에서 pH, ionic strength, donor amount를 조절해야 한다.

즉, LLM의 이점은 단순히 좋은 점을 찍는 것이 아니라, 변수를 의미 단위로 묶어 해석한다는 데 있다. BO는 세 dye를 각각 독립 변수로 본다. 하지만 LLM은 "dyes as a class are bad"라는 일반화를 만들 수 있다. 고차원 실험에서 이 semantic grouping이 탐색 효율을 크게 높였다.

### LLM-only 결과

같은 batch size 10 조건에서 o3-only는 hybrid보다 약간 더 좋았다.

| 조건 | 150회 후 평균 HER | STD | 최적점 도달 횟수 |
|---|---:|---:|---:|
| BO-only | 11.6 | 4.4 | 0/20 |
| o3/BO hybrid | 25.3 | 2.9 | 4/20 |
| o3-only | 26.2 | 2.9 | 9/20 |

또한 같은 50개 initial samples에서 시작한 비교에서도 o3 LLM-only가 BO-only보다 확실히 우수했다.

| 조건 | 150회 후 평균 HER | STD | 최적점 도달 횟수 |
|---|---:|---:|---:|
| BO-only | 12.0 | 4.6 | 0/20 |
| o3-only | 24.6 | 3.4 | 5/20 |

이 결과는 LLM이 단순한 warm-start 도구가 아니라, 특정 문제에서는 post-initialization acquisition strategy 자체로 작동할 수 있음을 보여준다.

### Batch size 효과

o3 LLM-only에서 batch size를 줄일수록 성능이 좋아졌다.

| Batch size | 조건 | 150회 후 평균 HER | 최적점 도달 횟수 |
|---:|---|---:|---:|
| 10 | o3-only | 26.2 | 9/20 |
| 5 | o3-only | 26.3 | 12/20 |
| 3 | o3-only | 26.6 | 13/20 |
| 1 | o3-only | 27.0 | 15/20 |

Batch size 1에서는 매 실험마다 reasoning을 업데이트한다. 논문에서 가장 강한 성능은 이 조건에서 나왔다. 이는 LLM의 핵심 강점이 "초기 지식"보다 "새 데이터가 들어올 때마다 가설을 재구성하는 능력"에 있음을 시사한다.

단, batch size 1은 LLM query 수가 많아져 비용과 에너지 사용량이 증가한다. 또 wet-lab에서는 매 샘플마다 decision loop를 돌리는 것이 자동화 장비 처리량과 맞지 않을 수 있다.

### 프롬프트와 추가 지식 주입 효과

논문에서 가장 발표 가치가 큰 부분 중 하나는 "어떤 프롬프트를 붙이느냐"에 따라 같은 optimizer의 행동이 크게 달라진다는 점이다. 저자들은 10-D photocatalysis 문제에서 o3/BO 또는 gpt-5/BO hybrid에 여러 종류의 prompt/context를 붙여 비교했다.

주의할 점은 논문에서 말하는 `no prompt`, `unprompted`, `without additional prompt`가 정말 아무 정보 없이 "해"라고만 지시한 조건은 아니라는 점이다. 모든 최적화에는 기본 experiment card가 들어간다. 이 card에는 실험 목표, 사용 가능한 변수, 제약 조건이 포함된다. 예를 들어 photocatalysis에서는 "수중 photocatalyst mixture에서 hydrogen production rate를 최대화하라", "P10, dyes, bases, NaCl, surfactants, L-cysteine을 조절한다", "P10을 제외한 총 액체 부피는 5 mL 이하" 같은 정보가 제공된다.

따라서 `no prompt`는 "기본 실험 정의만 있고, 추가 human hypothesis / executive order / prior paper / CSV data는 없는 조건"으로 이해해야 한다. 논문에는 실험 정의조차 없이 "해" 수준으로 던진 ablation은 없다.

#### 1. Human hypothesis prompt: bad / mixed / good

먼저 연구자가 자연어 hypothesis를 추가하는 조건을 만들었다. 조건은 세 가지다.

- Bad prompt: 저자들이 실제로 틀렸다고 아는 가설을 넣음. 예를 들어 dye/surfactant를 유리하게 보는 방향.
- Mixed prompt: 좋은 가설과 나쁜 가설을 섞음.
- Good prompt: 저자들이 실제로 유리하다고 아는 방향의 가설을 넣음.

조건은 o3/BO hybrid, batch size 10, 15 batches, 20 repeat runs다.

| 조건 | 25회 후 평균 HER | 150회 후 평균 HER | 150회 후 STD | 최적점 도달 횟수 |
|---|---:|---:|---:|---:|
| o3 no prompt | 10.5 | 25.3 | 2.9 | 4/20 |
| o3 bad prompt | 2.0 | 20.8 | 7.0 | 4/20 |
| o3 mixed prompt | 5.0 | 21.6 | 3.6 | 0/20 |
| o3 good prompt | 18.0 | 25.8 | 4.4 | 2/20 |

해석은 단순하지 않다.

Good prompt는 초반 성능을 크게 올렸다. 25회 후 평균 HER이 no prompt 10.5에서 18.0으로 상승했다. 하지만 150회 후에는 25.8로 no prompt 25.3과 큰 차이가 없고, 최적점 도달 횟수는 오히려 4/20에서 2/20으로 줄었다.

Bad prompt는 초반을 크게 망쳤다. 25회 후 평균 HER은 2.0에 불과했다. 그래도 LLM은 실험 결과를 보고 dye와 surfactant가 나쁘다는 방향으로 reasoning을 수정해 19/20 run에서 부분적으로 회복했다. 하지만 평균적으로는 150회 budget 안에서 완전히 회복하지 못했다.

Mixed prompt는 가장 애매했다. 좋은 가설과 나쁜 가설이 섞이면 LLM이 어떤 prior를 우선할지 불안정해지고, 최적점 도달은 0/20이었다.

여기서 중요한 insight는 "좋은 프롬프트도 search를 좁히는 bias"라는 점이다. 논문은 good prompt 안의 `P10 > 4 mg` 같은 구체적 수치 지시가 실제 optimum 근처 탐색을 방해했을 수 있다고 해석한다. 즉, 프롬프트는 일반 heuristic으로 주는 편이 낫고, 너무 구체적인 numerical prescription은 위험하다.

#### 2. Executive order prompt: "do not add dyes"

다음 실험은 hypothesis가 아니라 직접 명령형 rule을 붙인 것이다.

핵심 지시는 다음 내용이다.

- 실험 전체에서 dye를 넣지 말 것
- 문헌 검색이나 다른 아이디어보다 우선하는 executive order로 취급할 것
- BO가 dye 포함 후보를 만들더라도 LLM은 그런 BO point를 선택하지 말 것

조건은 batch size 10, 15 batches, 10 repeat runs다.

| 모델/조건 | 25회 후 평균 HER | 150회 후 평균 HER | 명령 준수 | 최적점 도달 |
|---|---:|---:|---:|---:|
| gemini-2.5-pro medium | 10.9 | 17.2 | 9/10 | 0/10 |
| o4-mini medium | 5.9 | 17.4 | 0/10 | 0/10 |
| o3 medium | 9.3 | 23.4 | 2/10 | 1/10 |
| gemini-2.5-pro high | 12.7 | 22.0 | 10/10 | 0/10 |
| gpt-5 medium | 10.1 | 24.8 | 10/10 | 2/10 |
| gpt-5 high | 7.1 | 26.6 | 10/10 | 4/10 |

이 결과는 두 가지를 보여준다.

첫째, instruction following 능력은 모델마다 크게 다르다. o4-mini는 0/10, o3 medium은 2/10만 끝까지 명령을 지켰다. 반면 gpt-5는 medium/high 모두 10/10 지켰다.

둘째, 명령을 잘 지킨다고 성능이 항상 최고는 아니다. "dye 금지" 자체는 유리한 지시지만, 최종 성능은 다른 reasoning 품질과 탐색 전략에도 의존한다. gpt-5 high가 평균 HER 26.6으로 가장 좋았지만, gemini-2.5-pro medium은 명령을 9/10 지켰음에도 최종 평균은 17.2에 그쳤다.

발표에서는 이 부분을 "LLM prompt를 hard constraint처럼 쓰려면 모델의 instruction-following 신뢰도를 별도로 검증해야 한다"는 메시지로 가져가면 좋다.

#### 3. Prior experimental data와 literature prompt

마지막으로 gpt-5/BO hybrid에 외부 자료를 붙였다.

- No additional prompt
- Prior experimental data: GPR oracle model을 만들 때 사용한 1027개 실제 실험 CSV
- Nature 2020 paper: 같은 photocatalysis 연구의 논문 PDF
- Data + paper: CSV와 PDF를 모두 제공

조건은 gpt-5/BO hybrid, batch size 10, 15 batches, 20 repeat runs다.

| 조건 | 25회 후 평균 HER | 150회 후 평균 HER | 150회 후 STD | 최적점 도달 횟수 |
|---|---:|---:|---:|---:|
| gpt-5 no prompt | 7.5 | 25.1 | 4.2 | 9/20 |
| + experimental data | 23.2 | 26.6 | 2.7 | 11/20 |
| + Nature 2020 paper | 18.5 | 21.8 | 1.5 | 0/20 |
| + data and paper | 22.5 | 27.0 | 2.2 | 13/20 |

가장 흥미로운 결과는 literature만 붙인 조건이다. Nature 2020 paper는 초반 warm-start를 크게 개선했다. 25회 후 HER이 7.5에서 18.5로 증가했다. LLM이 paper에서 dye/surfactant 회피, base synergy 같은 유용한 지식을 뽑았기 때문이다.

하지만 150회 후 최종 성능은 오히려 25.1에서 21.8로 나빠졌고, 최적점 도달은 0/20이었다. 저자들은 그 이유를 NaCl bias로 해석한다. 2020 paper에서는 NaCl이 약간 긍정적이지만 base보다 덜 중요해 최종적으로 deselect되었다는 식의 메시지가 있었다. 그런데 GPR oracle을 만든 후속 데이터에서는 NaCl 1 mL 근처가 실제 최고 조성에 중요했다. LLM은 오래된 논문을 너무 신뢰해 NaCl을 낮게 유지하는 방향으로 bias를 갖게 되었고, 이 때문에 최종 탐색이 제한되었다.

반대로 experimental data CSV를 붙이면 성능이 좋아졌다. 20회 중 11회가 최적 HER에 도달했고, 그중 8회는 첫 번째 실험에서 바로 maximum을 찍었다. 다만 gpt-5가 CSV 안의 best condition을 항상 정확히 식별하지는 못했다. 논문은 이것을 "사람 연구자라면 보통 이전 best experiment를 첫 실험으로 반복했을 것"이라며 LLM이 파일 처리와 best-row identification에서 인간보다 못한 사례로 본다.

Data와 paper를 함께 붙인 조건은 평균 HER 27.0, 최적점 13/20으로 가장 좋았다. CSV의 최신 실험 데이터가 paper의 NaCl bias를 상쇄했기 때문이다.

#### 프롬프트 관련 핵심 정리

프롬프트는 성능을 올리는 knowledge injection이지만 동시에 search bias다. 좋은 프롬프트는 초반을 빠르게 만들고, 나쁜 프롬프트는 초반 budget을 낭비하게 한다. 더 중요한 점은 "좋아 보이는 프롬프트"도 너무 구체적이면 long-run optimum을 막을 수 있다는 것이다.

따라서 closed-loop 실험에서 LLM prompt를 설계할 때는 다음 원칙이 필요하다.

- 구체적 수치 제약보다 일반 원리와 방향성을 준다.
- prior literature는 최신 데이터와 충돌할 수 있음을 명시한다.
- hard rule을 줄 때는 해당 모델이 실제로 끝까지 따르는지 검증한다.
- CSV/PDF를 붙일 때는 LLM이 best row, 최신성, 데이터 출처 차이를 제대로 해석하는지 확인한다.
- prompt 조건별 반복 run을 통해 outlier와 fixation을 반드시 본다.

### 결과 해석

Photocatalysis 문제에서 LLM이 강했던 이유는 변수들이 화학적 의미를 가진다는 점이다. LLM은 dye, surfactant, base, salt, sacrificial donor라는 개념적 범주를 이용해 search space를 줄였다. 특히 "dye가 나쁘다"는 것을 개별 dye 3개에 대해 따로 배우는 대신 하나의 class-level rule로 일반화했다.

그러나 실패 모드도 분명하다.

- formatting failure가 나면 random fallback이 발생해 warm-start가 망가질 수 있다.
- 일부 run에서는 LLM이 잘못된 hypothesis에 fixation된다.
- prior literature를 붙이면 항상 좋아지는 것이 아니다. 오래된 문헌의 "NaCl을 넣지 말라"는 식의 bias가 최신 데이터와 충돌할 수 있다.
- "P10 > 4 mg"처럼 그럴듯하지만 너무 구체적인 human hypothesis는 최적점 근처 탐색을 방해할 수 있다.

## 3. 실험 상황 B: 7-D Petanque Physics Simulation

### 실험 문제

두 번째 문제는 저자들이 만든 7차원 petanque 물리 시뮬레이션이다. 목표는 던진 공이 target ball, 즉 jack에 최대한 가까이 멈추도록 하는 것이다.

점수는 0-100이며, 100은 jack과의 거리가 0인 완벽한 shot을 의미한다. Photocatalysis와 달리 단일 조성 최적점이 있는 것이 아니라, 100점에 도달할 수 있는 유효 해가 많이 존재한다.

입력 변수는 pitch, yaw, velocity, spin, mass 등 투사체 운동을 결정하는 물리 변수들이다. 논문은 이 문제를 7-D physics-based simulation으로 설명한다.

### 기본 hybrid 조건

- 15 batches x 10 experiments = 총 150 experiments
- 20 repeat runs
- 처음 5 batches는 LLM warm-start
- 비교 조건: BO-only, o4-mini/BO, o3/BO, gpt-5/BO

### Hybrid 결과

| 조건 | 25회 후 평균 score | 150회 후 평균 score | 150회 후 STD |
|---|---:|---:|---:|
| BO-only | 9.3 | 52.6 | 26.8 |
| o4-mini/BO | 66.2 | 94.1 | 11.7 |
| o3/BO | 59.9 | 98.2 | 2.8 |
| gpt-5/BO | 63.9 | 99.2 | 0.9 |

BO-only는 평균 52.6에 그쳤고, 표준편차도 26.8로 매우 컸다. 반면 LLM/BO hybrid는 모두 100점에 가까운 점수로 수렴했다. gpt-5/BO는 평균 99.2, STD 0.9로 가장 안정적이었다.

### LLM-only 결과

o3 기준으로는 LLM-only가 hybrid보다 약간 더 좋았다.

| 조건 | 150회 후 평균 score | STD |
|---|---:|---:|
| BO-only | 52.6 | 26.8 |
| o3/BO hybrid | 98.2 | 2.8 |
| o3-only | 99.5 | 1.2 |

Petanque에서는 BO가 직접 성능을 올리는 기여가 photocatalysis보다 작았다. 한 o3/BO run 분석에서 BO sampling은 LLM reasoning을 위한 추가 데이터는 제공했지만, best score를 직접 갱신한 것은 LLM hypothesis였다.

### 결과 해석

Petanque 문제에서 LLM이 강했던 이유는 underlying physics가 명확하기 때문이다. LLM은 projectile motion, drag, Magnus lift, backspin, pitch-velocity tradeoff 같은 물리 개념을 이용해 초반부터 고득점 영역을 제안했다.

반면 BO는 이 문제가 낮은 차원임에도 어려웠다. 이유는 optimal solution이 "knife-edge"에 놓여 있기 때문이다. pitch, velocity, spin이 아주 조금만 바뀌어도 점수가 크게 떨어진다. 논문 예시에서 LLM은 최종 sensitivity 분석으로 velocity ±0.1 m/s, pitch ±0.05도, spin ±100 rpm 변화만으로도 점수가 크게 변한다고 설명했다.

즉, 이 문제는 차원 수보다 landscape geometry가 중요하다. 7-D라서 쉬운 것이 아니라, 고득점 ridge가 매우 좁기 때문에 black-box BO가 안정적으로 찾기 어렵다. LLM은 물리 법칙을 이용해 처음부터 plausibly good region을 좁힐 수 있었다.

## 4. 두 실험의 비교

| 항목 | Photocatalysis | Petanque |
|---|---|---|
| 문제 성격 | 화학/재료 최적화 | 물리 시뮬레이션 최적화 |
| 차원 | 10-D | 7-D |
| 목표 | HER 최대화 | jack과의 거리 최소화, score 최대화 |
| 최댓값 | 28.37 mmol h^-1 | 100 |
| 어려운 점 | 의미 있는 조합이 sparse하고, 많은 조합이 HER 거의 0 | optimum ridge가 매우 좁음 |
| LLM의 핵심 이점 | 변수의 semantic grouping, 화학적 hypothesis 생성 | 알려진 물리 법칙 기반의 초기 search narrowing |
| BO-only 한계 | ontology가 없어 dye class 같은 일반화를 못 함 | knife-edge landscape에서 분산이 큼 |
| 가장 강한 결과 | o3-only, batch size 1: 평균 HER 27.0, 최적점 15/20 | o3-only 평균 99.5 또는 gpt-5/BO 평균 99.2 |
| 주요 실패 모드 | literature bias, prompt sensitivity, formatting failure, fixation | 약한 모델의 지나치게 일반적인 hypothesis |

## 5. 발표에서 강조할 만한 insight

### Insight 1. LLM은 optimizer라기보다 "semantic compression engine"으로 봐야 한다.

BO는 변수 간 상관관계를 숫자로 배운다. 하지만 LLM은 변수들을 의미 단위로 압축한다. Photocatalysis에서 세 dye를 하나의 harmful class로 묶은 것이 대표적이다. 이 능력은 고차원 실험에서 매우 크다.

### Insight 2. LLM의 prior knowledge보다 iterative reasoning이 더 중요할 수 있다.

Batch size가 작아질수록 성능이 좋아졌다는 점이 중요하다. 이는 LLM이 "처음부터 알고 있어서" 잘하는 것이 아니라, 새 실험 결과를 보고 hypothesis를 반복적으로 수정할 때 가장 강해진다는 뜻이다.

### Insight 3. LLM-only가 BO를 대체할 수 있는 문제군이 있을 수 있다.

이 논문에서 o3-only는 photocatalysis와 petanque 모두에서 BO-only를 크게 이겼고, 일부 조건에서는 LLM/BO hybrid도 넘었다. 특히 petanque에서는 BO가 best score 갱신에 거의 기여하지 못했다. 다만 이것을 일반화하려면 noisy wet-lab 검증이 필요하다.

### Insight 4. LLM을 붙인다고 항상 더 robust해지는 것은 아니다.

LLM은 stochastic하고 outlier run이 존재한다. formatting failure, instruction-following failure, bad hypothesis fixation, prior literature over-trust가 모두 관찰됐다. 따라서 closed-loop 실험에 LLM을 넣을 때는 단일 성공 사례가 아니라 반복 run과 failure-mode audit이 필요하다.

### Insight 5. Human prior는 "좋은 방향성"과 "잘못된 제약"을 동시에 준다.

좋은 hypothesis는 warm-start를 개선하지만, 너무 구체적인 수치 조건은 탐색을 좁혀 최적점 도달을 방해할 수 있다. 발표에서 중요한 메시지는 "human knowledge injection은 정답 주입이 아니라 bias 주입"이라는 점이다.

### Insight 6. Literature search와 scientific reasoning은 다르다.

LLM이 관련 논문을 찾는 것과 그 논문의 정보를 현재 optimization에 맞게 우선순위화하는 것은 별개의 능력이다. Photocatalysis에서 오래된 문헌 정보는 유용한 rule도 제공했지만, NaCl 관련 bias처럼 최종 성능을 낮출 수 있는 정보도 제공했다.

### Insight 7. 문제의 "차원 수"보다 "구조를 말로 설명할 수 있는가"가 중요하다.

Photocatalysis는 10-D지만 화학적 범주가 있고, petanque는 7-D지만 물리 법칙이 명확하다. 두 경우 모두 LLM이 자연어 지식으로 search를 좁힐 수 있었다. 반대로 의미 구조가 약하거나 관측 noise가 큰 문제에서는 성능이 달라질 수 있다.

## 6. 세미나용 한 문장 결론

이 논문은 LLM이 closed-loop experiment에서 단순한 assistant가 아니라 hypothesis generator, ontology builder, candidate selector, standalone optimizer로 작동할 수 있음을 보여준다. 하지만 가장 중요한 메시지는 "LLM이 BO보다 항상 낫다"가 아니라, LLM reasoning이 강력한 탐색 bias를 제공하는 동시에 그 bias 자체가 새로운 실패 모드가 된다는 점이다.
