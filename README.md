# Majlas Dam & Flood Protection — Cost-Benefit Analysis

## Purpose
Quantify the flood risk and the economic + human case for the **Wadi Majlas** (Quriyat,
Oman) dam-and-channel flood-protection scheme. The analysis compares two conditions —
**Baseline** (no scheme) and **Scheme** (dam + dykes/channels) — across 10 return
periods (2 … 10 000 yr) and produces:

- **Annual Expected Damage (AED)** for each condition and the **avoided damage**,
- financial metrics **NPV** and **BCR** over the project horizon,
- **flood hazard classification (H1–H6, Australian AIDR)** — people, plots and area in
  each hazard class, and in particular the **H4+ "unsafe for people"** population,
- non-monetized **population exposure** (people flooded, and people in life-threatening
  >1 m water) and the **Expected Annual People Exposed (EAPE)** avoided,
- a full set of cartographic maps, charts, tables, a **print-ready map atlas (PDF)**, a
  **live Excel model** the client can re-run with different assumptions, and a compiled
  client report.

The honest finding: the scheme **fails a pure damage-based test (BCR ≈ 0.08)** but is a
strong **life-safety** intervention — at the 200 yr design event it removes **90% of the
people standing in hazard unsafe for life (H4+, 5,222 → 510)**. The decision is taken on
the combined economic + flood-hazard basis, not on the BCR alone. Both stories are
reported side by side.

## Inputs needed
| Input | Description | Location / source |
|---|---|---|
| **Flood depth layers** | HEC-RAS RAS Mapper **Depth (Max)** GeoTIFFs, 2 m, per RP, baseline (`Depth <RP>…`) and scheme (`Depth <RP>D…`) | `Data/Depth/` (not version-controlled — large) |
| **Flood hazard layers** | HEC-RAS **Australian hazard (H1–H6)** GeoTIFFs, 2 m, per RP, `Hazard <RP>yr[D].tif` | `Data/Hazard/` (not version-controlled — large) |
| **Depth-damage functions** | Damage vs depth (OMR/m²) by land-use class (Residential, Commercial, Industrial, Roads/Infrastructure, Agriculture); Oman-calibrated (JRC global functions) | `Data/XLS/`, encoded in `scripts/config.py` |
| **Land-use shapefile** | Cadastral plots classified by land use (`NewLUClass`) | `Data/SHP/Landuse Majlas Clip.shp` |
| **Initial costs** | Dam capital, channel capital, and **relocation** (derived from plots inside the project outline × unit land prices) | `scripts/config.py` / Excel **Inputs** sheet |
| **Maintenance** | Annual maintenance **rate** and **start year** for dam and channel | `scripts/config.py` / Excel **Inputs** sheet |
| **Discount rate** | Real discount rate `r` (default 4.2%) | `scripts/config.py` / Excel **Inputs** sheet |
| **Project horizon** | Appraisal period `n` (default 50 yr) | `scripts/config.py` / Excel **Inputs** sheet |
| **Scheme shapefiles (for maps)** | Project works used to annotate scheme maps: **Dam axis**, **Dykes**, **channels**, and the **project outline** (relocation footprint) | `Data/SHP/` + the QGIS project |
| **Population raster** | GHS-POP 2025 (persons/cell) for exposure & EAPE | `Data/Population/` (not version-controlled) |
| **Basemap / terrain** | Google Satellite Hybrid (cartography) and DTM (context); CRS **EPSG:32640** throughout | QGIS project |

## Outputs (`output/`)
| Output | Description |
|---|---|
| `maps/depth_<RP>yr_<cond>.png` (20) | Flood-hazard depth maps, satellite basemap, per-map stats table + population footer |
| `maps/damage_<RP>yr_<cond>.png` (20) | Direct-damage-intensity maps (OMR/m²) with damage/plots/area + population table |
| `maps/hazard_<RP>yr_<cond>.png` (20) | Australian flood hazard (H1–H6) maps with per-class plots/area/people table |
| `maps/landuse.png`, `maps/relocation.png` | Land-use classification; relocation footprint (keeps project outline) |
| `AED_curves.png`, `chart_depth_damage_curves.png`, `chart_exposure.png`, `chart_damage_by_class.png`, `chart_hazard_people.png`, `chart_hazard_plots_area.png`, `chart_hazard_h4plus.png`, `chart_cost_benefit.png`, `chart_mca.png` | Analysis charts |
| `damage_by_plan.csv`, `aed_summary.csv` | Damage per RP/condition; AED, avoided, NPV, BCR |
| `exposure_by_rp.csv`, `exposure_summary.csv`, `landuse_inventory.csv` | Population exposure, EAPE, land-use inventory |
| `plot_stats/enriched_landuse.shp` | **Per-plot** mean depth, damage, inundated area (>0.3 m) and population, every RP/condition |
| `plot_stats/class_summary.csv`, `plot_stats/relocation.csv` | Per-class inundation/damage/population; relocation by class |
| `hazard/hazard_class_summary.csv`, `hazard/hazard_by_rp.csv` | Hazard H1–H6 exposure (area, plots, people); unsafe-for-people (H4+) by RP |
| **`Techno-Economical Assessment Report.docx`** | Client report on the client template (cover, header, styles) — TOC / list of figures / list of tables, roman front matter then arabic body, native Word (OMML) equations, hazard analysis, decision assessment |
| **`Majlas_CBA.xlsx`** | **Live cost-benefit workbook** — edit the yellow Inputs (costs, discount rate, horizon, maintenance) and AED/NPV/BCR/EAPE recompute via formulas |
| **`Majlas_Map_Atlas.pdf`** | **Print-ready A4-landscape atlas** — cover, Table of Maps, all 62 maps one per page, running footers, PDF bookmarks (not version-controlled — 89 MB, regenerable) |
| `damage/damage_<RP>_<cond>.tif` | Per-pixel damage rasters (intermediate; not version-controlled) |

