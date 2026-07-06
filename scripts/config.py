"""
Central configuration for the Majlas dam / flood-protection cost-benefit analysis.
All paths, economic parameters, damage curves and scenario->plan mapping live here.
"""
import os

# ---------------------------------------------------------------- paths
RISK_DIR   = r"D:\Mojtaba\Renardet\2224 WS11\Majlas\Hydraulic\Flood Protection\Risk"
RAS_DIR    = r"D:\Mojtaba\Renardet\2224 WS11\Majlas\Hydraulic\Flood Protection\Hydraulic\HEC-RAS Majlas"
DATA_DIR   = os.path.join(RISK_DIR, "Data")
OUT_DIR    = os.path.join(RISK_DIR, "output")
DEPTH_DIR  = os.path.join(OUT_DIR, "depth")

LANDUSE_SHP = os.path.join(DATA_DIR, "SHP", "Landuse Majlas Clip.shp")
OUTLINE_SHP = os.path.join(DATA_DIR, "SHP", "Project Outline.shp")

# 2D flow area name inside every plan HDF
FLOW_AREA = "DS Protection"

# ---------------------------------------------------------------- RAS depth exports
# Authoritative Depth (Max) rasters exported from HEC-RAS RAS Mapper (2 m).
# Baseline: "Depth <RP>.Terrain (2).DTM_5m.tif"
# Scheme  : "Depth <RP>D.Terrain (2).DTM_5m.tif"   (D = Dam+channel)
DEPTH_RAS_DIR = os.path.join(DATA_DIR, "Depth")


def ras_depth_path(rp, condition):
    d = "D" if condition == "scheme" else ""
    return os.path.join(DEPTH_RAS_DIR, f"Depth {rp}{d}.Terrain (2).DTM_5m.tif")

# raster resolution for the reconstructed depth grid (metres)
RES = 5.0

# ---------------------------------------------------------------- scenarios
# Return period (years) -> HEC-RAS plan number, for baseline and dam+channel scheme.
# Verified from "Plan Title=" in each Majlas.pXX file.
RP_YEARS = [2, 5, 10, 25, 50, 100, 200, 500, 1000, 10000]

BASELINE_PLAN = {2:"01", 5:"02", 10:"03", 25:"04", 50:"05",
                 100:"06", 200:"07", 500:"08", 1000:"09", 10000:"10"}
SCHEME_PLAN   = {2:"11", 5:"12", 10:"13", 25:"14", 50:"15",
                 100:"21", 200:"22", 500:"23", 1000:"24", 10000:"25"}

# ---------------------------------------------------------------- landuse mapping
# shapefile field that holds the class, and how each class maps to a damage curve
LU_FIELD = "NewLUClass"
LU_TO_CURVE = {
    "Residential": "Residential",
    "Commercial":  "Commercial",
    "Industry":    "Industrial",
    "Agriculture": "Agriculture",
    # blank / roads rows -> infrastructure curve
    "":            "Roads",
}

# ---------------------------------------------------------------- damage curves
# Landuse-based absolute damage, OMR/m2, 2023 price level.
# Source: Data/XLS/OMAN flood depth damage functions.xlsx (matches Methodology.docx table).
DAMAGE_DEPTHS = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0]
DAMAGE_CURVES = {  # OMR per m2 at each depth in DAMAGE_DEPTHS
    "Residential": [0.0, 20.59496733, 31.15831475, 38.88540783, 45.45319157,
                    54.83861146, 58.74617699, 62.03304841, 63.06708703],
    "Commercial":  [0.0, 50.35933076, 71.86314275, 88.12279348, 101.9570949,
                    118.0628244, 125.8824003, 131.0821291, 133.6537093],
    "Industrial":  [0.0, 31.37206356, 53.35544733, 69.70756729, 79.45898803,
                    94.90613341, 100.6560567, 105.8352730, 110.7842882],
    "Roads":       [0.0, 4.595712174, 7.988699371, 12.94325164, 15.20908401,
                    17.32544814, 19.01318156, 20.76180003, 21.43153551],
    "Agriculture": [0.0, 0.002373324, 0.006504665, 0.009212012, 0.009809738,
                    0.011602915, 0.014661866, 0.017369213, 0.017580175],
}

# ---------------------------------------------------------------- economics
DISCOUNT_RATE = 0.025      # r
HORIZON_YEARS = 50         # n

COST_DAM_OMR     = 75_000_000
COST_CHANNEL_OMR = 5_000_000

MAINT_DAM_RATE     = 0.01   ; MAINT_DAM_START     = 5   # 1% of dam capital, from year 5
MAINT_CHANNEL_RATE = 0.007  ; MAINT_CHANNEL_START = 2   # 0.7% of channel capital, from year 2

# relocation unit prices, OMR/m2, applied to plot area inside project outline
RELOC_UNIT = {
    "Residential": 15.0,
    "Commercial":  20.0,
    "Industry":    20.0,
    "Agriculture": 2.0,
    "":            0.0,   # roads: not compensated
}

# AED tail assumptions (see methodology): damage below the most frequent event
# (prob 0.5 -> 1.0) is taken as zero; damage above the rarest event is held flat.
