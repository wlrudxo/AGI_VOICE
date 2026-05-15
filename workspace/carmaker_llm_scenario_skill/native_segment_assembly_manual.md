# Native Segment Assembly Manual

Created: 2026-05-12

## Purpose

This manual defines the current recommended workflow for LLM-based automatic CarMaker scenario generation on verified native maps.

The target is not free-form road geometry generation. The target is executable CarMaker scenario generation by assembling known-good native segments:

- verified `.rd5` map and road-control assets,
- route/path IDs,
- actor blocks,
- maneuver blocks,
- timing and conflict parameters.

This is the primary path for scenarios with surrounding vehicles, pedestrians, crosswalks, traffic lights, and route-based interactions.

## Why This Replaced The Previous Primary Method

The earlier direct OpenDRIVE/OpenSCENARIO path remains useful, but it is no longer the primary path for complex CarMaker-native scenes.

Observed problems:

- `AssignRouteAction` is standard OpenSCENARIO but is rejected by CarMaker 15 `osc2cm` supported-feature validation in maneuver contexts.
- Lane-only routing can make junction direction non-deterministic or different from the intended route.
- Timed `FollowTrajectoryAction` through junctions can trigger CarMaker velocity-polynomial sign-change errors.
- Path-only `FollowTrajectoryAction` plus a separate speed action can show the intended speed in the maneuver UI but not produce the intended actual speed.
- Traffic lights, crosswalks, and route behavior are native `.rd5` road/control assets, so generated XML alone is not enough for reliable CarMaker behavior.

Therefore, for complex scenes:

```text
LLM intent
  -> choose native map segment
  -> choose route/path/control segments
  -> choose verified actor/maneuver blocks
  -> bind parameters
  -> emit CarMaker TestRun
  -> user validates in CarMaker
```

## Current Implementation

Generator:

```text
workspace/carmaker_llm_scenario_skill/scripts/generate_native_route_scenarios.py
```

Base template:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/native_route_template/TGT003_native_route_template_v1
```

Generated output:

```text
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/
```

Reports:

```text
workspace/carmaker_llm_scenario_skill/reports/native_segment_assembly/
```

UrbanRoad catalog:

```text
workspace/carmaker_llm_scenario_skill/reports/urbanroad_catalog/urbanroad_catalog.md
workspace/carmaker_llm_scenario_skill/reports/urbanroad_catalog/urbanroad_catalog.json
```

Installed CarMaker TestRuns:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_*
```

## Generation Command

Build/update the map and overlay catalog first:

```bash
python3 workspace/carmaker_llm_scenario_skill/scripts/parse_urbanroad_catalog.py
```

Generate repo-local TestRuns:

```bash
python3 workspace/carmaker_llm_scenario_skill/scripts/generate_native_route_scenarios.py
```

Generate and install into the active CarMaker project:

```bash
python3 workspace/carmaker_llm_scenario_skill/scripts/generate_native_route_scenarios.py \
  --install-project /mnt/e/CarMakerProject/AGI
```

Extract summaries:

```bash
for f in workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_*; do
  b=$(basename "$f")
  python3 workspace/carmaker_llm_scenario_skill/scripts/extract_testrun_summary.py "$f" \
    --json-out "workspace/carmaker_llm_scenario_skill/reports/native_segment_assembly/${b}_summary.json" \
    --md-out "workspace/carmaker_llm_scenario_skill/reports/native_segment_assembly/${b}_summary.md"
done
```

## Current Native Map Segment

The first cataloged map segment is:

```text
Road.FName = Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5
```

Why this map:

- It is included with CarMaker 15.0.1.
- It has existing junctions, traffic-light controls, routes, pedestrians, cyclists, vehicles, and crosswalk/urban assets.
- IPG's own AEB examples use it for route-based intersection and pedestrian scenes.

Known road assets:

```text
nJunctions = 22
nRoutes = 17
Control.TrfLight.0 = 9921 TL001 ...
Control.TrfLight.1 = 9923 TL000 ...
PedestrianCrossing2S mounted in the road asset
```

## Initial Route Catalog

These route IDs are known because they are used by IPG example TestRuns on the selected road.

