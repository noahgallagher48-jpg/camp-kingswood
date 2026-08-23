#!/usr/bin/env python3
"""Builds the Camp Kingswood delivery page (delivery.html), in the shape of the
Interlaken delivery page, wearing the camp's OWN brand: ground #062A40,
vermilion #DB3A00, warm white #F3F1EC, typeface Raleway. Those values were read
off campkingswood.org's live computed styles on 2026-08-20, replacing colours I
had matched by eye (the ground was wrong: #112337 vs their #062A40).

The pool comes from the owner's arrangement (_work/arrangement_kw.json): every
frame EXCEPT the set-aside ten (replaced by the _2 re-edits, his call 8/19).
Noah's Picks reader leads with his top-choices group. Full-resolution downloads
come from Drive per frame (_work/drive_ids_kw.json); web downloads come from
img/present in this repo.

Commands:
    python3 build_delivery.py ingest /path/to/folder    (web tiers from masters)
    python3 build_delivery.py zip                        (pool web zip -> downloads/)
    python3 build_delivery.py build                      (delivery.html)

RELEASES: not connected to this delivery (Noah, 2026-08-19). The camp is
receiving photographs of its own community; the camp holds that relationship.

The "All for web" zip lives on DRIVE (Interlaken precedent; GitHub caps files
at 100MB). ZIP_URL below stays empty until the zip is uploaded and its uc id
is on file; the button hides itself while empty.
"""
import json, os, re, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
PAGE_OUT = os.path.join(HERE, "delivery.html")
ARR = os.path.join(HERE, "_work", "arrangement_kw.json")
DRIVE_IDS = os.path.join(HERE, "_work", "drive_ids_kw.json")
FOLDER_URL = "https://drive.google.com/drive/folders/1XqShLle7YVldJ6zmcd36SLBIZ_auyHYL"
# Zip link. NOT DRIVE, for a large file: Drive cannot virus-scan anything this
# big, so uc?export=download serves a "Virus scan warning" page, and the
# file-view form makes the client click Download a SECOND time. Noah, 2026-08-19:
# "I have to click twice to get to the thing, and that can't happen."
# A GitHub release asset streams the bytes on the first click (verified: 206,
# application/octet-stream) with no wrapper and no account. Zips ship from
# releases; per-frame masters stay on Drive, where uc?export=download is a real
# one-click download under the ~100MB scan limit.
ZIP_URL = ("https://github.com/noahgallagher48-jpg/camp-kingswood/releases/"
           "download/kingswood-2026-web/kingswood_web.zip")


def frame_no(f):
    m = re.search(r"_2-(\d+)\.jpg$", f)
    if m: return 200 + int(m.group(1))
    if f.endswith("_2.jpg"): return 201
    m = re.search(r"kwood820-(\d+)\.jpg$", f)
    if m: return 300 + int(m.group(1))
    if f.endswith("kwood820.jpg"): return 301
    m = re.search(r"-(\d+)\.jpg$", f)
    return int(m.group(1)) if m else 1


def pool():
    # The 2026-08-20 export is IN the delivery (Noah, 2026-08-20: "put all the
    # new ones in ... give me the whole thing"). The pool is everything on disk
    # minus the set-aside list; the aside list in the RECORD is the only fence.
    files = sorted((f for f in os.listdir(os.path.join(IMG, "present"))
                    if f.endswith(".jpg")), key=frame_no)
    by_num = {frame_no(f): f for f in files}
    a = json.load(open(ARR))
    aside = set(a.get("aside", []))
    keep = [n for n in sorted(by_num) if n not in aside]
    # picks selected BY NAME: groups[0] silently became "New since your last
    # pass" when the arrange tool reordered groups (same trap as the client
    # slideshow cut, caught 2026-08-20).
    by_name = {g["name"]: g["frames"] for g in a["groups"]}
    picks_src = by_name.get("Noah's Picks", a["groups"][0]["frames"])
    picks = [n for n in picks_src if n in by_num and n not in aside]
    return by_num, keep, picks


