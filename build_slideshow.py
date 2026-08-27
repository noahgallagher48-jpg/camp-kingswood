#!/usr/bin/env python3
"""Builds the slideshow maker: play any arranged group as a timed show, with
live controls for timing and transitions and up to two layered music tracks.
Built 2026-08-19 at Noah's direction ("options for timing, transitions, and
ideally layered music"). Successor to the fixed Interlaken slideshow pages.

Shows are built FROM THE ARRANGEMENT: every group in _work/arrangement_kw.json
is a playable show (plus All frames). Rearrange the groups, rebuild, and the
shows follow. Settings persist on the device; music is picked at runtime from
local files (nothing uploads anywhere), so any track on the Mac or phone works
and the page stays light.

Builds:
    python3 build_slideshow.py local     -> _work/slideshow.html
        Full 2560px frames off img/present. THE version for real presenting.
    python3 build_slideshow.py tv        -> _work/slideshow_tv.html
        5120x2880 frames off ../kwood_5K, for an external 5K screen. Opens on
        Noah's Picks at 3 seconds, with everything else as "The rest" to run
        after (Noah, 2026-08-25: "start with the picks at 3s, then I can play
        the rest in background"). Its settings live under their own storage key
        so it opens at 3s rather than inheriting whatever the desk build was
        last set to. Runs from disk, not the published site: the tier is 585MB
        and GitHub Pages soft-caps a site at 1GB.
    python3 build_slideshow.py artifact  -> _work/slideshow_portable.html
        700px embedded, self-contained; the phone/anywhere preview.
"""
import base64, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRESENT = os.path.join(HERE, "img", "present")
# The 5K tier sits outside the repo on purpose: 585MB of it, and this repo is
# published. _work/ is one level down from HERE, so the page reaches it with
# ../../kwood_5K/ and plays straight off the disk over HDMI.
TV = os.path.abspath(os.path.join(HERE, "..", "kwood_5K"))
TV_HREF = "../../kwood_5K/"
SAVED = os.path.join(HERE, "_work", "arrangement_kw.json")
KEY = "kwood-slideshow-v1"
TV_KEY = "kwood-tv-v1"


def frame_no(f):
    m = re.search(r"_2-(\d+)\.jpg$", f)
    if m: return 200 + int(m.group(1))
    if f.endswith("_2.jpg"): return 201
    m = re.search(r"kwood820-(\d+)\.jpg$", f)
    if m: return 300 + int(m.group(1))
    if f.endswith("kwood820.jpg"): return 301
    m = re.search(r"-(\d+)\.jpg$", f)
    return int(m.group(1)) if m else 1


