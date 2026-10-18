# Power-up carrier: its own graphic (friendly supply pod), window tinted with the colour of what it carries,
# flickering thrusters; carriers never turn into hunters.
import sys,base64
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
IMG='/tmp/claude-0/-home-claude-bang-shoot/ae8d7b5e-3457-5a66-9a7e-d466f5b48944/scratchpad/carrier/carrier.webp'
uri='data:image/webp;base64,'+base64.b64encode(open(IMG,'rb').read()).decode()
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
rep("function drawCarryGlow(e){",
"const CARRIER={img:new Image(),dw:46,dh:46*640/1131,win:[0.4032,0.4875,0.2207],noz:[[0.97,0.34],[0.97,0.66]]};CARRIER.img.src='"+uri+"';\n"
r'''function carryCol(e){return e.carry==='W'?Object.values(WCOL)[Math.floor(G.t*1.5)%4]:PUP_COL[e.carry]||C.gold;}
function drawCarrier(e){const C_=CARRIER,dw=C_.dw,dh=C_.dh,col=carryCol(e),pu=0.5+0.5*Math.sin(G.t*7),X=f=>-dw/2+f*dw,Y=f=>-dh/2+f*dh;
  ctx.save();ctx.translate(e.x,e.y);ctx.rotate(Math.sin(G.t*2.2+e.phase)*0.05);
  ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.3+0.25*pu;ctx.drawImage(glow(col),-dw*0.75,-dw*0.75,dw*1.5,dw*1.5);   // soft halo so it stands out
  for(const [nx,ny] of C_.noz){const f=4+Math.random()*3;ctx.globalAlpha=0.8;ctx.drawImage(glow(C.ember),X(nx)-2,Y(ny)-f/2,f*1.8,f);}   // thrusters
  ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.imageSmoothingEnabled=true;
  if(C_.img.complete&&C_.img.naturalWidth)ctx.drawImage(C_.img,-dw/2,-dh/2,dw,dh);
  // the cargo window shows what's inside
  const wx=X(C_.win[0]),wy=Y(C_.win[1]),wr=C_.win[2]*dh;ctx.save();ctx.beginPath();ctx.arc(wx,wy,wr,0,TAU);ctx.clip();
  ctx.globalCompositeOperation='multiply';ctx.fillStyle=col;ctx.fillRect(wx-wr,wy-wr,wr*2,wr*2);
  ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.35+0.35*pu;ctx.drawImage(glow(col),wx-wr*1.4,wy-wr*1.4,wr*2.8,wr*2.8);ctx.restore();
  if(e.flash>0){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=Math.min(1,e.flash*6)*0.7;ctx.drawImage(C_.img,-dw/2,-dh/2,dw,dh);}
  ctx.restore();}
function drawCarryGlow(e){''')
rep("  if(e.carry&&!e.dead)drawCarryGlow(e);\n","  if(e.carry&&!e.dead&&CARRIER.img.complete&&CARRIER.img.naturalWidth){drawCarrier(e);return;}\n  if(e.carry&&!e.dead)drawCarryGlow(e);\n")
# hit area to match the bigger pod
rep("const y=rnd(55,H-85),e=E('drone',W+20,y,{baseY:y,amp:18,freq:1.6,phase:0,spd:42,carry:k});e.hp=e.max=10*hpScale();e.score=1000;",
    "const y=rnd(55,H-85),e=E('drone',W+30,y,{baseY:y,amp:14,freq:1.6,phase:0,spd:42,carry:k});e.hp=e.max=10*hpScale();e.score=1000;e.hw=20;e.hh=10;")
# a carrier only ever means a reward: it never mutates into a hunter
rep("  if(!e.huntRoll||G.state!=='play'","  if(e.carry||!e.huntRoll||G.state!=='play'")
open(P,'w').write(s);print('OK')