| Route ID | Initial meaning | Evidence source |
| ---: | --- | --- |
| 4235 | Ego/main approach route | `AEB_CrossingCarIntersection`, `AEB_CrossingPedestrianCity` |
| 4236 | Crossing vehicle route for route 4235 | `AEB_CrossingCarIntersection` |
| 4232 | Oncoming/background vehicle route | `AEB_CrossingCarIntersection` |
| 4234 | Fast background route | AEB examples |
| 4226 | Secondary route/background vehicle route | AEB examples |
| 4227 | Truck/background route | AEB examples |
| 4228 | Pedestrian/crosswalk route candidate | `AEB_CrossingPedestrianCity` |
| 4225 | Pedestrian/static object route candidate | `AEB_CrossingPedestrianCity` |
| 4229 | Pedestrian/bus/curb-side route candidate | `AEB_CrossingPedestrianCity` |
| 4233 | Cyclist/background route | AEB examples |
| 4237 | Cyclist/conflict route candidate | AEB examples |
| 269 | Static roadside/parking-side placement route | AEB examples |

The first proven conflict pair is:

```text
ego route: 4235
crossing route: 4236
```

IPG's `Intersection.tcl` uses the following logic:

```tcl
set Speed_vut [expr [NamedValue get Speed_vut]/3.6]
set Speed_TO [expr [NamedValue get Speed_TO]/3.6]
set time2intersection [expr (164/$Speed_vut)]
NamedValue set Position_TO [expr 173-($time2intersection*$Speed_TO)]
```

For generated cases, the current generator writes direct numeric start/speed values instead of relying on named values.

## Actor Segment Catalog

The generator copies verified `Traffic.*` blocks from the native route-template base and renumbers them. As of the catalog-gated version, default generation must use `generation_library` entries from:

```text
workspace/carmaker_llm_scenario_skill/reports/urbanroad_catalog/urbanroad_catalog.json
```

Required tags for default generated actors:

```text
visible
validated
```

Collision-risk scenarios must include at least one actor tagged:

```text
conflict
```

Important CarMaker syntax rule:

```text
Traffic.*.Name must be unique and 8 characters or shorter.
```

| Source actor | Native role | Current use |
| ---: | --- | --- |
| `Traffic.0` | blue VW Beetle crossing vehicle on route 4236 | primary crossing target |
| `Traffic.1` | oncoming Mitsubishi Outlander | oncoming/background vehicle |
| `Traffic.2` | fast background S-Class | cataloged example only, not default-generated until visible validation |
| `Traffic.6` | Lexus NX background vehicle | cataloged example only, not default-generated until visible validation |
| `Traffic.7` | truck route segment | cataloged example only, not default-generated until visible validation |
| `Traffic.8` | pedestrian route 4228 with `FollowTraj` + `RoutingChange` | failed visibility in current ego segment |
| `Traffic.9` | pedestrian route 4225 with `y`/`y_abs` movement | failed visibility in current ego segment |
| `Traffic.10` | pedestrian route 4229 with repeated `FollowTraj`/`RoutingChange` | failed visibility in current ego segment |
| `Traffic.12` | cyclist route segment | failed visibility in current ego segment |
| `Traffic.16` | static bus | failed visibility in current ego segment |
| `Traffic.30` | static roadside car | cataloged example only, not default-generated until visible validation |
| `Traffic.31` | static roadside car | cataloged example only, not default-generated until visible validation |

Important rule:

```text
If a copied pedestrian block contains Pos.Reference = <old actor name>,
the generator must update it to the new actor name.
```

This is implemented in `generate_native_route_scenarios.py`.

## Scenario Recipe Rules

A scenario recipe contains:

```text
name
title
intent
ego_route_id
ego_start
ego_speed_kmh
end_sroad
actor specs
```

An actor spec contains:

```text
source_index
name
catalog_key
start_pos
speed_kmh
route_id override, optional
template override, optional
info text, optional
dyn override, optional
n_man override, optional
```

The generator performs these transformations:

1. Extract the base TestRun prelude before `Traffic.0`.
2. Extract each source `Traffic.<n>` block from the base template.
3. Patch ego route, start position, speed, and end condition.
4. Copy selected source actor blocks.
5. Renumber them sequentially from `Traffic.0`.
6. Patch actor names, self-references, start positions, route IDs, speeds, and dynamics.
7. Patch `Traffic.N`.
8. Write a TestRun file and manifest.

## Generated Scenario Batch

The first exploratory batch contained 10 installed scenarios. User validation found several useful failure modes; these are now recorded in `reports/urbanroad_catalog/urbanroad_catalog.md`.

