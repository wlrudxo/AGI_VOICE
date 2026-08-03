# ICCAS 2026 (#346) 리뷰 코멘트 대응 기록

- 논문: Simulator-in-the-Loop MPC Weight Tuning Using LLM-Based Search and Bayesian Optimization
- 결정: Accept (camera-ready 마감 2026-08-31, 6페이지 제한)
- 대응 커밋: `39a8392` (리뷰 반영), `4f1a1dc` (어법 정리)
- 대응 원칙: 추가 실험 없이 재현성·판정 기준만 실질 보완하고, 나머지는 claim calibration으로 처리. 최종본 6페이지 유지.

## Reviewer 1

### 1. LLM-based search 절차의 재현성 부족
- **판단**: 일부 타당. 전체 prompt/로그 수록은 지면상 불가.
- **대응**: 4.2절에 per-trial 절차 보강 — trial당 1개 후보를 다른 방법과 동일한 평가 파이프라인으로 제출, search bounds는 매 trial task context에 제공됨을 명시.

### 2. LLM vs BO 비교의 공정성 (candidate-selection overhead 차이)
- **판단**: 논점은 있으나 본 논문의 연구 질문(시뮬레이션 횟수 기준 효율)과는 별개.
- **대응**: 4.2절에 scope 문장 1개 추가 — "The comparison concerns simulator-evaluation efficiency, not candidate-selection time or cost, which differs between GP fitting and LLM inference." 별도 wall-clock/비용 측정 실험은 하지 않음.

### 3. 단일 slalom 시나리오 한정
- **판단**: 이미 명확한 한계. 신규 시나리오 실험은 불가.
- **대응**: Conclusion에 limitation 문장 추가 — 결과는 단일 CarMaker-Simulink slalom 벤치마크의 5회 반복에 기반한 exploratory comparison이며 일반 주행 조건 성능으로 해석하지 말 것. Future work에 broader scenarios/friction conditions 유지.

### 4. 5회 반복은 통계적 결론에 부족
- **판단**: 맞지만 추가 반복 실험은 하지 않음. 5회 결과에 유의성 검정을 붙이는 것은 오히려 부적절 — raw outcome(4/5, 3/5)을 그대로 보여주고 exploratory로 한정.
- **대응**: 본문 전반 claim calibration.
  - "LLM-based search is more effective as a rapid feasibility-seeking mechanism" → "in the five evaluated repetitions ... exhibited earlier feasibility discovery"
  - "consistent with its role as a reliable feasibility-seeking method" → "consistent with the feasibility-seeking behavior observed in these experiments"
  - Conclusion에 "exploratory comparison" 한정 + future work에 larger repetition counts 추가.

### 5. Cone contact / road departure 판정 기준 불명확
- **판단**: 가장 실질적인 지적. 구현 확인 후 반영 (`analyze_results_mat.m`, `erg_drive_summary.py`).
- **대응**: 2.4절(Simulation-Based Objective)에 정의 추가.
  - $I_{\mathrm{fail}}$: road departure로 시뮬레이션이 조기 종료된 경우 1.
  - Cone contact: 시나리오의 접촉 감지로 검출, 접촉별 도로 위치 기록. $N_{\mathrm{hit}}$은 첫 슬라럼 게이트 이후 접촉만 카운트.
  - Entry 구간 제외 사유: 초기 과도응답에서 기준 경로로 수렴하는 구간이라 평가 대상 기동이 아님.

### 6. Sparse-feasible-region 주장이 증거보다 강함
- **판단**: 타당, 저비용 수정.
- **대응**: 표현 완화.
  - Abstract: "indicating that feasible weight regions are sparse" → "showing a low hit-free fraction among the evaluated samples"
  - 5.3절: "hit-free regions are sparse" → "hit-free samples are rare under uniform sampling"
  - Conclusion: "occupy sparse regions" → "shows a low hit-free fraction under uniform sampling"
  - 기존 hedge("does not characterize the full feasible set")는 유지.

### 7. Tuned weight의 일반화(robustness) 미평가
- **판단**: 6페이지 논문 범위 초과. 신규 실험 생략.
- **대응**: Conclusion limitation 문장(코멘트 3과 공동 대응)으로 처리.

### 8. MPC 구현 세부 파라미터 부족
- **판단**: 지나치게 포괄적·비구체적. 모든 차량/컨트롤러 파라미터 공개는 불필요.
- **대응**: 무대응 (기존 본문에 $T_s$, $N_p$, $N_c$, steering 제약 이미 명시됨).

### 9. 기존 LLM-assisted BO 대비 novelty 불명확
- **판단**: 유용한 지적. 새 문단 없이 contribution 문장 교체로 처리.
- **대응**: 세 번째 contribution 교체 — "Unlike prior work coupling an LLM to a BO loop, the LLM is used as a standalone sequential candidate proposer and compared against BO under an identical simulator budget, separating feasibility discovery from objective minimization."

## Reviewer 2

### 1. 4.2절 첫 문단 마지막 문장 마침표 누락
- **판단**: 리뷰어 착오로 판단 — tex상 해당 문장에 마침표 존재.
- **대응**: 무조치. (다만 분량 압축 과정에서 해당 주변 문장이 재작성됨.)

### 2. LLM 후보의 search bounds 초과 시 처리 방식 미기술
- **판단**: 타당하고 저비용. 구현 및 로그 확인 후 반영.
- **대응**: 4.2절에 추가 — bounds는 매 trial task context에 제공되며, 5회 반복의 전체 LLM 제안(5 seed × 50 trial = 250건 로그 스캔으로 확인)이 모두 bounds 내에 있어 clipping/rejection이 발생하지 않았음을 명시. "all LLM proposals across the five repetitions remained within these bounds, so no clipping or rejection was needed."

### 3. 5회 반복이 성능 차이 주장을 뒷받침하기에 충분한지
- **판단**: Reviewer 1 코멘트 4와 동일.
- **대응**: 동일한 claim calibration + Conclusion limitation 문장으로 처리.

## 분량 확보를 위한 압축 (의미 변경 없음)

추가 문장으로 7페이지로 넘쳐 아래를 압축해 6페이지 복귀:

- "Sobol은 optimizer baseline이 아님" 3회 반복(3.2 / 4.2 / 5장 서두) → 3.2절 1회로 통합
- Intro 4번째 문단, 2.3절 black-box 설명, 3.1절 공통 파이프라인 설명, 4.1절 시나리오 설명, 5.1~5.3절 해석 문장들의 군더더기 제거
- BO acquisition 뒤 동어반복 문장, "R1--R6 are not separate search methods" 문장 삭제
