"""Stages 3 and 4 rebuilt as running orders locked to their new music (like stage 1).
Hive (music/stage3-hive.mp3, Insectoid Arpeggio trimmed): play from 23.82; Brood Beetle 8 bars in; 49.5 hive walls with pods;
  82.88 breakdown: the giant serpent; 109.83 full power: tunnel, then waves + acid rain; 146.61 Warning; Hive Mother on the big hit at 162.2.
Dreadnought (music/stage4-dread.mp3, Full Power trimmed): play from 3.48; approach waves; 40.29 the engines pass overhead
  (exhaust blasts, music muffled until 59.47); 73.86 the hull slides in under you (turrets, turret rows, reactor core);
  141.06 Warning; the bridge arrives as the music cuts at 150.65 and its boss music starts at the drop."""
import sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1]
src = open(path, encoding='utf-8').read()
A = json.load(open(os.path.join(HERE, 'art34.json')))
def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count: sys.exit(f'FAIL ({n}x, wanted {count}x): {old[:120]}')
    src = src.replace(old, new)

# ---------------- music ----------------
rep("""MUSIC.stage4={src:'music/stage4.mp3',""", """MUSIC.stage3h={src:'music/stage3-hive.mp3',ls:109.83,le:146.6,drop:23.82,beat:0.40055,anchor:23.82,buf:null};   // Insectoid Arpeggio (game edit): the Hive
MUSIC.stage4d={src:'music/stage4-dread.mp3',ls:96.27,le:141.0,drop:3.48,beat:0.40055,anchor:3.48,buf:null};   // Full Power (game edit): the Dreadnought
MUSIC.stage4={src:'music/stage4.mp3',""")
rep("""function stageTrack(n){const k=n===1?'stage1':n===4?'stage4':""", """function stageTrack(n){const k=n===1?'stage1':n===3&&MUSIC.stage3h?'stage3h':n===4?(MUSIC.stage4d?'stage4d':'stage4'):""")
rep("""const order=['title','stage1','boss','boss1',""", """const order=['title','stage1','boss','boss1','stage3h','stage4d',""")
rep("""{k:'stage1',n:'E Minor Assault (stage 1)'},""", """{k:'stage1',n:'E Minor Assault (stage 1)'},{k:'stage3h',n:'Insectoid Arpeggio (stage 3)'},{k:'stage4d',n:'Full Power (stage 4)'},""")
# a low-pass filter on the music, so a stage can muffle it (under the Dreadnought's engines)
rep("""  src.connect(g);g.connect(A.duck);src.start(now0,""", """  src.connect(g);g.connect(musicBus());src.start(now0,""")
rep("""function musicOff(fade){""", """function musicBus(){if(!A.mf&&A.ctx){A.mf=A.ctx.createBiquadFilter();A.mf.type='lowpass';A.mf.frequency.value=22000;A.mf.Q.value=0.8;A.mf.connect(A.duck);}return A.mf||A.duck;}
function muffle(on){if(!A.mf||!A.ctx)return;if(A.mfOn===on)return;A.mfOn=on;A.mf.frequency.setTargetAtTime(on?650:22000,A.ctx.currentTime,on?0.35:0.2);}
function musicOff(fade){""")

# ---------------- boss hand-off works for any music-locked stage ----------------
rep("""    G.pre=true;G.s1Pre=true;G.preT=0;""", """    G.pre=true;G.s1Pre=true;G.sCfg=S1CFG;G.preT=0;""")
rep("""const S1={DROP:28.30,""", """const S1CFG={get HIT(){return S1.HIT;},get END(){return S1.END;},clock:()=>s1Clock()};
const S1={DROP:28.30,""")
rep("""  if(G.s1Pre){G.preClock=Math.max(G.preClock,BOSS_DROP-(S1.HIT-s1Clock()));""", """  if(G.s1Pre){G.preClock=Math.max(G.preClock,BOSS_DROP-(G.sCfg.HIT-G.sCfg.clock()));""")
rep("""  if(!G.warned&&c>=BOSS_DROP-(G.s1Pre?S1.HIT-S1.END-0.2:WARN_AT)){""", """  if(!G.warned&&c>=BOSS_DROP-(G.s1Pre?G.sCfg.HIT-G.sCfg.END-0.2:WARN_AT)){""")

