#!/usr/bin/env python3
"""Builds the Kingswood arrangement tool: drag frames into groups you make up as
you go. Ported 2026-08-19 from the Interlaken arrange page at Noah's direction
("I need all of them in the way that we set up the Interlaken grouping and
selection page. Just an easy drag and drop into a group, create group thing.
That was the best interface for this.").

The model, unchanged from Interlaken: GROUPS HOLD COPIES. Pulling a frame into a
group never removes it from anywhere else, and one frame can sit in as many
groups as it needs. All frames stays whole at the bottom as the palette; the gold
badge on a palette frame counts how many groups hold it. No quota, no required
groups: every seeded group can be renamed or deleted in one click.

Two builds:
    python3 build_arrange.py local      -> _work/arrange.html
        Relative paths to img/. Full-size in the viewer. Best on the Mac.
    python3 build_arrange.py artifact   -> _work/arrange_portable.html
        Embeds 700px copies, self-contained, publishable, works on the phone.

The record: "Copy the arrangement" puts JSON on the clipboard. Paste it into a
session and it is saved to _work/arrangement_kw.json, which then SEEDS this page
on every later build. localStorage only lives in one browser on one origin; the
file is what makes the work survive a rebuild, a new device, or a new session.

Seeded groups are observations from the set read on 2026-08-19, offered as a
head start, not a structure: the proposed forty-two, and the three runs that are
plainly in the take (Shabbat, the sign, night and stars).
"""
import base64, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRESENT = os.path.join(HERE, "img", "present")
THUMB = os.path.join(HERE, "img", "thumb")
SAVED = os.path.join(HERE, "_work", "arrangement_kw.json")
KEY = "kwood-arrange-v1"

BOOK_GROUP = "The book"

SEED_GROUPS = [
    ("Shabbat", list(range(49, 65))),
    ("The sign", [13, 14, 21, 23, 24, 25, 26, 27, 30, 45, 108, 109, 122]),
    ("Night and stars", [31, 32, 34, 35, 36, 37, 38, 39, 101, 102, 103, 104,
                         105, 106, 107, 110, 117]),
]


def frame_no(f):
    """The bare kwood819.jpg is frame 1; numbers run 2 to 122 (83 absent). The _2
    re-edit set (2026-08-19) is 201-206: kwood819_2.jpg is 201, kwood819_2-N is 200+N."""
    m = re.search(r"_2-(\d+)\.jpg$", f)
    if m: return 200 + int(m.group(1))
    if f.endswith("_2.jpg"): return 201
    # The 2026-08-20 export (kwood820-*) is 300-341; the bare file is 301.
    m = re.search(r"kwood820-(\d+)\.jpg$", f)
    if m: return 300 + int(m.group(1))
    if f.endswith("kwood820.jpg"): return 301
    m = re.search(r"-(\d+)\.jpg$", f)
    return int(m.group(1)) if m else 1


