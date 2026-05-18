---
name: carmaker-project-and-vehicle
description: Use when the task is about CarMaker project structure, loading a project, choosing a TestRun, selecting a vehicle or trailer, or understanding how datasets relate inside a run configuration.
---

# CarMaker Project and Vehicle

project, TestRun, vehicle, trailer, dataset 관계를 정리할 때 쓰는 skill이다.

## 먼저 할 일

1. `references/overview.md`를 먼저 읽는다.
2. 질문이 GUI 중심인지 Python parametrization 중심인지 구분한다.
3. 아래 핵심 객체를 먼저 명확히 한다.
   - project path
   - TestRun path
   - vehicle dataset path
   - trailer dataset path

## 핵심 규칙

- “어떤 프로젝트를 기준으로 작업하는가”를 먼저 고정한다.
- TestRun과 vehicle dataset은 같은 것이 아니다.
- trailer, tire, submodel은 필요할 때만 추가 분기한다.

## Representative prompts

- “TestRun과 vehicle dataset 관계를 설명해 달라”
- “trailer를 붙이는 구조를 정리해 달라”
- “프로젝트 안에서 어떤 데이터셋을 먼저 찾아야 하지?”
