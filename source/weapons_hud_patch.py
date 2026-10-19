# v2.9: each weapon has its own power level; all four weapons shown along the top with their power pips;
# swap (LB / Q / tap) cycles the weapons you own. Power-up carrier: bigger hit area, less health, gentler bob.
import sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/bang_shoot/test.html'
s=open(P).read()
def rep(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit(f'expected {n} got {c}: {a[:80]}')
    s=s.replace(a,b)
rep("weapon:'pulse',stash:null,wflash:0","weapon:'pulse',stash:null,wpow:{pulse:1,laser:0,wave:0,homing:0},wflash:0",2)
rep("const WRATE={pulse:0.085,laser:0.07,wave:0.13,homing:0.085};",
r'''const WRATE={pulse:0.085,laser:0.07,wave:0.13,homing:0.085};
// each weapon keeps its own power; G.power is always the power of the weapon in use
const WORDER=['pulse','laser','wave','homing'];
function wSync(){if(G.wpow)G.wpow[G.weapon]=G.power;}
function wOwned(){return WORDER.filter(w=>G.wpow&&G.wpow[w]>0);}
function wNextStash(){const o=wOwned();if(o.length<2)return null;return o[(o.indexOf(G.weapon)+1)%o.length];}
function selectWeapon(w){wSync();G.weapon=w;G.power=Math.max(1,G.wpow[w]||1);G.wpow[w]=G.power;G.stash=wNextStash();G.wflash=1.2;}''')
rep("  const w=G.stash;G.stash=G.weapon;G.weapon=w;G.wflash=1.2;","  const w=G.stash;selectWeapon(w);")
rep("          if(w===G.weapon){if(G.power<5){G.power++;popup(p.x,p.y-10,WNAME[w]+' '+G.power,pc);}else{G.score+=5000;popup(p.x,p.y-10,'5000',pc);}}\n          else{G.stash=w;popup(p.x,p.y-10,WNAME[w]+' stored',pc);}   // no accidental switch: stored until you swap",
    "          if(w===G.weapon){if(G.power<5){G.power++;popup(p.x,p.y-10,WNAME[w]+' '+G.power,pc);}else{G.score+=5000;popup(p.x,p.y-10,'5000',pc);}wSync();}\n"
    "          else{wSync();const lv=G.wpow[w]||0;   // another weapon: powers that one up (or adds it); you stay on the one you're using\n"
    "            if(lv<=0){G.wpow[w]=1;popup(p.x,p.y-10,WNAME[w]+' stored',pc);}else if(lv<5){G.wpow[w]=lv+1;popup(p.x,p.y-10,WNAME[w]+' '+(lv+1),pc);}else{G.score+=5000;popup(p.x,p.y-10,'5000',pc);}\n"
    "            G.stash=wNextStash();}")
rep("G.lives--;G.power=Math.max(1,G.power-1);","G.lives--;G.power=Math.max(1,G.power-1);wSync();")
rep("G.cheated=true;if(CHEAT.full){G.power=5;G.speed=4;}","G.cheated=true;if(CHEAT.full){G.power=5;G.speed=4;G.wpow={pulse:5,laser:5,wave:5,homing:5};G.stash=wNextStash();}")
# HUD: weapons row
i=s.index("  // weapon: icon box + power pips; speed: five chevrons\n");j=s.index("  if(G.rear){ctx.fillStyle='rgba(8,4,24,.7)';ctx.fillRect(10,76,14,12);",i)
s=s[:i]+r'''  // weapons: all four along the top, each with its own power pips; the one in use glows, ones not collected yet are faint
  wSync();const wf=Math.max(0,G.wflash||0);
  WORDER.forEach((w,i)=>{const x=8+i*44,y=18,lv=G.wpow[w]||0,own=lv>0,cur=w===G.weapon,col=WCOL[w];
    if(cur){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=0.3+0.45*wf+0.15*BEAT.pulse;ctx.drawImage(glow(col),x-5,y-5,24,24);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';}
    ctx.fillStyle='rgba(8,4,24,.7)';ctx.fillRect(x,y,14,14);ctx.globalAlpha=cur?1:own?0.65:0.22;ctx.strokeStyle=col;ctx.lineWidth=1;ctx.strokeRect(x+0.5,y+0.5,13,13);
    drawWIcon(w,x+7,y+7,cur?9+wf*2:8);
    for(let k=0;k<5;k++){ctx.fillStyle=k<lv?col:'rgba(255,255,255,.14)';ctx.globalAlpha=cur?1:own?0.75:0.45;ctx.fillRect(x+17+k*5,y+5,4,4);}
    ctx.globalAlpha=1;});
  if(G.stash){ctx.font=F8;ctx.textAlign='left';ctx.textBaseline='middle';ctx.globalAlpha=0.8;txt(touchUI?'tap':GP.active?'LB':'Q',8+4*44,25,'#d9c8ff');ctx.globalAlpha=1;}
'''+s[j:]
rep("  for(let i=0;i<5;i++){const on=i<=G.speed,x=30+i*7;ctx.globalAlpha=on?(fast?0.55+0.45*Math.max(0,Math.sin(G.t*14-i*0.9)):1):1;\n    ctx.strokeStyle=on?PUP_COL.S:'rgba(255,255,255,.14)';ctx.beginPath();ctx.moveTo(x,28);ctx.lineTo(x+3,31);ctx.lineTo(x,34);ctx.stroke();}",
    "  for(let i=0;i<5;i++){const on=i<=G.speed,x=10+i*7;ctx.globalAlpha=on?(fast?0.55+0.45*Math.max(0,Math.sin(G.t*14-i*0.9)):1):1;\n    ctx.strokeStyle=on?PUP_COL.S:'rgba(255,255,255,.14)';ctx.beginPath();ctx.moveTo(x,37);ctx.lineTo(x+3,40);ctx.lineTo(x,43);ctx.stroke();}")
rep("  if(G.mult>1){txt('x'+G.mult,70,19,C.gold);ctx.fillStyle=C.gold;ctx.fillRect(70,30,30*(G.chainT/1.5),3);}",
    "  if(G.mult>1){ctx.textBaseline='top';txt('x'+G.mult,52,35,C.gold);ctx.fillStyle=C.gold;ctx.fillRect(52,45,30*(G.chainT/1.5),3);}")
# tap a weapon's box to switch to it
rep("  if(G.stash&&p.x<32&&p.y>14&&p.y<58){swapWeapon();return;}   // tap the weapon icons to swap",
    "  if(p.y>14&&p.y<36&&p.x>4&&p.x<186){const w=WORDER[Math.floor((p.x-6)/44)];if(w&&G.wpow[w]>0&&w!==G.weapon&&pl.alive){selectWeapon(w);popup(pl.x,pl.y-16,WNAME[w],WCOL[w]);if(!sx('weapon-swap',1,1))tone('square',520,1040,0.08,0.05);return;}}   // tap a weapon to use it")
# carrier: hit area matches the pod, less health, gentler bob
rep("const y=rnd(55,H-85),e=E('drone',W+30,y,{baseY:y,amp:14,freq:1.6,phase:0,spd:42,carry:k});e.hp=e.max=10*hpScale();e.score=1000;e.hw=12;e.hh=6;",
    "const y=rnd(55,H-85),e=E('drone',W+30,y,{baseY:y,amp:9,freq:1.4,phase:0,spd:42,carry:k});e.hp=e.max=5*hpScale();e.score=1000;e.hw=16;e.hh=10;")
rep("const GAME_VERSION='2.7';","const GAME_VERSION='2.9';")
open(P,'w').write(s);print('OK')
