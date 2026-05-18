from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path


DEFAULT_CARMAKER_ROOT = Path("/mnt/c/IPG/carmaker/win64-15.0.1")
KEY_VALUE_RE = re.compile(r"^([^#:\s][^:=]*?)\s*=\s*(.*)$")
CURATED_TESTRUNS = {
    "Examples/BasicFunctions/Traffic/Man_AutonomousJunctions",
    "Examples/BasicFunctions/Traffic/Man_FollowTraj_PedestrianCrossing",
    "Examples/BasicFunctions/Road/Expressway/Cruising_3lanes",
    "Examples/BasicFunctions/Road/Networks/RuralRoad",
    "Examples/BasicFunctions/Road/Surface/Bumps",
    "Examples/VehicleDynamics/Handling/LaneChange_ISO",
    "Examples/VehicleDynamics/Braking/Braking",
}


@dataclass
class TestRunInfo:
    id: str
    relative_path: str
    source_path: str
    road: str | None = None
    vehicle: str | None = None
    description: str = ""
    traffic_count: int = 0
    tags: list[str] = field(default_factory=list)


def sanitize_id(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")[:120] or "run"


def read_infofile(path: Path) -> tuple[dict[str, str], str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or "INFOFILE" not in lines[0]:
        raise RuntimeError(f"Not a CarMaker InfoFile: {path}")
    values: dict[str, str] = {}
    description_lines: list[str] = []
    in_description = False
    for line in lines[1:]:
        if line.startswith("Description:"):
            in_description = True
            continue
        match = KEY_VALUE_RE.match(line)
        if match:
            in_description = False
            values[match.group(1).strip()] = match.group(2).strip()
            continue
        if in_description and line.strip():
            description_lines.append(line.strip())
    return values, " ".join(description_lines)


def is_testrun_file(path: Path) -> bool:
    try:
        first = path.open("r", encoding="utf-8", errors="replace").readline()
    except OSError:
        return False
    if "INFOFILE" not in first:
        return False
    try:
        values, _ = read_infofile(path)
    except RuntimeError:
        return False
    return values.get("FileIdent", "").startswith("CarMaker-TestRun")


def infer_tags(relative_path: str, road: str | None, traffic_count: int) -> list[str]:
    text = f"{relative_path} {road or ''}".lower()
    tags = [
        token
        for token in [
            "traffic",
            "junction",
            "pedestrian",
            "expressway",
            "rural",
            "urban",
            "surface",
            "bumps",
            "braking",
            "handling",
            "lane",
        ]
        if token in text
    ]
    if traffic_count:
        tags.append("has_traffic")
    return sorted(set(tags))


def scan_catalog(carmaker_root: Path, limit: int | None = None) -> list[TestRunInfo]:
    root = carmaker_root / "Data" / "TestRun" / "Examples"
    if not root.exists():
        raise RuntimeError(f"Official TestRun root not found: {root}")
    items: list[TestRunInfo] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix in {".ts", ".tcl", ".md", ".txt"}:
            continue
        if not is_testrun_file(path):
            continue
        values, description = read_infofile(path)
        relative = "Examples/" + path.relative_to(root).as_posix()
        traffic_count = int(float(values.get("Traffic.N", "0") or 0))
        items.append(
            TestRunInfo(
                id=sanitize_id(relative.replace("Examples/", "")),
                relative_path=relative,
                source_path=str(path),
                road=values.get("Road.FName"),
                vehicle=values.get("Vehicle"),
                description=description,
                traffic_count=traffic_count,
                tags=infer_tags(relative, values.get("Road.FName"), traffic_count),
            )
        )
        if limit is not None and len(items) >= limit:
            break
    return items


def filter_catalog(
    items: list[TestRunInfo],
    tags: list[str] | None = None,
    search: str | None = None,
    curated_only: bool = False,
) -> list[TestRunInfo]:
    filtered = items
    if curated_only:
        filtered = [item for item in filtered if item.relative_path in CURATED_TESTRUNS]
    if tags:
        wanted = {tag.lower() for tag in tags}
        filtered = [item for item in filtered if wanted.issubset({tag.lower() for tag in item.tags})]
    if search:
        needle = search.lower()
        filtered = [
            item
            for item in filtered
            if needle in item.relative_path.lower()
            or needle in (item.road or "").lower()
            or needle in (item.vehicle or "").lower()
            or needle in item.description.lower()
        ]
    return filtered


def write_catalog(items: list[TestRunInfo], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "official_testrun_catalog.json"
    md_path = output_dir / "official_testrun_catalog.md"
    json_path.write_text(
        json.dumps([asdict(item) for item in items], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    lines = [
        "# Official IPG TestRun Catalog",
        "",
        f"Generated: {datetime.now(UTC).isoformat(timespec='seconds')}",
        "",
        "| Relative Path | Road | Vehicle | Traffic | Tags |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for item in items:
        lines.append(
            f"| `{item.relative_path}` | `{item.road or ''}` | "
            f"`{item.vehicle or ''}` | {item.traffic_count} | {', '.join(item.tags)} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def validate_testrun_choice(testrun: str, allow_uncurated: bool) -> None:
    if testrun in CURATED_TESTRUNS or allow_uncurated:
        return
    raise RuntimeError(
        f"Refusing uncurated TestRun '{testrun}'. Pass --allow-uncurated after inspecting it."
    )
