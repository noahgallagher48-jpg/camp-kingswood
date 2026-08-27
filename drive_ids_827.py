#!/usr/bin/env python3
"""Rebuild the per-frame Drive id maps from Drive Desktop's own database.

WHY NOT THE CONNECTOR. Listing the delivery folder through the Google Drive
connector cost 11.6K tokens in a single call on 2026-08-26 and would need
pagination for 298 frames. Drive Desktop keeps every file's real id in a local
SQLite database, so the same answer is free and offline.

WHY THIS EXISTS AT ALL. On 2026-08-26 the stored ids turned out to point at a
stale duplicate set: the folder held two files per name, and drive_ids_kw.json
named the copies the local mount does not manage. The page therefore showed a
new edit while its own download button served an old one. Regenerating from the
mount's own database is what keeps the map and the folder describing the same
files.

    python3 drive_ids_827.py            report only
    python3 drive_ids_827.py --write    write the two maps
"""
import glob, json, os, shutil, sqlite3, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_work")
FULL = os.path.join(WORK, "drive_ids_kw.json")
WEBM = os.path.join(WORK, "drive_web_ids_kw.json")
MASTER_FOLDER = "1XqShLle7YVldJ6zmcd36SLBIZ_auyHYL"   # Kingswood/kwood819
WEB_FOLDER = "1N7lviRxMS3d1A8LbE1KqjTWs8gpfZRs8"      # Kingswood/kwood819/web
DBGLOB = os.path.expanduser(
    "~/Library/Application Support/Google/DriveFS/*/metadata_sqlite_db")


def open_db():
    for p in glob.glob(DBGLOB):
        tmp = os.path.join(tempfile.gettempdir(), "kw_dfs_" + os.path.basename(os.path.dirname(p)))
        shutil.copy2(p, tmp)                 # never read the live db in place
        c = sqlite3.connect(tmp)
        n = c.execute("select count(*) from items where local_title like 'Kwood827-%'").fetchone()[0]
        if n:
            return c, n
        c.close()
    sys.exit("no Drive Desktop database holds Kwood827 files; is the account signed in?")


def folder_map(conn, folder_id, disk_dir):
    """Map filename -> Drive id for one folder, filtered to live files only.

    Two filters, both learned the hard way on 2026-08-27. The database keeps
    TRASHED rows and TOMBSTONES, so an unfiltered join reported 438 files in a
    folder holding 298, and reported names that had already been moved out.
    And stable_parents can hold stale parentage after a move, so the database
    alone is not enough: the answer is cross-checked against the folder on
    disk, which is the mount and therefore the truth.
    """
    sid = conn.execute("select stable_id from items where id=?", (folder_id,)).fetchone()
    if not sid:
        sys.exit(f"folder {folder_id} not in the local database")
    on_disk = ({f for f in os.listdir(disk_dir) if f.lower().endswith(".jpg")}
               if os.path.isdir(disk_dir) else set())
    rows = conn.execute(
        "select i.local_title, i.id from items i "
        "join stable_parents p on p.item_stable_id = i.stable_id "
        "where p.parent_stable_id = ? and i.is_folder = 0 "
        "and i.trashed = 0 and i.is_tombstone = 0 "
        "and lower(i.local_title) like '%.jpg'", (sid[0],)).fetchall()
    out, dupes = {}, []
    for title, fid in rows:
        if title not in on_disk:        # moved out, or never really here
            continue
        if title in out and out[title] != fid:
            dupes.append(title)
        out[title] = fid
    missing = sorted(on_disk - set(out)) if on_disk else []
    return out, sorted(set(dupes)), missing


MOUNT = os.path.expanduser(
    "~/Library/CloudStorage/GoogleDrive-noah@abba-photo.com/My Drive/Kingswood/kwood819")


def main():
    conn, n = open_db()
    print(f"  Drive knows {n} Kwood827 items")
    full, dfull, mfull = folder_map(conn, MASTER_FOLDER, MOUNT)
    web, dweb, mweb = folder_map(conn, WEB_FOLDER, os.path.join(MOUNT, "web"))
    print(f"  masters folder: {len(full)} live jpg" + (f"   {len(dfull)} DUPLICATE NAMES" if dfull else ""))
    print(f"  web folder:     {len(web)} live jpg" + (f"   {len(dweb)} DUPLICATE NAMES" if dweb else ""))
    for d in (dfull or dweb)[:5]:
        print(f"    duplicate: {d}")
    for label, miss in (("masters", mfull), ("web", mweb)):
        if miss:
            print(f"  {len(miss)} {label} files on disk with NO id yet (still uploading): {miss[:3]}")
    stale = [k for k in full if not k.startswith("Kwood827")]
    if stale:
        print(f"  {len(stale)} non-8/27 names still in the masters folder, e.g. {stale[:3]}")
    # PLACEHOLDER IDS (2026-08-27): Drive Desktop stamps a local-NNNN id the
    # moment a file lands in the mount and only swaps in the real id once the
    # upload commits. Those sail past the missing-id check above, and a page
    # built on one serves a download link that 404s. Treat them as not-yet-synced.
    pfull = sorted(k for k, v in full.items() if str(v).startswith("local-"))
    pweb = sorted(k for k, v in web.items() if str(v).startswith("local-"))
    for label, ph in (("masters", pfull), ("web", pweb)):
        if ph:
            print(f"  {len(ph)} {label} files still UPLOADING (placeholder id): {ph[:3]}")
    if mfull or mweb or pfull or pweb:
        print("  NOT WRITING: some files have no real Drive id yet. Rerun when sync finishes.")
        return
    if "--write" in sys.argv:
        json.dump(full, open(FULL, "w"), indent=1)
        json.dump(web, open(WEBM, "w"), indent=1)
        print(f"  wrote {os.path.basename(FULL)} and {os.path.basename(WEBM)}")
    else:
        print("  (report only; pass --write to save)")


if __name__ == "__main__":
    main()
