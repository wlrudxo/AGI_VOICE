# 03 CarMaker Python Automation

## 근거 위치

- Python packages:
  - `C:\IPG\carmaker\win64-15.0.1\Python\python3.11\cmapi`
  - 동일 구조가 `python3.8`~`python3.12`에 반복 존재
- Examples:
  - `C:\IPG\carmaker\win64-15.0.1\Examples\Python`

## 확인된 API 축

`cmapi` 폴더에는 다음과 같은 핵심 모듈이 확인된다.

- `runtime`
- `project`
- `variation`
- `testrun`
- `vehicle`
- `parametrization`
- `simcontrol`
- `simcontrol_batch`
- `simcontrol_interactive`
- `simio`
- `task`
- `application_carmaker`
- `gpusensornxserver`

즉, Python 자동화는 크게 두 층으로 나눌 수 있다.

- parametrization/workspace 구성
- runtime/simcontrol 기반 실행 제어

## 예제 기반 분류

### runtime 계열

- `runtime_minimal_example.py`
- `runtime_full_example.py`

핵심 흐름:

1. `Runtime.create_default_runtime()`
2. `Project.load(project_path)`
3. TestRun parametrization 로드
4. `Variation.create_from_testrun(...)`
5. variation queue
6. runtime start / wait / stop

이 축은 “batch execution”과 “variation execution” 출발점이다.

### simcontrol 계열

- `simcontrol_connect_to_server_example.py`
- `simcontrol_full_example.py`

핵심 흐름:

1. variation 준비
2. `SimControlInteractive()` 생성
3. `CarMaker()` master 설정
4. GPU sensor 등 외부 구성 설정
5. `start_and_connect()`
6. `start_sim()`
7. quantity condition 또는 simstate condition 대기
8. `stop_and_disconnect()`

이 축은 “실시간 interactive control” 출발점이다.

### parametrization 계열

- `parametrization_full_example.py`
- `parametrization_sim_param_example.py`

핵심 흐름:

1. `Project.load(project_path)`
2. TestRun / vehicle / trailer parametrization 로드
3. parameter value 변경
4. `Variation` clone 또는 key-value 확장
5. variation naming / testrun clone

이 축은 “project contents를 프로그래밍적으로 바꾸는 작업” 출발점이다.

### capturing / signal access 계열

- `1_ReadWrite.py`
- `2_BasicCapturing.py`
- `3_CapturingWithDurationWatcher.py`
- `4_CapturingWithConditionWatcher.py`
- `5_CaptureToFile.py`
- `6_MultiFetch.py`
- `7_ConfigurationParameters.py`

이 축은 “quantity read/write, watcher, capture to file” 질문에 대응한다.

## 기본 사고 모델

### Project

- 실제 CM project directory를 가리킨다.
- 대부분의 자동화는 `Project.load(...)`가 출발점이다.

### TestRun parametrization

- 특정 run configuration의 실질적인 설정 집합
- variation의 기반이 된다.

### Vehicle / Trailer parametrization

- TestRun에 꽂히는 개별 dataset
- 파라미터 변경 또는 key-value override의 대상

### Variation

- TestRun 기반 실행 단위
- clone, rename, override가 자연스럽다

### Runtime

- queue를 실행하는 runner
- 비대화형 일괄 실행에 적합

### SimControlInteractive

- 실행 중 상태와 quantity를 다루는 상호작용형 제어기
- live condition wait, dva read, sensor coupling에 적합

## 언제 어느 skill로 분기할까

- variation 생성/vehicle 교체/trailer 부착
  - `carmaker-python-parametrization`
- runtime queue/start/wait/stop
  - `carmaker-python-runtime`
- simstate/quantity condition wait, interactive execution
  - `carmaker-python-runtime`
- quantity capture/read/write/file export
  - `carmaker-python-runtime`

## 실무 규칙

- “프로젝트 경로”와 “TestRun 상대 경로”를 항상 먼저 확정한다.
- 예제 스크립트는 실제 production script의 최소 골격으로 쓰기 좋다.
- live control이 필요 없으면 `Runtime`부터, live control이 필요하면 `SimControlInteractive`부터 본다.
