"""
Zonal flood-damage integration.

For a depth raster, damage is integrated over space as
    total_damage = sum_pixels  curve[class(pixel)](depth(pixel)) * pixel_area
where class(pixel) comes from rasterizing the landuse plots onto the same grid
and curve[](.) is the landuse-based depth-damage function (OMR/m2).
"""
import os, numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
import config as C

_CLASSES = list(C.DAMAGE_CURVES.keys())          # curve names
_CID = {name: i + 1 for i, name in enumerate(_CLASSES)}   # 1-based ids, 0 = none


def _landuse_class_raster(gdf_curvecol, transform, shape):
    """Rasterize plots to curve-class ids on the given grid."""
    shapes = [(geom, _CID[c]) for geom, c in
              zip(gdf_curvecol.geometry, gdf_curvecol["_curve"]) if c in _CID]
    return rasterize(shapes, out_shape=shape, transform=transform,
                     fill=0, dtype="int32", all_touched=False)


def load_landuse():
    gdf = gpd.read_file(C.LANDUSE_SHP)
    cls = gdf[C.LU_FIELD].fillna("").astype(str).str.strip()
    gdf["_curve"] = cls.map(C.LU_TO_CURVE)
    gdf = gdf[gdf["_curve"].notna()].copy()
    return gdf


def raster_stats(depth_tif):
    """Return (max_depth_m, wet_area_km2) for a depth raster, honoring nodata."""
    with rasterio.open(depth_tif) as src:
        a = src.read(1).astype("float64")
        nod = src.nodata
        px = abs(src.res[0] * src.res[1])
    if nod is not None:
        a = np.where(a == nod, np.nan, a)
    wet = np.isfinite(a) & (a > 0)
    mx = float(np.nanmax(np.where(wet, a, np.nan))) if wet.any() else 0.0
    return round(mx, 2), round(float(wet.sum()) * px / 1e6, 3)


def damage_for_raster(depth_tif, gdf):
    """Return dict class -> damage OMR, plus 'total', for one depth raster."""
    with rasterio.open(depth_tif) as src:
        depth = src.read(1)
        transform = src.transform
        px_area = abs(src.res[0] * src.res[1])
        nod = src.nodata
    depth = np.where(np.isfinite(depth), depth, 0.0)
    if nod is not None:
        depth = np.where(depth == nod, 0.0, depth)

    cls_r = _landuse_class_raster(gdf, transform, depth.shape)
    out = {}
    dmg_total = 0.0
    for name in _CLASSES:
        m = (cls_r == _CID[name]) & (depth > 0)
        if not m.any():
            out[name] = 0.0; continue
        dmg_pp = np.interp(depth[m], C.DAMAGE_DEPTHS, C.DAMAGE_CURVES[name]) * px_area
        s = float(dmg_pp.sum())
        out[name] = s
        dmg_total += s
    out["total"] = dmg_total
    return out
