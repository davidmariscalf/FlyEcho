from __future__ import annotations

import argparse
import json
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
    motor_seen = False
    track = tracker.update(0.0, sensor.true_distance(0.0))
    state = brain.step(track, dt)

    while t <= seconds:
        if t + 1e-12 >= next_ping:
            m = sensor.ping(t)
            track = tracker.update(m.time_s, m.distance_m)
            next_ping = t + 1.0 / max(state.ping_hz, 0.1)

        state = brain.step(track, dt)
        threat_seen = threat_seen or state.threat
        motor_seen = motor_seen or state.motor_command

        if t - last_line >= 0.25 or state.gf_spike:
            ttc = " inf" if math.isinf(track.ttc_s) else f"{track.ttc_s:4.2f}"
            motor = "J" if state.jump_command else "-"
            motor += "F" if state.flight_command else "-"
            print(
                f"t={t:5.2f}s  d={track.distance_m:4.2f}m  "
                f"v={track.velocity_m_s:+5.2f}m/s  TTC={ttc}s  "
                f"ping={state.ping_hz:4.1f}Hz  danger={state.danger_score:4.2f}  "
                f"threat={'YES' if state.threat else 'no'}  motor={motor}"
            )
            last_line = t
        t += dt

    print(f"\nThreat event observed: {'yes' if threat_seen else 'no'}")
    print(f"Motor-path event observed: {'yes' if motor_seen else 'no'}")
    return 0


def run_circuit(output_format: str) -> int:
    from .topology import ESCAPE_EDGES, ESCAPE_NODES, topology_dot, topology_json

    if output_format == "json":
        print(topology_json())
    elif output_format == "dot":
        print(topology_dot())
    else:
        for node in ESCAPE_NODES:
            print(f"{node.name:12}  {node.role}  [{node.biological_name}]")
        print()
        for edge in ESCAPE_EDGES:
            print(
                f"{edge.pre:12} -> {edge.post:12}  "
                f"{edge.kind:10} model_weight={edge.model_weight:g}"
            )
    return 0


def run_brian_demo(seconds: float, dt: float, lc4_drive: float, lplc2_drive: float) -> int:
    from .brian_backend import simulate_escape_network

    result = simulate_escape_network(
        duration_s=seconds,
        dt_s=dt,
        lc4_drive=lc4_drive,
        lplc2_drive=lplc2_drive,
    )
    print(json.dumps(result.spike_counts, indent=2, sort_keys=True))
    print(f"motor_output_seen={str(result.motor_output_seen).lower()}")
    return 0


def run_connectome_summary(path: str, min_weight: int, hubs: int) -> int:
    from .connectome import FlyWireEdgeList

    graph = FlyWireEdgeList.from_csv(path, min_weight=min_weight)
    print(json.dumps(graph.summary(), indent=2, sort_keys=True))
    if hubs:
        print("\nTop weighted hubs:")
        for neuron_id, weight in graph.hubs(limit=hubs):
            print(f"{neuron_id}\t{weight}")
    return 0


def run_annotations(path: str, search: str | None, limit: int) -> int:
    from .annotations import FlyWireAnnotations

    annotations = FlyWireAnnotations.from_path(path)
    print(json.dumps(annotations.summary(), indent=2, sort_keys=True))
    if search is not None:
        for row in annotations.search(search, limit=limit):
            print(
                f"{row.root_id}\t{row.cell_type or '-'}\t"
                f"{row.cell_class or '-'}\t{row.super_class or '-'}"
            )
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

    c = sub.add_parser("circuit", help="Inspect or export the escape-circuit topology")
    c.add_argument("--format", choices=("text", "json", "dot"), default="text")

    b = sub.add_parser("brian-demo", help="Run the escape motif with the optional Brian2 backend")
    b.add_argument("--seconds", type=float, default=0.25)
    b.add_argument("--dt", type=float, default=0.001)
    b.add_argument("--lc4-drive", type=float, default=1.35)
    b.add_argument("--lplc2-drive", type=float, default=1.35)

    cs = sub.add_parser("connectome-summary", help="Summarize a FlyWire-style edge list")
    cs.add_argument("path")
    cs.add_argument("--min-weight", type=int, default=1)
    cs.add_argument("--hubs", type=int, default=10)

    a = sub.add_parser("annotations", help="Inspect a FlyWire-style annotation table")
    a.add_argument("path")
    a.add_argument("--search", default=None)
    a.add_argument("--limit", type=int, default=20)
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
    if args.command == "circuit":
        return run_circuit(args.format)
    if args.command == "brian-demo":
        try:
            return run_brian_demo(args.seconds, args.dt, args.lc4_drive, args.lplc2_drive)
        except RuntimeError as exc:
            print(f"error: {exc}")
            return 2
    if args.command == "connectome-summary":
        return run_connectome_summary(args.path, args.min_weight, args.hubs)
    if args.command == "annotations":
        return run_annotations(args.path, args.search, args.limit)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
