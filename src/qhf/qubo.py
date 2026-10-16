"""QUBO and Ising form of the objective over the free (non-excluded) qubits.

f(x) = c + Σ_i d_i x_i + Σ_{i<j} Q_ij x_i x_j  with
  d_i  = −μ_i/K + λΣ_ii/K² + (τ/H)(1 − 2x⁰_i)/(2K) + κ·(1/K − cap)·[i = capped, cap < 1/K]
  Q_ij = 2λΣ_ij/K²
  c    = (τ/H)·Σ_i x⁰_i/(2K)
The cardinality penalty P(Σx − K)² is added only for the penalty baseline.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit.quantum_info import SparsePauliOp

from qhf.bits import all_states
from qhf.config import Config, Profile
from qhf.portfolio import selection


@dataclass(frozen=True)
class Qubo:
    linear: np.ndarray  # d, shape (m,)
    quadratic: np.ndarray  # Q, strictly upper triangular, shape (m, m)
    constant: float

    @property
    def size(self) -> int:
        return len(self.linear)


def build_qubo(mu: np.ndarray, sigma: np.ndarray, profile: Profile, config: Config, free: list[int]) -> Qubo:
    k = config.cardinality
    x0 = selection(config.current, config).astype(float)
    tau = config.change_penalty / config.holding_horizon
    capped = config.index(config.capped_industry)
    linear = -mu / k + profile.risk_aversion * np.diag(sigma) / k**2 + tau * (1 - 2 * x0) / (2 * k)
    if profile.hitec_cap < 1 / k:
        linear[capped] += config.cap_penalty * (1 / k - profile.hitec_cap)
    quadratic = np.triu(2 * profile.risk_aversion * sigma / k**2, k=1)
    constant = tau * x0.sum() / (2 * k)
    # Excluded industries are fixed to 0: their terms vanish, the constant keeps the x⁰ part.
    return Qubo(linear[free].copy(), quadratic[np.ix_(free, free)].copy(), float(constant))


def with_cardinality_penalty(qubo: Qubo, k: int, penalty: float) -> Qubo:
    """Add P(Σx − K)² = P[(1 − 2K)Σx_i + 2Σ_{i<j} x_i x_j + K²]."""
    m = qubo.size
    return Qubo(
        qubo.linear + penalty * (1 - 2 * k),
        qubo.quadratic + np.triu(np.full((m, m), 2 * penalty), k=1),
        qubo.constant + penalty * k**2,
    )


def energies(qubo: Qubo) -> np.ndarray:
    """Energy of every basis state (index b ↔ bits of b, little endian)."""
    states = all_states(qubo.size).astype(float)
    return qubo.constant + states @ qubo.linear + np.einsum("bi,ij,bj->b", states, qubo.quadratic, states)


def ising_terms(qubo: Qubo) -> tuple[np.ndarray, np.ndarray, float]:
    """x = (1 − z)/2 → E = offset + Σ h_i z_i + Σ_{i<j} J_ij z_i z_j."""
    q = qubo.quadratic
    coupling = q / 4
    field = -qubo.linear / 2 - (q.sum(axis=1) + q.sum(axis=0)) / 4
    offset = qubo.constant + qubo.linear.sum() / 2 + q.sum() / 4
    return field, coupling, float(offset)


def to_sparse_pauli_op(qubo: Qubo) -> SparsePauliOp:
    field, coupling, offset = ising_terms(qubo)
    m = qubo.size
    terms = [("", [], offset)] + [("Z", [i], field[i]) for i in range(m)]
    terms += [("ZZ", [i, j], coupling[i, j]) for i in range(m) for j in range(i + 1, m) if coupling[i, j] != 0]
    return SparsePauliOp.from_sparse_list(terms, num_qubits=m).simplify(atol=0)
