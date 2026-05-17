from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import random
import re
from xml.etree import ElementTree as ET


class EnvironmentError(RuntimeError):
    pass


@dataclass
class CityEnvironmentResult:
    rd5_path: Path
    objects_added: int
    links_used: int
    seed: int
    building_density: float = 1.0
    sidewalk_bumps: int = 0
    tree_strips: int = 0
    pedestrian_lanes: int = 0
    pedestrian_lane_widths: int = 0
    pedestrian_lane_materials: int = 0


@dataclass
class SafetyMarginResult:
    rd5_path: Path
    links_used: int
    sidewalk_bumps: int
    shoulder_width: float
    sidewalk_width: float


@dataclass
class IntersectionDecorationResult:
    rd5_path: Path
    traffic_light_nodes: int
    crosswalk_nodes: int
    approach_links: int
    signal_objects: int
    crosswalk_markings: int
    crosswalk_stop_markers: int = 0
    traffic_light_stop_markers: int = 0
    traffic_light_stop_lines: int = 0
    traffic_light_phase_fixes: int = 0


@dataclass
class LinkRef:
    index: int
    rl_id: int
    length: float
    yaw: float
    x0: float
    y0: float
    x1: float
    y1: float
    odr_road_id: str | None = None


@dataclass
class RoadSegment:
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class BuildingSpec:
    model: str
    radius: float
    z_offset: float


@dataclass
class PlacedBuilding:
    x: float
    y: float
    radius: float


@dataclass(frozen=True)
class SidewalkBumpRef:
    link: LinkRef
    bump_type: str
    side_param: str


@dataclass(frozen=True)
class TrafficLightNode:
    node_id: str
    x: float
    y: float


@dataclass(frozen=True)
class GraphEdgeRef:
    x0: float
    y0: float
    x1: float
    y1: float
    lanes: int


@dataclass(frozen=True)
class IntersectionApproach:
    node: TrafficLightNode
    link: LinkRef
    at_end: bool
    lane_count: int


@dataclass(frozen=True)
class LanePathRef:
    lane_path_id: str
    lane_object_id: str
    direction_sign: int
    side: str
    lane_index: int
    width: float


@dataclass(frozen=True)
class ImportedTrfLightMountRef:
    control_id: int
    s: float
    t: float


CITY_BEGIN = "# RoadGen City Environment BEGIN"
CITY_END = "# RoadGen City Environment END"
SAFETY_BEGIN = "# RoadGen Safety Margins BEGIN"
SAFETY_END = "# RoadGen Safety Margins END"
INTERSECTION_BEGIN = "# RoadGen Intersection Decorations BEGIN"
INTERSECTION_END = "# RoadGen Intersection Decorations END"
CITY_TERRAIN = "3D/Terrain/CityRuralHighway.obj.gz"
DEFAULT_CARMAKER_ROOT = Path(r"C:\IPG\carmaker")
DEFAULT_ROAD_BUFFER = 9.0
DEFAULT_BUILDING_GAP = 3.0
DEFAULT_SHOULDER_WIDTH = 0.8
DEFAULT_SIDEWALK_WIDTH = 2.2
SAFETY_ROADSIDE_PADDING = 0.4
CITY_DENSITY_MIN = 0.5
CITY_DENSITY_MAX = 32.0
CITY_BUILDING_SLOT_MULTIPLIER = 1.6
CITY_MAX_BUILDING_ROWS = 5
MIN_BUILDING_SPACING_SCALE = 0.035
BUILDING_PARALLEL_YAW_JITTER_DEG = 2.0
CITY_BUILDING_Z_OFFSET_SCALE = 0.75
CITY_ROADSIDE_VISUAL_WIDTH = (
    DEFAULT_SHOULDER_WIDTH + DEFAULT_SIDEWALK_WIDTH + SAFETY_ROADSIDE_PADDING
)
CITY_ROADSIDE_VISUAL_SLOPE = 0.3
CITY_PEDESTRIAN_LANES_ENABLED = False
CITY_PEDESTRIAN_LANE_MIN_WIDTH = 0.5
CITY_PEDESTRIAN_LANE_MAX_WIDTH = 2.6
CITY_PEDESTRIAN_LANE_TARGET_WIDTH = 2.5
CITY_PEDESTRIAN_LANE_MATERIAL_ENABLED = False
CITY_PEDESTRIAN_LANE_MATERIAL = "Textures/Ground/Pavement_01.mtex 0 0 0 0 1 1 1 1 0 0 0"
CITY_SIDEWALK_BUMP_ENABLED = True
CITY_SIDEWALK_TEXTURE = "Textures/Ground/Roadside_Sidewalk.png"
CITY_SHOULDER_WIDTH = DEFAULT_SHOULDER_WIDTH
CITY_SIDEWALK_WIDTH = DEFAULT_SIDEWALK_WIDTH
CITY_SIDEWALK_EDGE_DROP = -0.02
CITY_SIDEWALK_CURB_HEIGHT = 0.12
CITY_SIDEWALK_SURFACE_HEIGHT = 0.15
CITY_SIDEWALK_START_EXTENSION = 10.0
CITY_SIDEWALK_END_EXTENSION = 10.0
CITY_TREE_STRIP_ENABLED = True
CITY_TREE_STRIP_LATERAL_OFFSET = 5.0
CITY_TREE_STRIP_WIDTH = 4.0
CITY_TREE_STRIP_DENSITY = 35.0
CITY_TREE_STRIP_MIN_LENGTH = 16.0
CITY_TREE_STRIP_END_MARGIN = 6.0
CITY_TREE_STRIP_SCALE_X = 1.0
CITY_TREE_STRIP_SCALE_Y = 1.0
CITY_TREE_STRIP_RANDOM_X = 0.5
CITY_TREE_STRIP_RANDOM_Y = 0.5
INTERSECTION_NODE_MATCH_RADIUS = 12.0
INTERSECTION_MIN_LINK_LENGTH = 18.0
INTERSECTION_CROSSWALK_SETBACK = 5.5
INTERSECTION_CROSSWALK_STRIPES = 5
INTERSECTION_CROSSWALK_STRIPE_WIDTH = 0.48
INTERSECTION_CROSSWALK_STRIPE_PITCH = 0.82
INTERSECTION_CROSSWALK_LANE_WIDTH = 3.5
INTERSECTION_CROSSWALK_EXTRA_WIDTH = 0.4
INTERSECTION_MARKING_LANE_EDGE_MARGIN = 0.12
INTERSECTION_STOP_LINE_TO_CROSSWALK_GAP = 2.8
INTERSECTION_CROSSWALK_STOP_MARKERS_ENABLED = True
INTERSECTION_CROSSWALK_PED_WATCH_DISTANCE = 18.0
INTERSECTION_SIGNAL_SETBACK = 2.6
INTERSECTION_SIGNAL_SIDE_CLEARANCE = 1.05
INTERSECTION_SIGNAL_SCALE = 1.0
INTERSECTION_MAX_SIGNAL_APPROACHES_PER_NODE = 1
INTERSECTION_SIGNAL_MODEL = "3D/StreetFurniture/HAWK_Signal_Composition_2_Lane.mobj"
# Dynamic TrfLight/DrvStop markers can keep CarMaker 15 stuck in
# Preprocessing when generated from incomplete synthetic junction metadata.
# Keep visual signal objects and crosswalk markings enabled by default, and
# add dynamic traffic control only after the controller graph is validated.
INTERSECTION_DYNAMIC_SIGNALS_ENABLED = False
INTERSECTION_SIGNAL_GREEN_SECONDS = 18.0
INTERSECTION_SIGNAL_RED_SECONDS = 45.0
INTERSECTION_STOP_MARKER_SETBACK = 4.2
INTERSECTION_ATTACH_IMPORTED_TRFLIGHT_STOPS_ENABLED = True
INTERSECTION_NORMALIZE_IMPORTED_TRFLIGHT_PHASES_ENABLED = True
INTERSECTION_IMPORTED_TRFLIGHT_INITIAL_PHASE = 3
INTERSECTION_SIGNAL_STOP_LINE_MARKINGS_ENABLED = True
INTERSECTION_SIGNAL_STOP_LINE_WIDTH = 0.45
INTERSECTION_SIGNAL_STOP_MARKER_MOUNT_OFFSET = 0.0
TRAFFIC_LIGHT_NODE_TYPES = {"traffic_light", "traffic_light_crosswalk"}
CROSSWALK_NODE_TYPES = {"traffic_light_crosswalk", "crosswalk"}
MAX_CITY_ATTEMPTS_PER_SLOT = 28
RLT_MARGIN = "5"
RLT_PEDESTRIAN = "11"

CITY_BUILDING_MODELS = [
    "3D/Buildings/Office_01.mobj",
    "3D/Buildings/Office_02.mobj",
    "3D/Buildings/Office_03.mobj",
    "3D/Buildings/Office_04.mobj",
    "3D/Buildings/Office_06.mobj",
    "3D/Buildings/Office_08.mobj",
    "3D/Buildings/Office_10_7St_1.mobj",
    "3D/Buildings/Office_11_5St_1.mobj",
    "3D/Buildings/Office_12_8St_1.mobj",
    "3D/Buildings/Neoclassical_01.mobj",
    "3D/Buildings/Neoclassical_02.mobj",
    "3D/Buildings/Neoclassical_03.mobj",
    "3D/Buildings/Neoclassical_04.mobj",
    "3D/Buildings/FamilyHouse_00_1.mobj",
    "3D/Buildings/FamilyHouse_01_1.mobj",
    "3D/Buildings/FamilyHouse_02_1.mobj",
    "3D/Buildings/FamilyHouse_03.mobj",
    "3D/Buildings/FireStation_01.mobj",
    "3D/Buildings/GasStation_01.mobj",
]

