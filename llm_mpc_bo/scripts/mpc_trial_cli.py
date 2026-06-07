#!/usr/bin/env python3
"""Run one shared-MATLAB CarMaker/Simulink MPC trial and append a ledger row."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TUNED_KEYS = ("q_y", "q_psi", "q_r", "r_delta", "r_d_delta")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    experiment_dir = Path(args.experiment_dir).resolve()
    run_id = args.run_id or default_run_id(args.method, args.iter)
    trial_dir = experiment_dir / "trials" / run_id

    params = load_params(args)
    record = {
        "timestamp": now_iso(),
        "method": args.method,
        "iter": args.iter,
        "runId": run_id,
        "params": params,
        "experimentDir": str(experiment_dir),
        "trialDir": str(trial_dir),
        "dryRun": args.dry_run,
    }

    if args.dry_run:
        print(json.dumps(record, indent=2, ensure_ascii=False))
        return 0

    experiment_dir.mkdir(parents=True, exist_ok=True)
    trial_dir.mkdir(parents=True, exist_ok=True)
    write_experiment_config(experiment_dir, args, repo_root)

    if args.load_testrun:
        load_testrun(args, repo_root)

    try:
        matlab_result = run_matlab_trial(args, repo_root, trial_dir, params, run_id)
        record.update(matlab_result)
        record["ok"] = True
        if not args.skip_trial_plots:
            record["plots"] = generate_trial_plots(args, repo_root, trial_dir, run_id)
    except Exception as exc:  # keep a recoverable experiment ledger
        record.update(
            {
                "ok": False,
                "error": str(exc),
                "J": None,
                "status": "CLI_ERROR",
                "pylonHits": None,
            }
        )
        append_jsonl(experiment_dir / "trials.jsonl", record)
        update_best_summary(experiment_dir)
        print(json.dumps(compact_record(record), ensure_ascii=False))
        raise

    append_jsonl(experiment_dir / "trials.jsonl", record)
    update_best_summary(experiment_dir)
    print(json.dumps(compact_record(record), ensure_ascii=False))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one MPC weight trial through an already shared MATLAB engine."
    )
    parser.add_argument("--engine", help="Shared MATLAB engine name. Defaults to first shared engine.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Default: current directory.")
    parser.add_argument(
        "--experiment-dir",
        default="llm_mpc_bo/results/experiments/standard_slalom_latest",
        help="Experiment directory containing trials.jsonl and trial outputs.",
    )
    parser.add_argument("--method", default="manual", help="Method label, e.g. lhc, bo, llm_only, hybrid_bo.")
    parser.add_argument("--iter", type=int, default=None, help="Iteration number for the ledger.")
    parser.add_argument("--run-id", default=None, help="Trial run id. Default derives from method/iter/time.")

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--params-json", help="JSON object containing q_y, q_psi, q_r, r_delta, r_d_delta.")
    source.add_argument("--params-file", help="Path to a JSON parameter file.")
    source.add_argument("--normalized-json", help="JSON array of 5 normalized values in [0,1].")

    parser.add_argument("--host", default="localhost", help="CarMaker TCP host for optional TestRun load.")
    parser.add_argument("--port", type=int, default=16660, help="CarMaker TCP port for optional TestRun load.")
    parser.add_argument("--testrun", default="LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL")
    parser.add_argument("--load-testrun", action="store_true", help="Load the TestRun before simulation.")
    parser.add_argument("--allow-uncurated", action="store_true", help="Pass through to CarMaker runner.")

    parser.add_argument("--cm-src-dir", default=r"E:\CarMakerProject\AGI\src_cm4sl")
    parser.add_argument("--model", default="UserSteer")
    parser.add_argument("--results-mat", default=r"E:\CarMakerProject\AGI\src_cm4sl\Results.mat")
    parser.add_argument("--steering-gain", type=float, default=1.0, help="Simulink steering Gain block value.")
    parser.add_argument("--reset-mpc", action="store_true", help="Re-run init_slalom_mpc.m before applying params.")
    parser.add_argument("--skip-trial-plots", action="store_true", help="Skip automatic trajectory/time PNG generation.")
    parser.add_argument("--plot-python", default="py -3", help="Python command for matplotlib plotting. Default: py -3")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved config without running MATLAB.")
    return parser.parse_args()


def load_params(args: argparse.Namespace) -> dict[str, float]:
    if args.params_json:
        raw = json.loads(args.params_json)
    elif args.params_file:
        raw = json.loads(Path(args.params_file).read_text(encoding="utf-8"))
    else:
        values = json.loads(args.normalized_json)
        if not isinstance(values, list) or len(values) != 5:
            raise ValueError("--normalized-json must be a JSON array of 5 numbers")
        raw = decode_normalized(values)

    if not isinstance(raw, dict):
        raise ValueError("Parameters must be a JSON object")

    params: dict[str, float] = {}
    missing = [key for key in TUNED_KEYS if key not in raw]
    if missing:
        raise ValueError(f"Missing tuned parameter(s): {', '.join(missing)}")
    extra = sorted(set(raw) - set(TUNED_KEYS))
    if extra:
        raise ValueError(
            "Unexpected parameter(s): "
            + ", ".join(extra)
            + ". Main experiment tunes only q_y, q_psi, q_r, r_delta, r_d_delta."
        )

    for key in TUNED_KEYS:
        value = float(raw[key])
        if not value > 0:
            raise ValueError(f"{key} must be positive")
        params[key] = value
    return params


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "timestamp",
        "method",
        "iter",
        "runId",
        "ok",
        "J",
        "status",
        "pylonHits",
        "crashOrSimFail",
        "rmseET",
        "maxAbsET",
        "rmseDelta",
        "rmseDeltaRate",
        "maxYawRate",
        "duration",
        "engine",
        "error",
    )
    compact = {key: record[key] for key in keys if key in record}
    if "params" in record:
        compact["params"] = record["params"]
    if "trialDir" in record:
        compact["trialDir"] = record["trialDir"]
    if "plots" in record:
        compact["plots"] = record["plots"]
    return compact


def generate_trial_plots(
    args: argparse.Namespace,
    repo_root: Path,
    trial_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    script = repo_root / "llm_mpc_bo" / "scripts" / "plot_mpc_trial.py"
    command = args.plot_python.split() + [
        str(script),
        "--trial-dir",
        str(trial_dir),
        "--label",
        run_id,
    ]
    try:
        result = subprocess.run(
            command,
            cwd=str(repo_root),
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        return {"ok": True, "trajectory": payload.get("trajectory"), "time": payload.get("time")}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def decode_normalized(values: list[Any]) -> dict[str, float]:
    import math

    ranges = {
        "q_y": (0.1, 100.0),
        "q_psi": (0.1, 100.0),
        "q_r": (0.01, 30.0),
        "r_delta": (0.01, 10.0),
        "r_d_delta": (0.01, 10.0),
    }
    params: dict[str, float] = {}
    for key, raw in zip(TUNED_KEYS, values):
        x = float(raw)
        if x < 0 or x > 1:
            raise ValueError("Normalized values must be in [0, 1]")
        lo, hi = ranges[key]
        params[key] = 10 ** (math.log10(lo) + x * (math.log10(hi) - math.log10(lo)))
    return params


def run_matlab_trial(
    args: argparse.Namespace,
    repo_root: Path,
    trial_dir: Path,
    params: dict[str, float],
    run_id: str,
) -> dict[str, Any]:
    import matlab.engine

    engine_name = args.engine
    if not engine_name:
        engines = matlab.engine.find_matlab()
        if not engines:
            raise RuntimeError("No shared MATLAB engines found. Run matlab.engine.shareEngine in MATLAB.")
        engine_name = engines[0]

    eng = matlab.engine.connect_matlab(engine_name)
    matlab_cmd = build_matlab_command(args, repo_root, trial_dir, params, run_id)
    eng.eval(matlab_cmd, nargout=0)

    compact_json = eng.eval("jsonencode(cliTrialRecord)")
    result = json.loads(compact_json)
    result["engine"] = engine_name
    return result


def build_matlab_command(
    args: argparse.Namespace,
    repo_root: Path,
    trial_dir: Path,
    params: dict[str, float],
    run_id: str,
) -> str:
    params_json = json.dumps(params, separators=(",", ":"))
    repo = matlab_quote(str(repo_root))
    cm_src = matlab_quote(args.cm_src_dir)
    model = matlab_quote(args.model)
    results_mat = matlab_quote(args.results_mat)
    out_dir = matlab_quote(str(trial_dir))
    run_id_q = matlab_quote(run_id)
    params_q = matlab_quote(params_json)
    steering_gain = f"{args.steering_gain:.17g}"
    reset_expr = "true" if args.reset_mpc else "false"

    return f"""
