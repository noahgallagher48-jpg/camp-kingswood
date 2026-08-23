#!/usr/bin/env python3
"""Builds wednesday.html, the surface for Jodi's on-site visit (Aug 26, 2026).

Noah, 2026-08-23: "one page for Wednesday... delivery is aimed at books... her
picks go into a book layout group and preview."

So this page does one job: turn a sit-down into a book lane. Noah's Picks lead,
a tap puts a frame in the book, the lane is draggable because a book is an order
and not a set, and Play the book runs the lane exactly as it will read.

It writes nothing. The lane leaves as JSON on the clipboard, the same contract
the arrange board already uses: paste it into a session, it saves to
_work/arrangement_kw.json, and build_book.py lays out from there.

PRINT SIZES ARE REAL AND PRICES ARE NOT. Sizes come from print_guidance.json,
computed against each frame's own pixels and the material's resolution floor.
Every price in catalog.json is "ladder rough-in" with no Millers lab cost on
file, so no price renders here. Pass --prices only after Noah has set them.

    python3 build_wednesday.py                sizes on, prices off
    python3 build_wednesday.py --prices       only once the ladder is real
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_delivery import pool, frame_no

ARR = os.path.join(HERE, "_work", "arrangement_kw.json")
GUIDE = os.path.expanduser("~/Desktop/ABBA/kingswood/_delivery_2026/print_guidance.json")
OUT = os.path.join(HERE, "wednesday.html")
SEND = os.path.join(HERE, "book_send.json")

BOOK_LANE = "The book"
PICKS_LANE = "Noah's Picks"

# The page is build_book.py's page. Imported rather than restated so the preview
# cannot drift from the PDF: 12x8 landscape, 6% of the short edge as the mat,
# and a landscape frame that would lose more than 12% to the page gets matted
# instead of bled.
from build_book import PAGE_IN, MARGIN, MAX_CROP, MATTE_ALL


def sizes_for(guidance, filename):
    """The honest max size per material, or None when the frame has no true
    standard size. print_sizes.py owns the rules; this only reads its output."""
    g = guidance.get(filename)
    if not g or g.get("note"):
        return None
    out = [(m, g[m]) for m in ("metal", "paper", "canvas") if g.get(m)]
    return out or None


def send_config():
    """Where a saved lane goes. The page may be driven from the CLIENT's machine
    (Noah, 2026-08-23: "I just screw it up if it's her desk"), so a download is
    not a destination. These are network drops, tried in order."""
    if not os.path.exists(SEND):
        return {}
    cfg = json.load(open(SEND))
    return {k: cfg.get(k, "") for k in ("drive_endpoint", "web3forms_key", "subject")}


def build(show_prices=False):
    by_num, keep, _ = pool()
    arrangement = json.load(open(ARR))
    by_name = {g["name"]: g["frames"] for g in arrangement["groups"]}
    guidance = json.load(open(GUIDE)) if os.path.exists(GUIDE) else {}

    # The aside list fences the DELIVERY pool. It does not fence the book:
    # build_book.py is explicit that a frame can be wrong for the camp's library
    # and right for the book, so the book's lane wins and the overlap is
    # reported rather than enforced. Same rule here, or this page would preview
    # a book the PDF builder will not produce.
    live = set(keep)
    picks = [n for n in by_name.get(PICKS_LANE, []) if n in live]
    book = [n for n in by_name.get(BOOK_LANE, []) if n in by_num]
    also_aside = [n for n in book if n not in live]
    rest = [n for n in keep if n not in set(picks)]

    frames = {}
    for n in sorted(set(keep) | set(book)):
        f = by_num[n]
        entry = {"f": f}
        g = guidance.get(f)
        if g:
            entry["w"], entry["h"] = g["w"], g["h"]
        s = sizes_for(guidance, f)
        if s:
            entry["s"] = s
        frames[n] = entry
    no_dims = [n for n in book if "w" not in frames[n]]

    data = {
        "frames": frames,
        "picks": picks,
        "rest": rest,
        "book": book,
        "prices": bool(show_prices),
        "page_in": list(PAGE_IN),
        "margin": MARGIN,
        "max_crop": MAX_CROP,
        "matte_all": bool(MATTE_ALL),
        "send": send_config(),
    }

    html = PAGE.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    open(OUT, "w").write(html)

    priced = "prices ON" if show_prices else "prices withheld (ladder rough-in only)"
    sized = sum(1 for n in frames if "s" in frames[n])
    print(f"wrote {OUT}")
    print(f"  {len(picks)} in Noah's Picks · {len(rest)} more available · "
          f"{len(book)} seeded in the book lane")
    print(f"  {sized} of {len(frames)} frames carry standard print sizes · {priced}")
    s = data["send"]
    where = "Drive endpoint" if s.get("drive_endpoint") else (
            "inbox via Web3Forms" if s.get("web3forms_key") else "NOWHERE, local file only")
    print(f"  a saved book goes to: {where}")
    if also_aside:
        print(f"  IN THE BOOK, though they also sit in the aside lane: {also_aside}")
    if no_dims:
        print(f"  NO DIMENSIONS, page type cannot be computed: {no_dims}")


PAGE = """<!doctype html>
<html lang=en><head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content="noindex,nofollow">
<title>Camp Kingswood &middot; The book</title>
<style>
@font-face{font-family:Raleway;src:url(fonts/raleway-400.woff2) format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:Raleway;src:url(fonts/raleway-600.woff2) format('woff2');font-weight:600;font-display:swap}
@font-face{font-family:Raleway;src:url(fonts/raleway-800.woff2) format('woff2');font-weight:800;font-display:swap}
:root{--ground:#062A40;--deep:#04202F;--accent:#DB3A00;--ink:#F3F1EC;
 --panel:rgba(243,241,236,.06);--line:rgba(243,241,236,.16);--soft:rgba(243,241,236,.62)}
