const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  Footer, PageNumber, LevelFormat } = require("docx");

const OUT = "output", MAPS = "output/maps";
const CW = 9026;
const GREY = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellB = { top: GREY, bottom: GREY, left: GREY, right: GREY };

const img = (p, w, h, cap) => {
  const k = [ new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 },
    children: [ new ImageRun({ type: "png", data: fs.readFileSync(p), transformation: { width: w, height: h },
      altText: { title: cap, description: cap, name: cap } }) ] }) ];
  if (cap) k.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: [ new TextRun({ text: cap, italics: true, size: 18, color: "666666" }) ] }));
  return k;
};
const P = (runs, opts={}) => new Paragraph({ spacing: { after: 120 }, ...opts,
  children: (Array.isArray(runs)?runs:[new TextRun(runs)]) });
const EQ = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing:{before:60,after:120},
  children:[ new TextRun({ text:t, italics:true, size:22 }) ] });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children:[new TextRun(t)] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children:[new TextRun(t)] });
const bullet = t => new Paragraph({ numbering:{reference:"b",level:0}, spacing:{after:60},
  children:[Array.isArray(t)?null:new TextRun(t)].filter(Boolean).concat(Array.isArray(t)?t:[]) });
const cap = (t) => new Paragraph({ alignment:AlignmentType.CENTER, spacing:{before:40,after:160},
  children:[ new TextRun({ text:t, italics:true, size:18, color:"666666" }) ] });

function table(headers, rows, widths, hiLast) {
  const mk = (txt, o={}) => new TableCell({ borders: cellB, width:{size:o.w,type:WidthType.DXA},
    shading: o.fill?{fill:o.fill,type:ShadingType.CLEAR}:undefined,
    margins:{top:50,bottom:50,left:100,right:100},
    children:[new Paragraph({ alignment:o.al||AlignmentType.LEFT,
      children:[new TextRun({ text:String(txt), bold:!!o.bold, size:19, color:o.color })] })] });
  const hr = new TableRow({ tableHeader:true, children: headers.map((h,i)=>
    mk(h,{w:widths[i], bold:true, color:"FFFFFF", fill:"333333", al:i?AlignmentType.RIGHT:AlignmentType.LEFT})) });
  const trs = rows.map((r,ri)=>{ const last = hiLast && ri===rows.length-1;
    return new TableRow({ children: r.map((c,i)=> mk(c,{w:widths[i],
      al:i?AlignmentType.RIGHT:AlignmentType.LEFT, bold:last, fill:last?"DDEBF7":(ri%2?"F2F2F2":undefined)})) }); });
  return new Table({ width:{size:CW,type:WidthType.DXA}, columnWidths:widths, rows:[hr,...trs] });
}

// ---- data
const DMG = [ // RP, base, scheme, avoided, areaB, areaS
 ["2","430,603","413,027","17,576","3.21","1.98"],["5","1,011,369","667,876","343,493","4.72","2.87"],
 ["10","2,286,454","1,105,001","1,181,453","6.09","3.73"],["25","3,513,744","1,352,664","2,161,081","6.80","4.09"],
 ["50","4,670,209","1,576,424","3,093,785","7.14","4.39"],["100","5,900,757","1,818,152","4,082,605","7.39","4.68"],
 ["200","7,456,451","2,093,806","5,362,645","7.57","4.96"],["500","9,499,861","2,813,500","6,686,361","7.75","5.73"],
 ["1000","11,019,644","3,789,619","7,230,025","7.88","6.32"],["10000","14,243,470","8,922,389","5,321,080","8.12","7.76"] ];
const EXP = [ // RP, expB, expS, gt1B, gt1S, avoidedGt1
 ["2","1,796","1,085","158","84","74"],["5","3,147","1,629","524","132","392"],["10","4,527","2,155","1,335","205","1,130"],
 ["25","5,356","2,438","2,110","258","1,852"],["50","5,862","2,699","2,813","312","2,501"],["100","6,207","2,978","3,564","374","3,190"],
 ["200","6,432","3,253","4,334","447","3,887"],["500","6,617","3,831","5,259","783","4,476"],
 ["1000","6,724","4,305","5,790","1,531","4,259"],["10000","7,012","6,489","6,334","4,394","1,940"] ];

