#!/usr/bin/env python3
"""Generate CarMaker native route-template scenarios from verified actor blocks."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path("workspace/carmaker_llm_scenario_skill")
DEFAULT_TEMPLATE = (
    ROOT
    / "generated"
    / "TGT-003_signalized_intersection_sudden_accel"
    / "native_route_template"
    / "TGT003_native_route_template_v1"
)
DEFAULT_OUT = (
    ROOT
    / "generated"
    / "native_segment_assembly"
    / "testruns"
)
DEFAULT_REPORT = (
    ROOT
    / "reports"
    / "native_segment_assembly"
)
DEFAULT_CATALOG = ROOT / "reports" / "urbanroad_catalog" / "urbanroad_catalog.json"


ACTOR_START_RE = re.compile(r"^Traffic\.(\d+)\.Name = ", re.MULTILINE)


@dataclass(frozen=True)
class ActorSpec:
    source_index: int
    name: str
    catalog_key: str
    start_pos: str | None = None
    speed_kmh: float | None = None
    route_id: int | None = None
    template: str | None = None
    info: str | None = None
    dyn: str | None = None
    detect_mask: str | None = None
    n_man: int | None = None


@dataclass(frozen=True)
class ScenarioSpec:
    name: str
    title: str
    intent: str
    ego_speed_kmh: float
    ego_start: str = "200.00 0"
    ego_route_id: int = 4235
    actors: tuple[ActorSpec, ...] = field(default_factory=tuple)
    end_sroad: float = 420.0


def load_generation_library(path: Path) -> dict[str, dict]:
    if not path.is_file():
        raise FileNotFoundError(f"catalog not found: {path}")
    catalog = json.loads(path.read_text(encoding="utf-8"))
    library = {}
    for item in catalog.get("generation_library", []):
        library[item["key"]] = item
    return library


def validate_catalog_refs(
    scenarios: tuple[ScenarioSpec, ...],
    library: dict[str, dict],
    require_conflict: bool = True,
) -> None:
    errors: list[str] = []
    for scenario in scenarios:
        has_conflict = False
        for actor in scenario.actors:
            entry = library.get(actor.catalog_key)
            if entry is None:
                errors.append(f"{scenario.name}: missing catalog entry {actor.catalog_key}")
                continue
            tags = set(entry.get("tags", []))
            missing = {"visible", "validated"} - tags
            if missing:
                errors.append(
                    f"{scenario.name}/{actor.name}: catalog entry {actor.catalog_key} missing tags {sorted(missing)}"
                )
            has_conflict = has_conflict or "conflict" in tags
            if entry.get("source_index") != actor.source_index:
                errors.append(
                    f"{scenario.name}/{actor.name}: source_index {actor.source_index} does not match catalog {entry.get('source_index')}"
                )
            if entry.get("route_id") is not None and actor.route_id is not None and int(entry["route_id"]) != actor.route_id:
                errors.append(
                    f"{scenario.name}/{actor.name}: route_id {actor.route_id} does not match catalog {entry.get('route_id')}"
                )
            if len(actor.name) > 8:
                errors.append(f"{scenario.name}/{actor.name}: CarMaker traffic Name exceeds 8 chars")
        if require_conflict and not has_conflict:
            errors.append(f"{scenario.name}: no actor is tagged conflict in catalog")
    if errors:
        raise ValueError("catalog validation failed:\n" + "\n".join(f"- {error}" for error in errors))


def split_template(text: str) -> tuple[str, dict[int, str], str]:
    starts = list(ACTOR_START_RE.finditer(text))
    if not starts:
        raise ValueError("template does not contain Traffic actor blocks")

    prelude = text[: starts[0].start()]
    traffic_n_match = re.search(r"^Traffic\.N = \d+$", text, flags=re.MULTILINE)
    if not traffic_n_match:
        raise ValueError("template does not contain Traffic.N")
    trailer = text[traffic_n_match.start() :]

    actors: dict[int, str] = {}
    for i, match in enumerate(starts):
        old_idx = int(match.group(1))
        end = starts[i + 1].start() if i + 1 < len(starts) else traffic_n_match.start()
        actors[old_idx] = text[match.start() : end].rstrip() + "\n"
    return prelude, actors, trailer


def replace_line(block: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)} = .*$", flags=re.MULTILINE)
    replacement = f"{key} = {value}"
    if pattern.search(block):
        return pattern.sub(replacement, block, count=1)
    return block.rstrip() + f"\n{replacement}\n"


def replace_info(block: str, prefix: str, info: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}\.Info:\n(?:\t.*\n)?", flags=re.MULTILINE)
    replacement = f"{prefix}.Info:\n\t{info}\n"
    if pattern.search(block):
        return pattern.sub(replacement, block, count=1)
    return block


def renumber_actor(block: str, old_idx: int, new_idx: int, spec: ActorSpec) -> str:
    old_prefix = f"Traffic.{old_idx}"
    new_prefix = f"Traffic.{new_idx}"
    block = re.sub(rf"\b{re.escape(old_prefix)}\b", new_prefix, block)
    if len(spec.name) > 8:
        raise ValueError(f"CarMaker traffic Name must be <= 8 chars: {spec.name}")
    block = replace_line(block, f"{new_prefix}.Name", spec.name)
    block = re.sub(
        rf"^({re.escape(new_prefix)}\.Man\.\d+\.LatStep\.\d+\.Pos\.Reference) = .*$",
        rf"\1 = {spec.name}",
        block,
        flags=re.MULTILINE,
    )
    if spec.info:
        block = replace_info(block, new_prefix, spec.info)
    if spec.template:
        block = replace_line(block, f"{new_prefix}.Template.FName", spec.template)
    if spec.detect_mask:
        block = replace_line(block, f"{new_prefix}.DetectMask", spec.detect_mask)
    if spec.route_id is not None:
        block = replace_line(block, f"{new_prefix}.Routing.ObjId", str(spec.route_id))
        block = replace_line(block, f"{new_prefix}.StartPos.ObjId", str(spec.route_id))
    if spec.start_pos is not None:
        block = replace_line(block, f"{new_prefix}.StartPos", spec.start_pos)
    if spec.speed_kmh is not None:
        speed = f"{spec.speed_kmh:g}"
        block = replace_line(block, f"{new_prefix}.Man.Start.Velocity", speed)
        long0 = f"{new_prefix}.Man.0.LongStep.0.Dyn"
        if spec.dyn:
            block = replace_line(block, long0, spec.dyn.format(speed=speed))
        elif re.search(rf"^{re.escape(long0)} = VelTransition\b", block, flags=re.MULTILINE):
            block = replace_line(block, long0, f"VelTransition {speed} linear")
        elif re.search(rf"^{re.escape(long0)} = auto\b", block, flags=re.MULTILINE):
            block = replace_line(block, long0, f"auto {speed}")
    if spec.n_man is not None:
        block = replace_line(block, f"{new_prefix}.nMan", str(spec.n_man))
    return block


def patch_prelude(prelude: str, scenario: ScenarioSpec) -> str:
    description = "\n".join(
        [
            "Description:",
            f"\tLLM native segment assembly scenario: {scenario.title}.",
            f"\tIntent: {scenario.intent}",
            "\tGenerated from verified CarMaker route/actor segments on UrbanRoad_RuralRoad_Expressway.rd5.",
        ]
    )
    prelude = re.sub(r"Description:\n(?:\t.*\n)+", description + "\n", prelude, count=1)
    prelude = replace_line(prelude, "Vehicle.Routing.ObjId", str(scenario.ego_route_id))
    prelude = replace_line(prelude, "Vehicle.StartPos.ObjId", str(scenario.ego_route_id))
    prelude = replace_line(prelude, "Vehicle.StartPos", scenario.ego_start)
    prelude = replace_line(prelude, "DrivMan.Man.Start.Velocity", f"{scenario.ego_speed_kmh:g}")
    prelude = replace_line(
        prelude,
        "DrivMan.Man.0.LongStep.0.EndCond",
        f"Sensor.Collision.Vhcl.Fr1.Count > 0 || Vhcl.sRoad > {scenario.end_sroad:g}",
    )
    prelude = replace_line(
        prelude,
        "DrivMan.Man.0.LongStep.0.Dyn",
        f"Driver 1 0 {scenario.ego_speed_kmh:g}",
    )
    prelude = replace_line(
        prelude,
        "DrivMan.Man.0.LatStep.0.EndCond",
        f"Sensor.Collision.Vhcl.Fr1.Count > 0 || Vhcl.sRoad > {scenario.end_sroad:g}",
    )
    return prelude


def patch_trailer(trailer: str, actor_count: int) -> str:
    trailer = replace_line(trailer, "Traffic.N", str(actor_count))
    trailer = replace_line(trailer, "RandomSeed", "12345")
    return trailer


def render_scenario(
    scenario: ScenarioSpec, template_parts: tuple[str, dict[int, str], str]
) -> str:
    prelude, actor_blocks, trailer = template_parts
    rendered = [patch_prelude(prelude, scenario).rstrip(), ""]
    for new_idx, spec in enumerate(scenario.actors):
        if spec.source_index not in actor_blocks:
            raise KeyError(f"missing source actor block Traffic.{spec.source_index}")
        rendered.append(renumber_actor(actor_blocks[spec.source_index], spec.source_index, new_idx, spec).rstrip())
        rendered.append("")
    rendered.append(patch_trailer(trailer, len(scenario.actors)).rstrip())
    return "\n".join(rendered) + "\n"


SCENARIOS: tuple[ScenarioSpec, ...] = (
    ScenarioSpec(
        name="CMASM_001_crossing_beetle_normal",
        title="single crossing vehicle, normal TTC",
        intent="Baseline ego route 4235 with a blue Beetle crossing on route 4236.",
        ego_speed_kmh=40,
        actors=(
            ActorSpec(0, "cross01", "aeb_crossing_vehicle_cross_ob", "55.00 0", 30, info="Blue Beetle crossing from route 4236"),
        ),
    ),
    ScenarioSpec(
        name="CMASM_002_fast_crossing_vehicle",
        title="faster crossing vehicle",
        intent="Same route pair as baseline, but faster target speed and earlier target start.",
        ego_speed_kmh=50,
        actors=(
            ActorSpec(0, "cross02", "aeb_crossing_vehicle_fast", "42.00 0", 45, info="Faster crossing Beetle"),
        ),
    ),
    ScenarioSpec(
        name="CMASM_004_crossing_with_oncoming",
        title="crossing target plus oncoming vehicle",
        intent="Baseline crossing target with one oncoming/background vehicle to check scene readability.",
        ego_speed_kmh=45,
        actors=(
            ActorSpec(0, "cross01", "aeb_crossing_vehicle_cross_ob", "52.00 0", 32, info="Primary crossing target"),
            ActorSpec(1, "oncom01", "aeb_oncoming_background", "0.00 0", None, info="Oncoming background vehicle"),
        ),
        end_sroad=430,
    ),
)


def write_manifest(scenarios: tuple[ScenarioSpec, ...], out_dir: Path, report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    data = []
    lines = [
        "# Native Segment Assembly Batch",
        "",
        "Generated CarMaker TestRuns assembled from verified native route and actor blocks.",
        "",
        "| Scenario | Intent | Ego | Actors | Output |",
        "| --- | --- | --- | --- | --- |",
    ]
    for scenario in scenarios:
        actors = ", ".join(f"{actor.name}(src Traffic.{actor.source_index})" for actor in scenario.actors)
        output = out_dir / scenario.name
        lines.append(
            f"| `{scenario.name}` | {scenario.intent} | route {scenario.ego_route_id}, {scenario.ego_speed_kmh:g} km/h | {actors} | `{output}` |"
        )
        data.append(
            {
                "name": scenario.name,
                "title": scenario.title,
                "intent": scenario.intent,
                "ego_route_id": scenario.ego_route_id,
                "ego_start": scenario.ego_start,
                "ego_speed_kmh": scenario.ego_speed_kmh,
                "actors": [actor.__dict__ for actor in scenario.actors],
                "output": str(output),
            }
        )
    (report_dir / "generated_batch_manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (report_dir / "generated_batch_manifest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--keep-stale", action="store_true", help="Do not remove stale CMASM_* files from the repo-local output directory.")
    parser.add_argument("--install-project", type=Path)
    args = parser.parse_args()

    validate_catalog_refs(SCENARIOS, load_generation_library(args.catalog))
    template_text = args.template.read_text(encoding="utf-8", errors="replace")
    parts = split_template(template_text)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if not args.keep_stale:
        active_names = {scenario.name for scenario in SCENARIOS}
        for existing in args.out_dir.glob("CMASM_*"):
            if existing.is_file() and existing.name not in active_names:
                existing.unlink()
    for scenario in SCENARIOS:
        destination = args.out_dir / scenario.name
        destination.write_text(render_scenario(scenario, parts), encoding="utf-8")
        if args.install_project:
            install_target = args.install_project / "Data" / "TestRun" / "LLM_Generated" / scenario.name
            install_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, install_target)
        print(destination)
    write_manifest(SCENARIOS, args.out_dir, args.report_dir)


if __name__ == "__main__":
    main()
