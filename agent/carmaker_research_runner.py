#!/usr/bin/env python3
from __future__ import annotations

"""
LLM-facing CarMaker research automation runner.

This script intentionally stays outside the Svelte/FastAPI UI surface. It uses
the existing V3 backend for socket ownership and gives an agent one deterministic
entrypoint for:
  - official IPG TestRun cataloging
  - TestRun load/start/stop
  - arbitrary DVARead quantity sampling
  - one trigger/action intervention
  - JSONL + Markdown result summaries
"""

import argparse
import json
import math
import re
import socket
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error, request

from carmaker_command import VehicleCommand, parse_commands
from carmaker_state import DirectCarMakerStateReader


DEFAULT_BACKEND_URL = "http://127.0.0.1:8010"
DEFAULT_CARMAKER_HOST = "localhost"
DEFAULT_CARMAKER_PORT = 16660
DEFAULT_CARMAKER_ROOT = Path("/mnt/c/IPG/carmaker/win64-15.0.1")
DEFAULT_REPORT_DIR = Path(
    "workspace/carmaker_llm_scenario_skill/reports/research_automation"
)
DEFAULT_QUANTITIES = [
    "Time",
    "Car.v",
    "Car.ax",
    "Vhcl.sRoad",
    "Vhcl.tRoad",
    "DM.v.Trgt",
    "DM.Gas",
    "DM.Brake",
    "DM.Steer.Ang",
    "Traffic.nObjs",
]
STATE_QUANTITIES = ["SC.State", "SC.TAccel"]
CURATED_TESTRUNS = {
    "Examples/BasicFunctions/Traffic/Man_AutonomousJunctions",
    "Examples/BasicFunctions/Traffic/Man_FollowTraj_PedestrianCrossing",
    "Examples/BasicFunctions/Road/Expressway/Cruising_3lanes",
    "Examples/BasicFunctions/Road/Networks/RuralRoad",
    "Examples/BasicFunctions/Road/Surface/Bumps",
    "Examples/VehicleDynamics/Handling/LaneChange_ISO",
    "Examples/VehicleDynamics/Braking/Braking",
}
KEY_VALUE_RE = re.compile(r"^([^#:\s][^:=]*?)\s*=\s*(.*)$")
TOKEN_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.]*\b")


@dataclass
class BackendClient:
    base_url: str

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}{path}"

    def get_json(self, path: str) -> Any:
        req = request.Request(self._url(path), method="GET")
        return self._read_json(req)

    def post_json(self, path: str, payload: dict[str, Any]) -> Any:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self._url(path),
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return self._read_json(req)

    def command(self, command: str) -> str:
        result = self.post_json("/api/carmaker/command", {"command": command})
        if not isinstance(result, str):
            raise RuntimeError(f"Unexpected command response: {result!r}")
        return result

    def _read_json(self, req: request.Request) -> Any:
        try:
            with request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{req.method} {req.full_url} failed: {exc.code} {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"{req.method} {req.full_url} failed: {exc.reason}") from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body


@dataclass
class DirectCarMakerCommandClient:
    host: str
    port: int
    timeout_seconds: float = 5.0

    def command(self, command: str) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(self.timeout_seconds)
            sock.connect((self.host, self.port))
            sock.sendall(f"{command}\n".encode("utf-8"))
            payload = sock.recv(65536)
        except OSError as exc:
            raise RuntimeError(f"Direct CarMaker command failed: {exc}") from exc
        finally:
            try:
                sock.close()
            except OSError:
                pass

        if not payload:
            raise RuntimeError("Direct CarMaker command returned no response")
        response = payload.decode("utf-8", errors="replace").strip()
        if response.startswith("E"):
            raise RuntimeError(f"CarMaker error: {response}")
        return response or "OK (no response)"


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


@dataclass
class TriggerSpec:
    expression: str
    action_text: str
    time_scale: float = 0.0001
    time_scale_duration_ms: int = 30000
    resume_before_action: bool = True
    fired: bool = False
    fired_sample: int | None = None
    fired_time: float | None = None
    action_results: list[str] = field(default_factory=list)


