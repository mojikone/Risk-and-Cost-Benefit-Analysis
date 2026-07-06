"""
Break-even / sensitivity analysis for the Majlas scheme.
Answers: at what dam cost, benefit level, or discount rate does BCR reach 1?
Uses the authoritative annual avoided damage from the last run.
"""
import csv, os
import config as C
import economics as EC
from economics import _pv_annuity

M = 1e6


def read_avoided():
    rows = list(csv.DictReader(open(os.path.join(C.OUT_DIR, "damage_by_plan.csv"))))
    b = {int(r["rp"]): float(r["total"]) for r in rows if r["condition"] == "baseline"}
    s = {int(r["rp"]): float(r["total"]) for r in rows if r["condition"] == "scheme"}
    return EC.aed(b) - EC.aed(s)


def metrics(avoided, dam=C.COST_DAM_OMR, chan=C.COST_CHANNEL_OMR, reloc=168080,
            r=C.DISCOUNT_RATE):
    pv_ben = sum(avoided / (1 + r) ** i for i in range(1, C.HORIZON_YEARS + 1))
    md = C.MAINT_DAM_RATE * dam
    mc = C.MAINT_CHANNEL_RATE * chan
    pv_maint = (sum(md / (1 + r) ** i for i in range(C.MAINT_DAM_START, C.HORIZON_YEARS + 1))
                + sum(mc / (1 + r) ** i for i in range(C.MAINT_CHANNEL_START, C.HORIZON_YEARS + 1)))
    initial = dam + chan + reloc
    pv_costs = initial + pv_maint
    return pv_ben / pv_costs, pv_ben - pv_maint - initial, pv_ben, pv_costs


def main():
    avoided = read_avoided()
    reloc = 168080
    a1 = _pv_annuity(1, 1)                       # benefit annuity factor
    a5 = _pv_annuity(1, C.MAINT_DAM_START)       # dam-maint annuity factor
    pv_ben = avoided * a1
    mc_pv = C.MAINT_CHANNEL_RATE * C.COST_CHANNEL_OMR * _pv_annuity(1, C.MAINT_CHANNEL_START)

    print(f"Annual avoided damage (authoritative): {avoided:,.0f} OMR/yr")
    print(f"Current BCR {metrics(avoided)[0]:.3f}\n")

    # ---- break-even dam cost (channel & benefit fixed)
    be_dam = (pv_ben - C.COST_CHANNEL_OMR - reloc - mc_pv) / (1 + C.MAINT_DAM_RATE * a5)
    print(f"Break-even DAM cost for BCR=1:  {be_dam/M:.2f} M OMR   (actual 50.0 M)")

    # ---- required benefit multiplier
    _, _, _, pv_costs = metrics(avoided)
    mult = pv_costs / pv_ben
    print(f"Required avoided damage for BCR=1: {avoided*mult/M:.2f} M/yr = {mult:.1f}x current\n")

    print("--- BCR / NPV vs dam capital cost ---")
    print(f"{'Dam cost (M)':>13} {'BCR':>7} {'NPV (M)':>10}")
    for dam in [50, 40, 30, 20, 10, 5, be_dam/M]:
        bcr, npv, *_ = metrics(avoided, dam=dam * M)
        print(f"{dam:>13.1f} {bcr:>7.3f} {npv/M:>10.1f}")

    print("\n--- BCR vs benefit multiplier (assets/damage x N) ---")
    print(f"{'x benefit':>10} {'avoided M/yr':>13} {'BCR':>7} {'NPV (M)':>10}")
    for m in [1, 2, 4, mult, 8]:
        bcr, npv, *_ = metrics(avoided * m)
        print(f"{m:>10.1f} {avoided*m/M:>13.2f} {bcr:>7.3f} {npv/M:>10.1f}")

    print("\n--- BCR vs discount rate (best case, lower r) ---")
    print(f"{'r %':>6} {'BCR':>7} {'NPV (M)':>10}")
    for r in [0.0, 0.01, 0.025, 0.04, 0.06]:
        bcr, npv, *_ = metrics(avoided, r=r)
        print(f"{r*100:>6.1f} {bcr:>7.3f} {npv/M:>10.1f}")


if __name__ == "__main__":
    main()
