# 06 Integration and Advanced Extension

## 근거 위치

- `C:\IPG\carmaker\win64-15.0.1\doc\APO`
- `C:\IPG\carmaker\win64-15.0.1\doc\CMAPI`
- `C:\IPG\carmaker\win64-15.0.1\doc\QuickStartGuide\Content\Content_Quickstart-Guide\D-CarMaker-for-Simulink`
- `C:\IPG\carmaker\win64-15.0.1\Examples\GPUCodingInterface`

## APO

APO는 online quantity communication의 핵심이다.

중요 개념:

- broker
- client
- server
- quantities
- subscribe / poll / read variable data
- application-defined messages

적합한 질문:

- “외부 app에서 CarMaker quantity를 읽고 싶다”
- “IPGControl / Instruments / 자체 툴을 APO로 붙이고 싶다”
- “broker/client/server 역할이 뭐지?”

## CMAPI

`CMAPI`는 `cmapi`와 연결되는 object model reference 축이다.

확인된 클래스 축:

- `Application`
- `CarMaker`
- `ApoConnection`
- `ApoQuantity`
- `ApoServer`
- runtime/variation/project/parametrization 관련 클래스 계열

적합한 질문:

- “이 클래스가 어떤 역할인지 정확히 알고 싶다”
- “Python 예제는 알겠는데 deeper reference가 필요하다”

## CarMaker for Simulink (CM4SL)

Quick Start Guide의 `D-CarMaker-for-Simulink`는 CM4SL 진입 문서다.

확인된 토픽:

- block properties
- dictionary blocks
- sync in / sync out
- CM dict read/write
- creating first simulation with CM4SL

적합한 질문:

- “Simulink에서 CarMaker blockset을 어떻게 붙이지?”
- “dictionary와 sync block 개념을 정리해 달라”
- “기존 모델을 CM4SL로 확장하고 싶다”

## GPUCodingInterface

근거:

- `Examples\GPUCodingInterface\src.GPUCodingInterface\README.md`

확인된 전제:

- CUDA Toolkit
- CMake
- sensor data definitions in `include`
- lidar/radar/ultrasonic samples

적합한 질문:

- “GPU sensor extension을 직접 만들고 싶다”
- “radar/lidar 샘플 구조를 이해하고 싶다”
- “build prerequisites를 정리해 달라”

## 실무 라우팅

- online connectivity / broker / subscription
  - `APO`
- class/object semantics / Python-C++ conceptual bridge
  - `CMAPI`
- Simulink coupling
  - `CM4SL`
- sensor-side advanced extension
  - `GPUCodingInterface`

## 주의점

- 이 영역은 GUI 입문보다 prerequisites가 많다.
- skill은 “무엇을 먼저 확인해야 하는지”를 분명히 말해야 한다.
- runtime 제어와 protocol/API integration은 같은 질문처럼 보여도 source 문서는 다르다.