| Scenario | Purpose | Installed TestRun |
| --- | --- | --- |
| `CMASM_001_crossing_beetle_normal` | baseline route 4235 vs 4236 crossing vehicle | `LLM_Generated/CMASM_001_crossing_beetle_normal` |
| `CMASM_002_fast_crossing_vehicle` | faster crossing vehicle and higher ego speed | `LLM_Generated/CMASM_002_fast_crossing_vehicle` |
| `CMASM_003_slow_heavy_crossing` | truck reassigned to crossing route | `LLM_Generated/CMASM_003_slow_heavy_crossing` |
| `CMASM_004_crossing_with_oncoming` | crossing target plus oncoming/background vehicle | `LLM_Generated/CMASM_004_crossing_with_oncoming` |
| `CMASM_005_bus_occluded_pedestrian` | static bus plus moving pedestrian | `LLM_Generated/CMASM_005_bus_occluded_pedestrian` |
| `CMASM_006_multi_pedestrian_crosswalk` | three pedestrian motion segments | `LLM_Generated/CMASM_006_multi_pedestrian_crosswalk` |
| `CMASM_007_cyclist_and_crossing_car` | crossing target plus cyclist | `LLM_Generated/CMASM_007_cyclist_and_crossing_car` |
| `CMASM_008_dense_urban_background` | crossing target with multiple moving vehicles | `LLM_Generated/CMASM_008_dense_urban_background` |
| `CMASM_009_late_near_miss_crossing` | higher ego speed and late crossing timing | `LLM_Generated/CMASM_009_late_near_miss_crossing` |
| `CMASM_010_static_clutter_pedestrian` | static bus/cars plus moving pedestrian | `LLM_Generated/CMASM_010_static_clutter_pedestrian` |

Current structural check:

```text
All 10 generated TestRuns have matching Traffic.N declared/found counts.
All 10 use Road.FName = Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5.
All 10 use Vehicle.Routing.ObjId = 4235.
No generated scenario contains leftover $Speed_* or $Position_* named-value placeholders.
Pedestrian Pos.Reference fields are rewritten to match generated actor names.
```

Manual CarMaker validation is still required for runtime behavior and visual semantics.

The current catalog-gated default generator intentionally emits only scenarios whose actor placements are tagged `visible` and `validated` in the catalog:

```text
CMASM_001_crossing_beetle_normal
CMASM_002_fast_crossing_vehicle
CMASM_004_crossing_with_oncoming
```

Pedestrian generation is not removed, but it is blocked from the car-intersection template until the `AEB_CrossingPedestrianCity` actor block is imported as a separate source block.

## Extension Workflow

To add a new scenario:

1. Pick the closest existing scenario recipe.
2. Choose route IDs only from the catalog unless a new route has been manually validated.
3. Choose actor blocks only from the actor segment catalog unless a new block has been manually validated.
4. Avoid inventing new pedestrian `FollowTraj` blocks by hand; copy an existing block and adjust only route/start/speed/name first.
5. Generate repo-local TestRuns.
6. Extract summaries and check:

```text
Traffic.N declared == traffic_count_found
Road.FName is a known road
Vehicle.Routing.ObjId is known
each actor has expected route/start/maneuver
no stale self-reference remains
```

7. Install into the CarMaker project.
8. Run in CarMaker and record:

```text
starts / aborts
ego route behavior
actor visibility
actor movement
collision/near-miss semantics
unexpected traffic-light or route behavior
```

## Known Limitations

- The route catalog now includes route, LanePath, RL-index, junction, traffic-light, right-of-way, example actor, and user-feedback overlays. It is still not a substitute for visual CarMaker validation.
- Generated scenarios can look new through actors, speeds, TTC, and clutter, but they are still on one native map.
- The generator does not yet compute exact TTC from route geometry. It currently binds start positions and speeds from recipes.
- Some actors copied from the full IPG example start far from the selected ego camera/route segment. They are blocked unless they receive a `visible` validation tag.
- Signal-light phase control is not yet parameterized.
- Runtime validation is intentionally left to the user for this batch, but generator input validation now prevents known-bad unvalidated placements from being emitted by default.

## Next Improvements

1. Add route-pair conflict catalog with approximate conflict `s` values.
2. Add TTC calculator for route 4235 vs 4236.
3. Add a slim visual-test mode with only ego plus one or two actors.
4. Import the `AEB_CrossingPedestrianCity` pedestrian `cross_ob` actor block as a second source template.
5. Add user feedback fields to the manifest after each CarMaker run.