FLOAT_RE = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?"
N_OBJECTS_RE = re.compile(r"^nObjects\s*=\s*(\d+)\s*$")
MAX_OBJ_RE = re.compile(r"^MaxUsedObjId\s*=\s*(\d+)\s*$")
LINK_RL_RE = re.compile(r"^Link\.(\d+)\.RL\.ID\s*=\s*(\d+)\s*$")
LINK_TYPE_RE = re.compile(r"^Link\.(\d+)\.Seg\.0\.Type\s*=\s*(\w+)\s*$")
LINK_PARAM_RE = re.compile(rf"^Link\.(\d+)\.Seg\.0\.Param\s*=\s*({FLOAT_RE})\b")
LINK_NODE0_RE = re.compile(rf"^Link\.(\d+)\.Node0\s*=\s*({FLOAT_RE})\s+({FLOAT_RE})\s+({FLOAT_RE})")
LINK_NODE1_RE = re.compile(rf"^Link\.(\d+)\.Node1\s*=\s*({FLOAT_RE})\s+({FLOAT_RE})\s+({FLOAT_RE})")
LINK_TAG_RE = re.compile(r"^Link\.(\d+)\.Tag\s*=\s*odrRoadId:([^\s]+)\s*$")
ANY_NODE0_RE = re.compile(rf"^(?:Link\.\d+|Junction\.\d+\.Link\.\d+)\.Node0\s*=\s*({FLOAT_RE})\s+({FLOAT_RE})\s+({FLOAT_RE})")
ANY_NODE1_RE = re.compile(rf"^(?:Link\.\d+|Junction\.\d+\.Link\.\d+)\.Node1\s*=\s*({FLOAT_RE})\s+({FLOAT_RE})\s+({FLOAT_RE})")
GEO_ID_RE = re.compile(r"^RL\.(\d+)\.GeoObject\.(\d+)\.ID\s*=\s*(\d+)\s+(\d+)\s*$")
BUMP_ID_RE = re.compile(r"^RL\.(\d+)\.Bump\.(\d+)\.ID\s*=\s*(\d+)\s+(\d+)\s*$")
TREESTRIP_ID_RE = re.compile(r"^RL\.(\d+)\.TreeStrip\.(\d+)\.ID\s*=\s*(\d+)\s+(\d+)\s*$")
ROADMARKING_ID_RE = re.compile(r"^RL\.(\d+)\.RoadMarking\.(\d+)\.ID\s*=\s*(\d+)\s+(\d+)\s*$")
MARKER_ID_RE = re.compile(r"^RL\.(\d+)\.Marker\.(\d+)\.ID\s*=\s*(\d+)\s+(\d+)\s*$")
MOUNT_ID_RE = re.compile(r"^RL\.(\d+)\.Mount\.(\d+)\.ID\s*=\s*(\d+)\s+(\d+)\s*$")
MOUNT_CHILD_ID_RE = re.compile(r"^RL\.(\d+)\.Mount\.(\d+)\.(\d+)\.ID\s*=\s*(\d+)\s*$")
MOUNT_CHILD_VALUE_RE = re.compile(
    rf"^RL\.(\d+)\.Mount\.(\d+)\.(\d+)\s*=\s*1\s+(\d+)\s+({FLOAT_RE})\s+({FLOAT_RE})\b"
)
CONTROL_TRFLIGHT_RE = re.compile(r"^Control\.TrfLight\.(\d+)\s*=\s*(\d+)\s+")
CONTROL_TRFLIGHT_LINE_RE = re.compile(
    r'^(Control\.TrfLight\.\d+\s*=\s*)(\d+)(\s+\S+\s+(?:"[^"]*"|\S+)\s+)(\d+)(\s+.*)$'
)
MARKER_TYPE_RE = re.compile(r"^RL\.(\d+)\.Marker\.(\d+)\.Type\s*=\s*(\w+)\s*$")
MARKER_PARAM_RE = re.compile(
    rf"^RL\.(\d+)\.Marker\.(\d+)\.Param\s*=\s*"
    rf"({FLOAT_RE})\s+({FLOAT_RE})\s+(-?\d+)\s+(-?\d+)\s+(\d+)\b"
)
ANY_ID_RE = re.compile(r"\.ID\s*=\s*(\d+)\b")
LINK_VISUALIZATION_RE = re.compile(r"^Link\.(\d+)\.Visualization\.(RoadsideWidth|RoadsideSlope)\s*=")
LINK_VISUALIZATION_VALUE_RE = re.compile(
    rf"^Link\.(\d+)\.Visualization\.(RoadsideWidth|RoadsideSlope)\s*="
    rf"\s*({FLOAT_RE})\s+({FLOAT_RE})\s*$"
)
LANE_DEF_RE = re.compile(
    r"^(?P<key>(?:Link\.(?P<link>\d+)|Junction\.\d+\.Link\.\d+)"
    r"\.LaneSection\.\d+\.Lane[LR]\.\d+)\s*=\s*(?P<lane_type>\d+)(?P<rest>(?:\s+.*)?)$"
)
LANE_WIDTH_HEADER_RE = re.compile(
    r"^(?P<key>(?:Link\.\d+|Junction\.\d+\.Link\.\d+)"
    r"\.LaneSection\.\d+\.Lane[LR]\.\d+)\.Width\.Points:\s*$"
)
LANE_MATERIAL_RE = re.compile(
    r"^(?P<key>(?:Link\.\d+|Junction\.\d+\.Link\.\d+)"
    r"\.LaneSection\.\d+\.Lane[LR]\.\d+)\.Material\.0\s*="
)
LINK_LANE_ID_RE = re.compile(r"^Link\.(\d+)\.LaneSection\.\d+\.Lane([RL])\.(\d+)\.ID\s*=\s*(\d+)")
LINK_LANE_VALUE_RE = re.compile(r"^Link\.(\d+)\.LaneSection\.\d+\.Lane([RL])\.(\d+)\s*=\s*(\d+)\b")
LINK_LANE_WIDTH_POINTS_RE = re.compile(r"^Link\.(\d+)\.LaneSection\.\d+\.Lane([RL])\.(\d+)\.Width\.Points:")
LINK_LANE_WIDTH_POINT_RE = re.compile(rf"^\s*\d+\s+(\d+)\s+\S+\s+\S+\s+({FLOAT_RE})\b")
LANE_PATH_RE = re.compile(r"^LanePath\.(\d+)\s*=\s*(\d+)\s+(\d+)\b")
BBOX_RE = re.compile(rf"^Geometry\.Bbox\s*=\s*({FLOAT_RE})\s+({FLOAT_RE})\s+({FLOAT_RE})\s+({FLOAT_RE})\s+({FLOAT_RE})\s+({FLOAT_RE})")


def _stable_seed(value: str | int | None) -> int:
    if isinstance(value, int):
        return value
    text = value or "roadgen-city"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _format_number(value: float) -> str:
    if abs(value) < 0.0005:
        value = 0.0
    return f"{value:.3f}".rstrip("0").rstrip(".") or "0"


def _format_pair(value: float) -> str:
    text = _format_number(value)
    return f"{text} {text}"


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1").splitlines()


def _find_movie_root() -> Path | None:
    if not DEFAULT_CARMAKER_ROOT.exists():
        return None
    candidates = sorted(DEFAULT_CARMAKER_ROOT.glob("win64-*"), key=lambda path: path.name, reverse=True)
    for candidate in candidates:
        movie = candidate / "Movie"
        if movie.exists():
            return movie
    return None


def _patch_scalar(lines: list[str], key: str, value: int | str) -> None:
    prefix = f"{key} ="
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{key} = {value}"
            return
    lines.append(f"{key} = {value}")


def _set_or_insert_after(lines: list[str], key: str, value: str, after_prefix: str) -> None:
    prefix = f"{key} ="
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{key} = {value}"
            return

    insert_at = None
    for index, line in enumerate(lines):
        if line.startswith(after_prefix):
            insert_at = index + 1
    if insert_at is None:
        lines.append(f"{key} = {value}")
    else:
        lines.insert(insert_at, f"{key} = {value}")


def _strip_generated_block(lines: list[str], begin_marker: str, end_marker: str) -> tuple[list[str], int]:
    stripped: list[str] = []
    in_block = False
    removed_objects = 0
    for line in lines:
        if line == begin_marker:
            in_block = True
            continue
        if line == end_marker:
            in_block = False
            continue
        if in_block:
            if (
                GEO_ID_RE.match(line)
                or BUMP_ID_RE.match(line)
                or TREESTRIP_ID_RE.match(line)
                or ROADMARKING_ID_RE.match(line)
                or MARKER_ID_RE.match(line)
                or MOUNT_ID_RE.match(line)
                or MOUNT_CHILD_ID_RE.match(line)
                or CONTROL_TRFLIGHT_RE.match(line)
            ):
                removed_objects += 1
            continue
        stripped.append(line)
    return stripped, removed_objects


def _strip_existing_city(lines: list[str]) -> tuple[list[str], int]:
    return _strip_generated_block(lines, CITY_BEGIN, CITY_END)


def _strip_existing_safety(lines: list[str]) -> tuple[list[str], int]:
    return _strip_generated_block(lines, SAFETY_BEGIN, SAFETY_END)


def _strip_existing_intersections(lines: list[str]) -> tuple[list[str], int]:
    return _strip_generated_block(lines, INTERSECTION_BEGIN, INTERSECTION_END)


def _strip_generated_city_terrain(lines: list[str]) -> list[str]:
    generated_terrain_lines = {
        f"Movie.TerrainFName = {CITY_TERRAIN}",
        f"Visualization.TerrainFName = {CITY_TERRAIN}",
    }
    cleaned: list[str] = []
    for line in lines:
        if line in generated_terrain_lines:
            continue
        if line == "Visualization.RoadsideWidth = 80 80":
            cleaned.append("Visualization.RoadsideWidth = 0 0")
            continue
        if line == "Visualization.RoadsideSlope = 0.01 0.01":
            cleaned.append("Visualization.RoadsideSlope = 1 1")
            continue
        cleaned.append(line)
    return cleaned


def _parse_lane_widths(lines: list[str]) -> dict[str, float]:
    widths: dict[str, float] = {}
    for index, line in enumerate(lines):
        match = LANE_WIDTH_HEADER_RE.match(line)
        if not match:
            continue

        key = match.group("key")
        for point_line in lines[index + 1 :]:
            stripped = point_line.strip()
            if not stripped:
                break
            tokens = stripped.split()
            if len(tokens) < 5:
                break
            try:
                widths[key] = float(tokens[4])
            except ValueError:
                pass
            break
    return widths


def _format_lane_width_point(line: str, width: float) -> str:
    prefix = line[: len(line) - len(line.lstrip())]
    tokens = line.strip().split()
    if len(tokens) >= 5:
        tokens[4] = _format_number(width)
    return prefix + " ".join(tokens)


def _patch_pedestrian_lane_widths(lines: list[str], lane_keys: set[str]) -> int:
    changed_keys: set[str] = set()
    current_key: str | None = None
    for index, line in enumerate(lines):
        if match := LANE_WIDTH_HEADER_RE.match(line):
            key = match.group("key")
            current_key = key if key in lane_keys else None
            continue
        if not current_key:
            continue

        stripped = line.strip()
        if not stripped:
            current_key = None
            continue
        tokens = stripped.split()
        if len(tokens) < 5:
            current_key = None
            continue
        try:
            current_width = float(tokens[4])
        except ValueError:
            current_key = None
            continue
        if abs(current_width - CITY_PEDESTRIAN_LANE_TARGET_WIDTH) > 0.001:
            lines[index] = _format_lane_width_point(line, CITY_PEDESTRIAN_LANE_TARGET_WIDTH)
            changed_keys.add(current_key)
    return len(changed_keys)


def _patch_pedestrian_lane_materials(lines: list[str], lane_keys: set[str]) -> int:
    if not CITY_PEDESTRIAN_LANE_MATERIAL_ENABLED:
        return 0

    existing = {match.group("key") for line in lines if (match := LANE_MATERIAL_RE.match(line))}
    added = 0
    patched: list[str] = []
    for line in lines:
        patched.append(line)
        match = LANE_DEF_RE.match(line)
        if not match:
            continue
        key = match.group("key")
        if key not in lane_keys or key in existing:
            continue
        patched.append(f"{key}.Material.0 = {CITY_PEDESTRIAN_LANE_MATERIAL}")
        existing.add(key)
        added += 1
    lines[:] = patched
    return added


