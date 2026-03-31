# Agent Autonomous Driving Target

## Goal

CarMaker 제어의 최종 목표는:

- 앱은 `관측/수동제어/설정/backend hub`
- agent는 `시나리오 해석/추가 신호 선택/주행 전략 생성/실패 분석/재시도`

구조로 나누는 것이다.

즉, 앱 내부 LLM 기능을 계속 키우는 대신:

- backend는 CarMaker 연결과 telemetry/control API를 제공하고
- agent는 CLI 기반 런타임으로 동작하면서
- 시나리오를 읽고
- 필요한 신호를 선택하고
- 주행 전략을 만들고
- 실패 시 원인을 분석해 다음 루프를 수정한다.


## Current Assumptions

- V3 backend가 CarMaker TCP 연결의 single hub 역할을 한다.
- frontend와 agent는 backend API를 공통으로 사용한다.
- agent 실행 시 앱 trigger monitoring은 꺼 둘 수 있다.
- agent는 `GET /api/carmaker/telemetry`와 `POST /api/carmaker/command`를 기본 도구로 사용한다.
- traffic object 정보는 watched object 구조로 확장한다.


## Final Target Shape

### 1. Scenario Understanding

agent는 먼저 현재 시나리오를 파악한다.

입력:
- 사용자의 목표
  - 예: "추월 시나리오를 수행해"
  - 예: "앞차를 안전하게 추월해"
- 현재 telemetry
- traffic object 정보
- 선택적으로 scenario metadata

agent가 파악해야 하는 것:
- ego 차량 상태
  - 속도, 차선 위치, heading/yaw rate, target speed
- 주변 차량 존재 여부
  - `Traffic.nObjs`
- 어떤 객체를 집중 관측해야 하는지
  - 예: 앞차, 좌측 차선 차량, 우측 차선 차량
- 현재 요청이
  - 단발 제어인지
  - 반복 주행 목표인지
  - 실패/복구 루프인지


### 2. Signal Selection

agent는 시나리오에 따라 필요한 추가 신호를 선택한다.

예:
- 추월:
  - `Traffic.T00.sRoad`
  - `Traffic.T00.tRoad`
  - `Traffic.T00.LongVel`
  - 필요 시 `T01`, `T02`
- 차선 유지:
  - `Vhcl.tRoad`
  - `Vhcl.YawRate`
- 회복/안전:
  - `SC.State`
  - `SC.TAccel`
  - `LongCtrl.AEB.IsActive`

즉 agent는:
- 현재 상태를 보고
- 필요한 watched object를 추가 요청하고
- 다음 루프부터 더 풍부한 telemetry를 받는다.


### 3. Planning

agent는 사용자의 요청과 현재 상태를 바탕으로 두 종류의 계획을 만든다.

#### A. Immediate control commands

바로 실행할 제어 명령.

예:
- `DM.Steer.Ang = ...`
- `DM.Gas = ...`
- `DM.Brake = ...`
- `DM.v.Trgt = ...`
- `DM.LaneOffset = ...`

#### B. Runtime strategy

계속 관찰하면서 유지할 전략.

예:
- "앞차와 sRoad 차이가 20m 이하이면 감속"
- "좌측 차선이 비면 lane change"
- "추월 완료 후 원차선 복귀"

이 전략은 최종적으로
- 트리거 집합
- 혹은 agent 내부 루프 규칙
형태로 표현된다.


### 4. Execution

실행 계층은 단순해야 한다.

- telemetry는 backend에서 읽는다
- command는 backend로 보낸다
- reset/restart도 backend API로 수행한다

즉 agent는:
- 판단
- 계획
- 명령 생성
만 담당하고,

실제 CarMaker TCP 직접 제어는 backend를 통하는 것을 기본으로 한다.


### 5. Failure Handling

주행 실패를 명시적으로 다뤄야 한다.

실패 예:
- 차선 이탈
- 충돌 위험 증가
- reward 급락
- AEB 활성화
- 속도/헤딩 회복 실패
- 지정 시간 내 목표 미달성

실패 시 agent는:
1. 현재 루프 중단
2. 실패 원인 기록
3. 어떤 trigger/rule/command가 잘못됐는지 분석
4. 수정된 전략으로 다음 루프 시작

즉 단순 제어기가 아니라:
- 실행
- 평가
- 수정
루프를 가져야 한다.


## Recommended Runtime Phases

## Phase 1

CLI가 현재 상태를 읽고 명령을 보낸다.

