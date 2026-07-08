const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  AlignmentType, HeadingLevel, WidthType, Math, MathRun, MathSum, MathIntegral,
  MathFraction, MathSubScript, MathSuperScript
} = require("docx");

const OUT = "output", MAPS = "output/maps", CW = 9026;
const HZ = JSON.parse(fs.readFileSync("output/hazard/hazard_tables.json", "utf8"));
const styles = fs.readFileSync("build/sample_styles.xml", "utf8");

let figN = 0, tabN = 0;
const P = (runs, o = {}) => new Paragraph({ spacing: { after: 120 }, ...o,
  children: Array.isArray(runs) ? runs : [new TextRun(runs)] });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const bul = t => new Paragraph({ style: "bullets", children: Array.isArray(t) ? t : [new TextRun(t)] });
const eqP = children => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 140 },
  children: [new Math({ children })] });

const figure = (path, w, h, title) => {
  figN++;
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 140, after: 40 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(path), transformation: { width: w, height: h },
        altText: { title, description: title, name: "fig" } })] }),
    new Paragraph({ style: "Caption", alignment: AlignmentType.CENTER, spacing: { after: 180 },
      children: [new TextRun(`Figure ${figN}- ${title}`)] })
  ];
};

const tblCaption = title => { tabN++; return new Paragraph({ style: "Caption", spacing: { before: 140, after: 60 },
  children: [new TextRun(`Table ${tabN}- ${title}`)] }); };

function table(headers, rows, widths, boldLastRow) {
  const cell = (txt, o = {}) => new TableCell({ width: { size: o.w, type: WidthType.DXA },
    margins: { top: 40, bottom: 40, left: 90, right: 90 },
    children: [new Paragraph({ alignment: o.al || AlignmentType.LEFT,
      children: [new TextRun({ text: String(txt), bold: !!o.bold, size: 18 })] })] });
  const head = new TableRow({ tableHeader: true, children: headers.map((h, i) =>
    cell(h, { w: widths[i], bold: true, al: i ? AlignmentType.RIGHT : AlignmentType.LEFT })) });
  const body = rows.map((r, ri) => new TableRow({ children: r.map((c, i) =>
    cell(c, { w: widths[i], al: i ? AlignmentType.RIGHT : AlignmentType.LEFT,
      bold: boldLastRow && ri === rows.length - 1 })) }));
  return new Table({ style: "PlainTable1", width: { size: CW, type: WidthType.DXA },
    columnWidths: widths, rows: [head, ...body] });
}

// ---------------- native OMML equations ----------------
const sub = (b, s) => new MathSubScript({ children: [new MathRun(b)], subScript: [new MathRun(s)] });
const eqDamage = () => eqP([ new MathRun("D(T) = "),
  new MathSum({ subScript: [new MathRun("c")], superScript: [new MathRun("")],
    children: [ sub("f", "c"), new MathRun("(h) · a") ] }) ]);
const eqAED = () => eqP([ new MathRun("AED = "),
  new MathIntegral({ subScript: [new MathRun("0")], superScript: [new MathRun("1")],
    children: [new MathRun("D(p) dp")] }) ]);
const eqAvoided = () => eqP([ new MathRun("B = "), sub("AED", "baseline"), new MathRun(" − "), sub("AED", "scheme") ]);
const eqNPV = () => eqP([ new MathRun("NPV = "),
  new MathSum({ subScript: [new MathRun("t = 1")], superScript: [new MathRun("n")],
    children: [ new MathFraction({ numerator: [new MathRun("B − M")],
      denominator: [ new MathSuperScript({ children: [new MathRun("(1 + r)")], superScript: [new MathRun("t")] }) ] }) ] }),
  new MathRun(" − "), sub("C", "0") ]);
const eqBCR = () => eqP([ new MathRun("BCR = "),
  new MathFraction({ numerator: [new MathRun("PV(B)")],
    denominator: [ sub("C", "0"), new MathRun(" + PV(M)") ] }) ]);
const eqEAPE = () => eqP([ new MathRun("EAPE = "),
  new MathIntegral({ subScript: [new MathRun("0")], superScript: [new MathRun("1")],
    children: [new MathRun("N(p) dp")] }) ]);

