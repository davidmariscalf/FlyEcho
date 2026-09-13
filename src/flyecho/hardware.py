from __future__ import annotations

from dataclasses import dataclass
import time

from .brain import FlyBrainController, BrainState
from .tracking import RangeTracker, TrackEstimate


def format_ping_rate(hz: float) -> bytes:
    """Encode a ping-rate command for the ESP32 bridge."""
    hz = min(30.0, max(1.0, float(hz)))
    return f"PING_HZ,{hz:.2f}\n".encode("ascii")


def parse_range_line(line: str) -> float | None:
    """Parse RANGE,<metres> from the ESP32 bridge."""
    line = line.strip()
    if not line.startswith("RANGE,"):
        return None
    try:
        value = float(line.split(",", 1)[1])
    except ValueError:
        return None
    return value if value > 0 else None


@dataclass(frozen=True)
class HardwareSample:
    track: TrackEstimate
    brain: BrainState


def run_serial_loop(port: str, baud: int = 115200, seconds: float | None = None) -> int:
    """Run the closed loop against the ESP32 bridge."""
    try:
        import serial  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            'Hardware mode requires pyserial. Install with: pip install -e ".[hardware]"'
        ) from exc

    tracker = RangeTracker()
    brain = FlyBrainController()
    start = time.monotonic()
    previous = start

    with serial.Serial(port, baudrate=baud, timeout=0.25) as ser:
        ser.reset_input_buffer()
        ser.write(format_ping_rate(brain.min_ping_hz))

        while True:
            now = time.monotonic()
            if seconds is not None and now - start >= seconds:
                break

            raw = ser.readline().decode("ascii", errors="ignore")
            distance = parse_range_line(raw)
            if distance is None:
                continue

            t = now - start
            dt = max(1e-3, now - previous)
            previous = now
            track = tracker.update(t, distance)
            state = brain.step(track, dt)
            ser.write(format_ping_rate(state.ping_hz))

            ttc = "inf" if track.ttc_s == float("inf") else f"{track.ttc_s:.2f}"
            print(
                f"t={t:6.2f}s  d={track.distance_m:5.3f}m  "
                f"v={track.velocity_m_s:+5.2f}m/s  TTC={ttc:>5}s  "
                f"ping={state.ping_hz:4.1f}Hz  threat={'YES' if state.threat else 'no'}"
            )
    return 0