*{box-sizing:border-box}
html,body{margin:0;background:var(--ground);color:var(--ink);
 font-family:Raleway,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
body{padding:0 0 190px}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
header{padding:40px 0 22px}
.eyebrow{font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--soft);margin:0 0 10px}
h1{font-weight:800;font-size:clamp(30px,5vw,46px);margin:0;letter-spacing:-.01em}
.lede{color:var(--soft);font-size:16px;margin:14px 0 0;max-width:62ch;line-height:1.55}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:26px 0 0}
.tab{background:transparent;border:1px solid var(--line);color:var(--ink);border-radius:24px;
 padding:9px 18px;font:600 13px Raleway,sans-serif;cursor:pointer}
.tab[aria-selected=true]{background:var(--accent);border-color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin:26px 0 0}
figure{margin:0;position:relative;background:var(--panel);border-radius:8px;overflow:hidden}
figure img{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;
 cursor:zoom-in}
figure{transition:box-shadow .14s,transform .14s}
figure.in{box-shadow:inset 0 0 0 3px var(--accent);transform:translateY(-2px)}
.n{position:absolute;top:9px;left:10px;font:600 11px Raleway,sans-serif;color:var(--ink);
 background:rgba(6,42,64,.72);border-radius:11px;padding:2px 9px;pointer-events:none}
.add{position:absolute;top:8px;right:8px;width:32px;height:32px;border-radius:50%;
 border:1px solid var(--line);background:rgba(6,42,64,.72);color:var(--ink);
 font:600 17px Raleway,sans-serif;cursor:pointer;line-height:1;padding:0}
figure.in .add{background:var(--accent);border-color:var(--accent);font-size:15px}
.szbtn{position:absolute;bottom:8px;right:8px;border:1px solid var(--line);
 background:rgba(6,42,64,.72);color:var(--ink);border-radius:14px;
 font:600 10.5px Raleway,sans-serif;letter-spacing:.06em;padding:5px 10px;cursor:pointer}
.sz{padding:11px 12px 13px;font-size:12.5px;color:var(--soft);line-height:1.6;display:none}
figure.showsz .sz{display:block}
.sz b{color:var(--ink);font-weight:600}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--deep);
 border-top:1px solid var(--line);padding:12px 0 14px;z-index:40}
.barin{max-width:1180px;margin:0 auto;padding:0 22px;display:flex;align-items:center;gap:16px}
.lane{display:flex;gap:7px;overflow-x:auto;flex:1;padding:3px 0 6px;min-height:60px}
.lane img{height:54px;width:auto;border-radius:4px;cursor:grab;flex:0 0 auto;
 border:2px solid transparent}
