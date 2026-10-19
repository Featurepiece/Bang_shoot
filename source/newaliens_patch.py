# v2.7: five new stage 1 aliens (spinner, hopper, gun turret, charger, spore mine), a scripted stage 1 running order
# (one new type at a time, fixed timeline), Dreadnought walkers only on the hull, Mothership eased at power 1-2.
import sys,base64,os
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
D='/tmp/claude-0/-home-claude-bang-shoot/ae8d7b5e-3457-5a66-9a7e-d466f5b48944/scratchpad/new1/'
def uri(n):return 'data:image/webp;base64,'+base64.b64encode(open(D+n+'.webp','rb').read()).decode()
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:80]}')
    s=s.replace(a,b)
# ---------- art (before the art loader runs) ----------
rep("for(const k in ART){const a=ART[k];if(!a.src)continue;const im=new Image();im.onload=()=>{",
 "Object.assign(ART,{\n"
 f"  spinner:{{dw:22,dh:22.9,cr:4,core:[0,0],gc:'#ffb43d',src:'{uri('spinner')}'}},\n"
 f"  hopper:{{dw:30,dh:23.9,cr:3,core:[-11.1,0],gc:'#ffb43d',src:'{uri('hopper')}'}},\n"
 f"  gturret:{{dw:42,dh:23.8,cr:3,core:[10.5,5.2],gc:'#ffb43d',src:'{uri('gturret')}'}},\n"
 f"  charger:{{dw:46,dh:19.55,cr:4,core:[20.5,0],gc:'#ff7a3d',src:'{uri('charger')}'}},\n"
 f"  smine:{{dw:20,dh:20.45,cr:5,core:[0,0],gc:'#ffb43d',src:'{uri('smine')}'}}}});\n"
 f"const GBAR=new Image();GBAR.src='{uri('gbarrel')}';   // the gun turret's barrels, drawn turning over its dome\n"
 "for(const k in ART){const a=ART[k];if(!a.src)continue;const im=new Image();im.onload=()=>{")
# ---------- stats, intro names, enemy guide ----------
rep("let DF={fire:1,spd:1,hp:1,spawn:1};",
 "Object.assign(DEF,{spinner:{hp:2,score:120,pw:1,drop:0},hopper:{hp:6,score:300,pw:1.6,drop:0},gturret:{hp:8,score:500,pw:2,drop:0},charger:{hp:5,score:400,pw:1.8,drop:0},smine:{hp:3,score:150,pw:1.4,drop:0}});\n"
 "let DF={fire:1,spd:1,hp:1,spawn:1};")
rep("const INTRO={drone:'Drone',","const INTRO={spinner:'Spinner',hopper:'Hopper',gturret:'Gun turret',charger:'Charger',smine:'Spore mine',drone:'Drone',")
rep(" [1,'swarm','Swarm','Small, fast darts that fly in tight formations.',['ram']],",
 " [1,'swarm','Swarm','Small, fast darts that fly in tight formations.',['ram']],\n"
 " [1,'spinner','Spinner','Small blades that loop through the air in groups.',['ram']],\n"
 " [1,'hopper','Hopper','Leaps along the ground and fires one shot at the top of each jump.',['shot','ram']],\n"
 " [1,'gturret','Gun turret','Sits on the ground. Its barrels turn to follow you, glow, then fire a pair of shells.',['shot','ram']],\n"
 " [1,'charger','Charger','Hangs back lining up with you. When its nose glows it dashes straight across the screen.',['ram']],\n"
 " [1,'smine','Spore mine','Drifts slowly. Shot, touched or left too long, it bursts into a ring of spores.',['shot','ram']],")
