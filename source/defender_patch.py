"""Defender-inspired enemy behaviour (from reading Defender's 1981 source, Williams / Eugene Jarvis & Sam Dicker):
1. Imperfect aim: ordinary enemies aim with up to +/-16 px of error, and half their shots lead the player's movement
   (Defender: +/-16 px random error, ~53% of shots add the player's velocity). Bosses keep their exact patterns.
2. Shot cap: at most 24 ordinary enemy shots on screen (Defender caps 20 shots + 10 mines). Boss and mini-boss fights are exempt.
3. Dodging: gunners and hunters sidestep out of your line when you're level with them and firing (Defender's mutants
   keep out of your firing line), with a cooldown so a second burst can catch them.
4. Hunters: a drone that gets past you shudders (warning), turns red and becomes a hunter - Defender's lander-into-mutant.
   It hovers just off your line, lines up to fire a 2-shot burst, jitters, leaves after ~9 s, and scores double.
   At most 2 at once in stage 1, 3 later; never in tunnels or boss fights.
5. Credits: Defender added under "Inspired by".
Usage: python3 defender_patch.py ../test.html
"""
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit(f'FAIL ({c}x): {a[:90]}')
    s = s.replace(a, b)


if 'DFN=' in s:
    sys.exit('already patched')

# --- tuning block + helpers ---
rep("""let DF={fire:1,spd:1,hp:1,spawn:1};   // current difficulty multipliers""",
"""let DF={fire:1,spd:1,hp:1,spawn:1};   // current difficulty multipliers
// Defender-inspired tuning (see source/defender_patch.py)
const DFN={aimJit:16,leadChance:0.5,lead:0.8,shotCap:24,dodgeSpd:125,dodgeT:0.3,dodgeCD:[1.1,1.9],huntMax1:2,huntMax:3,huntChance:0.6,huntLife:9};
function bossFiring(){return !!(G.boss||G.mini||(CUR_E&&(CUR_E.isBoss||CUR_E.mb)));}
// sidestep out of the player's firing line (Defender's mutants keep off your line); returns true while dodging
function dodgeLine(e,dt,d){
  if(e.dodgeCD>0)e.dodgeCD-=dt;
  if(e.dodgeT>0){e.dodgeT-=dt;e.y=clamp(e.y+e.dodgeV*dt,22,H-46);return true;}
  if(pl.alive&&G.firing&&!(e.dodgeCD>0)&&e.x>pl.x+40&&e.x<W-10&&Math.abs(e.y-pl.y)<16){
    let dir=e.y<pl.y?-1:1;if(e.y+dir*45<30||e.y+dir*45>H-60)dir=-dir;
    e.dodgeV=dir*DFN.dodgeSpd*Math.min(1.4,d);e.dodgeT=DFN.dodgeT;e.dodgeCD=rnd(DFN.dodgeCD[0],DFN.dodgeCD[1])/Math.min(1.5,d);return true;}
  return false;
}
// a drone that gets past you turns into a hunter (Defender's lander becoming a mutant)
function canHunt(e){
  if(e.huntRoll===undefined)e.huntRoll=Math.random()<DFN.huntChance;
  if(!e.huntRoll||G.state!=='play'||G.boss||G.pre||G.mini||!pl.alive||e.tfollow||tunAt(e.x+G.scroll))return false;
  let n=0;for(const q of enemies)if(q.hunter&&!q.dead&&!q.dying)n++;
  return n<(G.stage<=1?DFN.huntMax1:DFN.huntMax);
}
function mutate(e){
  e.hunter=true;e.ht=0;e.ph='circle';e.pt=rnd(1.2,1.8);e.hs=e.y<pl.y?-1:1;e.score*=2;e.amp=0;
  popup(e.x,e.y-14,'HUNTER',C.hot);tone('sawtooth',180,620,0.4,0.05);P(3,e.x,e.y,0,0,0.3,6,14,C.hot);
}
function hunterUpdate(e,dt,d){
  e.ht+=dt;
  if(e.ht<0.6){e.rot=Math.sin(e.ht*50)*0.3;e.x+=rnd(-1,1);e.y+=rnd(-1,1);return;}   // shudder: the warning before it hunts
  if(e.ht>DFN.huntLife||(!pl.alive&&e.ht>2)){e.x+=230*dt;e.rot*=0.9;if(e.x>W+40)e.dead=true;return;}
  const tx=clamp(pl.x+150,120,W-30);
  e.x+=Math.sign(tx-e.x)*Math.min(Math.abs(tx-e.x)*3,150+10*d)*dt;
  e.pt-=dt;
  if(e.pt<=0){if(e.ph==='strike'){e.ph='circle';e.pt=rnd(1.4,2.2)/Math.min(d,1.6);e.hs=-e.hs;}else{e.ph='strike';e.pt=0.9;e.shot=0;}}
  let ty=null;
  if(e.ph==='strike'){ty=pl.y;if(!e.shot&&e.pt<0.5&&G.state==='play'){e.shot=1;aim(e.x-6,e.y,120+15*d,2,0.12);}}
  else if(!dodgeLine(e,dt,d))ty=pl.y+e.hs*36;   // hover just off your line
  if(ty!==null)e.y+=Math.sign(ty-e.y)*Math.min(Math.abs(ty-e.y)*4,110+10*d)*dt;
  e.y=clamp(e.y+rnd(-1,1)*40*dt,22,H-46);   // jitter (Defender's random hop)
  e.rot=Math.sin(e.t*9)*0.15;
}""")

