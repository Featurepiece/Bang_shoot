# v3.5: Dreadnought rework. The boss is now the ship's main gun: it rises from the deck, tracks you, locks on and fires a beam;
# hide behind armoured deck blocks; its coils are a weak point while it charges. The bridge stays as scenery and keeps firing
# (half damage). When the gun dies the Dreadnought tries to escape: shoot the bridge to break the ship apart before it gets away.
# Damage dealt during the escape pays a bonus; destroying the ship pays a bigger one.
import sys,json,os
P=sys.argv[1] if len(sys.argv)>1 else 'test.html'
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'art','stage4-dreadnought','main_gun_art.json')))
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:90]}')
    s=s.replace(a,b)

GUNJS=r'''
/* ---------- the main gun: the Dreadnought's boss. It rises out of the deck in front of the bridge ---------- */
const GUNI={base:new Image(),barrel:new Image(),block:new Image()};
GUNI.base.src='%BASE%';GUNI.barrel.src='%BARREL%';GUNI.block.src='%BLOCK%';
// sizes in game pixels; sock = barrel socket on the base picture; coil = glowing coils along the barrel (from the muzzle end);
// piv = how far along the barrel (from the muzzle) it pivots; the gun sits 100 px in front of the bridge, two cover blocks further forward
const GUN={dw:112,dh:112*%BH%/%BW%,sock:[%SX%,%SY%],bw:70,bh:70*%RH%/%RW%,coil:[%C0%,%C1%],piv:0.9,get SX(){return BRIDGE_SX-100;},get BLOCKS(){return [BRIDGE_SX-300,BRIDGE_SX-225];},bkW:28,bkH:27,lock:0.5};
const ESC={hp:180,acc:7.3};   // escape: damage needed to break the ship apart; how fast it pulls away (px/s per second)
ART.bs_gun={dw:GUN.dw,dh:GUN.dh,cr:8,core:[0,-6],gc:'#ff7a3d',pal:[C.white,'#ff7a3d',C.ember]};
GUNI.base.onload=()=>{const c=toCanvas(GUNI.base);ART.bs_gun.n=c;ART.bs_gun.w=whiteOf(c);};
DEF.bs_gun={hp:300,score:60000,boss:true};
function gunDeck(e){return hullTopSX(e.sx);}
function gunTop(e){return gunDeck(e)+4-GUN.dh*(e.rise||0);}
function gunPivot(e){return [e.x-GUN.dw/2+GUN.sock[0]*GUN.dw,gunTop(e)+GUN.sock[1]*GUN.dh];}
function gunMuzzle(e){const p=gunPivot(e),l=GUN.piv*GUN.bw;return [p[0]-Math.cos(e.el)*l,p[1]-Math.sin(e.el)*l];}
function segDist(px,py,ax,ay,bx,by){const dx=bx-ax,dy=by-ay,l=dx*dx+dy*dy||1,t=clamp(((px-ax)*dx+(py-ay)*dy)/l,0,1);return Math.hypot(px-ax-dx*t,py-ay-dy*t);}
function blockTopSX(sx){if(!DN.blocks)return H+50;for(const b of DN.blocks)if(!b.dead&&Math.abs(sx-b.sx)<GUN.bkW/2)return hullTopSX(b.sx)+2-GUN.bkH;return H+50;}
function gunTopSX(sx){const g=DN.gun;if(!g||g.dead||(g.rise||0)<0.4)return H+50;return Math.abs(sx-g.sx)<GUN.dw*0.44?gunTop(g)+7:H+50;}
// the beam: from the muzzle until it meets a cover block, the deck or the edge of the screen
function gunRay(x,y,dx,dy){for(let d=4;d<720;d+=3){const qx=x+dx*d,qy=y+dy*d;if(qx<-30||qy<-30||qx>W+30)return [qx,qy,null];const sx=qx-BS.x0;
    if(DN.blocks)for(const b of DN.blocks)if(!b.dead&&Math.abs(sx-b.sx)<GUN.bkW/2&&qy>hullTopSX(b.sx)+2-GUN.bkH)return [qx,qy,b];
    if(qy>hullTopSX(sx)-1)return [qx,qy,null];}
  return [x+dx*720,y+dy*720,null];}
function dnFightStart(){BS.fight=true;
  const g=E('bs_gun',BS.x0+GUN.SX,hullTopSX(GUN.SX),{sx:GUN.SX,rise:0,entering:true,el:0.15,st:'idle',stT:2,chg:1,flakT:2,hw:0,hh:0});
  DN.gun=g;G.boss=g;G.bossDropT=8;if(!sx('door-alarm',0.6,0.8))tone('sawtooth',90,60,1.2,0.05);rumble(0.6,0.4,2000,true);}
function gunUpdate(e,dt){e.x=BS.x0+e.sx;
  if((e.rise||0)<1&&!e.dying){e.rise=Math.min(1,(e.rise||0)+dt/2.4);e.entering=true;const deck=gunDeck(e);
    if(Math.random()<0.6)P(2,e.x+rnd(-GUN.dw/2,GUN.dw/2),deck-2,rnd(-20,20),-30,1.2,2,8,null,0.5);trauma=Math.max(trauma,0.12);
    if(e.rise>=1){e.entering=false;e.t=0;e.stT=1.6;bossRoar(e);}}
  e.y=gunTop(e)+GUN.dh/2;
  if(e.rise>=1||e.dying)updateBoss(e,dt);}
// track the player, charge (coils glow, aim locks for the last half second), fire; phase 2 sweeps, phase 3 fires twice and breaks cover
function gunAttack(e,dt){const ph=bossPhase(e),d=diff(),p=gunPivot(e);
  const tgt=pl.alive?clamp(Math.atan2(p[1]-pl.y,p[0]-pl.x),-0.3,1.2):0.15,turn=[0.55,0.7,0.85][ph]*dt;
  const locked=e.st==='fire'||(e.st==='charge'&&e.stT<GUN.lock);if(!locked)e.el+=clamp(tgt-e.el,-turn,turn);
  e.stT-=dt*DF.fire;
  if(e.st==='idle'){e.bEnd=null;
    if(ph>=1){e.flakT-=dt*DF.fire;if(e.flakT<=0){e.flakT=ph===2?1.7:2.2;const m=gunMuzzle(e);aim(m[0],m[1],115+10*d,3,0.22,'#ffb43d');P(0,m[0],m[1],0,0,0.1,9,3,'#ffe08a');if(!samp('blaster',0.35,0.6))tone('square',200,90,0.06,0.03);}}
    if(e.stT<=0){e.st='charge';e.stT=e.chg=e.n2?0.75:[1.5,1.4,1.1][ph];if(!sx('zap-charge',0.7,1))tone('sawtooth',120,900,e.chg,0.05);}}
  else if(e.st==='charge'){const m=gunMuzzle(e);e.bEnd=gunRay(m[0],m[1],-Math.cos(e.el),-Math.sin(e.el));
    if(e.stT<=0){e.st='fire';e.stT=e.dur=ph===1?1.1:0.8;e.bHit=false;e.bBlk=false;e.sw=ph===1?[e.el+0.4,e.el-0.4]:null;
      if(!sx('zap-fire',0.8,0.7))noiseHit(0.6,0.3,1800,200);shake(0.2);rumble(0.6,0.5,500,true);}}
  else if(e.st==='fire'){
    if(e.sw)e.el=clamp(e.sw[0]+(e.sw[1]-e.sw[0])*(1-e.stT/e.dur),-0.3,1.2);
    const m=gunMuzzle(e),r=gunRay(m[0],m[1],-Math.cos(e.el),-Math.sin(e.el));e.bEnd=r;
    if(Math.random()<0.8)P(1,r[0],r[1],rnd(-140,140),rnd(-180,-20),0.25,1.8,0,pick([C.gold,C.white,C.ember]),4);
    if(r[2]&&ph===2&&!e.bBlk){e.bBlk=true;const b=r[2];b.hp--;b.fl=0.25;explode(r[0],r[1],1.3,PAL_HOT,true);shake(0.15);
      if(b.hp<=0){b.dead=true;const bx=BS.x0+b.sx,by=hullTopSX(b.sx)-GUN.bkH/2;for(let i=0;i<4;i++)later(i*0.08,()=>explode(bx+rnd(-10,10),by+rnd(-10,10),1.6,pick([PAL_HOT,PAL_EN])));
        BS.scorch.push({sx:b.sx,y:hullTopSX(b.sx)+2,r:14});popup(bx-20,by-20,'Cover destroyed',C.hot);}}
    if(!e.bHit&&pl.alive&&segDist(pl.x,pl.y,m[0],m[1],r[0],r[1])<7){e.bHit=true;playerDamage(30);}
    if(e.stT<=0){e.bEnd=null;if(ph===2&&!e.n2){e.n2=true;e.st='idle';e.stT=0.35;}else{e.n2=false;e.st='idle';e.stT=[4.2,3.8,3.0][ph];}}}}
// player shots against the gun: the barrel takes full damage, the glowing coils (while charging) take 3x, the armoured base 0.35x
function gunHit(e,b){if(e.dead||e.dying||b.k==='drop'||(e.rise||0)<0.3)return false;
  const p=gunPivot(e),dx=-Math.cos(e.el),dy=-Math.sin(e.el),rx=b.x-p[0],ry=b.y-p[1],al=rx*dx+ry*dy,pe=Math.abs(rx*dy-ry*dx);let mult=0;
  if(pe<GUN.bh/2+4&&al>-(1-GUN.piv)*GUN.bw&&al<GUN.piv*GUN.bw){const t=GUN.piv*GUN.bw-al;mult=(e.st==='charge'&&t>GUN.coil[0]*GUN.bw-3&&t<GUN.coil[1]*GUN.bw+3)?3:1;}
  else if(Math.abs(b.x-e.x)<GUN.dw*0.46&&b.y>gunTop(e)+4&&b.y<gunDeck(e)+3)mult=0.35;
  if(!mult)return false;
  if(b.pierce){if(b.pierce.has(e))return false;b.pierce.add(e);}else b.dead=true;
  if(e.entering){armourClang();P(1,b.x,b.y,rnd(-220,-80),rnd(-140,140),0.16,1.4,0,C.gold,5);return !b.pierce;}
  if(mult<1)hitEnemy(e,b.dmg*mult,b.x,b.y,'armour');
  else{hitEnemy(e,b.dmg*mult,b.x,b.y,b.k);if(mult>1){P(0,b.x,b.y,0,0,0.14,12,4,C.white);for(let i=0;i<3;i++)P(1,b.x,b.y,rnd(-200,-40),rnd(-140,140),0.2,1.6,0,C.ember,5);}}
  return !b.pierce;}
function drawGun(e){const im=GUNI.base,bi=GUNI.barrel;if(!im.complete)return;const top=gunTop(e),deck=gunDeck(e),x0=e.x-GUN.dw/2;
  ctx.save();ctx.beginPath();ctx.rect(-60,-60,W+120,deck+4+60);ctx.clip();ctx.imageSmoothingEnabled=true;
  ctx.drawImage(im,x0,top,GUN.dw,GUN.dh);if(e.flash>0&&ART.bs_gun.w){ctx.globalAlpha=0.7;ctx.drawImage(ART.bs_gun.w,x0,top,GUN.dw,GUN.dh);ctx.globalAlpha=1;}
  const p=gunPivot(e);ctx.translate(p[0],p[1]);ctx.rotate(e.el);const bx=-GUN.piv*GUN.bw;if(bi.complete)ctx.drawImage(bi,bx,-GUN.bh/2,GUN.bw,GUN.bh);
  // the coils: a faint glow at rest, blazing while it charges (that's when they can be hurt)
  const ch=e.st==='charge'&&!e.dying?1-e.stT/e.chg:0,pul=0.5+0.5*Math.sin(G.t*(8+30*ch)),c0=bx+GUN.coil[0]*GUN.bw,cw=(GUN.coil[1]-GUN.coil[0])*GUN.bw;
  ctx.globalCompositeOperation='lighter';ctx.globalAlpha=ch>0?0.5+0.5*ch:0.15+0.1*pul;ctx.drawImage(glow(C.ember),c0-6,-GUN.bh*1.4,cw+12,GUN.bh*2.8);
  if(ch>0){ctx.globalAlpha=0.35+0.55*ch*pul;ctx.drawImage(glow(C.white),c0,-GUN.bh*0.8,cw,GUN.bh*1.6);}
  ctx.restore();
  if(e.hp<e.max*0.66&&Math.random()<(e.hp<e.max*0.33?0.5:0.25)*Q)P(2,e.x+rnd(-GUN.dw*0.4,GUN.dw*0.4),top+rnd(4,14),rnd(-10,10),-25,1.2,2,7,null,0.45);
  if(e.dying||!e.bEnd)return;const m=gunMuzzle(e),end=e.bEnd;
  ctx.save();ctx.globalCompositeOperation='lighter';ctx.lineCap='round';
  if(e.st==='charge'){const lock=e.stT<GUN.lock,k=1-e.stT/e.chg;   // aim line: dashed while tracking, solid red when locked
    ctx.globalAlpha=lock?0.55+0.4*Math.sin(G.t*40):0.2;ctx.strokeStyle='#ff3d3d';ctx.lineWidth=lock?1.5:1;ctx.setLineDash(lock?[]:[4,4]);
    ctx.beginPath();ctx.moveTo(m[0],m[1]);ctx.lineTo(end[0],end[1]);ctx.stroke();ctx.setLineDash([]);
    const r=4+12*k;ctx.globalAlpha=0.5+0.5*k;ctx.drawImage(glow(C.ember),m[0]-r,m[1]-r,r*2,r*2);}
  else if(e.st==='fire'){const f=0.8+0.2*Math.random();
    for(const [w,c,a] of [[15*f,C.ember,0.35],[7*f,C.gold,0.7],[2.5,C.white,0.95]]){ctx.globalAlpha=a;ctx.strokeStyle=c;ctx.lineWidth=w;ctx.beginPath();ctx.moveTo(m[0],m[1]);ctx.lineTo(end[0],end[1]);ctx.stroke();}
    ctx.globalAlpha=0.9;const r=16*f;ctx.drawImage(glow(C.gold),end[0]-r,end[1]-r,r*2,r*2);ctx.drawImage(glow(C.white),m[0]-9,m[1]-9,18,18);}
  ctx.restore();}
function drawBlocks(){if(!BS.on||!DN.blocks||!GUNI.block.complete)return;ctx.save();ctx.imageSmoothingEnabled=true;
  for(const b of DN.blocks){if(b.dead)continue;const x=BS.x0+b.sx;if(x<-40||x>W+40)continue;const y=hullTopSX(b.sx)+2-GUN.bkH;
    ctx.drawImage(GUNI.block,x-GUN.bkW/2,y,GUN.bkW,GUN.bkH);
    if(b.fl>0){b.fl-=fdt;ctx.globalCompositeOperation='lighter';ctx.globalAlpha=b.fl*3;ctx.drawImage(glow(C.gold),x-GUN.bkW/2,y,GUN.bkW,GUN.bkH);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';}
    if(b.hp<2&&Math.random()<0.15*Q)P(2,x+rnd(-8,8),y+2,-8,-22,1,2,6,null,0.4);}
  ctx.restore();}

/* ---------- the escape: when the gun dies the Dreadnought fires its engines and runs. Shoot the bridge to break it apart ---------- */
function dnEscapeStart(g){DN.gun=null;G.boss=null;DN.esc={t:0,v:0,dmg:0,max:ESC.hp*DF.hp,lv:0,dead:false,end:false,deadT:0,sink:0,sinkV:0,tilt:0};
  later(0.9,()=>{if(!DN.esc||DN.esc.end)return;banner('The Dreadnought is escaping!',3);if(!samp('alarm',0.5,1))sfx.alarm();rumble(0.8,0.6,1500,true);});
  later(4,()=>{if(DN.esc&&!DN.esc.end&&!DN.esc.dead)banner('Shoot the bridge!',2.4);});}
function dnEscapeTick(dt){const s=DN.esc;s.t+=dt;
  if(!s.dead){const f=Math.min(1,s.dmg/s.max);s.v=Math.min(170,s.v+ESC.acc*(1-0.45*f)*dt);BS.s+=s.v*dt;   // the more damage, the slower it gets away
    const b=BS.bridge;
    if(b&&!b.dead){if(Math.random()<(0.2+1.6*f)*Q)P(2,b.x+rnd(-50,50),b.y+rnd(-60,20),-30,-20,1.4,2,9,null,0.5);
      if(Math.random()<dt*(0.5+6*f))explode(b.x+rnd(-55,55),b.y+rnd(-65,55),rnd(0.5,1)+f,pick([PAL_EN,PAL_HOT]),true);
      while(f>=(s.lv+1)*0.25&&s.lv<3){s.lv++;   // a big piece breaks away at every quarter
        for(let i=0;i<4;i++)later(i*0.1,()=>{if(b.dead)return;const hx=b.x+rnd(-50,50),hy=b.y+rnd(-60,40);explode(hx,hy,2,pick([PAL_EN,PAL_HOT]));spawnFrag(b,hx,hy,true);});
        shake(0.35);trauma=Math.max(trauma,0.5);popup(b.x-40,b.y-70,['Hull breached','Bridge burning','Breaking up'][s.lv-1],C.hot);}}
    if(s.dmg>=s.max)dnEscapeDestroyed();
    else if(BS.x0+SHIPLEN<-30||s.t>32)dnEscapeEnd(false);}
  else{s.deadT+=dt;BS.s+=s.v*dt*Math.max(0,1-s.deadT/2);
    if(s.deadT>1.2){s.sinkV+=55*dt;s.sink+=s.sinkV*dt;s.tilt=Math.min(0.5,s.tilt+dt*0.13);}
    if(s.deadT<3.5&&Math.random()<dt*10)explode(rnd(0,W),190+s.sink+rnd(-10,40),rnd(1,2.5),pick([PAL_EN,PAL_HOT]),true);
    if(s.deadT>4.6)dnEscapeEnd(true);}}
function dnEscapeDestroyed(){const s=DN.esc;s.dead=true;s.deadT=0;banner('Dreadnought destroyed!',4);eb.length=0;
  const b=BS.bridge;if(b&&!b.dead){for(let i=0;i<14;i++)later(i*0.08,()=>{explode(b.x+rnd(-60,60),b.y+rnd(-70,60),rnd(1.5,3),pick([PAL_EN,PAL_HOT]),i%3!==0);if(i%2===0)spawnFrag(b,b.x+rnd(-50,50),b.y+rnd(-60,50),true);});later(1.15,()=>{b.dead=true;explode(b.x,b.y,5,b.pal);});}
  for(const q of enemies)if(!q.dead&&!q.dying&&q.type.startsWith('bs_')&&q!==b){explode(q.x,q.y,1.2,PAL_HOT,true);q.dead=true;}
  for(let i=0;i<20;i++)later(0.1*i,()=>{explode(rnd(0,W),185+rnd(-10,40),rnd(1.5,3),pick([PAL_EN,PAL_HOT]),i%3!==0);trauma=Math.max(trauma,0.5);});
  whiteFlash=0.6;flashCol='255,200,140';rumble(1,1,1500,true);FB.kick=2;}
function dnEscapeEnd(dest){const s=DN.esc;if(s.end)return;s.end=true;
  const f=Math.min(1,s.dmg/s.max),dmgB=Math.round(f*100000/100)*100,bon=dmgB+(dest?200000:0);G.score+=bon;
  if(!dest)banner('The Dreadnought escaped',2.6);
  later(dest?0:2.6,()=>{if(G.state!=='play')return;banner(dest?'Damage bonus '+dmgB+'   Destroyed +200000':'Damage bonus '+dmgB,2.8);
    later(2.8,()=>{if(G.state!=='play')return;if(G.practice)practiceDone();else{stageClearNow();later(0.6,()=>{if(!say('stageClear',3))sfx.clear();});}});});}
function escHit(b){const s=DN.esc;if(!s||s.dead||s.end||b.k==='drop')return false;const t=hullTop(b.x);if(t>=H||b.y<t-6)return false;
  if(b.pierce){if(b.pierce.has(BS))return false;b.pierce.add(BS);}else b.dead=true;
  const sx=b.x-BS.x0,br=Math.abs(sx-BRIDGE_SX)<BSM.bridge.w/2;s.dmg+=b.dmg*(br?1:0.6);
  P(1,b.x,b.y,rnd(-200,-60),rnd(-120,60),0.18,1.5,0,pick([C.gold,C.white,C.ember]),5);hitSound(b.k==='beam'?'pulse':b.k);
  const q=BS.bridge;if(br&&q&&!q.dead){q.flash=0.045;s.acc=(s.acc||0)+b.dmg;if(s.acc>3){s.acc=0;spawnFrag(q,b.x,b.y,false);}}
  return !b.pierce;}
function drawEscBar(){const s=DN.esc;if(!s||s.end||s.dead||G.state!=='play')return;const f=Math.max(0,1-s.dmg/s.max);
  ctx.fillStyle='rgba(255,61,110,.2)';ctx.fillRect(W/2-100,24,200,4);ctx.fillStyle=C.hot;ctx.fillRect(W/2-100,24,200*f,4);ctx.globalAlpha=0.8;centerText('Dreadnought',33,8,C.hot);ctx.globalAlpha=1;}
function drawEscFlames(){const s=DN.esc;if(!s||s.dead||!BS.on)return;const x=BS.x0+SHIPLEN-8;if(x<-60||x>W+60)return;const k=Math.min(1,s.v/80);
  ctx.save();ctx.globalCompositeOperation='lighter';
  for(const fy of [0.3,0.53,0.76]){const y=STERNY+BSM.stern.h*fy,l=(24+80*k)*(0.85+0.3*Math.random());
    ctx.globalAlpha=0.6;ctx.drawImage(glow(C.ember),x-8,y-12,l,24);ctx.globalAlpha=0.8;ctx.drawImage(glow(C.gold),x-6,y-6,l*0.6,12);ctx.globalAlpha=0.9;ctx.drawImage(glow(C.white),x-4,y-3,l*0.3,6);}
  ctx.restore();}
// the hull, its deck pieces and the cover blocks; once destroyed the ship snaps in two at the bridge and sinks
function dnHullDraw(){const s=DN.esc;if(!s||!s.dead){drawHull();drawDNHull();drawBlocks();drawEscFlames();return;}
  const sp=BS.x0+BRIDGE_SX-BSM.bridge.w*0.2,py=200;
  for(const side of [-1,1]){ctx.save();ctx.beginPath();if(side<0)ctx.rect(-80,-80,sp+80,H+300);else ctx.rect(sp,-80,W+160,H+300);ctx.clip();
    ctx.translate(sp,py+s.sink*(side<0?1:1.3));ctx.rotate(-side*s.tilt);ctx.translate(-sp,-py);drawHull();drawDNHull();ctx.restore();}}
'''
GUNJS=(GUNJS.replace('%BASE%',A['base']['uri']).replace('%BARREL%',A['barrel']['uri']).replace('%BLOCK%',A['block']['uri'])
  .replace('%BH%',str(A['base']['h'])).replace('%BW%',str(A['base']['w'])).replace('%SX%',str(A['base']['socket'][0])).replace('%SY%',str(A['base']['socket'][1]))
  .replace('%RH%',str(A['barrel']['h'])).replace('%RW%',str(A['barrel']['w'])).replace('%C0%',str(A['barrel']['coil'][0])).replace('%C1%',str(A['barrel']['coil'][1])))
