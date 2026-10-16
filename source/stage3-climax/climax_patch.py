# Stage 3 music: Arcade Climax (game edit, 155.2 BPM). Source cut at 67.21 s (16 bars before the drop), -1.1 dB -> -16.1 LUFS.
#  DROP 24.75 drums slam in | MINI +8 bars | WALLS 58.74 drums re-enter after dropout 1 | BREAK 85.07 dropout 2: serpent
#  FULL 124.67 climax: tunnel + hardest waves | END 156.98 last phrase: Warning | HIT 169.88 final hit: boss
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
rep("MUSIC.stage3h={src:'music/stage3-hive.mp3',ls:109.83,le:146.6,drop:23.82,beat:0.40055,anchor:23.82,buf:null};",
    "MUSIC.stage3h={src:'music/stage3-climax.mp3',ls:124.67,le:171.4,drop:24.75,beat:0.38665,anchor:24.75,buf:null};   // Arcade Climax (game edit): the Hive\n"
    "MUSIC.uhive={src:'music/stage3-hive.mp3',ls:109.83,le:146.6,lazy:true,buf:null};   // Insectoid Arpeggio, the first Hive track (Jukebox only)")
rep("const HV={track:'stage3h',DROP:23.82,MINI:36.64,WALLS:49.5,BREAK:82.88,FULL:109.83,END:146.61,HIT:162.2,",
    "const HV={track:'stage3h',DROP:24.75,MINI:37.12,WALLS:58.74,BREAK:85.07,FULL:124.67,END:156.98,HIT:169.88,")
# the serpent section is longer now: once the serpent is dead, waves fill the rest of it
rep("if(T<HV.FULL){if(!HV.serp&&!HV.serpDone&&T<HV.FULL-4)serpSpawn();return true;}",
    "if(T<HV.FULL){if(!HV.serp&&!HV.serpDone&&T<HV.FULL-4)serpSpawn();if(HV.serpDone)sxWaves(dt,T,HV,1.0);return true;}")
# carriers at the same musical moments as before
rep("3:[[44,'W'],[70,'R'],[120,'W']]","3:[[45,'W'],[75,'R'],[135,'W']]")
# Jukebox names
rep("{k:'stage3h',n:'Insectoid Arpeggio (stage 3)'}","{k:'stage3h',n:'Arcade Climax (stage 3)'}")
rep("{k:'ub1',n:'Battleship Assault (unused)'}","{k:'uhive',n:'Insectoid Arpeggio (unused)'},{k:'ub1',n:'Battleship Assault (unused)'}")
open(P,'w').write(s);print('OK')
