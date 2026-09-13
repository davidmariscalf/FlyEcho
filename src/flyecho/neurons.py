from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LIFNeuron:
    """Minimal leaky-integrate-and-fire neuron.

    Units are intentionally normalized. This is a computational abstraction,
    not a biophysical model of a specific Drosophila neuron.
    """

    tau_s: float = 0.050
    threshold: float = 1.0
    reset: float = 0.0
    refractory_s: float = 0.008
    membrane: float = 0.0
    refractory_left_s: float = 0.0

    def step(self, current: float, dt_s: float) -> bool:
        if dt_s <= 0:
            raise ValueError("dt_s must be positive")

        if self.refractory_left_s > 0.0:
            self.refractory_left_s = max(0.0, self.refractory_left_s - dt_s)
            self.membrane = self.reset
            return False

        self.membrane += dt_s * (-self.membrane + current) / self.tau_s

        if self.membrane >= self.threshold:
            self.membrane = self.reset
            self.refractory_left_s = self.refractory_s
            return True
        return False
