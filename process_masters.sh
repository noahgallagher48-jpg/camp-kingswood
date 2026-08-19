#!/bin/zsh
# EXIF strip-and-stack for the Kingswood full-resolution masters, per the
# photo-web-processing skill. Run on the masters folder BEFORE Drive upload.
#   ./process_masters.sh /path/to/masters
# Strips everything including Lightroom tags and the C2PA manifest (lossless,
# pixels untouched), then writes the searchable credit set in ONE pass
# (keywords replace, never append; the complete list goes in a single command).
# NO caption or description fields, ever: the frame is never narrated.
set -e
DIR="$1"
[ -d "$DIR" ] || { echo "usage: process_masters.sh /path/to/masters"; exit 1; }
command -v exiftool >/dev/null || { echo "exiftool not installed (brew install exiftool)"; exit 1; }

exiftool -all= --icc_profile:all -overwrite_original "$DIR"

exiftool -overwrite_original \
  -IPTC:By-line="Noah Gallagher" -XMP-dc:Creator="Noah Gallagher" \
  -IPTC:Credit="Abba Photo" -XMP-photoshop:Credit="Abba Photo" \
  -IPTC:CopyrightNotice="(c) 2026 Noah Gallagher, Abba Photo" \
  -XMP-dc:Rights="(c) 2026 Noah Gallagher, Abba Photo" \
  -XMP-xmpRights:Marked=True \
  -XMP-xmpRights:WebStatement="https://www.abba-photo.com" \
  -XMP-iptcCore:CreatorWorkURL="https://www.abba-photo.com" \
  -IPTC:City="Bridgton" -IPTC:Province-State="Maine" -IPTC:Country-PrimaryLocationName="United States" \
  -IPTC:Keywords="Camp Kingswood" -IPTC:Keywords="campkingswood.org" \
  -IPTC:Keywords="Bridgton Maine" -IPTC:Keywords="Jewish summer camp" \
  -IPTC:Keywords="summer camp photography" -IPTC:Keywords="Abba Photo" \
  -IPTC:Keywords="Noah Gallagher" \
  -XMP-dc:Subject="Camp Kingswood" -XMP-dc:Subject="campkingswood.org" \
  -XMP-dc:Subject="Bridgton Maine" -XMP-dc:Subject="Jewish summer camp" \
  -XMP-dc:Subject="summer camp photography" -XMP-dc:Subject="Abba Photo" \
  -XMP-dc:Subject="Noah Gallagher" \
  -IPTC:SpecialInstructions="Camp Kingswood, Bridgton, Maine, campkingswood.org. Photograph: Noah Gallagher, Abba Photo, abba-photo.com" \
  -XMP-photoshop:Instructions="Camp Kingswood, Bridgton, Maine, campkingswood.org. Photograph: Noah Gallagher, Abba Photo, abba-photo.com" \
  "$DIR"

echo "verify one file:"
exiftool -By-line -Credit -Keywords -Caption-Abstract -Software "$DIR"/*.jpg(N[1])
