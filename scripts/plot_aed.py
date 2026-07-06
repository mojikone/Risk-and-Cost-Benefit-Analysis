"""
Plot the Annual Expected Damage (AED) curves for baseline and dam+channel scheme.
Damage is plotted against annual exceedance probability (1/RP); the area under a
curve is that scenario's AED, and the area between the curves is the annual
avoided damage.  Two panels: probability axis (integral view) and return-period
axis (engineering view).
"""
import os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import config as C
import economics as EC

M = 1e6


def read_damage():
    rows = list(csv.DictReader(open(os.path.join(C.OUT_DIR, "damage_by_plan.csv"))))
    base = {int(r["rp"]): float(r["total"]) for r in rows if r["condition"] == "baseline"}
    sch = {int(r["rp"]): float(r["total"]) for r in rows if r["condition"] == "scheme"}
    return base, sch


def main():
    base, sch = read_damage()
    rps = sorted(base)
    p = np.array([1.0 / r for r in rps])          # exceedance probability
    db = np.array([base[r] for r in rps]) / M
    ds = np.array([sch[r] for r in rps]) / M

    aed_b = EC.aed(base) / M
    aed_s = EC.aed(sch) / M
    avoided = aed_b - aed_s

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.6))

    # ---- panel 1: probability axis (area = AED) ------------------------------
    order = np.argsort(p)
    pp, dbb, dss = p[order], db[order], ds[order]
    ax1.fill_between(pp, dss, dbb, color="#f0a54a", alpha=.75,
                     label=f"Avoided damage (AED = {avoided:.2f} M/yr)")
    ax1.fill_between(pp, 0, dss, color="#9db8c9", alpha=.55,
                     label=f"Scheme residual (AED = {aed_s:.2f} M/yr)")
    ax1.plot(pp, dbb, "-o", color="#2b3a55", lw=2, ms=5, label=f"Baseline (AED = {aed_b:.2f} M/yr)")
    ax1.plot(pp, dss, "-o", color="#c0562b", lw=2, ms=5, label="Dam + channel scheme")
    ax1.set_xlabel("Annual exceedance probability  (1 / return period)")
    ax1.set_ylabel("Flood damage  (million OMR)")
    ax1.set_title("AED — area under curve = expected annual damage")
    ax1.set_xlim(0, 0.52); ax1.set_ylim(0, None)
    ax1.legend(loc="upper right", fontsize=8, framealpha=.9)
    ax1.grid(alpha=.3)
    for r, x, y in zip(rps, p, db):
        if r in (2, 10, 100, 1000, 10000):
            ax1.annotate(f"{r}yr", (x, y), textcoords="offset points",
                         xytext=(4, 5), fontsize=7, color="#2b3a55")

    # ---- panel 2: return-period axis (engineering view) ----------------------
    ax2.plot(rps, db, "-o", color="#2b3a55", lw=2, ms=5, label="Baseline")
    ax2.plot(rps, ds, "-o", color="#c0562b", lw=2, ms=5, label="Dam + channel scheme")
    ax2.fill_between(rps, ds, db, color="#f0a54a", alpha=.6, label="Avoided (per event)")
    ax2.set_xscale("log")
    ax2.set_xlabel("Return period  (years, log scale)")
    ax2.set_ylabel("Flood damage  (million OMR)")
    ax2.set_title("Damage vs return period")
    ax2.set_xticks(rps); ax2.set_xticklabels([str(r) for r in rps], fontsize=7, rotation=45)
    ax2.legend(loc="upper left", fontsize=8); ax2.grid(alpha=.3, which="both")

    fig.suptitle(
        f"Majlas flood protection — AED curves   |   "
        f"AED baseline {aed_b:.2f}  ·  scheme {aed_s:.2f}  ·  "
        f"annual avoided {avoided:.2f} M OMR/yr",
        fontsize=11, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(C.OUT_DIR, "AED_curves.png")
    fig.savefig(out, dpi=140)
    print("saved", out, "| avoided =", round(avoided, 3), "M OMR/yr")


if __name__ == "__main__":
    main()
