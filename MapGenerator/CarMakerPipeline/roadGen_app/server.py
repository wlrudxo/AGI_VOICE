from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent
EXPORTS = ROOT / "exports"


def find_netconvert() -> str | None:
    found = shutil.which("netconvert")
    if found:
        return found

    candidates = [
        Path(r"C:\Program Files (x86)\Eclipse\Sumo\bin\netconvert.exe"),
        Path(r"C:\Program Files\Eclipse\Sumo\bin\netconvert.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def find_osc2cm() -> str | None:
    candidates = []
    base = Path(r"C:\IPG\carmaker")
    if base.exists():
        candidates.extend(base.glob(r"win64-*\bin\osc2cm.exe"))

    def version_key(path: Path) -> tuple[int, int, int, str]:
        match = re.search(r"win64-(\d+)\.(\d+)\.(\d+)", str(path))
        if not match:
            return (0, 0, 0, str(path))
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)), str(path))

    if candidates:
        return str(sorted(candidates, key=version_key)[-1])
    return shutil.which("osc2cm")


def slugify(value: str) -> str:
    value = value.strip() or "road_graph"
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return value.strip("._-") or "road_graph"


def clean_id(value: str, fallback: str) -> str:
    value = (value or fallback).strip()
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return value or fallback


def write_xml(path: Path, root: ET.Element) -> None:
    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


SUMO_NODE_TYPE_ALIASES = {
    "traffic_light_crosswalk": "traffic_light",
    "crosswalk": "priority",
}


def sumo_node_type(node_type: object) -> str:
    raw = str(node_type or "").strip()
    return SUMO_NODE_TYPE_ALIASES.get(raw, raw)


def build_node_xml(nodes: list[dict], path: Path) -> None:
    root = ET.Element("nodes")
    for idx, node in enumerate(nodes, start=1):
        node_id = clean_id(node.get("id"), f"N{idx}")
        attrs = {
            "id": node_id,
            "x": f"{float(node.get('x', 0)):.3f}",
            "y": f"{float(node.get('y', 0)):.3f}",
        }
        node_type = sumo_node_type(node.get("type"))
        if node_type:
            attrs["type"] = node_type
        ET.SubElement(root, "node", attrs)
    write_xml(path, root)


def build_edge_xml(edges: list[dict], node_ids: set[str], path: Path) -> list[str]:
    root = ET.Element("edges")
    used_ids: set[str] = set()
    written: list[str] = []

    def add_edge(edge_id: str, from_node: str, to_node: str, lanes: int, speed_ms: float) -> None:
        if from_node not in node_ids or to_node not in node_ids:
            raise ValueError(f"Edge '{edge_id}' references a missing node.")
        edge_id = clean_id(edge_id, f"E_{from_node}_{to_node}")
        base = edge_id
        suffix = 2
        while edge_id in used_ids:
            edge_id = f"{base}_{suffix}"
            suffix += 1
        used_ids.add(edge_id)
        written.append(edge_id)
        ET.SubElement(
            root,
            "edge",
            {
                "id": edge_id,
                "from": from_node,
                "to": to_node,
                "numLanes": str(max(1, int(lanes))),
                "speed": f"{speed_ms:.3f}",
            },
        )

    for idx, edge in enumerate(edges, start=1):
        from_node = clean_id(edge.get("from"), "")
        to_node = clean_id(edge.get("to"), "")
        lanes = max(1, int(edge.get("numLanes", 1)))
        speed_kmh = max(1.0, float(edge.get("speedKmh", 50)))
        speed_ms = speed_kmh / 3.6
        edge_id = clean_id(edge.get("id"), f"E{idx}")
        add_edge(edge_id, from_node, to_node, lanes, speed_ms)
        if edge.get("twoWay", True):
            add_edge(f"{edge_id}_rev", to_node, from_node, lanes, speed_ms)

    write_xml(path, root)
    return written