// ---------------- data ----------------
const DMG = [["2","430,603","413,027","17,576"],["5","1,011,369","667,876","343,493"],["10","2,286,454","1,105,001","1,181,453"],
 ["25","3,513,744","1,352,664","2,161,081"],["50","4,670,209","1,576,424","3,093,785"],["100","5,900,757","1,818,152","4,082,605"],
 ["200","7,456,451","2,093,806","5,362,645"],["500","9,499,861","2,813,500","6,686,361"],["1000","11,019,644","3,789,619","7,230,025"],
 ["10000","14,243,470","8,922,389","5,321,080"]];
const HW = [900,1160,1160,1160,1160,1160,1160,1166];
const HH = ["RP (yr)","H1","H2","H3","H4","H5","H6","Total"];

const children = [
  // ---------------- Executive summary ----------------
  H1("Executive Summary"),
  P("The Wadi Majlas flood-protection scheme comprises a storage dam on the wadi and downstream channel dykes. This report assesses the scheme against the do-nothing baseline on two grounds: the economic return on avoided flood damage, and the reduction in flood hazard to the population. Ten return periods from 2 to 10,000 years were modelled for both conditions; the scheme is designed to the 200-year flood and checked at the 500-year event."),
  P("Direct flood damage avoided by the scheme amounts to 0.37 M OMR per year. Discounted at 4.2% over a 50-year horizon this is worth 7.8 M OMR, against an initial cost of 80.2 M OMR and 13.6 M OMR of discounted maintenance. The scheme therefore returns a benefit-cost ratio of 0.08 and a net present value of −86.0 M OMR. The protected land is predominantly agricultural and low-density residential, and the works reduce flood depth more than flood extent, so the monetary benefit is inherently modest."),
  P("The decisive benefit is to life. Classified against the Australian flood hazard vulnerability curves, the number of residents standing in floodwater that is unsafe for people (hazard class H4 and above) falls from 5,222 to 510 at the 200-year design event — a 90% reduction — and from 5,947 to 967 at the 500-year check. In expected-annual terms the scheme keeps 809 people per year out of floodwater altogether."),
  P("Weighed across economic return, flood hazard to life, design-standard compliance, access to essential services, livelihoods and environment, the scheme scores 3.0 out of 5 — moderately favourable. The recommendation is that the investment decision be taken on this combined economic and flood-hazard basis, rather than on the benefit-cost ratio alone, which values only property damage and is blind to loss of life."),

  // ---------------- 1 Introduction ----------------
  H1("Introduction"),
  P("Wadi Majlas drains a steep catchment to the coast at Quriyat, and its flash floods pass directly through the built-up area. The proposed protection scheme combines a storage dam, which attenuates the flood peak, with dykes that confine the residual flow to a defined channel through the town."),
  P("The purpose of this study is to establish the technical and economic case for that scheme. It quantifies, for the baseline and scheme conditions alike, the extent and depth of flooding, the flood hazard to people, the direct damage to property and land, and the resulting economic performance of the investment. The outcome is a decision basis that sets the monetary return alongside the reduction in risk to life."),
  P("The scheme is designed to provide protection against the 200-year flood. Its behaviour at the 500-year event is examined as a control on residual risk, and the full range from 2 to 10,000 years is reported so that both frequent nuisance flooding and extreme events are visible."),

  // ---------------- 2 Methodology ----------------
  H1("Methodology"),
  P("The assessment follows a single chain: the hydraulic model produces flood depth and hazard for every return period and both conditions; these are combined with land use and population to give damage and exposure per event; each is integrated over flood probability to give an expected annual value; the difference between conditions is the benefit of the scheme; and the monetary benefit is discounted and compared with cost, while the hazard benefit is carried forward un-monetized into the decision assessment."),

  H2("Technical basis"),
  P("Flooding is simulated with a two-dimensional HEC-RAS model of the wadi and floodplain. Maximum flood depth and maximum flow velocity are exported on a 2 m grid for ten return periods (2, 5, 10, 25, 50, 100, 200, 500, 1,000 and 10,000 years) under two conditions: the baseline, and the scheme with the dam and dykes represented in the terrain. All spatial data are held in WGS 84 / UTM Zone 40N (EPSG:32640). Land use is taken from the cadastral plot layer, and resident population from the GHS-POP 2025 gridded dataset."),

  H2("Flood damage"),
  P("Damage is evaluated cell by cell rather than plot by plot, so that partial inundation of a plot is captured correctly. Every 2 m cell is assigned a land-use class from the cadastral layer, and its flood depth is read from the model. A depth-damage function for that class returns the damage per square metre at that depth; multiplying by the cell area and summing over all flooded cells gives the total direct damage for the event:"),
  eqDamage(),
  P([ new TextRun("Here "), new TextRun({ text: "f", italics: true }), new TextRun("ᶜ(h) is the depth-damage value (OMR/m²) for land-use class "),
      new TextRun({ text: "c", italics: true }), new TextRun(" at flood depth "), new TextRun({ text: "h", italics: true }),
      new TextRun(", and "), new TextRun({ text: "a", italics: true }), new TextRun(" is the cell area (4 m²). Depth-damage functions are the JRC global curves calibrated to Oman at 2023 price level, defined separately for residential, commercial, industrial, road and agricultural land.") ]),

  H2("Annual Expected Damage"),
  P([ new TextRun("A single event does not describe risk. Damage is therefore integrated over the annual exceedance probability "),
      new TextRun({ text: "p", italics: true }), new TextRun(" = 1/"), new TextRun({ text: "T", italics: true }),
      new TextRun(" to give the Annual Expected Damage, evaluated by the trapezoidal rule across the modelled return periods:") ]),
  eqAED(),
  P("Damage more frequent than the 2-year event is taken as zero, and damage rarer than the 10,000-year event is held constant. The benefit of the scheme is the difference between the two conditions:"),
  eqAvoided(),

  H2("Economic appraisal"),
  P([ new TextRun("The avoided damage "), new TextRun({ text: "B", italics: true }), new TextRun(" is an annual benefit stream. It is discounted, net of annual maintenance "),
      new TextRun({ text: "M", italics: true }), new TextRun(", over the appraisal horizon "), new TextRun({ text: "n", italics: true }),
      new TextRun(" at the real discount rate "), new TextRun({ text: "r", italics: true }), new TextRun(", and set against the initial cost "),
      new TextRun({ text: "C", italics: true }), new TextRun("₀ of the dam, the dykes and land relocation:") ]),
  eqNPV(), eqBCR(),
  P("A scheme is economically justified in these terms when the net present value exceeds zero and the benefit-cost ratio exceeds one."),

  H2("Population exposure"),
  P([ new TextRun("The same probabilistic integration is applied to the number of residents standing in the flood, "),
      new TextRun({ text: "N", italics: true }), new TextRun("(p), giving the Expected Annual People Exposed:") ]),
  eqEAPE(),
  P("EAPE is reported for all floodwater and, as a life-safety measure, for water deeper than one metre. The reduction the scheme delivers is termed the EAPE avoided."),

  H2("Flood hazard classification"),
  P("Depth alone understates danger: shallow water moving quickly can sweep a person off their feet. Flood hazard to life is therefore derived in the hydraulic model from the combination of flow depth and velocity, and classified into six categories, H1 to H6, against the Australian combined hazard vulnerability curves (Smith et al., 2014; AIDR Guideline 7-3, Figure 6). The classification is threshold-based on depth, velocity and their product; it is not a single algebraic index. From class H4 upward, floodwater is unsafe for people. Section 6 sets out the classes and the resulting exposure."),

  H2("Decision framework"),
  P("The benefit-cost ratio measures only avoided property damage. Loss of life, continuity of access and livelihood protection are real benefits that it cannot see. The two strands are therefore brought together in a transparent multi-criteria assessment (Section 9), in which the economic result and the flood-hazard result are weighted alongside the wider factors to produce a single, auditable score."),

  // ---------------- 3 Assumptions ----------------
  H1("Assumptions and inputs"),
  P("The modelling and spatial data are described in Section 2. The parameters below are the economic assumptions adopted for the appraisal; each may be varied in the accompanying cost-benefit workbook."),
  tblCaption("Economic assumptions adopted for the appraisal"),
  table(["Parameter", "Value", "Basis"], [
    ["Dam capital cost", "75,000,000 OMR", "Client estimate"],
    ["Dyke / channel capital cost", "5,000,000 OMR", "Client estimate"],
    ["Relocation cost", "168,080 OMR", "Plots within the works footprint × unit land price"],
    ["Unit land price — residential", "15 OMR/m²", "Client rate"],
    ["Unit land price — commercial / industrial", "20 OMR/m²", "Client rate"],
    ["Unit land price — agricultural", "2 OMR/m²", "Client rate"],
    ["Maintenance — dam", "1.0% of capital per year, from year 5", "Standard allowance"],
    ["Maintenance — dykes", "0.7% of capital per year, from year 2", "Standard allowance"],
    ["Real discount rate", "4.2%", "Client instruction"],
    ["Appraisal horizon", "50 years", "Design life"],
    ["Damage below the 2-year event", "Zero", "Standard AED tail treatment"],
    ["Damage above the 10,000-year event", "Held constant", "Standard AED tail treatment"],
  ], [2600, 2500, 3926]),

  // ---------------- 4 Flood damage ----------------
  H1("Flood damage"),
  P("Direct damage rises steeply with return period and is dominated by residential property. Agriculture floods the largest area but contributes very little value, because agricultural depth-damage rates are two orders of magnitude below those for buildings. The scheme reduces damage at every return period by confining the flow and lowering depths across the protected area."),
  ...figure(OUT + "/chart_damage_by_class.png", 610, 235, "Flood damage by land-use class, baseline and scheme (total M OMR shown on each bar)"),
  tblCaption("Direct flood damage and avoided damage by return period"),
  table(["RP (yr)", "Baseline (OMR)", "Scheme (OMR)", "Avoided (OMR)"], DMG, [1400, 2542, 2542, 2542]),

  // ---------------- 5 Economic appraisal ----------------
  H1("Economic appraisal"),
  P("Integrating damage over probability gives an Annual Expected Damage of 0.77 M OMR/yr for the baseline and 0.40 M OMR/yr with the scheme. The annual avoided damage — the benefit stream — is therefore 0.37 M OMR."),
  ...figure(OUT + "/AED_curves.png", 610, 262, "Annual Expected Damage; the shaded area between the curves is the avoided damage"),
  tblCaption("Economic summary of the scheme (50-year horizon, 4.2% discount rate)"),
  table(["Metric", "Value (OMR)"], [
    ["Annual Expected Damage — baseline", "771,767"],
    ["Annual Expected Damage — scheme", "397,828"],
    ["Annual avoided damage (benefit)", "373,939"],
    ["Initial cost (dam 75 M + dykes 5 M + relocation 0.17 M)", "80,168,080"],
    ["Present value of benefits", "7,765,253"],
    ["Present value of maintenance", "13,558,148"],
    ["Present value of costs", "93,726,228"],
    ["Net Present Value (NPV)", "−85,960,975"],
    ["Benefit-Cost Ratio (BCR)", "0.083"],
  ], [6018, 3008], true),
  ...figure(OUT + "/chart_cost_benefit.png", 470, 272, "Present value of benefits against present value of costs"),
  P("On avoided direct damage alone the scheme does not recover its cost. The benefit-cost ratio of 0.08 and net present value of −86.0 M OMR reflect the low monetary value of the assets protected, not a failure of the works to perform: as Section 6 shows, the same works remove nine in ten people from life-threatening floodwater at the design event."),

  // ---------------- 6 Flood hazard ----------------
  H1("Flood hazard"),
  P("Flood hazard combines depth and velocity to describe what the floodwater does to a person, a vehicle or a building. The six Australian classes escalate from generally safe to complete building failure; from H4 upward the water is unsafe for people."),
  tblCaption("Australian flood hazard classification (AIDR Guideline 7-3)"),
  table(["Class", "Vulnerability", "Indicative limit (D and V in combination)"], [
    ["H1", "Generally safe for people, vehicles and buildings", "D·V ≤ 0.3; D ≤ 0.3 m; V ≤ 2.0 m/s"],
    ["H2", "Unsafe for small vehicles", "D·V ≤ 0.6; D ≤ 0.5 m; V ≤ 2.0 m/s"],
    ["H3", "Unsafe for vehicles, children and the elderly", "D·V ≤ 0.6; D ≤ 1.2 m; V ≤ 2.0 m/s"],
    ["H4", "Unsafe for vehicles and people", "D·V ≤ 1.0; D ≤ 2.0 m; V ≤ 2.0 m/s"],
    ["H5", "Unsafe for vehicles and people; buildings vulnerable to structural damage", "D·V ≤ 4.0; D ≤ 4.0 m; V ≤ 4.0 m/s"],
    ["H6", "Unsafe for all; all building types vulnerable to failure", "D·V > 4.0, or D > 4.0 m, or V > 4.0 m/s"],
  ], [900, 4300, 3826]),
  P("The scheme transforms the hazard composition of the floodplain. In the baseline a large share of the flooded area, and of the people standing in it, falls in the damaging H5 and H6 classes. With the dam and dykes in place, the flow is confined and slowed, and the great majority of the residual flooding is reduced to the benign H1 and H2 classes."),
  ...figure(OUT + "/chart_hazard_people.png", 620, 248, "People by flood hazard class and return period, baseline and scheme"),
  ...figure(OUT + "/chart_hazard_plots_area.png", 600, 400, "Plots and inundated area by flood hazard class, baseline and scheme"),

  H2("Hazard exposure — detailed results"),
  P("The following tables give, for every return period and both conditions, the number of people, the number of cadastral plots and the inundated area falling in each hazard class. Plots are assigned to their worst (maximum) hazard class. The 2-year baseline hazard grid was not exported and is omitted; it is immaterial to the design decision."),

  tblCaption("People by flood hazard class — baseline"),
  table(HH, HZ.people_baseline, HW),
  tblCaption("People by flood hazard class — scheme"),
  table(HH, HZ.people_scheme, HW),
  tblCaption("Plots by flood hazard class — baseline"),
  table(HH, HZ.plots_baseline, HW),
  tblCaption("Plots by flood hazard class — scheme"),
  table(HH, HZ.plots_scheme, HW),
  tblCaption("Inundated area (ha) by flood hazard class — baseline"),
  table(HH, HZ.area_baseline, HW),
  tblCaption("Inundated area (ha) by flood hazard class — scheme"),
  table(HH, HZ.area_scheme, HW),

  P("Aggregating the classes that are unsafe for people (H4, H5 and H6) gives the headline hazard benefit of the scheme."),
  tblCaption("People and plots in hazard unsafe for people (H4+), and the exposure avoided"),
  table(["RP (yr)", "People — baseline", "People — scheme", "People avoided", "Reduction", "Plots — baseline", "Plots — scheme"],
    HZ.h4, [1000, 1400, 1400, 1300, 1200, 1350, 1376]),
  ...figure(OUT + "/chart_hazard_h4plus.png", 610, 300, "People in hazard unsafe for people (H4+): baseline against scheme, with the reduction achieved"),
  P("At the 200-year design event the scheme reduces the population standing in unsafe hazard from 5,222 to 510, a reduction of 90%, and the number of plots so affected from 715 to 113. At the 500-year check the reduction is 5,947 to 967, or 84%. Only at the 10,000-year event, far beyond the design standard, does the margin narrow, as the dam's storage is exceeded."),

  // ---------------- 7 Population safety ----------------
  H1("Population safety"),
  P("Hazard class H4 and above is the threshold at which floodwater is unsafe for people. Section 6 shows that this population is reduced by around 90% at the design event. Considering all floodwater, irrespective of hazard class, the scheme keeps an expected 809 people per year out of the flood, and 345 per year out of water deeper than one metre."),
  ...figure(OUT + "/chart_exposure.png", 610, 235, "People exposed to flooding and to water deeper than one metre; the shaded band is the exposure avoided"),
  P("The scheme does not merely shrink the flood. It converts deep, fast, dangerous water into shallow nuisance flooding across the populated area — the change that determines whether an event costs lives."),

  // ---------------- 8 Non-monetized benefits ----------------
  H1("Non-monetized benefits"),
  P("Beyond lives saved, the scheme delivers benefits that a damage-based ratio cannot capture but that bear directly on the decision:"),
  bul("Injury and trauma avoided — the injuries, displacement and lasting distress that follow a fatal flash flood."),
  bul("Continuity of access — roads and routes to homes, the hospital and emergency services remain passable during an event, when they are most needed."),
  bul("Protected livelihoods — repeated inundation degrades farmland and interrupts businesses; reducing depth and duration protects income, not only assets."),
  bul("Lower response and recovery burden on the authorities after each event."),
  bul("Community stability and confidence — durable protection supports investment and discourages abandonment of exposed land."),
  bul("Reduced erosion and sedimentation along the wadi and to downstream infrastructure."),

  // ---------------- 9 Decision assessment ----------------
  H1("Decision assessment"),
  P("This section exists because the two preceding results point in opposite directions. The economic appraisal returns a benefit-cost ratio well below unity; the hazard assessment shows a near-elimination of life-threatening flooding at the design event. Neither result may be discarded, and neither is expressed in the units of the other. A transparent multi-criteria assessment is therefore used to combine them, so that the weight given to each consideration is explicit, auditable and open to challenge."),
  P("Each criterion is scored from 1 (weak) to 5 (strong) and weighted; the weighted contributions sum to an overall score out of 5."),
  tblCaption("Multi-criteria decision assessment of the scheme"),
  table(["Criterion", "Weight", "Score /5", "Weighted", "Assessment"], [
    ["Economic return (BCR / NPV)", "40%", "1", "0.40", "Benefits well below cost (BCR 0.08)"],
    ["Life safety (flood hazard)", "25%", "5", "1.25", "People in unsafe hazard (H4+) cut 90% at design event"],
    ["Design-standard compliance", "10%", "5", "0.50", "Meets the 200-year target; resilient at 500-year"],
    ["Access to essential services", "10%", "4", "0.40", "Roads and hospital access maintained during floods"],
    ["Livelihoods and property", "10%", "3", "0.30", "Reduced repeat inundation of homes and farmland"],
    ["Environment and wadi morphology", "5%", "3", "0.15", "Reduced erosion and sedimentation"],
    ["Overall", "100%", "—", "3.00 / 5", "Moderately favourable, despite weak economics"],
  ], [2450, 900, 900, 1100, 3676], true),
  ...figure(OUT + "/chart_mca.png", 590, 304, "Weighted contribution of each criterion to the overall decision score"),
  P("The scheme scores 3.00 out of 5 — moderately favourable. The result is sensitive to the weight placed on economic return, which is deliberately the heaviest at 40%: were it weighted at 25% the score would rise to 3.60, and at 50% it would fall to about 2.70. In every case the conclusion is the same in direction — the single weak economic criterion is outweighed by strong performance on flood hazard to life and on design-standard compliance — but the client should adopt the weighting explicitly, as it is the pivot of the recommendation."),

  // ---------------- 10 Flood maps ----------------
  H1("Flood maps"),
  P("Flood depth, flood hazard and direct damage at the 200-year design event and the 500-year control, baseline then scheme. On the scheme maps the dam axis is drawn in white and the dykes in black. The complete set for all return periods accompanies this report."),

  H2("200-year event — design target"),
  ...figure(MAPS + "/depth_200yr_baseline.png", 560, 396, "Flood depth, 200-year — baseline"),
  ...figure(MAPS + "/depth_200yr_scheme.png", 560, 396, "Flood depth, 200-year — scheme"),
  ...figure(MAPS + "/hazard_200yr_baseline.png", 560, 396, "Flood hazard (H1–H6), 200-year — baseline"),
  ...figure(MAPS + "/hazard_200yr_scheme.png", 560, 396, "Flood hazard (H1–H6), 200-year — scheme"),
  ...figure(MAPS + "/damage_200yr_baseline.png", 560, 396, "Flood damage, 200-year — baseline"),
  ...figure(MAPS + "/damage_200yr_scheme.png", 560, 396, "Flood damage, 200-year — scheme"),

  H2("500-year event — control"),
  ...figure(MAPS + "/depth_500yr_baseline.png", 560, 396, "Flood depth, 500-year — baseline"),
  ...figure(MAPS + "/depth_500yr_scheme.png", 560, 396, "Flood depth, 500-year — scheme"),
  ...figure(MAPS + "/hazard_500yr_baseline.png", 560, 396, "Flood hazard (H1–H6), 500-year — baseline"),
  ...figure(MAPS + "/hazard_500yr_scheme.png", 560, 396, "Flood hazard (H1–H6), 500-year — scheme"),
  ...figure(MAPS + "/damage_500yr_baseline.png", 560, 396, "Flood damage, 500-year — baseline"),
  ...figure(MAPS + "/damage_500yr_scheme.png", 560, 396, "Flood damage, 500-year — scheme"),

  // ---------------- 11 Conclusion ----------------
  H1("Conclusion"),
  P([new TextRun({ text: "Design performance. ", bold: true }), new TextRun("The scheme achieves the 200-year protection standard it was designed for, and retains most of its effectiveness at the 500-year control event. Its performance degrades only at events far beyond the design standard, where the dam's storage is exceeded — the expected and accepted behaviour of a scheme of this type.")]),
  P([new TextRun({ text: "Economic outcome. ", bold: true }), new TextRun("Measured on avoided direct damage alone, the scheme does not pay back: a benefit-cost ratio of 0.08 and a net present value of −86.0 M OMR. The reason is structural rather than hydraulic. The land protected is largely agricultural and low-density residential, whose damage rates are low, and the works reduce flood depth far more than flood extent, so the monetary saving is small relative to an 80 M OMR capital outlay. No plausible change to the discount rate alters this conclusion.")]),
  P([new TextRun({ text: "Flood hazard and life safety. ", bold: true }), new TextRun("Measured on hazard to life, the scheme is decisive. At the 200-year design event the population standing in floodwater unsafe for people falls from 5,222 to 510, a 90% reduction, and the plots so affected from 715 to 113. At the 500-year control the reduction is 84%. In expected-annual terms 809 people per year are kept out of floodwater. The scheme converts deep, fast water into shallow nuisance flooding across the town.")]),
  P([new TextRun({ text: "Wider benefits. ", bold: true }), new TextRun("Continuity of access to homes, the hospital and emergency services during an event; protection of farmland and businesses from repeated inundation; a reduced response and recovery burden; and reduced erosion of the wadi. None of these enter the benefit-cost ratio; all of them accrue.")]),
  P([new TextRun({ text: "Overall judgement. ", bold: true }), new TextRun("Weighed across all criteria the scheme scores 3.00 out of 5 — moderately favourable. The economic criterion, weighted most heavily, scores lowest; it is outweighed by flood-hazard reduction to life and by design-standard compliance. The benefit-cost ratio, taken in isolation, is not a sufficient basis for this decision, because it prices property and ignores people.")]),

  // ---------------- 12 Recommendations ----------------
  H1("Recommendations"),
  bul([new TextRun({ text: "Adopt the combined economic and flood-hazard basis set out in Section 9 for the investment decision, rather than the benefit-cost ratio alone.", bold: true })]),
  bul("Adopt the criterion weighting explicitly. The overall score is moderately favourable and is sensitive to the weight given to economic return; the weighting should be confirmed by the client as a matter of policy before the decision is recorded."),
  bul("Proceed on the 200-year design standard. The 500-year control confirms that residual risk beyond the design event remains substantially reduced."),
  bul("Complete the data set by exporting the 2-year baseline hazard grid, for consistency of the hazard series. It does not affect the design decision."),
  bul("Retain the flood-hazard classification as the reporting basis for life safety in subsequent design stages, in preference to depth thresholds alone."),
];

const doc = new Document({ externalStyles: styles,
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 },
    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } }, children }] });

Packer.toBuffer(doc).then(b => { fs.mkdirSync("build", { recursive: true });
  fs.writeFileSync("build/body.docx", b);
  console.log(`body.docx written — ${figN} figures, ${tabN} tables`); });
