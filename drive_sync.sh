#!/bin/zsh
# Make the client's Drive delivery folder match the local pool, exactly.
#
#   ./drive_sync.sh check     what differs, changes nothing
#   ./drive_sync.sh push      copy the pool up (overwrite in place)
#
# WHY THIS EXISTS: dragging files by hand leaves the folder silently stale.
# Twice the Drive copies were a build behind the local masters (first the
# unprocessed export, then the pre-credential metadata). The folder is the
# client's "All full res" link, so stale there means the client gets the wrong
# files while every local check says fine.
#
# Drive is a LOCAL MOUNT since 2026-08-19 (Drive for Desktop, account
# noah@abba-photo.com), so this is plain cp. Overwriting preserves Drive file
# IDs, which is why the delivery page's per-frame links survive a resync.
#
# DELETIONS ARE NOT DONE HERE. Removing files is refused by the Claude Code
# auto-mode classifier, so `check` REPORTS what should come out and stops.
# Noah removes those, or adds a Bash permission rule.
set -e
CMD="${1:-check}"
DRIVE="$HOME/Library/CloudStorage/GoogleDrive-noah@abba-photo.com/My Drive/Kingswood/kwood819"
POOL="$HOME/Desktop/ABBA/kingswood/DRIVE_UPLOAD_117"

[ -d "$POOL" ]  || { echo "pool folder missing: $POOL"; exit 1; }
[ -d "$DRIVE" ] || { echo "Drive not mounted at: $DRIVE
Add noah@abba-photo.com in Google Drive for Desktop."; exit 1; }

echo "pool:  $(ls "$POOL"/*.jpg | wc -l | tr -d ' ') files"
echo "drive: $(ls "$DRIVE"/*.jpg 2>/dev/null | wc -l | tr -d ' ') files"

case "$CMD" in
  check)
    echo "--- differ or missing on Drive:"
    for f in "$POOL"/*.jpg; do
      n=$(basename "$f"); d="$DRIVE/$n"
      if [ ! -f "$d" ]; then echo "   MISSING  $n"
      elif [ "$(stat -f%z "$f")" != "$(stat -f%z "$d")" ]; then echo "   DIFFERS  $n"; fi
    done
    echo "--- on Drive but not in the pool (should be removed, Noah's call):"
    for f in "$DRIVE"/*.jpg; do
      n=$(basename "$f"); [ -f "$POOL/$n" ] || echo "   EXTRA    $n"
    done
    ;;
  push)
    cp "$POOL"/*.jpg "$DRIVE"/
    echo "copied $(ls "$POOL"/*.jpg | wc -l | tr -d ' ') files (IDs preserved)"
    "$0" check
    ;;
  *) echo "usage: drive_sync.sh [check|push]"; exit 1 ;;
esac