repoRoot = '{repo}';
cmProjectSrcDir = '{cm_src}';
mdl = '{model}';
resultsMatPath = '{results_mat}';
outputDir = '{out_dir}';
runId = '{run_id_q}';
params = jsondecode('{params_q}');
cd(cmProjectSrcDir);
addpath(fullfile(repoRoot, 'llm_mpc_bo', 'simulink'));
addpath(fullfile(repoRoot, 'llm_mpc_bo', 'scripts'));
if exist('cmenv', 'file') == 2
    evalc('cmenv;');
end
if {reset_expr} || evalin('base', "exist('mpcobj','var')") ~= 1
    evalin('base', sprintf("run('%s')", fullfile(repoRoot, 'llm_mpc_bo', 'simulink', 'init_slalom_mpc.m')));
end
if ~bdIsLoaded(mdl)
    open_system(mdl);
end
steerGainBlock = [mdl '/CarMaker/VehicleControl/CreateBus VhclCtrl.Steering/Gain'];
if getSimulinkBlockHandle(steerGainBlock) ~= -1
    set_param(steerGainBlock, 'Gain', '{steering_gain}');
end
evalc('mpcobj = apply_slalom_mpc_params(params);');
if exist(resultsMatPath, 'file')
    beforeInfo = dir(resultsMatPath);
    beforeDatenum = beforeInfo.datenum;
