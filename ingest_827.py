#!/usr/bin/env python3
"""Ingest the 8/27 Kingswood set into the three web tiers, metadata intact.

Same tiers build_delivery.py has always made (3840 web / 2560 present / 900
thumb, sRGB), with the ordering fix from 2026-08-25: Pillow drops all metadata
on save, and process_masters.sh restores capture facts with -tagsfromfile @,
which reads the file itself and so finds nothing on freshly generated output.
Capture EXIF is therefore seeded from each master here FIRST, then the credit
pass runs over the tiers.

Writes to img_827/ rather than img/, so nothing live is touched until the swap
is deliberate. Resumable: a tier file that already exists is skipped.

    python3 ingest_827.py
"""
import io, os, subprocess, sys
from PIL import Image, ImageCms

SRC = os.path.expanduser("~/Abba_Photo/Kwood_827")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img_827")
TIERS = (("web", 3840, 90), ("present", 2560, 88), ("thumb", 900, 82))
CAPTURE = [
    "-EXIF:DateTimeOriginal", "-EXIF:CreateDate", "-EXIF:ModifyDate",
    "-EXIF:Make", "-EXIF:Model", "-EXIF:LensModel", "-EXIF:LensMake",
    "-EXIF:LensInfo", "-EXIF:ISO", "-EXIF:FNumber", "-EXIF:ExposureTime",
    "-EXIF:FocalLength", "-EXIF:FocalLengthIn35mmFormat",
    "-EXIF:ExposureProgram", "-EXIF:ExposureCompensation",
    "-EXIF:MeteringMode", "-EXIF:Flash", "-EXIF:Orientation",
]


def main():
    Image.MAX_IMAGE_PIXELS = None
    for t, _, _ in TIERS:
        os.makedirs(os.path.join(OUT, t), exist_ok=True)
    srgb = ImageCms.createProfile("sRGB")
    icc = ImageCms.ImageCmsProfile(srgb).tobytes()
    names = sorted(f for f in os.listdir(SRC) if f.lower().endswith((".jpg", ".jpeg")))
    print(f"ingesting {len(names)} frames -> {OUT}", flush=True)

    for i, n in enumerate(names, 1):
        sp = os.path.join(SRC, n)
        todo = [(t, px, q) for t, px, q in TIERS
                if not os.path.exists(os.path.join(OUT, t, n))]
        if not todo:
            continue
        im = Image.open(sp)
        prof = im.info.get("icc_profile")
        im = im.convert("RGB")
        if prof:
            p = ImageCms.ImageCmsProfile(io.BytesIO(prof))
            if "sRGB" not in ImageCms.getProfileDescription(p):
                im = ImageCms.profileToProfile(
                    im, p, srgb, outputMode="RGB",
                    renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
        for t, px, q in todo:
            c = im.copy()
            c.thumbnail((px, px), Image.LANCZOS)
            dp = os.path.join(OUT, t, n)
            c.save(dp, quality=q, icc_profile=icc,
                   subsampling=0 if t != "thumb" else 2)
            subprocess.run(["exiftool", "-q", "-overwrite_original",
                            "-tagsfromfile", sp, *CAPTURE, dp], check=False)
        if i % 25 == 0:
            print(f"  {i}/{len(names)}", flush=True)

    print(f"tiers written. now run:", flush=True)
    for t, _, _ in TIERS:
        print(f"  ./process_masters.sh {OUT}/{t}", flush=True)


if __name__ == "__main__":
    main()
