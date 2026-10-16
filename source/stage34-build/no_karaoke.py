# Jukebox: remove the lyric karaoke and lyric sync (Steven: it doesn't work). The title song plays like any other track.
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
rep("""  const part=loadPartial();
  if(part&&part.length)it.push({k:'resume',n:'Continue sync (line '+(part.length+1)+')'});
  it.push({k:'sync',n:part&&part.length?'Restart lyric sync':'Sync lyrics (tap along)'});if(LYR_T){it.push({k:'copy',n:'Copy lyric timings'});it.push({k:'clear',n:'Clear lyric timings'});}
  it.push({k:'back',n:'Back'});return it;}""","""  it.push({k:'back',n:'Back'});return it;}""")
rep("panel(10,40,236,MENU.playing==='title'?120:210);","panel(10,40,236,210);")
rep("function jbTop(n){const r=MENU.playing==='title'?9:JB_ROWS;","function jbTop(n){const r=JB_ROWS;")
rep("""  const kara=MENU.playing==='title'&&M.name==='title'&&M.node;
  drawVisualiser(256,40,214,kara?120:120);
  if(kara){const t=MUSIC.title,p=trackPos(),tot=t.buf?t.buf.duration:t.le;ctx.fillStyle='rgba(255,255,255,.15)';ctx.fillRect(262,154,202,2);ctx.fillStyle=C.gold;ctx.fillRect(262,154,202*clamp(p/tot,0,1),2);}
  else if(M.node""","""  drawVisualiser(256,40,214,120);
  if(M.node""")
rep("  if(MENU.playing==='title'&&M.name==='title'&&M.node)drawKaraoke();\n","")
open(P,'w').write(s);print('OK')
