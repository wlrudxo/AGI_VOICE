# Road Graph Generator

Small local tool for creating a road graph, exporting SUMO `node.xml`/`edge.xml`,
and converting the result to OpenDRIVE `.xodr` with SUMO `netconvert`.

## Desktop App, No Local Web Server

```powershell
cd C:\Users\user\Desktop\과제\AGI\roadGen_app
python desktop_app.py
```

This opens a Tkinter desktop window. It does not start a localhost web server.
The app calls the same Python generation pipeline directly.

## Browser App, Localhost Bridge

```powershell
cd C:\Users\user\Desktop\과제\AGI\roadGen_app
python server.py
```

Then open:

```text
http://127.0.0.1:8765
```

## Flow

1. Draw nodes and edges.
2. Keep bidirectional edges enabled for two-way roads.
3. Click `Generate XODR`.
4. Generated files are written under `exports/<project>_<timestamp>/`.
5. `Copy To CarMaker` writes the RD5 with default visual safety margins:
   a narrow `0.8 m` shoulder first, then a `2.2 m` sidewalk strip outside the
   driving road. These are added after XODR-to-RD5 conversion, so SUMO/OpenDRIVE
   driving lane IDs stay unchanged for TrafficGen route mapping.
6. Optional: set an intersection node's `Type` to `traffic_light`,
   `traffic_light_crosswalk`, or `crosswalk`. During `Copy To CarMaker`, the app
   detects those graph nodes and adds RD5 intersection decorations around the
   matching road endpoints. `traffic_light` creates signal objects plus
   visual signal objects for IPGMovie.
   `traffic_light_crosswalk` adds those signals and zebra-style crosswalk road
   markings plus pedestrian-aware `DrvStop` markers on the lane paths.
   `crosswalk` adds the crosswalk markings and the same pedestrian-aware stop
   markers without signal objects. Internally,
   `traffic_light_crosswalk` is exported to SUMO as `traffic_light`, while the
   richer type is kept in `graph.json` for the RD5 post-processing step.
   If the XODR-to-RD5 import already created CarMaker `Control.TrfLight` and
   `Mount` entries, RoadGen reuses those imported controllers instead of adding
   duplicate visual signal objects. It also adds LanePath-level
   `DrvStop` markers of type `RDST_TrfLight` at the imported signal mount's
   actual `s` position, draws matching visible stop-line markings, and changes
   imported controllers from initial phase `0` (off) to `3` (red), matching the
   structure used by CarMaker example roads where IPG Driver detects traffic
   lights.
7. Optional: set `Env` to `City` before `Copy To CarMaker` to add building
   scenery to the generated RD5. `City Seed` controls repeatability: `Stable`
   reuses the same layout for the same project name, while `Random` generates a
   fresh layout on each copy. `City Density` controls how tightly buildings are
   placed. `1.0` is the previous/default spacing; higher values create more
   building slots, raise the building cap, and relax building-to-building
   spacing so dense city blocks can overlap slightly while still keeping road
   clearance. Values up to `32.0` are available from the spinbox, slider, or
   mouse wheel. At higher densities the generator also places second and third
   rows of buildings farther from the road so the scene reads as a denser city,
   while road clearance is still preserved. Buildings are rotated parallel to
   the nearest generated road link. The City pass also adds RD5 `TreeStrip`
   vegetation along the roadside by default, so empty roadside space between
   sidewalks and buildings reads as grass/greenery instead of bare terrain.
8. For CarMaker, use `Copy To CarMaker` or the generated import notes. Do not
   select the `.xodr` directly as a normal file under `Data/Road`.

## Desktop Controls

- `Save Template` writes the current graph to `templates/<project>.json`.
- `Load Template` loads the selected file in the template list. If nothing is
  selected, it opens a file picker starting in `templates/`.
- In Select mode, Ctrl-click or Shift-click nodes/edges to multi-select.
- Drag a selected node to move all currently selected nodes together.
- Use the mouse wheel over the canvas to zoom around the cursor.
- Drag empty canvas space to pan the view like a map.
- When multiple nodes are selected, the Inspector can update their node type at
  once.
- When multiple edges are selected, the Inspector can update lanes, speed, and
  bidirectional state at once.

## CarMaker Import

