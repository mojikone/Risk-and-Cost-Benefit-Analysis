"""
End-to-end Majlas flood-protection cost-benefit run.

  1. build 20 max-depth rasters (baseline + dam scheme, 10 return periods)
  2. integrate flood damage per raster against landuse depth-damage curves
  3. compute AED (baseline & scheme) -> annual avoided damage
  4. relocation cost from the project outline
  5. NPV and BCR

Depth source: authoritative HEC-RAS RAS Mapper "Depth (Max)" exports (2 m),
in Data/Depth (see config.ras_depth_path).

Outputs (in Risk/output):
  damage_by_plan.csv          damage per return period & class, baseline vs scheme
  aed_summary.csv             AED, avoided damage, relocation, NPV, BCR
"""
import os, csv
import config as C
import damage as DM
import economics as EC


def main():
    os.makedirs(C.OUT_DIR, exist_ok=True)
    gdf = DM.load_landuse()

    rows = []
    dmg_base, dmg_scheme = {}, {}
    missing = []
    for rp in C.RP_YEARS:
        for cond, store in [("baseline", dmg_base), ("scheme", dmg_scheme)]:
            tif = C.ras_depth_path(rp, cond)
            if not os.path.exists(tif):
                missing.append(f"{rp}yr {cond} -> {os.path.basename(tif)}")
                continue
            d = DM.damage_for_raster(tif, gdf)
            mx, wet = DM.raster_stats(tif)
            store[rp] = d["total"]
            rows.append(dict(rp=rp, condition=cond,
                             max_depth_m=mx, wet_area_km2=wet,
                             **{k: round(v, 1) for k, v in d.items()}))
            print(f"{rp:>6}yr {cond:8s}  Dtotal={d['total']:,.0f} OMR  "
                  f"maxdepth={mx:.1f}m  wet={wet:.2f}km2")

    if missing:
        print("\n[WARN] missing plan results, excluded:", "; ".join(missing))
    # monotonicity check (damage must rise with return period)
    for name, store in [("baseline", dmg_base), ("scheme", dmg_scheme)]:
        rps = sorted(store)
        for a, b in zip(rps, rps[1:]):
            if store[b] < store[a]:
                print(f"[WARN] {name}: damage NOT monotonic  {a}yr={store[a]:,.0f} "
                      f"> {b}yr={store[b]:,.0f}  <-- suspect HEC-RAS run")

    # AED integrated only over return periods present in BOTH conditions
    common = sorted(set(dmg_base) & set(dmg_scheme))
    dmg_base = {r: dmg_base[r] for r in common}
    dmg_scheme = {r: dmg_scheme[r] for r in common}
    print(f"\nAED integrated over RPs: {common}")

    # ---- write per-plan damage table
    cols = ["rp", "condition", "max_depth_m", "wet_area_km2",
            *DM._CLASSES, "total"]
    with open(os.path.join(C.OUT_DIR, "damage_by_plan.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

    # ---- AED, relocation, NPV/BCR
    aed_base = EC.aed(dmg_base)
    aed_scheme = EC.aed(dmg_scheme)
    annual_avoided = aed_base - aed_scheme
    reloc_total, reloc_by = EC.relocation_cost()
    fin = EC.npv_bcr(annual_avoided, reloc_total)

    with open(os.path.join(C.OUT_DIR, "aed_summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value_OMR"])
        w.writerow(["AED baseline", round(aed_base)])
        w.writerow(["AED scheme", round(aed_scheme)])
        w.writerow(["Annual avoided damage", round(annual_avoided)])
        w.writerow(["Relocation cost", round(reloc_total)])
        w.writerow(["Initial cost (dam+channel+relocation)", round(fin["initial_cost"])])
        w.writerow(["PV benefits (avoided, 50yr @2.5%)", round(fin["pv_benefits"])])
        w.writerow(["PV maintenance", round(fin["pv_maint"])])
        w.writerow(["PV costs", round(fin["pv_costs"])])
        w.writerow(["NPV", round(fin["npv"])])
        w.writerow(["BCR", round(fin["bcr"], 3)])
        w.writerow([])
        w.writerow(["Relocation by class", "area_in_m2", "unit_OMR/m2", "cost_OMR"])
        for c, v in reloc_by.items():
            w.writerow([c, round(v["area_in_m2"]), v["unit"], round(v["cost_OMR"])])

    print("\n================ SUMMARY ================")
    print(f"AED baseline           {aed_base:>16,.0f} OMR/yr")
    print(f"AED scheme             {aed_scheme:>16,.0f} OMR/yr")
    print(f"Annual avoided damage  {annual_avoided:>16,.0f} OMR/yr")
    print(f"Relocation cost        {reloc_total:>16,.0f} OMR")
    print(f"Initial cost           {fin['initial_cost']:>16,.0f} OMR")
    print(f"PV benefits            {fin['pv_benefits']:>16,.0f} OMR")
    print(f"PV maintenance         {fin['pv_maint']:>16,.0f} OMR")
    print(f"PV costs               {fin['pv_costs']:>16,.0f} OMR")
    print(f"NPV                    {fin['npv']:>16,.0f} OMR")
    print(f"BCR                    {fin['bcr']:>16.3f}")


if __name__ == "__main__":
    main()
