# TGT-002 AEB Bus Stop Pedestrian Crossing Iteration Log

Created: 2026-05-12

Reference:

```text
E:\CarMakerProject\AGI\Data\TestRun\AEB_BusStop_collisiion_for_LLM
```

## Reference Baseline

Extracted summary:

```text
workspace/carmaker_llm_scenario_skill/reports/TGT-002_aeb_bus_stop_pedestrian/reference_summary.md
workspace/carmaker_llm_scenario_skill/reports/TGT-002_aeb_bus_stop_pedestrian/reference_summary.json
```

Reference traits:

```text
Road.FName = Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5
Vehicle.Routing.Type = Route
Vehicle.Routing.ObjId = 4238
DrivMan.nMan = 1
Traffic.N = 101
Traffic.0.Name = cross_ob
Traffic.0.Template.FName = 2_People/Pedestrian_Male_Casual_01_IPG
Traffic.0.Routing.Type = Route
Traffic.0.StartPos.Type = Route
Traffic.0.StartPos = 140.00 -4
Traffic.0.Man.Start.StartCond = Traffic.cross_ob.sRoad-Vhcl.sRoad<24.5
Traffic.0.Man.0.LongStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LatStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LatStep.0.Pos.Type = RelativeRoute
```

The full reference is a large native scenario with 101 traffic objects. For
generator iteration, the first acceptance slice is the core behavior:

- ego approaches a stopped/slow occluding vehicle
- a pedestrian starts near the occluder
- the pedestrian has a triggered `FollowTraj` crossing maneuver
- generated TestRun starts in CarMaker

## v0

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v0.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v0.xodr
```

Converted TestRun:

```text
workspace/carmaker_llm_scenario_skill/conversion_scratch/AGI_LLM_TestProject/Data/TestRun/TGT002_aeb_bus_stop_core_v0
```

Result:

- `osc2cm` conversion succeeded
- ego path converted to CarMaker `Path` / `FollowTraj`
- pedestrian converted to traffic object with `Routing.Type = Path`
- pedestrian has both `LongStep` and `LatStep` `FollowTraj`
- pedestrian start condition converted to a `DistToObj` trigger
- core crossing structural check passed

Gap found:

```text
Traffic.1.Man.0.LatStep.0.Limit = t {}
Traffic.1.Man.0.LongStep.0.Limit = t {}
```

This is a common converter/postprocess gap, not a TGT-002-specific patch.

## v0p1

Postprocess command:

```bash
python3 workspace/carmaker_llm_scenario_skill/scripts/postprocess_testrun.py \
  workspace/carmaker_llm_scenario_skill/conversion_scratch/AGI_LLM_TestProject/Data/TestRun/TGT002_aeb_bus_stop_core_v0 \
  --out workspace/carmaker_llm_scenario_skill/postprocessed/TGT-002_aeb_bus_stop_pedestrian/TGT002_aeb_bus_stop_core_v0p1 \
  --report workspace/carmaker_llm_scenario_skill/reports/TGT-002_aeb_bus_stop_pedestrian/v0p1/postprocess_report.txt
```

Postprocess result:

```text
Traffic.1.Man.0.LatStep.0.Limit: t {} -> t 4.500
Traffic.1.Man.0.LongStep.0.Limit: t {} -> t 4.500
```

Core check:

```text
workspace/carmaker_llm_scenario_skill/reports/TGT-002_aeb_bus_stop_pedestrian/v0p1/core_check.md
Overall: PASS
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT002_aeb_bus_stop_core_v0p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt002_aeb_bus_stop_core_v0.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v0_Bus
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v0_cross_ob
```

## Next Checks

Runtime result:

```text
LLM_Generated/TGT002_aeb_bus_stop_core_v0p1 starts successfully.
Pedestrian moves, but the path looks confusing because the converted global trajectory goes y=-3 -> -5 -> -2 -> 3.
```

Root cause:

```text
The source trajectory mixed lane ids and offsets. The converter produced a valid path, but the first segment moved away from the road before crossing back.
```

## v1p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v1.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v1.xodr
```

Changes:

- changed pedestrian start and trajectory vertices to explicit global positions
- made the pedestrian path monotonic lateral crossing: `y=-5 -> -2 -> 1 -> 5`
- fixed the heading to 90 degrees for the crossing direction
- kept the common empty FollowTraj limit postprocess

Postprocess result:

```text
Traffic.1.Man.0.LatStep.0.Limit: t {} -> t 5.000
Traffic.1.Man.0.LongStep.0.Limit: t {} -> t 5.000
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT002_aeb_bus_stop_core_v1p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt002_aeb_bus_stop_core_v1.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v1_Bus
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v1_cross_ob
```

Runtime result:

```text
LLM_Generated/TGT002_aeb_bus_stop_core_v1p1 starts, but the pedestrian stays still.
Ego stops for the static pedestrian before the distance trigger can activate the pedestrian maneuver.
```

Root cause:

```text
The pedestrian maneuver start condition still depended on ego/pedestrian relative distance.
Because AEB reacts to the static pedestrian first, ego does not close the distance enough to fire the trigger.
```

