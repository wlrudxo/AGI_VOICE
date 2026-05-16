# 2026-05-15 Route Driver Fix

## Symptom

IPGMovie opened, but the ego vehicle stayed still or the simulation looked like it did not really start.
The same symptom could appear even when no traffic actors were generated.

## Cause

The generated TestRun had route keys such as:

```text
Vehicle.Routing.Type = Route
Vehicle.StartPos.Type = Route
DrivMan.Man.0.LongStep.0.Dyn = Driver ...
DrivMan.Man.0.LatStep.0.Dyn = Driver 0
```

but it only wrote a few `Driver.Consider.*` lines. CarMaker example TestRuns that drive on
routes also save the route-driver profile in the TestRun itself, including:

```text
Driver.Course.Generation = Route
Driver.Long.Active = 1
Driver.Lat.Active = 1
DrivMan.VhclOperator.Driving.GearNo = 1
```

Without this profile, CarMaker can load the InfoFile without an error but still fail to create
a fully active route-following driver. That is why this looked different from the previous
InfoFile/BOM problem: there was no parse error, but the ego did not move.

## Fix

`trafficGen_app/testrun_core.py` now embeds a complete route driver/operator profile when it
generates a TestRun. Existing `route_traffic` and `route_traffic_1` in the MapGen_TEST project
were also patched once so they can be tested immediately.

Important: CarMaker treats repeated scalar InfoFile keys as a fatal syntax error. When patching
an already-generated TestRun, keep only one copy of each `Driver.Consider.*`,
`DrivMan.OW.Active`, and `DrivMan.OW.Quantities` key. A bad intermediate patch created this
error once:

```text
TestRun: Syntax error, file 'Data/TestRun/route_traffic'
line ... Duplicate key.
```

The current `route_traffic` and `route_traffic_1` files have been cleaned.

`trafficGen_app/carmaker_5x_runner.py` now logs the exact CMAPI phase around simulation start:

```text
Starting simulation.
Simulation start command returned; waiting for finish condition.
Simulation reached finished state.
```

If IPGMovie opens but the car still does not move, the newest
`C:\CM_Projects\MapGen_TEST\Data\Config\codex_cmapi_5x_*.log` file will show whether the
problem is before `start_sim()`, inside `start_sim()`, or after simulation has actually started.
