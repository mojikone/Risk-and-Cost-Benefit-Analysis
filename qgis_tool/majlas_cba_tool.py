"""
Flood Cost-Benefit Analysis — QGIS Processing tool.

A generic, config-driven flood cost-benefit engine. Everything is dynamic:
  * number of depth layers, return periods and scenarios  -> depth_manifest.csv
  * land-use classes and their depth-damage functions      -> depth_damage_curves.csv
  * capital + maintenance cost per scenario                -> scenario_costs.csv
  * relocation unit price per land-use class               -> relocation_unit_prices.csv
  * discount rate, horizon                                 -> tool parameters

Add via Processing Toolbox ▸ Scripts ▸ Add Script from File, then run
"Flood CBA (config-driven)".  Example config files are in qgis_tool/examples/.

Config file formats (CSV, header row required)
  depth_damage_curves.csv : depth, <Class1>, <Class2>, ...        (OMR/m2)
  depth_manifest.csv      : scenario, return_period, raster       (raster = path to depth GeoTIFF)
  scenario_costs.csv      : scenario, capital_OMR, maint_annual_OMR, maint_start_year
  relocation_unit_prices.csv (optional) : landuse_class, unit_OMR_per_m2

The land-use layer must have a field whose values match the class column names in the
curves file (e.g. Residential, Commercial, ...).  All layers must share one CRS.
"""
import os, csv
import numpy as np
from osgeo import gdal, ogr
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField, QgsProcessingParameterFile, QgsProcessingParameterString,
    QgsProcessingParameterNumber, QgsProcessingParameterFolderDestination,
    QgsProcessingException)

gdal.UseExceptions()


# ----------------------------------------------------------------- compute core
def _read_curves(path):
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    classes = [c.strip() for c in rows[0][1:]]
    depths, curves = [], {c: [] for c in classes}
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        depths.append(float(r[0]))
        for j, c in enumerate(classes):
            curves[c].append(float(r[j + 1]))
    return depths, curves, classes


