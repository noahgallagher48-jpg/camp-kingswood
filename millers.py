#!/usr/bin/env python3
"""Miller's production spec, as data rather than as constants buried in a builder.

WHY THIS FILE EXISTS. Until now the press spec lived as PAGE_IN = (12, 8) in two
separate builders (kingswood/hub/build_book.py and ramah/build_ramah_book.py),
with no bleed, no safe area, and no validation. That produced a file that
happened to print once. This makes the spec explicit, shared, and checkable, so
a layout either passes or names the reason it cannot ship.

SOURCED 2026-08-26 from millerslab.com. Every number carries its confidence,
because a spec that hides its uncertainty is worse than no spec.

CONFIRMED by Miller's published material:
- Signature Books are layflat, handcrafted, on Matte press, Pearl press, or
  Deep Matte photographic paper.
- Design templates carry 1/8 inch bleed on all sides.
- Hardcover (Custom Image, Bonded Leather, Brushed EcoLeather, Faux Leather,
  Linen, Velvet): 5 spread minimum, 50 spread maximum. 1 spread = 2 sides.
- Softcover: 10 spread minimum, 25 spread maximum.
- Keep important elements 3/8 to 1/2 inch off the edge of the file.
- Files sized to the largest size ordered at 250 DPI (stated for Signature
  Albums; we output 300, which is above the bar and safe either way).

PROVEN in our own work:
- 12x8 hardcover linen, Signature Book, $105.50 on press. Ramah 2026. That is
  the only configuration this studio has taken end to end.

CONFIRMED 2026-08-27 from Miller's own PDFs, not their web pages:
- instructions.pdf (templates): "All templates contain 1/8" bleed on all sides."
  Templates are layered Photoshop PSDs. This is the bleed already built in.
- SIGNATURE ALBUM.pdf (the order form) carries a Miller's Drop Box link and the
  instruction "Miller's Transfer Link to zip: right click on folder, Send to>
  Compressed folder", i.e. work is delivered as a ZIPPED FOLDER through
  transfer.millerslab.com, alongside the filled order form.
- That same form specifies cover treatment as FOIL and DEBOSSED TEXT by
  position: cover top / mid / bottom and back top / mid / bottom. So a LINEN
  cover takes typeset text on the order form and NO supplied artwork. The photo
  cover build_book.py makes is for a Custom Image cover, a different product.
  The linen path is the one this studio has actually printed, and it needs no
  cover file and no spine width at all.

NOT CONFIRMED, and flagged wherever it matters:
- Whether Signature Books are submitted as single sides or as composed layflat
  spreads. The layflat construction and Miller's own "1 spread = 2 sides"
  counting both point at spreads, but their published pages did not state the
  submission unit outright. build_book.py can emit either; confirm at order
  time and set SUBMIT_UNIT. Do not assume.
- Spine width for a Custom Image (photo wrap) cover. It is a function of page
  count and paper stock and Miller's publishes it per template. SPINE_IN below
  is a placeholder that MUST be replaced with the number from the actual
  template before a wrap cover is ordered. A front-only cover avoids the
  question entirely.
- The full size list. 12x8 is ours and is verified; the others here are not
  and are marked.
"""

# --- trim sizes, inches (w, h) -------------------------------------------
# verified=True means this studio has ordered it and held the result.
SIZES = {
    "12x8":   {"trim": (12, 8),   "verified": True,
               "note": "Ramah 2026, hardcover linen, $105.50 press"},
    "10x10":  {"trim": (10, 10),  "verified": False, "note": "square, unconfirmed"},
    "12x12":  {"trim": (12, 12),  "verified": False, "note": "square, referenced by Miller's"},
    "8x8":    {"trim": (8, 8),    "verified": False, "note": "square, unconfirmed"},
    "8x12":   {"trim": (8, 12),   "verified": False, "note": "portrait, unconfirmed"},
}
DEFAULT_SIZE = "12x8"

# --- press geometry ------------------------------------------------------
BLEED_IN = 0.125          # confirmed: templates carry 1/8" on all sides
SAFE_IN = 0.5             # confirmed: keep important elements 3/8 to 1/2" off
                          # the edge. We take the conservative half inch.
DPI_PRESS = 300           # Miller's states 250; 300 is above the bar
DPI_PREVIEW = 150

# --- binding limits, confirmed ------------------------------------------
SPREAD_MIN_HARD, SPREAD_MAX_HARD = 5, 50
SPREAD_MIN_SOFT, SPREAD_MAX_SOFT = 10, 25
SIDES_PER_SPREAD = 2

