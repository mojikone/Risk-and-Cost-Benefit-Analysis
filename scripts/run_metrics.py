"""
Compute non-monetized exposure metrics for all 20 runs and integrate an
Expected Annual value (people/plots) analogous to AED.

Outputs (Risk/output):
  landuse_inventory.csv      static: plots & area per landuse class
  exposure_by_rp.csv         per RP & condition: people, plots, flooded area
  exposure_summary.csv       expected-annual exposure, baseline vs scheme, avoided
"""
import os, csv
import config as C
import exposure as EX
import economics as EC

M = 1e6


def main():
    gdf = EX.load_landuse()

    # ---- static inventory
    inv = EX.landuse_inventory(gdf)
    with open(os.path.join(C.OUT_DIR, "landuse_inventory.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["landuse", "n_plots", "area_km2"])
        tot_n = tot_a = 0
        for k, v in inv.items():
            w.writerow([k, v["n_plots"], v["area_km2"]]); tot_n += v["n_plots"]; tot_a += v["area_km2"]
        w.writerow(["TOTAL", tot_n, round(tot_a, 3)])
    print("Landuse inventory:", {k: (v["n_plots"], v["area_km2"]) for k, v in inv.items()})

    # ---- per-RP exposure
    rows = []
    ppl = {"baseline": {}, "scheme": {}}
    for rp in C.RP_YEARS:
        for cond in ("baseline", "scheme"):
            tif = C.ras_depth_path(rp, cond)
            if not os.path.exists(tif):
                continue
            e = EX.exposure_for_raster(tif, gdf)
            e.update(rp=rp, condition=cond)
            rows.append(e)
            ppl[cond][rp] = e["people_exposed"]
            print(f"{rp:>6}yr {cond:8s}  people={e['people_exposed']:>6}  "
                  f">1m={e['people_gt1.0m']:>6}  plots={e['plots_inundated']:>4}  "
                  f"wet={e['wet_area_km2']:.2f}km2")

    cols = (["rp", "condition", "wet_area_km2", "people_exposed"]
            + [f"people_gt{b}m" for b in EX.DEPTH_BANDS]
            + ["plots_inundated"]
            + [f"plots_inund_{c}" for c in EX._CLASSES]
            + [f"flooded_km2_{c}" for c in EX._CLASSES])
    with open(os.path.join(C.OUT_DIR, "exposure_by_rp.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); [w.writerow(r) for r in rows]

    # ---- expected-annual population exposed (integrate over probability, like AED)
    eape_b = EC.aed(ppl["baseline"])
    eape_s = EC.aed(ppl["scheme"])
    with open(os.path.join(C.OUT_DIR, "exposure_summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["Expected annual people exposed - baseline", round(eape_b)])
        w.writerow(["Expected annual people exposed - scheme", round(eape_s)])
        w.writerow(["Annual people-exposure avoided", round(eape_b - eape_s)])
        w.writerow([])
        w.writerow(["RP", "people baseline", "people scheme", "people protected"])
        for rp in sorted(ppl["baseline"]):
            b, s = ppl["baseline"][rp], ppl["scheme"].get(rp, 0)
            w.writerow([rp, b, s, b - s])

    print(f"\nExpected annual people exposed: baseline {eape_b:,.0f}  "
          f"scheme {eape_s:,.0f}  avoided {eape_b - eape_s:,.0f} /yr")


if __name__ == "__main__":
    main()
