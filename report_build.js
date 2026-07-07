const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  Footer, PageNumber, LevelFormat } = require("docx");

const OUT = "output", MAPS = "output/maps", EQ = "output/eq";
const CW = 9026;
const GREY = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellB = { top: GREY, bottom: GREY, left: GREY, right: GREY };

const img = (p, w, h, capt) => {
  const k = [ new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 },
    children: [ new ImageRun({ type: "png", data: fs.readFileSync(p), transformation: { width: w, height: h },
      altText: { title: capt||"", description: capt||"", name: "img" } }) ] }) ];
  if (capt) k.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: [ new TextRun({ text: capt, italics: true, size: 18, color: "666666" }) ] }));
  return k;
};
const eq = (name, w, h) => new Paragraph({ alignment: AlignmentType.CENTER, spacing:{before:60,after:120},
  children:[ new ImageRun({ type:"png", data:fs.readFileSync(`${EQ}/eq_${name}.png`),
    transformation:{width:w,height:h}, altText:{title:name,description:name,name:name} }) ] });
const P = (runs, opts={}) => new Paragraph({ spacing: { after: 120 }, ...opts,
  children: (Array.isArray(runs)?runs:[new TextRun(runs)]) });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children:[new TextRun(t)] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children:[new TextRun(t)] });
const bullet = t => new Paragraph({ numbering:{reference:"b",level:0}, spacing:{after:60},
  children:[Array.isArray(t)?null:new TextRun(t)].filter(Boolean).concat(Array.isArray(t)?t:[]) });
const cap = t => new Paragraph({ alignment:AlignmentType.CENTER, spacing:{before:40,after:160},
  children:[ new TextRun({ text:t, italics:true, size:18, color:"666666" }) ] });

function table(headers, rows, widths, hiLast, hiRow) {
  const mk = (txt, o={}) => new TableCell({ borders: cellB, width:{size:o.w,type:WidthType.DXA},
    shading: o.fill?{fill:o.fill,type:ShadingType.CLEAR}:undefined, margins:{top:50,bottom:50,left:100,right:100},
    children:[new Paragraph({ alignment:o.al||AlignmentType.LEFT, children:[new TextRun({ text:String(txt), bold:!!o.bold, size:19, color:o.color })] })] });
  const hr = new TableRow({ tableHeader:true, children: headers.map((h,i)=>
    mk(h,{w:widths[i], bold:true, color:"FFFFFF", fill:"333333", al:i?AlignmentType.RIGHT:AlignmentType.LEFT})) });
  const trs = rows.map((r,ri)=>{ const last=(hiLast&&ri===rows.length-1)||(hiRow!=null&&ri===hiRow);
    return new TableRow({ children: r.map((c,i)=> mk(c,{w:widths[i], al:i?AlignmentType.RIGHT:AlignmentType.LEFT,
      bold:last, fill:last?"DDEBF7":(ri%2?"F2F2F2":undefined)})) }); });
  return new Table({ width:{size:CW,type:WidthType.DXA}, columnWidths:widths, rows:[hr,...trs] });
}

const DMG = [["2","430,603","413,027","17,576","3.21","1.98"],["5","1,011,369","667,876","343,493","4.72","2.87"],
 ["10","2,286,454","1,105,001","1,181,453","6.09","3.73"],["25","3,513,744","1,352,664","2,161,081","6.80","4.09"],
 ["50","4,670,209","1,576,424","3,093,785","7.14","4.39"],["100","5,900,757","1,818,152","4,082,605","7.39","4.68"],
 ["200","7,456,451","2,093,806","5,362,645","7.57","4.96"],["500","9,499,861","2,813,500","6,686,361","7.75","5.73"],
 ["1000","11,019,644","3,789,619","7,230,025","7.88","6.32"],["10000","14,243,470","8,922,389","5,321,080","8.12","7.76"]];