CODE = r"""
/* ================= music-locked stages 3 (the Hive) and 4 (the Dreadnought) ================= */
function sxClock(cfg){const g=cfg.DROP+G.stageT;let c=g;
  if(M.name===cfg.track&&M.node){const p=trackPos();if(p>=(G.sxc||0)-2)c=Math.max(p,g-1.0);}
  return G.sxc=Math.max(G.sxc||0,c);}
function sxReset(){G.sxc=0;HV.walls=null;HV.serp=null;HV.serpDone=false;HV.tun=false;HV.haz=false;DN.eng=null;DN.hull=false;DN.warned=false;DN.bossMus=false;DN.haz=false;if(typeof muffle==='function')muffle(false);}
function sxSeek(cfg,t){sxReset();G.stageT=t-cfg.DROP;G.miniDone=true;if(A.ctx)stopMusic(0.1);playMusic(cfg.track,t,0.1);}
function sxCur(){return G.stage===3&&MUSIC.stage3h?HV:G.stage===4&&MUSIC.stage4d?DN:null;}
function sxWaves(dt,T,cfg,k){
  if(T<cfg.DROP+3)return;
  {const busy=enemies.some(e=>!e.dead&&!e.dying&&e.x>-10&&e.x<W+10&&e.fx!=='rock'&&e.fx!=='crys'&&e.type!=='hpod');G.emptyT=busy?0:(G.emptyT||0)+dt;if(G.emptyT>0.6){G.emptyT=0;G.spawnT=0;}}
  if(introTick(dt))return;
  G.spawnT-=dt;if(G.spawnT<=0){introWave();G.spawnT*=DF.spawn*(k||1);}}
function sxMini(dt,T,at){
  if(!G.miniDone&&T>=at)spawnMini();
  if(G.mini&&!G.mini.dead){G.escT=(G.escT===undefined?3:G.escT)-dt;if(G.escT<=0){G.escT=rnd(4,5.5);const f=faction(),y=rnd(50,H-90);for(let i=0;i<5;i++)fxE('snake',f,'small',1.5,120,W+8+i*16,y,{baseY:y,ph:-i*0.45,fac:f});}return true;}
  return false;}
// "Attack here" pointer, shown the first time a one-weak-spot enemy appears in each game
function drawTip(x,y,t){if(t<=0)return;const bob=Math.sin(G.t*8)*2,above=y>60,ty=above?y-26+bob:y+26-bob;ctx.save();ctx.globalAlpha=Math.min(1,t);
  ctx.fillStyle=C.gold;ctx.beginPath();if(above){ctx.moveTo(x-5,ty+5);ctx.lineTo(x+5,ty+5);ctx.lineTo(x,ty+11);}else{ctx.moveTo(x-5,ty-5);ctx.lineTo(x+5,ty-5);ctx.lineTo(x,ty-11);}ctx.fill();
  ctx.font=F8;ctx.textAlign='center';ctx.textBaseline='middle';txt('Attack here',clamp(x,50,W-50),above?ty-4:ty+4,C.gold);ctx.restore();}
function sxImg(d){const o={img:new Image(),w:d.w/2,h:d.h/2};o.img.src=d.uri;return o;}

/* ---------- the Hive ---------- */
const HV={track:'stage3h',DROP:23.82,MINI:36.64,WALLS:49.5,BREAK:82.88,FULL:109.83,END:146.61,HIT:162.2,walls:null,serp:null,serpDone:false,tun:false,haz:false};
const HVCFG={HIT:HV.HIT,END:HV.END,clock:()=>sxClock(HV)};
const HVA={wall:sxImg(""" + json.dumps({'uri':A['wall']['uri'],'w':A['wall']['w'],'h':A['wall']['h']}) + r"""),podC:sxImg(""" + json.dumps({'uri':A['podC']['uri'],'w':A['podC']['w'],'h':A['podC']['h']}) + r"""),
  podO:sxImg(""" + json.dumps({'uri':A['podO']['uri'],'w':A['podO']['w'],'h':A['podO']['h']}) + r"""),head:sxImg(""" + json.dumps({'uri':A['head']['uri'],'w':A['head']['w'],'h':A['head']['h']}) + r"""),
  headG:sxImg(""" + json.dumps({'uri':A['headG']['uri'],'w':A['headG']['w'],'h':A['headG']['h']}) + r"""),seg:sxImg(""" + json.dumps({'uri':A['seg']['uri'],'w':A['seg']['w'],'h':A['seg']['h']}) + r""")};
const HV_PROF=""" + json.dumps(A['wall']['prof']) + r""",HV_WW=112,HV_WH=HV_WW*""" + str(A['wall']['h']/A['wall']['w']) + r""";   // wall tile drawn 112 wide; profile = lowest solid pixel per column of the 320-wide art
function hvDepth(X,bottom){const w=HV.walls;if(!w||X<w.X0-40||X>w.X1+40)return 0;
  const ramp=clamp(Math.min(X-w.X0+40,w.X1+40-X)/60,0,1),u=mod(X+(bottom?HV_WW*0.5:0),HV_WW)/HV_WW,i=Math.min(HV_PROF.length-1,(u*HV_PROF.length)|0);
  return (HV_PROF[i]/(HV_PROF.length*""" + str(A['wall']['h']/A['wall']['w']) + r"""))*HV_WH*ramp;}   // depth in screen px
function hvTop(x){return hvDepth(x+G.scroll,false);}
function hvBot(x){const d=hvDepth(x+G.scroll,true);return d?H-d:H+50;}
function hvWallsStart(T){const X0=G.scroll+W+20,X1=X0+60*(HV.BREAK-T)-W*0.6;HV.walls={X0,X1,pods:[]};let top=true;
  for(let X=X0+160;X<X1-60;X+=rnd(150,210)){const p=E('hpod',X-G.scroll,0,{X,top,prot:true,open:false,pt:rnd(1.2,3),hw:16,hh:9});HV.walls.pods.push(p);top=!top;}}
function hvPodUpdate(e,dt){const x=e.X-G.scroll;e.x=x;const d=hvDepth(e.X,!e.top);e.y=e.top?d-5:H-d+5;if(x<-40){e.dead=true;return;}
  e.flip=e.top;if(x>W-10||G.state!=='play')return;e.pt-=dt*DF.fire;
  if(!e.open&&e.pt<=0){e.open=true;e.prot=false;e.pt=1.5;e.shot=false;sx('egg-burst',0.6,1.2);}
  else if(e.open){if(!e.shot&&e.pt<1.15){e.shot=true;
      if(e.top){const a=Math.atan2(pl.y-e.y,pl.x-e.x);for(const s of [-0.18,0,0.18])shootE(e.x,e.y+6,Math.cos(a+s)*105,Math.sin(a+s)*105,'#b6ff3d');sx('spit',0.7,1);}
      else{for(let i=0;i<2;i++)E('dart',e.x,e.y-10-i*8,{stopX:rnd(W-200,W-80)});}}
    if(e.pt<=0){e.open=false;e.prot=true;e.pt=rnd(2.4,3.8);}}}
function hvWallHit(x,y,pad){if(!HV.walls)return false;return y<hvTop(x)-(pad||0)||y>hvBot(x)+(pad||0);}
function hvWallPlayer(){if(!HV.walls||!pl.alive||G.state!=='play')return;let hit=false;
  for(const sx of [-14,0,12]){const t=hvTop(pl.x+sx),b=hvBot(pl.x+sx);if(pl.y-5<t){hit=true;pl.y=t+5;}else if(pl.y+5>b){hit=true;pl.y=b-5;}}
  if(hit){if(Math.random()<0.5)P(1,pl.x,pl.y,rnd(-150,-40),rnd(-80,80),0.2,1.6,0,'#9dff3d',5);if(OPT.diff!=='easy'&&pl.inv<=0)playerDamage(25);}}
function drawHiveWalls(){const w=HV.walls;if(!w)return;const a=HVA.wall.img;if(!a.complete||!a.naturalWidth)return;
  const x0=w.X0-G.scroll,x1=w.X1-G.scroll;if(x1<-HV_WW||x0>W+HV_WW)return;ctx.save();ctx.imageSmoothingEnabled=true;
  const ts=Math.floor(Math.max(x0-HV_WW,G.scroll-HV_WW)/1)*0;
  for(let X=Math.floor((G.scroll-HV_WW)/HV_WW)*HV_WW;X<G.scroll+W+HV_WW;X+=HV_WW){if(X+HV_WW<w.X0-40||X>w.X1+40)continue;const x=X-G.scroll;
    const r=clamp(Math.min(X+HV_WW*0.5-w.X0+40,w.X1+40-X-HV_WW*0.5)/60,0,1);if(r<=0)continue;const h=HV_WH*r;
    ctx.drawImage(a,x,-HV_WH+h,HV_WW+0.5,HV_WH);
    ctx.save();ctx.translate(x-HV_WW*0.5,H+HV_WH-h);ctx.scale(1,-1);ctx.drawImage(a,0,0,HV_WW+0.5,HV_WH);ctx.drawImage(a,HV_WW,0,HV_WW+0.5,HV_WH);ctx.restore();}
  for(const p of w.pods){if(p.dead||p.x<-30||p.x>W+30)continue;const im=(p.open?HVA.podO:HVA.podC).img;if(!im.complete)continue;const pw=40,ph=pw*(p.open?HVA.podO:HVA.podC).h/(p.open?HVA.podO:HVA.podC).w;
    ctx.save();ctx.translate(p.x,p.y);if(p.top)ctx.scale(1,-1);ctx.drawImage(im,-pw/2,-ph+4,pw,ph);
    if(p.open){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.5+0.3*Math.sin(G.t*20);ctx.drawImage(glow('#d8ff3d'),-12,-ph,24,ph);}
    if(p.flash>0){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.8;ctx.drawImage(glow(C.white),-14,-ph,28,ph+6);}ctx.restore();}
  ctx.restore();}

/* the giant serpent: armoured body is a moving wall, only the head can be hurt */
ART.serpg={dw:44,dh:24,cr:0,core:[0,0],gc:'#9dff3d',pal:PAL_HIVE};DEF.serpg={hp:200,score:20000,pw:4,drop:1};
ART.hpod={dw:40,dh:18,cr:0,core:[0,0],gc:'#9dff3d',pal:PAL_HIVE};DEF.hpod={hp:7,score:500,pw:1.6,drop:0.12};
const SERP_N=16,SERP_SP=17,SERP_R=11;
function serpSpawn(){const first=!G.seen.serpTip;G.seen.serpTip=1;
  const e=E('serpg',W+90,H*0.4,{t0:0,hist:[],st:'in',h:Math.PI,v:95,nx:W+70,ny:H*0.4,wx:W*0.6,wy:H*0.45,wT:3,o:1,spT:3,lunge:0,biteT:3,tipT:first?6:0,hw:26,hh:16,glow:0});
  for(let k=0;k<SERP_N*SERP_SP+40;k+=2)e.hist.push({x:W+70+k,y:H*0.4});HV.serp=e;e.sg=[];for(let i=0;i<SERP_N;i++)e.sg.push(serpPos(e,i));
  if(!sx('miniboss-arrive',1,0.7)){tone('square',220,220,0.2,0.05);}shake(0.25);}
function serpPos(e,i){let need=(i+1)*SERP_SP,acc=0,p=e.hist[0];for(let k=1;k<e.hist.length;k++){const q=e.hist[k],d=Math.hypot(q.x-p.x,q.y-p.y);if(acc+d>=need){const f=(need-acc)/(d||1);return [p.x+(q.x-p.x)*f,p.y+(q.y-p.y)*f,Math.atan2(p.y-q.y,p.x-q.x)];}acc+=d;p=q;}return [p.x,p.y,0];}
// steering: the head always swims forward and turns towards a target at a limited rate, so its path is one smooth curve;
// a gentle slither is added to the direction of travel and ripples down the body because the body follows the path
function serpPick(e){const near=pl.alive&&Math.random()<0.4;
  e.wx=near?clamp(pl.x+rnd(40,120),W*0.3,W-50):rnd(W*0.35,W-50);e.wy=near?clamp(pl.y+rnd(-30,30),45,H-45):rnd(45,H-45);e.wT=rnd(2.5,4);}
function serpUpdate(e,dt){const t=(e.t0+=dt),leave=e.st==='out';
  if(e.st==='in'&&e.nx<W-40)e.st='swim';
  if(leave){e.wx=-400;e.wy=H*0.5;}
  else{e.wT-=dt;if(e.wT<=0||Math.hypot(e.wx-e.nx,e.wy-e.ny)<45)serpPick(e);}
  // lunge (the bite): a smooth burst of speed straight at you, then it eases back
  e.biteT-=dt;
  if(!leave&&G.state==='play'&&pl.alive&&e.lunge<=0&&e.biteT<=0&&Math.hypot(pl.x-e.x,pl.y-e.y)<120){e.lunge=0.6;e.biteT=2.6;e.wx=pl.x;e.wy=pl.y;sx('armour-chip',0.6,1.4);}
  const lk=e.lunge>0?Math.sin((1-e.lunge/0.6)*Math.PI):0;if(e.lunge>0)e.lunge-=dt;
  const want=Math.atan2(e.wy-e.ny,e.wx-e.nx),diffA=Math.atan2(Math.sin(want-e.h),Math.cos(want-e.h)),rate=leave?1.6:(1.7+1.6*lk);
  e.h+=clamp(diffA*2.2,-rate,rate)*dt;                                   // smooth, limited turning
  const vT=leave?170:95+150*lk;e.v+=(vT-e.v)*Math.min(1,dt*3);            // speed eases, never jumps
  const mv=e.h+Math.sin(t*2.6)*0.32*(1-lk);                              // slither
  e.nx+=Math.cos(mv)*e.v*dt;e.ny+=Math.sin(mv)*e.v*dt;
  if(!leave){e.ny=clamp(e.ny,30,H-30);if(e.st!=='in')e.nx=Math.max(e.nx,20);}
  e.ang=e.h;e.x=e.nx+Math.cos(e.h)*18;e.y=e.ny+Math.sin(e.h)*18;          // e.x/e.y = the head (the hit point)
  // the head rolls over smoothly when it turns round (no instant mirror flip); a little hysteresis stops it dithering near vertical
  const c=Math.cos(e.h);if(c<-0.25)e.oT=1;else if(c>0.25)e.oT=-1;e.o+=((e.oT||1)-e.o)*Math.min(1,dt*5);
  e.hist.unshift({x:e.nx,y:e.ny});if(e.hist.length>420)e.hist.length=420;e.sg=[];for(let i=0;i<SERP_N;i++)e.sg.push(serpPos(e,i));
  if(leave&&e.nx<-SERP_N*SERP_SP-100){e.dead=true;HV.serp=null;return;}
  if(G.state!=='play'||leave)return;
  // spit: the mouth glows, then acid
  e.spT-=dt*DF.fire;e.glow=e.spT<0.8?1:0;
  if(e.spT<=0){e.spT=2.3;const mx=e.x+Math.cos(e.h)*16,my=e.y+Math.sin(e.h)*16,a=pl.alive?Math.atan2(pl.y-my,pl.x-mx):e.h;
    for(const s of [-0.36,-0.18,0,0.18,0.36])shootE(mx,my,Math.cos(a+s)*110,Math.sin(a+s)*110,'#b6ff3d');if(!sx('spit',1,0.9))tone('sine',180,90,0.2,0.05);}
  // the body pushes and hurts
  if(pl.alive)for(let i=0;i<SERP_N;i++){const [x,y]=e.sg[i],ddx=pl.x-x,ddy=pl.y-y,d=Math.hypot(ddx,ddy);
    if(d<SERP_R+6){const k=(SERP_R+7)/(d||1);pl.x=clamp(x+ddx*k,8,W-8);pl.y=clamp(y+ddy*k,10,H-10);if(OPT.diff!=='easy'&&pl.inv<=0)playerDamage(25);break;}}}
function serpBlocks(b){const e=HV.serp;if(!e||e.dead||e.dying||!e.sg)return false;for(let i=0;i<SERP_N;i++){const [x,y]=e.sg[i];if((b.x-x)**2+(b.y-y)**2<SERP_R*SERP_R)return true;}return false;}
function serpDie(e){HV.serp=null;HV.serpDone=true;const pts=[];for(let i=0;i<SERP_N;i++)pts.push(serpPos(e,i));FB.kick=1;shake(0.5);
  pts.forEach(([x,y],k)=>later(0.07*k,()=>{explode(x,y,1.6,PAL_HIVE);G.score+=200*G.mult;}));sx('armour-chip',1,0.8);}
function drawSerpent(e){const S=HVA.seg,Hd=e.glow?HVA.headG:HVA.head;ctx.save();ctx.imageSmoothingEnabled=true;
  const sw=30,sh=sw*S.h/S.w,hw=78,hh=hw*HVA.head.h/HVA.head.w;
  const segs=e.sg||[];if(segs.length<SERP_N){ctx.restore();return;}
  const one=(i)=>{const [x,y,a]=segs[i];ctx.save();ctx.translate(x,y);ctx.rotate(a);if(S.img.complete)ctx.drawImage(S.img,-sw/2,-sh/2,sw,sh);ctx.restore();};
  for(let i=SERP_N-1;i>=0;i--)one(i);
  ctx.save();ctx.translate(e.nx,e.ny);ctx.rotate(e.h-Math.PI);ctx.scale(1,Math.abs(e.o)<0.15?(e.o<0?-0.15:0.15):e.o);if(Hd.img.complete)ctx.drawImage(Hd.img,-hw*0.78,-hh/2,hw,hh);
  if(e.flash>0){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.7;ctx.drawImage(glow(C.white),-hw*0.75,-hh/2,hw*0.8,hh);}ctx.restore();
  if(e.glow){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.5+0.3*Math.sin(G.t*30);const mx=e.x+Math.cos(e.ang)*16,my=e.y+Math.sin(e.ang)*16;ctx.drawImage(glow('#d8ff3d'),mx-12,my-12,24,24);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';}
  if(e.tipT>0&&e.x>20&&e.x<W-20){e.tipT-=fdt;drawTip(e.x,e.y,e.tipT);}
  ctx.restore();}

function hvTick(dt){const T=sxClock(HV);
  if(T>=HV.END){G.pre=true;G.s1Pre=true;G.sCfg=HVCFG;G.preT=0;G.preClock=0;G.warned=false;G.s1BossMus=false;
    if(G.mini&&!G.mini.dead)G.mini.leaving=true;if(HV.serp&&HV.serp.st!=='out'){HV.serp.st='out';HV.serp.outT=HV.serp.t0;}return true;}
  hazardTick(dt);
  if(T<HV.WALLS){if(sxMini(dt,T,HV.MINI))return true;sxWaves(dt,T,HV);return true;}
  if(T<HV.BREAK){if(G.mini&&!G.mini.dead&&!G.mini.leaving)G.mini.leaving=true;if(!HV.walls)hvWallsStart(T);sxWaves(dt,T,HV,1.6);return true;}
  if(T<HV.FULL){if(!HV.serp&&!HV.serpDone&&T<HV.FULL-4)serpSpawn();return true;}
  if(HV.serp&&HV.serp.st!=='out'){HV.serp.st='out';HV.serp.outT=HV.serp.t0;}
  if(!HV.tun){HV.tun=true;tunStart();}
  if(TUN.on&&G.scroll+W>TUN.X0-60&&G.scroll+W<TUN.X1+30)return true;
  if(TUN.on&&!TUN.exitSeen&&G.scroll+W>=TUN.X1+30){TUN.exitSeen=true;G.spawnT=Math.min(G.spawnT,0.3);}
  if(!HV.haz&&!TUN.on&&T>=HV.FULL+24){HV.haz=true;startHazard();}
  sxWaves(dt,T,HV,0.8);return true;}

/* ---------- the Dreadnought ---------- */
const DN={track:'stage4d',DROP:3.48,ENGINES:40.29,OPEN:59.47,HULL:73.86,WARN:141.06,HIT:150.65,eng:null,hull:false,warned:false,bossMus:false,haz:false};
const DNA={eng:sxImg(""" + json.dumps({'uri':A['engine']['uri'],'w':A['engine']['w'],'h':A['engine']['h']}) + r"""),trow:sxImg(""" + json.dumps({'uri':A['trow']['uri'],'w':A['trow']['w'],'h':A['trow']['h']}) + r"""),
  reactor:sxImg(""" + json.dumps({'uri':A['reactor']['uri'],'w':A['reactor']['w'],'h':A['reactor']['h']}) + r""")};
const ENG_W=120,ENG_H=ENG_W*""" + str(A['engine']['h']/A['engine']['w']) + r""",ENG_NOZ=""" + json.dumps(A['engine']['noz']) + r""",ENG_Y=-6;
function dnEngStart(){const X0=G.scroll+W+20,X1=X0+60*(DN.HULL-DN.ENGINES)-W*0.3;DN.eng={X0,X1,blasts:[],bt:1.6};}
function dnEngBottom(x){const g=DN.eng;if(!g)return -50;const X=x+G.scroll;if(X<g.X0||X>g.X1)return -50;return ENG_Y+ENG_H-8;}
function dnEngUpdate(dt,T){const g=DN.eng;if(!g)return;if(G.scroll>g.X1+40){DN.eng=null;return;}
  for(const b of g.blasts){b.t-=dt;if(b.st==='warn'&&b.t<=0){b.st='fire';b.t=0.85;b.hit=false;if(!sx('zap-fire',0.45,1.4))noiseHit(0.5,0.15,2500,300);shake(0.1);}
    const x=b.X-G.scroll;if(b.st==='fire'&&!b.hit&&pl.alive&&Math.abs(pl.x-x)<11&&pl.y>ENG_Y+ENG_H-12){b.hit=true;if(OPT.diff!=='easy'||true)playerDamage(30);}
    if(b.st==='fire')for(const e of enemies)if(!e.dead&&!e.dying&&!e.isBoss&&Math.abs(e.x-x)<10)hitEnemy(e,2,e.x,e.y);}
  g.blasts=g.blasts.filter(b=>!(b.st==='fire'&&b.t<=0));
  if(G.state!=='play')return;g.bt-=dt*DF.fire;
  if(g.bt<=0){g.bt=(T<DN.OPEN?1.35:1.0)*rnd(0.85,1.15);const n=T<DN.OPEN?1:2,cand=[];
    for(let X=Math.floor(g.X0/ENG_W)*ENG_W;X<g.X1;X+=ENG_W){if(X<g.X0-1)continue;for(const f of ENG_NOZ){const NX=X+f*ENG_W,x=NX-G.scroll;if(x>110&&x<W-20&&!g.blasts.some(b=>Math.abs(b.X-NX)<40))cand.push(NX);}}
    for(let i=0;i<n&&cand.length;i++){const k=(Math.random()*cand.length)|0;g.blasts.push({X:cand[k],st:'warn',t:0.9});cand.splice(k,1);}
    sx('press-warning',0.5,1.3);}}
function dnEngPlayer(){const g=DN.eng;if(!g||!pl.alive||G.state!=='play')return;let hit=false;for(const sx of [-14,0,12]){const b=dnEngBottom(pl.x+sx);if(pl.y-5<b){hit=true;pl.y=b+5;}}
  if(hit){if(Math.random()<0.5)P(1,pl.x,pl.y,rnd(-150,-40),rnd(10,80),0.2,1.6,0,C.gold,5);if(OPT.diff!=='easy'&&pl.inv<=0)playerDamage(25);}}
function drawEngines(){const g=DN.eng;if(!g)return;const im=DNA.eng.img;ctx.save();ctx.imageSmoothingEnabled=true;
  for(let X=Math.floor(g.X0/ENG_W)*ENG_W;X<g.X1;X+=ENG_W){if(X<g.X0-1)continue;const x=X-G.scroll;if(x<-ENG_W||x>W)continue;if(im.complete)ctx.drawImage(im,x,ENG_Y,ENG_W+0.5,ENG_H);}
  ctx.globalCompositeOperation='lighter';
  for(const b of g.blasts){const x=b.X-G.scroll,y0=ENG_Y+ENG_H-6;
    if(b.st==='warn'){const k=1-b.t/0.9,f=0.4+0.6*Math.abs(Math.sin(G.t*(10+20*k)));ctx.globalAlpha=f;ctx.drawImage(glow(C.ember),x-10-6*k,y0-8,20+12*k,18+10*k);ctx.globalAlpha=0.12*k;ctx.fillStyle=C.ember;ctx.fillRect(x-1,y0,2,H-y0);}
    else{const f=0.75+0.25*Math.random(),w=18*f;ctx.globalAlpha=0.85;ctx.drawImage(glow(C.ember),x-w,y0-10,w*2,H-y0+20);ctx.globalAlpha=0.9;ctx.drawImage(glow(C.gold),x-w*0.5,y0-6,w,H-y0+10);ctx.globalAlpha=0.7;ctx.drawImage(glow(C.white),x-w*0.2,y0,w*0.4,H-y0);
      if(Math.random()<0.6)P(1,x+rnd(-6,6),H-10,rnd(-120,120),rnd(-160,-40),0.3,1.6,0,pick([C.gold,C.ember]),3);}}
  ctx.restore();}

// hull furniture added for the long flyover: two turret rows and the reactor core
const TROW_W=140,TROW_H=TROW_W*""" + str(A['trow']['h']/A['trow']['w']) + r""",TROW_DOMES=""" + json.dumps(A['trow']['domes']) + r""",TROW_DECK=""" + str(A['trow']['deck']) + r""",TROWS=[1800,2320];
const RC_W=120,RC_H=RC_W*""" + str(A['reactor']['h']/A['reactor']['w']) + r""",RC_CORE=""" + json.dumps(A['reactor']['core']) + r""",RC_SX=2950;
ART.bs_dome={dw:16,dh:12,cr:0,core:[0,0],gc:'#ff7a3d',pal:PAL_EN};ART.bs_core={dw:RC_W,dh:RC_H,cr:0,core:[0,0],gc:'#ff7a3d',pal:PAL_HOT};
Object.assign(DEF,{bs_dome:{hp:7,score:500,pw:1.6,drop:0.15},bs_core:{hp:150,score:25000,pw:4,drop:1}});
function trowTopSX(sx){for(const s of TROWS)if(sx>=s&&sx<s+TROW_W)return hullTopSX(s+TROW_W/2)+22-TROW_H*(1-TROW_DECK);return H+50;}
function dnLayout(){return {T:[330,640,1060,1260,1560,2700,3250,3500,3800,4000],SG:[880,1420,3380],HT:[520,980,1340,2620,3150,3650,3900,4080]};}
function dnHullExtras(){for(const s of TROWS)for(const f of TROW_DOMES){const sx=s+f*TROW_W;E('bs_dome',BS.x0+sx,150,{sx,fireT:rnd(1,2.5)});}
  const first=!G.seen.coreTip;G.seen.coreTip=1;E('bs_core',BS.x0+RC_SX,150,{sx:RC_SX,tipT:first?6:0,fireT:2.5});}
function updateDNPart(e,dt,d){
  if(e.type==='bs_dome'){e.y=trowTopSX(e.sx)-5;e.fireT-=dt*DF.fire;
    if(e.fireT<=0&&e.x<W-10&&e.x>30&&G.state==='play'&&!BS.stop){e.fireT=rnd(1.6,2.4)/Math.max(1,d*0.8);aim(e.x-6,e.y-4,110+15*d,1,0,'#ff7a3d');P(0,e.x-6,e.y-4,0,0,0.1,7,3,C.ember);}}
  else if(e.type==='bs_core'){e.y=hullTopSX(e.sx)-RC_H/2+8;e.fireT-=dt*DF.fire;
    if(e.fireT<=0&&e.x<W-20&&e.x>40&&G.state==='play'){e.fireT=2.6;const cx=e.x+(RC_CORE[0]-0.5)*RC_W,cy=e.y+(RC_CORE[1]-0.5)*RC_H;radial(cx,cy,10,80,e.t,'#ff7a3d');}}}
function coreWeak(e,b){const cx=e.x+(RC_CORE[0]-0.5)*RC_W,cy=e.y+(RC_CORE[1]-0.5)*RC_H,r=RC_CORE[2]*RC_W+5;return (b.x-cx)**2+(b.y-cy)**2<r*r;}
function coreDie(e){FB.kick=1.4;shake(0.8);whiteFlash=Math.max(whiteFlash,0.5);flashCol='255,170,80';popup(e.x,e.y-30,'Reactor destroyed',C.gold);
  for(let i=0;i<10;i++)later(0.08*i,()=>explode(e.x+rnd(-60,60),e.y+rnd(-20,20),2.2,pick([PAL_HOT,PAL_EN])));
  // the ship loses power: every gun ahead of the reactor blows up in turn
  const ahead=enemies.filter(q=>!q.dead&&!q.dying&&(q.type==='bs_turret'||q.type==='bs_dome'||q.type==='bs_hatch'||q.type==='bs_shield')&&q.sx>e.sx-260).sort((a,b)=>a.sx-b.sx);
  ahead.forEach((q,k)=>later(0.35+0.12*k,()=>{if(!q.dead)kill(q);}));}
function drawDNHull(){if(!BS.on)return;const x0=BS.x0,im=DNA.trow.img;ctx.save();ctx.imageSmoothingEnabled=true;
  for(const s of TROWS){const x=x0+s;if(x>W+10||x+TROW_W<-10)continue;const top=trowTopSX(s+1);if(im.complete)ctx.drawImage(im,x,top-TROW_H*TROW_DECK,TROW_W,TROW_H);}
  for(const e of enemies){if(e.type!=='bs_dome'||!e.dead)continue;}
  for(const s of TROWS)for(const f of TROW_DOMES){const sx=s+f*TROW_W,dead=!enemies.some(q=>q.type==='bs_dome'&&q.sx===sx&&!q.dead);if(!dead)continue;const x=x0+sx,y=trowTopSX(sx)-5;if(x<-20||x>W+20)continue;
    const g=ctx.createRadialGradient(x,y,1,x,y,9);g.addColorStop(0,'rgba(12,8,6,.95)');g.addColorStop(1,'rgba(12,8,6,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,9,0,TAU);ctx.fill();if(Math.random()<0.08*Q)P(2,x,y-4,-10,-25,1,2,6,null,0.4);}
  ctx.restore();}
function drawCore(e){const im=DNA.reactor.img;ctx.save();ctx.imageSmoothingEnabled=true;if(im.complete)ctx.drawImage(im,e.x-RC_W/2,e.y-RC_H/2,RC_W,RC_H);
  const cx=e.x+(RC_CORE[0]-0.5)*RC_W,cy=e.y+(RC_CORE[1]-0.5)*RC_H,pu=0.5+0.5*Math.sin(G.t*6),r=RC_CORE[2]*RC_W*(1.6+0.4*pu);
  ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.45+0.3*pu;ctx.drawImage(glow(C.ember),cx-r*1.6,cy-r*1.6,r*3.2,r*3.2);ctx.globalAlpha=0.5*pu;ctx.drawImage(glow(C.white),cx-r*0.6,cy-r*0.6,r*1.2,r*1.2);
  if(e.flash>0){ctx.globalAlpha=0.8;ctx.drawImage(glow(C.white),cx-r,cy-r,r*2,r*2);}ctx.restore();
  if(e.tipT>0&&e.x<W-30&&e.x>30){e.tipT-=fdt;drawTip(cx,cy,e.tipT);}}

function dnTick(dt){const T=sxClock(DN);
  if(T<DN.HULL){
    if(T>=DN.ENGINES&&!DN.eng&&!DN.engDone){DN.engDone=true;dnEngStart();}
    muffle(T>=DN.ENGINES&&T<DN.OPEN);
    dnEngUpdate(dt,T);hazardTick(dt);
    sxWaves(dt,T,DN,T>=DN.ENGINES?1.5:1);return;}
  muffle(false);dnEngUpdate(dt,T);
  if(!DN.hull){DN.hull=true;bsInit();}
  if(!BS.on)return;
  const stopS=W+220+BRIDGE_SX-BRIDGE_STOP_X;
  BS.s=Math.min(stopS,Math.max(BS.s,60*(T-DN.HULL)));if(BS.s>=stopS)BS.stop=true;
  BS.x0=W+220-BS.s;
  if(!DN.warned&&T>=DN.WARN){DN.warned=true;banner('Warning',DN.HIT-DN.WARN);const v=say('warning',3);if(!samp('alarm',v?0.3:0.6,1))sfx.alarm();}
  if(!DN.bossMus&&T>=DN.HIT-0.03){DN.bossMus=true;playMusic(bossTrack(),BOSS_DROP,0.05,0.3);}
  if(BS.stop&&!BS.fight){BS.fight=true;const b=BS.bridge;if(b&&!b.dead){b.prot=false;G.boss=b;G.bossDropT=8;bossRoar(b);}if(!DN.bossMus){DN.bossMus=true;playMusic(bossTrack(),BOSS_DROP,0.05,0.3);}}
  hazardTick(dt);if(!DN.haz&&T>=DN.HULL+30&&!BS.stop){DN.haz=true;startHazard();}
  {const busy=enemies.some(e=>!e.dead&&!e.dying&&e.x>-10&&e.x<W+10&&!e.hidden&&e.fx!=='rock'&&e.fx!=='crys');G.emptyT=busy?0:(G.emptyT||0)+dt;if(G.emptyT>0.5){G.emptyT=0;BS.escT=0;}}
  if(!BS.stop&&G.state==='play'){BS.escT-=dt;if(BS.escT<=0){BS.escT=rnd(2.8,3.8)*DF.spawn;
    const onHull=hullTopSX(W+20-BS.x0)<H;
    if(onHull&&Math.random()<0.4){for(let i=0;i<2;i++)E('walker1',W+20+i*40,H-40,{walk:rnd(12,20),anim:rnd(0,4),st:'walk',frame:0,fireT:rnd(0.8,2)});}
    else{const y=rnd(40,120),d=diff();for(let i=0;i<5;i++)E('drone',W+20+i*26,y,{baseY:y,amp:rnd(12,26),freq:rnd(2,3),phase:i*0.6,spd:70+15*d});}}}}
"""
rep("""function director(dt){""", CODE + """function director(dt){""")
# director hooks
rep("""  if(isBattle()&&!(G.clearT>0)){bsDirector(dt);return;}""", """  if(isBattle()&&!(G.clearT>0)){if(MUSIC.stage4d){if(!G.pre)dnTick(dt);}else bsDirector(dt);return;}""")
rep("""  if(s1On()&&s1Tick(dt))return;""", """  if(s1On()&&s1Tick(dt))return;
  if(G.stage===3&&MUSIC.stage3h&&hvTick(dt))return;""")
