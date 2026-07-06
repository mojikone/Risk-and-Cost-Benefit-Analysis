"""
Economic layer: relocation cost, Annual Expected Damage (AED) integration,
NPV and BCR.
"""
import numpy as np, geopandas as gpd
import config as C


# ------------------------------------------------------------------ relocation
def relocation_cost(landuse_shp=C.LANDUSE_SHP, outline_shp=C.OUTLINE_SHP):
    """
    Sum over plots of  (plot area inside project outline) * unit price[class].
    Partially-overlapping plots are area-clipped to the outline.
    """
    lu = gpd.read_file(landuse_shp)
    ol = gpd.read_file(outline_shp).to_crs(lu.crs)
    outline = ol.union_all() if hasattr(ol, "union_all") else ol.unary_union

    cls = lu[C.LU_FIELD].fillna("").astype(str).str.strip()
    inter = lu.geometry.intersection(outline)
    area_in = inter.area
    unit = cls.map(C.RELOC_UNIT).fillna(0.0)
    cost = (area_in * unit)

    by_class = {}
    for c in sorted(cls.unique()):
        m = cls == c
        by_class[c or "(roads/blank)"] = dict(
            area_in_m2=float(area_in[m].sum()),
            unit=float(C.RELOC_UNIT.get(c, 0.0)),
            cost_OMR=float(cost[m].sum()))
    return float(cost.sum()), by_class


# ------------------------------------------------------------------ AED
def aed(damage_by_rp):
    """
    Annual Expected Damage = integral of damage over exceedance probability.
    damage_by_rp: {return_period_years: damage_OMR}.
    Trapezoidal over modelled points; flat tail above the rarest event
    (rectangle D_max * p_min); zero below the most frequent event.
    """
    rps = sorted(damage_by_rp)                      # ascending RP
    p = np.array([1.0 / r for r in rps])            # exceedance prob (descending)
    d = np.array([damage_by_rp[r] for r in rps])
    order = np.argsort(p)                           # ascending p
    p, d = p[order], d[order]
    # trapezoid between modelled points
    _trap = getattr(np, "trapezoid", None) or np.trapz
    integral = _trap(d, p)
    # flat tail from p=0 to smallest p (rarest event): rectangle
    integral += d[0] * p[0]
    # band more frequent than the 2yr event (p>p_max) contributes zero
    return float(integral)


# ------------------------------------------------------------------ NPV / BCR
def _pv_annuity(annual, start_year, r=C.DISCOUNT_RATE, n=C.HORIZON_YEARS):
    return sum(annual / (1 + r) ** i for i in range(start_year, n + 1))


def npv_bcr(annual_avoided, relocation):
    initial = C.COST_DAM_OMR + C.COST_CHANNEL_OMR + relocation
    maint_dam     = C.MAINT_DAM_RATE * C.COST_DAM_OMR
    maint_channel = C.MAINT_CHANNEL_RATE * C.COST_CHANNEL_OMR

    pv_benefits = _pv_annuity(annual_avoided, 1)
    pv_maint = (_pv_annuity(maint_dam, C.MAINT_DAM_START)
                + _pv_annuity(maint_channel, C.MAINT_CHANNEL_START))
    pv_costs = initial + pv_maint

    npv = pv_benefits - pv_maint - initial
    bcr = pv_benefits / pv_costs if pv_costs else float("nan")
    return dict(initial_cost=initial, pv_benefits=pv_benefits, pv_maint=pv_maint,
                pv_costs=pv_costs, npv=npv, bcr=bcr,
                maint_dam_annual=maint_dam, maint_channel_annual=maint_channel)