## v2p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v2.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v2.xodr
```

Changes:

- changed pedestrian trigger from relative-distance to `SimulationTime > 0.5`
- moved pedestrian start farther outward: `y=-7`
- kept monotonic crossing path: `y=-7 -> -4 -> -1 -> 3`
- kept common empty FollowTraj limit postprocess

Converted trigger:

```text
Traffic.1.Man.0.StartCond = rise(Time > 0.500)
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT002_aeb_bus_stop_core_v2p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt002_aeb_bus_stop_core_v2.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v2_Bus
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v2_cross_ob
```

Open issue:

```text
The scenario layout still has an ordering problem. Ego sees the pedestrian before or without the bus acting as a useful occluder.
For a bus-stop AEB scenario, avoid ego -> pedestrian -> bus ordering.
The bus/occluder should be between ego and the pedestrian emergence point, or close enough to hide the pedestrian initially.
```

Generation rule:

```text
For occlusion-based pedestrian scenarios, validate actor ordering as part of IR checks:
ego approach -> occluder/parked bus -> pedestrian emergence/crossing path.
If the pedestrian is exposed at init, ego may brake before the intended pedestrian trigger and the scenario semantics change.
```

## v3p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v3.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v3.xodr
```

Source changes:

- move the bus into the ego lane near the crossing zone so it functions as an occluder
- move the pedestrian farther outward and slightly ahead of the bus
- keep time-based trigger for this core movement test

Converted layout:

```text
Vehicle.StartPos = 10.000 0.000
Traffic.0.Name = T00
Traffic.0.StartPos = 78.000 0.000
Traffic.1.Name = T01
Traffic.1.StartPos = 84.000 -7.000 0.000
Traffic.1.Man.0.StartCond = rise(Time > 0.500)
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT002_aeb_bus_stop_core_v3p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt002_aeb_bus_stop_core_v3.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v3_Bus
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v3_cross_ob
```

Note:

```text
The current core checker marks the time-based trigger as FAIL because it expects a distance trigger.
For v3p1 this is intentional: time trigger is used to validate movement and occlusion layout before restoring a physically meaningful trigger.
```

Runtime/visual result:

```text
The pedestrian is now behind the bus, but the bus is in ego's lane.
Converted TestRun confirms both ego and bus use StartPos.ObjId = 31.
```

Root cause:

```text
The generated source placed the bus at OpenDRIVE laneId=-1.
In the current straight RHT road, lane -1 is the ego travel lane.
For the bus-stop occlusion case the bus should be in lane -2 or a bus-bay/curb lane.
```

## v4p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v4.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v4.xodr
```

Source changes:

- keep ego in `laneId=-1`
- move bus to `laneId=-2`
- keep bus longitudinally before the pedestrian emergence point
- keep pedestrian on the outside/far side of the bus

Converted layout:

```text
Vehicle.StartPos = 10.000 0.000
Vehicle.StartPos.ObjId = 31
Traffic.0.Name = T00
Traffic.0.StartPos = 78.000 0.000
Traffic.0.StartPos.ObjId = 41
Traffic.1.Name = T01
Traffic.1.StartPos = 84.000 -7.000 0.000
Traffic.1.Man.0.StartCond = rise(Time > 0.500)
```

Interpretation:

```text
Ego and bus now use different lane objects.
Ego is in lane -1 / ObjId 31.
Bus is in lane -2 / ObjId 41.
Pedestrian starts outside/far side of the bus and walks across at x=84.
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT002_aeb_bus_stop_core_v4p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt002_aeb_bus_stop_core_v4.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v4_Bus
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v4_cross_ob
```

## Next Checks

1. Runtime-start `LLM_Generated/TGT002_aeb_bus_stop_core_v4p1` in CarMaker.
3. Visually confirm the pedestrian crosses in a clean straight line and the bus acts as an occluder.
4. If timing is poor, tune `SimulationTimeCondition`, trajectory timing, and ego approach speed in the source `.xosc`.
5. After the core slice passes, decide whether TGT-002 should grow toward the full 101-object reference or remain a focused AEB crossing target.

Runtime/visual result:

```text
The pedestrian crosses much too early and then disappears.
```

Root causes / hypotheses:

```text
The source trigger is SimulationTime > 0.5, so the pedestrian starts independent of ego approach timing.
The converted pedestrian FollowTraj ends at 5.0 s after trigger; if the maneuver ends inside the scenario window, the actor may stop displaying instead of remaining visible.
```

## v5p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v5.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v5.xodr
```

Source changes:

- changed pedestrian start trigger from `SimulationTime > 0.5` to `SimulationTime > 2.0`
- slowed crossing vertices to `0, 2, 4, 6 s`
- added a final hold vertex at `12 s` at the completed crossing position
- kept ego/bus lane separation from v4

Converted/postprocessed checks:

```text
Traffic.1.Man.0.StartCond = rise(Time > 2.000)
Traffic.1.Man.0.LatStep.0.Data final row = 84.000 3.000 0.000 90.000 12.000
Traffic.1.Man.0.LatStep.0.Limit = t 12.000
Traffic.1.Man.0.LongStep.0.Limit = t 12.000
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT002_aeb_bus_stop_core_v5p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt002_aeb_bus_stop_core_v5.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v5_Bus
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT002_aeb_bus_stop_core_v5_cross_ob
```

Next runtime check:

```text
Run LLM_Generated/TGT002_aeb_bus_stop_core_v5p1.
Confirm whether the delayed trigger aligns crossing with ego approach and whether the final hold vertex prevents disappearance.
```

Runtime/visual result:

```text
User confirmed TGT002_aeb_bus_stop_core_v5p1 succeeds in CarMaker.
The delayed trigger and final hold vertex are accepted as the current generation pattern.
```