.lane img.drag{opacity:.4}
.lane img.over{border-color:var(--accent)}
.empty{color:var(--soft);font-size:13px;align-self:center;white-space:nowrap}
.acts{display:flex;gap:9px;flex-shrink:0;flex-wrap:wrap}
.btn{border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:6px;
 padding:10px 16px;font:600 13px Raleway,sans-serif;cursor:pointer;white-space:nowrap}
.btn.go{background:var(--accent);border-color:var(--accent)}
.btn:disabled{opacity:.4;cursor:default}
.book{position:fixed;inset:0;background:#04202F;z-index:60;display:none;flex-direction:column}
.book.on{display:flex}
.bkbar{flex:0 0 auto;display:flex;align-items:center;gap:16px;padding:13px 22px;
 border-bottom:1px solid var(--line)}
.bkbar .t{font:600 13.5px Raleway,sans-serif;flex:1}
.bkbar .t span{color:var(--soft);font-weight:400}
.bkstage{flex:1;display:flex;align-items:center;justify-content:center;padding:24px;min-height:0}
.spread{background:#F3F1EC;display:flex;position:relative;
 box-shadow:0 20px 60px rgba(0,0,0,.55);max-width:94vw}
.spread.two{aspect-ratio:3/1;width:min(94vw,calc((100vh - 168px)*3))}
.spread.solo{aspect-ratio:3/2;width:min(58vw,calc((100vh - 168px)*1.5))}
.pg{width:50%;height:100%;position:relative;overflow:hidden;background:#F3F1EC;
 display:flex;align-items:center;justify-content:center}
.spread.solo .pg{width:100%}
.pg.bleed img{width:100%;height:100%;object-fit:cover;display:block}
.pg.mat{padding:4%}
.pg.pair{padding:4%;gap:3.6%}
.pg img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.gut{position:absolute;top:0;bottom:0;left:50%;width:1px;background:rgba(6,42,64,.15);
 pointer-events:none}
.cov{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;
 justify-content:center;color:#062A40;position:relative;padding:6%}
.cov h3{font:400 clamp(19px,3.4vw,42px) Raleway,sans-serif;margin:0;letter-spacing:.01em}
.cov .rule{width:11%;height:3px;background:#DB3A00;margin:5% 0 3.4%}
.cov .sub{font:600 clamp(8px,1.05vw,13px) Raleway,sans-serif;margin:0;letter-spacing:.03em}
.cov .cred{position:absolute;bottom:9%;font:400 clamp(8px,1vw,12.5px) Raleway,sans-serif}
.pnum{position:absolute;bottom:9px;left:0;right:0;text-align:center;color:var(--faint);
 font:600 10px Raleway,sans-serif;letter-spacing:.16em}
.x{background:transparent;border:0;color:var(--ink);font:400 27px Raleway,sans-serif;
 cursor:pointer;line-height:1;padding:0 4px}
.nav{display:flex;gap:8px}
.how{color:var(--faint);font:600 10px Raleway,sans-serif;letter-spacing:.1em;
 text-transform:uppercase}
.lb{position:fixed;inset:0;background:#04202F;z-index:70;display:none;flex-direction:column}
.lb.on{display:flex}
.lbbar{flex:0 0 auto;display:flex;align-items:center;gap:14px;padding:13px 22px;
 border-bottom:1px solid var(--line)}
.lbn{font:800 17px Raleway,sans-serif}
.lbsz{flex:1;color:var(--soft);font-size:12.5px}
.lbsz b{color:var(--ink);font-weight:600}
.lbstage{flex:1;display:flex;align-items:center;justify-content:center;padding:22px;min-height:0}
.lbstage img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.lbfoot{flex:0 0 auto;display:flex;align-items:center;justify-content:center;gap:10px;
 padding:14px 22px 18px}
.btn.on{background:var(--accent);border-color:var(--accent)}
.hint{color:var(--faint);font-size:11.5px;margin:0 0 0 6px}
.pnum b{color:var(--soft);font-weight:600}
.note{margin:34px 0 0;padding:16px 18px;border:1px solid var(--line);border-radius:8px;
 color:var(--soft);font-size:13.5px;line-height:1.65}
@media(max-width:600px){
 .grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
 .barin{flex-direction:column;align-items:stretch;gap:10px}
 .acts{justify-content:stretch}.btn{flex:1}
}
</style></head>
<body>
<div class=wrap>
<header>
 <p class=eyebrow>Camp Kingswood &middot; Summer 2026</p>
 <h1>The book</h1>
 <p class=lede>Noah's Picks lead. Tap a photograph to put it in the book, tap again to take
 it out. The strip along the bottom is the book in order, and it drags. Play the book to
 read it the way it will read.</p>
 <div class=tabs role=tablist>
  <button class=tab role=tab aria-selected=true data-view=picks>Noah's Picks</button>
  <button class=tab role=tab aria-selected=false data-view=rest>Everything else</button>
  <button class=tab role=tab aria-selected=false data-view=book>In the book</button>
 </div>
</header>
<div class=grid id=grid></div>
<p class=note id=foot></p>
</div>

<div class=bar>
 <div class=barin>
  <div class=lane id=lane></div>
  <div class=acts>
   <button class="btn go" id=play>See the book</button>
   <button class=btn id=copy>Save the book</button>
  </div>
 </div>
</div>

<div class=lb id=lb>
 <div class=lbbar>
  <span class=lbn id=lbn></span>
  <span class=lbsz id=lbsz></span>
  <span class=nav>
   <button class=btn id=lbprev>Back</button>
   <button class=btn id=lbnext>Next</button>
  </span>
  <button class=x id=lbclose aria-label="Close">&times;</button>
 </div>
 <div class=lbstage><img id=lbimg alt=""></div>
 <div class=lbfoot>
  <button class="btn go" id=lbadd></button>
  <span class=hint>Arrow keys move, Esc closes</span>
 </div>
</div>

<div class=book id=book>
 <div class=bkbar>
  <span class=t id=bkt></span>
  <span class=nav>
   <button class=btn id=prev>Back</button>
   <button class=btn id=next>Next</button>
  </span>
  <button class=x id=close aria-label="Close the book">&times;</button>
 </div>
 <div class=bkstage><div class=spread id=spread></div></div>
 <p class=pnum id=pnum></p>
</div>

<script>
var D = __DATA__;
var KEY = "kwood-wednesday-v1";
var book = [];
try { var s = localStorage.getItem(KEY); if (s) book = JSON.parse(s); } catch(e){}
if (!book.length) book = D.book.slice();

var view = "picks";
var gridEl = document.getElementById("grid");
var laneEl = document.getElementById("lane");
var footEl = document.getElementById("foot");

function save(){ try{ localStorage.setItem(KEY, JSON.stringify(book)); }catch(e){} }
function inBook(n){ return book.indexOf(n) !== -1; }

function sizeLine(n){
  var f = D.frames[n];
  if (!f || !f.s) return "No standard size matches this frame's proportions. It prints as a custom cut.";
  return "Prints to " + f.s.map(function(p){
    return "<b>" + p[1].replace("x","&times;") + "&Prime;</b> " + p[0];
  }).join(" &middot; ");
}

function card(n){
  var f = D.frames[n];
  var fig = document.createElement("figure");
  if (inBook(n)) fig.className = "in";
  fig.innerHTML =
    '<img loading=lazy src="img/thumb/' + f.f + '" alt="Camp Kingswood, frame ' + n + '">' +
    '<span class=n>' + n + '</span>' +
    '<button class=add aria-label="Add frame ' + n + ' to the book">+</button>' +
    '<button class=szbtn>SIZE</button>' +
    '<div class=sz>' + sizeLine(n) + '</div>';
  function glyph(){ fig.querySelector(".add").innerHTML = inBook(n) ? "&#10003;" : "+"; }
  function toggle(){
    var i = book.indexOf(n);
    if (i === -1) book.push(n); else book.splice(i, 1);
    save();
    var shown = fig.classList.contains("showsz");
    fig.className = (inBook(n) ? "in" : "") + (shown ? " showsz" : "");
    glyph(); paintLane();
    if (view === "book") paint();
  }
  glyph();
  fig.querySelector("img").onclick = function(){ openFrame(n); };
  fig.querySelector(".add").onclick = function(e){ e.stopPropagation(); toggle(); };
  fig.querySelector(".szbtn").onclick = function(e){
    e.stopPropagation();
    fig.classList.toggle("showsz");
  };
  return fig;
}

function paint(){
  var list = view === "picks" ? D.picks : (view === "rest" ? D.rest : book);
  gridEl.innerHTML = "";
  list.forEach(function(n){ if (D.frames[n]) gridEl.appendChild(card(n)); });
  footEl.innerHTML = view === "book"
    ? "This is the book in order. Drag the strip below to change the order."
    : "Print sizes are computed from each photograph's own resolution, against what the lab sells off the shelf. No size here implies a crop.";
}

var dragging = null;
function paintLane(){
  laneEl.innerHTML = "";
  if (!book.length){
    var p = document.createElement("span");
    p.className = "empty";
    p.textContent = "The book is empty. Tap a photograph to start it.";
    laneEl.appendChild(p);
  }
  book.forEach(function(n, idx){
    var f = D.frames[n]; if (!f) return;
    var im = document.createElement("img");
    im.src = "img/thumb/" + f.f; im.draggable = true; im.dataset.i = idx;
    im.alt = "Frame " + n;
    im.title = "Frame " + n + ". Drag to reorder, double click to remove.";
    im.ondragstart = function(){ dragging = idx; im.classList.add("drag"); };
    im.ondragend = function(){ dragging = null; im.classList.remove("drag"); };
    im.ondragover = function(e){ e.preventDefault(); im.classList.add("over"); };
    im.ondragleave = function(){ im.classList.remove("over"); };
    im.ondrop = function(e){
      e.preventDefault(); im.classList.remove("over");
      if (dragging === null || dragging === idx) return;
      var moved = book.splice(dragging, 1)[0];
      book.splice(idx, 0, moved);
      save(); paintLane(); if (view === "book") paint();
    };
    im.ondblclick = function(){
      book.splice(idx, 1); save(); paintLane(); paint();
    };
    laneEl.appendChild(im);
  });
  document.getElementById("play").disabled = !book.length;
}

/* THE FULL-SIZE VIEW. A thumbnail is not enough to decide with, so clicking one
   opens the frame big, with its print sizes and one control that puts it in the
   book or takes it out. The + chip on the card stays the fast path for frames
   he already knows. */
var lbEl = document.getElementById("lb");
var lbAt = null;

function lbList(){
  return view === "picks" ? D.picks : (view === "rest" ? D.rest : book);
}

function paintCardState(n){
  var list = document.querySelectorAll("#grid figure");
  for (var i = 0; i < list.length; i++){
    var fig = list[i];
    if (fig.querySelector(".n").textContent !== String(n)) continue;
    var shown = fig.classList.contains("showsz");
    fig.className = (inBook(n) ? "in" : "") + (shown ? " showsz" : "");
    fig.querySelector(".add").innerHTML = inBook(n) ? "&#10003;" : "+";
  }
}

function paintLbButton(){
  var b = document.getElementById("lbadd");
  var isin = inBook(lbAt);
  b.textContent = isin ? "In the book, take it out" : "Add to the book";
  b.className = "btn" + (isin ? " on" : " go");
}

function openFrame(n){
  var f = D.frames[n];
  if (!f) return;
  lbAt = n;
  document.getElementById("lbimg").src = "img/present/" + f.f;
  document.getElementById("lbn").textContent = n;
  document.getElementById("lbsz").innerHTML = sizeLine(n);
  paintLbButton();
  var l = lbList();
  document.getElementById("lbprev").disabled = l.indexOf(n) <= 0;
  document.getElementById("lbnext").disabled = l.indexOf(n) === l.length - 1;
  lbEl.classList.add("on");
}

function lbStep(d){
  var l = lbList(), i = l.indexOf(lbAt);
  if (i === -1) return;
  var j = i + d;
  if (j < 0 || j >= l.length) return;
  openFrame(l[j]);
}

document.getElementById("lbadd").onclick = function(){
  var i = book.indexOf(lbAt);
  if (i === -1) book.push(lbAt); else book.splice(i, 1);
  save(); paintLbButton(); paintLane(); paintCardState(lbAt);
  if (view === "book") paint();
};
document.getElementById("lbclose").onclick = function(){ lbEl.classList.remove("on"); };
document.getElementById("lbnext").onclick = function(){ lbStep(1); };
document.getElementById("lbprev").onclick = function(){ lbStep(-1); };

document.querySelectorAll(".tab").forEach(function(t){
  t.onclick = function(){
    document.querySelectorAll(".tab").forEach(function(o){ o.setAttribute("aria-selected","false"); });
    t.setAttribute("aria-selected","true");
    view = t.dataset.view; paint();
  };
});

/* THE BOOK LAYOUT. This is not a slideshow. It lays the lane out on 12x8
   landscape pages using build_book.py's own rules, then shows facing pages the
   way the printed book opens:
     two portraits in a row  -> paired on one page
     everything else         -> matted on the camp's warm white
   Nothing bleeds (Noah, 2026-08-23). Every frame sits inside the margin, whole,
   at its own proportions, so no page costs a composition its edges.
   Change the lane and the pagination changes with it, because that is what the
   PDF will do. */
var PW = D.page_in[0], PH = D.page_in[1], MAXCROP = D.max_crop, MATTEALL = D.matte_all;

function cropLoss(w, h){
  var scale = Math.max(PW / w, PH / h);
  return 1 - (PW / (w * scale)) * (PH / (h * scale));
}

function paginate(seq){
  var pages = [], i = 0;
  while (i < seq.length){
    var n = seq[i], f = D.frames[n];
    if (!f || !f.w){ pages.push({t:"mat", n:[n], how:"no dimensions"}); i++; continue; }
    var tall = f.h > f.w;
    var nx = i + 1 < seq.length ? seq[i + 1] : null;
    var nf = nx !== null ? D.frames[nx] : null;
    if (tall && nf && nf.w && nf.h > nf.w){
      pages.push({t:"pair", n:[n, nx], how:"two portraits, one page"});
      i += 2; continue;
    }
    if (MATTEALL){
      pages.push({t:"mat", n:[n], how:tall ? "matted, portrait" : "matted, landscape"});
      i++; continue;
    }
    if (tall){ pages.push({t:"mat", n:[n], how:"portrait, matted"}); i++; continue; }
    var lost = cropLoss(f.w, f.h);
    if (lost > MAXCROP) pages.push({t:"mat", n:[n], how:"matted, would lose " + Math.round(lost*100) + "%"});
    else pages.push({t:"bleed", n:[n], how:"full bleed, " + Math.round(lost*100) + "% cropped"});
    i++;
  }
  return pages;
}

/* The cover stands alone the way it does on a table, then pages run in twos. */
function spreads(pages){
  var out = [{cover:true}];
  for (var k = 0; k < pages.length; k += 2)
    out.push({l: pages[k], r: pages[k+1] || null, first: k + 1});
  return out;
}

var SP = [], at = 0;
var bookEl = document.getElementById("book");
var spreadEl = document.getElementById("spread");
var bktEl = document.getElementById("bkt");
var pnumEl = document.getElementById("pnum");

function pageHTML(pg){
  if (!pg) return '<div class="pg"></div>';
  var imgs = pg.n.map(function(n){
    var f = D.frames[n];
    return f ? '<img src="img/present/' + f.f + '" alt="Frame ' + n + '">' : "";
  }).join("");
  return '<div class="pg ' + pg.t + '">' + imgs + '</div>';
}

function showSpread(i){
  if (i < 0 || i >= SP.length) return;
  at = i;
  var s = SP[i];
  if (s.cover){
    spreadEl.className = "spread solo";
    spreadEl.innerHTML =
      '<div class=cov><h3>Camp Kingswood</h3><div class=rule></div>' +
      '<p class=sub>Bridgton, Maine &middot; Summer 2026</p>' +
      '<span class=cred>Photographs by Noah Gallagher</span></div>';
    pnumEl.innerHTML = "<b>COVER</b>";
  } else {
    spreadEl.className = "spread two";
    spreadEl.innerHTML = pageHTML(s.l) + pageHTML(s.r) + '<span class=gut></span>';
    var label = s.r ? "PAGES " + s.first + " AND " + (s.first + 1) : "PAGE " + s.first;
    var how = [s.l && s.l.how, s.r && s.r.how].filter(Boolean).join("  &middot;  ");
    pnumEl.innerHTML = "<b>" + label + "</b>  &middot;  <span class=how>" + how + "</span>";
  }
  bktEl.innerHTML = "The book, as it lays out <span>&middot; spread " + (i + 1) +
                    " of " + SP.length + "</span>";
  document.getElementById("prev").disabled = i === 0;
  document.getElementById("next").disabled = i === SP.length - 1;
}

function openBook(){
  if (!book.length) return;
  var pages = paginate(book);
  SP = spreads(pages);
  bookEl.classList.add("on");
  showSpread(0);
}

document.getElementById("play").onclick = openBook;
document.getElementById("close").onclick = function(){ bookEl.classList.remove("on"); };
document.getElementById("next").onclick = function(){ showSpread(at + 1); };
document.getElementById("prev").onclick = function(){ showSpread(at - 1); };
document.addEventListener("keydown", function(e){
  if (lbEl.classList.contains("on")){
    if (e.key === "Escape") lbEl.classList.remove("on");
    if (e.key === "ArrowRight") { e.preventDefault(); lbStep(1); }
    if (e.key === "ArrowLeft") { e.preventDefault(); lbStep(-1); }
    if (e.key === " ") { e.preventDefault(); document.getElementById("lbadd").click(); }
    return;
  }
  if (!bookEl.classList.contains("on")) return;
  if (e.key === "Escape") bookEl.classList.remove("on");
  if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); showSpread(at + 1); }
  if (e.key === "ArrowLeft") showSpread(at - 1);
});

/* ONE CLICK, AND THE SET IS BANKED SOMEWHERE WE CAN BOTH GRAB IT.
   This page may be driven from the client's own machine, so saving to disk
   saves to HER desk and helps nobody. The button posts the lane out over the
   network instead, and tries destinations in order until one answers:
     1. the Drive endpoint, when it is deployed, one dated file per save
     2. the inbox, through the same Web3Forms account the vote page uses
     3. a local file, only if the network refuses, so a set made in the room
        is never lost even when everything else fails
   Nothing overwrites anything. Every click banks its own copy. */
var SEND = D.send || {};

function bookPayload(){
  return {
    group: "The book",
    frames: book,
    saved: new Date().toISOString(),
    source: "wednesday.html"
  };
}

function fallbackDownload(payload){
  try {
    var blob = new Blob([JSON.stringify(payload, null, 1)], {type: "application/json"});
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = "kingswood_book.json";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(url); }, 1000);
    return true;
  } catch (e) { return false; }
}

