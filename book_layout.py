#!/usr/bin/env python3
"""The book-layout tab, injected into the delivery page.

    from book_layout import CSS, HTML, JS

Noah, 2026-08-23: "Two tabs at the top. One is gallery, just gallery. And the
other is book layout. I choose one or the other at the top."

So the camp opens ONE link and picks a mode, instead of collecting a folder of
URLs by text. This module is the second mode. It reads the delivery page's own
ALL array, so there is no second copy of the frame data and the two tabs can
never disagree about what exists.

THE LAYOUT IS THE PRINTED LAYOUT. Pagination mirrors build_book.py exactly:
12x8 landscape pages, two portraits in a row paired on one page, everything
else matted on the camp's warm white, nothing bleeding (MATTE_ALL, his call the
same day). Verified page-for-page against that builder's own sequence file, so
what the camp approves on screen is what the PDF produces.

PRINT SIZES ARE NOT HERE. Noah, same day: "we had print stuff later, book has to
be in the can first." Sizes live on the gallery tab with the downloads, where
they belong. This tab lays out a book and does nothing else.

Injects into a page that defines: ALL (array of {n, f, wpx, hpx}),
BOOKSEED (array of frame numbers), BOOKSEND (where a saved lane goes), and an
img/present + img/thumb layout.
"""