def _patch_pedestrian_lanes(lines: list[str]) -> tuple[int, int, int]:
    if not CITY_PEDESTRIAN_LANES_ENABLED:
        return 0, 0, 0

    widths = _parse_lane_widths(lines)
    converted = 0
    pedestrian_keys: set[str] = set()
    for index, line in enumerate(lines):
        match = LANE_DEF_RE.match(line)
        if not match:
            continue

        key = match.group("key")
        lane_type = match.group("lane_type")
        width = widths.get(key)
        if width is None:
            continue
        if not (CITY_PEDESTRIAN_LANE_MIN_WIDTH <= width <= CITY_PEDESTRIAN_LANE_MAX_WIDTH):
            continue
        if lane_type not in {RLT_MARGIN, RLT_PEDESTRIAN}:
            continue

        pedestrian_keys.add(key)
        if lane_type == RLT_MARGIN:
            lines[index] = f"{key} = {RLT_PEDESTRIAN}{match.group('rest')}"
            converted += 1
    widened = _patch_pedestrian_lane_widths(lines, pedestrian_keys)
    materials = _patch_pedestrian_lane_materials(lines, pedestrian_keys)
    return converted, widened, materials


def _parse_int_scalar(lines: list[str], regex: re.Pattern[str], default: int = 0) -> int:
    for line in lines:
        match = regex.match(line)
        if match:
            return int(match.group(1))
    return default


def _max_object_id_in_lines(lines: list[str]) -> int:
    max_id = 0
    for line in lines:
        match = ANY_ID_RE.search(line)
        if match:
            max_id = max(max_id, int(match.group(1)))
        control_match = CONTROL_TRFLIGHT_RE.match(line)
        if control_match:
            max_id = max(max_id, int(control_match.group(2)))
    return max_id


def _parse_existing_geo_indices(lines: list[str]) -> dict[int, int]:
    result: dict[int, int] = {}
    for line in lines:
        match = GEO_ID_RE.match(line)
        if not match:
            continue
        rl_id = int(match.group(1))
        geo_index = int(match.group(2))
        result[rl_id] = max(result.get(rl_id, -1), geo_index)
    return result


def _parse_existing_bump_indices(lines: list[str]) -> dict[int, int]:
    result: dict[int, int] = {}
    for line in lines:
        match = BUMP_ID_RE.match(line)
        if not match:
            continue
        rl_id = int(match.group(1))
        bump_index = int(match.group(2))
        result[rl_id] = max(result.get(rl_id, -1), bump_index)
    return result


def _parse_existing_tree_strip_indices(lines: list[str]) -> dict[int, int]:
    result: dict[int, int] = {}
    for line in lines:
        match = TREESTRIP_ID_RE.match(line)
        if not match:
            continue
        rl_id = int(match.group(1))
        strip_index = int(match.group(2))
        result[rl_id] = max(result.get(rl_id, -1), strip_index)
    return result


def _parse_existing_roadmarking_indices(lines: list[str]) -> dict[int, int]:
    result: dict[int, int] = {}
    for line in lines:
        match = ROADMARKING_ID_RE.match(line)
        if not match:
            continue
        rl_id = int(match.group(1))
        marking_index = int(match.group(2))
        result[rl_id] = max(result.get(rl_id, -1), marking_index)
    return result


def _parse_existing_marker_indices(lines: list[str]) -> dict[int, int]:
    result: dict[int, int] = {}
    for line in lines:
        match = MARKER_ID_RE.match(line)
        if not match:
            continue
        rl_id = int(match.group(1))
        marker_index = int(match.group(2))
        result[rl_id] = max(result.get(rl_id, -1), marker_index)
    return result


def _parse_existing_mount_indices(lines: list[str]) -> dict[int, int]:
    result: dict[int, int] = {}
    for line in lines:
        match = MOUNT_ID_RE.match(line)
        if not match:
            continue
        rl_id = int(match.group(1))
        mount_index = int(match.group(2))
        result[rl_id] = max(result.get(rl_id, -1), mount_index)
    return result


def _parse_next_traffic_light_control_index(lines: list[str]) -> int:
    max_index = -1
    for line in lines:
        match = CONTROL_TRFLIGHT_RE.match(line)
        if match:
            max_index = max(max_index, int(match.group(1)))
    return max_index + 1


def _parse_imported_trflight_controls_by_rl(lines: list[str]) -> dict[int, list[ImportedTrfLightMountRef]]:
    control_ids = {int(match.group(2)) for line in lines if (match := CONTROL_TRFLIGHT_RE.match(line))}
    result: dict[int, list[ImportedTrfLightMountRef]] = {}
    seen: dict[int, set[int]] = {}
    for line in lines:
        match = MOUNT_CHILD_VALUE_RE.match(line)
        if not match:
            continue
        rl_id = int(match.group(1))
        control_id = int(match.group(4))
        if control_id not in control_ids:
            continue
        if control_id in seen.setdefault(rl_id, set()):
            continue
        seen[rl_id].add(control_id)
        result.setdefault(rl_id, []).append(
            ImportedTrfLightMountRef(
                control_id=control_id,
                s=float(match.group(5)),
                t=float(match.group(6)),
            )
        )
    return result


def _parse_existing_trflight_stop_lane_paths(lines: list[str]) -> set[tuple[int, str]]:
    marker_lanes: dict[tuple[int, int], str] = {}
    marker_types: dict[tuple[int, int], str] = {}
    marker_stop_types: dict[tuple[int, int], str] = {}
    for line in lines:
        if match := MARKER_ID_RE.match(line):
            marker_lanes[(int(match.group(1)), int(match.group(2)))] = match.group(4)
            continue
        if match := MARKER_TYPE_RE.match(line):
            marker_types[(int(match.group(1)), int(match.group(2)))] = match.group(3)
            continue
        if match := MARKER_PARAM_RE.match(line):
            marker_stop_types[(int(match.group(1)), int(match.group(2)))] = match.group(7)

    result: set[tuple[int, str]] = set()
    for key, lane_path_id in marker_lanes.items():
        if marker_types.get(key) == "DrvStop" and marker_stop_types.get(key) == "2":
            result.add((key[0], lane_path_id))
    return result


def _patch_imported_trflight_initial_phases(
    lines: list[str],
    controls_by_rl: dict[int, list[ImportedTrfLightMountRef]],
) -> int:
    if not INTERSECTION_NORMALIZE_IMPORTED_TRFLIGHT_PHASES_ENABLED:
        return 0
    mounted_control_ids = {ref.control_id for refs in controls_by_rl.values() for ref in refs}
    if not mounted_control_ids:
        return 0

    phase = str(INTERSECTION_IMPORTED_TRFLIGHT_INITIAL_PHASE)
    changed = 0
    for index, line in enumerate(lines):
        match = CONTROL_TRFLIGHT_LINE_RE.match(line)
        if not match:
            continue
        control_id = int(match.group(2))
        initial_phase = match.group(4)
        if control_id not in mounted_control_ids or initial_phase != "0":
            continue
        lines[index] = f"{match.group(1)}{match.group(2)}{match.group(3)}{phase}{match.group(5)}"
        changed += 1
    return changed


def _parse_lane_paths_by_link(lines: list[str]) -> dict[int, list[LanePathRef]]:
    lane_objects_by_link: dict[int, set[str]] = {}
    lane_type_by_key: dict[tuple[int, str, int], str] = {}
    lane_object_by_key: dict[tuple[int, str, int], str] = {}
    lane_direction_by_object: dict[str, int] = {}
    lane_meta_by_object: dict[str, tuple[str, int]] = {}
    lane_width_by_object: dict[str, float] = {}
    lane_paths_by_object: dict[str, list[LanePathRef]] = {}
    width_lane_object_id: str | None = None

    for line in lines:
        if match := LINK_LANE_VALUE_RE.match(line):
            lane_type_by_key[(int(match.group(1)), match.group(2), int(match.group(3)))] = match.group(4)
            width_lane_object_id = None
            continue
        if match := LINK_LANE_ID_RE.match(line):
            side = match.group(2)
            lane_index = int(match.group(3))
            lane_object_id = match.group(4)
            lane_object_by_key[(int(match.group(1)), side, lane_index)] = lane_object_id
            lane_direction_by_object[lane_object_id] = -1 if side == "L" else 1
            lane_meta_by_object[lane_object_id] = (side, lane_index)
            width_lane_object_id = None
            continue
        if match := LINK_LANE_WIDTH_POINTS_RE.match(line):
            width_lane_object_id = lane_object_by_key.get((int(match.group(1)), match.group(2), int(match.group(3))))
            continue
        if width_lane_object_id and (match := LINK_LANE_WIDTH_POINT_RE.match(line)):
            if match.group(1) == width_lane_object_id:
                lane_width_by_object[width_lane_object_id] = max(0.1, float(match.group(2)))
            continue
        if match := LANE_PATH_RE.match(line):
            lane_object_id = match.group(3)
            side, lane_index = lane_meta_by_object.get(lane_object_id, ("R", 0))
            lane_path = LanePathRef(
                lane_path_id=match.group(2),
                lane_object_id=lane_object_id,
                direction_sign=lane_direction_by_object.get(lane_object_id, 1),
                side=side,
                lane_index=lane_index,
                width=lane_width_by_object.get(lane_object_id, INTERSECTION_CROSSWALK_LANE_WIDTH),
            )
            lane_paths_by_object.setdefault(lane_path.lane_object_id, []).append(lane_path)
            width_lane_object_id = None

    for key, lane_object_id in lane_object_by_key.items():
        link_index, side, _lane_index = key
        if lane_type_by_key.get(key) != "0":
            continue
        lane_objects_by_link.setdefault(link_index, set()).add(lane_object_id)

    result: dict[int, list[LanePathRef]] = {}
    for link_index, lane_objects in lane_objects_by_link.items():
        refs: list[LanePathRef] = []
        for lane_object_id in sorted(
            lane_objects,
            key=lambda value: (*lane_meta_by_object.get(value, ("R", 0)), int(value)),
        ):
            refs.extend(lane_paths_by_object.get(lane_object_id, []))
        if refs:
            result[link_index] = refs
    return result


def _parse_existing_link_visualization(lines: list[str]) -> set[tuple[int, str]]:
    result: set[tuple[int, str]] = set()
    for line in lines:
        match = LINK_VISUALIZATION_RE.match(line)
        if match:
            result.add((int(match.group(1)), match.group(2)))
    return result


def _patch_roadside_visualization_width(lines: list[str], links: list[LinkRef]) -> int:
    link_indices = {link.index for link in links}
    if not link_indices or CITY_ROADSIDE_VISUAL_WIDTH <= 0:
        return 0

    changed = 0
    target = _format_pair(CITY_ROADSIDE_VISUAL_WIDTH)
    for index, line in enumerate(lines):
        match = LINK_VISUALIZATION_VALUE_RE.match(line)
        if not match or match.group(2) != "RoadsideWidth":
            continue
        link_index = int(match.group(1))
        if link_index not in link_indices:
            continue
        left_width = float(match.group(3))
        right_width = float(match.group(4))
        if min(left_width, right_width) >= CITY_ROADSIDE_VISUAL_WIDTH - 0.001:
            continue
        lines[index] = f"Link.{link_index}.Visualization.RoadsideWidth = {target}"
        changed += 1
    return changed


