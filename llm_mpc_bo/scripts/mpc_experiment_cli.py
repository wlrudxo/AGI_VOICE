#!/usr/bin/env python3
"""Run resumable MPC tuning experiments on top of mpc_trial_cli.py."""

from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TUNED_KEYS = ("q_y", "q_psi", "q_r", "r_delta", "r_d_delta")
LOG_RANGES = {
    "q_y": (0.1, 100.0),
    "q_psi": (0.1, 100.0),
    "q_r": (0.01, 30.0),
    "r_delta": (0.01, 10.0),
    "r_d_delta": (0.01, 10.0),
}


@dataclass(frozen=True)
class Candidate:
    method: str
    iteration: int
    run_id: str
    normalized: list[float]
    params: dict[str, float]
    source: str


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    experiment_dir = Path(args.experiment_dir).resolve()
    experiment_dir.mkdir(parents=True, exist_ok=True)

    rows = read_ledger(experiment_dir / "trials.jsonl")
    completed = completed_iterations(rows, args.method)

    if args.dry_run:
        candidates = plan_candidates(args, experiment_dir, rows, completed)
        print(json.dumps([candidate_to_json(c) for c in candidates], indent=2, ensure_ascii=False))
        return 0

    if args.strategy == "bo":
        for _ in range(args.count):
            rows = read_ledger(experiment_dir / "trials.jsonl")
            completed = completed_iterations(rows, args.method)
            candidate = plan_bo_candidate(args, experiment_dir, rows, completed)
            run_trial(args, repo_root, experiment_dir, candidate)
        return 0

    candidates = plan_candidates(args, experiment_dir, rows, completed)
    for candidate in candidates:
        run_trial(args, repo_root, experiment_dir, candidate)

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run/resume fixed-budget MPC tuning experiments using mpc_trial_cli.py."
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--experiment-dir",
        default="llm_mpc_bo/results/experiments/standard_slalom_latest",
    )
    parser.add_argument("--strategy", choices=["lhc", "random", "bo"], required=True)
    parser.add_argument("--method", default=None, help="Ledger method label. Defaults to strategy.")
    parser.add_argument("--count", type=int, required=True, help="Number of new trials to run.")
    parser.add_argument("--budget", type=int, default=None, help="Total planned trials for LHC/random plan.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--bo-init", type=int, default=10, help="Random/LHC observations before BO exploitation.")
    parser.add_argument("--bo-candidates", type=int, default=512, help="Candidate pool size for BO acquisition.")
    parser.add_argument("--engine", default=None)
    parser.add_argument("--trial-cli", default="llm_mpc_bo/scripts/mpc_trial_cli.py")
    parser.add_argument("--load-testrun", action="store_true")
    parser.add_argument("--allow-uncurated", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.count < 0:
        parser.error("--count must be non-negative")
    if args.budget is not None and args.budget < args.count:
        parser.error("--budget must be >= --count")
    if args.method is None:
        args.method = args.strategy
    if args.budget is None:
        args.budget = max(args.count, 30)
    return args


def plan_candidates(
    args: argparse.Namespace,
    experiment_dir: Path,
    rows: list[dict[str, Any]],
    completed: set[int],
) -> list[Candidate]:
    if args.count == 0:
        return []

    if args.strategy in {"lhc", "random"}:
        plan = load_or_create_space_plan(experiment_dir, args.strategy, args.seed, args.budget)
        iterations = next_missing_iterations(completed, args.budget, args.count)
        return [
            make_candidate(args.method, iteration, plan[iteration - 1], args.strategy)
            for iteration in iterations
        ]

    return plan_bo_candidates(args, experiment_dir, rows, completed)


def load_or_create_space_plan(
    experiment_dir: Path, strategy: str, seed: int, budget: int
) -> list[list[float]]:
    path = experiment_dir / f"candidate_plan_{strategy}_seed{seed}_budget{budget}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data["normalizedCandidates"]

    rng = random.Random(seed)
    if strategy == "lhc":
        plan = latin_hypercube(budget, len(TUNED_KEYS), rng)
    else:
        plan = [[rng.random() for _ in TUNED_KEYS] for _ in range(budget)]

    payload = {
        "strategy": strategy,
        "seed": seed,
        "budget": budget,
        "tunedKeys": list(TUNED_KEYS),
        "normalizedCandidates": plan,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return plan


def latin_hypercube(n: int, d: int, rng: random.Random) -> list[list[float]]:
    columns: list[list[float]] = []
    for _ in range(d):
        values = [(i + rng.random()) / n for i in range(n)]
        rng.shuffle(values)
        columns.append(values)
    return [[columns[j][i] for j in range(d)] for i in range(n)]


def plan_bo_candidates(
    args: argparse.Namespace,
    experiment_dir: Path,
    rows: list[dict[str, Any]],
    completed: set[int],
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for _ in range(args.count):
        candidate = plan_bo_candidate(args, experiment_dir, rows, completed)
        candidates.append(candidate)
        if args.dry_run:
            # For dry-run, pretend it would occupy the next iteration so the
            # printed plan contains distinct future rows.
            rows.append(
                {
                    "ok": True,
                    "method": args.method,
                    "iter": candidate.iteration,
                    "params": candidate.params,
                    "J": 1.0e9,
                }
            )
            completed.add(candidate.iteration)
    return candidates


def plan_bo_candidate(
    args: argparse.Namespace,
    experiment_dir: Path,
    rows: list[dict[str, Any]],
    completed: set[int],
) -> Candidate:
    next_iter = first_missing_iteration(completed)
    observations = successful_observations(rows)

    if len(observations) < args.bo_init:
        plan = load_or_create_space_plan(experiment_dir, "lhc", args.seed, max(args.bo_init, args.budget))
        normalized = plan[len(observations)]
        source = "bo_init_lhc"
    else:
        normalized = propose_bo_candidate(observations, args.seed + next_iter, args.bo_candidates)
        source = "bo_expected_improvement"

    return make_candidate(args.method, next_iter, normalized, source)


def propose_bo_candidate(
    observations: list[tuple[list[float], float]],
    seed: int,
    pool_size: int,
) -> list[float]:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("BO strategy requires numpy. Use --strategy lhc first or install numpy.") from exc

    x_obs = np.array([x for x, _ in observations], dtype=float)
    y_obs = np.array([y for _, y in observations], dtype=float)
    y_best = float(np.min(y_obs))

    rng = np.random.default_rng(seed)
    pool = rng.random((pool_size, len(TUNED_KEYS)))
    # Always include local perturbations around the current best observation.
    best_x = x_obs[int(np.argmin(y_obs))]
    local = np.clip(best_x + rng.normal(0.0, 0.12, size=(max(32, pool_size // 4), len(TUNED_KEYS))), 0.0, 1.0)
    pool = np.vstack([pool, local])

    mu, sigma = gp_predict(x_obs, y_obs, pool)
    ei = expected_improvement(mu, sigma, y_best)
    order = np.argsort(-ei)
    for idx in order:
        candidate = pool[int(idx)]
        if min_distance(candidate, x_obs) > 1e-4:
            return [float(v) for v in candidate]
    return [float(v) for v in pool[int(order[0])]]


def gp_predict(x_obs: Any, y_obs: Any, x_new: Any) -> tuple[Any, Any]:
    import numpy as np

    length_scale = 0.35
    noise = 1e-6

    def kernel(a: Any, b: Any) -> Any:
        a2 = np.sum(a * a, axis=1)[:, None]
        b2 = np.sum(b * b, axis=1)[None, :]
        dist2 = np.maximum(a2 + b2 - 2 * a @ b.T, 0.0)
        return np.exp(-0.5 * dist2 / (length_scale * length_scale))

    y_mean = float(np.mean(y_obs))
    y_std = float(np.std(y_obs)) or 1.0
    y_scaled = (y_obs - y_mean) / y_std

    k_xx = kernel(x_obs, x_obs) + noise * np.eye(len(x_obs))
    k_xs = kernel(x_obs, x_new)
    k_ss_diag = np.ones(x_new.shape[0])
    chol = np.linalg.cholesky(k_xx)
    alpha = np.linalg.solve(chol.T, np.linalg.solve(chol, y_scaled))
    mu_scaled = k_xs.T @ alpha
    v = np.linalg.solve(chol, k_xs)
    var = np.maximum(k_ss_diag - np.sum(v * v, axis=0), 1e-12)
    return y_mean + y_std * mu_scaled, y_std * np.sqrt(var)


def expected_improvement(mu: Any, sigma: Any, y_best: float) -> Any:
    import numpy as np

    z = (y_best - mu) / np.maximum(sigma, 1e-12)
    cdf = 0.5 * (1.0 + np.vectorize(math.erf)(z / math.sqrt(2.0)))
    pdf = np.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    return (y_best - mu) * cdf + sigma * pdf


def min_distance(candidate: Any, x_obs: Any) -> float:
    import numpy as np

    return float(np.min(np.linalg.norm(x_obs - candidate[None, :], axis=1)))


def make_candidate(method: str, iteration: int, normalized: list[float], source: str) -> Candidate:
    return Candidate(
        method=method,
        iteration=iteration,
        run_id=f"{method}_{iteration:04d}",
        normalized=[float(v) for v in normalized],
        params=decode_normalized(normalized),
        source=source,
    )


def run_trial(args: argparse.Namespace, repo_root: Path, experiment_dir: Path, candidate: Candidate) -> None:
    command = [
        sys.executable,
        str((repo_root / args.trial_cli).resolve()),
        "--repo-root",
        str(repo_root),
        "--experiment-dir",
        str(experiment_dir),
        "--method",
        candidate.method,
        "--iter",
        str(candidate.iteration),
        "--run-id",
        candidate.run_id,
        "--params-json",
        json.dumps(candidate.params, separators=(",", ":")),
    ]
    if args.engine:
        command.extend(["--engine", args.engine])
    if args.load_testrun:
        command.append("--load-testrun")
    if args.allow_uncurated:
        command.append("--allow-uncurated")

    candidate_path = experiment_dir / "candidates.jsonl"
    append_jsonl(candidate_path, candidate_to_json(candidate))
    subprocess.run(command, cwd=str(repo_root), check=True)


def read_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def completed_iterations(rows: list[dict[str, Any]], method: str) -> set[int]:
    done = set()
    for row in rows:
        if row.get("method") != method:
            continue
        if row.get("ok") is True and row.get("iter") is not None:
            done.add(int(row["iter"]))
    return done


def successful_observations(rows: list[dict[str, Any]]) -> list[tuple[list[float], float]]:
    observations = []
    for row in rows:
        if row.get("ok") is not True or row.get("J") is None:
            continue
        params = row.get("params") or {}
        if not all(key in params for key in TUNED_KEYS):
            continue
        observations.append((encode_normalized(params), float(row["J"])))
    return observations


def next_missing_iterations(completed: set[int], budget: int, count: int) -> list[int]:
    iterations = []
    for iteration in range(1, budget + 1):
        if iteration not in completed:
            iterations.append(iteration)
            if len(iterations) >= count:
                return iterations
    raise RuntimeError(f"No remaining iterations in budget={budget}; completed={len(completed)}")


def first_missing_iteration(completed: set[int]) -> int:
    iteration = 1
    while iteration in completed:
        iteration += 1
    return iteration


def decode_normalized(values: list[float]) -> dict[str, float]:
    params = {}
    for key, x in zip(TUNED_KEYS, values):
        lo, hi = LOG_RANGES[key]
        params[key] = 10 ** (math.log10(lo) + float(x) * (math.log10(hi) - math.log10(lo)))
    return params


def encode_normalized(params: dict[str, Any]) -> list[float]:
    encoded = []
    for key in TUNED_KEYS:
        lo, hi = LOG_RANGES[key]
        value = float(params[key])
        encoded.append((math.log10(value) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)))
    return [min(1.0, max(0.0, v)) for v in encoded]


def candidate_to_json(candidate: Candidate) -> dict[str, Any]:
    return {
        "method": candidate.method,
        "iter": candidate.iteration,
        "runId": candidate.run_id,
        "source": candidate.source,
        "normalized": candidate.normalized,
        "params": candidate.params,
    }


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
