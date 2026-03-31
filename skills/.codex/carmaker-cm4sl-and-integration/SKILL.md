---
name: carmaker-cm4sl-and-integration
description: Use when the task is about CarMaker for Simulink, APO-based online integration, or external coupling workflows that connect CarMaker to other tools or runtime environments.
---

# CarMaker CM4SL and Integration

CM4SL, APO, 외부 tool coupling을 정리하는 skill이다.

## 먼저 할 일

1. `references/overview.md`를 먼저 읽는다.
2. 질문을 아래 둘 이상으로 쪼갠다.
   - CM4SL blockset / dictionary / sync
   - APO broker/client/server
   - external tool coupling

## 답변 규칙

- Simulink면 `CM4SL` 진입 흐름을 먼저 제시한다.
- online connection이면 APO 개념을 먼저 설명한다.
- 외부 tool 연동이면 어떤 protocol 또는 app 경계를 넘는지 먼저 적는다.

## Representative prompts

- “CarMaker for Simulink에서 dictionary block이 뭔지 설명해 달라”
- “APO broker/client/server 구조를 정리해 달라”
- “외부 앱과 online quantity 연결을 어떻게 잡지?”
