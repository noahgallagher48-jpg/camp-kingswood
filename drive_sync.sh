#!/bin/zsh
# Make the client's Drive delivery folder match the local pool, exactly.
#
#   ./drive_sync.sh check     what differs, changes nothing
#   ./drive_sync.sh push      upload changed/new, trash what is not in the pool
#
# WHY THIS EXISTS: dragging files by hand leaves the folder silently stale.
# Twice now the Drive copies were a build behind the local masters (first the
# unprocessed export, then the pre-credential metadata). The folder is the
# client's "All full res" link, so stale there means the client gets the wrong
# files while every local check says fine. This script is the answer: one
# command, the folder matches, and `check` proves it.
#
# ACCOUNT REQUIREMENT (the thing that blocks a fresh machine):
# the delivery folder is owned by noah@abba-photo.com. A remote authenticated
# as any other Google account can READ it (it is shared "anyone: reader") and
# will fail every write with 403 insufficientFilePermissions. Configure the
# right account once:
#     rclone config          # new remote named "abba", type drive, sign in AS
#                            # noah@abba-photo.com, scope: drive
# Or add noah@abba-photo.com in Google Drive for Desktop, which makes the
# folder a plain local path and this script unnecessary for uploads.
set -e
CMD="${1:-check}"
REMOTE="${ABBA_DRIVE_REMOTE:-abba}"
FOLDER_ID="1XqShLle7YVldJ6zmcd36SLBIZ_auyHYL"
POOL="$HOME/Desktop/ABBA/kingswood/DRIVE_UPLOAD_117"   # built by build_delivery.py pool
R="$REMOTE: --drive-root-folder-id=$FOLDER_ID"

command -v rclone >/dev/null || { echo "rclone not installed"; exit 1; }
[ -d "$POOL" ] || { echo "pool folder missing: $POOL"; exit 1; }
rclone listremotes | grep -q "^${REMOTE}:$" || {
  echo "no rclone remote named '$REMOTE'. See ACCOUNT REQUIREMENT at the top of this file."
  exit 1; }

echo "local pool: $(ls "$POOL"/*.jpg | wc -l | tr -d ' ') files"

case "$CMD" in
  check)
    echo "--- differences (local vs Drive), nothing is changed:"
    rclone check "$POOL" ${=R} --size-only --one-way 2>&1 | grep -vE "client_id|^$" || true
    echo "--- files on Drive that are NOT in the pool (these would be trashed):"
    comm -13 <(ls "$POOL" | sort) <(rclone lsf ${=R} 2>/dev/null | sort)
    ;;
  push)
    # --ignore-times: metadata-only edits do not change size, so a size/time
    # comparison would skip them. Every credential restack must re-upload.
    # rclone updates an existing name IN PLACE, so Drive file IDs survive and
    # the delivery page's per-frame links keep working.
    echo "--- uploading (IDs preserved, metadata-only changes included):"
    rclone copy "$POOL" ${=R} --ignore-times --progress 2>&1 | grep -v client_id
    echo "--- trashing what is not in the pool (recoverable from Drive trash):"
    rclone lsf ${=R} 2>/dev/null | sort > /tmp/_drive_now.$$
    ls "$POOL" | sort > /tmp/_pool_now.$$
    comm -13 /tmp/_pool_now.$$ /tmp/_drive_now.$$ | while read -r f; do
      case "$f" in
        *.zip) echo "   keeping $f (zip lives here on purpose)" ;;
        *)     echo "   trashing $f"; rclone delete "${REMOTE}:$f" --drive-root-folder-id="$FOLDER_ID" ;;
      esac
    done
    rm -f /tmp/_drive_now.$$ /tmp/_pool_now.$$
    echo "--- verifying:"
    "$0" check
    ;;
  *) echo "usage: drive_sync.sh [check|push]"; exit 1 ;;
esac
