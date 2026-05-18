# 02 CarMaker Manual Map

## 목적

CarMaker 관련 질문에서 어떤 manual을 먼저 열어야 할지 결정하는 라우팅 문서다.

## 핵심 manuals

### `UsersGuide.pdf`

사용처:

- GUI 사용법
- 프로젝트 운영
- 일반 사용자 관점의 기능 흐름
- procedure 중심 질문

먼저 열어야 하는 경우:

- “이 메뉴/기능은 GUI에서 어디 있지?”
- “프로젝트를 어떻게 만들고 관리하지?”
- “일반적인 사용자 흐름이 궁금하다”

### `ProgrammersGuide.pdf`

사용처:

- 프로그래머 관점의 확장/통합
- custom code, hooks, build, template 기반 확장
- 외부 모델/기능 추가

먼저 열어야 하는 경우:

- “custom model을 붙이고 싶다”
- “template 기반으로 확장하고 싶다”
- “source-level integration 포인트가 어디지?”

### `ReferenceManual.pdf`

사용처:

- 키/파라미터/레퍼런스 조회
- 특정 parameter, quantity, object의 정확한 정의 탐색

먼저 열어야 하는 경우:

- “이 key/value가 정확히 뭘 의미하지?”
- “parameter 이름/카테고리/정의가 필요하다”

### `InstallationGuide`

사용처:

- 설치 확인
- 환경 요구사항
- setup/repair 질문

먼저 열어야 하는 경우:

- “설치가 꼬였다”
- “어떤 구성요소가 필요한가”
- “버전/환경 준비를 확인하고 싶다”

### `QuickStartGuide`

사용처:

- 입문 workflow
- 기능별 첫 진입 순서

먼저 열어야 하는 경우:

- “어디서부터 시작하지?”
- “처음 workflow를 잡아 달라”

## API / protocol manuals

### `APO`

사용처:

- online connection
- broker / client / server
- quantity subscription
- network communication

먼저 열어야 하는 경우:

- “실행 중 quantity를 외부에서 읽고 싶다”
- “APO broker/client/server 구조가 궁금하다”
- “IPGControl / Instruments / 외부 app와 online 연결하고 싶다”

### `CMAPI`

사용처:

- `cmapi` 클래스/개념
- Application, CarMaker, Runtime, Variation, SimControl 계열
- Python/C++ API usage

먼저 열어야 하는 경우:

- “Python으로 CarMaker를 제어하고 싶다”
- “runtime/simcontrol/variation 객체 관계가 궁금하다”
- “class reference가 필요하다”

### `IPGRoadAPI`

사용처:

- road generation/conversion API
- code samples
- 클래스 레퍼런스

먼저 열어야 하는 경우:

- “도로를 코드로 만들고 싶다”
- “IPGRoad 데이터 처리 자동화를 하고 싶다”

### `OpenSCENARIO`

사용처:

- schema 자산 확인
- import/export compatibility 판단

먼저 열어야 하는 경우:

- “OpenSCENARIO 버전/스키마 차이가 궁금하다”
- “ego/traffic용 XSD를 확인해야 한다”

## 업무별 추천 순서

### GUI 중심

1. `QuickStartGuide`
2. `UsersGuide.pdf`
3. `ReferenceManual.pdf`

### Python automation 중심

1. `Examples\Python`
2. `CMAPI`
3. `ProgrammersGuide.pdf`

### online integration 중심

1. `APO`
2. `CMAPI`
3. `IPGControl` / `Instrument Designer` docs

### road/scenario 중심

1. `QuickStartGuide -> Scenario Editor`
2. `OpenSCENARIO`
3. `IPGRoadAPI`

### validation/data request 중심

1. `RequestForm`
2. `ReferenceManual.pdf`
3. 필요 시 `UsersGuide.pdf`

## 실무 규칙

- workflow가 불명확할 때는 `QuickStartGuide`에서 시작한다.
- 정확한 key/definition이 필요하면 `ReferenceManual.pdf` 쪽으로 즉시 이동한다.
- code/API 질문은 `Examples\Python`과 `CMAPI`를 먼저 본다.
- runtime online communication은 `APO`와 companion tool 문서를 같이 본다.