def _parse_links(lines: list[str]) -> list[LinkRef]:
    raw: dict[int, dict[str, float | int | str]] = {}
    for line in lines:
        if match := LINK_RL_RE.match(line):
            raw.setdefault(int(match.group(1)), {})["rl_id"] = int(match.group(2))
            continue
        if match := LINK_TYPE_RE.match(line):
            raw.setdefault(int(match.group(1)), {})["type"] = match.group(2)
            continue
        if match := LINK_PARAM_RE.match(line):
            raw.setdefault(int(match.group(1)), {})["length"] = float(match.group(2))
            continue
        if match := LINK_NODE0_RE.match(line):
            raw.setdefault(int(match.group(1)), {})["x0"] = float(match.group(2))
            raw.setdefault(int(match.group(1)), {})["y0"] = float(match.group(3))
            raw.setdefault(int(match.group(1)), {})["yaw"] = float(match.group(4))
            continue
        if match := LINK_NODE1_RE.match(line):
            raw.setdefault(int(match.group(1)), {})["x1"] = float(match.group(2))
            raw.setdefault(int(match.group(1)), {})["y1"] = float(match.group(3))
            continue
        if match := LINK_TAG_RE.match(line):
            raw.setdefault(int(match.group(1)), {})["odr_road_id"] = match.group(2)

    links: list[LinkRef] = []
    for index, item in raw.items():
        if item.get("type") != "Straight":
            continue
        rl_id = item.get("rl_id")
        length = item.get("length")
        yaw = item.get("yaw")
        x0 = item.get("x0")
        y0 = item.get("y0")
        x1 = item.get("x1")
        y1 = item.get("y1")
        if (
            not isinstance(rl_id, int)
            or not isinstance(length, float)
            or not isinstance(yaw, float)
            or not isinstance(x0, float)
            or not isinstance(y0, float)
            or not isinstance(x1, float)
            or not isinstance(y1, float)
        ):
            continue
        odr_road_id = item.get("odr_road_id")
        links.append(
            LinkRef(
                index=index,
                rl_id=rl_id,
                length=length,
                yaw=yaw % 360.0,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                odr_road_id=str(odr_road_id) if odr_road_id is not None else None,
            )
        )
    return sorted(links, key=lambda item: item.index)


def _parse_road_segments(lines: list[str]) -> list[RoadSegment]:
    starts: list[tuple[float, float]] = []
    segments: list[RoadSegment] = []
    for line in lines:
        if match := ANY_NODE0_RE.match(line):
            starts.append((float(match.group(1)), float(match.group(2))))
            continue
        if match := ANY_NODE1_RE.match(line):
            if not starts:
                continue
            x0, y0 = starts.pop()
            x1 = float(match.group(1))
            y1 = float(match.group(2))
            if math.hypot(x1 - x0, y1 - y0) >= 0.25:
                segments.append(RoadSegment(x0=x0, y0=y0, x1=x1, y1=y1))
    return segments


def _link_geometry_key(link: LinkRef) -> tuple[tuple[int, int], tuple[int, int]]:
    a = (round(link.x0 * 10), round(link.y0 * 10))
    b = (round(link.x1 * 10), round(link.y1 * 10))
    return tuple(sorted([a, b]))  # type: ignore[return-value]


def _unique_links(links: list[LinkRef]) -> list[LinkRef]:
    unique: list[LinkRef] = []
    seen: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for link in links:
        key = _link_geometry_key(link)
        if key in seen:
            continue
        seen.add(key)
        unique.append(link)
    return unique


def _load_graph(graph_path: Path | None, graph: dict | None = None) -> dict:
    if graph is not None:
        return graph.get("graph", graph)
    if graph_path is None:
        return {}
    graph_path = Path(graph_path)
    if not graph_path.exists():
        return {}
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    return data.get("graph", data)


def _nodes_from_graph_types(graph: dict, node_types: set[str]) -> list[TrafficLightNode]:
    nodes: list[TrafficLightNode] = []
    for node in graph.get("nodes") or []:
        if str(node.get("type", "")).lower() not in node_types:
            continue
        try:
            nodes.append(
                TrafficLightNode(
                    node_id=str(node.get("id") or f"TL{len(nodes)}"),
                    x=float(node.get("x", 0.0)),
                    y=float(node.get("y", 0.0)),
                )
            )
        except (TypeError, ValueError):
            continue
    return nodes


def _traffic_light_nodes_from_graph(graph: dict) -> list[TrafficLightNode]:
    return _nodes_from_graph_types(graph, TRAFFIC_LIGHT_NODE_TYPES)


def _crosswalk_nodes_from_graph(graph: dict) -> list[TrafficLightNode]:
    return _nodes_from_graph_types(graph, CROSSWALK_NODE_TYPES)


def _graph_edges_from_graph(graph: dict) -> list[GraphEdgeRef]:
    node_lookup: dict[str, tuple[float, float]] = {}
    for node in graph.get("nodes") or []:
        node_id = str(node.get("id") or "")
        if not node_id:
            continue
        try:
            node_lookup[node_id] = (float(node.get("x", 0.0)), float(node.get("y", 0.0)))
        except (TypeError, ValueError):
            continue

    refs: list[GraphEdgeRef] = []
    for edge in graph.get("edges") or []:
        start = node_lookup.get(str(edge.get("from") or ""))
        end = node_lookup.get(str(edge.get("to") or ""))
        if not start or not end:
            continue
        try:
            lanes = max(1, int(edge.get("numLanes", 1)))
        except (TypeError, ValueError):
            lanes = 1
        refs.append(GraphEdgeRef(x0=start[0], y0=start[1], x1=end[0], y1=end[1], lanes=lanes))
    return refs


def _endpoint_pair_distance(
    ax0: float,
    ay0: float,
    ax1: float,
    ay1: float,
    bx0: float,
    by0: float,
    bx1: float,
    by1: float,
) -> float:
    forward = math.hypot(ax0 - bx0, ay0 - by0) + math.hypot(ax1 - bx1, ay1 - by1)
    reverse = math.hypot(ax0 - bx1, ay0 - by1) + math.hypot(ax1 - bx0, ay1 - by0)
    return min(forward, reverse)


def _lane_count_for_link(link: LinkRef, graph_edges: list[GraphEdgeRef]) -> int:
    best_lanes = 1
    best_distance = float("inf")
    for edge in graph_edges:
        distance = _endpoint_pair_distance(
            link.x0,
            link.y0,
            link.x1,
            link.y1,
            edge.x0,
            edge.y0,
            edge.x1,
            edge.y1,
        )
        if distance < best_distance:
            best_distance = distance
            best_lanes = edge.lanes
    if best_distance > INTERSECTION_NODE_MATCH_RADIUS * 2.5:
        return 1
    return max(1, best_lanes)


def _near_traffic_light_endpoint(
    link: LinkRef,
    node: TrafficLightNode,
    *,
    radius: float,
) -> tuple[bool, float] | None:
    distance_to_start = math.hypot(link.x0 - node.x, link.y0 - node.y)
    distance_to_end = math.hypot(link.x1 - node.x, link.y1 - node.y)
    best = min(distance_to_start, distance_to_end)
    if best > radius:
        return None
    return distance_to_end <= distance_to_start, best


def _xodr_approach_road_refs(
    xodr_path: Path | None,
    traffic_light_nodes: list[TrafficLightNode],
) -> dict[str, list[tuple[str, bool]]]:
    if xodr_path is None:
        return {}
    xodr_path = Path(xodr_path)
    if not xodr_path.exists():
        return {}

    try:
        root = ET.parse(xodr_path).getroot()
    except ET.ParseError:
        return {}

    wanted_names = {node.node_id for node in traffic_light_nodes}
    junction_name_by_id: dict[str, str] = {}
    for junction in root.findall("junction"):
        name = junction.attrib.get("name", "")
        junction_id = junction.attrib.get("id", "")
        if name in wanted_names and junction_id:
            junction_name_by_id[junction_id] = name

    refs: dict[str, list[tuple[str, bool]]] = {node.node_id: [] for node in traffic_light_nodes}
    if not junction_name_by_id:
        return refs

    for road in root.findall("road"):
        if road.attrib.get("junction", "-1") != "-1":
            continue
        road_id = road.attrib.get("id")
        if not road_id:
            continue
        link = road.find("link")
        if link is None:
            continue
        predecessor = link.find("predecessor")
        successor = link.find("successor")
        if predecessor is not None and predecessor.attrib.get("elementType") == "junction":
            node_id = junction_name_by_id.get(predecessor.attrib.get("elementId", ""))
            if node_id:
                refs.setdefault(node_id, []).append((road_id, False))
        if successor is not None and successor.attrib.get("elementType") == "junction":
            node_id = junction_name_by_id.get(successor.attrib.get("elementId", ""))
            if node_id:
                refs.setdefault(node_id, []).append((road_id, True))
    return refs


def _xodr_lane_counts(xodr_path: Path | None) -> dict[str, int]:
    if xodr_path is None:
        return {}
    xodr_path = Path(xodr_path)
    if not xodr_path.exists():
        return {}
    try:
        root = ET.parse(xodr_path).getroot()
    except ET.ParseError:
        return {}

    counts: dict[str, int] = {}
    for road in root.findall("road"):
        road_id = road.attrib.get("id")
        if not road_id:
            continue
        max_count = 0
        for lane_section in road.findall("lanes/laneSection"):
            count = 0
            for side in ("left", "right"):
                for lane in lane_section.findall(f"{side}/lane"):
                    if lane.attrib.get("type") == "driving":
                        count += 1
            max_count = max(max_count, count)
        if max_count:
            counts[road_id] = max_count
    return counts


def _approaches_from_xodr_refs(
    links: list[LinkRef],
    traffic_light_nodes: list[TrafficLightNode],
    graph_edges: list[GraphEdgeRef],
    road_refs: dict[str, list[tuple[str, bool]]],
    lane_counts: dict[str, int],
) -> list[IntersectionApproach]:
    if not road_refs:
        return []
    nodes_by_id = {node.node_id: node for node in traffic_light_nodes}
    links_by_road_id: dict[str, list[LinkRef]] = {}
    for link in links:
        if link.odr_road_id:
            links_by_road_id.setdefault(link.odr_road_id, []).append(link)

    approaches: list[IntersectionApproach] = []
    seen: set[tuple[str, int]] = set()
    for node_id, refs in road_refs.items():
        node = nodes_by_id.get(node_id)
        if node is None:
            continue
        for road_id, at_end in refs:
            if not at_end:
                continue
            for link in links_by_road_id.get(road_id, []):
                key = (node_id, link.rl_id)
                if key in seen:
                    continue
                seen.add(key)
                approaches.append(
                    IntersectionApproach(
                        node=node,
                        link=link,
                        at_end=at_end,
                        lane_count=max(1, lane_counts.get(road_id, _lane_count_for_link(link, graph_edges))),
                    )
                )
    return sorted(approaches, key=lambda item: (item.node.node_id, item.link.index))


def _approaches_for_traffic_lights(
    links: list[LinkRef],
    traffic_light_nodes: list[TrafficLightNode],
    graph_edges: list[GraphEdgeRef],
    *,
    radius: float = INTERSECTION_NODE_MATCH_RADIUS,
) -> list[IntersectionApproach]:
    grouped: dict[tuple[str, tuple[tuple[int, int], tuple[int, int]]], list[tuple[IntersectionApproach, float]]] = {}
    for node in traffic_light_nodes:
        for link in links:
            endpoint = _near_traffic_light_endpoint(link, node, radius=radius)
            if endpoint is None:
                continue
            at_end, distance = endpoint
            approach = IntersectionApproach(
                node=node,
                link=link,
                at_end=at_end,
                lane_count=_lane_count_for_link(link, graph_edges),
            )
            grouped.setdefault((node.node_id, _link_geometry_key(link)), []).append((approach, distance))

    approaches: list[IntersectionApproach] = []
    for items in grouped.values():
        items.sort(key=lambda item: (not item[0].at_end, item[1], item[0].link.index))
        approaches.append(items[0][0])
    return sorted(approaches, key=lambda item: (item.node.node_id, item.link.index))