# ---------- behaviours ----------
rep("      case 'boss':case 'queen':case 'mother':updateBoss(e,dt);break;",
r'''      case 'spinner':{   // loops along, spinning; follows the gate gaps when there are gates
        e.cx=(e.cx===undefined?e.x:e.cx)-e.spd*dt;const a=e.t*e.w+e.ph;
        if(e.gate){const gc=gateC(e.cx+G.scroll);if(gc!==null)e.y0+=(gc-e.y0)*Math.min(1,dt*3);}
        e.x=e.cx+Math.cos(a)*e.R;e.y=e.y0+Math.sin(a)*e.R*0.8;e.rot+=dt*9;if(e.cx<-50)e.dead=true;break;}
      case 'hopper':{    // crouch, leap, fire at the top of the jump, land
        const gy=groundY(e.x)-ART.hopper.dh/2+2;
        if(e.X===undefined){e.X=e.x+G.scroll;e.y=gy;e.st='crouch';e.vy=0;e.sqy=1;}
        if(e.st==='crouch'){e.x=e.X-G.scroll;e.y=groundY(e.x)-ART.hopper.dh/2+2;e.ct-=dt;e.sqy+=(0.78-e.sqy)*Math.min(1,dt*10);
          if(e.ct<=0&&e.x<W+10){e.st='air';e.vy=-(165+15*d);e.vx=-42;e.fired=false;if(e.x<W)sx('dive',0.35,1.6);}}
        else{e.X+=e.vx*dt;e.x=e.X-G.scroll;e.y+=e.vy*dt;const ov=e.vy;e.vy+=420*dt;e.sqy+=(1.12-e.sqy)*Math.min(1,dt*10);
          if(ov<0&&e.vy>=0&&!e.fired&&G.state==='play'&&e.x<W-10&&e.x>pl.x+40){e.fired=true;aim(e.x-10,e.y-2,95+15*d,1,0,'#ffb43d');}
          if(e.vy>0&&e.y>=gy){e.y=gy;e.st='crouch';e.ct=0.75;e.sqy=0.7;P(1,e.x,e.y+10,-30,-20,0.25,1.5,0,'#c9a4ff',3);}}
        break;}
      case 'gturret':{   // on the ground; barrels turn towards you, glow, then fire two shells
        if(e.X===undefined)e.X=e.x+G.scroll;e.x=e.X-G.scroll;e.y=groundY(e.x)-ART.gturret.dh/2+3;
        const [px,py]=gtPivot(e),tx=pl.alive?pl.x:60,ty=pl.alive?pl.y:H/2;let want=Math.atan2(ty-py,tx-px);if(want>0)want=want>Math.PI/2?-Math.PI:-Math.PI/2+0.01;   // only up and to the left
        want=clamp(want,-Math.PI,-Math.PI/2);const da=want-e.ang;e.ang+=clamp(da,-1.6*dt,1.6*dt);
        e.fireT-=dt*DF.fire;e.tellT=e.fireT<0.5&&e.fireT>0?0.5-e.fireT:0;
        if(e.fireT<=0){e.fireT=Math.max(1.4,2.6/d);if(G.state==='play'&&e.x<W-12&&e.x>pl.x+30){const m=gtMuzzles(e);
          for(let i=0;i<2;i++)later(i*0.13,()=>{if(e.dead||e.dying)return;const q=gtMuzzles(e)[i],v=(120+15*d)*DF.spd;eb.push({x:q[0],y:q[1],vx:Math.cos(e.ang)*v,vy:Math.sin(e.ang)*v,r:3,dead:false,col:'#ffb43d',s:'shell'});
            P(0,q[0],q[1],0,0,0.09,8,3,'#ffe08a');if(!samp('blaster',0.25,0.7))tone('square',200,100,0.05,0.025);});}}
        break;}
      case 'charger':{   // slides in, lines up with you, nose glows, then dashes straight across
        if(e.st==='in'){e.x+=(e.tx-e.x)*Math.min(1,dt*2.4);if(Math.abs(e.x-e.tx)<3){e.st='aim';e.st_t=1.0;}}
        else if(e.st==='aim'){const ty=pl.alive?pl.y:H/2;e.y+=clamp(ty-e.y,-55*dt,55*dt);e.st_t-=dt;if(e.st_t<=0){e.st='tell';e.st_t=0.6;sx('boss-tell',0.5,1.7);}}
        else if(e.st==='tell'){e.st_t-=dt;e.x+=Math.sin(e.t*60)*0.4;if(e.st_t<=0){e.st='dash';e.vx=0;if(!sx('kamikaze',0.7,1.15))tone('sawtooth',300,900,0.25,0.04);}}
        else{e.vx=Math.max(-(330+30*d)*DF.spd,e.vx-1400*dt);e.x+=e.vx*dt;if(Math.random()<0.6*Q)P(2,e.x+22,e.y,60,rnd(-10,10),0.4,2,6,null,0.5);}
        break;}
      case 'smine':{     // drifts; shot, touched or left too long, it arms and bursts
        e.x-=e.spd*dt;if(e.gate){const gc=gateC(e.x+G.scroll);if(gc!==null)e.baseY+=(gc-e.baseY)*Math.min(1,dt*2);}
        e.y=e.baseY+Math.sin(e.t*1.6+e.ph)*6;e.rot+=dt*0.7;
        if(e.arm===undefined&&G.state==='play'&&e.x<W-6&&(e.t>7||e.hp<e.max||(pl.alive&&Math.hypot(pl.x-e.x,pl.y-e.y)<46))){e.arm=0.7;sx('boss-tell',0.35,2);}
        if(e.arm!==undefined){e.arm-=dt;e.sc=1+0.12*Math.abs(Math.sin(e.t*30));if(e.arm<=0){smineBurst(e);explode(e.x,e.y,1.2,PAL_HOT,true);e.dead=true;}}
        break;}
      case 'boss':case 'queen':case 'mother':updateBoss(e,dt);break;''')