rep("\nfunction dnTick(dt){const T=sxClock(DN);", GUNJS+"\nfunction dnTick(dt){const T=sxClock(DN);")

# fight start (music-locked stage and the fallback director)
rep("BS.fight=true;const b=BS.bridge;if(b&&!b.dead){b.prot=false;G.boss=b;G.bossDropT=8;bossRoar(b);}","dnFightStart();",2)
# escape movement replaces the stop
rep("BS.s=Math.min(stopS,Math.max(BS.s,60*(T-DN.HULL)));if(BS.s>=stopS)BS.stop=true;",
    "if(DN.esc)dnEscapeTick(dt);else{BS.s=Math.min(stopS,Math.max(BS.s,60*(T-DN.HULL)));if(BS.s>=stopS)BS.stop=true;}")
rep("  if(!BS.stop){BS.s=Math.min(stopS,BS.s+60*dt);if(BS.s>=stopS)BS.stop=true;}",
    "  if(DN.esc)dnEscapeTick(dt);else if(!BS.stop){BS.s=Math.min(stopS,BS.s+60*dt);if(BS.s>=stopS)BS.stop=true;}")
# state reset
rep("DN.eng=null;DN.hull=false;DN.warned=false;DN.bossMus=false;DN.haz=false;",
    "DN.eng=null;DN.hull=false;DN.warned=false;DN.bossMus=false;DN.haz=false;DN.gun=null;DN.esc=null;DN.blocks=null;")
