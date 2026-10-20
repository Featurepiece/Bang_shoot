# v3.9: engine flames glow as you approach the Dreadnought; the bridge and main gun sit at the far right during the fight;
# cover blocks removed; the engine chase lasts longer.
import sys
P=sys.argv[1] if len(sys.argv)>1 else 'test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:90]}')
    s=s.replace(a,b)
# engine glow all the time (resting flames), not only during the escape
rep("function drawEscFlames(){const s=DN.esc;if(!s||s.dead||!BS.on)return;const ex=BS.x0+NZX;if(ex<-200||ex>W+60)return;const ys=nzYs(),k=Math.min(1,s.v/120);",
    "const IDLE_NZ=[{st:'idle'},{st:'idle'},{st:'idle'}];\nfunction drawEscFlames(){const s=DN.esc;if(!BS.on||(s&&s.dead))return;const ex=BS.x0+NZX;if(ex<-200||ex>W+60)return;const ys=nzYs(),k=s?Math.min(1,s.v/120):0.35,nz=s?s.nz:IDLE_NZ;")
rep("  s.nz.forEach((z,i)=>{const y=ys[i],burst=z.st==='burst'","  nz.forEach((z,i)=>{const y=ys[i],burst=z.st==='burst'")
# the bridge (and the gun 100 px in front of it) 60 px further along the ship and further right on screen; the ship still stops at the same moment
rep("const BRIDGE_SX=4257,BRIDGE_STOP_X=W-130;","const BRIDGE_SX=4317,BRIDGE_STOP_X=W-70;")
# no cover blocks
rep("function dnHullExtras(){DN.blocks=GUN.BLOCKS.map(sx=>({sx,hp:2,fl:0}));","function dnHullExtras(){DN.blocks=[];")
# a longer engine chase: slower creep away, more damage needed
rep("const ESC={hp:260,bolt:650,surge:420,brake:700,creep:10,creepX:150,acc:5,flame:150};","const ESC={hp:420,bolt:650,surge:420,brake:700,creep:8,creepX:150,acc:1.3,flame:150};")
rep("and fires a beam: hide behind the deck blocks.","and fires a beam: get out of its line.")
rep("const GAME_VERSION='3.7';","const GAME_VERSION='3.9';")
open(P,'w').write(s);print('OK')
