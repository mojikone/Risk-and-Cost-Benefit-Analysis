"""
Non-monetized exposure metrics per return period / condition:
  - population inundated (total + by depth band, life-safety proxy)
  - plots inundated (count) and flooded area, by landuse class
Population is distributed uniformly within each GHS cell (nearest resampling of
persons/m2 density onto the depth grid), which conserves mass.
"""
import os, numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
import config as C
from damage import _CLASSES, _CID

POP_TIF = os.path.join(C.DATA_DIR, "Population", "GHS POP 2025 Majlas.tif")
DEPTH_BANDS = [0.3, 0.5, 1.0, 2.0]   # people in water deeper than these (m)


def _density_on_grid(depth_src):
    """Resample GHS population density (persons/m2) onto the depth raster grid."""
    with rasterio.open(POP_TIF) as p:
        pop = p.read(1).astype("float64")
        nod = p.nodata
        if nod is not None:
            pop = np.where(pop == nod, 0.0, pop)
        pop[pop < 0] = 0.0
        dens = pop / abs(p.res[0] * p.res[1])      # persons per m2
        out = np.zeros((depth_src.height, depth_src.width), "float64")
        reproject(dens, out,
                  src_transform=p.transform, src_crs=p.crs,
                  dst_transform=depth_src.transform, dst_crs=depth_src.crs,
                  resampling=Resampling.nearest)
    return out


def load_landuse():
    gdf = gpd.read_file(C.LANDUSE_SHP)
    cls = gdf[C.LU_FIELD].fillna("").astype(str).str.strip()
    gdf["_curve"] = cls.map(C.LU_TO_CURVE)
    gdf = gdf[gdf["_curve"].notna()].reset_index(drop=True)
    return gdf


def landuse_inventory(gdf):
    inv = {}
    for name in _CLASSES:
        sub = gdf[gdf["_curve"] == name]
        inv[name] = dict(n_plots=int(len(sub)),
                         area_km2=round(float(sub.geometry.area.sum()) / 1e6, 3))
    return inv


def exposure_for_raster(depth_tif, gdf):
    with rasterio.open(depth_tif) as src:
        depth = src.read(1).astype("float64")
        nod = src.nodata
        px = abs(src.res[0] * src.res[1])
        if nod is not None:
            depth = np.where(depth == nod, np.nan, depth)
        wet = np.isfinite(depth) & (depth > 0)
        dens = _density_on_grid(src)
        # class raster + plot-id raster on same grid
        shp_cls = [(g, _CID[c]) for g, c in zip(gdf.geometry, gdf["_curve"])]
        cls_r = rasterize(shp_cls, out_shape=depth.shape, transform=src.transform,
                          fill=0, dtype="int32", all_touched=False)
        shp_id = [(g, i + 1) for i, g in enumerate(gdf.geometry)]
        pid_r = rasterize(shp_id, out_shape=depth.shape, transform=src.transform,
                          fill=0, dtype="int32", all_touched=False)

    people = dens * px
    out = {"wet_area_km2": round(float(wet.sum()) * px / 1e6, 3),
           "people_exposed": round(float(people[wet].sum()))}
    for b in DEPTH_BANDS:
        m = wet & (depth > b)
        out[f"people_gt{b}m"] = round(float(people[m].sum()))

    # plots inundated + flooded area by class
    inund_ids = np.unique(pid_r[wet & (pid_r > 0)])
    out["plots_inundated"] = int(inund_ids.size)
    cls_of_pid = {}
    for name in _CLASSES:
        fa = (wet & (cls_r == _CID[name])).sum() * px / 1e6
        out[f"flooded_km2_{name}"] = round(float(fa), 3)
    # count inundated plots per class
    id2cls = {i + 1: c for i, c in enumerate(gdf["_curve"])}
    from collections import Counter
    cc = Counter(id2cls[i] for i in inund_ids.tolist())
    for name in _CLASSES:
        out[f"plots_inund_{name}"] = int(cc.get(name, 0))
    return out
