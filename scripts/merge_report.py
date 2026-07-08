"""
Splice the generated report body into the client template `sample 1.docx`, keeping the
template's cover page, running header/footer, styles and numbering.

  cover (sample section 1)  +  our body  +  sample's header1/footer1 sectPr

Images from the body are copied into the template package with fresh relationship ids.
The header and cover title are re-worded for this report.
Output: output/Techno-Economical Assessment Report.docx
"""
import os, re, shutil, zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(BASE, "Data", "DOC", "sample 1.docx")
BODY = os.path.join(BASE, "build", "body.docx")
OUT = os.path.join(BASE, "output", "Techno-Economical Assessment Report.docx")

OLD_TITLE = "Hydrology Report"
NEW_TITLE = "Techno-Economical Assessment Report"

NS = {  # namespaces docx-js content may rely on
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def read_all(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def main():
    tpl, body = read_all(TPL), read_all(BODY)

    tdoc = tpl["word/document.xml"].decode("utf-8")
    bdoc = body["word/document.xml"].decode("utf-8")

    # ---- template: root tag, cover, and the sectPr that carries header1/footer1
    root_end = tdoc.index(">", tdoc.index("<w:document")) + 1
    root_tag = tdoc[:root_end]
    for pfx, uri in NS.items():
        if f'xmlns:{pfx}=' not in root_tag:
            root_tag = root_tag[:-1] + f' xmlns:{pfx}="{uri}">'

    tb0 = tdoc.index("<w:body>") + len("<w:body>")
    tb1 = tdoc.rindex("</w:body>")
    tbody = tdoc[tb0:tb1]

    # cover = everything up to and including the paragraph holding the first sectPr
    s = tbody.index("<w:sectPr")
    e = tbody.index("</w:sectPr>", s) + len("</w:sectPr>")
    cover = tbody[: tbody.index("</w:p>", e) + len("</w:p>")]

    # main sectPr = the one referencing header1 (rId16)
    main_sect = None
    for m in re.finditer(r"<w:sectPr.*?</w:sectPr>", tbody, re.S):
        if 'r:id="rId16"' in m.group(0):
            main_sect = m.group(0)
            break
    if main_sect is None:
        raise SystemExit("could not find the header1 sectPr in the template")

    # ---- body content (strip its trailing sectPr)
    bb0 = bdoc.index("<w:body>") + len("<w:body>")
    bb1 = bdoc.rindex("</w:body>")
    bcontent = bdoc[bb0:bb1]
    k = bcontent.rfind("<w:sectPr")
    if k != -1:
        bcontent = bcontent[:k]

    # ---- copy body media, remap relationship ids
    brels = body["word/_rels/document.xml.rels"].decode("utf-8")
    rid_target = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', brels))

    trels = tpl["word/_rels/document.xml.rels"].decode("utf-8")
    used = set(re.findall(r'Id="(rId\d+)"', trels))
    next_id = max(int(x[3:]) for x in used) + 1

    out = dict(tpl)
    new_rels = []
    for old_rid, target in rid_target.items():
        if not target.startswith("media/"):
            continue
        if f'r:embed="{old_rid}"' not in bcontent and f'r:id="{old_rid}"' not in bcontent:
            continue
        src = "word/" + target
        if src not in body:
            continue
        newname = "media/cba_" + os.path.basename(target)
        out["word/" + newname] = body[src]
        new_rid = f"rId{next_id}"; next_id += 1
        new_rels.append(f'<Relationship Id="{new_rid}" Type="http://schemas.openxmlformats.org/'
                        f'officeDocument/2006/relationships/image" Target="{newname}"/>')
        bcontent = bcontent.replace(f'r:embed="{old_rid}"', f'r:embed="{new_rid}"')

    # drop the template's chart (its body content is gone; its rels point off-machine)
    for name in [n for n in out if n.startswith("word/charts/")]:
        del out[name]
    trels = re.sub(r'<Relationship [^>]*Target="charts/[^"]*"[^>]*/>', "", trels)

    trels = trels.replace("</Relationships>", "".join(new_rels) + "</Relationships>")
    out["word/_rels/document.xml.rels"] = trels.encode("utf-8")

    # ---- content types: drop chart overrides; ensure png/jpeg defaults
    ct = out["[Content_Types].xml"].decode("utf-8")
    ct = re.sub(r'<Override [^>]*PartName="/word/charts/[^"]*"[^>]*/>', "", ct)
    for ext, mime in (("png", "image/png"), ("jpeg", "image/jpeg")):
        if f'Extension="{ext}"' not in ct:
            ct = ct.replace("</Types>", f'<Default Extension="{ext}" ContentType="{mime}"/></Types>')
    out["[Content_Types].xml"] = ct.encode("utf-8")

    # ---- clean a schema nit inherited from the template
    if "word/numbering.xml" in out:
        nb = out["word/numbering.xml"].decode("utf-8").replace(' w:hint="cs"', "")
        out["word/numbering.xml"] = nb.encode("utf-8")

    # ---- assemble document
    doc = root_tag + "<w:body>" + cover + bcontent + main_sect + "</w:body></w:document>"
    out["word/document.xml"] = doc.encode("utf-8")

    # ---- re-word header + cover title
    for part in ("word/header1.xml", "word/header2.xml", "word/document.xml"):
        if part in out:
            t = out[part].decode("utf-8").replace(f">{OLD_TITLE}<", f">{NEW_TITLE}<")
            out[part] = t.encode("utf-8")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in out.items():
            z.writestr(name, data)
    print("wrote", OUT)
    print(f"  cover kept ({cover.count('<w:drawing')} images), body images remapped: {len(new_rels)}")


if __name__ == "__main__":
    main()
