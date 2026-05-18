from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from carmaker_runtime import (
    CommandClient,
    evaluate_expression,
    quantities_for_expression,
    read_quantities,
)


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


@dataclass
class SnapshotLogger:
    client: CommandClient
    quantities: list[str]
    output_dir: Path
    jsonl_file: Any = None
    csv_file: Any = None
    csv_writer: Any = None
    started_monotonic: float = 0.0
    sample_count: int = 0
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
            fieldnames=["sample", "elapsedSec", "reason", *self.quantities],
        )
        self.csv_writer.writeheader()
        self.started_monotonic = time.monotonic()
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
        row = {"sample": self.sample_count, "elapsedSec": elapsed, "reason": reason}
        row.update(values)
        self.csv_writer.writerow(row)
        self.csv_file.flush()
        print(format_logged_sample(record), flush=True)
        return record


def format_logged_sample(record: dict[str, Any]) -> str:
    values = record["values"]
    preferred = [
        "Time",
        "Car.v",
        "DM.v.Trgt",
        "DM.LaneOffset",
        "Vhcl.sRoad",
        "Traffic.T00.sRoad",
        "Traffic.T00.LongVel",
    ]
    parts = []
    for key in preferred:
        value = values.get(key)
        if isinstance(value, (int, float)):
            parts.append(f"{key}={value:.4g}")
    return f"  sample[{record['sample']:03d}] {record['reason']} elapsed={record['elapsedSec']:.2f}s " + ", ".join(parts)


def parse_drive_action_lines(lines: list[str] | None, file_path: str | None) -> list[str]:
    if lines and file_path:
        raise RuntimeError("Use either --action-line or --action-file, not both")
    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise RuntimeError(f"Action file not found: {path}")
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    else:
        raw_lines = lines or []
    return [
        line.strip()
        for line in raw_lines
        if line.strip() and not line.strip().startswith("#")
    ]


def execute_drive_line(client: CommandClient, line: str, default_duration_ms: int) -> None:
    parts = [part for part in line.split() if part]
    if not parts:
        return
    op = parts[0].lower()
    if op == "raw":
        command = line[len(parts[0]):].strip()
    elif op == "start":
        command = "StartSim"
    elif op == "stop":
        command = "StopSim"
    elif op == "resume":
        duration_ms = int(float(parts[1])) if len(parts) > 1 else default_duration_ms
        command = f"DVAWrite SC.TAccel 1.0 {duration_ms} Abs"
    elif op == "pause":
        scale = float(parts[1]) if len(parts) > 1 else 0.0001
        duration_ms = int(float(parts[2])) if len(parts) > 2 else default_duration_ms
        command = f"DVAWrite SC.TAccel {scale} {duration_ms} Abs"
    elif op == "target_speed":
        if len(parts) < 2:
            raise RuntimeError("target_speed requires kph")
        duration_ms = int(float(parts[2])) if len(parts) > 2 else default_duration_ms
        command = f"DVAWrite DM.v.Trgt {float(parts[1]) / 3.6} {duration_ms} Abs"
    elif op == "lane_offset":
        if len(parts) < 2:
            raise RuntimeError("lane_offset requires meters")
        duration_ms = int(float(parts[2])) if len(parts) > 2 else default_duration_ms
        command = f"DVAWrite DM.LaneOffset {float(parts[1])} {duration_ms} Abs"
    elif op == "brake":
        if len(parts) < 2:
            raise RuntimeError("brake requires value")
        duration_ms = int(float(parts[2])) if len(parts) > 2 else default_duration_ms
        command = f"DVAWrite DM.Brake {float(parts[1])} {duration_ms} Abs"
    elif op == "gas":
        if len(parts) < 2:
            raise RuntimeError("gas requires value")
        duration_ms = int(float(parts[2])) if len(parts) > 2 else default_duration_ms
        command = f"DVAWrite DM.Gas {float(parts[1])} {duration_ms} Abs"
    else:
        raise RuntimeError(f"Unknown drive action: {op}")
    print(f"Action: {command}", flush=True)
    print(f"{command} -> {client.command(command)}", flush=True)
    time.sleep(0.03)


@dataclass
class TriggerPolicy:
    name: str
    trigger: str
    action_lines: list[str]
    fired: bool = False
    trigger_record: dict[str, Any] | None = None


@dataclass
class DriveLoopConfig:
    testrun: str
    quantities: list[str]
    policies: list[TriggerPolicy]
    output_dir: Path
    sample_interval: float
    duration: float
    pause_time_scale: float
    pause_duration_ms: int
    default_action_duration_ms: int
    skip_load: bool = False
    stop_at_end: bool = True
    settle_after_start_sec: float = 0.2


