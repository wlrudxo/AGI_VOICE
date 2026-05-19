from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


APP_DIR = Path(__file__).resolve().parent
WORKSPACE = APP_DIR.parent
ROADGEN_DIR = WORKSPACE / "roadGen_app"
TRAFFICGEN_DIR = WORKSPACE / "trafficGen_app"
PIPELINE_DIR = WORKSPACE / "carmaker_pipeline_app"
PIPELINE_RUNNER = PIPELINE_DIR / "run_app.bat"
PIPELINE_SETTINGS = PIPELINE_DIR / "settings.json"
DEFAULT_PROJECT_ROOT = Path(r"C:\CM_Projects\MapGen_TEST")
DEFAULT_CARMAKER_HOME = Path(r"C:\IPG\carmaker\win64-15.0.1")
DEFAULT_EGO_MODEL = "Examples/DemoCar_BA"
DEFAULT_EGO_DRIVER = "Car_Normal"
DEFAULT_TRAFFIC_MODEL = "1_Vehicles/VW_Transporter_2016"
DEFAULT_TRAFFIC_DRIVER = "Car_Generic_Normal"
DEFAULT_VIDEO_NAME = "\uc0ac\uace0 \uc0ac\ub840 \uc608\uc2dc \ucd08\uc548.mp4"
DEFAULT_IPGMOVIE_READY_DELAY = 5.0
DEFAULT_MOVIENX_READY_DELAY = 20.0

for module_dir in [ROADGEN_DIR, TRAFFICGEN_DIR]:
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))

try:
    from server import generate_project, slugify
    from carmaker_converter import convert_xodr_to_rd5
    from rd5_environment import decorate_rd5_city, decorate_rd5_intersections, decorate_rd5_safety_margins
except Exception as exc:  # pragma: no cover - surfaced in the GUI at runtime
    generate_project = None  # type: ignore[assignment]
    convert_xodr_to_rd5 = None  # type: ignore[assignment]
    decorate_rd5_city = None  # type: ignore[assignment]
    decorate_rd5_intersections = None  # type: ignore[assignment]
    decorate_rd5_safety_margins = None  # type: ignore[assignment]

    def slugify(value: str) -> str:
        cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value.strip())
        return cleaned.strip("._-") or "road_graph"

    ROADGEN_IMPORT_ERROR = exc
else:
    ROADGEN_IMPORT_ERROR = None

try:
    from traffic_core import RoadPackage, RoadPackageError, VehiclePlan, edge_id_from_lane, safe_name
    from rd5_core import Rd5Road, write_rd5_with_route
    from testrun_core import EgoPlan, TestRunConfig, project_road_reference, write_testrun
except Exception as exc:  # pragma: no cover - surfaced in the GUI at runtime
    RoadPackage = None  # type: ignore[assignment]
    RoadPackageError = RuntimeError  # type: ignore[assignment]
    VehiclePlan = None  # type: ignore[assignment]
    Rd5Road = None  # type: ignore[assignment]
    write_rd5_with_route = None  # type: ignore[assignment]
    EgoPlan = None  # type: ignore[assignment]
    TestRunConfig = None  # type: ignore[assignment]
    project_road_reference = None  # type: ignore[assignment]
    write_testrun = None  # type: ignore[assignment]

    def safe_name(value: str) -> str:
        return slugify(value)

    def edge_id_from_lane(lane_id: str) -> str:
        return lane_id.rsplit("_", 1)[0]

    TRAFFICGEN_IMPORT_ERROR = exc
else:
    TRAFFICGEN_IMPORT_ERROR = None


@dataclass
class FrameExtraction:
    video_path: Path
    output_dir: Path
    frame_paths: list[Path]
    contact_sheet: Path | None
    frame_count: int
    fps: float
    width: int
    height: int
    duration_s: float


@dataclass
class ScenarioBuildResult:
    export_dir: Path
    xodr_path: Path
    rd5_path: Path
    testrun_path: Path
    report_dir: Path
    ego_route_name: str
    traffic_route_name: str
    route_ids: dict[str, str]


def default_video_path() -> Path:
    preferred = WORKSPACE / DEFAULT_VIDEO_NAME
    if preferred.exists():
        return preferred
    matches = sorted(WORKSPACE.glob("*.mp4"), key=lambda path: path.stat().st_mtime, reverse=True)
    return matches[0] if matches else preferred


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_video_frames(video_path: Path, output_dir: Path, sample_count: int = 7) -> FrameExtraction:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required for video frame extraction. Install package `opencv-python`.") from exc

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration_s = frame_count / fps if fps else 0.0

    if frame_count <= 0:
        indices = [0]
    else:
        sample_count = max(1, min(sample_count, frame_count))
        if sample_count == 1:
            ratios = [0.5]
        else:
            ratios = [0.05 + (0.90 * idx / (sample_count - 1)) for idx in range(sample_count)]
        indices = [min(frame_count - 1, max(0, int(frame_count * ratio))) for ratio in ratios]

    frame_paths: list[Path] = []
    for index in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = cap.read()
        if not ok:
            continue
        ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        if not ok:
            continue
        path = output_dir / f"frame_{index:06d}.jpg"
        path.write_bytes(buffer.tobytes())
        frame_paths.append(path)

    cap.release()
    contact_sheet = build_contact_sheet(frame_paths, output_dir / "contact_sheet.jpg")
    return FrameExtraction(
        video_path=video_path,
        output_dir=output_dir,
        frame_paths=frame_paths,
        contact_sheet=contact_sheet,
        frame_count=frame_count,
        fps=fps,
        width=width,
        height=height,
        duration_s=duration_s,
    )