# cover blocks are part of the deck; the turret that stood there is gone
rep("function dnLayout(){return {T:[330,640,1060,1260,1560,2700,3250,3500,3800,4000],","function dnLayout(){return {T:[330,640,1060,1260,1560,2700,3250,3500,3800],")
rep("function dnHullExtras(){","function dnHullExtras(){DN.blocks=GUN.BLOCKS.map(sx=>({sx,hp:2,fl:0}));")
# solid blocks and gun base; nothing solid once the ship breaks apart
rep("function hullTop(x){if(!BS.on)return H+50;const sx=x-BS.x0;return Math.min(hullTopSX(sx),bridgeTopSX(sx),trowTopSX(sx));}",
    "function hullTop(x){if(!BS.on||(DN.esc&&DN.esc.dead))return H+50;const sx=x-BS.x0;return Math.min(hullTopSX(sx),bridgeTopSX(sx),trowTopSX(sx),blockTopSX(sx),gunTopSX(sx));}")
# the bridge: scenery that keeps firing (no longer a boss)
rep("BS.bridge=E('bs_bridge',BS.x0+BRIDGE_SX,100,{sx:BRIDGE_SX,prot:true,entering:false,f1:1,f2:1.5,f3:0.5});",
    "BS.bridge=E('bs_bridge',BS.x0+BRIDGE_SX,100,{sx:BRIDGE_SX,prot:true,isBoss:false,entering:false,f1:1,f2:1.5,f3:0.5});")
