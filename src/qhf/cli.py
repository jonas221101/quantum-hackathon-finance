"""Command line: ``run`` the full pipeline into results/<run_id>/ and ``diff`` two runs."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from dataclasses import replace
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from qhf import plots  # noqa: E402
from qhf.circuits import dicke_circuit, qaoa_circuit  # noqa: E402
from qhf.config import DEFAULT_CONFIG, FAST_QAOA, REPO_ROOT, Config, apply_overrides, config_hash, config_to_dict  # noqa: E402
from qhf.data import estimation_slice, evaluation_slice, load_returns  # noqa: E402
from qhf.decision import NONE_ADMISSIBLE, break_even, decide  # noqa: E402
from qhf.evaluation import holdout_table, rule_table  # noqa: E402
from qhf.exact import NoAdmissiblePortfolio, optimum, rank_portfolios  # noqa: E402
from qhf.portfolio import breach_count, label, selection, whole_portfolio_loss_probability  # noqa: E402
from qhf.qaoa import (  # noqa: E402
    build_problem,
    circuit_resources,
    method_qubo,
    random_floors,
    run_experiment,
    shot_noisy_comparison,
    summarise,
)
from qhf.scenarios import moments, scenario_sets  # noqa: E402
from qhf.sensitivity import decision_map, robustness_table, strict_convention_optima  # noqa: E402

DIGITS = 10
FAST_BOOTSTRAP_SAMPLES = 100


def _round(value: Any, digits: int = DIGITS) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, float):
        return None if np.isnan(value) else round(value, digits)
    if isinstance(value, dict):
        return {str(k): _round(v, digits) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_round(v, digits) for v in value]
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return _round(value.item(), digits)
    return value


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, float_format=f"%.{DIGITS}g")


def exact_section(scenarios: dict[str, np.ndarray], config: Config) -> tuple[dict, pd.DataFrame]:
    current, proposal = selection(config.current, config), selection(config.proposal, config)
    summary, tables = {}, []
    for profile in config.profiles:
        summary[profile.name] = {}
        for name, outcomes in scenarios.items():
            mu, sigma = moments(outcomes, config.ddof)
            table = rank_portfolios(mu, sigma, outcomes, profile, config)
            try:
                best = optimum(table)
                best_name, best_objective = best["holdings"], best["objective"]
            except NoAdmissiblePortfolio:
                best_name, best_objective = NONE_ADMISSIBLE, None
            rank = table.loc[table.holdings == label(current, config), "rank"]
            summary[profile.name][name] = {
                "optimum": best_name, "objective": best_objective,
                "admissible_count": int(table.passes_loss_rule.sum()),
                "ties_at_optimum": int(table.tied_with_optimum.sum()),
                "current_rank": None if rank.empty or pd.isna(rank.iloc[0]) else int(rank.iloc[0]),
                "proposal_breaches": breach_count(proposal, outcomes, profile.loss_threshold, config),
                "allowed_breaches": int(table.allowed_breaches.iloc[0]),
            }
            tables.append(table.assign(profile=profile.name, scenario=name))
    return summary, pd.concat(tables, ignore_index=True)


def _draw(circuit) -> str:
    """Text diagram; silences Qiskit's console-encoding warning on Windows (output is written as UTF-8)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return str(circuit.draw("text", fold=200))


def circuit_diagrams(problems: dict, config: Config) -> dict[str, str]:
    problem = problems.get(config.default_profile, next(iter(problems.values())))
    gamma, beta = (np.array([a]) for a in config.analysis.diagram_angles)
    m = problem.qubo.size
    return {
        f"Dicke state preparation |D({m},{config.cardinality})> (Bärtschi–Eidenbenz)":
            _draw(dicke_circuit(m, config.cardinality)),
        "One QAOA layer, rule-preserving (cost + XY mixer)":
            _draw(qaoa_circuit("dicke_xy", problem.qubo, problem.scale, gamma, beta, config.cardinality)),
        "One QAOA layer, penalty baseline (cost + X mixer)":
            _draw(qaoa_circuit("x_penalty", method_qubo(problem, "x_penalty", config), problem.scale, gamma, beta,
                               config.cardinality)),
    }


def computational_rows(runs: pd.DataFrame, config: Config) -> pd.DataFrame:
    rows = []
    for method in sorted(runs.method.unique()):
        for profile in config.profiles:
            part = runs[(runs.method == method) & (runs.profile == profile.name)]
            rows.append({"category": "computational", "change": f"QAOA {method}, all layers and seeds",
                         "profile": profile.name,
                         "optimum": f"decoded = exact answer in {part.decoded_is_optimum.mean():.0%} of runs",
                         "same_as_base": bool(part.decoded_is_optimum.all())})
    return pd.DataFrame(rows)


