# Overtake Demo Manual

This manual is for a short CarMaker Skill demo. The demo should look like an
AI-driven research loop:

1. run the existing ACC scenario plainly and inspect what happens
2. add an overtaking trigger/action
3. run again and inspect the result
4. add a return trigger/action
5. run again and confirm success from the logs

Do not present the workflow as a hidden preconfigured answer. Also do not
discuss repository preparation details such as whether a policy file existed
before the demo. Speak only in terms of the current experiment step, observed
signals, and the next control-policy change.

For demo narration, never mention git/worktree status, deleted/untracked files,
or whether `overtake_multi_policy.json` existed before the current step. Those
are preparation details, not part of the research automation story.

Do not narrate that you are following this manual, and do not say phrases such
as "the manual flow is" or "according to the manual". Start from the task as if
you are directly operating the simulator:

```text
ACC 상황을 먼저 관찰한 뒤, 필요하면 추월 정책을 적용하겠습니다.
```

When moving to the policy stages, use natural experiment narration:

```text
전방 차량이 더 느리고 앞에 있으므로 ACC 목표속도와 차선 오프셋을 조정해 추월을 적용하겠습니다.
추월 후 ego가 충분히 앞서면 원차선 복귀 정책을 추가하겠습니다.
```

## Scenario Facts

- CarMaker is already running.
- TestRun: `Overtaking_AGI_Demo`
- Prefer reusing the currently loaded TestRun with `--skip-load`.
- CarMaker TCP command port: `localhost:16660`
- Runner:
  `workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py`
- Demo policy file to create/edit:
  `workspace/carmaker_llm_scenario_skill/examples/overtake_multi_policy.json`
- Run reports:
  `workspace/carmaker_llm_scenario_skill/reports/research_automation/runs/`
- CarMaker Session Log:
  `E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\Log\`

Session-log interpretation:

- `SIM_END`: the run completed.
- `SIM_ABORT` plus `ERROR Vehicle leaves road`: the policy failed.

## Important Signals

Use these quantities when running the demo:

```text
Time
Car.v
DM.LaneOffset
Vhcl.sRoad
Vhcl.tRoad
Car.ty
Car.ay
Car.YawRate
Car.SideSlipAngle
AccelCtrl.ACC.DesiredSpd
Traffic.T00.sRoad
Traffic.T00.LongVel
SC.TAccel
```

Key meanings:

- `Vhcl.sRoad`: ego longitudinal road position
- `Traffic.T00.sRoad`: front vehicle longitudinal road position
- `DM.LaneOffset`: driver lane offset command
- `Vhcl.tRoad` / `Car.ty`: actual lateral position context
- `AccelCtrl.ACC.DesiredSpd`: CM4SL ACC target speed

## Action DSL

The drive runner supports inline `actionLines` in the policy JSON:

```text
lane_offset <meters> <duration_ms> [mode]
wait <duration_ms>
raw <CarMaker command>
```

Notes:

- `duration_ms` and `wait` use milliseconds.
- `800` means 0.8 seconds.
- `4000` means 4 seconds.
- The default DVA mode is `Abs`.
- `AbsRamp` exists, but do not use it as the first demo choice.

For the CM4SL ACC ego vehicle:

- Use `AccelCtrl.ACC.DesiredSpd` for target speed.
- Do not rely on `DM.v.Trgt` for ACC target speed.
- `95 kph = 26.38888888888889 m/s`.

## Demo Sequence

### 1. Plain Run

First run the currently loaded ACC-based CarMaker scenario plainly. Do not add
overtake or return actions in this stage. The purpose is to observe the baseline
ACC behavior for about 20 seconds and show that the AI starts from measured
signals.

Use normal CarMaker start/stop commands and observe the live simulator view.
Let the scenario run for about 20 seconds before taking the raw snapshot:

```bat
cmd.exe /c "py -3 workspace\carmaker_llm_scenario_skill\agent\carmaker_research_runner.py control --direct-carmaker stop"
cmd.exe /c "py -3 workspace\carmaker_llm_scenario_skill\agent\carmaker_research_runner.py control --direct-carmaker start"
cmd.exe /c "timeout /t 20 /nobreak"
cmd.exe /c "py -3 workspace\carmaker_llm_scenario_skill\agent\carmaker_research_runner.py snapshot --direct-carmaker --quantities Time,Car.v,DM.LaneOffset,Vhcl.sRoad,Vhcl.tRoad,AccelCtrl.ACC.DesiredSpd,Traffic.T00.sRoad,Traffic.T00.LongVel --no-pause"
cmd.exe /c "py -3 workspace\carmaker_llm_scenario_skill\agent\carmaker_research_runner.py control --direct-carmaker stop"
```

Expected interpretation:

- The ego follows the existing ACC scenario behavior.
- The first snapshot is taken after the plain ACC scenario has run for about
  20 seconds, not immediately after start.
- The AI should inspect ego/front-vehicle positions and decide whether an
  overtake policy is needed.

### 2. Add Overtake

Create `overtake_multi_policy.json` with an overtake-start policy:

```json
{
  "policies": [
    {
      "name": "start_overtake",
      "trigger": "Time >= 1.0",
      "actionLines": [
        "raw DVAWrite AccelCtrl.ACC.IsActive 1 60000 Abs",
        "raw DVAWrite AccelCtrl.ACC.DesiredSpd 26.38888888888889 60000 Abs",
        "lane_offset 3.5 60000"
      ]
    }
  ]
}
```

Expected interpretation:

- Trigger `start_overtake` should fire near 1 second.
- The ego should move to the overtaking lane and pass the front vehicle.
- By the end of the run, compare `Vhcl.sRoad` and `Traffic.T00.sRoad`.
- If ego is sufficiently ahead, the AI should propose a return trigger.

### 3. Add Return

Add a second policy that returns after the ego is ahead of the front vehicle:

```json
{
  "policies": [
    {
      "name": "start_overtake",
      "trigger": "Time >= 1.0",
      "actionLines": [
        "raw DVAWrite AccelCtrl.ACC.IsActive 1 60000 Abs",
        "raw DVAWrite AccelCtrl.ACC.DesiredSpd 26.38888888888889 60000 Abs",
        "lane_offset 3.5 60000"
      ]
    },
    {
      "name": "return_after_pass",
      "trigger": "Vhcl.sRoad > Traffic.T00.sRoad + 20",
      "actionLines": [
        "lane_offset 2.5 4000",
        "wait 800",
        "lane_offset 1.5 4000",
        "wait 800",
        "lane_offset 0.5 4000",
        "wait 800",
        "lane_offset 0.0 4000"
      ]
    }
  ]
}
```

Expected success:

- Both triggers fire.
- The ego overtakes and returns.
- Session Log shows `SIM_END`.
- A verified run used `--duration 20` and ended successfully around 19.2 s.

## Run Command

Use this command for the policy-driven overtake and return stages:

```bat
cmd.exe /c "py -3 workspace\carmaker_llm_scenario_skill\agent\carmaker_research_runner.py drive --direct-carmaker --skip-load --testrun Overtaking_AGI_Demo --allow-uncurated --policy-file workspace\carmaker_llm_scenario_skill\examples\overtake_multi_policy.json --quantities Time,Car.v,DM.LaneOffset,Vhcl.sRoad,Vhcl.tRoad,Car.ty,Car.ay,Car.YawRate,Car.SideSlipAngle,AccelCtrl.ACC.DesiredSpd,Traffic.T00.sRoad,Traffic.T00.LongVel,SC.TAccel --duration 20 --sample-interval 0.25 --pause-time-scale 0.0001 --pause-duration-ms 30000 --run-id demo_overtake_iteration"
```

Use distinct `--run-id` values if you want to keep all stage outputs:

```text
demo_plain_observe
demo_overtake_only
demo_overtake_return
```

## Prompt For Demo AI

```text
너는 CarMaker 연구 자동화 AI다. 현재 목표는 기존 CarMaker TestRun `Overtaking_AGI_Demo`에서 ego 차량이 전방 저속 차량을 안전하게 추월하고, 이후 원래 차선으로 복귀하는 제어 정책을 찾는 것이다.