CSS = """
/* book layout tab */
#tab-book{display:none}
#tab-book.on{display:block}
.bkchips{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px}
.bkchip{background:transparent;border:1px solid rgba(243,241,236,.22);color:inherit;
 border-radius:22px;padding:8px 17px;font:600 13px inherit;cursor:pointer}
.bkchip[aria-selected=true]{background:#DB3A00;border-color:#DB3A00;color:#F3F1EC}
.bkwho{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 14px}
.bkwholab{font-size:11px;letter-spacing:.14em;text-transform:uppercase;opacity:.6}
.bkwhobtn{background:transparent;border:1px solid rgba(243,241,236,.22);color:inherit;
  border-radius:999px;padding:5px 13px;font:inherit;font-size:12.5px;cursor:pointer}
.bkwhobtn[aria-pressed=true]{background:#F3F1EC;border-color:#F3F1EC;color:#062A40}
.bkwhonote{font-size:11.5px;opacity:.55}
.bkempty{opacity:.6;font-size:14px;padding:26px 2px}
.bkgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:13px}
.bkcard{margin:0;position:relative;border-radius:8px;overflow:hidden;
 background:rgba(243,241,236,.06);transition:box-shadow .14s,transform .14s}
.bkcard img{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;cursor:zoom-in}
.bkcard.in{box-shadow:inset 0 0 0 3px #DB3A00;transform:translateY(-2px)}
.bkcard .bn{position:absolute;top:8px;left:9px;font:600 11px inherit;
 background:rgba(6,42,64,.74);border-radius:11px;padding:2px 9px;pointer-events:none}
.bkcard .badd{position:absolute;top:7px;right:7px;width:31px;height:31px;border-radius:50%;
 border:1px solid rgba(243,241,236,.22);background:rgba(6,42,64,.74);color:inherit;
 font:600 17px inherit;cursor:pointer;line-height:1;padding:0}
.bkcard.in .badd{background:#DB3A00;border-color:#DB3A00;font-size:15px}
.bklane{position:fixed;left:0;right:0;bottom:0;background:#04202F;
 border-top:1px solid rgba(243,241,236,.16);padding:11px 0 13px;z-index:40;display:none}
.bklane.on{display:block}
.bklanein{max-width:1180px;margin:0 auto;padding:0 20px;display:flex;align-items:center;gap:15px}
.bkstrip{display:flex;gap:6px;overflow-x:auto;flex:1;padding:3px 0 6px;min-height:58px}
.bkstrip img{height:52px;width:auto;border-radius:4px;cursor:grab;flex:0 0 auto;
 border:2px solid transparent}
.bkstrip img.over{border-color:#DB3A00}
.bkempty{font-size:13px;align-self:center;white-space:nowrap;opacity:.66}
.bkacts{display:flex;gap:8px;flex-shrink:0;flex-wrap:wrap}
.bkbtn{border:1px solid rgba(243,241,236,.22);background:transparent;color:inherit;
 border-radius:6px;padding:10px 15px;font:600 13px inherit;cursor:pointer;white-space:nowrap}
.bkbtn.go{background:#DB3A00;border-color:#DB3A00;color:#F3F1EC}
.bkbtn:disabled{opacity:.4;cursor:default}
.bkview{position:fixed;inset:0;background:#04202F;z-index:70;display:none;flex-direction:column}
.bkview.on{display:flex}
.bkvbar{flex:0 0 auto;display:flex;align-items:center;gap:14px;padding:12px 20px;
 border-bottom:1px solid rgba(243,241,236,.16)}
.bkvt{flex:1;font:600 13.5px inherit}
.bkvt span{opacity:.6;font-weight:400}
.bkvstage{flex:1;display:flex;align-items:center;justify-content:center;padding:22px;min-height:0}
.spread{background:#F3F1EC;display:flex;position:relative;box-shadow:0 20px 60px rgba(0,0,0,.55)}
.spread.two{aspect-ratio:3/1;width:min(94vw,calc((100vh - 160px)*3))}
.spread.solo{aspect-ratio:3/2;width:min(58vw,calc((100vh - 160px)*1.5))}
.bpg{width:50%;height:100%;position:relative;overflow:hidden;background:#F3F1EC;
 display:flex;align-items:center;justify-content:center}
.spread.solo .bpg{width:100%}
.bpg.mat{padding:4%}
.bpg.pair{padding:4%;gap:3.6%}
.bpg.bleed img{width:100%;height:100%;object-fit:cover}
/* the grid page that faces a bleedhero: book margins, paper between the frames */
.bpg[class*=" g"]{display:grid;padding:5.4%;gap:3.2%}
.bpg.g4{grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr}
.bpg.g2{grid-template-columns:1fr 1fr}
.bpg.g3,.bpg.g6{grid-template-columns:1fr 1fr 1fr}
.bpg.g6{grid-template-rows:1fr 1fr}
.bpg[class*=" g"] img{width:100%;height:100%;object-fit:cover;display:block}
.bpg img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.bgut{position:absolute;top:0;bottom:0;left:50%;width:1px;background:rgba(6,42,64,.15)}
.bcov{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;
 justify-content:center;color:#062A40;position:relative;padding:6%}
.bcov h3{font:400 clamp(19px,3.4vw,42px) inherit;margin:0}
.bcov .brule{width:11%;height:3px;background:#DB3A00;margin:5% 0 3.4%}
.bcov .bsub{font:600 clamp(8px,1.05vw,13px) inherit;margin:0;letter-spacing:.03em}
.bcov .bcred{position:absolute;bottom:9%;font:400 clamp(8px,1vw,12.5px) inherit}
.bpnum{flex:0 0 auto;text-align:center;padding:11px 0 15px;font:600 10px inherit;
 letter-spacing:.16em;opacity:.55}
.bpnum b{opacity:1}
.bkfull{position:fixed;inset:0;background:#04202F;z-index:80;display:none;flex-direction:column}
.bkfull.on{display:flex}
.bkfimg{flex:1;display:flex;align-items:center;justify-content:center;padding:20px;min-height:0}
.bkfimg img{max-width:100%;max-height:100%;object-fit:contain}
.bkffoot{flex:0 0 auto;display:flex;justify-content:center;gap:10px;padding:13px 20px 18px}
.bkx{background:transparent;border:0;color:inherit;font:400 27px inherit;cursor:pointer;padding:0 4px}
@media(max-width:600px){
 .bkgrid{grid-template-columns:repeat(auto-fill,minmax(145px,1fr))}
 .bklanein{flex-direction:column;align-items:stretch;gap:9px}
 .bkacts{justify-content:stretch}.bkbtn{flex:1}
}
"""