function toDrive(payload){
  if (!SEND.drive_endpoint) return Promise.reject("no endpoint");
  /* text/plain keeps this a simple request, so it does not trip a CORS
     preflight that Apps Script will not answer. The body is still JSON. */
  return fetch(SEND.drive_endpoint, {
    method: "POST",
    headers: {"Content-Type": "text/plain;charset=utf-8"},
    body: JSON.stringify(payload)
  }).then(function(r){ return r.json(); }).then(function(r){
    if (r && r.ok) return "Drive";
    throw new Error(r && r.error ? r.error : "refused");
  });
}

function toInbox(payload){
  if (!SEND.web3forms_key) return Promise.reject("no key");
  return fetch("https://api.web3forms.com/submit", {
    method: "POST",
    headers: {"Content-Type": "application/json", Accept: "application/json"},
    body: JSON.stringify({
      access_key: SEND.web3forms_key,
      subject: (SEND.subject || "Kingswood book") + ": " + payload.frames.length + " frames",
      from_name: "Kingswood book",
      botcheck: "",
      saved: payload.saved,
      frames: payload.frames.join(", "),
      lane_json: JSON.stringify(payload)
    })
  }).then(function(r){ return r.json(); }).then(function(r){
    if (r && r.success) return "inbox";
    throw new Error("refused");
  });
}

document.getElementById("copy").onclick = function(){
  var b = document.getElementById("copy");
  if (!book.length) return;
  var payload = bookPayload();
  var reset = function(text){
    b.textContent = text;
    setTimeout(function(){ b.textContent = "Save the book"; b.disabled = false; }, 2600);
  };
  b.disabled = true;
  b.textContent = "Saving";

  toDrive(payload)
    .catch(function(){ return toInbox(payload); })
    .then(function(where){ reset("Banked, " + where); })
    .catch(function(){
      reset(fallbackDownload(payload) ? "No connection, saved here"
                                      : "Could not save");
    });
};

paint(); paintLane();
</script>
</body></html>
"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", action="store_true",
                    help="render prices; only valid once the ladder is real")
    build(ap.parse_args().prices)
