"""
Compute avoided-depth rasters = baseline depth - scheme depth, per return period.
Positive = depth reduced by the scheme (benefit); negative = increased (adverse).
Both-dry pixels are set to nodata. Output: output/avoided/avoided_<RP>.tif (2 m).
"""
import os, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
import config as C

AVDIR = os.path.join(C.OUT_DIR, "avoided")
NEG = 0.05  # |diff| below this treated as no-change -> nodata


def _read(path, ref=None):
    with rasterio.open(path) as s:
        a = s.read(1).astype("float64"); nod = s.nodata
        prof = s.profile
    if nod is not None:
        a = np.where(a == nod, 0.0, a)
    a[a < 0] = 0.0
    return a, prof


def main():
    os.makedirs(AVDIR, exist_ok=True)
    for rp in C.RP_YEARS:
        bpath = C.ras_depth_path(rp, "baseline")
        spath = C.ras_depth_path(rp, "scheme")
        base, prof = _read(bpath)
        with rasterio.open(bpath) as b, rasterio.open(spath) as s:
            sch = s.read(1).astype("float64")
            if (s.width, s.height, s.transform) != (b.width, b.height, b.transform):
                out = np.zeros((b.height, b.width), "float64")
                reproject(np.where(sch == s.nodata, 0.0, sch), out,
                          src_transform=s.transform, src_crs=s.crs,
                          dst_transform=b.transform, dst_crs=b.crs,
                          resampling=Resampling.bilinear)
                sch = out
            else:
                sch = np.where(sch == s.nodata, 0.0, sch)
        sch[sch < 0] = 0.0
        diff = base - sch                       # + = reduction (benefit)
        both_dry = (base <= 0) & (sch <= 0)
        diff[both_dry | (np.abs(diff) < NEG)] = np.nan

        prof.update(dtype="float32", nodata=-9999, compress="lzw")
        arr = np.where(np.isfinite(diff), diff, -9999).astype("float32")
        out = os.path.join(AVDIR, f"avoided_{rp}.tif")
        with rasterio.open(out, "w", **prof) as dst:
            dst.write(arr, 1)
        red = np.nansum(np.where(diff > 0, 1, 0)) * abs(prof["transform"][0])**2 / 1e6
        adv = np.nansum(np.where(diff < 0, 1, 0)) * abs(prof["transform"][0])**2 / 1e6
        print(f"{rp:>6}yr  reduced {red:5.2f} km2  worse {adv:4.2f} km2  "
              f"maxred {np.nanmax(diff):.1f}m  maxworse {(-np.nanmin(diff)):.1f}m")


if __name__ == "__main__":
    main()