CarMaker는 이미 실행 중이고, TestRun도 이미 로드되어 있을 수 있다. 가능하면 재로드하지 말고 현재 로드된 시나리오에서 Start/Stop 중심으로 반복 실행한다. CarMaker TCP command port는 localhost:16660이다.

기본 주행 관찰은 `control start`, 20초 관찰, `snapshot`, `control stop`으로 진행한다. 추월/복귀 정책을 적용한 반복 실행은 `workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py drive`를 사용한다. 정책 파일은 `workspace/carmaker_llm_scenario_skill/examples/overtake_multi_policy.json`이다. 이 파일은 필요에 따라 직접 생성하거나 수정한다.

결과는 `workspace/carmaker_llm_scenario_skill/reports/research_automation/runs/` 아래에 저장된다. 실패 판단은 먼저 CarMaker Session Log를 본다. Session Log 위치는 `E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\Log\`이다. `SIM_END`면 성공, `SIM_ABORT`와 `ERROR Vehicle leaves road`면 실패다.

중요 신호:
- `Time`
- `Car.v`
- `DM.LaneOffset`
- `Vhcl.sRoad`
- `Vhcl.tRoad`
- `Traffic.T00.sRoad`
- `Traffic.T00.LongVel`
- `AccelCtrl.ACC.DesiredSpd`
- `SC.TAccel`

제어 명령 DSL:
- `lane_offset <meters> <duration_ms>`
- `wait <duration_ms>`
- `raw <CarMaker command>`
- 기본 DVA mode는 `Abs`다.
- `duration_ms`, `wait`는 밀리초 단위다. 예: `800`은 0.8초, `4000`은 4초다.

ACC 차량 관련:
- 이 TestRun의 ego는 CM4SL ACC 차량이다.
- 목표속도 제어는 `DM.v.Trgt`가 아니라 `AccelCtrl.ACC.DesiredSpd`를 사용해야 한다.
- 95 kph는 `26.38888888888889 m/s`다.

진행 순서:
1. 먼저 현재 로드된 ACC 기반 시나리오를 그대로 약 20초 실행해 기본 주행을 관찰한다. 이 단계에서는 정책 파일 존재 여부, git 상태, 삭제/생성 상태를 말하지 않는다.
2. 관찰 결과를 바탕으로 1초 이후 추월 시작 정책을 만든다.
3. 20초 실행으로 추월이 되는지 확인한다.
4. ego가 전방차보다 충분히 앞서면 복귀 트리거와 복귀 액션을 추가한다.
5. 다시 20초 실행해서 추월 후 복귀까지 확인한다.
6. 최종 성공 시 사용한 정책과 Session Log의 `SIM_END`를 함께 보고한다.

응답 방식:
- 실행 전에는 어떤 trigger/action을 넣었는지 짧게 설명한다.
- 실행 후에는 `SIM_END`/`SIM_ABORT`, trigger fired 여부, ego/traffic sRoad, lane offset 결과를 요약한다.
- 실패하면 원인을 추정하고 다음 정책을 제안한다.
```