def sanitize_id(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")[:120] or "run"


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


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

        if in_description:
            stripped = line.strip()
            if stripped:
                description_lines.append(stripped)

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
    tags: list[str] = []
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
    ]:
        if token in text:
            tags.append(token)
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
        filtered = [
            item
            for item in filtered
            if wanted.issubset({tag.lower() for tag in item.tags})
        ]
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
        tag_text = ", ".join(item.tags)
        lines.append(
            f"| `{item.relative_path}` | `{item.road or ''}` | "
            f"`{item.vehicle or ''}` | {item.traffic_count} | {tag_text} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def parse_quantity_arg(text: str | None) -> list[str]:
    if not text:
        return list(DEFAULT_QUANTITIES)
    quantities = [part.strip() for part in text.split(",") if part.strip()]
    if not quantities:
        raise RuntimeError("Quantity list is empty")
    return quantities


def parse_dvaread_response(response: str, quantities: list[str]) -> dict[str, float]:
    if not response.startswith("O"):
        raise RuntimeError(f"DVARead failed: {response!r}")
    values = response[1:].strip().split()
    if len(values) < len(quantities):
        raise RuntimeError(
            f"DVARead returned {len(values)} value(s) for {len(quantities)} quantity request: {response!r}"
        )
    parsed: dict[str, float] = {}
    for quantity, raw_value in zip(quantities, values):
        try:
            parsed[quantity] = float(raw_value)
        except ValueError:
            parsed[quantity] = math.nan
    return parsed


def read_quantities(client: BackendClient | DirectCarMakerCommandClient, quantities: list[str]) -> dict[str, float]:
    response = client.command(f"DVARead {' '.join(quantities)}")
    return parse_dvaread_response(response, quantities)


def evaluate_expression(expression: str, values: dict[str, float]) -> bool:
    if not expression.strip():
        return False
    normalized = expression.replace("&&", " and ").replace("||", " or ")
    reserved = {"and", "or", "not", "abs", "sqrt", "pow", "min", "max", "True", "False"}

    def replace_token(match: re.Match[str]) -> str:
        token = match.group(0)
        if token in reserved:
            return token
        return f'_get("{token}")'

    python_expr = TOKEN_RE.sub(replace_token, normalized)
    safe_globals = {
        "__builtins__": {},
        "abs": abs,
        "sqrt": math.sqrt,
        "pow": pow,
        "min": min,
        "max": max,
    }
    safe_locals = {"_get": lambda key: values.get(key, 0.0)}
    return bool(eval(python_expr, safe_globals, safe_locals))


def ensure_connection(
    client: BackendClient,
    connect_if_needed: bool,
    host: str,
    port: int,
) -> dict[str, Any]:
    status = client.get_json("/api/carmaker/status")
    if status.get("connected"):
        return status
    if not connect_if_needed:
        raise RuntimeError("CarMaker is not connected. Start V3 backend and connect first, or pass --connect.")
    return client.post_json("/api/carmaker/connect", {"host": host, "port": port})


def execute_vehicle_command(
    client: BackendClient | DirectCarMakerCommandClient,
    command: VehicleCommand,
) -> str:
    duration = 99999 if command.duration == -1 else command.duration
    raw = f"DVAWrite {command.variable} {command.value} {duration} {command.mode}"
    return client.command(raw)


def execute_trigger_action(
    client: BackendClient | DirectCarMakerCommandClient,
    trigger: TriggerSpec,
) -> list[str]:
    results: list[str] = []
    commands = parse_commands(trigger.action_text)
    if trigger.resume_before_action:
        results.append(client.command("DVAWrite SC.TAccel 1.0 3000 Abs"))
    for command in commands:
        results.append(execute_vehicle_command(client, command))
        time.sleep(0.05)
    trigger.action_results.extend(results)
    return results


def read_state_snapshot(state_reader: DirectCarMakerStateReader) -> dict[str, float | str | None]:
    try:
        return state_reader.read()
    except RuntimeError as exc:
        return {
            "SC.State": math.nan,
            "SC.TAccel": math.nan,
            "SC.State.Label": f"unavailable: {exc}",
            "SC.TimeMode": "unknown",
        }


def load_action_text(args: argparse.Namespace) -> str:
    if args.action:
        return args.action
    if args.action_file:
        return Path(args.action_file).read_text(encoding="utf-8")
    return ""


def validate_testrun_choice(testrun: str, allow_uncurated: bool) -> None:
    if testrun in CURATED_TESTRUNS:
        return
    if allow_uncurated:
        return
    raise RuntimeError(
        f"Refusing uncurated TestRun '{testrun}'. Pass --allow-uncurated after inspecting it."
    )


def run_dry_plan(args: argparse.Namespace, quantities: list[str], trigger: TriggerSpec | None) -> None:
    print("DRY RUN: no backend or CarMaker commands will be sent.", flush=True)
    print(f"TestRun: {args.testrun}", flush=True)
    print(f"Load command: LoadTestRun \"{args.testrun}\"", flush=True)
    print("Start command: StartSim", flush=True)
    print(f"Quantities: {', '.join(quantities + STATE_QUANTITIES)}", flush=True)
    if trigger:
        print(f"Trigger: {trigger.expression}", flush=True)
        print(f"Trigger action:\n{trigger.action_text}", flush=True)
    if not args.no_stop:
        print("Stop command: StopSim", flush=True)


def run_experiment(args: argparse.Namespace) -> int:
    validate_testrun_choice(args.testrun, args.allow_uncurated)
    quantities = parse_quantity_arg(args.quantities)
    action_text = load_action_text(args)
    trigger = None
    if args.trigger:
        if not action_text:
            raise RuntimeError("--trigger requires --action or --action-file")
        trigger = TriggerSpec(
            expression=args.trigger,
            action_text=action_text,
            time_scale=args.trigger_time_scale,
            time_scale_duration_ms=args.trigger_duration_ms,
            resume_before_action=not args.no_resume_before_action,
        )

    if args.dry_run:
        run_dry_plan(args, quantities, trigger)
        return 0

    run_id = args.run_id or f"{sanitize_id(args.testrun)}_{utc_stamp()}"
    output_dir = Path(args.output_dir) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    samples_path = output_dir / "samples.jsonl"
    summary_path = output_dir / "summary.md"

    if args.direct_carmaker:
        client = DirectCarMakerCommandClient(args.host, args.port)
        state_reader = DirectCarMakerStateReader(args.host, args.port)
        print(f"Connected directly to CarMaker: {args.host}:{args.port}", flush=True)
    else:
        client = BackendClient(args.backend_url)
        state_reader = DirectCarMakerStateReader(args.host, args.port, backend_url=args.backend_url)
        status = ensure_connection(client, args.connect, args.host, args.port)
        print(f"Connected to CarMaker via backend: {status['host']}:{status['port']}", flush=True)

    sample_count = 0
    failure: str | None = None
    load_result = ""
    start_result = ""
    stop_result = ""
    try:
        load_result = client.command(f'LoadTestRun "{args.testrun}"')
        print(f"LoadTestRun -> {load_result}", flush=True)
        start_result = client.command("StartSim")
        print(f"StartSim -> {start_result}", flush=True)
        started_monotonic = time.monotonic()

        with samples_path.open("w", encoding="utf-8") as samples_file:
            while True:
                elapsed = time.monotonic() - started_monotonic
                if elapsed > args.duration:
                    break

                values = read_quantities(client, quantities)
                state = read_state_snapshot(state_reader)
                values.update(
                    {
                        "SC.State": float(state["SC.State"]),
                        "SC.TAccel": float(state["SC.TAccel"]),
                    }
                )
                sample_count += 1
                record = {
                    "sample": sample_count,
                    "elapsedSec": round(elapsed, 4),
                    "values": values,
                    "stateLabel": state["SC.State.Label"],
                    "timeMode": state["SC.TimeMode"],
                }
                samples_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                samples_file.flush()
                print(format_sample(record), flush=True)

                if trigger and not trigger.fired and evaluate_expression(trigger.expression, values):
                    trigger.fired = True
                    trigger.fired_sample = sample_count
                    trigger.fired_time = values.get("Time")
                    client.command(
                        f"DVAWrite SC.TAccel {trigger.time_scale} "
                        f"{trigger.time_scale_duration_ms} Abs"
                    )
                    print(f"TRIGGER FIRED: {trigger.expression}", flush=True)
                    execute_trigger_action(client, trigger)

                time.sleep(args.interval)
    except Exception as exc:
        failure = str(exc)
        raise
    finally:
        if not args.no_stop:
            try:
                stop_result = client.command("StopSim")
                print(f"StopSim -> {stop_result}", flush=True)
            except Exception as exc:
                stop_result = f"failed: {exc}"
                if failure is None:
                    failure = stop_result
        write_run_summary(
            summary_path=summary_path,
            args=args,
            quantities=quantities,
            trigger=trigger,
            sample_count=sample_count,
            samples_path=samples_path,
            load_result=load_result,
            start_result=start_result,
            stop_result=stop_result,
            failure=failure,
        )
        print(f"Summary: {summary_path}", flush=True)
    return 0


def format_sample(record: dict[str, Any]) -> str:
    values = record["values"]
    preferred = ["Time", "SC.State", "SC.TAccel", "Car.v", "Vhcl.sRoad", "Vhcl.tRoad", "DM.Brake"]
    parts = [
        f"{key}={values[key]:.4f}"
        for key in preferred
        if key in values and isinstance(values[key], (int, float))
    ]
    return f"[{record['sample']:03d}] elapsed={record['elapsedSec']:.2f}s " + ", ".join(parts)


def write_run_summary(
    summary_path: Path,
    args: argparse.Namespace,
    quantities: list[str],
    trigger: TriggerSpec | None,
    sample_count: int,
    samples_path: Path,
    load_result: str,
    start_result: str,
    stop_result: str,
    failure: str | None,
) -> None:
    lines = [
        f"# CarMaker Research Run: {summary_path.parent.name}",
        "",
        f"- TestRun: `{args.testrun}`",
        f"- Duration requested: `{args.duration}` seconds",
        f"- Interval: `{args.interval}` seconds",
        f"- Samples: `{sample_count}`",
        f"- Quantities: `{', '.join(quantities)}`",
        f"- Sample log: `{samples_path.name}`",
        f"- Load result: `{load_result}`",
        f"- Start result: `{start_result}`",
        f"- Stop result: `{stop_result}`",
        f"- Status: `{'failed' if failure else 'completed'}`",
    ]
    if failure:
        lines.append(f"- Failure: `{failure}`")
    if trigger:
        lines.extend(
            [
                "",
                "## Trigger",
                "",
                f"- Expression: `{trigger.expression}`",
                f"- Fired: `{trigger.fired}`",
                f"- Fired sample: `{trigger.fired_sample}`",
                f"- Fired Time: `{trigger.fired_time}`",
                f"- Action results: `{len(trigger.action_results)}` command response(s)",
            ]
        )
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def catalog_command(args: argparse.Namespace) -> int:
    items = scan_catalog(Path(args.carmaker_root), args.limit)
    items = filter_catalog(items, curated_only=args.curated_only)
    json_path, md_path = write_catalog(items, Path(args.output_dir))
    print(f"Catalog entries: {len(items)}", flush=True)
    print(f"JSON: {json_path}", flush=True)
    print(f"Markdown: {md_path}", flush=True)
    return 0


def select_command(args: argparse.Namespace) -> int:
    tags = [tag.strip() for tag in (args.tags or "").split(",") if tag.strip()]
    items = scan_catalog(Path(args.carmaker_root), None)
    matches = filter_catalog(
        items,
        tags=tags,
        search=args.search,
        curated_only=args.curated_only,
    )
    if not matches:
        raise RuntimeError("No TestRun matched the selection filters")

    print(f"Matched TestRuns: {len(matches)}", flush=True)
    for item in matches[: args.limit]:
        tag_text = ", ".join(item.tags)
        print(
            f"- {item.relative_path} | road={item.road or ''} | "
            f"traffic={item.traffic_count} | tags={tag_text}",
            flush=True,
        )
    if len(matches) > args.limit:
        print(f"... {len(matches) - args.limit} more omitted; raise --limit to inspect.", flush=True)
    return 0


def self_test_command(args: argparse.Namespace) -> int:
    parsed = parse_dvaread_response("O 1.0 13.5 42.0", ["Time", "Car.v", "Vhcl.sRoad"])
    if parsed["Car.v"] != 13.5:
        raise RuntimeError("DVARead parser self-test failed")
    if not evaluate_expression("Car.v >= 10 and Vhcl.sRoad > 40", parsed):
        raise RuntimeError("Expression evaluator self-test failed")
    commands = parse_commands("DM.Brake = 0.3 | 1000 | Abs\nDM.Gas = 0.0")
    if len(commands) != 2:
        raise RuntimeError("Action parser should keep only executable vehicle commands")
    try:
        validate_testrun_choice("Examples/BasicFunctions/Driver/HandlingCourse", False)
    except RuntimeError:
        pass
    else:
        raise RuntimeError("Curated TestRun guard self-test failed")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.md"
    samples_path = output_dir / "samples.jsonl"
    samples_path.write_text(
        json.dumps({"sample": 1, "values": parsed}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    fake_args = argparse.Namespace(
        testrun="Examples/BasicFunctions/Traffic/Man_AutonomousJunctions",
        duration=1.0,
        interval=0.5,
    )
    trigger = TriggerSpec(
        expression="Car.v >= 10",
        action_text="DM.Brake = 0.3 | 1000 | Abs",
        fired=True,
        fired_sample=1,
        fired_time=1.0,
        action_results=["O"],
    )
    write_run_summary(
        summary_path=summary_path,
        args=fake_args,
        quantities=["Time", "Car.v", "Vhcl.sRoad"],
        trigger=trigger,
        sample_count=1,
        samples_path=samples_path,
        load_result="O",
        start_result="O",
        stop_result="O",
        failure=None,
    )
    if "Status: `completed`" not in summary_path.read_text(encoding="utf-8"):
        raise RuntimeError("Summary writer self-test failed")
    print("Self-test passed.", flush=True)
    print(f"Scratch output: {output_dir}", flush=True)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Catalog and run official CarMaker TestRuns for LLM research loops."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser("catalog", help="Scan official IPG TestRuns.")
    catalog.add_argument("--carmaker-root", default=str(DEFAULT_CARMAKER_ROOT))
    catalog.add_argument("--output-dir", default=str(DEFAULT_REPORT_DIR))
    catalog.add_argument("--limit", type=int)
    catalog.add_argument("--curated-only", action="store_true")

    select = subparsers.add_parser("select", help="Select official TestRuns by tag/search filters.")
    select.add_argument("--carmaker-root", default=str(DEFAULT_CARMAKER_ROOT))
    select.add_argument("--tags", help="Comma-separated tags such as traffic,junction.")
    select.add_argument("--search", help="Case-insensitive text search over path, road, vehicle, description.")
    select.add_argument("--curated-only", action="store_true")
    select.add_argument("--limit", type=int, default=20)

    run = subparsers.add_parser("run", help="Load, run, monitor, and summarize one TestRun.")
    run.add_argument("--testrun", required=True, help='Example: "Examples/BasicFunctions/Traffic/Man_AutonomousJunctions"')
    run.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    run.add_argument("--direct-carmaker", action="store_true", help="Bypass the V3 backend and send commands directly to CarMaker TcpCmdPort.")
    run.add_argument("--connect", action="store_true")
    run.add_argument("--host", default=DEFAULT_CARMAKER_HOST)
    run.add_argument("--port", type=int, default=DEFAULT_CARMAKER_PORT)
    run.add_argument("--quantities", help="Comma-separated DVARead quantities.")
    run.add_argument("--duration", type=float, default=15.0)
    run.add_argument("--interval", type=float, default=0.5)
    run.add_argument("--trigger", help='Expression such as "Car.v >= 13 and Vhcl.sRoad > 50".')
    run.add_argument("--action", help='Action command block, e.g. "DM.Brake = 0.4 | 1200 | Abs".')
    run.add_argument("--action-file", help="Read trigger action commands from a file.")
    run.add_argument("--trigger-time-scale", type=float, default=0.0001)
    run.add_argument("--trigger-duration-ms", type=int, default=30000)
    run.add_argument("--no-resume-before-action", action="store_true")
    run.add_argument("--no-stop", action="store_true")
    run.add_argument("--allow-uncurated", action="store_true")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--run-id")
    run.add_argument("--output-dir", default=str(DEFAULT_REPORT_DIR / "runs"))

    self_test = subparsers.add_parser("self-test", help="Run offline parser and summary self-tests.")
    self_test.add_argument("--output-dir", default="/tmp/carmaker_research_runner_selftest")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "catalog":
            return catalog_command(args)
        if args.command == "select":
            return select_command(args)
        if args.command == "run":
            return run_experiment(args)
        if args.command == "self-test":
            return self_test_command(args)
        raise RuntimeError(f"Unknown command: {args.command}")
    except KeyboardInterrupt:
        print("\nInterrupted.", flush=True)
        return 130
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
