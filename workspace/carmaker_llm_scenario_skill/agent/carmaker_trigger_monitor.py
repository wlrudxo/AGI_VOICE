#!/usr/bin/env python3
from __future__ import annotations

"""
Trigger-aware CarMaker telemetry monitor for the running V3 backend.

What it does:
    1. Polls telemetry like carmaker_monitor.py.
    2. Evaluates a trigger condition such as "Car.v >= 13.0".
    3. When the condition matches, sends SC.TAccel = 0.0001 to nearly pause simulation time.
    4. Prints a trigger message and a compact snapshot for LLM action planning.
    5. Waits for the operator or LLM to run carmaker_command.py with --resume-time.

Example:
    python carmaker_trigger_monitor.py --connect --condition "Car.v >= 13.0"

After trigger:
    python carmaker_command.py --connect --resume-time --command "DM.Brake = 0.2 | 1000 | Abs"

Condition format:
    VARIABLE OPERATOR VALUE
    Supported operators: >, >=, <, <=, ==, !=

Examples:
    Car.v >= 13.0
    Traffic.nObjs <= 2
    Vhcl.tRoad != 0
    abs(DM.Steer.Ang) > 0.1
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from carmaker_state import DirectCarMakerStateReader


DEFAULT_BACKEND_URL = "http://127.0.0.1:8010"
DEFAULT_CARMAKER_HOST = "localhost"
DEFAULT_CARMAKER_PORT = 16660
DEFAULT_TRIGGER_TIME_SCALE = 0.0001
DEFAULT_TRIGGER_TIME_DURATION_MS = 30000
SUPPORTED_OPERATORS = {">", ">=", "<", "<=", "==", "!="}
ABS_CONDITION_PATTERN = re.compile(r"^abs\((?P<variable>[A-Za-z0-9._]+)\)$", re.IGNORECASE)


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
class TriggerCondition:
    variable: str
    operator: str
    threshold: float
    absolute_value: bool = False

    @property
    def display_variable(self) -> str:
        return f"abs({self.variable})" if self.absolute_value else self.variable

    def resolve_value(self, raw_data: dict[str, float]) -> float | None:
        if self.variable not in raw_data:
            return None
        value = raw_data[self.variable]
        return abs(value) if self.absolute_value else value

    def matches(self, value: float) -> bool:
        if self.operator == ">":
            return value > self.threshold
        if self.operator == ">=":
            return value >= self.threshold
        if self.operator == "<":
            return value < self.threshold
        if self.operator == "<=":
            return value <= self.threshold
        if self.operator == "==":
            return value == self.threshold
        if self.operator == "!=":
            return value != self.threshold
        raise RuntimeError(f"Unsupported operator: {self.operator}")


def format_snapshot(raw_data: dict[str, float]) -> str:
    preferred_keys = [
        "Time",
        "SC.State",
        "SC.TAccel",
        "Car.v",
        "DM.v.Trgt",
        "DM.Gas",
        "DM.Brake",
        "DM.Steer.Ang",
        "Vhcl.sRoad",
        "Vhcl.tRoad",
    ]
    keys = [key for key in preferred_keys if key in raw_data]
    remainder = sorted(key for key in raw_data if key not in keys)
    ordered = keys + remainder
    return ", ".join(f"{key}={raw_data[key]:.4f}" for key in ordered)


def format_state_summary(state_data: dict[str, float | str | None]) -> str:
    return (
        f"SC.State={state_data['SC.State']:.0f} "
        f"({state_data['SC.State.Label']}), "
        f"SC.TAccel={state_data['SC.TAccel']:.4f}, "
        f"mode={state_data['SC.TimeMode']}"
    )


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
            "CarMaker is not connected. Start V3 backend and connect first, "
            "or rerun with --connect."
        )

    return client.post_json(
        "/api/carmaker/connect",
        {
            "host": host,
            "port": port,
        },
    )


def ensure_monitoring(client: BackendClient) -> bool:
    was_monitoring = bool(client.get_json("/api/carmaker/monitoring"))
    if not was_monitoring:
        client.post_json("/api/carmaker/monitoring", {"active": True})
    return was_monitoring


def restore_monitoring(client: BackendClient, was_monitoring: bool) -> None:
    if not was_monitoring:
        try:
            client.post_json("/api/carmaker/monitoring", {"active": False})
        except RuntimeError:
            pass


def set_time_scale(client: BackendClient, value: float, duration_ms: int) -> None:
    command = f"DVAWrite SC.TAccel {value} {duration_ms} Abs"
    client.post_json("/api/carmaker/command", {"command": command})


def parse_condition(text: str) -> TriggerCondition:
    parts = text.strip().split()
    if len(parts) != 3:
        raise RuntimeError(
            "Condition must be in the form 'VARIABLE OPERATOR VALUE', "
            "for example 'Car.v >= 13.0'."
        )

    variable_text, operator, threshold_text = parts
    if operator not in SUPPORTED_OPERATORS:
        raise RuntimeError(
            f"Unsupported operator '{operator}'. Supported operators: "
            + ", ".join(sorted(SUPPORTED_OPERATORS))
        )

    try:
        threshold = float(threshold_text)
    except ValueError as exc:
        raise RuntimeError(f"Invalid threshold value: {threshold_text}") from exc

    abs_match = ABS_CONDITION_PATTERN.match(variable_text)
    if abs_match:
        variable = abs_match.group("variable")
        absolute_value = True
    else:
        variable = variable_text
        absolute_value = False

    return TriggerCondition(
        variable=variable,
        operator=operator,
        threshold=threshold,
        absolute_value=absolute_value,
    )


def maybe_trigger(
    client: BackendClient,
    raw_data: dict[str, float],
    state_data: dict[str, float | str | None],
    condition: TriggerCondition,
    trigger_time_scale: float,
    trigger_duration_ms: int,
) -> bool:
    value = condition.resolve_value(raw_data)
    if value is None:
        return False

    if not condition.matches(value):
        return False

    set_time_scale(client, trigger_time_scale, trigger_duration_ms)
    print(
        "TRIGGER FIRED: "
        f"{condition.display_variable}={value:.4f} "
        f"{condition.operator} {condition.threshold:.4f}",
        flush=True,
    )
    print(
        "Simulation slowed for LLM action wait: "
        f"SC.TAccel={trigger_time_scale} for {trigger_duration_ms}ms",
        flush=True,
    )
    print(f"State summary: {format_state_summary(state_data)}", flush=True)
    print("Snapshot for LLM:", flush=True)
    print(format_snapshot(raw_data), flush=True)
    print(
        "Awaiting action command. Run carmaker_command.py with --resume-time "
        "to restore SC.TAccel and execute control commands.",
        flush=True,
    )
    return True


def monitor_until_trigger(
    client: BackendClient,
    state_reader: DirectCarMakerStateReader,
    condition: TriggerCondition,
    duration_seconds: float,
    interval_seconds: float,
    trigger_time_scale: float,
    trigger_duration_ms: int,
) -> tuple[int, bool]:
    started = time.monotonic()
    sample_index = 0

    while True:
        elapsed = time.monotonic() - started
        if elapsed > duration_seconds:
            break

        telemetry = client.get_json("/api/carmaker/telemetry")
        raw_data = telemetry.get("rawData") or telemetry.get("raw_data") or {}
        state_data = state_reader.read()
        raw_data = {
            **raw_data,
            "SC.State": float(state_data["SC.State"]),
            "SC.TAccel": float(state_data["SC.TAccel"]),
        }
        sample_index += 1
        print(
            f"[{sample_index:03d}] t={elapsed:6.2f}s | "
            f"{format_snapshot(raw_data)} | {format_state_summary(state_data)}",
            flush=True,
        )
        if maybe_trigger(
            client,
            raw_data,
            state_data,
            condition,
            trigger_time_scale,
            trigger_duration_ms,
        ):
            return sample_index, True
        time.sleep(interval_seconds)

    return sample_index, False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Monitor CarMaker telemetry until a trigger condition fires, then "
            "slow time and emit a snapshot for LLM action planning."
        )
    )
    parser.add_argument(
        "--backend-url",
        default=DEFAULT_BACKEND_URL,
        help=f"V3 backend base URL (default: {DEFAULT_BACKEND_URL})",
    )
    parser.add_argument(
        "--condition",
        required=True,
        help="Trigger condition like 'Car.v >= 13.0' or 'Traffic.nObjs <= 2'",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="How long to monitor in seconds before giving up (default: 30)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Polling interval in seconds (default: 0.5)",
    )
    parser.add_argument(
        "--trigger-time-scale",
        type=float,
        default=DEFAULT_TRIGGER_TIME_SCALE,
        help=(
            "SC.TAccel value sent when the trigger fires "
            f"(default: {DEFAULT_TRIGGER_TIME_SCALE})"
        ),
    )
    parser.add_argument(
        "--trigger-duration-ms",
        type=int,
        default=DEFAULT_TRIGGER_TIME_DURATION_MS,
        help=(
            "Duration passed to SC.TAccel when the trigger fires "
            f"(default: {DEFAULT_TRIGGER_TIME_DURATION_MS})"
        ),
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = BackendClient(args.backend_url)
    state_reader = DirectCarMakerStateReader(args.host, args.port, backend_url=args.backend_url)

    try:
        condition = parse_condition(args.condition)
        status = ensure_connection(client, args.connect, args.host, args.port)
        print(
            f"Connected to CarMaker via backend: {status['host']}:{status['port']}",
            flush=True,
        )
        was_monitoring = ensure_monitoring(client)
        print(
            "Trigger monitoring "
            f"({'already active' if was_monitoring else 'started'}); "
            f"condition: {condition.display_variable} {condition.operator} {condition.threshold}",
            flush=True,
        )
        sample_count, triggered = monitor_until_trigger(
            client,
            state_reader,
            condition,
            args.duration,
            args.interval,
            args.trigger_time_scale,
            args.trigger_duration_ms,
        )
        if triggered:
            print(f"Trigger fired after {sample_count} samples.", flush=True)
        else:
            print(
                f"No trigger fired after {sample_count} samples in {args.duration:.1f}s.",
                flush=True,
            )
        restore_monitoring(client, was_monitoring)
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.", flush=True)
        return 130
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
