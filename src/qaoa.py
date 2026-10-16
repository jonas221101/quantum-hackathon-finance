from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .config import AllocationConfig, MANDATES
from .data import CURRENT_PORTFOLIO, INDUSTRIES


def _portfolio_costs(
    returns: pd.DataFrame,
    mandate_name: str,
    allocation_config: AllocationConfig = AllocationConfig(),
) -> np.ndarray:
    mandate = MANDATES[mandate_name]
    mu = returns.loc[:, list(INDUSTRIES)].mean().to_numpy()
    covariance = returns.loc[:, list(INDUSTRIES)].cov().to_numpy()
    current = np.array([name in CURRENT_PORTFOLIO for name in INDUSTRIES], dtype=float)
    costs = []
    for bits in range(2 ** len(INDUSTRIES)):
        selection = np.array([(bits >> i) & 1 for i in range(len(INDUSTRIES))])
        weights = selection / 3.0
        turnover = np.abs(weights - current / 3.0).sum() / 2.0
        score = (
            mu @ weights
            - mandate.risk_weight * weights @ covariance @ weights
            - 0.002 * turnover
            - allocation_config.cap_penalty
            * max(0.0, weights[3] - mandate.hitec_cap)
        )
        costs.append(-score)
    return np.asarray(costs)


def _admissible_masks(returns: pd.DataFrame, mandate_name: str) -> np.ndarray:
    mandate = MANDATES[mandate_name]
    masks: list[int] = []
    for bits in range(2 ** len(INDUSTRIES)):
        if bits.bit_count() != 3:
            continue
        selection = [INDUSTRIES[i] for i in range(len(INDUSTRIES)) if bits & (1 << i)]
        losses = -returns.loc[:, selection].mean(axis=1)
        if float((losses > mandate.loss_threshold).mean()) <= mandate.tolerance + 1e-12:
            masks.append(bits)
    return np.asarray(masks, dtype=int)


def _penalized_costs(costs: np.ndarray, penalty: float) -> np.ndarray:
    masks = np.arange(len(costs))
    cardinality = np.array([mask.bit_count() for mask in masks])
    hitec = np.array([(mask >> 3) & 1 for mask in masks])
    return costs + penalty * (cardinality - 3) ** 2 + penalty * hitec


def _build_circuit(costs: np.ndarray, params: np.ndarray, reps: int, *, measure: bool):
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit.circuit.library import Diagonal
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise RuntimeError(
            "Qiskit and qiskit-aer are required for the IBM Aer simulator. "
            "Install with: python -m pip install -r requirements.txt"
        ) from exc

    n = int(np.log2(len(costs)))
    circuit = QuantumCircuit(n)
    circuit.h(range(n))
    for layer in range(reps):
        gamma, beta = params[layer], params[reps + layer]
        circuit.append(Diagonal(np.exp(-1j * gamma * costs)), range(n))
        for qubit in range(n):
            circuit.rx(2 * beta, qubit)
    if measure:
        circuit.measure_all()
    else:
        circuit.save_statevector()
    return circuit, AerSimulator(method="statevector")


def _dicke_state(n: int, weight: int) -> np.ndarray:
    states = [bits for bits in range(2**n) if bits.bit_count() == weight]
    state = np.zeros(2**n, dtype=complex)
    state[states] = 1 / np.sqrt(len(states))
    return state


def _build_xy_circuit(
    costs: np.ndarray, params: np.ndarray, reps: int, *, measure: bool
):
    try:
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import Diagonal
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise RuntimeError(
            "Qiskit and qiskit-aer are required for the IBM Aer simulator. "
            "Install with: python -m pip install -r requirements.txt"
        ) from exc

    n = int(np.log2(len(costs)))
    circuit = QuantumCircuit(n)
    circuit.initialize(_dicke_state(n, 3), range(n))
    for layer in range(reps):
        gamma, beta = params[layer], params[reps + layer]
        circuit.append(Diagonal(np.exp(-1j * gamma * costs)), range(n))
        for qubit in range(n):
            other = (qubit + 1) % n
            circuit.rxx(2 * beta, qubit, other)
            circuit.ryy(2 * beta, qubit, other)
    if measure:
        circuit.measure_all()
    else:
        circuit.save_statevector()
    return circuit, AerSimulator(method="statevector")


