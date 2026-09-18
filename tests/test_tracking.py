from flyecho.tracking import RangeTracker


def test_tracker_sees_approach():
    tr = RangeTracker(velocity_alpha=1.0)
    tr.update(0.0, 2.0)
    x = tr.update(1.0, 1.5)
    assert x.velocity_m_s == -0.5
    assert x.closing_speed_m_s == 0.5
    assert abs(x.ttc_s - 3.0) < 1e-9

def test_tracker_rejects_non_monotonic_time_without_corrupting_state():
    tr = RangeTracker(velocity_alpha=1.0)
    tr.update(1.0, 2.0)
    try:
        tr.update(0.5, 1.8)
    except ValueError as exc:
        assert "increase" in str(exc)
    else:
        raise AssertionError("non-monotonic sample must be rejected")

    x = tr.update(2.0, 1.5)
    assert x.velocity_m_s == -0.5


def test_tracker_rejects_non_finite_samples():
    tr = RangeTracker()
    for time_s, distance_m in ((float("nan"), 1.0), (0.0, float("nan")), (0.0, float("inf"))):
        try:
            tr.update(time_s, distance_m)
        except ValueError:
            pass
        else:
            raise AssertionError("non-finite sample must be rejected")

