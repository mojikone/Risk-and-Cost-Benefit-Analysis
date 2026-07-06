# Majlas Dam & Flood Protection — Cost-Benefit Analysis

## Purpose
Quantify the flood risk and the economic + human case for the **Wadi Majlas** (Quriyat,
Oman) dam-and-channel flood-protection scheme. The analysis compares two conditions —
**Baseline** (no scheme) and **Scheme** (dam + dykes/channels) — across 10 return
periods (2 … 10 000 yr) and produces:

- **Annual Expected Damage (AED)** for each condition and the **avoided damage**,
- financial metrics **NPV** and **BCR** over the project horizon,
- non-monetized **population exposure** (people flooded, and people in life-threatening
  >1 m water) and the **Expected Annual People Exposed (EAPE)** avoided,
- a full set of cartographic maps, charts, tables, and a **live Excel model** the client
  can re-run with different assumptions.

The honest finding: the scheme **fails a pure damage-based test (BCR ≈ 0.15)** but is a
strong **life-safety** intervention (removes ~90% of the population from >1 m flooding at
the 100 yr event). Both stories are reported side by side.

## Inputs needed
| Input | Description | Location / source |
|---|---|---|
| **Flood depth layers** | HEC-RAS RAS Mapper **Depth (Max)** GeoTIFFs, 2 m, one per return period, for **baseline** (`Depth <RP>…`) and **scheme** (`Depth <RP>D…`) | `Data/Depth/` (from the HEC-RAS model; not version-controlled — large) |
| **Depth-damage functions** | Damage vs depth (OMR/m²) by land-use class (Residential, Commercial, Industrial, Roads/Infrastructure, Agriculture); Oman-calibrated (JRC global functions) | `Data/XLS/`, encoded in `scripts/config.py` |
| **Land-use shapefile** | Cadastral plots classified by land use (`NewLUClass`) | `Data/SHP/Landuse Majlas Clip.shp` |
| **Initial costs** | Dam capital, channel capital, and **relocation** (derived from plots inside the project outline × unit land prices) | `scripts/config.py` / Excel **Inputs** sheet |
| **Maintenance** | Annual maintenance **rate** and **start year** for dam and channel | `scripts/config.py` / Excel **Inputs** sheet |
| **Discount rate** | Real discount rate `r` (default 2.5%) | `scripts/config.py` / Excel **Inputs** sheet |
| **Project horizon** | Appraisal period `n` (default 50 yr) | `scripts/config.py` / Excel **Inputs** sheet |
| **Scheme shapefiles (for maps)** | Project works used to annotate scheme maps: **Dam axis**, **Dykes**, **channels**, and the **project outline** (relocation footprint) | `Data/SHP/` + the QGIS project |
| **Population raster** | GHS-POP 2025 (persons/cell) for exposure & EAPE | `Data/Population/` (not version-controlled) |
| **Basemap / terrain** | Google Satellite Hybrid (cartography) and DTM (context); CRS **EPSG:32640** throughout | QGIS project |

## Outputs (`output/`)
| Output | Description |
|---|---|
| `maps/depth_<RP>yr_<cond>.png` (20) | Flood-hazard depth maps, satellite basemap, per-map stats table + population footer |
| `maps/damage_<RP>yr_<cond>.png` (20) | Direct-damage-intensity maps (OMR/m²) with damage/plots/area + population table |
| `maps/landuse.png`, `maps/relocation.png` | Land-use classification; relocation footprint (keeps project outline) |
| `AED_curves.png`, `chart_depth_damage_curves.png`, `chart_exposure.png`, `chart_damage_by_class.png` | Analysis charts |
| `damage_by_plan.csv`, `aed_summary.csv` | Damage per RP/condition; AED, avoided, NPV, BCR |
| `exposure_by_rp.csv`, `exposure_summary.csv`, `landuse_inventory.csv` | Population exposure, EAPE, land-use inventory |
| `plot_stats/enriched_landuse.shp` | **Per-plot** mean depth, damage, inundated area (>0.3 m) and population, every RP/condition |
| `plot_stats/class_summary.csv`, `plot_stats/relocation.csv` | Per-class inundation/damage/population; relocation by class |
| **`Majlas_CBA.xlsx`** | **Live cost-benefit workbook** — edit the yellow Inputs (costs, discount rate, horizon, maintenance) and AED/NPV/BCR/EAPE recompute via formulas |
| `damage/damage_<RP>_<cond>.tif` | Per-pixel damage rasters (intermediate; not version-controlled) |

Maps are authored as **QGIS print layouts** in `Data/QGIS RISK.qgz` and exported to
`output/maps/` (42 maps total).

## Headline result
| Metric | Value |
|---|---|
| AED baseline / scheme | 0.77 / 0.40 M OMR/yr |
| **Annual avoided damage** | **0.37 M OMR/yr** |
| Initial cost (dam 50 + channel 5 + relocation 0.17) | 55.2 M OMR |
| **NPV** (50 yr @ 2.5%) | **−57.8 M OMR** |
| **BCR** | **0.155** |
| EAPE avoided | ~686 people/yr |
| Life-safety (people in >1 m @100 yr) | 3,564 → 374 (−89%) |

## Pipeline (`scripts/`)
| Script | Purpose |
|---|---|
| `config.py` | Paths, damage curves, economic parameters, RP→file mapping |
| `damage.py` | Zonal flood-damage integration (depth-damage curves × land use) |
| `economics.py` | AED integration, relocation, NPV, BCR |
| `exposure.py` / `run_metrics.py` | Population exposure (GHS-POP), EAPE |
| `build_damage_raster.py` | Per-pixel damage rasters (OMR/m²) |
| `build_plot_stats.py` | Per-plot depth/damage/exposure → enriched shapefile + class summary |
| `run_all.py` | End-to-end damage → AED → NPV/BCR |
| `plot_aed.py` / `plot_charts.py` | Charts |
| `build_workbook.py` | Builds the live Excel model |
| `sensitivity.py` | Break-even (dam cost / benefit multiplier) |

Depth layers, damage/population rasters and archives are excluded via `.gitignore`
(regenerable from the HEC-RAS model). CRS: WGS84 UTM 40N (EPSG:32640).