def build(mode):
    srcdir = TV if mode == "tv" else PRESENT
    files = sorted((f for f in os.listdir(srcdir) if f.endswith(".jpg")), key=frame_no)
    by_num = {frame_no(f): f for f in files}
    allf = [frame_no(f) for f in files]

    shows = []
    if os.path.exists(SAVED):
        a = json.load(open(SAVED))
        for g in a.get("groups", []):
            ns = [n for n in g["frames"] if n in by_num]
            if ns:
                shows.append({"name": g["name"], "frames": ns})
    shows.append({"name": "All frames", "frames": allf})

    if mode == "client":
        # The cut for Jodi: one show, his top choices, clean labels, no process
        # names. Shared only by Noah, from the artifact share menu.
        # Selected BY NAME: taking shows[0] silently became "New since your last
        # pass" when the group order changed (caught 2026-08-20).
        by_name = {g["name"]: g["frames"] for g in shows}
        top = by_name.get("Noah's Picks") or (shows[0]["frames"] if shows else allf)
        shows = [{"name": "Summer 2026", "frames": top}]

    if mode == "tv":
        # The picks lead and everything else follows as one show, so the room
        # can keep running after the deliberate cut ends.
        # NO FALLBACK TO THE WHOLE POOL. `or allf` used to mean that an empty
        # picks group produced a show of all 298 frames LABELLED "Noah's Picks",
        # which is a claim he never made; after the 8/27 swap reset the
        # arrangement, that is exactly what a rebuild would have played on the
        # television. Found by Codex on review, 2026-08-27. An unpicked set gets
        # one honest show instead of a mislabelled one.
        by_name = {g["name"]: g["frames"] for g in shows}
        top = [n for n in by_name.get("Noah's Picks", []) if n in set(allf)]
        if top:
            rest = [n for n in allf if n not in set(top)]
            shows = [{"name": "Noah's Picks", "frames": top}]
            if rest:
                shows.append({"name": "The rest", "frames": rest})
        else:
            shows = [{"name": "All photographs", "frames": allf}]
            print("  no picks on file, so the show is All photographs; "
                  "pick some and rebuild to lead with them")
        shows.append({"name": "All frames", "frames": allf})

    if mode in ("artifact", "client"):
        from PIL import Image
        src = {}
        for n, f in by_num.items():
            im = Image.open(os.path.join(PRESENT, f))
            im.thumbnail((700, 700), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=65, optimize=True)
            src[n] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
        out = os.path.join(HERE, "_work",
                           "slideshow_client.html" if mode == "client" else "slideshow_portable.html")
        grade = ("preview quality" if mode == "client"
                 else "700px preview build; present from the local build for full resolution")
    elif mode == "tv":
        src = {n: TV_HREF + f for n, f in by_num.items()}
        out = os.path.join(HERE, "_work", "slideshow_tv.html")
        grade = "5120x2880 off the disk, for the screen on HDMI"
    else:
        src = {n: "../img/present/" + f for n, f in by_num.items()}
        out = os.path.join(HERE, "_work", "slideshow.html")
        grade = "full resolution"

    page = PAGE
    if mode == "client":
        page = (page.replace("Camp Kingswood &middot; internal", "Camp Kingswood")
                    .replace("Make the slideshow", "Summer 2026, the slideshow")
                    .replace("__GRADE__ &middot; shows come from your arrangement; rearrange there, rebuild, they follow",
                             "photographs Noah Gallagher &middot; Abba Photo")
                    .replace("<title>Camp Kingswood &middot; slideshow</title>",
                             "<title>Camp Kingswood &middot; Summer 2026</title>"))
    if mode == "tv":
        page = (page.replace('var cfg={show:0,secs:5,trans:"fade"};',
                             'var cfg={show:0,secs:3,trans:"fade"};')
                    .replace('id=secs min=2 max=12 step=0.5 value=5',
                             'id=secs min=2 max=12 step=0.5 value=3'))

    html = (page.replace("__SRC__", json.dumps(src))
                .replace("__SHOWS__", json.dumps(shows))
                .replace("__KEY__", TV_KEY if mode == "tv" else KEY)
                .replace("__GRADE__", grade))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)
    print(f"wrote {out} ({os.path.getsize(out)//1048576} MB, "
          f"{len(shows)} shows, {len(allf)} frames, {grade})")


