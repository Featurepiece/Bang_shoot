"""No auto-fire: each press of fire = one shot (keyboard and controller). Holding the button does nothing more.
A press made while the weapon is still recovering is remembered and fires as soon as it's ready (no lost taps).
Touch (drag-to-move) keeps firing while dragging, because a phone thumb can't move and tap at once.
The helper drone fires for a moment after each shot; the weapon sound plays per shot."""
import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n:sys.exit(f'FAIL ({c}x): {a[:100]}')
    s=s.replace(a,b)
rep("  let firing=!noFire&&(keys.Space||keys.KeyZ||keys.KeyJ||drag.id!==null||GP.fire);",
    "  const btn=!noFire&&!!(keys.Space||keys.KeyZ||keys.KeyJ||GP.fire),touchAuto=!noFire&&drag.id!==null;\n  if(btn&&!pl.fireHeld)pl.fireQ=0.25;pl.fireHeld=btn;if(pl.fireQ>0)pl.fireQ-=dt;   // a new press queues one shot (kept for 0.25 s)\n  let firing=btn||touchAuto;")
rep("  G.firing=firing;fireSound(firing);updateHealth(dt);",
    "  G.firingT=Math.max(0,(G.firingT||0)-dt);G.fsT=Math.max(0,(G.fsT||0)-dt);\n  G.firing=G.firingT>0;fireSound(G.fsT>0||(touchAuto&&firing));updateHealth(dt);")
rep("  if(firing&&pl.fireT<=0){pl.fireT=WRATE[G.weapon];playerFire();}",
    "  if(firing&&pl.fireT<=0&&(pl.fireQ>0||touchAuto)){pl.fireT=WRATE[G.weapon];pl.fireQ=0;playerFire();G.firingT=0.4;G.fsT=0.12;}")
open(p,'w',encoding='utf-8').write(s);print('OK')
