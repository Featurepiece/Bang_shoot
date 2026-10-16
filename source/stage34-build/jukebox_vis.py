# Jukebox: unused tracks under an "Unused" heading (plain names); visualiser with six styles (left/right or tap to change)
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
# --- unused section ---
rep("  {k:'stage',n:'Pixel Blaster (unused)'},{k:'stage3',n:'Pixelata Space (unused)'},{k:'stage4',n:'Hammer Press (unused)'},{k:'uhive',n:'Insectoid Arpeggio (unused)'},{k:'ub1',n:'Battleship Assault (unused)'},{k:'ub2',n:'Battleship Assault 2 (unused)'}];",
    "  {k:'stage',n:'Pixel Blaster',u:1},{k:'stage3',n:'Pixelata Space',u:1},{k:'stage4',n:'Hammer Press',u:1},{k:'uhive',n:'Insectoid Arpeggio',u:1},{k:'ub1',n:'Battleship Assault',u:1},{k:'ub2',n:'Battleship Assault 2',u:1}];")
rep("function jukeItems(){const it=TRACKS.filter(t=>MUSIC[t.k]).map(t=>({k:t.k,n:t.n}));\n  if(secretOn())it.splice(TRACKS.findIndex(t=>t.k==='stage'),0,{k:'secret',n:'** Secret song **'});",
    "function jukeItems(){const it=TRACKS.filter(t=>MUSIC[t.k]&&!t.u).map(t=>({k:t.k,n:t.n}));\n"
    "  if(secretOn())it.push({k:'secret',n:'** Secret song **'});\n"
    "  const un=TRACKS.filter(t=>MUSIC[t.k]&&t.u);if(un.length){it.push({k:'hdr',n:'Unused'});for(const t of un)it.push({k:t.k,n:t.n});}")
# up/down skip the heading; left/right change the visualiser
rep("    if(a==='up')MENU.sel=(MENU.sel+n-1)%n;else if(a==='down')MENU.sel=(MENU.sel+1)%n;\n    else if(a==='back'){MENU.scr='main';MENU.sel=1;MENU.playing=null;titleMusic();}",
    "    if(a==='up'||a==='down'){const st=a==='up'?n-1:1;MENU.sel=(MENU.sel+st)%n;if(items[MENU.sel].k==='hdr')MENU.sel=(MENU.sel+st)%n;}\n"
    "    else if(a==='left'||a==='right'){visStep(a==='left'?-1:1);}\n"
    "    else if(a==='back'){MENU.scr='main';MENU.sel=1;MENU.playing=null;titleMusic();}")
rep("      if(it.k==='back'){MENU.scr='main';MENU.sel=1;MENU.playing=null;titleMusic();}\n      else if(it.k==='sync')",
    "      if(it.k==='hdr'){}\n      else if(it.k==='back'){MENU.scr='main';MENU.sel=1;MENU.playing=null;titleMusic();}\n      else if(it.k==='sync')")
# touch: tapping the heading does nothing; tapping the visualiser changes style
rep("if(s==='jukebox'){const items=jukeItems(),[tp,rw]=jbTop(items.length);for(let i=tp;i<Math.min(items.length,tp+rw);i++){const y=JB_Y+(i-tp)*JB_DY;",
    "if(s==='jukebox'){if(p.x>256&&p.y>40&&p.y<160&&!MENU.sync){visStep(1);return;}const items=jukeItems(),[tp,rw]=jbTop(items.length);for(let i=tp;i<Math.min(items.length,tp+rw);i++){if(items[i].k==='hdr')continue;const y=JB_Y+(i-tp)*JB_DY;")
# draw the heading
rep("  items.forEach((it,i)=>{if(i<tp||i>=tp+rw)return;const y=JB_Y+(i-tp)*JB_DY,on=i===MENU.sel,pl_=MENU.playing===it.k&&M.name===it.k&&M.node;",
    "  items.forEach((it,i)=>{if(i<tp||i>=tp+rw)return;const y=JB_Y+(i-tp)*JB_DY,on=i===MENU.sel,pl_=MENU.playing===it.k&&M.name===it.k&&M.node;\n"
    "    if(it.k==='hdr'){ctx.fillStyle='rgba(185,168,232,.35)';ctx.fillRect(16,y,40,1);ctx.fillRect(112,y,126,1);txt('Unused',62,y,'#8d7fc0');return;}")