# --- 2. shot cap for ordinary enemies ---
rep("""function shootE(x,y,vx,vy,col,g){if(!g){vx*=DF.spd;vy*=DF.spd;}eb.push(""",
"""function shootE(x,y,vx,vy,col,g){if(eb.length>=DFN.shotCap&&!bossFiring())return;if(!g){vx*=DF.spd;vy*=DF.spd;}eb.push(""")

# --- 1. imperfect aim, half the shots lead the player ---
rep("""n=n||1;spread=spread||0;const tx=pl.alive?pl.x:70,ty=pl.alive?pl.y:H/2,a=Math.atan2(ty-y,tx-x);""",
"""n=n||1;spread=spread||0;let tx=pl.alive?pl.x:70,ty=pl.alive?pl.y:H/2;
  if(pl.alive&&!bossFiring()){const T=Math.hypot(tx-x,ty-y)/Math.max(40,spd*DF.spd);
    if(Math.random()<DFN.leadChance){tx+=clamp((pl.vx||0)*T*DFN.lead,-120,120);ty+=clamp((pl.vy||0)*T*DFN.lead,-80,80);}
    tx+=rnd(-DFN.aimJit,DFN.aimJit);ty+=rnd(-DFN.aimJit,DFN.aimJit);}
  const a=Math.atan2(ty-y,tx-x);""")

# player velocity, used for leading shots
rep("""const ivx=(pl.x-pl.lx)/Math.max(dt,1e-4),ivy=(pl.y-pl.ly)/Math.max(dt,1e-4);pl.lx=pl.x;pl.ly=pl.y;""",
"""const ivx=(pl.x-pl.lx)/Math.max(dt,1e-4),ivy=(pl.y-pl.ly)/Math.max(dt,1e-4);pl.lx=pl.x;pl.ly=pl.y;pl.vx=ivx;pl.vy=ivy;""")

# --- 4. hunters ---
rep("""case 'drone':case 'swarm':""",
"""case 'drone':case 'swarm':
        if(e.type==='drone'&&!e.hunter&&!e.dying&&e.t>1.5&&e.x<pl.x-20&&canHunt(e))mutate(e);
        if(e.hunter){hunterUpdate(e,dt,d);break;}""")

# --- 3. gunners dodge your line ---
rep("""e.y=clamp(e.y+Math.sin(e.t*2.2)*14*dt,20,H-40);""",
"""if(!dodgeLine(e,dt,d))e.y=clamp(e.y+Math.sin(e.t*2.2)*14*dt,20,H-40);""")

# hunter look: pulsing red overlay
rep("""else if(white){ctx.globalAlpha=e.dying?0.75:0.45;ctx.drawImage(fi>=0?a.wframes[fi]:a.w,-a.dw/2,-a.dh/2+oy,a.dw,a.dh);}""",
"""else if(white){ctx.globalAlpha=e.dying?0.75:0.45;ctx.drawImage(fi>=0?a.wframes[fi]:a.w,-a.dw/2,-a.dh/2+oy,a.dw,a.dh);}
  if(e.hunter&&!e.dying){ctx.globalAlpha=0.45+0.25*Math.sin(e.t*12);ctx.drawImage(tintOf(img,'#ff2d55'),-a.dw/2,-a.dh/2+oy,a.dw,a.dh);}""")

# --- 5. credits ---
rep("""['Gradius  -  Darius',8,C.white],""",
"""['Gradius  -  Darius',8,C.white],['Defender',8,C.white],""")

open(p, 'w', encoding='utf-8').write(s)
print('ok')
