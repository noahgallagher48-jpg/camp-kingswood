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
# camp sees. The selection is NOAH'S PICKS (his ruling 2026-08-23: the client
# is not counting frames, so no count is ever the label). Any group not named
# here is a working label and stays internal.
SECTIONS = [
    ("Noah's Picks", "Noah's Picks",
     "The frames Noah selected across the week. The agreement sets twelve "
     "mastered campscapes and thirty storytelling candids as the floor."),
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
    parts = [("Metal", p["metal"]), ("Paper", p["paper"]),
             ("Canvas", p["canvas"])]
    rows = "".join(
        f'<dt>{lab}</dt><dd>{size.replace("x", "&times;")}&Prime;</dd>'
        for lab, size in parts if size)
    return (f'<dl class="print-grid" aria-label="Largest standard print sizes">'
            f'{rows}</dl>') if rows else ""


def card(r, sec):
    dl = []
    if r["wb"]:
        dl.append(f'<a href="{r["wb"]}" target="_blank" rel="noopener">Web</a>')
    if r["d"]:
        dl.append(f'<a href="{r["d"]}" target="_blank" rel="noopener">Full res</a>')
    # The pill marks a frame as one of the selected. Inside the Picks' own
    # section that is what the heading already says, so it only earns its place
    # where a reader would not otherwise know.
    pill = ('<span class="pill pick">Noah\'s Picks</span>'
            if r["pick"] and sec != "Noah's Picks" else "")
    p = r["print"]
    return f'''<figure class="card" data-frame="{r["n"]}" data-section="{slug(sec)}"
  data-pick="{str(r["pick"]).lower()}" data-metal="{esc(p["metal"] or "")}"
  data-paper="{esc(p["paper"] or "")}" data-canvas="{esc(p["canvas"] or "")}">
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

    body, nav, section_options, placed = [], [], [], set()
    for src, title, lede in SECTIONS:
        seen = set()
        frames = [n for n in groups.get(src, [])
                  if n in rows and not (n in seen or seen.add(n))]
        if not frames:
            continue
        # Noah's Picks is a selection across the whole set, not a bucket that
        # spends its frames: only the themed sections claim a frame as placed,
        # or every pick would vanish from the section it actually belongs to.
        if src != "Noah's Picks":
            placed.update(frames)
        body.append(
            f'<div class="group" data-group="{slug(title)}">'
            f'<h2 class="mv" id="{slug(title)}">{esc(title)}</h2><section>'
            + (f'<p class="lede">{esc(lede)}</p>' if lede else "")
            + f'<div class="cards">{"".join(card(rows[n], title) for n in frames)}</div>'
            "</section></div>")
        nav.append(f'<a href="#{slug(title)}">{esc(title)}</a>')
        section_options.append(
            f'<option value="{slug(title)}">{esc(title)}</option>')

    rest = [n for n in keep if n not in placed]
    if rest:
        title, lede = REST
        body.append(
            f'<div class="group" data-group="{slug(title)}">'
            f'<h2 class="mv" id="{slug(title)}">{esc(title)}</h2><section>'
            f'<p class="lede">{esc(lede)}</p>'
            f'<div class="cards">{"".join(card(rows[n], title) for n in rest)}</div>'
            "</section></div>")
        nav.append(f'<a href="#{slug(title)}">{esc(title)}</a>')
        section_options.append(
            f'<option value="{slug(title)}">{esc(title)}</option>')

    data = [{"n": n, "f": rows[n]["f"], "d": rows[n]["d"], "wb": rows[n]["wb"],
             "p": [rows[n]["print"]["metal"], rows[n]["print"]["paper"],
                   rows[n]["print"]["canvas"]], "pn": rows[n]["print"]["note"]}
            for n in keep]

    out = (PAGE.replace("__NAV__", "".join(nav))
               .replace("__SECTION_OPTIONS__", "".join(section_options))
               .replace("__BODY__", "\n".join(body))
               .replace("__DATA__", json.dumps(data))
               .replace("__FOLDER__", FOLDER_URL)
               .replace("__ZIP__", ZIP_URL)
               .replace("__DELIVERY__", DELIVERY_URL))
    open(OUT, "w").write(out)

    no_full = [n for n in keep if not rows[n]["d"]]
    no_web = [n for n in keep if not rows[n]["wb"]]
    notes = sum(1 for n in keep if rows[n]["print"]["note"])
    print(f"wrote {OUT}\n  {len(keep)} frames · {len(picks)} in Noah's Picks · "
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
html{scroll-behavior:smooth;scroll-padding-top:148px}
body{background:var(--ground);color:var(--ink);
     font-family:Raleway,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
     font-size:15px;line-height:1.55}
a{color:var(--warm);text-decoration:none}a:hover{text-decoration:underline}
nav{position:sticky;top:0;z-index:20;background:rgba(6,42,64,.95);backdrop-filter:blur(6px);
    border-bottom:1px solid var(--line);padding:0 16px}
nav .in{max-width:1280px;margin:0 auto;display:flex;gap:2px;overflow-x:auto}
nav a{font-size:11.5px;letter-spacing:.05em;color:var(--muted);padding:12px 11px;white-space:nowrap;
      border-bottom:2px solid transparent}
nav a:hover{color:var(--accent);text-decoration:none}
nav a.active{color:var(--ink);border-bottom-color:var(--accent)}
header{max-width:820px;margin:0 auto;padding:44px 20px 24px;text-align:center}
h1{font-weight:800;font-size:clamp(30px,5.5vw,46px);letter-spacing:-.015em;color:var(--ink)}
header .date{color:var(--muted);font-size:14.5px;margin-top:6px}
header .lede{color:var(--muted);font-size:14.5px;margin-top:16px;max-width:62ch;
             margin-left:auto;margin-right:auto}
.opts{margin-top:20px}
.opts a{border:1px solid rgba(219,58,0,.55);border-radius:4px;padding:8px 15px;
        font-size:12.5px;display:inline-block;margin:3px 2px;color:var(--ink)}
.opts a:hover{background:rgba(219,58,0,.15);text-decoration:none}
.tools{position:sticky;top:41px;z-index:19;background:rgba(6,42,64,.97);
       border-bottom:1px solid var(--line);border-top:1px solid var(--line)}
.tools .in{max-width:1280px;margin:0 auto;padding:10px 20px;display:grid;
           grid-template-columns:minmax(190px,1.2fr) minmax(150px,.8fr) minmax(190px,1fr) auto;
           gap:8px;align-items:end}
.field{display:flex;flex-direction:column;gap:3px}
.field label{font-size:9.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}
.find{display:flex;gap:6px}.find input{min-width:0;flex:1}
input,select,.find button{height:36px;border:1px solid rgba(243,241,236,.22);border-radius:4px;
       background:#092F46;color:var(--ink);font:inherit;font-size:12px;padding:0 10px}
select{width:100%}.find button{cursor:pointer;border-color:rgba(219,58,0,.7);font-weight:700}
.find button:hover{background:rgba(219,58,0,.16)}
.tool-status{font-size:11px;color:var(--muted);padding-bottom:8px;white-space:nowrap}
.tool-status.bad{color:var(--warm)}
.recent{max-width:1280px;margin:0 auto;padding:0 20px 9px;display:none;align-items:center;gap:5px;flex-wrap:wrap}
.recent.on{display:flex}.recent>span{font-size:9.5px;font-weight:700;letter-spacing:.1em;
       text-transform:uppercase;color:var(--faint);margin-right:2px}
.recent button{border:0;background:rgba(243,241,236,.09);color:var(--ink);border-radius:3px;
       font:inherit;font-size:10.5px;padding:3px 7px;cursor:pointer}
.recent button:hover{background:var(--accent)}
.start{max-width:820px;margin:18px auto 0;padding:0 20px 6px}
.start summary{list-style:none;cursor:pointer;border:1px solid var(--line);border-radius:6px;
       padding:15px 17px;font-weight:800;font-size:18px;color:var(--ink);display:flex;
       align-items:baseline;justify-content:space-between;gap:12px}
.start summary::-webkit-details-marker{display:none}
.start summary:after{content:'+';color:var(--accent);font-size:23px;line-height:1}
.start[open] summary:after{content:'\2212'}
.start summary span{font-weight:400;font-size:11px;color:var(--faint);letter-spacing:.05em}
.start .manual{padding:18px 0 4px}
.start dl{border-top:1px solid var(--line)}
.start dt{font-weight:600;font-size:15px;color:var(--ink);
          padding:16px 0 5px;border-top:1px solid var(--line)}
.start dt:first-of-type{border-top:0}
.start dd{color:var(--muted);font-size:14px;line-height:1.62;padding-bottom:4px;max-width:68ch}
.start dd b{color:var(--ink);font-weight:600}
h2.mv{max-width:1280px;margin:34px auto 0;padding:0 20px;font-weight:800;font-size:26px;
      color:var(--ink);scroll-margin-top:150px}
section{max-width:1280px;margin:0 auto;padding:14px 20px 4px}
.lede{color:var(--muted);font-size:13.5px;max-width:70ch;margin-bottom:12px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;overflow:hidden;
      content-visibility:auto;contain-intrinsic-size:260px 300px}
.card.found{animation:found 1.6s ease-out}
@keyframes found{0%,35%{box-shadow:0 0 0 3px var(--accent)}100%{box-shadow:none}}
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
.print-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);
            border-bottom:1px solid var(--line);padding:6px 0;margin-top:1px}
.print-grid dt{grid-row:1;font-size:8.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
.print-grid dd{grid-row:2;font-size:12px;font-weight:600;color:var(--ink)}
.print-grid dt:nth-of-type(1),.print-grid dd:nth-of-type(1){grid-column:1}
.print-grid dt:nth-of-type(2),.print-grid dd:nth-of-type(2){grid-column:2}
.print-grid dt:nth-of-type(3),.print-grid dd:nth-of-type(3){grid-column:3}
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
@media (max-width:760px){html{scroll-padding-top:214px}.tools .in{padding:9px 14px;
  grid-template-columns:1fr 1fr}.field.find-field{grid-column:1/-1}.tool-status{padding:4px 0 0}
  .recent{padding:0 14px 8px}header{padding:32px 16px 18px}section{padding:12px 14px 4px}
  .start{padding:0 14px 6px}h2.mv{padding:0 14px;scroll-margin-top:216px}
  .cards{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.card{border-radius:4px}
  figcaption{padding:8px}.dl{gap:4px}.dl a{padding:4px 7px}.print-grid dd{font-size:10.5px}}
@media (max-width:350px){.cards{grid-template-columns:1fr}.tools .in{grid-template-columns:1fr}
  .field.find-field{grid-column:auto}.start summary span{display:none}}
</style></head><body>

<nav><div class=in><a href="#start">Start here</a>__NAV__</div></nav>

<header>
  <h1>Camp Kingswood</h1>
  <p class=date>Bridgton, Maine &middot; Summer 2026</p>
  <p class=lede>Photographs from the week of August 5, each one in two file sizes,
     with the largest size it prints at on every material. Noah's Picks are marked.</p>
  <p class=opts>
    <a href="__FOLDER__" target=_blank rel=noopener>All full res</a>
    <a href="__ZIP__">Everything for web</a>
    <a href="__DELIVERY__">The delivery page</a>
  </p>
</header>

<div class=tools aria-label="Guide controls"><div class=in>
  <form class="field find-field" id=find-form>
    <label for=find-frame>Find a frame</label>
    <span class=find><input id=find-frame inputmode=numeric autocomplete=off placeholder="Frame number, for example 108">
      <button type=submit>Find</button></span>
  </form>
  <span class=field><label for=section-filter>Section</label><select id=section-filter>
    <option value=all>All sections</option>__SECTION_OPTIONS__</select></span>
  <span class=field><label for=size-filter>Print capability</label><select id=size-filter>
    <option value=all>Any print size</option>
    <option value=metal-large>Metal: 16&times;24&Prime; or larger</option>
    <option value=paper-large>Paper: 20&times;30&Prime; or larger</option>
    <option value=canvas-large>Canvas: 24&times;36&Prime; or larger</option>
  </select></span>
  <span class=tool-status id=tool-status aria-live=polite>All photographs</span>
</div><div class=recent id=recent><span>Recently viewed</span></div></div>

<details class=start id=start>
  <summary>Start here <span>File sizes, printing, credit, and finding frames</span></summary>
  <div class=manual>
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
</details>

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
var cur=0,lastTrigger=null,recent=[];
try{recent=JSON.parse(localStorage.getItem("kingswood-guide-recent")||"[]");}catch(e){}
function renderRecent(){var box=$("recent"),old=box.querySelectorAll("button");
  old.forEach(function(b){b.remove();});
  recent.forEach(function(n){var b=document.createElement("button");b.type="button";
    b.textContent=n;b.setAttribute("data-jump",n);box.appendChild(b);});
  box.className=recent.length?"recent on":"recent";}
function remember(n){recent=[n].concat(recent.filter(function(x){return x!==n;})).slice(0,8);
  try{localStorage.setItem("kingswood-guide-recent",JSON.stringify(recent));}catch(e){}
  renderRecent();}
function openLb(i,trigger){cur=i;lastTrigger=trigger||null;paintLb();$("lb").className="on";
  document.body.style.overflow="hidden";remember(DATA[cur].n);document.querySelector("#lb .x").focus();}
function closeLb(){$("lb").className="";document.body.style.overflow="";
  if(lastTrigger){lastTrigger.focus();lastTrigger=null;}}
function paintLb(){if(cur<0)cur=DATA.length-1;if(cur>=DATA.length)cur=0;
  var r=DATA[cur];$("lbi").src="img/present/"+r.f;
  $("lbm").textContent=r.n;
  $("lbsz").innerHTML=printText(r);
  $("lbw").href=r.wb||"__FOLDER__";
  $("lbf").href=r.d||"__FOLDER__";}
document.addEventListener("click",function(e){
  var b=e.target.closest("[data-open]");
  if(b){e.preventDefault();openLb(BY[b.getAttribute("data-open")],b);return;}
  var j=e.target.closest("[data-jump]");if(j){jumpFrame(j.getAttribute("data-jump"));}});
document.querySelector("#lb .zl").onclick=function(){cur--;paintLb();};
document.querySelector("#lb .zr").onclick=function(){cur++;paintLb();};
document.querySelector("#lb .x").onclick=closeLb;
document.addEventListener("keydown",function(e){
  if($("lb").className!=="on")return;
  if(e.key==="Escape")closeLb();
  else if(e.key==="ArrowRight"){cur++;paintLb();}
  else if(e.key==="ArrowLeft"){cur--;paintLb();}});
var sectionFilter=$("section-filter"),sizeFilter=$("size-filter"),toolStatus=$("tool-status");
function sizeAtLeast(value,shortSide,longSide){if(!value)return false;
  var p=value.split("x").map(Number).sort(function(a,b){return a-b;});
  return p[0]>=shortSide&&p[1]>=longSide;}
function passesSize(card){var f=sizeFilter.value;
  if(f==="all")return true;
  if(f==="metal-large")return sizeAtLeast(card.dataset.metal,16,24);
  if(f==="paper-large")return sizeAtLeast(card.dataset.paper,20,30);
  return sizeAtLeast(card.dataset.canvas,24,36);}
function applyFilters(){var sec=sectionFilter.value;
  document.querySelectorAll(".group").forEach(function(group){var groupOn=sec==="all"||group.dataset.group===sec;
    var any=false;group.querySelectorAll(".card").forEach(function(card){
      var on=groupOn&&passesSize(card);card.hidden=!on;if(on)any=true;});group.hidden=!any;});
  var labels=[];if(sec!=="all")labels.push(sectionFilter.options[sectionFilter.selectedIndex].text);
  if(sizeFilter.value!=="all")labels.push(sizeFilter.options[sizeFilter.selectedIndex].text);
  toolStatus.textContent=labels.length?labels.join(" \\u00b7 "):"All photographs";toolStatus.className="tool-status";markNav();}
sectionFilter.onchange=applyFilters;sizeFilter.onchange=applyFilters;
function jumpFrame(value){var m=String(value).match(/\\d+/),n=m?String(parseInt(m[0],10)):"";
  var target=document.querySelector('.card[data-frame="'+n+'"]');
  if(!target){toolStatus.textContent="Frame "+(value||"")+" is not in this guide.";toolStatus.className="tool-status bad";return;}
  sectionFilter.value="all";sizeFilter.value="all";applyFilters();
  requestAnimationFrame(function(){target.scrollIntoView({behavior:"smooth",block:"center"});
    target.classList.remove("found");void target.offsetWidth;target.classList.add("found");});}
$("find-form").onsubmit=function(e){e.preventDefault();jumpFrame($("find-frame").value);};
document.querySelectorAll("nav a").forEach(function(a){a.addEventListener("click",function(){
  var id=a.getAttribute("href").slice(1),group=document.querySelector('.group[data-group="'+id+'"]');
  if(group&&group.hidden){sectionFilter.value=id;applyFilters();}});});
var heads=[].slice.call(document.querySelectorAll("h2.mv"));
function markNav(){var active="start",cut=window.scrollY+175;
  heads.forEach(function(h){if(!h.closest(".group").hidden&&h.offsetTop<=cut)active=h.id;});
  document.querySelectorAll("nav a").forEach(function(a){a.classList.toggle("active",a.getAttribute("href")==="#"+active);});}
window.addEventListener("scroll",markNav,{passive:true});renderRecent();applyFilters();markNav();
</script>
</body></html>"""


if __name__ == "__main__":
    build()
