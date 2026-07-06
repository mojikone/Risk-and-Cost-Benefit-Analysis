const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  Footer, PageNumber, LevelFormat } = require("docx");

const OUT = "output", MAPS = "output/maps";
const CW = 9026; // A4 content width (DXA)
const GREY = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellB = { top: GREY, bottom: GREY, left: GREY, right: GREY };

const img = (p, w, h, cap) => {
  const kids = [ new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 },
    children: [ new ImageRun({ type: "png", data: fs.readFileSync(p),
      transformation: { width: w, height: h },
      altText: { title: cap, description: cap, name: cap } }) ] }) ];
  if (cap) kids.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: [ new TextRun({ text: cap, italics: true, size: 18, color: "666666" }) ] }));
  return kids;
};
const P = (runs, opts={}) => new Paragraph({ spacing: { after: 120 }, ...opts,
  children: (Array.isArray(runs)?runs:[new TextRun(runs)]) });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children:[new TextRun(t)] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children:[new TextRun(t)] });
const bullet = t => new Paragraph({ numbering:{reference:"b",level:0}, spacing:{after:60},
  children:[Array.isArray(t)?null:new TextRun(t)].filter(Boolean).concat(Array.isArray(t)?t:[]) });

// table helper
function table(headers, rows, widths, highlightLast) {
  const mk = (txt, opts={}) => new TableCell({ borders: cellB, width:{size:opts.w,type:WidthType.DXA},
    shading: opts.fill?{fill:opts.fill,type:ShadingType.CLEAR}:undefined,
    margins:{top:60,bottom:60,left:110,right:110},
    children:[new Paragraph({ alignment: opts.al||AlignmentType.LEFT,
      children:[new TextRun({ text:String(txt), bold:!!opts.bold, size:20, color:opts.color })] })] });
  const hr = new TableRow({ tableHeader:true, children: headers.map((h,i)=>
    mk(h,{w:widths[i], bold:true, color:"FFFFFF", fill:"333333", al:i?AlignmentType.RIGHT:AlignmentType.LEFT})) });
  const trs = rows.map((r,ri)=>{ const last = highlightLast && ri===rows.length-1;
    return new TableRow({ children: r.map((c,i)=> mk(c,{w:widths[i],
      al:i?AlignmentType.RIGHT:AlignmentType.LEFT, bold:last, fill:last?"DDEBF7":(ri%2?"F2F2F2":undefined)})) }); });
  return new Table({ width:{size:CW,type:WidthType.DXA}, columnWidths:widths, rows:[hr,...trs] });
}

const AED = [["2","345,808","413,027"],["5","1,011,369","667,876"],["10","2,286,454","1,105,001"],
 ["25","3,513,744","1,352,664"],["50","4,670,209","1,576,424"],["100","5,900,757","1,818,153"],
 ["200","7,456,451","2,093,806"],["500","9,499,861","2,813,500"],["1000","11,019,644","3,789,619"],
 ["10000","14,243,470","8,922,389"]];