rep("    const top=bsBridgeTop();e.y=top+BSM.bridge.h*0.455;\n    if(G.boss===e)updateBoss(e,dt);",
    "    const top=bsBridgeTop();e.y=top+BSM.bridge.h*0.455;\n    if(BS.fight&&G.state==='play'&&e.x<W+30&&e.x>-60&&!(DN.esc&&(DN.esc.dead||DN.esc.end))){tellTick(e,dt);bridgeAttack(e,dt);}\n  }else if(e.type==='bs_gun'){gunUpdate(e,dt);")
rep("case 'bs_bridge':updateBSPart(e,dt,d);break;","case 'bs_bridge':case 'bs_gun':updateBSPart(e,dt,d);break;")
rep("  const ph=bossPhase(e),sp=1+(G.stage-1)*0.05;\n  e.x=BS.x0+e.sx+rnd(-0.4,0.4);",
    "  const ph=e.isBoss?bossPhase(e):DN.esc?1:DN.gun?(DN.gun.ph||0):0,sp=1+(G.stage-1)*0.05;   // the bridge follows the main gun's phase\n  e.x=BS.x0+e.sx+rnd(-0.4,0.4);")
rep("col:'#ffb43d',s:'shell'});\n  P(0,x-2,y,0,0,0.09,10,4,'#ffe08a');","col:'#ffb43d',s:'shell',dk:0.5});\n  P(0,x-2,y,0,0,0.09,10,4,'#ffe08a');")
rep("s:'rocket',ho:1.3});","s:'rocket',ho:1.3,dk:0.5});")
rep("const c=brPt(e,BR_LENS);radial(c[0],c[1],ph===2?18:13,80*sp,e.t,'#ff3d3d');",
    "const c=brPt(e,BR_LENS),n0=eb.length;radial(c[0],c[1],ph===2?18:13,80*sp,e.t,'#ff3d3d');for(let i=n0;i<eb.length;i++)eb[i].dk=0.5;")
