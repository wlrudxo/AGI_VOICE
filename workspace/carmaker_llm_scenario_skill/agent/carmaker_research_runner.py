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
import csv
import json
import math
import re
import socket
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
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


class CommandClient(Protocol):
    def command(self, command: str) -> str:
        ...


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
    if len(values) != len(quantities):
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


def read_quantities(client: CommandClient, quantities: list[str]) -> dict[str, float]:
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
    client: CommandClient,
    command: VehicleCommand,
) -> str:
    return client.command(command.raw_command)


def execute_trigger_action(
    client: CommandClient,
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
    return state_reader.read()


def load_action_text(args: argparse.Namespace) -> str:
    if args.action and args.action_file:
        raise RuntimeError("Use either --action or --action-file, not both")
    if args.action:
        return args.action
    if args.action_file:
        path = Path(args.action_file)
        if not path.exists():
            raise RuntimeError(f"Action file not found: {path}")
        return path.read_text(encoding="utf-8")
    return ""


def validate_positive(name: str, value: float) -> None:
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero")


def validate_run_args(args: argparse.Namespace) -> None:
    validate_positive("--duration", args.duration)
    validate_positive("--interval", args.interval)
    validate_positive("--trigger-time-scale", args.trigger_time_scale)
    if args.trigger_duration_ms <= 0:
        raise RuntimeError("--trigger-duration-ms must be greater than zero")
    if args.direct_carmaker and args.connect:
        raise RuntimeError("--connect is only valid when using the V3 backend")


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


def create_command_client(args: argparse.Namespace) -> CommandClient:
    if args.direct_carmaker:
        print(f"Connected directly to CarMaker: {args.host}:{args.port}", flush=True)
        return DirectCarMakerCommandClient(args.host, args.port)

    client = BackendClient(args.backend_url)
    status = ensure_connection(client, args.connect, args.host, args.port)
    print(f"Connected to CarMaker via backend: {status['host']}:{status['port']}", flush=True)
    return client


def strip_ok_prefix(response: str) -> str:
    return response[1:].strip() if response.startswith("O") else response


def load_testrun_command(args: argparse.Namespace) -> int:
    validate_testrun_choice(args.testrun, args.allow_uncurated)
    if args.direct_carmaker and args.connect:
        raise RuntimeError("--connect is only valid when using the V3 backend")

    verify_keys = args.verify_key or [
        "Vehicle",
        "Traffic.N",
        "DrivMan.Man.0.LongStep.0.Dyn",
        "DrivMan.Man.0.LatStep.0.Dyn",
    ]

    print(f"TestRun: {args.testrun}", flush=True)
    if args.dry_run:
        print("DRY RUN: no backend or CarMaker commands will be sent.", flush=True)
        if args.stop_first:
            print("Stop command: StopSim", flush=True)
        print(f"Load command: LoadTestRun \"{args.testrun}\"", flush=True)
        print(f"Verify keys: {', '.join(verify_keys)}", flush=True)
        return 0

    client = create_command_client(args)
    if args.stop_first:
        stop_result = client.command("StopSim")
        print(f"StopSim -> {stop_result}", flush=True)

    load_result = client.command(f'LoadTestRun "{args.testrun}"')
    print(f"LoadTestRun -> {load_result}", flush=True)

    for key in verify_keys:
        response = client.command(f'IFileRead TestRun "{key}"')
        print(f"{key} = {strip_ok_prefix(response)}", flush=True)
    return 0


def snapshot_command(args: argparse.Namespace) -> int:
    if args.direct_carmaker and args.connect:
        raise RuntimeError("--connect is only valid when using the V3 backend")

    quantities = parse_quantity_arg(args.quantities)
    for required in STATE_QUANTITIES:
        if required not in quantities:
            quantities.append(required)

    print(f"Quantities: {', '.join(quantities)}", flush=True)
    if args.dry_run:
        print("DRY RUN: no backend or CarMaker commands will be sent.", flush=True)
        if not args.no_pause:
            print(
                f"Pause command: DVAWrite SC.TAccel {args.pause_time_scale} "
                f"{args.pause_duration_ms} Abs",
                flush=True,
            )
        print(f"Read command: DVARead {' '.join(quantities)}", flush=True)
        if args.resume_after_read:
            print("Resume command: DVAWrite SC.TAccel 1.0 3000 Abs", flush=True)
        return 0

    client = create_command_client(args)
    if not args.no_pause:
        pause_result = client.command(
            f"DVAWrite SC.TAccel {args.pause_time_scale} {args.pause_duration_ms} Abs"
        )
        print(f"Pause -> {pause_result}", flush=True)
        time.sleep(args.pause_settle_sec)

    values = read_quantities(client, quantities)
    for key in quantities:
        value = values.get(key)
        if isinstance(value, float):
            print(f"{key} = {value:.6g}", flush=True)
        else:
            print(f"{key} = {value}", flush=True)

    if args.resume_after_read:
        resume_result = client.command("DVAWrite SC.TAccel 1.0 3000 Abs")
        print(f"Resume -> {resume_result}", flush=True)
    return 0


def build_control_commands(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    action = args.control_action
    commands: list[str] = []
    readback: list[str] = []

    if action == "start":
        return ["StartSim"], ["SC.State", "SC.TAccel"]
    if action == "stop":
        return ["StopSim"], ["SC.State", "SC.TAccel"]
    if action == "pause":
        return [
            f"DVAWrite SC.TAccel {args.pause_time_scale} {args.duration_ms} Abs"
        ], ["SC.TAccel", "SC.State"]
    if action == "resume":
        return ["DVAWrite SC.TAccel 1.0 3000 Abs"], ["SC.TAccel", "SC.State"]
    if action == "raw":
        if not args.raw_command:
            raise RuntimeError("control raw requires --command")
        return [args.raw_command], []

    if args.resume_first:
        commands.append("DVAWrite SC.TAccel 1.0 3000 Abs")

    variable = {
        "gas": "DM.Gas",
        "brake": "DM.Brake",
        "steer": "DM.Steer.Ang",
        "lane-offset": "DM.LaneOffset",
        "target-speed": "DM.v.Trgt",
    }[action]

    if action == "target-speed":
        if args.kph is None and args.mps is None:
            raise RuntimeError("control target-speed requires --kph or --mps")
        if args.kph is not None and args.mps is not None:
            raise RuntimeError("Use either --kph or --mps, not both")
        value = args.mps if args.mps is not None else args.kph / 3.6
    else:
        if args.value is None:
            raise RuntimeError(f"control {action} requires --value")
        value = args.value

    commands.append(f"DVAWrite {variable} {value} {args.duration_ms} {args.mode}")
    readback.extend([variable, "SC.TAccel", "SC.State"])
    return commands, readback


def control_command(args: argparse.Namespace) -> int:
    if args.direct_carmaker and args.connect:
        raise RuntimeError("--connect is only valid when using the V3 backend")

    commands, readback = build_control_commands(args)
    print(f"Control action: {args.control_action}", flush=True)
    for command in commands:
        print(f"Command: {command}", flush=True)

    if args.dry_run:
        print("DRY RUN: no backend or CarMaker commands will be sent.", flush=True)
        if readback and not args.no_readback:
            print(f"Readback: DVARead {' '.join(readback)}", flush=True)
        return 0

    client = create_command_client(args)
    for command in commands:
        result = client.command(command)
        print(f"{command} -> {result}", flush=True)
        time.sleep(args.command_delay_sec)

    if readback and not args.no_readback:
        values = read_quantities(client, readback)
        for key in readback:
            value = values.get(key)
            if isinstance(value, float):
                print(f"{key} = {value:.6g}", flush=True)
            else:
                print(f"{key} = {value}", flush=True)
    return 0


def split_script_line(line: str) -> list[str]:
    return [part for part in re.split(r"\s+", line.strip()) if part]


def quantities_for_expression(expression: str) -> list[str]:
    reserved = {"and", "or", "not", "abs", "sqrt", "pow", "min", "max", "True", "False"}
    quantities: list[str] = []
    for token in TOKEN_RE.findall(expression):
        if token not in reserved and token not in quantities:
            quantities.append(token)
    return quantities


def load_script_lines(args: argparse.Namespace) -> list[str]:
    if args.script and args.line:
        raise RuntimeError("Use either --script or --line, not both")
    if args.script:
        path = Path(args.script)
        if not path.exists():
            raise RuntimeError(f"Script file not found: {path}")
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    else:
        raw_lines = args.line or []
    lines = []
    for raw_line in raw_lines:
        line = raw_line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    if not lines:
        raise RuntimeError("Script is empty")
    return lines


@dataclass
class SnapshotLogger:
    client: CommandClient
    quantities: list[str]
    sample_interval_sec: float
    output_dir: Path
    start_settle_sec: float = 0.2
    jsonl_file: Any = None
    csv_file: Any = None
    csv_writer: Any = None
    started_monotonic: float = 0.0
    next_sample_monotonic: float = 0.0
    sample_count: int = 0
    active: bool = False
    jsonl_path: Path | None = None
    csv_path: Path | None = None

    def __enter__(self) -> "SnapshotLogger":
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.output_dir / "samples.jsonl"
        self.csv_path = self.output_dir / "samples.csv"
        self.jsonl_file = self.jsonl_path.open("w", encoding="utf-8")
        self.csv_file = self.csv_path.open("w", encoding="utf-8", newline="")
        self.csv_writer = csv.DictWriter(
            self.csv_file,
            fieldnames=["sample", "elapsedSec", *self.quantities],
        )
        self.csv_writer.writeheader()
        self.started_monotonic = time.monotonic()
        self.next_sample_monotonic = self.started_monotonic
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.jsonl_file:
            self.jsonl_file.close()
        if self.csv_file:
            self.csv_file.close()

    def sample(self, reason: str) -> dict[str, Any]:
        values = read_quantities(self.client, self.quantities)
        self.sample_count += 1
        elapsed = round(time.monotonic() - self.started_monotonic, 4)
        record = {
            "sample": self.sample_count,
            "elapsedSec": elapsed,
            "reason": reason,
            "values": values,
        }
        self.jsonl_file.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.jsonl_file.flush()
        row = {"sample": self.sample_count, "elapsedSec": elapsed}
        row.update(values)
        self.csv_writer.writerow(row)
        self.csv_file.flush()
        print(format_logged_sample(record), flush=True)
        return record

    def begin(self) -> None:
        self.active = True
        if self.start_settle_sec > 0:
            time.sleep(self.start_settle_sec)
        self.started_monotonic = time.monotonic()
        self.sample("start")
        self.next_sample_monotonic = time.monotonic() + self.sample_interval_sec

    def sample_if_due(self, reason: str) -> dict[str, Any] | None:
        if not self.active:
            return None
        now = time.monotonic()
        if now < self.next_sample_monotonic:
            return None
        record = self.sample(reason)
        self.next_sample_monotonic = now + self.sample_interval_sec
        return record

    def wait(self, seconds: float, reason: str) -> None:
        deadline = time.monotonic() + seconds
        while True:
            self.sample_if_due(reason)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(remaining, self.sample_interval_sec / 2))


def format_logged_sample(record: dict[str, Any]) -> str:
    values = record["values"]
    preferred = ["Time", "Car.v", "DM.v.Trgt", "DM.LaneOffset", "Vhcl.sRoad", "DM.Brake"]
    parts = []
    for key in preferred:
        value = values.get(key)
        if isinstance(value, (int, float)):
            parts.append(f"{key}={value:.4g}")
    return f"  sample[{record['sample']:03d}] elapsed={record['elapsedSec']:.2f}s " + ", ".join(parts)


def script_command(args: argparse.Namespace) -> int:
    if args.direct_carmaker and args.connect:
        raise RuntimeError("--connect is only valid when using the V3 backend")

    lines = load_script_lines(args)
    log_quantities = parse_quantity_arg(args.quantities)
    args.manual_log_start = any(split_script_line(line)[0].lower() == "log_start" for line in lines)
    print("Script:", flush=True)
    for idx, line in enumerate(lines, start=1):
        print(f"  {idx}. {line}", flush=True)
    if args.log_snapshots:
        print(f"Snapshot log quantities: {', '.join(log_quantities)}", flush=True)

    if args.dry_run:
        print("DRY RUN: no backend or CarMaker commands will be sent.", flush=True)
        if args.log_snapshots:
            run_id = args.run_id or f"script_{utc_stamp()}"
            print(f"Snapshot log output: {Path(args.output_dir) / run_id}", flush=True)
        return 0

    client = create_command_client(args)
    logger_context: Any
    if args.log_snapshots:
        run_id = args.run_id or f"script_{utc_stamp()}"
        logger_context = SnapshotLogger(
            client=client,
            quantities=log_quantities,
            sample_interval_sec=args.sample_interval,
            output_dir=Path(args.output_dir) / run_id,
            start_settle_sec=args.start_settle_sec,
        )
    else:
        logger_context = None

    def execute_lines(logger: SnapshotLogger | None) -> None:
        for idx, line in enumerate(lines, start=1):
            if logger:
                logger.sample_if_due("before_line")
            execute_script_line(args, client, logger, idx, line)
        if logger and logger.active:
            logger.sample("final")

    if logger_context:
        with logger_context as logger:
            execute_lines(logger)
            print(f"Snapshot JSONL: {logger.jsonl_path}", flush=True)
            print(f"Snapshot CSV: {logger.csv_path}", flush=True)
    else:
        execute_lines(None)
    return 0


def execute_script_line(
    args: argparse.Namespace,
    client: CommandClient,
    logger: SnapshotLogger | None,
    idx: int,
    line: str,
) -> None:
    parts = split_script_line(line)
    op = parts[0].lower()
    print(f"[{idx}] {line}", flush=True)

    if op == "load":
        if len(parts) != 2:
            raise RuntimeError("load requires one TestRun name")
        result = client.command(f'LoadTestRun "{parts[1]}"')
        print(f"LoadTestRun -> {result}", flush=True)
    elif op == "stop":
        print(f"StopSim -> {client.command('StopSim')}", flush=True)
    elif op == "start":
        print(f"StartSim -> {client.command('StartSim')}", flush=True)
        if logger and not logger.active and not args.manual_log_start:
            logger.begin()
    elif op == "log_start":
        if not logger:
            print("log_start skipped: snapshot logging is disabled", flush=True)
            return
        if logger.active:
            print("log_start skipped: snapshot logging is already active", flush=True)
            return
        logger.begin()
    elif op == "resume":
        duration_ms = int(float(parts[1])) if len(parts) > 1 else args.default_duration_ms
        command = f"DVAWrite SC.TAccel 1.0 {duration_ms} Abs"
        print(f"{command} -> {client.command(command)}", flush=True)
    elif op == "pause":
        scale = float(parts[1]) if len(parts) > 1 else 0.0001
        duration_ms = int(float(parts[2])) if len(parts) > 2 else args.default_duration_ms
        command = f"DVAWrite SC.TAccel {scale} {duration_ms} Abs"
        print(f"{command} -> {client.command(command)}", flush=True)
    elif op == "target_speed":
        if len(parts) < 2:
            raise RuntimeError("target_speed requires kph")
        kph = float(parts[1])
        duration_ms = int(float(parts[2])) if len(parts) > 2 else args.default_duration_ms
        command = f"DVAWrite DM.v.Trgt {kph / 3.6} {duration_ms} Abs"
        print(f"{command} -> {client.command(command)}", flush=True)
    elif op == "lane_offset":
        if len(parts) < 2:
            raise RuntimeError("lane_offset requires meters")
        value = float(parts[1])
        duration_ms = int(float(parts[2])) if len(parts) > 2 else args.default_duration_ms
        command = f"DVAWrite DM.LaneOffset {value} {duration_ms} Abs"
        print(f"{command} -> {client.command(command)}", flush=True)
    elif op == "raw":
        command = line[len(parts[0]):].strip()
        if not command:
            raise RuntimeError("raw requires a CarMaker command")
        print(f"{command} -> {client.command(command)}", flush=True)
    elif op == "wait":
        if len(parts) != 2:
            raise RuntimeError("wait requires seconds")
        seconds = float(parts[1])
        if logger:
            logger.wait(seconds, "wait")
        else:
            time.sleep(seconds)
    elif op == "wait_until":
        if len(parts) < 2:
            raise RuntimeError("wait_until requires an expression")
        timeout_sec = args.wait_timeout_sec
        interval_sec = args.wait_interval_sec
        expression_tokens = parts[1:]
        if len(expression_tokens) >= 2:
            try:
                timeout_sec = float(expression_tokens[-1])
                expression_tokens = expression_tokens[:-1]
            except ValueError:
                pass
        expression = " ".join(expression_tokens)
        quantities = quantities_for_expression(expression)
        if not quantities:
            raise RuntimeError(f"No quantities found in expression: {expression}")
        deadline = time.monotonic() + timeout_sec
        while True:
            if logger:
                logger.sample_if_due("wait_until")
            values = read_quantities(client, quantities)
            print(
                "  "
                + ", ".join(f"{key}={values.get(key):.6g}" for key in quantities),
                flush=True,
            )
            if evaluate_expression(expression, values):
                print(f"  condition met: {expression}", flush=True)
                break
            if time.monotonic() >= deadline:
                raise RuntimeError(f"wait_until timed out after {timeout_sec}s: {expression}")
            time.sleep(interval_sec)
    else:
        raise RuntimeError(f"Unknown script operation: {op}")


def read_queued_script_lines(command_file: Path, offset: int) -> tuple[list[str], int]:
    if not command_file.exists():
        return [], offset
    with command_file.open("r", encoding="utf-8") as file:
        file.seek(offset)
        raw_lines = file.readlines()
        new_offset = file.tell()
    lines = []
    for raw_line in raw_lines:
        line = raw_line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines, new_offset


def load_optional_line_block(lines: list[str] | None, file_path: str | None) -> list[str]:
    if lines and file_path:
        raise RuntimeError("Use either inline trigger lines or a trigger file, not both")
    raw_lines: list[str]
    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise RuntimeError(f"Trigger action file not found: {path}")
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    else:
        raw_lines = lines or []
    return [
        line.strip()
        for line in raw_lines
        if line.strip() and not line.strip().startswith("#")
    ]


def live_command(args: argparse.Namespace) -> int:
    if args.direct_carmaker and args.connect:
        raise RuntimeError("--connect is only valid when using the V3 backend")
    if args.duration <= 0:
        raise RuntimeError("--duration must be greater than zero")
    if args.sample_interval <= 0:
        raise RuntimeError("--sample-interval must be greater than zero")

    quantities = parse_quantity_arg(args.quantities)
    trigger_lines = load_optional_line_block(args.trigger_line, args.trigger_action_file)
    if args.trigger and not trigger_lines:
        raise RuntimeError("--trigger requires --trigger-line or --trigger-action-file")
    if trigger_lines and not args.trigger:
        raise RuntimeError("Trigger actions require --trigger")
    if args.trigger:
        for quantity in quantities_for_expression(args.trigger):
            if quantity not in quantities:
                quantities.append(quantity)
    command_file = Path(args.command_file)
    run_id = args.run_id or f"live_{utc_stamp()}"
    output_dir = Path(args.output_dir) / run_id
    print(f"Live snapshot quantities: {', '.join(quantities)}", flush=True)
    if args.trigger:
        print(f"Trigger: {args.trigger}", flush=True)
        print("Trigger actions:", flush=True)
        for line in trigger_lines:
            print(f"  - {line}", flush=True)
    print(f"Command queue: {command_file}", flush=True)
    print(f"Output: {output_dir}", flush=True)
    if args.dry_run:
        print("DRY RUN: no backend or CarMaker commands will be sent.", flush=True)
        return 0

    command_file.parent.mkdir(parents=True, exist_ok=True)
    command_file.touch(exist_ok=True)
    command_offset = 0 if args.replay_existing else command_file.stat().st_size

    client = create_command_client(args)
    args.manual_log_start = True
    command_index = 0
    trigger_fired = False
    deadline = time.monotonic() + args.duration
    with SnapshotLogger(
        client=client,
        quantities=quantities,
        sample_interval_sec=args.sample_interval,
        output_dir=output_dir,
        start_settle_sec=args.start_settle_sec,
    ) as logger:
        logger.begin()
        while True:
            lines, command_offset = read_queued_script_lines(command_file, command_offset)
            for line in lines:
                if line.lower() in {"quit", "exit"}:
                    print("Live loop exit requested.", flush=True)
                    print(f"Snapshot JSONL: {logger.jsonl_path}", flush=True)
                    print(f"Snapshot CSV: {logger.csv_path}", flush=True)
                    return 0
                command_index += 1
                execute_script_line(args, client, logger, command_index, line)
            if time.monotonic() >= deadline:
                break
            record = logger.sample_if_due("live")
            if args.trigger and not trigger_fired and record:
                if evaluate_expression(args.trigger, record["values"]):
                    trigger_fired = True
                    print(f"TRIGGER FIRED: {args.trigger}", flush=True)
                    for line in trigger_lines:
                        command_index += 1
                        execute_script_line(args, client, logger, command_index, line)
            time.sleep(min(0.05, args.sample_interval / 2))
        logger.sample("final")
        print(f"Snapshot JSONL: {logger.jsonl_path}", flush=True)
        print(f"Snapshot CSV: {logger.csv_path}", flush=True)
    return 0


def run_experiment(args: argparse.Namespace) -> int:
    validate_run_args(args)
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
        client = create_command_client(args)
        state_reader = DirectCarMakerStateReader(args.host, args.port)
    else:
        client = create_command_client(args)
        state_reader = DirectCarMakerStateReader(args.host, args.port, backend_url=args.backend_url)

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
                state_value = state["SC.State"]
                time_accel_value = state["SC.TAccel"]
                if not isinstance(state_value, (int, float)) or not isinstance(
                    time_accel_value, (int, float)
                ):
                    raise RuntimeError(f"Invalid state snapshot: {state!r}")
                values.update(
                    {
                        "SC.State": float(state_value),
                        "SC.TAccel": float(time_accel_value),
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
        f"- Command path: `{'direct-carmaker' if args.direct_carmaker else 'v3-backend'}`",
        f"- Endpoint: `{args.host}:{args.port}`",
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
        direct_carmaker=True,
        host=DEFAULT_CARMAKER_HOST,
        port=DEFAULT_CARMAKER_PORT,
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

    load = subparsers.add_parser("load", help="Load one TestRun and verify key InfoFile values.")
    load.add_argument("--testrun", required=True, help='Example: "Overtaking"')
    load.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    load.add_argument("--direct-carmaker", action="store_true", help="Bypass the V3 backend and send commands directly to CarMaker TcpCmdPort.")
    load.add_argument("--connect", action="store_true")
    load.add_argument("--host", default=DEFAULT_CARMAKER_HOST)
    load.add_argument("--port", type=int, default=DEFAULT_CARMAKER_PORT)
    load.add_argument("--stop-first", action="store_true", help="Send StopSim before loading the TestRun.")
    load.add_argument("--allow-uncurated", action="store_true")
    load.add_argument("--dry-run", action="store_true")
    load.add_argument(
        "--verify-key",
        action="append",
        help="InfoFile key to read after loading. Repeat for multiple keys.",
    )

    snapshot = subparsers.add_parser(
        "snapshot",
        help="Optionally slow simulation time, read selected DVA quantities, and keep the scene stable.",
    )
    snapshot.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    snapshot.add_argument("--direct-carmaker", action="store_true", help="Bypass the V3 backend and send commands directly to CarMaker TcpCmdPort.")
    snapshot.add_argument("--connect", action="store_true")
    snapshot.add_argument("--host", default=DEFAULT_CARMAKER_HOST)
    snapshot.add_argument("--port", type=int, default=DEFAULT_CARMAKER_PORT)
    snapshot.add_argument("--quantities", help="Comma-separated DVARead quantities.")
    snapshot.add_argument("--no-pause", action="store_true", help="Read quantities without changing SC.TAccel first.")
    snapshot.add_argument("--pause-time-scale", type=float, default=0.0001)
    snapshot.add_argument("--pause-duration-ms", type=int, default=30000)
    snapshot.add_argument("--pause-settle-sec", type=float, default=0.1)
    snapshot.add_argument("--resume-after-read", action="store_true")
    snapshot.add_argument("--dry-run", action="store_true")

    control = subparsers.add_parser("control", help="Send named simulation or ego control commands.")
    control.add_argument(
        "control_action",
        choices=[
            "start",
            "stop",
            "pause",
            "resume",
            "target-speed",
            "gas",
            "brake",
            "steer",
            "lane-offset",
            "raw",
        ],
    )
    control.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    control.add_argument("--direct-carmaker", action="store_true", help="Bypass the V3 backend and send commands directly to CarMaker TcpCmdPort.")
    control.add_argument("--connect", action="store_true")
    control.add_argument("--host", default=DEFAULT_CARMAKER_HOST)
    control.add_argument("--port", type=int, default=DEFAULT_CARMAKER_PORT)
    control.add_argument("--value", type=float, help="Control value for gas/brake/steer/lane-offset.")
    control.add_argument("--kph", type=float, help="Target speed in km/h for target-speed.")
    control.add_argument("--mps", type=float, help="Target speed in m/s for target-speed.")
    control.add_argument("--duration-ms", type=int, default=3000)
    control.add_argument("--mode", default="Abs", choices=["Abs", "AbsRamp", "Fac", "FacRamp", "Off"])
    control.add_argument("--pause-time-scale", type=float, default=0.0001)
    control.add_argument("--resume-first", action="store_true", help="Restore SC.TAccel=1.0 before ego control commands.")
    control.add_argument("--command", dest="raw_command", help="Raw CarMaker command for control raw.")
    control.add_argument("--command-delay-sec", type=float, default=0.05)
    control.add_argument("--no-readback", action="store_true")
    control.add_argument("--dry-run", action="store_true")

    script = subparsers.add_parser("script", help="Run a small CarMaker control script with waits and conditions.")
    script.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    script.add_argument("--direct-carmaker", action="store_true", help="Bypass the V3 backend and send commands directly to CarMaker TcpCmdPort.")
    script.add_argument("--connect", action="store_true")
    script.add_argument("--host", default=DEFAULT_CARMAKER_HOST)
    script.add_argument("--port", type=int, default=DEFAULT_CARMAKER_PORT)
    script.add_argument("--script", help="Path to a script file.")
    script.add_argument("--line", action="append", help="Script line. Repeat for multiple lines.")
    script.add_argument("--default-duration-ms", type=int, default=60000)
    script.add_argument("--wait-timeout-sec", type=float, default=10.0)
    script.add_argument("--wait-interval-sec", type=float, default=0.25)
    script.add_argument("--quantities", help="Comma-separated DVARead quantities to log during script execution.")
    script.add_argument("--log-snapshots", action="store_true", help="Write selected DVARead quantities to JSONL and CSV while the script runs.")
    script.add_argument("--sample-interval", type=float, default=0.5, help="Snapshot logging interval in seconds.")
    script.add_argument("--start-settle-sec", type=float, default=0.2, help="Delay after StartSim before taking the first logged snapshot.")
    script.add_argument("--run-id", help="Output folder name for snapshot logs.")
    script.add_argument("--output-dir", default=str(DEFAULT_REPORT_DIR / "runs"))
    script.add_argument("--dry-run", action="store_true")

    live = subparsers.add_parser(
        "live",
        help="Continuously log selected raw DVA snapshots and execute queued script commands.",
    )
    live.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    live.add_argument("--direct-carmaker", action="store_true", help="Bypass the V3 backend and send commands directly to CarMaker TcpCmdPort.")
    live.add_argument("--connect", action="store_true")
    live.add_argument("--host", default=DEFAULT_CARMAKER_HOST)
    live.add_argument("--port", type=int, default=DEFAULT_CARMAKER_PORT)
    live.add_argument("--quantities", help="Comma-separated DVARead quantities to log.")
    live.add_argument("--sample-interval", type=float, default=0.5)
    live.add_argument("--duration", type=float, default=60.0)
    live.add_argument("--trigger", help='Expression evaluated against logged raw snapshots, e.g. "Time > 0.3 and Time < 2".')
    live.add_argument("--trigger-line", action="append", help="Script command to execute once when --trigger fires. Repeat for multiple commands.")
    live.add_argument("--trigger-action-file", help="Read trigger script commands from a file.")
    live.add_argument("--command-file", default=str(DEFAULT_REPORT_DIR / "live_commands.txt"))
    live.add_argument("--replay-existing", action="store_true", help="Execute lines already present in --command-file.")
    live.add_argument("--default-duration-ms", type=int, default=60000)
    live.add_argument("--wait-timeout-sec", type=float, default=10.0)
    live.add_argument("--wait-interval-sec", type=float, default=0.25)
    live.add_argument("--start-settle-sec", type=float, default=0.0)
    live.add_argument("--run-id", help="Output folder name for snapshot logs.")
    live.add_argument("--output-dir", default=str(DEFAULT_REPORT_DIR / "runs"))
    live.add_argument("--dry-run", action="store_true")

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
        if args.command == "load":
            return load_testrun_command(args)
        if args.command == "snapshot":
            return snapshot_command(args)
        if args.command == "control":
            return control_command(args)
        if args.command == "script":
            return script_command(args)
        if args.command == "live":
            return live_command(args)
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
