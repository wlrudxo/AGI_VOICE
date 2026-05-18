#!/usr/bin/env python3
from __future__ import annotations

"""
Simple CarMaker command CLI for the running V3 backend.

Supported command format:
    VARIABLE = VALUE | DURATION_MS | MODE

Examples:
    DM.Steer.Ang = 0.1 | 2000 | Abs
    DM.Gas = 0.3 | 1500 | Abs
    DM.Brake = 0.0

Time-scale control is also supported because SC.TAccel is just another DVA variable:
    SC.TAccel = 0.0001 | 30000 | Abs  # slow / near-pause simulation
    SC.TAccel = 1.0   | 30000 | Abs   # resume normal speed

Regular action commands can also restore time first:
    python carmaker_command.py --resume-time --command "DM.Brake = 0.2 | 1000 | Abs"

Recommended workflow with trigger monitoring:
    1. Run carmaker_trigger_monitor.py with a trigger condition.
    2. When the trigger fires, it slows time with SC.TAccel=0.0001 and prints a snapshot.
    3. After the LLM or operator decides the action, run this CLI with --resume-time.
    4. This CLI restores SC.TAccel=1.0 first, then sends the action commands.

Notes:
    - Use --resume-time only for vehicle action commands such as DM.Brake, DM.Steer.Ang, DM.v.Trgt.
    - Do not combine --resume-time with SC.TAccel commands. Time-scale commands should be sent directly.
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_BACKEND_URL = "http://127.0.0.1:8010"
DEFAULT_CARMAKER_HOST = "localhost"
DEFAULT_CARMAKER_PORT = 16660
DEFAULT_RESUME_TIME_VALUE = 1.0
DEFAULT_RESUME_TIME_DURATION_MS = 3000

COMMAND_PATTERN = re.compile(
    r"^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*\|\s*(-?\d+)(?:\s*\|\s*(AbsRamp|FacRamp|Abs|Off|Fac))?$",
    re.IGNORECASE,
)
LEGACY_PATTERN = re.compile(r"^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*$")
CODE_BLOCK_PATTERN = re.compile(r"```(?:[\w]*)\n([\s\S]*?)\n```")


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
class VehicleCommand:
    variable: str
    value: float
    duration: int
    mode: str

    @property
    def actual_duration(self) -> int:
        return 99999 if self.duration == -1 else self.duration

    @property
    def raw_command(self) -> str:
        return f"DVAWrite {self.variable} {self.value} {self.actual_duration} {self.mode}"

    @property
    def is_time_scale_command(self) -> bool:
        return self.variable.lower() == "sc.taccel"


def extract_command_text(text: str) -> str:
    match = CODE_BLOCK_PATTERN.search(text)
    return match.group(1) if match else text


def parse_commands(text: str) -> list[VehicleCommand]:
    command_text = extract_command_text(text)
    commands: list[VehicleCommand] = []

    for raw_line in command_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue

        command_match = COMMAND_PATTERN.match(line)
        if command_match:
            commands.append(
                VehicleCommand(
                    variable=command_match.group(1),
                    value=float(command_match.group(2)),
                    duration=int(command_match.group(3)),
                    mode=command_match.group(4) or "Abs",
                )
            )
            continue

        legacy_match = LEGACY_PATTERN.match(line)
        if legacy_match:
            commands.append(
                VehicleCommand(
                    variable=legacy_match.group(1),
                    value=float(legacy_match.group(2)),
                    duration=2000,
                    mode="Abs",
                )
            )
            continue

        raise RuntimeError(f"Unsupported command line: {raw_line}")

    if not commands:
        raise RuntimeError("No executable vehicle commands found")

    return commands


def load_command_text(args: argparse.Namespace) -> str:
    if args.command:
        return args.command
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise RuntimeError("Provide --command, --file, or stdin input")


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
        raise RuntimeError(
            "CarMaker is not connected. Connect first or rerun with --connect."
        )

    return client.post_json(
        "/api/carmaker/connect",
        {
            "host": host,
            "port": port,
        },
    )


def execute_commands(
    client: BackendClient,
    commands: list[VehicleCommand],
    dry_run: bool,
) -> int:
    success_count = 0
    for index, command in enumerate(commands, start=1):
        print(
            f"[{index}/{len(commands)}] {command.variable} = {command.value} | "
            f"{command.duration} | {command.mode}",
            flush=True,
        )
        if dry_run:
            print(f"  raw: {command.raw_command}", flush=True)
            success_count += 1
            continue

        result = client.post_json("/api/carmaker/command", {"command": command.raw_command})
        print(f"  -> {result}", flush=True)
        success_count += 1
        time.sleep(0.05)
    return success_count


def maybe_resume_time(
    client: BackendClient,
    commands: list[VehicleCommand],
    dry_run: bool,
    resume_time: bool,
    resume_value: float,
    resume_duration_ms: int,
) -> None:
    if not resume_time:
        return

    if any(command.is_time_scale_command for command in commands):
        raise RuntimeError(
            "--resume-time cannot be used with SC.TAccel commands. "
            "Send time-scale commands directly."
        )

    resume_command = VehicleCommand(
        variable="SC.TAccel",
        value=resume_value,
        duration=resume_duration_ms,
        mode="Abs",
    )
    print(
        "Resuming simulation time before action: "
        f"{resume_command.variable} = {resume_command.value} | "
        f"{resume_command.duration} | {resume_command.mode}",
        flush=True,
    )
    if dry_run:
        print(f"  raw: {resume_command.raw_command}", flush=True)
        return

    result = client.post_json("/api/carmaker/command", {"command": resume_command.raw_command})
    print(f"  -> {result}", flush=True)
    time.sleep(0.05)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send CarMaker control commands through the running V3 backend."
    )
    parser.add_argument(
        "--backend-url",
        default=DEFAULT_BACKEND_URL,
        help=f"V3 backend base URL (default: {DEFAULT_BACKEND_URL})",
    )
    parser.add_argument(
        "--command",
        help='Single command or multi-line block, e.g. "DM.Steer.Ang = 0.1 | 2000 | Abs"',
    )
    parser.add_argument(
        "--file",
        help="Read commands from a text file",
    )
    parser.add_argument(
        "--connect",
        action="store_true",
        help="If CarMaker is not connected, ask the backend to connect first.",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_CARMAKER_HOST,
        help=f"CarMaker host used with --connect (default: {DEFAULT_CARMAKER_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_CARMAKER_PORT,
        help=f"CarMaker port used with --connect (default: {DEFAULT_CARMAKER_PORT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and print the commands without sending them",
    )
    parser.add_argument(
        "--resume-time",
        action="store_true",
        help="Restore SC.TAccel before executing non-time-scale action commands.",
    )
    parser.add_argument(
        "--resume-value",
        type=float,
        default=DEFAULT_RESUME_TIME_VALUE,
        help=f"SC.TAccel value used with --resume-time (default: {DEFAULT_RESUME_TIME_VALUE})",
    )
    parser.add_argument(
        "--resume-duration-ms",
        type=int,
        default=DEFAULT_RESUME_TIME_DURATION_MS,
        help=(
            "Duration passed to SC.TAccel when using --resume-time "
            f"(default: {DEFAULT_RESUME_TIME_DURATION_MS})"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = BackendClient(args.backend_url)

    try:
        command_text = load_command_text(args)
        commands = parse_commands(command_text)
        if args.dry_run:
            maybe_resume_time(
                client,
                commands,
                True,
                args.resume_time,
                args.resume_value,
                args.resume_duration_ms,
            )
            success_count = execute_commands(client, commands, True)
            print(f"Validated {success_count}/{len(commands)} commands.", flush=True)
            return 0
        status = ensure_connection(client, args.connect, args.host, args.port)
        print(
            f"Connected to CarMaker via backend: {status['host']}:{status['port']}",
            flush=True,
        )
        maybe_resume_time(
            client,
            commands,
            False,
            args.resume_time,
            args.resume_value,
            args.resume_duration_ms,
        )
        success_count = execute_commands(client, commands, args.dry_run)
        print(f"Executed {success_count}/{len(commands)} commands.", flush=True)
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.", flush=True)
        return 130
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
