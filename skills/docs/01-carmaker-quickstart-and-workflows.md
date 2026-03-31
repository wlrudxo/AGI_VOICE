# 01 CarMaker Quickstart and Workflows

## 근거 문서

- `C:\IPG\carmaker\win64-14.0.1\doc\QuickStartGuide`
- Quick Start Guide 섹션:
  - `A-Introduction-Topics`
  - `B0-Create-first-TestRun`
  - `B1-Vehicle-Dynamics`
  - `B2-ADAS`
  - `B3-Powertrain`
  - `B4-Scenario-Editor`
  - `C-Procedure-Topics`
  - `C-Vehicle-model-parametrization`
  - `D-CarMaker-for-Simulink`
  - `E-Additional-information`

## 가장 먼저 잡아야 할 기본 흐름

### 1. 첫 TestRun 만들기

Quick Start Guide의 기본 입문 축은 “새 프로젝트를 이해하고 첫 TestRun을 구성해 돌리는 것”이다.

질문 예시:

- “BackAndForth 같은 기본 테스트를 어디서 시작하지?”
- “프로젝트 로딩 후 어떤 entity를 먼저 건드려야 하지?”

우선 확인할 것:

- 프로젝트 위치
- 사용할 vehicle dataset
- 선택할 TestRun 템플릿 또는 예제
- GUI 기반인지 Python/runtime 기반인지

### 2. 차량 동역학/ADAS/Powertrain 중 어느 workflow인가

Quick Start Guide는 실무 흐름을 기능 축으로 분리한다.

- `B1-Vehicle-Dynamics`
  - 차체/타이어/서스펜션/steering 등 vehicle dynamics
- `B2-ADAS`
  - ADAS 관련 센서/시나리오/동작 흐름
- `B3-Powertrain`
  - engine, gearbox, driveline, fuel consumption 등 powertrain
- `B4-Scenario-Editor`
  - scenario authoring과 도로/traffic/event 구성

skill 설계에서는 이 네 축을 모두 “quickstart skill 내부 분기 질문”으로 취급한다.

### 3. Vehicle model parametrization

`C-Vehicle-model-parametrization`는 vehicle dataset를 만들거나 수정할 때 가장 먼저 보는 practical guide다.

중요 토픽:

- `Creating-new-vehicle-data-set`
- `Saving-new-vehicle-data-set`
- `Using-import-feature`
- `Using-vehicle-data-set-generator`
- `Specifying-vehicle-submodels`
- tire / suspension / powertrain / sensors / vehicle control

### 4. CarMaker for Simulink

`D-CarMaker-for-Simulink`는 CM4SL의 최초 진입점이다.

핵심 질문:

- Simulink 쪽에서 CarMaker 환경을 어떻게 띄우는가
- dictionary block과 sync block의 역할은 무엇인가
- CM dict를 읽고 쓰는 흐름은 무엇인가

## 작업 분류 체크리스트

아래 질문에 따라 하위 skill로 보내면 된다.

- GUI로 첫 프로젝트/첫 테스트를 만들고 싶은가
- vehicle dataset를 수정하려는가
- ADAS 시나리오나 Scenario Editor가 필요한가
- powertrain 파라미터를 조정하는가
- Simulink 결합이 필요한가

## 대표적인 시작 지점

### 입문형

- `QuickStartGuide -> B0-Create-first-TestRun`
- 기본 TestRun, example project, GUI navigation

### vehicle setup형

- `QuickStartGuide -> C-Vehicle-model-parametrization`
- vehicle/trailer/tire/powertrain dataset

### scenario authoring형

- `QuickStartGuide -> B4-Scenario-Editor`
- 이후 필요 시 `OpenSCENARIO`, `IPGRoadAPI`로 확장

### Simulink coupling형

- `QuickStartGuide -> D-CarMaker-for-Simulink`
- 이후 `CM4SL` 폴더와 integration docs로 확장

## 실무용 해석

- Quick Start Guide는 “무엇이 가능한가”보다 “어떤 순서로 시작하는가”를 정하는 문서다.
- 구현형 질문이 오면 Quick Start만으로 끝내지 말고, 이후 `UsersGuide`, `ReferenceManual`, `ProgrammersGuide`, `CMAPI`, `APO` 중 어느 쪽으로 넘길지 같이 정해야 한다.
