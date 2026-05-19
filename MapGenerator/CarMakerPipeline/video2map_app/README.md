# Video2Map RoadGen Assistant

Small preprocessor app for turning a reference driving video into a schematic
RoadGen graph, then using the existing RoadGen, TrafficGen, and CarMaker helpers
to create a runnable scenario.

## Purpose

This app does not try to reconstruct survey-grade road geometry. It creates a
simple, editable graph that is good enough for:

- approximate road shape and lane count
- signal/crosswalk hints
- an ego route hint
- one default traffic car
- RoadGen export generation
- direct CarMaker RD5/TestRun generation

No OpenAI API key is used. The app is local-draft only.

## Run

Double-click:

```text
video2map_app\run_app.bat
```

or:

```powershell
cd <workspace>\video2map_app
python desktop_app.py
```

## Workflow

1. Select a video.
2. Click `Extract Frames`.
   Use 12-20 frame samples when you want Codex to inspect more of the scene.
3. Review or edit the local draft JSON graph.
4. Optional: click `Prepare Codex Review`, ask Codex to review the generated
   request package, then click `Load Codex Result`.
5. Click `Generate RoadGen Export`.
6. Click `Generate Ego + Traffic TestRun` to create RD5 routes and a CarMaker
   TestRun under `C:\CM_Projects\MapGen_TEST`.
7. Click `Generate + Run CarMaker (5x)` to launch with classic IPGMovie, or
   `Generate + Run CarMaker (5x + MovieNX)` to attach MovieNX to the running
   CarMaker process. The MovieNX path waits longer for the movie frontend to
   finish warming up before switching the simulation to 5x.

For a higher-accuracy manual workflow, open `carmaker_pipeline_app` after step 5.
The RoadGen export includes `video2map_trafficgen_preset.json`; when the
pipeline opens TrafficGen, it passes that preset so TrafficGen starts with the
intended ego route and traffic car already loaded for visual checking.

The generated RoadGen export contains `video2map_analysis.json` with the
summary, graph, assumptions, and ego route hint. Scenario reports are written
under `video2map_app\exports\<project>\*_testrun`.

## CLI Smoke Test

```powershell
python desktop_app.py --project accident_case_video --generate --testrun
```
