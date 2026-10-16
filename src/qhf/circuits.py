"""Qiskit circuits: Dicke-state preparation, cost layer, X mixer and XY ring mixer.

The XY mixer is a one-step (Trotterised) ring mixer: exp(−iβ(X_iX_j + Y_iY_j)/2) applied edge by edge in a
fixed order (``ring_edges``), not exp(−iβΣ…) itself. Every factor preserves Hamming weight, so the product does
too; ``kernel.py`` applies exactly the same product. The ring follows the order of the free qubits.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RYGate, XXPlusYYGate

from qhf.qubo import Qubo, ising_terms

BASIS_GATES = ["cx", "rz", "sx", "x"]


def ring_edges(n: int) -> list[tuple[int, int]]:
    """Ring edges in parity order: (0,1),(2,3),… then (1,2),(3,4),… then the closing edge if not yet used."""
    if n < 2:
        return []
    if n == 2:
        return [(0, 1)]
    ring = [(i, (i + 1) % n) for i in range(n)]
    even = [e for idx, e in enumerate(ring) if idx % 2 == 0 and idx != n - 1]
    odd = [e for idx, e in enumerate(ring) if idx % 2 == 1]
    closing = [ring[-1]] if ring[-1] not in odd else []
    return even + odd + closing


def _scs(qc: QuantumCircuit, n: int, k: int) -> None:
    """Split & cyclic shift SCS_{n,k} of Bärtschi & Eidenbenz (2019) on qubits labelled 1..n (index = label − 1)."""
    q = lambda label: label - 1  # noqa: E731
    qc.cx(q(n - 1), q(n))
    qc.cry(2 * np.arccos(np.sqrt(1 / n)), q(n), q(n - 1))
    qc.cx(q(n - 1), q(n))
    for l in range(2, k + 1):
        qc.cx(q(n - l), q(n))
        qc.append(RYGate(2 * np.arccos(np.sqrt(l / n))).control(2), [q(n), q(n - l + 1), q(n - l)])
        qc.cx(q(n - l), q(n))


def dicke_circuit(n: int, k: int) -> QuantumCircuit:
    """Deterministic preparation of |D_n^k⟩ (equal superposition of all weight-k basis states)."""
    if not 0 < k < n:
        raise ValueError("need 0 < k < n")
    qc = QuantumCircuit(n, name=f"Dicke({n},{k})")
    for label in range(n - k + 1, n + 1):
        qc.x(label - 1)
    for m in range(n, k, -1):
        _scs(qc, m, k)
    for m in range(k, 1, -1):
        _scs(qc, m, m - 1)
    return qc


def cost_layer(qubo: Qubo, gamma: float, scale: float) -> QuantumCircuit:
    """exp(−iγ·H_cost/scale), H_cost = Σ h_i Z_i + Σ J_ij Z_iZ_j (constant dropped: global phase)."""
    field, coupling, _ = ising_terms(qubo)
    m = qubo.size
    qc = QuantumCircuit(m, name="cost")
    for i in range(m):
        if field[i] != 0:
            qc.rz(2 * gamma * field[i] / scale, i)
    for i in range(m):
        for j in range(i + 1, m):
            if coupling[i, j] != 0:
                qc.rzz(2 * gamma * coupling[i, j] / scale, i, j)
    return qc


def x_mixer_layer(m: int, beta: float) -> QuantumCircuit:
    qc = QuantumCircuit(m, name="X mixer")
    for i in range(m):
        qc.rx(2 * beta, i)
    return qc


def xy_mixer_layer(m: int, beta: float) -> QuantumCircuit:
    qc = QuantumCircuit(m, name="XY mixer")
    for i, j in ring_edges(m):
        qc.append(XXPlusYYGate(2 * beta, 0.0), [i, j])  # = exp(−iβ(XX+YY)/2)
    return qc


def qaoa_circuit(
    method: str, qubo: Qubo, scale: float, gammas: np.ndarray, betas: np.ndarray, cardinality: int
) -> QuantumCircuit:
    """Full QAOA circuit for ``method`` in {'dicke_xy', 'x_penalty', 'x_penalty_tuned'} with bound angles."""
    m = qubo.size
    qc = QuantumCircuit(m, name=f"QAOA {method}")
    if method == "dicke_xy":
        qc.compose(dicke_circuit(m, cardinality), inplace=True)
    else:
        qc.h(range(m))
    for gamma, beta in zip(gammas, betas):
        qc.compose(cost_layer(qubo, gamma, scale), inplace=True)
        mixer = xy_mixer_layer(m, beta) if method == "dicke_xy" else x_mixer_layer(m, beta)
        qc.compose(mixer, inplace=True)
    return qc


def gate_counts(circuit: QuantumCircuit) -> dict[str, int]:
    compiled = transpile(circuit, basis_gates=BASIS_GATES, optimization_level=1, seed_transpiler=0)
    ops = compiled.count_ops()
    return {"depth": int(compiled.depth()), "two_qubit_gates": int(ops.get("cx", 0)), "total_gates": int(sum(ops.values()))}