HTML = """
<div class=bklane id=bklane>
 <div class=bklanein>
  <div class=bkstrip id=bkstrip></div>
  <div class=bkacts>
   <button class="bkbtn go" id=bksee>See the book</button>
   <button class=bkbtn id=bksave>Save the book</button>
  </div>
 </div>
</div>

<div class=bkview id=bkview>
 <div class=bkvbar>
  <span class=bkvt id=bkvt></span>
  <button class=bkbtn id=bkprev>Back</button>
  <button class=bkbtn id=bknext>Next</button>
  <button class=bkx id=bkclose aria-label=Close>&times;</button>
 </div>
 <div class=bkvstage><div class=spread id=bkspread></div></div>
 <p class=bpnum id=bpnum></p>
</div>

<div class=bkfull id=bkfull>
 <div class=bkvbar>
  <span class=bkvt id=bkfn></span>
  <button class=bkbtn id=bkfprev>Back</button>
  <button class=bkbtn id=bkfnext>Next</button>
  <button class=bkx id=bkfclose aria-label=Close>&times;</button>
 </div>
 <div class=bkfimg><img id=bkfimg alt=""></div>
 <div class=bkffoot><button class="bkbtn go" id=bkfadd></button></div>
</div>
"""

JS = r"""
/* ---- the book layout tab ------------------------------------------------
   Reads ALL from the gallery, so both tabs describe the same set. Pagination
   mirrors build_book.py: 12x8 landscape, two portraits in a row paired on one
   page, everything else matted, nothing bleeding. */
var BKPW = 12, BKPH = 8, BKMATTEALL = true;
/* Frame number -> the frames that face it, for the bleedhero spread. One line
   per spread; the same data build_book.py takes as {"style":"bleedhero"}. */
var BKBLEEDHERO = {224: [221, 222, 223, 225]};
/* TWO PICKERS, ONE PAGE (Noah, 2026-08-27): "one section Jody's picks, one
   section Noah's picks. Jody can pick Jody's picks, Noah picks Noah's picks
   ... we should be able to see each others."

   Each identity writes to its OWN localStorage store, so neither can overwrite
   the other by opening the same link. What each SEES of the other is the list
   baked into the page at build time: Noah's from the arrangement, the camp's
   from _work/selections_client.json. That is the honest shape on a static host
   with no server; the camp's live picks travel back with Save, and folding them
   in is a rebuild.

   THE KEY CARRIES THE SET (827). Selections are stored by frame NUMBER, and on
   2026-08-27 the whole delivery was swapped, so a stored number now points at a
   different photograph. Reusing the old key painted the old set's checks onto
   the new one, which is exactly what Noah saw. Bump this whenever the pool is
   replaced. */
var BKSET = "827b";   /* bumped 2026-08-27 on Noah's "reset picks": every
   device opens a clean sheet, his and hers both. The 827 keys are dead. */
var BKWHOKEY = "kwood-who";
var bkWho = "camp";
try { var w = localStorage.getItem(BKWHOKEY); if (w === "noah" || w === "camp") bkWho = w; } catch(e){}
function bkKeyFor(who){ return "kwood-book-" + BKSET + "-" + who; }
var BKKEY = bkKeyFor(bkWho);
var BKBY = {}; ALL.forEach(function(r){ BKBY[r.n] = r; });
/* The book may hold frames the gallery does not: the aside list fences the
   camp's library, not the book (build_book.py's rule). Those records ride
   along separately so the lane never silently shortens. */
if (typeof BOOKEXTRA !== "undefined") BOOKEXTRA.forEach(function(r){ BKBY[r.n] = r; });
var bkBook = [];
function bkLoad(){
  bkBook = [];
  try { var s = localStorage.getItem(BKKEY); if (s) bkBook = JSON.parse(s); } catch(e){}
  /* Seed ONLY for the owner, and only when he has never picked on this set.
     The camp opens an empty sheet, which is the point: nothing is checked
     until she checks it. */
  if (!bkBook.length && bkWho === "noah")
    bkBook = (typeof BOOKSEED !== "undefined" ? BOOKSEED : []).slice();
  bkBook = bkBook.filter(function(n){ return BKBY[n]; });
}
bkLoad();
var bkView = "mine", bkFullAt = null;

function bkSave(){ try{ localStorage.setItem(BKKEY, JSON.stringify(bkBook)); }catch(e){} }

/* Switching identity swaps the whole store. Nothing is merged and nothing is
   copied across, so one person can never quietly inherit the other's sheet. */
function bkSetWho(who){
  if (who !== "noah" && who !== "camp") return;
  bkSave();
  bkWho = who;
  try { localStorage.setItem(BKWHOKEY, who); } catch(e){}
  BKKEY = bkKeyFor(who);
  bkLoad();
  bkPaintWho(); bkStrip(); bkGrid();
}
function bkPaintWho(){
  ["noah","camp"].forEach(function(w){
    var b = document.getElementById("bkwho-" + w);
    if (b) b.setAttribute("aria-pressed", w === bkWho ? "true" : "false");
  });
  var note = document.getElementById("bkwhonote");
  if (note) note.textContent = (bkWho === "noah"
    ? "your picks save on this device"
    : "your picks save on this device; Save the book sends them to Noah");
  var mine = document.getElementById("bkchip-mine");
  if (mine) mine.textContent = (bkWho === "noah" ? "My picks (Noah)"
                                                 : "My picks (Camp Kingswood)");
}
function bkIn(n){ return bkBook.indexOf(n) !== -1; }
function bkList(){
  if (bkView === "book") return bkBook;
  if (bkView === "mine") return bkBook;
  /* The other side's picks are whatever was baked in at build time. If a list
     is empty the grid says so rather than showing the whole set, because an
     unfenced grid under a named heading reads as "they picked everything". */
  if (bkView === "picks")
    return (typeof BOOKPICKS !== "undefined" ? BOOKPICKS : []).filter(function(n){ return BKBY[n]; });
  if (bkView === "clientpicks")
    return (typeof CLIENTPICKS !== "undefined" ? CLIENTPICKS : []).filter(function(n){ return BKBY[n]; });
  return ALL.map(function(r){ return r.n; });
}
function bkEmptyNote(){
  if (bkView === "mine") return "Nothing picked yet. Tap a photograph to add it.";
  if (bkView === "picks") return "Noah has not sent his picks for this set yet.";
  if (bkView === "clientpicks") return "Camp Kingswood has not sent picks for this set yet.";
  if (bkView === "book") return "The book is empty. Add photographs from My picks.";
  return "";
}

function bkToggle(n){
  var i = bkBook.indexOf(n);
  if (i === -1) bkBook.push(n); else bkBook.splice(i, 1);
  bkSave(); bkStrip(); bkPaintCard(n);
  if (bkFullAt === n) bkPaintFullBtn();
  if (bkView === "book") bkGrid();
}
function bkPaintCard(n){
  var els = document.querySelectorAll("#bkgrid .bkcard");
  for (var i = 0; i < els.length; i++){
    if (els[i].getAttribute("data-n") !== String(n)) continue;
    els[i].className = "bkcard" + (bkIn(n) ? " in" : "");
    els[i].querySelector(".badd").innerHTML = bkIn(n) ? "&#10003;" : "+";
  }
}
function bkGrid(){
  var g = document.getElementById("bkgrid");
  g.innerHTML = "";
  var list = bkList();
  if (!list.length){
    var p = document.createElement("p");
    p.className = "bkempty";
    p.textContent = bkEmptyNote();
    g.appendChild(p);
    return;
  }
  list.forEach(function(n){
    var r = BKBY[n]; if (!r) return;
    var fig = document.createElement("figure");
    fig.className = "bkcard" + (bkIn(n) ? " in" : "");
    fig.setAttribute("data-n", n);
    fig.innerHTML = '<img loading=lazy src="img/thumb/' + r.f + '" alt="Frame ' + n + '">' +
      '<span class=bn>' + n + '</span>' +
      '<button class=badd aria-label="Add frame ' + n + ' to the book">' +
      (bkIn(n) ? "&#10003;" : "+") + '</button>';
    fig.querySelector("img").onclick = function(){ bkFull(n); };
    fig.querySelector(".badd").onclick = function(e){ e.stopPropagation(); bkToggle(n); };
    g.appendChild(fig);
  });
}

var bkDrag = null;
function bkStrip(){
  var el = document.getElementById("bkstrip");
  el.innerHTML = "";
  if (!bkBook.length){
    var p = document.createElement("span");
    p.className = "bkempty";
    p.textContent = "The book is empty. Tap a photograph to start it.";
    el.appendChild(p);
  }
  bkBook.forEach(function(n, idx){
    var r = BKBY[n]; if (!r) return;
    var im = document.createElement("img");
    im.src = "img/thumb/" + r.f; im.draggable = true; im.alt = "Frame " + n;
    im.title = "Frame " + n + ". Drag to reorder, double click to remove.";
    im.ondragstart = function(){ bkDrag = idx; };
    im.ondragover = function(e){ e.preventDefault(); im.classList.add("over"); };
    im.ondragleave = function(){ im.classList.remove("over"); };
    im.ondrop = function(e){
      e.preventDefault(); im.classList.remove("over");
      if (bkDrag === null || bkDrag === idx) return;
      var moved = bkBook.splice(bkDrag, 1)[0];
      bkBook.splice(idx, 0, moved);
      bkSave(); bkStrip(); if (bkView === "book") bkGrid();
    };
    im.ondblclick = function(){ bkBook.splice(idx, 1); bkSave(); bkStrip(); bkGrid(); };
    el.appendChild(im);
  });
  document.getElementById("bksee").disabled = !bkBook.length;
  document.getElementById("bksave").disabled = !bkBook.length;
}

/* ---- full size, so a frame is judged before it is chosen ---- */
function bkPaintFullBtn(){
  var b = document.getElementById("bkfadd");
  var isin = bkIn(bkFullAt);
  b.textContent = isin ? "In the book, take it out" : "Add to the book";
}
function bkFull(n){
  var r = BKBY[n]; if (!r) return;
  bkFullAt = n;
  document.getElementById("bkfimg").src = "img/present/" + r.f;
  document.getElementById("bkfn").innerHTML = "<b>Frame " + n + "</b>";
  bkPaintFullBtn();
  var l = bkList();
  document.getElementById("bkfprev").disabled = l.indexOf(n) <= 0;
  document.getElementById("bkfnext").disabled = l.indexOf(n) === l.length - 1;
  document.getElementById("bkfull").classList.add("on");
}
function bkFullStep(d){
  var l = bkList(), i = l.indexOf(bkFullAt);
  if (i === -1) return;
  var j = i + d; if (j < 0 || j >= l.length) return;
  bkFull(l[j]);
}

/* ---- pagination, mirroring build_book.py ---- */
function bkCropLoss(w, h){
  var s = Math.max(BKPW / w, BKPH / h);
  return 1 - (BKPW / (w * s)) * (BKPH / (h * s));
}
function bkPaginate(seq){
  var pages = [], i = 0;
  while (i < seq.length){
    var n = seq[i], r = BKBY[n];
    if (!r || !r.wpx){ pages.push({t:"mat", n:[n], how:"no dimensions"}); i++; continue; }
    var tall = r.hpx > r.wpx;
    var nx = i + 1 < seq.length ? seq[i+1] : null;
    var nr = nx !== null ? BKBY[nx] : null;
    if (tall && nr && nr.wpx && nr.hpx > nr.wpx){
      pages.push({t:"pair", n:[n, nx], how:"two portraits, one page"}); i += 2; continue;
    }
    /* BLEEDHERO (Noah, 2026-08-27, the plaque-wall spread): an establishing frame
       that bleeds on the left, four details facing it on the right. Mirrors the
       bleedhero style in build_book.py, so what shows here is what prints. Fires
       only where the spec asks for it, by frame number, never guessed. */
    var bh = BKBLEEDHERO[n];
    if (bh && bh.every(function(g){ return BKBY[g]; })){
      var lostH = bkCropLoss(r.wpx, r.hpx);
      if (lostH <= 0.12){
        pages.push({t:"bleed", n:[n], how:"full bleed, the establishing frame"});
        pages.push({t:"grid g" + bh.length, n:bh.slice(), how:"the " + bh.length + " it looks at"});
        i++; continue;
      }
    }
    if (BKMATTEALL){
      pages.push({t:"mat", n:[n], how:tall ? "matted, portrait" : "matted, landscape"}); i++; continue;
    }
    var lost = bkCropLoss(r.wpx, r.hpx);
    if (lost > 0.12) pages.push({t:"mat", n:[n], how:"matted"});
    else pages.push({t:"bleed", n:[n], how:"full bleed"});
    i++;
  }
  return pages;
}
function bkSpreads(pages){
  var out = [{cover:true}];
  for (var k = 0; k < pages.length; k += 2)
    out.push({l: pages[k], r: pages[k+1] || null, first: k + 1});
  return out;
}
var BKSP = [], bkAt = 0;
function bkPageHTML(pg){
  if (!pg) return '<div class="bpg"></div>';
  var imgs = pg.n.map(function(n){
    var r = BKBY[n];
    return r ? '<img src="img/present/' + r.f + '" alt="Frame ' + n + '">' : "";
  }).join("");
  return '<div class="bpg ' + pg.t + '">' + imgs + '</div>';
}
function bkShow(i){
  if (i < 0 || i >= BKSP.length) return;
  bkAt = i;
  var s = BKSP[i], sp = document.getElementById("bkspread");
  if (s.cover){
    sp.className = "spread solo";
    sp.innerHTML = '<div class=bcov><h3>Camp Kingswood</h3><div class=brule></div>' +
      '<p class=bsub>Bridgton, Maine &middot; Summer 2026</p>' +
      '<span class=bcred>Photographs by Noah Gallagher</span></div>';
    document.getElementById("bpnum").innerHTML = "<b>COVER</b>";
  } else {
    sp.className = "spread two";
    sp.innerHTML = bkPageHTML(s.l) + bkPageHTML(s.r) + '<span class=bgut></span>';
    var label = s.r ? "PAGES " + s.first + " AND " + (s.first + 1) : "PAGE " + s.first;
    var how = [s.l && s.l.how, s.r && s.r.how].filter(Boolean).join("  &middot;  ");
    document.getElementById("bpnum").innerHTML = "<b>" + label + "</b>  &middot;  " + how;
  }
  document.getElementById("bkvt").innerHTML = "The book, as it lays out <span>&middot; spread " +
    (i + 1) + " of " + BKSP.length + "</span>";
  document.getElementById("bkprev").disabled = i === 0;
  document.getElementById("bknext").disabled = i === BKSP.length - 1;
}

/* ---- saving: it leaves the machine, because the machine may be hers ---- */
function bkPayload(){
  return { group: "The book", frames: bkBook,
           saved: new Date().toISOString(), source: "delivery.html" };
}
function bkToDrive(p){
  if (!BOOKSEND.drive_endpoint) return Promise.reject("no endpoint");
  return fetch(BOOKSEND.drive_endpoint, {method:"POST",
    headers:{"Content-Type":"text/plain;charset=utf-8"}, body:JSON.stringify(p)})
    .then(function(r){ return r.json(); })
    .then(function(r){ if (r && r.ok) return "Drive"; throw new Error("refused"); });
}
function bkToInbox(p){
  if (!BOOKSEND.web3forms_key) return Promise.reject("no key");
  return fetch("https://api.web3forms.com/submit", {method:"POST",
    headers:{"Content-Type":"application/json", Accept:"application/json"},
    body: JSON.stringify({access_key: BOOKSEND.web3forms_key,
      subject: (BOOKSEND.subject || "Kingswood book") + ": " + p.frames.length + " frames",
      from_name: "Kingswood book", botcheck: "", saved: p.saved,
      frames: p.frames.join(", "), lane_json: JSON.stringify(p)})})
    .then(function(r){ return r.json(); })
    .then(function(r){ if (r && r.success) return "inbox"; throw new Error("refused"); });
}
function bkFallback(p){
  try {
    var b = new Blob([JSON.stringify(p, null, 1)], {type:"application/json"});
    var u = URL.createObjectURL(b), a = document.createElement("a");
    a.href = u; a.download = "kingswood_book.json";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(u); }, 1000);
    return true;
  } catch(e){ return false; }
}

function bkWire(){
  document.querySelectorAll(".bkchip").forEach(function(c){
    c.onclick = function(){
      document.querySelectorAll(".bkchip").forEach(function(o){ o.setAttribute("aria-selected","false"); });
      c.setAttribute("aria-selected","true");
      bkView = c.getAttribute("data-view"); bkGrid();
    };
  });
  document.querySelectorAll(".bkwhobtn").forEach(function(b){
    b.onclick = function(){ bkSetWho(b.getAttribute("data-who")); };
  });
  bkPaintWho();
  document.getElementById("bksee").onclick = function(){
    if (!bkBook.length) return;
    BKSP = bkSpreads(bkPaginate(bkBook));
    document.getElementById("bkview").classList.add("on");
    bkShow(0);
  };
  document.getElementById("bkclose").onclick = function(){ document.getElementById("bkview").classList.remove("on"); };
  document.getElementById("bknext").onclick = function(){ bkShow(bkAt + 1); };
  document.getElementById("bkprev").onclick = function(){ bkShow(bkAt - 1); };
  document.getElementById("bkfclose").onclick = function(){ document.getElementById("bkfull").classList.remove("on"); };
  document.getElementById("bkfnext").onclick = function(){ bkFullStep(1); };
  document.getElementById("bkfprev").onclick = function(){ bkFullStep(-1); };
  document.getElementById("bkfadd").onclick = function(){ bkToggle(bkFullAt); };

  document.getElementById("bksave").onclick = function(){
    var b = document.getElementById("bksave");
    if (!bkBook.length) return;
    var p = bkPayload();
    var reset = function(t){ b.textContent = t;
      setTimeout(function(){ b.textContent = "Save the book"; b.disabled = false; }, 2600); };
    b.disabled = true; b.textContent = "Saving";
    bkToDrive(p).catch(function(){ return bkToInbox(p); })
      .then(function(w){ reset("Banked, " + w); })
      .catch(function(){ reset(bkFallback(p) ? "No connection, saved here" : "Could not save"); });
  };

  document.addEventListener("keydown", function(e){
    var full = document.getElementById("bkfull").classList.contains("on");
    var view = document.getElementById("bkview").classList.contains("on");
    if (full){
      if (e.key === "Escape") document.getElementById("bkfull").classList.remove("on");
      if (e.key === "ArrowRight"){ e.preventDefault(); bkFullStep(1); }
      if (e.key === "ArrowLeft"){ e.preventDefault(); bkFullStep(-1); }
      if (e.key === " "){ e.preventDefault(); bkToggle(bkFullAt); }
      return;
    }
    if (view){
      if (e.key === "Escape") document.getElementById("bkview").classList.remove("on");
      if (e.key === "ArrowRight" || e.key === " "){ e.preventDefault(); bkShow(bkAt + 1); }
      if (e.key === "ArrowLeft") bkShow(bkAt - 1);
    }
  });
  bkGrid(); bkStrip();
}
"""