def build(mode):
    files = sorted((f for f in os.listdir(PRESENT) if f.endswith(".jpg")), key=frame_no)
    allf = [frame_no(f) for f in files]
    by_num = {frame_no(f): f for f in files}

    proposed = []
    p42 = os.path.join(HERE, "forty_two.json")
    if os.path.exists(p42):
        proposed = [frame_no(f) for f in json.load(open(p42))]

    if os.path.exists(SAVED):
        a = json.load(open(SAVED))
        groups = [{"name": g["name"], "frames": [n for n in g["frames"] if n in by_num]}
                  for g in a.get("groups", [])]
        aside = [n for n in a.get("aside", []) if n in by_num]
        seeded_from = "your saved arrangement"
        # Frames ingested since the saved pass land in their own group so they
        # are seen, not buried in the palette (first use: the _2 re-edit set).
        known = set(aside)
        for g in a.get("groups", []):
            known.update(g["frames"])
        known.update(a.get("ungrouped", []))
        fresh = [n for n in allf if n not in known]
        if fresh:
            groups.insert(0, {"name": "New since your last pass", "frames": fresh})
        # The dedicated book's lane. ORDER IN THIS LANE IS THE BOOK'S SEQUENCE, first
        # frame to last, which is why it is a lane and not a checkbox: a book is
        # an order, not a set. Seeded empty and only when absent, so a pass that
        # already filled it is never overwritten. Constraint on file (2026-08-07):
        # non-identifiable kids only.
        if not any(g["name"] == BOOK_GROUP for g in groups):
            groups.insert(0, {"name": BOOK_GROUP, "frames": []})
    else:
        groups = []
        if proposed:
            groups.append({"name": "Proposed forty-two", "frames": proposed})
        groups += [{"name": nm, "frames": [n for n in ns if n in by_num]}
                   for nm, ns in SEED_GROUPS]
        aside = []
        seeded_from = "a starting sketch you can gut"

    if mode == "artifact":
        from PIL import Image
        src = {}
        for n, f in by_num.items():
            im = Image.open(os.path.join(PRESENT, f))
            im.thumbnail((560, 560), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=63, optimize=True)
            # One copy per frame, not two: the viewer falls back to the thumb source.
            # Storing it under both keys doubled the page and blew the size ceiling.
            src[n] = {"t": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()}
        out = os.path.join(HERE, "_work", "arrange_portable.html")
    else:
        src = {n: {"t": "../img/thumb/" + f, "p": "../img/present/" + f}
               for n, f in by_num.items()}
        out = os.path.join(HERE, "_work", "arrange.html")

    # THE RESOLUTION STANDARD (Noah, 2026-08-20): fullscreen play renders the
    # 2560 tier. The portable build can only embed small previews (16MB artifact
    # cap), so it declares itself on its face; judgment happens on the Mac
    # build, where play is sharp.
    banner = ("" if mode != "artifact" else
              '<div style="position:sticky;top:0;z-index:40;background:#3a2f14;'
              'color:#e2c46a;font-size:11.5px;padding:5px 12px;text-align:center">'
              'PREVIEW BUILD: arrange anywhere. Playback here is preview quality; '
              'sharp play lives on the Mac build.</div>')
    html = (PAGE.replace('</style>', '</style>' + banner, 1)
                .replace("__SRC__", json.dumps(src))
                .replace("__ALL__", json.dumps(allf))
                .replace("__SEED__", json.dumps({"groups": groups, "aside": aside}))
                .replace("__KEY__", KEY)
                .replace("__N__", str(len(allf)))
                .replace("__FROM__", seeded_from))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)
    # Local builds sit in _work/ and reference ../img/, and browsers refuse that
    # parent traversal over file://, so the board opens with every frame blank.
    # Serve the hub instead; nothing about the page needs fixing.
    if mode != "artifact":
        print("  serve it, do not double-click it:")
        print("    cd " + HERE)
        print("    python3 -m http.server 8899 --bind 127.0.0.1")
        print("    open http://127.0.0.1:8899/_work/arrange.html")
    print(f"wrote {out} ({os.path.getsize(out)//1048576} MB, {len(allf)} frames, "
          f"{len(groups)} groups seeded from {seeded_from})")


