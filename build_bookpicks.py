#!/usr/bin/env python3
"""Builds book-picks.html: Noah's Kingswood book picks, on their own link.

Noah, 2026-08-27: "give me my kingswood book picks in an independent link with
a gallery."

WHERE THE PICKS ACTUALLY LIVE. Nowhere on disk. The book tab stores selections
in the BROWSER, under kwood-book-827b-<who>, and that key was deliberately
bumped on 8/27 so every device opened a clean sheet after the set was replaced.
The record's lanes are empty, and forty_two.json still names kwood819 files
from the superseded set, so it cannot be trusted as a pick list.

So this page READS THE SAME KEYS. It is served from the same origin as
delivery.html, which is what lets it see them. That also means it shows picks
only on the device they were made on; the page says so rather than rendering an
empty gallery and letting it read as "you picked nothing".

Copy the list moves a set between devices, and Open in the book tab hands it
back so the strip and the spread view work on it.

    python3 build_bookpicks.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "delivery.html")
OUT = os.path.join(HERE, "book-picks.html")

s = open(SRC).read()
i = s.index("var ALL=") + len("var ALL=")
ALL, _ = json.JSONDecoder().raw_decode(s[i:])
data = {r["n"]: {"f": r["f"], "d": r.get("d", ""), "p": r.get("p") or []} for r in ALL}

PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content="noindex,nofollow">
<title>Camp Kingswood &middot; the book picks</title>
<link rel=icon href='data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="%23062A40"/><circle cx="16" cy="16" r="7" fill="none" stroke="%23DB3A00" stroke-width="2.4"/></svg>'>
<style>
:root{--ground:#062A40;--panel:#0C3A55;--ink:#F3F1EC;--muted:#9CAABF;--accent:#DB3A00}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
 font:15px/1.5 "Avenir Next",-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 clamp(16px,3vw,44px)}
header{padding:38px 0 4px;text-align:center}
h1{font:500 clamp(24px,3.4vw,32px)/1.1 "Iowan Old Style",Palatino,Georgia,serif;margin:0 0 6px}
.sub{color:var(--muted);font-size:13.5px;margin:0}
.who{display:flex;gap:8px;justify-content:center;margin:26px 0 10px;flex-wrap:wrap}
.wb{background:transparent;border:1px solid rgba(243,241,236,.24);color:inherit;border-radius:999px;
 padding:7px 16px;font:600 13px inherit;cursor:pointer}
.wb[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:var(--ink)}
.acts{display:flex;gap:8px;justify-content:center;margin:0 0 30px;flex-wrap:wrap}
.ab{background:transparent;border:1px solid rgba(243,241,236,.24);color:inherit;border-radius:6px;
 padding:8px 15px;font:600 13px inherit;cursor:pointer;text-decoration:none}
.ab:hover{border-color:var(--accent)}
.note{color:var(--muted);font-size:13px;text-align:center;max-width:62ch;margin:0 auto 26px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;padding-bottom:60px}
figure{margin:0;position:relative;border-radius:8px;overflow:hidden;background:rgba(243,241,236,.06)}
figure img{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;cursor:zoom-in}
.n{position:absolute;top:8px;left:9px;font:600 11px inherit;background:rgba(6,42,64,.76);
 border-radius:11px;padding:2px 9px}
.seq{position:absolute;top:8px;right:9px;font:600 11px inherit;background:var(--accent);
 border-radius:11px;padding:2px 9px}
figcaption{padding:9px 11px 12px;font-size:12px;color:var(--muted);display:flex;
 justify-content:space-between;gap:10px}
figcaption a{color:var(--accent);text-decoration:none}
.empty{text-align:center;color:var(--muted);padding:40px 0 80px;line-height:1.7}
.empty b{color:var(--ink);display:block;margin-bottom:8px;font-size:16px}
#lb{position:fixed;inset:0;background:rgba(4,20,30,.96);display:none;z-index:60;
 align-items:center;justify-content:center;padding:24px}
#lb.on{display:flex}
#lb img{max-width:100%;max-height:100%;object-fit:contain}
#lbx{position:absolute;top:14px;right:18px;background:none;border:0;color:var(--ink);
 font-size:30px;cursor:pointer}
footer{border-top:1px solid rgba(243,241,236,.12);padding:18px 0 40px;text-align:center;
 color:var(--muted);font-size:12.5px}
</style></head><body>
<div class=wrap>
<header>
  <h1>The book picks</h1>
  <p class=sub>Camp Kingswood &middot; August 2026</p>
</header>
<div class=who>
  <button class=wb id=w-noah data-who=noah aria-pressed=true>Noah&#x27;s picks</button>
  <button class=wb id=w-camp data-who=camp aria-pressed=false>Camp Kingswood&#x27;s picks</button>
</div>
<div class=acts>
  <a class=ab href="delivery.html#book">Open the book tab</a>
  <button class=ab id=copy>Copy the list</button>
  <button class=ab id=paste>Paste a list</button>
</div>
<p class=note id=note></p>
<div class=grid id=grid></div>
</div>
<div id=lb><button id=lbx aria-label=Close>&times;</button><img id=lbi alt=""></div>
<footer>Photographs by Noah Gallagher &middot; Abba Photo</footer>
<script>
var DATA=__DATA__, SET="827b", who="noah";
function key(w){ return "kwood-book-" + SET + "-" + w; }
function read(w){ try{ var v=JSON.parse(localStorage.getItem(key(w))||"[]");
  return Array.isArray(v)?v.filter(function(n){return DATA[n];}):[]; }catch(e){ return []; } }
function draw(){
  var list=read(who), g=document.getElementById("grid"), note=document.getElementById("note");
  document.querySelectorAll(".wb").forEach(function(b){
    b.setAttribute("aria-pressed", b.getAttribute("data-who")===who ? "true":"false"); });
  g.innerHTML="";
  if(!list.length){
    note.textContent="";
    g.innerHTML='<div class=empty style="grid-column:1/-1"><b>No picks on this device.</b>'
      + 'Selections are stored in the browser they were made in, so a set picked on the laptop '
      + 'will not appear on the phone. Open the book tab on the device you picked on, or use '
      + 'Paste a list to bring one over.</div>';
    return;
  }
  note.textContent=list.length+" frames, in book order. The number on the right is the page order.";
  list.forEach(function(n,idx){
    var r=DATA[n];
    var f=document.createElement("figure");
    f.innerHTML='<span class=n>'+n+'</span><span class=seq>'+(idx+1)+'</span>'
      +'<img src="img/present/'+r.f+'" alt="Frame '+n+'" loading=lazy>'
      +'<figcaption><span>'+(r.p.length?r.p.join(" &middot; "):"&nbsp;")+'</span>'
      +(r.d?'<a href="'+r.d+'" target=_blank rel=noopener>Full</a>':'')+'</figcaption>';
    f.querySelector("img").onclick=function(){
      document.getElementById("lbi").src="img/present/"+r.f;
      document.getElementById("lb").className="on"; };
    g.appendChild(f);
  });
}
document.querySelectorAll(".wb").forEach(function(b){
  b.onclick=function(){ who=b.getAttribute("data-who"); draw(); }; });
document.getElementById("copy").onclick=function(){
  var l=read(who); if(!l.length){ this.textContent="Nothing to copy"; return; }
  var t=JSON.stringify(l); var b=this;
  (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject())
    .then(function(){ b.textContent="Copied "+l.length; setTimeout(function(){b.textContent="Copy the list";},1600); })
    .catch(function(){ window.prompt("Copy this list:", t); });
};
document.getElementById("paste").onclick=function(){
  var t=window.prompt("Paste a list of frame numbers:");
  if(!t) return;
  var nums=(t.match(/\\d+/g)||[]).map(Number).filter(function(n){return DATA[n];});
  if(!nums.length){ alert("No frames in this set matched that list."); return; }
  try{ localStorage.setItem(key(who), JSON.stringify(nums)); }catch(e){}
  draw();
};
document.getElementById("lbx").onclick=function(){ document.getElementById("lb").className=""; };
document.getElementById("lb").onclick=function(e){ if(e.target.id!=="lbi") this.className=""; };
document.addEventListener("keydown",function(e){ if(e.key==="Escape") document.getElementById("lb").className=""; });
draw();
</script>
</body></html>"""

open(OUT, "w").write(PAGE.replace("__DATA__", json.dumps(data, separators=(",", ":"))))
print(f"wrote book-picks.html ({len(data)} frames available, picks read from the browser)")
