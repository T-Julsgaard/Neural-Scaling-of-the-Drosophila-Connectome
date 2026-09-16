"""Chronological validation episode and serializable state, without a campaign API."""
import copy
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from .data import encode
from .rules import Learner


def stream(seed, component):
    if seed not in range(5):
        raise ValueError("This runner is validation-only: seeds 0..4")
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([2, 0, seed, 0, component])))


class ValidationEpisode:
    """One 384-trial episode; paired latent data never enters the learner."""

    def __init__(self, projection, arm="feedback", seed=0, family="reversal", eta=0.001, temperature=0.2):
        if family not in ("reversal", "interference"):
            raise ValueError("Unknown family")
        if not np.isfinite(temperature) or temperature <= 0:
            raise ValueError("Invalid temperature")
        self.projection = np.array(projection, dtype=np.float64, copy=True)
        if self.projection.shape != (40, 73):
            raise ValueError("Validation episode requires the 40x73 D05 projection")
        self.seed, self.family, self.temperature = seed, family, temperature
        self.priority = stream(seed, 1).permutation(73)
        prototype_rng = stream(seed, 2)
        prototypes = []
        for _ in range(2):
            pair = []
            while len(pair) < 2:
                u = np.zeros(40)
                u[prototype_rng.choice(40, 10, replace=False)] = 1.
                if not pair or not np.array_equal(u, pair[0]):
                    pair.append(u)
            prototypes.extend(pair)
        self.prototypes = np.array(prototypes)
        self.order = prototype_rng.permutation(2)
        self.noise = stream(seed, 3)
        outcome_rng = stream(seed, 4)
        self.uniforms = stream(seed, 5).random(384)
        self.rewards = np.empty((384, 2), dtype=np.int8)
        for t in range(384):
            preference = self.preferred(t)
            self.rewards[t] = np.where(outcome_rng.random(2) < np.where(np.arange(2) == preference, 0.8, 0.2), 1, -1)
        self.learner = Learner.initial(arm, 73, eta)
        self.trial, self.records = 0, []

    def preferred(self, trial):
        canonical = int(self.family == "reversal" and 128 <= trial < 256)
        return int(np.flatnonzero(self.order == canonical)[0])

    def _present(self, trial, noise, sigma):
        offset = 2 if self.family == "interference" and 128 <= trial < 256 else 0
        cues = self.prototypes[offset + self.order]
        return np.array([encode(self.projection, np.clip(u + noise.normal(0., sigma, 40), 0., 1.), self.priority) for u in cues])

    def step(self):
        if self.trial >= 384:
            raise StopIteration("Episode complete")
        t = self.trial
        cues = self._present(t, self.noise, 0.1)
        p = self.learner.probabilities(cues, self.temperature)
        choice = int(self.uniforms[t] >= p[0])
        reward = int(self.rewards[t, choice])
        diagnostic = self.learner.update(cues[choice], reward)
        record = {"trial": t, "choice": choice, "reward": reward,
                  "preferred_probability": float(p[self.preferred(t)]), **diagnostic}
        self.records.append(record)
        self.trial += 1
        return record

    def run_until(self, stop):
        if not self.trial <= stop <= 384:
            raise ValueError("Invalid stop trial")
        while self.trial < stop:
            self.step()
        return self.records

    def probe(self, sigma=0.1):
        # Clone the entire episode, including RNG. Probes cannot consume training noise.
        # Different probe keys distinguish checkpoints and sigma without new benchmark components.
        clone = copy.deepcopy(self)
        clone.noise = np.random.Generator(np.random.PCG64(np.random.SeedSequence(
            [2, 0, self.seed, 0, 3, 32, self.trial, int(round(sigma * 1000))])))
        return float(np.mean([clone.learner.probabilities(
            clone._present(0, clone.noise, sigma), clone.temperature)[clone.preferred(0)] for _ in range(32)]))

    def payload(self):
        return {"schema_version": 1, "kind": "validation_episode_not_campaign", "numpy_version": np.__version__,
                "seed_derivation": [2, 0, self.seed, 0, "component"],
                "projection": self.projection.tolist(), "projection_sha256": hashlib.sha256(self.projection.astype("<f8").tobytes()).hexdigest(),
                "seed": self.seed, "family": self.family, "temperature": self.temperature,
                "arm": self.learner.arm, "eta": self.learner.eta, "gamma": self.learner.gamma,
                "plus": self.learner.plus.tolist(), "minus": self.learner.minus.tolist(),
                "priority": self.priority.tolist(), "prototypes": self.prototypes.tolist(), "order": self.order.tolist(),
                "noise_state": copy.deepcopy(self.noise.bit_generator.state), "uniforms": self.uniforms.tolist(),
                "rewards": self.rewards.tolist(), "trial": self.trial, "records": copy.deepcopy(self.records)}

    def checkpoint(self, path):
        path = Path(path)
        payload = self.payload()
        serialized = json.dumps(payload, sort_keys=True, allow_nan=False)
        envelope = {"sha256": hashlib.sha256(serialized.encode()).hexdigest(), "payload": payload}
        tmp = path.with_name(path.name + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(envelope, f, sort_keys=True, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    @classmethod
    def restore(cls, path, expected_projection):
        envelope = json.loads(Path(path).read_text(encoding="utf-8"))
        p = envelope["payload"]
        if hashlib.sha256(json.dumps(p, sort_keys=True, allow_nan=False).encode()).hexdigest() != envelope["sha256"]:
            raise ValueError("Checkpoint digest mismatch")
        if p["schema_version"] != 1 or p["kind"] != "validation_episode_not_campaign" or p["numpy_version"] != np.__version__:
            raise ValueError("Checkpoint schema/environment mismatch")
        if p["projection_sha256"] != hashlib.sha256(np.asarray(expected_projection, dtype="<f8").tobytes()).hexdigest():
            raise ValueError("Checkpoint graph mismatch")
        obj = cls(expected_projection, p["arm"], p["seed"], p["family"], p["eta"], p["temperature"])
        if not np.array_equal(obj.projection, p["projection"]):
            raise ValueError("Checkpoint graph payload differs")
        for name in ("priority", "prototypes", "order", "uniforms", "rewards"):
            if not np.array_equal(getattr(obj, name), p[name]):
                raise ValueError("Checkpoint deterministic inputs differ: " + name)
        if not 0 <= p["trial"] <= 384 or len(p["records"]) != p["trial"]:
            raise ValueError("Checkpoint chronology mismatch")
        obj.learner = Learner(p["arm"], p["eta"], p["plus"], p["minus"], p["gamma"])
        obj.noise.bit_generator.state = p["noise_state"]
        obj.trial, obj.records = p["trial"], p["records"]
        return obj
