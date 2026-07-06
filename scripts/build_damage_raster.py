"""
Per-pixel flood-damage rasters (OMR/m2) = depth-damage curve applied by land-use
class, for every return period and condition. Output: output/damage/damage_<RP>_<cond>.tif
"""
import os, numpy as np, rasterio
import config as C
import damage as DM

DMDIR = os.path.join(C.OUT_DIR, "damage")


def main():
    os.makedirs(DMDIR, exist_ok=True)
    gdf = DM.load_landuse()
    for rp in C.RP_YEARS:
        for cond in ("baseline", "scheme"):
            tif = C.ras_depth_path(rp, cond)
            with rasterio.open(tif) as src:
                depth = src.read(1).astype("float64"); nod = src.nodata
                transform, prof = src.transform, src.profile
            depth = np.where(np.isfinite(depth), depth, 0.0)
            if nod is not None:
                depth = np.where(depth == nod, 0.0, depth)
            depth[depth < 0] = 0.0
            cls_r = DM._landuse_class_raster(gdf, transform, depth.shape)
            dmg = np.zeros(depth.shape, "float64")
            for name in DM._CLASSES:
                m = (cls_r == DM._CID[name]) & (depth > 0)
                if m.any():
                    dmg[m] = np.interp(depth[m], C.DAMAGE_DEPTHS, C.DAMAGE_CURVES[name])
            out = np.where(dmg > 0, dmg, -9999).astype("float32")
            prof.update(dtype="float32", nodata=-9999, compress="lzw")
            with rasterio.open(os.path.join(DMDIR, f"damage_{rp}_{cond}.tif"), "w", **prof) as d:
                d.write(out, 1)
        print(f"{rp:>6}yr done")
    print("damage rasters written to", DMDIR)


if __name__ == "__main__":
    main()
