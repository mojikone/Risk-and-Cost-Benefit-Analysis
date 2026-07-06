"""
Reconstruct the HEC-RAS 2D mesh cells from a plan HDF and burn a maximum-depth
raster (depth = Max WSE - Cell Minimum Elevation) to GeoTIFF at RES metres.

Cell minimum elevations are stored per geometry and already reflect the correct
burned terrain (baseline vs dam+channel), so no external DEM is required.
"""
import os, numpy as np, h5py
import rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize
from shapely.geometry import Polygon
import config as C

WKT = ('PROJCS["WGS_1984_UTM_Zone_40N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
       'SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],'
       'UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],'
       'PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],'
       'PARAMETER["Central_Meridian",57.0],PARAMETER["Scale_Factor",0.9996],'
       'PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]')

BASE = "Results/Unsteady/Output/Output Blocks/Base Output/Summary Output/2D Flow Areas"
DRY = 0.01  # depths below this (m) are treated as dry


def _cell_polygons(g, area):
    """Return (list_of_shapely_polys_or_None, centers, min_elev) for a geometry HDF."""
    grp = g[f"Geometry/2D Flow Areas/{area}"]
    fp = grp["FacePoints Coordinate"][:]                 # (nfp, 2)
    idx = grp["Cells FacePoint Indexes"][:]              # (ncell, 8) padded
    centers = grp["Cells Center Coordinate"][:]
    elev = grp["Cells Minimum Elevation"][:]
    nfp = fp.shape[0]
    polys = []
    for i in range(idx.shape[0]):
        pts_i = [k for k in idx[i] if 0 <= k < nfp]
        if len(pts_i) < 3:
            polys.append(None); continue
        pts = fp[pts_i]
        # order vertices CCW by angle about the cell centre
        ang = np.arctan2(pts[:, 1] - centers[i, 1], pts[:, 0] - centers[i, 0])
        pts = pts[np.argsort(ang)]
        try:
            p = Polygon(pts)
            polys.append(p if p.is_valid and p.area > 0 else None)
        except Exception:
            polys.append(None)
    return polys, centers, elev


def build(plan_no, geom_hdf, out_tif, area=C.FLOW_AREA):
    ph = os.path.join(C.RAS_DIR, f"Majlas.p{plan_no}.hdf")
    with h5py.File(os.path.join(C.RAS_DIR, geom_hdf), "r") as g:
        polys, centers, elev = _cell_polygons(g, area)
    with h5py.File(ph, "r") as f:
        wse = f[f"{BASE}/{area}/Maximum Water Surface"][0, :]   # row 0 = max value

    depth = wse - elev
    depth[~np.isfinite(depth)] = 0.0
    depth[depth < DRY] = 0.0

    # raster grid over mesh extent, snapped to RES
    xs, ys = centers[:, 0], centers[:, 1]
    pad = 50.0
    minx = np.floor((xs.min() - pad) / C.RES) * C.RES
    maxy = np.ceil((ys.max() + pad) / C.RES) * C.RES
    maxx = np.ceil((xs.max() + pad) / C.RES) * C.RES
    miny = np.floor((ys.min() - pad) / C.RES) * C.RES
    w = int((maxx - minx) / C.RES); h = int((maxy - miny) / C.RES)
    transform = from_origin(minx, maxy, C.RES, C.RES)

    shapes = [(polys[i], float(depth[i])) for i in range(len(polys))
              if polys[i] is not None and depth[i] > 0]
    grid = rasterize(shapes, out_shape=(h, w), transform=transform,
                     fill=0.0, dtype="float32", all_touched=False)

    os.makedirs(os.path.dirname(out_tif), exist_ok=True)
    with rasterio.open(out_tif, "w", driver="GTiff", height=h, width=w, count=1,
                       dtype="float32", crs=WKT, transform=transform,
                       nodata=0.0, compress="lzw") as dst:
        dst.write(grid, 1)

    wet_cells = int((depth > 0).sum())
    wet_area_km2 = float((grid > 0).sum()) * C.RES * C.RES / 1e6
    return dict(plan=plan_no, wet_cells=wet_cells, max_depth=float(depth.max()),
                wet_area_km2=round(wet_area_km2, 3), tif=out_tif)


if __name__ == "__main__":
    # quick self-test on baseline 100yr (p06, geometry g01)
    r = build("06", "Majlas.g01.hdf",
              os.path.join(C.DEPTH_DIR, "_test_100yr.tif"))
    print(r)
