"""New stage 1: a fixed running order locked to E Minor Assault (music/stage1-assault.mp3).
Sections (track time): drums in 28.3 = play starts -> waves + the Warden -> 60.0 gate pillars -> 91.0 the ring (breakdown)
-> 111.15 full power: tunnel, then the hardest waves and a meteor shower -> 155.76 ending: Warning -> 168.0 the Mothership arrives on the final hit.
Each replacement must match the expected number of times or nothing is written."""
import sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1]
src = open(path, encoding='utf-8').read()
ART = json.load(open(os.path.join(HERE, 'art.json')))

def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f'FAIL ({n}x, wanted {count}x): {old[:110]}')
    src = src.replace(old, new)

# ---------------- music ----------------
rep("""const MUSIC={
  stage:{src:'music/stage.mp3',ls:66.363,le:135.861,buf:null},""",
"""const MUSIC={
  // Stage 1: E Minor Assault (game edit). Play starts on the drums at 28.30; the stage is timed to this track (see S1)
  stage1:{src:'music/stage1-assault.mp3',ls:111.154,le:176.0,drop:28.30,beat:0.394737,anchor:28.31,buf:null},
  stage:{src:'music/stage.mp3',ls:66.363,le:135.861,buf:null},   // Pixel Blaster, the original stage 1 music (Jukebox)""")
rep("""const order=['title','stage','boss','boss1',""", """const order=['title','stage1','boss','boss1',""")
rep("""'stage5','ending'];let chain=Promise.resolve();""", """'stage5','ending','stage'];let chain=Promise.resolve();""")
rep("""function stageTrack(n){const k=n===4?'stage4':n===5?'stage5':['stage','stage2','stage3'][(n-1)%3];return MUSIC[k]?k:'stage';}""",
    """function stageTrack(n){const k=n===1?'stage1':n===4?'stage4':n===5?'stage5':['stage','stage2','stage3'][(n-1)%3];return MUSIC[k]?k:'stage';}""")
rep("""{k:'stage',n:'Pixel Blaster (stage 1)'}""", """{k:'stage1',n:'E Minor Assault (stage 1)'},{k:'stage',n:'Pixel Blaster (old stage 1)'}""")
# new game / intro use the new track (the hyperspace jump lands on its drums)
rep("""  if(A.ctx){stopMusic(0.2);}M.pos={};playMusic('stage',0,0.05);
}""", """  if(A.ctx){stopMusic(0.2);}M.pos={};playMusic('stage1',MUSIC.stage1.drop-0.05,0.05);
}""")
rep("""const DROP=19.07,SHORT_START=12.76,VPX=240,VPY=92;   // drop time in Pixel Blaster; short intro = 4 bars before it""",
    """const DROP=MUSIC.stage1.drop,SHORT_START=DROP-6.316,FULL_START=DROP-19.07,VPX=240,VPY=92;   // the drums coming in, in E Minor Assault; short intro = 4 bars before; full intro = same length as before""")
rep("""G.introStart=OPT.intro==='full'?0:OPT.intro==='short'?SHORT_START:(introCount++===0?0:SHORT_START);""",
    """G.introStart=OPT.intro==='full'?FULL_START:OPT.intro==='short'?SHORT_START:(introCount++===0?FULL_START:SHORT_START);""")
rep("""  if(A.ctx){stopMusic(0.2);}M.pos={};playMusic('stage',G.introStart,0.3);
  introEngine(DROP-G.introStart);""", """  if(A.ctx){stopMusic(0.2);}M.pos={};playMusic('stage1',G.introStart,0.3);
  introEngine(DROP-G.introStart);""")
rep("""const waiting=A.ctx&&MUSIC.stage&&!MUSIC.stage.buf&&G.introWall<3;""", """const waiting=A.ctx&&MUSIC.stage1&&!MUSIC.stage1.buf&&G.introWall<3;""")
rep("""G.introClock=Math.max(G.introClock,(M.name==='stage'&&M.node)?Math.max(trackPos(),game-0.5):game);""",
    """G.introClock=Math.max(G.introClock,(M.name==='stage1'&&M.node)?Math.max(trackPos(),game-0.5):game);""")