rep("""function tunReset(){TUN.on=false;TUN.done=false;if(typeof s1Reset==='function'){s1Reset();G.s1Ring=false;G.s1RingDone=false;}}""",
    """function tunReset(){TUN.on=false;TUN.done=false;if(typeof s1Reset==='function'){s1Reset();G.s1Ring=false;G.s1RingDone=false;}if(typeof sxReset==='function'){sxReset();DN.engDone=false;}}""")
# longer Dreadnought: 11 hull tiles, bridge where the ship stops on the music's last beat
rep("""const NT=5,BOWW=""", """const NT=11,BOWW=""")
rep("""const BRIDGE_SX=2050,BRIDGE_STOP_X=W-130;""", """const BRIDGE_SX=4257,BRIDGE_STOP_X=W-130;   // the ship stops with the bridge on screen exactly as the stage music ends""")
rep("""  const T=[330,640,1060,1260,1560,1780],SG=[880,1420],HT=[520,980,1340,1660,1880];""", """  const L=dnLayout(),T=L.T,SG=L.SG,HT=L.HT;""")
rep("""  BS.bridge=E('bs_bridge',BS.x0+BRIDGE_SX,100,{""", """  dnHullExtras();
  BS.bridge=E('bs_bridge',BS.x0+BRIDGE_SX,100,{""")