def run(config: Config, out_dir: Path, fast: bool) -> dict:
    timings: dict[str, float] = {}
    tick = time.perf_counter()
    figures = out_dir / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    returns = load_returns(config)
    estimation, evaluation = estimation_slice(returns, config), evaluation_slice(returns, config)
    scenarios = scenario_sets(estimation, config)
    base = scenarios["base"]
    current, proposal = selection(config.current, config), selection(config.proposal, config)

    exact, rankings = exact_section(scenarios, config)
    _write_csv(rankings, out_dir / "exact_rankings.csv")
    verdicts = {p.name: decide(scenarios, p, config) for p in config.profiles}
    timings["exact_and_bootstrap"] = time.perf_counter() - tick

    break_evens = {p.name: {param: break_even(base, p, config, param, lo, hi, log_scale=log)
                            for param, lo, hi, log in config.analysis.break_even_ranges}
                   for p in config.profiles}
    robustness = robustness_table(scenarios, config)
    default = config.profile(config.default_profile)
    maps = {axis: decision_map(base, default, config, axis) for axis in ("hitec_shift", "change_penalty")}
    timings["sensitivity"] = time.perf_counter() - tick

    mu, sigma = moments(base, config.ddof)
    problems = {p.name: build_problem(mu, sigma, base, p, config) for p in config.profiles}
    runs = run_experiment(problems, config)
    if config.cvar_variant:
        runs = pd.concat([runs, run_experiment(problems, config, cvar=True)], ignore_index=True)
    _write_csv(runs, out_dir / "quantum_runs.csv")
    floors = random_floors(problems)
    quantum = summarise(runs, floors)
    _write_csv(quantum, out_dir / "quantum_summary.csv")
    resources = circuit_resources(problems[config.default_profile], config, config.qaoa.layers)
    noisy = shot_noisy_comparison(problems, config, layers=min(2, max(config.qaoa.layers)))
    _write_csv(noisy, out_dir / "quantum_shot_noise.csv")
    timings["quantum"] = time.perf_counter() - tick

    robustness = pd.concat([robustness, computational_rows(runs, config)], ignore_index=True)
    _write_csv(robustness, out_dir / "sensitivity.csv")
    for axis, grid in maps.items():
        _write_csv(grid, out_dir / f"decision_map_{axis}.csv")

    recommended = {p.name: selection(tuple(verdicts[p.name].target.split("+")), config) for p in config.profiles}
    holdout_portfolios = {"current": current, "proposal": proposal,
                          **{f"recommended_{name}": x for name, x in recommended.items()}}
    holdout = holdout_table(evaluation, holdout_portfolios, config)
    rules = rule_table(evaluation, {"current": current, "proposal": proposal}, config)
    _write_csv(holdout, out_dir / "holdout.csv")
    _write_csv(rules, out_dir / "holdout_rules.csv")
    whole = {p.name: {role: whole_portfolio_loss_probability(x, base, p, config)
                      for role, x in {"current": current, "proposal": proposal, "recommended": recommended[p.name]}.items()}
             for p in config.profiles}

    base_table = rankings[(rankings.profile == config.default_profile) & (rankings.scenario == "base")]
    plots.risk_return(base_table, config, figures / "fig_risk_return.png")
    plots.decision_map(maps["hitec_shift"], config, figures / "fig_decision_map.png", axis="hitec_shift")
    plots.decision_map(maps["change_penalty"], config, figures / "fig_decision_map_cost.png", axis="change_penalty")
    plots.bootstrap({k: v.evidence for k, v in verdicts.items()}, config, figures / "fig_bootstrap.png")
    plots.qaoa_comparison(quantum, figures / "fig_qaoa_comparison.png")
    plots.circuits(circuit_diagrams(problems, config), figures / "fig_circuits.png")
    plots.holdout(evaluation, {"current": current, "proposal": proposal}, config, figures / "fig_holdout.png")
    timings["total"] = time.perf_counter() - tick

    summary = {
        "config": config_to_dict(config),
        "config_hash": config_hash(config),
        "fast": fast,
        "exact": exact,
        "strict_loss_rule_optima": strict_convention_optima(scenarios, config),
        "verdicts": {k: {"verdict": v.verdict, "target": v.target, "candidate": v.candidate, "reason": v.reason,
                         "action": v.action, "optima": v.optima, "margin": v.margin,
                         "bootstrap_candidate_beats_current": v.evidence.target_beats_current,
                         "bootstrap_candidate_admissible": v.evidence.target_admissible,
                         "bootstrap_current_admissible": v.evidence.current_admissible,
                         "bootstrap_none_admissible": v.evidence.none_admissible,
                         "is_default_profile": v.is_default_profile}
                     for k, v in verdicts.items()},
        "break_even": break_evens,
        "bootstrap": {k: v.evidence.modal for k, v in verdicts.items()},
        "quantum": {
            "summary": quantum.to_dict(orient="records"),
            "random_guess_p_opt": floors,
            "h1_minimum_is_admissible": {k: p.h1_minimum_is_admissible for k, p in problems.items()},
            "circuit_resources": resources.to_dict(orient="records"),
            "shot_noisy_optimisation": noisy.groupby(["profile", "method", "mode"])[["p_opt", "h1_mass", "nfev"]]
                .median().reset_index().to_dict(orient="records"),
            "notes": ["ideal noiseless simulation", "Dicke+XY searches the valid states only, penalty QAOA all basis states",
                      "optimisation on exact expectations is optimistic; see shot_noisy_optimisation",
                      "mean-cost optimisation does not maximise P(opt); see min-max and share_below_random_floor",
                      "budget = equal restarts and maxiter per method; evaluations reported as nfev",
                      "no quantum-advantage claim: the options are enumerated exactly in milliseconds"],
        },
        "holdout": {"buy_and_hold": holdout.to_dict(orient="records"), "rules": rules.to_dict(orient="records")},
        "whole_portfolio": whole,
    }
    summary = _round(summary)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    (out_dir / "timings.json").write_text(json.dumps(_round(timings, 2), indent=2), encoding="utf-8")
    return summary