rep("function kill(e){\n","function kill(e){\n  if(e.type==='smine'&&!e.burst)smineBurst(e);\n")
rep("function tunnelUpdate(dt){",
r'''function smineBurst(e){if(e.burst)return;e.burst=true;if(G.state!=='play')return;const n=8,v=(80+10*diff())*DF.spd,a0=e.t;
  for(let i=0;i<n;i++){const a=a0+i*TAU/n;eb.push({x:e.x,y:e.y,vx:Math.cos(a)*v,vy:Math.sin(a)*v,r:3,dead:false,col:'#ffb43d',s:'ring'});}
  if(!sx('egg-burst',0.7,0.8))noiseHit(0.2,0.08,3000,400);}
// gun turret geometry (fractions of its picture): barrel pivot and the two muzzles at the barrels' resting angle
const GT={piv:[0.52,0.42],mz:[[0.17,0.05],[0.12,0.16]],a0:-2.63};
function gtPivot(e){const a=ART.gturret;return [e.x-a.dw/2+GT.piv[0]*a.dw,e.y-a.dh/2+GT.piv[1]*a.dh];}
function gtMuzzles(e){const a=ART.gturret,[px,py]=gtPivot(e),r=e.ang-GT.a0,c=Math.cos(r),sn=Math.sin(r);
  return GT.mz.map(([fx,fy])=>{const lx=(fx-GT.piv[0])*a.dw,ly=(fy-GT.piv[1])*a.dh;return [px+lx*c-ly*sn,py+lx*sn+ly*c];});}
function drawGTurret(e){const a=ART.gturret,white=e.flash>0||(e.dying&&Math.random()<0.3),[px,py]=gtPivot(e);
  ctx.save();ctx.imageSmoothingEnabled=true;
  if(GBAR.complete&&GBAR.naturalWidth){ctx.save();ctx.translate(px,py);ctx.rotate(e.ang-GT.a0);const ox=-GT.piv[0]*a.dw,oy=-GT.piv[1]*a.dh;
    ctx.drawImage(GBAR,ox,oy,a.dw,a.dh);if(white){ctx.globalAlpha=0.45;ctx.drawImage(tintOf(gbarCanvas(),'#ffffff'),ox,oy,a.dw,a.dh);}ctx.restore();}
  ctx.drawImage(a.n,e.x-a.dw/2,e.y-a.dh/2,a.dw,a.dh);if(white){ctx.globalAlpha=0.45;ctx.drawImage(a.w,e.x-a.dw/2,e.y-a.dh/2,a.dw,a.dh);}
  ctx.restore();}
let _gbc=null;function gbarCanvas(){if(!_gbc&&GBAR.naturalWidth){_gbc=mk(GBAR.naturalWidth,GBAR.naturalHeight);_gbc.getContext('2d').drawImage(GBAR,0,0);}return _gbc;}
function tunnelUpdate(dt){''')
# drawing: turret has its own draw, the hopper squashes and stretches
rep("  if(e.carry&&!e.dead&&CARRIER.img.complete&&CARRIER.img.naturalWidth){drawCarrier(e);return;}",
    "  if(e.carry&&!e.dead&&CARRIER.img.complete&&CARRIER.img.naturalWidth){drawCarrier(e);return;}\n  if(e.type==='gturret'&&ART.gturret.n){drawGTurret(e);return;}")
rep("ctx.save();ctx.translate(e.x,e.y);if(e.rot)ctx.rotate(e.rot);if(e.sc)ctx.scale(e.sc,e.sc);if(e.flipY)ctx.scale(1,-1);",
    "ctx.save();ctx.translate(e.x,e.y);if(e.rot)ctx.rotate(e.rot);if(e.sc)ctx.scale(e.sc,e.sc);if(e.sqy)ctx.translate(0,(1-e.sqy)*ART[e.type].dh/2),ctx.scale(2-e.sqy,e.sqy);if(e.flipY)ctx.scale(1,-1);")