rep("""  if(skipped){if(A.ctx)stopMusic(0.05);playMusic('stage',DROP-0.02,0.05);}""", """  if(skipped){if(A.ctx)stopMusic(0.05);playMusic('stage1',DROP-0.02,0.05);}""")

# ---------------- the running order ----------------
S1 = r"""
/* ---------- Stage 1 running order, locked to E Minor Assault ----------
   T = position in the track (the game clock stands in if the music isn't playing). Play starts on the drums (DROP).
   main theme: waves, the Warden 8 bars in -> gate pillars -> breakdown: the ring -> full power: tunnel, then the hardest waves
   and a meteor shower -> ending: Warning, and the Mothership arrives on the final hit (its own music starts at its drop). */
const S1={DROP:28.30,CALM:3.0,WARDEN:28.30+12.63,GATE:60.0,RING:91.0,FULL:111.154,END:155.76,HIT:168.0};
function s1On(){return G.stage===1&&!!MUSIC.stage1;}
function s1Clock(){
  const g=S1.DROP+G.stageT;let c=g;
  if(M.name==='stage1'&&M.node){const p=trackPos();if(p>=(G.s1c||0)-2)c=Math.max(p,g-1.0);}   // follow the music, never more than 1 s behind the game
  return G.s1c=Math.max(G.s1c||0,c);}
function s1Reset(){G.s1c=0;G.s1Pre=false;G.s1BossMus=false;G.s1Tun=false;G.s1Haz=false;gateReset();RING.e=null;RING.debris.length=0;}
function s1Seek(t){s1Reset();G.stageT=t-S1.DROP;G.miniDone=true;if(A.ctx)stopMusic(0.1);playMusic('stage1',t,0.1);}   // cheat key: jump along the track
function s1Waves(dt,T){
  if(T<S1.DROP+S1.CALM)return;   // a calm moment after the jump
  {const busy=enemies.some(e=>!e.dead&&!e.dying&&e.x>-10&&e.x<W+10&&e.fx!=='rock'&&e.fx!=='crys');G.emptyT=busy?0:(G.emptyT||0)+dt;
   if(G.emptyT>0.5){G.emptyT=0;G.spawnT=0;}}
  if(introTick(dt))return;
  G.spawnT-=dt;if(G.spawnT<=0){introWave();G.spawnT*=DF.spawn*(T>=S1.FULL?0.8:1);}}
function s1Tick(dt){
  const T=s1Clock();
  if(T>=S1.END){   // the ending: waves stop, Warning, the Mothership arrives on the final hit
    G.pre=true;G.s1Pre=true;G.preT=0;G.preClock=0;G.warned=false;G.s1BossMus=false;
    if(G.mini&&!G.mini.dead)G.mini.leaving=true;if(RING.e&&!RING.e.dead)RING.e.st='out';return true;}
  hazardTick(dt);
  if(T<S1.GATE){
    if(!G.miniDone&&T>=S1.WARDEN)spawnMini();
    if(G.mini&&!G.mini.dead){G.escT=(G.escT===undefined?3:G.escT)-dt;if(G.escT<=0){G.escT=rnd(4,5.5);const f=faction(),y=rnd(50,H-90);for(let i=0;i<5;i++)fxE('snake',f,'small',1.5,120,W+8+i*16,y,{baseY:y,ph:-i*0.45,fac:f});}return true;}
    s1Waves(dt,T);return true;}
  if(T<S1.RING){if(G.mini&&!G.mini.dead&&!G.mini.leaving)G.mini.leaving=true;gateTick(dt,T);return true;}
  if(T<S1.FULL){if(!RING.e&&!G.s1Ring){G.s1Ring=true;ringSpawn();}return true;}
  if(!G.s1Tun){G.s1Tun=true;if(RING.e&&!RING.e.dead)RING.e.st='out';tunStart();}
  if(TUN.on&&G.scroll+W>TUN.X0-60&&G.scroll+W<TUN.X1+30)return true;   // the tunnel runs its own waves
  if(TUN.on&&!TUN.exitSeen&&G.scroll+W>=TUN.X1+30){TUN.exitSeen=true;G.spawnT=Math.min(G.spawnT,0.3);}
  if(!G.s1Haz&&!TUN.on&&T>=S1.FULL+30){G.s1Haz=true;startHazard();}
  s1Waves(dt,T);return true;}

/* ---------- gate pillars: alien columns from the ceiling and floor, leaving a gap to fly through ---------- */
const PIL={ceil:new Image(),floor:new Image()};PIL.ceil.src='""" + ART['ceil'] + """';PIL.floor.src='""" + ART['floor'] + r"""';
const GATE={on:false,list:[],i:0,nextX:0,swT:0},GATE_W=56,GATE_HW=GATE_W*0.36;
const GATE_PLAN=[135,135,112,158,96,172,124,150,92,138,176,118];   // gap centres: open first, then weaving up and down
function gateReset(){GATE.on=false;GATE.list.length=0;GATE.i=0;}
function gateGap(){return {easy:104,medium:86,hard:74}[OPT.diff]||86;}
function gateTick(dt,T){
  if(!GATE.on){GATE.on=true;GATE.i=0;GATE.nextX=G.scroll+W+40;GATE.swT=1.6;}
  while(GATE.nextX<G.scroll+W+60&&T<S1.RING-7&&GATE.i<GATE_PLAN.length){const c=GATE_PLAN[GATE.i],gap=gateGap()*(GATE.i<2?1.3:1);
    GATE.list.push({X:GATE.nextX,c,top:c-gap/2,bot:c+gap/2});GATE.i++;GATE.nextX+=150;}
  // small flyers threading the gaps
  GATE.swT-=dt;if(GATE.swT<=0&&T<S1.RING-5&&G.state==='play'){GATE.swT=rnd(2.6,3.4)*DF.spawn;const y=gateC(G.scroll+W+10)||H/2;
    if(Math.random()<0.6)for(let i=0;i<6;i++)E('swarm',W+10+i*16,y,{baseY:y,amp:8,freq:3,phase:-i*0.35,spd:115,tfollow:true});
    else for(let i=0;i<4;i++)E('drone',W+20+i*24,y,{baseY:y,amp:6,freq:2.5,phase:i*0.6,spd:85,tfollow:true});}
}
function gateUpdate(){for(let i=GATE.list.length-1;i>=0;i--)if(GATE.list[i].X<G.scroll-80)GATE.list.splice(i,1);if(!GATE.list.length&&GATE.on&&!(s1On()&&s1Clock()<S1.RING))GATE.on=false;}
// gap centre at world position X, blended between the gate just passed and the next one, so flyers steer through
function gateC(X){let L=null,R=null;for(const g of GATE.list){if(g.X<=X){if(!L||g.X>L.X)L=g;}else if(!R||g.X<R.X)R=g;}
  if(L&&R)return R.c+(L.c-R.c)*((R.X-X)/(R.X-L.X));return L?L.c:R?R.c:null;}
// a solid pillar at screen point (x,y)?
function gateHit(x,y,pad){for(const g of GATE.list){const gx=g.X-G.scroll;if(Math.abs(x-gx)<GATE_HW+(pad||0)&&(y<g.top||y>g.bot))return g;}return null;}
function gatePlayer(){
  if(!GATE.list.length||!pl.alive||G.state!=='play')return;
  for(const g of GATE.list){const gx=g.X-G.scroll,ox=GATE_HW+9-Math.abs(pl.x-gx);if(ox<=0)continue;
    const oy=pl.y-5<g.top?g.top-(pl.y-5):pl.y+5>g.bot?(pl.y+5)-g.bot:0;if(oy<=0)continue;
    if(oy<ox){pl.y+=pl.y-5<g.top?oy:-oy;}else pl.x+=pl.x<gx?-ox:ox;   // push out the shortest way
    pl.x=Math.max(8,pl.x);
    if(Math.random()<0.5)P(1,pl.x,pl.y,rnd(-150,-40),rnd(-80,80),0.2,1.6,0,C.gold,5);
    if(OPT.diff!=='easy'&&pl.inv<=0)playerDamage(25);}}
function drawPillar(img,x,tipY,top){
  if(!img.complete||!img.naturalWidth)return;const iw=img.naturalWidth,ih=img.naturalHeight,w=GATE_W,nat=w*ih/iw;
  if(top){const L=tipY+6;if(L<=nat){ctx.drawImage(img,x-w/2,tipY-nat,w,nat);return;}
    const s=ih*0.42,low=(ih-s)*w/iw;ctx.drawImage(img,0,s,iw,ih-s,x-w/2,tipY-low,w,low);ctx.drawImage(img,0,0,iw,s,x-w/2,-6,w,L-low+0.5);}   // stretch the upper shaft to reach the ceiling
  else{const L=H+6-tipY;if(L<=nat){ctx.drawImage(img,x-w/2,tipY,w,nat);return;}
    const s=ih*0.58,hi=s*w/iw;ctx.drawImage(img,0,0,iw,s,x-w/2,tipY,w,hi);ctx.drawImage(img,0,s,iw,ih-s,x-w/2,tipY+hi-0.5,w,L-hi+0.5);}}
function drawGates(){
  if(!GATE.list.length)return;ctx.save();ctx.imageSmoothingEnabled=true;
  for(const g of GATE.list){const x=g.X-G.scroll;if(x<-GATE_W||x>W+GATE_W)continue;drawPillar(PIL.ceil,x,g.top+4,true);drawPillar(PIL.floor,x,g.bot-4,false);
    ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.35+0.35*BEAT.pulse;   // claw tips glow on the beat
    ctx.drawImage(glow(C.ember),x-9,g.top-4,18,12);ctx.drawImage(glow(C.ember),x-9,g.bot-8,18,12);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';}
  ctx.restore();}

/* ---------- the ring: armoured pods close around you; one glowing pod, travelling round the ring, is the only weak point ---------- */
const POD={n:new Image(),w:new Image(),grey:null};POD.n.src='""" + ART['pod'] + """';POD.w.src='""" + ART['podw'] + r"""';
POD.n.onload=()=>{const c=mk(POD.n.width,POD.n.height),g=c.getContext('2d');g.filter='grayscale(0.85) brightness(0.55)';g.drawImage(POD.n,0,0);POD.grey=c;};
const RING={e:null,debris:[]},POD_R=10,POD_D=22;
ART.ring={dw:22,dh:22,cr:0,core:[0,0],gc:C.gold,pal:PAL_HOT};DEF.ring={hp:70,score:8000,pw:4,drop:1};
function ringSpawn(){const n=20;RING.e=E('ring',W+130,H/2,{cx:W+140,cy:H/2,R:94,n,rot:Math.PI*0.5,wk:3,wkT:0.5,gap:[0,1],st:'in',fireT:3});
  if(!sx('miniboss-arrive',1,0.8)){tone('square',330,330,0.2,0.05);}shake(0.2);}
function ringIn(e,i){return !e.gap.includes(i);}
function ringPod(e,i){const a=e.rot+i/e.n*TAU;return [e.cx+Math.cos(a)*e.R,e.cy+Math.sin(a)*e.R*0.9];}
function ringUpdate(e,dt){
  const rp=pl.alive?pl:{x:120,y:H/2};
  if(e.st==='in'){e.cx+=(330-e.cx)*Math.min(1,dt*1.1);if(e.cx<340)e.st='hunt';}
  else if(e.st==='hunt'){const tx=clamp(rp.x+30,140,W-110),ty=clamp(rp.y,96,H-100);   // drifts over you, so you end up inside
    e.cx+=clamp(tx-e.cx,-26*dt,26*dt);e.cy+=clamp(ty-e.cy,-20*dt,20*dt);e.R=Math.max(62,e.R-dt*1.7);}
  else if(e.st==='out'){e.cx+=170*dt;if(e.cx>W+160){e.dead=true;RING.e=null;}}
  e.rot+=dt*0.5;
  e.wkT-=dt;if(e.wkT<=0){e.wkT=0.45;do{e.wk=(e.wk+1)%e.n;}while(!ringIn(e,e.wk));}   // the weak point runs round the ring
  const [x,y]=ringPod(e,e.wk);e.x=x;e.y=y;e.hw=e.hh=POD_R;
  if(G.state==='play'&&e.st==='hunt'){e.fireT-=dt*DF.fire;e.tell=e.fireT<0.5;if(e.fireT<=0){e.fireT=1.9;aim(x,y,100+10*diff(),3,0.24,'#ffb347');P(0,x,y,0,0,0.12,10,4,'#ffb347');}}
  // touching the armour pushes you away and hurts
  if(pl.alive&&G.state==='play'&&e.st!=='out')for(let i=0;i<e.n;i++){if(!ringIn(e,i))continue;const [px,py]=ringPod(e,i),dx=pl.x-px,dy=pl.y-py,d=Math.hypot(dx,dy);
    if(d<POD_R+6){const k=(POD_R+7)/(d||1);pl.x=px+dx*k;pl.y=py+dy*k;pl.x=clamp(pl.x,8,W-8);pl.y=clamp(pl.y,10,H-10);
      if(Math.random()<0.5)P(1,pl.x,pl.y,rnd(-120,120),rnd(-120,120),0.2,1.5,0,C.gold,5);if(OPT.diff!=='easy'&&pl.inv<=0)playerDamage(25);}}}
// shots that hit any pod except the weak one bounce off the armour
function ringBlocks(b){const e=RING.e;if(!e||e.dead||e.dying)return false;
  for(let i=0;i<e.n;i++){if(i===e.wk||!ringIn(e,i))continue;const [x,y]=ringPod(e,i);if((b.x-x)**2+(b.y-y)**2<(POD_R+1)**2)return true;}return false;}
function ringDie(e){const pods=[];for(let i=0;i<e.n;i++)if(ringIn(e,i))pods.push(ringPod(e,i));RING.e=null;G.s1RingDone=true;FB.kick=1;shake(0.5);
  pods.forEach(([x,y],k)=>later(0.05*k,()=>{explode(x,y,1.6,pick([PAL_HOT,PAL_EN]));RING.debris.push({x,y,vx:rnd(-50,-20),vy:rnd(-20,20),rot:rnd(0,TAU),vr:rnd(-2,2),t:0});}));
  sx('armour-chip',1,0.8);}
function ringDebrisUpdate(dt){for(let i=RING.debris.length-1;i>=0;i--){const d=RING.debris[i];d.t+=dt;d.x+=d.vx*dt;d.y+=d.vy*dt;d.vy+=14*dt;d.rot+=d.vr*dt;if(d.t>5||d.x<-30||d.y>H+30)RING.debris.splice(i,1);}}
function drawRing(e){
  ctx.save();ctx.imageSmoothingEnabled=true;const t=G.t;
  for(let i=0;i<e.n;i++){if(!ringIn(e,i)||i===e.wk)continue;const [x,y]=ringPod(e,i);if(POD.n.complete)ctx.drawImage(POD.n,x-POD_D/2,y-POD_D/2,POD_D,POD_D);}
  const [x,y]=ringPod(e,e.wk),pu=0.5+0.5*Math.sin(t*14);
  ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.45+0.35*pu+(e.tell?0.3:0);const r=14+4*pu+(e.tell?6:0);ctx.drawImage(glow(C.gold),x-r,y-r,r*2,r*2);
  ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';
  if(POD.w.complete)ctx.drawImage(POD.w,x-POD_D/2,y-POD_D/2,POD_D,POD_D);
  if(e.flash>0){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.8;ctx.drawImage(glow(C.white),x-12,y-12,24,24);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';}
  ctx.restore();}
function drawRingDebris(){if(!RING.debris.length||!POD.grey)return;ctx.save();ctx.imageSmoothingEnabled=true;
  for(const d of RING.debris){ctx.globalAlpha=Math.min(1,(5-d.t)/1.5);ctx.save();ctx.translate(d.x,d.y);ctx.rotate(d.rot);ctx.drawImage(POD.grey,-POD_D/2,-POD_D/2,POD_D,POD_D);ctx.restore();}
  ctx.restore();}
"""
rep("""function director(dt){""", S1 + """function director(dt){""")
rep("""  if(G.stage===5&&finalTick(dt))return;
  if(G.stageT>=BOSS_AT&&!(G.mini&&!G.mini.dead)){""", """  if(G.stage===5&&finalTick(dt))return;
  if(s1On()&&s1Tick(dt))return;
  if(G.stageT>=BOSS_AT&&!(G.mini&&!G.mini.dead)){""")
