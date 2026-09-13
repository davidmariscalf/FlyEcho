from flyecho.hardware import format_ping_rate, parse_range_line


def test_hardware_protocol_helpers():
    assert format_ping_rate(12.345) == b"PING_HZ,12.35\n"
    assert format_ping_rate(100) == b"PING_HZ,30.00\n"
    assert parse_range_line("RANGE,0.7342\n") == 0.7342
    assert parse_range_line("noise") is None
    assert parse_range_line("RANGE,-1") is None
