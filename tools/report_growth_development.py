"""Summarize nested development results and plot descriptive growth profiles."""
import json
import os
from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from exp002.campaign import atomic_json, read_json
from exp003.development import grid, stream
from exp003.growth import ARMS, SIZES

FOLDER = ROOT / "results/exp003_development"
METRICS = ("acquisition", "early_reversal", "retention_after", "robustness_0.3")
LABELS = {"clone": "Clone", "structured": "Structured", "uniform": "Uniform", "degree_null": "Degree null", "whole_uniform": "Whole uniform"}


def interval(values):
    a = np.asarray(values, dtype=float)
    if a.shape != (10,):
        raise ValueError("Expected ten independent block values")
    random = stream("development", 100, 2, 7)
    boot = a[random.integers(0, 10, (10000, 10))].mean(axis=1)
    return {"mean": float(a.mean()), "interval": np.quantile(boot, [.025, .975]).tolist(),
            "block_values": a.tolist(), "coverage": .95, "interpretation": "descriptive development only"}


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


def main():
    selection = read_json(FOLDER / "selection.json")
    report = read_json(FOLDER / "report.json")
    frozen = read_json(FOLDER / "contract.json")["frozen_utc"]
    elapsed = (datetime.fromisoformat(report["completed_utc"]) - datetime.fromisoformat(frozen)).total_seconds()
    blocks = [read_json(FOLDER / f"block_{b}/summary.json")["conditions"] for b in range(100, 110)]
    profiles = {}
    for label, index in (("shared", selection["index"]), ("fixed_EXP002", 6)):
        rows = {}
        for arm in (*ARMS, "whole_uniform"):
            for size in SIZES:
                rows[f"{arm}_{size}_full"] = profile(blocks, size, arm, "full", index)
        for mode, arms in (("fixed4", ("clone", "structured", "degree_null")), ("bottleneck", ("structured", "degree_null"))):
            for arm in arms:
                for size in (73, 110):
                    rows[f"{arm}_{size}_{mode}"] = profile(blocks, size, arm, mode, index)
        profiles[label] = rows
    contrasts = {}
    for label, rows in profiles.items():
        local = {}
        def difference(a, b):
            return {m: interval(np.array(a["metrics"][m]["block_values"]) - np.array(b["metrics"][m]["block_values"])) for m in METRICS}
        for arm in (*ARMS, "whole_uniform"):
            for size in (110, 146):
                local[f"{arm}_{size}_minus_73"] = difference(rows[f"{arm}_{size}_full"], rows[f"{arm}_73_full"])
        for mode in ("full", "fixed4", "bottleneck"):
            local[f"structured_minus_null_110_{mode}"] = difference(rows[f"structured_110_{mode}"], rows[f"degree_null_110_{mode}"])
        for mode, arms in (("fixed4", ("clone", "structured", "degree_null")), ("bottleneck", ("structured", "degree_null"))):
            for arm in arms:
                local[f"{arm}_110_minus_73_{mode}"] = difference(rows[f"{arm}_110_{mode}"], rows[f"{arm}_73_{mode}"])
        contrasts[label] = local
    analysis = {"stage": "development", "selection": selection, "profiles": profiles, "paired_contrasts": contrasts,
                "uncertainty": "95% paired block bootstrap; descriptive after development selection, not H3 confirmation"}
    atomic_json(FOLDER / "analysis.json", analysis)
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
    sys.path.insert(1, str(ROOT / ".cache/baseline-plot-deps"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), layout="constrained")
    colors = {"clone": "#947142", "structured": "#247f6b", "uniform": "#387cc0", "degree_null": "#a557ac", "whole_uniform": "#7b7b7b"}
    titles = ("Acquisition", "Early reversal", "Post-interference retention", "Robustness (noise 0.3)")
    for ax, metric, title in zip(axes.flat, METRICS, titles):
        for arm in (*ARMS, "whole_uniform"):
            values = [profiles["shared"][f"{arm}_{n}_full"]["metrics"][metric] for n in SIZES]
            mean = np.array([v["mean"] for v in values])
            lo, hi = np.array([v["interval"] for v in values]).T
            ax.plot(SIZES, mean, marker="o", color=colors[arm], lw=1.7, ls="--" if arm == "whole_uniform" else "-", label=LABELS[arm])
            ax.fill_between(SIZES, lo, hi, color=colors[arm], alpha=.07)
        ax.set(title=title, xlabel="KC feature count", ylabel="Preferred-choice probability", xticks=SIZES)
        ax.grid(alpha=.17)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=5, frameon=False)
    fig.suptitle("EXP-003 development: shared setting, proportional sparsity\nTen task blocks; shaded 95% descriptive intervals", fontsize=13)
    fig.savefig(FOLDER / "development_profiles.png", dpi=170)
    fig.savefig(FOLDER / "development_profiles.svg")
    plt.close(fig)
    selected = selection["selected"]
    lines = ["# EXP-003 fresh development results", "", "2026-09-12. **Ten development blocks completed; confirmation has not run.**",
             "", f"The frozen selection rule chose **eta={selected['eta']:g}, temperature={selected['temperature']:g}** for generic delta, shared across main growth rules and sizes. The same blocks selected the setting and generated the comparisons below, so intervals are descriptive rather than confirmatory.", "",
             "[Frozen protocol](EXP-003-development-protocol.md), [validation evidence](../research/exp003_development_validation.json), [run audit](../research/runs/EXP-003-development.json), [complete profiles and contrasts](../results/exp003_development/analysis.json).", "",
             "![Development growth profiles](../results/exp003_development/development_profiles.png)", "", "## Selected-setting profiles", "",
             "Means across ten independent task blocks after averaging three nested graph replicates. Native N=73 is reused once per block. Main curves use proportional sparsity and full readouts. All values below are probabilities.", "",
             "| Rule | Cells | Acquisition | Early reversal | Retention | Robustness 0.3 |", "|---|---:|---:|---:|---:|---:|"]
    for size in (73, 110, 146):
        for arm in (*ARMS, "whole_uniform"):
            if size == 73 and arm not in ("clone", "whole_uniform"):
                continue
            row = profiles["shared"][f"{arm}_{size}_full"]
            label = "Native baseline" if size == 73 and arm == "clone" else LABELS[arm]
            lines.append(f"| {label} | {size} | " + " | ".join(f"{row['metrics'][m]['mean']:.3f}" for m in METRICS) + " |")
    lines += ["", "## Paired changes", "", "Change from each arm's 73-cell baseline; values in brackets are descriptive 95% block intervals.", "",
              "| Rule / size | Early reversal change | Retention change | Acquisition change |", "|---|---|---|---|"]
    def formatted(value):
        return f"{value['mean']:+.3f} [{value['interval'][0]:+.3f}, {value['interval'][1]:+.3f}]"
    for arm in ARMS:
        for size in (110, 146):
            row = contrasts["shared"][f"{arm}_{size}_minus_73"]
            lines.append(f"| {LABELS[arm]} / {size} | " + " | ".join(formatted(row[m]) for m in ("early_reversal", "retention_after", "acquisition")) + " |")
    lines += ["", "## Sparsity and readout controls", "", "The selected shared setting is also used here. Each change compares 110 with its own matching 73-cell control; the bottleneck has 64 trainable output weights at both sizes.", "",
              "| Control | Rule | Early reversal change | Retention change |", "|---|---|---|---|"]
    for mode, arms in (("fixed4", ("clone", "structured", "degree_null")), ("bottleneck", ("structured", "degree_null"))):
        for arm in arms:
            row = contrasts["shared"][f"{arm}_110_minus_73_{mode}"]
            lines.append(f"| {mode} | {LABELS[arm]} | {formatted(row['early_reversal'])} | {formatted(row['retention_after'])} |")
    primary = contrasts["shared"]["structured_minus_null_110_full"]
    lines += ["", "Structured minus degree-null early reversal at 110 cells: **" + formatted(primary["early_reversal"]) + "**. The confirmatory practical margin remains +0.05 and its 98.33% test is unrun.", "", "## Feature participation and selection", "",
              "| Rule at 110 cells | Added cells unused | Cell covariance participation rank |", "|---|---:|---:|"]
    for arm in ARMS:
        features = profiles["shared"][f"{arm}_110_full"]["cell_features"]
        lines.append(f"| {LABELS[arm]} | {100*features['added_never_active_fraction']['mean']:.1f}% | {features['covariance_participation_rank']['mean']:.2f} |")
    lines += ["", "Unused cells refer to both presented cues under this synthetic encoder, not biologically inactive neurons. More feature diversity does not necessarily improve learning. The complete artifact reports native/added participation, readout ranks, edges, contact counts and output weights.", "",
              "| Learning rate | Temperature | Equal-weight development score |", "|---:|---:|---:|"]
    for config, score in zip(grid(), selection["scores"]):
        lines.append(f"| {config.eta:g} | {config.temperature:g} | {score:.6f} |")
    lines += ["", "Each size/arm combination receives equal weight, including the reused native baseline. Whole-uniform, fixed-four and bottleneck results do not enter selection. Fixed EXP-002 eta=.01/T=.1 sensitivity results are retained under `fixed_EXP002` in the analysis artifact, including paired changes and learning curves.", "", "## Execution and limits", "",
              f"All 36 preflight tests passed. The run completed 800 representation conditions, 16,000 reset episode batches and {report['configuration_episodes']:,} configuration-episodes, with no excluded episodes or numerical failures. Frozen native controls remained at chance. The audit recomputed every condition's metrics and checked shared selection against the frozen weighting rule.", "",
              f"Elapsed time from the original contract freeze to completion, including interruptions/recovery: {elapsed:.1f} seconds using up to {report['workers']} CPU workers. The final invocation took {report['wall_seconds_this_invocation']:.1f} seconds. Summed worker episode CPU time: {report['summed_worker_cpu_seconds']:.1f} seconds; maximum individual worker peak memory: {report['max_worker_peak_memory_bytes']/1024**2:.1f} MiB (not total concurrent memory). Retained run artifacts before this report: {report['retained_bytes_before_report']/1024**2:.1f} MiB. These measurements belong to the current session, not the colleague's workstation. No energy measurement.", "",
              "Confirmation blocks 1000-1019 remain untouched. No broad cognition, adult circuit, biological superiority or evolutionary-search result follows from these development measurements. The selected setting is frozen for a possible confirmation campaign; the next research decision must account for reversal/retention tradeoffs and both controls.", ""]
    (ROOT / "experiments/EXP-003-development-results.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(json.dumps({"selected": selected, "organization_reversal": primary["early_reversal"], "report": "experiments/EXP-003-development-results.md"}))


if __name__ == "__main__":
    main()