# reset with the tunnel (new game, every stage change)
rep("""function tunReset(){TUN.on=false;TUN.done=false;}""", """function tunReset(){TUN.on=false;TUN.done=false;if(typeof s1Reset==='function'){s1Reset();G.s1Ring=false;G.s1RingDone=false;}}""")

# boss arrival on the music's final hit
rep("""  G.preClock=Math.max(G.preClock,(isBossTrack(M.name)&&M.node)?Math.max(trackPos(),G.preT-0.5):G.preT);
  const c=G.preClock;
  if(!G.warned&&c>=BOSS_DROP-WARN_AT){""", """  if(G.s1Pre){G.preClock=Math.max(G.preClock,BOSS_DROP-(S1.HIT-s1Clock()));   // stage 1: the stage track's ending is the warning
    if(!G.s1BossMus&&G.preClock>=BOSS_DROP-0.03){G.s1BossMus=true;playMusic(bossTrack(),BOSS_DROP,0.05,0.3);}}   // boss music starts at its drop, on the hit
  else G.preClock=Math.max(G.preClock,(isBossTrack(M.name)&&M.node)?Math.max(trackPos(),G.preT-0.5):G.preT);
  const c=G.preClock,ENT=G.s1Pre?6:ENTRY;
  if(!G.warned&&c>=BOSS_DROP-(G.s1Pre?S1.HIT-S1.END-0.2:WARN_AT)){""")