도구:
- telemetry read
- watched object add/remove
- direct command execute
- reset
- restart

목표:
- 단발 제어와 기본 모니터링 검증


## Phase 2

CLI가 시나리오를 읽고 추가 신호를 선택한다.

예:
- 추월 시나리오면 앞차/측면차량 watched object 등록
- 필요한 ego/object state를 조합해 해석

목표:
- "상황 파악 + 필요한 신호 요청" 자동화


## Phase 3

CLI가 반복 루프를 돌며 trigger 또는 규칙 기반 제어를 수행한다.

예:
- 조건 충족 시 감속
- 좌측 차선 비면 lane change
- 추월 완료 시 복귀

목표:
- agent loop 초안 완성


## Phase 4

실패 조건과 재시도 루프를 도입한다.

예:
- failure condition 정의
- 실패 시 reset/restart
- 실패 원인 분석
- 다음 루프에서 trigger/command 수정

목표:
- recovery-capable driving agent


## Open Design Choice: Scenario vs Current State

시나리오 입력은 두 방식이 가능하다.

### A. Current-state driven

사용자가 현재 목표만 주고,
agent가 지금 telemetry를 보고 즉석에서 판단한다.

장점:
- 단순함
- DB 불필요
- 현재 바로 구현 가능

적합:
- 초기 추월 agent
- recovery agent


### B. Scenario-driven

시나리오 단위 메타데이터를 따로 관리한다.

예:
- "고속도로 추월"
- "정체구간 차선 변경"
- "RL recovery test #3"

장점:
- 반복 실험과 기록에 유리
- failure history 누적 가능

단점:
- DB/저장 구조 필요

적합:
- 후반 실험 단계
- loop tuning / benchmark


## Recommendation

지금은 `Current-state driven`으로 시작하는 것이 맞다.

즉:
- 별도 scenario DB는 아직 두지 않고
- 현재 telemetry와 사용자 목표만으로 판단
- 필요한 watched object를 agent가 동적으로 추가
- 실패/재시도 루프를 먼저 검증

그 다음에:
- 반복 실험이 많아질 때
- scenario DB 또는 skill-level memory를 추가한다.


## Initial Overtake Agent Target

첫 agent 목표는 추월 시나리오로 잡는다.

최소 기능:
- 현재 ego 상태 읽기
- `Traffic.nObjs` 확인
- 앞차 후보 watched object 선택
- 상대 차량의 `sRoad`, `tRoad`, `LongVel` 읽기
- 추월 필요 여부 판단
- 안전 시 lane change / acceleration / return command 생성
- 실패 조건 감시
  - 차선 이탈
  - AEB 활성화
  - 일정 시간 내 추월 실패

이 단계에서는:
- 트리거를 backend에 영구 저장하지 않아도 된다
- agent 내부 loop에서만 조건 판단해도 충분하다


## Summary

최종 목표는 적절하다.

핵심은:
- backend를 hub로 유지
- agent가 시나리오를 해석하고 필요한 신호를 선택
- 주행 전략을 만들고
- 실패 시 수정하는 loop를 갖는 것이다

현재는:
- skill보다 CLI/스크립트 기반 agent runtime을 먼저 만들고
- scenario DB는 나중으로 미루는 것이 적절하다


## Future Expansion

이 agent 구조는 단순 추월/복구를 넘어서, 이후 다음 기능까지 확장하는 것을 전제로 한다.

- 제어기 파라미터 튜닝
  - 주행 결과를 보고 steering / throttle / brake 관련 파라미터를 조정
  - rule 기반 제어기 또는 외부 controller의 파라미터를 반복적으로 개선

- 강화학습 가이드
  - RL 정책이 현재 어떤 상태인지 해석
  - 어떤 상황에서 실패하는지 설명
  - 어떤 관측/행동/보상 구성이 적절한지 가이드

- 강화학습 리워드 재설정
  - reward 급락 상황 분석
  - reward shaping 제안
  - 특정 실패 패턴에 대해 penalty/bonus 항목 수정안 제시

- 주행 상황 평가
  - 현재 주행이 안전한지/불안정한지/비효율적인지 평가
  - 추월, 차선 유지, 감속, 회피 등 maneuver별 품질 평가
  - 실패 원인과 개선 포인트를 구조화해서 기록

즉 최종적으로는 agent가:
- 실시간 제어 판단
- 실패 복구
- 성능 평가
- 학습/튜닝 지원

까지 담당하는 형태를 목표로 한다.
