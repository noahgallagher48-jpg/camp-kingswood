#!/usr/bin/env python3
"""Rebuild _work/dims_kw.json from the 8/27 masters.

dims drives the per-frame print ladder on the delivery page, so it must read
the MASTER pixels, not a web tier. A frame's largest honest print comes from
what the camera made, not from what we resized for a browser.

    python3 dims_827.py
"""
import json, os
from PIL import Image

SRC = os.path.expanduser("~/Abba_Photo/Kwood_827")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_work", "dims_kw.json")


def main():
    Image.MAX_IMAGE_PIXELS = None
    dims, small = {}, []
    names = sorted(f for f in os.listdir(SRC) if f.lower().endswith((".jpg", ".jpeg")))
    for f in names:
        with Image.open(os.path.join(SRC, f)) as im:
            dims[f] = [im.width, im.height]
            if max(im.size) < 3000:
                small.append((f, im.size))
    json.dump(dims, open(OUT, "w"), indent=1)
    print(f"wrote {OUT}")
    print(f"  {len(dims)} frames measured from masters")
    if small:
        print(f"  {len(small)} under 3000px on the long edge, print ladder will be short:")
        for f, s in small[:10]:
            print(f"    {f}  {s[0]}x{s[1]}")


if __name__ == "__main__":
    main()
