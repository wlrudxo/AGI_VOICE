---
name: carmaker-data-validation
description: Use when the task is to structure vehicle data requests, identify missing model inputs, or design validation maneuvers, signals, and checklists from the CarMaker RequestForm materials.
---

# CarMaker Data Validation

RequestForm 기반으로 입력 데이터 요구사항과 validation scope를 정리하는 skill이다.

## 먼저 할 일

1. `references/overview.md`를 먼저 읽는다.
2. 질문을 아래 둘로 나눈다.
   - data acquisition checklist
   - validation maneuvers / signals / subsystems

## 답변 규칙

- 수집 항목과 검증 항목을 섞지 않는다.
- brake / CAN / hydraulic / vehicle dynamics처럼 하위 시스템을 먼저 분리한다.
- 실제 문서 섹션 이름을 가능한 한 같이 적는다.

## Representative prompts

- “실차 데이터 기반 모델링에 필요한 입력 항목을 정리해 달라”
- “validation maneuver와 signal checklist를 뽑아 달라”
- “brake model 관련 추가 요청 항목이 무엇인지 알려 달라”
