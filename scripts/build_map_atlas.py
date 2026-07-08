"""
Assemble every map into a single print-ready A4-landscape PDF atlas:
cover page, Table of Maps (roman pagination), then the maps (arabic pagination),
with running footers and PDF bookmarks.

Output: output/Majlas_Map_Atlas.pdf
"""
import os, datetime
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import config as C

JPG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "atlas_jpg")
JPG_QUALITY = 88   # print-grade; embedded directly as DCTDecode (no re-encode by reportlab)


def as_jpeg(png_path):
    """Convert a map PNG to a print-quality JPEG once, and reuse it."""
    os.makedirs(JPG_DIR, exist_ok=True)
    dst = os.path.join(JPG_DIR, os.path.splitext(os.path.basename(png_path))[0] + ".jpg")
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(png_path):
        with Image.open(png_path) as im:
            im.convert("RGB").save(dst, "JPEG", quality=JPG_QUALITY, optimize=True, dpi=(200, 200))
    return dst

PAGE = landscape(A4)                    # 842 x 595 pt
W, H = PAGE
MAPS = os.path.join(C.OUT_DIR, "maps")
OUT = os.path.join(C.OUT_DIR, "Majlas_Map_Atlas.pdf")

MARGIN_X, MARGIN_TOP, FOOTER_H = 14, 12, 26
TITLE = "Wadi Majlas Flood Protection Dam"
SUBTITLE = "Map Atlas — Techno-Economical Assessment"
FOOT_L = "Wadi Majlas Flood Protection Dam  ·  Map Atlas"

RPS = C.RP_YEARS
COND = (("baseline", "Baseline"), ("scheme", "Scheme"))


def roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s; n -= v
    return out


def sections():
    s = [("General", [("landuse.png", "Land Use Classification"),
                      ("relocation.png", "Relocation — Project Footprint")])]
    for key, label in (("depth", "Flood Depth"), ("hazard", "Flood Hazard"), ("damage", "Flood Damage")):
        items = []
        for rp in RPS:
            for c, cl in COND:
                fn = f"{key}_{rp}yr_{c}.png"
                if os.path.exists(os.path.join(MAPS, fn)):
                    items.append((fn, f"{label} — {rp:,}-year — {cl}"))
        s.append((label, items))
    return s


def footer(cv, left, centre, right=""):
    cv.setFont("Helvetica", 7.5); cv.setFillGray(0.42)
    cv.drawString(MARGIN_X, 11, left)
    cv.drawCentredString(W / 2, 11, centre)
    if right:
        cv.drawRightString(W - MARGIN_X, 11, right)
    cv.setFillGray(0)


def cover(cv):
    cv.setFillGray(0.30); cv.setFont("Helvetica", 11.5)
    cv.drawCentredString(W / 2, H - 58, "Sultanate of Oman")
    cv.drawCentredString(W / 2, H - 76, "Ministry of Agriculture, Fisheries & Water Resources")
    cv.setFillGray(0.45); cv.setFont("Helvetica", 9.5)
    cv.drawCentredString(W / 2, H - 106, "Consultancy Services for Design Review and Supervision of")
    cv.drawCentredString(W / 2, H - 121, "Wadi Majlas Dam in Wilayat Qurayat, Muscat Governorate")

    cv.setFillColorRGB(0.12, 0.22, 0.39); cv.setFont("Helvetica-Bold", 28)
    cv.drawCentredString(W / 2, H - 172, TITLE)
    cv.setFont("Helvetica", 16); cv.setFillGray(0.32)
    cv.drawCentredString(W / 2, H - 200, SUBTITLE)

    cv.setStrokeGray(0.62); cv.setLineWidth(0.8)
    cv.line(W / 2 - 190, H - 218, W / 2 + 190, H - 218)

    cv.setFont("Helvetica", 10); cv.setFillGray(0.40)
    cv.drawCentredString(W / 2, H - 242, "Flood depth · Flood hazard (H1–H6) · Flood damage · Land use · Relocation")
    cv.drawCentredString(W / 2, H - 257, "Baseline and Scheme conditions, 2 to 10,000-year return periods")

    # locator panel: the land-use map, reduced
    key = os.path.join(MAPS, "landuse.png")
    if os.path.exists(key):
        kw = 350.0
        img = ImageReader(as_jpeg(key))
        iw, ih = img.getSize()
        kh = kw * ih / iw
        x0, y0 = (W - kw) / 2, 76
        cv.drawImage(img, x0, y0, kw, kh)
        cv.setStrokeGray(0.75); cv.setLineWidth(0.5); cv.rect(x0, y0, kw, kh)
        cv.setFont("Helvetica-Oblique", 8); cv.setFillGray(0.5)
        cv.drawCentredString(W / 2, y0 - 13, "Study area and land-use classification")

    cv.setFont("Helvetica", 9.5); cv.setFillGray(0.5)
    cv.drawCentredString(W / 2, 42, "Rev 00   ·   " + datetime.date.today().strftime("%B %Y"))
    cv.setFillGray(0)
    cv.showPage()