rep("playerDamage(b.m?35:b.r>=5?30:b.g?20:20);","playerDamage((b.m?35:b.r>=5?30:b.g?20:20)*(b.dk||1));")   # dk: the bridge's shots do half damage
# boss logic and death
rep("  if(e.type==='bs_bridge'){bridgeAttack(e,dt);bossDamageFx(e,dt);return;}",
    "  if(e.type==='bs_gun'){gunAttack(e,dt);bossDamageFx(e,dt);return;}\n  if(e.type==='bs_bridge'){bridgeAttack(e,dt);bossDamageFx(e,dt);return;}")
i=s.index("      else if(G.practice){G.ending=true;");j=s.index("\n",i);practice=s[i:j]
k=s.index("      else{G.boss=null;G.clearT=RUNUP;",j);m=s.index("      const bonus=e.score*G.stage;",k);clear=s[k:m]
assert practice.startswith("      else if(G.practice){") and practice.endswith("}") ,practice[-30:]
pbody=practice[len("      else if(G.practice){"):-1]
cbody=clear.rstrip()[len("      else{"):-1]
s=s[:i]+"      else if(e.type==='bs_gun')dnEscapeStart(e);   // the ship runs: the stage ends when it escapes or breaks apart\n      else if(G.practice)practiceDone();\n      else stageClearNow();\n"+s[m:]
rep("function updateBoss(e,dt){","function practiceDone(){"+pbody+"}\nfunction stageClearNow(){"+cbody+"}\nfunction updateBoss(e,dt){")
rep("      if(e.type!=='titan'){pups.push({x:e.x,y:e.y,type:'W',t:0,wi:(Math.random()*4)|0});\n        later(0.6,()=>{if(!say('stageClear',3))sfx.clear();});}",
    "      if(e.type!=='titan'){pups.push({x:e.x,y:e.y,type:'W',t:0,wi:(Math.random()*4)|0});\n        if(e.type!=='bs_gun')later(0.6,()=>{if(!say('stageClear',3))sfx.clear();});}")
