#!/usr/bin/env python3
"""Builds the Kingswood selection page: every frame, pick or unpick, then play
the picks as a preview slideshow. Built 2026-08-19 at Noah's direction ("set up
all images for selection and inclusion in a preview slideshow").

Two builds, same page:

    python3 build_select.py local      -> _work/select.html
        References img/present directly. Full 2560px in the slideshow.
        Open it on this Mac. Best quality, no size ceiling.

    python3 build_select.py artifact   -> _work/select_portable.html
        Embeds 760px copies as data URIs (~11MB). Self-contained, so it works
        as a published artifact on the phone or anywhere else.

Picks live in the browser's localStorage under KEY, so they survive reloads on
that device. "Copy the picks" puts a JSON list on the clipboard; paste it into
a session and it becomes forty_two.json.

Starting selection: forty_two.json if present, else empty. INTERNAL ONLY, faces
throughout; never a client surface, never pushed to the public repo.
"""
import base64, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRESENT = os.path.join(HERE, "img", "present")
KEY = "kwood-select-v1"


def frame_no(f):
    """The bare kwood819.jpg is frame 1; numbers run 2 to 122 (83 absent). The _2
    re-edit set (2026-08-19) is 201-206: kwood819_2.jpg is 201, kwood819_2-N is 200+N."""
    m = re.search(r"_2-(\d+)\.jpg$", f)
    if m: return 200 + int(m.group(1))
    if f.endswith("_2.jpg"): return 201
    m = re.search(r"-(\d+)\.jpg$", f)
    return int(m.group(1)) if m else 1


