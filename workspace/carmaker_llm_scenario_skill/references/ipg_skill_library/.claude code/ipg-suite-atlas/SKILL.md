---
name: ipg-suite-atlas
description: Use when a task mentions IPG, CarMaker, IPGControl, Movie NX, Instrument Designer, or IPGGraph and you need to route the request to the right product, manual, example set, or companion tool.
---

# IPG Suite Atlas

`C:\IPG` 전체 제품군에서 현재 요청이 어느 제품과 어느 문서 축에 속하는지 먼저 정리하는 skill이다.

## Usage

1. `references/overview.md`를 먼저 읽는다.
2. 질문을 아래 축 중 하나로 분류한다.
   - CarMaker core workflow
   - CarMaker Python/API/integration
   - road/scenario
   - visualization/postprocess
   - data acquisition/validation
3. 필요하면 더 구체적인 하위 skill로 넘긴다.

## Routing

- 입문/첫 실행/GUI -> `carmaker-quickstart`
- project, TestRun, vehicle, trailer -> `carmaker-project-and-vehicle`
- Python runtime/simcontrol/capture -> `carmaker-python-runtime`
- Python parametrization/variation shaping -> `carmaker-python-parametrization`
- road/scenario/OpenSCENARIO/IPGRoad -> `carmaker-road-and-scenario`
- CM4SL/APO/GPU/ext integration -> `carmaker-cm4sl-and-integration`
- IPGControl/Movie NX/Instruments/Graph -> `ipg-visualization-and-postprocess`
- deep CMAPI/APO/IPGRoad/GPU API -> `carmaker-advanced-apis`
- data request/validation -> `carmaker-data-validation`
