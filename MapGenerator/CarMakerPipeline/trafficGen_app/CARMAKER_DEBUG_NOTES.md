# CarMaker Debug Notes

이 문서는 RoadGen/TrafficGen 앱에서 만든 RD5/TestRun을 CarMaker 15.0.1에서 실행할 때
발생했던 문제와 원인을 기록한다.

## 2026-05-15: 신호등/횡단보도, ego 정지, InfoFile 오류

### 증상

- RoadGen에서 `traffic_light_crosswalk` 또는 `crosswalk` node를 설정해도 IPGMovie에서 횡단보도가 보이지 않았다.
- 신호등은 보이지만 ego car가 신호등에서 멈추지 않았다.
- 이후 `Vehicle.DriverTemplate.FName = TestRun`으로 바꿨더니 ego car가 움직이지 않았다.
- 다시 수정하는 과정에서 IPGMovie/roadutil이 다음 오류를 냈다.

```text
File 'C:/CM_Projects/MapGen_TEST/Data/TestRun/route_traffic' seems not to be a correct Info File
ERROR: Invalid route
Please recheck your data(route:0, usepath:1, bumps:0, dynamic path:)
```

### 원인 1: route 전용 RD5에 교차로 장식 블록이 빠짐

RoadGen의 `Copy To CarMaker` 단계에서는 RD5에 다음 장식 블록을 추가한다.

```text
# RoadGen Intersection Decorations BEGIN
...
Control.TrfLight...
RL.<id>.Marker.<id>.Type = DrvStop
RL.<id>.RoadMarking...
...
# RoadGen Intersection Decorations END
```

하지만 TrafficGen에서 route를 추가한 RD5 copy를 만들 때, 초기 구현은 route/ConPath만 추가하고
RoadGen의 교차로 장식 블록을 다시 동기화하지 않았다. 그래서 실행에 실제로 쓰이는
`*_E18_rev_to_E10.rd5` 같은 route 전용 RD5에는 신호등 정지 마커와 횡단보도 마킹이 없을 수 있었다.

수정:

- TrafficGen이 route 전용 RD5를 쓸 때 `roadGen_app/rd5_environment.py`의
  `decorate_rd5_intersections()`를 다시 호출하도록 했다.
- 현재 route RD5에도 `RoadGen Intersection Decorations` 블록이 들어가는지 확인해야 한다.

확인 명령:

```powershell
rg -n "RoadGen Intersection Decorations|Control\.TrfLight|DrvStop|RoadMarking\..*PointList" `
  "C:\CM_Projects\MapGen_TEST\Data\Road\<route_rd5>.rd5"
```

### 원인 2: CarMaker 예제의 `TestRun` DriverTemplate을 그대로 쓰면 안 됨

CarMaker 예제 `AEB_CrossingCatCity`는 다음처럼 되어 있다.

```text
Vehicle.DriverTemplate.FName = TestRun
Driver.Consider.TrfLight = 1
DrivMan.Man.0.LongStep.0.Dyn = Driver ...
DrivMan.Man.0.LatStep.0.Dyn = Driver 0
```

그래서 처음에는 ego가 신호등을 인식하려면 `DriverTemplate = TestRun`이 필요하다고 추정했다.
하지만 현재 프로젝트/설치 경로의 driver template 목록에는 `TestRun` 파일이 없고
`Car_Normal`, `Car_Defensive`, `Car_Aggressive` 계열만 있었다.

이 상태에서 `Vehicle.DriverTemplate.FName = TestRun`을 넣으면 ego driver 초기화가 불안정해지고,
ego car가 움직이지 않는 문제가 생겼다.

수정:

- ego 기본값은 다시 `Vehicle.DriverTemplate.FName = Car_Normal`로 돌렸다.
- 신호등 인식은 다음 조합으로 유지한다.

```text
Vehicle.DriverTemplate.FName = Car_Normal
Driver.Consider.TrfLight = 1
DrivMan.VhclOperator.Kind = IPGOperator 1
DrivMan.Man.0.LongStep.0.Dyn = Driver 1 0 <speed>
DrivMan.Man.0.LatStep.0.Dyn = Driver 0
```

### 원인 3: PowerShell `Set-Content -Encoding UTF8`이 BOM을 붙임

수동으로 현재 CarMaker 프로젝트의 TestRun 파일을 고치면서 Windows PowerShell 5.1의
`Set-Content -Encoding UTF8`을 사용했다. 이 방식은 UTF-8 BOM을 파일 맨 앞에 붙인다.

CarMaker InfoFile 파서는 파일 첫 글자가 정확히 `#INFOFILE...`이어야 하는데, BOM이 있으면
실제 첫 byte가 `EF-BB-BF`가 된다. 그래서 CarMaker가 다음 오류를 냈다.

```text
File ... seems not to be a correct Info File
```

정상 파일 시작:

```text
23-49-4E  # "#IN"
```

문제가 생긴 파일 시작:

```text
EF-BB-BF-23-49-4E  # BOM + "#IN"
```

수정:

