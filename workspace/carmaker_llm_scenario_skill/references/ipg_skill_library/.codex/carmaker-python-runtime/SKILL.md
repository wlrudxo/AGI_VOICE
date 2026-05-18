---
name: carmaker-python-runtime
description: Use when the user wants to execute CarMaker from Python, queue variations, use Runtime or SimControl, read or write quantities, wait on conditions, or capture simulation data.
---

# CarMaker Python Runtime

`Runtime`, `SimControlInteractive`, quantity access, capture 흐름을 다루는 skill이다.

## 먼저 할 일

1. `references/overview.md`를 먼저 읽는다.
2. 질문을 아래 둘 중 하나로 분기한다.
   - batch execution/runtime queue
   - live control/simcontrol/conditions/capture
3. 항상 아래 정보를 먼저 확인한다.
   - project path
   - TestRun or Variation source
   - live connection 필요 여부

## 답변 규칙

- 최소 실행 골격을 먼저 제시한다.
- runtime와 simcontrol 중 어느 쪽이 맞는지 이유를 말한다.
- capture/watcher/read-write는 실행 흐름 뒤에 붙인다.

## Representative prompts

- “Python으로 variation을 실행하고 끝날 때까지 기다리고 싶다”
- “SimControlInteractive로 속도 조건이 만족될 때까지 기다리고 싶다”
- “quantity를 캡처해서 파일로 떨구고 싶다”