rep("""function hullTop(x){if(!BS.on)return H+50;const sx=x-BS.x0;return Math.min(hullTopSX(sx),bridgeTopSX(sx));}""",
    """function hullTop(x){if(!BS.on)return H+50;const sx=x-BS.x0;return Math.min(hullTopSX(sx),bridgeTopSX(sx),trowTopSX(sx));}""")
rep("""      case 'bs_turret':case 'bs_shield':case 'bs_hatch':case 'bs_bridge':updateBSPart(e,dt,d);break;""",
    """      case 'bs_turret':case 'bs_shield':case 'bs_hatch':case 'bs_bridge':updateBSPart(e,dt,d);break;
      case 'bs_dome':case 'bs_core':e.x=BS.x0+e.sx;updateDNPart(e,dt,d);break;
      case 'hpod':hvPodUpdate(e,dt);break;
      case 'serpg':serpUpdate(e,dt);break;""")
rep("""  if(e.type==='ring')ringDie(e);""", """  if(e.type==='ring')ringDie(e);
  if(e.type==='serpg')serpDie(e);
  if(e.type==='bs_core')coreDie(e);""")
rep("""  if(e.type==='ring'){drawRing(e);return;}""", """  if(e.type==='ring'){drawRing(e);return;}
  if(e.type==='hpod'||e.type==='bs_dome')return;
  if(e.type==='serpg'){drawSerpent(e);return;}
  if(e.type==='bs_core'){drawCore(e);return;}""")
