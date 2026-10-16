"""Power-up economy: pickups come from set moments, not random kills.
- Ordinary enemies no longer drop pickups (the rare extra life from big enemies stays).
- A gold-glowing carrier crosses at fixed points in each stage and releases one pickup when destroyed:
  two weapon pods and one utility pickup per stage (speed, helper drone, rear gun or bomb).
- Mini-boss: no free pod on arrival; one weapon pod when destroyed.
- Boss: pickups on each rage phase as before; the timed drops during the fight every 25 s (was 12-15 s); one weapon pod when destroyed (was weapon + speed/bomb + bomb).
Measured before: 21 pickups in stage 1, full power ~2 minutes into the game."""
import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n:sys.exit(f'FAIL ({c}x): {a[:100]}')
    s=s.replace(a,b)
rep("  if(Math.random()<ch)pups.push({x:e.x,y:e.y,type:pickDrop(),t:0,wi:(Math.random()*4)|0});",
    "  if(e.carry){pups.push({x:e.x,y:e.y,type:e.carry,t:0,wi:(Math.random()*4)|0});P(3,e.x,e.y,0,0,0.4,6,40,C.gold);popup(e.x,e.y-14,'Pickup!',C.gold);}   // carriers are the only ordinary enemies that drop pickups")
rep("G.mini=e;banner(MB[k].name,2.2);pups.push({x:W+6,y:H*0.62,type:'W',t:0,wi:(Math.random()*4)|0});",
    "G.mini=e;banner(MB[k].name,2.2);")
rep("  pups.push({x:e.x,y:e.y,type:pickDrop(),t:0,wi:(Math.random()*4)|0},{x:e.x+14,y:e.y+10,type:'W',t:0,wi:(Math.random()*4)|0});",
    "  pups.push({x:e.x,y:e.y,type:'W',t:0,wi:(Math.random()*4)|0});")
rep("    if(G.bossDropT<=0){G.bossDropT=rnd(12,15);","    if(G.bossDropT<=0){G.bossDropT=rnd(24,27);")
rep("      if(e.type!=='titan'){pups.push({x:e.x,y:e.y-24,type:'W',t:0,wi:(Math.random()*4)|0},{x:e.x,y:e.y,type:G.speed<4?'S':'B',t:0},{x:e.x,y:e.y+24,type:'B',t:0});",
    "      if(e.type!=='titan'){pups.push({x:e.x,y:e.y,type:'W',t:0,wi:(Math.random()*4)|0});")
CODE=r"""
/* ---------- pickup carriers: the set moments where power-ups come from ----------
   times are on each stage's own clock (music position for stages 1, 3, 4; stage time for 2 and 5) */
const CARRY={1:[[56,'W'],[76,'S'],[120,'W']],2:[[16,'W'],[32,'D'],[48,'W']],3:[[44,'W'],[70,'R'],[120,'W']],4:[[22,'W'],[60,'B'],[100,'W']],5:[[14,'W'],[34,'S'],[50,'W']]};
function carryClock(){if(G.stage===1&&s1On())return s1Clock();if(G.stage===3&&MUSIC.stage3h)return sxClock(HV);if(G.stage===4&&MUSIC.stage4d)return sxClock(DN);return G.stageT;}
function carryTick(){if(G.state!=='play'||G.pre||G.boss||G.clearT>0||G.ending)return;const L=CARRY[G.stage];if(!L)return;G.cDone=G.cDone||{};const T=carryClock();
  for(let i=0;i<L.length;i++){if(G.cDone[i]||T<L[i][0])continue;G.cDone[i]=1;let k=L[i][1];
    if(k==='S'&&G.speed>=4)k='B';if(k==='D'&&DR.on)k='B';if(k==='R'&&G.rear)k='B';
    const y=rnd(55,H-85),e=E('drone',W+20,y,{baseY:y,amp:18,freq:1.6,phase:0,spd:42,carry:k});e.hp=e.max=10*hpScale();e.score=1000;}}
function drawCarryGlow(e){const pu=0.5+0.5*Math.sin(G.t*7);ctx.save();ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.45+0.35*pu;
  ctx.drawImage(glow(PUP_COL[e.carry]||C.gold),e.x-22,e.y-22,44,44);ctx.globalAlpha=0.7;ctx.strokeStyle=C.gold;ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(e.x,e.y,14+2*pu,0,TAU);ctx.stroke();ctx.restore();}
"""
rep("function director(dt){",CODE+"function director(dt){")
rep("  G.stageT+=dt;\n","  G.stageT+=dt;carryTick();\n")
rep("function drawEnemy(e){\n","function drawEnemy(e){\n  if(e.carry&&!e.dead)drawCarryGlow(e);\n")
rep("function tunReset(){TUN.on=false;TUN.done=false;","function tunReset(){TUN.on=false;TUN.done=false;G.cDone={};")
open(p,'w',encoding='utf-8').write(s);print('OK')