rep("""G.warned=true;banner('Warning',3);""", """G.warned=true;banner('Warning',G.s1Pre?6.4:3);""")   # stage 1: stays up until the Mothership starts coming in
rep("""  if(!G.boss&&c>=BOSS_DROP-(G.stage===5?TBUILD:ENTRY)){""", """  if(!G.boss&&c>=BOSS_DROP-(G.stage===5?TBUILD:ENT)){""")
rep("""    const dur=b.type==='titan'?TBUILD:ENTRY,k=clamp((c-(BOSS_DROP-dur))/dur,0,1);""", """    const dur=b.type==='titan'?TBUILD:ENT,k=clamp((c-(BOSS_DROP-dur))/dur,0,1);""")
rep("""    if(k>=1){b.entering=false;b.t=0;G.pre=false;bossRoar(b);}""", """    if(k>=1){b.entering=false;b.t=0;G.pre=false;if(G.s1Pre&&!G.s1BossMus){G.s1BossMus=true;playMusic(bossTrack(),BOSS_DROP,0.05,0.3);}G.s1Pre=false;bossRoar(b);}""")

# cheat skip keys: jump along the track in stage 1
rep("""else if(!G.boss&&!G.pre&&!(G.clearT>0))G.stageT=BOSS_AT;return;}""", """else if(!G.boss&&!G.pre&&!(G.clearT>0)){if(s1On())s1Seek(S1.END-1);else G.stageT=BOSS_AT;}return;}""", 2)