rep("""  drawTunnel();drawGates();drawRingDebris();""", """  drawTunnel();drawGates();drawRingDebris();drawHiveWalls();""")
rep("""  drawHull();drawPresses();""", """  drawHull();drawDNHull();drawPresses();drawEngines();""")
# collisions
rep("""  gatePlayer();
  const shards=""", """  gatePlayer();hvWallPlayer();dnEngPlayer();
  const shards=""")
rep("""    if(RING.e&&b.k!=='beam'&&ringBlocks(b)){""", """    if(HV.serp&&b.k!=='beam'&&serpBlocks(b)){b.dead=true;armourClang();for(let i=0;i<3;i++)P(1,b.x,b.y,rnd(-200,-60),rnd(-120,120),0.18,1.5,0,'#9dff3d',5);continue;}
    if(RING.e&&b.k!=='beam'&&ringBlocks(b)){""")
rep("""        if(e.isBoss&&(e.entering||e.shUp>0)){""", """        if(e.type==='bs_core'&&!coreWeak(e,b)){b.dead=true;armourClang();for(let i=0;i<2;i++)P(1,b.x,b.y,rnd(-220,-80),rnd(-140,140),0.16,1.4,0,C.gold,5);break;}
        if(e.isBoss&&(e.entering||e.shUp>0)){""")
