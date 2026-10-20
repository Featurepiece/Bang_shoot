# v3.7: the Dreadnought is mirrored (bow to the right, engines on the left: you catch it from behind).
# Escape reworked into a chase: the ship bolts right, the hull races past underneath, then the stern strains to pull away;
# drop in behind it and hit the engines while dodging their exhaust bursts. Break it apart or it escapes.
import sys
P=sys.argv[1] if len(sys.argv)>1 else 'test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:90]}')
    s=s.replace(a,b)
# mirrored hull profile and drawing
rep("function hullTopSX(sx){          // top of the hull at ship coordinate sx (y), or H+50 where there is no hull\n",
    "function hullTopSX(sx){return hullTopRaw(SHIPLEN-1e-3-sx);}   // the ship is mirrored: engines (stern) at the left end, bow at the right\n"
    "function hullTopRaw(sx){          // top of the unmirrored hull at ship coordinate sx (y), or H+50 where there is no hull\n")
i=s.index("  if(BSI.bow&&x0+BOWW>-5&&x0<W+5)ctx.drawImage(BSI.bow,x0,BOWY,BOWW,BSM.bow.h);")
j=s.index("ctx.drawImage(BSI.stern,x0+STERN0,STERNY,BSM.stern.w,BSM.stern.h);",i);j=s.index("\n",j)
s=s[:i]+'''  // mirrored: engines at the left end, bow at the right end, every piece flipped
  const fl=(im,x,y,w,h)=>{if(x+w<-5||x>W+5)return;ctx.save();ctx.translate(x+w,y);ctx.scale(-1,1);ctx.drawImage(im,0,0,w,h);ctx.restore();};
  if(BSI.bow)fl(BSI.bow,x0+SHIPLEN-BOWW,BOWY,BOWW,BSM.bow.h);
  for(let i=0;i<NT;i++)fl(BSI.tile,x0+SHIPLEN-BOWW-(i+1)*TILEW-0.5,TILEY,TILEW+1,BSM.tile.h);
  if(BSI.stern)fl(BSI.stern,x0,STERNY,BSM.stern.w,BSM.stern.h);'''+s[j:]