def run_netconvert(node_xml: Path, edge_xml: Path, net_xml: Path, xodr: Path) -> list[dict]:
    netconvert = find_netconvert()
    if not netconvert:
        raise RuntimeError("netconvert.exe was not found in PATH.")

    commands = [
        [
            netconvert,
            "--node-files",
            str(node_xml),
            "--edge-files",
            str(edge_xml),
            "--output-file",
            str(net_xml),
        ],
        [
            netconvert,
            "--sumo-net-file",
            str(net_xml),
            "--opendrive-output",
            str(xodr),
            "--geometry.min-radius.fix.railways",
            "false",
            "--geometry.avoid-overlap",
            "false",
            "--geometry.max-grade.fix",
            "false",
            "--offset.disable-normalization",
            "true",
            "--lefthand",
            "false",
            "--no-turnarounds",
            "true",
            "--junctions.corner-detail",
            "5",
            "--junctions.limit-turn-speed",
            "5.50",
            "--walkingareas",
            "false",
        ],
    ]

    results: list[dict] = []
    for command in commands:
        proc = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
        results.append(
            {
                "command": " ".join(f'"{part}"' if " " in part else part for part in command),
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr or proc.stdout or "netconvert failed.")
    return results


def build_openscenario_bridge(project_name: str, xodr_name: str, path: Path) -> None:
    root = ET.Element("OpenSCENARIO")
    ET.SubElement(
        root,
        "FileHeader",
        {
            "revMajor": "1",
            "revMinor": "2",
            "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "description": f"RoadGen OpenDRIVE import bridge for {project_name}",
            "author": "roadGen_app",
        },
    )
    ET.SubElement(root, "ParameterDeclarations")
    ET.SubElement(root, "CatalogLocations")
    road_network = ET.SubElement(root, "RoadNetwork")
    ET.SubElement(road_network, "LogicFile", {"filepath": f"./{xodr_name}"})
    ET.SubElement(root, "Entities")
    storyboard = ET.SubElement(root, "Storyboard")
    init = ET.SubElement(storyboard, "Init")
    ET.SubElement(init, "Actions")
    ET.SubElement(storyboard, "Story", {"name": "RoadGenEmptyStory"})
    stop = ET.SubElement(storyboard, "StopTrigger")
    group = ET.SubElement(stop, "ConditionGroup")
    condition = ET.SubElement(
        group,
        "Condition",
        {"name": "StopAfterImport", "delay": "0", "conditionEdge": "rising"},
    )
    by_value = ET.SubElement(condition, "ByValueCondition")
    ET.SubElement(by_value, "SimulationTimeCondition", {"value": "0.1", "rule": "greaterThan"})
    write_xml(path, root)


def build_carmaker_import_notes(project_name: str, xodr_name: str, xosc_name: str, path: Path) -> None:
    osc2cm = find_osc2cm() or r"C:\IPG\carmaker\win64-15.0.1\bin\osc2cm.exe"
    command = (
        f'& "{osc2cm}" --cmprojpath "<YOUR_CARMAKER_PROJECT>" '
        f'--oscfname "Data/OpenSCENARIO/RoadGen/{xosc_name}" '
        f'--rdfname "{project_name}.rd5" '
        f'--trfname "{project_name}_import" --logtoconsole'
    )
    text = f"""# CarMaker Import Notes

This folder contains an OpenDRIVE road generated by roadGen_app.

Important:

- Do not select `{xodr_name}` directly as a normal CarMaker Road file under `Data/Road`.
- CarMaker Road files are ROAD5 InfoFiles (`.rd5`) and usually start with `#INFOFILE1.1`.
- If CarMaker tries to read an `.xodr` as a Road InfoFile, it can report:
  `seems not to be a correct Info File`.

Recommended GUI flow:

1. Open CarMaker.
2. Go to `Parameters > Scenario / Road`.
3. Use the menu/import function for `Import road definition`.
4. Select `{xodr_name}` as an OpenDRIVE road definition.
5. Save/export the imported result as a ROAD5 `.rd5` file.
6. Use that `.rd5` as the Road file in the TestRun.

RoadGen desktop direct conversion:

The desktop app's `Copy To CarMaker` button tries CarMaker 15's bundled
IPGRoad Python API first:

```text
RoadReadOpenDRIVE() -> RoadWriteFile(...rd5...)
```

If the CarMaker license is reachable, it writes `{project_name}.rd5` directly
to `<YOUR_CARMAKER_PROJECT>/Data/Road/`. The desktop app then adds default
visual safety margins in RD5: a `0.8 m` shoulder and a `2.2 m` sidewalk outside
the driving road, without changing SUMO/OpenDRIVE lane IDs used by TrafficGen.

CarMaker 15 command-line bridge:

1. Copy `{xodr_name}` and `{xosc_name}` into:
   `<YOUR_CARMAKER_PROJECT>/Data/OpenSCENARIO/RoadGen/`
2. Run:

```powershell
{command}
```

The command uses `osc2cm.exe` to convert the OpenSCENARIO file that references
the OpenDRIVE file. It should create a Road5 file named `{project_name}.rd5`
and a TestRun named `{project_name}_import` inside the selected CarMaker project.
"""
    path.write_text(text, encoding="utf-8")


def generate_project(payload: dict) -> dict:
    graph = payload.get("graph") or {}
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    if len(nodes) < 2:
        raise ValueError("At least two nodes are required.")
    if not edges:
        raise ValueError("At least one edge is required.")

    node_ids = [clean_id(node.get("id"), f"N{idx}") for idx, node in enumerate(nodes, start=1)]
    if len(set(node_ids)) != len(node_ids):
        raise ValueError("Node IDs must be unique.")
    for node, node_id in zip(nodes, node_ids):
        node["id"] = node_id

    project_name = slugify(payload.get("projectName", "road_graph"))
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = EXPORTS / f"{project_name}_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    node_xml = out_dir / "node.xml"
    edge_xml = out_dir / "edge.xml"
    net_xml = out_dir / f"{project_name}.net.xml"
    xodr = out_dir / f"{project_name}.xodr"
    xosc = out_dir / f"{project_name}_carmaker_import.xosc"
    carmaker_notes = out_dir / "CARMAKER_IMPORT.md"
    graph_json = out_dir / "graph.json"

    build_node_xml(nodes, node_xml)
    edge_ids = build_edge_xml(edges, set(node_ids), edge_xml)
    graph_json.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    commands = run_netconvert(node_xml, edge_xml, net_xml, xodr)
    build_openscenario_bridge(project_name, xodr.name, xosc)
    build_carmaker_import_notes(project_name, xodr.name, xosc.name, carmaker_notes)

    rel = out_dir.relative_to(ROOT).as_posix()
    return {
        "project": out_dir.name,
        "edgeIds": edge_ids,
        "files": {
            "graph": f"/{rel}/graph.json",
            "nodeXml": f"/{rel}/node.xml",
            "edgeXml": f"/{rel}/edge.xml",
            "netXml": f"/{rel}/{net_xml.name}",
            "xodr": f"/{rel}/{xodr.name}",
            "xosc": f"/{rel}/{xosc.name}",
            "carmakerNotes": f"/{rel}/{carmaker_notes.name}",
        },
        "commands": commands,
        "carmaker": {
            "osc2cm": find_osc2cm(),
            "warning": "Import the .xodr as OpenDRIVE or convert through the generated .xosc; do not use .xodr directly as a ROAD5 InfoFile.",
        },
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:
        print(f"[roadGen] {self.address_string()} - {format % args}")

    def send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self.send_json(
                200,
                {
                    "ok": True,
                    "netconvert": find_netconvert(),
                    "osc2cm": find_osc2cm(),
                    "root": str(ROOT),
                },
            )
            return
        if self.path == "/":
            self.path = "/index.html"
        self.path = unquote(self.path)
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/generate":
            self.send_json(404, {"ok": False, "error": "Unknown API route."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = generate_project(payload)
            self.send_json(200, {"ok": True, **result})
        except Exception as exc:
            self.send_json(400, {"ok": False, "error": str(exc)})


def main() -> None:
    EXPORTS.mkdir(exist_ok=True)
    host = "127.0.0.1"
    port = 8765
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"roadGen app running at http://{host}:{port}")
    print(f"exports: {EXPORTS}")
    server.serve_forever()


if __name__ == "__main__":
    main()
