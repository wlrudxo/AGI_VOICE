# CarMaker Map/Traffic Pipeline 정리

이 문서는 `MapGenerator/CarMakerPipeline`에 추가된 CarMaker 맵/트래픽 생성 파이프라인의 사용 목적과 현재 구조를 정리합니다.

## 목표

LLM 또는 Codex와 대화하면서 도로 graph를 만들고, 이를 CarMaker에서 실행 가능한 RD5/TestRun 시나리오로 변환하는 도구 체인을 만드는 것이 목표입니다.

현재 파이프라인은 다음 문제를 해결합니다.

- 사람이 graph 형태로 도로 node/edge를 구성
- 기본 양방향 도로와 lane/speed 설정
- SUMO net과 OpenDRIVE xodr 생성
- CarMaker 15의 IPGRoad API를 통한 RD5 변환
- RD5 내부 LanePath를 분석해서 route 작성
- Ego car와 traffic car를 다른 route로 배치
- lane change와 checkpoint 기반 route planning
- city scenery, 건물, roadside mesh, 시각적 신호등, 횡단보도 생성
- CarMaker GUI와 IPGMovie를 실행하고 5x로 시뮬레이션 실행

## 사람이 해야 하는 단계

- CarMaker와 SUMO 설치
- CarMaker 프로젝트 폴더 준비
- 필요한 경우 CarMaker GUI에서 RD5/xodr import 결과 확인
- RoadGen에서 graph를 설계
- TrafficGen에서 route와 vehicle plan을 선택

## 앱이 자동화하는 단계

- RoadGen export 탐색
- xodr 파일 선택과 RD5 출력 경로 설정
- xodr to rd5 변환
- RD5 decoration 적용
- RD5 LanePath mapping
- route와 TestRun 파일 생성
- CarMaker/IPGMovie 실행

## 대표 실행 파일

```text
MapGenerator\CarMakerPipeline\carmaker_pipeline_app\run_app.bat
```

이 파일을 기준으로 실행하면 됩니다.

## 주의 사항

- `settings.json`은 사용자 PC 경로를 포함하므로 Git에 포함하지 않습니다.
- `exports/` 폴더는 생성물이므로 Git에 포함하지 않습니다.
- Python 3.14는 CarMaker 15.0.1 CMAPI wheel과 맞지 않습니다. Python 3.11 사용을 권장합니다.
- 동적 traffic light controller는 현재 기본 비활성화입니다. 시각적 신호등/횡단보도 생성은 지원하지만, 신호 인식/정지 동작은 CarMaker junction/controller metadata가 더 안정화된 뒤 다시 켜는 방향이 안전합니다.

## 향후 작업 후보

- CarMaker traffic light controller를 안전하게 생성하는 junction metadata 보강
- 횡단보도 road marking의 CarMaker material/shape 추가 개선
- 보행자 route와 보행자 신호 연동
- LLM prompt를 통한 graph 생성과 route plan 자동 생성
- CarMaker project template 자동 생성
