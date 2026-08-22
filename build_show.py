#!/usr/bin/env python3
"""A slideshow at its own URL: one link, press play, the frames in Noah's order.

    python3 build_show.py     ->  show.html

For texting a director a link. No sign-in, no downloads, no grid to browse,
no share menu: she taps the link, taps play, and watches the set in the order
it was arranged. That order is the argument, which is why this show does not
shuffle and does not let her jump around.

Frames come from a group in _work/arrangement_kw.json. By default that is the
delivery picks, IN HIS SEQUENCE, and the show neither shuffles nor lets a viewer
jump around, because there the order is the argument.

--shuffle exists for the opposite case. A book preview shows the CANDIDATES, and
its real sequence is the thing the client has not approved yet, so playing them
in book order would quietly present a layout decision as settled. Mixed, the
frames read as a body of work and the sequence stays an open question. The
shuffle is seeded off the group name, so the same lane always plays in the same
order and a link that was already sent does not reshuffle under the viewer.

    python3 build_show.py
    python3 build_show.py --group "The book" --shuffle --out book-preview.html

Playback renders the present tier (2560px), per the resolution standard;
thumbs are never presented full screen.
"""
import argparse, hashlib, json, os, random, re

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
ARR = os.path.join(HERE, "_work", "arrangement_kw.json")
OUT = os.path.join(HERE, "show.html")
PICKS_GROUP = "Proposed forty-two"
HOLD = 5  # seconds a frame is held, matching tick() below


def frame_no(f):
    m = re.search(r"_2-(\d+)\.jpg$", f)
    if m: return 200 + int(m.group(1))
    if f.endswith("_2.jpg"): return 201
    m = re.search(r"kwood820-(\d+)\.jpg$", f)
    if m: return 300 + int(m.group(1))
    if f.endswith("kwood820.jpg"): return 301
    m = re.search(r"-(\d+)\.jpg$", f)
    return int(m.group(1)) if m else 1


def build(group=PICKS_GROUP, shuffle=False, out=OUT, sub="Summer 2026",
          end="That is the summer."):
    a = json.load(open(ARR))
    by_num = {frame_no(f): f for f in os.listdir(os.path.join(IMG, "present"))
              if f.endswith(".jpg")}
    aside = set(a.get("aside", []))
    by_name = {g["name"]: g["frames"] for g in a["groups"]}
    if group not in by_name:
        raise SystemExit(f"No '{group}' lane in {ARR}")
    order = by_name[group]
    dropped = [n for n in order if n in aside]
    kept = [n for n in order if n in by_num and n not in aside]
    if shuffle:
        seed = int(hashlib.sha1(group.encode()).hexdigest()[:8], 16)
        random.Random(seed).shuffle(kept)
    files = [by_num[n] for n in kept]
    mins = len(files) * HOLD / 60
    hint = (f"{len(files)} photographs, about {mins:.0f} minutes. "
            f"Best full screen with the sound off.")
    html = (PAGE.replace("__FRAMES__", json.dumps(files))
                .replace("__HINT__", hint)
                .replace("__SUB__", sub)
                .replace("__END__", end)
                .replace("__N__", str(len(files))))
    open(out, "w").write(html)
    print(f"wrote {out}  ({len(files)} frames from '{group}', "
          f"{'mixed' if shuffle else 'in his order'})")
    if dropped:
        print(f"  HELD BACK, they sit in your aside lane too: {dropped}")
    return kept, dropped


PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name=robots content=noindex>
<title>Camp Kingswood &middot; Summer 2026</title><style>
@font-face{font-family:Raleway;src:url(fonts/raleway-400.woff2) format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:Raleway;src:url(fonts/raleway-800.woff2) format('woff2');font-weight:800;font-display:swap}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%}
body{background:#062A40;color:#F3F1EC;font-family:Raleway,-apple-system,Helvetica,Arial,sans-serif;
     display:flex;align-items:center;justify-content:center;text-align:center;
     padding:24px;overflow:hidden}
