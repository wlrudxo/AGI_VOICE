#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

from carmaker_state import DirectCarMakerStateReader


DEFAULT_BACKEND_URL = "http://127.0.0.1:8010"
DEFAULT_CARMAKER_HOST = "localhost"
DEFAULT_CARMAKER_PORT = 16660
DEFAULT_CONFIG_PATH = Path(__file__).with_name("carmaker_monitor_config.json")


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


def load_config(config_path: Path) -> dict[str, Any]:
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Monitor config file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid monitor config JSON: {config_path}") from exc


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


def format_front_traffic(raw_data: dict[str, float], config: dict[str, Any]) -> str:
    traffic_config = config.get("frontTraffic") or {}
    object_indices = traffic_config.get("objectIndices") or []
    fields = traffic_config.get("fields") or []
    ego_s_road = raw_data.get("Vhcl.sRoad")
    lines: list[str] = []

    for index in object_indices:
        prefix = f"Traffic.T{int(index):02d}."
        values: list[str] = []
        has_any = False
        object_s_road = raw_data.get(prefix + "sRoad")
        delta_s = None
        if ego_s_road is not None and object_s_road is not None:
            delta_s = object_s_road - ego_s_road

        for field in fields:
            key = prefix + field
            value = raw_data.get(key)
            if value is None:
                continue
            has_any = True
            values.append(f"{field}={value:.4f}")

        if delta_s is not None:
            has_any = True
            values.append(f"delta_s={delta_s:.4f}")

        if has_any:
            lines.append(f"T{int(index):02d}[" + ", ".join(values) + "]")

    return " | ".join(lines) if lines else "front_traffic=unavailable"


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


def monitor_loop(
    client: BackendClient,
    state_reader: DirectCarMakerStateReader,
    config: dict[str, Any],
    duration_seconds: float,
    interval_seconds: float,
) -> int:
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
            f"{format_snapshot(raw_data)} | "
            f"{format_front_traffic(raw_data, config)} | "
            f"{format_state_summary(state_data)}",
            flush=True,
        )
        time.sleep(interval_seconds)

    return sample_index


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read CarMaker telemetry from the running V3 backend for N seconds."
    )
    parser.add_argument(
        "--backend-url",
        default=DEFAULT_BACKEND_URL,
        help=f"V3 backend base URL (default: {DEFAULT_BACKEND_URL})",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="How long to monitor in seconds (default: 10)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Polling interval in seconds (default: 0.5)",
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
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help=f"Monitor config JSON path (default: {DEFAULT_CONFIG_PATH})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = BackendClient(args.backend_url)
    state_reader = DirectCarMakerStateReader(args.host, args.port, backend_url=args.backend_url)
    config = load_config(Path(args.config))

    try:
        status = ensure_connection(client, args.connect, args.host, args.port)
        print(
            f"Connected to CarMaker via backend: {status['host']}:{status['port']}",
            flush=True,
        )
        was_monitoring = ensure_monitoring(client)
        print(
            f"Monitoring {'already active' if was_monitoring else 'started'}; "
            f"sampling for {args.duration:.1f}s every {args.interval:.3f}s",
            flush=True,
        )
        samples = monitor_loop(client, state_reader, config, args.duration, args.interval)
        print(f"Completed {samples} telemetry samples.", flush=True)
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
