from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .config import MANDATES
from .data import CURRENT_PORTFOLIO, INDUSTRIES


def _portfolio_costs(returns: pd.DataFrame, mandate_name: str) -> np.ndarray:
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
        )
        costs.append(-score)
    return np.asarray(costs)


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
    shots: int,
) -> dict[str, float]:
    valid = {sum(1 << i for i in combo) for combo in combinations(range(6), 3)}
    probabilities = np.abs(state) ** 2
    sampled_feasible = sum(
        count for bits, count in counts.items() if int(bits[::-1], 2) in valid
    )
    return {
        "probability_best": float(probabilities[best]),
        "probability_feasible": float(probabilities[list(valid)].sum()),
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
    valid = [sum(1 << i for i in combo) for combo in combinations(range(6), 3)]
    output: dict[str, Any] = {"backend": "AerSimulator(statevector)", "mandates": {}}
    for offset, mandate_name in enumerate(MANDATES):
        costs = _portfolio_costs(returns, mandate_name)
        state, params = _optimize(costs, reps, starts, seed + offset)
        feasible = np.asarray(valid)
        best = int(feasible[np.argmin(costs[feasible])])
        counts = _aer_counts(costs, params, reps, shots)
        x_summary = _summarize_result(costs, state, counts, best, shots)
        xy_state, xy_params = _optimize_xy(costs, reps, starts, seed + 100 + offset)
        xy_counts = _aer_counts_xy(costs, xy_params, reps, shots)
        xy_summary = _summarize_result(costs, xy_state, xy_counts, best, shots)
        output["mandates"][mandate_name] = {
            "best_portfolio": "+".join(
                name for i, name in enumerate(INDUSTRIES) if best & (1 << i)
            ),
            "x_mixer": x_summary,
            "xy_mixer": xy_summary,
            "shots": shots,
            "reps": reps,
            "starts": starts,
        }
    return output