def ingest(folder):
    import io
    from PIL import Image, ImageCms
    os.makedirs(os.path.join(IMG, "web"), exist_ok=True)
    os.makedirs(os.path.join(IMG, "present"), exist_ok=True)
    os.makedirs(os.path.join(IMG, "thumb"), exist_ok=True)
    srgb = ImageCms.createProfile("sRGB")
    srgb_icc = ImageCms.ImageCmsProfile(srgb).tobytes()
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg")))
    for n in names:
        im = Image.open(os.path.join(folder, n))
        icc = im.info.get("icc_profile")
        im = im.convert("RGB")
        if icc:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            if "sRGB" not in ImageCms.getProfileDescription(src):
                im = ImageCms.profileToProfile(im, src, srgb, outputMode="RGB",
                    renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
        out = os.path.splitext(n)[0] + ".jpg"
        # Deliverable web tier, THE RULE (Noah, 2026-08-19): 3840px long edge,
        # q90, 4:4:4. Anything smaller is display-only and never ships as "web".
        # After ingest, run ./process_masters.sh img/web (credits; Pillow drops them).
        w = im.copy(); w.thumbnail((3840, 3840), Image.LANCZOS)
        w.save(os.path.join(IMG, "web", out), quality=90, icc_profile=srgb_icc, subsampling=0)
        a = im.copy(); a.thumbnail((2560, 2560), Image.LANCZOS)
        a.save(os.path.join(IMG, "present", out), quality=88, icc_profile=srgb_icc, subsampling=0)
        b = im.copy(); b.thumbnail((900, 900), Image.LANCZOS)
        b.save(os.path.join(IMG, "thumb", out), quality=82, icc_profile=srgb_icc)
    print(f"ingested {len(names)} frames")


def make_zip():
    by_num, keep, _ = pool()
    os.makedirs(os.path.join(HERE, "downloads"), exist_ok=True)
    out = os.path.join(HERE, "downloads", "kingswood_web.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
        for n in keep:
            z.write(os.path.join(IMG, "web", by_num[n]), by_num[n])
    print(f"wrote {out} ({os.path.getsize(out)//1048576} MB, {len(keep)} frames)")


def build():
    by_num, keep, picks = pool()
    drive = json.load(open(DRIVE_IDS)) if os.path.exists(DRIVE_IDS) else {}
    # Web tier lives on DRIVE since 2026-08-20, not in git: JPEGs do not delta-
    # compress, so re-stamping metadata and re-committing tripled the repo and
    # pushed it to 95% of the 1GB Pages limit. Per-frame files are 3-7MB, under
    # Drive's ~100MB scan limit, so uc?export=download is a true one-click.
    webids = os.path.join(HERE, "_work", "drive_web_ids_kw.json")
    web = json.load(open(webids)) if os.path.exists(webids) else {}
    # Print guidance is a STANDING component of every client delivery page
    # (Noah, 2026-08-19), sized off the master's true resolution and limited to
    # sizes a client can buy without a custom order. Shared rules so every
    # engagement gives the same answer: dashboard/tools/print_sizes.py
    sys.path.insert(0, os.path.expanduser("~/Abba_Photo/dashboard/tools"))
    from print_sizes import print_line
    dims = json.load(open(os.path.join(HERE, "_work", "dims_kw.json")))

    def rec(n):
        f = by_num[n]
        d = drive.get(f)
        w, h = dims.get(f, (0, 0))
        p = print_line(w, h) if w else {"metal": None, "paper": None,
                                        "canvas": None, "note": None}
        wd = web.get(f)
        return {"n": n, "f": f,
                "d": f"https://drive.google.com/uc?export=download&id={d}" if d else None,
                "w": f"https://drive.google.com/uc?export=download&id={wd}" if wd else None,
                "p": [p["metal"], p["paper"], p["canvas"]], "pn": p["note"],
                "wpx": w, "hpx": h}
    data_all = [rec(n) for n in keep]
    data_picks = [rec(n) for n in picks]
    page = (PAGE.replace("</style>", SEL_CSS + "</style>")
                .replace("</body>", SEL_HTML + "<script>" + SEL_JS + """
$("seldl").onclick=downloadAll;
$("selplay").onclick=playSelection;
$("selwall").onclick=openWall;
$("selbook").onclick=openBook;
</script></body>"""))
    html = (page.replace("__ALL__", json.dumps(data_all))
                .replace("__PICKS__", json.dumps(data_picks))
                .replace("__N__", str(len(keep)))
                .replace("__NP__", str(len(picks)))
                .replace("__FOLDER__", FOLDER_URL)
                .replace("__ZIP__", ZIP_URL))
    open(PAGE_OUT, "w").write(html)
    missing = [r["n"] for r in data_all if not r["d"]]
    print(f"wrote delivery.html ({len(keep)} frames, {len(picks)} picks; "
          f"full-res pending for {missing if missing else 'none'})")


sys.path.insert(0, os.path.expanduser("~/Abba_Photo/dashboard/tools"))
from selection_actions import CSS as SEL_CSS, HTML as SEL_HTML, JS as SEL_JS

PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Camp Kingswood &middot; Summer 2026</title><style>
/* The camp's own brand, read off campkingswood.org's live computed styles
   2026-08-20, not eyeballed: ground #062A40, accent #DB3A00, warm white
   #F3F1EC, typeface Raleway (400/600/800). Noah's rule: when the client has a
   palette and a face, the delivery wears theirs, not ours. */
@font-face{font-family:Raleway;src:url(fonts/raleway-400.woff2) format('woff2');
           font-weight:400;font-display:swap}
@font-face{font-family:Raleway;src:url(fonts/raleway-600.woff2) format('woff2');
           font-weight:600;font-display:swap}
@font-face{font-family:Raleway;src:url(fonts/raleway-800.woff2) format('woff2');
           font-weight:800;font-display:swap}
:root{--ground:#062A40;--panel:#0C3A55;--line:rgba(243,241,236,.13);
      --ink:#F3F1EC;--muted:#9CAABF;--faint:#6E7E94;--accent:#DB3A00;--accent2:#F04A0E}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--ground);color:var(--ink);
     font-family:Raleway,"Avenir Next",-apple-system,Helvetica,Arial,sans-serif;
     font-size:15.5px;line-height:1.55}
a{color:var(--accent2);text-decoration:none}a:hover{text-decoration:underline}
.home{position:absolute;top:16px;left:20px;font-size:12px;letter-spacing:.14em;
      text-transform:uppercase;color:var(--faint)}
.open{max-width:720px;margin:0 auto;padding:84px 20px 46px;text-align:center}
h1{font-family:Raleway,"Avenir Next",sans-serif;font-weight:800;letter-spacing:-.01em;
   font-size:clamp(32px,6vw,46px);letter-spacing:.01em}
.date{color:var(--muted);font-size:14.5px;margin-top:6px}
.rule{width:56px;height:2px;background:var(--accent);margin:22px auto}
.play{background:var(--accent);color:#fff;border:0;border-radius:5px;padding:13px 30px;
      font-size:14px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
      cursor:pointer;font-family:inherit}
.play:hover{background:var(--accent2)}
.play:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
.play:focus:not(:focus-visible){outline:none}
.play .tri{font-size:11px;margin-right:8px}
.dlline{color:var(--muted);font-size:13.5px;margin-top:22px}
.opts{margin-top:10px}
.opts a,.lnk{background:none;border:1px solid rgba(219,58,0,.55);color:var(--accent2);
     border-radius:4px;padding:8px 15px;font-size:12.5px;cursor:pointer;font-family:inherit;
     display:inline-block;margin:3px 2px}
.opts a:hover,.lnk:hover{background:rgba(219,58,0,.12);text-decoration:none}
.dot{color:var(--faint);margin:0 4px}

.reader{max-width:1100px;margin:0 auto;padding:0 16px}
.reader figure{margin:0 0 14px}
.reader img{width:100%;height:auto;display:block;border-radius:4px}
.rhead{max-width:1100px;margin:20px auto 14px;padding:0 16px;display:flex;
       align-items:baseline;gap:12px;flex-wrap:wrap}
.rhead h2{font-family:Raleway,"Avenir Next",sans-serif;font-weight:800;font-size:24px}
.rhead span{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:11px;
            letter-spacing:.14em;color:var(--faint)}

.wrap{max-width:1280px;margin:44px auto 0;padding:0 16px}
.secthead{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.secthead h2{font-family:Raleway,"Avenir Next",sans-serif;font-weight:800;font-size:24px}
.secthead span{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:11px;
               letter-spacing:.14em;color:var(--faint)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.grid .c{position:relative;cursor:pointer;border-radius:4px;overflow:hidden;background:var(--panel);
         content-visibility:auto;contain-intrinsic-size:235px 176px}
.grid img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}
.grid .n{position:absolute;left:7px;bottom:6px;font-family:"SF Mono",ui-monospace,Menlo,monospace;
         font-size:10.5px;color:#fff;text-shadow:0 1px 5px #000;pointer-events:none}
body.sel .grid .c::after{content:"";position:absolute;top:8px;left:8px;width:22px;height:22px;
         border:2px solid #fff;border-radius:50%;background:rgba(14,27,44,.4)}
body.sel .grid .c.on::after{background:var(--accent);border-color:var(--accent);
         box-shadow:inset 0 0 0 3px var(--ground)}

footer{max-width:1280px;margin:56px auto 0;padding:20px 16px 46px;border-top:1px solid var(--line);
       display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;
       color:var(--faint);font-size:12.5px}

#selbar{position:fixed;left:0;right:0;bottom:0;z-index:25;display:none;gap:12px;align-items:center;
        background:rgba(14,27,44,.97);border-top:1px solid var(--line);padding:12px 18px;
        backdrop-filter:blur(8px)}
body.sel #selbar{display:flex}
#selbar .ct{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:13px;color:var(--muted);
            margin-right:auto}
#getlist{position:fixed;inset:0;z-index:30;background:rgba(10,16,26,.97);display:none;
         overflow-y:auto;padding:46px 18px}
#getlist.on{display:block}
#getlist .inner{max-width:640px;margin:0 auto}
#getlist h3{font-family:Raleway,"Avenir Next",sans-serif;font-weight:800;font-size:22px;
            margin-bottom:6px}
#getlist p{color:var(--muted);font-size:13px;margin-bottom:18px}
#getlist .row{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}
#getlist .row b{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:13px;font-weight:600;
                min-width:52px}