def _sidewalk_bump_refs(links: list[LinkRef]) -> list[SidewalkBumpRef]:
    grouped: dict[tuple[tuple[int, int], tuple[int, int]], list[LinkRef]] = {}
    for link in links:
        grouped.setdefault(_link_geometry_key(link), []).append(link)

    refs: list[SidewalkBumpRef] = []
    for group in grouped.values():
        ordered = sorted(group, key=lambda item: item.index)
        if len(ordered) >= 2:
            # RoadGen two-way roads import as two opposite one-way links.
            # The right side of each directed link is the physical outside edge.
            for link in ordered:
                refs.append(SidewalkBumpRef(link=link, bump_type="LatProfileRSR", side_param="-1 1"))
        else:
            link = ordered[0]
            refs.append(SidewalkBumpRef(link=link, bump_type="LatProfileRSL", side_param="1 0"))
            refs.append(SidewalkBumpRef(link=link, bump_type="LatProfileRSR", side_param="-1 1"))
    return refs


def _model_objinfo_path(movie_root: Path, model: str) -> Path:
    return movie_root / model.replace(".mobj", ".objinfo")


def _load_building_specs(movie_root: Path | None) -> list[BuildingSpec]:
    specs: list[BuildingSpec] = []
    for model in CITY_BUILDING_MODELS:
        radius = 14.0
        z_offset = 0.0
        if movie_root:
            objinfo = _model_objinfo_path(movie_root, model)
            if objinfo.exists():
                for line in _read_lines(objinfo):
                    match = BBOX_RE.match(line)
                    if not match:
                        continue
                    xmin, xmax, ymin, ymax, zmin, _zmax = [float(match.group(i)) for i in range(1, 7)]
                    corners = [
                        (xmin, ymin),
                        (xmin, ymax),
                        (xmax, ymin),
                        (xmax, ymax),
                    ]
                    radius = max(6.0, max(math.hypot(x, y) for x, y in corners))
                    z_offset = max(0.0, -zmin * CITY_BUILDING_Z_OFFSET_SCALE)
                    break
        specs.append(BuildingSpec(model=model, radius=radius, z_offset=z_offset))
    return specs


def _link_point(link: LinkRef, s_pos: float, lateral: float) -> tuple[float, float]:
    angle = math.radians(link.yaw)
    along_x = math.cos(angle)
    along_y = math.sin(angle)
    left_x = -math.sin(angle)
    left_y = math.cos(angle)
    return link.x0 + along_x * s_pos + left_x * lateral, link.y0 + along_y * s_pos + left_y * lateral


def _point_segment_distance(x: float, y: float, segment: RoadSegment) -> float:
    vx = segment.x1 - segment.x0
    vy = segment.y1 - segment.y0
    wx = x - segment.x0
    wy = y - segment.y0
    length_sq = vx * vx + vy * vy
    if length_sq <= 1e-9:
        return math.hypot(x - segment.x0, y - segment.y0)
    ratio = max(0.0, min(1.0, (wx * vx + wy * vy) / length_sq))
    px = segment.x0 + ratio * vx
    py = segment.y0 + ratio * vy
    return math.hypot(x - px, y - py)


def _is_clear_of_roads(
    x: float,
    y: float,
    radius: float,
    segments: list[RoadSegment],
    road_buffer: float,
) -> bool:
    required = road_buffer + radius
    return all(_point_segment_distance(x, y, segment) >= required for segment in segments)


def _is_clear_of_buildings(
    x: float,
    y: float,
    radius: float,
    placed: list[PlacedBuilding],
    *,
    building_gap: float,
    spacing_scale: float,
) -> bool:
    return all(
        math.hypot(x - item.x, y - item.y) >= (radius + item.radius) * spacing_scale + building_gap
        for item in placed
    )


