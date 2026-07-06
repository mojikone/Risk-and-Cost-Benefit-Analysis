"""
Per-plot zonal statistics for every RP and condition:
  - mean flood depth over wet area of the plot
  - direct damage cost (OMR)
  - inundated area with depth > 0.3 m
Outputs:
  output/plot_stats/enriched_landuse.shp   per-plot depth & damage, each RP/cond
  output/plot_stats/class_summary.csv      per class: damage, #plots(>0.3m), area(>0.3m)
Plots are counted as inundated only where depth > 0.3 m.
"""
import os, csv, numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
import config as C
import damage as DM

OUTDIR = os.path.join(C.OUT_DIR, "plot_stats")
THR = 0.3     # inundation threshold (m) for plot counts / area


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    gdf = DM.load_landuse().reset_index(drop=True)
    N = len(gdf)
    plot_area = gdf.geometry.area.values

    # rasterize plot ids once (grid from any depth raster)
    with rasterio.open(C.ras_depth_path(2, "baseline")) as src:
        transform, shape = src.transform, (src.height, src.width)
        px = abs(src.res[0] * src.res[1]); grid_crs = src.crs
    pid = rasterize([(g, i + 1) for i, g in enumerate(gdf.geometry)],
                    out_shape=shape, transform=transform, fill=0, dtype="int32").ravel()

    # population density (persons/m2) resampled to the depth grid (nearest = mass-conserving)
    with rasterio.open(os.path.join(C.DATA_DIR, "Population", "GHS POP 2025 Majlas.tif")) as p:
        pop = p.read(1).astype("float64"); pnod = p.nodata
        if pnod is not None:
            pop = np.where(pop == pnod, 0.0, pop)
        pop[pop < 0] = 0.0
        dens = pop / abs(p.res[0] * p.res[1])
        dens_grid = np.zeros(shape, "float64")
        reproject(dens, dens_grid, src_transform=p.transform, src_crs=p.crs,
                  dst_transform=transform, dst_crs=grid_crs, resampling=Resampling.nearest)
    people_pp = (dens_grid * px).ravel()   # people per depth pixel

    summary = []   # rows: rp, condition, class, damage_OMR, plots_gt03, area_gt03_m2
    for rp in C.RP_YEARS:
        for cond in ("baseline", "scheme"):
            with rasterio.open(C.ras_depth_path(rp, cond)) as s:
                d = s.read(1).astype("float64"); nod = s.nodata
            d = np.where(np.isfinite(d), d, 0.0)
            if nod is not None:
                d = np.where(d == nod, 0.0, d)
            d[d < 0] = 0.0
            dmgtif = os.path.join(C.OUT_DIR, "damage", f"damage_{rp}_{cond}.tif")
            with rasterio.open(dmgtif) as s:
                dm = s.read(1).astype("float64"); dnod = s.nodata
            dm = np.where((dm == dnod) | ~np.isfinite(dm), 0.0, dm)
            df = d.ravel(); dmf = dm.ravel()
            wet = df > 0
            sd = np.bincount(pid[wet], weights=df[wet], minlength=N + 1)
            cw = np.bincount(pid[wet], minlength=N + 1)
            mean_d = np.divide(sd, cw, out=np.zeros_like(sd), where=cw > 0)[1:]
            has = dmf > 0
            dmg = np.bincount(pid[has], weights=dmf[has], minlength=N + 1)[1:] * px
            gt = df > THR
            a03 = np.bincount(pid[gt], minlength=N + 1)[1:] * px
            pop03 = np.bincount(pid[gt], weights=people_pp[gt], minlength=N + 1)[1:]

            tag = "B" if cond == "baseline" else "S"
            gdf[f"d{tag}_{rp}"] = np.round(mean_d, 3)
            gdf[f"c{tag}_{rp}"] = np.round(dmg, 1)
            gdf[f"a{tag}_{rp}"] = np.round(a03, 1)
            gdf[f"p{tag}_{rp}"] = np.round(pop03, 1)

            for name in DM._CLASSES:
                m = (gdf["_curve"] == name).values
                summary.append(dict(rp=rp, condition=cond, landuse=name,
                                    damage_OMR=round(float(dmg[m].sum())),
                                    plots_gt03=int((a03[m] > 0).sum()),
                                    area_gt03_ha=round(float(a03[m].sum()) / 1e4, 2),
                                    people_gt03=round(float(pop03[m].sum()))))
            print(f"{rp:>6}yr {cond:8s} damage {dmg.sum():,.0f} OMR  plots>0.3m {(a03>0).sum()}")

    out_shp = os.path.join(OUTDIR, "enriched_landuse.shp")
    gdf.drop(columns=["_curve"]).to_file(out_shp)
    with open(os.path.join(OUTDIR, "class_summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rp", "condition", "landuse", "damage_OMR", "plots_gt03", "area_gt03_ha", "people_gt03"])
        w.writeheader(); [w.writerow(r) for r in summary]
    print("wrote", out_shp, "and class_summary.csv")


if __name__ == "__main__":
    main()
