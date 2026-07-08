"""
Presentation-friendly charts: flood hazard composition, life-safety reduction,
cost-benefit balance and the multi-criteria decision score.
Saved to output/chart_*.png
"""
import os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import config as C

M = 1e6
HCOL = {1:"#0000ff", 2:"#00ecff", 3:"#00a504", 4:"#00ff30", 5:"#fff900", 6:"#f41f1f"}
HLAB = {1:"H1 safe", 2:"H2", 3:"H3", 4:"H4 unsafe for people", 5:"H5", 6:"H6 buildings fail"}
# 2-yr baseline hazard grid was not exported
RPS = [5, 10, 25, 50, 100, 200, 500, 1000, 10000]


def _haz():
    rows = list(csv.DictReader(open(os.path.join(C.OUT_DIR, "hazard", "hazard_class_summary.csv"))))
    d = {}
    for r in rows:
        d[(int(r["rp"]), r["condition"], int(r["hclass"]))] = r
    agg = {(int(r["rp"]), r["condition"]): r
           for r in csv.DictReader(open(os.path.join(C.OUT_DIR, "hazard", "hazard_by_rp.csv")))}
    return d, agg


def _stacked(ax, d, cond, metric, title, ylab):
    x = np.arange(len(RPS)); bottom = np.zeros(len(RPS))
    for cl in range(1, 7):
        v = np.array([float(d[(rp, cond, cl)][metric]) if (rp, cond, cl) in d else 0 for rp in RPS])
        ax.bar(x, v, bottom=bottom, color=HCOL[cl], edgecolor="white", linewidth=.4,
               label=HLAB[cl] if cond == "baseline" else None)
        bottom += v
    for xi, tot in zip(x, bottom):
        ax.annotate(f"{tot:,.0f}", (xi, tot), textcoords="offset points", xytext=(0, 3),
                    ha="center", fontsize=8, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([str(r) for r in RPS], rotation=45, fontsize=8)
    ax.set_title(title); ax.set_ylabel(ylab); ax.set_xlabel("Return period (yr)")
    ax.grid(alpha=.3, axis="y")


def fig_hazard_people(d):
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), sharey=True)
    for ax, cond in zip(axes, ("baseline", "scheme")):
        _stacked(ax, d, cond, "people", cond.title(), "People")
    axes[0].legend(fontsize=8, loc="upper left")
    fig.suptitle("People by flood hazard class — Baseline vs Scheme", weight="bold")
    fig.tight_layout(rect=[0, 0, 1, .95])
    fig.savefig(os.path.join(C.OUT_DIR, "chart_hazard_people.png"), dpi=150); plt.close(fig)


def fig_hazard_plots_area(d):
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9), sharex=True)
    for j, cond in enumerate(("baseline", "scheme")):
        _stacked(axes[0][j], d, cond, "plots", f"Plots — {cond.title()}", "Plots")
        _stacked(axes[1][j], d, cond, "area_ha", f"Area — {cond.title()}", "Area (ha)")
    axes[0][0].legend(fontsize=8, loc="upper left")
    fig.suptitle("Plots and inundated area by flood hazard class", weight="bold")
    fig.tight_layout(rect=[0, 0, 1, .96])
    fig.savefig(os.path.join(C.OUT_DIR, "chart_hazard_plots_area.png"), dpi=150); plt.close(fig)


def fig_h4plus(agg):
    b = [float(agg[(rp, "baseline")]["people_H4plus"]) for rp in RPS]
    s = [float(agg[(rp, "scheme")]["people_H4plus"]) for rp in RPS]
    x = np.arange(len(RPS)); w = .38
    fig, ax = plt.subplots(figsize=(11, 5.4))
    ax.bar(x - w/2, b, w, color="#2b3a55", label="Baseline")
    ax.bar(x + w/2, s, w, color="#c0562b", label="Scheme")
    for xi, bb, ss in zip(x, b, s):
        if bb > 0:
            ax.annotate(f"−{(1-ss/bb)*100:.0f}%", (xi, max(bb, ss)), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=9, fontweight="bold", color="#1a6b1a")
    ax.set_xticks(x); ax.set_xticklabels([str(r) for r in RPS], rotation=45)
    ax.set_xlabel("Return period (yr)"); ax.set_ylabel("People in hazard H4+ (unsafe for people)")
    ax.set_title("People exposed to hazard unsafe for life (H4+) — reduction delivered by the scheme", weight="bold")
    ax.legend(); ax.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(os.path.join(C.OUT_DIR, "chart_hazard_h4plus.png"), dpi=150); plt.close(fig)


def fig_cost_benefit():
    pv_b, pv_m, init = 7_765_253, 13_558_148, 80_168_080
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.bar(["PV of benefits"], [pv_b/M], color="#31a354", width=.55)
    ax.bar(["PV of costs"], [init/M], color="#c0562b", width=.55, label="Initial cost")
    ax.bar(["PV of costs"], [pv_m/M], bottom=[init/M], color="#e6a17a", width=.55, label="PV maintenance")
    ax.annotate(f"{pv_b/M:.1f}", (0, pv_b/M), ha="center", va="bottom", fontweight="bold")
    ax.annotate(f"{(init+pv_m)/M:.1f}", (1, (init+pv_m)/M), ha="center", va="bottom", fontweight="bold")
    ax.set_ylabel("Present value (M OMR)")
    ax.set_title("Benefits vs costs (50 yr @ 4.2%)   —   NPV −86.0 M OMR,  BCR 0.083", weight="bold")
    ax.legend(); ax.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(os.path.join(C.OUT_DIR, "chart_cost_benefit.png"), dpi=150); plt.close(fig)


def fig_mca():
    crit = ["Economic return\n(BCR / NPV)", "Life safety\n(flood hazard)", "Design-standard\ncompliance",
            "Access to essential\nservices", "Livelihoods and\nproperty", "Environment and\nwadi morphology"]
    wt = [40, 25, 10, 10, 10, 5]; sc = [1, 5, 5, 4, 3, 3]
    wsc = [w/100*s for w, s in zip(wt, sc)]
    cols = ["#c0562b", "#31a354", "#31a354", "#6baed6", "#6baed6", "#9db8c9"]
    y = np.arange(len(crit))[::-1]
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.barh(y, wsc, color=cols, height=.6)
    for yi, v, w, s in zip(y, wsc, wt, sc):
        ax.annotate(f"{v:.2f}   (w {w}%, score {s}/5)", (v, yi), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=9)
    ax.set_yticks(y); ax.set_yticklabels(crit, fontsize=9)
    ax.set_xlim(0, 1.9); ax.set_xlabel("Weighted contribution to overall score")
    ax.set_title(f"Multi-criteria decision assessment — overall {sum(wsc):.2f} / 5", weight="bold")
    ax.grid(alpha=.3, axis="x")
    fig.tight_layout(); fig.savefig(os.path.join(C.OUT_DIR, "chart_mca.png"), dpi=150); plt.close(fig)


if __name__ == "__main__":
    d, agg = _haz()
    fig_hazard_people(d); fig_hazard_plots_area(d); fig_h4plus(agg); fig_cost_benefit(); fig_mca()
    print("extra charts written to", C.OUT_DIR)