# glows: charger exhaust and nose warning, turret muzzle warning, mine arming
rep("    if(e.type==='mine'&&e.fuse<0.8){",
    "    if(e.type==='charger'){const f=e.st==='dash'?14+Math.random()*6:5+Math.random()*2;ctx.globalAlpha=0.8;ctx.drawImage(glow(C.ember),e.x+21,e.y-f/2,f*2.2,f);\n"
    "      if(e.st==='tell'){const r=8+6*Math.abs(Math.sin(G.t*30));ctx.globalAlpha=0.9;ctx.drawImage(glow('#ffb43d'),e.x-23-r,e.y-r,r*2,r*2);}ctx.globalAlpha=1;}\n"
    "    if(e.type==='gturret'&&e.tellT>0&&!e.dying){for(const q of gtMuzzles(e)){const r=4+14*e.tellT;ctx.globalAlpha=0.5+e.tellT;ctx.drawImage(glow('#ffb43d'),q[0]-r,q[1]-r,r*2,r*2);}ctx.globalAlpha=1;}\n"
    "    if(e.type==='smine'&&e.arm!==undefined){const rr=7+4*Math.abs(Math.sin(e.t*30));ctx.globalAlpha=0.45;ctx.drawImage(glow('#ffb43d'),e.x-rr,e.y-rr,rr*2,rr*2);ctx.globalAlpha=1;}\n"
    "    if(e.type==='mine'&&e.fuse<0.8){")
# ---------- stage 1 running order ----------
rep("function s1Waves(dt,T){",
r'''// Stage 1 running order: each entry is [music time, wave]. One new kind of enemy at a time; never a crowd.
// noMini: skipped if the Warden is still alive when its time comes. Entries more than 1.5 s late are dropped (after the tunnel).
const S1W_=()=>{const d=diff(),gx=k=>s1Ground(W+20+k);
  const spin=(n,y,gate)=>{for(let i=0;i<n;i++)E('spinner',W+24+i*22,y,{y0:y,ph:i*0.9,R:24,w:3.2,spd:75,gate:!!gate});},
    hop=(n)=>{for(let i=0;i<n;i++)E('hopper',gx(i*44),H-40,{ct:0.35+i*0.4});},
    tur=(xs)=>{for(const x of xs){const X=gx(x);E('gturret',X,H-30,{ang:GT.a0,fireT:1.6+x*0.004});}},
    mines=(ys,gate)=>ys.forEach((y,i)=>E('smine',W+20+i*34,y,{baseY:y,ph:i*1.3,spd:30,gate:!!gate})),
    chg=(y)=>E('charger',W+30,y,{st:'in',tx:W-64}),
    line=(n,y,amp)=>{for(let i=0;i<n;i++)E('drone',W+20+i*26,y,{baseY:y,amp,freq:2.6,phase:i*0.6,spd:75+10*d});},
    vee=(y)=>{for(let i=0;i<5;i++){const o=i-2;E('drone',W+20+Math.abs(o)*20,y+o*18,{baseY:y+o*18,amp:6,freq:2,phase:0,spd:80+10*d});}},
    sw=(n)=>{const y=gateC(G.scroll+W+10)||H/2;for(let i=0;i<n;i++)E('swarm',W+10+i*16,y,{baseY:y,amp:8,freq:3,phase:-i*0.35,spd:115,tfollow:true});},
    gun=(ys)=>ys.forEach((y,i)=>E('gunner',W+20+i*30,y,{stopX:380-i*40,spd:90,hold:4.5,leaving:false})),
    heavy=(y)=>E('heavy',W+30,y,{spd:22,baseY:y});
  return [
    [31.5,()=>spin(3,100)],[34.5,()=>line(4,175,18)],[37.5,()=>hop(2)],
    [49,()=>vee(120),1],[53,()=>spin(4,80),1],[56.5,()=>chg(150),1],
    [61.5,()=>sw(4)],[64.5,()=>tur([0])],[68,()=>spin(4,135,true)],[71.5,()=>mines([110,165],true)],[75,()=>tur([0,70])],
    [78,()=>sw(4)],[81.5,()=>gun([100])],[87,()=>hop(2)],
    [139.5,()=>spin(4,90)],[143,()=>chg(110)],[147,()=>heavy(130)],[150.5,()=>mines([70,140,205])],[153,()=>gun([80,180])]];};
function s1Ground(x){   // a spot on the ground clear of the gate towers
  for(let k=0;k<6;k++){const X=x+G.scroll;if(!GATE.list.some(g=>Math.abs(g.X-X)<GATE_HW+22))return x;x+=48;}return x;}
function s1Script(T){if(!G.s1W)G.s1W=S1W_();if(G.s1wI===undefined)G.s1wI=0;
  while(G.s1wI<G.s1W.length&&T>=G.s1W[G.s1wI][0]){const w=G.s1W[G.s1wI++];
    if(T-w[0]>1.5)continue;if(w[2]&&G.mini&&!G.mini.dead)continue;if(G.state==='play')w[1]();}}
function s1Waves(dt,T){''')
rep("    s1Waves(dt,T);return true;}\n  if(T<S1.RING){if(G.mini&&!G.mini.dead&&!G.mini.leaving)G.mini.leaving=true;gateTick(dt,T);return true;}",
    "    s1Script(T);return true;}\n  if(T<S1.RING){if(G.mini&&!G.mini.dead&&!G.mini.leaving)G.mini.leaving=true;gateTick(dt,T);s1Script(T);return true;}")