rep("""    if(GATE.list.length&&!b.dead&&gateHit(b.x,b.y)){""", """    if(HV.walls&&!b.dead&&hvWallHit(b.x,b.y)){b.dead=true;P(1,b.x,b.y,rnd(-120,-40),rnd(-60,60),0.15,1.4,0,'#9dff3d',6);}
    if(GATE.list.length&&!b.dead&&gateHit(b.x,b.y)){""")
rep("""    if(GATE.list.length&&!b.dead&&gateHit(b.x,b.y,-2)){""", """    if(HV.walls&&!b.dead&&hvWallHit(b.x,b.y,2)){b.dead=true;P(0,b.x,b.y,0,0,0.12,4,1,b.col||C.hot);}
    if(GATE.list.length&&!b.dead&&gateHit(b.x,b.y,-2)){""")
rep("""    {const g=gateHit(p.x,p.y,6);if(g)p.y=clamp(p.y,g.top+10,g.bot-10);}""", """    {const g=gateHit(p.x,p.y,6);if(g)p.y=clamp(p.y,g.top+10,g.bot-10);}
    if(HV.walls)p.y=clamp(p.y,hvTop(p.x)+12,hvBot(p.x)-12);if(DN.eng)p.y=Math.max(p.y,dnEngBottom(p.x)+12);""")