#getlist .row a{font-size:12.5px;border:1px solid rgba(219,58,0,.5);border-radius:4px;padding:5px 12px}
#getlist .x{position:fixed;top:12px;right:18px;background:none;border:0;color:var(--muted);
            font-size:30px;cursor:pointer}

#lb{position:fixed;inset:0;z-index:40;background:#000;display:none}
#lb.on{display:block}
#lb img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}
#lb .zone{position:absolute;top:0;bottom:0;width:28%;z-index:2;cursor:pointer;
          background:none;border:0;padding:0;appearance:none}
#lb .zl{left:0}#lb .zr{right:0}
#lb .x{position:absolute;top:10px;right:16px;z-index:3;background:none;border:0;color:#9CAABF;
       font-size:32px;cursor:pointer;line-height:1}
#lb .bar{position:absolute;bottom:0;left:0;right:0;z-index:3;display:flex;gap:12px;align-items:center;
         justify-content:center;padding:14px;background:linear-gradient(transparent,rgba(0,0,0,.75))}
#lb .bar .m{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:12px;color:#9CAABF}
#lb .bar .sz{font-size:12px;color:#C9D2DF}
#lb .bar .sz b{color:#fff;font-weight:600}
#getlist .row .sz{font-size:11.5px;color:var(--muted);flex-basis:100%;margin-top:2px}
#getlist .row{flex-wrap:wrap}
.printnote{max-width:720px;margin:26px auto 0;padding:14px 18px;border:1px solid var(--line);
     border-radius:5px;color:var(--muted);font-size:13px;line-height:1.6}
