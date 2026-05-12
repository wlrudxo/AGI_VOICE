#!/usr/bin/env python3
"""Deterministic postprocessing for generated CarMaker TestRun files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FOLLOWTRAJ_DYN_RE = re.compile(
    r"^(Traffic\.\d+\.Man\.\d+\.(?:LatStep|LongStep)\.\d+)\.Dyn = FollowTraj$"
)
LIMIT_RE = re.compile(r"^(Traffic\.\d+\.Man\.\d+\.(?:LatStep|LongStep)\.\d+)\.Limit = t \{\}$")
LATSTEP_DATA_RE = re.compile(r"^(Traffic\.\d+\.Man\.\d+\.LatStep\.\d+)\.Data:$")


def parse_last_time_from_data(lines: list[str]) -> dict[str, str]:
    last_times: dict[str, str] = {}
    index = 0
    while index < len(lines):
        match = LATSTEP_DATA_RE.match(lines[index])
        if not match:
            index += 1
            continue
        prefix = match.group(1)
        index += 1
        last_time = ""
        while index < len(lines) and (lines[index].startswith("\t") or lines[index].startswith(" ")):
            cols = lines[index].strip().split()
            if cols:
                last_time = cols[-1]
            index += 1
        if last_time:
            last_times[prefix] = last_time
    return last_times


def sibling_lat_prefix(prefix: str) -> str:
    return re.sub(r"\.LongStep\.", ".LatStep.", prefix)


def fix_empty_followtraj_limits(lines: list[str]) -> tuple[list[str], list[str]]:
    last_times = parse_last_time_from_data(lines)
    followtraj_prefixes = {
        match.group(1)
        for line in lines
        if (match := FOLLOWTRAJ_DYN_RE.match(line))
    }
    changes: list[str] = []
    out: list[str] = []
    for line in lines:
        match = LIMIT_RE.match(line)
        if not match:
            out.append(line)
            continue
        prefix = match.group(1)
        if prefix not in followtraj_prefixes:
            out.append(line)
            continue
        time_value = last_times.get(prefix) or last_times.get(sibling_lat_prefix(prefix))
        if not time_value:
            out.append(line)
            continue
        out.append(f"{prefix}.Limit = t {time_value}")
        changes.append(f"{prefix}.Limit: t {{}} -> t {time_value}")
    return out, changes


def postprocess(path: Path, output: Path | None = None) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    lines, changes = fix_empty_followtraj_limits(lines)
    target = output or path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("testrun", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    changes = postprocess(args.testrun, args.out)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(changes) + ("\n" if changes else ""), encoding="utf-8")
    for change in changes:
        print(change)


if __name__ == "__main__":
    main()
