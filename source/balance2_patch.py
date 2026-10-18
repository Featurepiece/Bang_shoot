# Balance after one-shot-per-press: weapons +15% damage; Mothership 1100 -> 460 HP (it took twice as long as the stage 2 boss).
# Ring: armour pods can be shot off (option 3). Each takes a few hits, cracks, then breaks away as drifting debris and leaves a gap.
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:70]}')
    s=s.replace(a,b)
rep("  fireWeapon(x,y,G.power,G.weapon,1,pl);","  fireWeapon(x,y,G.power,G.weapon,WDMG,pl);")
rep("const HOMING_RANGE=190;","const HOMING_RANGE=190,WDMG=1.15;   // player weapon damage scale")
rep("boss:{hp:1100,","boss:{hp:460,")
# ring pods get health; hits on armour chip it, broken pods leave a gap
rep("RING.e=E('ring',W+130,H/2,{tipT:first?6:0,cx:W+140,cy:H/2,R:94,n,rot:Math.PI*0.5,wk:3,wkT:0.5,gap:[0,1],st:'in',fireT:3});",
    "RING.e=E('ring',W+130,H/2,{tipT:first?6:0,cx:W+140,cy:H/2,R:94,n,rot:Math.PI*0.5,wk:3,wkT:0.5,gap:[0,1],st:'in',fireT:3,podHp:Array(n).fill(RING_POD_HP*DF.hp),podFl:Array(n).fill(0)});")
rep("const RING={e:null,debris:[]},POD_R=10,POD_D=22;","const RING={e:null,debris:[]},POD_R=10,POD_D=22,RING_POD_HP=10,RING_POD_DMG=4;")
rep("function ringBlocks(b){const e=RING.e;if(!e||e.dead||e.dying)return false;\n  for(let i=0;i<e.n;i++){if(i===e.wk||!ringIn(e,i))continue;const [x,y]=ringPod(e,i);if((b.x-x)**2+(b.y-y)**2<(POD_R+1)**2)return true;}return false;}",
    "function ringBlocks(b){const e=RING.e;if(!e||e.dead||e.dying)return false;\n"
    "  for(let i=0;i<e.n;i++){if(i===e.wk||!ringIn(e,i))continue;const [x,y]=ringPod(e,i);if((b.x-x)**2+(b.y-y)**2<(POD_R+1)**2){if(b.pb!==false)ringChip(e,i,b.dmg||1,x,y);return true;}}return false;}\n"
    "function ringChip(e,i,d,x,y){if(!e.podHp||e.st!=='hunt')return;e.podHp[i]-=d;e.podFl[i]=0.08;\n"
    "  if(e.podHp[i]<=0){e.gap.push(i);explode(x,y,1.4,pick([PAL_HOT,PAL_EN]),true);RING.debris.push({x,y,vx:rnd(-60,-25),vy:rnd(-25,25),rot:rnd(0,TAU),vr:rnd(-3,3),t:0});\n"
    "    G.score+=150*G.mult;popup(x,y-10,'+150',C.gold);sx('armour-chip',1,0.9);shake(0.12);
    hitEnemy(e,RING_POD_DMG*DF.hp,x,y,'armour');if(e.dead||e.dying)return;   // every pod broken weakens the ring itself\n"
    "    if(e.wk===i){do{e.wk=(e.wk+1)%e.n;}while(!ringIn(e,e.wk));}}}")
# draw: chipped pods flash on a hit and smoke when badly damaged
rep("  for(let i=0;i<e.n;i++){if(!ringIn(e,i)||i===e.wk)continue;const [x,y]=ringPod(e,i);if(POD.n.complete)ctx.drawImage(POD.n,x-POD_D/2,y-POD_D/2,POD_D,POD_D);}",
    "  for(let i=0;i<e.n;i++){if(!ringIn(e,i)||i===e.wk)continue;const [x,y]=ringPod(e,i);if(POD.n.complete)ctx.drawImage(POD.n,x-POD_D/2,y-POD_D/2,POD_D,POD_D);\n"
    "    if(e.podHp){const f=e.podHp[i]/(RING_POD_HP*DF.hp);if(e.podFl[i]>0){e.podFl[i]-=fdt;ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.8;ctx.drawImage(glow(C.white),x-10,y-10,20,20);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';}\n"
    "      if(f<0.5){ctx.fillStyle='rgba(20,10,10,.45)';ctx.beginPath();ctx.arc(x+2,y-1,5,0,TAU);ctx.fill();if(Math.random()<0.08*Q)P(2,x,y,rnd(-8,8),-18,0.7,2,6,null,0.4);}}}")
# the Extras description mentions the new rule
open(P,'w').write(s);print('OK')