def build_contact_sheet(frame_paths: list[Path], output_path: Path) -> Path | None:
    if not frame_paths:
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None

    thumbs = []
    for path in frame_paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((284, 160))
        canvas = Image.new("RGB", (284, 184), "white")
        canvas.paste(image, ((284 - image.width) // 2, 0))
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 164), path.stem, fill=(20, 20, 20))
        thumbs.append(canvas)

    columns = 2
    rows = (len(thumbs) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * 284, rows * 184), (245, 245, 245))
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % columns) * 284, (index // columns) * 184))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, quality=92)
    return output_path


def local_draft_analysis(project_name: str) -> dict:
    safe_project = slugify(project_name or "accident_case_video")
    return {
        "projectName": safe_project,
        "summary": (
            "Draft graph for a dashcam-style urban scene: a multi-lane approach, "
            "left turn through a signalized intersection, then a straight westbound four-lane ego road."
        ),
        "hardConstraints": {
            "accidentCaseSouthToWest4Lane": True,
            "egoRouteEdges": ["E1", "E2", "E3"],
            "egoRouteNumLanes": 4,
            "egoRouteLaneIndex": 3,
            "egoAllowLaneChanges": False,
            "noNorthwestRoad": True,
            "description": (
                "This accident-case map is a south-to-west left turn. "
                "The ego route must use four-lane edges E1/E2/E3, stay in lane index 3 after the intersection, "
                "and there must be no north-west exit road."
            ),
        },
        "confidence": 0.55,
        "assumptions": [
            "Distances are schematic meters, not surveyed measurements.",
            "The graph favors a simple CarMaker-valid topology over visual exactness.",
            "The video perspective can make the west exit look north-west, but the map topology is south-to-west only.",
            "The ego route edges are fixed as four-lane roads, and the ego should not change lanes after the intersection.",
            "Roadside buildings and trees should be added by the pipeline City environment option.",
        ],
        "graph": {
            "nodes": [
                {"id": "N1", "x": 0.0, "y": -115.0, "type": "priority"},
                {"id": "N2", "x": 0.0, "y": 0.0, "type": "traffic_light_crosswalk"},
                {"id": "N3", "x": -62.0, "y": 0.0, "type": "traffic_light_crosswalk"},
                {"id": "N4", "x": -190.0, "y": 0.0, "type": "priority"},
                {"id": "N5", "x": 95.0, "y": 0.0, "type": "traffic_light_crosswalk"},
                {"id": "N6", "x": 0.0, "y": 105.0, "type": "traffic_light_crosswalk"},
            ],
            "edges": [
                {"id": "E1", "from": "N1", "to": "N2", "numLanes": 4, "speedKmh": 40.0, "twoWay": True},
                {"id": "E2", "from": "N2", "to": "N3", "numLanes": 4, "speedKmh": 30.0, "twoWay": True},
                {"id": "E3", "from": "N3", "to": "N4", "numLanes": 4, "speedKmh": 35.0, "twoWay": True},
                {"id": "E4", "from": "N6", "to": "N2", "numLanes": 3, "speedKmh": 40.0, "twoWay": True},
                {"id": "E5", "from": "N2", "to": "N5", "numLanes": 3, "speedKmh": 40.0, "twoWay": True},
            ],
        },
        "ego": {
            "description": "Ego approaches from the south, turns left, and continues straight west on four-lane edges.",
            "routeHintEdges": ["E1", "E2", "E3"],
            "startNode": "N1",
            "goalNode": "N4",
            "speedKmh": 35.0,
        },
        "trafficHints": [],
    }


def normalize_analysis(analysis: dict, fallback_project: str) -> dict:
    analysis = dict(analysis or {})
    analysis["projectName"] = slugify(str(analysis.get("projectName") or fallback_project or "video_road"))
    graph = analysis.setdefault("graph", {})
    graph["nodes"] = list(graph.get("nodes") or [])
    graph["edges"] = list(graph.get("edges") or [])

    for index, node in enumerate(graph["nodes"], start=1):
        node["id"] = str(node.get("id") or f"N{index}")
        node["x"] = float(node.get("x", 0.0))
        node["y"] = float(node.get("y", 0.0))
        node["type"] = str(node.get("type") or "priority")

    valid_nodes = {node["id"] for node in graph["nodes"]}
    kept_edges = []
    for index, edge in enumerate(graph["edges"], start=1):
        from_node = str(edge.get("from") or "")
        to_node = str(edge.get("to") or "")
        if from_node not in valid_nodes or to_node not in valid_nodes or from_node == to_node:
            continue
        kept_edges.append(
            {
                "id": str(edge.get("id") or f"E{index}"),
                "from": from_node,
                "to": to_node,
                "numLanes": max(1, min(5, int(edge.get("numLanes", 1)))),
                "speedKmh": max(5.0, min(100.0, float(edge.get("speedKmh", 40.0)))),
                "twoWay": bool(edge.get("twoWay", True)),
            }
        )
    graph["edges"] = kept_edges
    analysis.setdefault("summary", "")
    analysis.setdefault("confidence", 0.5)
    analysis.setdefault("assumptions", [])
    analysis.setdefault("ego", {})
    analysis.setdefault("trafficHints", [])
    apply_hard_constraints(analysis)
    return analysis


def apply_hard_constraints(analysis: dict) -> None:
    constraints = analysis.get("hardConstraints") or {}
    is_accident_case = analysis.get("projectName") == "accident_case_video"
    if not constraints.get("accidentCaseSouthToWest4Lane") and not is_accident_case:
        return

    graph = analysis.setdefault("graph", {})
    nodes = {node["id"]: node for node in graph.get("nodes", []) if node.get("id")}
    forced_nodes = {
        "N1": {"id": "N1", "x": 0.0, "y": -115.0, "type": "priority"},
        "N2": {"id": "N2", "x": 0.0, "y": 0.0, "type": "traffic_light_crosswalk"},
        "N3": {"id": "N3", "x": -62.0, "y": 0.0, "type": "traffic_light_crosswalk"},
        "N4": {"id": "N4", "x": -190.0, "y": 0.0, "type": "priority"},
    }
    nodes.update(forced_nodes)

    if constraints.get("noNorthwestRoad") or is_accident_case:
        nodes = {
            node_id: node
            for node_id, node in nodes.items()
            if node_id in forced_nodes or not (float(node.get("x", 0.0)) < -1.0 and float(node.get("y", 0.0)) > 1.0)
        }

    ego_edges = list(constraints.get("egoRouteEdges") or ["E1", "E2", "E3"])
    ego_lane_count = max(1, min(5, int(constraints.get("egoRouteNumLanes") or 4)))
    forced_edges = {
        "E1": {"id": "E1", "from": "N1", "to": "N2", "numLanes": ego_lane_count, "speedKmh": 40.0, "twoWay": True},
        "E2": {"id": "E2", "from": "N2", "to": "N3", "numLanes": ego_lane_count, "speedKmh": 30.0, "twoWay": True},
        "E3": {"id": "E3", "from": "N3", "to": "N4", "numLanes": ego_lane_count, "speedKmh": 35.0, "twoWay": True},
    }
    edges = {
        edge["id"]: edge
        for edge in graph.get("edges", [])
        if edge.get("id") and edge.get("from") in nodes and edge.get("to") in nodes and edge.get("id") not in forced_edges
    }
    edges.update({edge_id: forced_edges[edge_id] for edge_id in ego_edges if edge_id in forced_edges})
    graph["nodes"] = list(nodes.values())
    graph["edges"] = [edges[edge_id] for edge_id in ego_edges if edge_id in edges] + [
        edge for edge_id, edge in edges.items() if edge_id not in ego_edges
    ]

    ego = analysis.setdefault("ego", {})
    ego["description"] = "Ego approaches from the south, turns left, and continues straight west on four-lane edges."
    ego["routeHintEdges"] = ego_edges
    ego["startNode"] = "N1"
    ego["goalNode"] = "N4"
    ego["routeLaneIndex"] = max(0, min(ego_lane_count - 1, int(constraints.get("egoRouteLaneIndex", ego_lane_count - 1))))
    ego["allowLaneChanges"] = bool(constraints.get("egoAllowLaneChanges", False))


def generate_roadgen_export(analysis: dict) -> tuple[dict, Path]:
    if ROADGEN_IMPORT_ERROR is not None or generate_project is None:
        raise RuntimeError(f"Could not import roadGen generator: {ROADGEN_IMPORT_ERROR}")
    analysis = normalize_analysis(analysis, str(analysis.get("projectName") or "video_road"))
    payload = {"projectName": analysis["projectName"], "graph": analysis["graph"]}
    result = generate_project(payload)
    export_dir = ROADGEN_DIR / "exports" / result["project"]
    write_json(export_dir / "video2map_analysis.json", analysis)
    write_trafficgen_preset(analysis, export_dir)
    update_pipeline_settings(export_dir, result)
    return result, export_dir


def update_pipeline_settings(export_dir: Path, roadgen_result: dict) -> None:
    settings = {}
    if PIPELINE_SETTINGS.exists():
        try:
            settings = read_json(PIPELINE_SETTINGS)
        except Exception:
            settings = {}

    xodr_path = next(export_dir.glob("*.xodr"), None)
    preset_path = export_dir / "video2map_trafficgen_preset.json"
    project_root = Path(settings.get("project") or DEFAULT_PROJECT_ROOT)
    rd5_path = ""
    if xodr_path:
        rd5_path = str(project_root / "Data" / "Road" / f"{slugify(xodr_path.stem)}.rd5")

    settings.update(
        {
            "project": str(project_root),
            "export": str(export_dir),
            "xodr": str(xodr_path or ""),
            "rd5": rd5_path,
            "scenario": settings.get("scenario") or "video_road_ego",
            "traffic_preset": str(preset_path) if preset_path.exists() else "",
            "environment": settings.get("environment") or "City",
            "auto_follow_latest": True,
        }
    )
    write_json(PIPELINE_SETTINGS, settings)


def short_hash(text: str, length: int = 10) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()[:length]


def shorten_stem(stem: str, max_length: int = 56) -> str:
    clean = safe_name(stem) or "video_road"
    if len(clean) <= max_length:
        return clean
    digest = short_hash(clean)
    keep = max(8, max_length - len(digest) - 1)
    return f"{clean[:keep].rstrip('_-')}_{digest}"


def route_ids_from_rd5(rd5, route_names: set[str]) -> dict[str, str]:
    route_ids: dict[str, str] = {}
    for route in rd5.routes.values():
        if not route.name or not route.route_id:
            continue
        candidates = {route.name, safe_name(route.name)}
        for route_name in route_names:
            if route_name in candidates or safe_name(route_name) in candidates:
                route_ids[route_name] = route.route_id
    return route_ids


def pick_lane(package, edge_id: str, prefer_index: int = 0) -> str | None:
    lanes = [
        lane
        for lane in package.lanes.values()
        if not lane.internal and lane.edge_id == edge_id
    ]
    if not lanes:
        return None
    lanes.sort(key=lambda lane: (abs(lane.index - prefer_index), lane.index))
    return lanes[0].id


def route_hint_lane_tokens(package, edge_ids: list[str], prefer_index: int = 0) -> list[str]:
    tokens: list[str] = []
    for edge_id in edge_ids:
        lane_id = pick_lane(package, edge_id, prefer_index=prefer_index)
        if lane_id and lane_id not in tokens:
            tokens.append(lane_id)
    return tokens


def plan_named_route(
    package,
    edge_ids: list[str],
    fallback: tuple[str, str],
    name: str,
    *,
    allow_lane_changes: bool = True,
    prefer_index: int = 0,
):
    tokens = route_hint_lane_tokens(package, edge_ids, prefer_index=prefer_index)
    if len(tokens) < 2:
        tokens = [token for token in fallback if token in package.lanes]
    if len(tokens) < 2:
        external = package.external_lanes
        if len(external) < 2:
            raise RoadPackageError("Could not find enough external lanes for route planning.")
        tokens = [external[0], external[-1]]
    route = package.plan_route_via(tokens, allow_lane_changes=allow_lane_changes)
    route.name = safe_name(name)
    return route


def build_default_routes(package, analysis: dict):
    ego = analysis.get("ego") or {}
    ego_edges = list(ego.get("routeHintEdges") or ["E1", "E2", "E3"])
    ego_lane_index = int(ego.get("routeLaneIndex", 0))
    ego_allow_lane_changes = bool(ego.get("allowLaneChanges", True))
    ego_route = plan_named_route(
        package,
        ego_edges,
        (f"E1_{ego_lane_index}", f"E3_{ego_lane_index}"),
        "ego_left_turn",
        allow_lane_changes=ego_allow_lane_changes,
        prefer_index=ego_lane_index,
    )

    graph_edges = {edge.get("id") for edge in (analysis.get("graph") or {}).get("edges", [])}
    if {"E4", "E5"}.issubset(graph_edges):
        try:
            traffic_route = plan_named_route(package, ["E4", "E5"], ("E4_0", "E5_0"), "traffic_crossing")
        except Exception:
            traffic_route = ego_route
    else:
        traffic_route = ego_route
    return ego_route, traffic_route


def write_trafficgen_preset(analysis: dict, export_dir: Path) -> Path:
    project_name = safe_name(analysis.get("projectName") or export_dir.name)
    ego = analysis.get("ego") or {}
    ego_edges = list(ego.get("routeHintEdges") or ["E1", "E2", "E3"])
    ego_lane_index = int(ego.get("routeLaneIndex", 0))
    ego_allow_lane_changes = bool(ego.get("allowLaneChanges", True))
    traffic_edges = ["E4", "E5"]
    graph_edges = {edge.get("id") for edge in (analysis.get("graph") or {}).get("edges", [])}
    if not set(traffic_edges).issubset(graph_edges):
        traffic_edges = ego_edges
    package = None
    if RoadPackage is not None:
        try:
            package = RoadPackage.load(export_dir)
        except Exception:
            package = None

    preset = {
        "version": 1,
        "source": "video2map_app",
        "scenario_name": f"{project_name}_ego_traffic",
        "notes": [
            "Generated as an editable intent preset for TrafficGen.",
            "TrafficGen replans routes against the loaded SUMO net.xml before writing RD5/TestRun files.",
        ],
        "routes": [
            {
                "name": "ego_left_turn",
                "role": "ego",
                "edge_ids": ego_edges,
                "lane_tokens": route_hint_lane_tokens(package, ego_edges, prefer_index=ego_lane_index)
                if package is not None
                else [],
                "allow_lane_changes": ego_allow_lane_changes,
                "include_uturns": False,
            },
            {
                "name": "traffic_crossing",
                "role": "traffic",
                "edge_ids": traffic_edges,
                "lane_tokens": route_hint_lane_tokens(package, traffic_edges) if package is not None else [],
                "allow_lane_changes": True,
                "include_uturns": False,
            },
        ],
        "ego": {
            "enabled": True,
            "route_name": "ego_left_turn",
            "model": DEFAULT_EGO_MODEL,
            "driver": DEFAULT_EGO_DRIVER,
            "speed_kmh": float((analysis.get("ego") or {}).get("speedKmh") or 35.0),
            "start_s": 0.0,
            "lane_offset": 0.0,
        },
        "traffic": [
            {
                "name": "TrafficCar_1",
                "route_name": "traffic_crossing",
                "model": DEFAULT_TRAFFIC_MODEL,
                "driver_model": DEFAULT_TRAFFIC_DRIVER,
                "control_mode": "ipg_driver",
                "speed_kmh": 25.0,
                "start_s_ratio": 0.12,
                "lane_offset": 0.0,
                "start_delay_s": 0.0,
            }
        ],
    }
    path = export_dir / "video2map_trafficgen_preset.json"
    write_json(path, preset)
    return path


def ensure_roadgen_ready() -> None:
    if ROADGEN_IMPORT_ERROR is not None or generate_project is None or convert_xodr_to_rd5 is None:
        raise RuntimeError(f"Could not import RoadGen/CarMaker generator modules: {ROADGEN_IMPORT_ERROR}")
    if TRAFFICGEN_IMPORT_ERROR is not None or RoadPackage is None or Rd5Road is None:
        raise RuntimeError(f"Could not import TrafficGen modules: {TRAFFICGEN_IMPORT_ERROR}")


def convert_and_decorate_rd5(export_dir: Path, analysis: dict, project_dir: Path) -> Path:
    ensure_roadgen_ready()
    xodr_path = next(export_dir.glob("*.xodr"), None)
    if not xodr_path:
        raise RuntimeError(f"No XODR file found in RoadGen export: {export_dir}")

    rd5_path = project_dir / "Data" / "Road" / f"{slugify(xodr_path.stem)}.rd5"
    try:
        result = convert_xodr_to_rd5(xodr_path, rd5_path)  # type: ignore[misc]
        rd5_path = result.rd5_path
    except Exception as exc:
        if not rd5_path.exists() or not rd5_matches_xodr(rd5_path, xodr_path):
            raise RuntimeError(
                "XODR to RD5 conversion failed, and no matching current RD5 was available to reuse. "
                "Open the pipeline app and convert this RoadGen export to RD5 before generating traffic. "
                f"Original error: {exc}"
            ) from exc

    try:
        decorate_rd5_safety_margins(rd5_path)  # type: ignore[misc]
    except Exception:
        pass
    try:
        decorate_rd5_city(rd5_path, seed=analysis.get("projectName") or xodr_path.stem)  # type: ignore[misc]
    except Exception:
        pass
    try:
        decorate_rd5_intersections(  # type: ignore[misc]
            rd5_path,
            graph_path=export_dir / "graph.json",
            xodr_path=xodr_path,
        )
    except Exception:
        pass
    return rd5_path


def rd5_matches_xodr(rd5_path: Path, xodr_path: Path) -> bool:
    try:
        text = rd5_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False
    original = ""
    for line in text.splitlines()[:40]:
        if "Original File:" in line:
            original = line.split("Original File:", 1)[1].strip()
            break
    if not original:
        return rd5_path.stat().st_mtime >= xodr_path.stat().st_mtime
    original_norm = original.replace("\\\\", "\\").replace("\\", "/").lower()
    xodr_norm = str(xodr_path.resolve()).replace("\\", "/").lower()
    return original_norm == xodr_norm


def write_routes_to_project_rd5(base_rd5_path: Path, routes: list, project_dir: Path, report_dir: Path) -> tuple[Path, dict[str, str]]:
    if write_rd5_with_route is None or Rd5Road is None:
        raise RuntimeError(f"Could not import RD5 route writer: {TRAFFICGEN_IMPORT_ERROR}")

    road_dir = project_dir / "Data" / "Road"
    road_dir.mkdir(parents=True, exist_ok=True)
    current_path = base_rd5_path
    route_ids: dict[str, str] = {}
    route_names = {route.name for route in routes}
    bundle_hash = short_hash("\n".join(sorted(route_names)))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for index, route in enumerate(routes, start=1):
        rd5 = Rd5Road.load(current_path)
        known = route_ids_from_rd5(rd5, route_names)
        route_ids.update(known)
        if route.name in route_ids:
            continue
        output_path = road_dir / f"{shorten_stem(base_rd5_path.stem)}_with_routes_{bundle_hash}_{stamp}_{index:02d}.rd5"
        result = write_rd5_with_route(rd5, route, output_path, route_name=route.name)
        route_ids[route.name] = result.route_id
        report_path = report_dir / f"rd5_route_{shorten_stem(route.name, 40)}.md"
        report_path.write_text(result.report, encoding="utf-8")
        current_path = result.output_path

    final_rd5 = Rd5Road.load(current_path)
    route_ids.update(route_ids_from_rd5(final_rd5, route_names))
    return current_path, route_ids


def build_ego_traffic_testrun(analysis: dict, export_dir: Path, *, run_name: str | None = None) -> ScenarioBuildResult:
    ensure_roadgen_ready()
    project_dir = DEFAULT_PROJECT_ROOT
    report_dir = APP_DIR / "exports" / safe_name(analysis.get("projectName") or "video_road") / datetime.now().strftime(
        "%Y%m%d_%H%M%S_testrun"
    )
    report_dir.mkdir(parents=True, exist_ok=True)

    base_rd5_path = convert_and_decorate_rd5(export_dir, analysis, project_dir)
    package = RoadPackage.load(export_dir)
    ego_route, traffic_route = build_default_routes(package, analysis)
    routes = [ego_route]
    if traffic_route.name != ego_route.name:
        routes.append(traffic_route)

    route_rd5_path, route_ids = write_routes_to_project_rd5(base_rd5_path, routes, project_dir, report_dir)
    missing = [route.name for route in routes if route.name not in route_ids]
    if missing:
        raise RoadPackageError(f"Missing CarMaker route ObjId for: {', '.join(missing)}")

    testrun_dir = project_dir / "Data" / "TestRun"
    testrun_dir.mkdir(parents=True, exist_ok=True)
    scenario_name = shorten_stem(run_name or f"{safe_name(analysis.get('projectName') or 'video_road')}_ego_traffic", 80)
    road_ref = project_road_reference(project_dir, route_rd5_path)  # type: ignore[misc]

    traffic_start = min(max(traffic_route.total_length * 0.12, 8.0), max(8.0, traffic_route.total_length - 5.0))
    if traffic_route.name == ego_route.name:
        traffic_start = min(max(ego_route.total_length * 0.42, 35.0), max(35.0, ego_route.total_length - 10.0))

    ego = EgoPlan(  # type: ignore[operator]
        enabled=True,
        route_name=ego_route.name,
        vehicle_model=DEFAULT_EGO_MODEL,
        driver_template=DEFAULT_EGO_DRIVER,
        speed_kmh=float((analysis.get("ego") or {}).get("speedKmh") or 35.0),
        start_s=0.0,
        lane_offset=0.0,
    )
    traffic = [
        VehiclePlan(  # type: ignore[operator]
            name="TrafficCar_1",
            route_name=traffic_route.name,
            model=DEFAULT_TRAFFIC_MODEL,
            driver_model=DEFAULT_TRAFFIC_DRIVER,
            speed_kmh=25.0,
            start_s=traffic_start,
            lane_offset=0.0,
            start_delay_s=0.0,
            control_mode="ipg_driver",
        )
    ]
    route_lengths = {ego_route.name: ego_route.total_length, traffic_route.name: traffic_route.total_length}
    config = TestRunConfig(  # type: ignore[operator]
        scenario_name=scenario_name,
        road_file_ref=road_ref,
        route_ids=route_ids,
        ego=ego,
        traffic=traffic,
        route_lengths=route_lengths,
        duration_s=1000.0,
    )
    testrun_result = write_testrun(config, testrun_dir / scenario_name)  # type: ignore[misc]
    (report_dir / "testrun_project_report.md").write_text(testrun_result.report, encoding="utf-8")
    write_json(
        report_dir / "video2map_scenario.json",
        {
            "export_dir": str(export_dir),
            "base_rd5": str(base_rd5_path),
            "route_rd5": str(route_rd5_path),
            "testrun": str(testrun_result.output_path),
            "ego_route": ego_route.name,
            "traffic_route": traffic_route.name,
            "route_ids": route_ids,
        },
    )
    update_pipeline_settings(export_dir, {"project": export_dir.name})
    settings = read_json(PIPELINE_SETTINGS)
    settings["rd5"] = str(route_rd5_path)
    settings["scenario"] = scenario_name
    write_json(PIPELINE_SETTINGS, settings)

    xodr_path = next(export_dir.glob("*.xodr"))
    return ScenarioBuildResult(
        export_dir=export_dir,
        xodr_path=xodr_path,
        rd5_path=route_rd5_path,
        testrun_path=testrun_result.output_path,
        report_dir=report_dir,
        ego_route_name=ego_route.name,
        traffic_route_name=traffic_route.name,
        route_ids=route_ids,
    )


def probe_python(command: list[str]) -> tuple[tuple[int, int], str] | None:
    probe_script = "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}'); print(sys.executable)"
    try:
        completed = subprocess.run(
            [*command, "-c", probe_script],
            capture_output=True,
            text=True,
            timeout=8,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    try:
        major_text, minor_text = lines[0].split(".", 1)
        version = (int(major_text), int(minor_text))
    except ValueError:
        return None
    return version, lines[1]


def find_cmapi_python() -> tuple[list[str] | None, str]:
    env_value = os.environ.get("CARMAKER_CMAPI_PYTHON", "").strip()
    candidates: list[list[str]] = []
    if env_value:
        env_path = Path(env_value.strip('"'))
        if env_path.exists():
            candidates.append([str(env_path)])
        else:
            candidates.append([part.strip('"') for part in shlex.split(env_value, posix=False)])
    candidates.extend([[sys.executable], ["py", "-3.13"], ["py", "-3.12"], ["py", "-3.11"], ["py", "-3.10"], ["py", "-3.9"]])
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        local_python_root = Path(local_appdata) / "Programs" / "Python"
        for minor in (13, 12, 11, 10, 9):
            candidates.append([str(local_python_root / f"Python3{minor}" / "python.exe")])
    candidates.append(["python"])

    seen: set[tuple[str, ...]] = set()
    for candidate in candidates:
        if not candidate:
            continue
        key = tuple(candidate)
        if key in seen:
            continue
        seen.add(key)
        probe = probe_python(candidate)
        if not probe:
            continue
        version, executable = probe
        major, minor = version
        if major == 3 and 9 <= minor <= 13:
            return candidate, f"{executable} (Python {major}.{minor})"
    return None, ""


def run_carmaker(
    testrun_path: Path,
    project_dir: Path = DEFAULT_PROJECT_ROOT,
    *,
    factor: float = 5.0,
    movie_backend: str = "ipgmovie",
    movie_ready_delay: float | None = None,
) -> tuple[int, Path, str]:
    runner = TRAFFICGEN_DIR / "carmaker_5x_runner.py"
    if not runner.exists():
        raise RuntimeError(f"CMAPI runner script was not found: {runner}")
    if not DEFAULT_CARMAKER_HOME.exists():
        raise RuntimeError(f"CarMaker home was not found: {DEFAULT_CARMAKER_HOME}")
    python_cmd, python_label = find_cmapi_python()
    if not python_cmd:
        raise RuntimeError(
            "CarMaker runner needs Python 3.9-3.13 for CMAPI/APO wheels. "
            "Install Python 3.13/3.12 or set CARMAKER_CMAPI_PYTHON."
        )

    config_dir = project_dir / "Data" / "Config"
    config_dir.mkdir(parents=True, exist_ok=True)
    factor_label = str(factor).replace(".", "p")
    movie_label = safe_name(movie_backend or "ipgmovie")
    if movie_ready_delay is None:
        movie_ready_delay = DEFAULT_MOVIENX_READY_DELAY if movie_backend == "movienx" else DEFAULT_IPGMOVIE_READY_DELAY
    log_path = (
        config_dir
        / f"video2map_cmapi_{factor_label}x_{movie_label}_{safe_name(testrun_path.name)}_{datetime.now():%Y%m%d_%H%M%S}.log"
    )
    args = [
        *python_cmd,
        str(runner),
        "--project",
        str(project_dir),
        "--testrun",
        str(testrun_path),
        "--cm-home",
        str(DEFAULT_CARMAKER_HOME),
        "--factor",
        str(factor),
        "--movie-backend",
        movie_backend,
        "--movie-ready-delay",
        str(movie_ready_delay),
        "--keep-movie-open",
    ]
    with log_path.open("w", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            args,
            cwd=str(TRAFFICGEN_DIR),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
    return proc.pid, log_path, python_label


class Video2MapApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Video2Map RoadGen Assistant")
        self.geometry("1180x760")
        self.minsize(980, 640)

        self.video_var = tk.StringVar(value=str(default_video_path()))
        self.project_var = tk.StringVar(value="accident_case_video")
        self.sample_count_var = tk.IntVar(value=7)
        self.status_var = tk.StringVar(value="Ready")
        self.frames: FrameExtraction | None = None
        self.analysis: dict | None = None
        self.last_export_dir: Path | None = None
        self.last_scenario: ScenarioBuildResult | None = None
        self.preview_image = None

        self._build_ui()
        self.load_local_draft()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="ns")
        right = ttk.Frame(self, padding=(0, 10, 10, 10))
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        ttk.Label(left, text="Video").grid(row=0, column=0, sticky="w")
        video_entry = ttk.Entry(left, textvariable=self.video_var, width=46)
        video_entry.grid(row=1, column=0, sticky="ew", pady=(4, 2))
        ttk.Button(left, text="Browse Video", command=self.browse_video).grid(row=2, column=0, sticky="ew", pady=2)

        ttk.Label(left, text="Project name").grid(row=3, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(left, textvariable=self.project_var, width=32).grid(row=4, column=0, sticky="ew", pady=(4, 2))

        ttk.Label(left, text="Frame samples").grid(row=5, column=0, sticky="w", pady=(12, 0))
        ttk.Spinbox(left, from_=3, to=20, textvariable=self.sample_count_var, width=10).grid(
            row=6, column=0, sticky="w", pady=(4, 2)
        )

        ttk.Button(left, text="Extract Frames", command=self.extract_frames).grid(row=7, column=0, sticky="ew", pady=(12, 2))
        ttk.Button(left, text="Load Default Draft", command=self.load_local_draft).grid(row=8, column=0, sticky="ew", pady=2)
        ttk.Button(left, text="Prepare Codex Review", command=self.prepare_codex_review).grid(
            row=9, column=0, sticky="ew", pady=2
        )
        ttk.Button(left, text="Load Codex Result", command=self.load_codex_result).grid(
            row=10, column=0, sticky="ew", pady=2
        )

        ttk.Separator(left).grid(row=11, column=0, sticky="ew", pady=14)
        ttk.Button(left, text="Generate RoadGen Export", command=self.generate_export).grid(
            row=12, column=0, sticky="ew", pady=2
        )
        ttk.Button(left, text="Generate Ego + Traffic TestRun", command=self.generate_ego_traffic).grid(
            row=13, column=0, sticky="ew", pady=2
        )
        ttk.Button(left, text="Generate + Run CarMaker (5x)", command=lambda: self.generate_and_run_carmaker(5.0)).grid(
            row=14, column=0, sticky="ew", pady=2
        )
        ttk.Button(
            left,
            text="Generate + Run CarMaker (5x + MovieNX)",
            command=lambda: self.generate_and_run_carmaker(5.0, "movienx"),
        ).grid(
            row=15, column=0, sticky="ew", pady=2
        )
        ttk.Button(left, text="Open Pipeline App", command=self.open_pipeline).grid(row=16, column=0, sticky="ew", pady=2)

        self.preview_label = ttk.Label(left, text="No frames extracted yet.", anchor="center")
        self.preview_label.grid(row=17, column=0, sticky="nsew", pady=(16, 4))
        left.rowconfigure(17, weight=1)

        top = ttk.Frame(right)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        ttk.Label(top, textvariable=self.status_var).grid(row=0, column=0, sticky="w")

        self.graph_text = tk.Text(right, wrap="none", undo=True, font=("Consolas", 10))
        self.graph_text.grid(row=1, column=0, sticky="nsew", pady=(8, 8))

        bottom = ttk.Frame(right)
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        self.log_text = tk.Text(bottom, height=8, wrap="word", font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="ew")

    def browse_video(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select video",
            initialdir=str(WORKSPACE),
            filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")],
        )
        if selected:
            self.video_var.set(selected)

    def extract_frames(self) -> None:
        try:
            video = Path(self.video_var.get())
            project = slugify(self.project_var.get() or video.stem)
            output_dir = APP_DIR / "exports" / project / time.strftime("%Y%m%d_%H%M%S_frames")
            self.frames = extract_video_frames(video, output_dir, int(self.sample_count_var.get()))
            self.status_var.set(
                f"Extracted {len(self.frames.frame_paths)} frames from {self.frames.duration_s:.2f}s video"
            )
            self.log(
                f"Video: {self.frames.width}x{self.frames.height}, "
                f"{self.frames.frame_count} frames, {self.frames.fps:.2f} fps"
            )
            if self.frames.contact_sheet:
                self.show_preview(self.frames.contact_sheet)
                self.log(f"Contact sheet: {self.frames.contact_sheet}")
        except Exception as exc:
            messagebox.showerror("Extract Frames", str(exc))
            self.log(f"Extract Frames failed: {exc}")

    def show_preview(self, image_path: Path) -> None:
        try:
            from PIL import Image, ImageTk
        except ImportError:
            self.preview_label.configure(text=str(image_path))
            return
        image = Image.open(image_path)
        image.thumbnail((360, 420))
        self.preview_image = ImageTk.PhotoImage(image)
        self.preview_label.configure(image=self.preview_image, text="")

    def load_local_draft(self) -> None:
        self.analysis = local_draft_analysis(self.project_var.get())
        self.set_analysis_text(self.analysis)
        self.status_var.set("Loaded local draft graph")
        self.log("Loaded local draft graph. Edit JSON before generating if needed.")

    def prepare_codex_review(self) -> None:
        try:
            if self.frames is None:
                self.extract_frames()
            if self.frames is None:
                return
            analysis = self.read_analysis_text()
            project = safe_name(self.project_var.get() or analysis.get("projectName") or "video_road")
            package_dir = APP_DIR / "exports" / project / datetime.now().strftime("%Y%m%d_%H%M%S_codex_review")
            frame_dir = package_dir / "frames"
            frame_dir.mkdir(parents=True, exist_ok=True)

            copied_frames = []
            for frame_path in self.frames.frame_paths:
                target = frame_dir / frame_path.name
                shutil.copy2(frame_path, target)
                copied_frames.append(str(target))
            contact_sheet = ""
            if self.frames.contact_sheet and self.frames.contact_sheet.exists():
                target = package_dir / self.frames.contact_sheet.name
                shutil.copy2(self.frames.contact_sheet, target)
                contact_sheet = str(target)

            request = {
                "version": 1,
                "source": "video2map_app",
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "goal": (
                    "Review sampled video frames and improve the RoadGen graph plus TrafficGen intent. "
                    "Prefer a simple CarMaker-valid approximation over survey-grade reconstruction. "
                    "For accident_case_video, keep the ego topology as a south-to-west left turn: "
                    "E1/E2/E3 must be four-lane ego-route edges, the ego must not change lanes after the intersection, "
                    "and no north-west exit road may be added."
                ),
                "video_path": str(self.frames.video_path),
                "contact_sheet": contact_sheet,
                "frame_paths": copied_frames,
                "current_analysis": analysis,
                "expected_result_file": str(package_dir / "video2map_ai_result.json"),
                "result_format": {
                    "projectName": "string",
                    "summary": "string",
                    "confidence": "number 0..1",
                    "assumptions": ["string"],
                    "graph": {"nodes": "RoadGen nodes", "edges": "RoadGen edges"},
                    "hardConstraints": {
                        "accidentCaseSouthToWest4Lane": True,
                        "egoRouteEdges": ["E1", "E2", "E3"],
                        "egoRouteNumLanes": 4,
                        "egoRouteLaneIndex": 3,
                        "egoAllowLaneChanges": False,
                        "noNorthwestRoad": True,
                    },
                    "ego": {
                        "description": "string",
                        "routeHintEdges": ["edge id"],
                        "startNode": "node id",
                        "goalNode": "node id",
                        "speedKmh": "number",
                    },
                    "trafficHints": ["optional vehicle/pedestrian hints"],
                },
            }
            request_path = package_dir / "codex_review_request.json"
            write_json(request_path, request)
            self.status_var.set(f"Prepared Codex review: {package_dir.name}")
            self.log(f"Codex review request: {request_path}")
            self.log("Ask Codex to review this package, then use Load Codex Result.")
            messagebox.showinfo(
                "Prepare Codex Review",
                "Prepared a review package for Codex.\n"
                f"Request: {request_path}\n\n"
                "Tell Codex to review this package and write video2map_ai_result.json.",
            )
        except Exception as exc:
            messagebox.showerror("Prepare Codex Review", str(exc))
            self.log(f"Prepare Codex Review failed: {exc}")

    def load_codex_result(self) -> None:
        try:
            project = safe_name(self.project_var.get() or "video_road")
            search_root = APP_DIR / "exports" / project
            candidates = sorted(
                search_root.glob("*_codex_review/video2map_ai_result.json"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                selected = candidates[0]
            else:
                selected_text = filedialog.askopenfilename(
                    initialdir=str(search_root if search_root.exists() else APP_DIR),
                    title="Select Codex result JSON",
                    filetypes=[("Codex result", "video2map_ai_result.json"), ("JSON files", "*.json"), ("All files", "*.*")],
                )
                if not selected_text:
                    return
                selected = Path(selected_text)
            analysis = normalize_analysis(read_json(selected), self.project_var.get())
            self.analysis = analysis
            self.set_analysis_text(analysis)
            self.status_var.set(f"Loaded Codex result: {selected.parent.name}")
            self.log(f"Loaded Codex result: {selected}")
        except Exception as exc:
            messagebox.showerror("Load Codex Result", str(exc))
            self.log(f"Load Codex Result failed: {exc}")

    def set_analysis_text(self, analysis: dict) -> None:
        self.graph_text.delete("1.0", tk.END)
        self.graph_text.insert(tk.END, json.dumps(analysis, ensure_ascii=False, indent=2))

    def read_analysis_text(self) -> dict:
        text = self.graph_text.get("1.0", tk.END).strip()
        if not text:
            raise RuntimeError("Graph JSON is empty.")
        return normalize_analysis(json.loads(text), self.project_var.get())

    def generate_export(self) -> None:
        try:
            analysis = self.read_analysis_text()
            result, export_dir = generate_roadgen_export(analysis)
            self.analysis = analysis
            self.last_export_dir = export_dir
            self.status_var.set(f"Generated RoadGen export: {export_dir.name}")
            self.log(f"RoadGen export: {export_dir}")
            self.log(f"XODR: {next(export_dir.glob('*.xodr'), '')}")
            self.log("Pipeline settings were updated to this export.")
            messagebox.showinfo("Generate RoadGen Export", f"Generated:\n{export_dir}")
        except Exception as exc:
            messagebox.showerror("Generate RoadGen Export", str(exc))
            self.status_var.set("RoadGen export failed")
            self.log(f"RoadGen export failed: {exc}")

    def ensure_export(self) -> tuple[dict, Path]:
        analysis = self.read_analysis_text()
        if self.last_export_dir and self.last_export_dir.exists():
            existing_graph = self.last_export_dir / "video2map_analysis.json"
            if existing_graph.exists():
                try:
                    existing = normalize_analysis(read_json(existing_graph), self.project_var.get())
                    if existing.get("graph") == analysis.get("graph"):
                        return analysis, self.last_export_dir
                except Exception:
                    pass
        _, export_dir = generate_roadgen_export(analysis)
        self.analysis = analysis
        self.last_export_dir = export_dir
        self.log(f"RoadGen export: {export_dir}")
        return analysis, export_dir

    def generate_ego_traffic(self) -> ScenarioBuildResult | None:
        try:
            analysis, export_dir = self.ensure_export()
            self.status_var.set("Generating RD5 routes and TestRun...")
            self.update_idletasks()
            scenario = build_ego_traffic_testrun(analysis, export_dir)
            self.last_scenario = scenario
            self.status_var.set(f"Generated TestRun: {scenario.testrun_path.name}")
            self.log(f"Route-enabled RD5 copy: {scenario.rd5_path}")
            self.log(f"TestRun: {scenario.testrun_path}")
            self.log(f"Ego route: {scenario.ego_route_name}")
            self.log(f"Traffic route: {scenario.traffic_route_name}")
            self.log(f"Report dir: {scenario.report_dir}")
            messagebox.showinfo(
                "Generate Ego + Traffic TestRun",
                "Generated CarMaker files.\n"
                f"RD5: {scenario.rd5_path}\n"
                f"TestRun: {scenario.testrun_path}",
            )
            return scenario
        except Exception as exc:
            messagebox.showerror("Generate Ego + Traffic TestRun", str(exc))
            self.status_var.set("TestRun generation failed")
            self.log(f"TestRun generation failed: {exc}")
            return None

    def generate_and_run_carmaker(self, factor: float = 5.0, movie_backend: str = "ipgmovie") -> None:
        scenario = self.last_scenario
        if scenario is None or not scenario.testrun_path.exists():
            scenario = self.generate_ego_traffic()
        if scenario is None:
            return
        try:
            movie_ready_delay = (
                DEFAULT_MOVIENX_READY_DELAY if movie_backend == "movienx" else DEFAULT_IPGMOVIE_READY_DELAY
            )
            pid, log_path, python_label = run_carmaker(
                scenario.testrun_path,
                DEFAULT_PROJECT_ROOT,
                factor=factor,
                movie_backend=movie_backend,
                movie_ready_delay=movie_ready_delay,
            )
            self.status_var.set(f"Started CarMaker runner pid {pid}")
            self.log(
                f"Started CarMaker {factor:g}x runner ({movie_backend}, movie wait {movie_ready_delay:g}s): pid {pid}"
            )
            self.log(f"CMAPI Python: {python_label}")
            self.log(f"Run log: {log_path}")
        except Exception as exc:
            messagebox.showerror("Generate + Run CarMaker", str(exc))
            self.status_var.set("CarMaker run failed")
            self.log(f"CarMaker run failed: {exc}")

    def open_pipeline(self) -> None:
        try:
            if not PIPELINE_RUNNER.exists():
                raise RuntimeError(f"Pipeline runner not found: {PIPELINE_RUNNER}")
            subprocess.Popen([str(PIPELINE_RUNNER)], cwd=str(PIPELINE_DIR))
            self.log(f"Opened pipeline app: {PIPELINE_RUNNER}")
        except Exception as exc:
            messagebox.showerror("Open Pipeline App", str(exc))
            self.log(f"Open Pipeline App failed: {exc}")

    def log(self, message: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{stamp}] {message}\n")
        self.log_text.see(tk.END)


def cli_main(args: argparse.Namespace) -> int:
    video = Path(args.video or default_video_path())
    project = slugify(args.project or video.stem or "video_road")
    frames_dir = APP_DIR / "exports" / project / time.strftime("%Y%m%d_%H%M%S_frames")
    frames = extract_video_frames(video, frames_dir, args.samples)
    analysis = local_draft_analysis(project)

    if args.generate:
        result, export_dir = generate_roadgen_export(analysis)
        payload = {"frames": str(frames.output_dir), "export": str(export_dir), "roadgen": result}
        if args.testrun:
            scenario = build_ego_traffic_testrun(analysis, export_dir)
            payload["scenario"] = {
                "rd5": str(scenario.rd5_path),
                "testrun": str(scenario.testrun_path),
                "report_dir": str(scenario.report_dir),
            }
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps({"frames": str(frames.output_dir), "analysis": analysis}, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Video to RoadGen graph assistant")
    parser.add_argument("--video", type=Path, help="Input video path")
    parser.add_argument("--project", default="accident_case_video", help="RoadGen project name")
    parser.add_argument("--samples", type=int, default=7, help="Number of frames to sample")
    parser.add_argument("--generate", action="store_true", help="Generate a RoadGen export after analysis")
    parser.add_argument("--testrun", action="store_true", help="Generate ego + traffic CarMaker TestRun after export")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.generate or args.video or args.testrun:
        raise SystemExit(cli_main(args))
    app = Video2MapApp()
    app.mainloop()


if __name__ == "__main__":
    main()
