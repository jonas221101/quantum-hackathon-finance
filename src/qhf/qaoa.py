"""Quantum-vs-quantum experiment: rule-preserving QAOA (Dicke start + XY mixer) vs penalty QAOA (X mixer).

Budget rule: every method gets the same seeds, the same shared start draws (mapped to one γ period of its own
cost spectrum), the same COBYLA settings and the same number of restarts (equal restarts, not equal
evaluations; evaluations are reported as ``nfev``). Optimisation minimises the expected cost (or the CVaR
objective), which does not maximise P(optimum); results are therefore reported over seeds with min–max and
the share of seeds below random guessing. Ideal, noiseless simulation; no quantum-advantage claim.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from qiskit.primitives import StatevectorSampler
from scipy.optimize import minimize

from qhf.bits import all_states, bits_to_index, embed, qiskit_key_to_bits
from qhf.circuits import gate_counts, qaoa_circuit
from qhf.config import Config, Profile, QaoaSettings
from qhf.exact import free_indices
from qhf.kernel import QaoaKernel, dicke_vector, uniform_vector
from qhf.portfolio import cap_excess, passes_loss_rule
from qhf.qubo import Qubo, build_qubo, energies, with_cardinality_penalty

METHODS = ("x_penalty", "x_penalty_tuned", "dicke_xy")
SAMPLE_SALT, SHOT_SALT = 7, 99  # fixed extra entropy words separating the sampling and shot-noise streams


@dataclass(frozen=True)
class Problem:
    profile: Profile
    free: list[int]
    qubo: Qubo  # financial objective only
    energy: np.ndarray  # financial energy of every basis state on the free qubits
    h1: np.ndarray  # exactly K holdings
    h3: np.ndarray  # passes the binding loss rule (False where h1 fails)
    cap_ok: np.ndarray  # respects the cap preference
    optimum: int  # basis index of the admissible optimum (answer key)
    second: int  # second-best admissible state, −1 if only one is admissible
    scale: float  # energy range over H1-feasible states (common normaliser)
    h1_minimum_is_admissible: bool  # False → the loss-rule post-check removes the cost minimum, P(opt) is bounded


def build_problem(mu: np.ndarray, sigma: np.ndarray, outcomes: np.ndarray, profile: Profile, config: Config) -> Problem:
    free = free_indices(config)
    n = len(config.industries)
    qubo = build_qubo(mu, sigma, profile, config, free)
    energy = energies(qubo)
    states = all_states(len(free))
    h1 = states.sum(axis=1) == config.cardinality
    full = [embed(s, free, n) for s in states]
    h3 = np.array([bool(ok) and passes_loss_rule(x, outcomes, profile, config) for ok, x in zip(h1, full)])
    cap_ok = np.array([cap_excess(x, profile, config) <= 0 for x in full])
    admissible = np.flatnonzero(h1 & h3)
    if admissible.size == 0:
        raise ValueError(f"no admissible portfolio for {profile.name}")
    order = admissible[np.lexsort((admissible, energy[admissible]))]
    h1_states = np.flatnonzero(h1)
    h1_minimum = int(h1_states[np.lexsort((h1_states, energy[h1_states]))][0])
    scale = float(np.ptp(energy[h1])) or 1.0
    second = int(order[1]) if order.size > 1 else -1
    return Problem(profile, free, qubo, energy, h1, h3, cap_ok, int(order[0]), second, scale, h1_minimum == int(order[0]))


def tuned_penalty(problem: Problem, config: Config, iterations: int = 60) -> float:
    """Stronger baseline: critical penalty P* (smallest P whose global minimum has K holdings) × (1 + margin).

    Returns 0 when the unpenalised minimum already has K holdings (the method is then plain X-mixer QAOA).
    """
    counts = all_states(problem.qubo.size).sum(axis=1)
    violation = (counts - config.cardinality) ** 2

    def feasible_minimum(penalty: float) -> bool:
        return bool(problem.h1[np.argmin(problem.energy + penalty * violation)])

    if feasible_minimum(0.0):
        return 0.0
    low, high = 0.0, float(np.ptp(problem.energy)) + config.qaoa.penalty_margin
    for _ in range(iterations):
        mid = (low + high) / 2
        low, high = (low, mid) if feasible_minimum(mid) else (mid, high)
    return high * (1 + config.qaoa.tuned_penalty_margin)


def method_qubo(problem: Problem, method: str, config: Config) -> Qubo:
    if method == "dicke_xy":
        return problem.qubo
    if method == "x_penalty":
        penalty = float(np.ptp(problem.energy)) + config.qaoa.penalty_margin
    elif method == "x_penalty_tuned":
        penalty = tuned_penalty(problem, config)
    else:
        raise ValueError(f"unknown method {method!r}")
    return with_cardinality_penalty(problem.qubo, config.cardinality, penalty)


def normalised_cost(problem: Problem, qubo: Qubo) -> np.ndarray:
    return (energies(qubo) - problem.energy[problem.optimum]) / problem.scale


def make_kernel(problem: Problem, method: str, cost: np.ndarray, config: Config) -> QaoaKernel:
    m = problem.qubo.size
    if method == "dicke_xy":
        return QaoaKernel(m, cost, "xy", dicke_vector(m, config.cardinality))
    return QaoaKernel(m, cost, "x", uniform_vector(m))


def cost_spread(kernel: QaoaKernel) -> float:
    """Range of the cost over the states the start vector covers (20 valid states, or all 64)."""
    return float(np.ptp(kernel.cost[np.abs(kernel.start) > 0]))


def start_points(rng: np.random.Generator, n_starts: int, layers: int, spread: float) -> np.ndarray:
    """Shared uniform draws mapped to one γ period of each method's spectrum: γ ∈ (0, 2π/spread), β ∈ (0, π)."""
    u = rng.uniform(size=(n_starts, 2 * layers))
    gammas = u[:, :layers] * 2 * np.pi / max(1.0, spread)
    betas = u[:, layers:] * np.pi
    return np.hstack([gammas, betas])


