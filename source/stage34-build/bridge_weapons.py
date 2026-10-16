# Dreadnought bridge: every attack comes out of a weapon you can see on the tower, each with its own shot shape and a wind-up.
#  twin cannon (left, mid-height)  -> bursts of tracer shells, alternating barrels, muzzle flash + smoke
#  red lens (centre)                -> charges up, then a ring of energy rings
#  rocket launcher (left, lower)    -> phase 2+: rockets with smoke trails that home for 1.3 s, then fly straight
# (replaces: orange balls from two points near the guns, red balls from the middle, missiles rising out of the bare deck)
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
old_start="function bridgeAttack(e,dt){"
i=s.index(old_start);j=s.index("function bsVictory(e){",i)
new='''// weapon positions on the bridge art (fractions of the picture): barrel tips of the left twin cannon, the rocket launcher, the lens
const BR_GUN=[[0.012,0.546],[0.012,0.571]],BR_LAUNCH=[0.07,0.675],BR_LENS=[0.5,0.47];
function brPt(e,f){const a=ART.bs_bridge;return [e.x-a.dw/2+f[0]*a.dw,e.y+(a.ofy||0)-a.dh/2+f[1]*a.dh];}
function brShell(x,y,spd){const tx=pl.alive?pl.x:70,ty=pl.alive?pl.y:H/2,a=Math.atan2(ty-y,tx-x)+rnd(-0.04,0.04);
  eb.push({x,y,vx:Math.cos(a)*spd*DF.spd,vy:Math.sin(a)*spd*DF.spd,r:3,dead:false,col:'#ffb43d',s:'shell'});
  P(0,x-2,y,0,0,0.09,10,4,'#ffe08a');for(let i=0;i<3;i++)P(2,x-3,y,rnd(-40,-10),rnd(-12,12),0.5,2,6,null,0.5);
  if(!samp('blaster',0.35,0.55))tone('square',180,90,0.06,0.03);}
function brRocket(x,y){const a=-2.3+rnd(-0.15,0.15),v=95*DF.spd;
  eb.push({x,y,vx:Math.cos(a)*v,vy:Math.sin(a)*v,r:3,dead:false,col:'#ff7a3d',m:true,s:'rocket',ho:1.3});
  P(0,x,y,0,0,0.12,9,4,'#ffd08a');for(let i=0;i<4;i++)P(2,x,y,rnd(-30,20),rnd(-10,25),0.7,2,7,null,0.5);
  if(!sx('missile-launch',0.6,rnd(0.8,0.9)))tone('sawtooth',200,600,0.14,0.035);}
function bridgeAttack(e,dt){
  const ph=bossPhase(e),sp=1+(G.stage-1)*0.05;
  e.x=BS.x0+e.sx+rnd(-0.4,0.4);
  e.f1-=dt*DF.fire;e.f2-=dt*DF.fire;e.f3-=dt*DF.fire;
  if(ph===2&&Math.random()<dt*2)explode(e.x+rnd(-50,50),e.y+rnd(-60,30),0.8,e.pal,true);
  // a cannon burst in progress: one shell at a time, barrels alternating
  if(e.burst>0){e.bT-=dt;if(e.bT<=0){e.bT=0.14;e.burst--;const g=brPt(e,BR_GUN[e.burst%2]);brShell(g[0],g[1],150*sp);}return;}
  if(e.tell||G.state!=='play')return;   // one attack winds up at a time
  if(e.f1<=0){e.f1=(ph===2?1.6:ph===1?2.0:2.4)/sp;
    bossTell(e,0.45,()=>BR_GUN.map(f=>brPt(e,f)),'#ffb43d',()=>{e.burst=ph===2?5:ph===1?4:3;e.bT=0;});}
  else if(e.f2<=0){e.f2=(ph===0?3.6:2.8)/sp;
    bossTell(e,0.65,()=>[brPt(e,BR_LENS)],'#ff3d3d',()=>{const c=brPt(e,BR_LENS);radial(c[0],c[1],ph===2?18:13,80*sp,e.t,'#ff3d3d');trauma=Math.max(trauma,0.15);});}
  else if(ph>=1&&e.f3<=0){e.f3=(ph===2?3.2:4.2)/sp;
    bossTell(e,0.6,()=>[brPt(e,BR_LAUNCH)],'#ff7a3d',()=>{const n=ph===2?3:2;for(let i=0;i<n;i++)later(i*0.28,()=>{if(e.dead||e.dying||!G.boss)return;const p=brPt(e,BR_LAUNCH);brRocket(p[0],p[1]);});});}
}
'''
s=s[:i]+new+s[j:]
# the telegraph glow is drawn for the bridge too
rep("if(e.type==='bs_bridge'&&ART.bs_bridge.n){drawBridge(e,ART.bs_bridge);return;}",
    "if(e.type==='bs_bridge'&&ART.bs_bridge.n){drawBridge(e,ART.bs_bridge);drawTell(e);return;}")