def contents(cv, secs, first_map_page):
    """Draw the Table of Maps; returns number of pages used."""
    entries = []
    page = first_map_page
    for name, items in secs:
        entries.append(("H", name, None))
        for _, title in items:
            entries.append(("E", title, page)); page += 1

    col_w = (W - 2 * MARGIN_X - 30) / 2
    top, bottom = H - 96, 44
    lead = 13.2
    pages = 0
    i = 0
    while i < len(entries):
        pages += 1
        cv.setFont("Helvetica-Bold", 17); cv.setFillColorRGB(0.12, 0.22, 0.39)
        cv.drawString(MARGIN_X + 6, H - 58, "Table of Maps" + ("  (cont.)" if pages > 1 else ""))
        cv.setFillGray(0)
        for col in range(2):
            x = MARGIN_X + 6 + col * (col_w + 30)
            y = top
            while i < len(entries) and y > bottom:
                kind, text, pg = entries[i]
                if kind == "H":
                    if y - lead * 1.6 < bottom:      # keep header with content
                        break
                    y -= 6
                    cv.setFont("Helvetica-Bold", 9.6); cv.setFillColorRGB(0.18, 0.33, 0.59)
                    cv.drawString(x, y, text.upper()); cv.setFillGray(0)
                    y -= lead
                else:
                    cv.setFont("Helvetica", 8.6)
                    num = str(pg)
                    tw = cv.stringWidth(text, "Helvetica", 8.6)
                    nw = cv.stringWidth(num, "Helvetica", 8.6)
                    cv.drawString(x, y, text)
                    cv.drawRightString(x + col_w, y, num)
                    gap = col_w - tw - nw - 8
                    if gap > 6:
                        cv.setFillGray(0.62)
                        dots = "." * int(gap / cv.stringWidth(".", "Helvetica", 8.6))
                        cv.drawString(x + tw + 4, y, dots)
                        cv.setFillGray(0)
                    y -= lead
                i += 1
        footer(cv, FOOT_L, roman(pages), "Table of Maps")
        cv.showPage()
    return pages


def draw_map(cv, png):
    path = as_jpeg(png)                 # JPEG is passed straight through as DCTDecode
    img = ImageReader(path)
    iw, ih = img.getSize()
    avail_w = W - 2 * MARGIN_X
    avail_h = H - MARGIN_TOP - FOOTER_H
    scale = min(avail_w / iw, avail_h / ih)
    w, h = iw * scale, ih * scale
    cv.drawImage(img, (W - w) / 2, FOOTER_H + (avail_h - h) / 2, w, h,
                 preserveAspectRatio=True, anchor="c")


def main():
    secs = sections()
    total = sum(len(v) for _, v in secs)
    cv = canvas.Canvas(OUT, pagesize=PAGE)
    cv.setPageCompression(1)
    cv.setTitle("Wadi Majlas Flood Protection Dam — Map Atlas")
    cv.setAuthor("Renardet"); cv.setSubject("Techno-Economical Assessment — Map Atlas")

    cover(cv)
    contents(cv, secs, first_map_page=1)

    page = 1
    for si, (name, items) in enumerate(secs):
        first = True
        for fn, title in items:
            draw_map(cv, os.path.join(MAPS, fn))
            footer(cv, FOOT_L, str(page), name)
            # distinct destination names: reportlab keys outline titles by destination
            if first:
                cv.bookmarkPage(f"sec{si}")
                cv.addOutlineEntry(name, f"sec{si}", level=0, closed=False)
                first = False
            cv.bookmarkPage(f"p{page}")
            cv.addOutlineEntry(title, f"p{page}", level=1)
            cv.showPage()
            page += 1

    cv.showOutline()
    cv.save()
    size = os.path.getsize(OUT) / 1e6
    print(f"wrote {OUT}")
    print(f"  {total} maps | cover + table of maps + {total} map pages | {size:.1f} MB")


if __name__ == "__main__":
    main()
