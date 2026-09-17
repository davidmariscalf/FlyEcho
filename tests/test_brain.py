from flyecho.brain import FlyBrainController
from flyecho.tracking import TrackEstimate


def run(brain, track, seconds=1.0, dt=0.005):
    return [brain.step(track, dt) for _ in range(int(seconds / dt))]


def test_safe_scene_stays_low_rate():
    brain = FlyBrainController()
    track = TrackEstimate(0.0, 3.0, 0.0, 0.0, float("inf"))
    states = run(brain, track)
    assert max(s.ping_hz for s in states) < 10.0
    assert not any(s.gf_spike for s in states)
    assert not any(s.ttm_spike for s in states)
    assert not any(s.psi_spike for s in states)
    assert not any(s.dlm_spike for s in states)


def test_approaching_scene_triggers_threat_and_motor_pathway():
    brain = FlyBrainController()
    track = TrackEstimate(0.0, 0.55, -0.7, 0.7, 0.78)
    states = run(brain, track)
    assert any(s.gf_spike for s in states)
    assert any(s.threat for s in states)
    assert max(s.ping_hz for s in states) == brain.max_ping_hz

    gf_indices = [i for i, s in enumerate(states) if s.gf_spike]
    assert gf_indices
    assert any(states[i].ttm_spike for i in gf_indices)
    assert any(states[i].psi_spike for i in gf_indices)
    assert any(states[i].dlm_spike for i in gf_indices)
