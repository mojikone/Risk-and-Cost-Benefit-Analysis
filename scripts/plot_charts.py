"""
Report charts for the Majlas cost-benefit analysis:
  1. depth-damage curves (per land-use class) with max-value labels
  2. population exposure vs return period (total + life-safety >1 m) with avoided values
  3. damage by land-use class vs return period, baseline AND scheme, with totals on bars
Saved to output/chart_*.png
"""
import os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import config as C
import economics as EC

M = 1e6
PLOT = dict(Residential="#e6550d", Commercial="#d73027", Industrial="#756bb1",
            Roads="#636363", Agriculture="#31a354")


def fig_curves():
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    for name, col in PLOT.items():
        y = C.DAMAGE_CURVES[name]
        ax.plot(C.DAMAGE_DEPTHS, y, "-o", color=col, lw=2, ms=4, label=name)
        ax.annotate(f"{y[-1]:.1f}", (C.DAMAGE_DEPTHS[-1], y[-1]),
                    textcoords="offset points", xytext=(6, 0), fontsize=8.5,
                    color=col, va="center", fontweight="bold")
    ax.set_xlabel("Flood depth (m)"); ax.set_ylabel("Damage (OMR / m²)")
    ax.set_title("Depth–Damage Functions by Land-Use Class  (Oman, 2023 price level)")
    ax.set_xlim(0, 6.7); ax.grid(alpha=.3); ax.legend(loc="center right")
    fig.tight_layout(); fig.savefig(os.path.join(C.OUT_DIR, "chart_depth_damage_curves.png"), dpi=150)


def _exposure():
    r = list(csv.DictReader(open(os.path.join(C.OUT_DIR, "exposure_by_rp.csv"))))
    d = {(int(x["rp"]), x["condition"]): x for x in r}
    return d


def fig_exposure():
    d = _exposure(); rps = C.RP_YEARS
    col = lambda cond, k: [float(d[(rp, cond)][k]) for rp in rps]
    # EAPE (expected annual people exposed) via same integral as AED
    eape = lambda k: (EC.aed({rp: float(d[(rp, 'baseline')][k]) for rp in rps})
                      - EC.aed({rp: float(d[(rp, 'scheme')][k]) for rp in rps}))
    av_tot = eape("people_exposed"); av_life = eape("people_gt1.0m")

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    for ax, k, ttl, av in [(a1, "people_exposed", "People exposed to flooding", av_tot),
                           (a2, "people_gt1.0m", "People in >1 m water (life-safety)", av_life)]:
        b, s = col("baseline", k), col("scheme", k)
        ax.plot(rps, b, "-o", color="#2b3a55", lw=2, label="Baseline")
        ax.plot(rps, s, "-o", color="#c0562b", lw=2, label="Scheme")
        ax.fill_between(rps, s, b, color="#f0a54a", alpha=.5,
                        label=f"Avoided  (EAPE {av:,.0f}/yr)")
        ax.set_xscale("log"); ax.set_title(ttl); ax.set_xlabel("Return period (yr)")
        ax.set_ylabel("People"); ax.grid(alpha=.3, which="both"); ax.legend(loc="upper left")
        ax.set_xticks(rps); ax.set_xticklabels(rps, rotation=45, fontsize=7)
    fig.suptitle("Population Exposure — Baseline vs Scheme", weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(os.path.join(C.OUT_DIR, "chart_exposure.png"), dpi=150)


def fig_damage_class():
    r = list(csv.DictReader(open(os.path.join(C.OUT_DIR, "damage_by_plan.csv"))))
    data = {(int(x["rp"]), x["condition"]): x for x in r}
    rps = C.RP_YEARS; classes = ["Residential", "Commercial", "Industrial", "Roads", "Agriculture"]
    x = np.arange(len(rps))
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4), sharey=True)
    for ax, cond in zip(axes, ("baseline", "scheme")):
        bottom = np.zeros(len(rps))
        for c in classes:
            vals = np.array([float(data[(rp, cond)][c]) / M for rp in rps])
            ax.bar(x, vals, bottom=bottom, color=PLOT[c], label=c); bottom += vals
        for xi, tot in zip(x, bottom):
            ax.annotate(f"{tot:.1f}", (xi, tot), textcoords="offset points",
                        xytext=(0, 2), ha="center", fontsize=7.5, fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels([str(rp) for rp in rps], rotation=45)
        ax.set_xlabel("Return period (yr)"); ax.set_title(cond.title())
        ax.grid(alpha=.3, axis="y")
    axes[0].set_ylabel("Damage (M OMR)"); axes[1].legend(loc="upper left", fontsize=8)
    fig.suptitle("Flood Damage by Land-Use Class — Baseline vs Scheme  (total M OMR on bars)", weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(os.path.join(C.OUT_DIR, "chart_damage_by_class.png"), dpi=150)


if __name__ == "__main__":
    fig_curves(); fig_exposure(); fig_damage_class()
    print("charts written to", C.OUT_DIR)
