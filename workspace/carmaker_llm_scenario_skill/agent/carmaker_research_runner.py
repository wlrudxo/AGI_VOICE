#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from carmaker_catalog import (
    DEFAULT_CARMAKER_ROOT,
    filter_catalog,
    scan_catalog,
    validate_testrun_choice,
    write_catalog,
)
from carmaker_drive_loop import (
    DriveLoopConfig,
    TriggerPolicy,
    parse_drive_action_lines,
    run_triggered_drive,
    utc_stamp,
)
from carmaker_runtime import (
    DEFAULT_BACKEND_URL,
    DEFAULT_CARMAKER_HOST,
    DEFAULT_CARMAKER_PORT,
    DEFAULT_QUANTITIES,
    STATE_QUANTITIES,
    create_command_client,
    evaluate_expression,
    parse_dvaread_response,
    parse_quantity_arg,
    read_quantities,
    strip_ok_prefix,
)


DEFAULT_REPORT_DIR = Path(
    "workspace/carmaker_llm_scenario_skill/reports/research_automation"
)


def add_connection_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    parser.add_argument(
        "--direct-carmaker",
        action="store_true",
        help="Bypass the V3 backend and send commands directly to CarMaker TcpCmdPort.",
    )
    parser.add_argument("--connect", action="store_true")
    parser.add_argument("--host", default=DEFAULT_CARMAKER_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_CARMAKER_PORT)


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
        print(
            f"- {item.relative_path} | road={item.road or ''} | "
            f"traffic={item.traffic_count} | tags={', '.join(item.tags)}",
            flush=True,
        )
    if len(matches) > args.limit:
        print(f"... {len(matches) - args.limit} more omitted; raise --limit to inspect.", flush=True)
    return 0


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
        print(f"StopSim -> {client.command('StopSim')}", flush=True)
    load_command = f'LoadTestRun "{args.testrun}"'
    print(f"LoadTestRun -> {client.command(load_command)}", flush=True)
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
            print(f"Pause command: DVAWrite SC.TAccel {args.pause_time_scale} {args.pause_duration_ms} Abs", flush=True)
        print(f"Read command: DVARead {' '.join(quantities)}", flush=True)
        return 0
    client = create_command_client(args)
    if not args.no_pause:
        pause_result = client.command(
            f"DVAWrite SC.TAccel {args.pause_time_scale} {args.pause_duration_ms} Abs"
        )
        print(f"Pause -> {pause_result}", flush=True)
    values = read_quantities(client, quantities)
    print(json.dumps(values, ensure_ascii=False, indent=2), flush=True)
    if args.resume_after_read:
        print(f"Resume -> {client.command('DVAWrite SC.TAccel 1.0 3000 Abs')}", flush=True)
    return 0


def control_command(args: argparse.Namespace) -> int:
    if args.direct_carmaker and args.connect:
        raise RuntimeError("--connect is only valid when using the V3 backend")
    command = build_control_command(args)
    print(f"Command: {command}", flush=True)
    if args.dry_run:
        print("DRY RUN: no backend or CarMaker commands will be sent.", flush=True)
        return 0
    client = create_command_client(args)
    print(f"{command} -> {client.command(command)}", flush=True)
    return 0


def build_control_command(args: argparse.Namespace) -> str:
    action = args.control_action
    if action == "start":
        return "StartSim"
    if action == "stop":
        return "StopSim"
    if action == "pause":
        return f"DVAWrite SC.TAccel {args.pause_time_scale} {args.duration_ms} Abs"
    if action == "resume":
        return f"DVAWrite SC.TAccel 1.0 {args.duration_ms} Abs"
    if action == "raw":
        if not args.raw_command:
            raise RuntimeError("control raw requires --command")
        return args.raw_command
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
    return f"DVAWrite {variable} {value} {args.duration_ms} {args.mode}"


def drive_command(args: argparse.Namespace) -> int:
    validate_testrun_choice(args.testrun, args.allow_uncurated)
    if args.direct_carmaker and args.connect:
        raise RuntimeError("--connect is only valid when using the V3 backend")
    quantities = parse_quantity_arg(args.quantities)
    policies = build_trigger_policies(args)
    run_id = args.run_id or f"{args.testrun.replace('/', '_')}_{utc_stamp()}"
    output_dir = Path(args.output_dir) / run_id
    if args.dry_run:
        print("DRY RUN: no backend or CarMaker commands will be sent.", flush=True)
        print(f"TestRun: {args.testrun}", flush=True)
        print(f"LoadTestRun skipped: {args.skip_load}", flush=True)
        print(f"Quantities: {', '.join(quantities)}", flush=True)
        print("Trigger policies:", flush=True)
        for policy in policies:
            print(f"  - {policy.name}: {policy.trigger}", flush=True)
            for line in policy.action_lines:
                print(f"      action: {line}", flush=True)
        print(f"Output: {output_dir}", flush=True)
        return 0
    client = create_command_client(args)
    config = DriveLoopConfig(
        testrun=args.testrun,
        quantities=quantities,
        policies=policies,
        output_dir=output_dir,
        sample_interval=args.sample_interval,
        duration=args.duration,
        pause_time_scale=args.pause_time_scale,
        pause_duration_ms=args.pause_duration_ms,
        default_action_duration_ms=args.default_duration_ms,
        skip_load=args.skip_load,
        stop_at_end=not args.no_stop,
        settle_after_start_sec=args.settle_after_start_sec,
        verbose=not args.quiet,
    )
    summary_path = run_triggered_drive(client, config)
    if args.quiet:
        print(f"Summary: {summary_path}", flush=True)
    return 0


