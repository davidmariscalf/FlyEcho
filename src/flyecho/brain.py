from __future__ import annotations

from dataclasses import dataclass
import math

from .neurons import LIFNeuron
from .tracking import TrackEstimate


@dataclass(frozen=True)
class BrainState:
    ping_hz: float
    threat: bool
    lc4_spike: bool
    lplc2_spike: bool
    gf_spike: bool
    danger_score: float


class FlyBrainController:
    """Compact fly-inspired active-sensing circuit.

    Biological inspiration: in Drosophila, LC4 and LPLC2 visual projection
    neurons encode complementary looming features and both make direct input
    to the giant fiber (GF) escape neuron. Here we preserve that parallel
    convergence motif while replacing vision with engineered echo-derived
    features. This is a bio-inspired controller, not a literal simulation of
    the fly's native sensory system.
    """

    def __init__(
        self,
        min_ping_hz: float = 5.0,
        max_ping_hz: float = 30.0,
        threat_hold_s: float = 0.20,
    ) -> None:
        self.min_ping_hz = min_ping_hz
        self.max_ping_hz = max_ping_hz
        self.threat_hold_s = threat_hold_s
        self.lc4 = LIFNeuron(tau_s=0.050, threshold=0.85, refractory_s=0.020)
        self.lplc2 = LIFNeuron(tau_s=0.055, threshold=0.85, refractory_s=0.020)
        self.gf = LIFNeuron(tau_s=0.025, threshold=0.72, refractory_s=0.050)
        self._threat_left_s = 0.0

    @staticmethod
    def _clamp01(x: float) -> float:
        return min(1.0, max(0.0, x))

    def _drives(self, track: TrackEstimate) -> tuple[float, float, float, float]:
        proximity = self._clamp01((1.8 - track.distance_m) / 1.6)
        closing = self._clamp01(track.closing_speed_m_s / 0.8)
        urgency = 0.0 if math.isinf(track.ttc_s) else self._clamp01((3.0 - track.ttc_s) / 2.6)
        danger = self._clamp01(0.35 * proximity + 0.35 * closing + 0.45 * urgency)
        return proximity, closing, urgency, danger

    def step(self, track: TrackEstimate, dt_s: float) -> BrainState:
        proximity, closing, urgency, danger = self._drives(track)

        lc4_current = 0.18 + 1.45 * closing + 0.30 * urgency
        lc4_spike = self.lc4.step(lc4_current, dt_s)

        lplc2_current = 0.18 + 1.10 * proximity + 0.80 * urgency
        lplc2_spike = self.lplc2.step(lplc2_current, dt_s)

        gf_current = (
            0.08
            + 0.35 * danger
            + (0.95 if lc4_spike else 0.0)
            + (1.05 if lplc2_spike else 0.0)
        )
        gf_spike = self.gf.step(gf_current, dt_s)

        if gf_spike:
            self._threat_left_s = self.threat_hold_s
        else:
            self._threat_left_s = max(0.0, self._threat_left_s - dt_s)

        threat = self._threat_left_s > 0.0
        adaptive = self.min_ping_hz + danger * (self.max_ping_hz - self.min_ping_hz)
        if threat:
            adaptive = self.max_ping_hz

        return BrainState(
            ping_hz=adaptive,
            threat=threat,
            lc4_spike=lc4_spike,
            lplc2_spike=lplc2_spike,
            gf_spike=gf_spike,
            danger_score=danger,
        )