PAGE = """<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Camp Kingswood &middot; slideshow</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#14110d;color:#ede7dd;
     font-family:"Avenir Next",Avenir,-apple-system,Helvetica,Arial,sans-serif;min-height:100vh}
#setup{max-width:760px;margin:0 auto;padding:36px 20px 60px}
.eyebrow{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:#e2a73e;margin:0 0 10px}
h1{font-family:"Iowan Old Style",Palatino,Georgia,serif;font-weight:500;font-size:clamp(24px,4vw,32px)}
.note{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:12px;color:#7a7060;margin-top:6px}
fieldset{border:1px solid rgba(237,231,221,.14);border-radius:8px;padding:16px 18px;margin-top:22px}
legend{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.16em;
       text-transform:uppercase;color:#e2a73e;padding:0 8px}
.rowset{display:flex;flex-wrap:wrap;gap:8px}
.chip{border:1px solid rgba(237,231,221,.25);border-radius:20px;padding:8px 15px;font-size:13.5px;
      color:#c9bfa9;cursor:pointer;background:none;font-family:inherit}
.chip[aria-pressed=true]{background:#e2a73e;color:#14110d;border-color:#e2a73e;font-weight:600}
.slider-row{display:flex;align-items:center;gap:14px;margin-top:6px}
input[type=range]{flex:1;accent-color:#e2a73e}
.val{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:13px;color:#ede7dd;min-width:74px;text-align:right}
.mrow{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-top:10px}
.mrow label.file{border:1px solid rgba(226,167,62,.5);color:#e2a73e;border-radius:5px;
      padding:8px 14px;font-size:12.5px;cursor:pointer}
.mrow input[type=file]{display:none}
.mname{font-size:12.5px;color:#a69b8a;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mrow input[type=range]{width:130px}
.loopl{font-size:12px;color:#a69b8a;display:flex;align-items:center;gap:5px}
#golive{margin-top:26px;width:100%;background:#e2a73e;color:#14110d;border:0;border-radius:6px;
        padding:15px;font-size:15px;font-weight:600;letter-spacing:.06em;cursor:pointer;font-family:inherit}
#golive:hover{background:#ecb654}
.hint{font-size:12px;color:#7a7060;margin-top:12px;line-height:1.55}

#stage{position:fixed;inset:0;background:#000;display:none;z-index:20}
#stage.on{display:block}
#stage:fullscreen{background:#000}
#stage::backdrop{background:#000}
html.showing,html.showing body{background:#000}
#stage img{position:absolute;inset:0;width:100%;height:100%;
           object-fit:contain;opacity:0;transition:opacity var(--fade,900ms) ease}
#stage img.show{opacity:1}
#stage img.drift{animation:drift var(--driftms,14s) ease-out forwards}
@keyframes drift{from{transform:scale(1)}to{transform:scale(1.06)}}
#stage .zone{position:absolute;top:0;bottom:0;width:30%;z-index:3;cursor:pointer;background:none;border:0;padding:0;appearance:none}
.zl{left:0}.zr{right:0}
#hud{position:absolute;left:0;right:0;bottom:0;z-index:4;display:flex;gap:14px;align-items:center;
     padding:14px 18px;background:linear-gradient(transparent,rgba(10,8,6,.85));
     opacity:0;transition:opacity .3s}
#stage:hover #hud,#hud.pin{opacity:1}
#hud .m{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:12px;color:#a69b8a;margin-right:auto}
#hud button{background:none;border:1px solid rgba(237,231,221,.3);color:#c9bfa9;border-radius:4px;
            padding:6px 12px;font-size:12px;cursor:pointer;font-family:inherit}
#hud button:hover{border-color:#e2a73e;color:#e2a73e}
@media (prefers-reduced-motion:reduce){#stage img{transition:none}#stage img.drift{animation:none}}
</style>

<div id=setup>
 <p class=eyebrow>Camp Kingswood &middot; internal</p>
 <h1>Make the slideshow</h1>
 <p class=note>__GRADE__ &middot; shows come from your arrangement; rearrange there, rebuild, they follow</p>

 <fieldset><legend>The show</legend><div class=rowset id=shows></div></fieldset>

 <fieldset><legend>Timing</legend>
  <div class=slider-row><input type=range id=secs min=2 max=12 step=0.5 value=5>
   <span class=val id=secsval></span></div>
  <div class=slider-row style="margin-top:2px"><span style="font-size:12px;color:#7a7060" id=runtime></span></div>
 </fieldset>

 <fieldset><legend>Transition</legend>
  <div class=rowset id=trans>
   <button class=chip type=button data-t=cut>Cut</button>
   <button class=chip type=button data-t=fade aria-pressed=true>Crossfade</button>
   <button class=chip type=button data-t=drift>Crossfade + drift</button>
  </div>
 </fieldset>

 <fieldset><legend>Music &middot; two layers, files stay on this device</legend>
  <div class=mrow>
   <label class=file>Track<input type=file id=m1 accept="audio/*"></label>
   <span class=mname id=m1n>none</span>
   <input type=range id=m1v min=0 max=1 step=0.05 value=0.9>
   <label class=loopl><input type=checkbox id=m1l checked>loop</label>
  </div>
  <div class=mrow>
   <label class=file>Layer 2<input type=file id=m2 accept="audio/*"></label>
   <span class=mname id=m2n>none</span>
   <input type=range id=m2v min=0 max=1 step=0.05 value=0.35>
   <label class=loopl><input type=checkbox id=m2l checked>loop</label>
  </div>
  <p class=hint>Pick any audio file on this Mac or phone: the track carries the show, the second
  layer sits under it (ambience, room tone, a second instrument). Volumes are live during the
  show. Music fades out over the last three seconds. Files never upload; re-pick after a reload.</p>
 </fieldset>

 <button id=golive type=button>Begin</button>
 <p class=hint>During the show: space pauses, arrows step, Esc comes back here, F goes fullscreen.
 Settings save on this device.</p>
</div>

<div id=stage>
 <img id=ia alt=""><img id=ib alt="">
 <button class="zone zl" type=button aria-label="Previous"></button>
 <button class="zone zr" type=button aria-label="Next"></button>
 <div id=hud>
  <span class=m id=meta></span>
  <button id=pp type=button>Pause</button>
  <button id=fs type=button>Fullscreen</button>
  <button id=bk type=button>Back</button>
 </div>
</div>

<script>
(function(){
var SRC=__SRC__, SHOWS=__SHOWS__, KEY="__KEY__";
var cfg={show:0,secs:5,trans:"fade"};
try{var s=JSON.parse(localStorage.getItem(KEY)||"null");if(s)cfg=Object.assign(cfg,s);}catch(e){}
if(cfg.show>=SHOWS.length)cfg.show=0;
function save(){try{localStorage.setItem(KEY,JSON.stringify(cfg));}catch(e){}}

var showsEl=document.getElementById("shows");
SHOWS.forEach(function(sh,i){
  var b=document.createElement("button");b.type="button";b.className="chip";
  b.textContent=sh.name+" ("+sh.frames.length+")";
  b.setAttribute("aria-pressed",i===cfg.show);
  b.onclick=function(){cfg.show=i;save();paint();};
  showsEl.appendChild(b);});
var secs=document.getElementById("secs"),secsval=document.getElementById("secsval"),
    runtime=document.getElementById("runtime");
secs.value=cfg.secs;
secs.oninput=function(){cfg.secs=+secs.value;save();paint();};
document.querySelectorAll("#trans .chip").forEach(function(b){
  b.onclick=function(){cfg.trans=b.dataset.t;save();paint();};});
function paint(){
  showsEl.querySelectorAll(".chip").forEach(function(b,i){b.setAttribute("aria-pressed",i===cfg.show);});
  document.querySelectorAll("#trans .chip").forEach(function(b){
    b.setAttribute("aria-pressed",b.dataset.t===cfg.trans);});
  secsval.textContent=(+cfg.secs).toFixed(1)+" s";
  var n=SHOWS[cfg.show].frames.length, t=Math.round(n*cfg.secs);
  runtime.textContent=n+" frames \\u2192 "+Math.floor(t/60)+"m "+(t%60)+"s";
}
paint();

var audio=[{el:null},{el:null}];
function wireAudio(i,fileInput,nameEl,volEl,loopEl){
  fileInput.addEventListener("change",function(){
    var f=fileInput.files[0];if(!f)return;
    if(audio[i].el){audio[i].el.pause();URL.revokeObjectURL(audio[i].el.src);}
    var a=new Audio(URL.createObjectURL(f));
    a.loop=loopEl.checked;a.volume=+volEl.value;
    audio[i].el=a;nameEl.textContent=f.name;});
  volEl.addEventListener("input",function(){if(audio[i].el)audio[i].el.volume=+volEl.value;});
  loopEl.addEventListener("change",function(){if(audio[i].el)audio[i].el.loop=loopEl.checked;});
}
wireAudio(0,document.getElementById("m1"),document.getElementById("m1n"),
          document.getElementById("m1v"),document.getElementById("m1l"));
wireAudio(1,document.getElementById("m2"),document.getElementById("m2n"),
          document.getElementById("m2v"),document.getElementById("m2l"));

var stage=document.getElementById("stage"),ia=document.getElementById("ia"),ib=document.getElementById("ib"),
    meta=document.getElementById("meta"),pp=document.getElementById("pp");
var order=[],cur=0,timer=null,front=null,running=false;
function fadems(){return cfg.trans==="cut"?0:900;}
function render(){
  if(cur<0)cur=order.length-1;if(cur>=order.length)cur=0;
  var n=order[cur],inc=(front===ia)?ib:ia,out=(front===ia)?ia:ib;
  document.documentElement.style.setProperty("--fade",fadems()+"ms");
  document.documentElement.style.setProperty("--driftms",Math.max(cfg.secs*2.4,8)+"s");
  inc.className="";void inc.offsetWidth;
  inc.onload=function(){
    inc.className="show"+(cfg.trans==="drift"?" drift":"");
    out.className=out.className.replace("show","").trim();
    front=inc;};
  inc.src=SRC[n];
  if(inc.complete)inc.onload();
  meta.textContent="#"+n+"  \\u00b7  "+(cur+1)+" / "+order.length+"  \\u00b7  "+SHOWS[cfg.show].name;}
function tick(){timer=setTimeout(function(){cur++;render();if(running)tick();},cfg.secs*1000);}
function stopTimer(){clearTimeout(timer);timer=null;}
function begin(){
  order=SHOWS[cfg.show].frames.slice();cur=0;front=null;
  ia.className="";ib.className="";ia.removeAttribute("src");ib.removeAttribute("src");
  stage.className="on";running=true;pp.textContent="Pause";
  document.documentElement.classList.add("showing");
  audio.forEach(function(a){if(a.el){a.el.currentTime=0;a.el.play().catch(function(){});}});
  render();tick();}
function fadeAudioOut(ms){
  audio.forEach(function(a){if(!a.el)return;var el=a.el,v0=el.volume,steps=20,i=0;
    var iv=setInterval(function(){i++;el.volume=Math.max(0,v0*(1-i/steps));
      if(i>=steps){clearInterval(iv);el.pause();el.volume=v0;}},ms/20);});}
function end(){running=false;stopTimer();stage.className="";
  document.documentElement.classList.remove("showing");fadeAudioOut(3000);}
document.getElementById("golive").onclick=begin;
document.getElementById("bk").onclick=end;
pp.onclick=function(){
  if(running){running=false;stopTimer();pp.textContent="Play";
    audio.forEach(function(a){if(a.el)a.el.pause();});}
  else{running=true;pp.textContent="Pause";
    audio.forEach(function(a){if(a.el)a.el.play().catch(function(){});});tick();}};
document.getElementById("fs").onclick=function(){
  if(document.fullscreenElement)document.exitFullscreen();
  else stage.requestFullscreen&&stage.requestFullscreen();};
stage.querySelector(".zl").onclick=function(){stopTimer();cur--;render();if(running)tick();};
stage.querySelector(".zr").onclick=function(){stopTimer();cur++;render();if(running)tick();};
document.addEventListener("keydown",function(e){
  if(stage.className!=="on")return;
  if(e.key==="Escape")end();
  else if(e.key===" "){e.preventDefault();pp.onclick();}
  else if(e.key==="ArrowRight"){stopTimer();cur++;render();if(running)tick();}
  else if(e.key==="ArrowLeft"){stopTimer();cur--;render();if(running)tick();}
  else if(e.key==="f"||e.key==="F")document.getElementById("fs").onclick();});
})();
</script>
"""


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "local")
