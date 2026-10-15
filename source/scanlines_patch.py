"""Screen look: replace Arcade CRT (low-res + vignette, looked blurry) with Scanlines: full resolution like Clean, plus crisp dark lines."""
import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n:sys.exit(f'FAIL ({c}x): {a[:90]}')
    s=s.replace(a,b)
rep("""let SCREEN='crt';try{SCREEN=JSON.parse(localStorage.getItem('bangshoot-options')||'{}').screen||'crt';}catch(e){}""",
"""let SCREEN='scan';try{SCREEN=JSON.parse(localStorage.getItem('bangshoot-options')||'{}').screen||'scan';}catch(e){}
if(SCREEN==='crt')SCREEN='scan';   // the old Arcade CRT setting becomes Scanlines""")
rep("""  if(SCREEN==='clean'){cv.width""","""  if(SCREEN!=='pixel'){cv.width""")
rep("""  cv.classList.toggle('px',SCREEN!=='clean');""","""  cv.classList.toggle('px',SCREEN==='pixel');""")
rep("""  if(SCREEN==='crt'){const r=cv.getBoundingClientRect(),row=ch/H,per=row>=3?row:row*2;   // one dark line per game row, or per two on small screens so lines stay visible
    Object.assign(crt.style,{display:'block',left:r.left+'px',top:r.top+'px',width:cw+'px',height:ch+'px',
      backgroundImage:'radial-gradient(ellipse at center,rgba(0,0,0,0) 58%,rgba(0,0,0,.55) 100%),repeating-linear-gradient(to bottom,rgba(0,0,0,0) 0px,rgba(0,0,0,0) '+(per*0.55)+'px,rgba(0,0,0,.32) '+(per*0.55)+'px,rgba(0,0,0,.32) '+per+'px)'});}""",
"""  if(SCREEN==='scan'){const r=cv.getBoundingClientRect(),per=Math.max(3,Math.round(ch/H)),dk=Math.max(1,Math.round(per*0.45));   // one line per game row, in whole screen pixels so every line is equally sharp
    Object.assign(crt.style,{display:'block',left:r.left+'px',top:r.top+'px',width:cw+'px',height:ch+'px',
      backgroundImage:'repeating-linear-gradient(to bottom,rgba(0,0,0,0) 0px,rgba(0,0,0,0) '+(per-dk)+'px,rgba(0,0,0,.38) '+(per-dk)+'px,rgba(0,0,0,.38) '+per+'px)'});}""")
rep("""diff:'medium',screen:'crt'};""","""diff:'medium',screen:'scan'};""")
rep("""const L=['clean','pixel','crt'];OPT.screen=L[(L.indexOf(OPT.screen)+(d>0?1:2))%3];""","""const L=['clean','scan','pixel'];OPT.screen=L[(Math.max(0,L.indexOf(OPT.screen))+(d>0?1:2))%3];""")
rep("""['Screen',{clean:'Clean',pixel:'Pixel',crt:'Arcade CRT'}[OPT.screen]||'Arcade CRT']""","""['Screen',{clean:'Clean',scan:'Scanlines',pixel:'Pixel'}[OPT.screen]||'Scanlines']""")
rep("""try{Object.assign(OPT,JSON.parse(localStorage.getItem('bangshoot-options')||'{}'));}catch(e){}""","""try{Object.assign(OPT,JSON.parse(localStorage.getItem('bangshoot-options')||'{}'));}catch(e){}
if(OPT.screen==='crt')OPT.screen='scan';""")
open(p,'w',encoding='utf-8').write(s);print('OK')
