# 00 Product Atlas

## 목적

`C:\IPG` 설치 트리를 사람이 빠르게 이해하고, 어떤 질문에서 어느 제품/문서/예제를 먼저 열어야 하는지 정하는 기준 문서다.

## 최상위 설치 구조

- `C:\IPG\carmaker`
  - 주력 시뮬레이션 제품. 이번 skill 라이브러리의 중심축이다.
- `C:\IPG\control`
  - 신호 모니터링, 다이어그램, 온라인/오프라인 데이터 소스 분석용 `IPGControl`
- `C:\IPG\graph`
  - 그래프/플롯 정의와 튜토리얼 자산 중심의 `IPGGraph`
- `C:\IPG\instruments`
  - 시뮬레이션 중 quantity를 모니터/제어하는 대시보드 도구 `Instrument Designer`
- `C:\IPG\movienx`
  - 3D 장면, 렌더링, Python API를 제공하는 `Movie NX`
- `C:\IPG\doc`
  - 공통 EULA

## CarMaker 설치 구조

주 버전:

- `C:\IPG\carmaker\win64-14.0.1`

핵심 하위 폴더:

- `doc`
  - HTML help와 PDF manuals
- `Examples`
  - Python, GPUCodingInterface, ADTF, FMI, Matlab 등 샘플
- `Python`
  - `python3.8`~`python3.12`용 `cmapi`, `ASAM`, `IPG`
- `CM4SL`
  - CarMaker for Simulink 관련 자산
- `Movie`
  - Movie 관련 카탈로그/렌더링 자산
- `Templates`
  - RTW, project update, 모델 확장 템플릿
- `Plugins`, `SimInput`, `TrafficSigns`, `Data`
  - 부가 자산

## CarMaker 문서 중심축

다음 문서 세트가 실제 skill 설계의 기준이 된다.

- `doc\QuickStartGuide`
  - 입문, 대표 workflow, Scenario Editor, ADAS, powertrain, CM4SL 출발점
- `doc\InstallationGuide`
  - 설치/환경 준비
- `doc\APO`
  - 네트워크 quantity 연결과 broker/client/server 개념
- `doc\CMAPI`
  - C++/Python API 개념과 클래스 레퍼런스
- `doc\IPGRoadAPI`
  - 도로 생성/변환용 API reference
- `doc\OpenSCENARIO`
  - schema 자산 중심
- `doc\RequestForm`
  - 데이터 획득 요구사항, validation 체크리스트
- PDF manuals
  - `UsersGuide.pdf`
  - `ProgrammersGuide.pdf`
  - `ReferenceManual.pdf`
  - `ProductExamples.pdf`
  - `IPGDriver.pdf`, `IPGMovie.pdf`, `IPGRoad.pdf`

## CarMaker 예제 중심축

### Python automation

위치:

- `C:\IPG\carmaker\win64-14.0.1\Examples\Python`

확인된 핵심 예제:

- `runtime_minimal_example.py`
- `runtime_full_example.py`
- `simcontrol_connect_to_server_example.py`
- `simcontrol_full_example.py`
- `parametrization_full_example.py`
- `parametrization_sim_param_example.py`
- `1_ReadWrite.py`
- `2_BasicCapturing.py`
- `3_CapturingWithDurationWatcher.py`
- `4_CapturingWithConditionWatcher.py`
- `5_CaptureToFile.py`
- `6_MultiFetch.py`
- `7_ConfigurationParameters.py`

### Advanced extension

위치:

- `C:\IPG\carmaker\win64-14.0.1\Examples\GPUCodingInterface`

특징:

- CUDA Toolkit, CMake 전제를 가진 고급 확장 예제
- lidar/radar/ultrasonic 샘플이 분리되어 있음

## Companion tool atlas

### IPGControl

- 설치: `C:\IPG\control\win64-3.0.15`
- 문서: `doc\Content\Content_IPGControl`
- 강점:
  - diagrams
  - quantities
  - online connection
  - export, snapshot, calculated signals

### Movie NX

- 설치: `C:\IPG\movienx\win64-14.0.1`
- 문서: `doc\MovieNX.pdf`, `doc\PythonApi`
- 강점:
  - 3D scene 편집/렌더링
  - Python scripting
  - scene access / annotation / node structure

### Instrument Designer

- 설치: `C:\IPG\instruments\win64-2.2.0`
- 문서: `resources\assets\doc`
- examples:
  - JSON dashboards
  - custom components (`Template.js`, gauge component examples)
- 강점:
  - simulation mode dashboard
  - quantity monitor/control
  - custom component 작성

### IPGGraph

- 설치: `C:\IPG\graph\win64-2.9.2`
- 중심 자산: `tutorial`
- 확인된 형식:
  - `.gdl`
  - tutorial data files
  - `graphlibdemo.c`
- 성격:
  - 깊은 standalone app skill보다는 plotting/reference helper에 가깝다

## Skill 라우팅 기준

- “처음 CarMaker를 어떻게 시작하지?” -> `carmaker-quickstart`
- “프로젝트/vehicle/trailer/test run을 어떻게 잡지?” -> `carmaker-project-and-vehicle`
- “Python으로 variation 실행/제어하고 싶다” -> `carmaker-python-runtime` 또는 `carmaker-python-parametrization`
- “도로/시나리오/OpenSCENARIO/IPGRoad가 필요하다” -> `carmaker-road-and-scenario`
- “Simulink, APO, GPU sensor, 외부 모델 연동” -> `carmaker-cm4sl-and-integration` 또는 `carmaker-advanced-apis`
- “plot, dashboard, render, postprocess” -> `ipg-visualization-and-postprocess`
- “입력 데이터 요구사항이나 validation 체크가 필요하다” -> `carmaker-data-validation`
