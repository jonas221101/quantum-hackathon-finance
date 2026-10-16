"""Prototype: standard QAOA (X mixer + penalties) vs constraint-preserving QAOA (Dicke start + XY ring mixer)
for the 3-of-6 industry selection. Exact statevector simulation in numpy (6 qubits = 64 amplitudes).

Score per mandate (organiser definition): mean - lambda * variance - tau * one-way turnover, weights x/3.
QAOA minimises cost = -score. The HiTec cap is enforced by a penalty (X version) or by dropping the
HiTec qubit (XY version). Every result is compared with exact enumeration of all feasible portfolios.

Usage: python scripts/qaoa_mixer_comparison.py Database/returns_6_industries_monthly.csv
"""
from dataclasses import dataclass
from functools import reduce
from itertools import combinations
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.optimize import minimize

INDUSTRIES = ["NoDur", "Manuf", "Enrgy", "HiTec", "Hlth", "Utils"]
CURRENT = np.array([1, 0, 0, 0, 1, 1])
K = 3
CHANGE_PENALTY = 0.002
MANDATES = {"growth": (1.0, 1.00), "balanced": (5.0, 0.35), "risk_sensitive": (20.0, 0.20)}  # (lambda, HiTec cap)
REPS = (1, 2, 3)
STARTS = 20
SEED = 7


@dataclass
class Result:
    method: str
    mandate: str
    p: int
    p_optimum: float
    p_feasible: float
    top_is_optimum: bool
    gap: float  # expected normalised cost above optimum, 0 = perfect


def financial_cost(x: np.ndarray, mu: np.ndarray, sigma: np.ndarray, lam: float) -> float:
    w = x / K
    turnover = np.abs(w - CURRENT / K).sum() / 2
    return -(mu @ w - lam * w @ sigma @ w - CHANGE_PENALTY * turnover)


def bitstrings(n: int) -> np.ndarray:
    return np.array([[(b >> i) & 1 for i in range(n)] for b in range(2 ** n)])


def pauli_kron(ops: list[np.ndarray]) -> np.ndarray:
    return reduce(np.kron, ops[::-1])  # qubit 0 = least significant bit


def xy_ring_hamiltonian(n: int) -> np.ndarray:
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    y = np.array([[0, -1j], [1j, 0]])
    eye = np.eye(2)
    h = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n):
        j = (i + 1) % n
        for p in (x, y):
            ops = [eye] * n
            ops[i], ops[j] = p, p
            h += pauli_kron(ops) / 2
    return h


def unitary_from_hermitian(h: np.ndarray):
    vals, vecs = np.linalg.eigh(h)
    return lambda beta: (vecs * np.exp(-1j * beta * vals)) @ vecs.conj().T


def x_mixer(n: int):
    def u(beta: float) -> np.ndarray:
        rx = np.array([[np.cos(beta), -1j * np.sin(beta)], [-1j * np.sin(beta), np.cos(beta)]])
        return pauli_kron([rx] * n)
    return u


def run_qaoa(cost: np.ndarray, psi0: np.ndarray, mixer, p: int, rng: np.random.Generator) -> np.ndarray:
    def state(params: np.ndarray) -> np.ndarray:
        psi = psi0.copy()
        for gamma, beta in zip(params[:p], params[p:]):
            psi = mixer(beta) @ (np.exp(-1j * gamma * cost) * psi)
        return psi

    def expectation(params: np.ndarray) -> float:
        return float(np.abs(state(params)) ** 2 @ cost)

    best = None
    for _ in range(STARTS):
        x0 = np.concatenate([rng.uniform(0, 2 * np.pi, p), rng.uniform(0, np.pi, p)])
        res = minimize(expectation, x0, method="Nelder-Mead", options={"maxiter": 3000, "xatol": 1e-6, "fatol": 1e-9})
        if best is None or res.fun < best.fun:
            best = res
    return np.abs(state(best.x)) ** 2


def main(csv_path: Path) -> None:
    returns = pd.read_csv(csv_path, index_col=0).loc["2015-01":"2019-12", INDUSTRIES]
    mu, sigma = returns.mean().to_numpy(), returns.cov().to_numpy()
    rng = np.random.default_rng(SEED)
    results: list[Result] = []

    for mandate, (lam, cap) in MANDATES.items():
        hitec_blocked = cap < 1 / K
        states = bitstrings(6)
        fin = np.array([financial_cost(x, mu, sigma, lam) for x in states])
        feasible = (states.sum(axis=1) == K) & ~(hitec_blocked & (states[:, 3] == 1))
        best_idx = np.flatnonzero(feasible)[np.argmin(fin[feasible])]
        scale = fin[feasible].max() - fin[feasible].min()
        exact_pick = "+".join(np.array(INDUSTRIES)[states[best_idx] == 1])

        # Method 1: X mixer, uniform start, penalties larger than the whole financial range.
        penalty = fin.max() - fin.min() + 1e-6
        penalised = fin + penalty * (states.sum(axis=1) - K) ** 2 + penalty * hitec_blocked * states[:, 3]
        cost_x = (penalised - fin[best_idx]) / scale
        psi_plus = np.full(64, 1 / 8, dtype=complex)
        for p in REPS:
            probs = run_qaoa(cost_x, psi_plus, x_mixer(6), p, rng)
            results.append(Result("X+penalty", mandate, p, probs[best_idx], probs[feasible].sum(),
                                  int(np.argmax(probs)) == best_idx, float(probs @ np.clip(cost_x, 0, None))))

        # Method 2: Dicke start + XY ring mixer; HiTec qubit dropped when the cap forbids it.
        keep = [i for i in range(6) if not (hitec_blocked and i == 3)]
        n = len(keep)
        sub_states = bitstrings(n)
        full_index = np.array([sum(int(s[k]) << keep[k] for k in range(n)) for s in sub_states])
        cost_xy = (fin[full_index] - fin[best_idx]) / scale
        dicke = (sub_states.sum(axis=1) == K).astype(complex)
        dicke /= np.linalg.norm(dicke)
        mixer_xy = unitary_from_hermitian(xy_ring_hamiltonian(n))
        sub_best = int(np.flatnonzero(full_index == best_idx)[0])
        sub_feasible = feasible[full_index]
        for p in REPS:
            probs = run_qaoa(cost_xy, dicke, mixer_xy, p, rng)
            results.append(Result("Dicke+XY", mandate, p, probs[sub_best], probs[sub_feasible].sum(),
                                  int(np.argmax(probs)) == sub_best, float(probs @ cost_xy)))

        n_feasible = int(feasible.sum())
        print(f"{mandate:15s} exact optimum: {exact_pick:18s} feasible portfolios: {n_feasible} "
              f"(random guess P(opt) = {1 / n_feasible:.3f})")

    table = pd.DataFrame([r.__dict__ for r in results])
    print()
    print(table.round(3).to_string(index=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
