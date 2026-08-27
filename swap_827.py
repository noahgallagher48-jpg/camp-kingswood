#!/usr/bin/env python3
"""Swap the delivery over to the 8/27 set. Nothing is deleted.

Noah, 2026-08-27: use the 8/27 images, keep the systems the same, and for any
old capture with no match in the new export, "if no match keep them." Those 15
were carried into the source folder as Kwood827-901..915 (see that folder's
_CARRIED_FORWARD.txt), so the pool is 298.

WHY THE ARRANGEMENT IS RESET. The aside list and every group in
arrangement_kw.json are lists of FRAME NUMBERS, and a frame number now points
at a different photograph. Carrying the old arrangement forward would fence
frames nobody chose to fence and seed a book lane nobody chose. It is archived,
not discarded, and the fresh one carries the same group names so the tools that
read it by name keep working.

Two selection stores, per his ask: his picks live in the arrangement as they
always have, and hers land in _work/selections_client.json, separate, so a
client layout can never overwrite the owner's.

    python3 swap_827.py --check   report what would happen, change nothing
    python3 swap_827.py --go      do it
"""
import json, os, shutil, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
NEW = os.path.join(HERE, "img_827")
WORK = os.path.join(HERE, "_work")
ARR = os.path.join(WORK, "arrangement_kw.json")
CLIENT_SEL = os.path.join(WORK, "selections_client.json")
TIERS = ("web", "present", "thumb")
KEEP_DIRS = ("lastjune", "rooms")          # not frame tiers; must survive
STAMP = "pre827"


def counts():
    out = {}
    for t in TIERS:
        out[t] = (len(os.listdir(os.path.join(IMG, t))) if os.path.isdir(os.path.join(IMG, t)) else 0,
                  len(os.listdir(os.path.join(NEW, t))) if os.path.isdir(os.path.join(NEW, t)) else 0)
    return out


def check():
    print("SWAP TO THE 8/27 SET, dry run\n")
    ok = True
    for t, (old, new) in counts().items():
        flag = "" if new else "   <== NEW TIER EMPTY, ingest not finished"
        if not new:
            ok = False
        print(f"  img/{t:<8} {old:>4} now  ->  {new:>4} after{flag}")
    n = {c[1] for c in counts().values()}
    if len(n) > 1:
        print(f"\n  TIERS DISAGREE {n}: ingest is still running or a tier failed.")
        ok = False
    print(f"\n  preserved untouched: {', '.join(KEEP_DIRS)}")
    print(f"  old tiers archived to: img_{STAMP}/  (kept, not deleted)")
    if os.path.exists(ARR):
        a = json.load(open(ARR))
        print(f"\n  arrangement now: {len(a.get('aside', []))} aside, "
              f"{len(a.get('groups', []))} groups "
              f"({', '.join(g['name'] for g in a.get('groups', []))})")
        print(f"  -> archived to arrangement_kw.{STAMP}.bak, replaced with empty groups")
        print("     because frame numbers now point at different photographs")
    print(f"\n  {'READY' if ok else 'NOT READY'}")
    return ok


def go():
    if not check():
        sys.exit("\nrefusing to swap while the above is unresolved")
    print("\n--- swapping ---")
    arch = os.path.join(HERE, f"img_{STAMP}")
    os.makedirs(arch, exist_ok=True)
    for t in TIERS:
        src, dst = os.path.join(IMG, t), os.path.join(arch, t)
        if os.path.isdir(src) and not os.path.isdir(dst):
            shutil.move(src, dst)
            print(f"  archived img/{t} -> img_{STAMP}/{t}")
        shutil.move(os.path.join(NEW, t), os.path.join(IMG, t))
        print(f"  img_827/{t} -> img/{t}")

    if os.path.exists(ARR):
        bak = os.path.join(WORK, f"arrangement_kw.{STAMP}.bak")
        if not os.path.exists(bak):
            shutil.copy2(ARR, bak)
            print(f"  arrangement archived -> {os.path.basename(bak)}")
    fresh = {"groups": [{"name": "Noah's Picks", "frames": []},
                        {"name": "The book", "frames": []}],
             "aside": [], "ungrouped": [],
             "reset": "2026-08-27, swapped to the 8/27 set"}
    json.dump(fresh, open(ARR, "w"), indent=1)
    print("  arrangement reset: empty picks, empty book lane, nothing fenced")

    if not os.path.exists(CLIENT_SEL):
        json.dump({"who": "Camp Kingswood", "sets": [],
                   "note": "client layout selections; never written by the owner's tools"},
                  open(CLIENT_SEL, "w"), indent=1)
        print(f"  created {os.path.basename(CLIENT_SEL)} for her selections")

    print("\nnext: python3 dims_827.py && python3 build_delivery.py build")


if __name__ == "__main__":
    if "--go" in sys.argv:
        go()
    else:
        check()
