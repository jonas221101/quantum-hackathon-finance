"""Single place for bit ordering. Qubit i ↔ industry i ↔ bit i of the basis-state index (little endian, as Qiskit).

Qiskit bitstrings (counts keys) are written most significant qubit first, i.e. reversed.
"""
from __future__ import annotations

import numpy as np


def index_to_bits(index: int, n: int) -> np.ndarray:
    return np.array([(index >> i) & 1 for i in range(n)], dtype=int)


def bits_to_index(bits: np.ndarray) -> int:
    return int(sum(int(b) << i for i, b in enumerate(bits)))


def all_states(n: int) -> np.ndarray:
    """Shape (2**n, n): row b holds the bits of basis state b."""
    return np.array([index_to_bits(b, n) for b in range(2**n)], dtype=int)


def qiskit_key_to_bits(key: str) -> np.ndarray:
    return np.array([int(c) for c in reversed(key)], dtype=int)


def embed(free_bits: np.ndarray, free: list[int], n_total: int) -> np.ndarray:
    """Map bits on the free (non-excluded) qubits back to the full industry vector."""
    x = np.zeros(n_total, dtype=int)
    x[free] = free_bits
    return x
