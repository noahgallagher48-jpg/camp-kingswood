#!/bin/zsh
# EXIF strip-and-stack for Camp Kingswood image sets, per the photo-web-processing
# skill. Run on the masters folder BEFORE Drive upload, and on every derived tier
# after generation (Pillow drops metadata on save).
#   ./process_masters.sh /path/to/folder
# Strips everything including Lightroom tags and the C2PA manifest (lossless,
# pixels untouched), then writes the searchable credit + location set in ONE pass
# (keywords replace, never append; the complete list goes in a single command).
# NO caption or description fields, ever: the frame is never narrated.
set -e
DIR="$1"
[ -d "$DIR" ] || { echo "usage: process_masters.sh /path/to/folder"; exit 1; }
command -v exiftool >/dev/null || { echo "exiftool not installed (brew install exiftool)"; exit 1; }

# Location, added 2026-08-19. Coordinates geocoded from the camp's own published
# street address (104 Wildwood Road, Bridgton, ME 04009); the camera wrote no GPS.
# Nothing here is private: the camp publishes this address itself.
LAT=44.027979
LON=70.723265   # west, sign carried by GPSLongitudeRef

exiftool -all= --icc_profile:all -overwrite_original "$DIR"

exiftool -overwrite_original \
  -IPTC:By-line="Noah Gallagher" -XMP-dc:Creator="Noah Gallagher" \
  -IPTC:Credit="Abba Photo" -XMP-photoshop:Credit="Abba Photo" \
  -IPTC:CopyrightNotice="(c) 2026 Noah Gallagher, Abba Photo" \
  -XMP-dc:Rights="(c) 2026 Noah Gallagher, Abba Photo" \
  -XMP-xmpRights:Marked=True \
  -XMP-xmpRights:WebStatement="https://www.abba-photo.com" \
  -XMP-iptcCore:CreatorWorkURL="https://www.abba-photo.com" \
  -XMP-iptcCore:CreatorWorkEmail="noah@abba-photo.com" \
  -XMP-plus:ImageCreatorName="Noah Gallagher" \
  -XMP-plus:CopyrightOwnerName="Noah Gallagher, Abba Photo" \
  -XMP-plus:LicensorName="Abba Photo" \
  -XMP-plus:LicensorURL="https://www.abba-photo.com" \
  -XMP-plus:LicensorEmail="noah@abba-photo.com" \
  -XMP-iptcExt:DigitalSourceType="http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture" \
  -IPTC:City="Bridgton" -IPTC:Province-State="Maine" \
  -IPTC:Country-PrimaryLocationName="United States" \
  -IPTC:Country-PrimaryLocationCode="USA" \
  -IPTC:Sub-location="Camp Kingswood" \
  -XMP-photoshop:City="Bridgton" -XMP-photoshop:State="Maine" \
  -XMP-photoshop:Country="United States" \
  -EXIF:GPSLatitude="$LAT" -EXIF:GPSLatitudeRef=N \
  -EXIF:GPSLongitude="$LON" -EXIF:GPSLongitudeRef=W \
  -XMP:GPSLatitude="$LAT" -XMP:GPSLongitude="-$LON" \
  -XMP-iptcExt:LocationCreatedSublocation="Camp Kingswood" \
  -XMP-iptcExt:LocationCreatedCity="Bridgton" \
  -XMP-iptcExt:LocationCreatedProvinceState="Maine" \
  -XMP-iptcExt:LocationCreatedCountryName="United States" \
  -XMP-iptcExt:LocationCreatedCountryCode="US" \
  -XMP-iptcExt:LocationCreatedGPSLatitude="$LAT" \
  -XMP-iptcExt:LocationCreatedGPSLongitude="-$LON" \
  -XMP-iptcExt:LocationShownSublocation="Camp Kingswood" \
  -XMP-iptcExt:LocationShownCity="Bridgton" \
  -XMP-iptcExt:LocationShownProvinceState="Maine" \
  -XMP-iptcExt:LocationShownCountryName="United States" \
  -XMP-iptcExt:LocationShownCountryCode="US" \
  -XMP-iptcExt:LocationShownGPSLatitude="$LAT" \
  -XMP-iptcExt:LocationShownGPSLongitude="-$LON" \
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
exiftool -By-line -Credit -CopyrightNotice -CreatorWorkURL -CreatorWorkEmail \
  -ImageCreatorName -CopyrightOwnerName -LicensorName -DigitalSourceType \
  -Sub-location -GPSPosition -Keywords \
  -Caption-Abstract -Software "$DIR"/*.jpg(N[1])