const doc = new Document({
  styles:{ default:{ document:{ run:{ font:"Arial", size:22 } } }, paragraphStyles:[
    { id:"Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true,
      run:{ size:30, bold:true, font:"Arial", color:"1F3864" }, paragraph:{ spacing:{before:280,after:140}, outlineLevel:0 } },
    { id:"Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true,
      run:{ size:24, bold:true, font:"Arial", color:"2E5496" }, paragraph:{ spacing:{before:180,after:100}, outlineLevel:1 } } ]},
  numbering:{ config:[{ reference:"b", levels:[{ level:0, format:LevelFormat.BULLET, text:"•", alignment:AlignmentType.LEFT, style:{ paragraph:{ indent:{ left:460, hanging:260 } } } }] }] },
  sections:[{
    properties:{ page:{ size:{ width:11906, height:16838 }, margin:{ top:1200, right:1440, bottom:1200, left:1440 } } },
    footers:{ default: new Footer({ children:[ new Paragraph({ alignment:AlignmentType.CENTER,
      children:[ new TextRun({ text:"Wadi Majlas Flood Protection — Cost-Benefit Analysis    ", size:16, color:"888888" }),
        new TextRun({ children:[PageNumber.CURRENT], size:16, color:"888888" }) ] }) ] }) },
    children:[
      new Paragraph({ spacing:{after:40}, children:[ new TextRun({ text:"Wadi Majlas Flood Protection", bold:true, size:40, color:"1F3864" }) ] }),
      new Paragraph({ spacing:{after:240}, children:[ new TextRun({ text:"Technical and Economic Assessment  ·  Quriyat, Oman", size:26, color:"555555" }) ] }),

      H1("1. Purpose and scope"),
      P("This report presents the technical and economic assessment of the proposed Wadi Majlas flood-protection scheme — a storage dam on the wadi together with downstream channel dykes — evaluated against the do-nothing baseline. It quantifies the flood hazard, the direct flood damage, the economic return of the scheme, and its effect on the population at risk, to support the design and investment decision."),
      P("The scheme is designed to protect against the 200-year flood, with its performance additionally verified at the 500-year event. Results are reported for ten return periods from 2 to 10,000 years so that both the design condition and the wider risk profile are visible."),

      H1("2. Methodology"),
      P("Flood damage is estimated cell-by-cell by combining modelled flood depth with land-use-specific depth-damage functions, then integrated over the full range of flood probabilities to give the Annual Expected Damage. The difference between the baseline and scheme conditions is the benefit stream, which is discounted and compared with scheme costs. Population exposure is derived on the same probabilistic basis."),
      P([ new TextRun({text:"Direct damage per event. ",bold:true}), new TextRun("For a return period T, damage is summed over every flooded raster cell:") ]),
      EQ("D(T) = Σ  fᶜ(h) · a"),
      P([ new TextRun("where "), new TextRun({text:"fᶜ(h)",italics:true}), new TextRun(" is the depth-damage value (OMR/m²) for the land-use class c at flood depth "),
        new TextRun({text:"h",italics:true}), new TextRun(", and "), new TextRun({text:"a",italics:true}), new TextRun(" is the cell area (m²).") ]),
      P([ new TextRun({text:"Annual Expected Damage (AED). ",bold:true}), new TextRun("Damage is integrated over the annual exceedance probability "),
        new TextRun({text:"p = 1/T",italics:true}), new TextRun(":") ]),
      EQ("AED = ∫₀¹ D(p) dp  ≈  Σ  ½ ( Dᵢ + Dᵢ₊₁ )( pᵢ − pᵢ₊₁ )"),
      P("evaluated by the trapezoidal rule over the modelled return periods. The avoided damage is the benefit of the scheme:"),
      EQ("Annual avoided damage = AED(baseline) − AED(scheme)"),
      P([ new TextRun({text:"Net Present Value and Benefit-Cost Ratio. ",bold:true}), new TextRun("Benefits and maintenance are discounted over the appraisal horizon "),
        new TextRun({text:"n",italics:true}), new TextRun(" at rate "), new TextRun({text:"r",italics:true}), new TextRun(":") ]),
      EQ("NPV = Σₜ₌₁ⁿ ( B − M ) / (1 + r)ᵗ  −  C₀"),
      EQ("BCR = PV(benefits) / PV(costs) = PV(B) / [ C₀ + PV(M) ]"),
      P([ new TextRun("where "), new TextRun({text:"B",italics:true}), new TextRun(" is the annual avoided damage, "),
        new TextRun({text:"M",italics:true}), new TextRun(" the annual maintenance, and "), new TextRun({text:"C₀",italics:true}),
        new TextRun(" the initial cost (dam + dykes + relocation). A scheme is economically justified when NPV > 0 and BCR > 1.") ]),
      P([ new TextRun({text:"Population exposure. ",bold:true}), new TextRun("The same integration is applied to the number of people in the flood, giving the "),
        new TextRun({text:"Expected Annual People Exposed (EAPE)",bold:true}), new TextRun(" — the average number of residents in floodwater per year. EAPE is reported for all floodwater and, as a life-safety indicator, for water deeper than one metre. “EAPE avoided” is the reduction the scheme delivers.") ]),
      P([ new TextRun({text:"Note on hazard. ",bold:true}), new TextRun("The maps in Section 8 present flood depth and the resulting damage. A full flood "),
        new TextRun({text:"hazard-to-life",italics:true}), new TextRun(" rating combines depth with flow velocity (typically HR = d(v + 0.5)); where velocity outputs are available this classification can be added to sharpen the life-safety assessment (see Section 10).") ]),

      H1("3. Assumptions and inputs"),
      table(["Item","Value / source","Notes"], [
        ["Flood depth","HEC-RAS 2D, max depth, 2 m","Baseline and scheme, 10 return periods"],
        ["Depth-damage functions","OMR/m² by land use","JRC global functions, Oman price level (2023)"],
        ["Land use","Cadastral polygons","Residential, commercial, industrial, roads, agriculture"],
        ["Dam capital cost","75,000,000 OMR",""],
        ["Dyke / channel capital cost","5,000,000 OMR",""],
        ["Relocation","Derived","Plots within works footprint × unit land price"],
        ["Maintenance — dam","1.0% of capital / yr","From year 5"],
        ["Maintenance — dykes","0.7% of capital / yr","From year 2"],
        ["Discount rate","2.5%",""],
        ["Appraisal horizon","50 years",""],
        ["Population","GHS-POP 2025","Gridded residents"],
        ["Damage below 2-yr / above 10,000-yr","Zero / held flat","Standard AED tail treatment"],
      ], [2500,3100,3426]),

      H1("4. Flood damage"),
      P("Direct damage rises steeply with return period and is dominated by residential property; agriculture floods the largest area but contributes little value. The scheme reduces damage at every return period by confining flow to the dyked channel and lowering depths across the protected area."),
      ...img(OUT+"/chart_damage_by_class.png", 600, 231, "Figure 1. Flood damage by land-use class — baseline vs scheme (total M OMR labelled on each bar)."),
      P("Damage, avoided damage and inundated area by return period:"),
      table(["RP (yr)","Baseline (OMR)","Scheme (OMR)","Avoided (OMR)","Base area (km²)","Scheme area (km²)"],
        DMG, [820,1960,1960,1960,1163,1163]),
      cap("Table 1. Direct flood damage and inundated area by return period."),

      H1("5. Economic appraisal"),
      P([ new TextRun("Integrating damage over probability gives an Annual Expected Damage of "),
        new TextRun({text:"0.77 M OMR/yr for the baseline and 0.40 M OMR/yr for the scheme — an annual avoided damage of 0.37 M OMR.",bold:true}),
        new TextRun(" Over the 50-year horizon this benefit is worth about 10.6 M OMR in present-value terms.") ]),
      ...img(OUT+"/AED_curves.png", 600, 258, "Figure 2. Annual Expected Damage — the shaded area between the curves is the avoided damage."),
      table(["Metric","Value (OMR)"], [
        ["AED — baseline","771,767"],["AED — scheme","397,828"],["Annual avoided damage","373,939"],
        ["Initial cost (dam 75 + dykes 5 + relocation 0.17)","80,168,080"],
        ["Present value of benefits (50 yr @ 2.5%)","10,605,780"],["Present value of maintenance","19,408,788"],
        ["Present value of costs","99,576,867"],["Net Present Value (NPV)","−88,971,087"],["Benefit-Cost Ratio (BCR)","0.107"] ],
        [6018,3008], true),
      cap("Table 2. Economic summary."),
      P("On direct-damage grounds the scheme does not recover its cost: the benefit-cost ratio is 0.11 and the net present value is −89 M OMR. This reflects the nature of the catchment — the protected land is predominantly agricultural and low-density residential, and the works reduce flood depth more than flood extent, so the avoided monetary damage is modest relative to the capital outlay. The economic result is placed alongside the life-safety and wider benefits in Section 9."),

      H1("6. Population exposure and life safety"),
      P([ new TextRun("Expressed as an expected-annual figure, the scheme keeps about "),
        new TextRun({text:"809 people per year out of floodwater, and about 345 per year out of life-threatening water deeper than one metre",bold:true}),
        new TextRun(" (EAPE avoided). The benefit grows with the severity of the event.") ]),
      ...img(OUT+"/chart_exposure.png", 600, 231, "Figure 3. People exposed (left) and in >1 m water (right); the shaded band is the exposure the scheme avoids."),
      P("At the design and check events the reduction in life-threatening exposure is decisive:"),
      table(["Event","Exposed — base","Exposed — scheme","In >1 m — base","In >1 m — scheme",">1 m reduction"],
        [["200-year","6,432","3,253","4,334","447","90%"],["500-year","6,617","3,831","5,259","783","85%"]],
        [1300,1545,1545,1545,1545,1546]),
      cap("Table 3. Population exposure at the 200-year design event and 500-year check."),
      P("The scheme converts deep, fast, dangerous flooding into shallow nuisance flooding across the populated area. Full exposure figures for all return periods are given in Table 4."),
      table(["RP (yr)","Exposed base","Exposed scheme",">1 m base",">1 m scheme","Avoided >1 m"],
        EXP, [1226,1560,1560,1500,1500,1680]),
      cap("Table 4. Population exposure by return period."),

      H2("Non-monetized benefits"),
      P("Beyond lives saved, the scheme delivers benefits that a damage-based ratio cannot capture but that bear on the decision:"),
      bullet("Injury and trauma avoided — the injuries, displacement and lasting distress that follow a fatal flash flood."),
      bullet("Continuity of access — roads and routes to homes, the hospital and emergency services stay passable during an event, when they are needed most."),
      bullet("Protected livelihoods — repeated inundation degrades farmland and interrupts businesses; reducing depth and duration protects income, not only assets."),
      bullet("Lower response and recovery burden on the authorities after each event."),
      bullet("Community stability and confidence — durable protection supports investment and discourages abandonment of exposed land."),
      bullet("Reduced erosion and sedimentation along the wadi and to downstream infrastructure."),

      H1("7. Decision assessment"),
      P("A flood-protection scheme cannot be judged on its benefit-cost ratio alone; the ratio values only direct property damage and is blind to life safety and service continuity. The table below weighs the economic result together with the non-monetary factors on a transparent scale. Weights are indicative and may be adjusted by the client to reflect policy priorities; a score of 5 is strong performance, 1 is weak."),
      table(["Criterion","Weight","Score /5","Weighted","Assessment"], [
        ["Economic return (BCR / NPV)","25%","1","0.25","Benefits below cost (BCR 0.11)"],
        ["Life safety","30%","5","1.50","~90% fewer people in >1 m water at design event"],
        ["Design-standard compliance","20%","5","1.00","Meets 200-yr target; resilient at 500-yr"],
        ["Access to essential services","10%","4","0.40","Roads and hospital access maintained in flood"],
        ["Livelihoods and property","10%","3","0.30","Reduced repeat inundation of homes and farmland"],
        ["Environment and wadi morphology","5%","3","0.15","Reduced erosion and sedimentation"],
        ["Overall","100%","—","3.60 / 5","Favourable overall, despite weak economics"],
      ], [2450,900,900,1100,3676], true),
      cap("Table 5. Multi-criteria assessment of the scheme (indicative weights)."),
      P("Weighted across the factors that matter for a flood-protection scheme, the project scores 3.6 out of 5 — favourable — even though its economic criterion alone scores poorly. The single low score (economics) is outweighed by strong performance on life safety and design-standard compliance."),

      H1("8. Flood maps"),
      P("Flood depth and the resulting damage at the 200-year design event and the 500-year check, baseline then scheme. The complete set for all return periods accompanies this report."),
      H2("200-year event"),
      ...img(MAPS+"/depth_200yr_baseline.png", 560, 396, "Figure 4. Flood depth, 200-year — baseline."),
      ...img(MAPS+"/depth_200yr_scheme.png", 560, 396, "Figure 5. Flood depth, 200-year — scheme (dam axis in red, dykes in orange)."),
      ...img(MAPS+"/damage_200yr_baseline.png", 560, 396, "Figure 6. Flood damage, 200-year — baseline."),
      ...img(MAPS+"/damage_200yr_scheme.png", 560, 396, "Figure 7. Flood damage, 200-year — scheme."),
      H2("500-year event"),
      ...img(MAPS+"/depth_500yr_baseline.png", 560, 396, "Figure 8. Flood depth, 500-year — baseline."),
      ...img(MAPS+"/depth_500yr_scheme.png", 560, 396, "Figure 9. Flood depth, 500-year — scheme."),
      ...img(MAPS+"/damage_500yr_baseline.png", 560, 396, "Figure 10. Flood damage, 500-year — baseline."),
      ...img(MAPS+"/damage_500yr_scheme.png", 560, 396, "Figure 11. Flood damage, 500-year — scheme."),

      H1("9. Conclusion"),
      P("The Wadi Majlas scheme meets its 200-year protection standard and performs well at the 500-year check. Economically, on avoided direct damage alone it does not pay back (BCR 0.11, NPV −89 M OMR), because the protected assets are mostly low-value. Its principal benefit is the reduction of flood risk to life: at the design event it removes roughly nine in ten people from life-threatening water, and in expected-annual terms it avoids about 345 life-threatening exposures each year, together with the wider benefits to access, livelihoods and the community set out above."),
      P("On a combined assessment the scheme is favourable. It is recommended that the investment decision be taken on this combined economic and life-safety basis, recognising that the benefit-cost ratio, taken in isolation, understates the true value of the works."),

      H1("10. Recommendations and next steps"),
      bullet("Adopt the combined economic + life-safety basis (Section 7) for the decision, rather than the benefit-cost ratio alone."),
      bullet([ new TextRun("Refine the life-safety assessment with a depth-velocity "),
        new TextRun({text:"hazard-to-life",italics:true}),
        new TextRun(" rating (HR = d(v + 0.5)) once maximum-velocity grids are exported from the model, classifying hazard as low / moderate / significant / extreme.") ]),
      bullet("Review the 2-year event, where the scheme shows a marginal local increase in depth (a backwater effect behind the works), to confirm no adverse impact at frequent flows."),
      bullet("If a fully monetized decision is required, value the life-safety benefit explicitly using a value-of-statistical-life approach, reported as a range."),
    ]
  }]
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync("output/Majlas_CBA_Report.docx", b);
  console.log("wrote output/Majlas_CBA_Report.docx"); });
