from __future__ import annotations

from dataclasses import dataclass

from .topology import edge_weight


@dataclass(frozen=True)
class Brian2Result:
    duration_s: float
    spike_counts: dict[str, int]

    @property
    def motor_output_seen(self) -> bool:
        return bool(self.spike_counts.get("TTMn-like", 0) or self.spike_counts.get("DLMn-like", 0))


def brian2_available() -> bool:
    try:
        import brian2  # noqa: F401
    except ImportError:
        return False
    return True


def _require_brian2():
    try:
        import brian2 as b2
    except ImportError as exc:
        raise RuntimeError(
            'Brian2 is optional. Install the simulator extra with: pip install -e ".[simulation]"'
        ) from exc
    return b2


def simulate_escape_network(
    *,
    duration_s: float = 0.25,
    dt_s: float = 0.001,
    lc4_drive: float = 1.35,
    lplc2_drive: float = 1.35,
) -> Brian2Result:
    """Run the six-node escape motif in Brian2.

    This backend is a simulator cross-check and scaling path, not a claim that
    the normalized parameters are fitted Drosophila membrane properties.
    """

    if duration_s <= 0:
        raise ValueError("duration_s must be positive")
    if dt_s <= 0:
        raise ValueError("dt_s must be positive")
    if lc4_drive < 0 or lplc2_drive < 0:
        raise ValueError("input drives must be non-negative")

    b2 = _require_brian2()
    b2.start_scope()

    eqs = """
    dv/dt = (-v + drive) / tau : 1 (unless refractory)
    drive : 1
    tau : second
    """

    def neuron(name: str, tau_ms: float, refractory_ms: float):
        group = b2.NeuronGroup(
            1,
            eqs,
            threshold="v > 1",
            reset="v = 0",
            refractory=refractory_ms * b2.ms,
            method="euler",
            dt=dt_s * b2.second,
            name=name,
        )
        group.tau = tau_ms * b2.ms
        group.v = 0
        group.drive = 0
        return group

    lc4 = neuron("lc4_like", 50.0, 20.0)
    lplc2 = neuron("lplc2_like", 55.0, 20.0)
    gf = neuron("gf_like", 25.0, 50.0)
    ttm = neuron("ttmn_like", 15.0, 30.0)
    psi = neuron("psi_like", 15.0, 30.0)
    dlm = neuron("dlmn_like", 20.0, 30.0)
    lc4.drive = lc4_drive
    lplc2.drive = lplc2_drive

    def connect(pre, post, jump: float, name: str):
        syn = b2.Synapses(pre, post, on_pre=f"v_post += {jump}", name=name)
        syn.connect()
        return syn

    synapses = (
        connect(lc4, gf, edge_weight("LC4-like", "GF-like"), "lc4_to_gf"),
        connect(lplc2, gf, edge_weight("LPLC2-like", "GF-like"), "lplc2_to_gf"),
        connect(gf, ttm, edge_weight("GF-like", "TTMn-like"), "gf_to_ttm"),
        connect(gf, psi, edge_weight("GF-like", "PSI-like"), "gf_to_psi"),
        connect(psi, dlm, edge_weight("PSI-like", "DLMn-like"), "psi_to_dlm"),
    )

    groups = {
        "LC4-like": lc4,
        "LPLC2-like": lplc2,
        "GF-like": gf,
        "TTMn-like": ttm,
        "PSI-like": psi,
        "DLMn-like": dlm,
    }
    monitors = {name: b2.SpikeMonitor(group) for name, group in groups.items()}

    network = b2.Network(*groups.values(), *synapses, *monitors.values())
    network.run(duration_s * b2.second)

    return Brian2Result(
        duration_s=duration_s,
        spike_counts={name: int(monitor.num_spikes) for name, monitor in monitors.items()},
    )