def print_report(summary: dict) -> None:
    print("Verdicts (exact answer key):")
    for name, v in summary["verdicts"].items():
        print(f"  {name:15s} {v['verdict']:7s} target={v['target']:18s} candidate beats current in "
              f"{v['bootstrap_candidate_beats_current']:.0%} of resamples | {v['reason']}")
    print("Quantum (median P(best) at the deepest layer):")
    rows = summary["quantum"]["summary"]
    deepest = max(r["layers"] for r in rows)
    for r in rows:
        if r["layers"] == deepest:
            print(f"  {r['profile']:15s} {r['method']:22s} P(best)={r['p_opt_median']:.2f}  valid={r['h1_mass_median']:.0%}"
                  f"  decoded=exact in {r['decoded_is_optimum_share']:.0%}")


def diff(a: Path, b: Path) -> list[str]:
    left = json.loads((a / "summary.json").read_text(encoding="utf-8"))
    right = json.loads((b / "summary.json").read_text(encoding="utf-8"))
    changed = sorted(k for k in left["config"] if left["config"][k] != right["config"].get(k))
    lines = [f"config fields changed: {changed or 'none'}"]
    for name in left["verdicts"]:
        lv, rv = left["verdicts"][name], right["verdicts"].get(name, {})
        for key in ("verdict", "target", "reason"):
            if lv.get(key) != rv.get(key):
                lines.append(f"{name}: {key} '{lv.get(key)}' -> '{rv.get(key)}'")
        for scen, opt in lv["optima"].items():
            if rv.get("optima", {}).get(scen) != opt:
                lines.append(f"{name}: optimum under {scen} {opt} -> {rv['optima'].get(scen)}")
        for scen in left["exact"][name]:
            la, ra = left["exact"][name][scen], right["exact"][name][scen]
            if la["admissible_count"] != ra["admissible_count"]:
                lines.append(f"{name}: admissible portfolios under {scen} {la['admissible_count']} -> {ra['admissible_count']}")
        for param, points in left["break_even"][name].items():
            new = right["break_even"][name].get(param)
            if new != points:
                lines.append(f"{name}: break-even {param} {[p['value'] for p in points]} -> {[p['value'] for p in new or []]}")
    return lines


def build_config(overrides: list[str], fast: bool, no_cvar: bool) -> Config:
    base = DEFAULT_CONFIG
    if fast:
        base = replace(base, qaoa=FAST_QAOA, bootstrap_samples=FAST_BOOTSTRAP_SAMPLES, cvar_variant=False)
    if no_cvar:
        base = replace(base, cvar_variant=False)
    return apply_overrides(base, overrides)  # explicit overrides always win


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qhf", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run", help="run the full pipeline")
    run_p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override a parameter (repeatable)")
    run_p.add_argument("--fast", action="store_true", help="small QAOA grid and bootstrap (demo / tests)")
    run_p.add_argument("--canonical", action="store_true", help="write to results/canonical (full default run only)")
    run_p.add_argument("--no-cvar", action="store_true", help="skip the CVaR-objective variant")
    run_p.add_argument("--out", default=str(REPO_ROOT / "results"), help="results root folder")
    diff_p = sub.add_parser("diff", help="compare two runs")
    diff_p.add_argument("run_a")
    diff_p.add_argument("run_b")
    args = parser.parse_args(argv)

    if args.command == "diff":
        root = REPO_ROOT / "results"
        resolve = lambda r: Path(r) if Path(r).exists() else root / r  # noqa: E731
        for line in diff(resolve(args.run_a), resolve(args.run_b)):
            print(line)
        return 0

    if args.canonical and (args.fast or args.set or args.no_cvar):
        parser.error("--canonical is only for the full default run (no --fast, --set or --no-cvar)")
    config = build_config(args.set, args.fast, args.no_cvar)
    run_id = "canonical" if args.canonical else f"run_{config_hash(config)[:8]}{'_fast' if args.fast else ''}"
    out_dir = Path(args.out) / run_id  # same config → same id → identical, deterministic content
    summary = run(config, out_dir, fast=args.fast)
    print_report(summary)
    print(f"results written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