def aggregate(probs: np.ndarray, cost: np.ndarray, cvar_alpha: float | None) -> float:
    """Mean cost, or the CVaR objective (mean of the best α share of probability mass)."""
    if cvar_alpha is None:
        return float(probs @ cost)
    order = np.argsort(cost)
    capped = np.minimum(np.cumsum(probs[order]), cvar_alpha)
    take = np.clip(capped - np.concatenate([[0.0], capped[:-1]]), 0, None)
    return float(take @ cost[order] / cvar_alpha)


def optimise(
    kernel: QaoaKernel,
    starts: np.ndarray,
    settings: QaoaSettings,
    cvar_alpha: float | None = None,
    shot_rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, float, int]:
    """COBYLA from every start. The best start is chosen by the objective the optimiser saw (exact, or the
    shot-noisy estimate in hardware-like mode), never by the answer key."""
    cost = kernel.cost

    def evaluate(params: np.ndarray) -> float:
        probs = kernel.probabilities(params)
        if shot_rng is not None:
            probs = shot_rng.multinomial(settings.shot_noise_shots, probs / probs.sum()) / settings.shot_noise_shots
        return aggregate(probs, cost, cvar_alpha)

    best_params, best_value, nfev = None, np.inf, 0
    for x0 in starts:
        result = minimize(evaluate, x0, method="COBYLA",
                          options={"maxiter": settings.maxiter, "rhobeg": settings.rhobeg, "tol": settings.tol})
        nfev += int(result.nfev)
        value = float(result.fun) if shot_rng is not None else aggregate(kernel.probabilities(result.x), cost, cvar_alpha)
        if value < best_value:
            best_params, best_value = result.x, value
    return best_params, best_value, nfev


def sample(problem: Problem, qubo: Qubo, method: str, params: np.ndarray, config: Config, seed: int) -> dict[int, int]:
    """Run the Qiskit circuit with shots; returns counts keyed by basis index on the free qubits."""
    p = len(params) // 2
    circuit = qaoa_circuit(method, qubo, problem.scale, params[:p], params[p:], config.cardinality)
    circuit.measure_all()
    result = StatevectorSampler(seed=seed).run([circuit], shots=config.qaoa.shots).result()
    counts = result[0].data.meas.get_counts()
    return {bits_to_index(qiskit_key_to_bits(key)): value for key, value in counts.items()}


def run_metrics(problem: Problem, probs: np.ndarray, cost: np.ndarray, counts: dict[int, int]) -> dict[str, float]:
    """All methods on a common basis: P(opt), P(opt | valid) and the financial gap (no penalty energy)."""
    shots = sum(counts.values())
    admissible = problem.h1 & problem.h3
    candidates = [(count, -index) for index, count in counts.items() if admissible[index]]
    decoded = -max(candidates)[1] if candidates else -1  # most frequent admissible sample, ties → lower index
    h1_mass = float(probs[problem.h1].sum())
    others = np.delete(probs, problem.optimum)
    financial_cost = (problem.energy - problem.energy[problem.optimum]) / problem.scale
    return {
        "p_opt": float(probs[problem.optimum]),
        "p_opt_given_valid": float(probs[problem.optimum] / h1_mass) if h1_mass > 0 else 0.0,
        "p_top2": float(probs[problem.optimum] + (probs[problem.second] if problem.second >= 0 else 0.0)),
        "h1_mass": h1_mass,
        "h3_mass": float(probs[admissible].sum()),
        "cap_mass": float(probs[problem.h1 & problem.cap_ok].sum()),
        "gap": float(probs @ cost),
        "financial_gap": float(probs @ financial_cost),
        "top_is_optimum": bool(probs[problem.optimum] > others.max() + 1e-12),  # strict: ties do not count
        "sampled_p_opt": counts.get(problem.optimum, 0) / shots,
        "decoded_is_optimum": bool(decoded == problem.optimum),
    }