# the escape becomes a chase
i=s.index("/* ---------- the escape: when the gun dies");j=s.index("\nfunction dnTick(dt){")
s=s[:i]+r'''/* ---------- the escape: when the gun dies the Dreadnought bolts to the right. Chase it and hit its engines ---------- */
function nzYs(){return [0.235,0.51,0.733].map(f=>STERNY+BSM.stern.h*f);}   // the three engine nozzles (screen y) on the stern
const NZX=28;                                                                   // nozzle exits, from the ship's left end
function dnEscapeStart(g){DN.gun=null;G.boss=null;
  DN.esc={t:0,v:0,dmg:0,max:ESC.hp*DF.hp,lv:0,ph:'bolt',dead:false,end:false,deadT:0,sink:0,sinkV:0,tilt:0,nz:[0,1,2].map(()=>({st:'idle',t:0,hit:0})),nzT:1.5};
  later(0.5,()=>{if(!DN.esc||DN.esc.end)return;banner('The Dreadnought is escaping!',2.6);if(!samp('alarm',0.5,1))sfx.alarm();rumble(0.8,0.6,1500,true);});}
function dnEscapeTick(dt){const s=DN.esc;s.t+=dt;
  if(!s.dead){const f=Math.min(1,s.dmg/s.max);
    if(s.ph==='bolt'){   // it surges right: the hull races past underneath, then brakes as the stern reaches you
      const d=ESC.creepX-BS.x0,vt=clamp(Math.sqrt(Math.max(0,2*ESC.brake*d)),ESC.creep,ESC.bolt);
      s.v=s.t<0.6?0:Math.min(vt,s.v+ESC.surge*dt);BS.s-=s.v*dt;trauma=Math.max(trauma,0.08*Math.min(1,s.v/200));
      if(BS.x0>=ESC.creepX-2&&s.t>1){s.ph='creep';s.v=ESC.creep;banner('Chase it! Hit the engines!',2.6);}}
    else{s.v+=ESC.acc*(1-0.5*f)*dt;BS.s-=s.v*dt;dnEngineFlares(dt);   // straining to pull away: the more damage, the slower
      const ex=BS.x0+NZX,ys=nzYs();
      if(Math.random()<(0.15+1.4*f)*Q)P(2,ex+rnd(0,60),rnd(ys[0]-20,ys[2]),-40,-20,1.4,2,9,null,0.5);
      if(Math.random()<dt*(0.4+5*f))explode(ex+rnd(0,120),rnd(ys[0]-15,ys[2]),rnd(0.5,1)+f,pick([PAL_EN,PAL_HOT]),true);
      while(f>=(s.lv+1)*0.25&&s.lv<3){s.lv++;   // a big blast at every quarter
        const hx=ex+rnd(10,90),hy=rnd(ys[0],ys[2]);for(let i=0;i<4;i++)later(i*0.1,()=>explode(hx+rnd(-20,20),hy+rnd(-15,15),2,pick([PAL_EN,PAL_HOT])));
        BS.scorch.push({sx:hx-BS.x0,y:hy,r:16});shake(0.35);trauma=Math.max(trauma,0.5);popup(ex+20,ys[0]-30,['Engine hit','Engines burning','Breaking up'][s.lv-1],C.hot);}}
    if(s.dmg>=s.max)dnEscapeDestroyed();
    else if(BS.x0>W+20||s.t>45)dnEscapeEnd(false);}
  else{s.deadT+=dt;BS.s-=s.v*dt*Math.max(0,1-s.deadT/2);
    if(s.deadT>1.2){s.sinkV+=55*dt;s.sink+=s.sinkV*dt;s.tilt=Math.min(0.5,s.tilt+dt*0.13);}
    if(s.deadT<3.5&&Math.random()<dt*10)explode(rnd(Math.max(0,BS.x0),W),190+s.sink+rnd(-10,40),rnd(1,2.5),pick([PAL_EN,PAL_HOT]),true);
    if(s.deadT>4.6)dnEscapeEnd(true);}}
// exhaust bursts: a nozzle brightens and flickers (the warning), then blasts a long flame back at you
function dnEngineFlares(dt){const s=DN.esc,f=Math.min(1,s.dmg/s.max),ys=nzYs(),ex=BS.x0+NZX;
  s.nzT-=dt*DF.fire;if(s.nzT<=0)inStream('escnz',()=>{s.nzT=rnd(1.5,2.1)*(1-0.2*f);const idle=[0,1,2].filter(i=>s.nz[i].st==='idle'),n=Math.min(idle.length,f>0.5?2:1);
    for(let k=0;k<n;k++){const i=idle.splice((Math.random()*idle.length)|0,1)[0];s.nz[i].st='tell';s.nz[i].t=0.7;}});
  s.nz.forEach((z,i)=>{z.t-=dt;z.hit-=dt;
    if(z.st==='tell'&&z.t<=0){z.st='burst';z.t=0.9;if(!sx('door-blast',0.5,1.3))noiseHit(0.4,0.3,900,120);shake(0.12);}
    else if(z.st==='burst'){if(z.t<=0)z.st='idle';
      else if(pl.alive&&z.hit<=0&&pl.x>ex-ESC.flame&&pl.x<ex+6&&Math.abs(pl.y-ys[i])<9){z.hit=0.7;playerDamage(22);}}});}
function dnEscapeDestroyed(){const s=DN.esc;s.dead=true;s.deadT=0;s.splitSX=clamp(W/2-BS.x0,160,SHIPLEN-160);banner('Dreadnought destroyed!',4);eb.length=0;
  const ex=BS.x0+NZX;for(let i=0;i<10;i++)later(i*0.08,()=>explode(ex+rnd(0,80),rnd(190,262),rnd(1.5,3),pick([PAL_EN,PAL_HOT]),i%3!==0));
  for(const q of enemies)if(!q.dead&&!q.dying&&q.type.startsWith('bs_')){if(q.x>-60&&q.x<W+60)explode(q.x,q.y,1.2,PAL_HOT,true);q.dead=true;}
  for(let i=0;i<20;i++)later(0.1*i,()=>{explode(rnd(Math.max(0,BS.x0),W),185+rnd(-10,40),rnd(1.5,3),pick([PAL_EN,PAL_HOT]),i%3!==0);trauma=Math.max(trauma,0.5);});
  whiteFlash=0.6;flashCol='255,200,140';rumble(1,1,1500,true);FB.kick=2;}
function dnEscapeEnd(dest){const s=DN.esc;if(s.end)return;s.end=true;
  const f=Math.min(1,s.dmg/s.max),dmgB=Math.round(f*100000/100)*100,bon=dmgB+(dest?200000:0);G.score+=bon;
  if(!dest)banner('The Dreadnought escaped',2.6);
  later(dest?0:2.6,()=>{if(G.state!=='play')return;banner(dest?'Damage bonus '+dmgB+'   Destroyed +200000':'Damage bonus '+dmgB,2.8);
    later(2.8,()=>{if(G.state!=='play')return;if(G.practice)practiceDone();else{stageClearNow();later(0.6,()=>{if(!say('stageClear',3))sfx.clear();});}});});}
// player shots during the escape: anything on the ship counts; the engine nozzles count most
function escHit(b){const s=DN.esc;if(!s||s.dead||s.end||b.k==='drop')return false;const t=hullTop(b.x);if(t>=H||b.y<t-6)return false;
  if(b.pierce){if(b.pierce.has(BS))return false;b.pierce.add(BS);}else b.dead=true;
  const sx=b.x-BS.x0,eng=s.ph==='creep'&&sx<NZX+50&&nzYs().some(y=>Math.abs(b.y-y)<12);s.dmg+=b.dmg*(eng?1.5:(s.ph==='creep'&&sx<90)?1:0.6);   // nozzles 1.5x, the rest of the engine end 1x, elsewhere 0.6x
  P(1,b.x,b.y,rnd(-200,-60),rnd(-120,60),0.18,1.5,0,pick(eng?[C.white,C.gold]:[C.gold,C.ember]),5);if(eng)P(0,b.x,b.y,0,0,0.1,9,3,C.gold);hitSound(b.k==='beam'?'pulse':b.k);
  return !b.pierce;}
function drawEscBar(){const s=DN.esc;if(!s||s.end||s.dead||G.state!=='play')return;const f=Math.max(0,1-s.dmg/s.max);
  ctx.fillStyle='rgba(255,61,110,.2)';ctx.fillRect(W/2-100,24,200,4);ctx.fillStyle=C.hot;ctx.fillRect(W/2-100,24,200*f,4);ctx.globalAlpha=0.8;centerText('Dreadnought',33,8,C.hot);ctx.globalAlpha=1;}
// engine exhaust while it runs: short flames at rest, a bright flicker as a warning, then a long blast
function drawEscFlames(){const s=DN.esc;if(!s||s.dead||!BS.on)return;const ex=BS.x0+NZX;if(ex<-200||ex>W+60)return;const ys=nzYs(),k=Math.min(1,s.v/120);
  ctx.save();ctx.globalCompositeOperation='lighter';
  s.nz.forEach((z,i)=>{const y=ys[i],burst=z.st==='burst',tell=z.st==='tell',tk=tell?1-z.t/0.7:0,fk=0.85+0.3*Math.random();
    const l=(burst?ESC.flame:tell?22+26*tk:18+20*k)*fk,h=burst?11:tell?7:5;
    ctx.globalAlpha=burst?0.8:0.6;ctx.drawImage(glow(C.ember),ex-l,y-h*1.6,l+8,h*3.2);ctx.globalAlpha=0.85;ctx.drawImage(glow(C.gold),ex-l*0.75,y-h,l*0.75+6,h*2);
    ctx.globalAlpha=burst?0.95:0.7;ctx.drawImage(glow(C.white),ex-l*0.4,y-h*0.5,l*0.4+4,h);
    if(tell){ctx.globalAlpha=0.5+0.5*Math.sin(G.t*45);const r=8+10*tk;ctx.drawImage(glow(C.white),ex-r,y-r,r*2,r*2);}});
  ctx.restore();}
// the hull, its deck pieces and the cover blocks; once destroyed the ship snaps in two and sinks
function dnHullDraw(){const s=DN.esc;if(!s||!s.dead){drawHull();drawDNHull();drawBlocks();drawEscFlames();return;}
  const sp=BS.x0+s.splitSX,py=200;
  for(const side of [-1,1]){ctx.save();ctx.beginPath();if(side<0)ctx.rect(-80,-80,sp+80,H+300);else ctx.rect(sp,-80,W+160,H+300);ctx.clip();
    ctx.translate(sp,py+s.sink*(side<0?1.3:1));ctx.rotate(-side*s.tilt);ctx.translate(-sp,-py);drawHull();drawDNHull();ctx.restore();}}
'''+s[j:]
rep("const ESC={hp:180,acc:7.3};   // escape: damage needed to break the ship apart; how fast it pulls away (px/s per second)",
    "// escape: damage needed to break the ship apart; the surge (top speed, acceleration, braking) and the creep once the stern reaches you\nconst ESC={hp:260,bolt:650,surge:420,brake:700,creep:10,creepX:150,acc:5,flame:150};")
