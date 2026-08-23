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
MASTER = os.path.expanduser("~/Desktop/ABBA/kingswood/_delivery_2026/master")
OUTDIR = os.path.join(HERE, "book")
BOOK_GROUP = "The book"

PAGE_IN = (12, 8)                 # inches, landscape, the Ramah standard
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

    dpi = 300 if press else 150
    page = (PAGE_IN[0] * dpi, PAGE_IN[1] * dpi)
    os.makedirs(OUTDIR, exist_ok=True)

    ims = {n: Image.open(src[n]).convert("RGB") for n in seq}
    pages, notes, i = [], [], 0
    while i < len(seq):
        n = seq[i]
        im = ims[n]
        tall = im.height > im.width
        nxt = seq[i + 1] if i + 1 < len(seq) else None
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

    cover = title_page(page, len(seq))
    sheets = [cover] + [p for p, _, _ in pages]

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
    print(f"  sequence: {OUTDIR}/sequence_book.txt")
    if dropped:
        print(f"  IN THE BOOK, though they also sit in your aside lane: {dropped}")
    for nt in notes:
        print(f"  {nt}")
    print("  non-identifiable kids only (2026-08-07): the lane is your call, "
          "not checked here")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--press", action="store_true")
    build(ap.parse_args().press)
