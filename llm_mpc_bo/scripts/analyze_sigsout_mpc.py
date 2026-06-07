#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from bisect import bisect_right
from datetime import datetime
from pathlib import Path
from statistics import mean


def load_signal(path: Path) -> tuple[list[float], list[float]]:
    times: list[float] = []
    values: list[float] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                t = float(row["Time"])
                v = float(row["Value"])
            except (KeyError, TypeError, ValueError):
                continue
            if math.isfinite(t) and math.isfinite(v):
                times.append(t)
                values.append(v)
    return times, values


def normalize_name(path: Path) -> str:
    stem = path.stem
    if "_" in stem and stem[:2].isdigit():
        return stem.split("_", 1)[1]
    return stem


def interp(times: list[float], values: list[float], x: float) -> float:
    if not times:
        return float("nan")
    if x <= times[0]:
        return values[0]
    if x >= times[-1]:
        return values[-1]
    i = bisect_right(times, x)
    t0, t1 = times[i - 1], times[i]
    v0, v1 = values[i - 1], values[i]
    if t1 == t0:
        return v0
    a = (x - t0) / (t1 - t0)
    return v0 + a * (v1 - v0)


def stats(values: list[float]) -> dict[str, float | None]:
    finite = [v for v in values if math.isfinite(v)]
    if not finite:
        return {"min": None, "max": None, "mean": None, "rmse": None, "maxAbs": None}
    return {
        "min": min(finite),
        "max": max(finite),
        "mean": mean(finite),
        "rmse": math.sqrt(mean([v * v for v in finite])),
        "maxAbs": max(abs(v) for v in finite),
    }


