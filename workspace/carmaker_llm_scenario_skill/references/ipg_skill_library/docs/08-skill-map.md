# 08 Skill Map

## 목적

이 문서는 `C:\IPG\skills` 아래 skill 세트의 source of truth다.
새 skill을 추가하거나 범위를 줄일 때 이 문서를 먼저 갱신한다.

## Skill inventory

### 1. `ipg-suite-atlas`

- 역할:
  - 제품/문서/예제 위치를 빠르게 라우팅
- 주 source:
  - `00-product-atlas.md`
- 대표 질문:
  - “이 질문은 CarMaker냐 Movie NX냐 Instruments냐?”

### 2. `carmaker-quickstart`

- 역할:
  - 입문 workflow와 첫 TestRun, 대표 기능축 진입
- 주 source:
  - `01-carmaker-quickstart-and-workflows.md`
- 대표 질문:
  - “처음 CarMaker를 어떤 순서로 써야 하지?”

### 3. `carmaker-project-and-vehicle`

- 역할:
  - project/TestRun/vehicle/trailer/dataset 관점 정리
- 주 source:
  - `01-carmaker-quickstart-and-workflows.md`
  - `02-carmaker-manual-map.md`
  - `03-carmaker-python-automation.md`
- 대표 질문:
  - “vehicle dataset와 TestRun을 어떻게 연결하지?”

### 4. `carmaker-python-runtime`

- 역할:
  - runtime queue, simcontrol, capture, live condition
- 주 source:
  - `03-carmaker-python-automation.md`
- 대표 질문:
  - “Python으로 variation 실행/제어하고 싶다”

### 5. `carmaker-python-parametrization`

- 역할:
  - project contents, TestRun, vehicle, trailer, key-value override
- 주 source:
  - `03-carmaker-python-automation.md`
- 대표 질문:
  - “programmatically vehicle/trailer/TestRun을 바꾸고 싶다”

### 6. `carmaker-road-and-scenario`

- 역할:
  - Scenario Editor, OpenSCENARIO, IPGRoad API 라우팅
- 주 source:
  - `04-road-scenario-and-ipgroad.md`
- 대표 질문:
  - “road/scenario/OpenSCENARIO 중 어디서 시작해야 하지?”

### 7. `carmaker-cm4sl-and-integration`

- 역할:
  - CM4SL, APO, external coupling, integration workflow
- 주 source:
  - `06-integration-and-advanced-extension.md`
- 대표 질문:
  - “Simulink나 APO로 붙이고 싶다”

### 8. `ipg-visualization-and-postprocess`

- 역할:
  - IPGControl, Movie NX, Instruments, Graph 선택과 사용 흐름
- 주 source:
  - `05-visualization-and-postprocess.md`
- 대표 질문:
  - “plot/render/dashboard/postprocess는 어떤 도구를 써야 하지?”

### 9. `carmaker-advanced-apis`

- 역할:
  - CMAPI object model, APO deep dive, IPGRoad API, GPUCodingInterface
- 주 source:
  - `03-carmaker-python-automation.md`
  - `04-road-scenario-and-ipgroad.md`
  - `06-integration-and-advanced-extension.md`
- 대표 질문:
  - “고급 API/class/protocol 수준으로 설명해 달라”

### 10. `carmaker-data-validation`

- 역할:
  - Request Form 기반 입력 데이터/validation 구조화
- 주 source:
  - `07-data-acquisition-and-validation.md`
- 대표 질문:
  - “어떤 데이터를 받아야 하고 어떤 validation을 해야 하지?”

## 플랫폼별 구현 정책

### Codex

- 로컬 Codex skill 형식에 맞는 간결한 `SKILL.md`
- `references/overview.md`를 먼저 열도록 유도
- 질문을 하위 source로 분기하는 style

### Claude Code

- 공식 `SKILL.md` frontmatter 사용
- description을 자동 로드 친화적으로 작성
- source-library 목적상 aggressive tool restriction은 두지 않음

## 중복 허용 원칙

- Quickstart와 project skill 사이 중복은 허용
- runtime와 advanced API 사이 중복은 허용
- 단, “어떤 질문을 이 skill이 먼저 받는가”는 분명히 써야 한다

## 유지보수 규칙

- 새 source 문서를 발견하면 먼저 `docs/`를 갱신한다
- skill 참조 요약은 그 다음에 갱신한다
- Codex와 Claude pack은 concept 이름을 최대한 동일하게 유지한다