PAGE = """<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Camp Kingswood &middot; arrange</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#14110d;color:#ede7dd;
     font-family:"Avenir Next",Avenir,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;
     padding-bottom:70px}
header{position:sticky;top:0;z-index:9;background:rgba(24,20,15,.97);
       border-bottom:1px solid rgba(226,167,62,.35);padding:12px 18px;
       display:flex;align-items:center;gap:10px;flex-wrap:wrap}
h1{font-family:"Iowan Old Style",Palatino,Georgia,serif;font-weight:600;font-size:19px;margin-right:auto}
header button{background:none;border:1px solid rgba(226,167,62,.55);color:#e2a73e;
              padding:8px 13px;border-radius:3px;font-size:12px;letter-spacing:.08em;
              text-transform:uppercase;cursor:pointer;font-family:inherit}
header button.go{background:#e2a73e;color:#14110d;font-weight:600}
header button:hover{background:rgba(226,167,62,.14)}
header button.go:hover{background:#ecb654}
.help{width:100%;color:#a69b8a;font-size:12.5px;line-height:1.55;max-width:96ch}
.grp{max-width:1400px;margin:20px auto 0;padding:0 14px}
.ghead{display:flex;align-items:center;gap:10px;border-bottom:1px solid rgba(237,231,221,.14);
       padding-bottom:6px;cursor:pointer}
.gname{font-family:"Iowan Old Style",Palatino,Georgia,serif;font-size:18px;color:#c9bfa9;font-weight:500}
.gcnt{font-size:12px;color:#7d745f;font-variant-numeric:tabular-nums}
.ghead .tools{margin-left:auto;display:flex;gap:6px}
.ghead .tools button{background:none;border:1px solid rgba(237,231,221,.25);color:#a69b8a;
                     border-radius:3px;font-size:12px;padding:4px 9px;cursor:pointer;font-family:inherit}
.ghead .tools button:hover{border-color:#e2a73e;color:#e2a73e}
.lane{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;
      padding:12px 0 4px;min-height:60px}
.lane.over{outline:2px dashed rgba(226,167,62,.6);outline-offset:4px}
.th{position:relative;cursor:grab;border-radius:3px;overflow:hidden;background:#1d1913;content-visibility:auto;contain-intrinsic-size:150px 112px}
.th img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;pointer-events:none}
.th .n{position:absolute;left:5px;bottom:4px;font-size:10.5px;color:#cfc6b4;
       text-shadow:0 1px 4px #000;pointer-events:none;font-family:"SF Mono",ui-monospace,Menlo,monospace}
.th .v{position:absolute;top:4px;right:4px;width:24px;height:24px;border:0;border-radius:3px;
       background:rgba(20,17,13,.55);color:#ede7dd;font-size:12px;cursor:pointer;line-height:24px}
.th .rm{position:absolute;top:4px;left:4px;width:24px;height:24px;border:0;border-radius:3px;
        background:rgba(20,17,13,.55);color:#ede7dd;font-size:15px;cursor:pointer;line-height:24px}
.th .u{position:absolute;top:4px;left:4px;min-width:20px;height:20px;border-radius:10px;
       background:#e2a73e;color:#14110d;font-size:11px;font-weight:700;line-height:20px;
       text-align:center;padding:0 4px;pointer-events:none}
.th.parked img{opacity:.35}
.th.sel{outline:3px solid #e2a73e;outline-offset:-3px}
.th.drag{opacity:.35}
.th.mark{outline:2px dashed rgba(226,167,62,.8);outline-offset:-2px}
#toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#ede7dd;color:#14110d;
       padding:10px 16px;border-radius:4px;font-size:13px;opacity:0;pointer-events:none;
       transition:opacity .25s;z-index:12;max-width:88vw;text-align:center}
#toast.on{opacity:1}
#dock{position:fixed;right:10px;top:50%;transform:translateY(-50%);z-index:11;display:none;
      flex-direction:column;gap:6px;max-height:80vh;overflow-y:auto;background:rgba(24,20,15,.97);
      border:1px solid rgba(226,167,62,.45);border-radius:6px;padding:10px}
#dock.on{display:flex}
#dock .dk{border:1px solid rgba(237,231,221,.3);border-radius:4px;padding:9px 14px;font-size:13px;
          color:#c9bfa9;min-width:150px;text-align:left}
#dock .dk.hot{background:#e2a73e;color:#14110d;border-color:#e2a73e;font-weight:600}
#dock .lbl{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:#7d745f;padding:0 2px}
#lb{position:fixed;inset:0;background:rgba(10,8,6,.97);display:none;align-items:center;
    justify-content:center;z-index:10}
#lb.on{display:flex}
#lb img{max-width:100vw;max-height:100vh;object-fit:contain}
/* Play a group as a slideshow without leaving the arranger (Noah, 2026-08-20:
   "connect it to the arranger"). Zones are stripped buttons: default ButtonFace
   chrome painted white bars on the stage once already. */
#stage{position:fixed;inset:0;z-index:60;background:#000;display:none}
#stage.on{display:block}
#stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
           opacity:0;transition:opacity 800ms ease}
#stage img.show{opacity:1}
#stage .zone{position:absolute;top:0;bottom:0;width:30%;z-index:2;cursor:pointer;
             background:none;border:0;padding:0;appearance:none}
#stage .zl{left:0}#stage .zr{right:0}
#stage .x{position:fixed;top:8px;right:12px;z-index:3;font-size:30px;color:#a69b8a;
          background:none;border:0;cursor:pointer}
#lb .x{position:fixed;top:8px;right:12px;font-size:30px;color:#a69b8a;background:none;border:0;
       cursor:pointer;padding:6px 10px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
<header>
  <h1>Arrange the Kingswood set</h1>
  <button id=ng type=button>+ Group</button>
  <button id=rs type=button>Start over</button>
  <button id=cp class=go type=button>Copy the arrangement</button>
  <div class=help>All __N__ frames, in shoot order, seeded from __FROM__. No quota and no
    required groups: rename or delete any of them. Groups hold copies, so pulling a frame
    into a group never takes it out of anywhere else and one frame can live in as many
    groups as it needs. Drag from All frames into a group to add it, drag between groups to
    move, and the &#215; on a copy takes it out of that group only. Tapping works the same:
    tap a frame, then tap a group title to add it there, or tap a frame inside a group to
    slot in front of it. While you drag, a dock of group names appears on the right, and the
    page scrolls itself near the edges. &#8599; shows a frame large. The gold badge in All
    frames counts the groups holding that frame. Everything saves as you go; Copy the
    arrangement when you want it on the record.</div>
</header>
<div id=board></div>
<div id=dock></div>
<div id=toast></div>
<div id=lb><img id=lbi alt=""><button class=x type=button aria-label="Close">&times;</button></div>
<div id=stage><img id=sa alt=""><img id=sb alt="">
  <button class="zone zl" type=button aria-label=Previous></button>
  <button class="zone zr" type=button aria-label=Next></button>
  <button class=x type=button aria-label="End the show">&times;</button></div>
<script>
var SRC=__SRC__, ALL=__ALL__, SEED=__SEED__, KEY="__KEY__";
var state=null, sel=null, dragEl=null, tt=null;
function $(i){return document.getElementById(i);}
function toast(m){var t=$("toast");t.textContent=m;t.className="on";
  clearTimeout(tt);tt=setTimeout(function(){t.className="";},2400);}
function load(){try{var s=JSON.parse(localStorage.getItem(KEY));
  if(s&&s.groups)return {groups:s.groups,aside:s.aside||[]};}catch(e){}
  return JSON.parse(JSON.stringify(SEED));}
function read(){var gs=[],aside=[];
  document.querySelectorAll(".grp").forEach(function(g){
    if(g.dataset.kind==="pal")return;
    var ns=Array.from(g.querySelectorAll(".th")).map(function(t){return +t.dataset.n;});
    if(g.dataset.kind==="aside")aside=ns;
    else gs.push({name:g.querySelector(".gname").textContent,frames:ns});});
  state={groups:gs,aside:aside};}
function save(){read();try{localStorage.setItem(KEY,JSON.stringify(state));}catch(e){}count();}
function dupe(laneEl,n,skip){return Array.from(laneEl.querySelectorAll(".th")).some(
  function(t){return +t.dataset.n===n&&t!==skip;});}
function place(el,src,laneEl,before){
  var pal=laneEl.closest(".grp").dataset.kind==="pal";
  if(pal){if(src==="g"){el.remove();save();}return;}
  var n=+el.dataset.n;
  if(src==="p"){if(dupe(laneEl,n)){toast(n+" is already in that group.");return;}
    var c=thumb(n,"g");before?laneEl.insertBefore(c,before):laneEl.appendChild(c);save();}
  else{if(laneEl!==el.parentNode&&dupe(laneEl,n,el)){toast(n+" is already in that group.");return;}
    before?laneEl.insertBefore(el,before):laneEl.appendChild(el);save();}}
function thumb(n,kind){var d=document.createElement("div");
  d.className="th";d.dataset.n=n;d.dataset.src=kind;d.draggable=true;
  d.innerHTML='<img loading="lazy" src="'+SRC[n].t+'" alt="frame '+n+'">'+
    '<span class="n">'+n+'</span>'+
    (kind==="p"?'<span class="u" style="display:none"></span>'
              :'<button class="rm" type="button" aria-label="Take out of this group">&#215;</button>')+
    '<button class="v" type="button" aria-label="View large">&#8599;</button>';
  d.addEventListener("dragstart",function(e){dragEl=d;d.classList.add("drag");dock(true);
    e.dataTransfer.effectAllowed="copyMove";try{e.dataTransfer.setData("text/plain",String(n));}catch(x){}});
  d.addEventListener("dragend",function(){d.classList.remove("drag");dock(false);
    document.querySelectorAll(".th.mark").forEach(function(m){m.classList.remove("mark");});
    document.querySelectorAll(".lane.over").forEach(function(l){l.classList.remove("over");});});
  d.addEventListener("dragover",function(e){e.preventDefault();
    if(dragEl&&dragEl!==d)d.classList.add("mark");});
  d.addEventListener("dragleave",function(){d.classList.remove("mark");});
  d.addEventListener("drop",function(e){e.preventDefault();e.stopPropagation();
    d.classList.remove("mark");
    if(dragEl&&dragEl!==d)place(dragEl,dragEl.dataset.src,d.parentNode,d);dragEl=null;});
  d.querySelector(".v").onclick=function(e){e.stopPropagation();
    $("lbi").src=SRC[n].p||SRC[n].t;$("lb").className="on";};
  if(kind==="g")d.querySelector(".rm").onclick=function(e){e.stopPropagation();
    if(sel===d)sel=null;d.remove();save();};
  d.onclick=function(){
    if(sel===d){d.classList.remove("sel");sel=null;return;}
    if(sel){place(sel,sel.dataset.src,d.parentNode,d);sel.classList.remove("sel");sel=null;return;}
    sel=d;d.classList.add("sel");};
  return d;}
function lane(){var l=document.createElement("div");l.className="lane";
  l.addEventListener("dragover",function(e){e.preventDefault();l.classList.add("over");});
  l.addEventListener("dragleave",function(){l.classList.remove("over");});
  l.addEventListener("drop",function(e){e.preventDefault();l.classList.remove("over");
    if(dragEl)place(dragEl,dragEl.dataset.src,l,null);dragEl=null;});
  return l;}
function section(kind,name,ns){var g=document.createElement("div");
  g.className="grp";g.dataset.kind=kind;
  var h=document.createElement("div");h.className="ghead";
  h.innerHTML='<span class="gname"></span><span class="gcnt"></span>';
  h.querySelector(".gname").textContent=name;
  if(kind==="g"){var t=document.createElement("span");t.className="tools";
    var pb=document.createElement("button");pb.type="button";pb.textContent="\u25b6 play";
    pb.onclick=function(e){e.stopPropagation();
      var ns=[].map.call(g.querySelectorAll(".lane .th"),function(t){return +t.dataset.n;});
      if(ns.length)playShow(ns);};
    t.appendChild(pb);
    ["\\u2191","\\u2193"].forEach(function(a,i){var b=document.createElement("button");
      b.type="button";b.textContent=a;
      b.onclick=function(e){e.stopPropagation();
        var sib=i?g.nextElementSibling:g.previousElementSibling;
        if(!sib||sib.dataset.kind!=="g")return;
        if(i)g.parentNode.insertBefore(sib,g);else g.parentNode.insertBefore(g,sib);
        save();};t.appendChild(b);});
    var r=document.createElement("button");r.type="button";r.textContent="rename";
    r.onclick=function(e){e.stopPropagation();
      var nm=window.prompt("Group name",g.querySelector(".gname").textContent);
      if(nm){g.querySelector(".gname").textContent=nm;save();}};t.appendChild(r);
    var x=document.createElement("button");x.type="button";x.textContent="\\u00d7";
    x.onclick=function(e){e.stopPropagation();
      if(!window.confirm("Delete this group? Its copies go away; every frame stays in All frames."))return;
      if(sel&&sel.closest(".grp")===g)sel=null;g.remove();save();};t.appendChild(x);
    h.appendChild(t);}
  h.onclick=function(){if(sel){place(sel,sel.dataset.src,g.querySelector(".lane"),null);
    sel.classList.remove("sel");sel=null;}};
  g.appendChild(h);
  var l=lane();var tk=kind==="pal"?"p":"g";
  ns.forEach(function(n){if(SRC[n])l.appendChild(thumb(n,tk));});
  g.appendChild(l);
  return g;}
function count(){var use={},aside={};
  document.querySelectorAll('.grp[data-kind="g"] .th').forEach(function(t){
    use[t.dataset.n]=(use[t.dataset.n]||0)+1;});
  document.querySelectorAll('.grp[data-kind="aside"] .th').forEach(function(t){aside[t.dataset.n]=1;});
  document.querySelectorAll(".grp").forEach(function(g){
    g.querySelector(".gcnt").textContent="("+g.querySelectorAll(".th").length+")";});
  document.querySelectorAll('.grp[data-kind="pal"] .th').forEach(function(t){
    var n=t.dataset.n,b=t.querySelector(".u"),c=use[n]||0;
    b.textContent=c;b.style.display=c?"":"none";
    t.classList.toggle("parked",!!aside[n]);});}
function render(){var b=$("board");b.innerHTML="";
  state.groups.forEach(function(gr){b.appendChild(section("g",gr.name,gr.frames));});
  b.appendChild(section("aside","Set aside",state.aside));
  b.appendChild(section("pal","All frames",ALL));
  count();}
function dock(on){var k=$("dock");if(!on){k.className="";return;}
  k.innerHTML='<span class="lbl">Drop on a group</span>';
  document.querySelectorAll('.grp[data-kind="g"],.grp[data-kind="aside"]').forEach(function(g){
    var row=document.createElement("div");row.className="dk";
    row.textContent=g.querySelector(".gname").textContent;
    row.addEventListener("dragover",function(e){e.preventDefault();row.classList.add("hot");});
    row.addEventListener("dragleave",function(){row.classList.remove("hot");});
    row.addEventListener("drop",function(e){e.preventDefault();row.classList.remove("hot");
      if(dragEl)place(dragEl,dragEl.dataset.src,g.querySelector(".lane"),null);
      dragEl=null;dock(false);});
    k.appendChild(row);});
  k.className="on";}
document.addEventListener("dragover",function(e){
  var m=150,b=100,y=e.clientY,h=window.innerHeight;
  if(y<m)window.scrollBy(0,-Math.ceil((m-y)*.35));
  else if(y>h-b)window.scrollBy(0,Math.ceil((y-(h-b))*.35));});
state=load();render();
$("ng").onclick=function(){var nm=window.prompt("Group name","");if(!nm)return;
  var aside=document.querySelector('.grp[data-kind="aside"]');
  aside.parentNode.insertBefore(section("g",nm,[]),aside);save();
  toast("Group added. Drag frames into it.");};
$("rs").onclick=function(){
  if(window.confirm("Throw away this arrangement and go back to the seeded one?")){
    try{localStorage.removeItem(KEY);}catch(e){}
    state=JSON.parse(JSON.stringify(SEED));sel=null;render();}};
$("cp").onclick=function(){read();
  var used={};state.groups.forEach(function(g){g.frames.forEach(function(n){used[n]=1;});});
  state.aside.forEach(function(n){used[n]=1;});
  var exp={groups:state.groups,aside:state.aside,
           ungrouped:ALL.filter(function(n){return !used[n];})};
  var s=JSON.stringify(exp,null,1);
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(s).then(
      function(){toast("Arrangement copied. Paste it to me and it goes on the record.");},
      function(){window.prompt("Copy this:",s);});}
  else window.prompt("Copy this:",s);};
document.querySelector("#lb .x").onclick=function(){$("lb").className="";};
$("lb").onclick=function(e){if(e.target.id==="lb")$("lb").className="";};
var shFrames=[],shIdx=0,shTimer=null,shFront=null;
function shRender(){if(shIdx<0)shIdx=shFrames.length-1;if(shIdx>=shFrames.length)shIdx=0;
  var inc=(shFront===$("sa"))?$("sb"):$("sa"),out=(shFront===$("sa"))?$("sa"):$("sb");
  inc.className="";void inc.offsetWidth;
  inc.onload=function(){inc.className="show";out.className="";shFront=inc;};
  var n=shFrames[shIdx];inc.src=SRC[n].p||SRC[n].t;
  if(inc.complete)inc.onload();}
function shTick(){shTimer=setTimeout(function(){shIdx++;shRender();shTick();},5000);}
function shEnd(){clearTimeout(shTimer);$("stage").className="";}
function playShow(ns){shFrames=ns;shIdx=0;shFront=null;
  $("sa").className="";$("sb").className="";$("stage").className="on";shRender();shTick();}
document.querySelector("#stage .x").onclick=shEnd;
document.querySelector("#stage .zl").onclick=function(){clearTimeout(shTimer);shIdx--;shRender();shTick();};
document.querySelector("#stage .zr").onclick=function(){clearTimeout(shTimer);shIdx++;shRender();shTick();};
document.addEventListener("keydown",function(e){
  if($("stage").className==="on"){
    if(e.key==="Escape")shEnd();
    else if(e.key==="ArrowRight"){clearTimeout(shTimer);shIdx++;shRender();shTick();}
    else if(e.key==="ArrowLeft"){clearTimeout(shTimer);shIdx--;shRender();shTick();}
    return;}
  if(e.key==="Escape"&&$("lb").className==="on")$("lb").className="";});
</script>
"""


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "local")
