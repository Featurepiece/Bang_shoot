"""Hive walls: grow smoothly out of the ceiling/floor at the start and sink back at the end (was a hard vertical cut).
Drawn in 3 px vertical strips; each strip is lowered by a smooth ramp over 150 px, and the hit area follows the same ramp."""
import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n:sys.exit(f'FAIL ({c}x): {a[:90]}')
    s=s.replace(a,b)
rep("""function hvDepth(X,bottom){const w=HV.walls;if(!w||X<w.X0-40||X>w.X1+40)return 0;
  const ramp=clamp(Math.min(X-w.X0+40,w.X1+40-X)/60,0,1),""",
"""const HV_RAMP=150;
function hvRamp(X){const w=HV.walls;if(!w)return 0;const r=clamp(Math.min(X-w.X0,w.X1-X)/HV_RAMP,0,1);return r*r*(3-2*r);}   // smoothstep
function hvDepth(X,bottom){const w=HV.walls;if(!w||X<w.X0||X>w.X1)return 0;
  const ramp=hvRamp(X),""")
a=s.index("function drawHiveWalls(){");b=s.index("\n  for(const p of w.pods)",a)
s=s[:a]+r"""function drawHiveWalls(){const w=HV.walls;if(!w)return;const a=HVA.wall.img;if(!a.complete||!a.naturalWidth)return;
  const x0=w.X0-G.scroll,x1=w.X1-G.scroll;if(x1<0||x0>W)return;ctx.save();ctx.imageSmoothingEnabled=true;
  const iw=a.naturalWidth,ih=a.naturalHeight,SW=3,xa=Math.max(0,Math.floor(x0)),xb=Math.min(W,Math.ceil(x1));
  for(let x=xa;x<xb;x+=SW){const X=x+G.scroll,r=hvRamp(X);if(r<=0.01)continue;const off=HV_WH*(1-r);
    let u=mod(X,HV_WW)/HV_WW*iw;ctx.drawImage(a,Math.min(u,iw-1),0,Math.min(SW/HV_WW*iw,iw-u),ih,x,-off,SW+0.6,HV_WH);                 // ceiling strip
    u=mod(X+HV_WW*0.5,HV_WW)/HV_WW*iw;ctx.save();ctx.translate(0,H);ctx.scale(1,-1);
    ctx.drawImage(a,Math.min(u,iw-1),0,Math.min(SW/HV_WW*iw,iw-u),ih,x,-off,SW+0.6,HV_WH);ctx.restore();}                                // floor strip (flipped)"""+s[b:]
open(p,'w',encoding='utf-8').write(s);print('OK')