rep("  if(!G.s1Haz&&!TUN.on&&T>=S1.FULL+30){G.s1Haz=true;startHazard();}\n  s1Waves(dt,T);return true;}",
    "  if(!G.s1Haz&&!TUN.on&&T>=S1.FULL+30){G.s1Haz=true;startHazard();}\n  s1Script(T);return true;}")
# gates no longer stream swarms on their own: the running order sends them
rep("GATE.swT-=dt;if(GATE.swT<=0&&T<S1.RING-5&&G.state==='play'){","GATE.swT-=dt;if(!s1On()&&GATE.swT<=0&&T<S1.RING-5&&G.state==='play'){")
# reset / seek
rep("function s1Reset(){G.s1c=0;","function s1Reset(){G.s1W=null;G.s1wI=0;G.s1c=0;")
rep("function s1Seek(t){s1Reset();G.stageT=t-S1.DROP;","function s1Seek(t){s1Reset();G.s1W=S1W_();G.s1wI=G.s1W.findIndex(w=>w[0]>=t);if(G.s1wI<0)G.s1wI=G.s1W.length;G.stageT=t-S1.DROP;")
# ---------- Dreadnought: walkers only where the hull is ----------
rep("  if(G.stage!==5&&G.stageT>6&&Math.random()<0.2&&enemies.filter(e=>e.type.startsWith('walker')).length<4){",
    "  if(G.stage!==5&&!(G.stage===4&&!(BS.on&&hullTop(W+20)<H&&hullTop(W+150)<H))&&G.stageT>6&&Math.random()<0.2&&enemies.filter(e=>e.type.startsWith('walker')).length<4){")
rep("function keepInGap(){",
    "function walkersOffHull(){if(G.stage!==4||G.state!=='play')return;for(const e of enemies){if(e.dead||e.dying||!e.type.startsWith('walker')||e.ceilW)continue;\n"
    "  if(!(BS.on&&hullTop(e.x)<H)){e.fall=(e.fall||0)+dt60();e.y+=e.fall*2;e.rot=(e.rot||0)+0.05;if(e.y>H+40)e.dead=true;}}}\n"
    "function dt60(){return 1;}\n"
    "function keepInGap(){walkersOffHull();")
# ---------- Mothership eased while your power is low ----------
rep("  e.f1-=dt*DF.fire;e.f2-=dt*DF.fire;e.f3-=dt*DF.fire;\n  const sp=1+(G.stage-1)*0.15,B=ART.boss,",
    "  const lowP=G.power<=2?0.75:1;   // at power 1-2 it attacks a quarter less often\n  e.f1-=dt*DF.fire*lowP;e.f2-=dt*DF.fire*lowP;e.f3-=dt*DF.fire*lowP;\n  const sp=1+(G.stage-1)*0.15,B=ART.boss,")
rep("e.lch=(e.lch===undefined?3.5:e.lch)-dt*DF.fire;if(e.lch<=0&&!e.tell&&G.state==='play'){e.lch=(ph===2?4.6:ph===1?5.4:6.4)/sp;msLaunch(e);}\n  msTurretFire(e,dt,ph,sp);",
    "e.lch=(e.lch===undefined?3.5:e.lch)-dt*DF.fire*lowP;if(e.lch<=0&&!e.tell&&G.state==='play'){e.lch=(ph===2?4.6:ph===1?5.4:6.4)/sp;msLaunch(e);}\n  msTurretFire(e,dt*lowP,ph,sp);")
rep("ty==='hpod'||ty==='serpg'||ty==='ring')continue;","ty==='hpod'||ty==='serpg'||ty==='ring'||ty==='hopper'||ty==='gturret')continue;")
rep("const GAME_VERSION='2.5';","const GAME_VERSION='2.7';")
open(P,'w').write(s);print('OK')
