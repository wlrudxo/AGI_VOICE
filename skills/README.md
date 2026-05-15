# IPG Skill Library

이 폴더는 `C:\IPG`에 설치된 IPG Automotive 제품군을 기반으로 만든 개인용 source-library 스타일 skill 저장소다.
실사용 runtime 디렉터리에 자동 배포되는 구조가 아니라, 문서 코퍼스를 먼저 정리하고 그 위에 Codex/Claude Code용 skill 세트를 병렬로 유지하는 목적의 작업 공간이다.

## 포함 범위

- 1차 대상: `CarMaker`
- 보조 대상: `IPGControl`, `Movie NX`, `Instrument Designer`, `IPGGraph`
- 제외: live install, symlink, post-install activation automation

## 이 라이브러리에 들어 있는 것

- `docs/`
  - IPG 제품 구조, 문서 위치, 예제 위치, 권장 사용 흐름을 정리한 canonical Markdown 코퍼스
- `.codex/`
  - Codex 로컬 skill 형식에 맞춘 skill 폴더 모음
- `.claude code/`
  - Claude Code `SKILL.md` 형식에 맞춘 skill 폴더 모음

## 참조한 로컬 source 문서

주요 근거는 모두 `C:\IPG` 내부에 이미 설치된 자료다.

- CarMaker
  - `C:\IPG\carmaker\win64-15.0.1\doc\QuickStartGuide`
  - `C:\IPG\carmaker\win64-15.0.1\doc\InstallationGuide`
  - `C:\IPG\carmaker\win64-15.0.1\doc\APO`
  - `C:\IPG\carmaker\win64-15.0.1\doc\CMAPI`
  - `C:\IPG\carmaker\win64-15.0.1\doc\IPGRoadAPI`
  - `C:\IPG\carmaker\win64-15.0.1\doc\OpenSCENARIO`
  - `C:\IPG\carmaker\win64-15.0.1\doc\RequestForm`
  - `C:\IPG\carmaker\win64-15.0.1\doc\UsersGuide.pdf`
  - `C:\IPG\carmaker\win64-15.0.1\doc\ProgrammersGuide.pdf`
  - `C:\IPG\carmaker\win64-15.0.1\doc\ReferenceManual.pdf`
- CarMaker examples
  - `C:\IPG\carmaker\win64-15.0.1\Examples\Python`
  - `C:\IPG\carmaker\win64-15.0.1\Examples\GPUCodingInterface`
- Companion tools
  - `C:\IPG\control\win64-3.0.15\doc`
  - `C:\IPG\movienx\win64-14.0.1\doc`
  - `C:\IPG\instruments\win64-2.2.0\resources\assets\doc`
  - `C:\IPG\graph\win64-2.9.2\tutorial`

## 문서 코퍼스와 skill 매핑

- `docs/00-product-atlas.md`
  - 전체 제품 구조와 skill 분기 기준
- `docs/01-carmaker-quickstart-and-workflows.md`
  - 입문/GUI 기반 흐름
- `docs/02-carmaker-manual-map.md`
  - 어느 매뉴얼을 언제 열어야 하는지
- `docs/03-carmaker-python-automation.md`
  - `cmapi` Python 자동화
- `docs/04-road-scenario-and-ipgroad.md`
  - Scenario Editor, OpenSCENARIO, IPGRoad API
- `docs/05-visualization-and-postprocess.md`
  - IPGControl, Movie NX, Instruments, Graph
- `docs/06-integration-and-advanced-extension.md`
  - CM4SL, APO, GPUCodingInterface, 외부 연동
- `docs/07-data-acquisition-and-validation.md`
  - Request Form, 데이터 수집, 검증
- `docs/08-skill-map.md`
  - 최종 skill 설계의 source of truth

각 skill 폴더의 `references/overview.md`는 위 canonical docs를 재가공한 축약본이다.

## 실제 사용 경로로 승격하는 방법

이 저장소는 source library다. 아래 경로에 자동 감지되지는 않는다.

### Codex

Codex 개인 skill 기본 경로 예시:

- `C:\Users\user\.codex\skills\<skill-name>\SKILL.md`

승격 절차:

1. `C:\IPG\skills\.codex\<skill-name>` 폴더를 확인한다.
2. 필요한 skill 폴더를 `C:\Users\user\.codex\skills\` 아래로 복사한다.
3. Codex 새 세션에서 skill 이름이 노출되는지 확인한다.

### Claude Code

Claude Code 개인 skill 기본 경로 예시:

- `%USERPROFILE%\.claude\skills\<skill-name>\SKILL.md`

프로젝트 로컬 경로 예시:

- `<project>\.claude\skills\<skill-name>\SKILL.md`

승격 절차:

1. `C:\IPG\skills\.claude code\<skill-name>` 폴더를 확인한다.
2. 개인용이면 `%USERPROFILE%\.claude\skills\`, 프로젝트용이면 `<project>\.claude\skills\` 아래로 복사한다.
3. Claude Code에서 `/skill-name` 또는 자동 로드 동작을 확인한다.

## 유지 원칙

- Korean-first 설명을 사용한다.
- 제품명, API명, 클래스명, 파일 경로는 영어 원문을 유지한다.
- 로컬에 실제 존재하는 경로만 인용한다.
- skill 간 중복은 허용하되, 각 skill의 “가장 먼저 열어야 할 참고자료”는 명확히 분리한다.

## Layout Notes

- Codex skill pack은 설치된 로컬 skill 패턴에 맞춰 `SKILL.md`, `references/`, `assets/`, `agents/openai.yaml` 구조를 사용한다.
- Claude Code skill pack은 공식 skill 형식에 맞춰 `SKILL.md`와 `references/`를 기본으로 두고, 필요 시 `assets/`와 `examples/`를 추가한다.