def build_trigger_policies(args: argparse.Namespace) -> list[TriggerPolicy]:
    if args.policy_file and (args.trigger or args.trigger_time is not None or args.action_line or args.action_file):
        raise RuntimeError("Use either --policy-file or the single-trigger --trigger/--action-file arguments")
    if args.policy_file:
        return load_policy_file(Path(args.policy_file))

    trigger = args.trigger
    if args.trigger_time is not None:
        trigger = f"Time >= {args.trigger_time}"
    if not trigger:
        raise RuntimeError("drive requires --policy-file, --trigger, or --trigger-time")
    action_lines = parse_drive_action_lines(args.action_line, args.action_file)
    if not action_lines:
        raise RuntimeError("drive requires --policy-file, --action-line, or --action-file")
    return [TriggerPolicy(name="default", trigger=trigger, action_lines=action_lines)]


def load_policy_file(path: Path) -> list[TriggerPolicy]:
    if not path.exists():
        raise RuntimeError(f"Policy file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        entries = data.get("policies")
    else:
        entries = data
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("Policy file must contain a non-empty policy list")
    policies: list[TriggerPolicy] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise RuntimeError(f"Policy #{index} must be an object")
        name = str(entry.get("name") or f"policy_{index}")
        trigger = str(entry.get("trigger") or "").strip()
        if not trigger:
            raise RuntimeError(f"Policy '{name}' is missing trigger")
        action_lines = [str(line).strip() for line in entry.get("actionLines", []) if str(line).strip()]
        action_file = entry.get("actionFile")
        if action_file:
            action_path = Path(str(action_file))
            if not action_path.is_absolute():
                action_path = path.parent / action_path
            action_lines.extend(parse_drive_action_lines(None, str(action_path)))
        if not action_lines:
            raise RuntimeError(f"Policy '{name}' has no actionLines or actionFile")
        policies.append(TriggerPolicy(name=name, trigger=trigger, action_lines=action_lines))
    return policies


def self_test_command(args: argparse.Namespace) -> int:
    parsed = parse_dvaread_response("O 1.0 13.5 42.0", ["Time", "Car.v", "Vhcl.sRoad"])
    if parsed["Car.v"] != 13.5:
        raise RuntimeError("DVARead parser self-test failed")
    if not evaluate_expression("Car.v >= 10 and Vhcl.sRoad > 40", parsed):
        raise RuntimeError("Expression evaluator self-test failed")
    print("Self-test passed.", flush=True)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Catalog, snapshot, and run one triggered CarMaker LLM drive loop."
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
    add_connection_args(load)
    load.add_argument("--testrun", required=True)
    load.add_argument("--stop-first", action="store_true")
    load.add_argument("--allow-uncurated", action="store_true")
    load.add_argument("--verify-key", action="append")
    load.add_argument("--dry-run", action="store_true")

    snapshot = subparsers.add_parser("snapshot", help="Read selected raw DVA quantities.")
    add_connection_args(snapshot)
    snapshot.add_argument("--quantities")
    snapshot.add_argument("--no-pause", action="store_true")
    snapshot.add_argument("--pause-time-scale", type=float, default=0.0001)
    snapshot.add_argument("--pause-duration-ms", type=int, default=30000)
    snapshot.add_argument("--resume-after-read", action="store_true")
    snapshot.add_argument("--dry-run", action="store_true")

    control = subparsers.add_parser("control", help="Send one named or raw CarMaker command.")
    add_connection_args(control)
    control.add_argument(
        "control_action",
        choices=["start", "stop", "pause", "resume", "target-speed", "gas", "brake", "steer", "lane-offset", "raw"],
    )
    control.add_argument("--value", type=float)
    control.add_argument("--kph", type=float)
    control.add_argument("--mps", type=float)
    control.add_argument("--duration-ms", type=int, default=3000)
    control.add_argument("--mode", default="Abs", choices=["Abs", "AbsRamp", "Fac", "FacRamp", "Off"])
    control.add_argument("--pause-time-scale", type=float, default=0.0001)
    control.add_argument("--command", dest="raw_command")
    control.add_argument("--dry-run", action="store_true")

    drive = subparsers.add_parser(
        "drive",
        help="The single automation path: log raw snapshots, pause on trigger, then execute action.",
    )
    add_connection_args(drive)
    drive.add_argument("--testrun", required=True)
    drive.add_argument("--allow-uncurated", action="store_true")
    drive.add_argument("--quantities")
    drive.add_argument(
        "--policy-file",
        help="JSON file with multiple trigger policies. Each policy has name, trigger, and actionFile/actionLines.",
    )
    drive.add_argument("--trigger")
    drive.add_argument("--trigger-time", type=float, help="Pause and snapshot when Time reaches this value.")
    drive.add_argument("--action-line", action="append")
    drive.add_argument("--action-file")
    drive.add_argument("--duration", type=float, default=12.0)
    drive.add_argument("--sample-interval", type=float, default=0.5)
    drive.add_argument("--pause-time-scale", type=float, default=0.0001)
    drive.add_argument("--pause-duration-ms", type=int, default=30000)
    drive.add_argument("--default-duration-ms", type=int, default=60000)
    drive.add_argument("--settle-after-start-sec", type=float, default=0.2)
    drive.add_argument(
        "--skip-load",
        action="store_true",
        help="Reuse the currently loaded TestRun and only StopSim/StartSim for demo reruns.",
    )
    drive.add_argument("--no-stop", action="store_true")
    drive.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-command and per-sample console logs while still writing CSV/JSONL.",
    )
    drive.add_argument("--run-id")
    drive.add_argument("--output-dir", default=str(DEFAULT_REPORT_DIR / "runs"))
    drive.add_argument("--dry-run", action="store_true")

    self_test = subparsers.add_parser("self-test", help="Run offline parser self-tests.")
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
        if args.command == "drive":
            return drive_command(args)
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
