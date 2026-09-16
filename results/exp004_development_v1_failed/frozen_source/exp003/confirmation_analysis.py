"""Prospectively frozen nested block inference for EXP-003 confirmation."""
import numpy as np
from exp003.confirmation_inputs import stream
from exp003.growth import ARMS, SIZES

METRICS = ("acquisition", "early_reversal", "retention_after", "robustness_0.3")


def bootstrap_indices(stage="confirmation", block=1000):
    return stream(stage, block, 2, 7).integers(0, 20, (10000, 20))


def interval(values, coverage=.95, indices=None):
    a = np.asarray(values, dtype=float)
    if a.shape != (20,) or not np.isfinite(a).all():
        raise ValueError("Expected twenty finite independent block values")
    if coverage not in (.95, .9833):
        raise ValueError("Unplanned coverage")
    if indices is None:
        indices = bootstrap_indices()
    boot = a[indices].mean(axis=1)
    tail = (1-coverage)/2
    return {"mean": float(a.mean()), "interval": np.quantile(boot, [tail, 1-tail]).tolist(),
            "block_values": a.tolist(), "coverage": coverage}


def profile(blocks, size, arm, mode, index):
    selected = []
    for block in blocks:
        # The native no-growth full control is shared by main arms and fixed-four.
        query_arm = "clone" if size == 73 and arm != "whole_uniform" else arm
        query_mode = "full" if size == 73 and mode == "fixed4" else mode
        rows = [r for r in block if (r["size"], r["arm"], r["mode"]) == (size, query_arm, query_mode)]
        if len(rows) != (1 if size == 73 and arm != "whole_uniform" else 3):
            raise ValueError("Missing graph replicates")
        selected.append(rows)
    metrics = {}
    for metric in selected[0][0]["metrics"]:
        values = [np.mean([r["metrics"][metric][index] for r in rows], axis=0) for rows in selected]
        metrics[metric] = np.mean(values, axis=0).tolist() if metric.endswith("curve") else interval(values)
    features = {}
    for key in ("never_active_fraction", "native_never_active_fraction", "added_never_active_fraction",
                "covariance_participation_rank", "duplicate_normalized_columns"):
        features[key] = None if selected[0][0]["cell_features"][key] is None else interval([
            np.mean([r["cell_features"][key] for r in rows]) for rows in selected])
    return {"size": size, "arm": arm, "mode": mode, "config_index": index, "metrics": metrics, "cell_features": features,
            "readout_rank": interval([np.mean([r["readout_features"]["covariance_participation_rank"] for r in rows]) for rows in selected]),
            "edges_mean": float(np.mean([r["edges"] for rows in selected for r in rows])),
            "contacts_mean": float(np.mean([r["contacts"] for rows in selected for r in rows])),
            "readout_weights": selected[0][0]["readout_weights"]}



def analyze(blocks):
    if len(blocks) != 20:
        raise ValueError("All twenty blocks are required before analysis")
    rows = {}
    for arm in (*ARMS, "whole_uniform"):
        for size in SIZES:
            rows[f"{arm}_{size}_full"] = profile(blocks, size, arm, "full", 0)
    for mode, arms in (("fixed4", ("clone", "structured", "degree_null")), ("bottleneck", ("structured", "degree_null"))):
        for arm in arms:
            for size in (73, 110):
                rows[f"{arm}_{size}_{mode}"] = profile(blocks, size, arm, mode, 0)
    contrasts = {}
    def difference(a, b):
        return {m: interval(np.array(a["metrics"][m]["block_values"])-np.array(b["metrics"][m]["block_values"]))
                for m in a["metrics"] if not m.endswith("curve")}
    for arm in (*ARMS, "whole_uniform"):
        for size in (110, 146):
            contrasts[f"{arm}_{size}_minus_73"] = difference(rows[f"{arm}_{size}_full"], rows[f"{arm}_73_full"])
    for mode in ("full", "fixed4", "bottleneck"):
        contrasts[f"structured_minus_null_110_{mode}"] = difference(rows[f"structured_110_{mode}"], rows[f"degree_null_110_{mode}"])
    for mode, arms in (("fixed4", ("clone", "structured", "degree_null")), ("bottleneck", ("structured", "degree_null"))):
        for arm in arms:
            contrasts[f"{arm}_110_minus_73_{mode}"] = difference(rows[f"{arm}_110_{mode}"], rows[f"{arm}_73_{mode}"])
    primary = interval(contrasts["structured_minus_null_110_full"]["early_reversal"]["block_values"], .9833)
    low, high = primary["interval"]
    primary.update({"practical_margin": .05, "contrast": "structured_minus_null_110_full", "metric": "early_reversal",
                    "decision": "supports_practical_advantage" if low > .05 else
                    "against_practical_advantage" if high < .05 else "inconclusive"})
    for values in contrasts.values():
        values["acquisition"]["noninferiority_margin"] = -.02
        values["acquisition"]["noninferiority_passed"] = values["acquisition"]["interval"][0] > -.02
    return {"stage": "confirmation", "independent_blocks": list(range(1000, 1020)),
            "profiles": rows, "paired_contrasts": contrasts, "primary": primary,
            "uncertainty": "10,000 paired block bootstrap resamples; primary 98.33%; all other comparisons secondary exploratory 95%"}
