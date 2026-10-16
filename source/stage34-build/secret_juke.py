import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
# track entry (loaded on demand)
rep("  ub1:{src:'music/unused-battleship1.mp3',",
    "  secret:{src:'music/secret.mp3',ls:0,le:160.2,lazy:true,buf:null},   // secret song: Jukebox only, after finishing the game or in cheat mode\n"
    "  ub1:{src:'music/unused-battleship1.mp3',")
# finishing the whole game (not cheated, not practice) unlocks it
rep("function finalVictory(e){\n  G.ending=true;G.boss=null;banner('Titan Prime destroyed',4.5);musicOff(4);\n  if(!G.cheated&&!G.practice&&PROG.done<5){PROG.done=5;saveProg();}",
    "function finalVictory(e){\n  G.ending=true;G.boss=null;banner('Titan Prime destroyed',4.5);musicOff(4);\n  if(!G.cheated&&!G.practice&&PROG.done<5){PROG.done=5;saveProg();}\n"
    "  if(!G.cheated&&!G.practice&&!PROG.beat){PROG.beat=true;PROG.secretNew=true;saveProg();}")
# tell the player once, back on the title screen
rep("function goTitle(scr){",
    "function goTitle(scr){if(PROG.secretNew){PROG.secretNew=false;saveProg();showToast('Secret song unlocked in the Jukebox');}")
# list it in the Jukebox when unlocked
rep("function jukeItems(){const it=TRACKS.filter(t=>MUSIC[t.k]).map(t=>({k:t.k,n:t.n}));",
    "function secretOn(){return !!(PROG.beat||CHEAT.on);}\n"
    "function jukeItems(){const it=TRACKS.filter(t=>MUSIC[t.k]).map(t=>({k:t.k,n:t.n}));\n"
    "  if(secretOn())it.splice(TRACKS.findIndex(t=>t.k==='stage'),0,{k:'secret',n:'** Secret song **'});")
rep("const nm=(TRACKS.find(x=>x.k===M.name)||{}).n||M.name;",
    "const nm=M.name==='secret'?'Secret song':(TRACKS.find(x=>x.k===M.name)||{}).n||M.name;")
open(P,'w').write(s);print('OK')
