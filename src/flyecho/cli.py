from __future__ import annotations

import argparse
import math

from .brain import FlyBrainController
from .sensor import EchoSimulator
from .tracking import RangeTracker


def run_demo(distance: float, velocity: float, seconds: float, seed: int) -> int:
    sensor = EchoSimulator(initial_distance_m=distance, radial_velocity_m_s=velocity, seed=seed)
    tracker = RangeTracker()
    brain = FlyBrainController()

    t = 0.0
    next_ping = 0.0
    dt = 0.005
    last_line = -1.0
    threat_seen = False
    track = tracker.update(0.0, sensor.true_distance(0.0))
    state = brain.step(track, dt)

    while t <= seconds:
        if t + 1e-12 >= next_ping:
            m = sensor.ping(t)
            track = tracker.update(m.time_s, m.distance_m)
            next_ping = t + 1.0 / max(state.ping_hz, 0.1)

        state = brain.step(track, dt)
        threat_seen = threat_seen or state.threat

        if t - last_line >= 0.25 or state.gf_spike:
            ttc = " inf" if math.isinf(track.ttc_s) else f"{track.ttc_s:4.2f}"
            print(
                f"t={t:5.2f}s  d={track.distance_m:4.2f}m  "
                f"v={track.velocity_m_s:+5.2f}m/s  TTC={ttc}s  "
                f"ping={state.ping_hz:4.1f}Hz  danger={state.danger_score:4.2f}  "
                f"threat={'YES' if state.threat else 'no'}"
            )
            last_line = t
        t += dt

    print(f"\nThreat event observed: {'yes' if threat_seen else 'no'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="flyecho")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("demo", help="Run the closed-loop ultrasonic simulation")
    d.add_argument("--distance", type=float, default=2.4, help="initial range in metres")
    d.add_argument("--velocity", type=float, default=-0.45, help="radial velocity in m/s; negative approaches")
    d.add_argument("--seconds", type=float, default=6.0)
    d.add_argument("--seed", type=int, default=7)

    h = sub.add_parser("hardware", help="Run against an ESP32 ultrasonic bridge")
    h.add_argument("--port", required=True, help="serial port, e.g. COM3 or /dev/ttyUSB0")
    h.add_argument("--baud", type=int, default=115200)
    h.add_argument("--seconds", type=float, default=None)
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return run_demo(args.distance, args.velocity, args.seconds, args.seed)
    if args.command == "hardware":
        from .hardware import run_serial_loop
        try:
            return run_serial_loop(args.port, args.baud, args.seconds)
        except RuntimeError as exc:
            print(f"error: {exc}")
            return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
