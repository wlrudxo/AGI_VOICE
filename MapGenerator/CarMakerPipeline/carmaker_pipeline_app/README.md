# CarMaker Pipeline App

Unified control app for the current RoadGen and TrafficGen workflow.

## Run

```powershell
cd C:\Users\user\Desktop\과제\AGI\carmaker_pipeline_app
python desktop_app.py
```

or double-click:

```text
run_app.bat
```

## Flow

1. Open RoadGen App.
2. Draw or load a graph and click `Generate XODR`.
3. The pipeline app automatically follows the latest RoadGen export.
4. Optional: set `Env` to `City` to add randomized building scenery after RD5
   conversion.
5. Click `Convert XODR to RD5`.
6. Click `Open TrafficGen With Current Paths`.
7. In TrafficGen, plan lane routes, add vehicles, and click
   `Generate + Run 5x + IPGMovie`.

`Auto-follow latest RoadGen export` is enabled by default. When RoadGen creates a
new export folder, the pipeline app updates:

- RoadGen export folder
- `*.xodr`
- RD5 output path

Those same values are passed to TrafficGen when `Open TrafficGen With Current
Paths` is clicked.

`Generate + Run 5x + IPGMovie` lives in TrafficGen because it needs the current
route and vehicle plan. It writes the TestRun under:

```text
<CarMakerProject>/Data/TestRun/<TestRun name>
```

Then it starts a CMAPI interactive runner that launches CarMaker, attaches
IPGMovie, and requests realtime factor `5.0`. When the simulation finishes,
CarMaker/IPGMovie are kept open for inspection or replay; close those windows
when you want the background runner to exit.

## What This App Connects

- RoadGen export folder: `roadGen_app/exports/<road>_<timestamp>`
- OpenDRIVE file: `*.xodr`
- CarMaker project: usually under `C:\CM_Projects`
- RD5 output: `<CarMakerProject>/Data/Road/<road>.rd5`
- TrafficGen launch arguments:
  - `--folder`
  - `--rd5`
  - `--project`
  - `--scenario`

The XODR to RD5 conversion uses CarMaker 15's bundled IPGRoad Python API:

```text
RoadReadOpenDRIVE() -> RoadWriteFile(...rd5...)
```

The `City` environment option post-processes the generated RD5 by inserting
road-relative `GeoObject` building scenery plus default RD5 `TreeStrip`
vegetation for empty roadside space. Building placement reads the
CarMaker building `.objinfo` bounding boxes and rejects candidates that are too
close to any RD5 road segment, so larger buildings are placed farther away from
the road. Tree strips are based on CarMaker's own urban-road examples and fill
non-building gaps with grass/greenery near the sidewalk. The option does not
replace the RD5 terrain, because mismatched terrain height can make the vehicle
appear to drive through the ground. It also adds a modest per-link roadside
mesh. The roadside additions are generated once per physical road geometry to
avoid stacked surfaces on bidirectional duplicate links. This is visual roadside
scenery; it does not rewrite the lane topology into routeable `RLT_Pedestrian`
lanes.

If conversion fails, use the RoadGen `Copy To CarMaker` fallback or the CarMaker
GUI OpenDRIVE import flow.