# ---------------- hooks: update, collisions, drawing ----------------
rep("""  if(G.state==='play'||G.state==='over')tunnelUpdate(dt);""", """  if(G.state==='play'||G.state==='over')tunnelUpdate(dt);
  if(G.state==='play'||G.state==='over'){gateUpdate();ringDebrisUpdate(dt);}""")
rep("""        if(e.tfollow){const t=tunAt(e.x+G.scroll);if(t)e.baseY+=(t.c-e.baseY)*Math.min(1,dt*4);}""",
    """        if(e.tfollow){const t=tunAt(e.x+G.scroll),gc=t?null:gateC(e.x+G.scroll);if(t)e.baseY+=(t.c-e.baseY)*Math.min(1,dt*4);else if(gc!==null)e.baseY+=(gc-e.baseY)*Math.min(1,dt*3);}""")
rep("""      case 'ms_turret':""", """      case 'ring':ringUpdate(e,dt);break;
      case 'ms_turret':""")
rep("""  if(e.type==='ms_turret'&&e.host){""", """  if(e.type==='ring')ringDie(e);
  if(e.type==='ms_turret'&&e.host){""")
rep("""  if(e.type==='ms_turret')return;""", """  if(e.type==='ms_turret')return;
  if(e.type==='ring'){drawRing(e);return;}""")