const doc = new Document({
  styles: { default:{ document:{ run:{ font:"Arial", size:22 } } }, paragraphStyles:[
    { id:"Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true,
      run:{ size:30, bold:true, font:"Arial", color:"1F3864" }, paragraph:{ spacing:{before:280,after:140}, outlineLevel:0 } },
    { id:"Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true,
      run:{ size:24, bold:true, font:"Arial", color:"2E5496" }, paragraph:{ spacing:{before:180,after:100}, outlineLevel:1 } },
  ]},
  numbering:{ config:[{ reference:"b", levels:[{ level:0, format:LevelFormat.BULLET, text:"•", alignment:AlignmentType.LEFT, style:{ paragraph:{ indent:{ left:460, hanging:260 } } } }] }] },
  sections:[{
    properties:{ page:{ size:{ width:11906, height:16838 }, margin:{ top:1200, right:1440, bottom:1200, left:1440 } } },
    footers:{ default: new Footer({ children:[ new Paragraph({ alignment:AlignmentType.CENTER,
      children:[ new TextRun({ text:"Wadi Majlas Flood Protection — Cost-Benefit Analysis   ·   ", size:16, color:"888888" }),
        new TextRun({ children:[PageNumber.CURRENT], size:16, color:"888888" }) ] }) ] }) },
    children:[
      new Paragraph({ spacing:{after:40}, children:[ new TextRun({ text:"Wadi Majlas Flood Protection", bold:true, size:40, color:"1F3864" }) ] }),
      new Paragraph({ spacing:{after:240}, children:[ new TextRun({ text:"Cost-Benefit Analysis  ·  Quriyat, Oman", size:26, color:"555555" }) ] }),

      H1("1. Purpose"),
      P("This study assesses whether the proposed Wadi Majlas dam-and-channel scheme is worth building. It compares the world with no scheme (baseline) against the world with the dam and dykes in place (scheme), across ten flood return periods from 2 to 10,000 years. For each we estimate flood damage, the annual expected damage, the resulting net present value and benefit-cost ratio, and — separately — how many people are pulled out of harm's way."),
      P("The short answer is uncomfortable: on money alone the scheme does not pay back. But the same scheme is a strong life-safety measure. Both results are reported here so the decision can be made with eyes open."),

      H1("2. Approach"),
      P("Flood depth for every return period and both conditions comes from the HEC-RAS 2D model, exported at 2 m resolution. Depth is combined with land-use-specific depth-damage functions to produce a damage value for each event, which is then integrated over probability to give the Annual Expected Damage (AED). The difference between baseline and scheme AED is the annual avoided damage — the benefit stream. This is discounted over the project horizon and compared with construction, relocation and maintenance costs to give NPV and BCR. Population exposure is estimated the same way, using gridded population instead of damage."),

      H1("3. Inputs"),
      bullet("Flood depth (max) grids — HEC-RAS 2D, 2 m, baseline and scheme, 10 return periods."),
      bullet("Depth-damage functions — OMR/m² by land use (residential, commercial, industrial, roads, agriculture), Oman price level."),
      bullet("Cadastral land-use polygons, classified by use."),
      bullet("Costs — dam 75 M OMR, dykes/channel 5 M OMR, relocation derived from plots within the works footprint; maintenance 1%/yr (dam) and 0.7%/yr (channel)."),
      bullet("Discount rate 2.5%, appraisal horizon 50 years."),
      bullet("Gridded population (GHS-POP 2025) for exposure and life-safety metrics."),

      H1("4. Flood damage"),
      P("Damage rises steeply with return period and is overwhelmingly residential — agriculture floods the largest area but contributes almost nothing in value. The scheme cuts damage at every return period by confining flow to the channel and lowering depths across the protected zone."),
      ...img(OUT+"/chart_damage_by_class.png", 600, 231, "Figure 1. Flood damage by land-use class — baseline vs scheme (total M OMR on each bar)."),
      P("Total direct damage per event (OMR):"),
      table(["Return period (yr)","Baseline","Scheme"], AED, [3009,3009,3008]),

      H1("5. Economics"),
      P([ new TextRun("Integrating these over probability gives an "),
        new TextRun({text:"AED of 0.77 M OMR/yr baseline against 0.40 M OMR/yr with the scheme — an annual avoided damage of about 0.37 M OMR.", bold:true}),
        new TextRun(" Discounted over 50 years this is worth ~10.6 M OMR, well short of the ~80 M OMR of capital and relocation, before maintenance.") ]),
      ...img(OUT+"/AED_curves.png", 600, 258, "Figure 2. Annual Expected Damage — the area between the curves is the avoided damage."),
      table(["Metric","Value (OMR)"], [
        ["AED baseline","771,767"],["AED scheme","397,828"],["Annual avoided damage","373,939"],
        ["Initial cost (dam 75 + channel 5 + relocation 0.17)","80,168,080"],
        ["PV of benefits (50 yr @ 2.5%)","10,605,780"],["PV of maintenance","19,408,788"],
        ["PV of costs","99,576,867"],["NPV","−88,971,087"],["BCR","0.107"]],
        [6018,3008], true),
      P([ new TextRun({text:"On a pure damage basis the scheme returns about 11 fils per rial spent (BCR 0.107; NPV −89 M OMR).", bold:true}),
        new TextRun(" It would need land-and-buildings at risk several times greater than exists, or a far cheaper structure, to break even.") ]),

      H1("6. Population and life safety"),
      P("This is where the scheme earns its keep. It does not simply cut a monetary loss — it removes people from dangerous water. Expressed as an expected-annual figure, the scheme keeps about 809 people a year out of floodwater altogether, and about 345 a year out of life-threatening water deeper than one metre."),
      ...img(OUT+"/chart_exposure.png", 600, 231, "Figure 3. Population exposed (left) and in >1 m life-threatening water (right); orange is the exposure the scheme avoids."),
      P([ new TextRun("At the 100-year event the effect is stark: people in water deeper than one metre fall from "),
        new TextRun({text:"3,564 to 374 — an 89% reduction.", bold:true}),
        new TextRun(" The scheme converts deep, fast, dangerous flooding into shallow nuisance flooding across the populated area.") ]),

      H2("Other non-monetized benefits"),
      P("Lives saved are the headline, but they are not the only benefit that the damage-based ratio cannot see. A decision on this scheme should also weigh:"),
      bullet("Injury and trauma avoided — the physical injuries, and the lasting displacement and psychological toll, that follow a fatal flash flood."),
      bullet("Continuity of access — roads and routes to homes, the hospital and emergency services stay passable during an event, exactly when they are needed most; deep wadi flooding otherwise cuts the town in two."),
      bullet("Protected livelihoods — repeated inundation degrades farmland and interrupts shops and businesses; reducing depth and duration protects income, not just buildings."),
      bullet("Lower response and recovery burden — every avoided major flood is a rescue, clean-up and reconstruction effort the authorities do not have to mount."),
      bullet("Community stability and confidence — durable flood protection supports investment and discourages abandonment of exposed but valuable land."),
      bullet("Reduced erosion and sedimentation along the wadi and to downstream roads, culverts and services."),
      P("None of these sit in the numbers above, and several could be quantified with further study. They all point the same way: the scheme is worth more than its property-damage benefit alone suggests."),

      H1("7. Hazard maps"),
      P("The 200- and 500-year events — depth then damage, baseline then scheme. The full set (all return periods, both conditions) accompanies this report."),
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

      H1("8. Findings and recommendation"),
      P([ new TextRun({text:"Do not defend this scheme on its benefit-cost ratio. ", bold:true}),
        new TextRun("At 0.107 it fails the economic test decisively, and no reasonable change to the discount rate rescues it. The reason is structural: the protected land is mostly low-value agriculture and modest housing, and the works reduce flood depth more than flood extent, so the monetary saving is small.") ]),
      P([ new TextRun({text:"Do weigh it on life safety. ", bold:true}),
        new TextRun("The scheme removes roughly nine in ten people from life-threatening flooding at the design event and avoids around 345 life-threatening exposures a year in expectation. That is the honest case for building it, and a benefit-cost ratio built only on property damage cannot see it.") ]),
      P("Two practical points. First, at the very frequent 2-year event the scheme currently shows slightly worse flooding than baseline — a likely backwater/ponding effect behind the works that should be checked in the hydraulic model. Second, if a monetary decision is unavoidable, the life-safety benefit can be valued explicitly (value-of-statistical-life), but that is a policy choice and is deliberately left out of the figures above."),
      P([ new TextRun({text:"Bottom line: ", bold:true}),
        new TextRun("a poor investment in property terms, a strong one in human terms. The decision should be made on that trade-off, not on the BCR alone.") ]),
    ]
  }]
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync("output/Majlas_CBA_Report.docx", b);
  console.log("wrote output/Majlas_CBA_Report.docx"); });