# collisions, drawing, HUD
rep("  for(const b of pb){if(b.dead)continue;\n","  for(const b of pb){if(b.dead)continue;\n    if(DN.gun&&gunHit(DN.gun,b))continue;\n    if(DN.esc&&escHit(b))continue;\n")
rep("  if(e.type==='bs_bridge'&&ART.bs_bridge.n){drawBridge(e,ART.bs_bridge);drawTell(e);return;}",
    "  if(e.type==='bs_gun'){drawGun(e);return;}\n  if(e.type==='bs_bridge'&&ART.bs_bridge.n){drawBridge(e,ART.bs_bridge);drawTell(e);return;}")
rep("  drawHull();drawDNHull();drawPresses();drawEngines();","  dnHullDraw();drawPresses();drawEngines();")
rep("  drawMiniBar();drawHealth();","  drawMiniBar();drawEscBar();drawHealth();")
# names and the enemy guide
rep("const INTRO={spinner:'Spinner',","const INTRO={bs_gun:'Main gun',spinner:'Spinner',")
rep(" [4,'bs_bridge','Dreadnought bridge','The ship\\'s command tower. Its twin cannon fires bursts of shells and its red lens fires energy rings, then its launcher adds homing rockets.',['shot','msl'],'Boss'],",
    " [4,'bs_gun','Main gun','Rises from the deck. It tracks you, locks on (solid red line) and fires a beam: hide behind the deck blocks. Its coils glow while it charges. Hit them then for big damage.',['gbeam','shot'],'Boss'],\n"
    " [4,'bs_bridge','Dreadnought bridge','The command tower. Its cannon, lens and rockets fire through the gun fight. When the ship runs, shoot the bridge to break the ship apart before it escapes.',['shot2','msl2'],'Target'],")
