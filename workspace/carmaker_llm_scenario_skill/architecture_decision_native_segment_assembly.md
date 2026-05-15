# Architecture Decision: Native Segment Assembly for CarMaker Scenario Generation

Date: 2026-05-12

## Decision

Use native CarMaker segment assembly as the primary generation strategy for complex CarMaker scenarios with surrounding vehicles, pedestrians, intersections, crosswalks, and traffic lights.

Keep direct OpenDRIVE/OpenSCENARIO generation as a secondary strategy for simple roads, lane-change scenarios, regression tests, and portability experiments.

## Context

The project goal is LLM-based automatic scenario generation for CarMaker. A "scenario" means the full executable situation:

- map and road network,
- ego initial state and driving behavior,
- surrounding vehicles,
- pedestrians,
- static/occluding objects,
- actor trajectories or routes,
- triggers, timing, and conflict geometry.

Initial work used this flow:

```text
LLM intent
  -> generate OpenDRIVE + OpenSCENARIO 1.2
  -> convert with CarMaker osc2cm
  -> postprocess generated TestRun
  -> run in CarMaker
```

This worked for some simple/generated cases but became fragile for native CarMaker intersection behavior.

## Evidence From Iterations

### What Worked

TGT-001 double lane change:

- Generated OpenDRIVE/OpenSCENARIO converted to CarMaker.
- Runtime started after road-envelope and actor-placement fixes.
- Useful for validating lane positions, relative placements, lane changes, and generated road geometry.

TGT-002 AEB bus-stop pedestrian crossing:

- A compact generated scenario with ego, stopped bus/occluder, and moving pedestrian became runnable.
- A common postprocessor fixed converter output gaps.
- Final hold vertex fixed disappearing pedestrian behavior after crossing.

### What Failed Or Remained Fragile

TGT-003 signalized intersection:

- Lane-only routing let CarMaker/default behavior choose unintended junction directions.
- `AssignRouteAction` is valid OpenSCENARIO, but CarMaker 15 `osc2cm` supported-feature validation rejects it in maneuver contexts.
- Timed `FollowTrajectoryAction` for ego turning produced velocity-polynomial sign-change errors.
- Path-only `FollowTrajectoryAction` plus a separate speed action displayed target speed in the maneuver but did not reliably control actual vehicle speed during path following.
- Traffic-light and crosswalk behavior are native `.rd5` road/control assets, not just abstract OpenSCENARIO story elements.

Pedestrian behavior:

- Global generated pedestrian trajectories can convert but are sensitive to trigger timing, final hold points, and route/path support.
- Native examples anchor pedestrians to CarMaker route/path objects and use bounded route-relative `FollowTraj` or `RoutingChange`.

## Root Cause

The main issue is not XML syntax. The issue is that CarMaker's executable behavior depends heavily on native `.rd5` route/path/control assets and on the supported subset of `osc2cm`.

OpenSCENARIO can express many concepts that CarMaker 15's converter does not preserve as native runnable behavior. For intersections, route choice, traffic-light state, crosswalk placement, and actor path following are better represented by CarMaker-native route and road-control objects.

## New Primary Strategy

Use a segment library and assemble scenarios from verified pieces:

```text
user scenario intent
  -> select map segment
  -> select route/path/control segment
  -> select actor segment
  -> bind start positions, offsets, speeds, TTC, triggers
  -> emit native CarMaker TestRun
  -> run/inspect in CarMaker
```

Segment categories:

| Segment | Meaning |
| --- | --- |
| map segment | Known `.rd5` or generated road with validated geometry, junctions, signals, crosswalks |
| route/path segment | Known route IDs/path IDs and valid `s`/offset ranges |
| actor segment | Vehicle, pedestrian, cyclist, bus, static obstacle templates and defaults |
| maneuver segment | Proven native blocks such as `Driver`, `auto`, `VelTransition`, bounded `FollowTraj`, `RoutingChange` |
| timing segment | TTC/conflict formulas using route distance and actor speed |
| validation segment | Expected CarMaker runtime/visual checks |

## Recommended Division Of Labor

LLM responsibilities:

- Parse scenario intent.
- Choose appropriate verified segments.
- Bind numeric parameters.
- Generate a native TestRun or converter-backed source.
- Produce a sidecar manifest explaining selected segments and assumptions.

Generator/tooling responsibilities:

- Maintain segment catalog.
- Validate route IDs, start positions, and actor references.
- Compute timing deterministically.
- Emit native CarMaker TestRun blocks.
- Run structural checks before manual CarMaker validation.

CarMaker/manual validation responsibilities:

- Confirm route behavior, signal visibility/state, actor movement, and collision/near-miss semantics in the simulator.

## When To Use Each Strategy

Use native segment assembly for:

- intersections,
- signalized scenarios,
- pedestrian/crosswalk scenarios,
- surrounding-traffic scenes,
- occlusion scenes,
- route-based AEB/collision scenarios,
- scenarios where CarMaker runtime behavior matters more than OpenSCENARIO portability.

Use direct OpenDRIVE/OpenSCENARIO generation for:

- simple straight roads,
- lane changes,
- simple generated AEB slices,
- converter regression tests,
- examples intended to stay portable,
- cases where a new road is intentionally part of the target.

## Immediate Test Plan

Reset TGT-003 as a native route-template smoke test:

- base road: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`
- ego route: `4235`
- crossing vehicle route: `4236`
- ego control: `Driver 1 0 <speed>`
- target control: `VelTransition <speed> linear`
- conflict timing: copy the route-distance formula from IPG's `Intersection.tcl`

The first test does not need to be novel. It only needs to prove that the new generation target, `native_route_template`, loads and runs without the OpenSCENARIO route/trajectory issues seen in TGT-003.

After that, build a parameterized generator that can vary:

- ego speed,
- target speed,
- target start position,
- actor type,
- optional pedestrians/static actors,
- signal timing assumptions,
- end conditions.

## Decision Summary

Do not discard the existing OpenDRIVE/OpenSCENARIO work. It remains useful.

However, for the user's actual goal, LLM-based automatic generation of executable CarMaker scenarios with surrounding vehicles and pedestrians, native segment assembly should become the main path.
