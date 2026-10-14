"""Retro screen option: Clean (full resolution, as before), Pixel (true 480x270, blocky upscale), Arcade CRT (Pixel + scanlines + dark edges)."""
import sys
path=sys.argv[1];src=open(path,encoding='utf-8').read()
def rep(old,new,count=1):
    global src
    n=src.count(old)
    if n!=count: sys.exit(f'FAIL ({n}x, wanted {count}x): {old[:100]}')
    src=src.replace(old,new)
rep("""canvas{display:block;touch-action:none;max-width:100%}""",
"""canvas{display:block;touch-action:none;max-width:100%}
canvas.px{image-rendering:crisp-edges;image-rendering:pixelated}
#crt{position:fixed;pointer-events:none;display:none;z-index:2}""")
rep("""<canvas id="c" aria-label="Bang Shoot! game screen"></canvas>""","""<canvas id="c" aria-label="Bang Shoot! game screen"></canvas>
<div id="crt"></div>""")
rep("""let K=1;
function resize(){""","""let K=1;
// Screen look (Options): 'clean' = full resolution; 'pixel' = drawn at the real 480x270 and enlarged with hard pixels (also less work for the phone);
// 'crt' = pixel + scanlines and darkened edges, a see-through layer the browser composites almost for free
let SCREEN='crt';try{SCREEN=JSON.parse(localStorage.getItem('bangshoot-options')||'{}').screen||'crt';}catch(e){}
function resize(){""")
rep("""  cv.width=Math.round(cw*dpr); cv.height=Math.round(ch*dpr);
  K=cv.width/W;""","""  if(SCREEN==='clean'){cv.width=Math.round(cw*dpr); cv.height=Math.round(ch*dpr);}else{cv.width=W;cv.height=H;}
  cv.classList.toggle('px',SCREEN!=='clean');
  K=cv.width/W;
  const crt=document.getElementById('crt');
  if(SCREEN==='crt'){const r=cv.getBoundingClientRect(),row=ch/H,per=row>=3?row:row*2;   // one dark line per game row, or per two on small screens so lines stay visible
    Object.assign(crt.style,{display:'block',left:r.left+'px',top:r.top+'px',width:cw+'px',height:ch+'px',
      backgroundImage:'radial-gradient(ellipse at center,rgba(0,0,0,0) 58%,rgba(0,0,0,.55) 100%),repeating-linear-gradient(to bottom,rgba(0,0,0,0) 0px,rgba(0,0,0,0) '+(per*0.55)+'px,rgba(0,0,0,.32) '+(per*0.55)+'px,rgba(0,0,0,.32) '+per+'px)'});}
  else crt.style.display='none';""")
rep("""const OPT={music:8,sfx:8,rumble:'light',intro:'auto',diff:'medium'};""","""const OPT={music:8,sfx:8,rumble:'light',intro:'auto',diff:'medium',screen:'crt'};""")
# options menu: new 'Screen' row before Back
rep("""    const n=6;
    if(a==='up')MENU.sel""","""    const n=7;
    if(a==='up')MENU.sel""")
rep("""      else if(MENU.sel===4){const L=['auto','full','short'];OPT.intro=L[(L.indexOf(OPT.intro)+(d>0?1:2))%3];}""",
"""      else if(MENU.sel===4){const L=['auto','full','short'];OPT.intro=L[(L.indexOf(OPT.intro)+(d>0?1:2))%3];}
      else if(MENU.sel===5){const L=['clean','pixel','crt'];OPT.screen=L[(L.indexOf(OPT.screen)+(d>0?1:2))%3];SCREEN=OPT.screen;resize();}""")
rep("""['Intro',{auto:'Full first',full:'Always full',short:'Always short'}[OPT.intro]],['Back',null]];""",
"""['Intro',{auto:'Full first',full:'Always full',short:'Always short'}[OPT.intro]],['Screen',{clean:'Clean',pixel:'Pixel',crt:'Arcade CRT'}[OPT.screen]||'Arcade CRT'],['Back',null]];""")
rep("""  if(s==='options'){for(let i=0;i<6;i++){const y=OPT_Y+i*18;if(Math.abs(p.y-y)<9){MENU.sel=i;
      if(i===5)menuInput('ok');""","""  if(s==='options'){for(let i=0;i<7;i++){const y=OPT_Y+i*18;if(Math.abs(p.y-y)<9){MENU.sel=i;
      if(i===6)menuInput('ok');""")
open(path,'w',encoding='utf-8').write(src);print('OK')
