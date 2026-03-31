# 07 Data Acquisition and Validation

## 근거 위치

- `C:\IPG\carmaker\win64-14.0.1\doc\RequestForm`

확인된 섹션:

- `General-points`
- `Data-acquisition`
- `Example-skc-file`
- `Parameters-for-brake-model`
- `Validation`

## 이 문서의 역할

`RequestForm`은 단순 사용 설명서가 아니라, 모델링/검증 작업 전에 어떤 데이터를 받아야 하는지 정리하는 요구사항 문서에 가깝다.

즉, 다음 상황에서 중요하다.

- OEM/실차 데이터로 vehicle model을 만들려는 경우
- brake, steering, tire, suspension, powertrain 데이터를 어떻게 요청해야 하는지 정리해야 하는 경우
- validation scope를 사전에 정의해야 하는 경우

## Data acquisition 축

확인된 주제:

- general data
- axis systems
- aerodynamics
- brake system
- kinematics compliance
- powertrain
- spring damper
- steering
- tire characteristics
- vehicle masses geometry
- wavefront file

해석:

- vehicle model 생성/보정 전에 필요한 입력 데이터 checklist를 만들 때 가장 유용하다.

## Validation 축

확인된 주제:

- maneuvers
- signals
- CAN signals
- validation of vehicle dynamics
- validation of CAN communication
- validation of the hydraulic system

해석:

- validation question이 오면 “무슨 maneuver와 signal을 준비해야 하는가”를 먼저 구조화해야 한다.

## Brake model parameters

별도 섹션이 존재하므로, brake 관련 질문은 일반 vehicle setup와 분리해서 보는 편이 좋다.

## 실무용 질문 템플릿

- “이 차량을 모델링하려면 어떤 입력 데이터를 받아야 하지?”
- “validation maneuver와 signals를 어떻게 정리하지?”
- “brake/hydraulic/CAN validation 범위를 어떻게 잡지?”

## skill 설계 원칙

- 답변은 반드시 두 갈래로 나눈다:
  - 입력 데이터 수집
  - 검증 항목 설계
- 가능한 경우 parameter category를 명시하고, 실제 로컬 문서 섹션 이름을 같이 적는다.