def corr(a: list[float], b: list[float]) -> float | None:
    pairs = [(x, y) for x, y in zip(a, b) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 3:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = mean(xs)
    my = mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    cov = sum((x - mx) * (y - my) for x, y in pairs)
    return cov / math.sqrt(vx * vy)


def sign_vote(error: list[float], command: list[float]) -> dict[str, float | int | None]:
    pairs = [(e, u) for e, u in zip(error, command) if math.isfinite(e) and math.isfinite(u)]
    active = [(e, u) for e, u in pairs if abs(e) > 0.02 and abs(u) > 1e-4]
    if not active:
        return {
            "n": 0,
            "sameSignFraction": None,
            "oppositeSignFraction": None,
            "meanErrorTimesCommand": None,
        }
    products = [e * u for e, u in active]
    same = sum(1 for p in products if p > 0)
    opposite = sum(1 for p in products if p < 0)
    return {
        "n": len(active),
        "sameSignFraction": same / len(active),
        "oppositeSignFraction": opposite / len(active),
        "meanErrorTimesCommand": mean(products),
    }


def first_where(rows: list[dict[str, float]], predicate) -> dict[str, float] | None:
    for row in rows:
        if predicate(row):
            return row
    return None


def fmt(value: float | None, digits: int = 4) -> str:
    if value is None or not math.isfinite(value):
        return "n/a"
    return f"{value:.{digits}f}"


def analyze(input_dir: Path) -> dict:
    signals = {normalize_name(path): load_signal(path) for path in sorted(input_dir.glob("*.csv"))}
    if not signals:
        raise FileNotFoundError(f"No CSV signals found in {input_dir}")

    aliases = {
        "delta_cmd": ["delta_cmd", "mv", "MPC", "steer_control"],
        "steer_manual": ["steer_manual"],
        "s": ["s"],
        "t": ["t"],
        "t_ref": ["t_ref"],
        "devang": ["devang"],
        "psi_ref": ["psi_ref"],
        "yawrate": ["yawrate"],
        "v": ["v"],
        "e_t": ["e_t"],
        "e_psi": ["e_psi"],
    }

    def find_signal(canonical: str) -> str | None:
        for name in aliases[canonical]:
            if name in signals:
                return name
        lowered = {name.lower(): name for name in signals}
        for name in aliases[canonical]:
            if name.lower() in lowered:
                return lowered[name.lower()]
        return None

    delta_name = find_signal("delta_cmd")
    if delta_name is None:
        raise KeyError(f"No delta command signal found. Available: {sorted(signals)}")

    base_times = signals[delta_name][0]
    rows: list[dict[str, float]] = []
    names = {key: find_signal(key) for key in aliases}
    for t0 in base_times:
        row = {"Time": t0}
        for canonical, actual in names.items():
            if actual is None:
                continue
            row[canonical] = interp(signals[actual][0], signals[actual][1], t0)
        if "e_t" not in row and "t" in row and "t_ref" in row:
            row["e_t"] = row["t"] - row["t_ref"]
        if "e_psi" not in row and "devang" in row and "psi_ref" in row:
            row["e_psi"] = row["devang"] - row["psi_ref"]
        rows.append(row)

    final = rows[-1]
    straight = [
        row
        for row in rows
        if row.get("s", 0.0) < 280.0 and row.get("v", 999.0) > 1.0
    ]
    active = straight or rows

    e_t = [row.get("e_t", float("nan")) for row in active]
    e_psi = [row.get("e_psi", float("nan")) for row in active]
    delta = [row.get("delta_cmd", float("nan")) for row in active]
    manual = [row.get("steer_manual", float("nan")) for row in active]

    et_delta_vote = sign_vote(e_t, delta)
    et_manual_vote = sign_vote(e_t, manual)
    corr_et_delta = corr(e_t, delta)
    corr_et_manual = corr(e_t, manual)

    likely_sign_issue = False
    reason = []
    if et_delta_vote["sameSignFraction"] is not None and et_delta_vote["sameSignFraction"] > 0.7:
        likely_sign_issue = True
        reason.append("lateral error and MPC command have the same sign for most active samples")
    if corr_et_delta is not None and corr_et_delta > 0.7:
        likely_sign_issue = True
        reason.append("corr(e_t, delta_cmd) is strongly positive")
    if corr_et_manual is not None and corr_et_manual < -0.5 and corr_et_delta is not None and corr_et_delta > 0.5:
        likely_sign_issue = True
        reason.append("manual/reference steering trend is opposite to MPC trend")

    first_et_01 = first_where(rows, lambda r: abs(r.get("e_t", 0.0)) > 0.1)
    first_et_05 = first_where(rows, lambda r: abs(r.get("e_t", 0.0)) > 0.5)
    first_cmd_01 = first_where(rows, lambda r: abs(r.get("delta_cmd", 0.0)) > 0.1)

    return {
        "inputDir": str(input_dir),
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "signals": {key: value for key, value in names.items() if value is not None},
        "timeRange": {
            "start": rows[0]["Time"],
            "end": rows[-1]["Time"],
            "numSamples": len(rows),
        },
        "final": final,
        "stats": {
            "delta_cmd": stats([row.get("delta_cmd", float("nan")) for row in rows]),
            "e_t": stats([row.get("e_t", float("nan")) for row in rows]),
            "e_psi": stats([row.get("e_psi", float("nan")) for row in rows]),
            "yawrate": stats([row.get("yawrate", float("nan")) for row in rows]),
            "s": stats([row.get("s", float("nan")) for row in rows]),
            "v": stats([row.get("v", float("nan")) for row in rows]),
        },
        "straightRegion": {
            "numSamples": len(straight),
            "e_t": stats(e_t),
            "e_psi": stats(e_psi),
            "delta_cmd": stats(delta),
        },
        "signDiagnosis": {
            "likelySignIssue": likely_sign_issue,
            "reason": reason,
            "corr_e_t_delta_cmd": corr_et_delta,
            "corr_e_t_steer_manual": corr_et_manual,
            "e_t_delta_cmd_vote": et_delta_vote,
            "e_t_steer_manual_vote": et_manual_vote,
            "recommendedAction": "Flip steerSign in init_slalom_mpc.m and rerun." if likely_sign_issue else "Keep steering sign; tune weights/rate/plant if tracking is weak.",
        },
        "events": {
            "first_abs_e_t_gt_0p1": first_et_01,
            "first_abs_e_t_gt_0p5": first_et_05,
            "first_abs_delta_cmd_gt_0p1": first_cmd_01,
        },
    }


def write_markdown(result: dict, output: Path) -> None:
    sign = result["signDiagnosis"]
    final = result["final"]
    stats_block = result["stats"]
    lines = [
        "# MPC Signal Diagnosis",
        "",
        f"- Generated: `{result['generatedAt']}`",
        f"- Input: `{result['inputDir']}`",
        f"- Time: `{fmt(result['timeRange']['start'])}` to `{fmt(result['timeRange']['end'])}` s, samples `{result['timeRange']['numSamples']}`",
        f"- Final s/v/t/e_t: `{fmt(final.get('s'))}` m, `{fmt(final.get('v'))}` m/s, `{fmt(final.get('t'))}` m, `{fmt(final.get('e_t'))}` m",
        "",
        "## Signal Map",
        "",
    ]
    for canonical, actual in result["signals"].items():
        lines.append(f"- `{canonical}` <- `{actual}`")
    lines.extend(
        [
            "",
            "## Key Metrics",
            "",
            f"- `maxAbs(e_t)`: `{fmt(stats_block['e_t']['maxAbs'])}`",
            f"- `rmse(e_t)`: `{fmt(stats_block['e_t']['rmse'])}`",
            f"- `maxAbs(e_psi)`: `{fmt(stats_block['e_psi']['maxAbs'])}`",
            f"- `maxAbs(delta_cmd)`: `{fmt(stats_block['delta_cmd']['maxAbs'])}`",
            "",
            "## Sign Diagnosis",
            "",
            f"- likely sign issue: `{sign['likelySignIssue']}`",
            f"- corr(e_t, delta_cmd): `{fmt(sign['corr_e_t_delta_cmd'])}`",
            f"- corr(e_t, steer_manual): `{fmt(sign['corr_e_t_steer_manual'])}`",
            f"- same-sign fraction e_t*delta_cmd: `{fmt(sign['e_t_delta_cmd_vote']['sameSignFraction'])}`",
            f"- opposite-sign fraction e_t*delta_cmd: `{fmt(sign['e_t_delta_cmd_vote']['oppositeSignFraction'])}`",
            f"- recommendation: `{sign['recommendedAction']}`",
            "",
        ]
    )
    if sign["reason"]:
        lines.append("Reasons:")
        for item in sign["reason"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend(["## Events", ""])
    for name, row in result["events"].items():
        if row is None:
            lines.append(f"- `{name}`: n/a")
        else:
            lines.append(
                f"- `{name}`: time `{fmt(row.get('Time'))}`, s `{fmt(row.get('s'))}`, "
                f"e_t `{fmt(row.get('e_t'))}`, delta `{fmt(row.get('delta_cmd'))}`"
            )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Simulink sigsOut CSV exports for slalom MPC debugging.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("llm_mpc_bo/results/processed/sigsOut_latest"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("llm_mpc_bo/results/processed/sigsOut_latest_analysis"),
    )
    args = parser.parse_args()

    result = analyze(args.input_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "diagnosis.json"
    md_path = args.output_dir / "diagnosis.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(result, md_path)
    print(json.dumps(result["signDiagnosis"], ensure_ascii=False, indent=2))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