const HAZ = [["5","605","110","82%"],["10","1,832","212","88%"],["25","2,805","303","89%"],["50","3,581","378","89%"],
 ["100","4,498","432","90%"],["200","5,222","510","90%"],["500","n/a","967","—"],["1000","6,203","1,749","72%"],["10000","6,512","4,892","25%"]];

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
      P([ new TextRun({text:"Direct damage per event. ",bold:true}), new TextRun("For a return period T, damage is summed over every flooded raster cell, where fᶜ(h) is the depth-damage value (OMR/m²) for land-use class c at depth h, and a is the cell area:") ]),
      eq("damage",165,51),
      P([ new TextRun({text:"Annual Expected Damage (AED). ",bold:true}), new TextRun("Damage is integrated over the annual exceedance probability p = 1/T by the trapezoidal rule; the avoided damage is the scheme benefit:") ]),
      eq("aed",474,65), eq("avoided",452,32),
      P([ new TextRun({text:"Net Present Value and Benefit-Cost Ratio. ",bold:true}), new TextRun("Benefits B (avoided damage) and maintenance M are discounted over horizon n at rate r; C₀ is the initial cost (dam + dykes + relocation):") ]),
      eq("npv",250,66), eq("bcr",318,63),
      P([ new TextRun({text:"Population exposure. ",bold:true}), new TextRun("The same integration applied to the number of people in the flood N(p) gives the Expected Annual People Exposed (EAPE); “EAPE avoided” is the scheme’s reduction:") ]),
      eq("eape",196,51),
      P([ new TextRun({text:"Flood hazard. ",bold:true}), new TextRun("Hazard-to-life is derived in the hydraulic model from depth d and velocity v as a hazard rating and classified H1–H6 per the Australian flood hazard vulnerability curves (Smith et al. 2014; AIDR Guideline 7-3):") ]),
      eq("hr",229,32),

      H1("3. Assumptions and inputs"),
      table(["Item","Value / source","Notes"], [
        ["Flood depth & hazard","HEC-RAS 2D, 2 m","Max depth and Australian hazard (H1–H6), baseline and scheme, 10 RPs"],
        ["Depth-damage functions","OMR/m² by land use","JRC global functions, Oman price level (2023)"],
        ["Land use","Cadastral polygons","Residential, commercial, industrial, roads, agriculture"],
        ["Dam capital cost","75,000,000 OMR",""],["Dyke / channel capital cost","5,000,000 OMR",""],
        ["Relocation","Derived","Plots within works footprint × unit land price"],
        ["Maintenance","Dam 1.0%/yr (yr 5+); dykes 0.7%/yr (yr 2+)","of respective capital"],
        ["Discount rate","4.2%",""],["Appraisal horizon","50 years",""],
        ["Population","GHS-POP 2025","Gridded residents"],
      ], [2500,3100,3426]),

      H1("4. Flood damage"),
      P("Direct damage rises steeply with return period and is dominated by residential property; agriculture floods the largest area but contributes little value. The scheme reduces damage at every return period by confining flow to the dyked channel and lowering depths across the protected area."),
      ...img(OUT+"/chart_damage_by_class.png", 600, 231, "Figure 1. Flood damage by land-use class — baseline vs scheme (total M OMR labelled on each bar)."),
      table(["RP (yr)","Baseline (OMR)","Scheme (OMR)","Avoided (OMR)","Base area (km²)","Scheme area (km²)"], DMG, [820,1960,1960,1960,1163,1163]),
      cap("Table 1. Direct flood damage and inundated area by return period."),

      H1("5. Economic appraisal"),
      P([ new TextRun("Integrating damage over probability gives an Annual Expected Damage of "),
        new TextRun({text:"0.77 M OMR/yr baseline and 0.40 M OMR/yr with the scheme — an annual avoided damage of 0.37 M OMR.",bold:true}),
        new TextRun(" At a 4.2% discount rate over 50 years this benefit is worth about 7.8 M OMR in present value.") ]),
      ...img(OUT+"/AED_curves.png", 600, 258, "Figure 2. Annual Expected Damage — the shaded area between the curves is the avoided damage."),
      table(["Metric","Value (OMR)"], [
        ["AED — baseline","771,767"],["AED — scheme","397,828"],["Annual avoided damage","373,939"],
        ["Initial cost (dam 75 + dykes 5 + relocation 0.17)","80,168,080"],
        ["Present value of benefits (50 yr @ 4.2%)","7,765,253"],["Present value of maintenance","13,558,148"],
        ["Present value of costs","93,726,228"],["Net Present Value (NPV)","−85,960,975"],["Benefit-Cost Ratio (BCR)","0.083"] ],
        [6018,3008], true),
      cap("Table 2. Economic summary (discount rate 4.2%)."),
      P("On direct-damage grounds the scheme does not recover its cost: the benefit-cost ratio is 0.08 and the net present value is −86 M OMR. This reflects the nature of the catchment — the protected land is predominantly agricultural and low-density residential, and the works reduce flood depth more than flood extent, so the avoided monetary damage is modest relative to the capital outlay. The economic result is placed alongside the flood-hazard and life-safety findings in Section 7."),

      H1("6. Flood hazard and population safety"),
      P("Flood hazard-to-life is classified using the Australian combined depth-velocity vulnerability curves. The classes escalate from H1 (generally safe) to H6 (all buildings vulnerable to failure); from H4 upward, floodwater is unsafe for people."),
      table(["Class","Vulnerability"], [
        ["H1","Generally safe for people, vehicles and buildings"],
        ["H2","Unsafe for small vehicles"],
        ["H3","Unsafe for vehicles, children and the elderly"],
        ["H4","Unsafe for vehicles and people"],
        ["H5","Unsafe for vehicles and people; buildings vulnerable to structural damage"],
        ["H6","Unsafe for all; all building types vulnerable to failure"] ], [1400,7626]),
      cap("Table 3. Australian flood hazard classification (AIDR Guideline 7-3)."),
      P([ new TextRun("Counting the residents standing in hazard unsafe for people (H4 and above), the scheme is decisive. At the "),
        new TextRun({text:"200-year design event it reduces people in unsafe hazard from 5,222 to 510 — a 90% reduction",bold:true}),
        new TextRun("; the effect holds across the frequent and design range and only narrows at extreme events beyond the design standard.") ]),
      table(["RP (yr)","Baseline (H4+)","Scheme (H4+)","Reduction"], HAZ, [1600,2476,2475,2475], false, 5),
      cap("Table 4. People in flood hazard unsafe for people (H4+), baseline vs scheme. The 200-year row is the design target; 500-year baseline hazard is pending re-export."),
      P("Considering all floodwater, the scheme keeps about 809 people per year out of the flood and about 345 per year out of water deeper than one metre in expected-annual terms."),
      ...img(OUT+"/chart_exposure.png", 600, 231, "Figure 3. People exposed (left) and in >1 m water (right); the shaded band is the exposure the scheme avoids."),

      H2("Non-monetized benefits"),
      P("Beyond lives saved, the scheme delivers benefits that a damage-based ratio cannot capture but that bear on the decision:"),
      bullet("Injury and trauma avoided — the injuries, displacement and lasting distress that follow a fatal flash flood."),
      bullet("Continuity of access — roads and routes to homes, the hospital and emergency services stay passable during an event, when they are needed most."),
      bullet("Protected livelihoods — repeated inundation degrades farmland and interrupts businesses; reducing depth and duration protects income, not only assets."),
      bullet("Lower response and recovery burden on the authorities after each event."),
      bullet("Community stability and confidence — durable protection supports investment and discourages abandonment of exposed land."),
      bullet("Reduced erosion and sedimentation along the wadi and to downstream infrastructure."),

      H1("7. Decision assessment"),
      P("A flood-protection scheme cannot be judged on its benefit-cost ratio alone; the ratio values only direct property damage and is blind to loss of life and service continuity. The table below weighs the economic result together with the flood-hazard and non-monetary factors on a transparent scale. Weights are indicative and may be adjusted by the client; a score of 5 is strong performance, 1 is weak."),
      table(["Criterion","Weight","Score /5","Weighted","Assessment"], [
        ["Economic return (BCR / NPV)","25%","1","0.25","Benefits below cost (BCR 0.08)"],
        ["Life safety (flood hazard)","30%","5","1.50","People in unsafe hazard (H4+) cut ~90% at design event"],
        ["Design-standard compliance","20%","5","1.00","Meets 200-yr target; resilient at 500-yr"],
        ["Access to essential services","10%","4","0.40","Roads and hospital access maintained in flood"],
        ["Livelihoods and property","10%","3","0.30","Reduced repeat inundation of homes and farmland"],
        ["Environment and wadi morphology","5%","3","0.15","Reduced erosion and sedimentation"],
        ["Overall","100%","—","3.60 / 5","Favourable overall, despite weak economics"] ],
        [2450,900,900,1100,3676], true),
      cap("Table 5. Multi-criteria assessment of the scheme (indicative weights)."),
      P("Weighted across the factors that matter for a flood-protection scheme, the project scores 3.6 out of 5 — favourable — even though its economic criterion alone scores poorly. The single low economic score is outweighed by strong performance on flood-hazard reduction to life and design-standard compliance."),

      H1("8. Flood maps"),
      P("Flood depth, direct damage and Australian flood hazard at the 200-year design event and the 500-year check, baseline then scheme. On the hazard maps the dam axis is shown in white and the dykes in black. The complete set for all return periods accompanies this report."),
      H2("200-year event (design target)"),
      ...img(MAPS+"/depth_200yr_baseline.png", 560, 396, "Figure 4. Flood depth, 200-year — baseline."),
      ...img(MAPS+"/depth_200yr_scheme.png", 560, 396, "Figure 5. Flood depth, 200-year — scheme."),
      ...img(MAPS+"/hazard_200yr_baseline.png", 560, 396, "Figure 6. Flood hazard (H1–H6), 200-year — baseline."),
      ...img(MAPS+"/hazard_200yr_scheme.png", 560, 396, "Figure 7. Flood hazard (H1–H6), 200-year — scheme."),
      ...img(MAPS+"/damage_200yr_baseline.png", 560, 396, "Figure 8. Flood damage, 200-year — baseline."),
      ...img(MAPS+"/damage_200yr_scheme.png", 560, 396, "Figure 9. Flood damage, 200-year — scheme."),
      H2("500-year event (control)"),
      ...img(MAPS+"/depth_500yr_baseline.png", 560, 396, "Figure 10. Flood depth, 500-year — baseline."),
      ...img(MAPS+"/depth_500yr_scheme.png", 560, 396, "Figure 11. Flood depth, 500-year — scheme."),
      ...img(MAPS+"/hazard_500yr_scheme.png", 560, 396, "Figure 12. Flood hazard (H1–H6), 500-year — scheme."),
      ...img(MAPS+"/damage_500yr_scheme.png", 560, 396, "Figure 13. Flood damage, 500-year — scheme."),

      H1("9. Conclusion"),
      P("The Wadi Majlas scheme meets its 200-year protection standard and performs well at the 500-year check. Economically, on avoided direct damage alone it does not pay back (BCR 0.08, NPV −86 M OMR), because the protected assets are predominantly low-value. Its principal benefit is the reduction of flood risk to life: at the design event it removes about 90% of the residents standing in floodwater that is unsafe for people, together with the wider benefits to access, livelihoods and the community set out above."),
      P("On a combined assessment the scheme is favourable. It is recommended that the investment decision be taken on this combined economic and life-safety basis, recognising that the benefit-cost ratio, taken in isolation, understates the value of the works."),

      H1("10. Recommendations and next steps"),
      bullet("Adopt the combined economic + flood-hazard basis (Section 7) for the decision, rather than the benefit-cost ratio alone."),
      bullet("Re-export the 500-year baseline hazard grid, which was written without georeferencing, to complete the 500-year control set."),
      bullet("If a fully monetized decision is required, value the life-safety benefit explicitly using a value-of-statistical-life approach, reported as a range."),
    ]
  }]
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync("output/Majlas_CBA_Report.docx", b);
  console.log("wrote output/Majlas_CBA_Report.docx"); });