# enemy guide: the gun's card shows base and barrel; the bridge shows the escape target and its half-damage shots
rep("const GD={shot:['Shots',20],","const GD={shot2:['Shots',10],msl2:['Missiles',17],gbeam:['Beam',30],shot:['Shots',20],")
rep("function guideArt(g){if(g.k==='ms_turret')return msTurretArt();",
    "function guideArt(g){if(g.k==='ms_turret')return msTurretArt();if(g.k==='bs_gun')return gunCard();")
rep("  const d=DEF[g.k];return d?{n:Math.round(d.hp*sc)}:{n:0};}",
    "  if(g.k==='bs_bridge')return {n:ESC.hp};   // the damage that breaks the ship apart when it runs\n  const d=DEF[g.k];return d?{n:Math.round(d.hp*sc)}:{n:0};}")
rep("function drawBlocks(){","function gunCard(){if(GUN.card)return GUN.card;if(!GUNI.base.complete||!GUNI.barrel.complete)return ART.bs_gun;const k=4,px=32,c=mk(Math.round((GUN.dw+px)*k),Math.round(GUN.dh*1.5*k)),g=c.getContext('2d'),oy=GUN.dh*0.5*k;\n  g.imageSmoothingEnabled=true;g.drawImage(GUNI.base,px*k,oy,GUN.dw*k,GUN.dh*k);g.translate((px+GUN.sock[0]*GUN.dw)*k,oy+GUN.sock[1]*GUN.dh*k);g.rotate(0.35);g.drawImage(GUNI.barrel,-GUN.piv*GUN.bw*k,-GUN.bh*k/2,GUN.bw*k,GUN.bh*k);\n  GUN.card={n:c,dw:GUN.dw+px,dh:GUN.dh*1.5};return GUN.card;}\nfunction drawBlocks(){")
rep("const GAME_VERSION='3.3';","const GAME_VERSION='3.5';")
open(P,'w').write(s);print('OK')
