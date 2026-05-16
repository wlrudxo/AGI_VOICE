# Pipeline App

`run_app.bat`을 실행하면 RoadGen, xodr to rd5 변환, TrafficGen 실행을 연결하는 Tkinter 앱이 열립니다.

이 앱은 repo 안의 sibling 폴더를 기준으로 동작합니다.

```text
CarMakerPipeline/
  carmaker_pipeline_app/
  roadGen_app/
  trafficGen_app/
```

`settings.json`은 앱 종료 시 자동 생성되는 사용자 로컬 설정입니다. Git에는 올리지 않고, 새 PC에서는 앱을 한 번 실행하거나 `settings.example.json`을 복사해서 시작하면 됩니다.
