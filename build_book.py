#!/usr/bin/env python3
"""Builds the dedicated book layout from the arrange board's book lane.

ONE book, not the two the sent agreement described. Scope settled with the
client 2026-08-07; the reasons are client-private and live in the private
abba-dashboard repo, not here. This repo is public.

THE SEQUENCE IS THE LANE'S ORDER. A book is an order, not a set, so the frames
come out of _work/arrangement_kw.json in exactly the order they sit in the book
lane. Reordering happens on the arrange board, not here.

CONSTRAINT ON FILE (2026-08-07): non-identifiable kids only. This script cannot
see faces and does not pretend to. It reports the constraint next to the count
so the claim is never made on the machine's behalf; the lane's contents are the
owner's call and his alone.

The book's recipients are never named on any surface in this repo, filenames
included. They are named only in private docs.

    python3 build_book.py              preview PDF, 150 DPI, spreads
    python3 build_book.py --press      300 DPI single pages for the lab

Cropping is honest: a frame whose proportions do not match the page is matted
rather than cropped past ~12 percent, because a donor book that quietly amputates
a composition is worse than one with a margin.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_delivery import frame_no

ARR = os.path.join(HERE, "_work", "arrangement_kw.json")
MASTER = os.path.expanduser("~/Abba_Photo/Kwood_827")   # THE master set since the 8/27
                                  # consolidation; superseded staging lives in
                                  # kingswood/_archive_pre827_staging
OUTDIR = os.path.join(HERE, "book")
BOOK_GROUP = "The book"

import millers                    # the press spec, shared and checkable

SIZE_KEY = millers.DEFAULT_SIZE   # "12x8". Any key in millers.SIZES.
PAGE_IN = millers.SIZES[SIZE_KEY]["trim"]   # trim, inches. Bleed is added on top.

# The cover, added 2026-08-26 on Noah's word ("You can do a cover, do a cover")
# after he released the Codex reservation. COVER_FRAME is the frame number the
# cover wears; None falls back to the typographic cover this file shipped with.
# The face is the camp's own, per the client-brand rule: Raleway, from the
# hub's fonts folder, SIL OFL. The woff2 in that folder cannot be loaded by
# Pillow, so the same family is kept alongside as TTF.
COVER_FRAME = 312
COVER_FACE = os.path.join(HERE, "fonts", "Raleway-%d.ttf")
COVER_SCRIM = 0.20                # ink laid over the cover frame so type reads.
                                  # Tiled at 0.20 / 0.30 / 0.42 on 2026-08-26:
                                  # 0.42 flattened the greens and shifted the
                                  # whole frame blue. 0.20 keeps the picture a
                                  # picture and the type still carries, because
                                  # it sits over road and grass rather than sky.
GROUND = (243, 241, 236)          # #F3F1EC, the camp's warm white
INK = (6, 42, 64)                 # #062A40, the camp's ground colour as ink
ACCENT = (219, 58, 0)             # #DB3A00
MARGIN = 0.06                     # of the short edge, for matted frames
MAX_CROP = 0.12                   # crop more of a frame than this and it gets matted
MATTE_ALL = True                  # Noah, 2026-08-23: "have book layout matte all
                                  # frames." Nothing bleeds. Every frame sits inside
                                  # the margin on the camp's warm white, whole, at
                                  # its own proportions. Set False to restore the
                                  # bleed-under-12-percent rule.
FONT = "/System/Library/Fonts/Avenir Next.ttc"

# HERO FACING ITS B-ROLL, Jodi's idea via Noah 2026-08-26: "the artful one is on
# the left and then a montage of the other on the right."
# hero frame number -> the frames montaged opposite it, 1 to 6.
# EMPTY BY DEFAULT and it must stay that way until Noah assigns pairs, because
# nobody but him decides which frames belong together. Codex caught on
# 2026-08-27 that montage() had no caller at all: the function shipped and was
# never wired, so the feature existed only in the commit message.
# The hero must be in the book lane; its montage frames need not be.
MONTAGE_SPREADS = {}


def lane():
    a = json.load(open(ARR))
    by_name = {g["name"]: g["frames"] for g in a["groups"]}
    if BOOK_GROUP not in by_name:
        sys.exit(f"No '{BOOK_GROUP}' lane in {ARR}.\n"
                 f"Run build_arrange.py, fill the lane, paste the export back.")
    # The aside lane fences the delivery pool, which is a different deliverable.
    # A frame can be wrong for the camp's library and right for the book, so the
    # book's lane wins and the overlap is reported rather than enforced.
    aside = set(a.get("aside", []))
    seq = list(by_name[BOOK_GROUP])
    return seq, [n for n in seq if n in aside]


def sources():
    return {frame_no(f): os.path.join(MASTER, f)
            for f in os.listdir(MASTER) if f.lower().endswith(".jpg")}


def fit(im, box):
    """Cover-crop to the box, or mat it if that would cut too much away."""
    from PIL import Image
    bw, bh = box
    scale = max(bw / im.width, bh / im.height)
    kept = (bw / (im.width * scale)) * (bh / (im.height * scale))
    if 1 - kept > MAX_CROP:
        return None, 1 - kept
    w, h = round(im.width * scale), round(im.height * scale)
    im = im.resize((w, h), Image.LANCZOS)
    return im.crop(((w - bw) // 2, (h - bh) // 2,
                    (w - bw) // 2 + bw, (h - bh) // 2 + bh)), 1 - kept


def matted(im, page):
    from PIL import Image
    pw, ph = page
    m = round(min(pw, ph) * MARGIN)
    box = (pw - 2 * m, ph - 2 * m)
    c = im.copy()
    c.thumbnail(box, Image.LANCZOS)
    out = Image.new("RGB", page, GROUND)
    out.paste(c, ((pw - c.width) // 2, (ph - c.height) // 2))
    return out


def pair(a, b, page):
    """Two portraits facing each other on one landscape page."""
    from PIL import Image
    pw, ph = page
    m = round(min(pw, ph) * MARGIN)
    gut = round(m * 0.9)
    cell = ((pw - 2 * m - gut) // 2, ph - 2 * m)
    out = Image.new("RGB", page, GROUND)
    for i, im in enumerate((a, b)):
        c = im.copy()
        c.thumbnail(cell, Image.LANCZOS)
        x = m + i * (cell[0] + gut) + (cell[0] - c.width) // 2
        out.paste(c, (x, m + (cell[1] - c.height) // 2))
    return out


def montage(frames, page, cols=None):
    """A grid of supporting frames on one page, to face a hero on the other.

    Jodi's idea, 2026-08-26, in Noah's words: "the artful one is on the left and
    then a montage of the other on the right." The girl reading the plaques
    faces the plaques themselves; the waterfront hero faces the waterfront.

    The grid holds its own margin rather than inheriting MATTE_ALL's, because a
    matte around each cell plus a matte around the page reads as a mistake. One
    outer margin, one gutter, cells cover-cropped to a common shape so the grid
    is a grid and not a ragged wall.
    """
    from PIL import Image
    pw, ph = page
    n = len(frames)
    if n == 0:
        return Image.new("RGB", page, GROUND)
    cols = cols or (1 if n == 1 else 2 if n <= 4 else 3)
    rows = -(-n // cols)
    m = round(min(pw, ph) * MARGIN)
    gut = round(m * 0.55)
    cw = (pw - 2 * m - gut * (cols - 1)) // cols
    chh = (ph - 2 * m - gut * (rows - 1)) // rows
    out = Image.new("RGB", page, GROUND)
    for i, im in enumerate(frames):
        s = max(cw / im.width, chh / im.height)
        w, h = round(im.width * s), round(im.height * s)
        cell = im.resize((w, h), Image.LANCZOS).crop(
            ((w - cw) // 2, (h - chh) // 2, (w - cw) // 2 + cw, (h - chh) // 2 + chh))
        x = m + (i % cols) * (cw + gut)
        y = m + (i // cols) * (chh + gut)
        out.paste(cell, (x, y))
    return out


def on_bleed(sheet, canvas):
    """Place a trim-sized sheet on the full bleed canvas.

    Every page this builder makes carries the camp's ground to its edge, because
    MATTE_ALL is on, so extending that ground into the bleed is exact rather
    than invented: the trimmer cuts through flat colour and cannot cut into the
    picture. A page built to fill the bleed (MATTE_ALL off) arrives here already
    canvas-sized and passes straight through.
    """
    from PIL import Image
    if sheet.size == canvas:
        return sheet
    out = Image.new("RGB", canvas, GROUND)
    out.paste(sheet, ((canvas[0] - sheet.width) // 2,
                      (canvas[1] - sheet.height) // 2))
    return out


def photo_cover(im, canvas, dpi, title, sub):
    """A cover the camp would recognise: its own photograph, its own typeface.

    The frame fills the whole canvas including bleed, so the wrap has stock to
    be trimmed and turned. Text sits inside Miller's safe inset measured from
    the TRIM edge, not the canvas edge, which is the distinction that puts type
    off the fold instead of into it.
    """
    from PIL import Image, ImageDraw, ImageFont
    cw, ch = canvas
    scale = max(cw / im.width, ch / im.height)
    w, h = round(im.width * scale), round(im.height * scale)
    art = im.resize((w, h), Image.LANCZOS).crop(
        ((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch))

    # A scrim, not a wash: the picture stays a picture, the type stays legible.
    veil = Image.new("RGB", canvas, INK)
    art = Image.blend(art, veil, COVER_SCRIM)

    d = ImageDraw.Draw(art)
    inset = millers.bleed_px(dpi) + millers.safe_px(dpi)
    big = round(ch * 0.072)
    small = round(ch * 0.021)
    f1 = ImageFont.truetype(COVER_FACE % 800, big)
    f2 = ImageFont.truetype(COVER_FACE % 400, small)
    y = ch - inset - big - round(small * 3.2)
    d.text((inset, y), title, font=f1, fill=GROUND)
    rule_y = y + round(big * 1.28)
    d.line([(inset, rule_y), (inset + round(cw * 0.055), rule_y)],
           fill=ACCENT, width=max(3, round(ch * 0.0045)))
    d.text((inset, rule_y + round(small * 0.9)), sub, font=f2, fill=GROUND)
    return art


def title_page(page, n):
    from PIL import Image, ImageDraw, ImageFont
    out = Image.new("RGB", page, GROUND)
    d = ImageDraw.Draw(out)
    pw, ph = page
    big = round(ph * 0.085)
    small = round(ph * 0.026)
    # Avenir Next faces: 7 Regular, 5 Medium, 2 Demi Bold, 0 Bold. The title
    # carries at size and does not need weight; the line under it must not
    # outweigh it, which is what happened when the subtitle was set in Bold.
    f1 = ImageFont.truetype(FONT, big, index=7)
    f2 = ImageFont.truetype(FONT, small, index=5)
    t1, t2 = "Camp Kingswood", "Bridgton, Maine  ·  Summer 2026"
    w1 = d.textbbox((0, 0), t1, font=f1)[2]
    w2 = d.textbbox((0, 0), t2, font=f2)[2]
    y = round(ph * 0.40)
    d.text(((pw - w1) // 2, y), t1, font=f1, fill=INK)
    rule_y = y + round(big * 1.45)
    d.line([(pw // 2 - round(pw * 0.05), rule_y), (pw // 2 + round(pw * 0.05), rule_y)],
           fill=ACCENT, width=max(2, round(ph * 0.004)))
    d.text(((pw - w2) // 2, rule_y + round(small * 1.1)), t2, font=f2, fill=INK)
    f3 = ImageFont.truetype(FONT, small, index=7)
    cred = "Photographs by Noah Gallagher"
    w3 = d.textbbox((0, 0), cred, font=f3)[2]
    d.text(((pw - w3) // 2, ph - round(ph * 0.10)), cred, font=f3, fill=INK)
    return out


def build(press=False):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    seq, dropped = lane()
    if not seq:
        sys.exit(f"The '{BOOK_GROUP}' lane is empty. Fill it on the arrange board "
                 f"(python3 build_arrange.py), copy the arrangement, paste it back.")
    src = sources()
    missing = [n for n in seq if n not in src]
    if missing:
        sys.exit(f"No master on disk for frames {missing}")

    dpi = millers.DPI_PRESS if press else millers.DPI_PREVIEW
    page = millers.trim_px(SIZE_KEY, dpi)      # where the layout lives
    canvas = millers.page_px(SIZE_KEY, dpi)    # what the lab receives, bleed included
    os.makedirs(OUTDIR, exist_ok=True)

    # Refuse to print a frame that would arrive soft. Miller's bar is 250 DPI at
    # the ordered size; a frame under that gets named rather than quietly resized.
    floor = millers.min_pixels_for(SIZE_KEY)
    soft = []
    for n in seq:
        with Image.open(src[n]) as probe:
            if probe.width < floor[0] and probe.height < floor[1]:
                soft.append(f"frame {n}: {probe.width}x{probe.height}, "
                            f"under {floor[0]}x{floor[1]} for a {SIZE_KEY} at 250 DPI")

    ims = {n: Image.open(src[n]).convert("RGB") for n in seq}
    pages, notes, i = [], [], 0
    while i < len(seq):
        n = seq[i]
        im = ims[n]
        tall = im.height > im.width
        nxt = seq[i + 1] if i + 1 < len(seq) else None
        if n in MONTAGE_SPREADS:
            grid = [m for m in MONTAGE_SPREADS[n] if m in src]
            gone = [m for m in MONTAGE_SPREADS[n] if m not in src]
            if grid:
                pages.append((matted(im, page), str(n), "montage hero"))
                gims = [Image.open(src[m]).convert("RGB") for m in grid]
                pages.append((montage(gims, page), "+".join(map(str, grid)),
                              f"montage, {len(grid)} facing {n}"))
                if gone:
                    notes.append(f"montage for {n} skipped missing frames {gone}")
                i += 1
                continue
            notes.append(f"montage for {n} has no frames on disk {MONTAGE_SPREADS[n]}; "
                         f"it fell back to a plain page")
        if tall and nxt is not None and ims[nxt].height > ims[nxt].width:
            pages.append((pair(im, ims[nxt], page), f"{n} + {nxt}", "paired"))
            i += 2
            continue
        if MATTE_ALL:
            pages.append((matted(im, page), str(n),
                          "matted, portrait" if tall else "matted, landscape"))
            i += 1
            continue
        if tall:
            pages.append((matted(im, page), str(n), "matted, portrait"))
            i += 1
            continue
        full, lost = fit(im, page)
        if full is None:
            pages.append((matted(im, page), str(n), f"matted, would lose {lost:.0%}"))
        else:
            pages.append((full, str(n), f"full bleed, {lost:.0%} cropped"))
            if lost > 0.06:
                notes.append(f"frame {n} loses {lost:.0%} to the page")
        i += 1

    if COVER_FRAME is not None and COVER_FRAME in ims:
        cover = photo_cover(ims[COVER_FRAME], canvas, dpi,
                            "Camp Kingswood", "Bridgton, Maine  ·  Summer 2026")
        cover_note = f"photographic, frame {COVER_FRAME}, Raleway"
    else:
        cover = on_bleed(title_page(page, len(seq)), canvas)
        cover_note = "typographic"
    sheets = [cover] + [on_bleed(p, canvas) for p, _, _ in pages]

    checks = millers.check_book(len(pages), SIZE_KEY)

    tag = "press" if press else "preview"
    jdir = os.path.join(OUTDIR, f"{tag}_pages")
    os.makedirs(jdir, exist_ok=True)
    for k, s in enumerate(sheets):
        s.save(os.path.join(jdir, f"page_{k+1:03d}.jpg"), quality=95 if press else 88,
               subsampling=0 if press else 2, dpi=(dpi, dpi))

    if press:
        out = os.path.join(OUTDIR, "Kingswood_book_press_12x8.pdf")
        sheets[0].save(out, save_all=True, append_images=sheets[1:],
                       resolution=dpi, quality=95)
    else:
        # A book reads in spreads, so the preview shows facing pages together.
        # The cover stands alone, the way it does on a table.
        spreads = [cover]
        rest = [p for p, _, _ in pages]
        for k in range(0, len(rest), 2):
            a = rest[k]
            b = rest[k + 1] if k + 1 < len(rest) else Image.new("RGB", page, GROUND)
            sp = Image.new("RGB", (page[0] * 2, page[1]), GROUND)
            sp.paste(a, (0, 0)); sp.paste(b, (page[0], 0))
            spreads.append(sp)
        out = os.path.join(OUTDIR, "Kingswood_book_preview_12x8.pdf")
        spreads[0].save(out, save_all=True, append_images=spreads[1:],
                        resolution=dpi, quality=88)

    with open(os.path.join(OUTDIR, "sequence_book.txt"), "w") as fh:
        fh.write(f"The book, {len(seq)} frames, {len(pages)} pages\n\n")
        for k, (_, label, how) in enumerate(pages, 1):
            fh.write(f"{k:3d}. {label:<12} {how}\n")

    print(f"wrote {out}")
    print(f"  {len(seq)} frames · {len(pages)} pages · {len(sheets)} sheets at {dpi} DPI")
    print(f"  cover: {cover_note}")
    print(f"  lab: Miller's {SIZE_KEY} Signature Book, "
          f"{canvas[0]}x{canvas[1]} px with {millers.BLEED_IN}in bleed, "
          f"{len(pages)/millers.SIDES_PER_SPREAD:.0f} spreads")
    for c in checks:
        print(f"  LAB CHECK: {c}")
    for s in soft:
        print(f"  RESOLUTION: {s}")
    if millers.SUBMIT_UNIT == "sides":
        print("  submitting as single sides; confirm with Miller's whether this "
              "book wants composed layflat spreads instead (millers.py SUBMIT_UNIT)")
    print(f"  sequence: {OUTDIR}/sequence_book.txt")
    if dropped:
        print(f"  IN THE BOOK, though they also sit in your aside lane: {dropped}")
    for nt in notes:
        print(f"  {nt}")
    print("  non-identifiable kids only (2026-08-07): the lane is your call, "
          "not checked here")


def submit(cover_route="linen"):
    """Package the press pages the way Miller's order form asks for them, and
    print the checklist that turns a folder into an ordered book.

    Their form says it plainly: "Miller's Transfer Link to zip: right click on
    folder, Send to> Compressed folder". So the deliverable is a zipped folder
    of numbered pages plus the filled order form, not a PDF emailed anywhere.
    """
    import zipfile
    build(press=True)
    jdir = os.path.join(OUTDIR, "press_pages")
    pages = sorted(f for f in os.listdir(jdir) if f.endswith(".jpg"))
    zpath = os.path.join(OUTDIR, f"Kingswood_{SIZE_KEY}_press.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
        for f in pages:
            z.write(os.path.join(jdir, f), f)
    mb = os.path.getsize(zpath) / 1e6
    route = millers.COVER_ROUTES[cover_route]
    sides = len(pages) - 1                      # the cover is not a side
    print(f"\n=== READY TO SUBMIT ===")
    print(f"  zip        {zpath}  ({mb:.0f} MB, {len(pages)} files)")
    print(f"  book       Miller's {SIZE_KEY} Signature Book, "
          f"{sides} sides = {sides/millers.SIDES_PER_SPREAD:.0f} spreads")
    print(f"  cover      {cover_route}: {route['how']}")
    if not route["artwork"]:
        print(f"             page_001 in the zip is a photographic cover and is "
              f"NOT used on this route; remove it or order Custom Image instead")
    print(f"\n  1. upload the zip: {millers.DROP_URL}")
    print(f"  2. fill and send:  {millers.ORDER_FORM}")
    print(f"  3. on the form, cover text goes in the foil/deboss fields by position")
    print(f"  4. paper: Matte press, Pearl press, or Deep Matte photographic")
    if millers.SUBMIT_UNIT == "sides":
        print(f"\n  UNCONFIRMED: submitting single sides. If Miller's wants composed")
        print(f"  layflat spreads, set millers.SUBMIT_UNIT and rebuild.")
    return zpath


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--press", action="store_true")
    ap.add_argument("--submit", action="store_true",
                    help="press build, then zip it the way Miller's asks")
    ap.add_argument("--cover", default="linen", choices=list(millers.COVER_ROUTES))
    a = ap.parse_args()
    if a.submit:
        submit(a.cover)
    else:
        build(a.press)
