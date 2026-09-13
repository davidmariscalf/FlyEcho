from flyecho.tracking import RangeTracker


def test_tracker_sees_approach():
    tr = RangeTracker(velocity_alpha=1.0)
    tr.update(0.0, 2.0)
    x = tr.update(1.0, 1.5)
    assert x.velocity_m_s == -0.5
    assert x.closing_speed_m_s == 0.5
    assert abs(x.ttc_s - 3.0) < 1e-9
