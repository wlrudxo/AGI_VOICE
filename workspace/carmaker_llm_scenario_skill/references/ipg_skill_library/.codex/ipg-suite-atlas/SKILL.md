---
name: ipg-suite-atlas
description: Use when a task mentions IPG, CarMaker, IPGControl, Movie NX, Instrument Designer, or IPGGraph and you need to route the question to the right product, manual, example set, or companion tool.
---

# IPG Suite Atlas

`C:\IPG` 전체 제품군에서 지금 질문이 어느 제품과 어느 문서 축에 속하는지 먼저 정리하는 skill이다.

## 먼저 할 일

1. `references/overview.md`를 먼저 읽는다.
2. 질문을 아래 다섯 축 중 하나로 분류한다.
   - CarMaker core workflow
   - CarMaker Python/API/integration
   - road/scenario
   - visualization/postprocess
   - data acquisition/validation
3. 필요하면 아래 하위 skill로 넘긴다.

## 라우팅 규칙

- 입문/첫 실행/GUI -> `carmaker-quickstart`
- project, TestRun, vehicle, trailer -> `carmaker-project-and-vehicle`
- Python runtime/simcontrol/capture -> `carmaker-python-runtime`
- Python parametrization/variation shaping -> `carmaker-python-parametrization`
- road/scenario/OpenSCENARIO/IPGRoad -> `carmaker-road-and-scenario`
- CM4SL/APO/GPU/ext integration -> `carmaker-cm4sl-and-integration`
- IPGControl/Movie NX/Instruments/Graph -> `ipg-visualization-and-postprocess`
- deep CMAPI/APO/IPGRoad/GPU API -> `carmaker-advanced-apis`
- data request/validation -> `carmaker-data-validation`

## Representative prompts

- “이 IPG 질문은 어느 제품 문서를 먼저 봐야 하지?”
- “CarMaker 말고 Movie NX를 써야 하나?”
- “dashboard냐 diagram이냐 render냐를 구분해 달라”
