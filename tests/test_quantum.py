from dataclasses import replace

import numpy as np
import pytest
from qiskit.quantum_info import Operator, Statevector

from qhf.bits import all_states, bits_to_index, embed, index_to_bits, qiskit_key_to_bits
from qhf.circuits import dicke_circuit, qaoa_circuit, ring_edges, xy_mixer_layer
from qhf.config import FAST_QAOA
from qhf.exact import free_indices
from qhf.kernel import dicke_vector
from qhf.portfolio import objective
from qhf.qaoa import (
    METHODS,
    build_problem,
    make_kernel,
    method_qubo,
    normalised_cost,
    run_experiment,
    sample,
    tuned_penalty,
)
from qhf.qubo import build_qubo, energies, ising_terms, to_sparse_pauli_op


@pytest.fixture(scope="module")
def problems(base_moments, scenarios, config):
    mu, sigma = base_moments
    return {p.name: build_problem(mu, sigma, scenarios["base"], p, config) for p in config.profiles}


def test_bit_order_round_trip():
    for index in range(64):
        assert bits_to_index(index_to_bits(index, 6)) == index
    assert list(qiskit_key_to_bits("000011")) == [1, 1, 0, 0, 0, 0]  # qubits 0 and 1 set


@pytest.mark.parametrize("profile", ["growth", "balanced", "risk_sensitive"])
def test_qubo_energy_equals_objective_for_all_64_states(base_moments, config, profile):
    mu, sigma = base_moments
    prof = config.profile(profile)
    qubo = build_qubo(mu, sigma, prof, config, free_indices(config))
    for bits, energy in zip(all_states(6), energies(qubo)):
        assert energy == pytest.approx(objective(bits, mu, sigma, prof, config), abs=1e-14)


def test_ising_diagonal_plus_offset_equals_qubo(base_moments, config):
    mu, sigma = base_moments
    qubo = build_qubo(mu, sigma, config.profile("risk_sensitive"), config, free_indices(config))
    diagonal = np.real(np.diag(to_sparse_pauli_op(qubo).to_matrix()))
    np.testing.assert_allclose(diagonal, energies(qubo), atol=1e-14)
    field, coupling, offset = ising_terms(qubo)
    assert np.allclose(coupling, np.triu(coupling, 1))


def test_qubo_with_exclusion_matches_embedded_objective(base_moments, config):
    mu, sigma = base_moments
    cfg = replace(config, excluded=("Enrgy",))
    free = free_indices(cfg)
    qubo = build_qubo(mu, sigma, cfg.profile("balanced"), cfg, free)
    for bits, energy in zip(all_states(len(free)), energies(qubo)):
        assert energy == pytest.approx(objective(embed(bits, free, 6), mu, sigma, cfg.profile("balanced"), cfg), abs=1e-14)


@pytest.mark.parametrize("n, k", [(6, 3), (5, 3), (4, 2), (6, 1)])
def test_dicke_circuit_prepares_exact_dicke_state(n, k):
    np.testing.assert_allclose(Statevector(dicke_circuit(n, k)).data, dicke_vector(n, k), atol=1e-10)


def test_xy_mixer_conserves_hamming_weight():
    unitary = Operator(xy_mixer_layer(6, 0.37)).data
    weight = all_states(6).sum(axis=1)
    leak = np.abs(unitary[weight[:, None] != weight[None, :]]).max()
    assert leak < 1e-12
    assert len(ring_edges(6)) == 6 and len(ring_edges(5)) == 5


@pytest.mark.parametrize("method", METHODS)
def test_kernel_matches_qiskit_statevector(problems, config, method):
    problem = problems["balanced"]
    qubo = method_qubo(problem, method, config)
    kernel = make_kernel(problem, method, normalised_cost(problem, qubo), config)
    params = np.random.default_rng(3).uniform(0, 1.5, 6)
    ours = kernel.state(params)
    theirs = Statevector(qaoa_circuit(method, qubo, problem.scale, params[:3], params[3:], config.cardinality)).data
    overlap = np.vdot(theirs, ours)
    assert abs(abs(overlap) - 1) < 1e-10  # equal up to a global phase


def test_cost_expectation_on_dicke_state_is_mean_of_feasible_energies(problems, config):
    problem = problems["growth"]
    qubo = method_qubo(problem, "dicke_xy", config)
    kernel = make_kernel(problem, "dicke_xy", normalised_cost(problem, qubo), config)
    probs = kernel.probabilities(np.zeros(2))
    assert probs @ problem.energy == pytest.approx(problem.energy[problem.h1].mean(), abs=1e-14)


def test_sampled_bitstrings_decode_to_feasible_portfolios(problems, config):
    problem = problems["risk_sensitive"]
    counts = sample(problem, method_qubo(problem, "dicke_xy", config), "dicke_xy", np.array([0.4, 0.3]), config, seed=1)
    assert sum(counts.values()) == config.qaoa.shots
    assert all(problem.h1[index] for index in counts)


def test_tuned_penalty(problems, config):
    # balanced: the unpenalised minimum already has 3 holdings, so no penalty is needed
    assert tuned_penalty(problems["balanced"], config) == 0.0
    for name in ("growth", "risk_sensitive"):
        problem = problems[name]
        tuned = tuned_penalty(problem, config)
        full = float(np.ptp(problem.energy)) + config.qaoa.penalty_margin
        assert 0 < tuned < full
        assert problem.h1[np.argmin(energies(method_qubo(problem, "x_penalty_tuned", config)))]


def test_metrics_edge_cases(problems, config):
    from qhf.qaoa import run_metrics

    problem = problems["growth"]
    uniform = np.full(64, 1 / 64)
    metrics = run_metrics(problem, uniform, np.zeros(64), {problem.optimum: 1})
    assert not metrics["top_is_optimum"]  # a tie is not a win
    assert metrics["p_opt_given_valid"] == pytest.approx(1 / 20)
    assert all(p.h1_minimum_is_admissible for p in problems.values())


def test_answer_key_matches_exact_optimum(problems, config):
    names = {"growth": "HiTec+Hlth+Utils", "balanced": "HiTec+Hlth+Utils", "risk_sensitive": "NoDur+Hlth+Utils"}
    for name, problem in problems.items():
        bits = embed(index_to_bits(problem.optimum, problem.qubo.size), problem.free, 6)
        assert "+".join(c for c, b in zip(config.industries, bits) if b) == names[name]


def test_small_experiment_is_deterministic_and_rule_preserving(problems, config):
    cfg = replace(config, qaoa=replace(FAST_QAOA, layers=(1,), seeds=2, starts_per_seed=1, maxiter=40, shots=256))
    subset = {"risk_sensitive": problems["risk_sensitive"]}
    first = run_experiment(subset, cfg)
    second = run_experiment(subset, cfg)
    assert first.equals(second)
    dicke = first[first.method == "dicke_xy"]
    assert np.allclose(dicke.h1_mass, 1.0)
    assert (dicke.sampled_h1_share == 1.0).all()  # every measured shot is a valid 3-of-6 portfolio
    assert (first.sampled_admissible_share <= first.sampled_h1_share).all()
    assert ((first.p_opt >= 0) & (first.p_opt <= 1)).all()