.open{max-width:560px}
h1{font-weight:800;font-size:clamp(26px,7vw,40px);letter-spacing:-.01em}
p{color:#9CAABF;font-size:15px;margin-top:8px}
button.play{margin-top:30px;background:#DB3A00;color:#fff;border:0;border-radius:6px;
     padding:17px 40px;font-family:inherit;font-size:16px;font-weight:700;
     letter-spacing:.09em;text-transform:uppercase;cursor:pointer}
button.play:hover{background:#F04A0E}
.hint{font-size:12.5px;color:#6E7E94;margin-top:20px}
#stage{position:fixed;inset:0;background:#000;display:none;z-index:10}
#stage.on{display:block}
#stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
           opacity:0;transition:opacity 1000ms ease}
#stage img.show{opacity:1}
#stage .zone{position:absolute;top:0;bottom:0;width:32%;z-index:2;cursor:pointer;
             background:none;border:0;padding:0;appearance:none}
#stage .zl{left:0}#stage .zr{right:0}
#stage .x{position:absolute;top:calc(10px + env(safe-area-inset-top));right:16px;z-index:3;
          background:none;border:0;color:#8b96a3;font-size:34px;line-height:1;cursor:pointer}
#stage .n{position:absolute;left:16px;top:calc(14px + env(safe-area-inset-top));z-index:3;
          color:#8b96a3;font-size:12px;font-variant-numeric:tabular-nums}
#stage.done .end{display:flex}
.end{display:none;position:absolute;inset:0;z-index:4;background:rgba(6,42,64,.94);
     flex-direction:column;align-items:center;justify-content:center;gap:18px}
.end button{background:none;border:1px solid rgba(219,58,0,.6);color:#F3F1EC;border-radius:5px;
     padding:12px 26px;font-family:inherit;font-size:14px;cursor:pointer}
@media (prefers-reduced-motion:reduce){#stage img{transition:none}}
</style></head><body>

<div class=open id=open>
  <h1>Camp Kingswood</h1>
  <p>__SUB__</p>
  <button class=play id=go type=button>&#9654;&nbsp; Play</button>
  <p class=hint>__HINT__</p>
</div>

<div id=stage>
  <img id=a alt="Camp Kingswood, Summer 2026"><img id=b alt="Camp Kingswood, Summer 2026">
  <span class=n id=num></span>
  <button class="zone zl" type=button aria-label=Previous></button>
  <button class="zone zr" type=button aria-label=Next></button>
  <button class=x type=button aria-label=Close>&times;</button>
  <div class=end><p style="color:#F3F1EC;font-size:17px">__END__</p>
    <button id=again type=button>Play it again</button></div>
</div>

<script>
var F=__FRAMES__, i=0, t=null, front=null;
function $(x){return document.getElementById(x);}
function render(){
  var inc=(front===$('a'))?$('b'):$('a'), out=(front===$('a'))?$('a'):$('b');
  inc.className=''; void inc.offsetWidth;
  inc.onload=function(){inc.className='show'; out.className=''; front=inc;};
  inc.src='img/present/'+F[i];
  if(inc.complete)inc.onload();
  $('num').textContent=(i+1)+' / '+F.length;
  // preload the next frame so the crossfade never stalls
  if(i+1<F.length){var p=new Image(); p.src='img/present/'+F[i+1];}
}
function tick(){t=setTimeout(next,5000);}
function next(){
  if(i>=F.length-1){clearTimeout(t);$('stage').className='on done';return;}
  i++;render();tick();
}
function prev(){clearTimeout(t); if(i>0)i--; render(); tick();}
function start(){
  i=0;front=null;$('a').className='';$('b').className='';
  $('stage').className='on';render();tick();
  if($('stage').requestFullscreen)$('stage').requestFullscreen().catch(function(){});
}
$('go').onclick=start;
$('again').onclick=function(){$('stage').className='on';start();};
document.querySelector('#stage .x').onclick=function(){
  clearTimeout(t);$('stage').className='';
  if(document.fullscreenElement&&document.exitFullscreen)document.exitFullscreen().catch(function(){});
};
document.querySelector('#stage .zr').onclick=function(){clearTimeout(t);next();};
document.querySelector('#stage .zl').onclick=prev;
document.addEventListener('keydown',function(e){
  if($('stage').className.indexOf('on')<0)return;
  if(e.key==='Escape')document.querySelector('#stage .x').click();
  else if(e.key==='ArrowRight'){clearTimeout(t);next();}
  else if(e.key==='ArrowLeft')prev();
});
</script>
<script data-goatcounter="https://abbaphoto.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default=PICKS_GROUP)
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--sub", default="Summer 2026")
    ap.add_argument("--end", default="That is the summer.")
    g = ap.parse_args()
    build(g.group, g.shuffle, g.out, g.sub, g.end)