# shots that reach the hull count as escape damage (they used to just stop on the deck)
rep("    if(BS.on&&!b.dead&&b.y>hullTopSX(b.x-BS.x0)){   // shots stop on the deck (the bridge tower itself is the target)\n",
    "    if(BS.on&&!b.dead&&b.y>hullTopSX(b.x-BS.x0)&&!(DN.esc&&(DN.esc.dead||escHit(b)))){   // shots stop on the deck; during the escape they damage the ship\n")
rep("    if(BS.on&&!b.dead&&b.y>trowTopSX(b.x-BS.x0)){b.dead=true;","    if(BS.on&&!b.dead&&b.y>trowTopSX(b.x-BS.x0)&&!(DN.esc&&(DN.esc.dead||escHit(b)))){b.dead=true;")
# words
rep("'Fly its hull. Take out the bridge!'","'Fly its hull. Take out the main gun!'")
rep("'The command tower. Its cannon, lens and rockets fire through the gun fight. When the ship runs, shoot the bridge to break the ship apart before it escapes.'",
    "'The command tower. Its cannon, lens and rockets fire through the gun fight. Then the ship bolts right: chase it and hit its engines to break it apart.'")
rep("const GAME_VERSION='3.5';","const GAME_VERSION='3.7';")
open(P,'w').write(s);print('OK')