def _read_dicts(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _classid_layer(landuse_path, field, classes):
    """OGR memory layer copy with an integer 'cbaid' field (1..n by class order)."""
    src = ogr.Open(landuse_path)
    if src is None:
        raise QgsProcessingException(f"cannot open land-use layer: {landuse_path}")
    lyr = src.GetLayer()
    mem = ogr.GetDriverByName("MEMORY").CreateDataSource("m")
    out = mem.CopyLayer(lyr, "lu")
    out.CreateField(ogr.FieldDefn("cbaid", ogr.OFTInteger))
    cid = {c: i + 1 for i, c in enumerate(classes)}
    fi = out.GetLayerDefn().GetFieldIndex(field)
    for feat in out:
        val = feat.GetField(fi)
        feat.SetField("cbaid", cid.get(str(val).strip() if val is not None else "", 0))
        out.SetFeature(feat)
    out.ResetReading()
    return mem, out


def _damage_for_raster(raster, memlyr, depths, curves, classes):
    ds = gdal.Open(raster)
    if ds is None:
        raise QgsProcessingException(f"cannot open raster: {raster}")
    gt = ds.GetGeoTransform(); xs, ys = ds.RasterXSize, ds.RasterYSize
    px = abs(gt[1] * gt[5])
    band = ds.GetRasterBand(1)
    d = band.ReadAsArray().astype("float64"); nod = band.GetNoDataValue()
    if nod is not None:
        d = np.where(d == nod, 0.0, d)
    d[~np.isfinite(d)] = 0.0; d[d < 0] = 0.0
    mem = gdal.GetDriverByName("MEM").Create("", xs, ys, 1, gdal.GDT_Int32)
    mem.SetGeoTransform(gt); mem.SetProjection(ds.GetProjection())
    gdal.RasterizeLayer(mem, [1], memlyr, options=["ATTRIBUTE=cbaid"])
    cid = mem.ReadAsArray()
    total = 0.0; wet = d > 0
    for i, c in enumerate(classes, 1):
        m = (cid == i) & wet
        if m.any():
            total += float(np.interp(d[m], depths, curves[c]).sum()) * px
    return total


def _aed(damage_by_rp):
    rps = sorted(damage_by_rp)
    p = [1.0 / r for r in rps]; dvals = [damage_by_rp[r] for r in rps]
    integ = 0.0
    for i in range(len(rps) - 1):
        integ += 0.5 * (dvals[i] + dvals[i + 1]) * (p[i] - p[i + 1])
    return integ + dvals[-1] * p[-1]          # + flat tail; zero below most frequent


def _relocation(landuse_path, field, outline_path, unit):
    if not outline_path or not unit:
        return 0.0
    lu_ds = ogr.Open(landuse_path); lu = lu_ds.GetLayer()
    ol_ds = ogr.Open(outline_path); ol = ol_ds.GetLayer()
    olg = None
    for f in ol:
        g = f.GetGeometryRef().Clone()
        olg = g if olg is None else olg.Union(g)
    ol.ResetReading()
    fi = lu.GetLayerDefn().GetFieldIndex(field); cost = 0.0
    for f in lu:
        g = f.GetGeometryRef()
        if g is None or olg is None or not g.Intersects(olg):
            continue
        inter = g.Intersection(olg)
        cls = str(f.GetField(fi)).strip() if f.GetField(fi) is not None else ""
        cost += inter.GetArea() * unit.get(cls, 0.0)
    return cost


def run_cba(landuse, field, curves_csv, manifest_csv, costs_csv, baseline,
            rate, horizon, out_dir, reloc_csv=None, outline=None, feedback=None):
    depths, curves, classes = _read_curves(curves_csv)
    manifest = _read_dicts(manifest_csv)
    costs = {r["scenario"]: r for r in _read_dicts(costs_csv)}
    unit = None
    if reloc_csv:
        unit = {r["landuse_class"].replace("(blank)", "").strip(): float(r["unit_OMR_per_m2"])
                for r in _read_dicts(reloc_csv)}
    mem, memlyr = _classid_layer(landuse, field, classes)

    dmg = {}                     # scenario -> {rp: damage}
    for i, row in enumerate(manifest):
        sc = row["scenario"].strip(); rp = int(float(row["return_period"]))
        val = _damage_for_raster(row["raster"].strip(), memlyr, depths, curves, classes)
        dmg.setdefault(sc, {})[rp] = val
        if feedback:
            feedback.setProgress(100 * (i + 1) / len(manifest))
            feedback.pushInfo(f"{sc} {rp}yr  damage {val:,.0f} OMR")

    aed = {sc: _aed(d) for sc, d in dmg.items()}
    reloc = _relocation(landuse, field, outline, unit) if unit else 0.0
    ann = lambda start: sum(1 / (1 + rate) ** t for t in range(int(start) if start else 1, horizon + 1))

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "damage_by_rp.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["scenario", "return_period", "damage_OMR"])
        for sc, d in dmg.items():
            for rp in sorted(d):
                w.writerow([sc, rp, round(d[rp])])

    res = []
    for sc in dmg:
        if sc == baseline:
            continue
        avoided = aed[baseline] - aed[sc]
        c = costs.get(sc, {})
        cap = float(c.get("capital_OMR", 0)); maint = float(c.get("maint_annual_OMR", 0))
        mstart = float(c.get("maint_start_year", 1) or 1)
        initial = cap + reloc
        pv_ben = avoided * ann(1)
        pv_maint = maint * ann(mstart)
        pv_cost = initial + pv_maint
        npv = pv_ben - pv_maint - initial
        bcr = pv_ben / pv_cost if pv_cost else float("nan")
        res.append(dict(scenario=sc, AED_baseline=round(aed[baseline]), AED_scenario=round(aed[sc]),
                        avoided_annual=round(avoided), relocation=round(reloc), initial_cost=round(initial),
                        PV_benefits=round(pv_ben), PV_maintenance=round(pv_maint), PV_costs=round(pv_cost),
                        NPV=round(npv), BCR=round(bcr, 3)))
    with open(os.path.join(out_dir, "cba_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys()) if res else ["scenario"])
        w.writeheader(); [w.writerow(r) for r in res]
    return res


# ----------------------------------------------------------------- QGIS wrapper
class FloodCBAAlgorithm(QgsProcessingAlgorithm):
    LANDUSE, FIELD, CURVES, MANIFEST, COSTS = "LANDUSE", "FIELD", "CURVES", "MANIFEST", "COSTS"
    RELOC, OUTLINE, BASELINE, RATE, HORIZON, OUTPUT = "RELOC", "OUTLINE", "BASELINE", "RATE", "HORIZON", "OUTPUT"

    def tr(self, s): return QCoreApplication.translate("FloodCBA", s)
    def createInstance(self): return FloodCBAAlgorithm()
    def name(self): return "flood_cba"
    def displayName(self): return self.tr("Flood CBA (config-driven)")
    def group(self): return self.tr("Flood risk")
    def groupId(self): return "floodrisk"
    def shortHelpString(self):
        return self.tr("Config-driven flood cost-benefit: damage per return period, AED, "
                       "NPV and BCR per scenario. Scenarios, return periods, land-use classes, "
                       "depth-damage curves and costs are all defined in CSV config files.")

    def initAlgorithm(self, cfg=None):
        self.addParameter(QgsProcessingParameterVectorLayer(self.LANDUSE, "Land-use layer"))
        self.addParameter(QgsProcessingParameterField(self.FIELD, "Land-use class field", parentLayerParameterName=self.LANDUSE))
        self.addParameter(QgsProcessingParameterFile(self.CURVES, "Depth-damage curves CSV", extension="csv"))
        self.addParameter(QgsProcessingParameterFile(self.MANIFEST, "Depth-layer manifest CSV", extension="csv"))
        self.addParameter(QgsProcessingParameterFile(self.COSTS, "Scenario costs CSV", extension="csv"))
        self.addParameter(QgsProcessingParameterString(self.BASELINE, "Baseline scenario name", defaultValue="baseline"))
        self.addParameter(QgsProcessingParameterFile(self.RELOC, "Relocation unit prices CSV (optional)", optional=True, extension="csv"))
        self.addParameter(QgsProcessingParameterVectorLayer(self.OUTLINE, "Project outline for relocation (optional)", optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.RATE, "Discount rate", defaultValue=0.025, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.HORIZON, "Horizon (years)", defaultValue=50))
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT, "Output folder"))

    def processAlgorithm(self, params, context, feedback):
        lu = self.parameterAsVectorLayer(params, self.LANDUSE, context)
        ol = self.parameterAsVectorLayer(params, self.OUTLINE, context)
        res = run_cba(
            landuse=lu.source().split("|")[0], field=self.parameterAsString(params, self.FIELD, context),
            curves_csv=self.parameterAsFile(params, self.CURVES, context),
            manifest_csv=self.parameterAsFile(params, self.MANIFEST, context),
            costs_csv=self.parameterAsFile(params, self.COSTS, context),
            baseline=self.parameterAsString(params, self.BASELINE, context),
            rate=self.parameterAsDouble(params, self.RATE, context),
            horizon=self.parameterAsInt(params, self.HORIZON, context),
            out_dir=self.parameterAsString(params, self.OUTPUT, context),
            reloc_csv=self.parameterAsFile(params, self.RELOC, context) or None,
            outline=ol.source().split("|")[0] if ol else None, feedback=feedback)
        for r in res:
            feedback.pushInfo(f"[{r['scenario']}]  avoided {r['avoided_annual']:,} OMR/yr  "
                              f"NPV {r['NPV']:,}  BCR {r['BCR']}")
        return {self.OUTPUT: self.parameterAsString(params, self.OUTPUT, context)}
