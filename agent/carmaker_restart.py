#!/usr/bin/env python3
"""
Restart a running CarMaker simulation through the V3 backend API.

This script performs a restart as:
  1. POST /api/carmaker/command with "StopSim"
  2. optional wait
  3. POST /api/carmaker/command with "StartSim"

Examples:
  python carmaker_restart.py
  python carmaker_restart.py --delay 1.0
  python carmaker_restart.py --backend-url http://127.0.0.1:8010 --delay 0.5
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def request_json(method: str, url: str, body: dict | None = None) -> dict:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{method} {url} failed: {exc.reason}") from exc

    if not raw.strip():
        return {}
    return json.loads(raw)


def execute_raw_command(base_url: str, command: str) -> dict:
    command_url = f"{base_url.rstrip('/')}/api/carmaker/command"
    result = request_json("POST", command_url, {"command": command})
    return {
        "command": command,
        "result": result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restart CarMaker with StopSim + StartSim through /api/carmaker/command."
    )
    parser.add_argument(
        "--backend-url",
        default="http://127.0.0.1:8010",
        help="V3 backend base URL (default: http://127.0.0.1:8010)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds to wait between stop and start (default: 0.5)",
    )
    args = parser.parse_args()

    base = args.backend_url.rstrip("/")
    status_url = f"{base}/api/carmaker/status"

    try:
        status = request_json("GET", status_url)
        if not status.get("connected"):
            print("ERROR: backend is not connected to CarMaker.", file=sys.stderr)
            return 1

        print("[1/2] StopSim")
        stop_result = execute_raw_command(base, "StopSim")
        print(json.dumps(stop_result, ensure_ascii=False, indent=2))

        if args.delay > 0:
            print(f"Waiting {args.delay:.3f}s...")
            time.sleep(args.delay)

        print("[2/2] StartSim")
        start_result = execute_raw_command(base, "StartSim")
        print(json.dumps(start_result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
