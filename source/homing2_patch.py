"""Homing lock-on range: missiles only seek enemies within ~190 px of the ship, and burn out after 1.1 s
(at full power Homing killed enemies 0.33 s after they appeared, 87% of them in the right-hand third)."""
import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n:sys.exit(f'FAIL ({c}x): {a[:90]}')
    s=s.replace(a,b)
rep("function nearestEnemy(x,y){let best=null,bd=1e9;for(const e of enemies){if(e.dead||e.dying||e.entering||e.hidden||e.prot||e.x>W+10||e.x<x-40||e.type==='mb_magnet')continue;",
    "const HOMING_RANGE=190;\nfunction nearestEnemy(x,y,lock){let best=null,bd=1e9;for(const e of enemies){if(e.dead||e.dying||e.entering||e.hidden||e.prot||e.x>W+10||e.x<x-40||e.type==='mb_magnet')continue;if(lock&&Math.hypot(e.x-pl.x,e.y-pl.y)>HOMING_RANGE+(e.isBoss?60:0))continue;")
rep("if(!b.tgt||b.tgt.dead||b.tgt.dying||b.rt<=0){b.tgt=nearestEnemy(b.x,b.y);b.rt=0.15;}",
    "if(!b.tgt||b.tgt.dead||b.tgt.dying||b.rt<=0){b.tgt=nearestEnemy(b.x,b.y,b.k==='homing');b.rt=0.15;}")
rep("dmg:1.5*sc,life:3,","dmg:1.5*sc,life:1.1,")
open(p,'w',encoding='utf-8').write(s);print('OK')