# --- unconfirmed, must be set from the real template --------------------
SUBMIT_UNIT = "sides"     # "sides" or "spreads". See NOT CONFIRMED above.
SPINE_IN = None           # placeholder. Wrap covers refuse to build while None.
                          # Not needed at all on the linen path: that cover is
                          # foil text on the order form, not artwork.

# How the work actually reaches the press, from the order form itself.
DROP_URL = "https://transfer.millerslab.com/filedrop/"
ORDER_FORM = "SIGNATURE ALBUM.pdf, from millerslab.com/artdept/order-forms"
DELIVERY = "zip the numbered page folder, upload to the drop, send the form"

# Cover routes. "linen" is the proven one and needs no file from us.
COVER_ROUTES = {
    "linen": {"artwork": False,
              "how": "foil or debossed text by position on the order form: "
                     "cover top/mid/bottom and back top/mid/bottom",
              "proven": "Ramah 2026, 12x8 hardcover linen, $105.50 press"},
    "custom_image": {"artwork": True,
                     "how": "supply a wrap; needs SPINE_IN from Miller's template",
                     "proven": None},
}


def page_px(size_key=DEFAULT_SIZE, dpi=DPI_PRESS, bleed=True):
    """Full canvas in pixels, bleed included. Trim sits inside it."""
    w, h = SIZES[size_key]["trim"]
    b = BLEED_IN if bleed else 0
    return (round((w + 2 * b) * dpi), round((h + 2 * b) * dpi))


def trim_px(size_key=DEFAULT_SIZE, dpi=DPI_PRESS):
    w, h = SIZES[size_key]["trim"]
    return (round(w * dpi), round(h * dpi))


def bleed_px(dpi=DPI_PRESS):
    return round(BLEED_IN * dpi)


def safe_px(dpi=DPI_PRESS):
    """Inset from the TRIM edge that copy and faces must stay inside."""
    return round(SAFE_IN * dpi)


def min_pixels_for(size_key=DEFAULT_SIZE, dpi=250):
    """Smallest acceptable source frame to fill this trim at Miller's own
    250 DPI bar. Used to refuse a frame that would print soft."""
    w, h = SIZES[size_key]["trim"]
    return (round(w * dpi), round(h * dpi))


def check_book(n_sides, size_key=DEFAULT_SIZE, cover="hardcover"):
    """Validate a book before it goes anywhere. Returns a list of problems;
    empty list means it passes. Never guesses: an unconfirmed size is a
    warning, not a silent pass."""
    problems = []
    if size_key not in SIZES:
        return [f"unknown size {size_key}"]
    if not SIZES[size_key]["verified"]:
        problems.append(
            f"WARNING size {size_key} has never been ordered by this studio "
            f"({SIZES[size_key]['note']}); confirm it exists before ordering")
    lo, hi = ((SPREAD_MIN_HARD, SPREAD_MAX_HARD) if cover == "hardcover"
              else (SPREAD_MIN_SOFT, SPREAD_MAX_SOFT))
    spreads = n_sides / SIDES_PER_SPREAD
    if n_sides % SIDES_PER_SPREAD:
        problems.append(
            f"{n_sides} sides is not a whole number of spreads; Miller's counts "
            f"1 spread as 2 sides, so this needs one more or one fewer page")
    if spreads < lo:
        problems.append(f"{spreads:.0f} spreads is under the {cover} minimum of {lo}")
    if spreads > hi:
        problems.append(f"{spreads:.0f} spreads is over the {cover} maximum of {hi}")
    return problems


def report(size_key=DEFAULT_SIZE):
    t = SIZES[size_key]
    lines = [
        f"Miller's Signature Book, {size_key} ({'verified' if t['verified'] else 'UNVERIFIED'})",
        f"  trim        {t['trim'][0]} x {t['trim'][1]} in",
        f"  bleed       {BLEED_IN} in all sides",
        f"  safe inset  {SAFE_IN} in from trim",
        f"  press       {DPI_PRESS} DPI -> {page_px(size_key)[0]} x {page_px(size_key)[1]} px with bleed",
        f"  trim px     {trim_px(size_key)[0]} x {trim_px(size_key)[1]}",
        f"  min source  {min_pixels_for(size_key)[0]} x {min_pixels_for(size_key)[1]} px to fill at 250 DPI",
        f"  spreads     hardcover {SPREAD_MIN_HARD}-{SPREAD_MAX_HARD}, softcover {SPREAD_MIN_SOFT}-{SPREAD_MAX_SOFT}",
        f"  submit unit {SUBMIT_UNIT}  (CONFIRM AT ORDER TIME)",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    print(report(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SIZE))