```powershell
$enc = New-Object System.Text.UTF8Encoding($false)
$text = [System.IO.File]::ReadAllText($path)
[System.IO.File]::WriteAllText($path, $text, $enc)
```

앱의 Python `Path.write_text(..., encoding="utf-8")`는 기본적으로 BOM 없는 UTF-8로 저장하므로
앱에서 생성한 파일은 이 문제를 만들지 않는다. 수동 수정 시에만 주의하면 된다.

확인 명령:

```powershell
$p = "C:\CM_Projects\MapGen_TEST\Data\TestRun\route_traffic"
[System.BitConverter]::ToString([System.IO.File]::ReadAllBytes($p)[0..2])
```

정상 출력:

```text
23-49-4E
```

### 원인 4: `Invalid route`는 InfoFile 파싱 실패의 후속 오류일 가능성이 큼

`route_traffic`이 BOM 때문에 TestRun으로 제대로 읽히지 않으면, IPGMovie/roadutil 단계에서
route 정보도 정상적으로 전달되지 않아 `Invalid route`가 연쇄적으로 뜰 수 있다.

RD5 자체는 별도로 `roadutil`로 검증했다.

```powershell
& "C:\IPG\carmaker\win64-15.0.1\bin\roadutil.exe" `
  -datadir "C:\CM_Projects\MapGen_TEST\Data\Road" `
  -rlen 0 `
  "C:\CM_Projects\MapGen_TEST\Data\Road\<route_rd5>.rd5"
```

참고:

- `roadutil -rlen 0`의 `0`은 RD5 내부 route index를 의미한다.
- TestRun의 `Vehicle.Routing.ObjId`는 `Route.<index>.ID` object ID를 사용한다.
- 따라서 `roadutil -rlen 4040`처럼 ObjId를 넣으면 실패할 수 있다. 이것이 곧 TestRun이 틀렸다는 뜻은 아니다.

추가 검증:

```powershell
& "C:\IPG\carmaker\win64-15.0.1\bin\roadutil.exe" `
  -datadir "C:\CM_Projects\MapGen_TEST\Data\Road" `
  -route 0 `
  -o "C:\CM_Projects\MapGen_TEST\tmp\movie.dat" `
  -movie `
  "C:\CM_Projects\MapGen_TEST\Data\Road\<route_rd5>.rd5"
```

이 명령이 성공하면 RD5 route 0 자체는 IPGMovie용 road data로 변환 가능하다는 뜻이다.

## 재발 방지 체크리스트

1. TestRun 파일 첫 3 bytes가 `23-49-4E`인지 확인한다.
2. ego가 안 움직이면 `Vehicle.DriverTemplate.FName`이 `Car_Normal`인지 먼저 본다.
3. 신호등 정지를 기대하면 TestRun에 `Driver.Consider.TrfLight = 1`이 있어야 한다.
4. 실행 RD5에 `RoadGen Intersection Decorations` 블록이 있어야 한다.
5. `DrvStop` marker가 ego route가 지나가는 LanePath에 붙어 있는지 확인한다.
6. `roadutil -rlen 0`과 `roadutil -route 0 -movie`로 RD5 route 자체를 따로 검증한다.
7. 수동으로 CarMaker InfoFile을 수정할 때는 PowerShell `Set-Content -Encoding UTF8`을 피한다.

## 현재 권장 기본값

```text
Vehicle.DriverTemplate.FName = Car_Normal
Driver.Consider.TrfLight = 1
Driver.Consider.Stop = 1
DrivMan.VhclOperator.Kind = IPGOperator 1
```

TrafficGen 앱은 route 전용 RD5 생성 후 교차로 장식을 다시 동기화해야 한다. 이 동기화가 빠지면
RoadGen에서 보이는 신호등/횡단보도 설정과 실제 CarMaker 실행 RD5가 달라진다.

## 2026-05-15: IPGMovie shows wrong/default map, then target TestRun does not move

Observed with `route_traffic_1` and `figure8_extended_E18_rev_to_E10.rd5`.

- The old runner started IPGMovie before the target TestRun was actually simulating. Movie could attach to CarMaker's initial/default idle TestRun (`route_traffic`) and show the wrong map.
- The runner now starts the target TestRun at a temporary `0.1x`, waits until `Time > 0.001`, then starts IPGMovie and switches to `5x`.
- If the target TestRun does not advance within 45 seconds, the runner starts IPGMovie for diagnosis and leaves a clear log message.

Root cause for the `Time=0` / `Preprocessing` hang:

- Generated `# RoadGen Intersection Decorations` added dynamic `Control.TrfLight` plus `DrvStop` markers.
- Removing that generated intersection block made the same TestRun simulate normally: `SIM_END route_traffic_1 50.749s 564.198m`.
- The generated dynamic stop markers are not safe enough yet for CarMaker 15 synthetic junctions.

Current fix:

- RoadGen keeps visual signal objects and crosswalk road markings.
- Dynamic `Control.TrfLight`/`DrvStop` generation is disabled by default in `roadGen_app/rd5_environment.py`.
- The dynamic signal feature should be re-enabled only after validating the full controller/marker graph against CarMaker examples.