# serpent body steers flyers? no; drones in the walls section follow the corridor centre
# cheat skip keys jump along these stages too
rep("""else if(!G.boss&&!G.pre&&!(G.clearT>0)){if(s1On())s1Seek(S1.END-1);else G.stageT=BOSS_AT;}return;}""",
    """else if(!G.boss&&!G.pre&&!(G.clearT>0)){if(s1On())s1Seek(S1.END-1);else if(G.stage===3&&MUSIC.stage3h)sxSeek(HV,HV.END-1);else G.stageT=BOSS_AT;}return;}""", 2)
rep("""function bsSkip(){if(BS.on&&!BS.stop)BS.s=Math.max(BS.s,W+220+BRIDGE_SX-BRIDGE_STOP_X-60*11);}""",
    """function bsSkip(){if(MUSIC.stage4d){if(!BS.stop){const t=Math.max(sxClock(DN),DN.WARN-1);sxReset();DN.engDone=true;G.stageT=t-DN.DROP;if(A.ctx)stopMusic(0.1);playMusic(DN.track,t,0.1);}return;}if(BS.on&&!BS.stop)BS.s=Math.max(BS.s,W+220+BRIDGE_SX-BRIDGE_STOP_X-60*11);}""")
# muffle off on stage clear / title
rep("""function goTitle(scr){G.state='title';""", """function goTitle(scr){if(typeof muffle==='function')muffle(false);G.state='title';""")
open(path, 'w', encoding='utf-8').write(src)
print('OK')
