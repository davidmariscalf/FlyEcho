from flyecho.brain import FlyBrainController
from flyecho.tracking import TrackEstimate


def run(brain, track, seconds=1.0, dt=0.005):
    return [brain.step(track, dt) for _ in range(int(seconds / dt))]


def test_safe_scene_stays_low_rate():
    brain = FlyBrainController()
    track = TrackEstimate(0.0, 3.0, 0.0, 0.0, float("inf"))
    states = run(brain, track)
    assert max(s.ping_hz for s in states) < 10.0


def test_approaching_scene_triggers_threat():
    brain = FlyBrainController()
    track = TrackEstimate(0.0, 0.55, -0.7, 0.7, 0.78)
    states = run(brain, track)
    assert any(s.gf_spike for s in states)
    assert any(s.threat for s in states)
    assert max(s.ping_hz for s in states) == brain.max_ping_hz
