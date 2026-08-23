#!/usr/bin/env python3
"""Lands a book lane saved from wednesday.html into the record.

Noah, 2026-08-23: "one click sends to you and saves... not to disk, to
somewhere you can access like drive or github... I just screw it up if it's
her desk... it just needs to go to a location we can grab."

WHERE A SAVE GOES (the page decides, first one that answers wins):
  1. the Drive endpoint, once _work/book_inbox.gs is deployed and its URL is in
     book_send.json. One dated JSON file per save, in a Drive folder that is
     also a local mount on the Mac.
  2. the noah@abba-photo.com inbox, through the Web3Forms account the vote page
     already uses. VERIFIED WORKING 2026-08-23: subject "Kingswood book: N
     frames", and the whole lane rides in the lane_json field. This needs no
     setup, which is why it is the standing fallback.
  3. a local file, only when the network refuses, so a set made in the room is
     never lost.

This script takes route 1 or 3, from a file on disk or the Drive mount. Route 2
is read straight out of the inbox with the Gmail connector, no script needed.

Whatever the route, it does three things:

  1. BANKS it under _work/book_bank/ with the time it was made. Nothing is ever
     overwritten, so every pass survives, including the ones replaced later.
  2. LANDS it in _work/arrangement_kw.json, the record build_book.py lays the
     PDF out from. The previous record is backed up first.
  3. REPORTS the difference against the lane that was there before, so a change
     made in conversation is never silent.

    python3 import_book.py                  take whatever is waiting
    python3 import_book.py --watch          take each save as it lands
    python3 import_book.py --list           show the bank
    python3 import_book.py <path>           take a specific file
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DROP = Path.home() / "Downloads" / "kingswood_book.json"
WORK = HERE / "_work"
ARR = WORK / "arrangement_kw.json"
BANK = WORK / "book_bank"
LANE = "The book"


def stamp(when=None):
    return (when or datetime.now()).strftime("%Y-%m-%dT%H-%M-%S")


def read_drop(path: Path):
    """Read and sanity-check a saved lane. A bad file is refused, never landed."""
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        return None, f"not readable JSON: {e}"
    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        return None, "no frames in the file"
    if not all(isinstance(n, int) for n in frames):
        return None, "frames must be numbers"
    if len(set(frames)) != len(frames):
        dupes = sorted({n for n in frames if frames.count(n) > 1})
        return None, f"the same frame appears twice: {dupes}"
    return data, None


def current_lane():
    arrangement = json.loads(ARR.read_text())
    for g in arrangement["groups"]:
        if g["name"] == LANE:
            return arrangement, g
    g = {"name": LANE, "frames": []}
    arrangement["groups"].append(g)
    return arrangement, g


def describe(before, after):
    """What actually changed, in the terms a person would use."""
    added = [n for n in after if n not in before]
    removed = [n for n in before if n not in after]
    kept_before = [n for n in before if n in after]
    kept_after = [n for n in after if n in before]
    lines = []
    if added:
        lines.append(f"added {len(added)}: {added}")
    if removed:
        lines.append(f"removed {len(removed)}: {removed}")
    if not added and not removed and kept_before != kept_after:
        lines.append("same frames, new order")
    elif kept_before != kept_after and (added or removed):
        lines.append("the frames that stayed were also reordered")
    if not lines:
        lines.append("no change, the lane already read this way")
    return lines


def take(path: Path, quiet=False):
    data, problem = read_drop(path)
    if problem:
        print(f"REFUSED {path.name}: {problem}")
        print("  the record was not touched")
        return False

    frames = data["frames"]
    BANK.mkdir(parents=True, exist_ok=True)

    # 1. bank it, permanently, before anything else can go wrong
    when = stamp()
    banked = BANK / f"book_{when}.json"
    banked.write_text(json.dumps(data, indent=1) + "\n")

    # 2. land it, with the old record kept
    arrangement, group = current_lane()
    before = list(group["frames"])
    backup = WORK / f"arrangement_kw.{when}.bak"
    shutil.copy2(ARR, backup)
    group["frames"] = frames
    ARR.write_text(json.dumps(arrangement, indent=1) + "\n")

    # 3. say what moved
    print(f"BANKED  {banked.relative_to(HERE)}")
    print(f"LANDED  the book lane is now {len(frames)} frames (was {len(before)})")
    for line in describe(before, frames):
        print(f"  {line}")
    if data.get("saved"):
        print(f"  saved from the page at {data['saved']}")

    # the drop is consumed so the next save is never ambiguous
    path.unlink()
    print(f"  {path.name} taken, the Downloads copy is cleared")
    print("  next: python3 build_wednesday.py   and   python3 build_book.py")
    return True


def watch():
    print(f"watching {DROP}")
    print("click Save the book on the page; each save banks and lands here.")
    print("ctrl-c to stop.\n")
    try:
        while True:
            if DROP.exists():
                # let the browser finish writing before reading
                size = -1
                while size != DROP.stat().st_size:
                    size = DROP.stat().st_size
                    time.sleep(0.4)
                print(f"[{datetime.now():%H:%M:%S}] a save landed")
                take(DROP)
                print()
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("\nstopped watching")


def show_bank():
    if not BANK.exists():
        print("nothing banked yet")
        return
    rows = sorted(BANK.glob("book_*.json"), reverse=True)
    if not rows:
        print("nothing banked yet")
        return
    print(f"{len(rows)} banked sets, newest first:")
    for r in rows:
        try:
            d = json.loads(r.read_text())
            n = len(d.get("frames", []))
        except Exception:
            n = "?"
        print(f"  {r.stem.replace('book_', '')}   {n} frames   {r.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true", help="take each save as it lands")
    ap.add_argument("--list", action="store_true", help="show the bank")
    ap.add_argument("file", nargs="?", help="a specific saved file, instead of Downloads")
    a = ap.parse_args()

    if a.list:
        show_bank()
    elif a.watch:
        watch()
    else:
        target = Path(a.file).expanduser() if a.file else DROP
        if not target.exists():
            print(f"nothing waiting at {target}")
            print("click Save the book on the page first, or pass a file path")
        else:
            take(target)
