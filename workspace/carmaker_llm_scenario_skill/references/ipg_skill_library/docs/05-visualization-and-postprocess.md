# 05 Visualization and Postprocess

## 목적

CarMaker 외부의 companion tools를 언제 써야 하는지 정리한다.

## IPGControl

근거 위치:

- `C:\IPG\control\win64-3.0.15\doc\Content\Content_IPGControl`

확인된 문서 주제:

- diagrams
- data sources
- quantities
- reference quantities
- analyze cursor / analyze range
- calculated signals
- snapshot / export / print
- online connection

적합한 질문:

- “실행 결과를 다이어그램으로 보고 싶다”
- “online connection으로 quantity를 보고 싶다”
- “계산 신호를 추가하고 싶다”
- “오프라인 파일 데이터를 같이 비교하고 싶다”

한 줄 요약:

- `IPGControl`은 “신호 해석과 diagram 기반 후처리”에 가장 적합하다.

## Movie NX

근거 위치:

- `C:\IPG\movienx\win64-14.0.1\doc\MovieNX.pdf`
- `C:\IPG\movienx\win64-14.0.1\doc\PythonApi`

확인된 Python API 문서 축:

- getting started
- first script
- script types
- basic modules
- scene access
- scene annotation
- node structure
- migration guide

적합한 질문:

- “Movie NX에서 장면을 자동화하고 싶다”
- “Python으로 scene node를 만지고 싶다”
- “annotation이나 render-related scripting이 필요하다”

한 줄 요약:

- `Movie NX`는 “시각 장면 편집/렌더링/스크립팅” 도구다.

## Instrument Designer

근거 위치:

- `C:\IPG\instruments\win64-2.2.0\resources\assets\doc`
- `C:\IPG\instruments\win64-2.2.0\examples`

확인된 기능 축:

- dashboard design mode
- simulation mode
- command line
- components
- layout
- custom components

확인된 예제 자산:

- `Cockpit_HEV-Automatic.json`
- `TestBench_ESP-HIL.json`
- `custom-component\Template.js`
- gauge component 예제들

적합한 질문:

- “interactive dashboard를 만들고 싶다”
- “quantity를 보면서 일부 값을 제어하고 싶다”
- “custom component를 직접 추가하고 싶다”

한 줄 요약:

- `Instrument Designer`는 “실행 중 모니터링/조작용 대시보드”에 적합하다.

## IPGGraph

근거 위치:

- `C:\IPG\graph\win64-2.9.2\tutorial`

확인된 자산:

- `.gdl` 튜토리얼 파일
- `graphlibdemo.c`
- plotting data 예제

적합한 질문:

- “GDL 예제를 기반으로 플롯 정의를 이해하고 싶다”
- “graph 튜토리얼 자산을 빠르게 훑고 싶다”

한 줄 요약:

- `IPGGraph`는 deep product workflow보다 “tutorial/reference plotting 자산”에 가깝다.

## 도구 선택 규칙

- quantity 분석, cursor, export, diagram
  - `IPGControl`
- 3D 장면/렌더링/Python scene scripting
  - `Movie NX`
- dashboard UI, control widget, HIL/DIL operator panel
  - `Instrument Designer`
- 튜토리얼성 plotting asset, GDL reference
  - `IPGGraph`