else
    beforeDatenum = -Inf;
end
simStart = datetime('now');
evalc('simOut = sim(mdl);');
simEnd = datetime('now');
assignin('base', 'simOut', simOut);
if ~exist(resultsMatPath, 'file')
    error('Results.mat was not created: %s', resultsMatPath);
end
afterInfo = dir(resultsMatPath);
if afterInfo.datenum <= beforeDatenum
    error('Results.mat timestamp did not advance. Old/new datenum: %.12f / %.12f', beforeDatenum, afterInfo.datenum);
end
summary = analyze_results_mat(resultsMatPath, outputDir, 'applied', '', false, '{matlab_quote(args.testrun)}');
cliTrialRecord = struct();
cliTrialRecord.runId = runId;
cliTrialRecord.params = params;
cliTrialRecord.outputDir = outputDir;
cliTrialRecord.resultsMatPath = resultsMatPath;
cliTrialRecord.simStart = char(simStart);
cliTrialRecord.simEnd = char(simEnd);
cliTrialRecord.J = summary.objective.JFailClosed;
cliTrialRecord.status = char(summary.objective.ergStatus);
cliTrialRecord.pylonHits = summary.objective.NViolation;
cliTrialRecord.crashOrSimFail = summary.objective.crashOrSimFail;
cliTrialRecord.rmseET = summary.metrics.rmseET;
cliTrialRecord.maxAbsET = summary.metrics.maxAbsET;
cliTrialRecord.rmseEPsi = summary.metrics.rmseEPsi;
cliTrialRecord.maxAbsEPsi = summary.metrics.maxAbsEPsi;
cliTrialRecord.rmseDelta = summary.metrics.rmseAppliedDeltaCmd;
cliTrialRecord.maxAbsDelta = summary.metrics.maxAbsAppliedDeltaCmd;
cliTrialRecord.rmseDeltaRate = summary.metrics.rmseAppliedDeltaRate;
cliTrialRecord.maxYawRate = summary.metrics.maxAbsYawRate;
cliTrialRecord.finalS = summary.finalS;
cliTrialRecord.finalV = summary.finalV;
cliTrialRecord.duration = summary.duration;
cliTrialRecord.steeringGain = {steering_gain};
cliTrialRecord.mvMin = mpcobj.MV.Min;
cliTrialRecord.mvMax = mpcobj.MV.Max;
cliTrialRecord.mvRateMin = mpcobj.MV.RateMin;
cliTrialRecord.mvRateMax = mpcobj.MV.RateMax;
trialSummaryPath = fullfile(outputDir, 'trial_summary.json');
fid = fopen(trialSummaryPath, 'w');
if fid < 0
    error('Failed to open trial summary for writing: %s', trialSummaryPath);
end
fprintf(fid, '%s\\n', jsonencode(cliTrialRecord, PrettyPrint=true));
fclose(fid);
assignin('base', 'cliTrialRecord', cliTrialRecord);
"""


def load_testrun(args: argparse.Namespace, repo_root: Path) -> None:
    runner = repo_root / "workspace" / "carmaker_llm_scenario_skill" / "agent" / "carmaker_research_runner.py"
    command = [
        sys.executable,
        str(runner),
        "load",
        "--direct-carmaker",
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--testrun",
        args.testrun,
    ]
    if args.allow_uncurated:
        command.append("--allow-uncurated")
    subprocess.run(command, check=True, cwd=str(repo_root))


def write_experiment_config(experiment_dir: Path, args: argparse.Namespace, repo_root: Path) -> None:
    path = experiment_dir / "experiment_config.json"
    if path.exists():
        return
    config = {
        "createdAt": now_iso(),
        "repoRoot": str(repo_root),
        "scenario": args.testrun,
        "model": args.model,
        "cmSrcDir": args.cm_src_dir,
        "resultsMat": args.results_mat,
        "tunedKeys": list(TUNED_KEYS),
        "fixedConstraints": {
            "mvMin": -12.0,
            "mvMax": 12.0,
            "mvRateMin": -0.6,
            "mvRateMax": 0.6,
        },
    }
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def update_best_summary(experiment_dir: Path) -> None:
    ledger = experiment_dir / "trials.jsonl"
    if not ledger.exists():
        return
    best: dict[str, Any] | None = None
    count = 0
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        count += 1
        row = json.loads(line)
        if not row.get("ok", False):
            continue
        j = row.get("J")
        if j is None:
            continue
        if best is None or float(j) < float(best["J"]):
            best = row
    summary = {"updatedAt": now_iso(), "trialCount": count, "best": best}
    (experiment_dir / "best_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def default_run_id(method: str, iteration: int | None) -> str:
    if iteration is not None:
        return f"{method}_{iteration:04d}"
    return f"{method}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def matlab_quote(value: str) -> str:
    return value.replace("'", "''")


if __name__ == "__main__":
    raise SystemExit(main())
