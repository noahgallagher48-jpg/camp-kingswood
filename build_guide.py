#!/usr/bin/env python3
"""Builds the Camp Kingswood image use guide (guide.html).

This is the "written instructions" half of the August 30 deliverable: the
agreement owes the camp its summer media library "closed and organized with
written instructions", and the delivery page is the library. The guide is what
tells them what they are holding and what to do with it.

Ported from the Ramah in the Rockies guide (guide v2, the client-guide
template): the information architecture is what carried the value there, so it
carries over. Named sections, per-frame print guidance off the master's true
resolution, one click to both file sizes, a lightbox. What changes is the
camp, the brand, and the instructions.

THE POOL IS IMPORTED, NOT RECOMPUTED. build_delivery.pool() is the single
answer to "what does the camp see", and the aside list is its only fence. A
guide that built its own pool would drift from the delivery page the first time
Noah set a frame aside, and the camp would find a photograph in the guide that
is not in the library.

VALUE IS ASSERTED AT DELIVERY (doctrine): the justification lives here, in the
guide, not in why-lines under the frames. A frame carries its label and its
sizes. The guide carries the reasoning.

EDITORIAL PLACEMENT IS NOAH'S. The themed sections are his own arrangement
groups, read from _work/arrangement_kw.json. Working labels ("New since your
last pass") are not themes and never reach the client; frames he has not
threaded sit in the closing section in shoot order, which is honest, rather
than being grouped by a guess about what they are for.

    python3 build_guide.py
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser("~/Abba_Photo/dashboard/tools"))

from build_delivery import pool, FOLDER_URL, ZIP_URL
from print_sizes import print_line

OUT = os.path.join(HERE, "guide.html")
DIMS = os.path.join(HERE, "_work", "dims_kw.json")
DRIVE_IDS = os.path.join(HERE, "_work", "drive_ids_kw.json")
WEB_IDS = os.path.join(HERE, "_work", "drive_web_ids_kw.json")
ARR = os.path.join(HERE, "_work", "arrangement_kw.json")
DELIVERY_URL = "delivery.html"

# His groups, in the order the guide should read them, mapped to the name the
# camp sees. "Proposed forty-two" is his working title for the agreement's
# headline selection; the camp knows it as the forty-two. Any group not named
# here is a working label and stays internal.
SECTIONS = [
    ("Proposed forty-two", "The forty-two",
     "The agreement's twelve campscapes and thirty storytelling candids. "
     "Forty-two is a floor rather than a cap, and the selection grew in the edit."),
    ("Shabbat", "Shabbat", ""),
    ("The sign", "The sign", ""),
    ("Night and stars", "Night and stars", ""),
]
REST = ("The rest of the week", "In the order it happened, from Wednesday evening "
        "through Sunday.")

esc = lambda s: html.escape(s or "")
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def load():
    by_num, keep, picks = pool()
    dims = json.load(open(DIMS))
    drive = json.load(open(DRIVE_IDS)) if os.path.exists(DRIVE_IDS) else {}
    web = json.load(open(WEB_IDS)) if os.path.exists(WEB_IDS) else {}
    uc = lambda i: f"https://drive.google.com/uc?export=download&id={i}" if i else None
    rows = {}
    for n in keep:
        f = by_num[n]
        w, h = dims.get(f, (0, 0))
        p = print_line(w, h) if w else {"metal": None, "paper": None,
                                        "canvas": None, "note": None}
        rows[n] = {"n": n, "f": f, "w": w, "h": h, "print": p,
                   "d": uc(drive.get(f)), "wb": uc(web.get(f)),
                   "pick": n in picks}
    return rows, keep, picks


def print_html(r):
    p = r["print"]
    if p["note"]:
        return f'<div class="note">{esc(p["note"])}</div>'
    parts = [(p["metal"], "metal"), (p["paper"], "paper"), (p["canvas"], "canvas")]
    inner = " &middot; ".join(f'<b>{s.replace("x", "&times;")}&Prime;</b> {lab}'
                              for s, lab in parts if s)
    return f'<div class="sz">Prints to {inner}</div>' if inner else ""


def card(r, sec):
    dl = []
    if r["wb"]:
        dl.append(f'<a href="{r["wb"]}" target="_blank" rel="noopener">Web</a>')
    if r["d"]:
        dl.append(f'<a href="{r["d"]}" target="_blank" rel="noopener">Full res</a>')
    # The pill marks a frame as one of the selected. Inside the forty-two's own
    # section that is what the heading already says, so it only earns its place
    # where a reader would not otherwise know.
    pill = ('<span class="pill pick">The forty-two</span>'
            if r["pick"] and sec != "The forty-two" else "")
    return f'''<figure class="card">
  <button class="ph" data-open="{r["n"]}" aria-label="Open frame {r["n"]}">
    <img loading="lazy" src="img/thumb/{r["f"]}" alt="Camp Kingswood, frame {r["n"]}">
    <span class="num">{r["n"]}</span></button>
  <figcaption>
    <div class="pills">{pill}</div>
    {print_html(r)}
    <div class="dl">{"".join(dl)}</div>
  </figcaption>
</figure>'''


def build():
    rows, keep, picks = load()
    groups = {g["name"]: g["frames"] for g in json.load(open(ARR))["groups"]}

    body, nav, placed = [], [], set()
    for src, title, lede in SECTIONS:
        seen = set()
        frames = [n for n in groups.get(src, [])
                  if n in rows and not (n in seen or seen.add(n))]
        if not frames:
            continue
        # The forty-two is a selection across the whole set, not a bucket that
        # spends its frames: only the themed sections claim a frame as placed,
        # or every pick would vanish from the section it actually belongs to.
        if src != "Proposed forty-two":
            placed.update(frames)
        body.append(
            f'<h2 class="mv" id="{slug(title)}">{esc(title)}'
            f'<span>{len(frames)} frames</span></h2><section>'
            + (f'<p class="lede">{esc(lede)}</p>' if lede else "")
            + f'<div class="cards">{"".join(card(rows[n], title) for n in frames)}</div>'
            "</section>")
        nav.append(f'<a href="#{slug(title)}">{esc(title)}</a>')

    rest = [n for n in keep if n not in placed]
    if rest:
        title, lede = REST
        body.append(
            f'<h2 class="mv" id="{slug(title)}">{esc(title)}'
            f'<span>{len(rest)} frames</span></h2><section>'
            f'<p class="lede">{esc(lede)}</p>'
            f'<div class="cards">{"".join(card(rows[n], title) for n in rest)}</div>'
            "</section>")
        nav.append(f'<a href="#{slug(title)}">{esc(title)}</a>')

    data = [{"n": n, "f": rows[n]["f"], "d": rows[n]["d"], "wb": rows[n]["wb"],
             "p": [rows[n]["print"]["metal"], rows[n]["print"]["paper"],
                   rows[n]["print"]["canvas"]], "pn": rows[n]["print"]["note"]}
            for n in keep]

    out = (PAGE.replace("__NAV__", "".join(nav))
               .replace("__BODY__", "\n".join(body))
               .replace("__DATA__", json.dumps(data))
               .replace("__N__", str(len(keep)))
               .replace("__NP__", str(len(picks)))
               .replace("__FOLDER__", FOLDER_URL)
               .replace("__ZIP__", ZIP_URL)
               .replace("__DELIVERY__", DELIVERY_URL))
    open(OUT, "w").write(out)

    no_full = [n for n in keep if not rows[n]["d"]]
    no_web = [n for n in keep if not rows[n]["wb"]]
    notes = sum(1 for n in keep if rows[n]["print"]["note"])
    print(f"wrote {OUT}\n  {len(keep)} frames · {len(picks)} in the forty-two · "
          f"{len(rest)} in the closing section · {notes} print notes")
    if no_full: print(f"  FULL RES MISSING for {no_full}")
    if no_web:  print(f"  WEB MISSING for {no_web}")
    if not no_full and not no_web:
        print("  every frame has both file sizes one click away")


PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Camp Kingswood &middot; Image Guide 2026</title><style>
/* The camp's own brand, read off campkingswood.org's live computed styles
   2026-08-20: ground #062A40, vermilion #DB3A00, warm white #F3F1EC.
   Raleway is SIL OFL and embedded from this repo. */
@font-face{font-family:Raleway;src:url(fonts/raleway-400.woff2) format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:Raleway;src:url(fonts/raleway-600.woff2) format('woff2');font-weight:600;font-display:swap}
@font-face{font-family:Raleway;src:url(fonts/raleway-800.woff2) format('woff2');font-weight:800;font-display:swap}
:root{--ground:#062A40;--panel:#0C3A54;--line:rgba(243,241,236,.13);
      --ink:#F3F1EC;--muted:#9DB4C4;--faint:#6D8698;
      --accent:#DB3A00;--warm:#F0A882;--sand:#E8DFD2}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:62px}
body{background:var(--ground);color:var(--ink);
     font-family:Raleway,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
     font-size:15px;line-height:1.55}
a{color:var(--warm);text-decoration:none}a:hover{text-decoration:underline}
nav{position:sticky;top:0;z-index:20;background:rgba(6,42,64,.95);backdrop-filter:blur(6px);
    border-bottom:1px solid var(--line);padding:0 16px}
nav .in{max-width:1280px;margin:0 auto;display:flex;gap:2px;overflow-x:auto}
nav a{font-size:11.5px;letter-spacing:.05em;color:var(--muted);padding:12px 11px;white-space:nowrap}
nav a:hover{color:var(--accent);text-decoration:none}
header{max-width:820px;margin:0 auto;padding:52px 20px 30px;text-align:center}
h1{font-weight:800;font-size:clamp(30px,5.5vw,46px);letter-spacing:-.015em;color:var(--ink)}
header .date{color:var(--muted);font-size:14.5px;margin-top:6px}
header .lede{color:var(--muted);font-size:14.5px;margin-top:16px;max-width:62ch;
             margin-left:auto;margin-right:auto}
.opts{margin-top:20px}
.opts a{border:1px solid rgba(219,58,0,.55);border-radius:4px;padding:8px 15px;
        font-size:12.5px;display:inline-block;margin:3px 2px;color:var(--ink)}
.opts a:hover{background:rgba(219,58,0,.15);text-decoration:none}
.start{max-width:820px;margin:8px auto 0;padding:26px 20px 6px}
.start h2{font-weight:800;font-size:22px;color:var(--ink);margin-bottom:4px}
.start .sub{color:var(--faint);font-size:12px;letter-spacing:.13em;
            text-transform:uppercase;margin-bottom:16px}
.start dl{border-top:1px solid var(--line)}
.start dt{font-weight:600;font-size:15px;color:var(--ink);
          padding:16px 0 5px;border-top:1px solid var(--line)}
.start dt:first-of-type{border-top:0}
.start dd{color:var(--muted);font-size:14px;line-height:1.62;padding-bottom:4px;max-width:68ch}
.start dd b{color:var(--ink);font-weight:600}
h2.mv{max-width:1280px;margin:46px auto 0;padding:0 20px;font-weight:800;font-size:26px;
      color:var(--ink);display:flex;align-items:baseline;gap:12px}
h2.mv span{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}
section{max-width:1280px;margin:0 auto;padding:14px 20px 4px}
.lede{color:var(--muted);font-size:13.5px;max-width:70ch;margin-bottom:12px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;overflow:hidden;
      content-visibility:auto;contain-intrinsic-size:260px 300px}
.card .ph{display:block;position:relative;width:100%;padding:0;border:0;background:none;cursor:pointer}
.card img{width:100%;aspect-ratio:3/2;object-fit:cover;display:block}
.card .num{position:absolute;left:7px;bottom:6px;font-size:10.5px;font-weight:700;color:#fff;
           text-shadow:0 1px 5px #000}
figcaption{padding:10px 12px 12px}
.pills{display:flex;flex-wrap:wrap;gap:5px}
.pills:not(:empty){margin-bottom:7px}
.pill{font-size:9.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
      padding:2.5px 7px;border-radius:3px}
.pill.pick{background:var(--accent);color:#fff}
.sz{font-size:12px;color:var(--muted);line-height:1.5}
.sz b{color:var(--ink);font-weight:600}
.note{font-size:12px;color:var(--sand);line-height:1.5}
.dl{margin-top:9px;display:flex;gap:7px}
.dl a{font-size:11.5px;border:1px solid rgba(219,58,0,.5);border-radius:4px;padding:4px 10px;
      color:var(--ink)}
.dl a:hover{background:rgba(219,58,0,.15);text-decoration:none}
footer{max-width:1280px;margin:44px auto 0;padding:20px 20px 48px;border-top:1px solid var(--line);
       display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;
       color:var(--faint);font-size:12.5px}
#lb{position:fixed;inset:0;z-index:40;background:#000;display:none}
#lb.on{display:block}
#lb img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}
#lb .zone{position:absolute;top:0;bottom:0;width:28%;z-index:2;cursor:pointer;
          background:none;border:0;padding:0;appearance:none}
#lb .zl{left:0}#lb .zr{right:0}
#lb .x{position:absolute;top:10px;right:16px;z-index:3;background:none;border:0;
       color:#9DB4C4;font-size:32px;cursor:pointer;line-height:1}
#lb .bar{position:absolute;bottom:0;left:0;right:0;z-index:3;display:flex;gap:12px;
         align-items:center;justify-content:center;padding:14px;flex-wrap:wrap;
         background:linear-gradient(transparent,rgba(0,0,0,.78))}
#lb .bar .m{font-size:12px;color:#9DB4C4}
#lb .bar .sz{font-size:12px;color:#DCE5EB}
#lb .bar a{font-size:12px;border:1px solid rgba(219,58,0,.6);border-radius:4px;padding:6px 13px;
           color:#F3F1EC}
@media (max-width:680px){header{padding:36px 16px 22px}section{padding:12px 14px 4px}
  .start{padding:22px 16px 6px}}
</style></head><body>

<nav><div class=in><a href="#start">Start here</a>__NAV__</div></nav>

<header>
  <h1>Camp Kingswood</h1>
  <p class=date>Bridgton, Maine &middot; Summer 2026</p>
  <p class=lede>__N__ photographs from the week of August 5, each one in two file sizes,
     with the largest size it prints at on every material. __NP__ of them are the forty-two.</p>
  <p class=opts>
    <a href="__FOLDER__" target=_blank rel=noopener>All full res</a>
    <a href="__ZIP__">Everything for web</a>
    <a href="__DELIVERY__">The delivery page</a>
  </p>
</header>

<div class=start id=start>
  <h2>Start here</h2>
  <p class=sub>How to use this library</p>
  <dl>
    <dt>Which file to use</dt>
    <dd><b>Web</b> is 3840 pixels on the long edge. It is sized for screens: the website,
        email, social, slide decks, anything anyone reads on a device. <b>Full res</b> is the
        developed file at its full size. Use it for print, and for anything a designer will
        crop into. They are the same photograph. The difference is how much room there is to
        enlarge or crop before the pixels show.</dd>

    <dt>Printing</dt>
    <dd>Every frame lists the largest size it prints at on each material. <b>Metal</b> and
        acrylic hold the most detail and ask the most resolution, <b>photo paper</b> a little
        less, <b>canvas</b> least, because the weave and the viewing distance forgive it.
        These are stock sizes, orderable as listed with no custom cutting, and each one
        matches that frame's own proportions, so nothing is cropped to fit. A few frames
        print true only as a custom cut, and those say so instead of naming a size.</dd>

    <dt>Credit</dt>
    <dd>Photograph by Noah Gallagher, wherever a credit line fits. Every file carries it in
        its metadata as well, so it travels with the photograph into whatever system holds
        it next.</dd>

    <dt>Finding one again</dt>
    <dd>Every file carries the date it was made and a set of keywords: Camp Kingswood,
        Bridgton Maine, and the rest. Search any of those in whatever holds your library and
        the set comes back together. The frame numbers on the thumbnails are the same numbers
        in the filenames, so a number is enough to ask about a specific photograph.</dd>

    <dt>One thing worth knowing</dt>
    <dd>When you need a smaller file, export a fresh one from the web or full res copy rather
        than re-saving the file you have. A JPEG loses a little every time it is saved again,
        and re-saving tends to drop the date and the credit along with it.</dd>
  </dl>
</div>

__BODY__

<footer>
  <span>Photographs by Noah Gallagher</span>
  <span>Abba Photo &middot; <a href="https://www.abba-photo.com" target=_blank rel=noopener>abba-photo.com</a></span>
</footer>

<div id=lb><img id=lbi alt="Camp Kingswood, Summer 2026">
  <button class="zone zl" type=button aria-label=Previous></button>
  <button class="zone zr" type=button aria-label=Next></button>
  <button class=x type=button aria-label=Close>&times;</button>
  <div class=bar><span class=m id=lbm></span><span class=sz id=lbsz></span>
    <a id=lbw target=_blank rel=noopener>Web</a><a id=lbf target=_blank rel=noopener>Full res</a></div>
</div>

<script>
var DATA=__DATA__, BY={};
DATA.forEach(function(r,i){BY[r.n]=i;});
function $(i){return document.getElementById(i);}
function printText(r){
  if(r.pn) return r.pn;
  var m=["metal","paper","canvas"],out=[];
  for(var i=0;i<3;i++) if(r.p[i]) out.push("<b>"+r.p[i].replace("x","\\u00d7")+"\\u2033</b> "+m[i]);
  return out.length? "Prints to "+out.join(" \\u00b7 ") : "";
}
var cur=0;
function openLb(i){cur=i;paintLb();$("lb").className="on";}
function paintLb(){if(cur<0)cur=DATA.length-1;if(cur>=DATA.length)cur=0;
  var r=DATA[cur];$("lbi").src="img/present/"+r.f;
  $("lbm").textContent=r.n+"  \\u00b7  "+(cur+1)+" / "+DATA.length;
  $("lbsz").innerHTML=printText(r);
  $("lbw").href=r.wb||"__FOLDER__";
  $("lbf").href=r.d||"__FOLDER__";}
document.addEventListener("click",function(e){
  var b=e.target.closest("[data-open]");
  if(b){e.preventDefault();openLb(BY[b.getAttribute("data-open")]);}});
document.querySelector("#lb .zl").onclick=function(){cur--;paintLb();};
document.querySelector("#lb .zr").onclick=function(){cur++;paintLb();};
document.querySelector("#lb .x").onclick=function(){$("lb").className="";};
document.addEventListener("keydown",function(e){
  if($("lb").className!=="on")return;
  if(e.key==="Escape")$("lb").className="";
  else if(e.key==="ArrowRight"){cur++;paintLb();}
  else if(e.key==="ArrowLeft"){cur--;paintLb();}});
</script>
<script data-goatcounter="https://abbaphoto.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body></html>"""


if __name__ == "__main__":
    build()
