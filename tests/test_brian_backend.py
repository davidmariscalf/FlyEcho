import pytest

pytest.importorskip("brian2")

from flyecho.brian_backend import simulate_escape_network


def test_brian2_escape_network_reaches_motor_pathway():
    result = simulate_escape_network(duration_s=0.25, dt_s=0.001)
    assert result.spike_counts["LC4-like"] > 0
    assert result.spike_counts["LPLC2-like"] > 0
    assert result.spike_counts["GF-like"] > 0
    assert result.motor_output_seen
