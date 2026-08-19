# Delivery runbook: Camp Kingswood, due Sunday Aug 23

Scaffolded 2026-08-18 so delivery day is one hour of mechanics, not a build.
Everything below is tooling in this repo; nothing is live until step 7 pushes.

## Releases
Not connected to this delivery (Noah, 2026-08-19). The camp is receiving
photographs of its own community and holds that relationship. No gate in the
build. A frame moving to one of Noah's own promotional surfaces is a separate
decision, made separately.

## The day, in order
1. Noah exports the cull from Lightroom, sRGB, full resolution, one folder.
2. `./process_masters.sh /path/to/masters` (EXIF strip and stack, then verify
   output). Upload masters to the client Drive folder; note its share link.
3. `python3 build_delivery.py ingest /path/to/masters` (web tiers into img/).
4. Write `forty_two.json`: the presentation order, twelve mastered campscapes
   first, then the thirty storytelling frames. Filenames as ingested.
5. Write `links.json`: `{"web_zip": "downloads/kingswood_web.zip",
   "drive_fullres": "<the Drive share link>"}`.
6. `python3 build_delivery.py zip` then `python3 build_delivery.py build`.
   Open delivery.html locally; walk it; Noah walks it too (nothing ships
   before his own pass over the live set: the 8/14 lesson).
7. Commit, push, verify live at /camp-kingswood/delivery.html: spot-check a
   thumbnail, the lightbox, both download buttons, and read EXIF back off one
   live file (curl + exiftool).
8. Link the page from index.html (one line), push, log STATE.md.
9. STAGE the delivery email to Jodi (never send): numbered payload, bold
   label-links up top, photos lead, plain register, no counts that could
   change, no earliness claims. Noah reads and clicks.
10. Board: move the deliverable to Done with the date; the invoice waits for
    Jodi in person per the standing plan.

## What this covers and what it does not
The Aug 23 delivery is the photo library. The media-library handback (Aug 30)
and the two photo books (scoped on site, Bader book in the deal) are separate
deliverables with their own dates; do not fold them into this page.
