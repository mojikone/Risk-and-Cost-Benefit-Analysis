# Majlas Dam & Flood Protection — Cost-Benefit Analysis

Flood risk and cost-benefit analysis for the Wadi Majlas (Quriyat, Oman) dam + channel
flood-protection scheme. Compares **Baseline** (no scheme) against the **Scheme**
(dam + channels) across 10 return periods (2 … 10 000 yr), and evaluates the investment.

## Headline result
| Metric | Value |
|---|---|
| AED baseline | 0.77 M OMR/yr |
| AED scheme | 0.40 M OMR/yr |
| **Annual avoided damage** | **0.37 M OMR/yr** |
| Initial cost (dam 50 + channel 5 + relocation 0.17) | 55.2 M OMR |
| **NPV** (50 yr @ 2.5%) | **−57.8 M OMR** |
| **BCR** | **0.155** |
| Expected Annual People Exposed avoided | ~686 /yr |
| Life-safety (people in >1 m water @100 yr) | 3,564 → 374 (−89%) |

The scheme fails a pure damage-based cost-benefit test (BCR ≈ 0.15) but is a strong
**life-safety** intervention — it removes ~90% of the population from dangerous (>1 m)
flooding at design events. See the honest multi-metric synthesis in the report/summary.

## Pipeline (`scripts/`)
| Script | Purpose |
|---|---|
| `config.py` | All paths, damage curves, economic parameters, RP→file mapping |
| `damage.py` | Zonal flood-damage integration (depth-damage curves × land use) |
| `economics.py` | AED integration, relocation, NPV, BCR |
| `exposure.py` / `run_metrics.py` | Population exposure (GHS-POP 2025), EAPE |
| `build_damage_raster.py` | Per-pixel damage rasters (OMR/m²) |
| `build_plot_stats.py` | Per-plot depth/damage/exposure → enriched shapefile + class summary |
| `run_all.py` | End-to-end damage → AED → NPV/BCR |
| `plot_aed.py` / `plot_charts.py` | Charts (AED curves, depth-damage, exposure, damage-by-class) |
| `build_workbook.py` | **Live Excel** (`output/Majlas_CBA.xlsx`) — formula-driven NPV/BCR |
| `sensitivity.py` | Break-even (dam cost / benefit multiplier) |

Depth is taken from authoritative **HEC-RAS RAS Mapper "Depth (Max)" 2 m exports**
(not stored here — see `.gitignore`). Maps are produced as QGIS print layouts in
`Data/QGIS RISK.qgz` and exported to `output/maps/` (42 maps: 20 depth, 20 damage,
land use, relocation).

## Live workbook
`output/Majlas_CBA.xlsx` — edit the yellow **Inputs** cells (dam/channel cost,
relocation, discount rate, horizon, maintenance rates) and AED, NPV and BCR recompute
automatically. Verified against the Python pipeline (BCR 0.155).

## Key deliverables
- `output/maps/` — cartographic maps (satellite basemap, per-map stats tables)
- `output/*.png` — analysis charts
- `output/*.csv` — damage, exposure, inventory tables
- `output/plot_stats/enriched_landuse.shp` — per-plot depth & damage, each RP
- `output/Majlas_CBA.xlsx` — live cost-benefit model