def run_experiment(
    problems: dict[str, Problem], config: Config, methods: tuple[str, ...] = METHODS, cvar: bool = False
) -> pd.DataFrame:
    """Grid over profiles × methods × layers × seeds with shared start draws per (profile, layers, seed)."""
    settings = config.qaoa
    rows = []
    for p_idx, (name, problem) in enumerate(problems.items()):
        for p in settings.layers:
            for seed in range(settings.seeds):
                draw_seed = np.random.SeedSequence([config.seed, p_idx, p, seed])
                for method in methods:
                    qubo = method_qubo(problem, method, config)
                    cost = normalised_cost(problem, qubo)
                    kernel = make_kernel(problem, method, cost, config)
                    starts = start_points(np.random.default_rng(draw_seed), settings.starts_per_seed, p, cost_spread(kernel))
                    params, value, nfev = optimise(kernel, starts, settings, settings.cvar_alpha if cvar else None)
                    probs = kernel.probabilities(params)
                    sample_seed = int(np.random.SeedSequence([config.seed, p_idx, p, seed, SAMPLE_SALT]).generate_state(1)[0])
                    counts = sample(problem, qubo, method, params, config, sample_seed)
                    rows.append({"profile": name, "method": method + ("_cvar" if cvar else ""), "layers": p,
                                 "seed": seed, "objective_value": value, "nfev": nfev,
                                 **run_metrics(problem, probs, cost, counts)})
    return pd.DataFrame(rows)


def shot_noisy_comparison(problems: dict[str, Problem], config: Config, layers: int) -> pd.DataFrame:
    """Same starts optimised twice: on exact expectations and on finite-shot estimates (hardware-like)."""
    settings = config.qaoa
    rows = []
    for p_idx, (name, problem) in enumerate(problems.items()):
        for method in METHODS:
            qubo = method_qubo(problem, method, config)
            cost = normalised_cost(problem, qubo)
            kernel = make_kernel(problem, method, cost, config)
            for seed in range(settings.shot_noise_seeds):
                draws = np.random.SeedSequence([config.seed, p_idx, layers, seed])
                starts = start_points(np.random.default_rng(draws), settings.starts_per_seed, layers, cost_spread(kernel))
                for mode in ("exact", "shots"):
                    shot_rng = (np.random.default_rng(np.random.SeedSequence([config.seed, p_idx, seed, SHOT_SALT]))
                                if mode == "shots" else None)
                    params, _, nfev = optimise(kernel, starts, settings, shot_rng=shot_rng)
                    probs = kernel.probabilities(params)
                    rows.append({"profile": name, "method": method, "layers": layers, "seed": seed, "mode": mode,
                                 "nfev": nfev, "p_opt": float(probs[problem.optimum]),
                                 "h1_mass": float(probs[problem.h1].sum())})
    return pd.DataFrame(rows)


def circuit_resources(problem: Problem, config: Config, layers: tuple[int, ...]) -> pd.DataFrame:
    """Transpiled size per method and depth for one profile (dicke_xy includes the one-off Dicke preparation)."""
    gamma, beta = config.analysis.diagram_angles
    rows = []
    for method in METHODS:
        qubo = method_qubo(problem, method, config)
        for p in layers:
            circuit = qaoa_circuit(method, qubo, problem.scale, np.full(p, gamma), np.full(p, beta), config.cardinality)
            rows.append({"profile": problem.profile.name, "method": method, "layers": p,
                         "qubits": circuit.num_qubits, **gate_counts(circuit)})
    return pd.DataFrame(rows)


def random_floors(problems: dict[str, Problem]) -> dict[str, dict[str, float]]:
    """P(opt) of uniform guessing over the valid states and over all basis states."""
    return {name: {"valid_states": 1 / int(p.h1.sum()), "all_states": 1 / len(p.h1)} for name, p in problems.items()}


def summarise(runs: pd.DataFrame, floors: dict[str, dict[str, float]]) -> pd.DataFrame:
    """Median and min–max over seeds, and the share of seeds doing worse than guessing among valid states."""
    metrics = ["p_opt", "p_opt_given_valid", "p_top2", "h1_mass", "h3_mass", "cap_mass", "gap", "financial_gap",
               "sampled_p_opt", "nfev"]
    keys = ["profile", "method", "layers"]
    grouped = runs.groupby(keys)
    table = grouped[metrics].median().add_suffix("_median")
    table = table.join(grouped["p_opt"].min().rename("p_opt_min")).join(grouped["p_opt"].max().rename("p_opt_max"))
    floor = runs.profile.map({name: f["valid_states"] for name, f in floors.items()})
    table = table.join(runs.assign(below=runs.p_opt < floor).groupby(keys).below.mean().rename("share_below_random_floor"))
    table = table.join(grouped["top_is_optimum"].mean().rename("top_is_optimum_share"))
    table = table.join(grouped["decoded_is_optimum"].mean().rename("decoded_is_optimum_share"))
    return table.reset_index()
