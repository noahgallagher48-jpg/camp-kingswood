#!/usr/bin/env python3
"""Build the 5K TV tier for the Camp Kingswood gallery.

Every frame becomes a 5120x2880 canvas, which is what a 5K television wants:
one constant size, so nothing resizes between slides. The frame is fitted
inside it and centred on black, the same presentation the delivery page's
lightbox already gives (background:#000, object-fit:contain) and the right
ground for a screen in a room.

NOTHING IS UPSCALED (Noah, 2026-08-25: "matte the ones that cannot hit").
The scale factor is capped at 1.0, so a frame that cannot fill the canvas sits
at its own native size on the matte instead of being stretched into a claim its
pixels do not support. 130 of 138 fill it; 8 are matted.

Metadata: Pillow drops everything on save, and process_masters.sh restores the
capture facts with -tagsfromfile @, which reads the file itself and so finds
nothing on freshly generated output. Capture EXIF is therefore seeded from each
master here, and the credit pass runs afterwards.

    python3 build_5k.py            build every pool frame
    python3 build_5k.py <name>...  build only those frames
"""
import io, json, os, re, subprocess, sys
from PIL import Image, ImageCms

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser("~/Desktop/ABBA/kingswood/kwood_5K")
CW, CH = 5120, 2880
MATTE = (0, 0, 0)
QUALITY = 92

MASTER_DIRS = [
    os.path.expanduser("~/Library/CloudStorage/GoogleDrive-noah@abba-photo.com/My Drive/Kingswood/kwood819"),
    os.path.expanduser("~/Desktop/ABBA/kingswood/masters_delivery"),
    os.path.expanduser("~/Desktop/ABBA/kingswood/DRIVE_UPLOAD_117"),
]

CAPTURE_TAGS = [
    "-EXIF:DateTimeOriginal", "-EXIF:CreateDate", "-EXIF:ModifyDate",
    "-EXIF:Make", "-EXIF:Model", "-EXIF:LensModel", "-EXIF:LensMake",
    "-EXIF:LensInfo", "-EXIF:ISO", "-EXIF:FNumber", "-EXIF:ExposureTime",
    "-EXIF:FocalLength", "-EXIF:FocalLengthIn35mmFormat",
    "-EXIF:ExposureProgram", "-EXIF:ExposureCompensation",
    "-EXIF:MeteringMode", "-EXIF:Flash", "-EXIF:Orientation",
]


def pool():
    html = open(os.path.join(HERE, "delivery.html"), encoding="utf-8").read()
    return list(dict.fromkeys(re.findall(r'\{"n": \d+, "f": "([^"]+)"', html)))


def master_for(name):
    for d in MASTER_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    want = sys.argv[1:] or pool()
    srgb = ImageCms.createProfile("sRGB")
    srgb_icc = ImageCms.ImageCmsProfile(srgb).tobytes()
    filled = matted = 0
    missing, report = [], {}

    for i, name in enumerate(want, 1):
        src = master_for(name)
        if not src:
            missing.append(name)
            continue
        im = Image.open(src)
        icc = im.info.get("icc_profile")
        im = im.convert("RGB")
        if icc:
            p = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            if "sRGB" not in ImageCms.getProfileDescription(p):
                im = ImageCms.profileToProfile(
                    im, p, srgb, outputMode="RGB",
                    renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)

        w, h = im.size
        scale = min(CW / w, CH / h, 1.0)          # never upscale
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        if scale < 1.0:
            im = im.resize((nw, nh), Image.LANCZOS)

        canvas = Image.new("RGB", (CW, CH), MATTE)
        canvas.paste(im, ((CW - nw) // 2, (CH - nh) // 2))
        dst = os.path.join(OUT, name)
        canvas.save(dst, quality=QUALITY, icc_profile=srgb_icc, subsampling=0)

        fits = nw >= CW or nh >= CH
        filled += fits
        matted += not fits
        report[name] = {"master": [w, h], "placed": [nw, nh], "fills": bool(fits)}

        subprocess.run(["exiftool", "-q", "-overwrite_original",
                        "-tagsfromfile", src, *CAPTURE_TAGS, dst], check=False)
        if i % 20 == 0:
            print(f"  {i}/{len(want)}", flush=True)

    print(f"built {filled + matted} frames -> {OUT}")
    print(f"  fill the canvas : {filled}")
    print(f"  matted at native: {matted}")
    if missing:
        print(f"  NO MASTER FOUND ({len(missing)}): {', '.join(missing)}")
    json.dump(report, open(os.path.join(OUT, "_5k_report.json"), "w"), indent=1)
    print("\nNow run:  ./process_masters.sh " + OUT)


if __name__ == "__main__":
    main()
