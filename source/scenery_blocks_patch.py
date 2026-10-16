"""Scenery blocks shots on every stage.
- Gate towers: hit area follows the tower's real outline (wide cap, narrowing blocks, spike tips) for shots and for the ship.
- Dreadnought engines (stage 4) and the stage 5 crushers now stop player and enemy shots too.
- Dreadnought turret rows stop shots like the deck.
(Tunnels, hive walls and the hull already did.)"""
import sys,json,os
p=sys.argv[1];s=open(p,encoding='utf-8').read();PROF=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'tower_prof.json')))
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n:sys.exit(f'FAIL ({c}x): {a[:100]}')
    s=s.replace(a,b)
rep("function gateHit(x,y,pad){for(const g of GATE.list){const gx=g.X-G.scroll;if(Math.abs(x-gx)<GATE_HW+(pad||0)&&(y<g.top||y>g.bot))return g;}return null;}",
"""const TOW_PROF="""+json.dumps(PROF)+""",TOW_IW=506,TOW_IH=655;   // tower width (fraction of full width) every 10 px of the art, top to tip
// half-width of a tower at depth d above its tip (d<0 = past the tip); matches drawPillar: tip part at natural size, then repeated armour blocks, cap at the ceiling
function towHalf(d,reach){if(d<0)return -1;const k=GATE_W/TOW_IW,row0=TOW_IH-d/k;let row;
  if(reach<=TOW_IH*k||d<=(TOW_IH-TOW_IH*TOW.band1)*k)row=row0;else{const bh=(TOW.band1-TOW.band0)*TOW_IH*k,lowH=(1-TOW.band1)*TOW_IH*k;row=TOW_IH*TOW.band1-(((d-lowH)%bh)/k);}
  if(d>reach-(TOW.cap*TOW_IH*k))row=Math.min(row,40);
  row=clamp(row,0,TOW_IH-1);return GATE_W*TOW_PROF[Math.min(TOW_PROF.length-1,(row/10)|0)]/2;}
function gateHalfAt(g,y){if(y<g.top+4)return towHalf(g.top+4-y,g.top+10);if(y>g.bot-4)return towHalf(y-(g.bot-4),H-g.bot+10);return -1;}
function gateHit(x,y,pad){for(const g of GATE.list){const gx=g.X-G.scroll;if(Math.abs(x-gx)>GATE_W)continue;const h=gateHalfAt(g,y);if(h>0&&Math.abs(x-gx)<h+(pad||0))return g;}return null;}""")
rep("""  for(const g of GATE.list){const gx=g.X-G.scroll,ox=GATE_HW+9-Math.abs(pl.x-gx);if(ox<=0)continue;
    const oy=pl.y-5<g.top?g.top-(pl.y-5):pl.y+5>g.bot?(pl.y+5)-g.bot:0;if(oy<=0)continue;""",
"""  for(const g of GATE.list){const gx=g.X-G.scroll,h=Math.max(gateHalfAt(g,pl.y-5),gateHalfAt(g,pl.y+5),gateHalfAt(g,pl.y));if(h<=0)continue;const ox=h+9-Math.abs(pl.x-gx);if(ox<=0)continue;
    const oy=pl.y-5<g.top+4?g.top+4-(pl.y-5):pl.y+5>g.bot-4?(pl.y+5)-(g.bot-4):0;if(oy<=0)continue;""")
# player shots
rep("""    if(HV.walls&&!b.dead&&hvWallHit(b.x,b.y)){""","""    if(DN.eng&&!b.dead&&b.y<dnEngBottom(b.x)){b.dead=true;P(1,b.x,b.y,rnd(-120,-40),rnd(10,60),0.15,1.4,0,C.gold,6);}
    if(BS.on&&!b.dead&&b.y>trowTopSX(b.x-BS.x0)){b.dead=true;P(1,b.x,b.y,rnd(-120,-40),rnd(-80,-10),0.15,1.4,0,C.gold,6);}
    if(FL.presses.length&&!b.dead)for(const q of FL.presses)if(q.st>=1&&Math.abs(b.x-q.x)<PR_W*0.42&&b.y<q.yb){b.dead=true;P(1,b.x,b.y,rnd(-120,-40),rnd(-60,60),0.15,1.4,0,C.gold,6);break;}
    if(HV.walls&&!b.dead&&hvWallHit(b.x,b.y)){""")
# enemy shots
rep("""    if(HV.walls&&!b.dead&&hvWallHit(b.x,b.y,2)){""","""    if(DN.eng&&!b.dead&&b.y<dnEngBottom(b.x)-2){b.dead=true;P(0,b.x,b.y,0,0,0.12,4,1,b.col||C.hot);}
    if(FL.presses.length&&!b.dead)for(const q of FL.presses)if(q.st>=1&&Math.abs(b.x-q.x)<PR_W*0.4&&b.y<q.yb-2){b.dead=true;P(0,b.x,b.y,0,0,0.12,4,1,b.col||C.hot);break;}
    if(HV.walls&&!b.dead&&hvWallHit(b.x,b.y,2)){""")
open(p,'w',encoding='utf-8').write(s);print('OK')
