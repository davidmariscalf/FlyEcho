from __future__ import annotations

from dataclasses import dataclass
import random


SPEED_OF_SOUND_M_S = 343.0


@dataclass(frozen=True)
class EchoMeasurement:
    time_s: float
    distance_m: float
    round_trip_s: float
    amplitude: float


class EchoSimulator:
    """Simple point-target ultrasonic echo simulator."""

    def __init__(
        self,
        initial_distance_m: float = 2.0,
        radial_velocity_m_s: float = -0.35,
        noise_std_m: float = 0.004,
        seed: int = 7,
    ) -> None:
        if initial_distance_m <= 0:
            raise ValueError("initial_distance_m must be positive")
        self.initial_distance_m = initial_distance_m
        self.radial_velocity_m_s = radial_velocity_m_s
        self.noise_std_m = max(0.0, noise_std_m)
        self._rng = random.Random(seed)

    def true_distance(self, time_s: float) -> float:
        return max(0.03, self.initial_distance_m + self.radial_velocity_m_s * time_s)

    def ping(self, time_s: float) -> EchoMeasurement:
        d_true = self.true_distance(time_s)
        d_measured = max(0.02, d_true + self._rng.gauss(0.0, self.noise_std_m))
        round_trip = 2.0 * d_measured / SPEED_OF_SOUND_M_S
        amplitude = min(1.0, 0.16 / max(d_measured * d_measured, 1e-6))
        return EchoMeasurement(
            time_s=time_s,
            distance_m=d_measured,
            round_trip_s=round_trip,
            amplitude=amplitude,
        )
