import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
# 1) two unused tracks, loaded only when picked in the Jukebox
rep("  boss4:{src:'music/boss4.mp3',",
    "  // unused tracks: Jukebox only, loaded on demand (lazy) so they never slow the game start\n"
    "  ub1:{src:'music/unused-battleship1.mp3',ls:0,le:198.3,lazy:true,buf:null},\n"
    "  ub2:{src:'music/unused-battleship2.mp3',ls:0,le:189.1,lazy:true,buf:null},\n"
    "  boss4:{src:'music/boss4.mp3',")
# loader for a single track (used by the Jukebox for lazy tracks)
rep("function trackPos(){",
    "function loadTrack(name){const t=MUSIC[name];if(!t||t.buf||t.loading||!A.ctx)return;t.loading=true;\n"
    "  fetch(t.src).then(r=>{if(!r.ok)throw 0;return r.arrayBuffer();}).then(ab=>new Promise((res,rej)=>{const pr=A.ctx.decodeAudioData(ab,res,rej);if(pr&&pr.then)pr.then(res,rej);}))\n"
    "    .then(buf=>{t.buf=buf;if(M.want===name&&!M.node)playMusic(name,M.wantOff,0.2);}).catch(()=>{t.loading=false;});}\n"
    "function trackPos(){")
# 2) track list: in-game tracks first, unused at the end with the suffix
rep("{k:'stage4d',n:'Full Power (stage 4)'},{k:'stage',n:'Pixel Blaster (old stage 1)'},{k:'stage2',n:'Arcade Rush (stage 2)'},\n"
    "  {k:'stage3',n:'Pixelata Space (stage 3)'},{k:'stage4',n:'Hammer Press (stage 4)'},{k:'stage5',n:'Final Battle (stage 5)'},",
    "{k:'stage4d',n:'Full Power (stage 4)'},{k:'stage2',n:'Arcade Rush (stage 2)'},\n"
    "  {k:'stage5',n:'Final Battle (stage 5)'},")
rep("{k:'ending',n:'Victory Arpeggio (ending)'}];",
    "{k:'ending',n:'Victory Arpeggio (ending)'},\n"
    "  {k:'stage',n:'Pixel Blaster (unused)'},{k:'stage3',n:'Pixelata Space (unused)'},{k:'stage4',n:'Hammer Press (unused)'},{k:'ub1',n:'Battleship Assault (unused)'},{k:'ub2',n:'Battleship Assault 2 (unused)'}];")
# play: load a lazy track first (playMusic waits via M.want)
rep("else{if(A.ctx)stopMusic(0.3);playMusic(it.k,0,0.2);MENU.playing=it.k;}}}",
    "else{if(A.ctx)stopMusic(0.3);playMusic(it.k,0,0.2);MENU.playing=it.k;if(!MUSIC[it.k].buf){loadTrack(it.k);flash('Loading...');}}}}")
# 3) scrolling list: JB_ROWS visible rows, window follows the selection
rep("const MAIN_Y=148,MAIN_DY=16,OPT_Y=70,JB_Y=52,JB_DY=12,NAME_Y=150;",
    "const MAIN_Y=148,MAIN_DY=16,OPT_Y=70,JB_Y=52,JB_DY=12,NAME_Y=150,JB_ROWS=16;\n"
    "function jbTop(n){const r=MENU.playing==='title'?9:JB_ROWS;MENU.jbTop=clamp(MENU.jbTop||0,Math.max(0,MENU.sel-r+1),Math.min(MENU.sel,Math.max(0,n-r)));return [MENU.jbTop,r];}")
rep("if(s==='jukebox'){const items=jukeItems();for(let i=0;i<items.length;i++){const y=JB_Y+i*JB_DY;",
    "if(s==='jukebox'){const items=jukeItems(),[tp,rw]=jbTop(items.length);for(let i=tp;i<Math.min(items.length,tp+rw);i++){const y=JB_Y+(i-tp)*JB_DY;")
rep("  items.forEach((it,i)=>{const y=JB_Y+i*JB_DY,on=i===MENU.sel,pl_=MENU.playing===it.k&&M.name===it.k&&M.node;\n    if(MENU.playing==='title'&&y>152)return;",
    "  const [tp,rw]=jbTop(items.length);\n"
    "  if(tp>0)txt('^',230,JB_Y-9,'#b9a8e8');if(tp+rw<items.length)txt('v',230,JB_Y+rw*JB_DY-4,'#b9a8e8');\n"
    "  items.forEach((it,i)=>{if(i<tp||i>=tp+rw)return;const y=JB_Y+(i-tp)*JB_DY,on=i===MENU.sel,pl_=MENU.playing===it.k&&M.name===it.k&&M.node;")
rep("txt(nm.length>24?nm.slice(0,23)+'.':nm,260,183,C.white);","txt(nm.length>33?nm.slice(0,32)+'.':nm,260,183,C.white);")
open(P,'w').write(s);print('OK')
