---
name: carmaker-python-parametrization
description: Use when the task is to load or modify CarMaker TestRun, vehicle, trailer, or other parametrization objects from Python and shape new variations programmatically.
---

# CarMaker Python Parametrization

project contents를 코드로 읽고 바꾸는 질문에 대응하는 skill이다.

## Usage

1. `references/overview.md`를 먼저 읽는다.
2. 아래 작업 중 무엇인지 확정한다.
   - project load
   - TestRun load
   - vehicle/trailer load
   - parameter 변경
   - variation clone and override

## Working style

- path와 객체 관계를 먼저 정리한다.
- parameter 변경인지 key-value override인지 구분한다.
- variation을 만들 때 clone 기준이 무엇인지 분명히 한다.
