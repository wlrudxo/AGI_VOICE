#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from carmaker_state import DirectCarMakerStateReader


DEFAULT_BACKEND_URL = "http://127.0.0.1:8010"
DEFAULT_CARMAKER_HOST = "localhost"
DEFAULT_CARMAKER_PORT = 16660

TRAFFIC_FIELDS = [
    "tx",
    "ty",
    "v_0.x",
    "v_0.y",
    "LongVel",
    "sRoad",
    "tRoad",
]


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

    def delete_json(self, path: str) -> Any:
        req = request.Request(self._url(path), method="DELETE")
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


def sync_watched_objects(
    client: BackendClient,
    traffic_n_objs: int,
    clear_existing: bool,
) -> list[int]:
    if clear_existing:
        client.delete_json("/api/carmaker/watched-objects")

    watched = client.get_json("/api/carmaker/watched-objects")
    watched_set = {int(index) for index in watched}

    target_count = max(0, traffic_n_objs)
    for index in range(target_count):
        if index not in watched_set:
            updated = client.post_json("/api/carmaker/watched-objects", {"index": index})
            watched_set = {int(value) for value in updated}

    return sorted(watched_set)


def collect_traffic_objects(raw_data: dict[str, float], watched_objects: list[int]) -> list[dict[str, float | int | None]]:
    objects: list[dict[str, float | int | None]] = []
    for index in watched_objects:
        prefix = f"Traffic.T{index:02d}."
        values: dict[str, float | int | None] = {"index": index}
        has_any = False
        for field in TRAFFIC_FIELDS:
            key = prefix + field
            value = raw_data.get(key)
            values[field] = value
            if value is not None:
                has_any = True
        if has_any:
            objects.append(values)
    return objects


def print_snapshot(
    telemetry: dict[str, Any],
    state_data: dict[str, float | str | None],
    watched_objects: list[int],
) -> None:
    raw_data = telemetry.get("rawData") or telemetry.get("raw_data") or {}
    traffic_n_objs = int(raw_data.get("Traffic.nObjs", 0))
    objects = collect_traffic_objects(raw_data, watched_objects)

    print("=== CarMaker Surroundings Snapshot ===", flush=True)
    print(f"Time: {raw_data.get('Time')}", flush=True)
    print(
        "State: "
        f"SC.State={state_data['SC.State']:.0f} ({state_data['SC.State.Label']}), "
        f"SC.TAccel={state_data['SC.TAccel']:.4f}, "
        f"mode={state_data['SC.TimeMode']}",
        flush=True,
    )
    print(
        "Ego: "
        f"Car.v={raw_data.get('Car.v')}, "
        f"Vhcl.sRoad={raw_data.get('Vhcl.sRoad')}, "
        f"Vhcl.tRoad={raw_data.get('Vhcl.tRoad')}, "
        f"DM.v.Trgt={raw_data.get('DM.v.Trgt')}",
        flush=True,
    )
    print(f"Traffic.nObjs: {traffic_n_objs}", flush=True)
    print(f"Watched objects: {watched_objects}", flush=True)
    print("", flush=True)

    if not objects:
        print("No watched traffic object data available.", flush=True)
        return

    print("Traffic objects:", flush=True)
    for obj in objects:
        print(
            f"- T{obj['index']:02d}: "
            f"sRoad={obj['sRoad']}, "
            f"tRoad={obj['tRoad']}, "
            f"LongVel={obj['LongVel']}, "
            f"tx={obj['tx']}, "
            f"ty={obj['ty']}, "
            f"v_0.x={obj['v_0.x']}, "
            f"v_0.y={obj['v_0.y']}",
            flush=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a one-shot CarMaker surroundings snapshot including nearby traffic objects."
    )
    parser.add_argument(
        "--backend-url",
        default=DEFAULT_BACKEND_URL,
        help=f"V3 backend base URL (default: {DEFAULT_BACKEND_URL})",
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
        "--sync-watched",
        action="store_true",
        help="Automatically watch all current traffic objects from 0 to Traffic.nObjs-1.",
    )
    parser.add_argument(
        "--clear-watched",
        action="store_true",
        help="Clear existing watched objects before syncing current traffic objects.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = BackendClient(args.backend_url)
    state_reader = DirectCarMakerStateReader(args.host, args.port, backend_url=args.backend_url)

    try:
        status = ensure_connection(client, args.connect, args.host, args.port)
        print(
            f"Connected to CarMaker via backend: {status['host']}:{status['port']}",
            flush=True,
        )

        was_monitoring = ensure_monitoring(client)
        try:
            telemetry = client.get_json("/api/carmaker/telemetry")
            raw_data = telemetry.get("rawData") or telemetry.get("raw_data") or {}
            traffic_n_objs = int(raw_data.get("Traffic.nObjs", 0))

            watched_objects = client.get_json("/api/carmaker/watched-objects")
            watched_objects = [int(index) for index in watched_objects]

            if args.sync_watched:
                watched_objects = sync_watched_objects(
                    client,
                    traffic_n_objs=traffic_n_objs,
                    clear_existing=args.clear_watched,
                )
                telemetry = client.get_json("/api/carmaker/telemetry")

            state_data = state_reader.read()
            print_snapshot(telemetry, state_data, watched_objects)
        finally:
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
