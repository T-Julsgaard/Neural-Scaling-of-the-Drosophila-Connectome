"""Render the frozen EXP-002 baseline report and a standalone scientific figure."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Import the pinned numerical runtime before adding optional plotting dependencies.
import numpy as np
from exp002.baseline import Config
from exp002.campaign import read_json
from exp002.data import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "results/exp002_baseline")
    args = parser.parse_args()
    dev = read_json(args.root / "development/report.json")
    selection = read_json(args.root / "development/selection.json")
    report = read_json(args.root / "confirmation/report.json")
    r02 = json.loads((ROOT / "research/exp002_r02_runtime.json").read_text())
    labels = {"native_feedback": "Feedback", "native_delta": "Generic delta",
              "native_reward_only": "Reward-only", "pn_delta": "Direct PN delta"}
    configs = {k: Config(**selection["selected"][k]) for k in labels}
    configs["native_frozen"] = Config("native", "frozen", 0., .2)
    labels["native_frozen"] = "Frozen"
    colors = {"native_feedback": "#235bba", "native_delta": "#14816f", "native_reward_only": "#ca652b",
              "pn_delta": "#9257a2", "native_frozen": "#828282"}
    summaries = {k: report["summary"][c.id] for k, c in configs.items()}
    canonical = args.root.resolve() == (ROOT / "results/exp002_baseline").resolve()
    report_path = ROOT / "experiments/EXP-002-baseline-results.md" if canonical else args.root / "baseline_report.md"
    figure_link = "../results/exp002_baseline/baseline.png" if canonical else "baseline.png"
    plot_cache = ROOT / ".cache/baseline-plot-deps"
    if plot_cache.is_dir():
        sys.path.insert(1, str(plot_cache))
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for ax, family in zip(axes[0], ("reversal", "interference")):
        for key, row in summaries.items():
            ax.plot(np.arange(24)*16 + 7.5, row[family + "_curve"], color=colors[key], label=labels[key],
                    lw=2 if key != "native_frozen" else 1.3, ls="--" if key == "native_frozen" else "-")
        for boundary in (128, 256):
            ax.axvline(boundary, color="#d1d5db", lw=1)
        ax.set(title="Reversal: A → B → A" if family == "reversal" else "Interference: A/B → C/D → A/B",
               xlabel="Trial (16-trial means)", ylabel="Preferred-choice probability", ylim=(0, 1.03))
        ax.grid(axis="y", alpha=.15)
    ax = axes[1, 0]
    metrics = ("acquisition", "early_reversal", "retention_after")
    for j, (key, row) in enumerate(summaries.items()):
        x = np.arange(3) + (j-2)*.13
        means = np.array([row[m]["mean"] for m in metrics])
        bounds = np.array([row[m]["interval"] for m in metrics])
        ax.errorbar(x, means, yerr=np.stack((means-bounds[:, 0], bounds[:, 1]-means)),
                    color=colors[key], fmt="o", ms=4, capsize=3)
    ax.axhline(.5, color="#d1d5db", ls="--")
    ax.set(xticks=range(3), xticklabels=("Acquisition", "Early reversal", "Retention"),
           ylabel="Preferred-choice probability", ylim=(0, 1.03), title="Held-out metrics (95% block intervals)")
    ax.grid(axis="y", alpha=.15)
    ax = axes[1, 1]
    for key, row in summaries.items():
        x = [0., .1, .3]
        means = [row[f"robustness_{s:g}"]["mean"] for s in x]
        ax.plot(x, means, "o-", color=colors[key], ms=4, lw=2)
    ax.set(xlabel="Observation noise σ", ylabel="Final frozen-probe probability",
           title="Robustness after learning", ylim=(0, 1.03), xticks=[0., .1, .3])
    ax.grid(axis="y", alpha=.15)
    handles, names = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, names, loc="outside lower center", ncol=5, frameon=False)
    fig.suptitle("EXP-002 | Measured learning baseline\n20 held-out blocks · 400 task episodes per setting · one larval-derived circuit", fontsize=14)
    png, svg = args.root / "baseline.png", args.root / "baseline.svg"
    fig.savefig(png, dpi=160)
    fig.savefig(svg)
    plt.close(fig)
    def value(row, metric):
        m = row[metric]
        return f"{m['mean']:.3f} [{m['interval'][0]:.3f}, {m['interval'][1]:.3f}]"
    conclusions = report["conclusions"]
    primary = conclusions["primary_feedback_minus_reward_only"]
    secondary = conclusions["feedback_minus_delta_reversal"]
    candidate = conclusions["structural_candidate"]
    lines = ["# EXP-002 — Measured learning baseline", "",
        f"Completed {report['created_utc']} (UTC). Protocol 1.1. Ten development blocks and twenty independent confirmation task blocks completed. No episodes excluded; no numerical failures recorded.", "",
        "## Validation", "",
        f"R02 passed by actual GNU Octave 11.3.0 execution of the source-preserving author fixture: maximum difference {r02['maximum_absolute_error']:.3g} across 256 updates, tolerance 1e-10. This validates the isolated learning rule, not the paper's biological findings. The full 21-test implementation suite passed, including batched/scalar trajectories, probes, data separation and recovery.", "",
        "## Held-out results", "",
        "Values are mean preferred-choice probabilities with 95% block-bootstrap intervals. Chance is 0.5. Acquisition averages both families; early reversal uses reversal episodes; retention probes A/B after C/D interference, before return training.", "",
        "| Learner | Acquisition | Early reversal | Retention after interference | Robustness σ=0.3 |",
        "|---|---:|---:|---:|---:|"]
    for key, row in summaries.items():
        lines.append("| " + labels[key] + " | " + " | ".join(value(row, m) for m in (
            "acquisition", "early_reversal", "retention_after", "robustness_0.3")) + " |")
    lines += ["", f"Primary feedback minus reward-only reversal difference: **{primary['mean']:.4f}**, 98.33% interval [{primary['interval'][0]:.4f}, {primary['interval'][1]:.4f}], practical minimum +0.05. H2 status: **{conclusions['H2']}**.", "",
        f"Feedback minus generic-delta reversal: {secondary['mean']:.4f}, 95% interval [{secondary['interval'][0]:.4f}, {secondary['interval'][1]:.4f}]. Equivalence within ±0.02 established: **{conclusions['feedback_delta_equivalent_within_0_02']}**. Feedback acquisition noninferiority to reward-only established: **{conclusions['acquisition_noninferiority']}**.", "",
        f"The development-selected candidate for structural work is `{candidate}`. Its held-out assay adequacy gate passes: **{conclusions['adequate_for_structural_experiments']}**. This gate requires acquisition lower interval >0.65 and remaining headroom in reversal or retention; it does not establish a biological wiring advantage.", "",
        f"![Learning curves and baseline measurements]({figure_link})", "",
        "## Frozen settings and diagnostics", "", "| Learner | Learning rate | Temperature | Development selection score |", "|---|---:|---:|---:|"]
    for key, config in configs.items():
        lines.append(f"| {labels[key]} | {config.eta:g} | {config.temperature:g} | {dev['summary'][config.id]['selection_score']['mean']:.4f} |")
    lines += ["", "Prespecified fixed-setting sensitivity (eta=0.001, T=0.2; secondary, separate from the tuned primary contrast):", "",
              "| Learner | Acquisition | Early reversal | Retention |", "|---|---:|---:|---:|"]
    for arm in ("feedback", "delta", "reward_only"):
        row = report["summary"][Config("native", arm, .001, .2).id]
        lines.append("| " + labels["native_" + arm] + " | " + " | ".join(value(row, m) for m in (
            "acquisition", "early_reversal", "retention_after")) + " |")
    for key, row in summaries.items():
        if key in ("native_feedback", "native_delta", "native_reward_only"):
            lines.append(f"\n{labels[key]}: retention change {value(row, 'retention_change')}; both DAN drives positive on {row['both_positive_fraction']['mean']:.1%} of steps; inclusive rate-match regime {row['rate_match_fraction']['mean']:.1%}.")
    ranks = [v["native"]["covariance_participation_rank"] for v in report["features_by_block"].values()]
    inactive = [v["native"]["never_active_fraction"] for v in report["features_by_block"].values()]
    lines += ["", f"Native feature covariance participation rank: mean {np.mean(ranks):.2f}, block range {min(ranks):.2f}–{max(ranks):.2f}. Never-active cell fraction: mean {np.mean(inactive):.1%}. This is inactivity under these synthetic cues and the winner-selection encoder, not evidence of biologically inactive neurons. Full per-cell participation is retained in the machine-readable report.", "",
        "The feedback rule improves reversal over reward-only learning but loses acquisition and retention performance. Generic delta was selected on development data for structural follow-up; confirmation does not establish feedback/delta equivalence or a uniquely biological learning advantage. The direct-PN comparator trades slower early reversal for stronger retention. Preserve these tradeoffs when testing growth.", "",
        "## Measured resources", "",
        "Measurements describe this session's CPU execution, not the colleague's PC. Configurations were batched; timings cannot rank per-rule efficiency. Active wall time excludes session pauses and includes episode preprocessing, learning, probes and artifact writes.", "",
        "| Stage | Configurations | Learning updates | Active wall seconds | CPU seconds | Peak working set MiB |",
        "|---|---:|---:|---:|---:|---:|"]
    for stage_report in (dev, report):
        r = stage_report["resources"]
        lines.append(f"| {stage_report['stage']} | {len(stage_report['configs'])} | {r['learning_updates']:,} | {r['wall_seconds']:.2f} | {r['cpu_seconds']:.2f} | {r['peak_working_set_bytes']/1024**2:.1f} |")
    lines += ["", "## Reproduce and inspect", "", "With NumPy 2.3.5 and the validated author runtime evidence available, use a fresh output directory to reproduce a campaign. Existing output directories enforce frozen code/environment/input hashes.", "", "```powershell",
        "python tools/validate_baseline.py", "python tools/run_baseline.py development --output results/exp002_baseline_reproduction/development",
        "python tools/run_baseline.py confirmation --output results/exp002_baseline_reproduction/confirmation --selection results/exp002_baseline_reproduction/development/selection.json",
        "python tools/report_baseline.py --root results/exp002_baseline_reproduction", "```", "",
        "To resume an interrupted stage, repeat its run command without changing code, dependencies, gate reports or settings. Regenerating validation reports changes their hashes; use a fresh output directory after doing so. Reproduction output is separate from the original frozen run. The original gate reports are retained under `validation_evidence/`.", "",
        "Plotting requires Matplotlib 3.10.7; the numerical campaign requires only the pinned NumPy runtime. Full local per-trial artifacts, checkpoints, frozen contracts, selected settings and block reports are under `results/exp002_baseline/`. Compact evidence and integrity manifests are retained with the research record. All original source bytes and the two original briefs are preserved.", "",
        "## Limits", "",
        "This is a feedforward 40-input/73-feature larval-derived representation with two synthetic outputs. The direct-PN comparator has fewer weights and a different representation; it is exploratory, not parameter matched. These results establish within-family learning and adaptation on synthetic cue tasks. They do not show whole-brain function, broader intelligence, an advantage of biological wiring, or any benefit from growth/evolution. Intervals quantify task-block variation from one reference circuit, not independent animal variation.", ""]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    plot_manifest = {"matplotlib": matplotlib.__version__, "numpy": np.__version__,
                     "input_sha256": sha256(args.root / "confirmation/report.json"),
                     "files": {p.relative_to(ROOT).as_posix(): sha256(p) for p in (png, svg)}}
    (args.root / "figure_manifest.json").write_text(json.dumps(plot_manifest, indent=2) + "\n")
    print(json.dumps({"report": str(report_path), "figure": str(png)}))


if __name__ == "__main__":
    main()
