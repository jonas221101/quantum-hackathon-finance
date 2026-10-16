"""Fast numpy statevector simulation of exactly the circuits in ``circuits.py`` (used inside the optimiser).

Equality with Qiskit (up to a global phase) is checked in the tests.
"""
from __future__ import annotations

import numpy as np

from qhf.bits import all_states
from qhf.circuits import ring_edges


def dicke_vector(m: int, k: int) -> np.ndarray:
    weight = all_states(m).sum(axis=1)
    vec = (weight == k).astype(complex)
    return vec / np.linalg.norm(vec)


def uniform_vector(m: int) -> np.ndarray:
    return np.full(2**m, 1 / np.sqrt(2**m), dtype=complex)


class QaoaKernel:
    """psi(γ, β) = Π_l [mixer(β_l) · exp(−iγ_l·cost)] |start⟩ with cost = normalised energy vector."""

    def __init__(self, m: int, cost: np.ndarray, mixer: str, start: np.ndarray):
        if mixer not in {"x", "xy"}:
            raise ValueError("mixer must be 'x' or 'xy'")
        self.m = m
        self.cost = np.asarray(cost, dtype=float)
        self.mixer = mixer
        self.start = np.asarray(start, dtype=complex)
        states = all_states(m)
        self._pairs = []
        for i, j in ring_edges(m):
            a = np.flatnonzero((states[:, i] == 0) & (states[:, j] == 1))
            b = a + (1 << i) - (1 << j)  # same state with bits i and j swapped
            self._pairs.append((a, b))

    def _apply_x_mixer(self, psi: np.ndarray, beta: float) -> np.ndarray:
        c, s = np.cos(beta), -1j * np.sin(beta)
        tensor = psi.reshape([2] * self.m)
        for axis in range(self.m):
            t0 = np.take(tensor, 0, axis=axis)
            t1 = np.take(tensor, 1, axis=axis)
            tensor = np.stack([c * t0 + s * t1, s * t0 + c * t1], axis=axis)
        return tensor.reshape(-1)

    def _apply_xy_mixer(self, psi: np.ndarray, beta: float) -> np.ndarray:
        c, s = np.cos(beta), -1j * np.sin(beta)
        psi = psi.copy()
        for a, b in self._pairs:
            pa, pb = psi[a].copy(), psi[b]
            psi[a] = c * pa + s * pb
            psi[b] = s * pa + c * pb
        return psi

    def state(self, params: np.ndarray) -> np.ndarray:
        p = len(params) // 2
        gammas, betas = params[:p], params[p:]
        psi = self.start.copy()
        apply_mixer = self._apply_xy_mixer if self.mixer == "xy" else self._apply_x_mixer
        for gamma, beta in zip(gammas, betas):
            psi = apply_mixer(np.exp(-1j * gamma * self.cost) * psi, beta)
        return psi

    def probabilities(self, params: np.ndarray) -> np.ndarray:
        return np.abs(self.state(params)) ** 2