# more analyser detail for the visualiser (also gives a waveform)
rep("A.an.fftSize=128;","A.an.fftSize=256;")
# --- visualiser styles ---
i=s.index("function drawVisualiser(x,y,w,h){");j=s.index("function lyricIndex(pos){",i)
vis=r'''const VIS_N=['Bars','Mirror','Scope','Radial','Warp','Blocks'];
let visMode=0;try{visMode=(+localStorage.getItem('bangshoot-vis')||0)%VIS_N.length;}catch(e){}
const VIS={peaks:[],stars:[],rot:0,shown:0};
function visStep(d){visMode=(visMode+d+VIS_N.length)%VIS_N.length;VIS.shown=1.6;try{localStorage.setItem('bangshoot-vis',visMode);}catch(e){}if(typeof sx==='function')sx('menu-move',0.5,1.2);}
function visBand(d,n,i,bars){return d[Math.floor(Math.pow(i/bars,1.6)*n*0.8)]/255;}
function drawVisualiser(x,y,w,h){
  panel(x,y,w,h);
  const lbl=()=>{ctx.font=F8;ctx.textBaseline='middle';ctx.textAlign='right';ctx.globalAlpha=VIS.shown>0?1:0.45;txt('< '+VIS_N[visMode]+' >',x+w-6,y+9,VIS.shown>0?C.gold:'#8d7fc0');ctx.globalAlpha=1;ctx.textAlign='left';};
  VIS.shown=Math.max(0,VIS.shown-1/60);
  if(!A.an){lbl();return;}
  const n=A.an.frequencyBinCount,d=A.fbuf||(A.fbuf=new Uint8Array(n));A.an.getByteFrequencyData(d);
  let bass=0;for(let i=1;i<6;i++)bass+=d[i];bass/=5*255;
  ctx.save();ctx.beginPath();ctx.rect(x+2,y+2,w-4,h-4);ctx.clip();ctx.globalCompositeOperation='lighter';
  const m=visMode,cx=x+w/2,cy=y+h/2;
  if(m===0){const bars=28,bw=(w-12)/bars;   // Bars: the original
    for(let i=0;i<bars;i++){const v=visBand(d,n,i,bars),bh=Math.max(1,v*(h-12));ctx.fillStyle=NEON[i%NEON.length];ctx.globalAlpha=0.35+0.65*v;ctx.fillRect(x+6+i*bw,y+h-6-bh,bw-2,bh);}}
  else if(m===1){const bars=32,bw=(w-12)/bars;   // Mirror: bars grow up and down from the middle, with a soft reflection
    for(let i=0;i<bars;i++){const v=visBand(d,n,i,bars),bh=Math.max(1,v*(h/2-8));const c=NEON[i%NEON.length];
      ctx.fillStyle=c;ctx.globalAlpha=0.4+0.6*v;ctx.fillRect(x+6+i*bw,cy-bh,bw-2,bh);ctx.globalAlpha=(0.4+0.6*v)*0.45;ctx.fillRect(x+6+i*bw,cy,bw-2,bh);}
    ctx.globalAlpha=0.5;ctx.fillStyle=C.white;ctx.fillRect(x+6,cy,w-12,1);}
  else if(m===2){const td=A.tbuf||(A.tbuf=new Uint8Array(A.an.fftSize));A.an.getByteTimeDomainData(td);   // Scope: the waveform, glowing
    for(const [lw,al,col] of [[5,0.15,NEON[0]],[2.5,0.35,NEON[1]],[1.2,1,C.white]]){ctx.strokeStyle=col;ctx.globalAlpha=al;ctx.lineWidth=lw;ctx.beginPath();
      for(let i=0;i<td.length;i++){const px=x+6+i/(td.length-1)*(w-12),py=cy+((td[i]-128)/128)*(h/2-8)*1.6;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.stroke();}}
  else if(m===3){const bars=48,r0=16+bass*10;VIS.rot+=0.004+bass*0.02;   // Radial: spokes round a pulsing ring
    for(let i=0;i<bars;i++){const v=visBand(d,n,i%24,24),a=VIS.rot+i*TAU/bars,l=4+v*(h/2-r0-6);ctx.strokeStyle=NEON[i%NEON.length];ctx.globalAlpha=0.35+0.65*v;ctx.lineWidth=2.2;
      ctx.beginPath();ctx.moveTo(cx+Math.cos(a)*r0,cy+Math.sin(a)*r0);ctx.lineTo(cx+Math.cos(a)*(r0+l),cy+Math.sin(a)*(r0+l));ctx.stroke();}
    ctx.globalAlpha=0.5+0.5*bass;ctx.drawImage(glow(NEON[2]),cx-r0,cy-r0,r0*2,r0*2);}
  else if(m===4){const S=VIS.stars;while(S.length<90)S.push({a:Math.random()*TAU,z:Math.random(),c:NEON[S.length%NEON.length]});   // Warp: stars rush out with the bass
    const sp=0.004+bass*0.03;for(const st of S){const z0=st.z;st.z+=sp*(0.4+st.z);if(st.z>1){st.z=0.02;st.a=Math.random()*TAU;continue;}
      const R=w*0.7,r1=z0*z0*R,r2=st.z*st.z*R;ctx.strokeStyle=st.c;ctx.globalAlpha=Math.min(1,st.z*1.6);ctx.lineWidth=1+st.z*1.5;
      ctx.beginPath();ctx.moveTo(cx+Math.cos(st.a)*r1,cy+Math.sin(st.a)*r1*0.6);ctx.lineTo(cx+Math.cos(st.a)*r2,cy+Math.sin(st.a)*r2*0.6);ctx.stroke();}
    ctx.globalAlpha=0.25+0.6*bass;const g=20+bass*30;ctx.drawImage(glow(NEON[3]),cx-g,cy-g,g*2,g*2);}
  else{const bars=16,bw=(w-12)/bars,rows=12,rh=(h-14)/rows,P_=VIS.peaks;   // Blocks: LED meter with falling peak caps
    for(let i=0;i<bars;i++){const v=visBand(d,n,i,bars),on=Math.round(v*rows);P_[i]=Math.max((P_[i]||0)-0.12,on);
      for(let r=0;r<rows;r++){const lit=r<on,col=r>=rows-2?'#ff3d6e':r>=rows-5?C.gold:'#3dffa0';ctx.fillStyle=col;ctx.globalAlpha=lit?0.95:0.07;ctx.fillRect(x+7+i*bw,y+h-7-(r+1)*rh+1,bw-3,rh-2);}
      const pr=Math.min(rows-1,Math.floor(P_[i]));if(P_[i]>0.5){ctx.fillStyle=C.white;ctx.globalAlpha=0.9;ctx.fillRect(x+7+i*bw,y+h-7-(pr+1)*rh+1,bw-3,2);}}}
  ctx.restore();ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';lbl();
}
'''
s=s[:i]+vis+s[j:]
open(P,'w').write(s);print('OK')