def build(mode):
    files = sorted((f for f in os.listdir(PRESENT) if f.endswith(".jpg")), key=frame_no)
    start = []
    p42 = os.path.join(HERE, "forty_two.json")
    if os.path.exists(p42):
        start = [frame_no(f) for f in json.load(open(p42))]

    srcs, cards = {}, []
    if mode == "artifact":
        from PIL import Image
        for f in files:
            im = Image.open(os.path.join(PRESENT, f))
            im.thumbnail((560, 560), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=63, optimize=True)
            srcs[f] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    else:
        for f in files:
            srcs[f] = "../img/present/" + f

    for f in files:
        n = frame_no(f)
        cards.append(
            f'<figure class=card data-n="{n}">'
            f'<img loading=lazy src="{srcs[f]}" alt="frame {n}">'
            f'<button class=pick type=button aria-label="Pick frame {n}" aria-pressed=false></button>'
            f'<figcaption>#{n}</figcaption></figure>')

    page = PAGE.replace("__CARDS__", "\n".join(cards)) \
               .replace("__START__", json.dumps(sorted(start))) \
               .replace("__KEY__", KEY) \
               .replace("__N__", str(len(files)))
    out = os.path.join(HERE, "_work",
                       "select_portable.html" if mode == "artifact" else "select.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(page)
    print(f"wrote {out} ({os.path.getsize(out)//1048576} MB, {len(files)} frames, "
          f"{len(start)} pre-picked)")


PAGE = """<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Kingswood &middot; select</title>
<style>
  :root{--ground:#161310;--panel:#1E1A16;--line:rgba(237,231,221,.12);
        --ink:#EDE7DD;--dim:#A29786;--faint:#7A7060;--gold:#E2A73E}
  *{box-sizing:border-box}
  body{margin:0;background:var(--ground);color:var(--ink);
       font-family:"Avenir Next",Avenir,-apple-system,"Segoe UI",Helvetica,sans-serif;
       font-size:15px;padding:0 16px 90px}
  .wrap{max-width:1280px;margin:0 auto}
  header{padding:24px 0 10px}
  .eyebrow{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);margin:0 0 8px}
  h1{font-family:"Iowan Old Style",Palatino,Georgia,serif;font-weight:500;
     font-size:clamp(22px,3.4vw,30px);margin:0}
  .note{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:12px;color:var(--dim);margin:6px 0 0}
  .how{font-size:13.5px;color:var(--dim);margin:10px 0 0;max-width:64ch}

  .wall{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:10px;margin-top:20px}
  .card{position:relative;margin:0;content-visibility:auto;contain-intrinsic-size:230px 172px}
  .card img{width:100%;height:auto;display:block;border-radius:4px;
            border:2px solid transparent;transition:border-color .12s}
  .card.on img{border-color:var(--gold)}
  .card.on::after{content:"";position:absolute;top:9px;left:9px;width:20px;height:20px;
                  border-radius:50%;background:var(--gold);
                  box-shadow:inset 0 0 0 2px var(--ground)}
  .pick{position:absolute;inset:0;width:100%;height:100%;background:none;border:0;cursor:pointer}
  .pick:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
  figcaption{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:10.5px;
             color:var(--faint);margin-top:3px}
  .card.on figcaption{color:var(--gold)}

  .bar{position:fixed;left:0;right:0;bottom:0;z-index:30;background:rgba(22,19,16,.97);
       border-top:1px solid var(--line);padding:11px 16px;
       display:flex;gap:10px;align-items:center;flex-wrap:wrap;backdrop-filter:blur(8px)}
  .cnt{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:13px;color:var(--dim);margin-right:auto}
  .cnt b{color:var(--gold);font-size:15px}
  .bar button{background:none;border:1px solid rgba(226,167,62,.55);color:var(--gold);
              border-radius:5px;padding:9px 16px;font-size:13px;cursor:pointer;
              font-family:inherit;letter-spacing:.04em}
  .bar button:hover{background:rgba(226,167,62,.12)}
  .bar button.fill{background:var(--gold);color:var(--ground);font-weight:600;border-color:var(--gold)}
  .bar button.fill:hover{background:#ECB654}

  #show{position:fixed;inset:0;z-index:40;background:#0d0b09;display:none}
  #show.on{display:block}
  #show img{position:absolute;inset:0;margin:auto;max-width:100vw;max-height:100vh;object-fit:contain}
  #show .zone{position:absolute;top:0;bottom:0;width:33%;cursor:pointer;z-index:2}
  #show .zl{left:0}#show .zr{right:0}
  #show .x{position:absolute;top:12px;right:16px;z-index:3;background:none;border:0;
           color:var(--dim);font-size:32px;cursor:pointer;line-height:1}
  #show .meta{position:absolute;bottom:14px;left:0;right:0;text-align:center;z-index:3;
              font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:12px;color:var(--dim)}
  #show .drop{position:absolute;bottom:44px;left:0;right:0;text-align:center;z-index:3}
  #show .drop button{background:none;border:1px solid rgba(237,231,221,.25);color:var(--dim);
                     border-radius:20px;padding:6px 16px;font-size:12px;cursor:pointer;font-family:inherit}
  #show .drop button:hover{border-color:var(--gold);color:var(--gold)}
  #toast{position:fixed;left:50%;bottom:86px;transform:translateX(-50%);z-index:50;
         background:var(--panel);border:1px solid var(--line);border-radius:20px;
         padding:9px 18px;font-size:13px;opacity:0;transition:opacity .2s;pointer-events:none}
  #toast.on{opacity:1}
  @media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
<div class=wrap>
<header>
  <p class=eyebrow>Camp Kingswood &middot; internal selection</p>
  <h1>Pick the set, then watch it</h1>
  <p class=note>__N__ frames &middot; Aug 5 to 9 &middot; INTERNAL: faces throughout, never a client surface</p>
  <p class=how>Tap a frame to pick it or drop it. Picks save on this device. Play runs the picks
     in frame order, arrow keys or tap the sides to move, Esc to come back. Drop a frame from
     inside the slideshow and it leaves the selection.</p>
</header>
<div class=wall>
__CARDS__
</div>
</div>

<div class=bar>
  <span class=cnt><b id=n>0</b> picked <span id=sub></span></span>
  <button type=button id=all>Pick all</button>
  <button type=button id=none>Clear</button>
  <button type=button id=copy>Copy the picks</button>
  <button type=button id=play class=fill>Play</button>
</div>

<div id=show>
  <img id=si alt="">
  <button class="zone zl" type=button aria-label="Previous"></button>
  <button class="zone zr" type=button aria-label="Next"></button>
  <button class=x type=button aria-label="Close">&times;</button>
  <div class=drop><button type=button id=drop>Drop this frame</button></div>
  <div class=meta id=sm></div>
</div>
<div id=toast></div>

<script>
(function(){
  var KEY="__KEY__", START=__START__;
  var cards=[].slice.call(document.querySelectorAll(".card"));
  var byNum={}; cards.forEach(function(c){ byNum[+c.dataset.n]=c; });
  var picks;
  try{ picks=JSON.parse(localStorage.getItem(KEY)||"null"); }catch(e){ picks=null; }
  if(!picks || !picks.length) picks=START.slice();
  var set={}; picks.forEach(function(n){ set[n]=1; });

  var nEl=document.getElementById("n"), subEl=document.getElementById("sub"),
      toast=document.getElementById("toast"), tTimer=null;

  function say(m){ toast.textContent=m; toast.className="on";
    clearTimeout(tTimer); tTimer=setTimeout(function(){ toast.className=""; },1800); }
  function list(){ return Object.keys(set).map(Number).sort(function(a,b){return a-b;}); }
  function save(){
    try{ localStorage.setItem(KEY, JSON.stringify(list())); }catch(e){}
    var k=list().length;
    nEl.textContent=k;
    subEl.textContent = k===42 ? "\\u00b7 the forty-two" : (k>42 ? "\\u00b7 "+(k-42)+" over" : "\\u00b7 "+(42-k)+" to go");
  }
  function paint(n){ byNum[n].className = set[n] ? "card on" : "card";
    byNum[n].querySelector(".pick").setAttribute("aria-pressed", set[n]?"true":"false"); }
  function toggle(n){ if(set[n]) delete set[n]; else set[n]=1; paint(n); save(); }

  cards.forEach(function(c){
    var n=+c.dataset.n;
    c.querySelector(".pick").addEventListener("click",function(){ toggle(n); });
    paint(n);
  });
  save();

  document.getElementById("all").onclick=function(){
    cards.forEach(function(c){ set[+c.dataset.n]=1; paint(+c.dataset.n); }); save(); say("All picked."); };
  document.getElementById("none").onclick=function(){
    set={}; cards.forEach(function(c){ paint(+c.dataset.n); }); save(); say("Cleared."); };
  document.getElementById("copy").onclick=function(){
    var txt=JSON.stringify(list());
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(function(){ say("Picks copied."); },
                                             function(){ window.prompt("Copy the picks:",txt); });
    } else window.prompt("Copy the picks:",txt);
  };

  var show=document.getElementById("show"), si=document.getElementById("si"),
      sm=document.getElementById("sm"), order=[], cur=0;
  function render(){
    if(!order.length){ close(); return; }
    if(cur<0) cur=order.length-1; if(cur>=order.length) cur=0;
    var n=order[cur];
    si.src=byNum[n].querySelector("img").src;
    si.alt="frame "+n;
    sm.textContent="#"+n+"  \\u00b7  "+(cur+1)+" / "+order.length;
  }
  function open(){
    order=list();
    if(!order.length){ say("Nothing picked yet."); return; }
    cur=0; show.className="on"; render();
  }
  function close(){ show.className=""; si.src=""; }
  document.getElementById("play").onclick=open;
  show.querySelector(".x").onclick=close;
  show.querySelector(".zl").onclick=function(){ cur--; render(); };
  show.querySelector(".zr").onclick=function(){ cur++; render(); };
  document.getElementById("drop").onclick=function(){
    var n=order[cur]; delete set[n]; paint(n); save();
    order.splice(cur,1); say("#"+n+" dropped."); render();
  };
  document.addEventListener("keydown",function(e){
    if(show.className!=="on") return;
    if(e.key==="Escape") close();
    else if(e.key==="ArrowRight"||e.key===" "){ e.preventDefault(); cur++; render(); }
    else if(e.key==="ArrowLeft"){ cur--; render(); }
  });
})();
</script>
"""


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "local")