rep("""  drawTunnel();
  drawHull();drawPresses();""", """  drawTunnel();drawGates();drawRingDebris();
  drawHull();drawPresses();""")
# player against pillars (next to the tunnel wall check)
rep("""  const shards=G.boss?queenShards(G.boss):[];""", """  gatePlayer();
  const shards=G.boss?queenShards(G.boss):[];""")
# player shots: armour pods and pillars stop them
rep("""    if(blocked){b.dead=true;for(let i=0;i<3;i++)P(1,b.x,b.y,rnd(-200,-60),rnd(-120,120),0.18,1.5,0,'#ff3dd5',5);sfx.tick();continue;}""",
    """    if(blocked){b.dead=true;for(let i=0;i<3;i++)P(1,b.x,b.y,rnd(-200,-60),rnd(-120,120),0.18,1.5,0,'#ff3dd5',5);sfx.tick();continue;}
    if(RING.e&&b.k!=='beam'&&ringBlocks(b)){b.dead=true;for(let i=0;i<3;i++)P(1,b.x,b.y,rnd(-200,-60),rnd(-120,120),0.18,1.5,0,C.gold,5);continue;}""")
rep("""    if(TUN.on&&!b.dead){const t=tunAt(b.x+G.scroll);if(t&&(b.y<t.ceil||b.y>t.floor)){b.dead=true;if(b.k==='drop')dropBoom(b.x,b.y);else P(1,b.x,b.y,rnd(-120,-40),rnd(-60,60),0.15,1.4,0,C.gold,6);}}""",
    """    if(TUN.on&&!b.dead){const t=tunAt(b.x+G.scroll);if(t&&(b.y<t.ceil||b.y>t.floor)){b.dead=true;if(b.k==='drop')dropBoom(b.x,b.y);else P(1,b.x,b.y,rnd(-120,-40),rnd(-60,60),0.15,1.4,0,C.gold,6);}}
    if(GATE.list.length&&!b.dead&&gateHit(b.x,b.y)){b.dead=true;if(b.k==='drop')dropBoom(b.x,b.y);else P(1,b.x,b.y,rnd(-120,-40),rnd(-60,60),0.15,1.4,0,C.gold,6);}""")
