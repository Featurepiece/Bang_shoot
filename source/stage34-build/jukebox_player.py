# Jukebox music player: play/pause, stop, seek -/+10 s, previous/next track, a draggable seek bar, elapsed/total times.
# Controller: X play/pause, Y stop, LB/RB seek, LT/RT previous/next.  Keyboard: P play/pause, O stop, , . seek, [ ] track.
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
# ---------- player logic ----------
rep("function jbPlay(k){",
r'''const JB={paused:null,scrub:null,scrubT:0,flash:[0,0,0,0,0,0]};
const JB_BAR={x:266,y:204,w:194},JB_BTN={y:233,xs:[279,311,343,375,407,439],w:28,h:16};
function jbCur(){return M.node&&M.name&&M.name.startsWith('f_')?M.name:JB.paused?JB.paused.k:null;}
function jbDur(k){const t=k&&MUSIC[k];return t?(t.buf?t.buf.duration:t.le):0;}
function jbPos(){if(JB.paused)return JB.paused.pos;if(!M.node||!A.ctx)return 0;return clamp(M.offset+(A.ctx.currentTime-M.startedAt),0,jbDur(M.name));}
function jbTime(t){t=Math.max(0,Math.floor(t));return Math.floor(t/60)+':'+String(t%60).padStart(2,'0');}
function jbSeek(t){const k=jbCur();if(!k||!MUSIC[k].buf)return;t=clamp(t,0,jbDur(k)-0.25);
  if(JB.paused){JB.paused.pos=t;return;}stopMusic(0.02);playMusic(k,t,0.03);MENU.playing=k;}
function jbPause(){const k=jbCur();
  if(!k){const it=jukeItems()[MENU.sel];if(it&&it.k!=='hdr'&&it.k!=='back')jbPlay(it.k);return;}
  if(JB.paused){const p=JB.paused;JB.paused=null;playMusic(p.k,p.pos,0.05);MENU.playing=p.k;return;}
  JB.paused={k,pos:jbPos()};musicOff(0.05);MENU.playing=k;}
function jbStop(){JB.paused=null;if(M.node)musicOff(0.25);MENU.playing='none';}
function jbStep(d){const it=jukeItems().filter(x=>x.k!=='hdr'&&x.k!=='back');const k=jbCur();let i=it.findIndex(x=>jbKey(x.k)===k);
  if(d<0&&k&&jbPos()>3){jbSeek(0);return;}                  // previous: back to the start first, like a music player
  if(i<0)i=it.findIndex((x,j)=>jukeItems()[MENU.sel]&&x.k===jukeItems()[MENU.sel].k);
  const j=clamp(i+d,0,it.length-1);if(j===i&&k)return;JB.paused=null;MENU.playing=null;jbPlay(it[j].k);}
function jbButton(i){JB.flash[i]=0.25;[()=>jbStep(-1),()=>jbSeek(jbPos()-10),jbPause,jbStop,()=>jbSeek(jbPos()+10),()=>jbStep(1)][i]();}
function jbBarAt(x){const k=jbCur();return clamp((x-JB_BAR.x)/JB_BAR.w,0,1)*jbDur(k);}
cv.addEventListener('pointerdown',e=>{if(G.state!=='title'||MENU.scr!=='jukebox')return;const p=toWorld(e);
  if(Math.abs(p.y-JB_BAR.y)<7&&p.x>JB_BAR.x-6&&p.x<JB_BAR.x+JB_BAR.w+6&&jbCur()){JB.scrub=e.pointerId;JB.scrubT=jbBarAt(p.x);try{cv.setPointerCapture(e.pointerId);}catch(_){}}});
cv.addEventListener('pointermove',e=>{if(JB.scrub===e.pointerId)JB.scrubT=jbBarAt(toWorld(e).x);});
const jbScrubEnd=e=>{if(JB.scrub===e.pointerId){JB.scrub=null;jbSeek(JB.scrubT);}};
cv.addEventListener('pointerup',jbScrubEnd);cv.addEventListener('pointercancel',jbScrubEnd);
function jbPlay(k){''')
# picking a track clears any pause; leaving the Jukebox clears it too
rep("function jbPlay(k){const f=jbKey(k);","function jbPlay(k){JB.paused=null;const f=jbKey(k);")
rep("    else if(a==='back'){MENU.scr='main';MENU.sel=1;MENU.playing=null;titleMusic();}",
    "    else if(a==='back'){JB.paused=null;MENU.scr='main';MENU.sel=1;MENU.playing=null;titleMusic();}")
rep("      else if(it.k==='back'){MENU.scr='main';MENU.sel=1;MENU.playing=null;titleMusic();}",
    "      else if(it.k==='back'){JB.paused=null;MENU.scr='main';MENU.sel=1;MENU.playing=null;titleMusic();}")
# taps on the buttons; taps in the player area never fall through to the list
rep("if(s==='jukebox'){if(p.x>256&&p.y>40&&p.y<160&&!MENU.sync){visStep(1);return;}",
    "if(s==='jukebox'){if(p.x>256&&p.y>40&&p.y<160&&!MENU.sync){visStep(1);return;}\n"
    "    if(p.x>256&&p.y>164&&p.y<252){for(let i=0;i<6;i++)if(Math.abs(p.x-JB_BTN.xs[i])<JB_BTN.w/2+2&&Math.abs(p.y-JB_BTN.y)<JB_BTN.h/2+3){jbButton(i);return;}return;}")
# keyboard
rep("  if(e.code==='KeyM'){setMusicOn(!musicOn);return;}",
    "  if(e.code==='KeyM'){setMusicOn(!musicOn);return;}\n"
    "  if(G.state==='title'&&MENU.scr==='jukebox'){const jb={KeyP:2,KeyO:3,Comma:1,Period:4,BracketLeft:0,BracketRight:5}[e.code];if(jb!==undefined){jbButton(jb);return;}}")