def _insertion_index(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if line.startswith("MaxUsedObjId ="):
            return index
    return len(lines)


def _building_count_for_link(length: float, rng: random.Random, density: float) -> int:
    if length < 30:
        base = 1
    elif length < 75:
        base = rng.choice([1, 1, 2])
    elif length < 120:
        base = rng.choice([2, 2, 3])
    else:
        base = rng.choice([3, 3, 4])
    return max(1, int(round(base * density * CITY_BUILDING_SLOT_MULTIPLIER)))


def _building_row_count(density: float) -> int:
    if density < 4.0:
        return 1
    return max(1, min(CITY_MAX_BUILDING_ROWS, 1 + int((density - 4.0) // 4.0)))


def _building_yaw_for_link(link: LinkRef, side: int, rng: random.Random) -> float:
    side_flip = 180.0 if side < 0 else 0.0
    jitter = rng.choice(
        [
            -BUILDING_PARALLEL_YAW_JITTER_DEG,
            0.0,
            BUILDING_PARALLEL_YAW_JITTER_DEG,
        ]
    )
    return (link.yaw + side_flip + jitter) % 360.0


def _building_lateral_extra(rng: random.Random, density: float) -> float:
    density = max(1.0, density)
    extra_min = max(0.8, 4.0 / density)
    extra_max = max(extra_min + 1.0, 12.0 / math.sqrt(density))
    return rng.uniform(extra_min, extra_max)


def _building_row_lateral_offset(row_index: int, radius: float, rng: random.Random) -> float:
    if row_index <= 0:
        return 0.0
    row_pitch = max(8.0, radius * 1.15)
    return row_index * row_pitch + rng.uniform(-1.5, 1.5)


def _city_roadside_visualization_lines(
    links: list[LinkRef],
    existing_visualization: set[tuple[int, str]],
) -> list[str]:
    if CITY_ROADSIDE_VISUAL_WIDTH <= 0:
        return []
    lines: list[str] = []
    width = _format_pair(CITY_ROADSIDE_VISUAL_WIDTH)
    slope = _format_pair(CITY_ROADSIDE_VISUAL_SLOPE)
    for link in links:
        if (link.index, "RoadsideWidth") not in existing_visualization:
            lines.append(f"Link.{link.index}.Visualization.RoadsideWidth = {width}")
        if (link.index, "RoadsideSlope") not in existing_visualization:
            lines.append(f"Link.{link.index}.Visualization.RoadsideSlope = {slope}")
    return lines


def _city_sidewalk_bump_lines(
    refs: list[SidewalkBumpRef],
    existing_bumps: dict[int, int],
    next_obj_id: int,
) -> tuple[list[str], int, int]:
    lines: list[str] = []
    added = 0
    for ref in refs:
        link = ref.link
        start_s = -CITY_SIDEWALK_START_EXTENSION
        end_s = max(1.0, link.length + CITY_SIDEWALK_END_EXTENSION)
        bump_index = existing_bumps.get(link.rl_id, -1) + 1
        existing_bumps[link.rl_id] = bump_index
        key = f"RL.{link.rl_id}.Bump.{bump_index}"
        lines.append(f"{key}.ID = {next_obj_id} {link.rl_id}")
        lines.append(f"{key}.Type = {ref.bump_type}")
        lines.append(
            f"{key}.Param = {_format_number(start_s)} 0 {_format_number(end_s)} 0 0 "
            f"{ref.side_param} 0.2 0 0.2 0 0"
        )
        lines.append(
            f"{key}.Material.0 = {CITY_SIDEWALK_TEXTURE} 0 0 0 0 0 0 1 0 0 0 0"
        )
        lines.append(f"{key}.Profile:")
        if CITY_SHOULDER_WIDTH > 0:
            lines.append(f"\t{_format_number(CITY_SHOULDER_WIDTH)} 0")
        else:
            lines.append(f"\t0.3 {_format_number(CITY_SIDEWALK_EDGE_DROP)}")
        lines.append(f"\t0.02 {_format_number(CITY_SIDEWALK_CURB_HEIGHT)}")
        lines.append(f"\t0.1 {_format_number(CITY_SIDEWALK_CURB_HEIGHT)}")
        lines.append(f"\t{_format_number(CITY_SIDEWALK_WIDTH)} {_format_number(CITY_SIDEWALK_SURFACE_HEIGHT)}")
        lines.append("\t0 0")
        next_obj_id += 1
        added += 1
    return lines, next_obj_id, added


def _city_tree_strip_lines(
    links: list[LinkRef],
    existing_strips: dict[int, int],
    next_obj_id: int,
    rng: random.Random,
) -> tuple[list[str], int, int]:
    if not CITY_TREE_STRIP_ENABLED:
        return [], next_obj_id, 0

    lines: list[str] = []
    added = 0
    for link in links:
        start_s = min(CITY_TREE_STRIP_END_MARGIN, max(0.0, link.length * 0.15))
        end_s = max(start_s, link.length - start_s)
        if end_s - start_s < CITY_TREE_STRIP_MIN_LENGTH:
            continue

        sides = [-1, 1]
        rng.shuffle(sides)
        for side in sides:
            strip_index = existing_strips.get(link.rl_id, -1) + 1
            existing_strips[link.rl_id] = strip_index
            key = f"RL.{link.rl_id}.TreeStrip.{strip_index}"
            lateral = side * CITY_TREE_STRIP_LATERAL_OFFSET
            density = CITY_TREE_STRIP_DENSITY * rng.uniform(0.75, 1.25)
            width = CITY_TREE_STRIP_WIDTH * rng.uniform(0.85, 1.15)
            lines.append(f"{key}.ID = {next_obj_id} {link.rl_id}")
            lines.append(
                "{key} = {start_s} 0 {end_s} 0 {lateral} {side} {density} {width} "
                "{scale_x} {scale_y} {random_x} {random_y}".format(
                    key=key,
                    start_s=_format_number(start_s),
                    end_s=_format_number(end_s),
                    lateral=_format_number(lateral),
                    side=side,
                    density=_format_number(density),
                    width=_format_number(width),
                    scale_x=_format_number(CITY_TREE_STRIP_SCALE_X),
                    scale_y=_format_number(CITY_TREE_STRIP_SCALE_Y),
                    random_x=_format_number(CITY_TREE_STRIP_RANDOM_X),
                    random_y=_format_number(CITY_TREE_STRIP_RANDOM_Y),
                )
            )
            next_obj_id += 1
            added += 1
    return lines, next_obj_id, added


def _approach_s_position(approach: IntersectionApproach, setback: float) -> float:
    link = approach.link
    if approach.at_end:
        return max(0.2, min(link.length - 0.2, link.length - setback))
    return max(0.2, min(link.length - 0.2, setback))


def _approach_half_road_width(approach: IntersectionApproach) -> float:
    lane_width = INTERSECTION_CROSSWALK_LANE_WIDTH
    return max(lane_width * 0.5, approach.lane_count * lane_width * 0.5 + INTERSECTION_CROSSWALK_EXTRA_WIDTH)


def _approach_lane_paths(
    approach: IntersectionApproach,
    lane_paths_by_link: dict[int, list[LanePathRef]],
    *,
    require_incoming: bool = False,
) -> list[LanePathRef]:
    lane_paths = lane_paths_by_link.get(approach.link.index, [])
    if not lane_paths:
        return []

    expected_direction = 1 if approach.at_end else -1
    matching = [lane_path for lane_path in lane_paths if lane_path.direction_sign == expected_direction]
    if require_incoming:
        return matching
    return matching or lane_paths


def _lane_lateral_bounds(
    lane_path: LanePathRef,
    all_lane_paths: list[LanePathRef],
) -> tuple[float, float] | None:
    side = lane_path.side
    lane_widths = {
        (item.side, item.lane_index): max(0.1, item.width)
        for item in all_lane_paths
    }
    width = lane_widths.get((side, lane_path.lane_index), max(0.1, lane_path.width))
    inner = 0.0
    for index in range(lane_path.lane_index):
        inner += lane_widths.get((side, index), width)
    outer = inner + width
    margin = min(INTERSECTION_MARKING_LANE_EDGE_MARGIN, max(0.0, width * 0.2))
    if outer - inner <= margin * 2.0:
        return None

    if side == "L":
        return inner + margin, outer - margin
    return -(outer - margin), -(inner + margin)


def _fallback_approach_lateral_bounds(approach: IntersectionApproach) -> tuple[float, float]:
    lane_width = INTERSECTION_CROSSWALK_LANE_WIDTH
    total_width = max(lane_width, approach.lane_count * lane_width)
    inner = INTERSECTION_MARKING_LANE_EDGE_MARGIN
    outer = max(inner + 0.6, total_width - INTERSECTION_MARKING_LANE_EDGE_MARGIN)
    if approach.at_end:
        return -outer, -inner
    return inner, outer


def _approach_lateral_spans(
    approach: IntersectionApproach,
    lane_paths_by_link: dict[int, list[LanePathRef]],
    *,
    require_incoming: bool = False,
) -> list[tuple[LanePathRef | None, float, float]]:
    all_lane_paths = lane_paths_by_link.get(approach.link.index, [])
    spans: list[tuple[LanePathRef | None, float, float]] = []
    for lane_path in _approach_lane_paths(
        approach,
        lane_paths_by_link,
        require_incoming=require_incoming,
    ):
        bounds = _lane_lateral_bounds(lane_path, all_lane_paths)
        if bounds is None:
            continue
        spans.append((lane_path, bounds[0], bounds[1]))
    if spans:
        return spans
    if require_incoming:
        return []

    t0, t1 = _fallback_approach_lateral_bounds(approach)
    return [(None, t0, t1)]


def _combined_lateral_span(
    spans: list[tuple[LanePathRef | None, float, float]]
) -> tuple[float, float] | None:
    if not spans:
        return None
    values: list[float] = []
    for _lane_path, t0, t1 in spans:
        values.extend([t0, t1])
    return min(values), max(values)


def _crosswalk_lateral_span(
    approach: IntersectionApproach,
    lane_paths_by_link: dict[int, list[LanePathRef]],
) -> tuple[float, float]:
    spans = _approach_lateral_spans(approach, lane_paths_by_link)
    values: list[float] = []
    for _lane_path, t0, t1 in spans:
        values.extend([t0, t1])

    default_extent = max(0.8, _approach_half_road_width(approach) - 0.25)
    lane_extent = max((abs(value) for value in values), default=default_extent)
    lateral_extent = max(default_extent, lane_extent)
    return lateral_extent, -lateral_extent


def _crosswalk_stripe_distances_from_node() -> list[float]:
    stripe_span = (INTERSECTION_CROSSWALK_STRIPES - 1) * INTERSECTION_CROSSWALK_STRIPE_PITCH
    base_distance = max(0.4, INTERSECTION_CROSSWALK_SETBACK - stripe_span / 2.0)
    return [base_distance + index * INTERSECTION_CROSSWALK_STRIPE_PITCH for index in range(INTERSECTION_CROSSWALK_STRIPES)]


def _crosswalk_far_distance_from_node() -> float:
    stripe_span = (INTERSECTION_CROSSWALK_STRIPES - 1) * INTERSECTION_CROSSWALK_STRIPE_PITCH
    return INTERSECTION_CROSSWALK_SETBACK + stripe_span / 2.0


def _crosswalk_band_width() -> float:
    stripe_span = (INTERSECTION_CROSSWALK_STRIPES - 1) * INTERSECTION_CROSSWALK_STRIPE_PITCH
    return max(INTERSECTION_CROSSWALK_STRIPE_WIDTH, stripe_span + INTERSECTION_CROSSWALK_STRIPE_WIDTH)


def _intersection_stop_line_s(approach: IntersectionApproach) -> float:
    return _approach_s_position(
        approach,
        _crosswalk_far_distance_from_node() + INTERSECTION_STOP_LINE_TO_CROSSWALK_GAP,
    )


def _append_transverse_road_marking(
    lines: list[str],
    key: str,
    object_id: int,
    owner_id: int,
    s_position: float,
    t0: float,
    t1: float,
    stripe_width: float,
    *,
    broken: bool = False,
) -> None:
    lines.append(f"{key}.ID = {object_id} {owner_id}")
    marking_style = "2 1 0 0.5 0.5" if broken else "1 1 0 2 4"
    lines.append(
        f"{key} = {_format_number(s_position)} 0 -10 1 0 0 "
        f"{_format_number(stripe_width)} 0 {marking_style} 1 1 0"
    )
    lines.append(f"{key}.Material.0 = white 0 0 0 0 0 0 0 0 0 0 0")
    lines.append(f"{key}.PointList:")
    lines.append(f"\t0 {_format_number(t0)}")
    lines.append(f"\t0 {_format_number(t1)}")


def _approach_node_distance(approach: IntersectionApproach) -> float:
    link = approach.link
    if approach.at_end:
        return math.hypot(link.x1 - approach.node.x, link.y1 - approach.node.y)
    return math.hypot(link.x0 - approach.node.x, link.y0 - approach.node.y)


def _select_signal_display_approaches(approaches: list[IntersectionApproach]) -> list[IntersectionApproach]:
    if INTERSECTION_MAX_SIGNAL_APPROACHES_PER_NODE <= 0:
        return []
    grouped: dict[str, list[IntersectionApproach]] = {}
    for approach in approaches:
        grouped.setdefault(approach.node.node_id, []).append(approach)
    selected: list[IntersectionApproach] = []
    for node_id in sorted(grouped):
        items = sorted(
            grouped[node_id],
            key=lambda item: (_approach_node_distance(item), item.link.index, 0 if item.at_end else 1),
        )
        selected.extend(items[:INTERSECTION_MAX_SIGNAL_APPROACHES_PER_NODE])
    return selected


def _intersection_crosswalk_lines(
    approaches: list[IntersectionApproach],
    existing_markings: dict[int, int],
    lane_paths_by_link: dict[int, list[LanePathRef]],
    next_obj_id: int,
) -> tuple[list[str], int, int]:
    lines: list[str] = []
    added = 0
    for approach in approaches:
        link = approach.link
        lateral_span = _crosswalk_lateral_span(approach, lane_paths_by_link)
        marking_index = existing_markings.get(link.rl_id, -1) + 1
        existing_markings[link.rl_id] = marking_index
        key = f"RL.{link.rl_id}.RoadMarking.{marking_index}"
        _append_transverse_road_marking(
            lines,
            key,
            next_obj_id,
            link.rl_id,
            _approach_s_position(approach, INTERSECTION_CROSSWALK_SETBACK),
            lateral_span[0],
            lateral_span[1],
            _crosswalk_band_width(),
            broken=True,
        )
        next_obj_id += 1
        added += 1
    return lines, next_obj_id, added


def _intersection_crosswalk_stop_marker_lines(
    approaches: list[IntersectionApproach],
    existing_markers: dict[int, int],
    lane_paths_by_link: dict[int, list[LanePathRef]],
    next_obj_id: int,
) -> tuple[list[str], int, int]:
    if not INTERSECTION_CROSSWALK_STOP_MARKERS_ENABLED:
        return [], next_obj_id, 0

    lines: list[str] = []
    added = 0
    for approach in approaches:
        link = approach.link
        marker_s = _intersection_stop_line_s(approach)
        for lane_path in _approach_lane_paths(approach, lane_paths_by_link, require_incoming=True):
            marker_index = existing_markers.get(link.rl_id, -1) + 1
            existing_markers[link.rl_id] = marker_index
            marker_key = f"RL.{link.rl_id}.Marker.{marker_index}"
            lines.append(f"{marker_key}.ID = {next_obj_id} {lane_path.lane_path_id}")
            lines.append(f"{marker_key}.Type = DrvStop")
            # RDST_Pedestrian (3): vehicles watch for pedestrians within the distance.
            lines.append(
                f"{marker_key}.Param = {_format_number(marker_s)} 0 {lane_path.direction_sign} "
                f"-1 3 {_format_number(INTERSECTION_CROSSWALK_PED_WATCH_DISTANCE)}"
            )
            next_obj_id += 1
            added += 1
    return lines, next_obj_id, added


def _trflight_stop_s(
    link: LinkRef,
    mount_ref: ImportedTrfLightMountRef,
    lane_path: LanePathRef,
) -> float:
    offset = max(0.0, INTERSECTION_SIGNAL_STOP_MARKER_MOUNT_OFFSET)
    if lane_path.direction_sign >= 0:
        value = mount_ref.s - offset
    else:
        value = mount_ref.s + offset
    return max(0.2, min(link.length - 0.2, value))


def _intersection_signal_stop_line_lines(
    approaches: list[IntersectionApproach],
    existing_markings: dict[int, int],
    controls_by_rl: dict[int, list[ImportedTrfLightMountRef]],
    lane_paths_by_link: dict[int, list[LanePathRef]],
    next_obj_id: int,
) -> tuple[list[str], int, int]:
    if not INTERSECTION_SIGNAL_STOP_LINE_MARKINGS_ENABLED:
        return [], next_obj_id, 0

    lines: list[str] = []
    added = 0
    emitted: set[tuple[int, float, float, float]] = set()
    for approach in approaches:
        link = approach.link
        mount_refs = controls_by_rl.get(link.rl_id, [])
        lateral_span = _combined_lateral_span(
            _approach_lateral_spans(approach, lane_paths_by_link, require_incoming=True)
        )
        if not mount_refs or lateral_span is None:
            continue

        stop_s = _intersection_stop_line_s(approach)
        stop_key = (link.rl_id, round(stop_s, 3), round(lateral_span[0], 3), round(lateral_span[1], 3))
        if stop_key in emitted:
            continue
        emitted.add(stop_key)

        marking_index = existing_markings.get(link.rl_id, -1) + 1
        existing_markings[link.rl_id] = marking_index
        key = f"RL.{link.rl_id}.RoadMarking.{marking_index}"
        _append_transverse_road_marking(
            lines,
            key,
            next_obj_id,
            link.rl_id,
            stop_s,
            lateral_span[0],
            lateral_span[1],
            INTERSECTION_SIGNAL_STOP_LINE_WIDTH,
        )
        next_obj_id += 1
        added += 1
    return lines, next_obj_id, added


def _imported_trflight_stop_marker_lines(
    approaches: list[IntersectionApproach],
    existing_markers: dict[int, int],
    lane_paths_by_link: dict[int, list[LanePathRef]],
    controls_by_rl: dict[int, list[ImportedTrfLightMountRef]],
    existing_trflight_stops: set[tuple[int, str]],
    next_obj_id: int,
) -> tuple[list[str], int, int]:
    if not INTERSECTION_ATTACH_IMPORTED_TRFLIGHT_STOPS_ENABLED:
        return [], next_obj_id, 0

    lines: list[str] = []
    added = 0
    emitted: set[tuple[int, str]] = set()
    for approach in approaches:
        link = approach.link
        mount_refs = controls_by_rl.get(link.rl_id, [])
        lane_paths = _approach_lane_paths(approach, lane_paths_by_link, require_incoming=True)
        if not mount_refs or not lane_paths:
            continue

        for lane_index, lane_path in enumerate(lane_paths):
            stop_key = (link.rl_id, lane_path.lane_path_id)
            if stop_key in existing_trflight_stops or stop_key in emitted:
                continue
            mount_ref = mount_refs[min(lane_index, len(mount_refs) - 1)]
            stop_s = _intersection_stop_line_s(approach)
            marker_index = existing_markers.get(link.rl_id, -1) + 1
            existing_markers[link.rl_id] = marker_index
            marker_key = f"RL.{link.rl_id}.Marker.{marker_index}"
            lines.append(f"{marker_key}.ID = {next_obj_id} {lane_path.lane_path_id}")
            lines.append(f"{marker_key}.Type = DrvStop")
            lines.append(
                f"{marker_key}.Param = {_format_number(stop_s)} 0 {lane_path.direction_sign} {mount_ref.control_id} 2 0"
            )
            next_obj_id += 1
            added += 1
            emitted.add(stop_key)
    return lines, next_obj_id, added


def _intersection_signal_lines(
    approaches: list[IntersectionApproach],
    existing_geo: dict[int, int],
    existing_markers: dict[int, int],
    existing_mounts: dict[int, int],
    lane_paths_by_link: dict[int, list[LanePathRef]],
    imported_controls_by_rl: dict[int, list[ImportedTrfLightMountRef]],
    next_obj_id: int,
    next_control_index: int,
) -> tuple[list[str], int, int, int]:
    lines: list[str] = []
    added = 0
    phase_by_node: dict[str, int] = {}
    for approach in approaches:
        link = approach.link
        s_pos = _approach_s_position(approach, INTERSECTION_SIGNAL_SETBACK)
        half_width = _approach_half_road_width(approach)
        lateral = half_width + DEFAULT_SHOULDER_WIDTH + INTERSECTION_SIGNAL_SIDE_CLEARANCE
        if not imported_controls_by_rl.get(link.rl_id):
            geo_index = existing_geo.get(link.rl_id, -1) + 1
            existing_geo[link.rl_id] = geo_index
            key = f"RL.{link.rl_id}.GeoObject.{geo_index}"
            lines.append(f"{key}.ID = {next_obj_id} {link.rl_id}")
            lines.append(
                "{key} = {s} 0 {s} 0 {t} 0 0 0 0 0 {yaw} {scale} {scale} {scale} 0 {model}".format(
                    key=key,
                    s=_format_number(s_pos),
                    t=_format_number(lateral),
                    yaw=_format_number(link.yaw),
                    scale=_format_number(INTERSECTION_SIGNAL_SCALE),
                    model=INTERSECTION_SIGNAL_MODEL,
                )
            )
            next_obj_id += 1
            added += 1

        if not INTERSECTION_DYNAMIC_SIGNALS_ENABLED:
            continue

        control_id = next_obj_id
        phase_index = phase_by_node.get(approach.node.node_id, 0)
        phase_by_node[approach.node.node_id] = phase_index + 1
        phase_offset = 0.0 if phase_index % 2 == 0 else INTERSECTION_SIGNAL_GREEN_SECONDS
        initial_state = 1 if phase_index % 2 == 0 else 3
        control_name = re.sub(r"[^A-Za-z0-9_]+", "_", f"TL_{approach.node.node_id}_{phase_index}")[:24]
        lines.append(
            "Control.TrfLight.{idx} = {control_id} {name} \"\" {state} {offset} {red} 3 {green} 3".format(
                idx=next_control_index,
                control_id=control_id,
                name=control_name,
                state=initial_state,
                offset=_format_number(phase_offset),
                red=_format_number(INTERSECTION_SIGNAL_RED_SECONDS),
                green=_format_number(INTERSECTION_SIGNAL_GREEN_SECONDS),
            )
        )
        next_control_index += 1
        next_obj_id += 1
        added += 1

        mount_index = existing_mounts.get(link.rl_id, -1) + 1
        existing_mounts[link.rl_id] = mount_index
        mount_key = f"RL.{link.rl_id}.Mount.{mount_index}"
        mount_id = next_obj_id
        lines.append(f"{mount_key}.ID = {mount_id} {link.rl_id}")
        lines.append(
            "{key} = {s} 0 {t} 100 1 {span} 0 0 180 0 3.88".format(
                key=mount_key,
                s=_format_number(s_pos),
                t=_format_number(lateral),
                span=_format_number(abs(lateral) + 1.0),
            )
        )
        next_obj_id += 1
        added += 1

        child_id = next_obj_id
        lines.append(f"{mount_key}.0.ID = {child_id}")
        lines.append(f"{mount_key}.0 = 1 {control_id} 3 0 0 0 0 0 98 -1 0")
        next_obj_id += 1
        added += 1

        stop_s = _intersection_stop_line_s(approach)
        for lane_path in _approach_lane_paths(approach, lane_paths_by_link, require_incoming=True):
            marker_index = existing_markers.get(link.rl_id, -1) + 1
            existing_markers[link.rl_id] = marker_index
            marker_key = f"RL.{link.rl_id}.Marker.{marker_index}"
            lines.append(f"{marker_key}.ID = {next_obj_id} {lane_path.lane_path_id}")
            lines.append(f"{marker_key}.Type = DrvStop")
            lines.append(
                f"{marker_key}.Param = {_format_number(stop_s)} 0 {lane_path.direction_sign} {control_id} 2 0"
            )
            next_obj_id += 1
            added += 1
    return lines, next_obj_id, added, next_control_index


def decorate_rd5_intersections(
    rd5_path: Path,
    *,
    graph_path: Path | None = None,
    graph: dict | None = None,
    xodr_path: Path | None = None,
) -> IntersectionDecorationResult:
    rd5_path = Path(rd5_path)
    if not rd5_path.exists():
        raise EnvironmentError(f"RD5 file not found: {rd5_path}")

    lines, removed_objects = _strip_existing_intersections(_read_lines(rd5_path))
    graph_data = _load_graph(graph_path, graph)
    traffic_light_nodes = _traffic_light_nodes_from_graph(graph_data)
    crosswalk_nodes = _crosswalk_nodes_from_graph(graph_data)
    all_intersection_nodes_by_id = {node.node_id: node for node in traffic_light_nodes + crosswalk_nodes}
    all_intersection_nodes = list(all_intersection_nodes_by_id.values())

    n_objects = _parse_int_scalar(lines, N_OBJECTS_RE, 0)
    max_used_obj_id = _parse_int_scalar(lines, MAX_OBJ_RE, 0)
    if removed_objects:
        max_used_obj_id = max(_max_object_id_in_lines(lines), 0)

    if not all_intersection_nodes:
        if removed_objects:
            _patch_scalar(lines, "nObjects", max(0, n_objects - removed_objects))
            _patch_scalar(lines, "MaxUsedObjId", max_used_obj_id)
            rd5_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return IntersectionDecorationResult(
            rd5_path=rd5_path,
            traffic_light_nodes=0,
            crosswalk_nodes=0,
            approach_links=0,
            signal_objects=0,
            crosswalk_markings=0,
        )

    parsed_links = [link for link in _parse_links(lines) if link.length >= INTERSECTION_MIN_LINK_LENGTH]
    graph_edges = _graph_edges_from_graph(graph_data)
    all_approaches = _approaches_from_xodr_refs(
        parsed_links,
        all_intersection_nodes,
        graph_edges,
        _xodr_approach_road_refs(xodr_path, all_intersection_nodes),
        _xodr_lane_counts(xodr_path),
    )
    if not all_approaches:
        all_approaches = _approaches_for_traffic_lights(parsed_links, all_intersection_nodes, graph_edges)
    signal_node_ids = {node.node_id for node in traffic_light_nodes}
    crosswalk_node_ids = {node.node_id for node in crosswalk_nodes}
    signal_stop_approaches = [item for item in all_approaches if item.node.node_id in signal_node_ids]
    signal_approaches = _select_signal_display_approaches(signal_stop_approaches)
    crosswalk_approaches = [item for item in all_approaches if item.node.node_id in crosswalk_node_ids]
    if not signal_stop_approaches and not crosswalk_approaches:
        if removed_objects:
            _patch_scalar(lines, "nObjects", max(0, n_objects - removed_objects))
            _patch_scalar(lines, "MaxUsedObjId", max_used_obj_id)
            rd5_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return IntersectionDecorationResult(
            rd5_path=rd5_path,
            traffic_light_nodes=len(traffic_light_nodes),
            crosswalk_nodes=len(crosswalk_nodes),
            approach_links=0,
            signal_objects=0,
            crosswalk_markings=0,
        )

    generated: list[str] = [INTERSECTION_BEGIN]
    next_obj_id = max_used_obj_id + 1
    existing_markers = _parse_existing_marker_indices(lines)
    existing_markings = _parse_existing_roadmarking_indices(lines)
    lane_paths_by_link = _parse_lane_paths_by_link(lines)
    imported_controls_by_rl = _parse_imported_trflight_controls_by_rl(lines)
    traffic_light_phase_fixes = _patch_imported_trflight_initial_phases(lines, imported_controls_by_rl)
    signal_lines, next_obj_id, signal_objects, _next_control_index = _intersection_signal_lines(
        signal_approaches,
        _parse_existing_geo_indices(lines),
        existing_markers,
        _parse_existing_mount_indices(lines),
        lane_paths_by_link,
        imported_controls_by_rl,
        next_obj_id,
        _parse_next_traffic_light_control_index(lines),
    )
    generated.extend(signal_lines)
    traffic_light_marker_lines, next_obj_id, traffic_light_stop_markers = _imported_trflight_stop_marker_lines(
        signal_stop_approaches,
        existing_markers,
        lane_paths_by_link,
        imported_controls_by_rl,
        _parse_existing_trflight_stop_lane_paths(lines),
        next_obj_id,
    )
    generated.extend(traffic_light_marker_lines)
    traffic_light_stop_line_lines, next_obj_id, traffic_light_stop_lines = _intersection_signal_stop_line_lines(
        signal_stop_approaches,
        existing_markings,
        imported_controls_by_rl,
        lane_paths_by_link,
        next_obj_id,
    )
    generated.extend(traffic_light_stop_line_lines)
    crosswalk_lines, next_obj_id, crosswalk_markings = _intersection_crosswalk_lines(
        crosswalk_approaches,
        existing_markings,
        lane_paths_by_link,
        next_obj_id,
    )
    generated.extend(crosswalk_lines)
    crosswalk_marker_lines, next_obj_id, crosswalk_stop_markers = _intersection_crosswalk_stop_marker_lines(
        crosswalk_approaches,
        existing_markers,
        lane_paths_by_link,
        next_obj_id,
    )
    generated.extend(crosswalk_marker_lines)
    generated.append(INTERSECTION_END)

    generated_objects = (
        signal_objects
        + traffic_light_stop_markers
        + traffic_light_stop_lines
        + crosswalk_markings
        + crosswalk_stop_markers
    )
    _patch_scalar(lines, "nObjects", max(0, n_objects - removed_objects) + generated_objects)
    _patch_scalar(lines, "MaxUsedObjId", max(max_used_obj_id, next_obj_id - 1))

    index = _insertion_index(lines)
    lines[index:index] = generated
    rd5_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return IntersectionDecorationResult(
        rd5_path=rd5_path,
        traffic_light_nodes=len(traffic_light_nodes),
        crosswalk_nodes=len(crosswalk_nodes),
        approach_links=len(all_approaches),
        signal_objects=signal_objects,
        crosswalk_markings=crosswalk_markings,
        crosswalk_stop_markers=crosswalk_stop_markers,
        traffic_light_stop_markers=traffic_light_stop_markers,
        traffic_light_stop_lines=traffic_light_stop_lines,
        traffic_light_phase_fixes=traffic_light_phase_fixes,
    )


def decorate_rd5_safety_margins(
    rd5_path: Path,
    *,
    min_link_length: float = 18.0,
) -> SafetyMarginResult:
    rd5_path = Path(rd5_path)
    if not rd5_path.exists():
        raise EnvironmentError(f"RD5 file not found: {rd5_path}")

    lines, removed_objects = _strip_existing_safety(_read_lines(rd5_path))
    n_objects = _parse_int_scalar(lines, N_OBJECTS_RE, 0)
    max_used_obj_id = _parse_int_scalar(lines, MAX_OBJ_RE, 0)
    if removed_objects:
        max_used_obj_id = max(_max_object_id_in_lines(lines), 0)

    parsed_links = [link for link in _parse_links(lines) if link.length >= min_link_length]
    links = _unique_links(parsed_links)
    if not links:
        raise EnvironmentError("No straight RD5 links were found for safety margin placement.")
    roadside_links = sorted(links, key=lambda item: item.index)
    _patch_roadside_visualization_width(lines, roadside_links)
    existing_visualization = _parse_existing_link_visualization(lines)

    generated: list[str] = [SAFETY_BEGIN]
    generated.extend(
        _city_roadside_visualization_lines(
            roadside_links,
            existing_visualization,
        )
    )

    sidewalk_objects_added = 0
    next_obj_id = max_used_obj_id + 1
    if CITY_SIDEWALK_BUMP_ENABLED:
        existing_bumps = _parse_existing_bump_indices(lines)
        sidewalk_lines, next_obj_id, sidewalk_objects_added = _city_sidewalk_bump_lines(
            _sidewalk_bump_refs(parsed_links),
            existing_bumps,
            next_obj_id,
        )
        generated.extend(sidewalk_lines)

    generated.append(SAFETY_END)
    if len(generated) <= 2:
        raise EnvironmentError("No safety margin lines were generated.")

    _patch_scalar(lines, "nObjects", max(0, n_objects - removed_objects) + sidewalk_objects_added)
    _patch_scalar(lines, "MaxUsedObjId", max(max_used_obj_id, next_obj_id - 1))

    index = _insertion_index(lines)
    lines[index:index] = generated
    rd5_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return SafetyMarginResult(
        rd5_path=rd5_path,
        links_used=len(links),
        sidewalk_bumps=sidewalk_objects_added,
        shoulder_width=CITY_SHOULDER_WIDTH,
        sidewalk_width=CITY_SIDEWALK_WIDTH,
    )


def decorate_rd5_city(
    rd5_path: Path,
    *,
    seed: str | int | None = None,
    max_objects: int = 120,
    min_link_length: float = 18.0,
    road_buffer: float = DEFAULT_ROAD_BUFFER,
    building_density: float = 1.0,
) -> CityEnvironmentResult:
    rd5_path = Path(rd5_path)
    if not rd5_path.exists():
        raise EnvironmentError(f"RD5 file not found: {rd5_path}")
    building_density = max(CITY_DENSITY_MIN, min(float(building_density), CITY_DENSITY_MAX))
    effective_density = max(1.0, building_density) * CITY_BUILDING_SLOT_MULTIPLIER
    max_buildings = max(1, int(round(max_objects * effective_density)))
    density_for_spacing = max(1.0, building_density)
    spacing_scale = max(MIN_BUILDING_SPACING_SCALE, min(1.0, 0.75 / math.sqrt(density_for_spacing)))
    building_gap = (DEFAULT_BUILDING_GAP / density_for_spacing) - min(4.0, (density_for_spacing - 1.0) * 0.45)

    lines, removed_safety_objects = _strip_existing_safety(_read_lines(rd5_path))
    lines, removed_city_objects = _strip_existing_city(lines)
    removed_objects = removed_safety_objects + removed_city_objects
    if removed_city_objects:
        lines = _strip_generated_city_terrain(lines)
    pedestrian_lanes, pedestrian_lane_widths, pedestrian_lane_materials = _patch_pedestrian_lanes(lines)
    n_objects = _parse_int_scalar(lines, N_OBJECTS_RE, 0)
    max_used_obj_id = _parse_int_scalar(lines, MAX_OBJ_RE, 0)
    if removed_objects:
        max_used_obj_id = max(_max_object_id_in_lines(lines), 0)
    existing_geo = _parse_existing_geo_indices(lines)
    road_segments = _parse_road_segments(lines)
    parsed_links = [link for link in _parse_links(lines) if link.length >= min_link_length]
    links = _unique_links(parsed_links)
    if not links:
        raise EnvironmentError("No straight RD5 links were found for city environment placement.")
    if not road_segments:
        raise EnvironmentError("No RD5 road segments were found for city environment clearance checks.")

    building_specs = _load_building_specs(_find_movie_root())

    seed_int = _stable_seed(seed or str(rd5_path))
    rng = random.Random(seed_int)
    roadside_links = sorted(links, key=lambda item: item.index)
    _patch_roadside_visualization_width(lines, roadside_links)
    existing_visualization = _parse_existing_link_visualization(lines)
    rng.shuffle(links)

    generated: list[str] = [CITY_BEGIN]
    next_obj_id = max_used_obj_id + 1
    generated.extend(_city_roadside_visualization_lines(roadside_links, existing_visualization))
    sidewalk_objects_added = 0
    if CITY_SIDEWALK_BUMP_ENABLED:
        existing_bumps = _parse_existing_bump_indices(lines)
        sidewalk_lines, next_obj_id, sidewalk_objects_added = _city_sidewalk_bump_lines(
            _sidewalk_bump_refs(parsed_links),
            existing_bumps,
            next_obj_id,
        )
        generated.extend(sidewalk_lines)
    tree_strips_added = 0
    existing_tree_strips = _parse_existing_tree_strip_indices(lines)
    tree_strip_lines, next_obj_id, tree_strips_added = _city_tree_strip_lines(
        roadside_links,
        existing_tree_strips,
        next_obj_id,
        rng,
    )
    generated.extend(tree_strip_lines)
    objects_added = 0
    used_rl_ids: set[int] = set()
    placed: list[PlacedBuilding] = []
    row_count = _building_row_count(building_density)

    for link in links:
        if objects_added >= max_buildings:
            break

        per_side = _building_count_for_link(link.length, rng, building_density)
        sides = [-1, 1]
        rng.shuffle(sides)
        for side in sides:
            if objects_added >= max_buildings:
                break
            for slot in range(per_side):
                if objects_added >= max_buildings:
                    break

                usable_start = min(8.0, link.length * 0.2)
                usable_end = max(usable_start + 1.0, link.length - usable_start)
                candidate = None
                attempts = int(round(MAX_CITY_ATTEMPTS_PER_SLOT * min(6.0, max(1.0, building_density))))
                row_index = slot % row_count
                row_slot = slot // row_count
                row_slots = max(1, (per_side - row_index + row_count - 1) // row_count)
                for _attempt in range(attempts):
                    spec = rng.choice(building_specs)
                    scale = rng.uniform(0.82, 1.08)
                    radius = spec.radius * scale
                    fraction = (row_slot + 0.5) / row_slots
                    jitter = rng.uniform(-0.16, 0.16) * max(1.0, usable_end - usable_start)
                    s_pos = min(
                        usable_end,
                        max(usable_start, usable_start + fraction * (usable_end - usable_start) + jitter),
                    )
                    lateral_extra = _building_lateral_extra(rng, building_density)
                    lateral_extra += _building_row_lateral_offset(row_index, radius, rng)
                    lateral = side * (road_buffer + radius + lateral_extra)
                    x_pos, y_pos = _link_point(link, s_pos, lateral)
                    if not _is_clear_of_roads(x_pos, y_pos, radius, road_segments, road_buffer):
                        continue
                    if not _is_clear_of_buildings(
                        x_pos,
                        y_pos,
                        radius,
                        placed,
                        building_gap=building_gap,
                        spacing_scale=spacing_scale,
                    ):
                        continue
                    yaw = _building_yaw_for_link(link, side, rng)
                    candidate = (spec, scale, radius, s_pos, lateral, yaw, x_pos, y_pos)
                    break

                if not candidate:
                    continue

                spec, scale, radius, s_pos, lateral, yaw, x_pos, y_pos = candidate

                geo_index = existing_geo.get(link.rl_id, -1) + 1
                existing_geo[link.rl_id] = geo_index

                generated.append(f"RL.{link.rl_id}.GeoObject.{geo_index}.ID = {next_obj_id} {link.rl_id}")
                generated.append(
                    "RL.{rl}.GeoObject.{idx} = {s} 0 {s} 0 {t} 0 0 0 0 0 {yaw} {scale} {scale} {scale} {z} {model}".format(
                        rl=link.rl_id,
                        idx=geo_index,
                        s=_format_number(s_pos),
                        t=_format_number(lateral),
                        yaw=_format_number(yaw),
                        scale=_format_number(scale),
                        z=_format_number(spec.z_offset),
                        model=spec.model,
                    )
                )

                next_obj_id += 1
                objects_added += 1
                used_rl_ids.add(link.rl_id)
                placed.append(PlacedBuilding(x=x_pos, y=y_pos, radius=radius))

    generated.append(CITY_END)
    generated_object_ids = sidewalk_objects_added + tree_strips_added + objects_added
    if generated_object_ids == 0:
        raise EnvironmentError("No city objects were generated.")

    _patch_scalar(lines, "nObjects", max(0, n_objects - removed_objects) + generated_object_ids)
    _patch_scalar(lines, "MaxUsedObjId", max(max_used_obj_id, next_obj_id - 1))

    index = _insertion_index(lines)
    lines[index:index] = generated
    rd5_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return CityEnvironmentResult(
        rd5_path=rd5_path,
        objects_added=objects_added,
        links_used=len(used_rl_ids),
        seed=seed_int,
        building_density=building_density,
        sidewalk_bumps=sidewalk_objects_added,
        tree_strips=tree_strips_added,
        pedestrian_lanes=pedestrian_lanes,
        pedestrian_lane_widths=pedestrian_lane_widths,
        pedestrian_lane_materials=pedestrian_lane_materials,
    )
