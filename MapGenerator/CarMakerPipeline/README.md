# CarMaker Map + Traffic Pipeline

CarMaker용 도로 맵 생성, OpenDRIVE to RD5 변환, RD5 기반 route/vehicle TestRun 생성을 한 번에 묶은 실험용 파이프라인입니다.

## 빠른 실행

Windows에서 아래 파일을 더블클릭합니다.

```text
MapGenerator\CarMakerPipeline\carmaker_pipeline_app\run_app.bat
```

기본 실행 흐름은 다음과 같습니다.

1. Pipeline App에서 `Open RoadGen App`을 누릅니다.
2. RoadGen에서 graph node/edge를 만들고 `Generate XODR`을 실행합니다.
3. Pipeline App이 최신 RoadGen export를 자동으로 감지합니다.
4. `Convert XODR to RD5`로 CarMaker RD5 도로를 생성합니다.
5. 필요하면 `Env = City`를 선택해서 건물, roadside mesh, 신호등, 횡단보도 장식을 추가합니다.
6. `Open TrafficGen With Current Paths`로 TrafficGen을 엽니다.
7. TrafficGen에서 route, ego, traffic vehicle을 만들고 `Generate + Run 5x + IPGMovie`를 실행합니다.

## 포함된 앱

- `carmaker_pipeline_app`: RoadGen, RD5 변환, TrafficGen을 연결하는 통합 런처
- `roadGen_app`: graph 기반 SUMO/OpenDRIVE 도로 생성기
- `trafficGen_app`: RD5 lane/path 분석, route 생성, TestRun 생성, CarMaker/IPGMovie 실행기

## 필요한 외부 프로그램

- IPG CarMaker 15.x
- Python 3.9-3.13, 권장 3.11
- SUMO toolchain, RoadGen에서 net/xodr 생성에 사용
- CarMaker 프로젝트 폴더, 예: `C:\CM_Projects\MapGen_TEST`

CarMaker CMAPI runner는 Python 3.14를 지원하지 않습니다. `run_app.bat`은 먼저 `%LOCALAPPDATA%\Programs\Python\Python311\python.exe`를 찾고, 없으면 기본 `python`으로 실행합니다.

## Git에 포함하지 않는 생성물

아래 항목들은 실행 중 생성되거나 PC별 경로를 포함하므로 commit하지 않습니다.

- `roadGen_app/exports/`
- `trafficGen_app/exports/`
- `roadGen_app/.ipgroad_cache/`
- `trafficGen_app/.cmapi_runtime/`
- `carmaker_pipeline_app/settings.json`
- `__pycache__/`

설정 예시는 `carmaker_pipeline_app/settings.example.json`을 참고하세요.

## 현재 구현 상태

- Road graph를 기반으로 SUMO edge/node/net과 OpenDRIVE xodr 생성
- CarMaker IPGRoad API 기반 xodr to rd5 변환
- RD5 lane path 분석과 CarMaker route writing
- Ego/traffic vehicle TestRun 생성
- Traffic vehicle 등속 또는 IPG Driver 기반 주행 선택
- lane change route 시각화와 route checkpoint planning
- City scenery 생성, 건물 density 조절, 도로와 충돌하지 않는 배치
- 시각적 신호등과 zebra-style 횡단보도 decoration
- `Generate + Run 5x + IPGMovie` 실행 흐름

동적 traffic light controller는 현재 기본 비활성화 상태입니다. CarMaker 15에서 synthetic junction metadata가 부족하면 preprocessing 단계에서 멈출 수 있어서, 지금은 visual object와 road marking 중심으로 유지합니다.
