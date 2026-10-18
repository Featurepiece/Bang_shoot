# 1) one more power-up carrier per stage (3 -> 4), at a calm point of each stage
# 2) flying enemies and pickups are kept inside the open gap while a tunnel or the hive walls are beside them
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
rep("const CARRY={1:[[56,'W'],[76,'S'],[120,'W']],2:[[16,'W'],[32,'D'],[48,'W']],3:[[45,'W'],[75,'R'],[135,'W']],4:[[22,'W'],[60,'B'],[100,'W']],5:[[14,'W'],[34,'S'],[50,'W']]};",
    "const CARRY={1:[[56,'W'],[76,'S'],[120,'W'],[146,'W']],2:[[16,'W'],[32,'D'],[48,'W'],[60,'W']],3:[[45,'W'],[75,'R'],[110,'W'],[135,'W']],4:[[22,'W'],[60,'B'],[100,'W'],[130,'W']],5:[[14,'W'],[34,'S'],[50,'W'],[58,'W']]};")
rep("function tunnelUpdate(dt){",
r'''// the open space at screen x: between the tunnel walls and/or the hive walls (null when there are none)
function gapAt(x){let top=-1e9,bot=1e9;const t=TUN.on?tunAt(x+G.scroll):null;
  if(t&&t.r>0.25){top=t.ceil;bot=t.floor;}
  if(HV.walls){const a=hvTop(x),b=hvBot(x);if(a>0)top=Math.max(top,a);if(b<H)bot=Math.min(bot,b);}
  return top<-1e8&&bot>1e8?null:[top,bot];}
function keepInGap(){if(G.state!=='play'||!(TUN.on||HV.walls))return;
  const fit=(o,m)=>{const g=gapAt(o.x);if(!g)return;const lo=g[0]+m,hi=g[1]-m,ny=lo>hi?(g[0]+g[1])/2:clamp(o.y,lo,hi);
    if(ny!==o.y){const d=ny-o.y;o.y=ny;if(o.baseY!==undefined)o.baseY+=d;}};
  for(const e of enemies){if(e.dead||e.dying||e.isBoss||e.x<-30||e.x>W+40)continue;const ty=e.type;
    if(e.st==='walk'||e.ceilW||ty.startsWith('walker')||ty.startsWith('bs_')||ty.startsWith('mb_')||ty==='hpod'||ty==='serpg'||ty==='ring')continue;   // wall-walkers, wall pods and set pieces stay put
    fit(e,Math.min(e.hh||8,14)+3+(e.amp||0));}
  for(const p of pups)if(p.x>-20&&p.x<W+20)fit(p,8);}
function tunnelUpdate(dt){''')
rep("  if(G.state==='play'||G.state==='over')tunnelUpdate(dt);",
    "  if(G.state==='play'||G.state==='over')tunnelUpdate(dt);\n  keepInGap();")
open(P,'w').write(s);print('OK')