# controller: X play/pause, Y stop (instead of the music toggle here), LB/RB seek, LT/RT track
rep("    if(hit(3)||hit(8))setMusicOn(!musicOn);",
    "    if(MENU.scr==='jukebox'&&G.state==='title'){if(hit(2))jbButton(2);if(hit(3))jbButton(3);if(hit(4))jbButton(1);if(hit(5))jbButton(4);if(hit(6))jbButton(0);if(hit(7))jbButton(5);if(hit(8))setMusicOn(!musicOn);}\n"
    "    else if(hit(3)||hit(8))setMusicOn(!musicOn);")
# ---------- drawing: replace the old now-playing block with the player panel ----------
i=s.index("  if(M.node&&M.name&&MUSIC[M.name]){const t=MUSIC[M.name],p=trackPos(),tot=t.buf?t.buf.duration:t.le;")
j=s.index("  if(MENU.msgT>0){ctx.globalAlpha=Math.min(1,MENU.msgT);centerText(MENU.msg,262,8,'#6dffa8');ctx.globalAlpha=1;}",i)
s=s[:i]+"  drawJbPlayer();\n"+s[j:]
rep("  if(MENU.msgT>0){ctx.globalAlpha=Math.min(1,MENU.msgT);centerText(MENU.msg,262,8,'#6dffa8');ctx.globalAlpha=1;}\n}",
    "  if(MENU.msgT>0){ctx.globalAlpha=Math.min(1,MENU.msgT);centerText(MENU.msg,262,8,'#6dffa8');ctx.globalAlpha=1;}\n"
    "  else{ctx.globalAlpha=0.55;centerText(GP.active?'X play/pause   Y stop   LB/RB seek   LT/RT track':touchUI?'Drag the bar to move through the song':'P play/pause   O stop   , . seek   [ ] track',262,8,'#8d7fc0');ctx.globalAlpha=1;}\n}")
rep("const VIS_N=['Bars',",r'''function drawJbPlayer(){
  panel(256,166,214,84);for(let i=0;i<6;i++)JB.flash[i]=Math.max(0,JB.flash[i]-1/60);
  const k=jbCur(),dur=jbDur(k),pos=JB.scrub!==null?JB.scrubT:jbPos();ctx.font=F8;ctx.textBaseline='middle';ctx.textAlign='left';
  if(k){const bk=k.replace(/^f_/,''),nm=bk==='secret'?'Secret song':(TRACKS.find(x=>x.k===bk)||{}).n||bk;
    txt((JB.paused?'II ':'> ')+(nm.length>30?nm.slice(0,29)+'.':nm),264,178,JB.paused?'#b9a8e8':C.white);
    ctx.globalAlpha=0.6;txt(MUSIC[k].buf?'Full version':'Loading...',264,190,'#8d7fc0');ctx.globalAlpha=1;}
  else{ctx.globalAlpha=0.6;txt('Pick a track to play',264,178,'#8d7fc0');ctx.globalAlpha=1;}
  // seek bar with the knob, and the times under it
  const B=JB_BAR,f=dur>0?clamp(pos/dur,0,1):0;ctx.fillStyle='rgba(255,255,255,.15)';ctx.fillRect(B.x,B.y-1,B.w,3);
  ctx.fillStyle=C.gold;ctx.fillRect(B.x,B.y-1,B.w*f,3);if(k){ctx.fillStyle=JB.scrub!==null?C.white:C.gold;ctx.fillRect(B.x+B.w*f-2,B.y-4,4,9);}
  ctx.globalAlpha=0.8;txt(jbTime(pos),B.x,B.y+11,'#d9c8ff');ctx.textAlign='right';txt(k?jbTime(dur):'0:00',B.x+B.w,B.y+11,'#d9c8ff');ctx.textAlign='left';ctx.globalAlpha=1;
  // buttons: previous, back 10 s, play/pause, stop, forward 10 s, next
  const playing=!!(M.node&&k&&!JB.paused);
  for(let i=0;i<6;i++){const cx=JB_BTN.xs[i],cy=JB_BTN.y,w=JB_BTN.w,h=JB_BTN.h,fl=JB.flash[i]>0;
    ctx.fillStyle=fl?'rgba(255,210,74,.35)':'rgba(255,255,255,.06)';ctx.fillRect(cx-w/2,cy-h/2,w,h);ctx.strokeStyle=fl?C.gold:'rgba(185,168,232,.55)';ctx.lineWidth=1;ctx.strokeRect(cx-w/2+0.5,cy-h/2+0.5,w-1,h-1);
    ctx.fillStyle=fl?C.white:'#d9c8ff';const tri=(x,y,d,s)=>{ctx.beginPath();ctx.moveTo(x,y-s);ctx.lineTo(x+d*s*1.2,y);ctx.lineTo(x,y+s);ctx.closePath();ctx.fill();};
    if(i===0){ctx.fillRect(cx-6,cy-4,2,8);tri(cx+4,cy,-1,4);}
    else if(i===1){tri(cx,cy,-1,4);tri(cx+6,cy,-1,4);}
    else if(i===2){if(playing){ctx.fillRect(cx-4,cy-4,3,8);ctx.fillRect(cx+1,cy-4,3,8);}else tri(cx-3,cy,1,4.5);}
    else if(i===3)ctx.fillRect(cx-4,cy-4,8,8);
    else if(i===4){tri(cx-6,cy,1,4);tri(cx,cy,1,4);}
    else{tri(cx-4,cy,1,4);ctx.fillRect(cx+4,cy-4,2,8);}}
}
const VIS_N=['Bars',''')
open(P,'w').write(s);print('OK')