rep("""    if(TUN.on&&!b.dead){const t=tunAt(b.x+G.scroll);if(t&&t.r>0.5&&(b.y<t.ceil-2||b.y>t.floor+2)){b.dead=true;P(0,b.x,b.y,0,0,0.12,4,1,b.col||C.hot);}}}""",
    """    if(TUN.on&&!b.dead){const t=tunAt(b.x+G.scroll);if(t&&t.r>0.5&&(b.y<t.ceil-2||b.y>t.floor+2)){b.dead=true;P(0,b.x,b.y,0,0,0.12,4,1,b.col||C.hot);}}
    if(GATE.list.length&&!b.dead&&gateHit(b.x,b.y,-2)){b.dead=true;P(0,b.x,b.y,0,0,0.12,4,1,b.col||C.hot);}}""")
rep("""    if(TUN.on){const t=tunAt(p.x+G.scroll);if(t)p.y=clamp(p.y,t.ceil+10,t.floor-10);}""",
    """    if(TUN.on){const t=tunAt(p.x+G.scroll);if(t)p.y=clamp(p.y,t.ceil+10,t.floor-10);}
    {const g=gateHit(p.x,p.y,6);if(g)p.y=clamp(p.y,g.top+10,g.bot-10);}""")

open(path, 'w', encoding='utf-8').write(src)
print('OK')
