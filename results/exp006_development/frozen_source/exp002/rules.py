"""Float64 learning rules specified in experiments/EXP-002.md."""
from dataclasses import dataclass

import numpy as np

ARMS = ("frozen", "reward_only", "feedback", "delta")


@dataclass
class Learner:
    arm: str
    eta: float
    plus: np.ndarray
    minus: np.ndarray
    gamma: float = 0.1

    def __post_init__(self):
        self.plus = np.array(self.plus, dtype=np.float64, copy=True)
        self.minus = np.array(self.minus, dtype=np.float64, copy=True)
        if self.arm not in ARMS or not np.isfinite(self.eta) or self.eta < 0:
            raise ValueError("Invalid arm/learning rate")
        if not np.isfinite(self.gamma) or self.gamma < 0:
            raise ValueError("Invalid gamma")
        if self.plus.ndim != 1 or self.plus.size == 0 or self.minus.shape != self.plus.shape:
            raise ValueError("Expected equal nonempty weight vectors")
        self._check_weights(self.plus, self.minus)

    @classmethod
    def initial(cls, arm, n, eta=0.001, gamma=0.1):
        return cls(arm, eta, np.full(n, 0.1), np.full(n, 0.1), gamma)

    @staticmethod
    def _check_weights(*weights):
        if any(not np.isfinite(w).all() or (w < 0).any() or (w > 1e6).any() for w in weights):
            raise FloatingPointError("Nonfinite, negative, or >1e6 weight")

    def _activities(self, activities):
        s = np.asarray(activities, dtype=np.float64)
        if s.shape[-1:] != self.plus.shape or not np.isfinite(s).all() or (s < 0).any():
            raise ValueError("Invalid activities")
        return s

    def values(self, activities):
        return self._activities(activities) @ (self.plus - self.minus)

    def probabilities(self, activities, temperature):
        if not np.isfinite(temperature) or temperature <= 0:
            raise ValueError("Temperature must be positive and finite")
        q = self.values(activities)
        if q.shape != (2,):
            raise ValueError("Exactly two cues required")
        logits = (q - np.max(q)) / temperature
        p = np.exp(logits)
        return p / p.sum()

    def update(self, activity, reward):
        s = self._activities(activity)
        if s.ndim != 1 or reward not in (-1, 1):
            raise ValueError("One chosen activity and signed reward required")
        q = float(self.values(s))
        raw_plus = self.gamma * float(s.sum()) - q + reward
        raw_minus = self.gamma * float(s.sum()) + q - reward
        d_plus, d_minus = max(0., raw_plus), max(0., raw_minus)
        error = reward - q
        drive = {"frozen": 0., "reward_only": float(reward),
                 "feedback": d_plus - d_minus, "delta": error}[self.arm]
        change = self.eta * s * drive
        plus = np.maximum(0., self.plus + change)
        minus = np.maximum(0., self.minus - change)
        self._check_weights(plus, minus)  # Fail before committing either side.
        self.plus, self.minus = plus, minus
        return {"q": q, "d_plus": d_plus, "d_minus": d_minus,
                "both_strictly_positive": raw_plus > 0 and raw_minus > 0,
                "rate_match_regime": raw_plus >= 0 and raw_minus >= 0,
                "drive": drive}
