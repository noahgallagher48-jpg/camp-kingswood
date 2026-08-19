#!/usr/bin/env python3
"""Builds the Camp Kingswood delivery page (delivery.html) for the Aug 23
delivery to Jodi. Scaffolded 2026-08-18 so delivery day is images-in, not
build-under-deadline. Pattern: the Interlaken library build, simplified.

Three commands, in delivery-day order:

    python3 build_delivery.py ingest /path/to/lightroom/export
        Reads every JPEG in the folder, converts to sRGB (profile embedded),
        writes two tiers into img/: present/ at 2560px (lightbox) and
        thumb/ at 900px (cards). Export sRGB out of Lightroom to begin with.

    python3 build_delivery.py build
        Renders delivery.html from delivery.template.html: the forty-two
        (from forty_two.json, Noah's order) and the full gallery (everything
        in img/present, by filename). Download buttons come from links.json.

    python3 build_delivery.py zip
        Builds downloads/kingswood_web.zip from img/present.

RELEASES: not connected to this delivery (Noah, 2026-08-19). The delivery is a
camp receiving photographs of its own community, and the camp holds that
relationship. The build carries no releases gate.

Inputs the day supplies:
    forty_two.json   ["<filename>.jpg", ...] in Noah's presentation order
                     (twelve mastered campscapes first, then the thirty)
    links.json       {"web_zip": "downloads/kingswood_web.zip",
                      "drive_fullres": "https://drive.google.com/..."}
"""
import json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
TEMPLATE = os.path.join(HERE, "delivery.template.html")
PAGE = os.path.join(HERE, "delivery.html")
GATE = os.path.join(HERE, "_work", "releases.txt")


def ingest(folder):
    import io
    from PIL import Image, ImageCms
    os.makedirs(os.path.join(IMG, "present"), exist_ok=True)
    os.makedirs(os.path.join(IMG, "thumb"), exist_ok=True)
    srgb = ImageCms.createProfile("sRGB")
    srgb_icc = ImageCms.ImageCmsProfile(srgb).tobytes()
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg")))
    if not names:
        sys.exit(f"no JPEGs in {folder}")
    for n in names:
        im = Image.open(os.path.join(folder, n))
        icc = im.info.get("icc_profile")
        im = im.convert("RGB")
        if icc:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            desc = ImageCms.getProfileDescription(src).strip()
            if "sRGB" not in desc:
                im = ImageCms.profileToProfile(
                    im, src, srgb, outputMode="RGB",
                    renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
                print(f"  {n}: converted from {desc}")
        out = os.path.splitext(n)[0] + ".jpg"
        a = im.copy(); a.thumbnail((2560, 2560), Image.LANCZOS)
        a.save(os.path.join(IMG, "present", out), quality=88,
               icc_profile=srgb_icc, subsampling=0)
        b = im.copy(); b.thumbnail((900, 900), Image.LANCZOS)
        b.save(os.path.join(IMG, "thumb", out), quality=82, icc_profile=srgb_icc)
    print(f"ingested {len(names)} frames")


def card(fname):
    fid = os.path.splitext(fname)[0]
    return ('    <div class="card">'
            f'<button class="ph" type="button" data-file="{fname}" data-id="{fid}" '
            f'aria-label="View {fid}">'
            f'<img loading="lazy" src="img/thumb/{fname}" alt="{fid}"></button>'
            '</div>')


def build():
    # Releases are NOT connected to this delivery (Noah, 2026-08-19). Delivering a
    # camp photographs of its own community is not publication; the camp holds the
    # relationship with its families. No gate here. A frame moving to one of Noah's
    # own promotional surfaces is a separate question, decided separately.
    forty = json.load(open(os.path.join(HERE, "forty_two.json")))
    links = json.load(open(os.path.join(HERE, "links.json")))
    present = sorted(os.listdir(os.path.join(IMG, "present")))
    missing = [f for f in forty if f not in present]
    if missing:
        sys.exit(f"forty_two.json names files not ingested: {missing}")
    picks = "\n".join(card(f) for f in forty)
    rest = "\n".join(card(f) for f in present if f not in set(forty))
    html = (open(TEMPLATE).read()
            .replace("__PICKS__", picks)
            .replace("__GALLERY__", rest)
            .replace("__NPICKS__", str(len(forty)))
            .replace("__NALL__", str(len(present)))
            .replace("__WEBZIP__", links["web_zip"])
            .replace("__DRIVE__", links["drive_fullres"]))
    open(PAGE, "w").write(html)
    print(f"wrote delivery.html ({len(forty)} picks, {len(present)} frames total)")


def make_zip():
    os.makedirs(os.path.join(HERE, "downloads"), exist_ok=True)
    out = os.path.join(HERE, "downloads", "kingswood_web.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
        for f in sorted(os.listdir(os.path.join(IMG, "present"))):
            z.write(os.path.join(IMG, "present", f), f)
    print(f"wrote {out} ({os.path.getsize(out)//1048576} MB)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "ingest":
        ingest(sys.argv[2])
    elif cmd == "zip":
        make_zip()
    else:
        build()