# rocket smoke and flame go out of the back, whichever way it is flying
rep("if(b.m&&Math.random()<0.5*Q)P(2,b.x+rnd(-1,1),b.y+(b.vy>0?-5:5),rnd(-6,6),b.vy>0?-25:25,0.45,1.5,4,null,1);",
    "if(b.m&&Math.random()<0.5*Q){const sv=Math.hypot(b.vx,b.vy)||1;P(2,b.x-b.vx/sv*6+rnd(-1,1),b.y-b.vy/sv*6+rnd(-1,1),-b.vx/sv*25+rnd(-6,6),-b.vy/sv*25+rnd(-6,6),0.45,1.5,4,null,1);}")
rep("    if(b.m){const f=4+Math.random()*3;ctx.drawImage(glow(C.ember),b.x-f,b.vy>0?b.y-3-f*3:b.y+3,f*2,f*3);}}}",
    "    if(b.m){const f=4+Math.random()*3,sv=Math.hypot(b.vx,b.vy)||1,fx=b.x-b.vx/sv*(5+f),fy=b.y-b.vy/sv*(5+f);ctx.drawImage(glow(C.ember),fx-f,fy-f,f*2,f*2);}}}")
# glows: shells get a stretched tracer glow like needles
rep("    if(k==='needle'){const a=Math.atan2(b.vy,b.vx);",
    "    if(k==='needle'||k==='shell'){const a=Math.atan2(b.vy,b.vx);")
# bodies: shell = brass tracer round with a white-hot tip; rocket = body, red nose, fins
rep("      case 'ring':ctx.strokeStyle=C.white;",
    "      case 'shell':ctx.rotate(a);ctx.fillStyle='#ffcf6b';ctx.beginPath();ctx.ellipse(-1,0,4.2,1.7,0,0,TAU);ctx.fill();ctx.fillStyle=C.white;ctx.beginPath();ctx.arc(2.6,0,1.3,0,TAU);ctx.fill();ctx.fillStyle='rgba(255,150,60,.7)';ctx.fillRect(-9,-0.6,5,1.2);break;\n"
    "      case 'rocket':ctx.rotate(a);ctx.fillStyle='#3a3a44';ctx.beginPath();ctx.moveTo(-5,-1.8);ctx.lineTo(-7,-3.6);ctx.lineTo(-3.5,-1.8);ctx.lineTo(-3.5,1.8);ctx.lineTo(-7,3.6);ctx.lineTo(-5,1.8);ctx.closePath();ctx.fill();\n"
    "        ctx.fillStyle='#d6d8e0';ctx.fillRect(-5.5,-1.6,8,3.2);ctx.fillStyle='#ff3d3d';ctx.beginPath();ctx.moveTo(2.5,-1.6);ctx.lineTo(5.5,0);ctx.lineTo(2.5,1.6);ctx.closePath();ctx.fill();break;\n"
    "      case 'ring':ctx.strokeStyle=C.white;")
# Extras roster text
rep("'The ship\\'s command tower. Triple volleys and rings of bullets, then missiles from the deck.'",
    "'The ship\\'s command tower. Its twin cannon fires bursts of shells and its red lens fires energy rings, then its launcher adds homing rockets.'")
open(P,'w').write(s);print('OK')