CarMaker road files are ROAD5 InfoFiles (`.rd5`). A raw OpenDRIVE `.xodr` is not
the same format. If a generated `.xodr` is selected directly as a Road file in
`Data/Road`, CarMaker can report that it is not a correct Info File.

Use one of these flows:

- GUI: `Parameters > Scenario / Road > Import road definition`, select the
  generated `.xodr`, then save the imported road as `.rd5`.
- Direct app conversion: click `Generate XODR`, then `Copy To CarMaker`. The app
  tries CarMaker 15's bundled IPGRoad Python API first:
  `RoadReadOpenDRIVE()` -> `RoadWriteFile(...rd5...)`. If the CarMaker license is
  reachable, it writes `<CarMakerProject>/Data/Road/<project>.rd5` directly.
  After conversion, the app adds default RD5 roadside safety margins as visual
  geometry: `0.8 m` shoulder plus `2.2 m` sidewalk outside the generated road.
  This avoids SUMO `sidewalkWidth`, which would add a pedestrian lane to the
  `.net.xml` and shift route lane IDs such as `E*_0`.
  If any graph nodes are marked as `traffic_light`, `traffic_light_crosswalk`,
  or `crosswalk`, the app also adds a generated RD5 intersection-decoration
  block. Signal nodes get CarMaker Movie HAWK signal objects.
  Crosswalk nodes get zebra stripes as RD5 `RoadMarking` entries, using the same
  point-list pattern as CarMaker urban-road examples. They also get lane-level
  `RDST_Pedestrian` Driver stop markers so IPG Driver can watch for pedestrians
  around the crossing. These decorations are
  derived from the saved `graph.json`, the generated `.xodr`, and the converted
  RD5 `odrRoadId` tags, so changing a node back to `priority` removes the
  generated block the next time the RD5 is written.
  If `Env` is set to `City`, the app then adds RD5 `GeoObject` scenery blocks
  with building models from CarMaker's `Movie/3D/Buildings` asset folder. The
  placement uses each model's `.objinfo` bounding box and a full-road clearance
  check, so large buildings are pushed farther away from the road network. It
  uses the project name as the default stable seed; set `City Seed` to `Random`
  for a different building layout each time. `City Density` can be increased up
  to `32.0`; higher values multiply the requested building count, reduce
  building-to-building spacing, and add extra rows of buildings farther away
  from the roadside. Road clearance is still preserved. Building yaw is aligned
  parallel to the local road link, with only a tiny jitter so dense blocks look
  more ordered. It also writes `RL.*.TreeStrip.*` entries, based on CarMaker's
  own urban-road examples, to fill non-building roadside areas with vegetation.
  It leaves the RD5 terrain unchanged to avoid mismatched ground height in
  Movie.
  The city pass reuses the same shoulder+sidewalk profile and also adds a
  wider per-link roadside mesh. For generated two-way roads, it treats
  duplicated opposite links as one physical road and places each strip only on
  the outside of each directed link, so the center/opposite lane is not covered.
  Lane type, lane width, lane material, and route topology are left unchanged.
  CarMaker's own AEB urban examples keep vehicle routes on driving lanes and
  place pedestrians with route offsets; mutating generated margin lanes into
  pedestrian lanes can disturb route selection.
- Command line fallback: `Copy To CarMaker` also copies
  the `.xodr`, the generated `.xosc` bridge, and notes into
  `<CarMakerProject>/Data/OpenSCENARIO/RoadGen/`, and writes a PowerShell
  command for `osc2cm.exe`. The project picker starts in `C:\CM_Projects` when
  that folder exists. Running that command creates a `.rd5` and TestRun if the
  direct IPGRoad conversion is not used.

CarMaker 15 IPGRoad conversion was verified against
`figure8_with_high_way_road.xodr`. The import can report junction-link messages,
but still returns success and writes a usable `.rd5` when the license is
available.

The generator writes:

- `graph.json`
- `node.xml`
- `edge.xml`
- `<project>.net.xml`
- `<project>.xodr`
- `<project>_carmaker_import.xosc`
- `CARMAKER_IMPORT.md`

## Notes

- The app expects `netconvert.exe` to be available in `PATH`.
- Reverse SUMO edges are generated as `<edge_id>_rev` when an app edge is
  marked bidirectional.
- This handles road geometry generation only. Traffic route generation should be
  layered on top after this graph-to-xodr-to-rd5 pipeline is stable.