Maps are authored as **QGIS print layouts** in `Data/QGIS RISK.qgz` and exported to
`output/maps/` (62 maps total: depth, damage, hazard, land use, relocation).

## Headline result
| Metric | Value |
|---|---|
| AED baseline / scheme | 0.77 / 0.40 M OMR/yr |
| **Annual avoided damage** | **0.37 M OMR/yr** |
| Initial cost (dam 75 + dykes 5 + relocation 0.17) | 80.2 M OMR |
| **NPV** (50 yr @ 4.2%) | **−86.0 M OMR** |
| **BCR** | **0.083** |
| EAPE avoided | ~809 people/yr (all water); ~345/yr (>1 m) |
| **Life-safety (people in hazard H4+ @200 yr)** | **5,222 → 510 (−90%)** |
| Life-safety (people in hazard H4+ @500 yr) | 5,947 → 967 (−84%) |
| Multi-criteria decision score | 3 / 5 — moderately favourable |

## Pipeline (`scripts/`)
| Script | Purpose |
|---|---|
| `config.py` | Paths, damage curves, economic parameters, RP→file mapping |
| `damage.py` | Zonal flood-damage integration (depth-damage curves × land use) |
| `economics.py` | AED integration, relocation, NPV, BCR |
| `exposure.py` / `run_metrics.py` | Population exposure (GHS-POP), EAPE |
| `build_damage_raster.py` | Per-pixel damage rasters (OMR/m²) |
| `build_plot_stats.py` | Per-plot depth/damage/exposure → enriched shapefile + class summary |
| `build_hazard_stats.py` | Australian hazard (H1–H6) exposure: area, plots, people per class |
| `plot_extra_charts.py` | Hazard composition, H4+ reduction, cost-benefit and MCA charts |
| `merge_report.py` | Splices the report body into the client template (cover, header, styles) |
| `run_all.py` | End-to-end damage → AED → NPV/BCR |
| `plot_aed.py` / `plot_charts.py` | Charts |
| `build_workbook.py` | Builds the live Excel model |
| `build_map_atlas.py` | Combines all 62 maps into the print-ready atlas PDF |
| `sensitivity.py` | Break-even (dam cost / benefit multiplier) |

Depth layers, damage/population rasters, the atlas PDF and archives are excluded via
`.gitignore` (all regenerable). CRS: WGS84 UTM 40N (EPSG:32640).

## QGIS Processing tool (`qgis_tool/`)
`majlas_cba_tool.py` registers **"Flood CBA (config-driven)"** in the QGIS Processing
Toolbox so the analysis can be re-run on any scheme without touching `config.py`. Nothing
is hard-coded: the number of depth layers, the depth-damage curve table, the land-use
classes, the number of scenarios, maintenance rates/start years and per-class relocation
unit prices are all supplied as layers and CSVs.

| Tool input | File |
|---|---|
| Land-use layer + class field | any polygon layer |
| Depth-damage curves | `examples/depth_damage_curves.csv` |
| Depth layer manifest (scenario, return_period, raster) | `examples/depth_manifest.csv` |
| Scenario costs (capital, maintenance rate, start year) | `examples/scenario_costs.csv` |
| Relocation unit prices per class | `examples/relocation_unit_prices.csv` |
| Project outline, discount rate, horizon, output folder | tool parameters |

It reproduces the Python pipeline exactly (verified: AED baseline 771,767; avoided
373,939; relocation 168,080).

**Status / next step.** The tool currently covers damage → AED → relocation → NPV/BCR.
Work in progress is to bring it to full parity with `scripts/`: population exposure and
EAPE, hazard H1–H6 statistics, the per-plot enriched shapefile, chart and print-layout map
generation, and the map atlas — so every step of this analysis runs from inside QGIS.
