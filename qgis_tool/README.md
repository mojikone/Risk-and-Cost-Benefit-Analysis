# Flood CBA — QGIS Processing tool

`majlas_cba_tool.py` is a generic, config-driven flood cost-benefit engine for QGIS.
Everything is dynamic — scenarios, return periods, land-use classes, depth-damage
curves and costs are all defined in CSV config files, so the same tool works for any
project.

## Install
Processing Toolbox ▸ Scripts ▸ **Add Script from File** ▸ `majlas_cba_tool.py`.
It appears under **Flood risk ▸ Flood CBA (config-driven)**.

## Inputs
| Parameter | What |
|---|---|
| Land-use layer + class field | polygons; field values must match the curve column names |
| Depth-damage curves CSV | `depth, <Class1>, <Class2>, …` (OMR/m²) |
| Depth-layer manifest CSV | `scenario, return_period, raster` (one row per depth GeoTIFF) |
| Scenario costs CSV | `scenario, capital_OMR, maint_annual_OMR, maint_start_year` |
| Baseline scenario name | which scenario is the do-nothing case |
| Relocation prices CSV + project outline | optional: `landuse_class, unit_OMR_per_m2` |
| Discount rate, Horizon | economic parameters |

Working examples for this project are in `examples/` (use field **LUName**).

## Outputs (to the chosen folder)
- `damage_by_rp.csv` — total damage per scenario × return period
- `cba_results.csv` — AED, avoided damage, relocation, NPV, BCR per scenario

Validated against the Python pipeline (BCR 0.107 for dam 75 M + channel 5 M).
Note: the generic engine uses one maintenance stream per scenario; the project workbook
stages dam/channel maintenance separately (a small PV difference).