def _aer_statevector(costs: np.ndarray, params: np.ndarray, reps: int) -> np.ndarray:
    """Evaluate a QAOA circuit on IBM's local Aer statevector simulator."""
    try:
        from qiskit import transpile
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise RuntimeError(
            "Qiskit and qiskit-aer are required for the IBM Aer simulator. "
            "Install with: python -m pip install -r requirements.txt"
        ) from exc

    circuit, simulator = _build_circuit(costs, params, reps, measure=False)
    result = simulator.run(transpile(circuit, simulator)).result()
    return np.asarray(result.get_statevector(circuit))


def _aer_counts(
    costs: np.ndarray, params: np.ndarray, reps: int, shots: int
) -> dict[str, int]:
    """Sample the optimized circuit using Aer, matching hardware-style counts."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    circuit, simulator = _build_circuit(costs, params, reps, measure=True)
    result = simulator.run(
        transpile(circuit, simulator), shots=shots, seed_simulator=7
    ).result()
    return result.get_counts(circuit)


def _aer_statevector_xy(costs: np.ndarray, params: np.ndarray, reps: int) -> np.ndarray:
    from qiskit import transpile

    circuit, simulator = _build_xy_circuit(costs, params, reps, measure=False)
    result = simulator.run(transpile(circuit, simulator)).result()
    return np.asarray(result.get_statevector(circuit))


def _aer_counts_xy(
    costs: np.ndarray, params: np.ndarray, reps: int, shots: int
) -> dict[str, int]:
    from qiskit import transpile

    circuit, simulator = _build_xy_circuit(costs, params, reps, measure=True)
    result = simulator.run(
        transpile(circuit, simulator), shots=shots, seed_simulator=7
    ).result()
    return result.get_counts(circuit)


def _optimize(
    costs: np.ndarray, reps: int, starts: int, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)

    def expectation(params: np.ndarray) -> float:
        state = _aer_statevector(costs, params, reps)
        return float(np.abs(state) ** 2 @ costs)

    best = None
    for _ in range(starts):
        initial = np.concatenate(
            [rng.uniform(0, 2 * np.pi, reps), rng.uniform(0, np.pi, reps)]
        )
        candidate = minimize(
            expectation,
            initial,
            method="Nelder-Mead",
            options={"maxiter": 300, "xatol": 1e-4, "fatol": 1e-6},
        )
        if best is None or candidate.fun < best.fun:
            best = candidate
    if best is None:
        raise RuntimeError("QAOA optimizer did not produce a result")
    return _aer_statevector(costs, best.x, reps), best.x


def _optimize_xy(
    costs: np.ndarray, reps: int, starts: int, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)

    def expectation(params: np.ndarray) -> float:
        state = _aer_statevector_xy(costs, params, reps)
        return float(np.abs(state) ** 2 @ costs)

    best = None
    for _ in range(starts):
        initial = np.concatenate(
            [rng.uniform(0, 2 * np.pi, reps), rng.uniform(0, np.pi, reps)]
        )
        candidate = minimize(
            expectation,
            initial,
            method="Nelder-Mead",
            options={"maxiter": 300, "xatol": 1e-4, "fatol": 1e-6},
        )
        if best is None or candidate.fun < best.fun:
            best = candidate
    if best is None:
        raise RuntimeError("XY QAOA optimizer did not produce a result")
    return _aer_statevector_xy(costs, best.x, reps), best.x


def _summarize_result(
    costs: np.ndarray,
    state: np.ndarray,
    counts: dict[str, int],
    best: int,
    admissible: np.ndarray,
    shots: int,
) -> dict[str, float]:
    probabilities = np.abs(state) ** 2
    sampled_feasible = sum(
        count for bits, count in counts.items() if int(bits[::-1], 2) in set(admissible)
    )
    return {
        "probability_best": float(probabilities[best]),
        "probability_feasible": float(probabilities[admissible].sum()),
        "sampled_probability_best": counts.get(
            format(best, f"0{len(INDUSTRIES)}b")[::-1], 0
        )
        / shots,
        "sampled_probability_feasible": sampled_feasible / shots,
    }


def run_ibm_aer_comparison(
    returns: pd.DataFrame,
    *,
    reps: int = 1,
    starts: int = 2,
    shots: int = 1024,
    seed: int = 7,
) -> dict[str, Any]:
    """Run QAOA statevector optimization using IBM's local Aer simulator.

    The exact enumeration remains the verifier; QAOA probabilities are reported
    for the best portfolio and for all valid 3-of-6 selections.
    """
    output: dict[str, Any] = {"backend": "AerSimulator(statevector)", "mandates": {}}
    for offset, mandate_name in enumerate(MANDATES):
        financial_costs = _portfolio_costs(returns, mandate_name)
        penalty = float(financial_costs.max() - financial_costs.min() + 1e-6)
        x_costs = _penalized_costs(financial_costs, penalty)
        state, params = _optimize(x_costs, reps, starts, seed + offset)
        feasible = _admissible_masks(returns, mandate_name)
        best = int(feasible[np.argmin(financial_costs[feasible])])
        counts = _aer_counts(x_costs, params, reps, shots)
        x_summary = _summarize_result(
            financial_costs, state, counts, best, feasible, shots
        )
        xy_state, xy_params = _optimize_xy(
            financial_costs, reps, starts, seed + 100 + offset
        )
        xy_counts = _aer_counts_xy(financial_costs, xy_params, reps, shots)
        xy_summary = _summarize_result(
            financial_costs, xy_state, xy_counts, best, feasible, shots
        )
        output["mandates"][mandate_name] = {
            "best_portfolio": "+".join(
                name for i, name in enumerate(INDUSTRIES) if best & (1 << i)
            ),
            "x_mixer": x_summary,
            "xy_mixer": xy_summary,
            "shots": shots,
            "reps": reps,
            "starts": starts,
            "admissible_count": int(len(feasible)),
            "penalty": penalty,
        }
    return output


def benchmark_qaoa(
    returns: pd.DataFrame,
    reps_values: tuple[int, ...] = (1, 2, 3, 4),
    seeds: tuple[int, ...] = tuple(range(10)),
    shots: int = 1024,
) -> pd.DataFrame:
    """Benchmark both mixers across depths and seeds against exact admissibility."""
    rows: list[dict[str, Any]] = []
    for mandate_name in MANDATES:
        costs = _portfolio_costs(returns, mandate_name)
        admissible = _admissible_masks(returns, mandate_name)
        optimum = int(admissible[np.argmin(costs[admissible])])
        for reps in reps_values:
            for seed in seeds:
                for method in ("x", "xy"):
                    if method == "x":
                        penalized = _penalized_costs(
                            costs, float(costs.max() - costs.min() + 1e-6)
                        )
                        state, params = _optimize(penalized, reps, 1, seed)
                        counts = _aer_counts(penalized, params, reps, shots)
                    else:
                        state, params = _optimize_xy(costs, reps, 1, seed)
                        counts = _aer_counts_xy(costs, params, reps, shots)
                    probabilities = np.abs(state) ** 2
                    expected_gap = float(
                        (probabilities[admissible] * (costs[admissible] - costs[optimum])).sum()
                    )
                    top = int(np.argmax(probabilities))
                    rows.append(
                        {
                            "mandate": mandate_name,
                            "method": method,
                            "reps": reps,
                            "seed": seed,
                            "probability_optimum": float(probabilities[optimum]),
                            "probability_feasible": float(probabilities[admissible].sum()),
                            "expected_gap": expected_gap,
                            "top_sample_is_optimum": top == optimum,
                            "sampled_feasible": sum(
                                count
                                for bits, count in counts.items()
                                if int(bits[::-1], 2) in set(admissible)
                            )
                            / shots,
                        }
                    )
    return pd.DataFrame(rows)
