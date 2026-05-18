# 04 Road, Scenario, and IPGRoad

## 근거 위치

- Quick Start Guide Scenario Editor:
  - `C:\IPG\carmaker\win64-15.0.1\doc\QuickStartGuide\Content\Content_Quickstart-Guide\B4-Scenario-Editor`
- OpenSCENARIO schema assets:
  - `C:\IPG\carmaker\win64-15.0.1\doc\OpenSCENARIO`
- IPGRoad API docs:
  - `C:\IPG\carmaker\win64-15.0.1\doc\IPGRoadAPI`

## Scenario Editor 축

입문/GUI 레벨의 scenario authoring은 Quick Start Guide의 Scenario Editor 섹션에서 잡는다.

이 문서 축이 적합한 질문:

- “Scenario Editor로 이벤트/객체/traffic를 어떻게 구성하지?”
- “GUI 기반 시나리오 작성의 출발점이 필요하다”

규칙:

- GUI workflow 질문이면 Quick Start Guide를 먼저
- import/export/schema compatibility 질문이면 OpenSCENARIO 쪽으로 이동
- 코드 생성/변환 질문이면 IPGRoad API 또는 외부 툴 체인을 검토

## OpenSCENARIO 자산

확인된 파일:

- `OpenSCENARIO_v100_osc2cm_ego_1401.xsd`
- `OpenSCENARIO_v100_osc2cm_traffic_1401.xsd`
- `OpenSCENARIO_v110_osc2cm_ego_1401.xsd`
- `OpenSCENARIO_v110_osc2cm_traffic_1401.xsd`
- `OpenSCENARIO_v120_osc2cm_ego_1401.xsd`
- `OpenSCENARIO_v120_osc2cm_traffic_1401.xsd`
- `NValue_feature_list\..._nvalue.xsd`

해석:

- 이 설치본에서는 OpenSCENARIO가 “개념 설명서”보다 “버전별 schema asset” 성격이 강하다.
- 따라서 skill은 full tutorial보다:
  - 어떤 버전을 봐야 하는지
  - ego와 traffic schema가 분리되는지
  - nvalue feature list가 따로 있는지
  를 안내하는 방식이 맞다.

## IPGRoad API 축

문서 형식:

- Doxygen 기반 API reference

확인된 entry pages:

- `annotated.html`
- `classes.html`
- `examples.html`
- `CodeSamples-example.html`
- `ErrorCodes.html`

적합한 질문:

- “road geometry를 코드로 만들거나 수정하고 싶다”
- “IPGRoad API class/function reference가 필요하다”
- “예제 코드에서 어디서 시작할지 모르겠다”

## 추천 탐색 순서

### GUI scenario 작업

1. Quick Start Guide Scenario Editor
2. 필요 시 Users Guide
3. import/export 충돌 시 OpenSCENARIO schema 확인

### schema compatibility 작업

1. `doc\OpenSCENARIO`의 버전별 XSD 확인
2. ego / traffic 분리 여부 확인
3. NValue feature list 필요 여부 확인

### road automation 작업

1. `IPGRoadAPI\examples.html`
2. `IPGRoadAPI\CodeSamples-example.html`
3. class/function reference

## skill 설계 원칙

- road/scenario 질문은 하나의 skill에서 받아도 된다.
- 다만 답변은 반드시 세 갈래로 분리해야 한다:
  - Scenario Editor GUI
  - OpenSCENARIO schema compatibility
  - IPGRoad code/API
