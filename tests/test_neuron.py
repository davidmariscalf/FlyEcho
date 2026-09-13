from flyecho.neurons import LIFNeuron


def test_lif_spikes_under_sustained_current():
    n = LIFNeuron(tau_s=0.05, threshold=1.0)
    spiked = False
    for _ in range(200):
        spiked = n.step(1.5, 0.005) or spiked
    assert spiked