.printnote b{color:var(--ink);font-weight:600}
#lb .bar a{font-size:12px;border:1px solid rgba(240,74,14,.6);border-radius:4px;padding:6px 13px}

#stage{position:fixed;inset:0;z-index:50;background:#000;display:none}
#stage.on{display:block}
#stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
           opacity:0;transition:opacity 900ms ease}
#stage img.show{opacity:1}
#stage .zone{position:absolute;top:0;bottom:0;width:30%;z-index:2;cursor:pointer;
             background:none;border:0;padding:0;appearance:none}
#stage .zl{left:0}#stage .zr{right:0}
#stage .x{position:absolute;top:10px;right:16px;z-index:3;background:none;border:0;
          color:#9CAABF;font-size:32px;cursor:pointer}
@media (prefers-reduced-motion:reduce){#stage img,#lb img{transition:none}}
</style></head><body>

<a class=home href="https://www.abba-photo.com/">Abba Photo</a>
<div class=open>
  <h1>Camp Kingswood</h1>
  <p class=date>Bridgton, Maine &middot; Summer 2026</p>
  <div class=rule></div>
  <button class=play id=play type=button><span class=tri>&#9654;</span> Play</button>
  <p class=dlline>Every photograph in two sizes: full resolution for print, web for screens</p>
  <p class="dlline opts">
    <a href="__FOLDER__" target=_blank rel=noopener>All full res</a>
    <span class=dot>&middot;</span>
    <a id=zipall href="__ZIP__" style="display:none">All for web</a>
    <button class=lnk id=selmode type=button>Select frames</button>
    <span class=dot>&middot;</span>
    <a href="arrange.html">Arrange your own sets</a>
  </p>
  <p class=dlline style="font-size:12px">Full resolution comes from Google Drive. No sign-in needed.</p>
</div>

<div class=rhead><h2>Noah&#x27;s Picks</h2><span>EVERYTHING ELSE FOLLOWS BELOW</span></div>
<div class=reader id=picks></div>

<div class=wrap>
  <div class=secthead><h2>Everything</h2><span>__N__ &middot; IN THE ORDER THEY WERE MADE</span></div>
  <div class=grid id=grid></div>
</div>

<p class=printnote>Every frame carries the largest size it prints at on each material:
<b>metal</b> and <b>acrylic</b> hold the most detail and ask the most resolution,
<b>photo paper</b> a little less, <b>canvas</b> least because the weave and the
viewing distance forgive it. These are stock sizes, orderable as listed with no
custom cutting, and each one matches that frame's own proportions, so nothing is
cropped to fit. A few frames print true only as a custom cut; those say so.</p>

<footer>
  <span>Photographs by Noah Gallagher</span>
  <span>Abba Photo &middot; <a href="https://www.abba-photo.com" target=_blank rel=noopener>abba-photo.com</a></span>
</footer>

<div id=selbar><span class=ct id=selct>0 selected</span>
  <span class=act>
    <button class=lnk id=selget type=button disabled>Get these</button>
    <button class=lnk id=seldl type=button disabled>Download all</button>
    <button class=lnk id=selplay type=button disabled>Play these</button>
    <button class=lnk id=selwall type=button disabled>See it on a wall</button>
    <button class=lnk id=selbook type=button disabled>Book preview</button>
  </span>
  <button class=lnk id=seldone type=button>Done</button></div>

<div id=getlist><button class=x type=button aria-label=Close>&times;</button>
  <div class=inner><h3>Your frames</h3>
  <p>Web is sized for screens and social; full res is the print file, from Drive.
     Each frame lists the largest size it prints at on each material.</p>
  <div id=getrows></div></div></div>

<div id=lb><img id=lbi alt="Camp Kingswood, Bridgton, Maine, Summer 2026">
  <button class="zone zl" type=button aria-label=Previous></button>
  <button class="zone zr" type=button aria-label=Next></button>
  <button class=x type=button aria-label=Close>&times;</button>
  <div class=bar><span class=m id=lbm></span><span class=sz id=lbsz></span><a id=lbw download>Web</a><a id=lbf target=_blank rel=noopener>Full res</a></div>
</div>

<div id=stage><img id=sa alt=""><img id=sb alt="">
  <button class="zone zl" type=button aria-label=Previous></button>
  <button class="zone zr" type=button aria-label=Next></button>
  <button class=x type=button aria-label="End the show">&times;</button>
</div>

<script>
var ALL=__ALL__, PICKS=__PICKS__;
function $(i){return document.getElementById(i);}
// Largest size each frame prints at, off the master file, in sizes orderable
// without a custom cut. Absent when the frame's proportions have no true
// standard size; it says so rather than implying a crop.
function printText(r){
  if(r.pn) return r.pn;
  var m=["metal","paper","canvas"],out=[];
  for(var i=0;i<3;i++) if(r.p[i]) out.push("<b>"+r.p[i].replace("x","\\u00d7")+"\\u2033</b> "+m[i]);
  return out.length? "Prints to "+out.join(" \\u00b7 ") : "";
}
if("__ZIP__".length>8){$("zipall").style.display="";}

var reader=$("picks");
PICKS.forEach(function(r){
  var f=document.createElement("figure");
  f.innerHTML='<img loading=lazy src="img/present/'+r.f+'" alt="Camp Kingswood, Summer 2026">';
  f.onclick=function(){openLb(idxOf(r.n));};
  reader.appendChild(f);});

var grid=$("grid"), sel={}, selMode=false;
ALL.forEach(function(r,i){
  var c=document.createElement("div");c.className="c";c.dataset.n=r.n;
  c.innerHTML='<img loading=lazy src="img/thumb/'+r.f+'" alt="frame '+r.n+'">'+
              '<span class=n>'+r.n+'</span>';
  c.onclick=function(){
    if(selMode){ if(sel[r.n])delete sel[r.n];else sel[r.n]=1;
      c.className=sel[r.n]?"c on":"c";paintSel();return;}
    openLb(i);};
  grid.appendChild(c);});
function idxOf(n){for(var i=0;i<ALL.length;i++)if(ALL[i].n===n)return i;return 0;}

function paintSel(){var k=Object.keys(sel).length;
  $("selct").textContent=k+" selected";
  ["selget","seldl","selplay","selwall","selbook"].forEach(function(i){$(i).disabled=!k;});}
$("selmode").onclick=function(){selMode=true;document.body.className="sel";};
$("seldone").onclick=function(){selMode=false;document.body.className="";
  sel={};document.querySelectorAll(".grid .c.on").forEach(function(c){c.className="c";});paintSel();};
$("selget").onclick=function(){
  var rows=$("getrows");rows.innerHTML="";
  ALL.filter(function(r){return sel[r.n];}).forEach(function(r){
    var d=document.createElement("div");d.className="row";
    d.innerHTML='<b>#'+r.n+'</b>'+(r.w?'<a href="'+r.w+'" target=_blank rel=noopener>Web</a>':'')+
      (r.d?'<a href="'+r.d+'" target=_blank rel=noopener>Full res</a>':'')+
      '<span class=sz>'+printText(r)+'</span>';
    rows.appendChild(d);});
  $("getlist").className="on";};
document.querySelector("#getlist .x").onclick=function(){$("getlist").className="";};

var cur=0;
function openLb(i){cur=i;paintLb();$("lb").className="on";}
function paintLb(){if(cur<0)cur=ALL.length-1;if(cur>=ALL.length)cur=0;
  var r=ALL[cur];$("lbi").src="img/present/"+r.f;
  $("lbm").textContent="#"+r.n+"  \\u00b7  "+(cur+1)+" / "+ALL.length;
  $("lbsz").innerHTML=printText(r);
  if(r.w){$("lbw").style.display="";$("lbw").href=r.w;}else{$("lbw").style.display="none";}
  $("lbf").href=r.d||"__FOLDER__";}
document.querySelector("#lb .zl").onclick=function(){cur--;paintLb();};
document.querySelector("#lb .zr").onclick=function(){cur++;paintLb();};
document.querySelector("#lb .x").onclick=function(){$("lb").className="";};

var sIdx=0,sTimer=null,sFront=null;
function sRender(){if(sIdx<0)sIdx=PICKS.length-1;if(sIdx>=PICKS.length)sIdx=0;
  var inc=(sFront===$("sa"))?$("sb"):$("sa"),out=(sFront===$("sa"))?$("sa"):$("sb");
  inc.className="";void inc.offsetWidth;
  inc.onload=function(){inc.className="show";out.className="";sFront=inc;};
  inc.src="img/present/"+PICKS[sIdx].f;
  if(inc.complete)inc.onload();}
function sTick(){sTimer=setTimeout(function(){sIdx++;sRender();sTick();},5000);}
function sEnd(){clearTimeout(sTimer);$("stage").className="";}
$("play").onclick=function(){sIdx=0;sFront=null;
  $("sa").className="";$("sb").className="";$("stage").className="on";sRender();sTick();};
document.querySelector("#stage .x").onclick=sEnd;
document.querySelector("#stage .zl").onclick=function(){clearTimeout(sTimer);sIdx--;sRender();sTick();};
document.querySelector("#stage .zr").onclick=function(){clearTimeout(sTimer);sIdx++;sRender();sTick();};
document.addEventListener("keydown",function(e){
  if($("stage").className==="on"){
    if(e.key==="Escape")sEnd();
    else if(e.key==="ArrowRight"){clearTimeout(sTimer);sIdx++;sRender();sTick();}
    else if(e.key==="ArrowLeft"){clearTimeout(sTimer);sIdx--;sRender();sTick();}
    return;}
  if($("lb").className==="on"){
    if(e.key==="Escape")$("lb").className="";
    else if(e.key==="ArrowRight"){cur++;paintLb();}
    else if(e.key==="ArrowLeft"){cur--;paintLb();}}});
</script>
<script data-goatcounter="https://abbaphoto.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body></html>"""


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "ingest":
        ingest(sys.argv[2])
    elif cmd == "zip":
        make_zip()
    else:
        build()
