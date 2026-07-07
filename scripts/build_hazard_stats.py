"""
Australian flood-hazard (H1-H6) exposure statistics per return period and condition.
Hazard rasters (Data/Hazard/Hazard <RP>yr[D].tif) are classified 1-6 per the AIDR
Guideline 7-3 combined hazard curves. For each RP/condition this computes, by class:
  - inundated area (ha)
  - number of plots (each plot assigned to its worst/maximum hazard class)
  - number of people (GHS-POP)
plus aggregates: people/plots in H4+ ("unsafe for people") and H5+ (building failure).
Outputs: output/hazard/hazard_class_summary.csv, output/hazard/hazard_by_rp.csv
"""
import os, csv, numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
from rasterio.windows import from_bounds, Window
from rasterio.warp import reproject, Resampling
import config as C

HZDIR = os.path.join(C.DATA_DIR, "Hazard")
OUTDIR = os.path.join(C.OUT_DIR, "hazard")
CLASSES = [1, 2, 3, 4, 5, 6]
DESC = {1: "H1 generally safe", 2: "H2 unsafe small vehicles", 3: "H3 unsafe vehicles/children/elderly",
        4: "H4 unsafe for people", 5: "H5 unsafe; buildings damaged", 6: "H6 unsafe; buildings fail"}


def hz_path(rp, cond):
    return os.path.join(HZDIR, f"Hazard {rp}yr{'D' if cond=='scheme' else ''}.tif")


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    gdf = gpd.read_file(C.LANDUSE_SHP).reset_index(drop=True)
    minx, miny, maxx, maxy = gdf.total_bounds
    minx, miny, maxx, maxy = minx-150, miny-150, maxx+150, maxy+150

    # reference window (all hazard rasters share the grid)
    ref = None
    for rp in C.RP_YEARS:
        for cond in ("baseline", "scheme"):
            if os.path.exists(hz_path(rp, cond)):
                ref = hz_path(rp, cond); break
        if ref:
            break
    with rasterio.open(ref) as s:
        wf = from_bounds(minx, miny, maxx, maxy, s.transform)
        win = Window(int(wf.col_off), int(wf.row_off), int(wf.width), int(wf.height))
        wt = s.window_transform(win)
        shape = (int(win.height), int(win.width))
        px = abs(s.res[0] * s.res[1]); crs = s.crs

    pid = rasterize([(g, i+1) for i, g in enumerate(gdf.geometry)],
                    out_shape=shape, transform=wt, fill=0, dtype="int32")
    N = len(gdf)

    with rasterio.open(os.path.join(C.DATA_DIR, "Population", "GHS POP 2025 Majlas.tif")) as p:
        pop = p.read(1).astype("float64"); nod = p.nodata
        pop = np.where((pop == nod) | ~np.isfinite(pop), 0.0, pop); pop[pop < 0] = 0.0
        dens = pop / abs(p.res[0]*p.res[1])
        dens_g = np.zeros(shape, "float64")
        reproject(dens, dens_g, src_transform=p.transform, src_crs=p.crs,
                  dst_transform=wt, dst_crs=crs, resampling=Resampling.nearest)
    people_pp = dens_g * px

    rows, agg = [], []
    for rp in C.RP_YEARS:
        for cond in ("baseline", "scheme"):
            hp = hz_path(rp, cond)
            if not os.path.exists(hp):
                continue
            with rasterio.open(hp) as s:
                h = s.read(1, window=win).astype("float64")
            h = np.where(np.isfinite(h), h, 0)
            h[(h < 1) | (h > 6)] = 0
            hc = h.astype("int32")
            # per-plot max hazard class
            maxh = np.zeros(N+1); flat_pid = pid.ravel(); flat_h = h.ravel()
            m = flat_pid > 0
            np.maximum.at(maxh, flat_pid[m], flat_h[m])
            plot_cls = maxh[1:]
            for cl in CLASSES:
                area = float((hc == cl).sum()) * px / 1e4
                ppl = float(people_pp[hc == cl].sum())
                nplots = int((plot_cls == cl).sum())
                rows.append(dict(rp=rp, condition=cond, hclass=cl, desc=DESC[cl],
                                 area_ha=round(area, 2), plots=nplots, people=round(ppl)))
            unsafe = np.isin(hc, [4, 5, 6]); fail = np.isin(hc, [5, 6])
            agg.append(dict(rp=rp, condition=cond,
                            people_H4plus=round(float(people_pp[unsafe].sum())),
                            people_H5plus=round(float(people_pp[fail].sum())),
                            plots_H4plus=int((plot_cls >= 4).sum()),
                            area_H4plus_ha=round(float(unsafe.sum())*px/1e4, 2)))
            print(f"{rp:>6}yr {cond:8s} H4+ people {agg[-1]['people_H4plus']:>5}  "
                  f"plots {agg[-1]['plots_H4plus']:>4}")

    with open(os.path.join(OUTDIR, "hazard_class_summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rp", "condition", "hclass", "desc", "area_ha", "plots", "people"])
        w.writeheader(); [w.writerow(r) for r in rows]
    with open(os.path.join(OUTDIR, "hazard_by_rp.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rp", "condition", "people_H4plus", "people_H5plus", "plots_H4plus", "area_H4plus_ha"])
        w.writeheader(); [w.writerow(r) for r in agg]
    print("wrote", OUTDIR)


if __name__ == "__main__":
    main()