def run_triggered_drive(client: CommandClient, config: DriveLoopConfig) -> Path:
    if not config.policies:
        raise RuntimeError("At least one trigger policy is required")
    for policy in config.policies:
        for quantity in quantities_for_expression(policy.trigger):
            if quantity not in config.quantities:
                config.quantities.append(quantity)
    if "SC.TAccel" not in config.quantities:
        config.quantities.append("SC.TAccel")

    config.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = config.output_dir / "summary.md"
    with SnapshotLogger(client, config.quantities, config.output_dir) as logger:
        print(f"StopSim -> {client.command('StopSim')}", flush=True)
        if config.skip_load:
            print("LoadTestRun -> skipped; using the currently loaded TestRun", flush=True)
        else:
            load_command = f'LoadTestRun "{config.testrun}"'
            print(f"LoadTestRun -> {client.command(load_command)}", flush=True)
        print("DVAWrite DM.v.Trgt 13.88888888888889 120000 Abs -> " + client.command("DVAWrite DM.v.Trgt 13.88888888888889 120000 Abs"), flush=True)
        print("DVAWrite DM.LaneOffset 0.0 120000 Abs -> " + client.command("DVAWrite DM.LaneOffset 0.0 120000 Abs"), flush=True)
        print("DVAWrite DM.Brake 0.0 120000 Abs -> " + client.command("DVAWrite DM.Brake 0.0 120000 Abs"), flush=True)
        print("DVAWrite SC.TAccel 1.0 120000 Abs -> " + client.command("DVAWrite SC.TAccel 1.0 120000 Abs"), flush=True)
        print(f"StartSim -> {client.command('StartSim')}", flush=True)
        wait_for_fresh_sim_time(client, config.quantities, config.settle_after_start_sec)
        logger.started_monotonic = time.monotonic()
        start_time = time.monotonic()

        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= config.duration:
                break
            record = logger.sample("monitor")
            values = record["values"]
            for policy in config.policies:
                if policy.fired or not evaluate_expression(policy.trigger, values):
                    continue
                policy.fired = True
                print(f"TRIGGER FIRED [{policy.name}]: {policy.trigger}", flush=True)
                pause_cmd = f"DVAWrite SC.TAccel {config.pause_time_scale} {config.pause_duration_ms} Abs"
                print(f"{pause_cmd} -> {client.command(pause_cmd)}", flush=True)
                time.sleep(0.1)
                policy.trigger_record = logger.sample(f"trigger_paused_snapshot:{policy.name}")
                print(
                    f"TRIGGER SNAPSHOT JSON [{policy.name}]:",
                    json.dumps(policy.trigger_record, ensure_ascii=False),
                    flush=True,
                )
                print("DVAWrite SC.TAccel 1.0 120000 Abs -> " + client.command("DVAWrite SC.TAccel 1.0 120000 Abs"), flush=True)
                for line in policy.action_lines:
                    execute_drive_line(client, line, config.default_action_duration_ms)
            time.sleep(config.sample_interval)

        final_record = logger.sample("final")
        stop_result = ""
        if config.stop_at_end:
            stop_result = client.command("StopSim")
            print(f"StopSim -> {stop_result}", flush=True)

    lines = [
        f"# CarMaker Triggered Drive: {config.output_dir.name}",
        "",
        f"- TestRun: `{config.testrun}`",
        f"- LoadTestRun skipped: `{config.skip_load}`",
        f"- Trigger policies: `{len(config.policies)}`",
        f"- Samples: `{logger.sample_count}`",
        f"- Quantities: `{', '.join(config.quantities)}`",
        f"- CSV: `samples.csv`",
        f"- JSONL: `samples.jsonl`",
        f"- Final Time: `{final_record['values'].get('Time')}`",
        f"- Stop result: `{stop_result}`",
    ]
    for policy in config.policies:
        lines.append("")
        lines.append(f"## Trigger Policy: {policy.name}")
        lines.append(f"- Trigger: `{policy.trigger}`")
        lines.append(f"- Fired: `{policy.fired}`")
        lines.append(f"- Action lines: `{len(policy.action_lines)}`")
        if policy.trigger_record:
            lines.append(f"- Trigger Time: `{policy.trigger_record['values'].get('Time')}`")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Summary: {summary_path}", flush=True)
    return summary_path


def wait_for_fresh_sim_time(
    client: CommandClient,
    quantities: list[str],
    settle_after_start_sec: float,
    timeout_sec: float = 12.0,
) -> None:
    probe_quantities = ["Time"]
    if "Vhcl.sRoad" in quantities:
        probe_quantities.append("Vhcl.sRoad")
    deadline = time.monotonic() + timeout_sec
    previous_time: float | None = None
    while time.monotonic() < deadline:
        values = read_quantities(client, probe_quantities)
        sim_time = values.get("Time", 0.0)
        s_road = values.get("Vhcl.sRoad", 0.0)
        advancing = previous_time is not None and sim_time > previous_time + 0.02
        if 0.05 <= sim_time <= 2.0 and advancing and abs(s_road) < 1000:
            if settle_after_start_sec > 0:
                time.sleep(settle_after_start_sec)
            return
        previous_time = sim_time
        time.sleep(0.1)
    raise RuntimeError("Simulation time did not restart cleanly after StartSim")
