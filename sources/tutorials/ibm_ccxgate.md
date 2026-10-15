# IBM Quantum — CCXGate (Toffoli), Qiskit 2.2

Source: https://quantum.cloud.ibm.com/docs/en/api/qiskit/2.2/qiskit.circuit.library.CCXGate
(Condensed from the docs page; the raw HTML was not kept.)

- CCX = Toffoli gate. Applied with `QuantumCircuit.ccx(c0, c1, target)`.
- Action on basis states: flips `target` iff both controls are `|1⟩`. `|c0 c1 t⟩ → |c0 c1 (t ⊕ c0·c1)⟩`.
  With `t = 0` the target ends up holding `c0 AND c1` → reversible logical AND.
- Circuit symbol:
  ```
  q_0: ──■──
         │
  q_1: ──■──
       ┌─┴─┐
  q_2: ┤ X ├
       └───┘
  ```
- Matrix (Qiskit little-endian, q_0 least significant): `CCX(q0,q1,q2) = I⊗I⊗|0⟩⟨0| + CX⊗|1⟩⟨1|`.
  Swaps basis states |011⟩ ↔ |111⟩ (indices 3 and 7), identity elsewhere.
- **Endianness warning:** Qiskit puts higher qubit index = more significant bit. Textbooks often
  assume the opposite. Bitstrings from `get_counts()` read right-to-left (q_0 is rightmost).
- Self-inverse: applying CCX twice = identity → use it to uncompute ancillas.
- Useful related gates: `cx` (XOR / copy), `x` (NOT), `mcx` (AND of >2 controls),
  `ctrl_state` argument to trigger on `|0⟩` controls (negated inputs) without extra X gates.
- Logic building blocks: NOT = X; AND = CCX onto |0⟩; OR(a,b) = NOT(AND(NOT a, NOT b)); XOR = two CX onto a target.
