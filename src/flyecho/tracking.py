from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class TrackEstimate:
    time_s: float
    distance_m: float
    velocity_m_s: float
    closing_speed_m_s: float
    ttc_s: float


class RangeTracker:
    """Exponentially smoothed range-rate estimator."""

    def __init__(self, velocity_alpha: float = 0.35) -> None:
        if not 0.0 < velocity_alpha <= 1.0:
            raise ValueError("velocity_alpha must be in (0, 1]")
        self.velocity_alpha = velocity_alpha
        self._prev_t: float | None = None
        self._prev_d: float | None = None
        self._velocity = 0.0

    def update(self, time_s: float, distance_m: float) -> TrackEstimate:
        if not math.isfinite(time_s):
            raise ValueError("time_s must be finite")
        if not math.isfinite(distance_m) or distance_m <= 0:
            raise ValueError("distance_m must be finite and positive")

        if self._prev_t is not None and self._prev_d is not None:
            dt = time_s - self._prev_t
            if dt <= 1e-6:
                raise ValueError("time_s must increase between samples")
            raw_v = (distance_m - self._prev_d) / dt
            a = self.velocity_alpha
            self._velocity = a * raw_v + (1.0 - a) * self._velocity

        self._prev_t = time_s
        self._prev_d = distance_m

        closing = max(0.0, -self._velocity)
        ttc = distance_m / closing if closing > 1e-6 else math.inf

        return TrackEstimate(
            time_s=time_s,
            distance_m=distance_m,
            velocity_m_s=self._velocity,
            closing_speed_m_s=closing,
            ttc_s=ttc,
        )
