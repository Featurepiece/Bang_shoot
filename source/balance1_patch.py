"""Balance round 1 (Steven's Medium run: full Homing deleted everything; boss down in ~6 s, partly before its health bar showed).
- Homing: half damage per missile, slower turning (the safe weapon, not the strongest).
- Bosses can't be hurt until their health bar is up (shots spark off while they arrive; bombs skip them).
- Smart bombs: 60 -> 15 damage to bosses; dropped less often.
- Mothership: 600 -> 1000 health, and every ~8 s it raises a shield for 2.5 s after a 0.8 s warning (shots spark off; turrets still hittable).
- The ring: 'Attack here' pointer at the glowing pod, the first time it appears in each game."""
import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n:sys.exit(f'FAIL ({c}x): {a[:100]}')
    s=s.replace(a,b)
# homing
rep("vx:Math.cos(a)*170,vy:Math.sin(a)*170,dmg:2.2*sc,life:3","vx:Math.cos(a)*170,vy:Math.sin(a)*170,dmg:1.5*sc,life:3")
rep("a+=clamp(d,-(dm?2.5:6)*dt,(dm?2.5:6)*dt);","a+=clamp(d,-(dm?2.5:3.5)*dt,(dm?2.5:3.5)*dt);")
# no damage while a boss is arriving, or while the Mothership's shield is up
rep("""        if(e.type==='boss'&&enemies.some(t=>t.type==='ms_turret'""","""        if(e.isBoss&&(e.entering||e.shUp>0)){b.dead=true;for(let i=0;i<2;i++)P(1,b.x,b.y,rnd(-220,-80),rnd(-140,140),0.16,1.4,0,e.shUp>0?C.ice:C.gold,5);if(e.shUp>0)e.shHit=0.12;break;}   // no damage until the health bar is up, or while shielded
        if(e.type==='boss'&&enemies.some(t=>t.type==='ms_turret'""")
# bombs
rep("for(const e of enemies){if(e.dead||e.dying||e.hidden||e.prot||e.x>W+10)continue;hitEnemy(e,e.isBoss?60:40,e.x,e.y);}",
    "for(const e of enemies){if(e.dead||e.dying||e.hidden||e.prot||e.x>W+10||(e.isBoss&&(e.entering||e.shUp>0)))continue;hitEnemy(e,e.isBoss?15:40,e.x,e.y);}")
rep("if(r<0.8)return 'W';return 'B';}","if(r<0.92)return 'W';return 'B';}")
rep("(!G.rear&&r<0.36)?'R':r<0.68?'W':'B';","(!G.rear&&r<0.36)?'R':r<0.86?'W':'B';")
# Mothership health and shield
rep("boss:{hp:600,score:30000,boss:true}","boss:{hp:1100,score:30000,boss:true}")
rep("  msTurretFire(e,dt,ph,sp);","""  msTurretFire(e,dt,ph,sp);msShield(e,dt);""")
rep("function msTurretFire(e,dt,ph,sp){","""// Mothership shield: a warning flicker and hum, then 2.5 s when shots spark off the hull (the turrets can still be shot)
function msShield(e,dt){if(e.dying||G.state!=='play')return;e.shHit=Math.max(0,(e.shHit||0)-dt);
  if(e.shUp>0){e.shUp-=dt;if(e.shUp<=0){e.shUp=0;e.shT=7.5+rnd(0,1.5);}return;}
  e.shT=(e.shT===undefined?7:e.shT)-dt;
  if(e.shT<=0.8&&!e.shWarn){e.shWarn=true;sx('boss-tell',0.7,1.6);}
  if(e.shT<=0){e.shWarn=false;e.shUp=2.5;sx('charge-release',0.6,1.4);}}
function msShieldFx(e,a){const warn=!e.shUp&&e.shT<=0.8&&e.shT>0;if(!e.shUp&&!warn)return;
  const k=e.shUp>0?0.35+0.15*Math.sin(G.t*18)+(e.shHit>0?0.3:0):(Math.sin(G.t*40)>0?0.35:0);if(k<=0)return;
  ctx.save();ctx.globalCompositeOperation='lighter';ctx.globalAlpha=k;ctx.translate(e.x,e.y+Math.sin(G.t*1.3)*1.2);
  ctx.drawImage(glow(C.ice),-a.dw*0.62,-a.dh*0.75,a.dw*1.24,a.dh*1.5);ctx.restore();}
function msTurretFire(e,dt,ph,sp){""")
rep("  if(e.type==='boss'&&ART.boss.n){drawMothership(e,ART.boss);drawTell(e);msTurretFx(e);return;}",
    "  if(e.type==='boss'&&ART.boss.n){drawMothership(e,ART.boss);msShieldFx(e,ART.boss);drawTell(e);msTurretFx(e);return;}")
# ring: 'Attack here' the first time in each game
rep("""function ringSpawn(){const n=20;RING.e=E('ring',W+130,H/2,{""","""function ringSpawn(){const n=20,first=!G.seen.ringTip;G.seen.ringTip=1;RING.e=E('ring',W+130,H/2,{tipT:first?6:0,""")
rep("""  if(e.flash>0){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.8;ctx.drawImage(glow(C.white),x-12,y-12,24,24);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';}
  ctx.restore();}""","""  if(e.flash>0){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.8;ctx.drawImage(glow(C.white),x-12,y-12,24,24);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';}
  if(e.tipT>0&&e.st==='hunt'){e.tipT-=fdt;const bob=Math.sin(G.t*8)*2,above=y>60,ty=above?y-24+bob:y+24-bob;ctx.globalAlpha=Math.min(1,e.tipT);
    ctx.fillStyle=C.gold;ctx.beginPath();if(above){ctx.moveTo(x-5,ty+5);ctx.lineTo(x+5,ty+5);ctx.lineTo(x,ty+11);}else{ctx.moveTo(x-5,ty-5);ctx.lineTo(x+5,ty-5);ctx.lineTo(x,ty-11);}ctx.fill();
    ctx.font=F8;ctx.textAlign='center';ctx.textBaseline='middle';txt('Attack here',clamp(x,50,W-50),above?ty-4:ty+4,C.gold);ctx.globalAlpha=1;}
  ctx.restore();}""")
rep("DEF.ring={hp:70,score:8000,pw:4,drop:1};","DEF.ring={hp:130,score:8000,pw:4,drop:1};")
open(p,'w',encoding='utf-8').write(s);print('OK')
